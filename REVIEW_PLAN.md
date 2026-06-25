---
---
{% raw %}
# Review Plan — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

## Review Criteria

### Configuration Correctness
- [x] `_config.yml` — single `plugins:` list with all 3 plugins
- [x] `_config.yml` — `theme: minima` set
- [x] `_config.yml` — `defaults:` with `layout: default` for all pages
- [x] `Gemfile` — `jekyll-archives` removed
- [x] `Gemfile` — `gem "minima", "~> 2.5"` pinned

### Build Verification
- [x] `bundle exec jekyll build` — exit 0
- [x] 0 Liquid syntax errors
- [x] 0 Liquid warnings
- [x] 254 HTML pages generated

### Front Matter Coverage
- [x] 93 doc files in `docs/` directories have `---\n---\n`
- [x] 7 per-package README files have front matter
- [x] `grpc_client/.../README.md` has front matter

### raw/endraw Coverage
- [x] 5 workflow docs with Jinja2 wrapped (JOURNAL.md, PLAN.md, TODOS.md, docs/ws-event-flow.md, CODEBASE_REFERENCE.md)
- [x] 2 research docs with `{{ }}` wrapped (RESEARCH_JOURNAL.md, RESEARCH_PLAN.md)
- [x] No literal closing raw tag inside backtick spans in raw-wrapped files

### Link Correctness
- [x] 24 board_manager links fixed across 5 files
- [x] 27 medminder_dash links fixed across 5 files
- [x] All hrefs in `_site/` resolve to existing `.html` files
- [x] Nested subpackage doc directories exist: `board_manager/python/board_manager/board_manager/docs/`

### README Links
- [x] 9 README hrefs in `_site/index.html`
- [x] All README hrefs resolve to `.html` (not `.md`)
- [x] 8 README `.html` files exist in `_site/`

### Documentation Sync
- [x] PLAN.md — Phase 93 entry added
- [x] JOURNAL.md — Phase 93 entry updated
- [x] CODEBASE_REFERENCE.md — Jekyll section added
- [x] IMPLEMENTATION_* docs — all updated
- [x] TESTING_* docs — all updated
- [x] REVIEW_* docs — all updated (this file)
- [x] TODOS.md — Phase 93 entry added
## Phase 95 — Git Tree Preparation Plan

**Date**: 2026-06-20 15:40
**Status**: ✅ COMPLETED AND REVIEWED

### Review Criteria

#### File System Cleanliness
- [x] Stale upload sketches removed from working tree — ✅ (verified via `ls`)
- [x] `.gitignore` updated with new artifact patterns — ✅ (verified via `git status`)
- [x] `.gitkeep` markers present in empty data directories — ✅ (verified via `find`)

#### Documentation Accuracy
- [x] Workflow docs Phase 93→94 gap filled across 5 IMPLEMENTATION_* files — ✅ (verified via grep)
- [x] `scripts/docs/index.md` false `--help` claim corrected to `usage` — ✅ (verified via grep)
- [x] `WS_EVENT_FLOW.md` moved to `docs/ws-event-flow.md` — ✅ (old path gone, new path exists)
- [x] All cross-references updated to point to `docs/ws-event-flow.md` — ✅ (verified via grep)

#### Process
- [x] Sequential `git add` with user approval per group — ✅ (session log confirmed)
- [x] No unintended files staged — ✅

## Phase 96 — Wire test_ci.sh into Nox scripts_tests

**Date**: 2026-06-20 20:03
**Status**: ✅ COMPLETED AND REVIEWED

### Review Criteria

#### Code Correctness
- [x] `noxfile.py` change is minimal (+1 line) — ✅ (single `session.run()` call)
- [x] Pattern matches existing `test_install_arduino_deps.sh` call — ✅

#### Test Verification
- [x] `test_ci.sh` passes 30/30 assertions standalone — ✅ (exit 0)
- [x] `nox -s scripts_tests` includes test_ci.sh — ✅ (170 total, all pass in 24s)
- [x] No regression in pytest suite (128/128 pass) — ✅
- [x] No regression in existing bash tests (12/12 pass) — ✅

