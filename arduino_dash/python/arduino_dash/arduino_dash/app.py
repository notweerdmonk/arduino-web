"""Flask web app with HTMX + WebSocket bridge to BoardManagerService"""

import os

from flask import Flask

try:
    from flask_sock import Sock
except ImportError:
    Sock = None

from arduino_dash import state
from arduino_dash.pubsub import (
    _broadcast_ws,
)
from arduino_dash.html_routes import init_html_routes
from arduino_dash.api_routes import init_api_routes
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


# Re-export state names for test compatibility
from arduino_dash.sketch_management import _save_registry, _update_meta_hw_ids  # noqa: E402
