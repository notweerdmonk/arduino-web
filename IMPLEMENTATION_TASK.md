---
---
{% raw %}
# Implementation Task — Phase 103: API Route Restructure

**Date**: 2026-06-25 11:57

## Task Breakdown

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | arduino_dash events buffer | ✅ | state.py, pubsub.py, utils.py |
| Q2 | arduino_dash api_routes.py | ✅ | Move 4 PubSub routes → /api/pubsub/board/*, add 5 CRUD, enhance /api/sketches |
| Q3 | medminder_dash api_routes.py | ✅ | Add 4 PubSub, rename /api/board_list → /api/boards/list, add 5 CRUD, enhance /api/sketches |
| Q4 | medminder_dash html_routes.py | ✅ | Comment out /boards/event, remove get_board_events import |
| Q5 | Update tests | ✅ | 4 URL changes in test_app.py + redirect TestBoardsEvent |
| Q6 | Module docs | ✅ | state.md, utils.md, api_routes.md for both modules |
| Q7 | Verification | ✅ | `nox -s all_tests` — 8/8 sessions green |
| Q8 | Agent-facing docs sync | ✅ | PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md, all workflow docs |

## Detailed Tasks

### Q1 — arduino_dash events buffer

- [x] `state.py`: Add `_board_events: list[dict] = []` and `_board_events_lock = threading.Lock()`
- [x] `pubsub.py`: In `_on_board_event()`, append `data` to `state._board_events`, cap at 100
- [x] `utils.py`: Add `get_board_events() -> list[dict]`

### Q2 — arduino_dash api_routes.py

- [x] Move 4 PubSub routes to `/api/pubsub/board/*`
- [x] Add `GET /api/daemon/status`
- [x] Add `GET /api/board/<path:port>/status` (local CRUD)
- [x] Add `GET /api/boards/list`
- [x] Add `GET /api/boards/events`
- [x] Add `GET /api/sketches/last-upload` (returns null + 404 if none)
- [x] Enhance `GET /api/sketches` with `?hardware_id=X` filter
- [x] Import additions: `get_known_boards`, `get_board_events`, `get_port_info`, `get_assignment`, `_resolve_latest_upload`

### Q3 — medminder_dash api_routes.py

- [x] Add imports: `get_pubsub`, `is_connected`, `is_daemon_ready`, `get_board_events`
- [x] Add 4 PubSub endpoints
- [x] Rename `/api/board_list` → `/api/boards/list`
- [x] Add `GET /api/daemon/status`
- [x] Add `GET /api/board/<path:port>/status` (local CRUD)
- [x] Add `GET /api/boards/events`
- [x] Add `GET /api/sketches/last-upload`
- [x] Enhance `GET /api/sketches` with `?hardware_id=X` filter

### Q4 — medminder_dash html_routes.py

- [x] Comment out `/boards/event` route (lines 774-778)
- [x] Remove `get_board_events` from import line (line 44)

### Q5 — Update tests

- [x] `arduino_dash/tests/test_app.py`: 4 URL changes (lines 1505, 1514, 1523, 1532)
- [x] Update `TestApiBoardList` test to check new CRUD behavior
- [x] `medminder_dash/tests/test_routes.py`: Update `TestBoardsEvent` to hit `/api/boards/events`

### Q6 — Module docs

- [x] `arduino_dash/docs/state.md` — add `_board_events`, `_board_events_lock`
- [x] `arduino_dash/docs/utils.md` — add `get_board_events()`
- [x] `arduino_dash/docs/api_routes.md` — new route tables
- [x] `medminder_dash/docs/api_routes.md` — new route tables

### Q7 — Verification

- [x] `nox -s all_tests` — 8/8 sessions green
- [x] `scripts_tests`: pass
- [x] `tests(board_manager)`: pass
- [x] `tests(board_manager_client)`: pass
- [x] `tests(arduino_sketch_tools)`: pass
- [x] `tests(arduino_dash)`: pass
- [x] `tests(arduino_grpc)`: pass
- [x] `tests(medminder_dash)`: pass

### Q8 — Agent-facing docs sync

- [x] PLAN.md
- [x] JOURNAL.md
- [x] CODEBASE_REFERENCE.md
- [x] IMPLEMENTATION_* docs
- [x] TESTING_* docs
- [x] REVIEW_* docs
{% endraw %}
