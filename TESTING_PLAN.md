---
---
{% raw %}
# Testing Plan — Phase 99: HTML Template Homogenisation

**Date**: 2026-06-22 12:43

**Status**: ✅ COMPLETED

## Test Strategy

Template-only changes require verification that:
1. No template syntax errors (Jinja2 rendering)
2. No broken HTMX attribute references (IDs, endpoints)
3. No regression in existing test assertions

Since all changes are in Jinja2 templates, the primary test strategy is running the existing test suites — they exercise the templates via Flask's `render_template` and `client.get()`.

## Test Scenarios by Quantum

| Q | Files Changed | Test Command | What It Covers |
|---|-------------|-------------|----------------|
| Q1a | arduino_dash board_detail.html | `nox -s 'tests(arduino_dash)'` | Template renders, HTMX attrs correct, buttons have correct hx-include |
| Q1b | medminder_dash board_detail.html | `nox -s 'tests(medminder_dash)'` | Template renders, htmx /last-upload loads, modals not shown when guarded |
| Q1c | medicine_management.html new | `nox -s 'tests(medminder_dash)'` | Partial renders in board_detail context |
| Q1d | html_routes.py (both) | Both test suites | Route context includes new variables |
| Q2a | arduino_dash admin.html | `nox -s 'tests(arduino_dash)'` | Admin page renders, assigned-sketch-info conditional |
| Q2b | medminder_dash admin.html | `nox -s 'tests(medminder_dash)'` | Admin page renders, medicine section works via partial |
| Q3a | Both admin_board_selector.html | Both test suites | Template vars resolve, HTMX attrs correct |
| Q4a+b | Both compile_upload_card.html | Both test suites | Step numbers visible, description correct |
| T1+T2+T3 | 3 partials | Both test suites | No rendering errors, hx-vals correct |
| Q6 | medminder_dash base.html | `nox -s 'tests(medminder_dash)'` | No JS syntax errors in base template |

## Regression Risk

Low — all changes are structural template edits. No Python logic, no new routes, no CSS changes. Existing tests verify template rendering through route responses.
## Phase 100 — Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14

**Status**: ✅ COMPLETED

## Test Strategy

Server lifecycle changes require verification that:
1. Process survives bash tool exit (no `&`, `disown`, `timeout` hacks)
2. `--stop` flag kills the server cleanly
3. `--logfile` flag captures stdout/stderr
4. Stale pidfile is cleaned up (dead PID)

## Test Scenarios

| # | Scenario | Script | Verification |
|---|----------|--------|-------------|
| 1 | Start & survive | arduino_dash | `curl http://localhost:8765` returns 200 after bash exit |
| 2 | --stop | arduino_dash | `python3 arduino_dash_server.py --stop` prints "Stopped PID X" |
| 3 | --logfile | arduino_dash | Logfile has >0 bytes of output |
| 4 | Start & survive | medminder_dash | `curl http://localhost:8766` returns 200 after bash exit |
| 5 | --stop | medminder_dash | `python3 medminder_dash_server.py --stop` prints "Stopped PID X" |
| 6 | --logfile | medminder_dash | Logfile has >0 bytes of output |
| 7 | Stale pidfile | both | Dead PID in pidfile → cleaned up |

## Phase 100c — Fix Console Errors (idiomorph.js 404 + WS Invalid Frame Header)

**Date**: 2026-06-24 17:57

**Status**: ✅ COMPLETED

## Test Strategy

Two non-blocking console error fixes. Verification is mostly external (CDN resolution + dep presence):

| # | Test | Method | Pass Criteria |
|---|------|--------|--------------|
| 1 | New idiomorph CDN resolves | `curl -sIL https://unpkg.com/idiomorph/dist/idiomorph-ext.js` | HTTP 200 |
| 2 | Old idiomorph CDN returns 404 | `curl -sIL https://unpkg.com/htmx.org/dist/ext/idiomorph.js` | HTTP 404 |
| 3 | simple-websocket in arduino_dash pyproject.toml | `grep simple-websocket arduino_dash/.../pyproject.toml` | Match found |
| 4 | simple-websocket in medminder_dash pyproject.toml | `grep simple-websocket medminder_dash/.../pyproject.toml` | Match found |
| 5 | Correct idiomorph URL in arduino_dash base.html | `grep idiomorph arduino_dash/.../base.html` | `idiomorph/dist/idiomorph-ext.js` |
| 6 | Correct idiomorph URL in medminder_dash base.html | `grep idiomorph medminder_dash/.../base.html` | `idiomorph/dist/idiomorph-ext.js` |
| 7 | No regressions from dep changes | `nox -s 'tests(arduino_dash)' 'tests(medminder_dash)'` | Same results as pre-change |
## Phase 101 — Redesign & Rebuild Standalone Distributions

