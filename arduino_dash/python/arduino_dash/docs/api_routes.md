---
---
# api_routes (api_routes.py)

JSON API routes — all under the `/api/` prefix for programmatic access.

## Functions

### `init_api_routes(app: Flask) -> None`

Register all `/api/` route handlers on the Flask app.

## Routes

### Board Management

#### `POST /api/board/<path:port>/spawn`

Spawn the board monitor for the given port.

**Response:**
```json
{"status": "accepted"}
```

**Error (invalid port):**
```json
{"error": "Invalid port"}
```
Status: 400

#### `GET /api/board/<path:port>/status`

Request status for the board at the given port.

**Response:**
```json
{"status": "accepted"}
```

#### `POST /api/board/<path:port>/remove`

Remove the board at the given port.

**Response:**
```json
{"status": "accepted"}
```

#### `GET /api/boards`

List all known boards. Triggers a health check via PubSub.

**Response:**
```json
{"status": "accepted"}
```

> **Note:** Board list is returned via WebSocket events, not in this response. The actual board state is in `state._board_list`.

### Sketch Management

#### `GET /api/sketches`

List all uploaded sketches for the requesting client (keyed by IP + User-Agent).

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

Delete an uploaded sketch by path. Accepts `path` and optional `hardware_id` query parameters.

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