#### Code Quality
- [x] Script is self-contained (bash-only, fake nox shim) — ✅
- [x] Uses `BASH_SOURCE` for path resolution (works from any CWD) — ✅
- [x] Zero external dependencies beyond bash — ✅

## Phase 98 — WS Push Migration (Badge OOB → Compile/Upload OOB → Compile Progress Bar)

**Date**: 2026-06-21 11:55

**Status**: ✅ IMPLEMENTED AND REVIEWED

### Review Criteria

#### Code Quality
- [x] No remaining `hx-trigger="every 10s"` in any base template — ✅ (verified via grep, 0 matches)
- [x] Daemon badge partial has no hx-* attributes — ✅ (verified via grep, 0 hx- matches)
- [x] Board status badge partial has no hx-* attributes — ✅ (verified via grep, 0 hx- matches)
- [x] Board detail badge IDs are unique per port — ✅ (uses `--{{ port | replace('/', '_') }}` suffix)

#### Behavioral Regressions
- [x] Daemon badge still renders on initial page load — ✅ (hx-trigger="load" preserved on wrapper)
- [x] Board status badge still renders on initial page load — ✅ (hx-trigger="load" preserved on wrapper)
- [x] Compile output still appears in correct container — ✅ (OOB targeting matches existing output div IDs)
- [x] Upload output still appears in correct container — ✅ (OOB targeting matches existing output div IDs)
- [x] Progress bar appears and updates during compilation — ✅ (gRPC TaskProgress drives OOB updates)
- [x] [N%] prefix prepended to compile output lines — ✅ (format: `[42%] Compiling core...`)

#### Tests
- [x] All 8 nox sessions pass with 0 failures — ✅ (~3m, all green)
- [x] No pre-existing pipenv lock failures — ✅ (noxfile PROJECT_ROOT fix resolved them)

##### Quantum 6 — Rename TestAdminBoardSelectorPolling → TestAdminBoardSelector
- [x] Class renamed in `test_admin.py:811` + docstring updated to Phase 71 WS push ref — ✅
- [x] `README.md:205` reference updated — ✅
- [x] 186 medminder_dash tests pass, 1 skip — ✅ (0 regression)
- [x] No stale `TestAdminBoardSelectorPolling` in source code — ✅ (only auto-generated files)
- [x] Pure rename — no functional change, no test delta — ✅

## Phase 99 — HTML Template Homogenisation Across Both Dashboards

**Date**: 2026-06-22 12:43

**Status**: ✅ IMPLEMENTED AND REVIEWED

### Review Criteria

#### Template Correctness
- [x] arduino_dash board_detail.html — no `<form>` wrapper, flat `<div>` + htmx `/last-upload` — ✅
- [x] medminder_dash board_detail.html — htmx `/last-upload` replaces hidden input, `show_sketch_tools` guard — ✅
- [x] Both admin.html — assigned-sketch-info (arduino) and medicine partial (medminder) — ✅
- [x] Both admin_board_selector.html — template vars for route attrs — ✅
- [x] Both compile_upload_card.html — step nums, generic desc, entity converged — ✅

#### Partial Alignment (14 shared templates now identical)
- [x] dnd_overlay.html — trailing newline matches — ✅
- [x] board_card.html — `or 'Unknown'` guard — ✅
- [x] delete_confirm_modal.html — `hardware_id` in hx-vals — ✅
- [x] base.html — DnD listeners match — ✅

#### Route Context
- [x] `show_sketch_tools` / `show_medicines_section` set correctly in both apps — ✅
- [x] `active_board_sketch` resolved from shared SketchRegistry in arduino_dash admin — ✅
- [x] admin_board_selector template vars passed as Python kwargs — ✅

#### Shared Module
- [x] `SketchRegistry` class in `arduino_sketch_tools` — exports `get_assignment`, `set_assignment`, `clear_assignment`, `get_all_assignments` — ✅
- [x] Both per-app `sketch_registry.py` are thin wrappers — ✅
- [x] Wheel rebuilt, Pipfile.locks updated — ✅

#### Tests
- [x] `nox -s 'tests(arduino_dash)'` — 119 passed — ✅
- [x] `nox -s 'tests(medminder_dash)'` — 186 passed, 1 skipped — ✅
- [x] 3 TestBoardDetailFqbn tests updated for htmx /last-upload pattern — ✅

