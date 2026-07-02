"""board_manager/python/board_manager/tests/test_config.py

Tests for config module.

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
import tempfile


from board_manager.config import load_config


class TestConfigDefaults:
    def test_default_values(self):
        cfg = load_config()
        assert cfg.tcp_host == "127.0.0.1"
        assert cfg.tcp_port == 9090
        assert cfg.uds_path == "/tmp/board_mgr.sock"
        assert cfg.arduino_daemon == "localhost:50051"
        assert cfg.log_level == "INFO"

    def test_cli_args_override(self):
        cfg = load_config(
            {
                "tcp_host": "0.0.0.0",
                "tcp_port": 8080,
                "log_level": "DEBUG",
            }
        )
        assert cfg.tcp_host == "0.0.0.0"
        assert cfg.tcp_port == 8080
        assert cfg.log_level == "DEBUG"

    def test_env_vars_override(self, monkeypatch):
        monkeypatch.setenv("BOARD_MGR_TCP_HOST", "192.168.1.1")
        monkeypatch.setenv("BOARD_MGR_TCP_PORT", "7000")
        cfg = load_config()
        assert cfg.tcp_host == "192.168.1.1"
        assert cfg.tcp_port == 7000

    def test_cli_overrides_env(self, monkeypatch):
        monkeypatch.setenv("BOARD_MGR_TCP_HOST", "0.0.0.0")
        monkeypatch.setenv("BOARD_MGR_TCP_PORT", "7000")
        cfg = load_config({"tcp_host": "10.0.0.1"})
        assert cfg.tcp_host == "10.0.0.1"
        assert cfg.tcp_port == 7000

    def test_none_values_in_args_use_defaults(self):
        cfg = load_config({"tcp_host": None})
        assert cfg.tcp_host == "127.0.0.1"


class TestConfigToml:
    def test_toml_config_loading(self):
        toml_content = """
[service]
tcp_host = "0.0.0.0"
tcp_port = 7070
uds_path = "/tmp/custom.sock"
arduino_daemon = "localhost:60000"
log_level = "DEBUG"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            path = f.name

        try:
            cfg = load_config({"config_file": path})
            assert cfg.tcp_host == "0.0.0.0"
            assert cfg.tcp_port == 7070
            assert cfg.uds_path == "/tmp/custom.sock"
            assert cfg.arduino_daemon == "localhost:60000"
            assert cfg.log_level == "DEBUG"
        finally:
            os.unlink(path)

    def test_missing_config_file_ignored(self):
        cfg = load_config({"config_file": "/nonexistent/config.toml"})
        assert cfg.tcp_host == "127.0.0.1"

    def test_toml_overridden_by_env(self, monkeypatch):
        toml_content = """
[service]
tcp_port = 7070
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            path = f.name

        try:
            monkeypatch.setenv("BOARD_MGR_TCP_PORT", "9090")
            cfg = load_config({"config_file": path})
            assert cfg.tcp_port == 9090
        finally:
            os.unlink(path)

    def test_toml_overridden_by_cli(self, monkeypatch):
        toml_content = """
[service]
tcp_port = 7070
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            path = f.name

        try:
            monkeypatch.setenv("BOARD_MGR_TCP_PORT", "9090")
            cfg = load_config({"config_file": path, "tcp_port": 8080})
            assert cfg.tcp_port == 8080
        finally:
            os.unlink(path)

