"""medminder_dash/python/medminder_dash/tests/test_routes.py

Tests for HTML and API routes.

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

from unittest.mock import patch

import pytest
from medminder_dash.app import create_app
from medminder_dash.medicines_state import Medicine


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        from medminder_dash.app import store

        store._board_meta.clear()
        store._lock = __import__("threading").Lock()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_store(app, client):
    """Set board and add medicines directly to its meta."""
    from medminder_dash.app import store

    m1 = Medicine(name="Ibup", hour=8, minute=30, day_of_week=1, day_of_month=0)
    m2 = Medicine(name="PaRa", hour=20, minute=0, day_of_week=3, day_of_month=0)
    store._board_meta["TestBoard"] = {"medicines": [m1, m2]}
    with client.session_transaction() as sess:
        sess["board_port"] = "TestBoard"
    return m1


@pytest.fixture
def board(client):
    """Set a board in the session so CRUD routes pass the board guard."""
    with client.session_transaction() as sess:
        sess["board_port"] = "TestBoard"
    yield


class TestIndex:
    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"MedMinder" in resp.data

    def test_index_shows_count_zero(self, client):
        resp = client.get("/")
        assert b"No medicines scheduled yet" in resp.data or b"0 medicines" in resp.data


class TestListMedicines:
    def test_empty_list(self, client, board):
        resp = client.get("/medicines")
        assert resp.status_code == 200
        assert b"No medicines scheduled yet" in resp.data

    def test_lists_medicines(self, client, seeded_store):
        resp = client.get("/medicines")
        assert resp.status_code == 200
        assert b"Ibup" in resp.data
        assert b"PaRa" in resp.data


class TestCreateMedicineForm:
    def test_new_form_returns_200(self, client):
        resp = client.get("/medicine/new")
        assert resp.status_code == 200
        assert b"Add Medicine" in resp.data


class TestCreateMedicine:
    def test_create_valid_medicine(self, client, board):
        resp = client.post(
            "/medicine",
            data={
                "name": "Test",
                "hour": "12",
                "minute": "30",
                "day_of_week": "2",
                "day_of_month": "0",
            },
        )
        assert resp.status_code == 200
        assert b"Test" in resp.data
        assert b"medicine-list" in resp.data

    def test_create_missing_name(self, client, board):
        resp = client.post(
            "/medicine",
            data={
                "name": "",
                "hour": "12",
                "minute": "30",
            },
        )
        assert resp.status_code == 400
        assert b"Name is required" in resp.data

    def test_create_invalid_hour(self, client, board):
        resp = client.post(
            "/medicine",
            data={
                "name": "Test",
                "hour": "25",
                "minute": "30",
            },
        )
        assert resp.status_code == 400
        assert b"Hour must be 1-24" in resp.data

    def test_create_invalid_minute(self, client, board):
        resp = client.post(
            "/medicine",
            data={
                "name": "Test",
                "hour": "8",
                "minute": "15",
            },
        )
        assert resp.status_code == 400
        assert b"Minute must be" in resp.data

    def test_create_name_too_long(self, client, board):
        resp = client.post(
            "/medicine",
            data={
                "name": "TooLongName",
                "hour": "8",
                "minute": "0",
            },
        )
        assert resp.status_code == 400
        assert b"Name must be 10 characters" in resp.data


class TestEditMedicineForm:
    def test_edit_form_returns_200(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.get(f"/medicine/{med_id}/edit")
        assert resp.status_code == 200
        assert b"Ibup" in resp.data
        assert b"Edit" in resp.data

    def test_edit_form_404(self, client):
        resp = client.get("/medicine/nonexistent/edit")
        assert resp.status_code == 404


class TestUpdateMedicine:
    def test_update_medicine(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.put(
            f"/medicine/{med_id}",
            data={
                "name": "Ibup",
                "hour": "9",
                "minute": "0",
                "day_of_week": "1",
                "day_of_month": "0",
            },
        )
        assert resp.status_code == 200
        assert b"Ibup" in resp.data
        from medminder_dash.app import store

        meds = store._board_meta.get("TestBoard", {}).get("medicines", [])
        updated = next((m for m in meds if m.id == med_id), None)
        assert updated is not None
        assert updated.hour == 9
        assert updated.minute == 0

    def test_update_invalid(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.put(
            f"/medicine/{med_id}",
            data={
                "name": "",
                "hour": "99",
                "minute": "15",
            },
        )
        assert resp.status_code == 400

    def test_update_404(self, client, board):
        resp = client.put(
            "/medicine/nonexistent", data={"name": "x", "hour": "1", "minute": "0"}
        )
        assert resp.status_code == 404


class TestDeleteMedicine:
    def test_delete_medicine(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.delete(f"/medicine/{med_id}")
        assert resp.status_code == 200
        assert b"medicine-list" in resp.data
        from medminder_dash.app import store

        assert store.get(med_id) is None

    def test_delete_404(self, client, board):
        resp = client.delete("/medicine/nonexistent")
        assert resp.status_code == 404


class TestToggleMedicine:
    def test_toggle_disables(self, client, seeded_store):
        med_id = seeded_store.id
        assert seeded_store.enabled is True
        resp = client.put(f"/medicine/{med_id}/toggle")
        assert resp.status_code == 200
        assert b"medicine-list" in resp.data
        from medminder_dash.app import store

        meds = store._board_meta.get("TestBoard", {}).get("medicines", [])
        toggled = next((m for m in meds if m.id == med_id), None)
        assert toggled is not None
        assert toggled.enabled is False

    def test_toggle_enables(self, client, seeded_store):
        med_id = seeded_store.id
        from medminder_dash.app import store

        meds = store._board_meta.get("TestBoard", {}).get("medicines", [])
        target = next((m for m in meds if m.id == med_id), None)
        assert target is not None
        target.enabled = False
        resp = client.put(f"/medicine/{med_id}/toggle")
        assert resp.status_code == 200
        assert b"medicine-list" in resp.data
        meds = store._board_meta.get("TestBoard", {}).get("medicines", [])
        toggled = next((m for m in meds if m.id == med_id), None)
        assert toggled is not None
        assert toggled.enabled is True


class TestAdminSketchDir:
    """Legacy tests for the old /admin/sketch-dir route. Removed in Phase 60.
    The functionality is now provided by the merged /admin page.
    Placeholder class to maintain test count documentation in git history."""


class TestBoardDetailFqbn:
    def test_fqbn_prepopulated_from_board_info(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Arduino Uno",
                "fqbn": "arduino:avr:mega",
            }
        try:
            resp = client.get("/board/dev/ttyACM0")
            assert resp.status_code == 200
            assert b'value="arduino:avr:mega"' in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

    def test_fqbn_default_when_no_board_info(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports.pop("/dev/ttyACM0", None)
        resp = client.get("/board/dev/ttyACM0")
        assert resp.status_code == 200
        assert b'value="arduino:avr:uno"' in resp.data

    def test_heading_shows_board_name(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Arduino Uno",
                "fqbn": "arduino:avr:mega",
            }
        try:
            resp = client.get("/board/dev/ttyACM0")
            assert resp.status_code == 200
            assert b"<h2" in resp.data
            assert b"Board: Arduino Uno" in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

    def test_heading_falls_back_to_port(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports.pop("/dev/ttyACM0", None)
        resp = client.get("/board/dev/ttyACM0")
        assert resp.status_code == 200
        assert b"<h2" in resp.data
        assert b"Board: /dev/ttyACM0" in resp.data

    def test_fqbn_display_label_present(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Arduino Uno",
                "fqbn": "arduino:avr:mega",
            }
        try:
            resp = client.get("/board/dev/ttyACM0")
            assert resp.status_code == 200
            assert b'id="fqbn-display"' in resp.data
            assert b"arduino:avr:mega" in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

    def test_port_display_label_present(self, client):
        resp = client.get("/board/dev/ttyACM0")
        assert resp.status_code == 200
        assert b'id="port-display"' in resp.data
        assert b"Device Port" in resp.data
        assert b"/dev/ttyACM0" in resp.data

    def test_sketch_path_uses_per_board_assignment(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "arduino:avr:uno",
                "hardware_id": "USB VID:PID=2341:0043 SER=12345",
            }
        try:
            per_board_path = "/home/user/per-board-sketch"
            with patch(
                "medminder_dash.html_routes.get_board_sketch_assignment",
                return_value=per_board_path,
            ):
                resp = client.get("/board/dev/ttyACM0")
            assert resp.status_code == 200
            assert b'id="sketch-path-container"' in resp.data
            assert b'hx-get="/last-upload"' in resp.data
            assert b'hx-include="#active-board-hardware-id"' in resp.data
            assert b"USB VID:PID=2341:0043 SER=12345" in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

    def test_sketch_path_falls_back_to_default(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "arduino:avr:uno",
                "hardware_id": "USB VID:PID=2341:0043 SER=12345",
            }
        try:
            with patch(
                "medminder_dash.html_routes.get_board_sketch_assignment",
                return_value=None,
            ):
                resp = client.get("/board/dev/ttyACM0")
            assert resp.status_code == 200
            assert b'id="sketch-path-container"' in resp.data
            assert b'hx-get="/last-upload"' in resp.data
            assert b'hx-include="#active-board-hardware-id"' in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

    def test_sketch_path_uses_default_for_no_hardware_id(self, client):
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "arduino:avr:uno",
                "hardware_id": "",
            }
        try:
            resp = client.get("/board/dev/ttyACM0")
            assert resp.status_code == 200
            assert b'id="sketch-path-container"' in resp.data
            assert b'hx-get="/last-upload"' in resp.data
            assert b'hx-include="#active-board-hardware-id"' in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)


class TestDaemonStatus:
    def test_daemon_status_not_ready(self, client):
        resp = client.get("/daemon/status")
        assert resp.status_code == 200
        assert b"daemon-off" in resp.data

    def test_daemon_status_ready(self, client, monkeypatch):
        from medminder_dash import state

        monkeypatch.setattr("medminder_dash.html_routes.is_connected", lambda: True)
        state._daemon_ready = True
        try:
            resp = client.get("/daemon/status")
            assert resp.status_code == 200
            assert b"daemon-on" in resp.data
        finally:
            state._daemon_ready = False


class TestBoardSelect:
    def test_board_select_redirect(self, client):
        resp = client.get("/board/select/dev/ttyACM0")
        assert resp.status_code == 302
        assert "/board/dev/ttyACM0" in resp.location


class TestBoardRedirect:
    def test_board_redirect_no_session(self, client):
        resp = client.get("/board")
        assert resp.status_code == 400
        assert b"No board selected" in resp.data

    def test_board_redirect_with_session(self, client):
        with client.session_transaction() as sess:
            sess["board_port"] = "TestPort"
        resp = client.get("/board")
        assert resp.status_code == 302


class TestBoardConnectionStatus:
    def test_connection_status_disconnected(self, client):
        with patch("medminder_dash.html_routes.get_port_info", return_value=None):
            resp = client.get("/board/dev/ttyACM0/connection-status")
            assert resp.status_code == 200
            assert b"Disconnected" in resp.data

    def test_connection_status_connected(self, client):
        from medminder_dash import state

        with state._known_ports_lock:
            state._known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Test",
            }
        try:
            resp = client.get("/board/dev/ttyACM0/connection-status")
            assert resp.status_code == 200
            assert b"Connected" in resp.data
        finally:
            with state._known_ports_lock:
                state._known_ports.pop("/dev/ttyACM0", None)


class TestBoards:
    def test_boards_empty(self, client):
        resp = client.get("/boards")
        assert resp.status_code == 200


class TestBoardsEvent:
    def test_boards_event_empty(self, client):
        resp = client.get("/api/boards/events")
        assert resp.status_code == 200
        assert resp.get_json() == []


class TestBoardsGrid:
    def test_boards_grid_empty(self, client):
        resp = client.get("/boards/grid")
        assert resp.status_code == 200


class TestNormalizePort:
    def test_normalizes_with_dev_prefix(self):
        from medminder_dash.utils import normalize_port

        assert normalize_port("dev/ttyACM0") == "/dev/ttyACM0"

    def test_strips_extra_slashes(self):
        from medminder_dash.utils import normalize_port

        assert normalize_port("//dev/ttyACM0") == "/dev/ttyACM0"

    def test_keeps_valid(self):
        from medminder_dash.utils import normalize_port

        assert normalize_port("/dev/ttyACM0") == "/dev/ttyACM0"

    def test_rejects_empty(self):
        from medminder_dash.utils import normalize_port

        assert normalize_port("") is None

    def test_rejects_bare_port(self):
        from medminder_dash.utils import normalize_port

        assert normalize_port("ttyACM0") is None  # /ttyACM0 doesn't match /dev/...

    def test_rejects_non_dev_path(self):
        from medminder_dash.utils import normalize_port

        assert normalize_port("COM1") is None
        assert normalize_port("/random/path") is None

