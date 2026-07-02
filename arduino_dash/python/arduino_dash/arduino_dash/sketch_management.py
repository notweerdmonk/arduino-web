"""arduino_dash/python/arduino_dash/arduino_dash/sketch_management.py

Sketch upload/management helpers — routes moved to html_routes.py and api_routes.py

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
import json
import os
from pathlib import Path
from typing import Optional

from flask import render_template, request

from arduino_dash import state
from arduino_dash.pubsub import _compute_sketch_checksum

REGISTRY_DIR = Path.home() / ".config" / "arduino-dash"
REGISTRY_FILE = str(REGISTRY_DIR / "sketch_registry.json")


def _save_registry() -> None:
    """Persist the upload registry to disk as JSON.

    Caller must hold state._upload_registry_lock.
    """
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    serializable = {}
    for key, user_sketches in state._upload_registry.items():
        ip, ua = key
        serializable[json.dumps([ip, ua])] = user_sketches
    with open(REGISTRY_FILE, "w") as f:
        json.dump(serializable, f)


def _load_registry() -> None:
    """Load the upload registry from disk into memory.

    Caller must hold state._upload_registry_lock.
    """
    if not os.path.isfile(REGISTRY_FILE):
        return
    try:
        with open(REGISTRY_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return
    for key_json, user_sketches in data.items():
        ip, ua = json.loads(key_json)
        key = (ip, ua)
        state._upload_registry[key] = user_sketches


def _find_existing_version(user_sketches: dict, checksum: str) -> Optional[dict]:
    """Find an existing sketch version matching the checksum."""
    for versions in user_sketches.values():
        for v in versions:
            if v["checksum"] == checksum:
                return v
    return None


def _update_meta_hw_ids(
    sketch_dir: str, hardware_ids: list, board_timestamps: dict
) -> None:
    """Update the hardware IDs and board timestamps in a sketch's .meta file."""
    meta_path = os.path.join(os.path.dirname(sketch_dir), ".meta")
    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    meta["hardware_ids"] = hardware_ids
    meta["board_timestamps"] = board_timestamps
    try:
        with open(meta_path, "w") as f:
            json.dump(meta, f)
    except OSError:
        pass


def _normalize_ino_filename(sketch_dir: str, target_stem: str) -> None:
    """Rename the single .ino file in a sketch directory to match the sketch folder name."""
    target_name = target_stem + ".ino"
    try:
        entries = os.listdir(sketch_dir)
    except OSError:
        return
    ino_files = [e for e in entries if e.endswith(".ino")]
    if len(ino_files) != 1:
        return
    stem, _ = os.path.splitext(ino_files[0])
    if stem == target_stem:
        return
    os.rename(
        os.path.join(sketch_dir, ino_files[0]),
        os.path.join(sketch_dir, target_name),
    )


def _warm_upload_registry() -> None:
    """Populate the upload registry from the upload directory on disk."""
    if not os.path.isdir(state.UPLOAD_BASE_DIR):
        return
    _load_registry()
    for entry in os.listdir(state.UPLOAD_BASE_DIR):
        meta_path = os.path.join(state.UPLOAD_BASE_DIR, entry, ".meta")
        if not os.path.isfile(meta_path):
            continue
        try:
            with open(meta_path) as mf:
                meta = json.load(mf)
        except (json.JSONDecodeError, OSError):
            continue
        ip = meta.get("ip", "unknown")
        ua = meta.get("user_agent", "unknown")
        root_name = meta.get("root_name")
        if not root_name:
            continue
        key = (ip, ua)
        sketch_dir = os.path.join(state.UPLOAD_BASE_DIR, entry, root_name)
        server_ts = meta.get("server_timestamp") or meta.get("timestamp", "")
        version = {
            "path": sketch_dir,
            "checksum": meta.get("checksum") or _compute_sketch_checksum(sketch_dir),
            "server_timestamp": server_ts,
            "hardware_ids": meta.get("hardware_ids", []),
            "board_timestamps": meta.get("board_timestamps", {}),
        }
        versions = state._upload_registry.setdefault(key, {}).setdefault(root_name, [])
        if not any(v["path"] == version["path"] for v in versions):
            bisect.insort(versions, version, key=lambda v: v["server_timestamp"])


def _resolve_latest_upload() -> Optional[str]:
    """Return the path to the latest uploaded sketch for the requesting client."""
    ip = request.remote_addr or "unknown"
    ua = request.headers.get("User-Agent", "unknown")
    key = (ip, ua)
    with state._upload_registry_lock:
        if key not in state._upload_registry:
            _warm_upload_registry()
        all_latest = [
            vs[-1] for vs in state._upload_registry.get(key, {}).values() if vs
        ]
        if all_latest:
            latest = max(all_latest, key=lambda v: v["server_timestamp"])
            if os.path.isdir(latest["path"]):
                return latest["path"]
    return None


def _build_hw_labels() -> dict[str, str]:
    """Build a mapping of hardware IDs to human-readable labels."""
    labels = {}
    with state._board_list_lock:
        for port, info in state._board_list.items():
            hw_id = info.get("hardware_id", "")
            if hw_id:
                board_name = info.get("board", "") or port
                labels[hw_id] = f"{board_name} ({port})"
    return labels


def _render_sketch_path_selector(selected_path: str = "", hardware_id: str = "") -> str:
    """Render the sketch path selector dropdown HTML partial."""
    ip = request.remote_addr or "unknown"
    ua = request.headers.get("User-Agent", "unknown")
    key = (ip, ua)
    with state._upload_registry_lock:
        if key not in state._upload_registry:
            _warm_upload_registry()
        entries = state._upload_registry.get(key, {})
    hw_labels = _build_hw_labels()
    sketches = []
    seen_paths = set()
    all_versions = []
    for name, versions in entries.items():
        for v in versions:
            if hardware_id and hardware_id not in v.get("hardware_ids", []):
                continue
            all_versions.append((name, v))
    all_versions.sort(key=lambda x: x[1]["server_timestamp"], reverse=True)
    for name, v in all_versions:
        label = name
        ts = v.get("server_timestamp", "")
        if ts:
            try:
                dt = datetime.datetime.fromisoformat(ts).replace(
                    tzinfo=datetime.timezone.utc
                )
                local_dt = dt.astimezone()
                label = f"{name} ({local_dt.strftime('%Y-%m-%d %H:%M:%S')})"
            except (ValueError, TypeError):
                pass
        board_labels = [
            hw_labels[hw] for hw in v.get("hardware_ids", []) if hw in hw_labels
        ]
        if board_labels:
            label += f" [{' / '.join(board_labels)}]"
        sketches.append({"name": label, "path": v["path"]})
        seen_paths.add(v["path"])
    if selected_path and selected_path not in seen_paths:
        sketches.append(
            {
                "name": os.path.basename(selected_path) or selected_path,
                "path": selected_path,
            }
        )
    return render_template(
        "partials/sketch_path_selector.html", sketches=sketches, selected=selected_path
    )

