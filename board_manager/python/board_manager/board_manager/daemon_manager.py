"""board_manager/python/board_manager/board_manager/daemon_manager.py

Manages the arduino-cli daemon subprocess lifecycle

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
import signal
import socket
import subprocess
import time
from typing import Optional

import grpc
from cc.arduino.cli.commands.v1 import commands_pb2, commands_pb2_grpc

logger = logging.getLogger("board_manager.daemon")


class DaemonStartError(Exception):
    """Raised when the arduino-cli daemon fails to start."""


class DaemonManager:
    """Spawns, monitors, and auto-recovers the arduino-cli daemon subprocess.

    On startup, checks if the configured port is already in use. If it is,
    performs a gRPC health check (Create RPC) to determine whether a valid
    arduino-cli daemon is already running. If the health check passes, the
    existing daemon is reused. If it fails, the process holding the port is
    killed and a fresh daemon is spawned.
    """

    def __init__(
        self, binary: str = "arduino-cli", daemon_addr: str = "localhost:50051"
    ):
        """Initialize the daemon manager.

        Args:
            binary: Path or name of the arduino-cli binary.
            daemon_addr: Host:port address for the daemon.
        """
        self._binary = binary
        self._host, self._port = self._parse_addr(daemon_addr)
        self._process: Optional[subprocess.Popen] = None
        self._daemon_pid: Optional[int] = None

    @property
    def is_alive(self) -> bool:
        """Check whether the daemon process is still running.

        Returns:
            True if the daemon process is alive and not a zombie.
        """
        if self._daemon_pid is not None:
            try:
                os.kill(self._daemon_pid, 0)
            except OSError:
                self._daemon_pid = None
            else:
                if not self._is_zombie(self._daemon_pid):
                    return True
                self._daemon_pid = None  # zombie — treat as dead
        if self._process is not None:
            ret = self._process.poll()
            return ret is None
        return False

    @staticmethod
    def _is_zombie(pid: int) -> bool:
        """Check if a process is a zombie via /proc/<pid>/status"""
        try:
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("State:"):
                        return "Z (zombie)" in line
        except OSError:
            return False
        return False

    @staticmethod
    def _parse_addr(addr: str) -> tuple[str, int]:
        """Parse a host:port string into a tuple.

        Args:
            addr: The address string to parse.

        Returns:
            Tuple of (host, port).

        Raises:
            DaemonStartError: If the address format is invalid.
        """
        parts = addr.rsplit(":", 1)
        if len(parts) != 2:
            raise DaemonStartError(
                f"Invalid daemon address: {addr!r} (expected host:port)"
            )
        host = parts[0] or "127.0.0.1"
        try:
            port = int(parts[1])
        except ValueError:
            raise DaemonStartError(f"Invalid port in daemon address: {addr!r}")
        if port < 1 or port > 65535:
            raise DaemonStartError(f"Port out of range in daemon address: {addr!r}")
        return host, port

    def start(self, timeout: float = 15.0) -> None:
        """Start the arduino-cli daemon or reuse an existing one.

        Args:
            timeout: Seconds to wait for the daemon to become ready.

        Raises:
            DaemonStartError: If the daemon fails to start or does not become ready.
        """
        if self.is_alive:
            logger.info("Daemon already running on pid %d", self._process.pid)
            return

        if self._port_is_listening():
            if self._health_check():
                logger.info(
                    "Reusing existing daemon on %s:%d (health check passed)",
                    self._host,
                    self._port,
                )
                return
            logger.warning(
                "Port %d in use but health check failed; killing owner and restarting",
                self._port,
            )
            self._kill_port_owner()

        logger.info(
            "Starting daemon: %s daemon --port %d --daemonize", self._binary, self._port
        )
        try:
            self._process = subprocess.Popen(
                [self._binary, "daemon", "--port", str(self._port), "--daemonize"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise DaemonStartError(
                f"arduino-cli binary not found: {self._binary!r}. "
                "Install arduino-cli or set BOARD_MGR_DAEMON_BINARY env var."
            )

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._port_is_listening():
                # Do a quick health check to ensure it's responsive
                if self._health_check():
                    # With --daemonize, the parent process exits after fork.
                    # Find the actual daemon PID for proper lifecycle management.
                    try:
                        actual_pid = self._find_port_pid()
                    except Exception:
                        actual_pid = None
                    if actual_pid is not None:
                        self._daemon_pid = actual_pid
                        logger.info(
                            "Daemon ready on %s:%d (pid %d, actual pid %d)",
                            self._host,
                            self._port,
                            self._process.pid,
                            self._daemon_pid,
                        )
                    else:
                        logger.warning(
                            "Could not determine actual daemon PID, tracking parent pid %d",
                            self._process.pid,
                        )
                    return
            time.sleep(0.5)

        raise DaemonStartError(
            f"Daemon did not become ready within {timeout}s on {self._host}:{self._port}"
        )

    def stop(self) -> None:
        """Stop the arduino-cli daemon process and clean up."""
        if self._process is None and self._daemon_pid is None:
            return

        # Kill the actual daemon process (forked child) first
        if self._daemon_pid is not None:
            pid = self._daemon_pid
            logger.info("Stopping daemon (actual pid %d)", pid)
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
            try:
                os.kill(pid, 0)
                time.sleep(1)
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
            self._daemon_pid = None

        # Clean up the parent (already a zombie, but wait for it)
        if self._process is not None:
            pid = self._process.pid
            logger.info("Cleaning up daemon parent process (pid %d)", pid)
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
                self._process.wait()
            self._process = None

        logger.info("Daemon stopped")
        return

    def ensure_alive(self) -> bool:
        """Check daemon health and restart if necessary.

        Returns:
            True if the daemon is running after the check.
        """
        if self.is_alive:
            return True
        if self._port_is_listening():
            if self._health_check():
                logger.info("Daemon recovered (port still open, health check passed)")
                try:
                    actual_pid = self._find_port_pid()
                    if actual_pid is not None:
                        self._daemon_pid = actual_pid
                except Exception:
                    pass
                return True
            logger.warning("Port open but health check failed; killing owner")
            self._kill_port_owner()
        try:
            self.start(timeout=10.0)
            return True
        except DaemonStartError as e:
            logger.error("Failed to restart daemon: %s", e)
            return False

    def _port_is_listening(self) -> bool:
        """Check if something is listening on the configured daemon port.

        Returns:
            True if the port is open.
        """
        try:
            with socket.create_connection((self._host, self._port), timeout=1):
                return True
        except (OSError, ConnectionRefusedError, socket.timeout):
            return False

    def _health_check(self) -> bool:
        """Perform a gRPC health check against the daemon.

        Returns:
            True if the daemon responds to a Create RPC.
        """
        try:
            channel = grpc.insecure_channel(f"{self._host}:{self._port}")
            stub = commands_pb2_grpc.ArduinoCoreServiceStub(channel)
            create_resp = stub.Create(commands_pb2.CreateRequest(), timeout=3)
            if create_resp.HasField("instance"):
                instance = create_resp.instance
                try:
                    stub.Destroy(
                        commands_pb2.DestroyRequest(instance=instance), timeout=3
                    )
                except Exception:
                    pass
                return True
            return False
        except Exception:
            return False
        finally:
            if channel is not None:
                try:
                    channel.close()
                except Exception:
                    pass

    def _kill_port_owner(self) -> None:
        """Kill the process holding the configured daemon port."""
        pid = self._find_port_pid()
        if pid is None:
            logger.warning("Could not find PID of process on port %d", self._port)
            return
        logger.warning("Killing process %d on port %d", pid, self._port)
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        except OSError:
            pass

    def _find_port_pid(self) -> Optional[int]:
        """Find the PID of the process listening on the configured port.

        Tries ``fuser``, ``ss``, and ``lsof`` in order.

        Returns:
            The PID, or None if not found.
        """
        try:
            result = subprocess.run(
                ["fuser", f"{self._port}/tcp"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                for part in result.stdout.strip().split():
                    cleaned = part.strip()
                    if cleaned.isdigit():
                        return int(cleaned)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        try:
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            for line in result.stdout.splitlines():
                if f":{self._port}" in line and "LISTEN" in line:
                    pid_part = line.split("pid=")
                    if len(pid_part) > 1:
                        pid_str = pid_part[1].split(",")[0].strip()
                        if pid_str.isdigit():
                            return int(pid_str)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{self._port}", "-s", "TCP:LISTEN"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    line = line.strip()
                    if line.isdigit():
                        return int(line)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