## Phase 100 — Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14

**Status**: ✅ IMPLEMENTED AND REVIEWED

### Review Criteria

#### Code Correctness
- [x] `os.fork()` + `os.setsid()` creates new session immune to SIGHUP — ✅
- [x] `_redirect_io(logfile)` closes stdin, dup2 stdout/stderr to logfile — ✅
- [x] `--stop` reads pidfile, sends SIGTERM, waits for exit — ✅
- [x] `--force` sends SIGKILL if SIGTERM doesn't work — ✅
- [x] Stale pidfile detection (ProcessLookupError → clean up) — ✅
- [x] Stale PID check (`_remove_pidfile` verifies PID matches) — ✅

#### Behavioral Correctness
- [x] Process survives bash tool exit without `&`, `disown`, `timeout` — ✅
- [x] `--logfile` captures stdout/stderr — ✅ (571 / 649 bytes)
- [x] `--stop` performs clean shutdown — ✅
- [x] Second instance warns about existing PID — ✅

#### Tests
- [x] All 6 server lifecycle scenarios pass (both apps) — ✅
- [x] No regression in dashboard tests — ✅ (119 + 186 pass)
- [x] No shell hacks used — ✅

## Phase 101 — Redesign & Rebuild Standalone Distributions

**Date**: 2026-06-24 18:54

**Status**: ✅ REVIEWED AND APPROVED

### Review Criteria

#### Config Correctness
- [x] `@REPO_ROOT@` placeholder replaces all hardcoded absolute paths in 3 pyoxidizer.bzl files ✅
- [x] `"simple-websocket>=1.0.0"` added to both dashboard pyoxidizer.bzl files ✅
- [x] `pip_download()` → `pip_install()` for all local wheel paths ✅
- [x] `build_standalone.sh`: `sed -i` substitution + `git checkout` cleanup via RETURN trap ✅

#### Build Verification
- [x] `nox -s all_builds` — all 6 wheels built successfully ✅
- [x] `./scripts/build_standalone.sh` — all 3 binaries built (51MB each) ✅
- [x] No build errors or warnings ✅

#### Binary Verification
- [x] arduino-dash `--help` — exit 0, usage output ✅
- [x] medminder-dash `--help` — exit 0, usage output ✅
- [x] board-manager `--help` — exit 0, usage output ✅

#### Bundle Contents
- [x] All 7 current Python modules present in both dashboard bundles ✅
- [x] All templates + partials present in both dashboard bundles ✅
- [x] Static files (style.css, favicons) present in both dashboard bundles ✅
- [x] `simple-websocket` dep present in both dashboard bundles ✅

#### Documentation
- [x] PLAN.md updated with corrected approach (@REPO_ROOT@ placeholder, not __file__) ✅
- [x] IMPLEMENTATION_* docs updated with actual approach ✅
- [x] TESTING_* docs updated with test results ✅
- [x] REVIEW_* docs updated (this file) ✅
- [x] CODEBASE_REFERENCE.md updated with Phase 101 section ✅
- [x] JOURNAL.md updated with Phase 101 entry ✅
{% endraw %}

## Phase 100c — Fix Console Errors (idiomorph.js 404 + WS Invalid Frame Header)

**Date**: 2026-06-24 17:57

**Status**: ✅ REVIEWED AND APPROVED

### Review Criteria

#### idiomorph CDN URL
- [x] arduino_dash `base.html:9` — `htmx.org/dist/ext/idiomorph.js` → `idiomorph/dist/idiomorph-ext.js` ✅
- [x] medminder_dash `base.html:13` — Same URL change ✅
- [x] New URL returns HTTP 200 (`curl -sIL`) ✅
- [x] Old URL returns HTTP 404 ✅

#### simple-websocket dependency
- [x] arduino_dash `pyproject.toml:14` — `simple-websocket>=1.0.0` added ✅
- [x] medminder_dash `pyproject.toml:15` — `simple-websocket>=1.0.0` added ✅

#### No regressions
- [x] arduino_dash tests — same 111 pre-existing errors (unchanged) ✅
- [x] medminder_dash tests — same 1 pre-existing failure (unchanged) ✅

