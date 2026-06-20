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

## Route Table

### Board List

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/board_list` | `api_board_list()` | — | JSON list of board info dicts |

### Medicine Diff

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/medicines/diff` | `api_medicines_diff()` | — | JSON diff `{metadata, alarm_hpp, differ, alarm_hpp_exists, alarm_hpp_error, active_board}` |

### Medicine CRUD

| Method | Route | Handler | Request | Response |
|--------|-------|---------|---------|----------|
| GET | `/api/medicines` | `api_medicines_list()` | — | JSON array of all medicines |
| POST | `/api/medicine` | `api_medicine_create()` | JSON body: `{name, hour, minute, day_of_week, day_of_month}` | `201` + JSON of created medicine |
| GET | `/api/medicine/<med_id>` | `api_medicine_get(med_id)` | — | JSON of single medicine or `404` |
| PUT | `/api/medicine/<med_id>` | `api_medicine_update(med_id)` | JSON body: `{name, hour, minute, day_of_week, day_of_month}` | JSON of updated medicine |
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
| GET | `/api/sketches` | `api_sketches()` | — | JSON array `[{name, path, timestamp}]` with MedMinderV2 default prepended |
| POST | `/api/sketch/upload` | `api_sketch_upload()` | Multipart `files[]`, query `?hardware_id=...` | `{"path": "/path/to/sketch"}` |
| DELETE | `/api/sketch` | `api_sketch_delete()` | Query `?path=...&hardware_id=...` | `{"status": "deleted"}` or `404` |

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

**List sketches:**

```bash
curl http://localhost:8080/api/sketches
# 200: [{"name":"MedMinderV2","path":"/home/...","timestamp":""}, ...]
```
