"""JSON API routes — /api/ prefix"""

import bisect
import datetime
import hashlib
import json
import logging
import os
import shutil

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from arduino_dash import state
from arduino_dash.pubsub import (
    _broadcast_ws,
    _compute_sketch_checksum,
)
from arduino_dash.sketch_management import (
    _find_existing_version,
    _normalize_ino_filename,
    _save_registry,
    _update_meta_hw_ids,
)
from arduino_dash.sketch_registry import set_assignment
from arduino_dash.utils import normalize_port

logger = logging.getLogger(__name__)


def init_api_routes(app: Flask):
    """Register all /api/ route handlers on the Flask app."""

    @app.route("/api/board/<path:port>/spawn", methods=["POST"])
    def api_spawn(port: str):
        """Spawn the board monitor for the given port."""
        port = normalize_port(port)
        if port is None:
            return jsonify({"error": "Invalid port"}), 400
        state.pubsub.publish(
            f"board::{port}::cmd", {"method": "spawn"}, f"resp:spawn:{port}"
        )
        return jsonify({"status": "accepted"})

    @app.route("/api/board/<path:port>/status")
    def api_board_status(port: str):
        """Request status for the board at the given port."""
        port = normalize_port(port)
        if port is None:
            return jsonify({"error": "Invalid port"}), 400
        state.pubsub.publish(
            f"board::{port}::cmd", {"method": "status"}, f"resp:status:{port}"
        )
        return jsonify({"status": "accepted"})

    @app.route("/api/board/<path:port>/remove", methods=["POST"])
    def api_remove_board(port: str):
        """Remove the board at the given port."""
        port = normalize_port(port)
        if port is None:
            return jsonify({"error": "Invalid port"}), 400
        state.pubsub.publish(
            f"board::{port}::cmd", {"method": "remove"}, f"resp:remove:{port}"
        )
        return jsonify({"status": "accepted"})

    @app.route("/api/boards")
    def api_list_boards():
        """List all known boards."""
        state.pubsub.publish("sys/health", {"method": "health"}, "")
        return jsonify({"status": "accepted"})

    @app.route("/api/sketches")
    def api_sketches():
        """List all uploaded sketches for the requesting client."""
        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "unknown")
        key = (ip, ua)
        all_versions = []
        with state._upload_registry_lock:
            if key not in state._upload_registry:
                from arduino_dash.sketch_management import _warm_upload_registry

                _warm_upload_registry()
            entries = state._upload_registry.get(key, {})
            for name, versions in entries.items():
                for v in versions:
                    all_versions.append(
                        {
                            "name": name,
                            "path": v["path"],
                            "timestamp": v["server_timestamp"],
                        }
                    )
        all_versions.sort(key=lambda v: v["timestamp"], reverse=True)
        return jsonify(all_versions)

    @app.route("/api/sketch/upload", methods=["POST"])
    def api_sketch_upload():
        """Handle sketch file upload and return the sketch path."""
        request.get_data()
        files = request.files.getlist("files[]")
        hardware_id = request.args.get("hardware_id", "").strip()
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

        return jsonify({"path": sketch_dir})

    @app.route("/api/sketch", methods=["DELETE"])
    def api_sketch_delete():
        """Delete an uploaded sketch by path."""
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
            shutil.rmtree(os.path.dirname(norm_path), ignore_errors=True)
            _save_registry()
            _broadcast_ws(
                '<div class="sketch-event">Sketch deleted <!-- board-event --></div>'
            )
            return jsonify({"status": "deleted"})
        return jsonify({"error": "Not found"}), 404
