"""arduino_dash/python/arduino_dash/arduino_dash/app.py

Flask web app with HTMX + WebSocket bridge to BoardManagerService

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

from flask import Flask

try:
    from flask_sock import Sock
except ImportError:
    Sock = None

from arduino_dash import state
from arduino_dash.api_routes import init_api_routes
from arduino_dash.html_routes import init_html_routes
from arduino_dash.pubsub import (
    _broadcast_ws,
)
from arduino_sketch_tools import ArduinoSketchTools


def _get_board_info(port: str) -> dict:
    """Return board info dict for the given port."""
    with state._board_list_lock:
        if port in state._board_list:
            return state._board_list[port]
    return {}


def _record_deploy(port: str, sketch_path: str) -> None:
    """Record a deploy event linking a hardware ID to a sketch path."""
    import datetime

    with state._board_list_lock:
        board_info = state._board_list.get(port, {})
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
                        _update_meta_hw_ids(
                            sketch_path, v["hardware_ids"], v["board_timestamps"]
                        )
                        _save_registry()
                        _broadcast_ws(
                            '<div class="sketch-event">Deploy recorded <!-- board-event --></div>'
                        )
                        return


def create_app():
    """Create and configure the Flask application instance."""
    _app = Flask(__name__)
    _app.secret_key = os.getenv("ARDUINO_DASH_SECRET", "dev-secret-arduino")
    state._app = _app
    sock = Sock(_app) if Sock else None
    init_html_routes(_app, sock)
    init_api_routes(_app)
    arduino_tools = ArduinoSketchTools(
        broadcast_ws=_broadcast_ws,
        get_board_info=_get_board_info,
        record_deploy=_record_deploy,
    )
    arduino_tools.init_app(_app)
    return _app


app = create_app()


# Re-export names for test compatibility
from arduino_dash.pubsub import (  # noqa: E402, F401
    _compute_sketch_checksum,
    _get_sketch_mtime,
    _make_meta,
    _on_board_event,
    _on_daemon_ready,
    _on_pubsub_reconnect,
    _on_resp,
    _wait_for_response,
    init_pubsub,
)
from arduino_dash.sketch_management import (  # noqa: E402, F401
    _normalize_ino_filename,
    _render_sketch_path_selector,
    _save_registry,
    _update_meta_hw_ids,
    _warm_upload_registry,
)
from arduino_dash.state import (  # noqa: E402, F401
    _board_list,
    _board_list_lock,
    _compile_results,
    _compile_results_lock,
    _last_compile_mtime,
    _last_compile_mtime_lock,
    _last_compiled_sketch,
    _last_compiled_sketch_lock,
    _pending_responses,
    _pending_responses_lock,
    _upload_registry,
    _upload_registry_lock,
    _upload_results,
    _upload_results_lock,
)

