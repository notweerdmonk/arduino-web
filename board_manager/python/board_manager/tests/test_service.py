"""board_manager/python/board_manager/tests/test_service.py

Tests for service module.

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

import json
import socket
from unittest.mock import MagicMock, patch

import pytest

from board_manager.config import Config
from board_manager.daemon_manager import DaemonStartError
from board_manager.service import BoardManagerService, ClientConn
from board_manager.protocol import encode_and_frame


@pytest.fixture
def config():
    return Config(
        tcp_host="127.0.0.1",
        tcp_port=0,
        uds_path="/tmp/board_mgr_test.sock",
    )


@pytest.fixture
def mock_service(config):
    svc = BoardManagerService(config)
    svc._tcp_sock = MagicMock(spec=socket.socket)
    svc._uds_sock = MagicMock(spec=socket.socket)
    svc._running = True
    svc._read_list = [svc._tcp_sock, svc._uds_sock]
    return svc


class TestClientConn:
    def test_fileno(self):
        mock_sock = MagicMock(spec=socket.socket)
        mock_sock.fileno.return_value = 42
        conn = ClientConn(mock_sock, "test:1")
        assert conn.fileno() == 42

    def test_close(self):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "test:1")
        conn.close()
        mock_sock.close.assert_called_once()

    def test_default_framing(self):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "test:1")
        assert conn.framing_mode == "newline"
        assert conn.handshake_done is False


class TestMessageHandling:
    def test_handle_subscribe(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {"type": "subscribe", "topic": "board::+::event"}
        mock_service._handle_client_message(conn, msg)

        assert conn.addr in mock_service.router.subscribers_for("board::p1::event")
        mock_sock.sendall.assert_called_once()

    def test_handle_publish_unknown_topic(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {
            "type": "publish",
            "topic": "some::topic",
            "id": "r1",
            "reply_to": "resp::r1",
        }
        mock_service._handle_client_message(conn, msg)

        assert mock_sock.sendall.called

    def test_handle_publish_board_cmd(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {
            "type": "publish",
            "topic": "board::/dev/ttyACM0::cmd",
            "id": "r1",
            "reply_to": "resp::r1",
            "body": {"method": "ping", "params": {}},
        }
        with patch.object(mock_service.pool, "spawn") as mock_spawn:
            mock_service._handle_client_message(conn, msg)
            mock_spawn.assert_called_once_with("/dev/ttyACM0")

    def test_handle_publish_spawn_cmd(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {
            "type": "publish",
            "topic": "board::/dev/ttyACM0::cmd",
            "id": "r1",
            "reply_to": "resp::r1",
            "body": {"method": "spawn", "params": {}},
        }
        with patch.object(mock_service.pool, "spawn") as mock_spawn:
            mock_service._handle_client_message(conn, msg)
            mock_spawn.assert_called_once_with("/dev/ttyACM0")

    def test_handle_publish_status_cmd(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {
            "type": "publish",
            "topic": "board::/dev/ttyACM0::cmd",
            "id": "r1",
            "reply_to": "resp::r1",
            "body": {"method": "status", "params": {}},
        }
        mock_service._handle_client_message(conn, msg)
        assert mock_sock.sendall.called

    def test_handle_unsubscribe(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        mock_service.router.subscribe(conn.addr, "board::+::event")
        msg = {"type": "unsubscribe", "topic": "board::+::event"}
        mock_service._handle_client_message(conn, msg)

        assert conn.addr not in mock_service.router.subscribers_for("board::p1::event")

    def test_handle_health(self, mock_service, monkeypatch):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {
            "type": "publish",
            "topic": "sys::health",
            "id": "r1",
            "reply_to": "resp::r1",
            "body": {"method": "health", "params": {}},
        }
        mock_service._handle_client_message(conn, msg)

        send_data = mock_sock.sendall.call_args[0][0]
        assert b"running" in send_data

    def test_handle_remove(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        with patch.object(mock_service.pool, "remove") as mock_remove:
            msg = {
                "type": "publish",
                "topic": "board::/dev/ttyACM0::cmd",
                "id": "r1",
                "reply_to": "resp::r1",
                "body": {"method": "remove", "params": {}},
            }
            mock_service._handle_client_message(conn, msg)
            mock_remove.assert_called_once_with("/dev/ttyACM0")


class TestRoutePoolMessage:
    def test_routes_to_subscribed_client(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        mock_service.router.subscribe(conn.addr, "board::+::event")

        msg = {
            "type": "event",
            "topic": "board::/dev/ttyACM0::event",
            "data": {"event": "connected"},
        }
        mock_service._route_pool_message(
            "/dev/ttyACM0", msg, "board::/dev/ttyACM0::event"
        )

        mock_sock.sendall.assert_called_once()

    def test_no_subscribers_no_send(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {"type": "event", "topic": "board:/dev/ttyACM0/event", "data": {}}
        mock_service._route_pool_message(
            "/dev/ttyACM0", msg, "board:/dev/ttyACM0/event"
        )

        mock_sock.sendall.assert_not_called()

    def test_empty_topic_skipped(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg = {"type": "event", "topic": "", "data": {}}
        mock_service._route_pool_message("/dev/ttyACM0", msg, "")

        mock_sock.sendall.assert_not_called()


class TestClientLifecycle:
    def test_remove_client_unsubscribes(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        mock_sock.fileno.return_value = 42
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[42] = conn
        mock_service.router.subscribe("client:1", "board/+/event")

        mock_service._remove_client(conn)

        assert 42 not in mock_service._clients
        assert "client:1" not in mock_service.router.subscribers_for("board/p1/event")
        mock_sock.close.assert_called_once()


class TestSend:
    def test_send_newline_framed(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        conn.framing_mode = "newline"

        mock_service._send(conn, {"type": "ping"})

        sent_data = mock_sock.sendall.call_args[0][0]
        assert sent_data.endswith(b"\n")
        assert b"ping" in sent_data

    def test_send_error_removes_client(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        mock_sock.fileno.return_value = 42
        mock_sock.sendall.side_effect = ConnectionError("broken")
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[42] = conn

        mock_service._send(conn, {"type": "ping"})

        assert 42 not in mock_service._clients


class TestReadClient:
    def test_read_client_receives_message(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        mock_sock.fileno.return_value = 42
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[42] = conn

        msg = {"type": "subscribe", "topic": "test::+", "id": "r1"}
        mock_sock.recv.return_value = encode_and_frame(msg, "newline")

        mock_service._read_client(mock_sock)

        assert conn.addr in mock_service.router.subscribers_for("test::anything")

    def test_read_client_empty_data_disconnects(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        mock_sock.fileno.return_value = 42
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[42] = conn

        mock_sock.recv.return_value = b""

        mock_service._read_client(mock_sock)
        assert 42 not in mock_service._clients


class TestTick:
    """Tests for _tick method — specifically the pool.poll() message handling"""

    def test_tick_forwards_pool_messages(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msg_dict = {
            "type": "event",
            "topic": "board::/dev/ttyACM0::status",
            "data": {"progress": 42},
        }

        mock_service.pool.poll = MagicMock(return_value=[("/dev/ttyACM0", msg_dict)])

        with patch.object(mock_service, "_route_pool_message") as mock_route:
            with patch("select.select", return_value=([], [], [])):
                mock_service._tick()

            mock_route.assert_called_once_with(
                "/dev/ttyACM0", msg_dict, "board::/dev/ttyACM0::status"
            )

    def test_tick_forwards_multiple_pool_messages(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        msgs = [
            (
                "/dev/ttyACM0",
                {
                    "type": "event",
                    "topic": "board::p1::event",
                    "data": {"event": "connected"},
                },
            ),
            (
                "/dev/ttyACM0",
                {"type": "result", "topic": "resp::r1", "data": {"success": True}},
            ),
        ]

        mock_service.pool.poll = MagicMock(return_value=msgs)

        with patch.object(mock_service, "_route_pool_message") as mock_route:
            with patch("select.select", return_value=([], [], [])):
                mock_service._tick()

            assert mock_route.call_count == 2
            mock_route.assert_any_call("/dev/ttyACM0", msgs[0][1], "board::p1::event")
            mock_route.assert_any_call("/dev/ttyACM0", msgs[1][1], "resp::r1")

    def test_tick_handles_pool_messages_as_dict_not_iterable_keys(self, mock_service):
        """Regression: previously `for msg in msgs` iterated dict keys as strings.
        This test ensures a single dict from pool.poll() is treated as one message."""
        msg_dict = {"type": "result", "topic": "test::topic", "data": {}}

        mock_service.pool.poll = MagicMock(return_value=[("/dev/ttyACM0", msg_dict)])

        with patch.object(mock_service, "_route_pool_message") as mock_route:
            with patch("select.select", return_value=([], [], [])):
                mock_service._tick()

            mock_route.assert_called_once_with("/dev/ttyACM0", msg_dict, "test::topic")

    def test_tick_empty_pool_messages(self, mock_service):
        mock_service.pool.poll = MagicMock(return_value=[])

        with patch.object(mock_service, "_route_pool_message") as mock_route:
            with patch("select.select", return_value=([], [], [])):
                mock_service._tick()

            mock_route.assert_not_called()


class TestServiceStartStop:
    """Tests for service start/stop with DaemonManager integration"""

    @staticmethod
    def _mock_bindings(svc, monkeypatch):
        svc._tcp_sock = MagicMock(spec=socket.socket)
        svc._uds_sock = MagicMock(spec=socket.socket)
        svc._read_list = [svc._tcp_sock, svc._uds_sock]
        monkeypatch.setattr(svc, "_bind_tcp", MagicMock(return_value=svc._tcp_sock))
        monkeypatch.setattr(svc, "_bind_uds", MagicMock(return_value=svc._uds_sock))

    @patch("board_manager.service.DaemonManager")
    @patch("board_manager.service.BoardDetector")
    def test_start_creates_daemon_mgr(
        self, mock_board_detector, mock_daemon_mgr_cls, config, monkeypatch
    ):
        mock_daemon = MagicMock()
        mock_daemon_mgr_cls.return_value = mock_daemon
        svc = BoardManagerService(config)
        self._mock_bindings(svc, monkeypatch)

        with patch.object(svc, "_tick", side_effect=StopIteration):
            try:
                svc.start()
            except StopIteration:
                pass

        mock_daemon_mgr_cls.assert_called_once_with(
            binary=config.daemon_binary,
            daemon_addr=config.arduino_daemon,
        )
        mock_daemon.start.assert_called_once_with(timeout=15.0)

    @patch("board_manager.service.DaemonManager")
    @patch("board_manager.service.BoardDetector")
    def test_start_publishes_daemon_ready(
        self, mock_board_detector, mock_daemon_mgr_cls, config, monkeypatch
    ):
        mock_daemon = MagicMock()
        mock_daemon_mgr_cls.return_value = mock_daemon
        svc = BoardManagerService(config)
        self._mock_bindings(svc, monkeypatch)

        with patch.object(svc, "_publish_daemon_ready") as mock_publish:
            with patch.object(svc, "_tick", side_effect=StopIteration):
                try:
                    svc.start()
                except StopIteration:
                    pass
            mock_publish.assert_called_once()

    @patch("board_manager.service.DaemonManager")
    @patch("board_manager.service.BoardDetector")
    def test_start_daemon_failure_logs_warning(
        self, mock_board_detector, mock_daemon_mgr_cls, config, monkeypatch
    ):
        mock_daemon = MagicMock()
        mock_daemon_mgr_cls.return_value = mock_daemon
        mock_daemon.start.side_effect = DaemonStartError("port in use")
        svc = BoardManagerService(config)
        self._mock_bindings(svc, monkeypatch)

        with patch.object(svc, "_tick", side_effect=StopIteration):
            try:
                svc.start()
            except StopIteration:
                pass

        mock_board_detector.assert_called_once()

    @patch("board_manager.service.DaemonManager")
    @patch("board_manager.service.BoardDetector")
    def test_stop_calls_daemon_mgr_stop(
        self, mock_board_detector, mock_daemon_mgr_cls, config
    ):
        svc = BoardManagerService(config)
        mock_daemon = MagicMock()
        svc._daemon_mgr = mock_daemon
        svc._detector = MagicMock()
        svc.pool = MagicMock()

        svc.stop()

        mock_daemon.stop.assert_called_once()

    def test_publish_daemon_ready_sends_to_subscribers(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn
        mock_service.router.subscribe("client:1", "sys::daemon/ready")

        mock_service._publish_daemon_ready()

        send_data = mock_sock.sendall.call_args[0][0]
        assert b"sys::daemon/ready" in send_data
        assert b"event" in send_data

    def test_publish_daemon_ready_does_not_close_sockets(self, mock_service):
        mock_tcp = mock_service._tcp_sock
        mock_uds = mock_service._uds_sock

        mock_service._publish_daemon_ready()

        mock_tcp.close.assert_not_called()
        mock_uds.close.assert_not_called()

    def test_publish_daemon_ready_does_not_remove_clients(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        mock_sock.fileno.return_value = 99
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[99] = conn

        mock_service._publish_daemon_ready()

        assert 99 in mock_service._clients
        assert len(mock_service._clients) == 1


class TestDaemonStateReEmission:
    """Tests for Q8: BMS re-emits daemon state on subscribe"""

    def test_daemon_ready_flag_initially_false(self, mock_service):
        assert mock_service._daemon_ready is False

    def test_daemon_ready_flag_set_after_publish(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn
        mock_service.router.subscribe("client:1", "sys::daemon/ready")

        mock_service._publish_daemon_ready()

        assert mock_service._daemon_ready is True

    def test_send_daemon_state_to_sends_event_when_ready(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn
        mock_service.router.subscribe("client:1", "sys::daemon/ready")
        mock_service._daemon_ready = True

        mock_service._send_daemon_state_to(conn)

        send_data = mock_sock.sendall.call_args[0][0]
        assert b"sys::daemon/ready" in send_data
        assert b"event" in send_data

    def test_send_daemon_state_to_skips_when_not_ready(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn
        mock_service._daemon_ready = False

        mock_service._send_daemon_state_to(conn)

        mock_sock.sendall.assert_not_called()

    def test_send_daemon_state_to_skips_when_not_subscribed(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn
        mock_service._daemon_ready = True

        mock_service._send_daemon_state_to(conn)

        mock_sock.sendall.assert_not_called()

    def test_subscribe_triggers_daemon_state_re_emission(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        mock_service._daemon_ready = True

        msg = {"type": "subscribe", "topic": "sys::daemon/ready"}
        mock_service._handle_client_message(conn, msg)

        sendall_calls = mock_sock.sendall.call_args_list
        sent_all = b"".join(call[0][0] for call in sendall_calls)
        assert b"sys::daemon/ready" in sent_all

    def test_subscribe_does_not_re_emit_when_not_ready(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn

        mock_service._daemon_ready = False

        msg = {"type": "subscribe", "topic": "sys::daemon/ready"}
        mock_service._handle_client_message(conn, msg)

        sendall_calls = mock_sock.sendall.call_args_list
        assert len(sendall_calls) == 1
        sent = sendall_calls[0][0][0]
        parsed = json.loads(sent.decode())
        assert parsed["type"] == "result"
        assert parsed["topic"] == "sys::daemon/ready"

    def test_subscribe_twice_triggers_state_once(self, mock_service):
        mock_sock = MagicMock(spec=socket.socket)
        conn = ClientConn(mock_sock, "client:1")
        mock_service._clients[conn.fileno()] = conn
        mock_service.router.subscribe("client:1", "sys::daemon/ready")
        mock_service.router.subscribe("client:1", "board::+::event")

        mock_service._daemon_ready = True
        mock_service._board_state = {
            "/dev/ttyACM0": {
                "port": "/dev/ttyACM0",
                "board": "Arduino Uno",
                "fqbn": "arduino:avr:uno",
            }
        }

        msg1 = {"type": "subscribe", "topic": "sys::daemon/ready"}
        mock_service._handle_client_message(conn, msg1)

        msg2 = {"type": "subscribe", "topic": "board::+::event"}
        mock_service._handle_client_message(conn, msg2)

        sendall_calls = mock_sock.sendall.call_args_list
        parsed = [json.loads(call[0][0].decode()) for call in sendall_calls]
        daemon_events = [
            m
            for m in parsed
            if m.get("type") == "event" and m.get("topic") == "sys::daemon/ready"
        ]
        board_events = [
            m
            for m in parsed
            if m.get("type") == "event"
            and m.get("topic") == "board::/dev/ttyACM0::event"
        ]
        assert len(daemon_events) == 1, (
            f"Expected 1 daemon event, got {len(daemon_events)}: "
            f"{[m['topic'] for m in parsed if m.get('type') == 'event']}"
        )
        assert len(board_events) == 1, (
            f"Expected 1 board event, got {len(board_events)}: "
            f"{[m['topic'] for m in parsed if m.get('type') == 'event']}"
        )

