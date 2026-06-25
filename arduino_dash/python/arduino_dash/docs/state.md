---
---
# state (state.py)

Shared module-level state for the Arduino Dash webapp. All state is protected by `threading.Lock` instances.

## Module Attributes

### App Reference

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_app` | `Flask` | `None` | Reference to the Flask application instance (set in `create_app()`) |

### Logging

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `logger` | `Logger` | `logging.getLogger("arduino_dash")` | Module-level logger instance |

### PubSub

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `pubsub` | `PubSubClient` | `None` | PubSub client instance connected to `BoardManagerService` |

### WebSocket Clients

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_ws_clients` | `list` | `[]` | List of connected WebSocket client objects |
| `_ws_lock` | `Lock` | `threading.Lock()` | Lock protecting `_ws_clients` |

### Board List

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_board_list` | `dict[str, dict]` | `{}` | Map of port → board info dict (port, fqbn, board, hardware_id, event) |
| `_board_list_lock` | `Lock` | `threading.Lock()` | Lock protecting `_board_list` |

### Board Events Buffer

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_board_events` | `list[dict]` | `[]` | Recent board events buffer (capped at 100 entries, newest first). Each entry is the event data dict (port, event, board, fqbn, hardware_id) |
| `_board_events_lock` | `Lock` | `threading.Lock()` | Lock protecting `_board_events` |

### Pending Responses

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_pending_responses` | `dict[str, tuple[dict\|None, Event]]` | `{}` | Map of topic → (response_data, threading.Event) for synchronous request/response |
| `_pending_responses_lock` | `Lock` | `threading.Lock()` | Lock protecting `_pending_responses` |

### Compile Results

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_compile_results` | `dict[str, dict\|None]` | `{}` | Map of port → compile result |
| `_compile_results_lock` | `Lock` | `threading.Lock()` | Lock protecting `_compile_results` |
| `_compile_meta` | `dict[str, dict]` | `{}` | Map of port → compile metadata |
| `_compile_meta_lock` | `Lock` | `threading.Lock()` | Lock protecting `_compile_meta` |

### Upload Results

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_upload_results` | `dict[str, dict\|None]` | `{}` | Map of port → upload result |
| `_upload_results_lock` | `Lock` | `threading.Lock()` | Lock protecting `_upload_results` |
| `_upload_meta` | `dict[str, dict]` | `{}` | Map of port → upload metadata |
| `_upload_meta_lock` | `Lock` | `threading.Lock()` | Lock protecting `_upload_meta` |

### Daemon Ready

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_daemon_ready` | `bool` | `False` | Whether the Arduino daemon has reported ready |
| `_daemon_ready_lock` | `Lock` | `threading.Lock()` | Lock protecting `_daemon_ready` |

### Per-Port Sketch Tracking

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_last_compiled_sketch` | `dict[str, str]` | `{}` | Map of port → last compiled sketch path |
| `_last_compiled_sketch_lock` | `Lock` | `threading.Lock()` | Lock protecting `_last_compiled_sketch` |
| `_last_compile_mtime` | `dict[str, float\|None]` | `{}` | Map of port → last compile mtime |
| `_last_compile_mtime_lock` | `Lock` | `threading.Lock()` | Lock protecting `_last_compile_mtime` |
| `_last_compile_checksum` | `dict[str, str]` | `{}` | Map of port → last compile checksum |
| `_last_compile_checksum_lock` | `Lock` | `threading.Lock()` | Lock protecting `_last_compile_checksum` |
| `_last_uploaded_sketch` | `dict[str, str]` | `{}` | Map of port → last uploaded sketch path |
| `_last_uploaded_sketch_lock` | `Lock` | `threading.Lock()` | Lock protecting `_last_uploaded_sketch` |

### Upload Registry

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_upload_registry` | `dict[tuple[str, str], dict[str, list[dict]]]` | `{}` | Nested dict: `{(ip, user_agent): {sketch_name: [version_dict, ...]}}` |
| `_upload_registry_lock` | `Lock` | `threading.Lock()` | Lock protecting `_upload_registry` |

Each version dict has keys: `path`, `checksum`, `server_timestamp`, `hardware_ids`, `board_timestamps`.

### Upload Settings

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `UPLOAD_BASE_DIR` | `str` | `~/.local/share/arduino-dash/uploads` | Base directory for sketch uploads (from `settings.py`) |
| `MAX_SKETCH_UPLOAD_SIZE` | `int` | `10 * 1024 * 1024` (10 MB) | Maximum sketch upload size in bytes |

### Fallback Scanner

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_fallback_scanner` | `Thread\|None` | `None` | Background scanner thread for polling board glob patterns |
| `_stop_fallback_scan` | `bool` | `False` | Signal flag to stop the fallback scanner |
| `_fallback_patterns` | `list[str]` | `["/dev/ttyACM*", "/dev/ttyUSB*"]` | Glob patterns for fallback board detection |
| `_fallback_scan_interval` | `float` | `5.0` | Seconds between fallback scans |
