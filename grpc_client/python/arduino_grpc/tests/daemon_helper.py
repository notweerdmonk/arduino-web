"""grpc_client/python/arduino_grpc/tests/daemon_helper.py

Reusable daemon lifecycle management for arduino-cli integration tests

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
import signal
import socket
import subprocess
import time
from typing import Optional

import grpc

from cc.arduino.cli.commands.v1 import commands_pb2_grpc, commands_pb2


def _find_port_pid(port: int) -> Optional[int]:
    try:
        result = subprocess.run(
            ["fuser", f"{port}/tcp"],
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
            if f":{port}" in line and "LISTEN" in line:
                pid_part = line.split("pid=")
                if len(pid_part) > 1:
                    pid_str = pid_part[1].split(",")[0].strip()
                    if pid_str.isdigit():
                        return int(pid_str)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}", "-s", "TCP:LISTEN"],
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


def _port_is_listening(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (OSError, ConnectionRefusedError, socket.timeout):
        return False


def _health_check(host: str, port: int) -> bool:
    channel = grpc.insecure_channel(f"{host}:{port}")
    try:
        stub = commands_pb2_grpc.ArduinoCoreServiceStub(channel)
        create_resp = stub.Create(commands_pb2.CreateRequest(), timeout=3)
        if create_resp.HasField("instance"):
            instance = create_resp.instance
            try:
                stub.Destroy(commands_pb2.DestroyRequest(instance=instance), timeout=3)
            except Exception:
                pass
            return True
        return False
    except Exception:
        return False
    finally:
        channel.close()


class DaemonCtx:
    """Context manager for arduino-cli daemon lifecycle.

    Ensures a healthy daemon is available during the managed block.
    Starts the daemon if none is running, reuses if one is healthy.
    Kills the daemon on exit if it was started by this instance.
    """

    def __init__(
        self,
        binary: Optional[str] = None,
        port: Optional[int] = None,
        host: str = "127.0.0.1",
        timeout: float = 15.0,
    ):
        self.binary = binary or os.environ.get("ARDUINO_CLI_BINARY", "arduino-cli")
        self.port = (
            port
            if port is not None
            else int(os.environ.get("ARDUINO_CLI_PORT", "50051"))
        )
        self.host = host
        self._timeout = timeout
        self._started_pid: Optional[int] = None
        self._owns_daemon = False
        self.addr = f"{host}:{self.port}"

    def __enter__(self) -> str:
        if _port_is_listening(self.host, self.port):
            if _health_check(self.host, self.port):
                self._owns_daemon = False
                return self.addr
            pid = _find_port_pid(self.port)
            if pid is not None:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                try:
                    os.kill(pid, 0)
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass

        proc = subprocess.Popen(
            [self.binary, "daemon", "--port", str(self.port), "--daemonize"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            if _port_is_listening(self.host, self.port) and _health_check(
                self.host, self.port
            ):
                self._started_pid = _find_port_pid(self.port)
                break
            time.sleep(0.5)

        if self._started_pid is None:
            try:
                proc.wait(timeout=3)
            except Exception:
                try:
                    os.kill(proc.pid, signal.SIGKILL)
                except OSError:
                    pass
            raise RuntimeError(
                f"Daemon did not become ready on {self.addr} within {self._timeout}s"
            )

        self._owns_daemon = True
        return self.addr

    def __exit__(self, *args) -> None:
        if not self._owns_daemon:
            return
        pid = self._started_pid
        if pid is None:
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
        time.sleep(0.5)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
