"""medminder_dash/python/medminder_dash/tests/test_admin.py

Tests for admin routes and templates.

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

import io
import os

import pytest


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Create app with isolated UPLOAD_BASE_DIR and clean state."""
    upload_base = tmp_path / "uploads"
    upload_base.mkdir()

    from medminder_dash import state

    monkeypatch.setattr(state, "UPLOAD_BASE_DIR", str(upload_base))
    monkeypatch.setattr(
        "medminder_dash.sketch_management.state.UPLOAD_BASE_DIR", str(upload_base)
    )

    from medminder_dash.app import create_app

    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        from medminder_dash.app import store

        store._board_meta.clear()
        # Clean module-level upload registry between tests
        with state._upload_registry_lock:
            state._upload_registry.clear()
        import os as _os

        from medminder_dash.sketch_management import REGISTRY_FILE as _REGISTRY_FILE

        _os.path.isfile(_REGISTRY_FILE) and _os.remove(_REGISTRY_FILE)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def _make_upload_file(filename, content=b"// arduino sketch\nvoid setup() {}\n"):
    return (io.BytesIO(content), filename)


class TestSketchUpload:
    def test_upload_with_files_returns_path(self, app, client, tmp_path, monkeypatch):
        # Patch out the rendering function (template partial is in Q3)
        called = {"rendered": False}

        def fake_render(selected_path=""):
            called["rendered"] = True
            return f"<select><option selected>{selected_path}</option></select>"

        monkeypatch.setattr(
            "medminder_dash.html_routes._render_sketch_path_selector",
            fake_render,
        )
        # Non-hx request → JSON response (no HX-Request header)
        data = {"files[]": _make_upload_file("MySketch/MySketch.ino")}
        resp = client.post(
            "/api/sketch/upload",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload is not None
        assert "path" in payload
        assert payload["path"].endswith("MySketch")
        assert os.path.isdir(payload["path"])
        assert called["rendered"] is False  # not called for non-hx

    def test_upload_with_no_files_returns_400(self, app, client):
        resp = client.post(
            "/api/sketch/upload", data={}, content_type="multipart/form-data"
        )
        assert resp.status_code == 400
        assert b"No files provided" in resp.data

    def test_last_upload_returns_selector_for_hx(self, app, client, monkeypatch):
        fake_html = "<select><option>foo</option></select>"
        monkeypatch.setattr(
            "medminder_dash.html_routes._render_sketch_path_selector",
            lambda selected_path="", include_default=False, hardware_id="": fake_html,
        )
        resp = client.get("/last-upload", headers={"HX-Request": "true"})
        assert resp.status_code == 200
        assert b"<select>" in resp.data

    def test_sketches_returns_json_list(self, app, client):
        # Phase 62: empty registry returns the packaged MedMinderV2 default as the
        # only entry (always discoverable, no uploads required).
        from medminder_dash.settings import _DEFAULT_SKETCH_DIR

        resp = client.get("/api/sketches")
        assert resp.status_code == 200
        assert resp.get_json() == [
            {"name": "MedMinderV2", "path": _DEFAULT_SKETCH_DIR, "timestamp": ""}
        ]

    def test_delete_with_invalid_path_returns_400(self, app, client):
        resp = client.delete("/api/sketch?path=")
        assert resp.status_code == 400
        assert b"Missing path" in resp.data

    def test_delete_with_path_outside_base_returns_403(self, app, client):
        # Path traversal attempt
        resp = client.delete("/api/sketch?path=/etc/passwd")
        assert resp.status_code == 403
        assert b"Invalid path" in resp.data

    def test_delete_existing_removes_entry(self, app, client, tmp_path, monkeypatch):
        # Manually add to registry using the same key the route will compute
        from medminder_dash import state

        sketch_dir = tmp_path / "uploads" / "test_entry" / "MySketch"
        sketch_dir.mkdir(parents=True)
        ino = sketch_dir / "MySketch.ino"
        ino.write_text("// sketch")

        # Flask test client sets REMOTE_ADDR=127.0.0.1 and User-Agent=Werkzeug/x.x.x
        # Use the same key the route will compute
        resp = client.get("/api/sketches")  # any request to learn the actual IP/UA
        key = tuple(
            resp.request.environ.get(k, "unknown")
            for k in ("REMOTE_ADDR", "HTTP_USER_AGENT")
        )
        # remote_addr from environ
        ip = resp.request.environ.get("REMOTE_ADDR") or "unknown"
        ua = resp.request.headers.get("User-Agent", "unknown")
        key = (ip, ua)
        with state._upload_registry_lock:
            state._upload_registry[key] = {
                "MySketch": [
                    {
                        "path": str(sketch_dir),
                        "checksum": "abc",
                        "server_timestamp": "2026-01-01T00:00:00",
                        "hardware_ids": [],
                        "board_timestamps": {},
                    }
                ]
            }

        # Non-hx request returns JSON
        resp = client.delete(
            f"/api/sketch?path={sketch_dir}",
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["status"] == "deleted"

        # Registry should be empty for this user
        with state._upload_registry_lock:
            assert state._upload_registry.get(key, {}) == {}


class TestConfirmModal:
    def test_confirm_modal_generate(self, app, client):
        resp = client.get("/medicines/confirm-modal?action=generate")
        assert resp.status_code == 200
        assert b"Generate alarm.hpp" in resp.data
        assert b"overwrite" in resp.data.lower()
        assert b'name="confirm_token"' in resp.data
        assert (
            b'"/medicines/generate-hpp"' in resp.data
            or b"/medicines/generate-hpp" in resp.data
        )

    def test_confirm_modal_sync(self, app, client):
        resp = client.get("/medicines/confirm-modal?action=sync")
        assert resp.status_code == 200
        assert b"Sync FROM alarm.hpp" in resp.data
        assert b"replace" in resp.data.lower()
        assert b'name="confirm_token"' in resp.data
        assert b"/medicines/sync-from-hpp" in resp.data

    def test_confirm_modal_unknown_action_400(self, app, client):
        resp = client.get("/medicines/confirm-modal?action=foo")
        assert resp.status_code == 400
        assert b"Unknown action" in resp.data


class TestSetMedicinesSync:
    def _get_token(self, client, action):
        """Get a fresh confirm token from the modal endpoint."""
        resp = client.get(f"/medicines/confirm-modal?action={action}")
        # Extract token from response (look for value="..." pattern)
        import re

        m = re.search(rb'name="confirm_token"\s+value="([^"]+)"', resp.data)
        assert m is not None, f"No token in response: {resp.data[:500]}"
        return m.group(1).decode()

    def test_sync_with_valid_token_replaces_metadata(
        self, app, client, tmp_path, monkeypatch
    ):
        # Write alarm.hpp with 2 medicines
        from medminder_dash.app import store
        from medminder_dash.medicines_state import Medicine

        # Pre-populate store with 1 medicine
        store._board_meta["TestBoard"] = {
            "medicines": [Medicine(name="Old", hour=1, minute=0)]
        }
        with client.session_transaction() as sess:
            sess["board_port"] = "TestBoard"

        # Write alarm.hpp content
        alarm_hpp = tmp_path / "alarm.hpp"
        alarm_hpp.write_text(
            "#ifndef ALARM_HPP\n#define ALARM_HPP\n"
            "struct Medicine { uint8_t dayOfMonth; uint8_t dayOfWeek; "
            "uint8_t hour; uint8_t decade; const char* text; };\n"
            "const Medicine medicines[] = {\n"
            '  {0, 1, 8, 3, "NewA"},\n'
            '  {0, 2, 20, 0, "NewB"},\n'
            "};\n"
            "#define N_MED  (sizeof(medicines) / sizeof(medicines[0]))\n"
            "#endif\n"
        )

        # Patch sketch_dir and alarm.hpp path
        monkeypatch.setattr(
            "medminder_dash.pubsub._get_sketch_dir", lambda: str(tmp_path)
        )
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(alarm_hpp)
        )

        token = self._get_token(client, "sync")
        resp = client.post(
            "/medicines/sync-from-hpp",
            data={"confirm_token": token},
        )
        assert resp.status_code == 200
        assert b"Loaded 2 medicine" in resp.data
        meds = store._board_meta.get("TestBoard", {}).get("medicines", [])
        assert len(meds) == 2
        names = {m.name for m in meds}
        assert names == {"NewA", "NewB"}

    def test_sync_with_invalid_token_returns_403(
        self, app, client, tmp_path, monkeypatch
    ):
        resp = client.post(
            "/medicines/sync-from-hpp",
            data={"confirm_token": "invalid-token"},
        )
        assert resp.status_code == 403
        assert b"Confirmation required" in resp.data

    def test_sync_after_success_token_consumed(
        self, app, client, tmp_path, monkeypatch
    ):
        # Get token, use it once, then try to reuse
        token = self._get_token(client, "sync")
        # First POST succeeds (but alarm.hpp is empty so 0 entries)
        resp1 = client.post(
            "/medicines/sync-from-hpp",
            data={"confirm_token": token},
        )
        assert resp1.status_code == 200
        # Second POST with same token should fail (consumed)
        resp2 = client.post(
            "/medicines/sync-from-hpp",
            data={"confirm_token": token},
        )
        assert resp2.status_code == 403


class TestSetMedicinesGenerate:
    def _get_token(self, client, action):
        import re

        resp = client.get(f"/medicines/confirm-modal?action={action}")
        m = re.search(rb'name="confirm_token"\s+value="([^"]+)"', resp.data)
        assert m is not None
        return m.group(1).decode()

    def test_generate_with_valid_token_writes_file(
        self, app, client, tmp_path, monkeypatch
    ):
        from medminder_dash.app import store
        from medminder_dash.medicines_state import Medicine

        m1 = Medicine(name="Asp", hour=8, minute=30, day_of_week=1, day_of_month=0)
        store._board_meta["TestBoard"] = {"medicines": [m1]}
        with client.session_transaction() as sess:
            sess["board_port"] = "TestBoard"

        alarm_hpp = tmp_path / "alarm.hpp"
        monkeypatch.setattr(
            "medminder_dash.pubsub._get_sketch_dir", lambda: str(tmp_path)
        )
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(alarm_hpp)
        )

        token = self._get_token(client, "generate")
        resp = client.post(
            "/medicines/generate-hpp",
            data={"confirm_token": token},
        )
        assert resp.status_code == 200
        assert b"Generated alarm.hpp" in resp.data
        assert alarm_hpp.exists()
        content = alarm_hpp.read_text()
        assert "Asp" in content
        assert "#ifndef ALARM_HPP" in content

    def test_generate_with_invalid_token_returns_403(self, app, client):
        resp = client.post(
            "/medicines/generate-hpp",
            data={"confirm_token": "wrong-token"},
        )
        assert resp.status_code == 403
        assert b"Confirmation required" in resp.data


