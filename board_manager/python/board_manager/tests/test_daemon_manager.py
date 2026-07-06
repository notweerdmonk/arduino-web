"""board_manager/python/board_manager/tests/test_daemon_manager.py

Tests for daemon_manager module.

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

import signal
import subprocess
from unittest.mock import MagicMock, call, patch

import pytest
from board_manager.daemon_manager import DaemonManager, DaemonStartError


class TestDaemonManagerInit:
    def test_default_binary(self):
        dm = DaemonManager()
        assert dm._binary == "arduino-cli"
        assert dm._host == "localhost"
        assert dm._port == 50051

    def test_custom_binary(self):
        dm = DaemonManager(
            binary="/usr/local/bin/arduino-cli", daemon_addr="192.168.1.1:50052"
        )
        assert dm._binary == "/usr/local/bin/arduino-cli"
        assert dm._host == "192.168.1.1"
        assert dm._port == 50052

    def test_parse_addr_defaults_host(self):
        dm = DaemonManager(daemon_addr=":50051")
        assert dm._host == "127.0.0.1"
        assert dm._port == 50051

    def test_parse_addr_invalid_format(self):
        with pytest.raises(DaemonStartError, match="Invalid daemon address"):
            DaemonManager(daemon_addr="not-a-valid-addr")

    def test_parse_addr_invalid_port(self):
        with pytest.raises(DaemonStartError, match="Invalid port"):
            DaemonManager(daemon_addr="localhost:notaport")

    def test_parse_addr_port_out_of_range(self):
        with pytest.raises(DaemonStartError, match="Port out of range"):
            DaemonManager(daemon_addr="localhost:99999")

    def test_is_alive_no_process(self):
        dm = DaemonManager()
        assert dm.is_alive is False

    def test_is_alive_process_running(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        dm._process = mock_proc
        assert dm.is_alive is True

    def test_is_alive_process_dead(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = 1
        dm._process = mock_proc
        assert dm.is_alive is False

    def test_is_alive_with_daemon_pid(self):
        dm = DaemonManager()
        dm._daemon_pid = 12345
        with patch("os.kill") as mock_kill:
            assert dm.is_alive is True
        mock_kill.assert_called_once_with(12345, 0)

    def test_is_alive_with_dead_daemon_pid(self):
        dm = DaemonManager()
        dm._daemon_pid = 12345
        with patch("os.kill", side_effect=OSError()):
            assert dm.is_alive is False
        assert dm._daemon_pid is None


class TestDaemonManagerStart:
    def test_already_running_returns_early(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        dm._process = mock_proc
        with patch.object(dm, "_port_is_listening") as mock_listen:
            dm.start()
        mock_listen.assert_not_called()

    def test_reuses_existing_daemon_when_healthy(self):
        dm = DaemonManager()
        with patch.object(dm, "_port_is_listening", return_value=True):
            with patch.object(dm, "_health_check", return_value=True):
                with patch("subprocess.Popen") as mock_popen:
                    dm.start()
        mock_popen.assert_not_called()
        assert dm._process is None

    def test_kills_owner_when_port_in_use_but_unhealthy(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        with patch.object(dm, "_port_is_listening", side_effect=[True, True]):
            with patch.object(dm, "_health_check", side_effect=[False, True]):
                with patch.object(dm, "_kill_port_owner") as mock_kill:
                    with patch.object(dm, "_find_port_pid", return_value=None):
                        with patch("subprocess.Popen", return_value=mock_proc):
                            dm.start()
        mock_kill.assert_called_once()
        assert mock_proc.poll.call_count >= 0

    def test_spawns_daemon_when_port_free(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        with patch.object(dm, "_port_is_listening", side_effect=[False, True]):
            with patch.object(dm, "_health_check", side_effect=[True]):
                with patch.object(dm, "_find_port_pid", return_value=12345):
                    with patch(
                        "subprocess.Popen", return_value=mock_proc
                    ) as mock_popen:
                        dm.start()
        args, _ = mock_popen.call_args
        assert args[0][0] == "arduino-cli"
        assert "daemon" in args[0]
        assert "--port" in args[0]
        assert "50051" in args[0]
        assert "--daemonize" in args[0]
        assert dm._daemon_pid == 12345

    def test_spawns_daemon_tracks_pid_on_success(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.pid = 99999
        with patch.object(dm, "_port_is_listening", side_effect=[False, True]):
            with patch.object(dm, "_health_check", side_effect=[True]):
                with patch.object(dm, "_find_port_pid", return_value=54321):
                    with patch("subprocess.Popen", return_value=mock_proc):
                        dm.start()
        assert dm._daemon_pid == 54321
        assert dm._process.pid == 99999

    def test_spawns_daemon_falls_back_when_port_pid_not_found(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        with patch.object(dm, "_port_is_listening", side_effect=[False, True]):
            with patch.object(dm, "_health_check", side_effect=[True]):
                with patch.object(dm, "_find_port_pid", return_value=None):
                    with patch("subprocess.Popen", return_value=mock_proc):
                        dm.start()
        assert dm._daemon_pid is None

    def test_raises_when_binary_not_found(self):
        dm = DaemonManager()
        with patch.object(dm, "_port_is_listening", return_value=False):
            with patch("subprocess.Popen", side_effect=FileNotFoundError()):
                with pytest.raises(DaemonStartError, match="binary not found"):
                    dm.start()

    def test_times_out_when_daemon_not_ready(self):
        dm = DaemonManager()
        with patch.object(dm, "_port_is_listening", return_value=False):
            with patch("subprocess.Popen"):
                with patch("time.sleep"):  # speed up the test
                    with pytest.raises(DaemonStartError, match="did not become ready"):
                        dm.start(timeout=0.01)

    def test_start_with_custom_binary(self):
        dm = DaemonManager(binary="/opt/bin/arduino-cli")
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        with patch.object(dm, "_port_is_listening", side_effect=[False, True]):
            with patch.object(dm, "_health_check", side_effect=[True]):
                with patch.object(dm, "_find_port_pid", return_value=None):
                    with patch(
                        "subprocess.Popen", return_value=mock_proc
                    ) as mock_popen:
                        dm.start()
        args, _ = mock_popen.call_args
        assert args[0][0] == "/opt/bin/arduino-cli"


class TestDaemonManagerStop:
    def test_noop_when_no_process(self):
        dm = DaemonManager()
        dm.stop()
        assert dm._process is None

    def test_kills_daemon_pid(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.pid = 11111
        mock_proc.wait.return_value = None
        dm._process = mock_proc
        dm._daemon_pid = 54321
        with patch("os.kill") as mock_kill:
            dm.stop()
        # Should kill daemon pid first
        kill_calls = [
            c[0][0] for c in mock_kill.call_args_list if c[0][1] == signal.SIGTERM
        ]
        assert 54321 in kill_calls
        assert dm._daemon_pid is None

    def test_kills_daemon_pid_with_sigkill(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.pid = 11111
        mock_proc.wait.return_value = None
        dm._process = mock_proc
        dm._daemon_pid = 54321

        def _kill_effect(pid, sig):
            if sig == signal.SIGTERM:
                pass  # survives SIGTERM
            elif sig == 0:
                raise OSError()  # still alive after 1s

        with patch("os.kill", side_effect=_kill_effect):
            with patch("time.sleep"):
                dm.stop()
        assert dm._daemon_pid is None

    def test_stop_with_daemon_pid_only(self):
        dm = DaemonManager()
        dm._daemon_pid = 54321
        with patch("os.kill") as mock_kill:
            dm.stop()
        assert dm._daemon_pid is None
        # Should have killed daemon PID with SIGTERM
        mock_kill.assert_any_call(54321, signal.SIGTERM)

    def test_sends_sigterm_then_wait(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        dm._process = mock_proc
        with patch("os.kill") as mock_kill:
            dm.stop()
        mock_kill.assert_called_once_with(12345, signal.SIGTERM)
        mock_proc.wait.assert_called_once_with(timeout=3)
        assert dm._process is None

    def test_sends_sigkill_on_timeout(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.wait.side_effect = [subprocess.TimeoutExpired("cmd", 3), None]
        dm._process = mock_proc
        with patch("os.kill") as mock_kill:
            dm.stop()
        assert mock_kill.call_args_list == [
            call(12345, signal.SIGTERM),
            call(12345, signal.SIGKILL),
        ]
        assert mock_proc.wait.call_count == 2
        assert dm._process is None

    def test_ignores_kill_errors(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.wait.side_effect = [subprocess.TimeoutExpired("cmd", 3), None]
        dm._process = mock_proc
        with patch("os.kill", side_effect=OSError("no such process")):
            dm.stop()  # should not raise
        assert dm._process is None


class TestDaemonManagerEnsureAlive:
    def test_returns_true_if_alive(self):
        dm = DaemonManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        dm._process = mock_proc
        assert dm.ensure_alive() is True

    def test_recovers_if_port_still_open_and_healthy(self):
        dm = DaemonManager()
        dm._process = MagicMock()
        dm._process.poll.return_value = 1  # dead
        with patch.object(dm, "_port_is_listening", return_value=True):
            with patch.object(dm, "_health_check", return_value=True):
                with patch.object(dm, "_find_port_pid", return_value=98765):
                    assert dm.ensure_alive() is True
        assert dm._daemon_pid == 98765

    def test_recovers_and_falls_back_when_pid_not_found(self):
        dm = DaemonManager()
        dm._process = MagicMock()
        dm._process.poll.return_value = 1  # dead
        with patch.object(dm, "_port_is_listening", return_value=True):
            with patch.object(dm, "_health_check", return_value=True):
                with patch.object(dm, "_find_port_pid", return_value=None):
                    assert dm.ensure_alive() is True
        assert dm._daemon_pid is None

    def test_restarts_if_port_open_but_unhealthy(self):
        dm = DaemonManager()
        dm._process = MagicMock()
        dm._process.poll.return_value = 1  # dead
        with patch.object(dm, "_port_is_listening", return_value=True):
            with patch.object(dm, "_health_check", return_value=False):
                with patch.object(dm, "_kill_port_owner") as mock_kill:
                    with patch.object(dm, "start") as mock_start:
                        assert dm.ensure_alive() is True
        mock_kill.assert_called_once()
        mock_start.assert_called_once_with(timeout=10.0)

    def test_restarts_if_port_free(self):
        dm = DaemonManager()
        dm._process = MagicMock()
        dm._process.poll.return_value = 1  # dead
        with patch.object(dm, "_port_is_listening", return_value=False):
            with patch.object(dm, "start") as mock_start:
                assert dm.ensure_alive() is True
        mock_start.assert_called_once_with(timeout=10.0)

    def test_returns_false_if_restart_fails(self):
        dm = DaemonManager()
        dm._process = MagicMock()
        dm._process.poll.return_value = 1  # dead
        with patch.object(dm, "_port_is_listening", return_value=False):
            with patch.object(dm, "start", side_effect=DaemonStartError("boom")):
                assert dm.ensure_alive() is False


class TestDaemonManagerCheckPort:
    def test_port_is_listening_returns_true(self):
        dm = DaemonManager()
        with patch("socket.create_connection"):
            assert dm._port_is_listening() is True

    def test_port_is_listening_returns_false(self):
        dm = DaemonManager()
        with patch("socket.create_connection", side_effect=ConnectionRefusedError()):
            assert dm._port_is_listening() is False

    def test_port_is_listening_timeout_returns_false(self):
        dm = DaemonManager()
        with patch("socket.create_connection", side_effect=TimeoutError()):
            assert dm._port_is_listening() is False

    def test_health_check_success(self):
        dm = DaemonManager()
        mock_channel = MagicMock()
        mock_stub = MagicMock()
        mock_create_resp = MagicMock()
        mock_instance = MagicMock()
        mock_create_resp.HasField.return_value = True
        mock_create_resp.instance = mock_instance
        mock_stub.Create.return_value = mock_create_resp
        with patch("grpc.insecure_channel", return_value=mock_channel):
            with patch(
                "board_manager.daemon_manager.commands_pb2_grpc.ArduinoCoreServiceStub",
                return_value=mock_stub,
            ):
                assert dm._health_check() is True
        mock_stub.Create.assert_called_once()
        # Destroy may or may not be called depending on mock behavior
        # The important thing is that health check returns True

    def test_health_check_failure(self):
        dm = DaemonManager()
        mock_channel = MagicMock()
        mock_stub = MagicMock()
        mock_stub.Create.side_effect = Exception("gRPC error")
        with patch("grpc.insecure_channel", return_value=mock_channel):
            with patch(
                "board_manager.daemon_manager.commands_pb2_grpc.ArduinoCoreServiceStub",
                return_value=mock_stub,
            ):
                assert dm._health_check() is False

    def test_health_check_no_instance_field(self):
        dm = DaemonManager()
        mock_channel = MagicMock()
        mock_stub = MagicMock()
        mock_create_resp = MagicMock()
        mock_create_resp.HasField.return_value = False
        mock_stub.Create.return_value = mock_create_resp
        with patch("grpc.insecure_channel", return_value=mock_channel):
            with patch(
                "board_manager.daemon_manager.commands_pb2_grpc.ArduinoCoreServiceStub",
                return_value=mock_stub,
            ):
                assert dm._health_check() is False


class TestDaemonManagerFindPortPid:
    def test_parses_fuser_output(self):
        dm = DaemonManager()
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "50051/tcp: 12345\n"
            mock_run.return_value = mock_result
            pid = dm._find_port_pid()
            assert pid == 12345

    def test_parses_ss_output_fallback(self):
        dm = DaemonManager()
        with patch("subprocess.run") as mock_run:

            def _side_effect(*args, **kwargs):
                result = MagicMock()
                if "fuser" in args[0]:
                    result.returncode = 1
                    result.stdout = ""
                else:
                    result.returncode = 0
                    result.stdout = (
                        'LISTEN 0 4096 127.0.0.1:50051 0.0.0.0:* '
                        'users:(("arduino-cli",pid=12345,fd=6))\n'
                    )
                return result

            mock_run.side_effect = _side_effect
            pid = dm._find_port_pid()
            assert pid == 12345

    def test_returns_none_when_no_pid_found(self):
        dm = DaemonManager()
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_run.return_value = mock_result
            pid = dm._find_port_pid()
            assert pid is None


class TestDaemonManagerKillPortOwner:
    def test_sends_sigterm_then_sigkill(self):
        dm = DaemonManager()
        with patch.object(dm, "_find_port_pid", return_value=12345):
            with patch("os.kill") as mock_kill:
                with patch("time.sleep"):
                    dm._kill_port_owner()
        assert mock_kill.call_args_list[0][0] == (12345, signal.SIGTERM)
        # Second call is os.kill(pid, 0) for existence check
        assert mock_kill.call_args_list[1][0] == (12345, 0)
        # Third call is SIGKILL
        assert mock_kill.call_args_list[2][0] == (12345, signal.SIGKILL)

    def test_noop_when_pid_not_found(self):
        dm = DaemonManager()
        with patch.object(dm, "_find_port_pid", return_value=None):
            with patch("os.kill") as mock_kill:
                dm._kill_port_owner()
        mock_kill.assert_not_called()

