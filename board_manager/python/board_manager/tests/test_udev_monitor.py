"""board_manager/python/board_manager/tests/test_udev_monitor.py

Tests for udev_monitor module.

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

from unittest.mock import MagicMock, patch

from board_manager.udev_monitor import UdevMonitor


def _make_device(
    sys_name: str = "ttyACM0",
    device_node: str = "/dev/ttyACM0",
    action: str = "add",
    id_model: str = "Arduino_Uno",
    id_vendor_id: str = "2341",
    id_model_id: str = "0043",
) -> MagicMock:
    dev = MagicMock()
    dev.sys_name = sys_name
    dev.device_node = device_node
    dev.action = action
    dev.get = lambda key, default="": {
        "ID_MODEL": id_model,
        "ID_VENDOR_ID": id_vendor_id,
        "ID_MODEL_ID": id_model_id,
    }.get(key, default)
    return dev


class TestUdevMonitor:
    def test_add_event(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        monitor = UdevMonitor(callback=callback)
        device = _make_device()

        monitor._handle_device(device)

        assert len(events) == 1
        assert events[0][1]["data"]["event"] == "connected"
        assert events[0][1]["data"]["port"] == "/dev/ttyACM0"

    def test_remove_event(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        monitor = UdevMonitor(callback=callback)
        with monitor._lock:
            monitor._known_boards["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "fqbn": "",
                "name": "Arduino_Uno",
            }

        device = _make_device(action="remove")

        monitor._handle_device(device)

        assert len(events) == 1
        assert events[0][1]["data"]["event"] == "disconnected"
        assert events[0][1]["data"]["port"] == "/dev/ttyACM0"
        assert "/dev/ttyACM0" not in monitor._known_boards

    def test_duplicate_add_noop(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        monitor = UdevMonitor(callback=callback)
        with monitor._lock:
            monitor._known_boards["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "fqbn": "",
                "name": "Arduino_Uno",
            }

        device = _make_device()

        monitor._handle_device(device)

        assert len(events) == 0

    def test_remove_unknown_noop(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        monitor = UdevMonitor(callback=callback)
        device = _make_device(action="remove")

        monitor._handle_device(device)

        assert len(events) == 0

    def test_resolve_info_calls_arduino_cli(self):
        monitor = UdevMonitor(callback=lambda p, m: None)

        mock_client = MagicMock()
        mock_board = MagicMock()
        mock_board.port.address = "/dev/ttyACM0"
        mock_board.fqbn = "arduino:avr:uno"
        mock_board.name = "Arduino Uno"
        mock_board.port.hardware_id = "USB VID:PID=2341:0043"
        mock_client.list_boards.return_value = [mock_board]

        device = _make_device()

        with patch("arduino_grpc.client.ArduinoGrpcClient", return_value=mock_client):
            info = monitor._resolve_info("/dev/ttyACM0", device)

        assert info["fqbn"] == "arduino:avr:uno"
        assert info["name"] == "Arduino Uno"
        assert info["hardware_id"] == "USB VID:PID=2341:0043"
        assert info["source"] == "udev"

    def test_resolve_info_fallback(self):
        monitor = UdevMonitor(callback=lambda p, m: None)

        device = _make_device(id_model="Arduino_Mega")

        with patch("arduino_grpc.client.ArduinoGrpcClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.connect.side_effect = RuntimeError("no daemon")
            mock_cls.return_value = mock_instance
            info = monitor._resolve_info("/dev/ttyACM0", device)

        assert info["fqbn"] == ""
        assert info["name"] == "Arduino_Mega"
        assert info["hardware_id"] == "2341:0043"
        assert info["source"] == "udev"

    def test_scan_existing_on_startup(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        monitor = UdevMonitor(callback=callback)

        existing_devices = [
            _make_device(sys_name="ttyACM0", device_node="/dev/ttyACM0"),
            _make_device(sys_name="ttyACM1", device_node="/dev/ttyACM1"),
        ]

        mock_pyudev = MagicMock()
        mock_context = MagicMock()
        mock_pyudev.Context.return_value = mock_context
        mock_context.list_devices.return_value = existing_devices

        with (
            patch.dict("sys.modules", {"pyudev": mock_pyudev}),
            patch("arduino_grpc.client.ArduinoGrpcClient") as mock_grpc,
        ):
            mock_instance = MagicMock()
            mock_instance.connect.side_effect = RuntimeError("no daemon")
            mock_grpc.return_value = mock_instance
            monitor._scan_existing()

        assert len(events) == 2
        assert "/dev/ttyACM0" in monitor._known_boards
        assert "/dev/ttyACM1" in monitor._known_boards

    def test_filter_non_arduino_tty(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        monitor = UdevMonitor(callback=callback)
        device = _make_device(sys_name="ttyS0", device_node="/dev/ttyS0")

        monitor._handle_device(device)

        assert len(events) == 0

    def test_start_stop(self):
        monitor = UdevMonitor(callback=lambda p, m: None)

        mock_pyudev = MagicMock()
        mock_context = MagicMock()
        mock_pyudev.Context.return_value = mock_context
        mock_monitor = MagicMock()
        mock_pyudev.Monitor.from_netlink.return_value = mock_monitor

        mock_context.list_devices.return_value = []

        def poll_until_stop():
            if monitor._running:
                return _make_device()
            return None

        mock_monitor.poll.side_effect = poll_until_stop

        with (
            patch.dict("sys.modules", {"pyudev": mock_pyudev}),
            patch("arduino_grpc.client.ArduinoGrpcClient") as mock_grpc,
        ):
            mock_instance = MagicMock()
            mock_instance.connect.side_effect = RuntimeError("no daemon")
            mock_grpc.return_value = mock_instance
            monitor.start()
            monitor.stop()

        assert monitor._thread is not None
        monitor._thread.join(timeout=1.0)

    def test_get_known_boards_thread_safe(self):
        monitor = UdevMonitor(callback=lambda p, m: None)
        board_info = {"port": "/dev/ttyACM0", "fqbn": "", "name": "Arduino_Uno"}

        with monitor._lock:
            monitor._known_boards["/dev/ttyACM0"] = dict(board_info)

        snapshot = monitor.get_known_boards()
        assert snapshot == {"/dev/ttyACM0": board_info}
        assert snapshot is not monitor._known_boards

    def test_change_event_triggers_add(self):
        """A 'change' action should be treated like 'add' for unknown ports."""
        events = []

        def callback(port, msg):
            events.append((port, msg))

        monitor = UdevMonitor(callback=callback)
        device = _make_device(action="change")

        monitor._handle_device(device)

        assert len(events) == 1
        assert events[0][1]["data"]["event"] == "connected"

