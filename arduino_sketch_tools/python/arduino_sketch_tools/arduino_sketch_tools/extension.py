"""arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/extension.py

ArduinoSketchTools Flask Extension — compile/upload state and pubsub handlers

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
import re
import threading
import time

PORT_RE = re.compile(r"^/dev/[a-zA-Z0-9_/]+$")


def _normalize_port(port: str) -> str | None:
    """Normalize and validate a port path.

    Strips extra leading slashes, ensures exactly one / prefix,
    then validates against PORT_RE. Returns the normalized port
    if valid, None otherwise.
    """
    normed = "/" + port.lstrip("/")
    return normed if PORT_RE.match(normed) else None


class ArduinoSketchTools:
    """Flask Extension managing Arduino sketch compile/upload state.

    Encapsulates all compile/upload results, metadata, and pubsub response
    handling. Registers a Blueprint with compile/upload routes via init_app().
    """

    COMPILE_TIMEOUT = 150

    def __init__(self, pubsub=None, broadcast_ws=None, get_board_info=None, record_deploy=None):
        """Initialize the extension with optional pubsub, broadcast, and hooks."""
        self.pubsub = pubsub
        self._broadcast_ws = broadcast_ws or (lambda html: None)
        self._get_board_info = get_board_info or (lambda port: {})
        self._record_deploy = record_deploy or (lambda port, sketch_path: None)

        self._compile_results: dict[str, dict | None] = {}
        self._compile_results_lock = threading.Lock()
        self._compile_last_pct: dict[str, float] = {}
        self._compile_last_pct_lock = threading.Lock()
        self._upload_results: dict[str, dict | None] = {}
        self._upload_results_lock = threading.Lock()
        self._compile_start: dict[str, float] = {}
        self._compile_start_lock = threading.Lock()
        self._compile_meta: dict[str, dict] = {}
        self._compile_meta_lock = threading.Lock()
        self._upload_meta: dict[str, dict] = {}
        self._upload_meta_lock = threading.Lock()
        self._last_compiled_sketch: dict[str, str] = {}
        self._last_compiled_sketch_lock = threading.Lock()
        self._last_compile_mtime: dict[str, float | None] = {}
        self._last_compile_mtime_lock = threading.Lock()
        self._last_compile_checksum: dict[str, str] = {}
        self._last_compile_checksum_lock = threading.Lock()
        self._last_uploaded_sketch: dict[str, str] = {}
        self._last_uploaded_sketch_lock = threading.Lock()

    def init_app(self, app, pubsub=None):
        """Register the extension with a Flask app.

        Args:
            app: The Flask application instance.
            pubsub: Optional pubsub client; overrides self.pubsub if given.
        """
        if pubsub is not None:
            self.pubsub = pubsub
        app.extensions["arduino_sketch_tools"] = self
        if self.pubsub:
            self.pubsub.subscribe("resp::compile::*", self._on_compile_resp)
            self.pubsub.subscribe("resp::upload::*", self._on_upload_resp)
        from arduino_sketch_tools.routes import compile_bp

        app.register_blueprint(compile_bp)

    def _norm_port(self, port: str) -> str | None:
        """Normalize and validate a port path.

        Args:
            port: Raw port path.

        Returns:
            Normalized port string or None if invalid.
        """
        return _normalize_port(port)

    def _compute_sketch_checksum(self, sketch_dir: str) -> str:
        """Compute a SHA-256 checksum over all source files in a sketch directory.

        Args:
            sketch_dir: Path to the sketch directory.

        Returns:
            Hex digest string, or empty string if no source files found.
        """
        if not os.path.isdir(sketch_dir):
            return ""
        import hashlib

        hasher = hashlib.sha256()
        file_paths = []
        for root, _dirs, files in os.walk(sketch_dir):
            for f in files:
                if f.endswith((".ino", ".cpp", ".h", ".hpp", ".c")):
                    file_paths.append(os.path.join(root, f))
        file_paths.sort()
        for fp in file_paths:
            try:
                with open(fp, "rb") as fh:
                    while True:
                        chunk = fh.read(65536)
                        if not chunk:
                            break
                        hasher.update(chunk)
            except OSError:
                continue
        if not file_paths:
            return ""
        return hasher.hexdigest()

    def _get_sketch_mtime(self, sketch_path: str) -> float | None:
        """Return the latest modification time among source files in a sketch.

        Args:
            sketch_path: Path to the sketch directory.

        Returns:
            Latest mtime as float, or None if the directory is empty or missing.
        """
        if not os.path.isdir(sketch_path):
            return None
        max_mtime: float | None = None
        for root, _dirs, files in os.walk(sketch_path):
            for f in files:
                if f.endswith((".ino", ".cpp", ".h", ".hpp", ".c")):
                    try:
                        mtime = os.path.getmtime(os.path.join(root, f))
                        if max_mtime is None or mtime > max_mtime:
                            max_mtime = mtime
                    except OSError:
                        continue
        return max_mtime

    def _make_meta(self, port: str, sketch_path: str) -> dict:
        """Build a metadata dict for a compile or upload operation.

        Args:
            port: Normalized port path.
            sketch_path: Path to the sketch directory.

        Returns:
            Metadata dict with port, board info, sketch info, and start time.
        """
        board_info = self._get_board_info(port)
        utils_dir = os.path.basename(os.path.normpath(sketch_path)) if sketch_path else ""
        return {
            "port": port,
            "board": board_info.get("board", ""),
            "fqbn": board_info.get("fqbn", ""),
            "hardware_id": board_info.get("hardware_id", ""),
            "sketch": sketch_path,
            "sketch_name": utils_dir,
            "started_at": time.time(),
        }

    def _on_compile_resp(self, msg: dict) -> None:
        """Handle a compile response message from pubsub.

        Progress messages are broadcast as WebSocket HTML; final results
        are stored in _compile_results and update sketch metadata.
        """
        topic = msg.get("topic", "")
        if not topic.startswith("resp::compile::"):
            return
        rest = topic[len("resp::compile::") :]
        is_progress = rest.endswith("::progress")
        if is_progress:
            port = rest[: -len("::progress")]
            data = msg.get("data", {})
            out = data.get("output", "")
            err = data.get("error", "")
            percent = data.get("percent", 0.0)
            port_safe = port.replace("/", "_")
            with self._compile_last_pct_lock:
                last = self._compile_last_pct.get(port_safe, -1.0)
                if percent != last:
                    pct_int = int(round(percent))
                    self._compile_last_pct[port_safe] = percent
                    bar = (
                        f'<progress id="compile-progress-{port_safe}" value="{pct_int}" '
                        f'max="100" hx-swap-oob="true"></progress>'
                    )
                    self._broadcast_ws(bar)
            if out or err:
                text = (out + err).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                pct_prefix = f"[{pct_int}%] " if percent >= 0 else ""
                html = (
                    f'<span hx-swap-oob="beforeend:#compile-output-{port_safe}">'
                    f'<div class="compile-line" data-port="{port}">'
                    f"{pct_prefix}{text}</div></span>"
                )
                self._broadcast_ws(html)
        else:
            port = rest
            with self._compile_results_lock:
                self._compile_results[port] = msg
            if msg.get("status") == "ok":
                sketch_path = msg.get("data", {}).get("sketch_path", "")
                if sketch_path:
                    with self._last_compiled_sketch_lock:
                        self._last_compiled_sketch[port] = sketch_path
                    with self._last_compile_mtime_lock:
                        self._last_compile_mtime[port] = self._get_sketch_mtime(sketch_path)

    def _on_upload_resp(self, msg: dict) -> None:
        """Handle an upload response message from pubsub.

        Progress messages are broadcast as WebSocket HTML; final results
        are stored in _upload_results and trigger deploy recording.
        """
        topic = msg.get("topic", "")
        if not topic.startswith("resp::upload::"):
            return
        rest = topic[len("resp::upload::") :]
        is_progress = rest.endswith("::progress")
        if is_progress:
            port = rest[: -len("::progress")]
            data = msg.get("data", {})
            out = data.get("output", "")
            err = data.get("error", "")
            if out or err:
                text = (out + err).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                port_safe = port.replace("/", "_")
                html = (
                    f'<span hx-swap-oob="beforeend:#upload-output-{port_safe}">'
                    f'<div class="upload-line" data-port="{port}">'
                    f"{text}</div></span>"
                )
                self._broadcast_ws(html)
        else:
            port = rest
            with self._upload_results_lock:
                self._upload_results[port] = msg
            if msg.get("status") == "ok":
                with self._upload_meta_lock:
                    sketch_path = self._upload_meta.get(port, {}).get("sketch", "")
                if sketch_path:
                    self._record_deploy(port, sketch_path)
