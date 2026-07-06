"""medminder_dash/python/medminder_dash/tests/test_pubsub.py

Tests for pubsub module.

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


def test_resolve_board_info_includes_hardware_id():
    """_resolve_board_info returns hardware_id from Port.hardware_id."""
    from arduino_grpc.models import Board, Port

    board = Board(
        port=Port(
            address="/dev/ttyACM0", hardware_id="USB VID:PID=2341:0043 SER=12345"
        ),
        fqbn="arduino:avr:uno",
        name="Arduino Uno",
    )

    mock_client = MagicMock()
    mock_client.list_boards.return_value = [board]

    with patch("arduino_grpc.client.ArduinoGrpcClient", return_value=mock_client):
        from medminder_dash.pubsub import _resolve_board_info

        result = _resolve_board_info("/dev/ttyACM0")
        assert result["hardware_id"] == "USB VID:PID=2341:0043 SER=12345"
        assert result["board"] == "Arduino Uno"
        assert result["fqbn"] == "arduino:avr:uno"


def test_resolve_board_info_empty_hardware_id():
    """_resolve_board_info handles empty hardware_id gracefully."""
    from arduino_grpc.models import Board, Port

    board = Board(
        port=Port(address="/dev/ttyACM0", hardware_id=""),
        fqbn="arduino:avr:uno",
        name="Arduino Uno",
    )

    mock_client = MagicMock()
    mock_client.list_boards.return_value = [board]

    with patch("arduino_grpc.client.ArduinoGrpcClient", return_value=mock_client):
        from medminder_dash.pubsub import _resolve_board_info

        result = _resolve_board_info("/dev/ttyACM0")
        assert result["hardware_id"] == ""
        assert result["board"] == "Arduino Uno"


def test_resolve_board_info_empty_on_exception():
    """_resolve_board_info returns empty fields on exception."""
    with patch("arduino_grpc.client.ArduinoGrpcClient") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.connect.side_effect = Exception("connection failed")
        mock_cls.return_value = mock_instance

        from medminder_dash.pubsub import _resolve_board_info

        result = _resolve_board_info("/dev/ttyACM0")
        assert result == {"board": "", "fqbn": "", "hardware_id": ""}


def test_get_port_info_returns_hardware_id():
    """get_port_info returns hardware_id when stored in _known_ports."""
    from medminder_dash.utils import get_port_info

    from medminder_dash import state

    entry = {
        "port": "/dev/ttyACM0",
        "event": "connected",
        "board": "Arduino Uno",
        "fqbn": "arduino:avr:uno",
        "hardware_id": "USB VID:PID=2341:0043 SER=12345",
    }

    with state._known_ports_lock:
        state._known_ports["/dev/ttyACM0"] = entry

    try:
        result = get_port_info("/dev/ttyACM0")
        assert result is not None
        assert result["hardware_id"] == "USB VID:PID=2341:0043 SER=12345"
    finally:
        with state._known_ports_lock:
            state._known_ports.pop("/dev/ttyACM0", None)

