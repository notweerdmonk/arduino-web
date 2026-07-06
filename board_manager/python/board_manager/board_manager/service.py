"""board_manager/python/board_manager/board_manager/service.py

BoardManagerService — main event loop with TCP+UDS listener, pub/sub routing

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

import logging
import os
import select
import socket
from enum import Enum
from typing import Optional

from board_manager.board_detector import BoardDetector
from board_manager.config import Config
from board_manager.daemon_manager import DaemonManager, DaemonStartError
from board_manager.pool import BoardPool
from board_manager.protocol import (
    FrameReader,
    detect_mode_from_handshake,
    encode_and_frame,
)
from board_manager.router import TopicRouter

logger = logging.getLogger("board_manager")


class SysTopic(str, Enum):
    """System-level pub/sub topic constants."""

    DAEMON_READY = "sys::daemon/ready"


class ClientConn:
    """State container for a single TCP or UDS client connection."""

    def __init__(self, sock: socket.socket, addr: str):
        """Initialize a client connection container.

        Args:
            sock: The client socket.
            addr: Human-readable client address string.
        """
        self.sock = sock
        self.addr = addr
        self.reader = FrameReader("newline")
        self.framing_mode = "newline"
        self.handshake_done = False
        self.initial_state_sent = False

    def fileno(self) -> int:
        """Return the socket file descriptor number."""
        return self.sock.fileno()

    def close(self) -> None:
        """Close the client socket."""
        try:
            self.sock.close()
        except OSError:
            pass


class BoardManagerService:
    """Main service: TCP+UDS listener, message routing, subprocess management"""

    def __init__(self, config: Config):
        """Initialize the service with configuration.

        Args:
            config: Service configuration.
        """
        self.config = config
        self.pool = BoardPool()
        self.router = TopicRouter()
        self._clients: dict[int, ClientConn] = {}
        self._tcp_sock: Optional[socket.socket] = None
        self._uds_sock: Optional[socket.socket] = None
        self._running = False
        self._read_list: list = []
        self._detector: Optional[BoardDetector] = None
        self._daemon_mgr: Optional[DaemonManager] = None
        self._board_state: dict[str, dict] = {}
        self._daemon_ready: bool = False
        self._next_uds_id = 0

    def start(self) -> None:
        """Start the service: bind sockets, start daemon, start detector, and enter event loop."""
        self._tcp_sock = self._bind_tcp()
        self._uds_sock = self._bind_uds()
        self._running = True
        self._read_list = [self._tcp_sock, self._uds_sock]

        self._daemon_mgr = DaemonManager(
            binary=self.config.daemon_binary,
            daemon_addr=self.config.arduino_daemon,
        )
        try:
            self._daemon_mgr.start(timeout=15.0)
            self._publish_daemon_ready()
        except DaemonStartError as e:
            logger.error(
                "Failed to start arduino-cli daemon (binary=%s, addr=%s): %s",
                self.config.daemon_binary,
                self.config.arduino_daemon,
                e,
            )
            logger.warning("BoardDetector will retry daemon connection")

        self._detector = BoardDetector(
            callback=self._on_detector_event,
            daemon=self.config.arduino_daemon,
            daemon_manager=self._daemon_mgr,
            mode=self.config.board_detection_mode,
        )
        self._detector.start()

        logger.info(
            "BoardManagerService started on TCP %s:%d and UDS %s",
            self.config.tcp_host,
            self.config.tcp_port,
            self.config.uds_path,
        )

        while self._running:
            self._tick()

    def stop(self) -> None:
        """Stop the service and clean up all resources."""
        self._running = False
        if self._detector:
            self._detector.stop()
        self.pool.shutdown_all()
        if self._daemon_mgr:
            self._daemon_mgr.stop()

    def _publish_daemon_ready(self) -> None:
        """Publish a ``sys::daemon/ready`` event to subscribers."""
        self._daemon_ready = True
        msg = {"type": "event", "topic": SysTopic.DAEMON_READY, "data": {}}
        for addr in self.router.subscribers_for(SysTopic.DAEMON_READY):
            conn = self._find_client(addr)
            if conn:
                self._send(conn, msg)

    def _on_detector_event(self, port: str, msg: dict) -> None:
        """Handle a board connect/disconnect event from the detector.

        Args:
            port: The serial port address.
            msg: The event message dict.
        """
        topic = msg.get("topic", "")
        event = msg.get("data", {}).get("event", "")
        logger.debug("_on_detector_event: port=%s topic=%s event=%s", port, topic, event)
        if event == "connected":
            self._board_state[port] = msg.get("data", {})
        elif event == "disconnected":
            self._board_state.pop(port, None)
        self._route_pool_message(port, msg, topic)

    def _tick(self) -> None:
        """Single event loop iteration: accept connections and process I/O."""
        read_socks = self._read_list + [c.sock for c in self._clients.values()]

        try:
            readable, _, _ = select.select(read_socks, [], [], 0.1)
        except (ValueError, OSError):
            return

        for sock in readable:
            if sock is self._tcp_sock:
                self._accept_tcp()
            elif sock is self._uds_sock:
                self._accept_uds()
            else:
                self._read_client(sock)

        for port, msg in self.pool.poll(timeout=0):
            topic = msg.get("topic", "")
            self._route_pool_message(port, msg, topic)

    def _accept_tcp(self) -> None:
        """Accept a new TCP client connection and perform handshake."""
        try:
            client_sock, addr = self._tcp_sock.accept()
            client_sock.setblocking(True)
            conn = ClientConn(client_sock, f"tcp:{addr[0]}:{addr[1]}")
            reader = FrameReader("newline")
            data = client_sock.recv(1)
            if data:
                mode = detect_mode_from_handshake(data)
                if mode == "length":
                    conn.reader = FrameReader("length")
                    conn.framing_mode = "length"
                elif mode == "newline":
                    conn.reader = FrameReader("newline")
                    conn.framing_mode = "newline"
                else:
                    conn.reader = FrameReader("newline")
                    conn.framing_mode = "newline"
                    reader.feed(data)
                    while True:
                        msg = reader.read_one()
                        if msg:
                            self._handle_client_message(conn, msg)
                        else:
                            conn.reader.feed(data)
                            break
            conn.handshake_done = True
            self._clients[conn.fileno()] = conn
            logger.debug("Client connected: %s", conn.addr)
        except OSError as e:
            logger.error("Accept error: %s", e)

    def _accept_uds(self) -> None:
        """Accept a new UDS client connection."""
        try:
            client_sock, addr = self._uds_sock.accept()
            client_sock.setblocking(True)
            conn_id = self._next_uds_id
            self._next_uds_id += 1
            conn = ClientConn(client_sock, f"uds:{conn_id}")
            conn.handshake_done = True
            self._clients[conn.fileno()] = conn
            logger.debug("UDS client connected: %s", conn.addr)
        except OSError as e:
            logger.error("UDS accept error: %s", e)

    def _bind_tcp(self) -> socket.socket:
        """Create and bind the TCP listening socket.

        Returns:
            The bound listening socket.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config.tcp_host, self.config.tcp_port))
        sock.listen(10)
        sock.setblocking(True)
        return sock

    def _bind_uds(self) -> socket.socket:
        """Create and bind the UDS listening socket.

        Returns:
            The bound listening socket.
        """
        path = self.config.uds_path
        if os.path.exists(path):
            os.unlink(path)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(path)
        sock.listen(10)
        sock.setblocking(True)
        os.chmod(path, 0o666)
        return sock

    def _read_client(self, sock: socket.socket) -> None:
        """Read and process incoming data from a client socket.

        Args:
            sock: The client socket to read from.
        """
        conn = self._clients.get(sock.fileno())
        if conn is None:
            return
        try:
            data = sock.recv(65536)
        except (OSError, ConnectionError):
            self._remove_client(conn)
            return

        if not data:
            self._remove_client(conn)
            return

        conn.reader.feed(data)
        while True:
            msg = conn.reader.read_one()
            if msg is None:
                break
            self._handle_client_message(conn, msg)

    def _handle_client_message(self, conn: ClientConn, msg: dict) -> None:
        """Route a client message to the appropriate handler.

        Args:
            conn: The client connection.
            msg: The parsed message dict.
        """
        msg_type = msg.get("type", "")

        if msg_type == "subscribe":
            topics = msg.get("topics", [msg.get("topic", "")])
            for topic in topics:
                self.router.subscribe(conn.addr, topic)
            self._send(conn, {"type": "result", "status": "ok", "topic": msg.get("topic", "")})
            if not conn.initial_state_sent:
                self._send_current_boards_to(conn)
                self._send_daemon_state_to(conn)
                conn.initial_state_sent = True

        elif msg_type == "unsubscribe":
            topics = msg.get("topics", [msg.get("topic", "")])
            for topic in topics:
                self.router.unsubscribe(conn.addr, topic)
            self._send(conn, {"type": "result", "status": "ok", "topic": msg.get("topic", "")})

        elif msg_type == "publish":
            topic = msg.get("topic", "")
            body = msg.get("body", {})
            method = body.get("method", "")
            params = body.get("params", {})  # noqa: F841

            if topic.startswith("board::") and topic.endswith("::cmd"):
                port = topic[len("board::") : -len("::cmd")]
                self._handle_board_command(conn, port, msg)
            elif method == "list_all_boards":
                self._handle_list_all_boards(conn, msg)
            elif method == "list_boards":
                boards = list(self._detector.get_known_boards().values()) if self._detector else []
                self._send(
                    conn,
                    {
                        "type": "result",
                        "id": msg.get("id"),
                        "topic": msg.get("reply_to", ""),
                        "status": "ok",
                        "data": {"boards": boards},
                    },
                )
            elif method == "health":
                self._send(
                    conn,
                    {
                        "type": "result",
                        "id": msg.get("id"),
                        "topic": msg.get("reply_to", ""),
                        "status": "ok",
                        "data": {"status": "running"},
                    },
                )
            else:
                self._send(
                    conn,
                    {
                        "type": "result",
                        "id": msg.get("id"),
                        "topic": msg.get("reply_to", ""),
                        "status": "ok",
                        "data": {"ports": self.pool.list_ports()},
                    },
                )

        elif msg_type == "pong":
            pass

        else:
            logger.warning("Unknown message type from %s: %s", conn.addr, msg_type)

    def _handle_board_command(self, conn: ClientConn, port: str, msg: dict) -> None:
        """Handle a board-specific command (spawn, status, remove, or method dispatch).

        Args:
            conn: The client connection.
            port: The serial port address.
            msg: The command message dict.
        """
        method = (msg.get("body") or {}).get("method", "")
        logger.info("dispatching %s to port %s", method, port)

        if method == "spawn":
            try:
                self.pool.spawn(port)
                self._send(
                    conn,
                    {
                        "type": "result",
                        "id": msg.get("id"),
                        "topic": msg.get("reply_to", ""),
                        "status": "ok",
                    },
                )
            except RuntimeError as e:
                self._send(
                    conn,
                    {
                        "type": "error",
                        "id": msg.get("id"),
                        "code": "spawn_failed",
                        "message": str(e),
                    },
                )
            return

        if method == "status":
            status = self.pool.get_port_status(port)
            self._send(
                conn,
                {
                    "type": "result",
                    "id": msg.get("id"),
                    "topic": msg.get("reply_to", ""),
                    "status": "ok",
                    "data": status,
                },
            )
            return

        if method == "remove":
            self.pool.remove(port)
            self._send(
                conn,
                {
                    "type": "result",
                    "id": msg.get("id"),
                    "topic": msg.get("reply_to", ""),
                    "status": "ok",
                },
            )
            return

        bp = self.pool._boards.get(port)
        if bp is None:
            try:
                self.pool.spawn(port)
            except RuntimeError:
                self._send(
                    conn,
                    {
                        "type": "error",
                        "code": "spawn_failed",
                        "message": f"Cannot spawn worker for {port}",
                    },
                )
                return

        try:
            self.pool.dispatch(port, msg)
        except RuntimeError as e:
            self._send(
                conn,
                {
                    "type": "error",
                    "id": msg.get("id"),
                    "code": "dispatch_failed",
                    "message": str(e),
                },
            )

    def _handle_list_all_boards(self, conn: ClientConn, msg: dict) -> None:
        """Handle a list_all_boards request.

        Args:
            conn: The client connection.
            msg: The request message dict.
        """
        board_list = []
        for port in self.pool.list_ports():
            status = self.pool.get_port_status(port)
            board_list.append(status)
        self._send(
            conn,
            {
                "type": "result",
                "id": msg.get("id"),
                "topic": msg.get("reply_to", ""),
                "status": "ok",
                "data": {"boards": board_list, "ports": self.pool.list_ports()},
            },
        )

    def _route_pool_message(self, port: str, msg: dict, topic: str) -> None:
        """Route a message from a board worker to all matching subscribers.

        Args:
            port: The source serial port address.
            msg: The message dict to route.
            topic: The message topic.
        """
        if not topic:
            logger.debug("_route_pool_message: empty topic, skipping")
            return

        logger.info("routing %s from port %s", topic, port)

        is_result = not topic.endswith("::progress")
        if topic.startswith("resp::compile::") and is_result:
            extra = f" message={msg.get('message', '')}" if msg.get("status") == "error" else ""
            logger.info(
                "compile result for port %s: status=%s%s",
                port,
                msg.get("status", "?"),
                extra,
            )
        elif topic.startswith("resp::upload::") and is_result:
            extra = f" message={msg.get('message', '')}" if msg.get("status") == "error" else ""
            logger.info(
                "upload result for port %s: status=%s%s",
                port,
                msg.get("status", "?"),
                extra,
            )

        event_topic = f"board::{port}::event"
        status_topic = f"board::{port}::status"

        sub_ids = self.router.subscribers_for(topic)
        sub_ids.update(self.router.subscribers_for(event_topic))
        sub_ids.update(self.router.subscribers_for(status_topic))

        logger.debug("_route_pool_message: port=%s topic=%s sub_ids=%s", port, topic, sub_ids)

        if not sub_ids:
            logger.debug(
                "_route_pool_message: no subscribers for topic '%s' (patterns: %s)",
                topic,
                self.router.patterns,
            )

        for addr in sub_ids:
            conn = self._find_client(addr)
            if conn:
                logger.debug("_route_pool_message: sending to %s", addr)
                self._send(conn, msg)
            else:
                logger.debug(
                    "_route_pool_message: subscriber '%s' not found in _clients (keys: %s)",
                    addr,
                    list(self._clients.keys()),
                )

    def _send_current_boards_to(self, conn: ClientConn) -> None:
        """Send current board state as synthetic ``connected`` events to a subscriber.

        Args:
            conn: The client connection to send to.
        """
        if not self._board_state:
            logger.debug("_send_current_boards_to: no boards in state")
            return
        for port, data in self._board_state.items():
            synthetic = {
                "type": "event",
                "topic": f"board::{port}::event",
                "data": {
                    "event": "connected",
                    "port": data.get("port", port),
                    "board": data.get("board", ""),
                    "fqbn": data.get("fqbn", ""),
                },
            }
            event_topic = f"board::{port}::event"
            status_topic = f"board::{port}::status"
            sub_ids = self.router.subscribers_for(synthetic["topic"])
            sub_ids.update(self.router.subscribers_for(event_topic))
            sub_ids.update(self.router.subscribers_for(status_topic))
            if conn.addr in sub_ids:
                logger.debug(
                    "_send_current_boards_to: sending synthetic 'connected' for %s",
                    port,
                )
                self._send(conn, synthetic)

    def _send_daemon_state_to(self, conn: ClientConn) -> None:
        """Send current daemon state as synthetic event to a subscriber.

        Args:
            conn: The client connection to send to.
        """
        if not self._daemon_ready:
            return
        sub_ids = self.router.subscribers_for(SysTopic.DAEMON_READY)
        if conn.addr in sub_ids:
            self._send(
                conn,
                {
                    "type": "event",
                    "topic": SysTopic.DAEMON_READY,
                    "data": {},
                },
            )

    def _find_client(self, addr: str) -> Optional[ClientConn]:
        """Find a client connection by its address string.

        Args:
            addr: The client address string.

        Returns:
            The ClientConn, or None if not found.
        """
        logger.debug(
            "_find_client: looking for addr='%s' among %d clients",
            addr,
            len(self._clients),
        )
        for conn in self._clients.values():
            if conn.addr == addr:
                logger.debug(
                    "_find_client: found conn addr='%s' fileno=%d",
                    conn.addr,
                    conn.fileno(),
                )
                return conn
        logger.debug(
            "_find_client: addr='%s' NOT FOUND. Known addrs: %s",
            addr,
            [c.addr for c in self._clients.values()],
        )
        return None

    def _send(self, conn: ClientConn, msg: dict) -> None:
        """Encode, frame, and send a message to a client connection.

        Args:
            conn: The client connection.
            msg: The message dict to send.
        """
        try:
            data = encode_and_frame(msg, conn.framing_mode)
            conn.sock.sendall(data)
        except (OSError, ConnectionError) as e:
            logger.debug("Send error to %s: %s", conn.addr, e)
            self._remove_client(conn)

    def _remove_client(self, conn: ClientConn) -> None:
        """Remove a client connection, unsubscribe, and clean up.

        Args:
            conn: The client connection to remove.
        """
        self.router.unsubscribe_all(conn.addr)
        self._clients.pop(conn.fileno(), None)
        conn.close()
        logger.debug("Client disconnected: %s", conn.addr)
