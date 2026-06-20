---
---
# html_routes (html_routes.py)

HTML page and partial routes — no `/api/` prefix. Uses HTMX for dynamic content loading with OOB (Out-of-Band) swap responses.

## Functions

### `init_html_routes(app: Flask, sock) -> None`

Register all HTML route handlers on the Flask app. Registers both standard routes and a WebSocket endpoint.

## Routes

### Dashboard

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/` | `dashboard()` | Render the main dashboard page (`dashboard.html`) |

### Board Detail

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/board/<path:port>` | `board_detail(port)` | Render board detail page for a specific port. Normalizes and validates the port path, renders `board_detail.html` with board info. |
| GET | `/board/<path:port>/connection-status` | `html_board_connection_status(port)` | Render the connection status badge for a board. Returns `board_status_badge.html` partial showing connected/disconnected state. |

### Board Grid

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/boards/grid` | `html_boards_grid()` | Render the board grid partial (`board_grid.html`) with all connected boards from `state._board_list`. |

### Daemon Status

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/daemon/status` | `html_daemon_status()` | Render the daemon status badge (`daemon_badge.html`). Shows ready only when PubSub is connected AND daemon ready flag is set. |

### Admin

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/admin` | `admin()` | Render the admin page (`admin.html`) with board selector, compile/upload controls. Resolves the active board from session, URL parameter, or first known board. Defaults to `arduino:avr:uno` FQBN if none connected. |
| GET | `/admin/board-selector` | `html_admin_board_selector()` | Render the admin board selector partial (`admin_board_selector.html`). Resolves the active board from session/known ports. |

### Active Board

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| POST | `/admin/active-board` | `html_admin_active_board()` | Set the active board in the session. Accepts `port` form field. Returns OOB swap HTML updating `#global-fqbn-display`, `#global-fqbn`, `#fqbn`, and `#active-board-hardware-id` elements. |

### Compile/Upload

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/board/compile-upload-card` | `html_board_compile_upload_card()` | Render the compile-upload card partial (`compile_upload_card.html`). Resolves active board from session. |

### Sketch Management

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/last-upload` | `html_last_upload()` | Render the sketch path selector for the latest upload. Accepts `hardware_id` query parameter. If `hardware_id` has an assignment, that sketch is selected; otherwise the latest upload is resolved. |
| POST | `/sketch/upload` | `html_sketch_upload()` | Handle sketch upload via HTML form. Accepts `files[]` multipart upload and optional `hardware_id` query parameter. Saves files, normalizes `.ino` filenames, deduplicates by SHA-256 checksum, updates registry, and returns the updated sketch path selector HTML. |
| DELETE | `/sketch` | `html_sketch_delete()` | Handle sketch deletion. Accepts `path` and optional `hardware_id` query parameters. Validates path is within `UPLOAD_BASE_DIR`, removes from registry, deletes files, and returns the updated sketch path selector HTML. |

### WebSocket

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| WS | `/ws/board-events` | `ws_board_events(ws)` | WebSocket endpoint that streams board events to clients. Registers the WebSocket in `state._ws_clients`, receives (but currently ignores) client messages with a 30-second receive timeout. Removes the client on disconnection. |

## Internal Functions

### `_get_active_board_info() -> tuple[str, str, str]`

Return the active board (port, fqbn, hardware_id) from the Flask session. Returns `("", "", "")` if no active board is set.

```python
port, fqbn, hw_id = _get_active_board_info()
```

### `_resolve_board_info(active_board_port: str, active_board_fqbn: str, active_board_hardware_id: str, known_ports: list[dict]) -> tuple[str, str, str]`

Resolve board info, falling back to known ports if needed. Resolution priority:

1. Look up `active_board_port` in `state._board_list` via `get_port_info()`
2. If not found, try `find_board_info_by_fqbn()` using `active_board_fqbn`
3. If still not found, use `get_first_board(known_ports)`
4. Raises `ValueError("port missing")` or `ValueError("fqbn missing")` if unresolvable

## Sketch Upload Flow (HTML Form)

1. Uploaded files are saved to `UPLOAD_BASE_DIR/{salt}_{timestamp}_{safe_name}/`
2. The `.ino` file is renamed to match the sketch folder name via `_normalize_ino_filename()`
3. A SHA-256 checksum is computed over source files
4. If an identical checksum exists, the upload is deduplicated (files deleted, existing path reused)
5. A `.meta` JSON file is written with metadata (ip, user_agent, timestamp, checksum, hardware_ids, board_timestamps)
6. The version is inserted into the registry sorted by `server_timestamp`
7. If `hardware_id` is provided, `set_assignment()` links the hardware ID to the sketch
8. Returns the rendered sketch path selector partial
