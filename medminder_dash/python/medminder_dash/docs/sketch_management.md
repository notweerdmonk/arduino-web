---
---
# `sketch_management.py` — Sketch Management

**File:** `medminder_dash/sketch_management.py`

Sketch upload/management functions — registry persistence, checksum computation,
deduplication, file normalization, and path selector rendering.

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `REGISTRY_DIR` | `Path.home() / ".config" / "medminder"` | Registry config directory |
| `REGISTRY_FILE` | `str(REGISTRY_DIR / "sketch_registry.json")` | Registry persistence file |

## Functions

### `_save_registry() -> None`

Persist the upload registry to disk. Serializes `state._upload_registry` as JSON
to `REGISTRY_FILE`. Caller must hold `state._upload_registry_lock`.

Registry key (`(ip, user_agent)`) tuples are JSON-serialized as keys:

```json
{
  "[\"192.168.1.5\", \"Mozilla/5.0 ...\"]": {
    "MySketch": [{"path": "...", "checksum": "...", ...}]
  }
}
```

### `_load_registry() -> None`

Load the upload registry from disk. Reads `REGISTRY_FILE` and populates
`state._upload_registry`. Deserializes JSON string keys back to `(ip, ua)`
tuples.

### `_compute_sketch_checksum(sketch_dir: str) -> str`

Compute a SHA-256 checksum for all files in a sketch directory. Walks the
directory tree, hashing relative file paths and file contents in 64KB chunks.

| Param | Type | Purpose |
|-------|------|---------|
| `sketch_dir` | `str` | Path to the sketch directory |

Returns: Hex digest string, or `""` if the directory does not exist.

```python
checksum = _compute_sketch_checksum("/path/to/sketch")
# "a1b2c3d4..."
```

### `_find_existing_version(user_sketches: dict, checksum: str) -> Optional[dict]`

Find a sketch version by checksum in the user's sketches. Iterates all versions
across all sketch names and returns the first match.

| Param | Type | Purpose |
|-------|------|---------|
| `user_sketches` | `dict` | User's sketch entries (`{name: [versions]}`) |
| `checksum` | `str` | Checksum to match |

Returns: Matching version dict, or `None`.

### `_update_meta_hw_ids(sketch_dir: str, hardware_ids: list, board_timestamps: dict) -> None`

Update `hardware_ids` and `board_timestamps` metadata in the `.meta` file
associated with a sketch directory.

| Param | Type | Purpose |
|-------|------|---------|
| `sketch_dir` | `str` | Sketch directory path |
| `hardware_ids` | `list` | List of hardware IDs |
| `board_timestamps` | `dict` | `{hardware_id: timestamp}` mapping |

```python
_update_meta_hw_ids(sketch_dir, ["AD8F..."], {"AD8F...": "2026-06-20T12:00:00"})
```

### `_normalize_ino_filename(sketch_dir: str, target_stem: str) -> None`

Rename the `.ino` file in a sketch directory to match the directory name. Only
acts when there is exactly one `.ino` file and its stem differs from the target.

| Param | Type | Purpose |
|-------|------|---------|
| `sketch_dir` | `str` | Sketch directory path |
| `target_stem` | `str` | Desired stem name (directory name) |

```python
# sketch_dir = "/path/MySketch" with "Sketch.ino" inside
_normalize_ino_filename("/path/MySketch", "MySketch")
# Renames "Sketch.ino" -> "MySketch.ino"
```

### `_warm_upload_registry() -> None`

Load persisted uploads from disk into the in-memory registry. Scans
`UPLOAD_BASE_DIR` for `.meta` files and populates the registry with their
contents. In-line deduplication by path.

```python
# Called before first access to upload_registry for a new user key
_warm_upload_registry()
```

### `_resolve_latest_upload() -> Optional[str]`

Return the path to the latest upload for the current user (identified by
`request.remote_addr` and `User-Agent` header).

Returns: Sketch directory path string, or `None` if no uploads found.

```python
latest_path = _resolve_latest_upload()
# "/home/user/.local/share/medminder/uploads/.../MySketch"
```

### `_build_hw_labels() -> dict[str, str]`

Build a dict mapping hardware IDs to human-readable board labels. Iterates
`state._known_ports` and produces labels like `"Arduino Uno (/dev/ttyACM0)"`.

Returns: `{hardware_id: label_string}`

### `_render_sketch_path_selector(selected_path="", include_default=False, hardware_id="") -> str`

Render the sketch path selector HTML partial. Queries the upload registry for
the current user, builds a sorted list of sketch paths with timestamps and
board labels, and returns the rendered template.

| Param | Type | Default | Purpose |
|-------|------|---------|---------|
| `selected_path` | `str` | `""` | Currently selected sketch path |
| `include_default` | `bool` | `False` | Include MedMinderV2 default sketch |
| `hardware_id` | `str` | `""` | Filter sketches by hardware ID |

```python
html = _render_sketch_path_selector("/path/to/sketch", include_default=True)
# Rendered "partials/sketch_path_selector.html" with sketch options
```
