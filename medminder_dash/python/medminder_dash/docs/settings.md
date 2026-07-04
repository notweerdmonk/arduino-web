---
layout: default
---
# `settings.py` — Sketch Directory Configuration

**File:** `medminder_dash/settings.py`

Manages the sketch directory path used for `alarm.hpp` generation and Arduino
sketch compilation. The sketch directory can be configured via
`~/.config/medminder/sketch_dir.json`, with a fallback to the MedMinderV2
sketch bundled in the wheel.

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `CONFIG_DIR` | `Path.home() / ".config" / "medminder"` | Configuration directory |
| `CONFIG_FILE` | `CONFIG_DIR / "sketch_dir.json"` | Per-user config file |
| `_DEFAULT_SKETCH_DIR` | `_resolve_default_sketch_dir()` | Resolved default sketch path |

## Functions

### `_resolve_default_sketch_dir() -> str`

Return path to the MedMinderV2 default sketch, extracting from the package
wheel if needed.

Priority:
1. **XDG data dir** — `~/.local/share/medminder/sketches/MedMinderV2/` — if
   the directory already exists, return it immediately.
2. **Package extraction** — Look for
   `medminder_dash/sketches/MedMinderV2/` inside the installed package via
   `importlib.resources.files()`. If found, copy all files to the XDG data
   dir and return that path.
3. **Fallback** — Return `""` if neither exists.

```python
path = _resolve_default_sketch_dir()
# "/home/user/.local/share/medminder/sketches/MedMinderV2"
```

### `_ensure_config_dir() -> None`

Create the config directory `~/.config/medminder` if it does not exist.

### `reset_default_sketch_dir() -> None`

Recompute `_DEFAULT_SKETCH_DIR` by calling `_resolve_default_sketch_dir()`.
Intended for testing only.

### `load_sketch_dir() -> str`

Load the configured sketch directory path, falling back to the default.

1. Read `CONFIG_FILE` (`sketch_dir.json`)
2. If the file exists and contains a truthy `sketch_dir` key, return it
3. Otherwise return `_DEFAULT_SKETCH_DIR`

```python
sketch_dir = load_sketch_dir()
# "/home/user/.local/share/medminder/sketches/MedMinderV2"
```

### `set_sketch_dir(path: str) -> None`

Persist the sketch directory path to `sketch_dir.json`.

```python
set_sketch_dir("/home/user/custom_sketch")
# Writes {"sketch_dir": "/home/user/custom_sketch"} to config file
```

## Config File Format

```json
{
  "sketch_dir": "/home/user/.local/share/medminder/sketches/MedMinderV2"
}
```
