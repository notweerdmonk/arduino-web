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
{% endraw %}

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