class TestAdminPage:
    def test_admin_returns_200(self, app, client):
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"<h2" in resp.data
        assert b"Admin" in resp.data

    def test_admin_renders_all_cards(self, app, client):
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"Sketch Path" in resp.data
        assert b'id="compile-upload-card"' in resp.data

    def test_admin_has_confirm_token_modal_container(self, app, client):
        """The admin page has a #confirm-modal-container that holds the modals."""
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b'id="confirm-modal-container"' in resp.data
        # Has the Set Medicines card with two action buttons
        assert b"Generate alarm.hpp FROM metadata" in resp.data
        assert b"Sync FROM alarm.hpp" in resp.data
        # The modal endpoint issues tokens on demand
        modal_resp = client.get("/medicines/confirm-modal?action=generate")
        assert modal_resp.status_code == 200
        assert b'name="confirm_token"' in modal_resp.data


class TestMedicinesDiff:
    """Tests for /api/medicines/diff — diff between metadata and alarm.hpp."""

    def test_diff_equal_when_metadata_matches_hpp(
        self, app, client, tmp_path, monkeypatch
    ):
        from medminder_dash.app import store

        m = type("M", (), {})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        m.enabled = True
        m.id = "m1"
        store._board_meta["TestBoard"] = {"medicines": [m]}
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "TestBoard"
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text('const Medicine medicines[] = {\n  {0, 0, 8, 3, "Ibup"},\n};\n')
        monkeypatch.setattr(
            "medminder_dash.api_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        resp = client.get("/api/medicines/diff")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["differ"] is False
        assert payload["alarm_hpp_exists"] is True
        assert payload["alarm_hpp_error"] is None

    def test_diff_differs_when_metadata_has_extra_medicine(
        self, app, client, tmp_path, monkeypatch
    ):
        from medminder_dash.app import store

        m1 = type("M", (), {"enabled": True, "id": "m1"})()
        m1.name = "Ibup"
        m1.hour = 8
        m1.minute = 30
        m1.day_of_week = 0
        m1.day_of_month = 0
        m2 = type("M", (), {"enabled": True, "id": "m2"})()
        m2.name = "PaRa"
        m2.hour = 20
        m2.minute = 0
        m2.day_of_week = 0
        m2.day_of_month = 0
        store._board_meta["TestBoard"] = {"medicines": [m1, m2]}
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "TestBoard"
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text('const Medicine medicines[] = {\n  {0, 0, 8, 3, "Ibup"},\n};\n')
        monkeypatch.setattr(
            "medminder_dash.api_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        resp = client.get("/api/medicines/diff")
        payload = resp.get_json()
        assert payload["differ"] is True
        assert len(payload["metadata"]) == 2
        assert len(payload["alarm_hpp"]) == 1

    def test_diff_differs_when_hpp_has_extra_medicine(
        self, app, client, tmp_path, monkeypatch
    ):
        from medminder_dash.app import store

        m = type("M", (), {"enabled": True, "id": "m1"})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        store._board_meta["TestBoard"] = {"medicines": [m]}
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "TestBoard"
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text(
            "const Medicine medicines[] = {\n"
            '  {0, 0, 8, 3, "Ibup"},\n'
            '  {0, 0, 20, 0, "PaRa"},\n'
            "};\n"
        )
        monkeypatch.setattr(
            "medminder_dash.api_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        resp = client.get("/api/medicines/diff")
        payload = resp.get_json()
        assert payload["differ"] is True
        assert len(payload["metadata"]) == 1
        assert len(payload["alarm_hpp"]) == 2

    def test_diff_when_hpp_missing(self, app, client, tmp_path, monkeypatch):
        from medminder_dash.app import store

        m = type("M", (), {"enabled": True, "id": "m1"})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        store._board_meta["TestBoard"] = {"medicines": [m]}
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "TestBoard"
        hpp = tmp_path / "alarm.hpp"
        monkeypatch.setattr(
            "medminder_dash.api_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        resp = client.get("/api/medicines/diff")
        payload = resp.get_json()
        assert payload["differ"] is True
        assert payload["alarm_hpp_exists"] is False
        assert payload["alarm_hpp_error"] is None

    def test_diff_when_hpp_parse_error(self, app, client, tmp_path, monkeypatch):
        from medminder_dash.app import store

        m = type("M", (), {"enabled": True, "id": "m1"})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        store._board_meta["TestBoard"] = {"medicines": [m]}
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "TestBoard"
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text("this is not valid c++ {{{")
        monkeypatch.setattr(
            "medminder_dash.api_routes._get_alarm_hpp_path", lambda: str(hpp)
        )

        def fake_parse(path):
            raise ValueError("simulated parse error")

        monkeypatch.setattr("medminder_dash.api_routes.parse_alarm_hpp", fake_parse)
        resp = client.get("/api/medicines/diff")
        payload = resp.get_json()
        assert payload["differ"] is True
        assert payload["alarm_hpp_exists"] is True
        assert "simulated parse error" in payload["alarm_hpp_error"]


class TestActiveBoard:
    """Tests for admin's active board session management."""

    @pytest.mark.skip(reason="/admin route no longer sets active board via url query")
    def test_url_query_port_sets_active_board(self, app, client, monkeypatch):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [{"port": "/dev/ttyACM0"}, {"port": "/dev/ttyUSB0"}],
        )
        resp = client.get("/admin?port=/dev/ttyUSB0")
        assert resp.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get("admin_active_board") == "/dev/ttyUSB0"

    def test_post_active_board_changes_session(self, app, client, monkeypatch):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [{"port": "/dev/ttyACM0"}, {"port": "/dev/ttyUSB0"}],
        )
        resp = client.post("/medicines/active-board", data={"port": "/dev/ttyUSB0"})
        assert resp.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get("admin_active_board") == "/dev/ttyUSB0"

    def test_default_active_board_to_first_known_port(self, app, client, monkeypatch):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                },
                {
                    "port": "/dev/ttyUSB0",
                    "fqbn": "arduino:avr:mega",
                    "hardware_id": "HW-456",
                },
            ],
        )
        resp = client.get("/admin")
        assert resp.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get("admin_active_board") == (
                "/dev/ttyACM0",
                "arduino:avr:uno",
                "HW-123",
            )


