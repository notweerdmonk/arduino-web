"""PubSub infrastructure for board communication and WebSocket broadcast."""

import glob
import logging
import os
import threading
import time
from enum import Enum
from typing import Any, Optional

from medminder_dash import state
from board_manager_client.pubsub_client import PubSubClient

class PubSubTopic(str, Enum):
    """PubSub topic constants for board manager communication."""

    DAEMON_READY = "sys::daemon/ready"
    BOARD_EVENT = "board::+::event"
    RESP = "resp::*"
    HEALTH = "sys::health"
    RESP_COMPILE = "resp::compile::*"
    RESP_UPLOAD = "resp::upload::*"


_logger = logging.getLogger(__name__)

_pubsub: Optional[PubSubClient] = None
_pubsub_lock = threading.Lock()


def _start_fallback_scanner(ps: PubSubClient) -> None:
    """Start the fallback board scanner thread.

    Args:
        ps: PubSubClient instance for event callbacks.
    """
    state._stop_fallback_scan = False
    state._fallback_scanner = threading.Thread(
        target=_fallback_scan_loop, args=(ps,), daemon=True
    )
    state._fallback_scanner.start()
    _logger.info(
        "Fallback board scanner started (every %.1fs)", state._fallback_scan_interval
    )


def _stop_fallback_scanner() -> None:
    """Signal the fallback scanner thread to stop."""
    state._stop_fallback_scan = True
    _logger.info("Fallback board scanner stopped")


def _fallback_scan_loop(ps: PubSubClient) -> None:
    """Continuously scan for boards via glob patterns as a fallback.

    Args:
        ps: PubSubClient for publishing board events.
    """
    while not state._stop_fallback_scan:
        with state._daemon_ready_lock:
            if state._daemon_ready:
                time.sleep(state._fallback_scan_interval)
                continue
        try:
            found = set()
            for pattern in state._fallback_patterns:
                for path in glob.glob(pattern):
                    found.add(path)
            with state._known_ports_lock:
                before = set(state._known_ports.keys())
            added = found - before
            removed = {p for p in before if p.startswith("/dev/tty")} - found
            for port in removed:
                _logger.info("Fallback: board disconnected at %s", port)
                _on_board_event(
                    {
                        "data": {
                            "port": port,
                            "event": "disconnected",
                            "board": state._known_ports.get(port, {}).get("board", ""),
                            "fqbn": state._known_ports.get(port, {}).get("fqbn", ""),
                            "hardware_id": state._known_ports.get(port, {}).get(
                                "hardware_id", ""
                            ),
                        }
                    }
                )
            for port in sorted(added):
                _logger.info("Fallback: board connected at %s", port)
                info = _resolve_board_info(port)
                _on_board_event(
                    {
                        "data": {
                            "port": port,
                            "event": "connected",
                            "board": info["board"],
                            "fqbn": info["fqbn"],
                            "hardware_id": info.get("hardware_id", ""),
                        }
                    }
                )
        except Exception:
            _logger.exception("Fallback scanner error")
        time.sleep(state._fallback_scan_interval)


from .settings import load_sketch_dir


def _resolve_board_info(port: str) -> dict:
    """Resolve board name, FQBN, and hardware ID for a port.

    Args:
        port: Board port path.

    Returns:
        Dict with keys board, fqbn, hardware_id.
    """
    try:
        from arduino_grpc.client import ArduinoGrpcClient

        client = ArduinoGrpcClient()
        client.connect()
        client.init()
        boards = client.list_boards(timeout=3)
        client.disconnect()
        for b in boards:
            if b.port.address == port:
                return {
                    "board": b.name,
                    "fqbn": b.fqbn,
                    "hardware_id": b.port.hardware_id,
                }
    except Exception:
        _logger.debug("_resolve_board_info: failed for %s", port, exc_info=True)
    return {"board": "", "fqbn": "", "hardware_id": ""}


def ensure_sketch_dir() -> None:
    """Create the sketch directory if it does not exist."""
    os.makedirs(_get_sketch_dir(), exist_ok=True)


def _get_sketch_dir() -> str:
    """Return the current sketch directory path."""
    return load_sketch_dir()