**Date**: 2026-06-24 18:54

**Status**: ✅ COMPLETED

## Test Strategy

Verification of rebuilt PyOxidizer standalone binaries (no Python test suite — standalone builds are environment-dependent and can't run unit tests). Strategy:

1. **Smoke test** — Each binary `--help` must exit 0 with usage output
2. **Module verification** — All current Python modules present in the bundle's `site-packages`
3. **Template verification** — All templates + partials present in each dashboard bundle
4. **Static file verification** — `style.css`, favicon files present
5. **simple-websocket dep** — Present in both dashboard bundles

## Test Scenarios

| # | Test | Method | Pass Criteria |
|---|------|--------|--------------|
| 1 | arduino-dash smoke | `dist-standalone/arduino-dash/arduino-dash --help` | Exit 0, usage output |
| 2 | medminder-dash smoke | `dist-standalone/medminder-dash/medminder-dash --help` | Exit 0, usage output |
| 3 | board-manager smoke | `dist-standalone/board-manager/board-manager --help` | Exit 0, usage output |
| 4 | arduino-dash modules | `ls .../arduino_dash/` | html_routes, api_routes, pubsub, settings, state, utils, sketch_registry present |
| 5 | medminder-dash modules | `ls .../medminder_dash/` | Same 7 modules present |
| 6 | arduino-dash templates | `ls .../templates/` | base.html, admin.html, board_detail.html + all partials |
| 7 | medminder-dash templates | `ls .../templates/` | Same as above |
| 8 | simple-websocket (arduino-dash) | `ls .../site-packages/simple_websocket/` | Directory exists |
| 9 | simple-websocket (medminder-dash) | `ls .../site-packages/simple_websocket/` | Directory exists |
| 10 | Static files | `ls .../static/style.css` + `ls .../static/favicon/` | All files present in both dashboards |

## Phase 102 — Fix Pre-Existing Test Failures

**Date**: 2026-06-25 09:10

**Status**: ✅ COMPLETED

## Test Strategy

Fix test failures by correcting source code (missing re-exports, wrong imports, brittle assertions). Verification is the existing `nox -s all_tests` suite.

### Root Causes

| # | Issue | Type | Verification |
|---|-------|------|--------------|
| 1 | `app.py` missing state/pubsub/sketch_management re-exports | Test mismatch (access via `_app_module.*`) | `tests(arduino_dash)` passes |
| 2 | `state.py` missing `UPLOAD_BASE_DIR` re-export | Production bug (Phase 69 regression) | `tests(arduino_dash)` passes |
| 3 | `api_routes.py` wrong import (`html_routes`→`sketch_management`) | Production bug (wrong module path) | `tests(arduino_dash)` passes |
| 4 | 2 brittle test assertions (multi-line attrs after djlint) | Test assertion fragility | `tests(arduino_dash)` + `tests(medminder_dash)` pass |

---

## Phase 103 — API Route Restructure ✅ COMPLETED

**Date**: 2026-06-25 11:57

**Test Strategy**: All changes are to route registrations and state additions — no logic changes. Strategy: run the full `nox -s all_tests` suite (8 sessions). Key risk areas:
1. Route URL changes in arduino_dash (4 PubSub routes moved) — test assertions must match new URLs
2. New CRUD endpoints — existing tests should not be affected (they don't hit these endpoints)
3. medminder_dash `/boards/event` commented out — `TestBoardsEvent` must now hit `/api/boards/events`
4. No new test coverage needed for this phase (routes are thin wrappers around existing helpers)

**Test Changes**:
| File | Change |
|------|--------|
| `arduino_dash/tests/test_app.py:1505` | `/api/board/dev/ttyACM0/spawn` → `/api/pubsub/board/dev/ttyACM0/spawn` |
| `arduino_dash/tests/test_app.py:1514` | `/api/board/dev/ttyACM0/status` → `/api/pubsub/board/dev/ttyACM0/status` |
| `arduino_dash/tests/test_app.py:1523` | `/api/board/dev/ttyACM0/remove` → `/api/pubsub/board/dev/ttyACM0/remove` |
| `arduino_dash/tests/test_app.py:1532` | `/api/boards` → `/api/pubsub/boards/health` |
| `medminder_dash/tests/test_routes.py:469-472` | `/boards/event` → `/api/boards/events` |

**Verification**: `nox -s all_tests` — 8/8 sessions, 0 failures, 0 errors ✅
{% endraw %}
