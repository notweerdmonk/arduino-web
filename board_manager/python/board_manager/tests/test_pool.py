"""board_manager/python/board_manager/tests/test_pool.py

Tests for pool module.

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

import socket
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from board_manager.pool import BoardPool, PoolLimits
from board_manager.protocol import encode_and_frame


class FakePopen:
    """Minimal mock for subprocess.Popen"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.returncode = None
        self._poll_count = 0

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self.returncode = 0
        return 0

    def send_signal(self, sig):
        pass

    def kill(self):
        pass


@pytest.fixture
def pool():
    p = BoardPool()
    yield p
    p.shutdown_all()


class TestBoardPoolSpawn:
    def test_spawn_creates_worker(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            bp = pool.spawn("/dev/ttyACM0")

            assert bp.port == "/dev/ttyACM0"
            assert bp.parent_sock is parent_sock
            assert bp.restart_count == 0
            assert "/dev/ttyACM0" in pool._boards

    def test_spawn_twice_raises(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent = MagicMock(spec=socket.socket)
            child = MagicMock(spec=socket.socket)
            child.fileno.return_value = 5
            mock_sp.return_value = (parent, child)

            pool.spawn("/dev/ttyACM0")

            with pytest.raises(RuntimeError, match="already running"):
                pool.spawn("/dev/ttyACM0")

    def test_spawn_exceeded_restarts(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent = MagicMock(spec=socket.socket)
            child = MagicMock(spec=socket.socket)
            child.fileno.return_value = 5
            mock_sp.return_value = (parent, child)

            bp = pool.spawn("/dev/ttyACM0")
            bp.restart_count = PoolLimits.MAX_RESTARTS
            bp.proc = None

            with pytest.raises(RuntimeError, match="exceeded max restarts"):
                pool.spawn("/dev/ttyACM0")


class TestBoardPoolDispatch:
    def test_dispatch_sends_message(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            pool.spawn("/dev/ttyACM0")
            msg = {"type": "publish", "body": {"method": "ping"}}
            pool.dispatch("/dev/ttyACM0", msg)

            expected = encode_and_frame(msg, "newline")
            parent_sock.sendall.assert_called_once_with(expected)

    def test_dispatch_no_worker_raises(self, pool):
        with pytest.raises(RuntimeError, match="No worker"):
            pool.dispatch("/dev/ttyACM0", {"type": "ping"})

    def test_dispatch_send_failure_raises(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            pool.spawn("/dev/ttyACM0")
            parent_sock.sendall.side_effect = OSError("broken pipe")

            with pytest.raises(RuntimeError, match="Failed to send"):
                pool.dispatch("/dev/ttyACM0", {"type": "ping"})


class TestBoardPoolPoll:
    def test_poll_returns_messages(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            pool.spawn("/dev/ttyACM0")

            msg_data = encode_and_frame(
                {"type": "result", "topic": "resp:1", "status": "ok"}, "newline"
            )
            parent_sock.recv.return_value = msg_data

            with patch("board_manager.pool.select.select") as mock_select:
                mock_select.return_value = ([parent_sock], [], [])
                results = pool.poll(timeout=0.1)

            assert len(results) == 1
            port, msg = results[0]
            assert port == "/dev/ttyACM0"
            assert msg["status"] == "ok"

    def test_poll_empty_pool(self, pool):
        results = pool.poll(timeout=0)
        assert results == []

    def test_poll_detects_worker_ready(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            bp = pool.spawn("/dev/ttyACM0")
            assert bp.ready is False

            ready_msg = encode_and_frame(
                {"type": "event", "topic": "worker/ready", "data": {}}, "newline"
            )
            parent_sock.recv.return_value = ready_msg

            with patch("board_manager.pool.select.select") as mock_select:
                mock_select.return_value = ([parent_sock], [], [])
                pool.poll(timeout=0.1)

            assert bp.ready is True


class TestBoardPoolLifecycle:
    def test_remove_and_cleanup(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())

        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            pool.spawn("/dev/ttyACM0")
            assert "/dev/ttyACM0" in pool._boards

            pool.remove("/dev/ttyACM0")
            assert "/dev/ttyACM0" not in pool._boards

    def test_shutdown_all(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            pool.spawn("/dev/ttyACM0")
            pool.spawn("/dev/ttyACM1")
            assert len(pool._boards) == 2

            pool.shutdown_all()
            assert len(pool._boards) == 0

    def test_restart(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())

        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent = MagicMock(spec=socket.socket)
            child = MagicMock(spec=socket.socket)
            child.fileno.return_value = 5
            mock_sp.return_value = (parent, child)

            pool.spawn("/dev/ttyACM0")

        with patch("board_manager.pool.socket.socketpair") as mock_sp2:
            parent2 = MagicMock(spec=socket.socket)
            child2 = MagicMock(spec=socket.socket)
            child2.fileno.return_value = 6
            mock_sp2.return_value = (parent2, child2)

            bp = pool.restart("/dev/ttyACM0")
            assert bp.port == "/dev/ttyACM0"
            assert bp.parent_sock is parent2
            assert bp.restart_count == 0


class TestBoardPoolStatus:
    def test_get_port_status(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 5
            mock_sp.return_value = (parent_sock, child_sock)

            pool.spawn("/dev/ttyACM0")
            status = pool.get_port_status("/dev/ttyACM0")
            assert status is not None
            assert status["port"] == "/dev/ttyACM0"

    def test_get_port_status_missing(self, pool):
        assert pool.get_port_status("/dev/null") is None

    def test_list_ports(self, pool, monkeypatch):
        monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: FakePopen())
        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent = MagicMock(spec=socket.socket)
            child = MagicMock(spec=socket.socket)
            child.fileno.return_value = 5
            mock_sp.return_value = (parent, child)
            pool.spawn("/dev/ttyACM0")

            mock_sp2 = MagicMock(
                return_value=(
                    MagicMock(spec=socket.socket),
                    MagicMock(spec=socket.socket),
                )
            )
            mock_sp2.return_value[1].fileno.return_value = 6

        with patch("board_manager.pool.socket.socketpair") as mock_sp2:
            parent2 = MagicMock(spec=socket.socket)
            child2 = MagicMock(spec=socket.socket)
            child2.fileno.return_value = 6
            mock_sp2.return_value = (parent2, child2)
            pool.spawn("/dev/ttyACM1")

        ports = pool.list_ports()
        assert sorted(ports) == ["/dev/ttyACM0", "/dev/ttyACM1"]


class TestBoardPoolSpawnArgs:
    def test_spawn_passes_correct_args(self, pool, monkeypatch):
        popen_calls = []

        def fake_popen(*args, **kwargs):
            popen_calls.append((args, kwargs))
            return FakePopen()

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        with patch("board_manager.pool.socket.socketpair") as mock_sp:
            parent_sock = MagicMock(spec=socket.socket)
            child_sock = MagicMock(spec=socket.socket)
            child_sock.fileno.return_value = 7
            mock_sp.return_value = (parent_sock, child_sock)

            pool.spawn("/dev/ttyACM0")

            assert len(popen_calls) == 1
            args, kwargs = popen_calls[0]
            assert "board_worker" in args[0][1] or "board_worker" in args[0][2]
            assert kwargs.get("pass_fds") == [7]
            assert kwargs.get("close_fds") is True
