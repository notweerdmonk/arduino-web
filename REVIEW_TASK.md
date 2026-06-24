---
---
{% raw %}
# Review Task — Phase 99: HTML Template Homogenisation

**Date**: 2026-06-22 12:43

**Status**: ✅ REVIEWED AND APPROVED

## Review Items — All Passed

| # | Item | Result |
|---|------|--------|
| 1 | Template correctness (board_detail, admin, admin_board_selector, compile_upload_card) | ✅ |
| 2 | Partial alignment (dnd_overlay, board_card, delete_confirm_modal, base.html) | ✅ |
| 3 | Route context variables (show_sketch_tools, show_medicines_section, board_selector_*) | ✅ |
| 4 | Shared SketchRegistry module in arduino_sketch_tools | ✅ |
| 5 | Test regression — arduino_dash 119 pass | ✅ |
| 6 | Test regression — medminder_dash 186 pass, 1 skip | ✅ |
## Phase 100 — Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14

**Status**: ✅ REVIEWED AND APPROVED

## Review Items — All Passed

| # | Item | Result |
|---|------|--------|
| 1 | Daemonize pattern (fork + setsid + redirect) | ✅ |
| 2 | CLI flags (--pidfile, --stop, --force, --logfile) | ✅ |
| 3 | arduino_dash survival, --stop, --logfile | ✅ |
| 4 | medminder_dash survival, --stop, --logfile | ✅ |
| 5 | Stale pidfile + ProcessLookupError handling | ✅ |
| 6 | No shell hacks used | ✅ |
{% endraw %}

## 2026-06-24 12:02 — Linter Fix Round: ruff + eslint + djlint

**Status**: ✅ COMPLETED

## Review Items

| # | Item | Result |
|---|------|--------|
| 1 | Run ruff check — identify all 85 errors | ✅ Fixed |
| 2 | Run ruff format — format 16 files | ✅ Done |
| 3 | Fix F841 (unused hardware_id) in api_routes.py | ✅ Passed to _render_sketch_path_selector |
| 4 | Fix F841 (unused hardware_id) in html_routes.py | ✅ Passed to all _render_sketch_path_selector calls |
| 5 | Fix E402 in app.py (imports after logger) | ✅ Moved logger after all imports |
| 6 | Fix E402 in pubsub.py (late import load_sketch_dir) | ✅ Moved to top of file |
| 7 | Fix E402 in medminder_dash_server.py | ✅ Suppressed with # noqa (legitimate) |
| 8 | ESLint config exists | ✅ No standalone JS files to lint |
| 9 | Fix djlint H023 entity references | ✅ Replaced with actual Unicode |
| 10 | Fix djlint H021 inline styles | ✅ Replaced with CSS classes |
| 11 | Fix djlint H030/H031 meta tags | ✅ Added to base.html |
| 12 | Update CSS with modal-hidden and word-break-all classes | ✅ Done |
| 13 | Update showModal/hideModal JS to use classList | ✅ Done |
## 2026-06-24 12:32 — ESLint Inline JS Linting with eslint-plugin-html

**Status**: ✅ COMPLETED

## Review Items

| # | Item | Result |
|---|------|--------|
| 1 | Install eslint-plugin-html v8.1.4 | ✅ |
| 2 | Create top-level eslint.config.mjs proxy (import from config/) | ✅ Required by ESLint MCP |
| 3 | Add browser globals to HTML config section | ✅ document, window, htmx, fetch, etc. |
| 4 | Lint 4 HTML templates (base.html ×2, dnd_overlay.html ×2) | ✅ 0 errors, 4 warnings |
| 5 | Fix no-undef for showModal in dnd_overlay.html | ✅ Added `/* global showModal */` |
| 6 | Fix unused `e` param in dragleave handler | ✅ Removed parameter |

## 2026-06-24 02:52 — Code Review: pubsub_infra→pubsub Rename + Documentation Sync

**Status**: ✅ REVIEWED AND APPROVED

## Review Items

| # | Item | Result |
|---|------|--------|
| 1 | Verify all pubsub_infra references updated → pubsub | ✅ |
| 2 | Run ruff linter — identify all F401/E402/F841/E731/E713 issues | ✅ |
| 3 | Run ruff format check — identify unformatted files | ✅ |
| 4 | Review app.py unused imports (15+ F401 violations) | ✅ |
| 5 | Review pubsub.py correctness | ✅ |
| 6 | Review api_routes.py dead code (hardware_id on line 318) | ✅ |
| 7 | Review html_routes.py dead code (hardware_id on line 901) | ✅ |
| 8 | Review security: XSS in _on_board_event string concat | ✅ |
| 9 | Review test files for import correctness | ✅ |
| 10 | Suggest HTML/JS linters | ✅ |

## 2026-06-24 03:40 — Code Review: JS Linting Setup (ESLint)

**Status**: ✅ COMPLETED

## Review Items

| # | Item | Result |
|---|------|--------|
| 1 | Create eslint config in config/ | ✅ |
| 2 | Run eslint on inline JS (base.html) | ✅ — 22 warnings, 0 errors |
| 3 | Run eslint on TypeScript Playwright tests | ⏸️ Skipped per user request |
| 4 | Document eslint findings in REVIEW_JOURNAL.md | ✅ |
