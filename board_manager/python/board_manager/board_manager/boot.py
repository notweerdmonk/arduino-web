"""board_manager/python/board_manager/board_manager/boot.py

BMS lifecycle helpers for WSGI entry points.

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
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("board_manager.boot")


class BmsEnv(str, Enum):
    """Environment variable names for Board Manager Service configuration."""

    TCP_HOST = "BOARD_MGR_TCP_HOST"
    TCP_PORT = "BOARD_MGR_TCP_PORT"
    UDS_PATH = "BOARD_MGR_UDS_PATH"
    ARDUINO_DAEMON = "BOARD_MGR_ARDUINO_DAEMON"
    DAEMON_BINARY = "BOARD_MGR_DAEMON_BINARY"
    LOG_LEVEL = "BOARD_MGR_LOG_LEVEL"


@dataclass(frozen=True)
class BmsDefaults:
    """Default configuration values for Board Manager Service."""

    UDS_PATH: str = "/tmp/board_mgr.sock"
    TCP_HOST: str = "127.0.0.1"
    TCP_PORT: int = 9090
    ARDUINO_DAEMON: str = "localhost:50051"
    DAEMON_BINARY: str = "arduino-cli"
    LOG_LEVEL: str = "INFO"


def _get_bms_env_config() -> dict:
    """Read BMS configuration from environment variables with defaults.

    Returns:
        Dict of configuration values keyed by option name.
    """
    return {
        "tcp_host": os.environ.get(BmsEnv.TCP_HOST, BmsDefaults.TCP_HOST),
        "tcp_port": int(os.environ.get(BmsEnv.TCP_PORT, str(BmsDefaults.TCP_PORT))),
        "uds_path": os.environ.get(BmsEnv.UDS_PATH, BmsDefaults.UDS_PATH),
        "arduino_daemon": os.environ.get(
            BmsEnv.ARDUINO_DAEMON, BmsDefaults.ARDUINO_DAEMON
        ),
        "daemon_binary": os.environ.get(
            BmsEnv.DAEMON_BINARY, BmsDefaults.DAEMON_BINARY
        ),
        "log_level": os.environ.get(BmsEnv.LOG_LEVEL, BmsDefaults.LOG_LEVEL),
    }


def _free_bms_resources(tcp_host: str, tcp_port: int, uds_path: str) -> None:
    """Kill any stale BMS process holding the target TCP port.

    This prevents OSError: [Errno 98] Address already in use when a previous
    BMS instance (from an unclean shutdown) is still running. Also cleans up
    stale UDS socket files.
    """
    try:
        result = subprocess.run(
            ["lsof", "-ti", f"tcp:{tcp_port}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            for pid in result.stdout.strip().splitlines():
                logger.warning(
                    "Killing stale BMS (PID %s) on %s:%s", pid, tcp_host, tcp_port
                )
                try:
                    os.kill(int(pid), 15)
                except (OSError, ValueError) as e:
                    logger.warning("Failed to kill PID %s: %s", pid, e)
    except FileNotFoundError:
        logger.debug("lsof not available — cannot check for stale BMS on TCP port")
    except subprocess.TimeoutExpired:
        logger.warning("lsof timed out checking TCP port %s", tcp_port)
    if os.path.exists(uds_path):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(uds_path)
            s.close()
            logger.debug("UDS %s is alive — not removing", uds_path)
        except (OSError, ConnectionRefusedError):
            logger.info("Removing stale UDS socket: %s", uds_path)
            os.unlink(uds_path)


def start_bms() -> subprocess.Popen:
    """Start the Board Manager Service as a subprocess.

    Reads config from environment variables and cleans up stale resources
    before launching.

    Returns:
        The Popen handle for the BMS subprocess.
    """
    cfg = _get_bms_env_config()
    _free_bms_resources(cfg["tcp_host"], cfg["tcp_port"], cfg["uds_path"])
    args = [
        sys.executable,
        "-m",
        "board_manager",
        "--tcp-host",
        cfg["tcp_host"],
        "--tcp-port",
        str(cfg["tcp_port"]),
        "--uds-path",
        cfg["uds_path"],
        "--arduino-daemon",
        cfg["arduino_daemon"],
        "--daemon-binary",
        cfg["daemon_binary"],
        "--log-level",
        cfg["log_level"],
    ]
    logger.info("Starting BMS: %s", " ".join(str(a) for a in args))
    proc = subprocess.Popen(args)
    return proc


def stop_bms(proc: subprocess.Popen | None, timeout: float = 5.0) -> None:
    """Stop the Board Manager Service subprocess gracefully.

    Args:
        proc: The BMS subprocess handle.
        timeout: Seconds to wait for graceful shutdown before SIGKILL.
    """
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
        logger.info("BMS (PID %d) stopped gracefully", proc.pid)
    except subprocess.TimeoutExpired:
        logger.warning(
            "BMS (PID %d) did not exit in %.1fs, sending SIGKILL", proc.pid, timeout
        )
        proc.kill()
        proc.wait()


def wait_for_bms(
    uds_path: str = BmsDefaults.UDS_PATH,
    tcp_host: str = BmsDefaults.TCP_HOST,
    tcp_port: int = BmsDefaults.TCP_PORT,
    timeout: float = 10.0,
) -> bool:
    """Wait for the BMS to become reachable via UDS or TCP.

    Args:
        uds_path: Path to the UDS socket.
        tcp_host: TCP host to check.
        tcp_port: TCP port to check.
        timeout: Maximum seconds to wait.

    Returns:
        True if BMS became reachable within the timeout.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.exists(uds_path):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect(uds_path)
                s.close()
                logger.info("BMS ready on UDS %s", uds_path)
                return True
            except (OSError, ConnectionRefusedError):
                pass
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((tcp_host, tcp_port))
            s.close()
            logger.info("BMS ready on TCP %s:%s", tcp_host, tcp_port)
            return True
        except (OSError, ConnectionRefusedError):
            pass
        time.sleep(0.2)
    logger.warning(
        "BMS not ready within %.1fs (UDS=%s TCP=%s:%s)",
        timeout,
        uds_path,
        tcp_host,
        tcp_port,
    )
    return False

