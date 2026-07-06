"""medminder_dash/python/medminder_dash/medminder_dash/app.py

Flask application factory and top-level route wiring.

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

from __future__ import annotations

import logging
import os

from flask import Flask, session

from arduino_sketch_tools import ArduinoSketchTools
from medminder_dash import state
from medminder_dash.medicines_state import MedicineStore
from medminder_dash.pubsub import _get_alarm_hpp_path, broadcast_ws
from medminder_dash.settings import load_sketch_dir
from medminder_dash.sketch_management import _save_registry, _update_meta_hw_ids
from medminder_dash.utils import get_port_info

logger = logging.getLogger(__name__)


SKETCH_DIR = load_sketch_dir()
ALARM_HPP_PATH = _get_alarm_hpp_path()


def _get_board_info(port):
    """Return board info dict for a port, or empty dict.

    Args:
        port: Board port string.

    Returns:
        Board info dict or empty dict.
    """
    info = get_port_info(port)
    return info or {}


def _record_deploy(port: str, sketch_path: str) -> None:
    """Record a deploy event in the upload registry.

    Args:
        port: Board port that was deployed to.
        sketch_path: Path to the deployed sketch.
    """
    import datetime

    with state._known_ports_lock:
        board_info = state._known_ports.get(port, {})
    hardware_id = board_info.get("hardware_id", "")
    if not hardware_id:
        return
    deploy_ts = datetime.datetime.utcnow().isoformat()
    with state._upload_registry_lock:
        for user_sketches in state._upload_registry.values():
            for versions in user_sketches.values():
                for v in versions:
                    if v["path"] == sketch_path:
                        if hardware_id not in v["hardware_ids"]:
                            v["hardware_ids"].append(hardware_id)
                        v["board_timestamps"][hardware_id] = deploy_ts
                        _update_meta_hw_ids(sketch_path, v["hardware_ids"], v["board_timestamps"])
                        _save_registry()
                        broadcast_ws(
                            '<div class="sketch-event">Deploy recorded <!-- board-event --></div>'
                        )
                        return


def _migrate_default_board(store, session):
    """Migrate medicines from 'default' board to the current board port.

    Args:
        store: MedicineStore instance.
        session: Flask session object.
    """
    default_meds = store._board_meta.get("default", {}).get("medicines", [])
    if not default_meds:
        return
    if store.all():
        return
    logger.info(
        "Migrating %d medicine(s) from 'default' to board %s",
        len(default_meds),
        session.get("board_port"),
    )
    for med in default_meds:
        store.add(med)
    del store._board_meta["default"]
    store._save()


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    global store
    store = MedicineStore()

    arduino_tools = ArduinoSketchTools(
        broadcast_ws=broadcast_ws,
        get_board_info=_get_board_info,
        record_deploy=_record_deploy,
    )
    arduino_tools.init_app(app)

    @app.before_request
    def _sync_store_board():
        """Load the board's medicines into the store before each request."""
        port = session.get("board_port")
        if port:
            store.load_board(port)

    try:
        from flask_sock import Sock

        sock = Sock(app)
    except ImportError:
        sock = None

    from medminder_dash.api_routes import init_api_routes
    from medminder_dash.html_routes import init_html_routes

    init_html_routes(
        app,
        sock,
        store_param=store,
        migrate_default_board=lambda: _migrate_default_board(store, session),
        load_sketch_dir_param=load_sketch_dir,
        get_alarm_hpp_path_param=lambda: _get_alarm_hpp_path(),
    )
    init_api_routes(app, store_param=store)

    return app