def _get_alarm_hpp_path() -> str:
    """Return the full path to the alarm.hpp file."""
    return os.path.join(_get_sketch_dir(), "alarm.hpp")


def init_pubsub(
    app,
    use_uds=True,
    tcp_host="127.0.0.1",
    tcp_port=9090,
    uds_path="/tmp/board_mgr.sock",
):
    """Initialize PubSub connection to the BoardManagerService.

    Args:
        app: Flask application instance.
        use_uds: Whether to use Unix domain sockets.
        tcp_host: TCP host for BMS fallback.
        tcp_port: TCP port for BMS fallback.
        uds_path: Unix domain socket path.

    Returns:
        The PubSubClient instance.
    """
    global _pubsub, _app
    state._app = app
    ps = PubSubClient(
        uds_path=uds_path, use_uds=use_uds, tcp_host=tcp_host, tcp_port=tcp_port
    )
    ps.on_reconnect = _on_pubsub_reconnect
    with _pubsub_lock:
        _pubsub = ps
    try:
        ps.connect(retry=True)
    except (ConnectionError, OSError) as e:
        _logger.warning("Could not connect to BoardManagerService: %s", e)
    ps.subscribe(PubSubTopic.DAEMON_READY, _on_daemon_ready)
    ps.subscribe(PubSubTopic.BOARD_EVENT, _on_board_event)
    ps.subscribe(PubSubTopic.RESP, _on_resp)
    ps.subscribe(PubSubTopic.HEALTH, lambda msg: None)
    tools = app.extensions.get("arduino_sketch_tools")
    if tools:
        tools.pubsub = ps
        ps.subscribe(PubSubTopic.RESP_COMPILE, tools._on_compile_resp)
        ps.subscribe(PubSubTopic.RESP_UPLOAD, tools._on_upload_resp)
    ps.start_reader()
    return ps


def get_pubsub() -> Optional[PubSubClient]:
    """Return the current PubSubClient instance, or None.

    Returns:
        The PubSubClient or None if not initialized.
    """
    with _pubsub_lock:
        return _pubsub


def _clear_sketch_tools_state(port: str) -> None:
    """Clear arduino sketch tools state for a given port.

    Args:
        port: Board port to clear state for.
    """
    tools = state._app.extensions.get("arduino_sketch_tools") if state._app else None
    if tools is None:
        return
    _logger.debug("Clearing arduino_sketch_tools state for %s", port)
    cleanup_map: list[tuple[dict, Any]] = [
        (tools._compile_results, tools._compile_results_lock),
        (tools._upload_results, tools._upload_results_lock),
        (tools._compile_start, None),
        (tools._compile_meta, tools._compile_meta_lock),
        (tools._upload_meta, tools._upload_meta_lock),
        (tools._last_compiled_sketch, tools._last_compiled_sketch_lock),
        (tools._last_compile_mtime, tools._last_compile_mtime_lock),
        (tools._last_compile_checksum, tools._last_compile_checksum_lock),
        (tools._last_uploaded_sketch, tools._last_uploaded_sketch_lock),
    ]
    for d, lock in cleanup_map:
        if lock:
            with lock:
                d.pop(port, None)
        else:
            d.pop(port, None)


def _on_board_event(msg: dict) -> None:
    """Handle a board event (connected/disconnected) from PubSub.

    Args:
        msg: PubSub message dict with topic and data.
    """
    data = msg.get("data", {})
    event = data.get("event", "")
    port = data.get("port", "")
    if event == "connected":
        with state._known_ports_lock:
            if port in state._known_ports:
                return
            state._known_ports[port] = data
            _logger.debug(
                "Board connected: %s (total: %d)", port, len(state._known_ports)
            )
    elif event == "disconnected":
        with state._known_ports_lock:
            if port not in state._known_ports:
                return
            state._known_ports.pop(port, None)
            _logger.debug(
                "Board disconnected: %s (total: %d)", port, len(state._known_ports)
            )
        _clear_sketch_tools_state(port)
    if event:
        with state._board_events_lock:
            state._board_events.append(data)
            state._board_events[:] = state._board_events[-100:]
    if state._app and event:
        try:
            from flask import render_template

            with state._app.app_context():
                event_html = '<div hx-swap-oob="afterbegin:#live-events-card">' + render_template("partials/board_event.html", events=[data]) + '</div>'
            broadcast_ws(event_html)
        except Exception:
            _logger.debug("Failed to broadcast board event via WS", exc_info=True)


