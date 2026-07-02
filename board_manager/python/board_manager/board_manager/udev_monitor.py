"""board_manager/python/board_manager/board_manager/udev_monitor.py

USB serial port hotplug monitor via pyudev

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
from typing import Any, Optional

from board_manager.board_detector import BoardEventCallback

logger = logging.getLogger("board_manager.udev")


class UdevMonitor:
    """Detects board connect/disconnect events via pyudev USB netlink monitor.

    ``_scan_existing()`` runs synchronously at startup so that subscribers
    never see an empty board list.  After that, a daemon thread listens for
    async ``add`` / ``remove`` events from ``pyudev.Monitor``.

    Only ``ttyACM*`` and ``ttyUSB*`` devices are accepted; ``ttyS*`` and
    other serial devices are ignored.

    Gracefully degrades when ``pyudev`` is not installed: a warning is logged
    and the monitor thread immediately exits.
    """

    def __init__(
        self,
        callback: BoardEventCallback,
        daemon: str = "localhost:50051",
    ):
        """Initialize the udev monitor.

        Args:
            callback: Called with (port, msg) on connect/disconnect events.
            daemon: Arduino CLI daemon address for board info resolution.
        """
        self._callback = callback
        self._daemon = daemon
        self._known_boards: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the udev monitor: scan existing devices and begin listening."""
        if self._running:
            return
        self._running = True

        self._scan_existing()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("UdevMonitor started")

    def stop(self) -> None:
        """Stop the udev monitor thread."""
        self._running = False
        logger.info("UdevMonitor stopped")

    def get_known_boards(self) -> dict[str, dict]:
        """Return a snapshot of currently known boards.

        Returns:
            Dict mapping port address to board info.
        """
        with self._lock:
            return dict(self._known_boards)

    def _scan_existing(self) -> None:
        """Scan already-connected Arduino-like devices and emit events for them."""
        try:
            import pyudev
        except ImportError:
            logger.warning("pyudev not available, skipping _scan_existing")
            return

        try:
            context = pyudev.Context()
            for device in context.list_devices(subsystem="tty"):
                if self._is_arduino_like(device):
                    port = device.device_node
                    info = self._resolve_info(port, device)
                    with self._lock:
                        if port not in self._known_boards:
                            self._known_boards[port] = info
                            self._emit("connected", info)
        except Exception as e:
            logger.warning("UdevMonitor: _scan_existing failed: %s", e)

    def _run(self) -> None:
        """Background thread loop: poll udev monitor for device events."""
        try:
            import pyudev
        except ImportError:
            logger.warning("pyudev not available, pyudev monitor disabled")
            return

        try:
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem="tty")
        except Exception as e:
            logger.error("UdevMonitor: failed to create monitor: %s", e)
            return

        for device in iter(monitor.poll, None):
            if not self._running:
                break
            self._handle_device(device)

    def _handle_device(self, device: Any) -> None:
        """Process a single udev device event.

        Args:
            device: A pyudev Device object.
        """
        if not self._is_arduino_like(device):
            return

        port = device.device_node
        action = getattr(device, "action", "")

        if action == "add" or action == "change":
            info = self._resolve_info(port, device)
            with self._lock:
                if port not in self._known_boards:
                    self._known_boards[port] = info
                    should_emit = True
                else:
                    should_emit = False
            if should_emit:
                logger.info("UdevMonitor: board connected at %s", port)
                self._emit("connected", info)

        elif action == "remove":
            with self._lock:
                if port in self._known_boards:
                    info = self._known_boards.pop(port)
                    should_emit = True
                else:
                    should_emit = False
            if should_emit:
                logger.info("UdevMonitor: board disconnected at %s", port)
                self._emit("disconnected", info)

    def _resolve_info(self, port: str, device: Any) -> dict:
        """Resolve board info, trying arduino-cli first then udev properties.

        Args:
            port: The device port path.
            device: A pyudev Device object.

        Returns:
            Dict with port, fqbn, name, hardware_id, and source.
        """
        try:
            from arduino_grpc.client import ArduinoGrpcClient

            client = ArduinoGrpcClient(daemon=self._daemon)
            client.connect()
            client.init()
            boards = client.list_boards(timeout=3)
            client.disconnect()
            for b in boards:
                if b.port.address == port:
                    return {
                        "port": port,
                        "fqbn": b.fqbn,
                        "name": b.name,
                        "hardware_id": b.port.hardware_id,
                        "source": "udev",
                    }
        except Exception:
            pass

        return {
            "port": port,
            "fqbn": "",
            "name": device.get("ID_MODEL", ""),
            "hardware_id": (
                f"{device.get('ID_VENDOR_ID', '')}:{device.get('ID_MODEL_ID', '')}"
                if device.get("ID_VENDOR_ID") or device.get("ID_MODEL_ID")
                else ""
            ),
            "source": "udev",
        }

    @staticmethod
    def _is_arduino_like(device: Any) -> bool:
        """Check whether a udev device is an Arduino-like serial port.

        Args:
            device: A pyudev Device object.

        Returns:
            True if the device name starts with ``ttyACM`` or ``ttyUSB``.
        """
        name = device.sys_name
        return name.startswith("ttyACM") or name.startswith("ttyUSB")

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
            logger.error("UdevMonitor: callback error: %s", e)

