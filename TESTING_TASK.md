---
---
{% raw %}
# Testing Task — Phase 99: HTML Template Homogenisation

**Date**: 2026-06-22 12:43

**Status**: ✅ COMPLETED

## Testing Tasks — All Passed

| # | Command | Status | Result |
|---|---------|--------|--------|
| 1 | `nox -s 'tests(arduino_dash)'` after Q1a | ✅ | 119 pass |
| 2 | `nox -s 'tests(medminder_dash)'` after Q1b+c+d | ✅ | 186 pass, 1 skip |
| 3 | `nox -s 'tests(arduino_dash)' 'tests(medminder_dash)'` after Q2a+b | ✅ | 119 + 186 |
| 4 | Same after Q3a+b | ✅ | 119 + 186 |
| 5 | Same after Q4a+b | ✅ | 119 + 186 |
| 6 | Same after T1+T2+T3 | ✅ | 119 + 186 |
| 7 | Same after Q6 | ✅ | 119 + 186 |
| 8 | Final regression (both suites) | ✅ | 119 ✓ / 186 ✓ |

**Test fix applied**: 3 tests in `medminder_dash/tests/test_routes.py::TestBoardDetailFqbn` were updated to assert htmx `/last-upload` container attributes instead of static sketch_path values, since board_detail.html now uses dynamic loading.
## Phase 100 — Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14

**Status**: ✅ COMPLETED

## Testing Tasks — All Passed

| # | Task | Status | Result |
|---|------|--------|--------|
| 1 | arduino_dash survival (no shell hacks) | ✅ | HTTP 200 ✓ |
| 2 | arduino_dash --stop cleanup | ✅ | "Stopped PID" ✓ |
| 3 | arduino_dash --logfile capture | ✅ | 571 bytes ✓ |
| 4 | medminder_dash survival (no shell hacks) | ✅ | HTTP 200 ✓ |
| 5 | medminder_dash --stop cleanup | ✅ | "Stopped PID" ✓ |
| 6 | medminder_dash --logfile capture | ✅ | 649 bytes ✓ |
| 7 | Stale PID handling | ✅ | Cleans up pidfile ✓ |

## Phase 100c — Fix Console Errors (idiomorph.js 404 + WS Invalid Frame Header)

**Date**: 2026-06-24 17:57

**Status**: ✅ COMPLETED

## Testing Tasks — All Passed

| # | Task | Status | Result |
|---|------|--------|--------|
| 1 | New idiomorph CDN resolves | ✅ | HTTP 200 (via follow-redirect) |
| 2 | Old idiomorph CDN returns 404 | ✅ | HTTP 404 (via follow-redirect) |
| 3 | simple-websocket in arduino_dash pyproject.toml | ✅ | Present at line 14 |
| 4 | simple-websocket in medminder_dash pyproject.toml | ✅ | Present at line 15 |
| 5 | idiomorph URL fixed in arduino_dash base.html | ✅ | `idiomorph/dist/idiomorph-ext.js` |
| 6 | idiomorph URL fixed in medminder_dash base.html | ✅ | `idiomorph/dist/idiomorph-ext.js` |
| 7 | No regressions — arduino_dash tests | ✅ | Same 111 pre-existing errors (no new failures) |
| 8 | No regressions — medminder_dash tests | ✅ | Same 1 pre-existing failure (no new failures) |
## Phase 101 — Redesign & Rebuild Standalone Distributions

**Date**: 2026-06-24 18:54

**Status**: ✅ COMPLETED

## Testing Tasks — All Passed

| # | Task | Status | Result |
|---|------|--------|--------|
| 1 | arduino-dash smoke (`--help`) | ✅ | Exit 0, usage output shown |
| 2 | medminder-dash smoke (`--help`) | ✅ | Exit 0, usage output shown |
| 3 | board-manager smoke (`--help`) | ✅ | Exit 0, usage output shown |
| 4 | arduino-dash modules | ✅ | All 7 modules present |
| 5 | medminder-dash modules | ✅ | All 7 modules present |
| 6 | arduino-dash templates | ✅ | All templates + partials present |
| 7 | medminder-dash templates | ✅ | All templates + partials present |
| 8 | simple-websocket in arduino-dash | ✅ | Present in dist |
| 9 | simple-websocket in medminder-dash | ✅ | Present in dist |
| 10 | Static files (style.css + favicons) | ✅ | Present in both dashboards |
| 11 | All 3 binaries built | ✅ | 51MB each, `.tar.gz` archives created |
{% endraw %}
