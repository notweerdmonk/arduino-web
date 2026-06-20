"""WSGI entry point for medminder_dash.

Creates the Flask app for gunicorn. BMS lifecycle is managed by
gunicorn_conf.py hooks (when_ready / on_exit).

Usage:
    gunicorn -c gunicorn_conf.py medminder_dash.wsgi:app

Environment variables:
    BOARD_MGR_UDS_PATH   — UDS path for BMS (default: /tmp/board_mgr.sock)
    BOARD_MGR_TCP_HOST   — TCP host for BMS (default: 127.0.0.1)
    BOARD_MGR_TCP_PORT   — TCP port for BMS (default: 9090)
    BMS_NO_UDS           — Set to true to force TCP only
"""

import os

from medminder_dash.app import create_app

app = create_app()
app.config.update(
    BMS_UDS_PATH=os.environ.get("BOARD_MGR_UDS_PATH", "/tmp/board_mgr.sock"),
    BMS_TCP_HOST=os.environ.get("BOARD_MGR_TCP_HOST", "127.0.0.1"),
    BMS_TCP_PORT=int(os.environ.get("BOARD_MGR_TCP_PORT", "9090")),
    BMS_NO_UDS=os.environ.get("BMS_NO_UDS", "").lower() in ("1", "true"),
)
