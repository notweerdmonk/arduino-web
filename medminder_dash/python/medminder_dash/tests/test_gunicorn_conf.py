"""medminder_dash/python/medminder_dash/tests/test_gunicorn_conf.py

Tests for gunicorn_conf module.

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
from unittest.mock import MagicMock, patch


from medminder_dash import gunicorn_conf as conf


class MockServer:
    def __init__(self):
        self.log = MagicMock()


class MockWorker:
    def __init__(self):
        self.log = MagicMock()
        self.pid = 12345


class TestGetBmsConfig:
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = conf._get_bms_config()
            assert cfg["uds_path"] == "/tmp/board_mgr.sock"
            assert cfg["tcp_host"] == "127.0.0.1"
            assert cfg["tcp_port"] == 9090
            assert cfg["use_uds"] is True

    def test_env_overrides(self):
        env = {
            "BOARD_MGR_UDS_PATH": "/tmp/custom.sock",
            "BOARD_MGR_TCP_HOST": "0.0.0.0",
            "BOARD_MGR_TCP_PORT": "8080",
            "BMS_NO_UDS": "true",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = conf._get_bms_config()
            assert cfg["uds_path"] == "/tmp/custom.sock"
            assert cfg["tcp_host"] == "0.0.0.0"
            assert cfg["tcp_port"] == 8080
            assert cfg["use_uds"] is False


class TestWhenReady:
    @patch("board_manager.boot.start_bms")
    @patch("board_manager.boot.wait_for_bms")
    def test_starts_bms_and_waits(self, mock_wait, mock_start):
        mock_proc = MagicMock()
        mock_proc.pid = 9999
        mock_start.return_value = mock_proc
        old_proc = conf._bms_proc
        try:
            conf.when_ready(MockServer())
            mock_start.assert_called_once()
            mock_wait.assert_called_once()
            assert conf._bms_proc is mock_proc
        finally:
            conf._bms_proc = old_proc

    @patch("board_manager.boot.start_bms")
    @patch("board_manager.boot.wait_for_bms")
    def test_fire_and_forget_skips_wait(self, mock_wait, mock_start):
        mock_proc = MagicMock()
        mock_start.return_value = mock_proc
        old_proc = conf._bms_proc
        try:
            with patch.dict(os.environ, {"BMS_FIRE_AND_FORGET": "1"}, clear=True):
                conf.when_ready(MockServer())
                mock_start.assert_called_once()
                mock_wait.assert_not_called()
        finally:
            conf._bms_proc = old_proc


class TestPostWorkerInit:
    @patch("medminder_dash.pubsub.init_pubsub")
    def test_calls_init_pubsub(self, mock_init):
        conf.post_worker_init(MockWorker())
        mock_init.assert_called_once()

    @patch("medminder_dash.pubsub.init_pubsub")
    def test_passes_bms_config(self, mock_init):
        env = {
            "BOARD_MGR_TCP_HOST": "0.0.0.0",
            "BOARD_MGR_TCP_PORT": "8080",
            "BOARD_MGR_UDS_PATH": "/tmp/custom.sock",
            "BMS_NO_UDS": "true",
        }
        with patch.dict(os.environ, env, clear=True):
            conf.post_worker_init(MockWorker())
            assert mock_init.called
            args, kwargs = mock_init.call_args
            assert len(args) == 1  # app passed as positional arg
            assert kwargs == {
                "use_uds": False,
                "tcp_host": "0.0.0.0",
                "tcp_port": 8080,
                "uds_path": "/tmp/custom.sock",
            }


class TestOnExit:
    @patch("board_manager.boot.stop_bms")
    def test_stops_bms(self, mock_stop):
        mock_proc = MagicMock()
        mock_proc.pid = 9999
        old_proc = conf._bms_proc
        try:
            conf._bms_proc = mock_proc
            conf.on_exit(MockServer())
            mock_stop.assert_called_once_with(mock_proc)
        finally:
            conf._bms_proc = old_proc

    @patch("board_manager.boot.stop_bms")
    def test_noop_when_no_bms(self, mock_stop):
        old_proc = conf._bms_proc
        try:
            conf._bms_proc = None
            conf.on_exit(MockServer())
            mock_stop.assert_not_called()
        finally:
            conf._bms_proc = old_proc

