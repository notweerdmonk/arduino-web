---
---
# app (app.py)

Flask application factory, module-level re-exports, and two helper functions for board lookup and deploy recording.

## Functions

### `create_app() -> Flask`

Create and configure the Flask application instance. Initialization sequence:

1. Creates a `Flask(__name__)` instance
2. Sets `app.secret_key` from `ARDUINO_DASH_SECRET` env var (default: `"dev-secret-arduino"`)
3. Stores the app reference in `state._app`
4. Creates a `flask_sock.Sock` instance (if `flask-sock` is installed) for WebSocket support
5. Calls `init_html_routes(_app, sock)` to register all HTML route handlers
6. Calls `init_api_routes(_app)` to register all JSON API route handlers
7. Creates an `ArduinoSketchTools` extension instance with callbacks:
   - `broadcast_ws=_broadcast_ws` — WebSocket broadcast function
   - `get_board_info=_get_board_info` — board info lookup by port
   - `record_deploy=_record_deploy` — deploy event recorder
8. Calls `arduino_tools.init_app(_app)` to register the extension and its routes

```python
from arduino_dash.app import create_app
app = create_app()
```

### `_get_board_info(port: str) -> dict`

Return the board info dict for the given port from the shared state.

```python
info = _get_board_info("/dev/ttyACM0")
# Returns: {"port": "/dev/ttyACM0", "fqbn": "arduino:avr:uno", ...} or {}
```

### `_record_deploy(port: str, sketch_path: str) -> None`

Record a deploy event linking a hardware ID to a sketch path. Called after a successful compile+upload.

1. Looks up the board info for the given port to extract `hardware_id`
2. Searches the `_upload_registry` for the matching sketch path
3. Appends the `hardware_id` to `v["hardware_ids"]` if not already present
4. Updates `v["board_timestamps"][hardware_id]` with the current UTC timestamp
5. Persists the updated metadata via `_update_meta_hw_ids()` and `_save_registry()`
6. Broadcasts a "Deploy recorded" WebSocket event

## Module-Level Re-exports

`app.py` re-exports the following symbols from other modules at module level for test compatibility:

- **From `state`**: `_board_list`, `_board_list_lock`, `_compile_results`, `_compile_results_lock`, `_last_compiled_sketch`, `_last_compiled_sketch_lock`, `_last_compile_mtime`, `_last_compile_mtime_lock`, `_pending_responses`, `_pending_responses_lock`, `_upload_results`, `_upload_results_lock`, `_upload_registry`, `_upload_registry_lock`
- **From `pubsub`**: `_compute_sketch_checksum`, `_get_sketch_mtime`, `_make_meta`, `_on_board_event`, `_on_daemon_ready`, `_on_pubsub_reconnect`, `_on_resp`, `_wait_for_response`, `init_pubsub`
- **From `sketch_management`**: `_normalize_ino_filename`, `_render_sketch_path_selector`, `_save_registry`, `_update_meta_hw_ids`, `_warm_upload_registry`

## Module-Level App Instance

```python
app = create_app()
```

A module-level app instance is created for convenience (used by `wsgi.py` for gunicorn).

## App Configuration

Configuration is loaded in `wsgi.py` from environment variables after `create_app()`:

| Key | Env Variable | Default | Description |
|-----|-------------|---------|-------------|
| `BMS_UDS_PATH` | `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` | UDS path for BoardManager |
| `BMS_TCP_HOST` | `BOARD_MGR_TCP_HOST` | `127.0.0.1` | TCP host for BoardManager |
| `BMS_TCP_PORT` | `BOARD_MGR_TCP_PORT` | `9090` | TCP port for BoardManager |
| `BMS_NO_UDS` | `BMS_NO_UDS` | `""` | Force TCP only when truthy |
