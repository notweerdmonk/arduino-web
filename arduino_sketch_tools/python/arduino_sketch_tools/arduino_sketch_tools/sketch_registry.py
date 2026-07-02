"""arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/sketch_registry.py

Per-board sketch assignment registry keyed by hardware_id.

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
import threading
from typing import Optional


class SketchRegistry:
    """Thread-safe registry mapping hardware IDs to sketch paths.

    Operates on a shared upload registry dict (passed at init) whose
    structure is::

        {(ip, ua): {sketch_name: [version_dict, ...]}}

    Each version dict may contain a ``"hardware_ids"`` list that maps
    this board to a specific sketch version.
    """

    def __init__(self, registry: dict, lock: threading.Lock) -> None:
        self._registry = registry
        self._lock = lock
        self._op_lock = threading.Lock()

    def get_assignment(self, hardware_id: str) -> Optional[str]:
        if not hardware_id:
            return None
        with self._op_lock:
            with self._lock:
                for entry in self._registry.values():
                    for versions in entry.values():
                        for v in versions:
                            if hardware_id in v.get(
                                "hardware_ids", []
                            ) and os.path.isdir(v["path"]):
                                return v["path"]
        return None

    def set_assignment(self, hardware_id: str, sketch_dir: str) -> None:
        if not hardware_id:
            return
        with self._op_lock:
            with self._lock:
                for entry in self._registry.values():
                    for versions in entry.values():
                        for v in versions:
                            if v["path"] == sketch_dir:
                                if hardware_id not in v.get("hardware_ids", []):
                                    v.setdefault("hardware_ids", []).append(hardware_id)
                                return

    def clear_assignment(self, hardware_id: str) -> None:
        if not hardware_id:
            return
        with self._op_lock:
            with self._lock:
                for entry in self._registry.values():
                    for versions in entry.values():
                        for v in versions:
                            if hardware_id in v.get("hardware_ids", []):
                                v["hardware_ids"].remove(hardware_id)
                                return

    def get_all_assignments(self) -> dict[str, str]:
        result = {}
        with self._op_lock:
            with self._lock:
                for entry in self._registry.values():
                    for versions in entry.values():
                        for v in versions:
                            for hw_id in v.get("hardware_ids", []):
                                if os.path.isdir(v["path"]):
                                    result[hw_id] = v["path"]
        return result

    def reset_for_tests(self) -> None:
        pass

