---
---
# settings (settings.py)

Application settings and default paths.

## Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `CONFIG_DIR` | `Path` | `Path.home() / ".config" / "arduino-dash"` | Directory for configuration files (e.g., `sketch_registry.json`) |
| `UPLOAD_BASE_DIR` | `str` | `str(Path.home() / ".local" / "share" / "arduino-dash" / "uploads")` | Base directory for storing uploaded sketch files |

## Usage

```python
from arduino_dash.settings import CONFIG_DIR, UPLOAD_BASE_DIR

# CONFIG_DIR: /home/user/.config/arduino-dash
# UPLOAD_BASE_DIR: /home/user/.local/share/arduino-dash/uploads
```

`CONFIG_DIR` is used by `sketch_management.py` for the `REGISTRY_DIR` location. `UPLOAD_BASE_DIR` is re-exported from `state.py` and used across `html_routes.py`, `api_routes.py`, and `sketch_management.py` for sketch file storage.
