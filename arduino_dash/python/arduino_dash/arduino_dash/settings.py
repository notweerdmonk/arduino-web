"""Application settings and default paths."""

from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "arduino-dash"
UPLOAD_BASE_DIR = str(Path.home() / ".local" / "share" / "arduino-dash" / "uploads")
