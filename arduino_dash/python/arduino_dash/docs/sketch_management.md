---
layout: default
---
# sketch_management (sketch_management.py)

Sketch upload/management helpers — registry persistence, version lookup, filename normalization, and path selector rendering. Routes are in `html_routes.py` and `api_routes.py`.

## Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `REGISTRY_DIR` | `Path` | `Path.home() / ".config" / "arduino-dash"` | Directory for the sketch registry file |
| `REGISTRY_FILE` | `str` | `str(REGISTRY_DIR / "sketch_registry.json")` | Path to the persisted sketch registry JSON |

## Functions

### `_save_registry() -> None`

Persist the upload registry to disk as JSON. Caller must hold `state._upload_registry_lock`.

Serializes the `{(ip, ua): {name: [versions]}}` dict to `sketch_registry.json`. Tuple keys are JSON-serialized as `"[ip, ua]"` strings.

```python
with state._upload_registry_lock:
    _save_registry()
```

### `_load_registry() -> None`

Load the upload registry from disk into memory. Caller must hold `state._upload_registry_lock`. Reads `REGISTRY_FILE` and populates `state._upload_registry`. Silently returns if file doesn't exist or is malformed.

```python
with state._upload_registry_lock:
    _load_registry()
```

### `_find_existing_version(user_sketches: dict, checksum: str) -> Optional[dict]`

Find an existing sketch version matching the SHA-256 checksum. Searches all versions across all sketches for a given user. Returns the version dict or `None`.

```python
existing = _find_existing_version(user_sketches, computed_checksum)
if existing:
    print(f"Dedup: reusing {existing['path']}")
```

### `_update_meta_hw_ids(sketch_dir: str, hardware_ids: list, board_timestamps: dict) -> None`

Update the hardware IDs and board timestamps in a sketch's `.meta` file. Reads the `.meta` JSON from the upload directory (parent of `sketch_dir`), updates `hardware_ids` and `board_timestamps`, and writes back.

```python
_update_meta_hw_ids("/path/to/sketch", ["hw_id_1"], {"hw_id_1": "2026-01-01T00:00:00"})
```

### `_normalize_ino_filename(sketch_dir: str, target_stem: str) -> None`

Rename the single `.ino` file in a sketch directory to match the sketch folder name. Arduino IDE requires the `.ino` file to have the same name as its parent directory.

- If there is exactly one `.ino` file and its stem differs from `target_stem`, it is renamed to `{target_stem}.ino`
- If there are zero or multiple `.ino` files, no action is taken

```python
_normalize_ino_filename("/path/to/MySketch", "MySketch")
# Renames /path/to/MySketch/sketch.ino → /path/to/MySketch/MySketch.ino
```

### `_warm_upload_registry() -> None`

Populate the upload registry from the upload directory on disk. Used when the in-memory registry is empty but previous uploads exist on disk.

1. Loads the persisted registry file via `_load_registry()`
2. Scans all entries in `UPLOAD_BASE_DIR` for `.meta` files
3. For each valid `.meta`, extracts metadata and inserts a version entry into the in-memory registry (sorted by `server_timestamp`)
4. Skips entries already present (checked by path)

```python
_warm_upload_registry()
```

### `_resolve_latest_upload() -> Optional[str]`

Return the path to the latest uploaded sketch for the requesting client. Keyed by `(IP, User-Agent)` from the Flask request context. Warms the registry if the client has no in-memory entries. Returns `None` if no uploads exist.

```python
latest_path = _resolve_latest_upload()
```

### `_build_hw_labels() -> dict[str, str]`

Build a mapping of hardware IDs to human-readable labels from `state._board_list`. Labels have the format `"{board_name} ({port})"`.

```python
labels = _build_hw_labels()
# Returns: {"ABC123": "Arduino Uno (/dev/ttyACM0)", ...}
```

### `_render_sketch_path_selector(selected_path: str = "", hardware_id: str = "") -> str`

Render the sketch path selector dropdown HTML partial (`sketch_path_selector.html`).

1. Retrieves all sketche versions for the requesting client from the registry
2. If `hardware_id` is specified, filters to only sketches deployed to that hardware
3. Sorts versions by `server_timestamp` descending
4. Builds display labels with timestamp and board labels (e.g., `"SketchName (2026-01-01 12:00:00) [Arduino Uno (/dev/ttyACM0)]"`)
5. If `selected_path` is not in the available versions, appends it as a fallback entry

```python
html = _render_sketch_path_selector("/path/to/sketch")
html = _render_sketch_path_selector(hardware_id="ABC123")
```
