"""Sketch upload/management routes (ported from arduino_dash)"""

import bisect
import datetime
import json
import os
from typing import Optional
from pathlib import Path

from flask import render_template, request

from medminder_dash import state
from medminder_dash.settings import _DEFAULT_SKETCH_DIR

REGISTRY_DIR = Path.home() / ".config" / "medminder"
REGISTRY_FILE = str(REGISTRY_DIR / "sketch_registry.json")


def _save_registry() -> None:
    """Persist the upload registry to disk.

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
    """Load the upload registry from disk.

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


def _compute_sketch_checksum(sketch_dir: str) -> str:
    """Compute a SHA-256 checksum for all files in a sketch directory.

    Args:
        sketch_dir: Path to the sketch directory.

    Returns:
        Hex digest string, or empty string if directory does not exist.
    """
    import hashlib

    h = hashlib.sha256()
    if not os.path.isdir(sketch_dir):
        return ""
    for root, _dirs, files in os.walk(sketch_dir):
        for f in sorted(files):
            path = os.path.join(root, f)
            try:
                rel = os.path.relpath(path, sketch_dir)
            except ValueError:
                continue
            h.update(rel.encode("utf-8", errors="replace"))
            with open(path, "rb") as fh:
                while True:
                    chunk = fh.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
    return h.hexdigest()


def _find_existing_version(user_sketches: dict, checksum: str) -> Optional[dict]:
    """Find a sketch version by checksum in the user's sketches.

    Args:
        user_sketches: User's sketch entries dict.
        checksum: Checksum to match.

    Returns:
        Matching version dict, or None.
    """
    for versions in user_sketches.values():
        for v in versions:
            if v["checksum"] == checksum:
                return v
    return None


def _update_meta_hw_ids(
    sketch_dir: str, hardware_ids: list, board_timestamps: dict
) -> None:
    """Update hardware_id and board_timestamp metadata in .meta file.

    Args:
        sketch_dir: Sketch directory path.
        hardware_ids: List of hardware IDs.
        board_timestamps: Dict mapping hardware_id to timestamp.
    """
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
    """Rename the .ino file in a sketch directory to match the directory name.

    Args:
        sketch_dir: Sketch directory path.
        target_stem: Desired stem name for the .ino file.
    """
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
    """Load persisted uploads from disk into the in-memory registry.

    Scans UPLOAD_BASE_DIR for .meta files and populates the registry.
    """
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
    """Return the path to the latest upload for the current user.

    Returns:
        Path string, or None if no uploads found.
    """
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
    """Build a dict mapping hardware IDs to human-readable board labels.

    Returns:
        Dict of hardware_id -> label string.
    """
    labels = {}
    with state._known_ports_lock:
        for port, info in state._known_ports.items():
            hw_id = info.get("hardware_id", "")
            if hw_id:
                board_name = info.get("board", "") or port
                labels[hw_id] = f"{board_name} ({port})"
    return labels


def _render_sketch_path_selector(
    selected_path: str = "", include_default: bool = False, hardware_id: str = ""
) -> str:
    """Render the sketch path selector HTML partial.

    Args:
        selected_path: Currently selected sketch path.
        include_default: Whether to include the default MedMinderV2 sketch.
        hardware_id: Filter sketches by hardware ID.

    Returns:
        Rendered HTML template string.
    """
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
    if include_default and _DEFAULT_SKETCH_DIR not in seen_paths:
        sketches.insert(0, {"name": "MedMinderV2", "path": _DEFAULT_SKETCH_DIR})
        seen_paths.add(_DEFAULT_SKETCH_DIR)
    if not selected_path and include_default:
        selected_path = _DEFAULT_SKETCH_DIR
    if selected_path and selected_path not in seen_paths:
        sketches.append(
            {
                "name": os.path.basename(selected_path) or selected_path,
                "path": selected_path,
            }
        )
    return render_template(
        "partials/sketch_path_selector.html",
        sketches=sketches,
        selected=selected_path,
        hardware_id=hardware_id,
    )