def _on_daemon_ready(msg: dict) -> None:
    """Handle the daemon ready event from PubSub.

    Args:
        msg: PubSub event message.
    """
    if msg.get("type") != "event":
        return
    with state._daemon_ready_lock:
        if state._daemon_ready:
            return
        state._daemon_ready = True
    _logger.info("Daemon ready event received")


def _on_resp(msg: dict) -> None:
    """Handle a response message by setting the pending response event.

    Args:
        msg: Response message dict.
    """
    topic = msg.get("topic", "")
    _logger.debug("_on_resp: topic=%s", topic)
    with state._pending_responses_lock:
        entry = state._pending_responses.get(topic)
    if entry is not None:
        result, event = entry
        if not event.is_set():
            state._pending_responses[topic] = (msg, event)
            event.set()


def _wait_for_response(topic: str, timeout: float = 60.0) -> dict | None:
    """Wait for a response on a given topic.

    Args:
        topic: Topic to wait for.
        timeout: Maximum wait time in seconds.

    Returns:
        Response message dict, or None on timeout.
    """
    event = threading.Event()
    with state._pending_responses_lock:
        state._pending_responses[topic] = (None, event)
    try:
        if event.wait(timeout):
            with state._pending_responses_lock:
                result, _ = state._pending_responses.pop(topic, (None, None))
            return result
        _logger.warning("Response timeout for topic '%s'", topic)
        return None
    finally:
        with state._pending_responses_lock:
            state._pending_responses.pop(topic, None)


def _on_pubsub_reconnect() -> None:
    """Re-register all PubSub handlers after a reconnection."""
    with state._daemon_ready_lock:
        state._daemon_ready = False
    ps = get_pubsub()
    if not ps:
        _logger.info("PubSub reconnected — no pubsub instance yet")
        return
    ps.subscribe(PubSubTopic.DAEMON_READY, _on_daemon_ready)
    ps.subscribe(PubSubTopic.BOARD_EVENT, _on_board_event)
    ps.subscribe(PubSubTopic.RESP, _on_resp)
    ps.subscribe(PubSubTopic.HEALTH, lambda msg: None)
    if state._app is not None:
        tools = state._app.extensions.get("arduino_sketch_tools")
        if tools:
            tools.pubsub = ps
            ps.subscribe(PubSubTopic.RESP_COMPILE, tools._on_compile_resp)
            ps.subscribe(PubSubTopic.RESP_UPLOAD, tools._on_upload_resp)
    _logger.info("PubSub reconnected — all handlers re-registered")


def is_daemon_ready() -> bool:
    """Return whether the daemon has reported ready.

    Returns:
        True if daemon is ready.
    """
    with state._daemon_ready_lock:
        return state._daemon_ready


def is_connected() -> bool:
    """Return whether the PubSub client is connected.

    Returns:
        True if connected.
    """
    ps = get_pubsub()
    return ps is not None and ps.is_connected


def add_ws_client(ws) -> None:
    """Register a WebSocket client for broadcast.

    Args:
        ws: WebSocket connection object.
    """
    with state._ws_lock:
        state._ws_clients.append(ws)


def remove_ws_client(ws) -> None:
    """Unregister a WebSocket client.

    Args:
        ws: WebSocket connection object.
    """
    with state._ws_lock:
        if ws in state._ws_clients:
            state._ws_clients.remove(ws)


def broadcast_ws(html: str) -> None:
    """Send HTML to all connected WebSocket clients.

    Args:
        html: HTML string to broadcast.
    """
    with state._ws_lock:
        for ws in list(state._ws_clients):
            try:
                ws.send(html)
            except Exception:
                try:
                    state._ws_clients.remove(ws)
                except ValueError:
                    pass


SKETCH_DIR = load_sketch_dir()
ALARM_HPP_PATH = _get_alarm_hpp_path()
