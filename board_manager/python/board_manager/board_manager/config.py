"""board_manager/python/board_manager/board_manager/config.py

Configuration loading (TOML → env vars → CLI args)

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
from typing import Optional

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from dataclasses import dataclass

from board_manager.boot import BmsDefaults, BmsEnv


@dataclass
class Config:
    """Service configuration dataclass populated from TOML, env vars, and CLI args."""

    tcp_host: str = BmsDefaults.TCP_HOST
    tcp_port: int = BmsDefaults.TCP_PORT
    uds_path: str = BmsDefaults.UDS_PATH
    arduino_daemon: str = BmsDefaults.ARDUINO_DAEMON
    daemon_binary: str = BmsDefaults.DAEMON_BINARY
    log_level: str = BmsDefaults.LOG_LEVEL
    config_file: str = ""
    board_detection_mode: str = "watch"


def load_config(args: Optional[dict] = None) -> Config:
    """Load and merge configuration from TOML file, environment variables, and CLI args.

    Args:
        args: Optional dict of CLI argument overrides.

    Returns:
        A populated Config instance.
    """
    cfg = Config()
    args = args or {}

    cfg_file = args.get("config_file") or os.environ.get("BOARD_MGR_CONFIG") or ""
    if cfg_file and os.path.exists(cfg_file):
        with open(cfg_file, "rb") as f:
            data = tomllib.load(f)
        if "service" in data:
            svc = data["service"]
            cfg.tcp_host = svc.get("tcp_host", cfg.tcp_host)
            cfg.tcp_port = svc.get("tcp_port", cfg.tcp_port)
            cfg.uds_path = svc.get("uds_path", cfg.uds_path)
            cfg.arduino_daemon = svc.get("arduino_daemon", cfg.arduino_daemon)
            cfg.daemon_binary = svc.get("daemon_binary", cfg.daemon_binary)
            cfg.log_level = svc.get("log_level", cfg.log_level)
            cfg.board_detection_mode = svc.get("board_detection_mode", cfg.board_detection_mode)

    cfg.tcp_host = os.environ.get(BmsEnv.TCP_HOST, cfg.tcp_host)
    cfg.tcp_port = int(os.environ.get(BmsEnv.TCP_PORT, str(cfg.tcp_port)))
    cfg.uds_path = os.environ.get(BmsEnv.UDS_PATH, cfg.uds_path)
    cfg.arduino_daemon = os.environ.get(BmsEnv.ARDUINO_DAEMON, cfg.arduino_daemon)
    cfg.daemon_binary = os.environ.get(BmsEnv.DAEMON_BINARY, cfg.daemon_binary)
    cfg.log_level = os.environ.get(BmsEnv.LOG_LEVEL, cfg.log_level)
    cfg.board_detection_mode = os.environ.get("BOARD_MGR_DETECTION_MODE", cfg.board_detection_mode)

    if args:
        cfg.tcp_host = args.get("tcp_host") or cfg.tcp_host
        cfg.tcp_port = args.get("tcp_port") or cfg.tcp_port
        cfg.uds_path = args.get("uds_path") or cfg.uds_path
        cfg.arduino_daemon = args.get("arduino_daemon") or cfg.arduino_daemon
        cfg.daemon_binary = args.get("daemon_binary") or cfg.daemon_binary
        cfg.log_level = args.get("log_level") or cfg.log_level
        cfg.board_detection_mode = args.get("board_detection_mode") or cfg.board_detection_mode

    return cfg
