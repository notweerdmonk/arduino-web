"""board_manager/python/board_manager/board_manager/board_detector.py

Background board detector: polls arduino-cli daemon and emits connect/disconnect events

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
import threading
import time
from enum import Enum
from typing import Any, Callable, Optional

from arduino_grpc.client import ArduinoGrpcClient

logger = logging.getLogger("board_manager.detector")

BoardEventCallback = Callable[[str, dict], None]


class DetectorDefaults(Enum):
    """Default values for board detector configuration."""

    POLL_INTERVAL = 5.0
    LIST_TIMEOUT = 3


class BoardDetector:
    """Detects board connect/disconnect events.

    Supports two modes:
    - ``"watch"`` (default): uses arduino-cli BoardListWatch streaming RPC.
    - ``"poll"``: legacy periodic polling via ``list_boards()``.

    Runs a background thread that invokes a callback with ``"connected"`` or
    ``"disconnected"`` events. On connection failures, waits 2 seconds before
    retrying. If a ``daemon_manager`` is configured, attempts to restart the
    daemon before retrying.
    """

    def __init__(
        self,
        callback: BoardEventCallback,
        daemon: str = "localhost:50051",
        poll_interval: float = DetectorDefaults.POLL_INTERVAL.value,
        list_timeout: float = DetectorDefaults.LIST_TIMEOUT.value,
        daemon_manager: Any = None,
        mode: str = "watch",
    ):
        """Initialize the board detector.

        Args:
            callback: Called with (port, msg) on connect/disconnect events.
            daemon: Arduino CLI daemon address.
            poll_interval: Seconds between poll iterations.
            list_timeout: Timeout for list_boards gRPC call.
            daemon_manager: Optional DaemonManager for auto-recovery.
            mode: Detection mode — ``"watch"`` or ``"poll"``.
        """
        self._callback = callback
        self._daemon = daemon
        self._poll_interval = poll_interval
        self._list_timeout = list_timeout
        self._daemon_manager = daemon_manager
        self._mode = mode
        self._known_boards: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the detector background thread."""
        if self._running:
            return
        self._running = True
        if self._mode == "watch":
            self._thread = threading.Thread(target=self._run_watch, daemon=True)
            self._thread.start()
            logger.info("BoardDetector started (watch mode)")
        else:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            logger.info("BoardDetector started (poll mode, every %.1fs)", self._poll_interval)

    def stop(self) -> None:
        """Stop the detector background thread."""
        if not self._running:
            return
        self._running = False
        logger.info("BoardDetector stopped")

    def _connect_or_restart(self, silent: bool = False) -> Optional[ArduinoGrpcClient]:
        """Try to connect/init; on failure restart daemon and retry once."""
        client = ArduinoGrpcClient(daemon=self._daemon)
        try:
            client.connect()
            client.init()
            return client
        except Exception as e:
            if not silent:
                logger.warning("BoardDetector: failed to connect to daemon (%s), retrying...", e)
            client.disconnect()
            if self._restart_daemon():
                client = ArduinoGrpcClient(daemon=self._daemon)
                try:
                    client.connect()
                    client.init()
                    return client
                except Exception as e2:
                    logger.warning("BoardDetector: still cannot connect after restart (%s)", e2)
                    client.disconnect()
            return None

    def _restart_daemon(self) -> bool:
        """Restart the arduino-cli daemon via daemon_manager if available.

        Returns:
            True if the daemon was successfully restarted.
        """
        if not self._daemon_manager:
            return False
        try:
            ok = self._daemon_manager.ensure_alive()
            if ok:
                logger.info("BoardDetector: daemon restarted successfully")
            else:
                logger.warning("BoardDetector: daemon restart failed")
            return ok
        except Exception as e:
            logger.warning("BoardDetector: failed to restart daemon: %s", e)
            return False

    def get_known_boards(self) -> dict[str, dict]:
        """Return a snapshot of currently known boards."""
        with self._lock:
            return dict(self._known_boards)

    def _run(self) -> None:
        """Poll loop: continuously poll board list and detect changes."""
        while self._running:
            try:
                ok = self._run_once()
            except Exception as e:
                logger.error("BoardDetector: unexpected error: %s", e)
                ok = False
            if not self._running:
                break
            if ok:
                time.sleep(self._poll_interval)
            else:
                logger.info(
                    "BoardDetector: poll failed, next attempt in 2.0s",
                )
                time.sleep(2.0)

    def _run_once(self) -> bool:
        """Perform a single poll cycle: connect, list boards, emit events.

        Returns:
            True if the cycle completed without connection errors.
        """
        client = self._connect_or_restart()
        if client is None:
            return False

        try:
            while self._running:
                try:
                    boards = client.list_boards(timeout=self._list_timeout)
                except Exception as e:
                    logger.warning("BoardDetector: list_boards failed (%s), reconnecting...", e)
                    client.disconnect()
                    self._restart_daemon()
                    return False

                current = {}
                for b in boards:
                    key = b.port.address
                    current[key] = {
                        "port": b.port.address,
                        "fqbn": b.fqbn,
                        "name": b.name,
                        "hardware_id": b.port.hardware_id,
                    }

                with self._lock:
                    old = dict(self._known_boards)
                    self._known_boards = current

                for addr, info in current.items():
                    if addr not in old:
                        logger.info(
                            "Board detected: %s at %s (%s)",
                            info["name"],
                            addr,
                            info["fqbn"],
                        )
                        self._emit("connected", info)

                for addr, info in old.items():
                    if addr not in current:
                        logger.info(
                            "Board disconnected: %s at %s (%s)",
                            info["name"],
                            addr,
                            info.get("fqbn", ""),
                        )
                        self._emit("disconnected", info)
                time.sleep(self._poll_interval)
        finally:
            try:
                client.disconnect()
            except Exception:
                pass

        return True

    def _run_watch(self) -> None:
        """Stream board events via BoardListWatch."""
        while self._running:
            client = self._connect_or_restart(silent=False)
            if client is None:
                time.sleep(2.0)
                continue
            try:
                for board in client.watch_boards(timeout=None):
                    if not self._running:
                        break
                    addr = board.port.address
                    info = {
                        "port": addr,
                        "fqbn": board.fqbn,
                        "name": board.name,
                        "hardware_id": board.port.hardware_id,
                        "source": "watch",
                    }
                    with self._lock:
                        if board.detected and addr not in self._known_boards:
                            self._known_boards[addr] = info
                            event = "connected"
                            payload = info
                        elif not board.detected and addr in self._known_boards:
                            payload = self._known_boards.pop(addr)
                            event = "disconnected"
                        else:
                            event = None
                    if event:
                        logger.info(
                            "Board %s: %s at %s (%s)",
                            event,
                            info["name"],
                            addr,
                            info["fqbn"],
                        )
                        self._emit(event, payload)
            except Exception as e:
                logger.warning("BoardDetector: watch stream error (%s), reconnecting...", e)
                try:
                    client.disconnect()
                except Exception:
                    pass
                time.sleep(2.0)

    def _emit(self, event: str, info: dict) -> None:
        """Emit a board event to the registered callback.

        Args:
            event: ``"connected"`` or ``"disconnected"``.
            info: Board info dict.
        """
        msg = {
            "type": "event",
            "topic": f"board::{info['port']}::event",
            "data": {
                "event": event,
                "port": info["port"],
                "board": info.get("name", ""),
                "fqbn": info.get("fqbn", ""),
                "hardware_id": info.get("hardware_id", ""),
            },
        }
        try:
            self._callback(info["port"], msg)
        except Exception as e:
            logger.error("BoardDetector: callback error: %s", e)
