"""board_manager_client/python/board_manager_client/tests/test_pubsub_client.py

Tests for pubsub_client module.

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

import os
import socket
from unittest.mock import MagicMock, patch

import pytest
from board_manager_client.pubsub_client import PubSubClient


@pytest.fixture
def pubsub():
    client = PubSubClient(use_uds=False, tcp_host="127.0.0.1", tcp_port=9999)
    yield client
    client.disconnect()


class DummySocket:
    """Minimal socket-like object for connect/create_socket tests"""

    def __init__(self, family=socket.AF_INET):
        self.family = family
        self.closed = False
        self.connected = False
        self.fd = 123
        self.sent: list[bytes] = []

    def connect(self, address):
        if getattr(self, "_should_fail", False):
            raise ConnectionRefusedError("refused")
        self.connected = True

    def close(self):
        self.closed = True

    def settimeout(self, *args):
        pass

    def setsockopt(self, *args):
        pass

    def dup(self):
        return self

    def makefile(self, *args, **kwargs):
        return MagicMock()

    def detach(self):
        return self.fd

    def sendall(self, data: bytes):
        self.sent.append(data)

    @property
    def type(self):
        return socket.SOCK_STREAM


class TestPubSubClient:
    def test_initial_state(self, pubsub):
        assert pubsub._subscriptions == set()
        assert pubsub._handlers == {}
        assert pubsub._sock is None

    def test_subscribe_adds_topic(self, pubsub):
        def handler(m):
            return None

        pubsub.subscribe("board::+/event", handler)
        assert "board::+/event" in pubsub._subscriptions

    def test_unsubscribe_removes_topic(self, pubsub):
        def handler(m):
            return None

        pubsub.subscribe("test/topic", handler)
        pubsub.unsubscribe("test/topic")
        assert "test/topic" not in pubsub._subscriptions

    def test_subscribe_without_handler(self, pubsub):
        pubsub.subscribe("test/topic")
        assert "test/topic" in pubsub._subscriptions

    def test_publish_sends_message(self, pubsub):
        mock_sock = MagicMock()
        pubsub._sock = mock_sock
        pubsub.publish("test/topic", {"key": "value"})
        mock_sock.sendall.assert_called_once()
        sent = mock_sock.sendall.call_args[0][0]
        assert b'"topic":"test/topic"' in sent

    def test_publish_no_connection_does_not_crash(self, pubsub):
        pubsub._sock = None
        pubsub.publish("test/topic", {"key": "value"})

    def test_dispatch_calls_handler(self, pubsub):
        received = []
        pubsub.subscribe("test/topic", lambda m: received.append(m))
        pubsub._dispatch({"topic": "test/topic", "data": "hello"})
        assert len(received) == 1
        assert received[0]["data"] == "hello"

    def test_dispatch_wildcard_handler(self, pubsub):
        received = []
        pubsub.subscribe("test::*", lambda m: received.append(m))
        pubsub._dispatch({"topic": "test::foo", "data": "bar"})
        assert len(received) == 1
        assert received[0]["data"] == "bar"

    def test_dispatch_plus_wildcard(self, pubsub):
        received = []
        pubsub.subscribe("board::+::event", lambda m: received.append(m))
        pubsub._dispatch({"topic": "board::ttyACM0::event", "data": "x"})
        assert len(received) == 1

    def test_dispatch_error_handler_does_not_crash(self, pubsub):
        pubsub.subscribe("test/topic", lambda m: 1 / 0)
        pubsub._dispatch({"topic": "test/topic", "data": "crash"})

    def test_dispatch_resp_star_matches_double_colon(self, pubsub):
        received = []
        pubsub.subscribe("resp::*", lambda m: received.append(m))
        pubsub._dispatch({"topic": "resp::compile::/dev/ttyACM0", "status": "ok"})
        assert len(received) == 1

    def test_dispatch_resp_star_does_not_match_single_colon(self, pubsub):
        received = []
        pubsub.subscribe("resp::*", lambda m: received.append(m))
        pubsub._dispatch({"topic": "resp:compile:/dev/ttyACM0", "status": "ok"})
        assert len(received) == 0

    def test_dispatch_exact_topic_no_match(self, pubsub):
        received = []
        pubsub.subscribe("topic/one", lambda m: received.append(m))
        pubsub._dispatch({"topic": "topic/two"})
        assert len(received) == 0


class TestPubSubClientConnect:
    def test_connect_uds(self, tmp_path):
        socket_path = os.path.join(str(tmp_path), "uds.sock")
        open(socket_path, "w").close()

        def make_sock(family=socket.AF_INET, *args, **kwargs):
            return DummySocket(family=family)

        with patch("socket.socket", side_effect=make_sock):
            client = PubSubClient(use_uds=True, uds_path=socket_path)
            client.connect()
            assert client._sock is not None
            client.disconnect()

    def test_connect_tcp_fallback(self, tmp_path):
        socket_path = os.path.join(str(tmp_path), "missing.sock")
        uds_sock = DummySocket(family=socket.AF_UNIX)

        def make_sock(family=socket.AF_INET, *args, **kwargs):
            if family == socket.AF_UNIX:
                uds_sock._should_fail = True
                raise OSError("unix not available")
            return DummySocket(family=socket.AF_INET)

        with patch("socket.socket", side_effect=make_sock):
            client = PubSubClient(use_uds=True, uds_path=socket_path)
            client.connect()
            assert client._sock is not None
            client.disconnect()

    def test_resubscribe_on_connect(self, tmp_path):
        socket_path = os.path.join(str(tmp_path), "resub.sock")
        open(socket_path, "w").close()
        handler = MagicMock()

        def make_sock(family=socket.AF_INET, *args, **kwargs):
            return DummySocket(family=family)

        with patch("socket.socket", side_effect=make_sock):
            client = PubSubClient(use_uds=True, uds_path=socket_path)
            client.subscribe("test/topic", handler)
            client.connect()
            assert client._sock is not None
            client.disconnect()


class TestStaleUdsSocket:
    def test_stale_uds_unlinks_and_falls_back_to_tcp(self, tmp_path):
        socket_path = os.path.join(str(tmp_path), "stale.sock")
        open(socket_path, "w").close()
        connect_calls: list = []

        def make_sock(family=socket.AF_INET, *args, **kwargs):
            if family == socket.AF_UNIX:
                s = DummySocket(family=socket.AF_UNIX)

                def _connect(addr):
                    connect_calls.append(("uds", addr))
                    if len(connect_calls) == 1:
                        raise ConnectionRefusedError("stale socket")
                    s.connected = True

                s.connect = _connect
                return s
            s = DummySocket(family=socket.AF_INET)
            s.connect = lambda addr: connect_calls.append(("tcp", addr))
            return s

        with patch("socket.socket", side_effect=make_sock):
            client = PubSubClient(use_uds=True, uds_path=socket_path)
            client.connect()
            assert client._sock is not None
            assert os.path.exists(socket_path) is False
            client.disconnect()

    def test_stale_uds_unlink_fails_gracefully(self, tmp_path):
        socket_path = os.path.join(str(tmp_path), "missing.sock")
        connect_calls: list = []

        def make_sock(family=socket.AF_INET, *args, **kwargs):
            if family == socket.AF_UNIX:
                s = DummySocket(family=socket.AF_UNIX)

                def _connect(addr):
                    connect_calls.append(("uds", addr))
                    if len(connect_calls) == 1:
                        raise ConnectionRefusedError("stale socket")
                    s.connected = True

                s.connect = _connect
                return s
            s = DummySocket(family=socket.AF_INET)
            s.connect = lambda addr: connect_calls.append(("tcp", addr))
            return s

        with patch("socket.socket", side_effect=make_sock):
            client = PubSubClient(use_uds=True, uds_path=socket_path)
            client.connect()
            assert client._sock is not None
            client.disconnect()

    def test_stale_uds_retry_succeeds_if_new_socket_appears(self, tmp_path):
        socket_path = os.path.join(str(tmp_path), "appeared.sock")
        open(socket_path, "w").close()
        connect_count = [0]

        def make_sock(family=socket.AF_INET, *args, **kwargs):
            s = DummySocket(family=family)

            def _connect(addr):
                connect_count[0] += 1
                if connect_count[0] == 1:
                    raise ConnectionRefusedError("stale")
                s.connected = True

            s.connect = _connect
            return s

        with (
            patch("socket.socket", side_effect=make_sock),
            patch("os.unlink", side_effect=lambda p: os.remove(p)),
        ):
            client = PubSubClient(use_uds=True, uds_path=socket_path)
            client.connect()
            assert client._sock is not None
            client.disconnect()


class TestConnectRetry:
    def test_retry_succeeds_on_second_attempt(self):
        call_count = [0]

        def make_sock(family=socket.AF_INET, *args, **kwargs):
            call_count[0] += 1
            s = DummySocket()
            if call_count[0] == 1:

                def _connect_fail(addr):
                    raise ConnectionRefusedError("no")

                s.connect = _connect_fail
            return s

        with (
            patch("socket.socket", side_effect=make_sock),
            patch("time.sleep"),
        ):
            client = PubSubClient(use_uds=False, tcp_host="127.0.0.1", tcp_port=9999)
            client.connect(retry=True)
            assert client._sock is not None
            client.disconnect()

    def test_retry_all_fail_raises(self):
        def make_sock(*args, **kwargs):
            s = DummySocket()

            def _connect_fail(addr):
                raise ConnectionRefusedError("always")

            s.connect = _connect_fail
            return s

        with (
            patch("socket.socket", side_effect=make_sock),
            patch("time.sleep"),
            pytest.raises(ConnectionRefusedError),
        ):
            client = PubSubClient(use_uds=False, tcp_host="127.0.0.1", tcp_port=9999)
            client.connect(retry=True)

    def test_no_retry_connect_still_works(self):
        with patch("socket.socket", return_value=DummySocket()):
            client = PubSubClient(use_uds=False, tcp_host="127.0.0.1", tcp_port=9999)
            client.connect(retry=False)
            assert client._sock is not None
            client.disconnect()


class TestPubSubClientReconnect:
    def test_send_closes_socket_on_failure(self):
        mock_sock = MagicMock()
        mock_sock.sendall.side_effect = OSError("broken pipe")
        client = PubSubClient(use_uds=False, tcp_host="127.0.0.1", tcp_port=9999)
        client._sock = mock_sock
        client._running = True
        client._send({"type": "ping"})
        mock_sock.close.assert_called_once()
        assert client._sock is None

    def test_reconnect_delay_is_fixed(self):
        from board_manager_client.pubsub_client import ReconnectConfig

        assert ReconnectConfig.RECONNECT_DELAY == 2.0
