"""arduino_dash/python/arduino_dash/arduino_dash/pubsub.py

Infrastructure functions — pubsub init, response handling, board events, WebSocket broadcast

Author: notweerdmonk
SPDX-License-Identifier: Apache-2.0

Copyright 2026 notweerdmonk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import glob
import logging
import os
import threading
import time
from enum import Enum

from board_manager_client.pubsub_client import PubSubClient

from arduino_dash import state


class PubSubTopic(str, Enum):
    """PubSub topic constants used by the application."""

    DAEMON_READY = "sys::daemon/ready"
    BOARD_EVENT = "board::+::event"
    RESP = "resp::*"
    HEALTH = "sys::health"
    RESP_COMPILE = "resp::compile::*"
    RESP_UPLOAD = "resp::upload::*"


_logger = logging.getLogger(__name__)


def _start_fallback_scanner(ps: PubSubClient) -> None:
    """Start the background thread that polls for board connections via glob."""
    state._stop_fallback_scan = False
    state._fallback_scanner = threading.Thread(target=_fallback_scan_loop, args=(ps,), daemon=True)
    state._fallback_scanner.start()
    state.logger.info("Fallback board scanner started (every %.1fs)", state._fallback_scan_interval)


def _stop_fallback_scanner() -> None:
    """Signal the fallback scanner thread to stop."""
    state._stop_fallback_scan = True
    state.logger.info("Fallback board scanner stopped")


def _fallback_scan_loop(ps: PubSubClient) -> None:
    """Poll for boards via glob patterns and emit connect/disconnect events."""
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
            with state._board_list_lock:
                before = set(state._board_list.keys())
            added = found - before
            removed = {p for p in before if p.startswith("/dev/tty")} - found
            for port in removed:
                state.logger.info("Fallback: board disconnected at %s", port)
                _on_board_event(
                    {
                        "data": {
                            "port": port,
                            "event": "disconnected",
                            "board": state._board_list.get(port, {}).get("board", ""),
                            "fqbn": state._board_list.get(port, {}).get("fqbn", ""),
                        }
                    }
                )
            for port in sorted(added):
                state.logger.info("Fallback: board connected at %s", port)
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
            state.logger.exception("Fallback scanner error")
        time.sleep(state._fallback_scan_interval)


def _resolve_board_info(port: str) -> dict:
    """Resolve board metadata (name, fqbn, hardware_id) via the gRPC client."""
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
        state.logger.debug("_resolve_board_info: failed for %s", port, exc_info=True)
    return {"board": "", "fqbn": "", "hardware_id": ""}


def init_pubsub(
    use_uds: bool = True,
    tcp_host: str = "127.0.0.1",
    tcp_port: int = 9090,
    uds_path: str = "/tmp/board_mgr.sock",
):
    """Connect PubSub to BoardManagerService and subscribe to all topics."""
    state.pubsub = PubSubClient(
        tcp_host=tcp_host,
        tcp_port=tcp_port,
        uds_path=uds_path,
        use_uds=use_uds,
    )
    state.pubsub.on_reconnect = _on_pubsub_reconnect
    try:
        state.pubsub.connect(retry=True)
    except (ConnectionError, OSError) as e:
        state.logger.warning("Could not connect to BoardManagerService: %s", e)
    state.pubsub.subscribe(PubSubTopic.DAEMON_READY, _on_daemon_ready)
    state.pubsub.subscribe(PubSubTopic.BOARD_EVENT, _on_board_event)
    state.pubsub.subscribe(PubSubTopic.RESP, _on_resp)
    state.pubsub.subscribe(PubSubTopic.HEALTH, _on_health)
    tools = state._app.extensions.get("arduino_sketch_tools")
    if tools:
        tools.pubsub = state.pubsub
        state.pubsub.subscribe(PubSubTopic.RESP_COMPILE, tools._on_compile_resp)
        state.pubsub.subscribe(PubSubTopic.RESP_UPLOAD, tools._on_upload_resp)
    state.pubsub.start_reader()


def _on_daemon_ready(msg: dict) -> None:
    """Handle the daemon ready event by setting the daemon ready flag."""
    if msg.get("type") != "event":
        return
    with state._daemon_ready_lock:
        if state._daemon_ready:
            return
        state._daemon_ready = True
    state.logger.info("Daemon ready event received")
    _broadcast_daemon_badge()


def _on_pubsub_reconnect() -> None:
    """Re-register all PubSub subscriptions after a reconnection."""
    with state._daemon_ready_lock:
        state._daemon_ready = False
    _broadcast_daemon_badge()
    ps = state.pubsub
    if not ps:
        return
    ps.subscribe(PubSubTopic.DAEMON_READY, _on_daemon_ready)
    ps.subscribe(PubSubTopic.BOARD_EVENT, _on_board_event)
    ps.subscribe(PubSubTopic.RESP, _on_resp)
    ps.subscribe(PubSubTopic.HEALTH, _on_health)
    tools = state._app.extensions.get("arduino_sketch_tools") if state._app else None
    if tools:
        tools.pubsub = ps
        ps.subscribe(PubSubTopic.RESP_COMPILE, tools._on_compile_resp)
        ps.subscribe(PubSubTopic.RESP_UPLOAD, tools._on_upload_resp)
    state.logger.info("PubSub reconnected — all handlers re-registered")


def _on_board_event(msg: dict) -> None:
    """Handle board connect/disconnect events and broadcast them via WebSocket."""
    data = msg.get("data", {})
    event = data.get("event", "")
    port = data.get("port", "")
    state.logger.debug("_on_board_event: event=%s port=%s data=%s", event, port, data)
    with state._board_list_lock:
        if event == "connected":
            if port in state._board_list:
                return
            state._board_list[port] = data
            state.logger.debug(
                "Board added to _board_list: %s (total: %d)",
                port,
                len(state._board_list),
            )
        elif event == "disconnected":
            if port not in state._board_list:
                return
            state._board_list.pop(port, None)
            with state._last_compiled_sketch_lock:
                state._last_compiled_sketch.pop(port, None)
            with state._last_compile_mtime_lock:
                state._last_compile_mtime.pop(port, None)
            if state._app and "arduino_sketch_tools" in state._app.extensions:
                tools = state._app.extensions["arduino_sketch_tools"]
                with tools._last_compiled_sketch_lock:
                    tools._last_compiled_sketch.pop(port, None)
                with tools._last_compile_mtime_lock:
                    tools._last_compile_mtime.pop(port, None)
                with tools._last_compile_checksum_lock:
                    tools._last_compile_checksum.pop(port, None)
                with tools._last_uploaded_sketch_lock:
                    tools._last_uploaded_sketch.pop(port, None)
            state.logger.debug(
                "Board removed from _board_list: %s (total: %d)",
                port,
                len(state._board_list),
            )
        else:
            state.logger.debug("Unknown event type: '%s' — skipping _board_list update", event)
    try:
        from flask import render_template

        with state._app.app_context():
            event_html = (
                '<div hx-swap-oob="afterbegin:#live-events-card" data-event-port="'
                + port
                + '">'
                + render_template("partials/board_event.html", events=[data])
                + "</div>"
            )
        _broadcast_ws(event_html)
        port_safe = port.replace("/", "_")
        connected = event == "connected"
        badge = render_template(
            "partials/board_status_badge.html",
            port=port,
            port_path=port.lstrip("/"),
            connected=connected,
        )
        oob = f'<span id="board-status-badge--{port_safe}" hx-swap-oob="true">{badge}</span>'
        _broadcast_ws(oob)
    except Exception:
        state.logger.exception("Failed to broadcast board event")
    with state._board_events_lock:
        state._board_events.insert(0, data)
        if len(state._board_events) > 100:
            state._board_events.pop()


def _on_health(msg: dict) -> None:
    """Handle health check messages (no-op)."""
    pass


def _on_resp(msg: dict) -> None:
    """Handle response messages and wake waiting callers."""
    topic = msg.get("topic", "")
    state.logger.debug("_on_resp: topic=%s (compile/upload handled by extension)", topic)

    with state._pending_responses_lock:
        entry = state._pending_responses.get(topic)
    if entry is not None:
        result, event = entry
        if not event.is_set():
            state._pending_responses[topic] = (msg, event)
            event.set()
    else:
        state.logger.debug("_on_resp: no pending waiter for topic '%s'", topic)


def _wait_for_response(topic: str, timeout: float = 60.0) -> dict | None:
    """Wait for a response on the given topic with a timeout."""
    event = threading.Event()
    with state._pending_responses_lock:
        state._pending_responses[topic] = (None, event)
    try:
        if event.wait(timeout):
            with state._pending_responses_lock:
                result, _ = state._pending_responses.pop(topic, (None, None))
            return result
        state.logger.warning("Response timeout for topic '%s'", topic)
        return None
    finally:
        with state._pending_responses_lock:
            state._pending_responses.pop(topic, None)


def _compute_sketch_checksum(sketch_dir: str) -> str:
    """Compute a SHA-256 checksum over source files in a sketch directory."""
    if not os.path.isdir(sketch_dir):
        return ""
    import hashlib

    hasher = hashlib.sha256()
    file_paths = []
    for root, _dirs, files in os.walk(sketch_dir):
        for f in files:
            if f.endswith((".ino", ".cpp", ".h", ".hpp", ".c")):
                file_paths.append(os.path.join(root, f))
    file_paths.sort()
    for fp in file_paths:
        try:
            with open(fp, "rb") as fh:
                while True:
                    chunk = fh.read(65536)
                    if not chunk:
                        break
                    hasher.update(chunk)
        except OSError:
            continue
    if not file_paths:
        return ""
    return hasher.hexdigest()


def _get_sketch_mtime(sketch_path: str) -> float | None:
    """Return the latest modification time among source files in a sketch directory."""
    if not os.path.isdir(sketch_path):
        return None
    max_mtime: float | None = None
    for root, _dirs, files in os.walk(sketch_path):
        for f in files:
            if f.endswith((".ino", ".cpp", ".h", ".hpp", ".c")):
                try:
                    mtime = os.path.getmtime(os.path.join(root, f))
                    if max_mtime is None or mtime > max_mtime:
                        max_mtime = mtime
                except OSError:
                    continue
    return max_mtime


def _make_meta(port: str, sketch_path: str) -> dict:
    """Build a metadata dict for a compile or upload operation."""
    board_info = {}
    with state._board_list_lock:
        if port in state._board_list:
            board_info = state._board_list[port]
    utils_dir = os.path.basename(os.path.normpath(sketch_path)) if sketch_path else ""
    return {
        "port": port,
        "board": board_info.get("board", ""),
        "fqbn": board_info.get("fqbn", ""),
        "hardware_id": board_info.get("hardware_id", ""),
        "sketch": sketch_path,
        "sketch_name": utils_dir,
    }


def _broadcast_daemon_badge() -> None:
    """Broadcast daemon badge OOB update via WebSocket."""
    try:
        from flask import render_template

        with state._daemon_ready_lock:
            ready = state._daemon_ready
        with state._app.app_context():
            badge = render_template("partials/daemon_badge.html", ready=ready)
        oob = f'<span id="daemon-badge" hx-swap-oob="true">{badge}</span>'
        _broadcast_ws(oob)
    except Exception:
        state.logger.exception("Failed to broadcast daemon badge")


def _broadcast_ws(html: str) -> None:
    """Send HTML to all connected WebSocket clients."""
    with state._ws_lock:
        for ws in list(state._ws_clients):
            try:
                ws.send(html)
            except Exception:
                try:
                    state._ws_clients.remove(ws)
                except ValueError:
                    pass