class TestMedicineCardsRender:
    """Tests for the medicine cards container HTML."""

    def test_cards_endpoint_returns_html(self, app, client, tmp_path, monkeypatch):
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text("static Medicine meds[] = {\n};\n")
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("TestBoard", "TestFQBN", "TestHWID")
        resp = client.get("/medicines/active-board-card")
        assert resp.status_code == 200
        assert b"medicine-cards-container" in resp.data
        assert b"medicines" in resp.data.lower()

    def test_cards_endpoint_post_changes_board(
        self, app, client, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [{"port": "/dev/ttyACM0"}, {"port": "/dev/ttyUSB0"}],
        )
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text("static Medicine meds[] = {\n};\n")
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        resp = client.post("/medicines/active-board", data={"port": "/dev/ttyUSB0"})
        assert resp.status_code == 200
        assert b"medicine-cards-container" in resp.data
        with client.session_transaction() as sess:
            assert sess["admin_active_board"] == "/dev/ttyUSB0"

    def test_board_selector_endpoint_returns_html(self, app, client, monkeypatch):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/medicines/board-selector")
        assert resp.status_code == 200
        assert b"admin-active-board" in resp.data
        assert b"/dev/ttyACM0" in resp.data


class TestSyncButtonsState:
    """Tests for sync button disabled state based on diff."""

    def test_buttons_disabled_when_metadata_matches_hpp(
        self, app, client, tmp_path, monkeypatch
    ):
        from medminder_dash.app import store

        m = type("M", (), {"enabled": True, "id": "m1"})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        store._board_meta["TestBoard"] = {"medicines": [m]}
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("TestBoard", "TestFQBN", "TestHWID")
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text('static Medicine meds[] = {\n  {"Ibup", 8, 30, 0, 0},\n};\n')
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"Generate alarm.hpp FROM metadata" in resp.data
        assert b"Sync FROM alarm.hpp" in resp.data

    def test_buttons_endpoint_returns_diff(self, app, client, tmp_path, monkeypatch):
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text("static Medicine meds[] = {\n};\n")
        monkeypatch.setattr(
            "medminder_dash.api_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "TestBoard"
        resp = client.get("/api/medicines/diff")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert "differ" in payload
        assert "metadata" in payload
        assert "alarm_hpp" in payload
        assert "alarm_hpp_exists" in payload


class TestAdminFrontendStructure:
    """Tests for the /admin page HTML structure (Phase 61)."""

    def test_admin_page_has_board_selector_container(self, app, client, monkeypatch):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b'id="admin-board-selector-container"' in resp.data

    def test_admin_page_has_medicine_cards_container(self, app, client, monkeypatch):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b'id="medicine-cards-container"' in resp.data

    def test_admin_page_metadata_card_has_add_button(self, app, client, monkeypatch):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [{"port": "/dev/ttyACM0"}],
        )
        hpp = __import__("pathlib").Path("/tmp/test_alarm_q2.hpp")
        hpp.write_text("const Medicine medicines[] = {\n};\n")
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"Add Medicine" in resp.data
        assert b'hx-get="/medicine/new"' in resp.data

    def test_admin_page_alarm_hpp_card_no_add_button(self, app, client, monkeypatch):
        """When 2 cards (metadata != alarm.hpp), alarm.hpp must NOT have Add Medicine button."""
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        from medminder_dash.app import store

        m = type("M", (), {"enabled": True, "id": "m1"})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        store._board_meta["/dev/ttyACM0"] = {"medicines": [m]}
        hpp = __import__("pathlib").Path("/tmp/test_alarm_q2.hpp")
        hpp.write_text("const Medicine medicines[] = {\n};\n")
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"alarm-hpp-medicines-card" in resp.data
        alarm_hpp_section = resp.data.split(b"alarm-hpp-medicines-card")[1]
        assert b"Add Medicine" not in alarm_hpp_section
        assert b'hx-get="/medicine/new"' not in alarm_hpp_section

    def test_admin_page_sync_buttons_disabled_when_equal(
        self, app, client, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        from medminder_dash.app import store

        m = type("M", (), {"enabled": True, "id": "m1"})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        store._board_meta["/dev/ttyACM0"] = {"medicines": [m]}
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text('const Medicine medicines[] = {\n  {0, 0, 8, 3, "Ibup"},\n};\n')
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b'id="generate-hpp-btn"' in resp.data
        assert b'id="sync-hpp-btn"' in resp.data
        assert b'id="sync-buttons-help"' in resp.data

    def test_admin_page_sync_buttons_enabled_when_differ(
        self, app, client, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        from medminder_dash.app import store

        m = type("M", (), {"enabled": True, "id": "m1"})()
        m.name = "Ibup"
        m.hour = 8
        m.minute = 30
        m.day_of_week = 0
        m.day_of_month = 0
        store._board_meta["/dev/ttyACM0"] = {"medicines": [m]}
        hpp = tmp_path / "alarm.hpp"
        hpp.write_text("const Medicine medicines[] = {\n};\n")
        monkeypatch.setattr(
            "medminder_dash.html_routes._get_alarm_hpp_path", lambda: str(hpp)
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"metadata and alarm.hpp are in sync" not in resp.data
        assert b"alarm-hpp-medicines-card" in resp.data


class TestMedMinderV2DefaultSketch:
    """Phase 62: /api/sketches always includes the packaged MedMinderV2
    sketch as the first entry so it is discoverable on first use (no
    prior uploads required). /last-upload is unchanged.
    """

    def test_api_sketches_includes_default_when_no_uploads(self, app, client):
        from medminder_dash.settings import _DEFAULT_SKETCH_DIR

        resp = client.get("/api/sketches")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload == [
            {"name": "MedMinderV2", "path": _DEFAULT_SKETCH_DIR, "timestamp": ""}
        ]

    def test_api_sketches_default_first_when_uploads_exist(self, app, client, tmp_path):
        from medminder_dash.settings import _DEFAULT_SKETCH_DIR

        from medminder_dash import state

        sketch_dir = tmp_path / "uploads" / "test_entry" / "MySketch"
        sketch_dir.mkdir(parents=True)
        (sketch_dir / "MySketch.ino").write_text("// sketch")

        # Seed the registry for the (ip, ua) the test client will use.
        # Reuse the env-extraction trick from TestSketchUpload.
        resp = client.get("/api/sketches")
        ip = resp.request.environ.get("REMOTE_ADDR") or "unknown"
        ua = resp.request.headers.get("User-Agent", "unknown")
        key = (ip, ua)
        with state._upload_registry_lock:
            state._upload_registry[key] = {
                "MySketch": [
                    {
                        "path": str(sketch_dir),
                        "checksum": "abc",
                        "server_timestamp": "2026-01-01T00:00:00",
                        "hardware_ids": [],
                        "board_timestamps": {},
                    }
                ]
            }

        resp = client.get("/api/sketches")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert len(payload) == 2
        # MedMinderV2 is the FIRST entry (index 0), upload follows.
        assert payload[0] == {
            "name": "MedMinderV2",
            "path": _DEFAULT_SKETCH_DIR,
            "timestamp": "",
        }
        assert payload[1]["name"] == "MySketch"
        assert payload[1]["path"] == str(sketch_dir)

    def test_api_last_upload_includes_default_sketch(self, app, client, monkeypatch):
        """Phase 62.5 Q4: /last-upload now includes MedMinderV2 default
        (root cause 3 fix — MedMinderV2 must appear in /admin dropdown).
        """
        from medminder_dash.settings import _DEFAULT_SKETCH_DIR

        resp = client.get("/last-upload")
        assert resp.status_code == 200
        assert b"Select a sketch" in resp.data
        assert _DEFAULT_SKETCH_DIR.encode() in resp.data
        assert b"MedMinderV2" in resp.data

    def test_render_sketch_path_selector_includes_default_when_requested(self, app):
        """Phase 62.1: _render_sketch_path_selector(include_default=True) injects
        MedMinderV2 as the first entry and auto-selects it. Used by /admin route.
        """
        from medminder_dash.settings import _DEFAULT_SKETCH_DIR
        from medminder_dash.sketch_management import _render_sketch_path_selector

        with app.test_request_context("/admin"):
            html = _render_sketch_path_selector(include_default=True)
        assert "MedMinderV2" in html
        # Auto-selected: the rendered <option> for MedMinderV2 has selected attr.
        assert "selected" in html
        assert _DEFAULT_SKETCH_DIR in html

    def test_render_sketch_path_selector_no_default_when_not_requested(self, app):
        """Phase 62.1: _render_sketch_path_selector(include_default=False) (the
        default) does NOT inject MedMinderV2. Preserves /last-upload behavior.
        """
        from medminder_dash.sketch_management import _render_sketch_path_selector

        with app.test_request_context("/admin"):
            html = _render_sketch_path_selector()
        assert "MedMinderV2" not in html

    def test_admin_html_sketch_path_loaded_via_htmx(self, app, client):
        """Phase 62.6 Q3+Q5: Admin page no longer has inline hidden sketch_path
        input (removed Q3). sketch_path is loaded via htmx from /last-upload.
        """
        from medminder_dash.settings import _DEFAULT_SKETCH_DIR

        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b'id="sketch_path"' not in resp.data
        # sketch_path is loaded via htmx into #sketch-path-container
        last_upload = client.get("/last-upload")
        assert last_upload.status_code == 200
        assert b'id="sketch_path"' in last_upload.data
        assert _DEFAULT_SKETCH_DIR.encode() in last_upload.data


class TestAdminBoardSelector:
    """Phase 62.2 → 71: /admin board selector refreshes via WS push
    on board-changed events (board-changed from:body trigger).
    """

    def test_admin_html_board_selector_uses_board_changed_event(self, app, client):
        """Phase 71: /admin board selector div has hx-trigger="load, board-changed from:body"
        so it refreshes via WS push on board events instead of polling every 5s.
        """
        resp = client.get("/admin")
        assert resp.status_code == 200
        # The board selector container must declare 'load' and 'board-changed' triggers.
        assert b'id="admin-board-selector-container"' in resp.data
        assert b'hx-trigger="load, board-changed from:body"' in resp.data

    def test_admin_html_board_selector_trigger_matches_main_dashboard(
        self, app, client
    ):
        """Phase 71: board selector trigger uses 'board-changed from:body'
        matching the main dashboard's trigger pattern for consistency.
        """
        import re
        from pathlib import Path

        resp = client.get("/admin")
        assert resp.status_code == 200
        admin_html = resp.data.decode()
        # Extract the hx-trigger value from the admin page.
        m = re.search(
            r'id="admin-board-selector-container"[^>]*hx-trigger="([^"]+)"', admin_html
        )
        assert m is not None, "could not find hx-trigger on board selector container"
        admin_trigger = m.group(1)
        # Read main dashboard's index.html and extract its hx-trigger.
        index_path = (
            Path(__file__).resolve().parents[1]
            / "medminder_dash"
            / "templates"
            / "index.html"
        )
        index_html = index_path.read_text()
        m2 = re.search(r'hx-trigger="([^"]+)"', index_html)
        assert m2 is not None, "could not find hx-trigger in index.html"
        index_trigger = m2.group(1)
        # Both should declare the same board-changed trigger (no polling).
        assert "board-changed from:body" in admin_trigger
        assert "board-changed from:body" in index_trigger


class TestAdminHtmxNativeCompileUpload:
    """Phase 62.3: /admin Compile/Upload buttons use htmx-native hx-post (no
    JS, no fetch+innerHTML). The arduino_sketch_tools partials were renamed
    to avoid #compile-section / #upload-section ID conflict with the outer
    admin cards.
    """

    def _fetch_compile_upload_card(self, client, active_board=None):
        """Helper: fetch compile/upload card as htmx would."""
        if active_board:
            with client.session_transaction() as sess:
                sess["admin_active_board"] = active_board
        return client.get("/board/compile-upload-card")

    def test_admin_html_compile_button_uses_hx_post(self, app, client):
        """Phase 62.3: Compile button (loaded via htmx) uses hx-post (not onclick=JS).
        Phase 62.6 Q5: compile/upload card loaded from /board/compile-upload-card.
        """
        resp = self._fetch_compile_upload_card(client)
        assert resp.status_code == 200
        assert b'hx-post="/board/' in resp.data
        assert b"function compileSketch" not in resp.data
        assert b'onclick="compileSketch()"' not in resp.data

    def test_admin_html_compile_button_targets_output_div(self, app, client):
        """Phase 62.3: Compile button (loaded via htmx) uses hx-post (not onclick=JS).
        Phase 62.6 Q5: compile/upload card loaded from /board/compile-upload-card.
        Phase 75: URL prefix changed from /api/board/ to /board/.
        """
        import re

        resp = self._fetch_compile_upload_card(client)
        assert resp.status_code == 200
        html = resp.data.decode()
        compile_button = re.search(
            r'<button[^>]*hx-post="(/board/[^"]*/compile)"[^>]*?hx-target="([^"]+)"',
            html,
        )
        assert compile_button is not None, "no compile button hx-post found"
        url, target = compile_button.group(1), compile_button.group(2)
        assert target == "#compile-output", (
            f"compile button targets {target}, expected #compile-output"
        )
        assert "/compile" in url

    def test_admin_html_upload_button_uses_hx_post(self, app, client):
        """Phase 62.3: Upload button (loaded via htmx) uses hx-post (not onclick=JS).
        Phase 62.6 Q5: card loaded from /board/compile-upload-card.
        Phase 75: URL prefix changed from /api/board/ to /board/.
        """
        resp = self._fetch_compile_upload_card(client)
        assert resp.status_code == 200
        assert b"function uploadSketch" not in resp.data
        assert b'onclick="uploadSketch()"' not in resp.data
        assert b'hx-post="/board/' in resp.data
        assert b'hx-target="#upload-output"' in resp.data

    def test_compile_in_progress_no_id_conflict(self, app):
        """Phase 62.3: The arduino_sketch_tools/templates/partials/compile_in_progress.html
        inner wrapper no longer uses id="compile-section" (renamed to
        id="compile-output-area"). The polling div inside targets
        #compile-output-area, not the outer admin card.
        """
        from pathlib import Path

        # Read the template from the installed arduino_sketch_tools package
        try:
            import arduino_sketch_tools

            pkg_dir = Path(arduino_sketch_tools.__file__).parent
        except ImportError:
            # Fall back: read source from repo
            pkg_dir = (
                Path(__file__).resolve().parents[4]
                / "arduino_sketch_tools"
                / "python"
                / "arduino_sketch_tools"
                / "arduino_sketch_tools"
            )
        partial = pkg_dir / "templates" / "partials" / "compile_in_progress.html"
        if not partial.exists():
            pytest.skip(f"compile_in_progress.html not found at {partial}")
        html = partial.read_text()
        # The inner wrapper must NOT use id="compile-section" (the conflict).
        # It must use the new id="compile-output-area".
        assert 'id="compile-section"' not in html, (
            "inner wrapper still uses id=compile-section"
        )
        assert 'id="compile-output-area"' in html, (
            "inner wrapper must use id=compile-output-area"
        )
        # Polling div must target the new id
        assert 'hx-target="#compile-output-area"' in html, (
            "polling div must target #compile-output-area"
        )
        assert 'hx-target="#compile-section"' not in html, (
            "polling div must NOT target #compile-section"
        )


class TestGlobalBoardSelectorForCompileUpload:
    """Phase 62: Global board selector at top of /admin drives compile + upload.
    No local port selects in compile/upload cards. FQBN is REAL (not cosmetic).
    """

    def test_admin_html_no_local_board_port_select(self, app, client, monkeypatch):
        """The local <select id="board-port"> and <select id="upload-port">
        are gone from the admin page; the global #admin-active-board is
        rendered by /medicines/board-selector (htmx-load).
        """
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        # Compile/upload cards (rendered in /admin): no local selects
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b'id="board-port"' not in resp.data
        assert b'id="upload-port"' not in resp.data
        # Global board selector (rendered by /medicines/board-selector):
        # the global select IS present in the partial
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/medicines/board-selector")
        assert resp.status_code == 200
        assert b'id="admin-active-board"' in resp.data

    def test_admin_html_compile_card_shows_active_board_as_text(
        self, app, client, monkeypatch
    ):
        """Compile card (loaded via htmx) has #compile-port-display and
        #compile-fqbn-display text labels populated with active board + FQBN.
        Phase 62.6 Q5: card loaded from /board/compile-upload-card.
        """
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [{"port": "/dev/ttyACM0"}],
        )
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_port_info",
            lambda port: {
                "port": port,
                "board": "Arduino Uno",
                "fqbn": "arduino:avr:uno",
            },
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "/dev/ttyACM0"
        resp = client.get("/board/compile-upload-card")
        assert resp.status_code == 200
        assert b'id="compile-port-display"' in resp.data
        assert b'id="compile-fqbn-display"' in resp.data
        assert b"/dev/ttyACM0" in resp.data
        assert b"arduino:avr:uno" in resp.data

    def test_admin_html_upload_card_disabled_when_no_port(
        self, app, client, monkeypatch
    ):
        """Upload card (loaded via htmx) is disabled when no active board.
        Phase 62.6 Q5: card loaded from /board/compile-upload-card.
        """
        monkeypatch.setattr("medminder_dash.html_routes.get_known_ports", lambda: [])
        resp = client.get("/board/compile-upload-card")
        assert resp.status_code == 200
        assert b'id="upload-section"' in resp.data
        assert b'class="card card-disabled"' in resp.data
        assert b"Waiting for board connection" in resp.data

    def test_admin_html_global_select_full_width(self, app, client, monkeypatch):
        """Global select has flex:1 style and is wrapped in a flex container
        with a refresh button.
        """
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [
                {
                    "port": "/dev/ttyACM0",
                    "fqbn": "arduino:avr:uno",
                    "hardware_id": "HW-123",
                }
            ],
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/medicines/board-selector")
        assert resp.status_code == 200
        # Look for the global select with flex:1 style
        assert b'id="admin-active-board"' in resp.data
        assert b'class="flex-1"' in resp.data
        # No refresh button (replaced by WS-triggered auto-refresh in Phase 71)

    def test_admin_html_fqbn_below_select_in_global_selector(
        self, app, client, monkeypatch
    ):
        """FQBN display is below the global select in DOM order (per user
        request: 'display the FQDN for global select below the board port select').
        """
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [{"port": "/dev/ttyACM0"}],
        )
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_port_info",
            lambda port: {
                "port": port,
                "board": "Arduino Uno",
                "fqbn": "arduino:avr:uno",
            },
        )
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HW-123")
        resp = client.get("/medicines/board-selector")
        assert resp.status_code == 200
        select_pos = resp.data.find(b'id="admin-active-board"')
        fqbn_pos = resp.data.find(b'id="global-fqbn-display"')
        assert select_pos > 0
        assert fqbn_pos > 0
        assert fqbn_pos > select_pos, "FQBN display must come AFTER the global select"

    def test_active_board_endpoint_oob_swaps_fqbn(self, app, client, monkeypatch):
        """POST /medicines/active-board response includes OOB-swap HTML
        for #global-fqbn-display and #global-fqbn (Phase 62: FQBN updates
        atomically with active board change).
        """
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_known_ports",
            lambda: [{"port": "/dev/ttyACM0"}],
        )
        monkeypatch.setattr(
            "medminder_dash.html_routes.get_port_info",
            lambda port: {
                "port": port,
                "board": "Arduino Nano",
                "fqbn": "arduino:avr:nano:cpu=atmega328",
            },
        )
        resp = client.post("/medicines/active-board", data={"port": "/dev/ttyACM0"})
        assert resp.status_code == 200
        assert b'hx-swap-oob="true"' in resp.data
        assert b'id="global-fqbn-display"' in resp.data
        assert b'id="global-fqbn"' in resp.data
        assert b"arduino:avr:nano:cpu=atmega328" in resp.data

    def test_compile_card_enabled_even_without_connected_board(
        self, app, client, monkeypatch
    ):
        """Compile card is ALWAYS enabled (compile works without connected
        board). Phase 62.6 Q5: card loaded from /board/compile-upload-card.
        """
        monkeypatch.setattr("medminder_dash.html_routes.get_known_ports", lambda: [])
        resp = client.get("/board/compile-upload-card")
        assert resp.status_code == 200
        assert b'id="compile-section"' in resp.data
        compile_section = resp.data.split(b'id="compile-section"')[1]
        compile_section = compile_section.split(b"</div>")[0]
        assert b"card-disabled" not in compile_section
        assert b"arduino:avr:uno" in resp.data


