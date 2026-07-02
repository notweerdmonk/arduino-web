"""medminder_dash/python/medminder_dash/tests/test_bootstrap.py

Tests for app bootstrap and initialization.

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
        store._save()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


class TestMigration:
    def test_migrates_default_to_selected(self, app, client):
        from medminder_dash.app import store

        store._board_meta["default"] = {
            "medicines": [
                Medicine(
                    name="Migrated", hour=8, minute=0, day_of_week=0, day_of_month=0
                )
            ]
        }
        resp = client.get("/board/select/dev/ttyACM0", follow_redirects=True)
        assert resp.status_code == 200
        meds = store._board_meta.get("/dev/ttyACM0", {}).get("medicines", [])
        assert len(meds) == 1
        assert meds[0].name == "Migrated"
        assert "default" not in store._board_meta

    def test_does_not_migrate_when_selected_board_has_data(self, app, client):
        from medminder_dash.app import store

        store._board_meta["default"] = {
            "medicines": [
                Medicine(name="Orphan", hour=8, minute=0, day_of_week=0, day_of_month=0)
            ]
        }
        store._board_meta["/dev/ttyACM0"] = {
            "medicines": [
                Medicine(
                    name="Existing", hour=9, minute=0, day_of_week=0, day_of_month=0
                )
            ]
        }
        resp = client.get("/board/select/dev/ttyACM0", follow_redirects=True)
        assert resp.status_code == 200
        meds = store._board_meta.get("/dev/ttyACM0", {}).get("medicines", [])
        assert len(meds) == 1
        assert meds[0].name == "Existing"
        assert "default" in store._board_meta

    def test_no_default_no_migration(self, app, client, tmp_path):
        from medminder_dash.app import store

        missing = tmp_path / "nonexistent.hpp"
        with patch(
            "medminder_dash.html_routes._get_alarm_hpp_path", return_value=str(missing)
        ):
            resp = client.get("/board/select/dev/ttyACM1", follow_redirects=True)
        assert resp.status_code == 200
        meds = store._board_meta.get("/dev/ttyACM1", {})
        assert len(meds.get("medicines", [])) == 0

