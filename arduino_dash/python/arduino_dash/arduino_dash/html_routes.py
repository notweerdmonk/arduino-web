"""arduino_dash/python/arduino_dash/arduino_dash/html_routes.py

HTML page and partial routes — no /api/ prefix

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

import bisect
import datetime
import hashlib
import json
import logging
import os
import shutil

from flask import Flask, render_template, request, session
from werkzeug.utils import secure_filename

from arduino_dash import state
from arduino_dash.pubsub import (
    _broadcast_ws,
    _compute_sketch_checksum,
)
from arduino_dash.sketch_management import (
    _find_existing_version,
    _normalize_ino_filename,
    _resolve_latest_upload,
    _save_registry,
    _update_meta_hw_ids,
    _render_sketch_path_selector,
)
from arduino_dash.sketch_registry import get_assignment, set_assignment
from arduino_dash.utils import (
    find_board_info_by_fqbn,
    get_first_board,
    get_port_info,
    get_known_boards,
    normalize_port,
)

logger = logging.getLogger(__name__)


def _get_active_board_info():
    """Return the active board (port, fqbn, hardware_id) from the session."""
    raw = session.get("admin_active_board")
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        return (str(raw[0]), str(raw[1]), str(raw[2]))
    if isinstance(raw, str):
        return (raw, "", "")
    return ("", "", "")


def _resolve_board_info(
    active_board_port, active_board_fqbn, active_board_hardware_id, known_ports
):
    """Resolve board info, falling back to known ports if needed."""
    info = get_port_info(active_board_port)
    if not info:
        if active_board_fqbn:
            info = find_board_info_by_fqbn(active_board_fqbn, known_ports)
        if info:
            active_board_port = info.get("port", "")
            if not active_board_port:
                raise ValueError("port missing")
        elif known_ports:
            result = get_first_board(known_ports)
            if not result:
                raise ValueError("port missing")
            (active_board_port, active_board_fqbn, active_board_hardware_id) = result
            if not active_board_fqbn:
                raise ValueError("fqbn missing")
    else:
        port = info.get("port", "")
        if not port:
            raise ValueError("port missing")
        fqbn = info.get("fqbn", "")
        if not fqbn:
            raise ValueError("fqbn missing")
        if not active_board_fqbn:
            active_board_fqbn = fqbn
        elif fqbn != active_board_fqbn:
            info = find_board_info_by_fqbn(active_board_fqbn, known_ports)
            if info:
                active_board_port = info.get("port", "")
                if not active_board_port:
                    raise ValueError("port missing")
                active_board_fqbn = info.get("fqbn", "")
                if not active_board_fqbn:
                    raise ValueError("fqbn missing")
            else:
                active_board_fqbn = fqbn
    return active_board_port, active_board_fqbn, active_board_hardware_id


def init_html_routes(app: Flask, sock):
    """Register all HTML route handlers on the Flask app."""

    @app.route("/")
    def dashboard():
        """Render the main dashboard page."""
        return render_template("dashboard.html")

    @app.route("/board/<path:port>")
    def board_detail(port: str):
        """Render the board detail page."""
        norm_port = normalize_port(port)
        if norm_port is None:
            return "Invalid port", 400
        board_info = get_port_info(norm_port)
        board_name = board_info.get("board", "") or norm_port
        port_path = norm_port.lstrip("/")
        return render_template(
            "board_detail.html",
            port=norm_port,
            port_path=port_path,
            board_name=board_name,
            board_info=board_info,
            show_sketch_tools=True,
            show_medicines_section=False,
        )

    @app.route("/boards/grid")
    def html_boards_grid():
        """Render the board grid partial."""
        with state._board_list_lock:
            boards = list(state._board_list.values())
        return render_template("partials/board_grid.html", boards=boards)

    @app.route("/boards/grid/card/<path:port>")
    def html_boards_grid_card(port: str):
        """Render a single board card partial."""
        norm_port = normalize_port(port)
        if norm_port is None:
            return "", 400
        with state._board_list_lock:
            b = state._board_list.get(norm_port)
        if b is None:
            return "", 404
        return render_template("partials/board_card.html", b=b)

    @app.route("/board/<path:port>/connection-status")
    def html_board_connection_status(port: str):
        """Render the connection status badge for a board."""
        norm_port = normalize_port(port)
        if norm_port is None:
            return "Invalid port", 400
        port_path = norm_port.lstrip("/")
        with state._board_list_lock:
            connected = norm_port in state._board_list
        return render_template(
            "partials/board_status_badge.html",
            port=norm_port,
            port_path=port_path,
            connected=connected,
        )

    @app.route("/daemon/status")
    def html_daemon_status():
        """Render the daemon status badge."""
        connected = state.pubsub is not None and state.pubsub.is_connected
        with state._daemon_ready_lock:
            daemon_ready = state._daemon_ready
        return render_template(
            "partials/daemon_badge.html", ready=connected and daemon_ready
        )

    @app.route("/admin")
    def admin():
        """Render the admin page."""
        known_ports = get_known_boards()
        active_board_port = request.args.get("port", "").strip()
        active_board_fqbn = ""
        active_board_hardware_id = ""
        active_board_sketch = ""
        if not active_board_port:
            (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                _get_active_board_info()
            )
        if not active_board_port:
            if known_ports:
                result = get_first_board(known_ports)
                if not result:
                    return "port missing", 500
                (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                    result
                )
                if not active_board_fqbn:
                    return "fqbn missing", 500
                session["admin_active_board"] = (
                    active_board_port,
                    active_board_fqbn,
                    active_board_hardware_id,
                )

        # fetch fqbn and hardware id for active board port
        else:
            info = (
                state._board_list.get(active_board_port, {})
                if isinstance(active_board_port, str)
                else {}
            )
            # info missing for active_board_port
            # try to find port based on fqbn
            if not info:
                if active_board_fqbn:
                    info = find_board_info_by_fqbn(active_board_fqbn, known_ports)
                elif known_ports:
                    info = known_ports[0]

            if info:
                active_board_port = info.get("port", "")
                # default board is Arduino UNO
                active_board_fqbn = info.get("fqbn", "")
                active_board_hardware_id = info.get("hardware_id", "")
            else:
                active_board_port = ""
                active_board_fqbn = ""
                active_board_hardware_id = ""

        # no board is connected
        if not active_board_fqbn:
            # default board is Arduino UNO
            active_board_fqbn = "arduino:avr:uno"

        if active_board_hardware_id:
            active_board_sketch = get_assignment(active_board_hardware_id) or ""

        return render_template(
            "admin.html",
            ports=known_ports,
            active_board=active_board_port,
            active_board_fqbn=active_board_fqbn,
            active_board_hardware_id=active_board_hardware_id,
            active_board_sketch=active_board_sketch,
        )

    @app.route("/admin/board-selector")
    def html_admin_board_selector():
        """Render the admin board selector partial."""
        known_ports = get_known_boards()
        (active_board_port, active_board_fqbn, _) = _get_active_board_info()

        try:
            (active_board_port, active_board_fqbn, _) = _resolve_board_info(
                active_board_port, active_board_fqbn, "", known_ports
            )
        except ValueError as e:
            return str(e), 500

        return render_template(
            "partials/admin_board_selector.html",
            ports=known_ports,
            active_board=active_board_port,
            active_board_fqbn=active_board_fqbn,
            board_selector_label="Active Board (for compile and upload)",
            board_selector_hx_post="/admin/active-board",
            board_selector_hx_target="#compile-upload-card",
            board_selector_hx_swap="innerHTML",
        )

    @app.route("/admin/active-board", methods=["POST"])
    def html_admin_active_board():
        """Set the active board in the session and return OOB swap HTML."""
        port = request.form.get("port", "").strip()
        if not port:
            return "port required", 400
        info = state._board_list.get(port, {})
        fqbn = info.get("fqbn", "")
        if not fqbn:
            return "fqbn missing", 500
        hardware_id = info.get("hardware_id", "")

        session["admin_active_board"] = (port, fqbn, hardware_id)

        oob = (
            f'<span id="global-fqbn-display" hx-swap-oob="true">{fqbn}</span>'
            f'<input type="hidden" id="global-fqbn" value="{fqbn}" hx-swap-oob="true">'
            f'<input type="hidden" id="fqbn" name="fqbn" value="{fqbn}" hx-swap-oob="true">'
            f'<input type="hidden" id="active-board-hardware-id" name="hardware_id" value="{hardware_id}" hx-swap-oob="true">'
        )
        return oob

    @app.route("/board/compile-upload-card")
    def html_board_compile_upload_card():
        """Render the compile-upload card partial."""
        (active_board_port, active_board_fqbn, active_board_hardware_id) = (
            _get_active_board_info()
        )
        known_ports = get_known_boards()

        try:
            (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                _resolve_board_info(
                    active_board_port,
                    active_board_fqbn,
                    active_board_hardware_id,
                    known_ports,
                )
            )
        except ValueError as e:
            return str(e), 500

        active_board_path = (active_board_port or "").lstrip("/")
        return render_template(
            "partials/compile_upload_card.html",
            active_board=active_board_port,
            active_board_path=active_board_path,
            active_board_fqbn=active_board_fqbn,
            active_board_hardware_id=active_board_hardware_id,
        )

    @app.route("/last-upload")
    def html_last_upload():
        """Render the sketch path selector for the latest upload."""
        hardware_id = request.args.get("hardware_id", "").strip()
        if hardware_id:
            assigned = get_assignment(hardware_id)
            if assigned and os.path.isdir(assigned):
                return _render_sketch_path_selector(assigned, hardware_id=hardware_id)
        selected_path = _resolve_latest_upload()
        if selected_path is None:
            return _render_sketch_path_selector(hardware_id=hardware_id)
        return _render_sketch_path_selector(selected_path, hardware_id=hardware_id)

    @app.route("/sketch/upload", methods=["POST"])
    def html_sketch_upload():
        """Handle sketch upload via HTML form and return the path selector."""
        request.get_data()
        files = request.files.getlist("files[]")
        hardware_id = request.args.get("hardware_id", "").strip()
        if not files:
            return _render_sketch_path_selector()

        first_rel = files[0].filename or ""
        parts = first_rel.replace("\\", "/").split("/")
        root_name = parts[0] if parts else "sketch"

        server_ts = datetime.datetime.utcnow().isoformat()
        ts_dir = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = secure_filename(root_name) or "sketch"
        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "unknown")
        salt = hashlib.sha256(f"{ip}:{ua}".encode()).hexdigest()[:16]
        upload_dir = os.path.join(state.UPLOAD_BASE_DIR, f"{salt}_{ts_dir}_{safe_name}")
        os.makedirs(upload_dir, exist_ok=True)

        total_size = 0
        file_count = 0
        for f in files:
            rel_path = f.filename or ""
            if not rel_path:
                continue
            file_count += 1
            rel_parts = rel_path.replace("\\", "/").split("/")
            safe_parts = [secure_filename(p) or p for p in rel_parts]
            safe_rel = os.path.join(*safe_parts)
            dest = os.path.join(upload_dir, safe_rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            f.save(dest)
            total_size += os.path.getsize(dest)

        sketch_dir = os.path.join(upload_dir, safe_name)
        _normalize_ino_filename(sketch_dir, safe_name)

        checksum = _compute_sketch_checksum(sketch_dir)
        key = (ip, ua)

        with state._upload_registry_lock:
            user_sketches = state._upload_registry.setdefault(key, {})
            versions = user_sketches.setdefault(safe_name, [])
            existing = _find_existing_version(user_sketches, checksum)
            if existing:
                shutil.rmtree(upload_dir, ignore_errors=True)
                sketch_dir = existing["path"]
                if hardware_id and hardware_id not in existing["hardware_ids"]:
                    existing["hardware_ids"].append(hardware_id)
                    existing["board_timestamps"][hardware_id] = server_ts
                    _update_meta_hw_ids(
                        existing["path"],
                        existing["hardware_ids"],
                        existing["board_timestamps"],
                    )
                    _save_registry()
                    _broadcast_ws(
                        '<div class="sketch-event">Sketch deduplicated <!-- board-event --></div>'
                    )
            else:
                meta = {
                    "ip": ip,
                    "user_agent": ua,
                    "server_timestamp": server_ts,
                    "file_count": len(files),
                    "total_size": total_size,
                    "root_name": safe_name,
                    "checksum": checksum,
                    "hardware_ids": [hardware_id] if hardware_id else [],
                    "board_timestamps": {hardware_id: server_ts} if hardware_id else {},
                }
                with open(os.path.join(upload_dir, ".meta"), "w") as mf:
                    json.dump(meta, mf)
                bisect.insort(
                    versions,
                    {
                        "path": sketch_dir,
                        "checksum": checksum,
                        "server_timestamp": server_ts,
                        "hardware_ids": meta["hardware_ids"],
                        "board_timestamps": meta["board_timestamps"],
                    },
                    key=lambda v: v["server_timestamp"],
                )
                _save_registry()
                _broadcast_ws(
                    '<div class="sketch-event">Sketch updated <!-- board-event --></div>'
                )
                if hardware_id:
                    set_assignment(hardware_id, sketch_dir)

        return _render_sketch_path_selector(sketch_dir)

    @app.route("/sketch", methods=["DELETE"])
    def html_sketch_delete():
        """Handle sketch deletion and return the updated path selector."""
        sketch_path = request.args.get("path", "")
        if not sketch_path:
            return _render_sketch_path_selector()
        norm_path = os.path.normpath(sketch_path)
        norm_base = os.path.normpath(state.UPLOAD_BASE_DIR)
        if not norm_path.startswith(norm_base):
            return _render_sketch_path_selector()

        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "unknown")
        key = (ip, ua)
        removed = False
        with state._upload_registry_lock:
            entries = state._upload_registry.get(key, {})
            for name, versions in list(entries.items()):
                for i, v in enumerate(versions):
                    if not removed and v["path"] == norm_path:
                        versions.pop(i)
                        removed = True
                        if not versions:
                            del entries[name]
                        break
            if removed:
                all_latest = [vs[-1] for vs in entries.values() if vs]
                latest = (
                    max(all_latest, key=lambda v: v["server_timestamp"])
                    if all_latest
                    else None
                )
        if removed:
            shutil.rmtree(os.path.dirname(norm_path), ignore_errors=True)
            _save_registry()
            _broadcast_ws(
                '<div class="sketch-event">Sketch deleted <!-- board-event --></div>'
            )
            if latest is not None:
                return _render_sketch_path_selector(latest.get("path", ""))
            return _render_sketch_path_selector()
        return _render_sketch_path_selector()

    if sock:

        @sock.route("/ws/board-events")
        def ws_board_events(ws):
            """WebSocket endpoint that streams board events to clients."""
            with state._ws_lock:
                state._ws_clients.append(ws)
            try:
                while True:
                    data = ws.receive(timeout=30)
                    if data is None:
                        break
            except SystemExit:
                logger.info("WebSocket handler interrupted — gunicorn shutting down")
            finally:
                with state._ws_lock:
                    if ws in state._ws_clients:
                        state._ws_clients.remove(ws)

