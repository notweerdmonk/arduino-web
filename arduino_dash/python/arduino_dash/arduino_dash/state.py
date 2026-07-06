"""arduino_dash/python/arduino_dash/arduino_dash/state.py

Shared module-level state for the Arduino Dash webapp

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

import flask

from arduino_dash.settings import UPLOAD_BASE_DIR  # noqa: F401
from board_manager_client import PubSubClient

_app: flask.Flask = None

logger = logging.getLogger("arduino_dash")

pubsub: PubSubClient = None
_ws_clients: list = []
_ws_lock = threading.Lock()
_board_list: dict[str, dict] = {}
_board_list_lock = threading.Lock()
_board_events: list[dict] = []
_board_events_lock = threading.Lock()
_pending_responses: dict[str, tuple[dict | None, threading.Event]] = {}
_pending_responses_lock = threading.Lock()
_compile_results: dict[str, dict | None] = {}
_compile_results_lock = threading.Lock()
_upload_results: dict[str, dict | None] = {}
_upload_results_lock = threading.Lock()
_compile_meta: dict[str, dict] = {}
_compile_meta_lock = threading.Lock()
_upload_meta: dict[str, dict] = {}
_upload_meta_lock = threading.Lock()
_daemon_ready: bool = False
_daemon_ready_lock = threading.Lock()
_last_compiled_sketch: dict[str, str] = {}
_last_compiled_sketch_lock = threading.Lock()
_last_compile_mtime: dict[str, float | None] = {}
_last_compile_mtime_lock = threading.Lock()
_last_compile_checksum: dict[str, str] = {}
_last_compile_checksum_lock = threading.Lock()
_last_uploaded_sketch: dict[str, str] = {}
_last_uploaded_sketch_lock = threading.Lock()
_upload_registry: dict[tuple[str, str], dict[str, list[dict]]] = {}
_upload_registry_lock = threading.Lock()

MAX_SKETCH_UPLOAD_SIZE = 10 * 1024 * 1024

_fallback_scanner: threading.Thread | None = None
_stop_fallback_scan: bool = False
_fallback_patterns = ["/dev/ttyACM*", "/dev/ttyUSB*"]
_fallback_scan_interval = 5.0

