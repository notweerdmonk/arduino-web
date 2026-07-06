"""medminder_dash/python/medminder_dash/medminder_dash/settings.py

Sketch directory configuration and defaults.

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

import importlib.resources
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "medminder"
CONFIG_FILE = CONFIG_DIR / "sketch_dir.json"


def _resolve_default_sketch_dir() -> str:
    """Return path to MedMinderV2 default sketch, extracting from wheel if needed.

    Priority:
    1. Extracted XDG data dir (~/.local/share/medminder/sketches/MedMinderV2/)
    """
    xdg_dir = Path.home() / ".local" / "share" / "medminder" / "sketches" / "MedMinderV2"
    if xdg_dir.is_dir():
        return str(xdg_dir)

    try:
        pkg_sketch = importlib.resources.files("medminder_dash") / "sketches" / "MedMinderV2"
        if pkg_sketch.is_dir():
            xdg_dir.mkdir(parents=True, exist_ok=True)
            for entry in pkg_sketch.iterdir():
                if entry.is_file():
                    (xdg_dir / entry.name).write_bytes(entry.read_bytes())
            return str(xdg_dir)
    except Exception:
        pass

    return ""


_DEFAULT_SKETCH_DIR = _resolve_default_sketch_dir()


def _ensure_config_dir():
    """Create the config directory if it does not exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def reset_default_sketch_dir() -> None:
    """Recompute _DEFAULT_SKETCH_DIR (testing only)."""
    global _DEFAULT_SKETCH_DIR
    _DEFAULT_SKETCH_DIR = _resolve_default_sketch_dir()


def load_sketch_dir() -> str:
    """Load the configured sketch directory path, falling back to default."""
    _ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                path = data.get("sketch_dir", "")
                if path:
                    return path
        except (json.JSONDecodeError, OSError):
            pass
    return _DEFAULT_SKETCH_DIR


def set_sketch_dir(path: str) -> None:
    """Persist the sketch directory path to the config file."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump({"sketch_dir": path}, f)
