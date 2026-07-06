"""board_manager/python/board_manager/tests/test_board_detector.py

Tests for board_detector module.

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

from arduino_grpc.models import Board, Port
from board_manager.board_detector import BoardDetector


def _make_board(port: str, fqbn: str, name: str) -> Board:
    return Board(port=Port(address=port, protocol="serial"), fqbn=fqbn, name=name)


def _make_board_with_hardware_id(port: str, fqbn: str, name: str, hardware_id: str) -> Board:
    return Board(
        port=Port(address=port, protocol="serial", hardware_id=hardware_id),
        fqbn=fqbn,
        name=name,
    )


class TestBoardDetector:
    def test_emit_connected_on_first_poll(self):
        mock_client = MagicMock()
        mock_client.list_boards.return_value = [
            _make_board("/dev/ttyACM0", "arduino:avr:uno", "Arduino Uno"),
        ]

        events = []

        def callback(port, msg):
            events.append((port, msg))
            detector._running = False

        detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector._running = True
            detector._run_once()

        assert len(events) == 1
        port, msg = events[0]
        assert port == "/dev/ttyACM0"
        assert msg["type"] == "event"
        assert msg["data"]["event"] == "connected"
        assert msg["data"]["port"] == "/dev/ttyACM0"
        assert msg["data"]["board"] == "Arduino Uno"
        assert msg["data"]["fqbn"] == "arduino:avr:uno"

    def test_emit_connected_for_new_board(self):
        mock_client = MagicMock()
        mock_client.list_boards.return_value = [
            _make_board("/dev/ttyACM0", "arduino:avr:uno", "Arduino Uno"),
        ]

        events = []

        def callback(port, msg):
            events.append((port, msg))
            detector._running = False

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
            detector._running = True
            detector._known_boards = {
                "/dev/ttyACM0": {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "name": "Arduino Uno",
                },
            }

            mock_client.list_boards.return_value = [
                _make_board("/dev/ttyACM0", "arduino:avr:uno", "Arduino Uno"),
                _make_board("/dev/ttyACM1", "arduino:avr:nano", "Arduino Nano"),
            ]
            detector._run_once()

        assert len(events) == 1
        assert events[0][1]["data"]["event"] == "connected"
        assert events[0][1]["data"]["port"] == "/dev/ttyACM1"

    def test_emit_disconnected_for_removed_board(self):
        mock_client = MagicMock()
        mock_client.list_boards.return_value = []

        events = []

        def callback(port, msg):
            events.append((port, msg))
            detector._running = False

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
            detector._running = True
            detector._known_boards = {
                "/dev/ttyACM0": {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "name": "Arduino Uno",
                },
            }
            detector._run_once()

        assert len(events) == 1
        assert events[0][1]["data"]["event"] == "disconnected"
        assert events[0][1]["data"]["port"] == "/dev/ttyACM0"

    def test_no_event_when_no_change(self):
        mock_client = MagicMock()

        call_count = [0]

        def list_boards_fn(**kwargs):
            call_count[0] += 1
            if call_count[0] > 1:
                detector._running = False
            return [_make_board("/dev/ttyACM0", "arduino:avr:uno", "Arduino Uno")]

        mock_client.list_boards.side_effect = list_boards_fn

        events = []

        def callback(port, msg):
            events.append((port, msg))

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
            detector._running = True
            detector._known_boards = {
                "/dev/ttyACM0": {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "name": "Arduino Uno",
                },
            }
            detector._run_once()

        assert len(events) == 0

    def test_no_event_on_list_error(self):
        mock_client = MagicMock()
        mock_client.list_boards.side_effect = RuntimeError("daemon gone")

        events = []

        def callback(port, msg):
            events.append((port, msg))
            detector._running = False

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
            detector._running = True
            detector._run_once()

        assert len(events) == 0

    def test_callback_error_does_not_crash(self):
        mock_client = MagicMock()
        mock_client.list_boards.side_effect = [
            [_make_board("/dev/ttyACM0", "arduino:avr:uno", "Arduino Uno")],
            RuntimeError("stop"),
        ]

        def callback(port, msg):
            raise RuntimeError("callback crashed")

        detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector._running = True
            detector._run_once()

    def test_connect_failure_returns(self):
        with patch("board_manager.board_detector.ArduinoGrpcClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.connect.side_effect = RuntimeError("no daemon")
            mock_cls.return_value = mock_instance

            events = []

            def callback(port, msg):
                events.append((port, msg))

            detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
            detector._running = True
            detector._run_once()

            assert len(events) == 0

    def test_start_and_stop(self):
        mock_client = MagicMock()
        mock_client.list_boards.side_effect = RuntimeError("stop test")

        events = []

        def callback(port, msg):
            events.append((port, msg))

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(
                callback=callback,
                poll_interval=0.01,
                list_timeout=0.01,
            )
            detector.start()
            import time

            time.sleep(0.1)
            detector.stop()

            assert mock_client.connect.called
            assert mock_client.init.called

    def test_multiple_boards_connected(self):
        mock_client = MagicMock()
        mock_client.list_boards.return_value = [
            _make_board("/dev/ttyACM0", "arduino:avr:uno", "Arduino Uno"),
            _make_board("/dev/ttyACM1", "arduino:avr:nano", "Arduino Nano"),
        ]

        events = []

        def callback(port, msg):
            events.append((port, msg))
            detector._running = False

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
            detector._running = True
            detector._run_once()

        assert len(events) == 2
        ports = {e[1]["data"]["port"] for e in events}
        assert ports == {"/dev/ttyACM0", "/dev/ttyACM1"}

    def test_one_disconnects_while_another_stays(self):
        mock_client = MagicMock()
        mock_client.list_boards.return_value = [
            _make_board("/dev/ttyACM0", "arduino:avr:uno", "Arduino Uno"),
        ]

        events = []

        def callback(port, msg):
            events.append((port, msg))
            detector._running = False

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
            detector._running = True
            detector._known_boards = {
                "/dev/ttyACM0": {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "name": "Arduino Uno",
                },
                "/dev/ttyACM1": {
                    "port": "/dev/ttyACM1",
                    "fqbn": "arduino:avr:nano",
                    "name": "Arduino Nano",
                },
            }
            detector._run_once()

        assert len(events) == 1
        assert events[0][1]["data"]["event"] == "disconnected"
        assert events[0][1]["data"]["port"] == "/dev/ttyACM1"


class TestRunLoop:
    def test_sleeps_2s_on_failure(self):
        with patch("board_manager.board_detector.time.sleep") as mock_sleep:
            detector = BoardDetector(
                callback=lambda p, m: None,
                poll_interval=0.01,
                list_timeout=3,
            )
            detector._running = True
            call_count = [0]

            def fake_run_once():
                call_count[0] += 1
                if call_count[0] >= 2:
                    detector._running = False
                return False

            detector._run_once = fake_run_once
            detector._run()
            mock_sleep.assert_any_call(2.0)

    def test_sleeps_poll_interval_on_success(self):
        with patch("board_manager.board_detector.time.sleep") as mock_sleep:
            detector = BoardDetector(
                callback=lambda p, m: None,
                poll_interval=0.01,
                list_timeout=3,
            )
            detector._running = True
            call_count = [0]

            def fake_run_once():
                call_count[0] += 1
                if call_count[0] >= 2:
                    detector._running = False
                return True

            detector._run_once = fake_run_once
            detector._run()
            mock_sleep.assert_any_call(0.01)


class TestRestartDaemon:
    def test_calls_ensure_alive_when_configured(self):
        mock_daemon_mgr = MagicMock()
        mock_daemon_mgr.ensure_alive.return_value = True
        detector = BoardDetector(
            callback=lambda p, m: None,
            daemon_manager=mock_daemon_mgr,
        )
        result = detector._restart_daemon()
        assert result is True
        mock_daemon_mgr.ensure_alive.assert_called_once()

    def test_noop_when_no_daemon_manager(self):
        detector = BoardDetector(callback=lambda p, m: None)
        result = detector._restart_daemon()
        assert result is False

    def test_returns_false_when_ensure_alive_fails(self):
        mock_daemon_mgr = MagicMock()
        mock_daemon_mgr.ensure_alive.return_value = False
        detector = BoardDetector(
            callback=lambda p, m: None,
            daemon_manager=mock_daemon_mgr,
        )
        result = detector._restart_daemon()
        assert result is False

    def test_returns_false_when_ensure_alive_raises(self):
        mock_daemon_mgr = MagicMock()
        mock_daemon_mgr.ensure_alive.side_effect = RuntimeError("boom")
        detector = BoardDetector(
            callback=lambda p, m: None,
            daemon_manager=mock_daemon_mgr,
        )
        result = detector._restart_daemon()
        assert result is False

    def test_called_on_connect_failure(self):
        mock_client = MagicMock()
        mock_client.connect.side_effect = RuntimeError("no daemon")
        mock_daemon_mgr = MagicMock()
        mock_daemon_mgr.ensure_alive.return_value = True

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(
                callback=lambda p, m: None,
                daemon_manager=mock_daemon_mgr,
                poll_interval=0.01,
                list_timeout=3,
            )
            detector._running = True
            result = detector._run_once()
            assert result is False
            mock_daemon_mgr.ensure_alive.assert_called_once()

    def test_called_on_list_boards_failure(self):
        mock_client = MagicMock()
        mock_client.list_boards.side_effect = RuntimeError("daemon died")
        mock_daemon_mgr = MagicMock()
        mock_daemon_mgr.ensure_alive.return_value = True

        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector = BoardDetector(
                callback=lambda p, m: None,
                daemon_manager=mock_daemon_mgr,
                poll_interval=0.01,
                list_timeout=3,
            )
            detector._running = True
            result = detector._run_once()
            assert result is False
            mock_daemon_mgr.ensure_alive.assert_called_once()

    def test_includes_hardware_id_in_current_dict(self):
        """_run_once stores hardware_id in the current/known_boards dict."""
        mock_client = MagicMock()
        mock_client.list_boards.return_value = [
            _make_board_with_hardware_id(
                "/dev/ttyACM0",
                "arduino:avr:uno",
                "Arduino Uno",
                "USB VID:PID=2341:0043 SER=12345",
            ),
        ]

        detector = None

        def stop(port, msg):
            detector._running = False

        detector = BoardDetector(callback=stop, poll_interval=0.01, list_timeout=3)
        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector._running = True
            detector._run_once()

        assert "/dev/ttyACM0" in detector._known_boards
        entry = detector._known_boards["/dev/ttyACM0"]
        assert entry.get("hardware_id") == "USB VID:PID=2341:0043 SER=12345"
        assert entry.get("fqbn") == "arduino:avr:uno"
        assert entry.get("name") == "Arduino Uno"

    def test_emit_payload_contains_hardware_id(self):
        """Emitted payload includes hardware_id key."""
        mock_client = MagicMock()
        mock_client.list_boards.return_value = [
            _make_board_with_hardware_id(
                "/dev/ttyACM0",
                "arduino:avr:uno",
                "Arduino Uno",
                "USB VID:PID=2341:0043 SER=12345",
            ),
        ]

        events = []
        detector = None

        def callback(port, msg):
            events.append((port, msg))
            detector._running = False

        detector = BoardDetector(callback=callback, poll_interval=0.01, list_timeout=3)
        with patch("board_manager.board_detector.ArduinoGrpcClient", return_value=mock_client):
            detector._running = True
            detector._run_once()

        assert len(events) == 1
        assert events[0][1]["data"]["hardware_id"] == "USB VID:PID=2341:0043 SER=12345"

    def test_run_stops_when_running_flag_cleared(self):
        with patch("board_manager.board_detector.time.sleep"):
            detector = BoardDetector(
                callback=lambda p, m: None,
                poll_interval=0.01,
                list_timeout=3,
            )
            detector._running = True
            call_count = [0]

            def fake_run_once():
                call_count[0] += 1
                detector._running = False
                return False

            detector._run_once = fake_run_once
            detector._run()
            assert call_count[0] == 1


class TestBoardDetectorWatch:
    """Tests for watch-mode BoardDetector (BoardListWatch streaming)."""

    def _make_watch_board(self, port: str, detected: bool, fqbn: str = "", name: str = "") -> Board:
        return Board(
            port=Port(address=port, protocol="serial"),
            fqbn=fqbn,
            name=name,
            detected=detected,
        )

    def _run_watch_and_stop(self, detector, mock_client, timeout=0.3):
        """Run _run_watch in a background thread and stop after timeout."""
        import threading as _t

        t = _t.Thread(target=detector._run_watch, daemon=True)
        detector._running = True
        t.start()
        import time as _t2

        _t2.sleep(timeout)
        detector._running = False
        t.join(timeout=1.0)

    def test_watch_emit_connected_on_board_add(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        detector = BoardDetector(callback=callback, mode="watch")

        mock_client = MagicMock()

        def first_yield_then_raise(*a, **kw):
            yield self._make_watch_board(
                "/dev/ttyACM0",
                detected=True,
                fqbn="arduino:avr:uno",
                name="Arduino Uno",
            )
            raise RuntimeError("stop")

        mock_client.watch_boards = first_yield_then_raise

        with (
            patch(
                "board_manager.board_detector.ArduinoGrpcClient",
                return_value=mock_client,
            ),
            patch("board_manager.board_detector.time.sleep"),
        ):
            self._run_watch_and_stop(detector, mock_client)

        assert len(events) == 1
        port, msg = events[0]
        assert port == "/dev/ttyACM0"
        assert msg["type"] == "event"
        assert msg["data"]["event"] == "connected"
        assert msg["data"]["port"] == "/dev/ttyACM0"
        assert msg["data"]["board"] == "Arduino Uno"
        assert msg["data"]["fqbn"] == "arduino:avr:uno"
        assert "/dev/ttyACM0" in detector._known_boards

    def test_watch_emit_disconnected_on_board_remove(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        detector = BoardDetector(callback=callback, mode="watch")
        detector._known_boards = {
            "/dev/ttyACM0": {
                "port": "/dev/ttyACM0",
                "fqbn": "arduino:avr:uno",
                "name": "Arduino Uno",
            },
        }

        mock_client = MagicMock()

        def first_yield_then_raise(*a, **kw):
            yield self._make_watch_board(
                "/dev/ttyACM0",
                detected=False,
                fqbn="arduino:avr:uno",
                name="Arduino Uno",
            )
            raise RuntimeError("stop")

        mock_client.watch_boards = first_yield_then_raise

        with (
            patch(
                "board_manager.board_detector.ArduinoGrpcClient",
                return_value=mock_client,
            ),
            patch("board_manager.board_detector.time.sleep"),
        ):
            self._run_watch_and_stop(detector, mock_client)

        assert len(events) == 1
        port, msg = events[0]
        assert port == "/dev/ttyACM0"
        assert msg["data"]["event"] == "disconnected"
        assert msg["data"]["port"] == "/dev/ttyACM0"
        assert "/dev/ttyACM0" not in detector._known_boards

    def test_watch_noop_for_duplicate_add(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        detector = BoardDetector(callback=callback, mode="watch")
        detector._known_boards = {
            "/dev/ttyACM0": {
                "port": "/dev/ttyACM0",
                "fqbn": "arduino:avr:uno",
                "name": "Arduino Uno",
            },
        }

        mock_client = MagicMock()

        def first_yield_then_raise(*a, **kw):
            yield self._make_watch_board(
                "/dev/ttyACM0",
                detected=True,
                fqbn="arduino:avr:uno",
                name="Arduino Uno",
            )
            raise RuntimeError("stop")

        mock_client.watch_boards = first_yield_then_raise

        with (
            patch(
                "board_manager.board_detector.ArduinoGrpcClient",
                return_value=mock_client,
            ),
            patch("board_manager.board_detector.time.sleep"),
        ):
            self._run_watch_and_stop(detector, mock_client)

        assert len(events) == 0

    def test_watch_noop_for_unknown_remove(self):
        events = []

        def callback(port, msg):
            events.append((port, msg))

        detector = BoardDetector(callback=callback, mode="watch")

        mock_client = MagicMock()

        def first_yield_then_raise(*a, **kw):
            yield self._make_watch_board("/dev/ttyACM0", detected=False)
            raise RuntimeError("stop")

        mock_client.watch_boards = first_yield_then_raise

        with (
            patch(
                "board_manager.board_detector.ArduinoGrpcClient",
                return_value=mock_client,
            ),
            patch("board_manager.board_detector.time.sleep"),
        ):
            self._run_watch_and_stop(detector, mock_client)

        assert len(events) == 0

    def test_watch_stream_error_reconnects(self):
        mock_client = MagicMock()

        calls = [0]

        def watch_boards_side_effect(*a, **kw):
            calls[0] += 1
            if calls[0] == 1:
                raise RuntimeError("stream dropped")
            yield self._make_watch_board(
                "/dev/ttyACM0",
                detected=True,
                fqbn="arduino:avr:uno",
                name="Arduino Uno",
            )
            raise RuntimeError("stop")

        mock_client.watch_boards = watch_boards_side_effect

        events = []

        def callback(port, msg):
            events.append((port, msg))

        detector = BoardDetector(callback=callback, mode="watch")

        with (
            patch(
                "board_manager.board_detector.ArduinoGrpcClient",
                return_value=mock_client,
            ),
            patch("board_manager.board_detector.time.sleep"),
        ):
            self._run_watch_and_stop(detector, mock_client)

        assert len(events) == 1
        assert events[0][1]["data"]["event"] == "connected"

    def test_start_with_watch_mode(self):
        mock_client = MagicMock()
        mock_client.watch_boards.return_value = iter([])

        def callback(port, msg):
            pass

        with (
            patch(
                "board_manager.board_detector.ArduinoGrpcClient",
                return_value=mock_client,
            ),
            patch("board_manager.board_detector.time.sleep"),
        ):
            detector = BoardDetector(callback=callback, mode="watch")
            detector.start()
            import time

            time.sleep(0.2)
            detector.stop()
            detector._thread.join(timeout=1.0)

            assert mock_client.watch_boards.called
            assert detector._thread is not None
