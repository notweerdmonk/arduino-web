"""Per-board sketch assignment registry keyed by hardware_id.
Backed by _upload_registry in-memory dict.
"""

import os
import threading
from typing import Optional

from arduino_dash import state

_lock = threading.Lock()


def get_assignment(hardware_id: str) -> Optional[str]:
    """Return the sketch path assigned to the given hardware ID."""
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
    """Assign a sketch directory to a hardware ID."""
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
    """Remove the sketch assignment for a hardware ID."""
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
    """Return all hardware ID to sketch path assignments."""
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
    """Reset the registry for test isolation (no-op)."""
    pass
