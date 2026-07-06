"""medminder_dash/python/medminder_dash/medminder_dash/state.py

Shared mutable state for medminder_dash.

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
