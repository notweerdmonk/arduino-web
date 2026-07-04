---
layout: default
---
# `app.py` — Flask Application Factory

**File:** `medminder_dash/app.py`

## Functions

### `create_app() -> Flask`

The Flask application factory. Creates and configures the application instance,
wires up all routes, initializes the `MedicineStore`, and registers the
`ArduinoSketchTools` extension.

**Initialization sequence:**

1. **Flask instance** — `Flask(__name__)` with `secret_key` from
   `FLASK_SECRET_KEY` env var (fallback: `"dev-secret"`).
2. **`MedicineStore`** — Module-global `store` variable (singleton per process).
3. **`ArduinoSketchTools`** — Flask extension with callbacks:
   - `broadcast_ws` — WebSocket broadcast
   - `get_board_info` — resolves board info for a port
   - `record_deploy` — records deploy events in the upload registry
4. **`before_request` hook** `_sync_store_board()` — loads the board's medicines
   from session `board_port` before every request.
5. **Flask-Sock** — Optional WebSocket support via `flask_sock.Sock`.
6. **Route registration:**
   - `init_html_routes(...)` — All HTML routes
   - `init_api_routes(...)` — All `/api/` JSON routes

```python
app = create_app()
```

### `_migrate_default_board(store, session)`

Migrate medicines from the deprecated `"default"` board key to the current
board port in `session.get("board_port")`. Runs only when no medicines exist
for the current board and there are medicines under the `"default"` key.

| Param | Type | Purpose |
|-------|------|---------|
| `store` | `MedicineStore` | Store instance to migrate |
| `session` | `flask.session` | Current Flask session |

### `_record_deploy(port: str, sketch_path: str) -> None`

Record a deploy event in the upload registry. Looks up the board's `hardware_id`,
appends it to the sketch version's `hardware_ids` list, sets the
`board_timestamps[hardware_id]`, saves the registry, and broadcasts a WS event.

| Param | Type | Purpose |
|-------|------|---------|
| `port` | `str` | Board port that was deployed to |
| `sketch_path` | `str` | Path to the deployed sketch |

### `_get_board_info(port) -> dict`

Return board info dict for a port, or empty dict.

| Param | Type | Purpose |
|-------|------|---------|
| `port` | `str` | Board port string |

Returns: Board info dict or empty dict.

## Module-Level Globals

| Variable | Value | Description |
|----------|-------|-------------|
| `SKETCH_DIR` | `load_sketch_dir()` | Resolved sketch directory |
| `ALARM_HPP_PATH` | `_get_alarm_hpp_path()` | Path to `alarm.hpp` |
| `store` | `MedicineStore()` | Module-global store instance |
