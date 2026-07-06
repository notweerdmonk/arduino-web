"""medminder_dash/python/medminder_dash/medminder_dash/api_routes.py

JSON API routes — /api/ prefix

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

from flask import Flask, jsonify, request, session
from werkzeug.utils import secure_filename

from medminder_dash import state
from medminder_dash.medicines_state import Medicine
from medminder_dash.pubsub import (
    _get_alarm_hpp_path,
    broadcast_ws,
    ensure_sketch_dir,
    get_pubsub,
    is_connected,
    is_daemon_ready,
)
from medminder_dash.settings import _DEFAULT_SKETCH_DIR
from medminder_dash.sketch_gen import generate_alarm_hpp, parse_alarm_hpp
from medminder_dash.sketch_management import (
    _compute_sketch_checksum,
    _find_existing_version,
    _normalize_ino_filename,
    _resolve_latest_upload,
    _save_registry,
    _update_meta_hw_ids,
    _warm_upload_registry,
)
from medminder_dash.sketch_registry import (
    get_assignment,
    set_assignment,
)
from medminder_dash.utils import (
    get_board_events,
    get_known_ports,
    get_port_info,
    validate_medicine_data,
)

logger = logging.getLogger(__name__)

store = None


def _get_active_board_info():
    """Return the active board info tuple from the session.

    Returns:
        Tuple of (port, fqbn, hardware_id).
    """
    raw = session.get("admin_active_board")
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        return (str(raw[0]), str(raw[1]), str(raw[2]))
    if isinstance(raw, str):
        return (raw, "", "")
    return ("", "", "")


def _medicine_to_dict(med):
    """Convert a Medicine object to a serializable dict.

    Args:
        med: Medicine instance.

    Returns:
        Dict with medicine fields.
    """
    return {
        "name": med.name,
        "hour": med.hour,
        "minute": med.minute,
        "day_of_week": med.day_of_week,
        "day_of_month": med.day_of_month,
    }


def _medicine_dict_sort_key(d):
    """Return a sort key for a medicine dict.

    Args:
        d: Medicine dict.

    Returns:
        Tuple for sorting.
    """
    return (d["name"], d["hour"], d["minute"], d["day_of_week"], d["day_of_month"])


def _compute_diff(active_board):
    """Compute the difference between metadata and alarm.hpp entries.

    Args:
        active_board: Active board port string.

    Returns:
        Diff dict with metadata, alarm_hpp, differ flag, and active_board.
    """
    metadata_list = sorted(
        [_medicine_to_dict(m) for m in store.only_enabled()],
        key=_medicine_dict_sort_key,
    )
    path = _get_alarm_hpp_path()
    if not os.path.exists(path):
        return {
            "metadata": metadata_list,
            "alarm_hpp": [],
            "differ": True,
            "alarm_hpp_exists": False,
            "alarm_hpp_error": None,
            "active_board": active_board,
        }
    try:
        parsed = parse_alarm_hpp(path)
        alarm_hpp_list = sorted(
            [
                {
                    "name": e["name"],
                    "hour": e["hour"],
                    "minute": e["minute"],
                    "day_of_week": e["day_of_week"],
                    "day_of_month": e["day_of_month"],
                }
                for e in parsed
            ],
            key=_medicine_dict_sort_key,
        )
        differ = metadata_list != alarm_hpp_list
        return {
            "metadata": metadata_list,
            "alarm_hpp": alarm_hpp_list,
            "differ": differ,
            "alarm_hpp_exists": True,
            "alarm_hpp_error": None,
            "active_board": active_board,
        }
    except Exception as e:
        return {
            "metadata": metadata_list,
            "alarm_hpp": [],
            "differ": True,
            "alarm_hpp_exists": True,
            "alarm_hpp_error": str(e),
            "active_board": active_board,
        }


def _write_alarm_hpp(meds):
    """Write the alarm.hpp file from a list of medicines.

    Args:
        meds: List of Medicine instances.
    """
    try:
        ensure_sketch_dir()
        path = _get_alarm_hpp_path()
        content = generate_alarm_hpp(meds)
        with open(path, "w") as f:
            f.write(content)
        logger.info("Wrote alarm.hpp (%d medicines) to %s", len(meds), path)
    except Exception:
        logger.exception("Failed to write alarm.hpp")


def init_api_routes(app: Flask, store_param):
    """Register all JSON API routes on the Flask app.

    Args:
        app: Flask application instance.
        store_param: MedicineStore instance.
    """
    global store
    store = store_param

    # ------------------------------------------------------------------ #
    #  Existing JSON API routes from app.py                               #
    # ------------------------------------------------------------------ #

    @app.route("/api/medicines/diff")
    def api_medicines_diff():
        """Return the diff between store medicines and alarm.hpp."""
        active_board, _, _ = _get_active_board_info()
        if active_board:
            store.load_board(active_board)
        diff = _compute_diff(active_board)
        return jsonify(diff)

    # ------------------------------------------------------------------ #
    #  Existing JSON API routes from board_management.py                  #
    # ------------------------------------------------------------------ #

    @app.route("/api/boards/list")
    def api_board_list():
        """Return the list of known board ports as JSON."""
        boards = get_known_ports()
        return jsonify(boards)

    @app.route("/api/pubsub/board/<path:port>/spawn", methods=["POST"])
    def api_pubsub_spawn(port: str):
        """Spawn the board monitor via PubSub."""
        from medminder_dash.utils import normalize_port
        port = normalize_port(port)
        if port is None:
            return jsonify({"error": "Invalid port"}), 400
        ps = get_pubsub()
        if not ps:
            return jsonify({"error": "PubSub not connected"}), 503
        ps.publish(f"board::{port}::cmd", {"method": "spawn"}, f"resp:spawn:{port}")
        return jsonify({"status": "accepted"})

    @app.route("/api/pubsub/board/<path:port>/status")
    def api_pubsub_board_status(port: str):
        """Request board status via PubSub."""
        from medminder_dash.utils import normalize_port
        port = normalize_port(port)
        if port is None:
            return jsonify({"error": "Invalid port"}), 400
        ps = get_pubsub()
        if not ps:
            return jsonify({"error": "PubSub not connected"}), 503
        ps.publish(f"board::{port}::cmd", {"method": "status"}, f"resp:status:{port}")
        return jsonify({"status": "accepted"})

    @app.route("/api/pubsub/board/<path:port>/remove", methods=["POST"])
    def api_pubsub_remove_board(port: str):
        """Remove the board monitor via PubSub."""
        from medminder_dash.utils import normalize_port
        port = normalize_port(port)
        if port is None:
            return jsonify({"error": "Invalid port"}), 400
        ps = get_pubsub()
        if not ps:
            return jsonify({"error": "PubSub not connected"}), 503
        ps.publish(f"board::{port}::cmd", {"method": "remove"}, f"resp:remove:{port}")
        return jsonify({"status": "accepted"})

    @app.route("/api/pubsub/boards/health", methods=["POST"])
    def api_pubsub_boards_health():
        """Trigger health check for all boards via PubSub."""
        ps = get_pubsub()
        if not ps:
            return jsonify({"error": "PubSub not connected"}), 503
        ps.publish("sys/health", {"method": "health"}, "")
        return jsonify({"status": "accepted"})

    @app.route("/api/daemon/status")
    def api_daemon_status():
        """Return daemon status (ready + connected) as JSON."""
        ready = is_daemon_ready()
        connected = is_connected()
        return jsonify({"ready": ready, "connected": connected})

    @app.route("/api/board/<path:port>/status")
    def api_board_connection_status(port: str):
        """Return connection status for the board at the given port from local state."""
        from medminder_dash.utils import normalize_port
        port = normalize_port(port)
        if port is None:
            return jsonify({"error": "Invalid port"}), 400
        info = get_port_info(port)
        connected = bool(info)
        return jsonify({
            "connected": connected,
            "port": port,
            "fqbn": info.get("fqbn", ""),
            "hardware_id": info.get("hardware_id", ""),
        })

    @app.route("/api/boards/events")
    def api_boards_events():
        """Return the board events buffer as JSON."""
        events = get_board_events()
        return jsonify(events)

    # ------------------------------------------------------------------ #
    #  JSON API versions of sketch routes (from sketch_management.py)     #
    # ------------------------------------------------------------------ #

    @app.route("/api/sketches")
    def api_sketches():
        """Return all uploaded sketches as JSON. Supports ?hardware_id=X filter."""
        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "unknown")
        key = (ip, ua)
        hw_id = request.args.get("hardware_id", "").strip()
        all_versions = []
        with state._upload_registry_lock:
            if key not in state._upload_registry:
                _warm_upload_registry()
            entries = state._upload_registry.get(key, {})
            for name, versions in entries.items():
                for v in versions:
                    if hw_id and hw_id not in v.get("hardware_ids", []):
                        continue
                    all_versions.append(
                        {
                            "name": name,
                            "path": v["path"],
                            "timestamp": v["server_timestamp"],
                        }
                    )
        all_versions.sort(key=lambda v: v["timestamp"], reverse=True)
        all_versions.insert(
            0,
            {
                "name": "MedMinderV2",
                "path": _DEFAULT_SKETCH_DIR,
                "timestamp": "",
            },
        )
        return jsonify(all_versions)

    @app.route("/api/sketch/upload", methods=["POST"])
    def api_sketch_upload():
        """Handle sketch file upload via API."""
        request.get_data()
        files = request.files.getlist("files[]")
        hardware_id = request.args.get("hardware_id", "")
        if not files:
            return jsonify({"error": "No files provided"}), 400

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
                    broadcast_ws(
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
                broadcast_ws(
                    '<div class="sketch-event">Sketch updated <!-- board-event --></div>'
                )

        if hardware_id:
            set_assignment(hardware_id, sketch_dir)

        return jsonify({"path": sketch_dir})

    @app.route("/api/sketch", methods=["DELETE"])
    def api_sketch_delete():
        """Delete an uploaded sketch via API."""
        sketch_path = request.args.get("path", "")
        if not sketch_path:
            return jsonify({"error": "Missing path"}), 400
        norm_path = os.path.normpath(sketch_path)
        norm_base = os.path.normpath(state.UPLOAD_BASE_DIR)
        if not norm_path.startswith(norm_base):
            return jsonify({"error": "Invalid path"}), 403

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
            _save_registry()
            broadcast_ws(
                '<div class="sketch-event">Sketch deleted <!-- board-event --></div>'
            )
            shutil.rmtree(os.path.dirname(norm_path), ignore_errors=True)
            return jsonify({"status": "deleted"})
        return jsonify({"error": "Not found"}), 404

    @app.route("/api/sketches/last-upload")
    def api_sketches_last_upload():
        """Return the latest uploaded sketch as JSON, or null with 404 if none."""
        hardware_id = request.args.get("hardware_id", "").strip()
        if hardware_id:
            sketch_dir = get_assignment(hardware_id)
            if sketch_dir:
                sketch_name = os.path.basename(os.path.normpath(sketch_dir))
                return jsonify({
                    "path": sketch_dir,
                    "name": sketch_name,
                    "timestamp": "",
                })
        latest = _resolve_latest_upload()
        if latest:
            sketch_name = os.path.basename(os.path.normpath(latest))
            return jsonify({
                "path": latest,
                "name": sketch_name,
                "timestamp": "",
            })
        return jsonify(None), 404

    # ------------------------------------------------------------------ #
    #  NEW REST CRUD endpoints for medicines                              #
    # ------------------------------------------------------------------ #

    @app.route("/api/medicines", methods=["GET"])
    def api_medicines_list():
        """Return all medicines as JSON."""
        meds = store.all()
        return jsonify(
            [
                {
                    "id": m.id,
                    "name": m.name,
                    "hour": m.hour,
                    "minute": m.minute,
                    "day_of_week": m.day_of_week,
                    "day_of_month": m.day_of_month,
                    "enabled": m.enabled,
                }
                for m in meds
            ]
        )

    @app.route("/api/medicine", methods=["POST"])
    def api_medicine_create():
        """Create a new medicine via API."""
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be JSON"}), 400
        errors = validate_medicine_data(data)
        if errors:
            return jsonify({"error": errors}), 400
        med = Medicine(
            name=data.get("name", "").strip(),
            hour=int(data.get("hour", 0)),
            minute=int(data.get("minute", 0)),
            day_of_week=int(data.get("day_of_week", 0)),
            day_of_month=int(data.get("day_of_month", 0)),
        )
        store.add(med)
        _write_alarm_hpp(store.only_enabled())
        return jsonify(
            {
                "id": med.id,
                "name": med.name,
                "hour": med.hour,
                "minute": med.minute,
                "day_of_week": med.day_of_week,
                "day_of_month": med.day_of_month,
                "enabled": med.enabled,
            }
        ), 201

    @app.route("/api/medicine/<med_id>", methods=["GET"])
    def api_medicine_get(med_id):
        """Return a single medicine by ID as JSON."""
        med = store.get(med_id)
        if med is None:
            return jsonify({"error": "Not found"}), 404
        return jsonify(
            {
                "id": med.id,
                "name": med.name,
                "hour": med.hour,
                "minute": med.minute,
                "day_of_week": med.day_of_week,
                "day_of_month": med.day_of_month,
                "enabled": med.enabled,
            }
        )

    @app.route("/api/medicine/<med_id>", methods=["PUT"])
    def api_medicine_update(med_id):
        """Update a medicine by ID via API."""
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be JSON"}), 400
        med = store.get(med_id)
        if med is None:
            return jsonify({"error": "Not found"}), 404
        errors = validate_medicine_data(data)
        if errors:
            return jsonify({"error": errors}), 400
        store.update(
            med_id,
            name=data.get("name", "").strip(),
            hour=int(data.get("hour", 0)),
            minute=int(data.get("minute", 0)),
            day_of_week=int(data.get("day_of_week", 0)),
            day_of_month=int(data.get("day_of_month", 0)),
        )
        _write_alarm_hpp(store.only_enabled())
        updated = store.get(med_id)
        return jsonify(
            {
                "id": updated.id,
                "name": updated.name,
                "hour": updated.hour,
                "minute": updated.minute,
                "day_of_week": updated.day_of_week,
                "day_of_month": updated.day_of_month,
                "enabled": updated.enabled,
            }
        )

    @app.route("/api/medicine/<med_id>", methods=["DELETE"])
    def api_medicine_delete(med_id):
        """Delete a medicine by ID via API."""
        med = store.get(med_id)
        if med is None:
            return jsonify({"error": "Not found"}), 404
        store.delete(med_id)
        _write_alarm_hpp(store.only_enabled())
        return jsonify({"status": "deleted"})

    @app.route("/api/medicine/<med_id>/toggle", methods=["PUT"])
    def api_medicine_toggle(med_id):
        """Toggle a medicine's enabled state via API."""
        med = store.get(med_id)
        if med is None:
            return jsonify({"error": "Not found"}), 404
        store.toggle(med_id)
        _write_alarm_hpp(store.only_enabled())
        toggled = store.get(med_id)
        return jsonify(
            {
                "id": toggled.id,
                "name": toggled.name,
                "hour": toggled.hour,
                "minute": toggled.minute,
                "day_of_week": toggled.day_of_week,
                "day_of_month": toggled.day_of_month,
                "enabled": toggled.enabled,
            }
        )

