"""board_manager/python/board_manager/tests/test_boot.py

Tests for boot module.

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
import subprocess
from unittest.mock import MagicMock, patch

from board_manager.boot import (
    _get_bms_env_config,
    start_bms,
    stop_bms,
    wait_for_bms,
)


class TestGetBmsEnvConfig:
    def test_defaults_when_no_env(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = _get_bms_env_config()
            assert cfg["tcp_host"] == "127.0.0.1"
            assert cfg["tcp_port"] == 9090
            assert cfg["uds_path"] == "/tmp/board_mgr.sock"
            assert cfg["arduino_daemon"] == "localhost:50051"
            assert cfg["daemon_binary"] == "arduino-cli"
            assert cfg["log_level"] == "INFO"

    def test_env_vars_override_defaults(self):
        env = {
            "BOARD_MGR_TCP_HOST": "0.0.0.0",
            "BOARD_MGR_TCP_PORT": "8080",
            "BOARD_MGR_UDS_PATH": "/tmp/custom.sock",
            "BOARD_MGR_ARDUINO_DAEMON": "10.0.0.1:50051",
            "BOARD_MGR_DAEMON_BINARY": "/usr/local/bin/arduino-cli",
            "BOARD_MGR_LOG_LEVEL": "DEBUG",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = _get_bms_env_config()
            assert cfg["tcp_host"] == "0.0.0.0"
            assert cfg["tcp_port"] == 8080
            assert cfg["uds_path"] == "/tmp/custom.sock"
            assert cfg["arduino_daemon"] == "10.0.0.1:50051"
            assert cfg["daemon_binary"] == "/usr/local/bin/arduino-cli"
            assert cfg["log_level"] == "DEBUG"


class TestStartBms:
    @patch("board_manager.boot._free_bms_resources")
    @patch("board_manager.boot.subprocess.Popen")
    def test_spawns_correct_command(self, mock_popen, mock_free):
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        proc = start_bms()

        assert proc is mock_proc
        args, kwargs = mock_popen.call_args
        cmd = args[0]
        assert cmd[0] == "python" or cmd[0].endswith("python")
        assert "-m" in cmd
        assert "board_manager" in cmd
        assert cmd[cmd.index("--tcp-host") + 1] == "127.0.0.1"
        assert cmd[cmd.index("--tcp-port") + 1] == "9090"
        assert cmd[cmd.index("--uds-path") + 1] == "/tmp/board_mgr.sock"

    @patch("board_manager.boot._free_bms_resources")
    @patch("board_manager.boot.subprocess.Popen")
    def test_uses_env_config(self, mock_popen, mock_free):
        mock_popen.return_value = MagicMock()
        env = {"BOARD_MGR_TCP_HOST": "0.0.0.0", "BOARD_MGR_TCP_PORT": "8080"}
        with patch.dict(os.environ, env, clear=True):
            start_bms()
            args, _ = mock_popen.call_args
            cmd = args[0]
            assert cmd[cmd.index("--tcp-host") + 1] == "0.0.0.0"
            assert cmd[cmd.index("--tcp-port") + 1] == "8080"


class TestStopBms:
    def test_noop_when_none(self):
        stop_bms(None)

    def test_terminates_process(self):
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        stop_bms(mock_proc)
        mock_proc.terminate.assert_called_once()
        mock_proc.wait.assert_called_once()

    def test_kills_on_timeout(self):
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.wait.side_effect = [subprocess.TimeoutExpired("cmd", 5), None]
        stop_bms(mock_proc, timeout=1)
        mock_proc.terminate.assert_called_once()
        assert mock_proc.wait.call_count == 2
        mock_proc.kill.assert_called_once()


class TestWaitForBms:
    @patch("board_manager.boot.socket.socket")
    @patch("board_manager.boot.os.path.exists")
    def test_uds_success(self, mock_exists, mock_socket_cls):
        mock_exists.return_value = True
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        result = wait_for_bms(uds_path="/tmp/test.sock", timeout=5.0)

        assert result is True
        mock_sock.connect.assert_called_once_with("/tmp/test.sock")

    @patch("board_manager.boot.socket.socket")
    @patch("board_manager.boot.os.path.exists")
    def test_tcp_fallback(self, mock_exists, mock_socket_cls):
        mock_exists.return_value = False
        mock_uds_sock = MagicMock()
        mock_tcp_sock = MagicMock()

        def socket_side_effect(family, *args, **kwargs):
            if family == 1:
                return mock_uds_sock
            return mock_tcp_sock

        mock_socket_cls.side_effect = socket_side_effect

        result = wait_for_bms(tcp_host="127.0.0.1", tcp_port=9090, timeout=5.0)

        assert result is True
        mock_tcp_sock.connect.assert_called_once_with(("127.0.0.1", 9090))

    @patch("board_manager.boot.socket.socket")
    @patch("board_manager.boot.os.path.exists")
    def test_timeout(self, mock_exists, mock_socket_cls):
        mock_exists.return_value = False
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = ConnectionRefusedError
        mock_socket_cls.return_value = mock_sock

        result = wait_for_bms(timeout=0.5)

        assert result is False
