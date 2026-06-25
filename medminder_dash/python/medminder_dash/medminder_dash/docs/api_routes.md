---
---
# `api_routes.py` — JSON API Routes

**File:** `medminder_dash/api_routes.py`

All JSON API routes with `/api/` prefix. Registered via `init_api_routes()`.

## Function: `init_api_routes(app, store_param)`

| Param | Type | Purpose |
|-------|------|---------|
| `app` | `Flask` | Application instance |
| `store_param` | `MedicineStore` | Medicine store instance |

## Route Tables

### PubSub Board Commands (send to BoardManagerService)

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| POST | `/api/pubsub/board/<path:port>/spawn` | `api_pubsub_spawn(port)` | URL param `port` | `{"status": "accepted"}` |
| GET | `/api/pubsub/board/<path:port>/status` | `api_pubsub_board_status(port)` | URL param `port` | `{"status": "accepted"}` |
| POST | `/api/pubsub/board/<path:port>/remove` | `api_pubsub_remove_board(port)` | URL param `port` | `{"status": "accepted"}` |
| POST | `/api/pubsub/boards/health` | `api_pubsub_boards_health()` | — | `{"status": "accepted"}` |

These routes publish a command via PubSub to the BoardManagerService and return immediately. Returns 503 if PubSub is not connected.

### Local CRUD — Daemon

| Method | Route | Handler | Response |
|--------|-------|---------|----------|
| GET | `/api/daemon/status` | `api_daemon_status()` | `{"ready": bool, "connected": bool}` |

### Local CRUD — Board Status & Events

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/board/<path:port>/status` | `api_board_connection_status(port)` | URL param `port` | JSON `{connected, port, fqbn, hardware_id}` |
| GET | `/api/boards/list` | `api_board_list()` | — | JSON array of board info dicts |
| GET | `/api/boards/events` | `api_boards_events()` | — | JSON array of recent board events |

**`GET /api/board/<path:port>/status` response:**
```json
{"connected": true, "port": "/dev/ttyACM0", "fqbn": "arduino:avr:uno", "hardware_id": "ABC123"}
```

**`GET /api/boards/list` response:**
```json
[{"port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "hardware_id": "ABC123"}, ...]
```

**`GET /api/boards/events` response:**
```json
[{"port": "/dev/ttyACM0", "event": "connected", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "hardware_id": "ABC123"}, ...]
```

### Medicine Diff

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/medicines/diff` | `api_medicines_diff()` | — | JSON diff `{metadata, alarm_hpp, differ, alarm_hpp_exists, alarm_hpp_error, active_board}` |

### Medicine CRUD

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/medicines` | `api_medicines_list()` | — | JSON array of all medicines |
| POST | `/api/medicine` | `api_medicine_create()` | JSON body | `201` + JSON of created medicine |
| GET | `/api/medicine/<med_id>` | `api_medicine_get(med_id)` | — | JSON of single medicine or `404` |
| PUT | `/api/medicine/<med_id>` | `api_medicine_update(med_id)` | JSON body | JSON of updated medicine |
| DELETE | `/api/medicine/<med_id>` | `api_medicine_delete(med_id)` | — | `{"status": "deleted"}` or `404` |
| PUT | `/api/medicine/<med_id>/toggle` | `api_medicine_toggle(med_id)` | — | JSON of toggled medicine or `404` |

Each medicine JSON object:
```json
{
  "id": "abc123...",
  "name": "Aspirin",
  "hour": 8,
  "minute": 30,
  "day_of_week": 0,
  "day_of_month": 0,
  "enabled": true
}
```

### Sketch List / Upload / Delete

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/sketches` | `api_sketches()` | Optional `?hardware_id=X` | JSON array `[{name, path, timestamp}]` with MedMinderV2 default prepended |
| GET | `/api/sketches/last-upload` | `api_sketches_last_upload()` | Optional `?hardware_id=X` | JSON dict or `null` + 404 |
| POST | `/api/sketch/upload` | `api_sketch_upload()` | Multipart `files[]`, query `?hardware_id=...` | `{"path": "/path/to/sketch"}` |
| DELETE | `/api/sketch` | `api_sketch_delete()` | Query `?path=...&hardware_id=...` | `{"status": "deleted"}` or `404` |

**`GET /api/sketches`:** When `?hardware_id=X` is provided, only versions whose `hardware_ids` list includes X are returned.

**`GET /api/sketches/last-upload`:** Returns the latest uploaded sketch. If `hardware_id` provided, tries `get_assignment(hardware_id)` first, falls back to `_resolve_latest_upload()`. Returns `null` with 404 if none found.

### Deploy Flow

The compile/upload flow itself is handled by `arduino-sketch-tools` (a Flask
extension). The API routes in this module focus on sketch management and
medicine CRUD, while compile/upload is managed via PubSub topics
(`resp::compile::*`, `resp::upload::*`) with the `ArduinoSketchTools`
extension's response handlers.

## Private Helpers

| Function | Purpose |
|----------|---------|
| `_get_active_board_info()` | Return `(port, fqbn, hardware_id)` from session |
| `_medicine_to_dict(med)` | Convert `Medicine` to serializable dict |
| `_medicine_dict_sort_key(d)` | Sort key for medicine dicts |
| `_compute_diff(active_board)` | Compare store vs `alarm.hpp` |
| `_write_alarm_hpp(meds)` | Write `alarm.hpp` from medicine list |

## Request/Response Examples

**Get board list:**
```bash
curl http://localhost:8080/api/boards/list
# 200: [{"port":"/dev/ttyACM0","board":"Arduino Uno",...}]
```

**Get daemon status:**
```bash
curl http://localhost:8080/api/daemon/status
# 200: {"ready": true, "connected": true}
```

**Create medicine:**
```bash
curl -X POST http://localhost:8080/api/medicine \
  -H "Content-Type: application/json" \
  -d '{"name":"Aspirin","hour":8,"minute":30,"day_of_week":0,"day_of_month":0}'
# 201: {"id":"abc...","name":"Aspirin","hour":8,"minute":30,...}
```

**Upload sketch:**
```bash
curl -X POST http://localhost:8080/api/sketch/upload \
  -F "files[]=@mysketch/mysketch.ino"
# 200: {"path": "/home/user/.local/share/medminder/uploads/.../mysketch"}
```

**List sketches (filtered by hardware_id):**
```bash
curl "http://localhost:8080/api/sketches?hardware_id=ABC123"
# 200: [{"name":"MedMinderV2","path":"/home/...","timestamp":""}, ...]
```
