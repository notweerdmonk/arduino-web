---
---
# api_routes (api_routes.py)

JSON API routes — all under the `/api/` prefix for programmatic access.

## Functions

### `init_api_routes(app: Flask) -> None`

Register all `/api/` route handlers on the Flask app.

## Route Tables

### PubSub Board Commands (send to BoardManagerService)

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| POST | `/api/pubsub/board/<path:port>/spawn` | `api_spawn(port)` | URL param `port` | `{"status": "accepted"}` |
| GET | `/api/pubsub/board/<path:port>/status` | `api_board_status(port)` | URL param `port` | `{"status": "accepted"}` |
| POST | `/api/pubsub/board/<path:port>/remove` | `api_remove_board(port)` | URL param `port` | `{"status": "accepted"}` |
| POST | `/api/pubsub/boards/health` | `api_list_boards()` | — | `{"status": "accepted"}` |

These routes publish a command via PubSub to the BoardManagerService and return immediately. The actual operation happens asynchronously.

### Local CRUD — Daemon

| Method | Route | Handler | Response |
|--------|-------|---------|----------|
| GET | `/api/daemon/status` | `api_daemon_status()` | `{"ready": bool, "connected": bool}` |

### Local CRUD — Board Status

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/board/<path:port>/status` | `api_board_connection_status(port)` | URL param `port` | JSON `{connected, port, fqbn, hardware_id}` |
| GET | `/api/boards/list` | `api_boards_list()` | — | JSON array of board info dicts |
| GET | `/api/boards/events` | `api_boards_events()` | — | JSON array of recent board events |

**`GET /api/board/<path:port>/status` response:**
```json
{"connected": true, "port": "/dev/ttyACM0", "fqbn": "arduino:avr:uno", "hardware_id": "ABC123"}
```

**`GET /api/boards/list` response:**
```json
[{"port": "/dev/ttyACM0", "fqbn": "arduino:avr:uno", "board": "Arduino Uno", "hardware_id": "ABC123", "event": "connected"}, ...]
```

**`GET /api/boards/events` response:**
```json
[{"port": "/dev/ttyACM0", "event": "connected", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "hardware_id": "ABC123"}, ...]
```

### Sketch Management

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/sketches` | `api_sketches()` | Optional `?hardware_id=X` | JSON array `[{name, path, timestamp}]` |
| GET | `/api/sketches/last-upload` | `api_sketches_last_upload()` | Optional `?hardware_id=X` | JSON dict or `null` + 404 |
| POST | `/api/sketch/upload` | `api_sketch_upload()` | Multipart `files[]`, query `?hardware_id=...` | `{"path": "/path/to/sketch"}` |
| DELETE | `/api/sketch` | `api_sketch_delete()` | Query `?path=...` | `{"status": "deleted"}` or 404 |

#### `GET /api/sketches`

List all uploaded sketches for the requesting client (keyed by IP + User-Agent). When `?hardware_id=X` is provided, only versions whose `hardware_ids` list includes X are returned.

**Response:**
```json
[
    {
        "name": "sketch_name",
        "path": "/path/to/sketch",
        "timestamp": "2026-01-01T00:00:00.000000"
    },
    ...
]
```

Warms the registry from disk if the client has no in-memory entries.

#### `GET /api/sketches/last-upload`

Return the latest uploaded sketch as JSON. Accepts optional `?hardware_id=X`:
- If `hardware_id` provided: tries `get_assignment(hardware_id)` first, falls back to `_resolve_latest_upload()`
- If no `hardware_id`: just `_resolve_latest_upload()`

**Response (found):**
```json
{"path": "/path/to/sketch", "name": "sketch_name", "timestamp": ""}
```

**Response (none found):** `null` with HTTP 404.

#### `POST /api/sketch/upload`

Handle sketch file upload and return the sketch path. Accepts `files[]` multipart upload and optional `hardware_id` query parameter.

**Response (success):**
```json
{"path": "/path/to/uploaded/sketch"}
```

**Response (no files):**
```json
{"error": "No files provided"}
```
Status: 400

Upload flow:
1. Files saved to `UPLOAD_BASE_DIR/{salt}_{timestamp}_{safe_name}/`
2. `.ino` filename normalized to match folder name
3. SHA-256 checksum computed; deduplicates if identical checksum exists
4. `.meta` JSON written with metadata
5. Version inserted into registry sorted by timestamp
6. If `hardware_id` provided, `set_assignment()` links hardware ID to sketch

#### `DELETE /api/sketch`

Delete an uploaded sketch by path. Accepts `path` query parameter.

**Response (deleted):**
```json
{"status": "deleted"}
```

**Response (not found):**
```json
{"error": "Not found"}
```
Status: 404

**Response (missing path):**
```json
{"error": "Missing path"}
```
Status: 400

**Response (invalid path):**
```json
{"error": "Invalid path"}
```
Status: 403

Path validation: the sketch path must be within `UPLOAD_BASE_DIR` (checked via `os.path.normpath` prefix comparison).