#### Documentation
- [x] PLAN.md updated with Phase 100c entry ✅
- [x] JOURNAL.md updated with Phase 100c entry ✅
- [x] CODEBASE_REFERENCE.md updated with Phase 100c section ✅
- [x] IMPLEMENTATION_* documents all updated ✅
- [x] TESTING_* documents all updated ✅
- [x] REVIEW_* documents all updated ✅

## 2026-06-24 12:32 — ESLint Inline JS Linting with eslint-plugin-html

**Date**: 2026-06-24 12:32

**Status**: ✅ COMPLETED

### Scope

Configure ESLint to lint inline JavaScript inside Jinja2 HTML templates using `eslint-plugin-html`. Work around ESLint MCP limitation (only reads config from working directory root).

### Review Criteria

#### Configuration
- [x] `eslint-plugin-html` v8.1.4 installed as devDependency ✅
- [x] Top-level `eslint.config.mjs` proxy config importing from `config/eslint.config.mjs` ✅
- [x] HTML config section has own `languageOptions.globals` (browser globals don't carry over from `.js` section) ✅
- [x] `plugins: { html }` registered for HTML files (monkey-patch, no `processor` needed) ✅

#### Lint Results
- [x] 0 errors across 4 HTML templates with inline `<script>` ✅
- [x] 4 warnings (false positives from HTML `onchange`/`onclick` attributes) ✅

#### Fixes Applied
- [x] `dnd_overlay.html` — added `/* global showModal */` linter directive ✅
- [x] `dnd_overlay.html` — removed unused `e` parameter in `dragleave` handler ✅

## 2026-06-24 02:52 — Code Review: pubsub_infra→pubsub Rename + Documentation Sync

**Date**: 2026-06-24 02:52

**Status**: ✅ REVIEWED AND APPROVED

### Scope of Review

The changes under review span:
1. **Rename** `pubsub_infra.py` → `pubsub.py` (and `pubsub_infra.md` → `pubsub.md`) with all import references updated
2. **Documentation synchronization** across 45+ files (code references, plan/task/progress journals)
3. **Code quality audit** using ruff linter + ruff format check

### Review Criteria

#### Correctness
- [x] No missed `pubsub_infra` references in source files ✅
- [x] All imports updated correctly ✅
- [x] E2E server imports consistent with renamed module ✅

#### Linter Results
- [x] Ruff check executed — 208 errors found ✅
- [x] Ruff format check executed — 56 files need formatting ✅
- [x] Linter suggestions for HTML/JavaScript documented ✅

#### Code Quality (app.py)
- [x] Unused imports identified and quantified ✅
- [x] E402 (import order) violations identified ✅

#### Security
- [x] XSS vectors reviewed in template/WS code ✅
- [x] Path traversal protections reviewed ✅

#### Test Coverage
- [x] Test imports updated for rename ✅
- [x] Unused imports in tests identified ✅

## 2026-06-24 03:40 — Code Review: JS Linting Setup (ESLint)

**Date**: 2026-06-24 03:40

**Status**: ✅ COMPLETED

### Scope

Set up ESLint for the project's JavaScript (inline `<script>` in base.html templates). TypeScript linting skipped per user request.

### Files Under Review

| Language | Location | Description |
|----------|----------|-------------|
| JavaScript (inline) | `arduino_dash/.../base.html:23-105` | DnD prevention, WS event handling, JS helpers |
| JavaScript (inline) | `medminder_dash/.../base.html:23-105` | DnD prevention, WS event handling, JS helpers |
| TypeScript | `e2e/` (10 files) | ⏸️ Skipped per user request |

### Review Criteria

- [x] ESLint config created in `config/` ✅
- [x] Inline JS linting — 22 warnings, 0 errors ✅
- [ ] TypeScript linting — ⏸️ Skipped (needs typescript-eslint)
- [x] All findings documented in REVIEW_JOURNAL.md ✅
- [ ] djlint ⏸️ Postponed (blocked by click compatibility issue)

## 2026-06-24 12:02 — Linter Fix Round: ruff + eslint + djlint

**Date**: 2026-06-24 12:02

**Status**: ✅ COMPLETED

### Scope

Full pass across all project Python, JS, and HTML template files to fix linting warnings/errors:

1. **ruff** — Fix all F401/E402/F841/E731/E713 errors (85 total)
2. **ruff format** — Format all Python files (16 reformatted)
3. **eslint** — No standalone `.js` project files exist; config created in `config/eslint.config.mjs`
4. **djlint** — Fix all 8 template warnings (H021/H023/H030/H031)

### Review Criteria

#### Ruff Check
- [x] F841 unused local variables in `api_routes.py` and `html_routes.py` fixed ✅
- [x] E402 import ordering in `app.py` and `pubsub.py` fixed ✅
- [x] E402 in `medminder_dash_server.py` suppressed with `# noqa` (legitimate sys.path usage) ✅
- [x] 0 remaining ruff errors across all examined Python files ✅

#### Ruff Format
- [x] All 29 examined Python files properly formatted ✅

#### ESLint
- [x] `config/eslint.config.mjs` exists with JS recommended rules ✅
- [x] No standalone `.js` files in project (all JS inline in HTML templates) — properly documented ✅
- [x] ESLint MCP plugin available for inline JS linting (requires extraction to standalone files) ✅

#### djlint
- [x] Entity references (`&#9889;`, `&#8230;`) replaced with actual Unicode characters ✅
- [x] Inline `style="display:none"` replaced with CSS class `.modal-hidden` ✅
- [x] Inline `style="word-break:break-all"` replaced with CSS class `.word-break-all` ✅
- [x] Meta description/keywords added to `base.html` ✅
- [x] 0 remaining djlint errors across 25 template files ✅
- [x] `showModal`/`hideModal` JS functions updated to use `classList` instead of `style.display` ✅
- [x] `hx-on::after-request` handler updated to use `classList.add('modal-hidden')` ✅

## Phase 102 — Fix Pre-Existing Test Failures ✅ COMPLETED

**Date**: 2026-06-25 09:10

### Review Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | `app.py` re-exports are complete and correct | ✅ All 14 state vars, 9 pubsub functions, 5 sketch_management functions |
| 2 | No circular imports from added re-exports | ✅ Verified by successful `py_compile` and test run |
| 3 | `UPLOAD_BASE_DIR` correctly re-exported from `state.py` | ✅ `state.UPLOAD_BASE_DIR` now resolves to `settings.UPLOAD_BASE_DIR` |
| 4 | `api_routes.py` import points to correct module | ✅ `sketch_management._warm_upload_registry` |
| 5 | Test assertions are not brittle to HTML formatting | ✅ Changed to id-only checks; no contiguous multi-attr assertions |
| 6 | All 8 nox sessions pass | ✅ 0 failures, 0 errors

---

## Phase 103 — API Route Restructure ✅ COMPLETED

**Date**: 2026-06-25 11:57

### Review Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | PubSub routes moved to `/api/pubsub/board/*` in arduino_dash | ✅ 4 routes relocated |
| 2 | New CRUD routes added to arduino_dash | ✅ 5 endpoints: daemon status, board connection status, boards list, boards events, last-upload |
| 3 | PubSub routes added to medminder_dash | ✅ 4 endpoints matching arduino_dash |
| 4 | `/api/board_list` → `/api/boards/list` renamed | ✅ Old route removed, new route registered |
| 5 | `/boards/event` HTML route commented out | ✅ Lines 774-778 commented with explanatory note |
| 6 | `/api/sketches` enhanced with `?hardware_id=X` filter | ✅ Both dashboards |
| 7 | `/api/sketches/last-upload` returns `(None, 404)` when no sketch | ✅ Consistent across both dashboards |
| 8 | arduino_dash board events buffer added | ✅ `_board_events` + `_board_events_lock` + `get_board_events()` |
| 9 | Test URLs updated correctly | ✅ 4 changes in test_app.py + TestBoardsEvent redirect |
| 10 | `nox -s all_tests` passes | ✅ 8/8 sessions, 0 failures, 0 errors |
| 11 | Module docs updated | ✅ 4 doc files |
| 12 | Agent-facing docs synced | ✅ All workflow + project docs |
