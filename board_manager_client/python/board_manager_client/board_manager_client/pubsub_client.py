"""Persistent PubSub client for BoardManagerService with auto-reconnect"""

import logging
import os
import select
import socket
import threading
import time
from typing import Callable, Optional

OnReconnect = Callable[[], None]

logger = logging.getLogger("board_manager_client")

from board_manager.protocol import (  # noqa: E402
    FrameReader,
    Handshake,
    encode_and_frame,
)
from board_manager.router import _match  # noqa: E402

EventHandler = Callable[[dict], None]


class ReconnectConfig:
    """Reconnection timing configuration."""

    RECONNECT_DELAY: float = 2.0
    CONNECT_RETRY_DELAYS: list[float] = [0.5, 1.0, 2.0]


class PubSubClient:
    """Persistent PubSub connection to BoardManagerService

    Connects to TCP or UDS, auto-reconnects with exponential backoff,
    maintains subscriptions across reconnects.
    """

    def __init__(
        self,
        tcp_host: str = "127.0.0.1",
        tcp_port: int = 9090,
        uds_path: str = "/tmp/board_mgr.sock",
        use_uds: bool = True,
        on_reconnect: Optional[OnReconnect] = None,
    ):
        """Initialize the PubSub client.

        Args:
            tcp_host: TCP hostname for fallback connection.
            tcp_port: TCP port for fallback connection.
            uds_path: Path to the Unix domain socket.
            use_uds: Whether to attempt UDS connection first.
            on_reconnect: Optional callback invoked after each reconnect.
        """
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.uds_path = uds_path
        self.use_uds = use_uds
        self._sock: Optional[socket.socket] = None
        self._reader = FrameReader("newline")
        self._subscriptions: set[str] = set()
        self._handlers: dict[str, list[EventHandler]] = {}
        self._running = False
        self._reader_thread: Optional[threading.Thread] = None
        self._reconnect_count = 0
        self._lock = threading.Lock()
        self._pending_responses: dict[str, tuple[dict, threading.Event]] = {}
        self._resp_lock = threading.Lock()
        self.on_reconnect = on_reconnect

    def connect(self, retry: bool = False) -> None:
        """Connect to the BoardManagerService.

        Args:
            retry: If True, retry with delays from CONNECT_RETRY_DELAYS on failure.

        Raises:
            ConnectionError: If all connection attempts fail.
            OSError: On socket-level errors.
        """
        if retry:
            last_error: Optional[Exception] = None
            for attempt, delay in enumerate(ReconnectConfig.CONNECT_RETRY_DELAYS):
                try:
                    self._connect_once()
                    logger.info(
                        "Connected to BoardManagerService (mode: %s)",
                        "UDS"
                        if self.use_uds
                        and self._sock
                        and self._sock.family == socket.AF_UNIX
                        else "TCP",
                    )
                    return
                except (ConnectionError, OSError) as e:
                    last_error = e
                    logger.warning(
                        "Connect attempt %d/%d failed: %s, retrying in %.1fs...",
                        attempt + 1,
                        len(ReconnectConfig.CONNECT_RETRY_DELAYS),
                        e,
                        delay,
                    )
                    time.sleep(delay)
            logger.error("All connect attempts failed: %s", last_error)
            raise last_error  # type: ignore[misc]
        self._connect_once()
        logger.info(
            "Connected to BoardManagerService (mode: %s)",
            "UDS"
            if self.use_uds and self._sock and self._sock.family == socket.AF_UNIX
            else "TCP",
        )

    def _connect_once(self) -> None:
        """Perform a single connection attempt, including handshake and resubscribe."""
        self._sock = self._create_socket()
        self._send_handshake()
        self._resubscribe()
        self._reconnect_count = 0
        if self.on_reconnect:
            self.on_reconnect()

    def _create_socket(self) -> socket.socket:
        """Create and connect a socket (UDS preferred, TCP fallback).

        Returns:
            A connected socket object.

        Raises:
            ConnectionError: If all transport options fail.
        """
        if self.use_uds and os.path.exists(self.uds_path):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                sock.connect(self.uds_path)
            except ConnectionRefusedError:
                logger.warning("Stale UDS socket at %s, cleaning up", self.uds_path)
                try:
                    os.unlink(self.uds_path)
                except OSError:
                    pass
                sock.close()
                if os.path.exists(self.uds_path):
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.connect(self.uds_path)
                    self._reader = FrameReader("newline")
                    return sock
                logger.warning("UDS socket cleaned, falling back to TCP")
            else:
                self._reader = FrameReader("newline")
                return sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.tcp_host, self.tcp_port))
        self._reader = FrameReader("newline")
        return sock

    def _send_handshake(self) -> None:
        """Send the initial handshake if using TCP transport."""
        if not self.use_uds or not os.path.exists(self.uds_path):
            self._sock.sendall(Handshake.NEWLINE.value)

    @property
    def is_connected(self) -> bool:
        """Whether the client currently has an open socket."""
        return self._sock is not None

    def disconnect(self) -> None:
        """Disconnect from the service and close the socket."""
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def subscribe(self, topic: str, handler: Optional[EventHandler] = None) -> None:
        """Subscribe to a topic, optionally registering a handler.

        Args:
            topic: Topic pattern to subscribe to.
            handler: Optional callback invoked on matching messages.
        """
        with self._lock:
            is_new = topic not in self._subscriptions
            self._subscriptions.add(topic)
            if handler:
                hlist = self._handlers.setdefault(topic, [])
                if handler not in hlist:
                    hlist.append(handler)
        if self._sock and is_new:
            self._send({"type": "subscribe", "topic": topic})

    def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from a topic and remove its handlers.

        Args:
            topic: Topic pattern to unsubscribe from.
        """
        with self._lock:
            self._subscriptions.discard(topic)
            self._handlers.pop(topic, None)
        if self._sock:
            self._send({"type": "unsubscribe", "topic": topic})

    def request_boards(self, timeout: float = 10.0) -> list[dict] | None:
        """Request the list of boards and wait for the response.

        Args:
            timeout: Maximum seconds to wait for a response.

        Returns:
            List of board dicts, or None if the request timed out.
        """
        resp_topic = f"resp::list_boards::{id(self)}::{time.monotonic_ns()}"
        event = threading.Event()
        with self._resp_lock:
            self._pending_responses[resp_topic] = (None, event)
        self.subscribe(resp_topic, lambda msg: self._on_response(resp_topic, msg))
        self.publish("sys::boards", {"method": "list_boards"}, reply_to=resp_topic)
        if event.wait(timeout):
            with self._resp_lock:
                result, _ = self._pending_responses.pop(resp_topic, (None, None))
            return result.get("data", {}).get("boards", []) if result else None
        with self._resp_lock:
            self._pending_responses.pop(resp_topic, None)
        self.unsubscribe(resp_topic)
        return None

    def _on_response(self, topic: str, msg: dict) -> None:
        """Store a response message and signal the waiting caller.

        Args:
            topic: Response topic.
            msg: Response message dict.
        """
        with self._resp_lock:
            entry = self._pending_responses.get(topic)
        if entry is not None:
            result, event = entry
            if not event.is_set():
                with self._resp_lock:
                    self._pending_responses[topic] = (msg, event)
                event.set()

    def publish(self, topic: str, message: dict, reply_to: str = "") -> None:
        """Publish a message on a topic.

        Args:
            topic: Topic to publish on.
            message: Message payload dict.
            reply_to: Optional response topic for subscribers.
        """
        self._send(
            {
                "type": "publish",
                "topic": topic,
                "body": message,
                "reply_to": reply_to,
            }
        )

    def _send(self, msg: dict) -> None:
        """Send a framed message over the socket.

        Args:
            msg: Message dict to encode and send.
        """
        if not self._sock:
            return
        try:
            self._sock.sendall(encode_and_frame(msg, "newline"))
        except (OSError, ConnectionError) as e:
            logger.warning("Send failed: %s", e)
            if self._sock:
                try:
                    self._sock.close()
                except OSError:
                    pass
                self._sock = None

    def _resubscribe(self) -> None:
        """Re-send all subscription requests after reconnection."""
        with self._lock:
            topics = list(self._subscriptions)
        for topic in topics:
            self._send({"type": "subscribe", "topic": topic})

    def start_reader(self) -> None:
        """Start the background reader thread to process incoming messages."""
        self._running = True
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def _read_loop(self) -> None:
        """Continuously read and dispatch messages from the socket, reconnecting on error."""
        while self._running:
            if not self._sock:
                logger.debug("_read_loop: no socket, reconnecting")
                self._reconnect()
                time.sleep(0.1)
                continue
            try:
                sock = self._sock
                ready, _, _ = select.select([sock], [], [], 1.0)
                if not ready:
                    continue
                data = sock.recv(65536)
            except (
                OSError,
                ConnectionError,
                ValueError,
                TypeError,
                AttributeError,
            ) as e:
                if self._running:
                    logger.warning("Connection lost (%s), reconnecting...", e)
                    self._reconnect()
                continue

            if not data:
                if self._running:
                    logger.warning("Connection closed (empty recv), reconnecting...")
                    self._reconnect()
                continue

            logger.debug("_read_loop: received %d bytes", len(data))
            try:
                self._reader.feed(data)
                while True:
                    msg = self._reader.read_one()
                    if msg is None:
                        break
                    logger.debug(
                        "_read_loop: dispatching msg with topic='%s'",
                        msg.get("topic", ""),
                    )
                    self._dispatch(msg)
            except Exception as e:
                logger.error("_read_loop: error processing message (%s), skipping", e)

    def _dispatch(self, msg: dict) -> None:
        """Dispatch a message to all matching handlers.

        Args:
            msg: Message dict to dispatch.
        """
        topic = msg.get("topic", "")
        with self._lock:
            matched: list[EventHandler] = []
            for pattern, hlist in self._handlers.items():
                if pattern == "*" or _match(topic, pattern):
                    logger.debug(
                        "_dispatch: topic '%s' matched pattern '%s' (%d handlers)",
                        topic,
                        pattern,
                        len(hlist),
                    )
                    matched.extend(hlist)
        if not matched:
            logger.debug(
                "_dispatch: topic '%s' matched NO patterns (known patterns: %s)",
                topic,
                list(self._handlers.keys()),
            )
        for h in matched:
            try:
                h(msg)
            except Exception as e:
                logger.error("Handler error: %s", e)

    def _reconnect(self) -> None:
        """Close the current socket, wait, and attempt a new connection."""
        self._reconnect_count += 1
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        time.sleep(ReconnectConfig.RECONNECT_DELAY)
        try:
            self.connect()
        except (ConnectionError, OSError) as e:
            logger.warning(
                "Reconnect failed (%s), retrying in %.1fs...",
                e,
                ReconnectConfig.RECONNECT_DELAY,
            )
