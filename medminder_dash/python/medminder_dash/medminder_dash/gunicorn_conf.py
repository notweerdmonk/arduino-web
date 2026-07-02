"""medminder_dash/python/medminder_dash/medminder_dash/gunicorn_conf.py

gunicorn configuration for medminder_dash.

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
from enum import Enum


class GunicornEnv(str, Enum):
    """Environment variable names for gunicorn configuration."""

    BIND = "GUNICORN_BIND"
    WORKERS = "GUNICORN_WORKERS"
    TIMEOUT = "GUNICORN_TIMEOUT"
    LOG_LEVEL = "GUNICORN_LOG_LEVEL"


bind = os.environ.get(GunicornEnv.BIND, "0.0.0.0:8080")
workers = int(os.environ.get(GunicornEnv.WORKERS, "4"))
timeout = int(os.environ.get(GunicornEnv.TIMEOUT, "120"))
loglevel = os.environ.get(GunicornEnv.LOG_LEVEL, "info")
preload_app = False

_bms_proc = None


def _get_bms_config():
    """Return BMS connection configuration from environment variables."""
    return {
        "uds_path": os.environ.get("BOARD_MGR_UDS_PATH", "/tmp/board_mgr.sock"),
        "tcp_host": os.environ.get("BOARD_MGR_TCP_HOST", "127.0.0.1"),
        "tcp_port": int(os.environ.get("BOARD_MGR_TCP_PORT", "9090")),
        "use_uds": os.environ.get("BMS_NO_UDS", "").lower() not in ("1", "true"),
    }


def when_ready(server):
    """Start BMS and wait for it to become ready on master start."""
    global _bms_proc
    from board_manager.boot import start_bms, wait_for_bms

    _bms_proc = start_bms()
    fire_and_forget = os.environ.get("BMS_FIRE_AND_FORGET", "").lower() in (
        "1",
        "true",
        "yes",
    )
    if not fire_and_forget:
        cfg = _get_bms_config()
        ready = wait_for_bms(
            uds_path=cfg["uds_path"],
            tcp_host=cfg["tcp_host"],
            tcp_port=cfg["tcp_port"],
            timeout=float(os.environ.get("BMS_WAIT_TIMEOUT", "10")),
        )
        if not ready:
            server.log.warning(
                "BMS not ready within timeout — workers will retry on connect"
            )
        else:
            server.log.info("BMS ready")
    else:
        server.log.info("BMS started (fire-and-forget mode)")


def post_worker_init(worker):
    """Initialize PubSub connection in each gunicorn worker."""
    cfg = _get_bms_config()
    worker.log.info("Initializing PubSub for worker %d", worker.pid)
    from medminder_dash.pubsub import init_pubsub
    from medminder_dash.wsgi import app

    init_pubsub(
        app,
        use_uds=cfg["use_uds"],
        tcp_host=cfg["tcp_host"],
        tcp_port=cfg["tcp_port"],
        uds_path=cfg["uds_path"],
    )
    worker.log.info("PubSub initialized for worker %d", worker.pid)


def on_exit(server):
    """Stop BMS on gunicorn exit."""
    global _bms_proc
    if _bms_proc is not None:
        from board_manager.boot import stop_bms

        server.log.info("Stopping BMS (PID %d)", _bms_proc.pid)
        stop_bms(_bms_proc)
        _bms_proc = None

