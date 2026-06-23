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
{% endraw %}
