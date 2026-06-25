---
---
{% raw %}
# Implementation Plan — Phase 103: API Route Restructure

**Date**: 2026-06-25 11:57
**Status**: ✅ COMPLETED

## Motivation

Align API routes across both dashboards (arduino_dash and medminder_dash) into a consistent pattern:
- PubSub-backed board commands under `/api/pubsub/board/*`
- Local CRUD endpoints under `/api/boards/*`, `/api/board/<port>`, `/api/daemon/`, `/api/sketches/`
- medminder_dash gains PubSub endpoints it currently lacks
- arduino_dash gains board events buffer it currently lacks

## Route Naming Convention

| Prefix | Purpose |
|--------|---------|
| `/api/pubsub/board/*` | Commands sent via PubSub to BoardManagerService (spawn, status, remove, health) |
| `/api/board/<port>/status` | Local CRUD — connection status from cached state |
| `/api/boards/list` | Local CRUD — board list from cached state |
| `/api/boards/events` | Local CRUD — board events buffer |
| `/api/daemon/status` | Local CRUD — daemon status (connected + ready) |
| `/api/sketches` | Sketch version listing with optional `?hardware_id=X` filter |
| `/api/sketches/last-upload` | Latest upload details (null + 404 when none found) |

## Parts

### Part 1: arduino_dash — Events Buffer

Why: arduino_dash has no `_board_events` buffer, so `/api/boards/events` has no data source. medminder_dash already has this pattern.

**Files:**
- `state.py` — add `_board_events: list[dict] = []` and `_board_events_lock = threading.Lock()`
- `pubsub.py` — in `_on_board_event()`, append `data` to `state._board_events`, cap at 100
- `utils.py` — add `get_board_events() -> list[dict]` returning `list(state._board_events)`

### Part 2: arduino_dash — Restructure api_routes.py

**MOVE (PubSub → `/api/pubsub/board/*`):**

| Old Route | New Route | Line |
|-----------|-----------|------|
| `POST /api/board/<path:port>/spawn` | `POST /api/pubsub/board/<path:port>/spawn` | 34-43 |
| `GET /api/board/<path:port>/status` | `GET /api/pubsub/board/<path:port>/status` | 45-54 |
| `POST /api/board/<path:port>/remove` | `POST /api/pubsub/board/<path:port>/remove` | 56-65 |
| `GET /api/boards` | `POST /api/pubsub/boards/health` | 67-71 |

**ADD (5 new CRUD endpoints):**

| Route | Returns | Helper |
|-------|---------|--------|
| `GET /api/daemon/status` | `{"ready": bool, "connected": bool}` | `state._daemon_ready` + `state.pubsub.is_connected` |
| `GET /api/board/<path:port>/status` | `{"connected": bool, "port": str, "fqbn": str, "hardware_id": str}` | `get_port_info(port)` |
| `GET /api/boards/list` | `[{port, fqbn, board, hardware_id, event}, ...]` | `get_known_boards()` |
| `GET /api/boards/events` | `[{port, event, board, fqbn, hardware_id}, ...]` | `get_board_events()` |
| `GET /api/sketches/last-upload` | `{"path": ..., "name": ..., "timestamp": ...}` or `(null, 404)` | `get_assignment()` + `_resolve_latest_upload()` |

**ENHANCE:**
- `GET /api/sketches` — add `?hardware_id=X` filter: when provided, filter version dicts to those where `X` is in `version["hardware_ids"]`

### Part 3: medminder_dash — Restructure api_routes.py

**UPDATE IMPORTS:**
```python
from medminder_dash.pubsub import (
    get_pubsub, is_connected, is_daemon_ready,   # ADD
    ensure_sketch_dir, _get_alarm_hpp_path, broadcast_ws,  # EXISTING
)
from medminder_dash.utils import (
    get_board_events,          # ADD
    get_known_ports,
    validate_medicine_data,
)
```

**ADD (4 PubSub endpoints — match arduino_dash):**

