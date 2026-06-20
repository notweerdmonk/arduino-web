"""Shared mutable state for medminder_dash.

Holds application-level references, port registry, WebSocket clients,
upload registry, and synchronization primitives.
"""

import logging
import threading
from pathlib import Path
from typing import Optional

import flask

from board_manager_client.pubsub_client import PubSubClient


_app: flask.Flask = None
logger = logging.getLogger("medminder_dash")
pubsub: Optional[PubSubClient] = None

_ws_clients: list = []
_ws_lock = threading.Lock()

_known_ports: dict[str, dict] = {}
_known_ports_lock = threading.Lock()

_board_events: list[dict] = []
_board_events_lock = threading.Lock()

_pending_responses: dict = {}
_pending_responses_lock = threading.Lock()

_daemon_ready: bool = False
_daemon_ready_lock = threading.Lock()

_fallback_scanner: Optional[threading.Thread] = None
_stop_fallback_scan: bool = False
_fallback_patterns = ["/dev/ttyACM*", "/dev/ttyUSB*"]
_fallback_scan_interval = 5.0

UPLOAD_BASE_DIR = Path.home() / ".local" / "share" / "medminder" / "uploads"
_upload_registry: dict = {}
_upload_registry_lock = threading.Lock()
