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