| Route | PubSub call |
|-------|-------------|
| `POST /api/pubsub/board/<path:port>/spawn` | `get_pubsub().publish(f"board::{port}::cmd", {"method": "spawn"}, f"resp:spawn:{port}")` |
| `GET /api/pubsub/board/<path:port>/status` | `get_pubsub().publish(f"board::{port}::cmd", {"method": "status"}, f"resp:status:{port}")` |
| `POST /api/pubsub/board/<path:port>/remove` | `get_pubsub().publish(f"board::{port}::cmd", {"method": "remove"}, f"resp:remove:{port}")` |
| `POST /api/pubsub/boards/health` | `get_pubsub().publish("sys/health", {"method": "health"}, "")` |

**RENAME:**
| Old | New |
|-----|-----|
| `GET /api/board_list` | `GET /api/boards/list` |

Same callback function body, just registered at the new URL. Remove old registration.

**ADD (5 new CRUD endpoints — same as arduino_dash, using module's own helpers):**

| Route | Helper |
|-------|--------|
| `GET /api/daemon/status` | `is_connected()` + `is_daemon_ready()` |
| `GET /api/board/<path:port>/status` | `get_port_info(port)` |
| `GET /api/boards/list` | `get_known_ports()` (same as renamed endpoint) |
| `GET /api/boards/events` | `get_board_events()` |
| `GET /api/sketches/last-upload` | `get_assignment()` + `_resolve_latest_upload()` (from `sketch_registry` and `sketch_management`) |

**ENHANCE:**
- `GET /api/sketches` — add `?hardware_id=X` filter

### Part 4: medminder_dash — Comment Out `/boards/event`

**File: `html_routes.py`**
- Comment out lines 774-778 (the `/boards/event` route) with explanatory comment
- Remove `get_board_events` from import line at line 44 (only used by that route)

### Part 5: Update Tests

| File | Line(s) | Current | Change |
|------|---------|---------|--------|
| `arduino_dash/tests/test_app.py` | 1505 | `"/api/board/dev/ttyACM0/spawn"` | `"/api/pubsub/board/dev/ttyACM0/spawn"` |
| `arduino_dash/tests/test_app.py` | 1514 | `"/api/board/dev/ttyACM0/status"` | `"/api/pubsub/board/dev/ttyACM0/status"` |
| `arduino_dash/tests/test_app.py` | 1523 | `"/api/board/dev/ttyACM0/remove"` | `"/api/pubsub/board/dev/ttyACM0/remove"` |
| `arduino_dash/tests/test_app.py` | 1532 | `"/api/boards"` | `"/api/pubsub/boards/health"` |
| `medminder_dash/tests/test_routes.py` | 469-472 | `TestBoardsEvent → client.get("/boards/event")` | Update to test `GET /api/boards/events` |

### Part 6: Module Docs

| File | Update |
|------|--------|
| `arduino_dash/docs/state.md` | Add `_board_events`, `_board_events_lock` |
| `arduino_dash/docs/utils.md` | Add `get_board_events()` |
| `arduino_dash/docs/api_routes.md` | New route tables (pubsub + CRUD) |
| `medminder_dash/docs/api_routes.md` | New route tables (pubsub + CRUD) |

## Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | arduino_dash events buffer | `state.py`, `pubsub.py`, `utils.py` | ✅ |
| Q2 | arduino_dash api_routes.py | Move PubSub + add CRUD + enhance /api/sketches | ✅ |
| Q3 | medminder_dash api_routes.py | Add PubSub + rename + add CRUD + enhance /api/sketches | ✅ |
| Q4 | medminder_dash html_routes.py | Comment out /boards/event, remove import | ✅ |
| Q5 | Update tests | 4 URL changes in test_app.py + redirect TestBoardsEvent | ✅ |
| Q6 | Module docs | state.md, utils.md, api_routes.md for both modules | ✅ |
| Q7 | Verification | `nox -s all_tests` — 8/8 sessions green | ✅ |
| Q8 | Agent-facing docs sync | PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md, all workflow docs | ✅ |

## Rollback

Each source file change is scoped. Revert via `git checkout -- <file>` to undo individual changes.
{% endraw %}