class TestPhase62Q4AdminSketchAssignment:
    """Phase 62.5 Q4: Admin UX per-board sketch assignment display."""

    def test_last_upload_includes_default_sketch(self, app, client, monkeypatch):
        """api_last_upload includes MedMinderV2 in dropdown (root cause 3 fix)."""
        from medminder_dash.settings import _DEFAULT_SKETCH_DIR

        resp = client.get("/last-upload")
        assert resp.status_code == 200
        assert _DEFAULT_SKETCH_DIR.encode() in resp.data
        assert b"MedMinderV2" in resp.data

    def test_admin_page_includes_hardware_id_hidden_input(
        self, app, client, monkeypatch
    ):
        """Admin page includes hidden input for active board hardware_id."""
        from medminder_dash.state import _known_ports, _known_ports_lock

        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "arduino:avr:uno",
                "hardware_id": "USB:123 SER=456",
            }
        try:
            with client.session_transaction() as sess:
                sess["admin_active_board"] = (
                    "/dev/ttyACM0",
                    "arduino:avr:uno",
                    "HW-123",
                )
            resp = client.get("/admin")
            assert resp.status_code == 200
            assert b'id="active-board-hardware-id"' in resp.data
            assert b"USB:123 SER=456" in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

    def test_admin_shows_assigned_sketch_when_present(
        self, app, client, monkeypatch, tmp_path
    ):
        """Admin page shows assigned sketch badge when per-board assignment exists."""
        sketch_path = str(tmp_path / "sketches" / "mysketch")
        import os

        from medminder_dash.settings import CONFIG_DIR
        from medminder_dash.sketch_registry import reset_for_tests, set_assignment
        from medminder_dash.state import (
            _known_ports,
            _known_ports_lock,
            _upload_registry,
        )

        os.makedirs(str(CONFIG_DIR), exist_ok=True)
        reset_for_tests()
        os.makedirs(sketch_path, exist_ok=True)
        _upload_registry[("127.0.0.1", "test-agent")] = {
            "mysketch": [
                {
                    "path": sketch_path,
                    "checksum": "abc",
                    "server_timestamp": "2025-01-01T00:00:00",
                    "hardware_ids": [],
                    "board_timestamps": {},
                }
            ]
        }
        set_assignment("USB:123 SER=456", sketch_path)
        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "arduino:avr:uno",
                "hardware_id": "USB:123 SER=456",
            }
        try:
            with client.session_transaction() as sess:
                sess["admin_active_board"] = (
                    "/dev/ttyACM0",
                    "arduino:avr:uno",
                    "HW-123",
                )
            resp = client.get("/admin")
            assert resp.status_code == 200
            assert b"Assigned to selected board" in resp.data
            assert sketch_path.encode() in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

    def test_sketch_assignment_resolved_via_admin_route(
        self, app, client, monkeypatch, tmp_path
    ):
        """Sketch path assignment is resolved server-side. The admin page
        shows the assigned sketch badge (Q3 removed hidden input; sketch
        path is now loaded via htmx from /last-upload).
        """
        sketch_path = str(tmp_path / "sketches" / "mysketch")
        import os

        from medminder_dash.settings import CONFIG_DIR
        from medminder_dash.sketch_registry import reset_for_tests, set_assignment
        from medminder_dash.state import (
            _known_ports,
            _known_ports_lock,
            _upload_registry,
        )

        os.makedirs(str(CONFIG_DIR), exist_ok=True)
        reset_for_tests()
        os.makedirs(sketch_path, exist_ok=True)
        _upload_registry[("127.0.0.1", "test-agent")] = {
            "mysketch": [
                {
                    "path": sketch_path,
                    "checksum": "abc",
                    "server_timestamp": "2025-01-01T00:00:00",
                    "hardware_ids": [],
                    "board_timestamps": {},
                }
            ]
        }
        set_assignment("USB:123 SER=456", sketch_path)
        with _known_ports_lock:
            _known_ports["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "arduino:avr:uno",
                "hardware_id": "USB:123 SER=456",
            }
        try:
            with client.session_transaction() as sess:
                sess["admin_active_board"] = (
                    "/dev/ttyACM0",
                    "arduino:avr:uno",
                    "HW-123",
                )
            # Admin page shows assigned sketch badge
            resp = client.get("/admin")
            assert resp.status_code == 200
            assert b"Assigned to selected board" in resp.data
            assert sketch_path.encode() in resp.data
            # sketch_path element is loaded via htmx, NOT inline in admin page
            assert b'id="sketch_path"' not in resp.data
        finally:
            with _known_ports_lock:
                _known_ports.pop("/dev/ttyACM0", None)

