"""Per-board sketch assignment registry keyed by hardware_id.
Backed by _upload_registry in-memory dict.
"""

import os
import threading
from typing import Optional

from medminder_dash import state

_lock = threading.Lock()


def get_assignment(hardware_id: str) -> Optional[str]:
    """Return the sketch path assigned to a hardware ID, or None.

    Args:
        hardware_id: Board hardware ID.

    Returns:
        Sketch directory path or None.
    """
    if not hardware_id:
        return None
    with _lock:
        with state._upload_registry_lock:
            for entry in state._upload_registry.values():
                for versions in entry.values():
                    for v in versions:
                        if hardware_id in v.get("hardware_ids", []) and os.path.isdir(v["path"]):
                            return v["path"]
    return None


def set_assignment(hardware_id: str, sketch_dir: str) -> None:
    """Assign a sketch path to a hardware ID.

    Args:
        hardware_id: Board hardware ID.
        sketch_dir: Sketch directory path to assign.
    """
    if not hardware_id:
        return
    with _lock:
        with state._upload_registry_lock:
            for entry in state._upload_registry.values():
                for versions in entry.values():
                    for v in versions:
                        if v["path"] == sketch_dir:
                            if hardware_id not in v.get("hardware_ids", []):
                                v.setdefault("hardware_ids", []).append(hardware_id)
                            return


def clear_assignment(hardware_id: str) -> None:
    """Remove the sketch assignment for a hardware ID.

    Args:
        hardware_id: Board hardware ID.
    """
    if not hardware_id:
        return
    with _lock:
        with state._upload_registry_lock:
            for entry in state._upload_registry.values():
                for versions in entry.values():
                    for v in versions:
                        if hardware_id in v.get("hardware_ids", []):
                            v["hardware_ids"].remove(hardware_id)
                            return


def get_all_assignments() -> dict[str, str]:
    """Return all hardware ID to sketch path assignments.

    Returns:
        Dict of hardware_id -> sketch_dir.
    """
    result = {}
    with _lock:
        with state._upload_registry_lock:
            for entry in state._upload_registry.values():
                for versions in entry.values():
                    for v in versions:
                        for hw_id in v.get("hardware_ids", []):
                            if os.path.isdir(v["path"]):
                                result[hw_id] = v["path"]
    return result


def reset_for_tests() -> None:
    """Reset internal state for testing (no-op)."""
    pass
