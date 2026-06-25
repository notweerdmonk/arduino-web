---
---
{% raw %}
# Review Progress — Phase 102: Fix Pre-Existing Test Failures

**Date**: 2026-06-25 09:10

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Verify `app.py` re-exports | ✅ | 28 names re-exported across 3 import blocks |
| 2 | Verify `state.py` UPLOAD_BASE_DIR re-export | ✅ | Fixes 9 broken production references |
| 3 | Verify `api_routes.py` import fix | ✅ | `html_routes` → `sketch_management` |
| 4 | Verify test assertion fixes | ✅ | 2 files, 2 assertions relaxed |
| 5 | `nox -s all_tests` | ✅ | 8/8 sessions, 0 failures |

## Previous: ESLint Inline JS Linting (2026-06-24 12:32)

**Status**: ✅ COMPLETED

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | `eslint-plugin-html` installed and configured | ✅ | v8.1.4, CJS monkey-patch plugin (no processor export) |
| 2 | Top-level `eslint.config.mjs` proxy config | ✅ | Root file imports + re-exports `config/eslint.config.mjs` (MCP limitation) |
| 3 | Browser globals added to HTML config section | ✅ | `document`, `window`, `htmx`, `fetch`, etc. |
| 4 | Lint 4 HTML templates with inline `<script>` | ✅ | 0 errors, 4 warnings (false positives from HTML `onchange`/`onclick`) |
| 5 | Fix `showModal` no-undef in dnd_overlay.html | ✅ | Added `/* global showModal */` directive |
| 6 | Fix unused `e` param in dragleave handler | ✅ | Removed unused parameter |

## Phase 103 — API Route Restructure ✅ COMPLETED

**Date**: 2026-06-25 11:57

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | arduino_dash PubSub routes moved to `/api/pubsub/board/*` | ✅ | 4 routes relocated, no regressions |
| 2 | arduino_dash new CRUD routes | ✅ | 5 endpoints, all thin wrappers around existing helpers |
| 3 | medminder_dash PubSub routes added | ✅ | 4 endpoints |
| 4 | medminder_dash `/api/board_list` renamed | ✅ | Now `/api/boards/list` |
| 5 | medminder_dash `/boards/event` commented out | ✅ | Import removed too |
| 6 | `/api/sketches/last-upload` | ✅ | None + 404 handling confirmed |
| 7 | `/api/sketches ?hardware_id=X` | ✅ | Filter applied in both dashboards |
| 8 | arduino_dash events buffer | ✅ | `_board_events`, lock, `get_board_events()` |
| 9 | Test updates | ✅ | 4 URL changes + TestBoardsEvent redirect |
| 10 | `nox -s all_tests` | ✅ | 8/8 sessions, 0 failures, 0 errors |
| 11 | Module docs | ✅ | 4 files updated |
| 12 | Agent-facing docs | ✅ | All synced |
{% endraw %}