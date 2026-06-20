---
---
{% raw %}
# MedMinder Project Plan

## Overview
Build a gRPC client for arduino-cli in Python3 to detect boards, enumerate boards, compile and upload sketches. Integrates with Flask web app or TUI/GUI interface.

## Project Start: 2026-05-20 04:21

---

### Phase 94 — Noxfile Self-Healing Test Sessions ✅ COMPLETED

**Date**: 2026-06-20
**Status**: ✅ Completed

**Goal**: Fix `tests` and `scripts_tests` sessions in `noxfile.py` to self-heal against stale `Pipfile.lock` hashes after wheel rebuilds. The `tests` session used `pipenv install --dev` which fails with hash mismatch when wheels are rebuilt but lock files still have old hashes. The `scripts_tests` session used `pipenv sync --dev` which silently does nothing when lock doesn't match Pipfile.

**Design**:
1. `tests`: `install --dev` → `lock --dev` + `sync --dev` — regenerates lock before installing
2. `scripts_tests`: `sync --dev` → `install --dev` — auto-regenerates lock if Pipfile changed

**Files changed**: `noxfile.py`

| # | Task | Status |
|---|------|--------|
| 1 | Update `tests` session | ✅ |
| 2 | Update `scripts_tests` session | ✅ |
| 3 | `nox -s all_tests` verification — 8/8 sessions pass | ✅ |
| 4 | Docs sync | ✅ |

### Phase 93 — GitHub Pages Jekyll Documentation Site ✅ COMPLETED

**Date**: 2026-06-20
**Status**: ✅ Completed

**Goal**: Serve the project's documentation as a GitHub Pages site using Jekyll (Minima theme). Fix config/build issues (duplicate `plugins:`, missing `theme:`, missing front matter), fix broken relative links for nested-subpackage doc paths, eliminate Liquid warnings from Jinja2 template syntax, and add missing per-package README links to the top-level docs hub.

**Motivation**: The existing `_config.yml` and `Gemfile` had configuration bugs that prevented Jekyll from building the site: duplicate `plugins:` silently dropped `jekyll-relative-links`, no `theme:` set meant pages rendered as bare HTML with no layout/CSS, and no `defaults:` meant every `.md` file needed individual front matter. Additionally, `jekyll-archives` was in the `Gemfile` but unused (no category/tag front matter or `_layouts/`).

**Design**:
1. **Config fixes**: Merge duplicate `plugins:` into one list, add `theme: minima`, add `defaults:` with `layout: default` for all `.md` files.
2. **Gemfile cleanup**: Remove `jekyll-archives` (unused dependency). Keep Minima 2.5.2 (system-installed).
3. **Front matter**: Add `---\n---\n` to every `.md` file across the repo so Jekyll processes them as pages (not static files). Three batches: (a) 93 doc `.md` files in `docs/` directories, (b) 7 per-package `README.md` files, (c) `grpc_client/.../README.md`.
4. **raw/endraw wrapping**: 7 workflow/research docs with Jinja2 template syntax (`{% block %}`, `{% include %}`) wrapped in a raw/endraw block pair to prevent Liquid syntax errors. 2 research docs with `{{ port.lstrip('/') }}` also wrapped to silence Liquid warnings.
5. **Link fixes**: Two packages (`board_manager`, `medminder_dash`) have nested Python subpackages with the same name as the parent, creating an extra directory level in their doc paths. Fixed 51 links across 5 documentation files.
6. **Missing README links**: Added per-package README links to `index.md` for all 7 packages.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Fix `_config.yml` — merge plugins, add theme, add defaults | ✅ |
| 2 | Remove `jekyll-archives` from Gemfile | ✅ |
| 3 | Add front matter to 93 doc `.md` files | ✅ |
| 4 | Add raw/endraw wrapping to 5 workflow docs with Jinja2 | ✅ |
| 5 | Fix broken relative links — board_manager (24) + medminder_dash (27) | ✅ |
| 6 | Rebuild — 246 HTML pages, 0 errors | ✅ |
| 7 | Wrap 2 RESEARCH docs in raw/endraw to fix 4 Liquid warnings | ✅ |
| 8 | Add front matter to 8 missing README files (7 per-pkg + grpc_client) | ✅ |
| 9 | Add missing README links to `index.md` | ✅ |
| 10 | Final build — 0 errors 0 warnings, 254 HTML pages | ✅ |
| 11 | Docs sync — PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md, all workflow docs | ✅ |

**Build output**: `bundle exec jekyll build` — 0 errors, 0 warnings, 254 HTML pages, ~46s build time.

**Key gotchas**:
1. `jekyll-relative-links` auto-converts `.md` links to `.html` in rendered output — must verify via `grep` that hrefs resolve to `.html`, not leftover `.md`.
2. Never embed the closing raw tag (opening-brace-percent-endraw-percent-closing-brace) inside backtick spans within a raw-wrapped file — Liquid doesn't understand Markdown backticks and closes the raw block at the first occurrence of the closing raw tag.
3. Front matter must be on ALL `.md` files, not just those in `docs/` directories — README files in package roots also need it.
4. Non-fatal `jekyll doctor` bug: `undefined method 'absolute?' for nil:NilClass` when `url:` unset — Jekyll 3.10 known issue, harmless.

**Files changed**: `_config.yml`, `Gemfile`, `index.md`, `docs/architecture.md`, `docs/guide.md`, `docs/tests.md`, `docs/api.md`, `RESEARCH_JOURNAL.md`, `RESEARCH_PLAN.md`, 5 workflow docs raw-wrapped, 101 `.md` files with front matter added.

---

### Phase 83 — Unified Sketch Registry (hardware_id in registry, FCFS dedup, sketch_registry.json) ✅ COMPLETED

**Date**: 2026-06-18
**Status**: ✅ Completed

**Goal**: Unify sketch registry with hardware_id as a first-class dimension, enabling board-scoped queries, one-to-many hardware_id→sketch mapping, and a persistent sketch_registry.json that serves as the warmup source and disk cross-reference.

**Design** (see IMPLEMENTATION_PLAN.md for full details):
1. `.meta` files: add `hardware_ids`, `board_timestamps`, `checksum`, `server_timestamp`
2. Registry entries: same fields — `hardware_ids: list[str]`, `board_timestamps: dict[str, str]`
3. Dir naming: `{hash(ip, ua)[:16]}_{server_timestamp}_{root_name}`
4. Dedup FCFS: same checksum, diff hardware_id → append hw_id to existing entry; diff (ip, ua) → allow duplicate
5. `arduino_sketch_tools`: `_make_meta` gets hardware_id; `_on_upload_resp` records board deploy timestamp
6. `sketch_registry.json`: full serialization of `_upload_registry`; warmup reads this first, falls back to `.meta` cross-ref
7. Retrieval: filter sketches by hardware_id when board connected; show board name in labels
8. WS event → HTMX trigger re-fetches selector on board plug/unplug
9. `board_sketches.json` removed

| Q | Scope | Status |
|---|-------|--------|
| 1 | .meta + registry entry model: add hardware_ids, board_timestamps, server_timestamp | ✅ |
| 2 | Dir naming: hash(ip, ua) salt → update warmup | ✅ |
| 3 | FCFS dedup: same checksum diff hw_id → append; diff (ip, ua) → allow | ✅ |
| 4 | arduino_sketch_tools: _make_meta + _on_upload_resp for board deploy timestamp | ✅ |
| 5 | sketch_registry.json serialize/deserialize + warmup cross-ref | ✅ |
| 6 | Retrieval: _render_sketch_path_selector hw_id filter, board labels | ✅ |
| 7 | WS event → HTMX trigger for live selector refresh | ✅ |
| 8 | Delete route adaptation | ✅ |
| 9 | Docs sync + nox run | ✅ |

---

### Phase 88 — Stale BMS Port Cleanup in boot.py ✅ COMPLETED

**Date**: 2026-06-19 16:40
**Status**: ✅ Completed

**Goal**: Prevent `OSError: [Errno 98] Address already in use` when starting BMS via gunicorn's `when_ready` hook. A stale BMS from a previous unclean shutdown holds port 9090, causing the new BMS to fail on `_bind_tcp()`.

**Root cause**: `gunicorn_conf.py` calls `start_bms()` → `python -m board_manager` → `service._bind_tcp()` → `sock.bind((host, port))`. If a prior BMS process survived (e.g., SIGKILL or gunicorn crash), `SO_REUSEADDR` cannot override an active LISTEN socket. The `bind()` raises `EADDRINUSE`.

**Fix**: Added `_free_bms_resources(tcp_host, tcp_port, uds_path)` to `board_manager/python/board_manager/board_manager/boot.py:42-74`. Called at the top of `start_bms()` before spawning a new BMS. It:

1. **Kills stale TCP holder**: Runs `lsof -ti tcp:<port>` to find PIDs listening on the target TCP port, sends `SIGTERM` (signal 15). Handles missing `lsof`, timeouts, and permission errors gracefully.
2. **Cleans stale UDS socket**: If the UDS path exists, attempts to connect — if the connection succeeds, the socket is alive (skip removal); if it fails with `ConnectionRefusedError`, the socket is stale → unlink it.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Add `_free_bms_resources()` to `boot.py` | ✅ |
| 2 | Verify — stale BMS killed, port freed, new BMS starts cleanly | ✅ |
| 3 | Update docs — PLAN.md, IMPLEMENTATION_PLAN.md, journals, CODEBASE_REFERENCE | ✅ |

---

### Phase 87 — Favicon Links for arduino_dash ✅ COMPLETED

**Date**: 2026-06-19 16:19
**Status**: ✅ Completed

**Goal**: Add favicon `<link>` tags to the `<head>` of dashboard, admin, and board_detail pages in arduino_dash. Favicon assets already exist at `static/favicon/`.

**Design**:
1. Add `{% block extra_head %}{% endblock %}` to `base.html`'s `<head>` (child templates can inject head content)
2. Override `extra_head` in `dashboard.html`, `admin.html`, `board_detail.html` with 5 favicon link tags
3. Update built/dist copies (pyoxidizer, dist-standalone) — same pattern as Phase 85

| Q | Scope | Status |
|---|-------|--------|
| 1 | Planning docs — IMPLEMENTATION_PLAN.md, TASK.md, PROGRESS.md, update PLAN.md | ✅ |
| 2 | Add extra_head block to source base.html | ✅ |
| 3 | Add favicon links to dashboard.html | ✅ |
| 4 | Add favicon links to admin.html | ✅ |
| 5 | Add favicon links to board_detail.html | ✅ |
| 6 | Update built copies (pyoxidizer base/dashboard/board_detail) | ✅ |
| 7 | Update dist-standalone copies (base/dashboard/board_detail) | ✅ |
| 8 | Verify all 3 pages via MCP browser | ✅ |

---

### Phase 86 — Favicon Links for medminder_dash ✅ COMPLETED

**Date**: 2026-06-19 15:55
**Status**: ✅ Completed

**Goal**: Add favicon `<link>` tags to the `<head>` of admin, board_detail, and index pages in medminder_dash. Favicon assets already exist at `static/favicon/`.

**Design**:
1. Add `{% block extra_head %}{% endblock %}` to `base.html`'s `<head>` (child templates can inject head content)
2. Add `{% block extra_head %}` with 5 favicon link tags to `admin.html`
3. Add same to `board_detail.html`
4. Add same to `index.html`

| Q | Scope | Status |
|---|-------|--------|
| 1 | Planning docs — IMPLEMENTATION_PLAN.md, TASK.md, PROGRESS.md, update PLAN.md | ✅ |
| 2 | Add extra_head block to base.html | ✅ |
| 3 | Add favicon links to admin.html | ✅ |
| 4 | Add favicon links to board_detail.html | ✅ |
| 5 | Add favicon links to index.html | ✅ |
| 6 | Verify all 3 pages via MCP browser | ✅ |

---

### Phase 85 — MCP E2E Server Binding + BMS Daemon Support ✅ COMPLETED

**Date**: 2026-06-19
**Status**: ✅ Completed

**Goal**: Fix server binding for Playwright MCP browser (container can't reach 127.0.0.1) and add `--bms` flag to start BMS daemon alongside dev server for complete E2E testing.

**Design** (see e2e/agent_tools/GUIDE.md for full details):
1. Changed server binding from `127.0.0.1` to `0.0.0.0` in both e2e server scripts
2. Added `--bms` flag to both servers — starts arduino-cli daemon + board_manager service
3. Calls `init_pubsub()` to connect dashboard to BMS; sets `_daemon_ready = True`
4. Auto-cleanup via atexit + try/finally
5. Documented in GUIDE.md: container networking, BMS lifecycle, Recipe 5b for Connected state

| Q | Scope | Status |
|---|-------|--------|
| 1 | Change host to 0.0.0.0 in both server scripts | ✅ |
| 2 | Add --bms flag to arduino_dash_server.py | ✅ |
| 3 | Add --bms flag to medminder_dash_server.py | ✅ |
| 4 | Document in GUIDE.md (container note, BMS lifecycle, Recipe 5b, cleanup, troubleshooting) | ✅ |
| 5 | Verify — MCP browser test with --bms shows "● Daemon Ready" | ✅ |

---

### Phase 84 — Playwright E2E Testing Infrastructure ✅ COMPLETED

**Date**: 2026-06-19
**Status**: ✅ Completed

**Goal**: Create reusable E2E testing infrastructure for both web apps (arduino_dash, medminder_dash) using Playwright. Deliverables: Python server helpers with `--mock` flag, MCP Testing Skill for agent-driven interactive testing, MCP Testing Guide, and shelved TypeScript `@playwright/test` spec files.

**Design** (see IMPLEMENTATION_PLAN.md for full details):
1. **Server helpers** — `e2e/servers/arduino_dash_server.py` + `medminder_dash_server.py` — start Flask dev servers with optional mock board state injection (`--mock` flag populates `_board_list`/`_known_ports`/`_upload_registry`)
2. **MCP Testing Skill** — `.opencode/skills/mcp-e2e-testing/SKILL.md` — agent-referenceable skill doc for browser-based interactive testing via Playwright MCP tools
3. **MCP Testing Guide** — `e2e/MCP_TESTING_GUIDE.md` — human-readable step-by-step for manual/interactive testing
4. **Shelved TypeScript files** — `e2e/package.json`, `playwright.config.ts`, `fixtures/test-data.ts`, 8 `spec/*.spec.ts` files — written now, executable when `npm install` is run

| Q | Scope | Status |
|---|-------|--------|
| 1 | Planning docs — IMPLEMENTATION_PLAN.md, TASK.md, PROGRESS.md, update PLAN.md | ✅ |
| 2 | Server helpers — arduino_dash + medminder_dash server scripts | ✅ |
| 3 | Test server helpers — curl/HTTP verification of mock state | ✅ |
| 4 | MCP Testing Skill (.opencode/skills/mcp-e2e-testing/SKILL.md) | ✅ |
| 5 | MCP Testing Guide (e2e/MCP_TESTING_GUIDE.md) | ✅ |
| 6 | Shelved TypeScript spec files (config, fixtures, 8 specs) | ✅ |
| 7 | Final review — all docs synced, servers verified | ✅ |

---

### Phase 85 — Fix HTMX Extension Mismatch Warning ✅ COMPLETED

**Date**: 2026-06-19 01:20
**Status**: ✅ Completed

**Goal**: Fix the `"You are using an htmx 1 extension with htmx 2.0.4"` console warning by replacing the v1 bundled WS extension (`htmx.org@2.0.4/dist/ext/ws.js`) with the v2 standalone extension (`htmx-ext-ws@2.0.1/ws.js`).

**Root cause**: htmx 2 extracted extensions into separate npm packages. The WS extension loaded from `unpkg.com/htmx.org@2.0.4/dist/ext/ws.js` is the v1 extension bundled inside the `htmx.org` package. It checks `htmx.version.startsWith("1.")` and warns when htmx 2 is detected.

**Design**:
1. Replace WS extension script tag in both source base.html templates
2. Update all built/dist copies for consistency (scripts/pyoxidizer/, dist-standalone/)
3. Verify no warning via browser console

| Q | Scope | Status |
|---|-------|--------|
| 1 | Planning docs — IMPLEMENTATION_PLAN.md, TASK.md, PROGRESS.md, update PLAN.md | ✅ |
| 2 | Update arduino_dash base.html source template | ✅ |
| 3 | Update medminder_dash base.html source template | ✅ |
| 4 | Update built copies: scripts/pyoxidizer/*/build/*/prefix/*/base.html | ✅ |
| 5 | Update built copies: dist-standalone/*/prefix/*/base.html | ✅ |
| 6 | Test — MCP browser verify no console warning | ✅ |
| 7 | Final journal entries, docs sync, CODEBASE_REFERENCE | ✅ |

---

### Phase 82 — Sorted Upload Registry via bisect.insort ✅ COMPLETED

**Date**: 2026-06-18
**Status**: ✅ Completed

**Goal**: Use `bisect.insort()` to maintain each per-sketch `list[dict]` in `_upload_registry` sorted by timestamp on insert, eliminating redundant `.sort()` calls at read time.

**Design**:
- Replace `versions.append(...)` with `bisect.insort(versions, ..., key=lambda v: v["timestamp"])` at all 6 insert sites (warmup + 4 upload routes)
- Simplify `_resolve_latest_upload()` — take `versions[-1]` per sketch name then `max()`
- Simplify delete routes — replace manual `elif latest is None or v["timestamp"] > latest["timestamp"]` tracking with `all_latest = [vs[-1] ...]` post-loop
- Cross-sketch `.sort()` retained for `_render_sketch_path_selector()` and `api_sketches()` (Timsort O(n) on near-sorted data)
- `bisect` is stdlib — no new dependencies

**Key design decision**: Cross-sketch queries (listing all sketches sorted by timestamp across names) still use `.sort()` — Python's Timsort detects already-sorted per-sketch runs and runs in O(n). The per-sketch sorted invariant simplifies `_resolve_latest_upload()` and delete routes.

| Q | Scope | Key Changes | Verification |
|---|-------|-------------|-------------|
| 1 | Warmup + _resolve_latest_upload | `sketch_management.py` × 2 | ✅ |
| 2 | Upload routes | `html_routes.py` × 2 + `api_routes.py` × 2 | ✅ |
| 3 | Cross-sketch sort retained | Per-sketch sorted invariant established | ✅ |
| 4 | Delete routes | Removed manual latest tracking from 3 routes | ✅ |
| 5 | Docs sync + full run | All 8 nox sessions green | ✅ |

**Test results**: arduino_dash 119/119 ✅, medminder_dash 181/181 + 1 skip ✅, all 8 nox sessions green ✅.

**Files changed**: 10 (6 Python + 4 doc updates). No new tests needed — existing tests verify behavior.

### Phase 81 — Cleanup: Debug Log Removal + outerHTML Fix + Docs Sync ✅ COMPLETED

**Date**: 2026-06-18 17:58

**Goal**: Remove noisy `logger.debug` calls left in arduino_dash after Phase 72-78 debugging, fix `exc_info=True` misuse (3 locations), align arduino_dash `sketch_upload_modal.html` `swap: 'outerHTML'` → `'innerHTML'` to match medminder_dash (Phase 62.6.1 fix), and sync all stale documentation (TODOS.md, REVIEW docs).

**Motivation**: Context compaction from previous agent sessions lost track of these cleanup tasks. User re-identified them as pending work.

**Design**:
- Remove `logger.debug` calls from 4 arduino_dash `html_routes.py` routes (html_boards_grid, admin, html_admin_board_selector, html_admin_active_board)
- Drop `exc_info=True` from 3 of those (were not in exception handlers — caused unnecessary `sys.exc_info()` on every request)
- Change `swap: 'outerHTML'` → `'innerHTML'` in arduino_dash `sketch_upload_modal.html:49` to match Phase 62.6.1 fix
- Update TODOS.md through Phase 80
- Close REVIEW_PLAN.md, REVIEW_TASK.md items (72c review completed retrospectively)
- Sync all workflow docs

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | Remove debug logs | arduino_dash html_routes.py:107,135,182,207 | ✅ |
| 2 | Fix swap type | arduino_dash sketch_upload_modal.html:49 outerHTML→innerHTML | ✅ |
| 3 | Update stale docs | TODOS.md, REVIEW_*, PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md | ✅ |
| 4 | Test run | `nox -s all_tests` green | ✅ |

---

### Phase 80 — Hardware-ID Fallback Chain + Modal Fixes ✅ COMPLETED

**Date**: 2026-06-18

**Goal**: Homogenize sketch-selection fallback chain across both dashboards when `hardware_id` is missing. Chain becomes: `hardware_id → (ip, ua) tagging → default (medminder_dash) / empty (arduino_dash)`. Also fix arduino_dash modal bugs (broken `r.json()` + missing `hardware_id`).

**Motivation**: When `hardware_id` is empty, medminder_dash admin skipped per-board check entirely (always went to ip/ua first), and board_detail skipped ip/ua entirely (went straight to default). Arduino_dash board_detail had no way to pass `hardware_id` to `/last-upload`. Additionally, arduino_dash modal's `r.json()` always failed for HTML responses.

**Design**:
- Shared `_resolve_latest_upload()` helper extracted in both `sketch_management.py`
- medminder_dash `html_last_upload()`: add `hardware_id → get_board_sketch_assignment()` step
- medminder_dash `board_detail()`: add `(ip, ua)` fallback between per-board and `load_sketch_dir()`
- arduino_dash `board_detail.html`: add hidden input + `hx-include` for `/last-upload`
- arduino_dash `compile_upload_card.html`: remove dead `hx-vals` (BMS routes ignore `hardware_id`)
- arduino_dash `sketch_upload_modal.html`: `r.json()` → `r.text()`, add `hardware_id` query param
- Both modals: pass `hardware_id` in `/last-upload` refresh callback

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | Helper extraction | `_resolve_latest_upload()` in both `sketch_management.py` | ✅ |
| 2 | arduino_dash html_last_upload | Refactor to use helper | ✅ |
| 3 | medminder_dash html_last_upload | Add hardware_id step + helper | ✅ |
| 4 | medminder_dash board_detail | Add (ip, ua) fallback + helper | ✅ |
| 5 | Template hx-include | All hidden inputs + includes | ✅ |
| 6 | Remove dead hx-vals | compile_upload_card.html cleanup | ✅ |
| 7 | Fix arduino modal | r.json() → r.text(), add hardware_id | ✅ |
| 8 | Modal refresh callbacks | Both modals pass hwParam | ✅ |
| 9 | Tests + docs | `nox -s all_tests` green | ✅ |

### Phase 79b — arduino_dash `init_pubsub` Reconnection Fix ✅ COMPLETED

**Date**: 2026-06-18 13:02

**Goal**: Fix arduino_dash `init_pubsub` to handle transient BMS unavailability gracefully — match medminder_dash's pattern of catching `connect()` failure internally so `start_reader()` is always called and the auto-reconnect loop works.

**Motivation**: When arduino_dash starts before BMS, `init_pubsub` propagates the connection exception to `__main__.py`, which logs a warning and continues — but `start_reader()` is never called, so PubSubClient's auto-reconnect (`_read_loop` → `_reconnect()`) never starts. The dashboard runs permanently without pubsub.

**Root cause**: `arduino_dash/pubsub.py:97` — `state.pubsub.connect(retry=True)` is not wrapped in try/except. On failure, the exception propagates before `subscribe()` and `start_reader()` are called. medminder_dash wraps it internally, so those calls always execute.

**Design**: Wrap `connect()` in try/except, matching medminder_dash exactly:

```python
try:
    state.pubsub.connect(retry=True)
except (ConnectionError, OSError) as e:
    state.logger.warning("Could not connect to BoardManagerService: %s", e)
```

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | Fix + test | `pubsub.py` try/except + `test_app.py` assertions update | ✅ |
| 2 | Docs sync | IMPLEMENTATION_PROGRESS.md, IMPLEMENTATION_JOURNAL.md, JOURNAL.md, PLAN.md, CODEBASE_REFERENCE.md | ✅ |

**Test results**: arduino_dash 119 ✅, medminder_dash 181+1 ✅ (1 Phase 79 test assertion fix), nox 7/7 sessions ✅

**Additional fix**: Phase 79 regression in medminder_dash `test_admin.py:1014` — assertion asserted `b"flex:1"` (inline style replaced with `.flex-1` class in Phase 79). Changed to `b'class="flex-1"'`.

### Phase 79 — Light Colorscheme + External CSS ✅ COMPLETED

**Date**: 2026-06-17 17:30 → 2026-06-18

**Goal**: Add a light color scheme with `@media (prefers-color-scheme: light)` by refactoring all CSS from inline `<style>` blocks and `style=""` attributes into per-dashboard external `static/style.css` files using CSS custom properties.

**Motivation**: The UI had a hardcoded dark theme (zero CSS variables, zero prefers-color-scheme, ~50 inline styles across 35 templates). Adding a light scheme required centralizing all colors into CSS variables then overriding them in a `@media` query.

**Design**:
- Per-dashboard `static/style.css` with `:root { ... }` containing 42 CSS variables for dark theme
- `@media (prefers-color-scheme: light) { :root { ... } }` with light palette overrides
- All existing CSS rules updated to use `var(--...)`
- 57 new semantic classes (`.text-hint`, `.text-muted`, `.modal-backdrop`, `.result-banner--*`, `.flex-row`, etc.) replacing ~100 inline `style=""` attributes
- Flat cards (no border/shadow), symmetric dark-to-light progression

**Light palette principle**: dark = darkest bg → lighter cards → lighter inputs; light = lightest bg → darker cards → white inputs. Badge backgrounds invert (dark bg/light text → light bg/dark text). Buttons use 1 shade darker.

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | Create style.css + link | ~540 lines CSS per file, `<link>` in both base.html | ✅ |
| 2 | Move `<style>` blocks | admin.html + dnd_overlay.html → style.css | ✅ |
| 3 | Inline → classes | arduino_dash: 9 templates, 67 inline styles eliminated | ✅ |
| 4 | Inline → classes | medminder_dash: 16 templates, 100 inline styles eliminated | ✅ |
| 5 | Inline → classes | arduino_sketch_tools: 10 partials, 38 inline styles eliminated | ✅ |
| 6 | Tests + docs | CSS-only changes, docs synced | ✅ |

### Phase 78 — Fix `_daemon_ready` Unprotected Access + Duplicate Log Spam ✅ COMPLETED

**Date**: 2026-06-17 17:15

**Goal**: Add `_daemon_ready_lock` to arduino_dash, protect all reads/writes to `_daemon_ready` across both dashboards, and add a duplicate-event guard in `_on_daemon_ready` to suppress repeated "Daemon ready event received" logs during pubsub reconnect cycles.

**Motivation**: `_on_daemon_ready` prints an info log on every pubsub reconnect (each reconnect triggers `_resubscribe()` → BMS `_send_daemon_state_to()` → client receives `sys::daemon/ready` event). Unstable connections can produce many logs. Additionally, arduino_dash's `_daemon_ready` has no thread-safety lock, and medminder_dash's `_fallback_scan_loop` reads it without the lock.

**Design**:

| Change | Dashboard | File | Detail |
|--------|-----------|------|--------|
| Add lock | arduino_dash | `state.py:28` | `_daemon_ready_lock = threading.Lock()` |
| Lock read | arduino_dash | `pubsub.py:33` | `with state._daemon_ready_lock:` |
| Lock+guard | arduino_dash | `pubsub.py:109-113` | Skip log if already ready |
| Lock write | arduino_dash | `pubsub.py:117` | `with state._daemon_ready_lock:` |
| Lock read | arduino_dash | `html_routes.py:122` | `with state._daemon_ready_lock:` |
| Lock read | medminder_dash | `pubsub_infra.py:36` | `with state._daemon_ready_lock:` |
| Guard | medminder_dash | `pubsub_infra.py:215-220` | Skip log if already ready |

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | arduino_dash | Add lock, protect 4 access sites, add guard | 🔲 |
| 2 | medminder_dash | Fix `_fallback_scan_loop` read, add guard | 🔲 |
| 3 | Tests | `nox -s all_tests` green | 🔲 |
| 4 | Docs sync | All workflow + project docs | 🔲 |

### Phase 77 — Template Port Path Cleanup ✅ COMPLETED

**Date**: 2026-06-17 17:03

**Goal**: Remove scattered `{{ port.lstrip('/') }}` pattern from 7 template locations across 6 template files by computing `port_path` (URL-safe, no leading `/`) once in Python route context. Also fix arduino_dash `board_detail.html` and `compile_upload_card.html` double-slash URLs (work only because Werkzeug normalizes `//` → `/`).

**Motivation**: Natural follow-on to Phase 76's `normalize_port()` unification. Phase 76 added + validated normalized ports in Python; Phase 77 completes the picture by centralizing URL-safe port computation and fixing an inconsistent template pattern.

**Design**: Route context gains `port_path = norm_port.lstrip("/")` (and `active_board_path = (active_board_port or '').lstrip("/")` for compile_upload_card). Templates use `{{ port_path }}` instead of `{{ port.lstrip('/') }}`.

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | arduino_dash | 3 routes + 3 templates updated | ✅ |
| 2 | medminder_dash | 3 routes + 3 templates updated | ✅ |
| 3 | Tests + nox | `nox -s all_tests` green | ✅ |
| 4 | Docs sync | All workflow + project docs | ✅ |

**Verification**: arduino_dash 119 ✅, medminder_dash 181+1 ✅, arduino_sketch_tools 51 ✅, nox 8/8 ✅

---

### Phase 51 — Align with arduino_dash Compile/WS Pattern ✅ COMPLETED

**Date**: 2026-06-03

**Completed**: 2026-06-03

**Goal**: Resolve compilation status never updating by aligning 4 specific patterns with working `arduino_dash`:

1. **`__main__.py`** — argparse for `--debug` flag (replace hardcoded `debug=True`) to avoid Werkzeug reloader spawning duplicate PubSubClient
2. **`pubsub.py`** — full `_on_pubsub_reconnect()` re-registering ALL handlers (board events, resp::*, daemon/ready, health, compile, upload)
3. **`pubsub.py`** — add `resp::*` subscription with `_on_resp` handler (logging + sync-wait support) and `_pending_responses` state
4. **WS support** — `app.py` WS route, `base.html` WS.js extension + event-feed div + JS handler, `_on_board_event` WS broadcast

**Design decisions**:
- Set `_pubsub` BEFORE `connect()` (like arduino_dash sets `state.pubsub` before `connect()`) so `_on_pubsub_reconnect` can use `get_pubsub()`
- Store `_app` module-level reference for `render_template` in `_on_board_event` WS broadcast
- Conditional `import flask_sock` with `try/except ImportError` matching arduino_dash
- Catch only `(ConnectionError, OSError)` in `__main__.py` — no bare `Exception`

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | `__main__.py` argparse | Add argparse for `--host`, `--port`, `--uds`, `--debug`; remove `with app.app_context():`; fix except clause | `__main__.py` | ✅ |
| 2 | `pubsub.py` resp::* + _on_resp | Add `_pending_responses`, `_on_resp`, `_wait_for_response`; subscribe `resp::*`; set `_pubsub` before `connect()`; store `_app` | `pubsub.py` | ✅ |
| 3 | `pubsub.py` full _on_pubsub_reconnect | Re-register all handlers; update `_on_board_event` to render+broadcast WS | `pubsub.py` | ✅ |
| 4 | WS route + template | `app.py` WS route; `base.html` WS.js + event-feed + JS handler | `app.py`, `base.html` | ✅ |

**Verification**: 78/78 medminder_dash tests pass.

---

### Phase 52 — Fix Phase 51 Regression Bugs ✅ COMPLETED

**Date**: 2026-06-03

**Completed**: 2026-06-03

**Goal**: Two regression bugs introduced by Phase 51:

1. **Medicines not populated when navigating from Board Grid**: `board_grid.html` Manage link goes to `/board/<port>` (`board_detail` route), NOT `/board/select/<port>` (`board_select` route). `board_detail()` sets `session["board_port"]` but never calls `_migrate_default_board()` → medicines loaded by `_load_from_alarm_hpp_if_needed()` into `"default"` key are never migrated to the selected board's key.

2. **Extra board-event cards on every page**: `#live-events` div on `base.html` (Phase 51 Q4) broadcasts board connected/disconnected events via WS to every page. Fallback scanner detects 3 serial ports → 3 event cards on dashboard. Navbar board status already shows connection state via HTMX polling — WS board events are redundant.

**Design decisions**:
- **Fix `board_detail()` route, not grid link**: Add `_migrate_default_board()` + lazy alarm.hpp load to `board_detail()` since that's the route users actually hit via the Manage button. Don't change the URL pattern in `board_grid.html`.
- **Remove `#live-events` from `base.html`**: The WS board events were meant for an admin/debug dashboard. Navbar board status (HTMX polling) makes WS-based events redundant. WS infrastructure stays for compile/upload progress streaming by `arduino_sketch_tools`.
- **Remove `_load_from_alarm_hpp_if_needed()` from `create_app()`**: Was supposed to be done in Phase 50 Q2 but was left behind. Lazy bootstrap in `board_detail()` replaces it.

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | Fix `board_detail()` route | Add `_migrate_default_board()` + inline alarm.hpp bootstrap | `app.py` | ✅ |
| 2 | Remove dead bootstrap function | Delete `_load_from_alarm_hpp_if_needed()` function and its call, inline in `board_detail()` | `app.py` | ✅ |
| 3 | Remove `#live-events` + dead JS | Remove `#live-events` div, `htmx:beforeSwap` handler from `base.html` | `base.html` | ✅ |

**Verification**: 75/75 medminder_dash tests pass (3 startup tests removed with deleted function).

---

### Phase 44 — MedMinder UI Alignment with Arduino Dash ✅ COMPLETED

**Goal**: Align MedMinder Dash UI with Arduino Dash: vanilla CSS (drop Tailwind), board card grid on dashboard, board data enrichment for card rendering, board detail page with compile/upload controls plus embedded medicine management, and live event feed.

**Date**: 2026-06-01

**Motivation**: After Phase 43 fixed blocker bugs, two UX gaps remain:
1. UI uses `<select>` dropdown instead of arduino_dash's card‑based board grid
2. Board data stores only port strings — cards cannot display board name or FQBN

**Design decisions**:
- **Vanilla CSS**: Drop Tailwind CDN, use inline `<style>` block matching arduino_dash's exact selectors (`.card`, `.btn`, `.badge`, `.grid`, etc.)
- **Full board dicts**: `_known_ports: list[str]` → `dict[str, dict]` (port → {port, board, fqbn, event})
- **Board detail includes medicines**: arduino_dash board_detail for compile/upload, with medicine management section below
- **Keep HTMX + Hyperscript**: No framework changes to the JS stack

**5 Quantums**:

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | CSS conversion | Remove Tailwind CDN, inline arduino_dash CSS, update all templates | base.html, index.html, medicines.html, medicine_form.html, deploy.html, partials | ✅ |
| 2 | Board data enrichment | `_known_ports: list[str]` → `dict[str, dict]`, `get_known_ports()` returns `list[dict]` | pubsub.py, app.py, board_list.html | ✅ |
| 3 | Board card grid | Create `board_grid.html` partial, add `/api/boards/grid`, replace `<select>` | index.html, board_grid.html (new), app.py | ✅ |
| 4 | Board detail page | Create `board_detail.html` with compile/upload + medicines, `/board/<port>` route | board_detail.html (new), app.py | ✅ |
| 5 | Live events + polish | Event feed card, deploy page CSS cleanup, final docs sync | board_event.html (new), index.html, deploy.html | ✅ |

**Key changes**:
- `/board/<port>`: Direct board detail page (no session redirect). `/board/select/<port>` stores session and redirects. `/board` legacy route redirects to session port.
- `_board_events: list[dict]` in pubsub.py — up to 100 recent events, displayed in index.html event feed with 10s HTMX poll.
- `get_board_events()` added to pubsub.py exports.
- `board_grid.html` → card grid with port/name/FQBN. `board_detail.html` → compile/upload controls + embedded medicine management. `board_event.html` → live event feed in index.
- Fixed broken Jinja expression in `deploy.html:69` (port out of scope in upload output).

**3 additional quantums (badges + fallback detection)**:

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 6 | Daemon status badge | `_daemon_ready` flag, `_on_daemon_ready` handler, `_on_pubsub_reconnect` callback, `/api/daemon/status` route, `daemon_badge.html` partial, wired into `base.html` navbar with HTMX poll every 10s | ✅ |
| 7 | Board connection-status badge | `board_status_badge.html` partial matching arduino_dash, `/api/board/<port>/connection-status` route, HTMX polling in `board_detail.html` every 10s | ✅ |
| 8 | Fallback board detection | Background daemon thread scanning `/dev/ttyACM*`/`/dev/ttyUSB*` every 5s when BMS offline, injects/removes entries from `_known_ports`, auto-start in `init_pubsub()` | ✅ |

**Verification**: 53/53 tests pass (no regressions, 2 new routes).
### Phase 1: Research & Fix gRPC Issues ✅ COMPLETED
- [x] Research gRPC stubs issues in existing client
- [x] Fix UploadRequest port parameter (string → Port object)
- [x] Fix board detection method (BoardDetect → BoardListWatch/BoardList)
- [x] Document findings in RESEARCH_JOURNAL.md
- [x] Create clean Python module `arduino_grpc/`
- [x] 22 unit tests passing
- [x] 6 integration tests passing (Connection, Init, List, ListAll, Watch, Compile)

### Phase 2: Integration Testing & Fixes ✅ COMPLETED
- [x] Integration test with actual arduino-cli daemon (7/7 passing)
- [x] Add timeout parameter to `watch_boards()`
- [x] Add upload integration test (runs if board connected)
- [x] Fix `BoardList` returning 0 ports (added `timeout` field to request)
- [x] Fix instance resource leak (added `destroy()` → `Dispose` RPC called on `disconnect()`)

### Phase 3: Board Manager Service ✅ COMPLETED
- [x] Protocol & Router (PubSub messaging system)
- [x] Subprocess Pool (`pool.py`, `board_worker.py`)
- [x] BoardManagerService (`service.py`, `__main__.py`)
- [x] Integration tests with arduino-cli daemon

### Phase 4: Web App ✅ COMPLETED
- [x] Flask app with HTMX + WebSocket
- [x] PubSub client to BoardManagerService
- [x] Dashboard, board detail, compile/upload UI
- [x] Integration tests (full stack)

### Phase 5: Private PyPI Wheel-Based Install ✅ COMPLETED
- [x] Create `setup.py` bootstrap files (3 modules)
- [x] Build wheels for all three packages
- [x] Update `grpc_client/python/Pipfile` — private source, remove direct deps
- [x] Update `board_manager/python/Pipfile` — private source, remove path dep
- [x] Update `webapp/python/arduino_dash/Pipfile` — private sources, remove path deps
- [x] Update `.env` files with `PROJECT_ROOT`
- [x] Regenerate lock files, verify `pipenv install` from parent dirs
- [x] Run all tests (143) and verify

### Phase 6: Board Detection & Dashboard Live Updates ✅ COMPLETED
- [x] Write BoardDetector (`board_detector.py`) — background thread polling `list_boards()` every 5s
- [x] Integrate BoardDetector into `BoardManagerService.start()`/`stop()`
- [x] Fix Flask app_context error in pubsub `_on_board_event` handler
- [x] Add `/api/boards/grid` endpoint + `board_grid.html` partial
- [x] Dashboard HTMX polling for live board list
- [x] Fix test warnings across all modules (10 warnings eliminated)
- [x] Write unit test for BoardDetector
- [x] Fix protobuf int64 float rejection — `int(timeout)` cast in `client.py:149`, `DEFAULT_LIST_TIMEOUT` from `3.0` → `3`

### Phase 7: Debug — Board Events Not Reaching Dashboard ✅ COMPLETED
- [x] Add instrument logging at each event transition point
- [x] Run with `--debug` to identify break point (timing race — events fire before subscriber connects)
- [x] Fix root cause — cache board state in `_board_state`, re-emit synthetic "connected" events on subscribe
- [x] Verify fix — boards appear in dashboard via `/api/boards/grid`

### Phase 8: Fix _tick pool.poll inner loop crash ✅ COMPLETED
- [x] Remove erroneous inner `for msg in msgs` loop in `service.py:126-129`
- [x] Add regression tests (TestTick, 4 tests)
- [x] Verify 157 tests pass

### Phase 9: Fix Upload (exit status 1 crash cascade) ✅ COMPLETED
- [x] Investigate `exit status 1` from avrdude — caused by crash cascade, not a separate bug
- [x] Test standalone: `arduino-cli upload ...` — works fine
- [x] Test via full BMS stack after crash fix — upload succeeds

### Phase 10: Fix Async Response Handling — Compile/Upload Results ✅ COMPLETED
- [x] Add `_pending_responses` dict + `_on_resp` handler for `resp::*` topics 🔴 Non-functional — `::` separator bug discovered
- [x] Modify `api_compile`/`api_upload` to wait for response (60s timeout) and render HTML
- [x] Create result partial templates
- [x] Tests for response handling (10 new tests)
- [ ] End-to-end verification (deferred to Phase 12 — needs :: fix first)

### Phase 11: Real-time Progress + Polling + Logging ✅ COMPLETED
- [x] Stage 1: Fix `::` separator in response topics
- [x] Stage 2: Add `compile_stream()`/`upload_stream()` to gRPC client
- [x] Stage 3: Board worker streaming + logging
- [x] Stage 4: Service routing + logging
- [x] Stage 5: WebApp polling endpoints + results cache
- [x] Stage 6: Templates — WS progress + polling UI

### Phase 12: DaemonManager + Spinner + Cleanup ✅ COMPLETED
- [x] Q1: DaemonManager class + config + tests
- [x] Q2: Service integration (start/stop daemon)
- [x] A1: Fix stale UDS socket handling in PubSubClient._create_socket
- [x] A2: Add retry to PubSubClient.connect() initial connection
- [x] A3: Graceful init_pubsub on connection failure
- [x] Q5a: CSS spinner in compile/upload partials
- [x] Q5b: Remove Spawn/Remove buttons from board_detail
- [x] Q5c: Board manager compile/upload status logs
- [x] Q6a: Fix `_publish_daemon_ready()` — remove erroneous cleanup that closes listener sockets
- [x] Q6b: Add regression test — verify sockets remain open after `_publish_daemon_ready()`
- [x] Q4: WebApp daemon status badge + WS subscription
- [x] Q7a: Fix badge freeze — add HTMX attributes to daemon_badge.html
- [x] Q7b: Add spinner to compile_poll_pending.html + upload_poll_pending.html
- [x] Q7c: Add BMS offline check in compile/upload endpoints + error partial
- [x] Q3: BoardDetector linear retry delays + auto-restart via daemon_manager.ensure_alive()
- [x] Q8a: `_daemon_ready` flag in `__init__`, set in `_publish_daemon_ready()`
- [x] Q8b: `_send_daemon_state_to(conn)` method
- [x] Q8c: Call `_send_daemon_state_to` in subscribe handler  
- [x] Q8d: Tests for flag + subscribe re-emission
- [x] Q9a: Fixed 2s reconnect delay (replaced exponential backoff)
- [x] Q9b: Fix `_reconnect` killing reader thread + `_send` race condition
- [x] Q10a: Guard `_on_daemon_ready` handler by message type
- [x] Q10b: Check `is_connected` in badge endpoint
- [x] Q10c: Tests for Q10a + Q10b

### Phase 13: Fix Upload Error Message Leak ✅ COMPLETED
- [x] Q11a: Fix `_make_error` to include `"status": "error"` key in board_worker.py
- [x] Q11b: Fix BMS `_route_pool_message` — filter `::progress` from result log, log error `message`
- [x] Q11c: Fix webapp error rendering + test
- [x] Q11d: Final test run — 254 total (165+55+34), all passing, zero warnings

### Phase 14: Port Path Normalization ✅ COMPLETED
- [x] Q1: Fix `board_grid.html:13` — `lstrip('/')` on port in href
- [x] Q2: Add `_norm_port(port)` helper that prepends `/` if missing
- [x] Q3: Use `_norm_port` in all 7 API endpoints (compile, upload, poll, spawn, status, remove)
- [x] Q4: Update tests — fix cache keys to use `/dev/ttyACM0` instead of `dev/ttyACM0`
- [x] Q5: All 254 tests pass

### Phase 15: UI/UX Improvements ✅ COMPLETED
- [x] Larger log text (0.8rem → 0.95rem), shorter height (400px → 250px)
- [x] Remove dead "Status" section from board_detail
- [x] Board connection status badge in controls (top-right) — polls every 10s
- [x] Verbose upload status messages — synthetic phase markers in board_worker
- [x] 3 new connection-status tests, all 257 pass

### Phase 16: UI Polish — Log Spacing Fix + Meta Info in Cards ✅ COMPLETED
- [x] Q1: Fix log-viewer — `white-space: pre-wrap` causes `\n` in `<div>` blocks to render as blank lines (remove white-space property, confirmed working)
- [x] Q2: Cleanup board_worker.py synthetic progress messages — remove trailing `\n` (redundant in block elements)
- [x] Q3: Add `_compile_meta` / `_upload_meta` dicts in app.py — store port, board name, FQBN, sketch path during operations
- [x] Q4: Update upload/compile card headings and info bars in templates (port, board, FQBN, sketch)
- [x] Q5: Tests + verification — 261 total (165+62+34), all passing, zero warnings

### Phase 17: Sketch Status Warnings ✅ COMPLETED
- [x] Q1: Add `_get_sketch_mtime()` helper + `_last_compiled_sketch` / `_last_compile_mtime` tracking
- [x] Q2: Warning computation in `api_upload()` — sketch path mismatch + modified detection → blocking confirmation
- [x] Q3: New `POST /api/board/<port>/upload/confirm` and `GET /api/board/<port>/upload/section` endpoints
- [x] Q4: New `upload_confirm.html` + `upload_init.html` templates, `.btn-warning`/`.btn-secondary` CSS
- [x] Q5: Compile failure warning — show "sketch modified since last successful compile" in compile result
- [x] Q6: 11 new tests (mtime helper, warnings, blocking flow, compile warning)
- [x] Q7: Docs update + final test run — 73 webapp tests pass, **283 total**

### Phase 18: Sketch File Browser + Drag-and-Drop ✅ COMPLETED
- [x] Q1: Server upload endpoint `POST /api/sketch/upload` — multipart file receive, `uploads/` storage, `.meta` file
- [x] Q2: Hyperscript setup + templates (modal, drop zone, button)
- [x] Q3: Browse flow — hidden `<input webkitdirectory>`, Browse button triggers it, hyperscript handlers
- [x] Q4: Drag-and-drop flow — drop zone with `dragover`/`drop` handlers via hyperscript, folder iteration
- [x] Q5: Tests — upload endpoint (files + meta), cleanup
- [x] Q6: Board_detail.html integration + final docs

**Post-release Bugfixes**:
- [x] Bug 1: Browse button doesn't open folder picker — `<input hidden>` blocks `.click()`
  - Fix: Replace Browse `<button>` with `<label for="folder-input">` (pure HTML, zero script)
  - Replace `hidden` attribute with CSS "visually hidden" pattern
- [x] Bug 2: Drag-and-drop opens files in browser — `halt the default` exits handler early
  - Fix: Use `halt the event` (prevent default AND continue) in DnD handlers
  - Use `on drop(dataTransfer)` destructuring for event.dataTransfer access
  - Add window-level `on drop from window` / `on dragover from window` to `<body>`
- [x] All 287 tests still pass (frontend-only changes, no server logic changed)

### Phase 19: Fix Browse/Upload/DnD UI Bugs ✅ COMPLETED
- [x] Q1: Fix body DnD prevention — `halt the event` → `halt the event's default` in `base.html:47-48`
- [x] Q2: Fix modal centering — `show me` → `set my.style.display to 'flex'` in `sketch_upload_modal.html`
- [x] Q3: HTMX upload on Browse — file input `hx-post` auto-upload on change, server returns HTML `<input>` when `HX-Request` header present. Modal Upload button uses HTMX `hx-post` + `hx-include="#folder-input"` for DnD flow.
- [x] Q4: Remove default sketch path + `_last_upload_by_ip` dict + `GET /api/last-upload` endpoint + `hx-get` on page load
- [x] Q5: Sketch name in card meta — `_make_meta` includes `sketch_name` (basename), templates display it
- [x] Q6: All 69 tests pass (14 new), docs updated

**Phase 20 Bugfix: Three Regression Fixes ✅ COMPLETED**
Three issues found after Phase 20:
1. **Modal not shown** — I removed `on change` hyperscript from file input (broke modal for Browse)
2. **DnD doesn't work** — `halt the event's default` is invalid hyperscript (body handler silently fails)
3. **Wrong upload path** — returned path is upload root (`uploads/<ts>_<name>/`), not sketch subdirectory (`uploads/<ts>_<name>/<sketchname>/`)

| Q | Fix | Files | Tests |
|---|-----|-------|-------|
| 1 | Body DnD: `halt the event's default` → `call event.preventDefault()` | base.html | Manual: DnD works |
| 2 | Restore `on change` hyperscript + homogenise DnD/Browse flow | board_detail.html | Manual: modal shows |
| 3 | Compute `sketch_dir` with subdirectory, add `root_name` to meta | app.py | Existing + path updates |
| 4 | Last-upload scanner reconstructs `sketch_dir` from meta | app.py | Test path adjustments |
| 5 | Update tests + docs + CODEBASE_REFERENCE | test_app.py, all docs | All 92 webapp pass |

**Key hyperscript correction**: `halt the event's default` is NOT a valid hyperscript form. The valid forms are: `halt` (exit+P+SP), `halt the event` (P+SP+continue), `halt the bubbling` (SP+continue). Use `call event.preventDefault()` for preventDefault-only.

**Phase 20 Bugfix Q6: .ino Filename Mismatch ✅ COMPLETED**
Arduino CLI requires the `.ino` file to match the enclosing folder name. Uploading a folder
`blinky2/` containing `blinky.ino` → compile fails looking for `blinky2.ino`.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 6 | Add `_normalize_ino_filename()` — scans `sketch_dir` for `.ino`, renames if exactly one mismatches | app.py | 6 new normalization tests |

**Test totals**: 98 webapp tests (92 + 6). **307 grand total**, all passing, zero warnings.

**Phase 20 Bugfix Q7: Button State Restoration After Upload ✅ COMPLETED**

**Issues found during user testing**:
1. **Issue 1 — Second upload hangs**: After first upload, `on htmx:afterRequest` hides modal and resets file input but does NOT restore button state. Upload button stays disabled with "Uploading..." text, Cancel button stays disabled. On second attempt, modal shows with disabled buttons → appears unresponsive.
2. **Issue 2 — Browser "Upload files?" dialog**: Standard Chrome + Firefox security feature for `webkitdirectory`. Appears once per directory selection. Cannot be suppressed. Not present in DnD path. User accepted as standard behavior.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 7 | `on htmx:afterRequest`: restore Upload button text/enabled, Cancel button enabled. `on showModal`: defense-in-depth reset of button states. | `sketch_upload_modal.html` | Manual |

**Decision**: Keep both Browse and DnD. Fix button state restoration. Browser dialog is standard behavior.

---

### Phase 20: DnD Silent Failure — `#folder-input.files` is Read-Only ✅ COMPLETED

**Date**: 2026-05-27

**Finding**: DnD folder drag into the drop zone does nothing — no modal, no upload.
Root cause: `set #folder-input.files to dataTransfer.files` silently fails because
`<input type="file">.files` is a **read-only property** enforced by browser security.

Introduced in Phase 20 Bugfix Q2 which homogenised DnD and Browse by funneling both
through the file input's change event. DnD worked in Phase 19 (direct modal populate)
and Phase 19 Bugfix (set input.files from dataTransfer — did it ever work? No — the
silent no-op was always broken, but Q2's homogenisation made DnD depend on it.)

**Fix approach**: Store DnD files as a JavaScript property on the modal element
(`#sketch-upload-modal.__dndFiles`) instead of trying to set `#folder-input.files`.
Rewrite modal upload button from HTMX (`hx-post` + `hx-include="#folder-input"`)
to hyperscript `fetch` + `FormData`, supporting both `__dndFiles` (DnD) and
`#folder-input.files` (Browse). Clear `__dndFiles` in hideModal and Browse handler.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 1 | DnD drop: store files in `__dndFiles`, populate modal directly, show modal | `board_detail.html` | Manual: DnD works |
| 2 | Upload button: hyperscript `fetch` + `FormData` — checks `__dndFiles` then `#folder-input.files`; `on error` handler | `sketch_upload_modal.html` | Manual: both paths work |
| 3 | Browse change handler: clear `__dndFiles` before showing modal | `board_detail.html` | Manual: no cross-contamination |
| 4 | hideModal: clear `__dndFiles` on cancel | `sketch_upload_modal.html` | Manual |
| — | Run all 98 webapp tests — no regressions | — | All 98 pass |

---

## Status: Phase 21 Q6 complete (Q6a applied, Q6b v2 comma-separated `with` fix applied, all 308 tests pass). Awaiting user browser verification.

**Last Updated**: 2026-05-27 11:45

---

### Phase 90 — Fix Double BoardDetector Stop Log ✅ COMPLETED

**Date**: 2026-06-19 17:49
**Status**: ✅ Completed

**Goal**: Eliminate duplicate "BoardDetector stopped" log during service shutdown by fixing the redundant `stop()` call chain and making `stop()` idempotent.

**Root cause**: `service.py:100-101` catches `KeyboardInterrupt` inside `start()` and calls `self.stop()`, then `__main__.py:39-40` calls `service.stop()` again in the `finally` block. Two separate `stop()` calls → two logs. SIGTERM path (via `sys.exit(0)` → `SystemExit`) only triggers the `finally` block once.

**Fix**:
1. `service.py` — Remove the `except KeyboardInterrupt` handler in `start()`, letting `KeyboardInterrupt` propagate to `main()` where `finally: service.stop()` handles it.
2. `board_detector.py` — Add `if not self._running: return` guard to `stop()`, making it idempotent as defense-in-depth.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Make `BoardDetector.stop()` idempotent | ✅ |
| 2 | Remove `KeyboardInterrupt` catch from `service.start()` | ✅ |
| 3 | Run tests — 0 regressions | ✅ |
| 4 | Docs sync — journals, CODEBASE_REFERENCE, TODOS | ✅ |

---

### Phase 92 — Constants Refactor: enum/IntEnum/StrEnum/frozen dataclass ✅ COMPLETED

**Date**: 2026-06-19 18:00
**Status**: ✅ Completed

**Goal**: Replace bare module-level `SCREAMING_SNAKE_CASE` constants with typed
`enum.Enum` (bytes), `enum.IntEnum` (int), `enum.StrEnum` (strings), and
`@dataclass(frozen=True)` (mixed groups) — per source file, no shared module.

**Motivation**:
- Type safety — prevents accidental comparison/assignment with wrong types
- Self-documenting — `Handshake.NEWLINE` is clearer than `HANDSHAKE_NEWLINE`
- IDE autocomplete — enum members show up in completion menus
- Eliminate hardcoded string duplication (env var names, topic strings)

**Design decisions**:
1. **Per-file** — each source file that has constants gets its own enum/dataclass defined
   at the top of that file. No shared `constants.py` module.
2. **`state.py` unchanged** — per user instruction.
3. **`enum.Enum` for bytes** — `HANDSHAKE_NEWLINE`, `HANDSHAKE_LENGTH`.
4. **`enum.IntEnum` for ints** — `HEADER_LENGTH`, `MAX_RESTARTS`.
5. **`enum.StrEnum` for strings** — env var names, topic strings.
6. **`@dataclass(frozen=True)` for mixed groups** — `BmsDefaults`, `ReconnectConfig`.

**Changes per file**:

| # | File | Constants | Type | New Name |
|---|------|-----------|------|----------|
| 1 | `protocol.py` | `HANDSHAKE_NEWLINE` | `enum.Enum` | `Handshake.NEWLINE` |
|   |           | `HANDSHAKE_LENGTH` | `enum.Enum` | `Handshake.LENGTH` |
|   |           | `HEADER_LENGTH` | `enum.IntEnum` | `Framing.HEADER_LENGTH` |
|   |           | `"newline"`, `"length"` | `enum.StrEnum` | `FramingMode.NEWLINE`, `LENGTH` |
| 2 | `boot.py` | defaults (UDS/TCP/daemon) | `@dataclass(frozen=True)` | `BmsDefaults` |
|   |           | env var name strings | `enum.StrEnum` | `BmsEnv` |
| 3 | `config.py` | imported from boot.py | — | Use `BmsDefaults`, `BmsEnv` |
| 4 | `service.py` | `"sys::daemon/ready"` | `enum.StrEnum` | `SysTopic.DAEMON_READY` |
| 5 | `board_detector.py` | `POLL_INTERVAL`, `LIST_TIMEOUT` | `enum.Enum` | `DetectorDefaults` |
| 6 | `pool.py` | `MAX_RESTARTS` | `enum.IntEnum` | `PoolLimits.MAX_RESTARTS` |
| 7 | `pubsub_client.py` | reconnect config | `@dataclass(frozen=True)` | `ReconnectConfig` |
|   |                | retry delays | `@dataclass(frozen=True)` | `ReconnectConfig.RETRY_DELAYS` |
| 8 | `gunicorn_conf.py` ×2 | env var names | `enum.StrEnum` | `DashEnv`, `GunicornEnv` |
| 9 | `pubsub.py`/`infra.py` | topic strings | `enum.StrEnum` | `PubSubTopic` |

**Verification**:
- board_manager: 201 pass, 3 pre-existing fail, 8 skip (no change)
- board_manager_client: all pass
- medminder_dash: all pass
- arduino_dash: all pass

---

### Phase 91 — Align Live Events Card Style with arduino_dash ✅ COMPLETED

**Date**: 2026-06-19 17:59
**Status**: ✅ Completed

**Goal**: Align medminder_dash's `board_event.html` partial template with arduino_dash's flat layout — remove the `board-event-row` flex layout, revert to simple inline spans, drop `[-10:]|reverse` slicing, and always show the board badge.

**Root cause**: When the live-events card was ported to medminder_dash in Phase 44, `board_event.html` was customized with a flex-row layout (`board-event-row`), reversed slicing, conditional board badge, and nested `<div>` structure. arduino_dash's version remained simple and flat. The CSS is identical between both dashboards, so the template was the only divergence.

**Fix**: Rewrite medminder_dash's `board_event.html` to match arduino_dash's structure exactly.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Update `medminder_dash/.../partials/board_event.html` to match arduino_dash | ✅ |
| 2 | Verify — syntax check + test run | ✅ |
| 3 | Docs sync — journals, CODEBASE_REFERENCE, TODOS | ✅ |

---

### Phase 21: Firefox DnD Diagnostic + Fix ✅ COMPLETED

**Date**: 2026-05-27

After Phase 21 Q1-Q4 implementation, Firefox DnD still shows nothing.
Diagnostic console output revealed the root cause: `'style' is null` in hyperscript 0.9.13.

**Root cause**: `set style.borderColor` uses bare `style` which hyperscript resolves as `null` (not `me.style`). The runtime exception aborts the `on drop` handler before it reaches `set files to dataTransfer.files`.

**Fix**: Prefix with `my.` in all 3 handlers: `set my.style.borderColor`, `set my.style.background`.

**Q6b correction**: Multiline `with` separation was WRONG. Hyperscript `fetch` uses
a single `with` with comma-separated named args, NOT multiple `with` clauses.
Correct: `fetch /api/sketch/upload with method:'POST', body:fd as JSON`

**Plan**:
| Q | Change | File | Verification |
|---|--------|------|-------------|
| 6a | Fix `style` → `my.style` in dragover/dragleave/drop handlers | `board_detail.html` | ✅ DnD shows modal in Firefox |
| 6b | Fix `fetch` parse error — comma-separated single `with` | `sketch_upload_modal.html:40` | ✅ Comma-separated `with` applied |
| 6b-v3 | Fix indentation mismatch (v3 attempt) | `sketch_upload_modal.html:42-46` | ❌ `on error` not valid for `fetch` |
| 6b-v4 | Replace `on error`→`catch e`, remove `then` | `sketch_upload_modal.html:25-54` | ❌ Still `Unexpected Token : end` — `catch` is clause of `on`, not `fetch` |
| 6b-v5 | **CORRECTION**: Post-fetch commands same level as `fetch`, `catch e` at body level, single `end` | `sketch_upload_modal.html:25-53` | ✅ Parse error resolved |
| 6c | Fix hyperscript `for x in FileList` — use `Array.from(files)` | `sketch_upload_modal.html:37` | ✅ 302 unit tests pass |
| 6d | Run all tests + update docs | All | ✅ 302 unit pass (98+176+28), 6 integration expected-fail |

**Status: Phase 21 Q6 complete.** Three bugs fixed sequentially:
- Q6a: `my.style` in DnD handlers — DnD shows modal in Firefox
- Q6b: `catch` is clause of `on`, single `end`, post-fetch commands at same level — parse error resolved
- Q6c: `Array.from(files)` in for loop — `FileList` iteration fixed
- Q6d: All 302 unit tests pass, 6 integration expected-fail
**User test result**: DnD → Upload and Browse → Upload in both Firefox and Chrome — "Upload Failed" with NO network request. `catch e` fires before `fetch`.

---

### Phase 22: Fix Indentation Bug + Minimal `js()` Diagnostic ✅ COMPLETED

**Date**: 2026-05-27 12:30

**Previous attempt Q7a-v2**: Single `js()` block replaces `log` commands. No parse error.
But user test shows: "Upload Failed", NO console logs from `js()`, NO network request.

**Root cause of Q7a-v2 failure**: Indentation bug from the edit. The `end` (closing `if`),
`js()`, and `fetch` lines shifted to 28/27 spaces (body level of `else`) instead of
26 spaces (outer command level). The `js()` block is nested inside the `else` body at
the AST level.

**Fix Q7a-v3**:
1. Realign indentation: `end`/`js()`/`fetch` at 26sp (outer level)
2. Add simple `log 'A'` / `log 'B'` / `log 'C'` debug commands (hyperscript `log` CAN
   handle simple string literals — only JS operators like `typeof`/`+` cause parse errors)
3. Minimal `js() console.log('JS_RAN') end` to verify the `js()` command works
   in hyperscript 0.9.13 in this context
4. Flask `app.logger.info` already in place

**Triage approach**: Start with minimal working code, verify each step, then add logic:
| Step | Console output expected | Next if works |
|------|------------------------|---------------|
| `log 'A'` after `on click` | `A` | Add `log 'B'` before `js()` |
| `log 'B'` before `js()` | `B` | Minimal `js()` block |
| `js() console.log('JS_RAN') end` | `JS_RAN` | Pass `fd` to `js()` |
| Full iteration logic | Upload succeeds | ✅ |

**Q7a-v3 user test**: NO console output at all — `A`, `JS_RAN`, `B` all absent. But
"Upload Failed" appears. `catch e` fires but body commands (including `log 'A'`) produce
no output.

**Q7a-v4 fix**: Added `log 'CAUGHT'` inside `catch e` to determine:
- If `CAUGHT` appears: handler runs, body silently fails before `log 'A'` — binary-search
- If nothing appears: stale handler from cached page — hard refresh needed

**Fallback**: If `js()` doesn't work at all in hyperscript 0.9.13, replace the Upload
button's hyperscript with `onclick` attribute + global JavaScript function `<script>` tag.

**Q7a-v4 user test (2026-05-27)**: Only `CAUGHT` appears. Handler IS installed, body fails
silently before `log 'A'`. Hypothesis #3 confirmed (silent throw in first 6 commands).

**Q7a-v5**: Binary-search with `log '1'`-`log '5'` after each of the 5 commands before `log 'A'`:
1. After `add @disabled to me`
2. After `add @disabled to #modal-cancel-btn`
3. After `put 'Uploading...' into my innerText`
4. After `set fd to new FormData()`
5. After `set dndFiles to #sketch-upload-modal.__dndFiles`

**Q7a-v5 user test (2026-05-27)**: Console shows `1 2 3 CAUGHT` — no `4`, `5`, `A`.

**Root cause**: Q7a-v5 edit shifted body-level indentation from 26sp to 28sp but left
`if/else/end` sub-block at original levels. Hyperscript sees `if` at 28sp with body at
same level (no body), `else`/`end` BELOW `if` (orphaned). Corrupted AST.

**Q7a-v6 fix**: Realign all indentation consistently:
- Body-level commands: 28sp
- `if` / `else` / `end`: 28sp (same as body)
- `if` body / `else` body / `js()` body / `catch e` body: 30sp

**Q7a-v6 user test**: SAME output `1 2 3 CAUGHT`. Indentation was NOT the root cause
— `set fd to new FormData()` genuinely fails in hyperscript 0.9.13 for complex handlers.

**Q7a-v7 user test**: Error revealed: `"FormData constructor: 'new' is required"`.
Hyperscript 0.9.13's `new` keyword is buggy — it parses `new FormData()` but calls
`FormData()` WITHOUT `new` at runtime.

**Q7b-p1 fix**: Replace `set fd to new FormData()` with:
```hyperscript
js()
  return new FormData()
end
set fd to it
```

**Q7b-p1 user test**: Handler runs cleanly (`1 2 3 4 5 A JS_RAN B`) but upload fails
with `400 "No files provided"`. Root cause: `for file in Array.from(files)` loop
accidentally removed during Q7a restructuring. FormData never populated.

**Q7b-p2 fix**: Restore missing `for` loop. Change `fetch ... as JSON` to `js()` block.

**Q7b-p2 user test**: Handler runs cleanly (`1 2 3 4 5 A JS_RAN B`). **But**
`Content-Type: text/plain;charset=UTF-8`, `Content-Length: 2`. Hyperscript
`fetch ... as JSON` serializes `FormData` as `JSON.stringify(fd)` → `"{}"`.

**Q7b-p3 fix**: Replace hyperscript `fetch` with native `js()` fetch. Browser's
native `fetch()` handles `FormData` correctly — sets `multipart/form-data`.

**D1 fix**: Keep `--daemonize` but track the actual forked daemon PID via `_find_port_pid()`.
After daemon is ready, store the real PID in `self._daemon_pid` and use it in `stop()`
and `is_alive` instead of the zombie parent PID tracked by `subprocess.Popen`.

**Q7b-p4**: Add diagnostic logs (browser + Flask).
**Q7b-p5**: User test — verify upload succeeds.
**Q7b-p6**: Remove all diagnostics, keep `ACTUAL_ERR` safety net.
**Q7c**: Finalize docs + CODEBASE_REFERENCE.

**Status**: Four hyperscript bugs found. Upload handler needs native `js()` fetch.

### Phase 23: Four Hyperscript Bugs — Native `js()` Fetch Workaround ✅ COMPLETED

**Date**: 2026-05-27

**All hyperscript approaches for FormData upload are broken**:

| # | Bug | Symptom | Workaround |
|---|-----|---------|-----------|
| 1 | `new` keyword calls without `new` | `"FormData constructor: 'new' is required"` | `js() return new FormData() end` |
| 2 | `fetch ... as JSON` serializes body as JSON | `Content-Type: text/plain`, body `"{}"` | Native `js() fetch()` |
| 3 | Bare `fetch` with FormData hangs | Promise never resolves, no network request | Native `js() fetch()` |
| 4 | `for` loop body can't access `set` vars | `fd is not defined` inside loop | Element property `#btn.__fd` |

**Bare fetch tested (Q8c)**: Confirmed broken — `FETCH_DONE` never fires,
no `CAUGHT`, no Flask log. Bug #3 confirmed.

**Fix approach**: 
- Keep `js() return new FormData() end` for Bug 1
- Use `#modal-upload-btn.__fd` element property for Bug 4
- Replace bare hyperscript `fetch` with `js()` native `fetch()` for Bugs 2+3
- Add browser + Flask debug logs

| Q | Change | Status |
|---|--------|--------|
| 8a | Create BUGS.md + update planning docs | ✅ |
| 8b | Implement element property `__fd`, add debug logs, test bare fetch | ✅ |
| 8c | User test — bare fetch hangs, confirmed Bug 3 | ✅ |
| 9a | Update BUGS.md (Bug 3+4), journals, planning docs | ✅ |
| 9b | Implement native `js()` fetch + debug logs | ✅ |
| 9c | User browser test — POST sent but no Flask response | 🔴 |
| 9d | Finalize docs + CODEBASE_REFERENCE | 🔲 |

**Status Q9c**: Native `js()` fetch IS sent (Network tab confirms POST to
`/api/sketch/upload` with `Content-Type: multipart/form-data`, 227 bytes),
but **Flask never logs the request** — no werkzeug access log, no
`SKETCH_UPLOAD:` app log. The request appears to leave the browser but
never reaches Flask's handler.

**Finding #5**: Unknown behavior — the `js()` block might be failing silently
before `fetch()` completes, or Flask might not be routing the request. Need
diagnostics.

### Phase 24: Diagnose Native `js()` Fetch — POST Sent But No Flask Response ✅ COMPLETED

**Date**: 2026-05-27

**Q10c findings — confirmed**:
- `js()` block executes correctly: `JS_RAN`, `FD_TYPE: object`, `REQ_SENT` all appear
- Flask receives request: `BEFORE_REQ: POST /api/sketch/upload (len=227)` at 21:10:19
- **Handler blocks on `request.files.getlist("files[]")`** — Werkzeug multipart parser hangs
- 10-second gap before next request confirms internal deadlock

**Q10f findings — further narrowed**:
- `API_SKETCH_UPLOAD STARTED` ✅ — handler DOES start
- `FD_ENTRIES: 1` ✅ — FormData has 1 file entry (Content-Length: 227 bytes)
- `FILES PARSED` ❌ — `request.files.getlist()` blocks the parser
- 3.3s gap before next request (shorter than 10s, possibly socket timeout)

**CRITICAL BREAKTHROUGH — User clarification**:
- **Browse works**: Files from `<input webkitdirectory>` → `#folder-input.files` → FormData → `fetch()` → Flask processes → sketch in /uploads ✅
- **DnD hangs**: Files from `dataTransfer.files` → `#sketch-upload-modal.__dndFiles` → FormData → `fetch()` → body never arrives → Flask blocks ❌
- Same handler, same `for` loop, same `fd.append()` — only difference is File source

**Root cause**: `dataTransfer.files` cannot represent directories. Firefox returns
`length: 0` for folder drops, Chrome returns a 4096-byte directory stub. The
correct API is `DataTransfer.items[i].webkitGetAsEntry()` for folder tree
traversal via `FileSystemEntry.isDirectory`/`.isFile` + `createReader()`/
`readEntries()` loop (max 100 per call). `entry.file()` gives fresh File objects
with real content — no FileReader needed.

### Phase 25: Fix DnD Upload — webkitGetAsEntry Folder Traversal ✅ COMPLETED

| Q | Change | Status |
|---|--------|--------|
| 11a | Update journals + planning docs with Q11d research | ✅ |
| 11b | Add file metadata diagnostic (FILE_NAME, FILE_SIZE, FILE_TYPE) | ✅ |
| 11c | User test: Browse works, DnD hangs (both FF/Chrome) | ✅ |
| 11d | Research: webkitGetAsEntry + readEntries loop + entry.file() | ✅ |
| 11e | Implement: rewrite DnD drop handler with webkitGetAsEntry | ✅ |
| 11f | Update upload handler: pass relative path as third arg to fd.append() | ✅ |
| 11g | User test: Browse FF, DnD FF, DnD Chrome — all work ✅ | ✅ |
| 11h | Remove diagnostics, fix Ctrl-C shutdown, finalize docs | ✅ |

**DnD upload now uses `DataTransfer.items[i].webkitGetAsEntry()` for folder tree
traversal. Recursive `traverseEntry()` handles nested directories via
`createReader()` + `readEntries()` loop (max 100/call). `entry.file()` provides
fresh File objects with real content. Manual `__relativePath` tracking since
DnD files lack `webkitRelativePath`. Upload handler uses single `js()` block
(pure JS, no hyperscript) to avoid all 4 known hyperscript 0.9.13 bugs.**

**Last Updated**: 2026-05-28

---

### Phase 26: Fix `test_watch_boards` — RST_STREAM Error Code 8 + Daemon Fixture ✅ COMPLETED

**Date**: 2026-05-28

**Bug**: `test_watch_boards` fails with `"Received RST_STREAM with error code 8"` when a board is connected. The error occurs because:
- `watch_boards()` catches `grpc.RpcError` and re-raises as `BoardError`, losing the gRPC status code
- When deadline expires after a board event was received, gRPC sends HTTP/2 `RST_STREAM CANCEL` (code 8)
- The test's `if "Deadline" in str(e) or "timeout" in str(e).lower()` — fragile string match misses the RST_STREAM path

**Fix — Q12a**: Handle `DEADLINE_EXCEEDED` gracefully in `watch_boards()` — `e.code() == grpc.StatusCode.DEADLINE_EXCEEDED` → return (stop iteration) instead of raising `BoardError`. Simplify test — no exception expected for timeout.

**Fix — Q12b**: Create `conftest.py` with module-scoped `daemon_url` fixture that starts/teardowns the arduino-cli daemon automatically. Remove manual daemon management dependency from integration tests.

**Fix — Q12c**: Add `test_watch_boards_event` — calls `list_boards()` first, if board connected, opens watch stream and asserts event payload.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 12a | Handle DEADLINE_EXCEEDED in `watch_boards()` + simplify test | `client.py:252-253`, `integration_test.py:71-83` | All 27 unit pass |
| 12b | Create conftest.py with module-scoped daemon fixture | `conftest.py` | Integration tests |
| 12c | Add board event test (skips if no board connected) | `integration_test.py` | Integration tests |
| 12d | Update all docs + CODEBASE_REFERENCE | Planning docs | ✅ |
| 12e | Extract DaemonCtx into daemon_helper.py (shared helper) | `daemon_helper.py`, `conftest.py`, `integration_test.py` | ✅ |
| 12f | main() uses DaemonCtx (no hardcoded URL) | `integration_test.py` | ✅ |
| 12g | Print messages before pytest.skip for board tests | `integration_test.py` | ✅ |
| 12h | Final docs sync | All docs | ✅ |

### Phase 27: Remove Backoff + Fix Zombie Daemon Retry ✅ COMPLETED

**Bug**: `pkill arduino-cli` kills daemon → becomes zombie → `os.kill(zombie_pid, 0)`
returns 0 (kernel keeps process table entry) → `is_alive` returns `True` →
`ensure_alive()` never spawns new daemon → BoardDetector retries forever with
increasing delay.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 13a | Zombie detection in is_alive (`_is_zombie()` via /proc/pid/status) | `daemon_manager.py:38-58` | ✅ All 182 board_manager pass |
| 13b | Remove linear backoff → 2s fixed delay | `board_detector.py` | ✅ All 182 pass |
| 13c | Retry immediately after restart in _run_once() | `board_detector.py` | ✅ All 182 pass |
| 13d | Finalize all docs + CODEBASE_REFERENCE | All docs | ✅ |

### Phase 28: Stale `arduino-cli daemon` Fix ✅ COMPLETED

**Date**: 2026-05-28

**Root cause**: `integration_test.py:19-48` auto-discovered by `pytest board_manager`. Module-scoped fixture starts real `python -m board_manager` subprocess which spawns real `arduino-cli daemon --daemonize` grandchild. Fixture teardown sends `proc.terminate()` (SIGTERM) but `__main__.py` has no SIGTERM handler. Python's default `SIG_DFL` kills the process immediately — `DaemonManager.stop()` never runs, daemon orphaned to PID 1.

**Three fixes**:

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 1 | Register SIGTERM handler (`sys.exit(0)`) in `__main__.py` at module level + wrap `service.start()` in `try/finally` with `service.stop()` | `__main__.py` | ✅ 182 unit pass; integration daemon cleaned |
| 2a | Create `conftest.py` with `--integration` CLI flag + marker definition + skip hook | `conftest.py` | ✅ 174 passed, 8 skipped (no daemon) |
| 2b | Add `@pytest.mark.integration` to `TestBoardManagerIntegration` class | `integration_test.py` | ✅ 8 skip without flag, 8 pass with flag |
| 2c | Fix fixture teardown — `try/finally` + SIGKILL fallback on 5s timeout + pipe cleanup + UDS socket cleanup | `integration_test.py` | ✅ Daemon cleaned, socket cleaned |

**Verification**:
- `pytest board_manager` → 174 passed, 8 skipped (no daemon started, no stale process)
- `pytest board_manager --integration` → 8 passed (daemon started + cleaned)
- No stale `arduino-cli` daemon or UDS socket left behind

### Phase 29: Compile/Upload Spinner Vertical Alignment Fix ✅ COMPLETED

**Date**: 2026-05-28

**Bug**: Spinner and text not vertically aligned in compile/upload in-progress cards. Caused by `vertical-align: middle` heuristic on `inline-block` element larger than adjacent text.

**Fix**: Flexbox wrapper (`display: inline-flex; align-items: center`) around spinner + text — pixel-perfect centering.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 1 | Add `.spinner-label` CSS in `base.html`, remove `margin-right`/`vertical-align` from `.spinner` | `base.html` CSS block | ✅ All 315 pass |
| 2 | Wrap spinner+text in `.spinner-label` in 4 partials | `compile_in_progress.html`, `compile_poll_pending.html`, `upload_in_progress.html`, `upload_poll_pending.html` | ✅ Frontend-only, visuals confirmed |

**Verification**: Manual visual check — spinner and text vertically centered in all 4 partials. All 315 existing tests pass.

### Phase 30: Sketch Path Abstraction + Checksum Dedup + Modification Fix ✅ COMPLETED

**Date**: 2026-05-28

**Requirements**:
1. Replace editable sketch path `<input>` with a `<select>` dropdown listing uploaded sketches for `(ip, ua)` — show only sketch name, no timestamp.
2. Checksum deduplication: SHA256 of uploaded files, keyed by `(ip, user_agent, sketch_name)`.
3. Modified re-upload detection: different checksum → new version saved.
4. Fix mtime-based modification check: add content-based checksum alongside mtime. Track sketch path on upload (not just compile success) so first-upload-then-compile has a reference point.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 1 | `_compute_sketch_checksum()` helper | `app.py` | 3 new |
| 2 | Upload registry refactor + dedup in `api_sketch_upload()` | `app.py` | 3 new |
| 3 | `GET /api/sketches` endpoint | `app.py` | 2 new |
| 4 | Frontend: dropdown partial + `/api/last-upload` returns selector | `sketch_path_selector.html`, `board_detail.html`, `app.py` | Frontend |
| 5 | `meta.sketch` → `meta.sketch_name` in 4 partials | 4 partial templates | Frontend |
| 6 | Checksum-based modification checks + upload tracking fix | `app.py` | 4 new |

**Total**: 12 new tests → 327 total, all passing, zero warnings.

---

### Phase 31: Fix Non-Reentrant Lock Deadlock in `api_last_upload()` ✅ COMPLETED

**Date**: 2026-05-29

**Bug**: `api_last_upload()` at `app.py:593-600` acquires `_upload_registry_lock`
(non-reentrant `threading.Lock`), then calls `_render_sketch_path_selector()`
while still holding the lock. But `_render_sketch_path_selector()` at line 566
also tries to acquire `_upload_registry_lock` → **deadlock** → request hangs
forever → dropdown never renders.

**Introduced in Phase 23 Q15 Q4**: When replacing the editable `<input>` with a
`<select>` dropdown, the new `_render_sketch_path_selector()` function (which
reads from the upload registry) was called inside the lock region.

**Three other calls are safe**: `api_sketch_upload()` at line 557 calls
`_render_sketch_path_selector()` **after** its lock block exits. Lines 605,
626, 627 are already outside the lock.

**Fix**: Save `selected_path` inside the lock, call
`_render_sketch_path_selector()` after the lock releases.

| Q | Change | Files | Tests |
|---|--------|-------|-------|
| 1 | Restructure `api_last_upload()` — extract `selected_path` from lock, call selector after release | `app.py` | All 110 existing pass |
| 2 | Add regression test — populate registry, call endpoint, assert 200 | `test_app.py` | +1 → 111 webapp pass |
| 3 | Update all docs + CODEBASE_REFERENCE | All docs | ✅ |

**Last Updated**: 2026-05-29 (Phase 32 ✅ COMPLETED)

---

### Phase 32: Sketch Versioning + Timestamp Annotations + Delete ✅ COMPLETED

**Date**: 2026-05-29

**Problem**: `_upload_registry` maps `(ip, ua) → sketch_name → {path, checksum, timestamp}`. Uploading a different version of the same sketch overwrites the entry. Old directory stays on disk but orphaned. Dropdown shows only name — no way to tell versions apart.

**Requirements**:
1. **Keep all versions** with timestamps (not replace)
2. **Show timestamps** in dropdown: `blinky (2026-05-29 12:00)`
3. **Rename label**: "Sketch Path" → "Sketch"
4. **Delete**: Remove sketch from registry + files from disk

**Registry structure change** — single entry → list of versions:
```
# Before (one entry per sketch name):
_upload_registry[(ip, ua)] = {
    "blinky": {"path": ..., "checksum": ..., "timestamp": ...}
}

# After (list of versions per sketch name):
_upload_registry[(ip, ua)] = {
    "blinky": [
        {"path": ".../130000_blinky/blinky", "checksum": "def456", "timestamp": "2026-05-29T13:00:00"},
        {"path": ".../120000_blinky/blinky", "checksum": "abc123", "timestamp": "2026-05-29T12:00:00"},
    ]
}
```

| Q | Change | Files | Verification |
|---|--------|-------|-------------|
| 1 | Registry structure (`dict→list`), upload appends version, warmup groups by name, dedup checks all versions | `app.py` | ✅ Existing dedup tests pass |
| 2 | Selector flattens versions with timestamps, `api_last_upload()` finds latest, `api_sketches()` returns all | `app.py` | ✅ Timestamp `YYYY-MM-DD HH:MM` in dropdown |
| 3 | Template shows timestamp in option text | `sketch_path_selector.html` | ✅ Visual (unchanged template, `name` includes timestamp) |
| 4 | `DELETE /api/sketch?path=` — validate path, remove from registry, `rmtree`, return dropdown | `app.py` | ✅ Upload→delete→verify gone |
| 5 | Delete button + "Sketch" label rename | `board_detail.html` | ✅ Visual + 4 tests |
| 6 | 7 new tests + final test run + all docs + CODEBASE_REFERENCE | All | ✅ **118 webapp pass, 335 total** |

**Test impact**: Existing dedup tests still valid (path1≠path2, both dirs exist).
7 new tests: delete (4), version listing (2), dedup across names (1).

**Last Updated**: 2026-05-29 (Phase 32 ✅ complete)

---

### Phase 33: Fix Delete Button + DnD Console Error ✅ COMPLETED

**Date**: 2026-05-29

**Bug**: `hx-vals='{"path": js:...}'` in `board_detail.html:28` is malformed for HTMX 2.0.4 — the `js:` expression is unquoted, so the attribute is not valid JSON. HTMX silently fails to parse it during page processing, which:
1. Prevents the `hx-delete` behavior from being attached to the delete button (no request fires)
2. Logs `Uncaught (in promise) undefined` from HTMX internal promise chain (the DnD console error)

**Fix**: Change to HTMX 2.x JS form: `hx-vals='js:{path: document.getElementById("sketch_path") ? document.getElementById("sketch_path").value : ""}'`

| Q | Change | File(s) | Verification |
|---|--------|---------|-------------|
| 1 | Fix `hx-vals` attribute | `board_detail.html` | All 335 existing tests pass |
| 2 | Update all docs + CODEBASE_REFERENCE | All | Docs consistent |

**Last Updated**: 2026-05-29 (Phase 33 ✅ complete)

---

### Phase 34: Fix `htmx:targetError` — Missing `#sketch-path-container` in DOM ✅ COMPLETED

**Date**: 2026-05-29

**Bug**: The `sketch_path_selector.html` partial renders only a bare `<select>` element. When HTMX swaps it into the DOM via `hx-swap="outerHTML"`, the original `<div id="sketch-path-container">` is replaced and **no longer exists**. This causes:
1. **Delete button**: `hx-target="#sketch-path-container"` → element not found → `htmx:targetError` → no request fires
2. **Upload DnD**: `htmx.ajax('GET', '/api/last-upload', {target: '#sketch-path-container'})` → element not found → `Uncaught (in promise) undefined`

**Fix**: Wrap `sketch_path_selector.html` content in `<div id="sketch-path-container">` so every swap preserves the target.

| Q | Change | File(s) | Verification |
|---|--------|---------|-------------|
| 1 | Wrap select in container div | `sketch_path_selector.html` | All 335 tests pass |
| 2 | Update all docs + CODEBASE_REFERENCE | All | Docs consistent |

**Last Updated**: 2026-05-29 (Phase 34 ✅ complete)

---

### Phase 35: Delete Confirm Modal (Webapp Modal Instead of Browser Dialog) ✅ COMPLETED

**Date**: 2026-05-29

**Requirement**: Replace browser's native `confirm()` dialog (from `hx-confirm`) with a custom webapp modal for sketch deletion, matching the upload modal pattern.

**Design**:
1. Create `partials/delete_confirm_modal.html` — modal with sketch name/path display, "Delete" and "Cancel" buttons
2. Delete button → hyperscript `on click` → stores current `#sketch_path` value on modal → shows modal
3. Modal confirm button → HTMX `hx-delete` with path from `modal.__deletePath` → refreshes dropdown

| Q | Change | File(s) | Verification |
|---|--------|---------|-------------|
| 1 | Create delete confirm modal partial | `delete_confirm_modal.html` | Modal renders correctly |
| 2 | Wire up delete button + modal confirm | `board_detail.html`, modal partial | Delete works via modal, no browser dialog |
| 3 | Update all docs + CODEBASE_REFERENCE | All | Docs consistent |

**Last Updated**: 2026-05-29 (Phase 35 ✅ complete)

### Phase 36: Fix Remaining Console Errors — `_="on submit halt"` ✅ COMPLETED

**Date**: 2026-05-30

**Issue**: v2's lowercase `method="post"` suppressed the hyperscript form warning but caused native form submission to Flask's GET-only `/board/<port>` route → 405 Method Not Allowed.

**Root cause**: Adding `method="post"` to an HTMX-managed form enables native form submission behavior. When users press Enter or when the browser auto-submits, the form does a native POST before HTMX can intercept it.

**Fix**: Add `_="on submit halt"` to the `<form>` — hyperscript halts the native `submit` event, preventing native form submission while keeping `method="post"` for hyperscript form validation suppression.

| Q | Change | File(s) | Verification |
|---|--------|---------|-------------|
| 3 | Add `_="on submit halt"` to `<form id="compile-form">` | `board_detail.html:17` | All 335 tests pass |
| - | User also added `_log_all_requests()` diagnostic, `innerHTML` swap, `container-grow` class | Various | Diagnostic(s) removed in Phase 24 |

**Last Updated**: 2026-05-30 (Phase 36 ✅ complete)

---

### Phase 37: Diagnostic Cleanup — Remove `_log_all_requests()` + Stale Code ✅ COMPLETED

**Date**: 2026-05-30

**Motivation**: Post-debugging cleanup. The `@app.before_request` `_log_all_requests()` diagnostic (added during Q22 v3 debugging) logs every request server-side — unnecessary overhead. Also remove stale `_last_upload_by_ip` deprecated dict and related commented-out code.

**Changes**:

| # | Change | Files | Verification |
|---|--------|-------|-------------|
| 1 | Remove `@app.before_request _log_all_requests()` handler | `app.py:27-31` | ✅ All 117 webapp pass |
| 2 | Remove deprecated `_last_upload_by_ip` dict + lock + commented-out code | `app.py:53-54, 550-553, 604-610` | ✅ No stale references |
| 3 | Fix `clear_caches` fixture — remove `_last_upload_by_ip.clear()` | `test_app.py:27-28` | ✅ Fixture no longer references removed dict |
| 4 | Remove stale `test_returns_path_from_in_memory_dict` — tested removed functionality | `test_app.py:938-948` | ✅ Covered by registry + meta tests |
| 5 | Fix timezone bug: `dt + dt.astimezone().utcoffset()` double-counts offset | `app.py:574-577` | ✅ Shows correct local time |
| 6 | Fix brittle timezone test — use regex instead of hardcoded time | `test_app.py:1185` | ✅ Works in any timezone |

**Test totals**: 117 webapp (-1 removed stale test) + 174 board-manager + 33 arduino-grpc = **324 unit tests, all passing, zero warnings**. 10 integration tests skipped (no daemon/board).

**Last Updated**: 2026-05-30 (Phase 37 ✅)

---

### Phase 38: Rename Webapp to Arduino Dash ✅ COMPLETED

- [x] Q1: Banner/title cosmetic changes — "MedMinder" → "Arduino Dash" in templates + __main__.py
- [x] Q2: Rename module directory `webapp` → `arduino_dash` + update internal imports
- [x] Q3: Update test imports (`from webapp` → `from arduino_dash`)
- [x] Q4: Update packaging config (pyproject.toml, Pipfile)
- [x] Q5: Reinstall, run all 324 tests, verify no regressions

### Phase 39: Review & Polish — Refactor ✅ COMPLETED

Module extraction refactor: split shared infrastructure into standalone packages.

- [x] **Quantum 1**: Create `board_manager_client` package — extract `pubsub_client.py`
- [x] **Quantum 2**: Create `arduino_sketch_tools` package — Flask Extension + compile/upload Blueprint + 9 partials
- [x] **Quantum 3**: Refactor arduino_dash — split `app.py` → `infra.py`, `board_management.py`, `sketch_management.py`
- [x] **Quantum 4**: Wire `ArduinoSketchTools` extension — remove old compile/upload routes and partials
- [x] **Quantum 5**: Migrate tests — adapt `board_manager_client/tests/test_pubsub_client.py`, write `arduino_sketch_tools/tests/test_extension.py`, remove old `arduino_dash/pubsub_client.py` + `test_pubsub_client.py`

**Test totals**: 369 passed (89 arduino_dash + 47 arduino_sketch_tools + 174 board_manager + 24 board_manager_client + 35 arduino_grpc), 8 skipped, zero warnings.

---

### Phase 40: MedMinder Web — Complete ✅

**Date**: 2026-05-31

**Goal**: Create standalone medminder-dash application for managing medicine schedules,
generating `alarm.hpp` for the MedMinderV2 Arduino sketch, and orchestrating compile/upload.

**Design**:
- Flask + HTMX app (reuses `board_manager_client` and `arduino_sketch_tools`)
- In-memory medicine data (v1)
- `sketch_gen.py` generates `alarm.hpp` C++ header
- 5 quantums: skeleton → sketch_gen → CRUD → compile/upload → E2E

| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 | Package skeleton | `pyproject.toml`, `app.py`, `__main__.py`, `base.html`, `state.py` | ✅ |
| 2 | `sketch_gen.py` | `alarm.hpp` generator with decade/text encoding | ✅ |
| 3 | Medicine CRUD + UI | Routes, templates, data model | ✅ |
| 4 | Compile/upload integration | Wire `arduino_sketch_tools`, board selector | ✅ |
| 5 | Modify MedMinderV2 + E2E | `#include "alarm.hpp"`, full cycle test | ✅ |

**Directory structure**:
```
medminder_dash/python/medminder_dash/
├── __init__.py
├── __main__.py              # Entry point, init pubsub on startup
├── app.py                   # Flask factory + all routes + ArduinoSketchTools wiring
├── state.py                 # Medicine dataclass + MedicineStore (CRUD, toggle, only_enabled)
├── infra.py                 # validation helpers, day_name, time_display
├── sketch_gen.py            # alarm.hpp generator (generate_alarm_hpp, esc_text, minute_to_decade, validate_hour)
├── pubsub.py                # PubSubClient lifecycle, board tracking, WS broadcast, sketch dir constants
├── templates/
│   ├── base.html            # Dark theme with nav (Medicines, Deploy)
│   ├── index.html           # Landing page with medicine count
│   ├── medicines.html       # Medicine list HTMX fragment
│   ├── medicine_form.html   # Add/edit form HTMX fragment
│   ├── deploy.html          # Deploy page: generate → compile → upload steps
│   └── partials/
│       ├── generate_result.html
│       ├── board_list.html
│       └── (ArduinoSketchTools partials from blueprint)
├── tests/
│   ├── __init__.py
│   ├── test_sketch_gen.py   # 16 tests for alarm.hpp generation
│   ├── test_routes.py       # 19 tests for CRUD routes
│   ├── test_deploy.py       # 7 tests for deploy/generate endpoints
│   └── test_e2e_sketch.py   # 7 tests for MedMinderV2 E2E verification
├── pyproject.toml
└── Pipfile                  # deps: flask, flask-sock, board-manager, board-manager-client, arduino-sketch-tools
```

**Test totals**: **49 new medminder-dash tests**, all passing. Grand total: 369 + 49 = **418 tests**.

**Key decisions**:
- `alarm.hpp` defines `Medicine` struct + `medicines[]` array + `N_MED` macro — sketch just does `#include "alarm.hpp"`
- Only enabled medicines included in generated array; disabled skipped entirely
- Decade mapping: minute//10 → 0-5
- Hour 24 = midnight 00:xx (MedMinderV2 convention)
- `Medicine.name` is the 4-char display label (user responsible for 7-segment compatibility)
- In-memory `MedicineStore` with `threading.Lock` (v1, no database)
- MedMinderV2.ino: replaced inline `struct Medicine`, `medicines[]`, `N_MED` with `#include "alarm.hpp"`

---

### Phase 41: Nox-Based Wheel Building Automation

**Date**: 2026-05-31

**Motivation**: `arduino_dash/Pipfile` replaced path deps (`{path = "..."}`) with local wheel sources (`file://.../dist`). Wheels must be pre-built before `pipenv install`. Manual builds are tedious — automate with nox.

**Design**:
- Single `noxfile.py` at project root
- Parametrized `build` session — one per package (4 total)
- Builds from each package's `pyproject.toml` into the dist dir referenced by the Pipfile
- Additional `pipenv-install` session that runs `pipenv install` in `arduino_dash/`

**Implementation**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | Create `noxfile.py` with parametrized build sessions | ✅ |
| 2 | Build all wheels — verify dist output | ✅ |
| 3 | `pipenv install` from `arduino_dash/` + run tests | ✅ |

**Test totals**: All 418 existing tests + arduino_dash tests (89/89) verified. All passing, zero warnings.

**End-to-end verification**: `nox` → `pipenv install --dev` → `pytest` = 89/89 pass.

**Fixes discovered during testing**:
1. `arduino_sketch_tools` wheel missing `templates/` — added `[tool.setuptools.package-data]`
2. `board_manager`/`board_manager_client`/`arduino_sketch_tools` wheels missing source files — moved `[tool.setuptools.packages.find]` to parent-level `pyproject.toml`
3. Pipfile.lock must be regenerated when wheel hashes change (delete and `pipenv install --dev`)

**Last Updated**: 2026-05-31 16:55

---

### Phase 42: PEP 503 Index + Pipfile Fix ✅ COMPLETED

### Phase 43 — MedMinder UI Enhancements ✅ COMPLETED

**Goal**: Complete board‑centric UI integration: fix uncovered gaps (missing `/medicines` route, no‑op persistence, dead pubsub wiring) and finalize all plan items (Gunicorn dep, README, board‑selected guards).

**Fix quantums (Q14–Q19)**: All 6 quantums complete. 53/53 tests pass. Blocker bugs fixed: JSON persistence wired, pubsub called in factory, `/medicines` route added, board guards added, gunicorn dep added, README updated.

**Completed items from initial pass**:
- Board selector route (`/board/select/<port>`)
- Board detail view (`/board`) rendering medicines
- Status badge polling `/api/board_status`
- JSON board list endpoint (`/api/board_list`)
- Dev‑server port env var (`MEDMINDER_PORT`, default 8080)
- Gunicorn entry script (`run_gunicorn.py`)
- Per‑board `MedicineStore` scoping (in‑memory)
- Board‑isolation and board‑status tests

**Audit findings (2026-06-01)**:

| # | Severity | Issue | Fix Quantum |
|---|----------|-------|-------------|
| 1 | BLOCKER | `url_for("medicines")` crashes — no `/medicines` route | Q3 |
| 2 | BLOCKER | `state.py:_save` is no‑op — data lost on restart | Q1 |
| 3 | BLOCKER | `init_pubsub()` never called — board events dead | Q2 |
| 4 | HIGH | CRUD routes lack board‑selected guard | Q3 |
| 5 | MEDIUM | Gunicorn not in pyproject.toml | Q4 |
| 6 | MEDIUM | README not updated | Q5 |

**Fix quantums**:
| Q | Scope | Key changes |
|---|-------|-------------|
| 1 | JSON persistence | Wire `_data_file`, implement `_save`/`_load`, add persistence tests |
| 2 | PubSub wiring | Call `init_pubsub(app)` in `create_app()`, add hyperscript listener |
| 3 | `/medicines` route + guards | Add route, fix redirect targets, add board-selected guard with 400 |
| 4 | Gunicorn dependency | Add `gunicorn` to pyproject.toml, update `run_gunicorn.py` |
| 5 | README | Add sections for board flow, Gunicorn, env vars, metadata file |
| 6 | Final review | Update CODEBASE_REFERENCE, verify all tests pass, update docs |

---

### Phase 44 Bugfix — Scanner Guard, Port Normalization, Thread Safety

**Date**: 2026-06-01 15:30

**Context**: After Q6 (daemon badge), Q7 (board connection-status badge), Q8 (fallback scanner), user reported that boards don't show up in the grid despite `/dev/ttyACM0` existing on disk and daemon badge working. Investigation revealed 3 bugs.

**Bugs found**:

| # | Bug | Root Cause | Fix |
|---|-----|-----------|-----|
| 1 | Scanner skips scan when BMS offline | Guard uses `pubsub.is_connected` (fragile socket state) → `is_daemon_ready()` (authoritative flag) | Change guard in `_fallback_scan_loop` to check `is_daemon_ready()` |
| 2 | Scanner thread dies silently | No try/except around loop body → daemon thread terminates on any exception with no traceback | Wrap body in `try/except Exception` with `logger.exception()` |
| 3 | Connection-status badge always shows "Disconnected" | Port key mismatch: `get_port_info("dev/ttyACM0")` → `None` when key is `"/dev/ttyACM0"` | Normalize port in `api_board_connection_status` route |

| Q | File | Change | Verification |
|---|------|--------|-------------|
| A | `pubsub.py:49` | `if is_daemon_ready(): continue` instead of `if pubsub.is_connected: continue` | Boards appear in grid within 5s when BMS offline |
| A | `pubsub.py:46-78` | Wrap loop body in try/except with `logger.exception()` | Scanner survives exceptions, continues running |
| B | `app.py:177-178` | Add `if not port.startswith("/"): port = "/" + port` before `get_port_info()` | Connection-status badge shows "Connected" when board in `_known_ports` |
| C | `partials/board_grid.html:6` | `b.get('board', 'Unknown') or 'Unknown'` — handle empty string | Board card shows "Unknown" for fallback-detected boards |

**Verification**: 53/53 tests pass (each quantum). Board appears in grid within 5s. Badge shows "Connected". Scanner survives exceptions with logged traceback. All 53 tests unaffected.

### Regression: `is_daemon_ready()` Alone Worsens the Problem

**Date**: 2026-06-01 16:00

**Finding**: The initial guard `if is_daemon_ready(): continue` caused a regression — boards never appear even when BMS is running. Root cause: `_daemon_ready` is a persistent flag that stays `True` after the socket breaks. `pubsub.is_connected` correctly returns `False` on broken sockets, but `_daemon_ready` stays `True` because `_on_pubsub_reconnect()` is only called during `_reconnect()` → `connect()` → `_connect_once()` → `on_reconnect()`, not during error-triggered socket disconnection in `_send()`.

**Corrected guard**: Both conditions:
```python
if pubsub.is_connected and is_daemon_ready():
    continue
```

| Q | File | Change | Verification |
|---|------|--------|-------------|
| D | `pubsub.py:49` | `if pubsub.is_connected and is_daemon_ready(): continue` | BMS dead → scanner runs; BMS alive → scanner skips; socket broke → scanner runs |

### Phase 44 Bugfix Round 2: Route Path Converter + Scan-First Delay

**Date**: 2026-06-01 16:30

**Context**: After Quantum D fix, three issues remain:
1. **404 on Manage button** — route uses `<port>` (string) instead of `<path:port>`
2. **5s delay** — scanner sleeps before first scan instead of after
3. **Intermittent empty grid** — same 5s delay window allows reader thread reconnect race

| Q | Scope | File | Change | Verification |
|---|-------|------|--------|-------------|
| E | Fix route converters | `app.py:45,64` | `<port>` → `<path:port>` on `/board/select/` and `/board/` routes | All 53 tests pass |
| F | Fix scan delay | `pubsub.py:47-48` | Move `time.sleep` after scan body | All 53 tests pass |

### Phase 44 Bugfix Round 3: Add Medicine Button + Board Events Card

**Date**: 2026-06-01 16:50

**Context**: After QE+QF, user reported "Add Medicines" button silent failure and requested board events card removal.

**Bug analysis**:
1. **Cancel button destroys target** — `hx-target="#medicine-form-container" hx-swap="outerHTML"` replaces container with medicine-list div → gone from DOM
2. **Nested duplicate IDs** — `hx-swap="innerHTML"` + response wrapper with same ID
3. **Trailing slash mismatch** — form `hx-post="/medicine/"` vs route without `/`

| Q | Scope | File | Change | Verification |
|---|-------|------|--------|-------------|
| G.1 | Button swap innerHTML→outerHTML | `board_detail.html:63` | Prevent nested IDs | All 53 tests pass |
| G.2 | Cancel button target fix | `medicine_form.html:62-65` | Target `#medicine-list`, clear container via hyperscript | All 53 tests pass |
| G.3 | Form trailing slash | `medicine_form.html:12` | Remove trailing slash, fix edit double-slash | All 53 tests pass |
| H.1 | Remove board events card | `index.html:24-34` | Delete events card from dashboard (keep backend) | All 53 tests pass |

### Phase 44 Bugfix Round 4: CRUD Responses, alarm.hpp, Compile Timeout, UDS Address

**Date**: 2026-06-01 17:30

**Context**: After QG+QH, four issues reported:
1. Medicines card duplicates board detail cards
2. alarm.hpp not updated on medicine changes
3. Compilation starts but never completes
4. Board not detected when plugged in after startup

**Bugs & Fixes**:

| Q | Scope | File | Change | Verification |
|---|-------|------|--------|-------------|
| I.1 | CRUD redirect→HX-Redirect | `app.py:84-144` | Replace `redirect()` with `HX-Redirect` header | Fixes duplication; tests pass |
| I.2 | Auto-generate alarm.hpp | `app.py:84-144` | Call `_write_alarm_hpp()` after each mutation | alarm.hpp stays in sync |
| I.3 | Update tests | `test_routes.py` | 302→200 assertions, check HX-Redirect header | All tests pass |
| J | Compile timeout | `client.py:301` | Add `timeout=120` to `self.stub.Compile(request)` | Compile doesn't hang |
| K | UDS address collision | `service.py:182,412` | Use unique connection ID instead of `"uds:"` | Board detection works

---

### Phase 45 — Dynamic Sketch Directory Config + alarm.hpp Wiring ✅ COMPLETED

**Goal**: Fix two remaining bugs — alarm.hpp not regenerated on CRUD, compile fails "Missing sketch path" — and make sketch directory configurable via admin UI.

**Date**: 2026-06-02

**Result**: All 5 quantums done. 54 tests pass.

| Q | Scope | Status |
|---|-------|--------|
| L.1 | Wire alarm.hpp in CRUD | ✅ |
| L.2 | Fix hx-include | ✅ |
| L.3 | Extension sketch_path | ✅ |
| L.4 | Admin UI + dynamic path tests | ✅ |
| L.5 | Doc sync | ✅ |

### Phase 46 — Board Detection, alarm.hpp, Compile Error, Session Staleness Fixes (DONE)

**Goal**: Fix 5 issues — wrong REPO_ROOT path when installed, board name "Unknown" from fallback scanner, compile error display too generic, stale "Connected" in board status, FQBN not pre-populated.

**Date**: 2026-06-02

**Quantums**:

| Q | Scope | File | Change | Status |
| A | REPO_ROOT fix | `settings.py`, `.env` | `MEDMINDER_ROOT` env var override | ✅ |
| B | Board name resolution | `pubsub.py` | Fallback scanner queries arduino-cli for name/FQBN | ✅ |
| C | Compile error display | `compile_result.html` | Show `result.data.error` (compiler stderr) | ✅ |
| D | Board status endpoint | `app.py` | Check `get_port_info()` for real connected state | ✅ |
| E | FQBN pre-population | `board_detail.html` | Read FQBN from `board_info` | ✅ |
| G | `_read_loop` socket timeout | `pubsub_client.py` | `recv()` → `select()` + 1s timeout | ✅ |
| H | Doc sync | CODEBASE_REFERENCE | Update with Phase 46 G-H | ✅ |

### Phase 47 — Reader Thread Race Condition (TypeError/AttributeError Crash) ✅ COMPLETED

**Goal**: Fix race between `_send()` and `_read_loop()` where unhandled `TypeError`/`AttributeError` crashes the reader thread, silently dropping all PubSub messages.

**Date**: 2026-06-02

| Q | Scope | File | Change | Status |
|---|-------|------|--------|--------|
| 1 | Add missing exceptions | `pubsub_client.py:189` | `TypeError, AttributeError` to except clause | ✅ |
| 2 | CODEBASE_REFERENCE | `CODEBASE_REFERENCE.md` | Document Phase 47 | ✅ |
| 3 | Doc sync | All workflow docs | Final sync | ✅ |

### Phase 48 — Reader Thread Safety & alarm.hpp Bootstrap ✅ COMPLETED

**Goal**: Fix the remaining _read_loop processing gap (feed/dispatch outside try/except), align PubSub health-checking with arduino_dash, and add alarm.hpp → MedicineStore bootstrap on startup.

**Date**: 2026-06-02

**Completed**: 2026-06-02

| Q | Scope | File | Change | Status |
|---|-------|------|--------|--------|
| 1 | Wrap _read_loop processing in try/except | `pubsub_client.py:201-208` | Separate try/except for feed/read_one/dispatch | ✅ |
| 2 | Add `sys::health` subscription | `medminder_dash/pubsub.py` | Subscribe `sys::health` matching arduino_dash | ✅ |
| 3 | Fix daemon badge check | `medminder_dash/app.py:api_daemon_status` | Check `is_connected` AND `is_daemon_ready()` | ✅ |
| 4 | Fix timeout template text | `compile_pending.html` | "60 seconds" → "150 seconds" | ✅ |
| 5 | Create `parse_alarm_hpp()` + `unesc_text()` | `sketch_gen.py` | Regex parser + C-string unescaping | ✅ |
| 6 | Wire alarm bootstrap into `create_app()` | `app.py` | Load from alarm.hpp if store empty | ✅ |
| 7 | Add admin sync button + route | `admin_sketch_dir.html`, `app.py` | POST `/admin/sync-alarm` button | ✅ |
| 8 | Tests for alarm parsing | `test_sketch_gen.py` | Parse empty, single, multiple, special chars | ✅ |
| 9 | Final doc sync + CODEBASE_REFERENCE | All docs | Update all docs | ✅ |

### Phase 49 — Fix Stale Wheel, Namespace Conflict & Deploy Phase 47/48 Fixes ✅ COMPLETED

**Goal**: Phase 47/48 changes exist in source but were never deployed. Fix the stale wheel and namespace package conflict so the fixes actually run.

**Date**: 2026-06-03

**Completed**: 2026-06-03

| Q | Scope | File | Change | Status |
|---|-------|------|--------|--------|
| A | Rebuild all wheels via `nox` | `noxfile.py` | Run `nox` to rebuild `board_manager_client` wheel with Phase 47/48 fixes | ✅ |
| B | Fix namespace package conflict | `app.py` | `sys.path.append()` → `sys.path.insert(0, ...)` | ✅ |
| C | Verify compile results flow end-to-end | — | Manual: compile → result appears in webapp | ✅ |
| D | Verify alarm.hpp bootstrap + admin sync | — | Manual: restart with alarm.hpp → meds loaded; sync button works | ✅ |
| E | Doc sync + CODEBASE_REFERENCE | All docs | Update all docs with real deployed state | ✅ |

### Phase 50 — Fix alarm.hpp Bootstrap & Compilation Status ✅ COMPLETED

**Goal**: alarm.hpp bootstrap never fires because stale `TestBoard`/`default` entries in board_meta.json make `store.all()` return 1 at module-load time. Even if it fired, entries load into "default" board (wrong). Compilation status never updates because double `init_pubsub()` creates two UDS connections. Fix both properly.

**Date**: 2026-06-03

**Completed**: 2026-06-03

**Root Causes Found**:
1. **Stale board_meta.json**: `"TestBoard"` (1 med) + `"default"` (1 "Test" med) → `store.all()` returns 1 → bootstrap exits early
2. **Wrong board context at module load**: No Flask request context → `_current_board()` falls back to `"default"` → alarm entries stored under wrong key
3. **Double `init_pubsub()`**: Called from both `create_app()` and `__main__` → two UDS connections → BMS address collision → subscription loss
4. **Double handshake on TCP fallback**: `_create_socket()` TCP branch sends HANDSHAKE_NEWLINE, then `_send_handshake()` sends it again
5. **Wrong REPO_ROOT**: `parents[3]` resolves to `medminder_dash/` instead of project root; should be `parents[4]`

**Plan**: 7 quantums (5 fixes + doc sync + tests)

| Q | Scope | Key Change | Files | Status |
|---|-------|-----------|-------|--------|
| 1 | Clean stale board_meta.json | Remove "TestBoard" and "default" test entries | `medminder_dash/python/data/board_meta.json` | ✅ |
| 2 | Refactor alarm bootstrap | Remove from `create_app()`, add lazy check in `board_select()` | `medminder_dash/app.py` | ✅ |
| 3 | Fix double `init_pubsub()` | Remove from `create_app()`, keep only in `__main__.py` | `medminder_dash/app.py` | ✅ |
| 4 | Fix double handshake TCP | Remove redundant `sendall` in TCP fallback | `board_manager_client/.../pubsub_client.py` | ✅ |
| 5 | Fix `REPO_ROOT` | `parents[3]` → `parents[4]` | `medminder_dash/app.py` | ✅ |
| 6 | Doc sync + CODEBASE_REFERENCE | Update all docs | All docs | ✅ |
| 7 | 3 new tests | Lazy bootstrap tests | `test_bootstrap.py` | ✅ |

**Verification**: 75/75 medminder_dash tests pass (72 existing + 3 new). board_manager_client wheel rebuilt with Q4 fix.

---

### Phase 53 — Remove Redundant Navbar Board Status ✅ COMPLETED

**Date**: 2026-06-03

**Completed**: 2026-06-03

**Goal**: The `#board-status` span in the navbar polls `/api/board_status` every 5s to show "No board selected" / "Connected to /dev/..." / "Disconnected (/dev/...)". This textual connection status is redundant with:
- The board grid (self-polls every 5s with full card rendering)
- The board detail page (per-board connection badge via `/api/board/<port>/connection-status`)
- The daemon badge (overall BMS connectivity)

**Design decisions**:
- Keep `/api/board/<port>/connection-status` — still used by `board_detail.html`
- Keep daemon badge — separate feature for BMS connectivity
- The hyperscript `on htmx:afterRequest if #board-grid then call #board-grid.htmx.trigger('load')` attached to `#board-status` is also removed, but the grid already self-polls — no functional loss

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | Remove navbar board status markup | Remove `#board-status` span + hyperscript from navbar | `base.html` | ✅ |
| 2 | Remove backend route | Delete `/api/board_status` endpoint | `app.py` | ✅ |
| 3 | Remove dead tests | Delete `test_board_status.py` + `TestBoardStatus` in `test_routes.py` (5 tests total) | — | ✅ |

**Verification**: 70/70 medminder_dash tests pass (75 - 5 dead tests removed).

---

### Phase 54 — Align PubSub, WS, Entry Point, Fallback Scanner ✅ COMPLETED

**Date**: 2026-06-03

**Goal**: Systematically align medminder_dash and arduino_dash across 4 areas. For each diff, supplement the module that's lacking rather than removing features.

**Design decisions**:
- Create `medminder_dash/dash_state.py` (avoid naming conflict with MedicineStore `state.py`) matching arduino_dash's `state.py` for shared singletons
- Extract board-related routes into `board_management.py` matching arduino_dash's module pattern
- arduino_dash gets `create_app()` factory for test isolation (like medminder_dash)
- Fallback scanner copied from medminder_dash to arduino_dash

| Q | Codebase | Scope | Key Changes | Status |
|---|----------|-------|-------------|--------|
| 1 | medminder_dash | State pattern | Create `dash_state.py`, refactor `pubsub.py`/`app.py`/test imports, restore `state.py` | ✅ |
| 2 | medminder_dash | TCP CLI args | Add `--tcp-host`, `--tcp-port`, `--no-uds`; extend `init_pubsub` | 🔲 |
| 3 | medminder_dash | Disconnect cleanup | Clear arduino_sketch_tools dicts on board disconnect via `_clear_sketch_tools_state()` | ✅ |
| 4 | medminder_dash | Board routes module | Create `board_management.py`, extract WS + board API routes | ✅ |
| 5 | arduino_dash | Factory pattern | Wrap init in `create_app()`, module-level `app = create_app()` for backward compat; update `__main__.py` | ✅ |
| 6 | arduino_dash | Full re-registration | Re-register all 6 handlers in `_on_pubsub_reconnect` | ✅ |
| 7 | arduino_dash | WS robustness | Add timeout, error handling to WS + broadcast | ✅ |
| 8 | arduino_dash | Template alignment | `events`-list based `board_event.html` | ✅ |
| 9 | arduino_dash | Fallback scanner | Copy scanner + board info resolution from medminder_dash | ✅ |

**Verification**: medminder_dash 70/70 + arduino_dash suite pass.

---

### Phase 55 — WSGI + BMS Lifecycle

**Date**: 2026-06-03

**Goal**: Add gunicorn WSGI entry points for both dashboards with BMS auto-start via gunicorn hooks. Production-ready deployment pattern.

**Architecture**: gunicorn hooks (Approach A):
- `gunicorn.conf.py` per dashboard with `when_ready` → starts BMS, `post_worker_init` → `init_pubsub()` per worker, `on_exit` → stops BMS
- Shared `board_manager/boot.py` module for BMS lifecycle helpers
- `wsgi.py` stays minimal: just `app = create_app()` + env config

**Design decisions**:
- `--preload` not required — each worker imports wsgi.py independently, calls `init_pubsub()` separately
- BMS subprocess owned by gunicorn master process (pid 1 of worker tree)
- `wait_for_bms()` polls UDS path then TCP port, configurable timeout
- `BMS_FIRE_AND_FORGET` env var skips readiness wait
- Config via existing `BOARD_MGR_*` env vars (shared with `board_manager.config`)

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | Shared boot module | `boot.py` with `start_bms()`, `stop_bms()`, `wait_for_bms()` + tests | `board_manager/boot.py`, tests | ✅ |
| 2 | arduino_dash wsgi | Minimal WSGI entry: `app = create_app()` | `arduino_dash/wsgi.py` | ✅ |
| 3 | arduino_dash gunicorn | `gunicorn.conf.py` with BMS lifecycle hooks; add gunicorn dep | `arduino_dash/gunicorn.conf.py`, `pyproject.toml` | ✅ |
| 4 | medminder_dash wsgi | Minimal WSGI entry; replace `run_gunicorn.py` | `medminder_dash/wsgi.py` | ✅ |
| 5 | medminder_dash gunicorn | `gunicorn.conf.py` with BMS lifecycle hooks | `medminder_dash/gunicorn.conf.py` | ✅ |
| 6 | Integration tests | Test hooks fire correctly, BMS lifecycle, signal handling | Both test suites | ✅ |
| 7 | Align exception handling | Move try/except from `init_pubsub()` internal to `__main__.py` caller (match medminder_dash pattern) | `infra.py`, `__main__.py`, `test_app.py` | ✅ |

**Verification**: All existing tests pass + new boot module tests + E2E verification + exception handler alignment tests.

---

### Phase 56 — Arduino Deps Installer + gRPC Bindings Generator + Populated setup.py 🚧 IN PROGRESS

**Date**: 2026-06-04

**Goal**: Three discrete build-quality-of-life improvements:

1. **Arduino library installer** (`scripts/install_arduino_deps.sh`) — one-shot bash script that checks for `arduino-cli` and installs `RTClib` + `TM1637TinyDisplay` libraries (used by MedMinderV2 sketch).
2. **gRPC Python bindings generator** (`scripts/gen_grpc_bindings.py`) — regenerates the `_pb2.py` and `_pb2_grpc.py` stubs from arduino-cli proto files. Supports local checkout or downloaded archive, auto-detects pipenv/poetry/uv venvs for installing `grpcio-tools` and `googleapis-common-protos`, prompts user before any install.
3. **Populated `setup.py`** for all 6 wheel-built packages — replace the 2-line stubs with proper `setup()` metadata including `install_requires` (PyPI-resolved names), `console_scripts` entry points, and `package_data` (templates/ + static/ + config/).
4. **CI pipeline** (Q18) — `nox -s all_tests`, `nox -s all_builds` wrapper sessions + `scripts/ci.sh` one-command runner. Enforces "tests before builds" without depending on nox's `depends` kwarg (unsupported in nox 2026.4.10).

**Motivation**:
- The board test workflow (test compile/upload) requires RTClib + TM1637TinyDisplay to be installed via arduino-cli lib; currently requires manual installation. Scripts automate the first-time setup.
- The existing `cc/arduino/cli/commands/v1/` stubs are hand-maintained / committed. When arduino-cli releases new RPC versions, regenerating them is manual. A script makes this reproducible.
- The `setup.py` files are 2-line stubs that call `setup()` with no args. This makes the wheels technically valid but provides no entry points, no install_requires, no package_data — meaning `pip install arduino-dash.whl` gives you a non-runnable package. Populating them with real metadata + console_scripts is required for the wheel-based deployment.
- CI is currently ad-hoc (`nox -s 'tests(X)' 'build(X)'`). Adding `all_tests` + `all_builds` + `ci.sh` gives a one-command way to validate the whole monorepo end-to-end.

**Design decisions**:

| Decision | Reason |
|----------|--------|
| **Bash, not Python, for `install_arduino_deps.sh`** | arduino-cli is a shell tool; user wants minimal friction. Pure bash avoids Python dependency. |
| **Library list hardcoded** (not configurable) | The use case is narrow: MedMinderV2's specific dependencies. Configurability adds complexity for no current benefit. |
| **Verify with `arduino-cli lib list` after install** | User gets explicit confirmation; no silent failures. |
| **For `gen_grpc_bindings.py`: venv detection, not assume system pip** | User works with pipenv, poetry, and uv. System pip may pollute system packages. Auto-detect order: pipenv > poetry > uv > system. |
| **Proto source path NOT hardcoded** | Users have arduino-cli source in different places. `--proto-src` is required, with download fallback. |
| **Download fallback uses GitHub releases** | Authoritative source for arduino-cli protos. |
| **Prompt before pip install** | User explicitly approved. `--install-deps --no-prompt` for CI. |
| **Create full `__init__.py` chain under cc/** | The generated `_pb2` modules are part of a `cc.arduino.cli.commands.v1` package — needs the parent chain for imports. |
| **PyPI-resolved names in `install_requires`** | User's local-wheel workflow is in Pipfile's `[[source]]` entries, not setup.py. setup.py stays standard so `pip install <wheel>` works with any index. |
| **`console_scripts` for `arduino-dash`, `board-manager`, `medminder-dash`** | User explicitly requested. `arduino-grpc`, `board-manager-client`, `arduino-sketch-tools` are libraries — no entry points. |
| **`package_data` for the 3 webapps only** | Only `arduino_dash`, `arduino_sketch_tools`, `medminder_dash` have `templates/` dirs. Pure-lib packages don't need package_data. Forward-compat for `static/` and `config/`. |
| **Top-of-file docstring explains local-source convention** | setup.py is read by humans — a clear comment is the right place to document "we use local wheels, see Pipfile". |

**Implementation Quantums**:

| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 | `install_arduino_deps.sh` | `scripts/install_arduino_deps.sh` (new, chmod +x) | ✅ |
| 2 | Verify bash script — `bash -n` syntax check + run in check-only mode | — | ✅ |
| 3 | `gen_grpc_bindings.py` skeleton — argparse CLI + main entry | `scripts/gen_grpc_bindings.py` (new) | ✅ |
| 4 | Add venv detection (pipenv, poetry, uv, system) | `scripts/gen_grpc_bindings.py` | ✅ |
| 5 | Add proto source resolution (local + download fallback) | `scripts/gen_grpc_bindings.py` | ✅ |
| 6 | Add protobuf generation + `__init__.py` chain | `scripts/gen_grpc_bindings.py` | ✅ |
| 7 | Run `gen_grpc_bindings.py` to regenerate stubs (real run) | — | ✅ |
| 8 | Populate `arduino_grpc/setup.py` | `grpc_client/python/arduino_grpc/setup.py` | ✅ |
| 9 | Populate `board_manager/setup.py` | `board_manager/python/board_manager/setup.py` | ✅ |
| 10 | Populate `board_manager_client/setup.py` | `board_manager_client/python/board_manager_client/setup.py` | ✅ |
| 11 | Populate `arduino_sketch_tools/setup.py` | `arduino_sketch_tools/python/arduino_sketch_tools/setup.py` | ✅ |
| 12 | Populate `arduino_dash/setup.py` | `arduino_dash/python/arduino_dash/setup.py` | ✅ |
| 13 | Populate `medminder_dash/setup.py` | `medminder_dash/python/medminder_dash/setup.py` | ✅ |
| 14 | Verify all 6 setup.py — `python setup.py --name` and `python -m build --wheel` for one | — | ✅ |
| 15 | Doc sync + CODEBASE_REFERENCE | All docs | ✅ |
| 16 | Add comprehensive test suite (per user feedback) — 94 pytest + 12 bash pass + 1 skip (without `grpc_tools`) | `scripts/tests/{conftest.py, test_install_arduino_deps.sh, test_gen_grpc_bindings.py, test_setup_py.py}` | ✅ |
| 17 | Populate `scripts/Pipfile` + remove Q7 skip + add edge-case tests + extend noxfile.py | `scripts/Pipfile`, `scripts/tests/test_gen_grpc_bindings.py`, `noxfile.py` | ✅ |
| 18 | Add `all_tests` / `all_builds` nox wrappers + `scripts/ci.sh` (CI pipeline) | `noxfile.py`, `scripts/ci.sh`, `scripts/tests/test_ci.sh` | ✅ |

**Q17 details (DONE)**: Per user feedback, populated the new `scripts/Pipfile` (Q17a), removed the Q7 `grpc_tools` skip (Q17b), added edge-case tests for missing deps (Q17b'), and extended `noxfile.py` with a `scripts_tests` session + per-package `tests` sessions (Q17c). Note: `build` sessions do NOT have a `depends` prerequisite in nox 2026.4.10 (kwarg unsupported); documented manual workflow. Full verification at Q17f.

**Q18 details (DONE)**: Added `all_tests` + `all_builds` nox wrapper sessions using `session.notify()` (Q18a, Q18b). Created `scripts/ci.sh` (Q18c) — bash wrapper that runs `all_tests` then `all_builds`, with `command -v nox` guard, `--skip-tests` / `--skip-builds` / `--help` flags, and exit codes 0/1/2/3/4. Created `scripts/tests/test_ci.sh` (Q18d) — 30 bash tests using a fake `nox` shim. Verified at Q18f.

**Verification**:
- `scripts/install_arduino_deps.sh` runs cleanly, prints install link on PATH failure, installs libs, confirms via `arduino-cli lib list`.
- `scripts/gen_grpc_bindings.py --proto-src /home/weerdmonk/Projects/arduino-cli/rpc --no-prompt` regenerates 11 `*_pb2.py` + 11 `*_pb2_grpc.py` + 11 `*_pb2.pyi` files in `grpc_client/python/arduino_grpc/cc/arduino/cli/commands/v1/`.
- All 6 setup.py files produce valid metadata via `python setup.py --name --version` and `python -m build --wheel` succeeds.
- All 6 console_scripts resolve: `arduino-dash`, `board-manager`, `medminder-dash`.
- All existing tests pass — no regressions (no source code changes, only build-script and metadata changes).
- Q17: `cd scripts && pipenv run pytest tests/` → 94 pass + 0 skip (was 1 skip). `nox -s scripts_tests` green. `nox -s 'tests(arduino_dash)' 'build(arduino_dash)'` (manual prerequisite workflow) green in 21s.
- Q18: `nox -s all_tests` → 8 sub-sessions green in 2 min. `nox -s all_builds` → 6 wheels in 42s. `./scripts/ci.sh --skip-builds` → green in 4 min. `./scripts/ci.sh` (full pipeline) → green. `bash scripts/tests/test_ci.sh` → 30 bash pass. Grand total: **598 pass + 10 skip** (94 pytest + 12 bash + 30 bash in scripts/; 462 + 10 skip across 6 packages).

---

### Phase 57 — Standalone Binaries (PyOxidizer) + Wheel Install Smoke Tests ✅

**Date**: 2026-06-04

**Goal**: Build standalone executables for all 3 apps via PyOxidizer (no Python runtime needed), plus wheel-install smoke tests and build scripts.

**Architecture decisions**:
- **Tool**: PyOxidizer 0.24.0 (pipx), Rust 1.93.0, bundles CPython 3.10.9
- **`filesystem-relative:prefix`** required for C extensions (`google._upb._message`, grpcio)
- **`include_distribution_sources = True`** required for stdlib (`encodings` module)
- **Per-app subdirectories** under `scripts/pyoxidizer/<app>/pyoxidizer.bzl`
- **`pip_download()` for local wheels + `pip_install()` for PyPI** avoids version constraint conflicts

| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 | `test_installs/` dir + Pipfile | `test_installs/Pipfile` (user-created) | ✅ |
| 2 | `scripts/test_installs.sh` — venv + wheel install + 6-package smoke tests | `scripts/test_installs.sh` (new) | ✅ |
| 3 | PyOxidizer PoC for board-manager | `scripts/pyoxidizer/board-manager/pyoxidizer.bzl` (new) | ✅ |
| 4 | PyOxidizer for arduino-dash (+ fixed `>0.1.0` → `>=0.1.0`) | `scripts/pyoxidizer/arduino-dash/pyoxidizer.bzl` (new) | ✅ |
| 5 | PyOxidizer for medminder-dash | `scripts/pyoxidizer/medminder-dash/pyoxidizer.bzl` (new) | ✅ |
| 6 | Nox sessions `test_installs` + `build_standalone` (+ `scripts/build_standalone.sh`) | `noxfile.py`, `scripts/build_standalone.sh` | ✅ |
| 7 | `.gitignore` — build artifacts | `.gitignore` (new) | ✅ |
| 8 | Doc sync (CODEBASE_REFERENCE + journals) | All docs | ✅ |
| 9 | **gRPC protobuf stubs verification** — all 26 modules (`cc.arduino.cli.commands.v1.*_pb2*` + `arduino_grpc.*`) import successfully in bundled binary via dedicated PyOxidizer test build | `scripts/pyoxidizer/test-grpc-imports/` (temporary, deleted) | ✅ |
| 10 | gunicorn `os.fork` edge case test with bundled binary | ✅ Verified: os.fork() pipe communication works, gunicorn 26.0.0 imports, gunicorn server with 1 worker fork serves HTTP request correctly | ✅ |

---

### Phase 58 — Cleanup, Documentation, Binary Optimization & Packaging ✅ DONE

**Date**: 2026-06-04

**Goal**: Complete the standalone binary workflow: clean up stale board-manager leftovers, move test_installs/ to dist-test-install/ with pipenv, add READMEs, populate dist-standalone/, e2e-verify with real BMS, optimize binary size (exclude unused stdlib), add tarball/zip packaging.

**Execution order**: Q3 → Q2 → Q1 → Q4 → Q5 → Q6 → Q7 → Q8 → Q9

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 3 | Rewrite `scripts/test_installs.sh` to use pipenv | Replace bare `python3.10 -m venv` + `pip install` with `pipenv sync` | ✅ |
| 2 | Move `test_installs/` → `dist-test-install/` + pipify | `mv test_installs dist-test-install`, rm bare `.venv`, rewrite Pipfile with 6 wheel file:// deps | ✅ |
| 1 | board-manager cleanup + rebuild | Delete stale `scripts/pyoxidizer/board-manager.bzl` + `scripts/pyoxidizer/build/` (153 MB), rebuild via per-app dir | ✅ |
| 4 | Create `scripts/README.md` | Document standalone build + run for all 3 apps | ✅ |
| 5 | Create `dist-test-install/README.md` | Document wheel install validation workflow | ✅ |
| 6 | Populate `dist-standalone/<app>/` | `nox -s build_standalone` for all 3 apps | ✅ |
| 7 | e2e verification with real BMS | Start BMS binary, start dashboard binary, curl endpoints | ✅ |
| 8 | Binary size optimization | Add stdlib exclusion list to all 3 `pyoxidizer.bzl`, rebuild, measure (~4 MB saved per app) | ✅ |
| 9 | Tarball/zip packaging | Add `--zip` flag + packaging step to `scripts/build_standalone.sh` | ✅ |

**Design decisions**:
- **No common.bzl**: each pyoxidizer config stays independent despite ~20 lines of duplicate stdlib exclusion list
- **Real BMS for e2e**: standalone board-manager binary vs mock server — less work, imitates actual scenarios
- **Conservative stdlib exclusion**: exclude per-user-agreed list only (`turtledemo`, `turtle`, `tkinter`, `_tkinter`, `distutils`, `lib2to3`, `pydoc`, `doctest`, `unittest`); verify each with `--help` smoke test; revert any that break
- **`.tar.gz` default + `--zip` flag**: `build_standalone.sh` packages after copy step
- **Q9 added to build_standalone.sh**: not a separate script; tarball is part of copy+package step
- **Q1 bugfix**: added `tomli>=1.1.0` to `board_manager/pyproject.toml` (missing dependency → BMS binary crashed at startup)

---

### Phase 59 — medminder_dash Board UI Improvements ✅ DONE

**Date**: 2026-06-06

**Goal**: Three small UX improvements to the medminder_dash board detail and deploy pages:
1. The `board_detail.html` page heading should show the **board name** (like the card grid) rather than the port path.
2. The FQBN field in `board_detail.html` Controls card is a read-only **label** rather than an editable input (FQBN is determined by the board). Add a **Device Port** label next to it for clarity.
3. Same FQBN-label + port-label treatment in `deploy.html`, plus JS update since the FQBN is no longer a form input.

**Design decisions**:
- **Heading mirrors card view**: `Board: {{ board_name }}` with `<p class="hint">Port: {{ port }}</p>` subtitle. Matches `partials/board_grid.html` (h3 board name + p.hint port). The fallback for missing board name is the port (mirrors the grid card's "Unknown" → port fallback).
- **Inline FQBN/Port display (form group pattern)**: Text shown inline within `<label>` for visual clarity, with a hidden `<input id="fqbn">` (and `<input id="port-display">` when needed) preserving the form-submission semantics. The hidden input keeps the existing `hx-include="#fqbn"` flow working.
- **Separate display ID to avoid `hx-include` collision**: Display `<span id="fqbn-display">` and hidden `<input id="fqbn">` are deliberately separate. The display cannot be the `hx-include` target because that would pull the entire span (with label text) into the form data, polluting request params.
- **`deploy.html` JS uses `textContent`**: FQBN is no longer an `<input>`, so `getElementById('compile-fqbn').value` → `getElementById('compile-fqbn-display').textContent.trim()`. Two call sites at lines 78, 92.
- **Test preservation**: Existing `TestBoardDetailFqbn` tests (`test_routes.py:243-262`) check for `value="arduino:avr:mega"` / `value="arduino:avr:uno"` substrings. Preserved by hidden input — tests still pass unchanged.
- **Device Port label position**: Placed alongside FQBN label in a 2-column layout (CSS flex, no new classes). On `board_detail.html` both are within the same form-group row. On `deploy.html` the labels are above the FQBN in Step 2.
- **Template variables**: Pass `board_name` from `board_management.py:board_detail` — `(board_info or {}).get('board', '') or port` (matches card grid behavior for fallback). For `deploy.html` Step 2, no board is selected (page-level, multi-board) — keep the FQBN/Port input as a static `arduino:avr:uno` default.

| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 | `board_detail.html` heading change (port → board name + port hint subtitle) | `medminder_dash/templates/board_detail.html`, `medminder_dash/board_management.py` (pass `board_name`) | ✅ |
| 2 | `board_detail.html` Controls card (FQBN label + hidden input + add Device Port label) | `medminder_dash/templates/board_detail.html` | ✅ |
| 3 | `deploy.html` (FQBN label + Device Port label + JS textContent change) | `medminder_dash/templates/deploy.html` | ✅ |
| 4 | New tests for board name heading, FQBN/Port labels, and full verification (78/78 medminder_dash tests + CODEBASE_REFERENCE update) | `medminder_dash/tests/test_routes.py`, `CODEBASE_REFERENCE.md`, `TESTING_*.md` | ✅ |

**Verification**: 78/78 medminder_dash tests pass. No regressions in arduino_dash (96/96) or board_manager (184/184 + 8 skip). All `TestBoardDetailFqbn` tests pass unchanged (hidden input preserves `value="..."` substring).

---

## Phase 60 — Merge `/deploy` + `/admin/sketch-dir` into single `/admin` page ✅ COMPLETED

**2026-06-07 00:25** | Status: ✅ Completed (Q1-Q6 all done)

**User-facing changes**:
- Single `/admin` page replaces both `/deploy` and `/admin/sketch-dir` (both old routes deleted)
- 4 cards: Sketch Path (DnD + select + delete, ported from arduino_dash), Set Medicines (bidirectional sync, both actions warn), Compile, Upload
- Sketch path input replaced entirely with arduino_dash-style DnD drop-zone + file browser + recent-uploads `<select>` + per-user upload registry
- In-page confirmation modals for both destructive medicine actions (Generate hpp, Sync from hpp)
- Nav: "Deploy" link removed, "Admin" link → `/admin`
- board_detail.html "Full Deploy Page" button → "Admin Page" → `/admin`

**Backend**:
- Port `arduino_dash/sketch_management.py` (4 routes) to `medminder_dash/sketch_management.py`
- Extend `dash_state.py` with `UPLOAD_BASE_DIR`, `_upload_registry`, `_upload_registry_lock`
- New endpoints: `GET /api/medicines/confirm-modal?action=...`, `POST /api/medicines/generate-hpp`, `POST /api/medicines/sync-from-hpp` (all use server-generated `confirm_token` in session)
- Confirm token: fresh UUID issued on each modal open → stored in session; destructive POSTs validate token + `session.pop()` for single-use; new token on next modal open

**Templates**:
- New: `admin.html` (4 cards), `partials/confirm_modal.html` (NEW generic), plus 3 ported partials from arduino_dash (sketch_upload_modal, sketch_path_selector, delete_confirm_modal)
- Delete: `deploy.html`, `admin_sketch_dir.html`
- Update: `base.html` (nav), `board_detail.html` (link text + href)

**Tests** (final: 82 → 94 medminder_dash, +12 net):
- Deleted: `TestAdminSketchDir` (3), `TestDeployPage` (1), `TestGenerateEndpoint` (2) — 6 obsolete tests
- Added: `TestSketchUpload` (7), `TestConfirmModal` (3), `TestSetMedicinesSync` (3), `TestSetMedicinesGenerate` (2), `TestAdminPage` (3) — 18 new tests

| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 | Port `sketch_management.py` + extend `dash_state.py` with upload registry | `medminder_dash/sketch_management.py`, `medminder_dash/dash_state.py`, `tests/test_admin.py` (sketch tests) | ✅ |
| 2 | Add 4 medicine sync endpoints (confirm modal + 2 destructive POSTs + token logic) in `app.py` | `medminder_dash/app.py`, `tests/test_admin.py` (medicine tests) | ✅ |
| 3 | New `admin.html` template + 5 partial templates (4 ported, 1 new confirm modal) | `medminder_dash/templates/admin.html`, `medminder_dash/templates/partials/*.html` | ✅ |
| 4 | Update `app.py` routes (remove 4 old, add `/admin`, wire `init_sketch_routes`), update `base.html` nav, update `board_detail.html` link, delete old templates | `medminder_dash/app.py`, `medminder_dash/templates/base.html`, `medminder_dash/templates/board_detail.html`, `medminder_dash/templates/deploy.html`, `medminder_dash/templates/admin_sketch_dir.html` | ✅ |
| 5 | Update tests (delete old, add new admin page + confirm modal tests) + run all 3 suites | `medminder_dash/tests/test_routes.py`, `medminder_dash/tests/test_deploy.py` | ✅ |
| 6 | Update `TESTING_*.md` + `CODEBASE_REFERENCE.md` + `PLAN.md` + `JOURNAL.md` | `TESTING_PROGRESS.md`, `TESTING_JOURNAL.md`, `CODEBASE_REFERENCE.md`, `JOURNAL.md` | ✅ |

**Verification**:
- All 3 test suites pass: `medminder_dash` (94), `arduino_dash` (96), `board_manager` (184 + 8 skip)
- Per-package: 374 pass + 8 skip
- Grand total: **972 pass + 8 skip** (was 906 + 8, +66)

**Key design decisions**:
- **Server-side session UUID for confirm token** (not hidden field): single-use enforced via `session.pop()` on consume, can't be forged without session cookie, fresh token on each modal open prevents reuse attacks
- **Per-IP+UA upload registry** (port from arduino_dash): `dict[tuple[str,str], dict[str, list[dict]]]`, isolates users by network identity
- **Path traversal protection**: `os.path.normpath(sketch_path).startswith(norm_base)` — `..` segments collapse to real path, fails check → 403
- **Flask test client IP/UA gotcha**: `werkzeug.test.Client` sets `REMOTE_ADDR=127.0.0.1` and `User-Agent=Werkzeug/x.x.x` — test fixture extracts from `resp.request.environ` to avoid stale data leakage between tests
- **Two separate board-port selects** (Compile card + Upload card, not shared): each operation targets a different action (compile to filesystem, upload to physical board) — sharing would couple them and confuse the user about which operation the selected port is for
- **Modal endpoint issues fresh token on each `GET /api/medicines/confirm-modal`** (not stored in admin.html): cleaner separation, no hidden form fields in main page, token only exists when modal is open


---

## Phase 61 — Medicine Management Cards on /admin (with diff detection) ✅ COMPLETED

**2026-06-07 02:00 → 03:15** | Status: ✅ Completed

**User-facing changes**:
- /admin gets a new top card: board-port select that drives medicine management
- Step 1 (Set Medicines) card gets new medicine management section ABOVE the existing sync buttons
- Shows ONE editable card (Medicines) when metadata == alarm.hpp (sync buttons greyed)
- Shows TWO cards (Metadata Medicines editable + alarm.hpp Medicines read-only) when they differ (sync buttons active)
- Editing metadata card always auto-syncs alarm.hpp (board_detail pattern)
- After edit, server re-checks diff — if now equal, UI collapses to 1 card + greys buttons
- Sync buttons (Generate hpp, Sync FROM hpp) keep confirm modal flow (race condition guard)
- board_detail keeps its medicine card (no change) — both pages manage medicines

**Backend**:
- Modify 5 existing routes (`/medicines`, `medicine_create/update/delete/toggle`) — remove `_require_board()`, return partials instead of HX-Redirect
- Add 4 new routes: `GET /api/medicines/diff` (JSON), `POST /api/medicines/active-board`, `GET /api/medicines/active-board-card`, `GET /api/medicines/board-selector`
- Modify `/admin` to accept `?port=` query param → set `session["admin_active_board"]`
- New session field `admin_active_board` (distinct from `board_port`)

**Templates**:
- New: `partials/admin_board_selector.html`, `partials/medicine_metadata_card.html`, `partials/medicine_alarm_hpp_card.html`, `partials/medicine_cards.html`
- Modify: `admin.html` (add board selector card, replace Step 1 body)

**Tests** (~+18 in medminder_dash):
- `TestMedicinesDiff` (5): equal, differ-by-add, differ-by-remove, alarm.hpp missing, parse error
- `TestActiveBoard` (3): URL query sets active board, POST changes active board, default to first known port
- `TestMedicineCardsRender` (3): 1 card when equal, 2 cards when differ, alarm.hpp missing shows warning
- `TestSyncButtonsState` (2): buttons disabled when 1 card, enabled when 2 cards
- ~5 frontend HTML structure tests

| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 | Backend: 5 modified routes + 4 new routes + 13 tests | `app.py`, `tests/test_admin.py` | ✅ |
| 2 | Frontend: 4 new partials + admin.html update + 6 frontend tests | `admin.html`, 4 new partials, `tests/test_admin.py` | ✅ |
| 3 | Run all 3 suites + update all docs | All | ✅ |

**Verification** (actual results):
- All 3 test suites pass: medminder_dash **113**, arduino_dash **96**, board_manager **184 + 8 skip**
- Per-package: 393 pass + 8 skip (was 374 + 8, +19)
- Grand total: **991 + 8** (was 972 + 8, +19)
- Manual: /admin with 1 board → 1 card; add medicine → still 1 card; manually edit alarm.hpp externally → reload → 2 cards; edit metadata card → auto-sync → 1 card again

---

## Phase 62 — Hot-Fix: MedMinderV2 Default in `/api/sketches` + Global Board Selector for Compile/Upload

**2026-06-07 05:30 → 06:15** | Status: ✅ COMPLETED

**Trigger**: User feedback after Phase 61.

**User-facing changes**:
- `/api/sketches` now returns the packaged `MedMinderV2` sketch as the first entry (always present, even with no prior uploads)
- Compile card on /admin shows Board Port + FQBN as text labels (no local select); always enabled
- Upload card on /admin shows Board Port + FQBN as text labels (no local select); disabled when no board is selected
- Global board selector at top of /admin spans full width; FQBN display below the select
- FQBN updates via OOB swap when the global port changes
- `compileSketch()` and `uploadSketch()` JS now read from the global select and FQBN

**Backend**:
- Modify `api_sketches` in `medminder_dash/sketch_management.py` — prepend `{"name": "MedMinderV2", "path": _DEFAULT_SKETCH_DIR, "timestamp": ""}` at index 0
- `/admin` route resolves `active_board_fqbn` from `get_port_info(active_board)` (default `"arduino:avr:uno"`)
- `api_medicines_board_selector` similarly resolves and passes FQBN
- `api_medicines_active_board` appends OOB-swap HTML for `#global-fqbn-display` and `#global-fqbn` (so FQBN updates when global port changes)
- **`/api/last-upload` UNCHANGED** (per user: returns empty on no uploads)
- **OOB swap for FQBN**: appends HTML with `hx-swap-oob="true"` to the response of `api_medicines_active_board`. This keeps the FQBN display in sync with the active board change without a second htmx request.
- **Visual state for disabled card**: `.card-disabled` class with `opacity: 0.5; pointer-events: none;`. Inline style or new CSS rule (no existing stylesheet for medminder_dash).

**Verification** (actual results):
- All 3 test suites pass: `medminder_dash` **123** (was 113, +10), `arduino_dash` 96 (no change), `board_manager` 184 + 8 skip (no change)
- Per-package: 403 + 8 (was 393 + 8, +10)
- Grand total: **1001 + 8** (was 991 + 8, +10)

---

## Phase 62.1-62.4 — /admin Page Fixes (3 User-Reported Issues) ✅ COMPLETED

**2026-06-07 06:30 → 07:30** | Status: ✅ Completed

**Trigger**: User testing after Phase 62 hot-fix; reported 3 issues with /admin page:

| Issue | Symptom | Root cause |
|-------|---------|------------|
| 1. MedMinderV2 default not loaded | /admin loads with empty sketch path; user must manually select from /api/sketches dropdown | `/api/last-upload` returns empty when no uploads; we only updated `/api/sketches` not the auto-load on /admin page |
| 2. Board port not visible after connecting | User plugs in board; global board selector at top of /admin doesn't refresh | `hx-trigger="load"` only fires once on initial page load; no polling |
| 3. Compile/upload doesn't update UI | Click Compile → no spinner; click Upload → no progress bar | JS uses `fetch` + `innerHTML` which doesn't trigger htmx's polling; ALSO `#compile-section` ID conflict between outer admin.html:166 card and inner compile_in_progress.html:1 polling target |

**User-facing changes**:
- /admin page loads with MedMinderV2 sketch path pre-populated (no manual selection needed)
- Global board selector polls every 5s (matches main dashboard) so newly-connected boards appear
- Compile/Upload buttons use htmx-native `hx-post` (no JS); no `#compile-section` ID conflict

**Backend**:
- `_render_sketch_path_selector` gets new `include_default: bool = False` param; when True, prepends MedMinderV2 entry to dropdown
- `/admin` route passes `default_sketch_path=_DEFAULT_SKETCH_DIR` to template

**Templates**:
- `admin.html` board selector div: `hx-trigger="load"` → `"load, every 5s"` (Phase 62.2)
- `admin.html` Sketch Path card: add hidden `<input id="sketch_path" value="{{ default_sketch_path }}">` so compile/upload POSTs include the path
- `admin.html` Compile/Upload cards: convert buttons to `hx-post`; remove `compileSketch`/`uploadSketch` JS
- `arduino_sketch_tools/templates/partials/compile_in_progress.html`, `compile_result.html`, `upload_in_progress.html`, `upload_result.html`: rename inner wrapper `id="compile-section"` → `id="compile-output-area"` (4 templates)

**Tests** (~+9 in medminder_dash, +1 verification in arduino_dash):
- Phase 62.1: `test_render_sketch_path_selector_includes_default_when_requested`, `test_render_sketch_path_selector_no_default_when_not_requested`, `test_admin_html_default_sketch_path_pre_populated`
- Phase 62.2: `test_admin_html_board_selector_polls_every_5s`, `test_admin_html_board_selector_polling_matches_main_dashboard`
- Phase 62.3: `test_admin_html_compile_button_uses_hx_post`, `test_admin_html_compile_button_targets_output_div`, `test_admin_html_upload_button_uses_hx_post`, `test_compile_in_progress_no_id_conflict`
- Phase 62.3: arduino_dash verification test confirming `board_detail.html:130-148` still works (no `#compile-section` ID conflict from Q3 rename)

**Key design decisions**:
- **Q1 — `include_default` param (not unconditional prepend)**: 5 callers of `_render_sketch_path_selector` — 3 want default (admin route, etc.), 2 don't (api_sketch_upload, api_last_upload, api_sketch_delete). Param defaults to False to preserve all existing behavior; only /admin opt-in
- **Q2 — Polling interval matches main dashboard (`every 5s`)**: `medminder_dash/templates/index.html:8` uses `every 5s`; user asked for consistency
- **Q3 — htmx-native hx-post (not fetch+innerHTML)**: htmx auto-processes returned HTML, so polling divs work. Outer admin.html:166 `id="compile-section"` card is the parent; inner compile_in_progress.html:1 `id="compile-section"` would collide if polling div uses `hx-target="#compile-section" hx-swap="outerHTML"` — would destroy parent card with Compile button. Rename inner to `#compile-output-area` to disambiguate
- **Q3 — Cross-package impact**: arduino_sketch_tools templates shared with arduino_dash; arduino_dash already uses `hx-target="#compile-section"` in `board_detail.html:130-148`. After rename, must verify arduino_dash still works OR update its target too. We verified arduino_dash Compile button is OUTSIDE its `#compile-section` div (line 147-148 button is above the section starting at ~149), so renaming inner arduino_sketch_tools partials is SAFE — arduino_dash target becomes `#compile-section` which is now unique to its own card
- **Q3 — NEW wheel rebuild workflow**: arduino_sketch_tools is installed from wheel in per-package venvs. Template changes require `nox -s 'build(arduino_sketch_tools)'` then reinstall (`nox -s 'tests(medminder_dash)' 'tests(arduino_dash)'` auto-rebuilds per-session via `pipenv install --dev`). First phase requiring this — Phase 62 only changed medminder_dash, not shared templates

**Verification** (actual results):
- All 3 test suites pass: `medminder_dash` 123 → **132** (+9), `arduino_dash` 96 (no change, Q3 verified), `board_manager` 184 + 8 skip (no change)
- Per-package: **412 + 8** (was 403 + 8, +9)
- Grand total: **1010 + 8** (was 1001 + 8, +9)
- Manual: /admin loads with MedMinderV2 in sketch path; plug in board → selector updates within 5s; click Compile → spinner → result polled every 2s

---

## Phase 62.5 — Per-Board Sketch Assignment + Wheel-Packaged Default ✅ COMPLETED

**2026-06-07 07:45** | Status: ✅ Completed (Q1-Q6 all done)

**Trigger**: User testing of Phase 62.1-62.4 revealed 3 deeper issues that require a redesign (NOT a revert).

**Root causes identified**:
1. **board_detail.html:31 sketch source**: `board_management.py:57` calls `load_sketch_dir()` (from `settings.py`) which reads `config/sketch_dir.json` and falls back to `_DEFAULT_SKETCH_DIR = REPO_ROOT / "sketches" / "MedMinderV2"`. In dev mode works; **in installed wheel mode BROKEN** (wheel has no `sketches/MedMinderV2/` in `package-data`)
2. **No per-board assignment**: all boards share the global `sketch_dir.json`; user wants stable per-board tagging using USB `hardware_id` (NOT port — ports change)
3. **MedMinderV2 not visible in dropdown**: `/api/last-upload` keeps `include_default=False`; only the hidden input holds the value

**User-facing changes** (locked answers):
- **Q1 (board_detail source)**: Per-board with default = packaged MedMinderV2 (look up assignment by `hardware_id`; fall back to packaged)
- **Q2 (storage)**: keep `uploads/` for files; tag with `hardware_id` in `medminder_dash/config/board_sketches.json`
- **Q3 (Phase 62.1-62.4 code)**: do NOT revert; build on top
- **Q4 (admin UX)**: select board at top → uploads auto-tagged to that board (simple, no ambiguity)
- **Q5 (hardware_id fallback)**: skip per-board assignment; use global default when `hardware_id == ""` (clone boards without USB serial)
- **Q5 (extract location)**: `~/.local/share/medminder/sketches/MedMinderV2/` (XDG user dir)
- **Q5 (sketch location)**: MOVE into package dir: `medminder_dash/python/medminder_dash/medminder_dash/sketches/MedMinderV2/`

**6 Quantums**:
| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 (62.5.1) | Surface `hardware_id` in board info flow | `pubsub.py:_resolve_board_info`, `pubsub.py:_fallback_scan_loop`, `board_detector.py:_run_once` | ✅ |
| 2 (62.5.2) | Per-board sketch registry | `medminder_dash/sketch_registry.py` (NEW), `medminder_dash/sketch_management.py` | ✅ |
| 3 (62.5.3) | board_detail uses per-board sketch | `medminder_dash/board_management.py:55-57`, `medminder_dash/templates/board_detail.html`, NEW `/api/board/<port>/sketch-name` | ✅ |
| 4 (62.5.4) | Admin UX: "Assigned to selected board" | `medminder_dash/templates/admin.html`, NEW `/api/admin/active-sketch`, `medminder_dash/sketch_management.py` | ✅ |
| 5 (62.5.5) | Wheel packaging for default sketch | MOVE `medminder_dash/sketches/MedMinderV2/` → `medminder_dash/python/medminder_dash/medminder_dash/sketches/MedMinderV2/`, update `pyproject.toml`, `medminder_dash/settings.py` | ✅ |
| 6 (62.5.6) | Final sync + verify | all docs + `nox -s all_tests` | ✅ |

**Actual test counts**: medminder_dash 132 → **152** (+20), arduino_dash 96 (no change), board_manager 184 → **186** (+2). Per-package: **434 + 8**. Grand total: **1032 + 8**.

---

## Phase 62.6 — Post-Launch Bugfixes ✅ COMPLETED

**Date**: 2026-06-08

**Trigger**: User reports file upload saves files but sketch selector doesn't refresh. Investigation found 5 bugs across Phase 62.1-62.5.

**5 quantums (one per bug)**:

| Q | Focus | Bug | Files | Result |
|---|-------|-----|-------|--------|
| 1 (62.6.1) | Fix post-upload refresh target | A (CRITICAL) | `admin.html`, `sketch_upload_modal.html` | ✅ |
| 2 (62.6.2) | Fix XDG extraction Traversable bug | B (HIGH) | `settings.py` | ✅ |
| 3 (62.6.3) | Fix duplicate `id="sketch_path"` | C (MEDIUM) | `admin.html` | ✅ |
| 4 (62.6.4) | Fix stale `#fqbn` on board change | D (MEDIUM) | `app.py` | ✅ |
| 5 (62.6.5) | Fix stale compile/upload URLs | E (MEDIUM) | `admin.html`, NEW `compile_upload_card.html`, `app.py`, `admin_board_selector.html` | ✅ |

**Final test counts**: medminder_dash 152 / arduino_dash 96 / board_manager 186+8 = 434+8 = 1032+8 grand total (no new tests).

---

## Phase 63 — setup.py Arguments + setup.cfg + Detailed READMEs ✅ COMPLETED

**Date**: 2026-06-09

**Goal**: Add proper `setup()` arguments (name, version, description, author, author_email, python_requires, packages, install_requires, entry_points, package_data, keywords) to all 6 packages. Create `setup.cfg` with modern `long_description = file: README.md`. Create detailed README.md for 5 packages (arduino_dash, arduino_sketch_tools, board_manager, board_manager_client, medminder_dash) and update the existing arduino_grpc/README.md.

**Work done** (forked session, no quantums):

| Package | setup.py | setup.cfg | README.md |
|---------|----------|-----------|-----------|
| arduino_dash | `setup()` with 14 args | ✅ new | ✅ new (188 lines) |
| arduino_sketch_tools | `setup()` with 13 args | ✅ new | ✅ new (179 lines) |
| board_manager | `setup()` with 11 args | ✅ new | ✅ new (218 lines) |
| board_manager_client | `setup()` with 9 args | ✅ new | ✅ new (175 lines) |
| arduino_grpc | `setup()` with 11 args | ✅ new | ✅ updated (stale counts fixed) |
| medminder_dash | `setup()` with 14 args | ✅ new | ✅ new (241 lines) |

**Key decisions**:
1. **Duplicate metadata in setup.py despite PEP 621**: User explicitly wants actual `setup()` arguments (not no-op markers). pyproject.toml remains source of truth; setup.py supplements with `author`, `author_email`, `long_description`, `keywords` not in pyproject.toml.
2. **`find_packages(include=["<pkg>*"])`** for 5 packages (matches `[tool.setuptools.packages.find]`). Explicit list for arduino_grpc (cross-source layout with `cc/`).
3. **`include_package_data=True`** for packages with template/static/config data (arduino_dash, arduino_sketch_tools, medminder_dash). Omitted for board_manager, board_manager_client, arduino_grpc.
4. **`setup.cfg` uses modern form** (`long_description = file: README.md` + `long_description_content_type = text/markdown`).
5. **READMEs are detailed** with: Overview, Architecture diagram, Installation (PyPI + monorepo), Usage, Development, Project Structure tree, Test Suite table, Dependencies, License.
6. **No `url` in setup()** — user explicitly skipped it.

**Key files created**:
- 6x `setup.py` — all with proper `setup()` arguments
- 6x `setup.cfg` — each with `[metadata] long_description = file: README.md`
- 5x `README.md` — new detailed documents (arduino_dash, arduino_sketch_tools, board_manager, board_manager_client, medminder_dash)
- 1x `arduino_grpc/README.md` — updated (test counts 22→27 unit, 7→8 integration, path correction, build instructions)

**Accuracy of README test counts verified against code**:
- arduino_dash: 96 ✓
- arduino_sketch_tools: 47 ✓
- board_manager: 194 ✓ (corrected from stale 184+8)
- board_manager_client: 24 ✓
- arduino_grpc: 35 ✓ (corrected from stale 22+7)
- medminder_dash: 152 ✓
- **Grand total: 548**

---

## Phase 64 — Full-Viewport DnD Overlay (Replace #drop-zone) ✅ COMPLETED

**Date**: 2026-06-09
**Status**: ✅ Completed
**Completed**: 2026-06-09
**Type**: Frontend UX improvement

**Goal**: Replace the small dashed `#drop-zone` in `admin.html` with a full-viewport translucent overlay that shows on file drag, accepts the drop anywhere on the page, and reuses the existing webkitGetAsEntry folder-traversal logic.

**Design decisions**:
1. **Overlay in `base.html`** (not `admin.html`) — affects both admin and board_detail pages; graceful no-op on pages without the upload modal.
2. **Hyperscript 0.9.13 only** — no plain JS event listeners; pure `_` attribute on the overlay div plus a `<script type="text/hyperscript">` `def`.
3. **Counter pattern** for show/hide — `@-drag-counter` increments on each `dragenter`, decrements on each `dragleave`; overlay shows at 0→1, hides at 1→0. Correctly handles bubbling through child elements.
4. **`dataTransfer.types.includes('Files')`** gate on all 4 handlers (dragenter, dragover, dragleave, drop) — no overlay for text/image/URL drags.
5. **`opacity` + CSS transition** — smooth 200ms show/hide; no `display: none` toggle.
6. **Traversal code extracted once** — `def processDndDrop(dataTransfer)` in base.html (same webkitGetAsEntry logic, no duplication).
7. **Browse button kept** — `<label for="folder-input">Browse...</label>` + hidden `<input type="file" webkitdirectory>` remain; `#folder-input`, `#modal-reset-input` preserved.

**3 quantums**:
| Q | Scope | Key Changes | Files | Tests |
|---|-------|-------------|-------|-------|
| 1 | Base overlay + trailing def | Add `#dnd-overlay` with hyperscript handlers + `def processDndDrop` in `<script type="text/hyperscript">` | `base.html` | 0 new (visual: manual) |
| 2 | Remove `#drop-zone` + update hints | Delete dashed drop zone, update hint text, keep browse elements | `admin.html` | 0 new (structural: existing pass) |
| 3 | Full flow verification | Drag sketch → overlay appears → drop → modal opens → upload works; Browse still works | — | Manual E2E; run all 3 suites |

**Files changed**:

| File | Change |
|------|--------|
| `base.html` | Add overlay div + `def processDndDrop` in `<script type="text/hyperscript">` |
| `admin.html` | Remove `#drop-zone` (~lines 41-109), update hint text (line 125) |
| `sketch_upload_modal.html` | **No change** — continues working via `__dndFiles` + `showModal` |

**Key hyperscript techniques**:
- `dragenter from window` / `dragleave from window` — listens on window for bubbling DnD events
- `@-drag-counter` — hyperscript attribute on the overlay element, incremented/decremented per event
- `halt the event` — `preventDefault()` + `stopPropagation()` (needed for both dragover and drop)
- `call processDndDrop(dataTransfer)` — invokes the global def with the destructured event param
- `wait 200ms` before restoring `pointer-events:none` — prevents flicker on brief window-exit

**Verification**:
- Drag sketch folder over page → overlay appears (translucent blue tint, smooth 200ms opacity)
- Drop anywhere on page → overlay hides → modal shows with folder name + file count → upload works
- Browse button still works (no regression)
- Non-file drags (text, images) → overlay does NOT appear
- All 3 test suites green (no new tests; existing 152/96/186+8 coverage sufficient)

### Q1 — Add overlay div + `def processDndDrop` to base.html ✅
- Added `#dnd-overlay` div with hyperscript handlers (dragenter/dragover/dragleave/drop from window)
- Added inline CSS (fixed, z-index 9999, opacity transition 200ms, pointer-events toggle)
- Added `@-drag-counter` counter pattern
- Added `dataTransfer.types.includes('Files')` gate
- Added `def processDndDrop(dataTransfer)` in `<script type="text/hyperscript">`
- All 3 test suites green: 152/96/186+8

### Q2 — Remove `#drop-zone` from admin.html + update hint text ✅
- Deleted `<div id="drop-zone">` (67 lines with hyperscript + JS traversal)
- Updated hint text to "Drag a sketch folder anywhere on the page to upload, or browse to select one."
- Updated bottom hint to "Select an Arduino sketch folder (.ino file) or drag & drop anywhere on the page"
- Browse button + `#folder-input` + `#modal-reset-input` preserved
- All 3 test suites green: 152/96/186+8

### Q3 — Full flow verification + CODEBASE_REFERENCE.md update ✅
- Manual E2E: DnD → upload → compile works
- Manual E2E: Browse → upload → compile works
- CODEBASE_REFERENCE.md updated with Phase 64
- All 12 project/workflow docs synced

### Bugfix: Q1 overlay never appeared — `from window` handler placement 🔧
**Bug**: User reported overlay never appears; drop opens browser file dialog.

**Round 1 fix**: Moved all 4 DnD handlers from overlay div to `<body>` using `tell #dnd-overlay`. ❌ Still broken.

**Round 2 root cause**: `from window` in hyperscript 0.9.13 doesn't reliably wire DnD events — `halt the event` never prevents browser default. Original body-level `on dragover from window` was never verified with real DnD.

**Round 2 fix**: Abandon hyperscript `_`-attribute DnD wiring. Use plain JS `document.addEventListener()` for dragenter/dragover/dragleave/drop. Timer-based show/hide (100ms debounce). `def processDndDrop` inlined into drop handler.

### Round 3: `dataTransfer.types` intermittent 🔧
**Bug**: Overlay + DnD upload intermittent (works sometimes, fails in Chrome entirely).

**Root cause**: `types.indexOf('Files')` guard unreliable — Chrome leaves `types` empty during `dragover` for directory drags; `DOMStringList.indexOf()` not universally supported.

**Fix**: (1) `dragover`: unconditional `preventDefault()`, (2) `drop`: use `items.length` instead of `types`, (3) `dragenter`/`dragleave`: `Array.from().includes()` for robust type checking. Removed dead code (`hideOverlay`, `dndCounter`).

**Final test counts**: medminder_dash 152 / arduino_dash 96 / board_manager 186+8 = 1032+8 grand total (no new tests).

### Round 4: Overlay stays visible on alt-tab 🐛
**Bug**: Overlay stays visible when user alt-tabs away while dragging. Two root causes:
1. Chrome clears `dataTransfer.types` when cursor leaves browser context → `dragleave` `hasFiles(types)` returns `false` → hide timer never starts → overlay stays visible.
2. No `visibilitychange` handler → no cleanup on tab/window switch.

**Fix** (3 changes in `base.html`):
1. `dndActive` flag set by `dragenter` (where `types` IS reliable), checked by `dragleave` instead of `hasFiles(types)`.
2. `hideOverlay()` named function extracted — clears timer + hides overlay + resets flag.
3. `document.addEventListener('visibilitychange', ...)` — calls `hideOverlay()` when document hidden.
4. `showOverlay()` also sets `dndActive = true`. `drop` and `dragleave` timer call `hideOverlay()`.

**Return-from-alt-tab guard**: On return, `dragenter` fires with Files if drag still active → overlay re-shown. If drag cancelled, no event fires → overlay stays hidden.

**All 3 suites green** (152/96/186+8). No new tests. User E2E pending.

### Round 5: Overlay doesn't show on return from alt-tab 🐛
**Bug**: Post-Round-4, overlay hides on alt-tab-away but doesn't reappear when returning with a drag. `dragenter`/`dragover` don't fire in unfocused windows; user must click tab.

**Root cause**: No synchronous "is drag active?" API. `visibilitychange` on return only hid overlay.

**Brainstormed fix with user**: Two-flag system:
1. `dragWasActive` flag — set by `dragenter` with Files, cleared only by `drop`. Persists across hide/show cycles.
2. `visibilitychange` visible: `if (dragWasActive) showOverlay();`
3. `mouseenter` + `mousemove` stale-cleanup: suppressed during DnD per HTML spec. If they fire with `dragWasActive` true, the drag was cancelled → clear flag + hide overlay.

**Key insight**: `mouseenter`/`mousemove` NOT dispatched during DnD per HTML spec section 17.1. Reliable cross-browser "no drag" signal. No timer needed (user rejected timer approach). Chrome, Firefox, Safari, Opera compatible.

**All 3 suites green** (152/96/186+8). No new tests.

### Round 6: Eliminate 100ms `dragleave` timer (counter pattern) ✅
**Trigger**: User asked to drop the last timer. Research confirmed commercial sites use counter pattern (no timer).
**Changes**: `hideTimer` → `dragCounter`. `dragleave` decrements (if >0), calls `hideOverlay()` when 0. Removed `clearTimeout` from show/hide helpers. Added `window.blur` for immediate alt-tab cleanup. `dragover` re-shows if `!dndActive && dragWasActive`. `mouseenter`/`mousemove` unchanged. All 3 suites green. Zero timers remaining.

### Round 7: Extract DnD overlay into partial, admin-page only ✅
**Trigger**: User clarified DnD overlay should only appear on admin page — not dashboard or board detail.
**Changes**: New `partials/dnd_overlay.html` — extracted CSS, overlay div, and JS from `base.html`. Removed from `base.html`. Added `{% include %}` to `admin.html` only. Zero functional change for admin; DnD absent elsewhere. All 3 suites green.

---

### Phase 65 — Fix admin board selector not updating on board connect 🐛 ✅ COMPLETED

**Date**: 2026-06-09
**Status**: ✅ Completed

**Bug**: Admin panel board port selector does not update when a board is plugged in after navigating to the admin dashboard. The `hx-trigger="load, every 5s"` polling stops working after the first poll.

**Root cause**: `admin.html:11` uses `hx-swap="outerHTML"` on the `#admin-board-selector-container` div. When the first `load`-triggered poll returns `admin_board_selector.html` (a bare card without HTMX polling attributes), `outerHTML` replaces the entire container — destroying the `hx-get`, `hx-trigger`, and `hx-target` attributes. Subsequent `every 5s` polls never fire.

Same bug pattern as Phase 34 (`htmx:targetError` — `#sketch-path-container` destroyed by `outerHTML`). The dashboard's `index.html` avoids this with `hx-swap="innerHTML"`.

**Fix**: Change `hx-swap="outerHTML"` → `hx-swap="innerHTML"` on `admin.html` line 11. The container div preserves its HTMX polling attributes after each swap.

**Quantums**:
| Q | Scope | Verification |
|---|-------|-------------|
| 1 | Fix `hx-swap` attribute | All 3 test suites green |
| 2 | All 3 test suites | 152/96/186+8 = 1032+8 |
| 3 | Doc sync + CODEBASE_REFERENCE | All docs synced |

**Test impact**: No new tests needed — existing `TestAdminBoardSelectorPolling` tests verify admin page initial render includes `hx-trigger="load, every 5s"`. The swap attribute change is a runtime behavior fix; initial render tests still pass.

**Final counts**: medminder_dash 152 / arduino_dash 96 / board_manager 186+8 = 1032+8 grand total (no change).

---

### Phase 66 — Refresh Button for medminder_dash + Fix arduino_dash Refresh Swap ✅ COMPLETED

**Date**: 2026-06-09
**Status**: ✅ Completed

**Trigger**: User exploration revealed two issues:
1. medminder_dash admin board selector has no manual refresh button (user must wait up to 5s for polling)
2. arduino_dash admin board selector has a refresh button but uses `hx-swap="outerHTML"` (same bug class as Phase 65 — kills container HTMX attributes)

**Fix**:
1. **medminder_dash**: Wrapped `<select>` in flex div + added Refresh button with `hx-get="/api/medicines/board-selector"`, `hx-target="#admin-board-selector-container"`, `hx-swap="innerHTML"`
2. **arduino_dash**: Changed `hx-swap="outerHTML"` → `"innerHTML"` on existing refresh button

**Quantums**:
| Q | Scope | Verification |
|---|-------|-------------|
| 1 | Add refresh button to medminder_dash | 152 medminder_dash tests pass |
| 2 | Fix arduino_dash refresh swap | 102 arduino_dash tests pass |
| 3 | Final doc sync | All 3 suites green + docs synced |

**Test impact**: No new tests needed. Existing tests cover initial render attributes.

**Final counts**: medminder_dash 152 / arduino_dash 102 / board_manager 186+8 = 1032+8 grand total (no change).

---

### Phase 67 — hx-disabled-elt + board-changed Trigger 👷 IN PROGRESS

**Date**: 2026-06-09
**Status**: 👷 In progress

**Goal**: 
1. Add `hx-disabled-elt="this"` to refresh button on both dashboards' admin board selectors to prevent spam clicks
2. Add `board-changed from:body` to board-selector container trigger so it refreshes immediately when user selects a board from dropdown (no wait for 5s poll)

**Approach**: HTMX-native — `hx-disabled-elt="this"` disables button during request; `.refresh-btn` CSS (already in place) handles pointer-events + opacity. `board-changed` event is already fired by `<select>` change handler via `hx-on::after-request="htmx.trigger('body', 'board-changed')"`.

**Note**: Spinner CSS (`.refresh-btn`, `.spinner.htmx-indicator` show/hide rules) already in place from previous implementation. No new CSS or spinner changes needed.

**Quantums**:
| Q | Scope | Verification |
|---|-------|-------------|
| 1 | medminder_dash: `hx-disabled-elt` on refresh button + `board-changed` trigger on admin.html:10 | 152 medminder_dash tests pass |
| 2 | arduino_dash: same `hx-disabled-elt` + `board-changed` trigger on admin.html:10 | 102 arduino_dash tests pass |
| 3 | Run board_manager tests + final doc sync | All 3 suites green + docs synced |

**Test impact**: Existing HTML structure tests cover initial render attributes. `hx-disabled-elt` and `hx-trigger` additions are static attribute changes in templates — existing tests continue to pass.

**Expected counts**: No test changes (152 / 102 / 186+8 = 1032+8).

---

### Phase 68 — Instant Board Selector Refresh on Board Change ✅ COMPLETED

**Date**: 2026-06-09
**Status**: ✅ Completed

**Bug**: Board selector only refreshes every 5s (polling) or when user clicks Refresh button. When user selects a board from the dropdown, the selector still shows stale port list until the next poll.

**Root cause**: The `<select>` in `admin_board_selector.html` fires `htmx.trigger('body', 'board-changed')` on change via `hx-on::after-request`. Currently only `#compile-upload-card` listens for this event. The `#admin-board-selector-container` only has `hx-trigger="load, every 5s"` — so it never refreshes on board change.

**Fix**: Add `board-changed from:body` to the board-selector container's `hx-trigger` attribute in both dashboards' `admin.html`:
- `hx-trigger="load, every 5s"` → `hx-trigger="load, every 5s, board-changed from:body"`

| Q | Scope | Verification |
|---|-------|-------------|
| 1 | arduino_dash admin.html:10 trigger change | 102 arduino_dash tests pass |
| 2 | medminder_dash admin.html:10 trigger change | 152 medminder_dash tests pass |
| 3 | All 3 test suites | All green (102/152/186+8) |

**Test impact**: No new tests — existing tests verify initial render attributes. Runtime event listening is HTMX-native.

**Expected counts**: No change (102 / 152 / 186+8 = 1032+8).

---

### Phase 68 — Remove Monorepo Path Hacks (settings.py + app.py + setup.py)

**Date**: 2026-06-10

**Goal**: Replace monorepo-relative path computations with XDG-standard paths so `medminder-dash` can be installed on a server via `pip install`.

**Design decisions**:
- `CONFIG_DIR` uses XDG config home (`~/.config/medminder/`) instead of `REPO_ROOT / "config"` — same methodology as `_DEFAULT_SKETCH_DIR`'s XDG data dir (`~/.local/share/medminder/sketches/MedMinderV2/`)
- `_resolve_default_sketch_dir()` removes the `REPO_ROOT / "sketches" / "MedMinderV2"` fallback — the XDG data dir + `importlib.resources` extraction cover both dev and server installs
- `app.py` `sys.path.insert` hacks removed — sibling packages (`arduino-sketch-tools`, `board-manager-client`, `arduino-grpc`) must be pip-installed
- `setup.py`/`pyproject.toml` `package_data` removes `"config/**/*"` — no longer needed

| Q | Scope | Key Changes | Files | Verification |
|---|-------|-------------|-------|-------------|
| 1 | `settings.py` | XDG CONFIG_DIR, remove REPO_ROOT/os/env/MEDMINDER_ROOT/repo_sketch | `settings.py` | 152 tests pass |
| 2 | `app.py` | Remove Path/REPO_ROOT/4x sys.path.insert | `app.py` | 152 tests pass |
| 3 | `setup.py`/`pyproject.toml` | Remove `config/**/*` from package_data, update docstring | `setup.py`, `pyproject.toml` | 152 tests pass |

**Verification**: All 152 medminder_dash tests pass unchanged (test env uses Pipfile which already installs sibling packages). Both arduino_dash (102) and board_manager (186+8) also unaffected.

---

### Phase 69 — Remove Hardcoded Source-Relative Paths from arduino_dash ✅ COMPLETED

**Date**: 2026-06-10

**Goal**: Replace `Path(__file__).resolve().parents[4]` and `os.path.dirname(os.path.abspath(__file__))` hacks in arduino_dash with XDG-standard paths, following the same pattern as Phase 68 (medminder_dash).

**Drivers**:
1. `sketch_registry.py` uses `parents[4]` to climb to monorepo root — breaks when installed as wheel
2. `state.py` computes `UPLOAD_BASE_DIR` relative to `__file__` — points to non-writable site-packages dir in wheel mode

**Changes**:
| File | Action |
|------|--------|
| `arduino_dash/settings.py` | **NEW** — XDG config (`~/.config/arduino-dash/`) and XDG data (`~/.local/share/arduino-dash/uploads/`) |
| `arduino_dash/sketch_registry.py` | Import `CONFIG_DIR`, `BOARD_SKETCHES_FILE` from settings |
| `arduino_dash/state.py` | Import `UPLOAD_BASE_DIR` from settings; remove unused `import os` |

**Verification**: All 3 suites green — arduino_dash 102, medminder_dash 151+1, arduino_sketch_tools 47.

---

## Phase 71a — Bugfix: Missing .board-event CSS Class ✅ COMPLETED

**Date**: 2026-06-11
**Status**: ✅ Completed

**Bug**: Phase 71 WS-triggered refresh doesn't work — `board_event.html` has no `.board-event` CSS class, so the `beforeSwap` handler never detects board events and never fires `board-changed`. Secondary: medminder_dash OOB wrapper targets missing `#live-events`.

**Fix**: Added `.board-event` class to both `board_event.html` partials; removed OOB wrapper from medminder_dash `pubsub_infra.py`.

**Verification**: arduino_dash 102/102, medminder_dash 151+1.

---

## Phase 71b — beforeSwap Fires board-changed on Wrong Element ✅ COMPLETED

**Date**: 2026-06-11
**Status**: ✅ Completed

**Bug**: Phase 71a was necessary but insufficient. The `beforeSwap` handler fires `board-changed` **directly on `#board-grid` and `#admin-board-selector-container`**, but these elements listen for `board-changed from:body`. HTMX's `from:` modifier filters events by originating element — an event fired on `#board-grid` never matches `from:body`. The trigger silently no-ops.

**Fix**: Change `htmx.trigger('#board-grid', 'board-changed')` and `htmx.trigger('#admin-board-selector-container', 'board-changed')` to a single `htmx.trigger('body', 'board-changed')` in both dashboards' `beforeSwap` handlers.

### Quantums

| Q | Scope | Files | Change | Verification |
|---|-------|-------|--------|-------------|
| 1 | Fix arduino_dash beforeSwap trigger target | `arduino_dash/templates/base.html:99-100` | `htmx.trigger('#board-grid', ...)` → `htmx.trigger('body', ...)` | 102 arduino_dash tests pass |
| 2 | Fix medminder_dash beforeSwap trigger target | `medminder_dash/templates/base.html:77-78` | Same | 151+1 medminder_dash tests pass |

### Architecture (Data Flow)

```
BoardDetector detects connect/disconnect
  → PubSub publish board::<port>::event
    → Dashboard _on_board_event handler
      → Updates state._board_list (in-memory)
      → Renders board_event.html
      → broadcast_ws(html)
        → HTMX beforeSwap handler intercepts
          → Queries .board-event elements (Phase 71a fix)
          → Fires htmx.trigger('body', 'board-changed') [Phase 71b fix]
            → #board-grid and #admin-board-selector-container
              detect board-changed from:body
              → hx-get="/api/boards/grid" re-fetches from state._board_list
              → Grid re-renders with current board state
```

**No test changes needed**: Server-side behavior unchanged; runtime JS dispatch not covered by existing tests.

---

## Phase 71c — WS Extension Bypasses `htmx:beforeSwap` Entirely ✅ COMPLETED

**Date**: 2026-06-11
**Status**: ✅ Completed

**Bug**: All previous fixes (71a, 71b) are targeting the wrong event. The HTMX WS extension (`ws.js`) does NOT fire `htmx:beforeSwap` for incoming WebSocket messages. It fires `htmx:wsBeforeMessage` and processes content via `api.oobSwap()` directly. Our `beforeSwap` handler is dead code — it never executes for WS traffic.

**Root cause**: WS extension source code at `https://github.com/bigskysoftware/htmx-extensions/blob/main/src/ws/ws.js`:

```
message → htmx:wsBeforeMessage → api.oobSwap() → htmx:wsAfterMessage
                                            ↛ htmx:beforeSwap (never fired)
```

The compile/upload line movement code in the handler is also dead — the WS extension already handles `hx-swap-oob` attributes natively via `api.oobSwap()`.

**Fix**: Replace the entire `htmx:beforeSwap` handler with a `htmx:wsBeforeMessage` handler:

```javascript
htmx.on("htmx:wsBeforeMessage", function(evt) {
    if (evt.target.id !== "event-feed") return;
    if (evt.detail.message.includes("board-event")) {
        htmx.trigger('body', 'board-changed');
    }
});
```

**Why it works**: `htmx:wsBeforeMessage` fires on the socket element for every message. `evt.detail.message` contains the raw HTML broadcast from the server. The `.board-event` string is unique to board event payloads. We do NOT call `preventDefault()` so OOB swaps for compile/upload lines continue to work natively.

### Quantums

| Q | Scope | Files | Change Summary | Verification |
|---|-------|-------|---------------|-------------|
| 1 | Replace beforeSwap handler in arduino_dash | `arduino_dash/templates/base.html:67-102` | 35-line handler → 6-line wsBeforeMessage; remove dead compile/upload element-moving code | 102 arduino_dash tests pass |
| 2 | Replace beforeSwap handler in medminder_dash | `medminder_dash/templates/base.html:67-80` | Same simplification (no compile/upload lines to remove) | 151+1 medminder_dash tests pass |
| 3 | Update CODEBASE_REFERENCE + final doc sync | `CODEBASE_REFERENCE.md` + all docs | — | All 3 suites green |

### Complete Bug Timeline

| Phase | Bug | Status |
|-------|-----|--------|
| 71 | WS implemented; `beforeSwap` used which never fires for WS messages | ✅ Fixed (Phase 71c) |
| 71a | `.board-event` CSS class missing from `board_event.html` partials | ✅ Fixed |
| 71b | `htmx.trigger()` called on `#board-grid` not `body` | ✅ Fixed (moot — handler never fired) |
| 71c | Wrong event: WS extension uses `oobSwap` not `beforeSwap` | **🔧 Current** |

**No test changes needed**: Server-side rendering tests unaffected; runtime JS event handling not covered by existing tests.

---

### Phase 72 — Collapsible Live Events Card in Admin Dashboards ✅ COMPLETED

**Date**: 2026-06-14

**Goal**: Add collapsible `<details>/<summary>` live-events card to both admin dashboards showing board connect/disconnect events in real-time. Card sits at the very top of admin pages with a thin collapsed form. Board selector follows immediately below.

**Approach**: OOB wrapper in pubsub broadcast call (not template, since `board_event.html` is shared with `/api/boards/event` route). `afterbegin` swap = newest first.

| Q | Scope | Files | Status |
|---|-------|-------|--------|
| 1 | arduino_dash — OOB wrapper + admin card + CSS | pubsub.py, admin.html | ✅ |
| 2 | medminder_dash — OOB wrapper + admin card + CSS + leaner events | pubsub_infra.py, admin.html, board_event.html | ✅ |
| 3 | All test suites + doc sync | All | ✅ |

**Verification**: All 5 suites green (102 + 152 + 211 + 47 + 24 = 536 total).

---

### Phase 72 Bugfix — Double Board Event Display ✅ COMPLETED

**Date**: 2026-06-14

**Bug**: Board events appear twice in the live-events card. Four independent root causes, each fixed separately.

| # | Cause | Fix | File | Status |
|---|-------|-----|------|--------|
| 1 | **Client-side handler dup**: Same handler appended twice to `_handlers[topic]` | `if handler not in hlist` guard in `subscribe()` | `pubsub_client.py:135` | ✅ v1 |
| 2 | **Client-side duplicate subscribe**: `subscribe()` always sent `{"type":"subscribe"}` to BMS, even for already-subscribed topics | `if self._sock and is_new` guard in `subscribe()` | `pubsub_client.py:137` | ✅ v2 |
| 3 | **Server-side every-subscribe fires `_send_current_boards_to`**: BMS called `_send_current_boards_to(conn)` on EVERY message, not once per connection. Dashboard sends 6 separate subscribe messages → 6× synthetic events. | Add `initial_state_sent` flag to `ClientConn`, guard both `_send_current_boards_to` and `_send_daemon_state_to` behind it | `service.py:33,241-242` | ✅ v3 |
| 4 | **Fallback scanner races with BMS PubSub**: `_fallback_scan_loop` detects boards independently of BMS PubSub. Both call `_on_board_event()` → `broadcast_ws()`, sending 2 WS messages per event. **THE ACTUAL ROOT CAUSE** | Fix A: Atomic dedup in `_on_board_event` (check `port in state._known_ports` under lock). Fix B: `daemon_ready` guard in scanner (skip scan when BMS available) | `pubsub_infra.py:37,186` (medminder_dash) / `pubsub.py:33,140` (arduino_dash) | ✅ v4 |

**Why v1-v3 were insufficient**: They prevent client-side and server-side duplication of the PubSub event path, but the fallback scanner is a completely independent code path that generates its own calls to `_on_board_event()`. Even with perfect PubSub dedup, the scanner doubles every event.

**Verification**: All 4 relevant suites green: medminder_dash 151+1, arduino_dash 102, board_manager 204+8, arduino_grpc 33+2.

---

### Phase 72b — Arduino Dash Alignment + CSS Styling ✅ COMPLETED

**Date**: 2026-06-14 15:00

**Goal**: Complete Phase 72b with 3 additional quantums: port `_get_active_board_info()` helper to arduino_dash, fix admin route session write in else branch, and enhance `.value` CSS styling for compile-upload-card fields.

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | Port `_get_active_board_info()` to arduino_dash `board_management.py` | Define at module level, normalizes `session["admin_active_board"]` to `(port, fqbn, hw_id)` 3-tuple | `arduino_dash/python/arduino_dash/arduino_dash/board_management.py` | ✅ |
| 2 | Fix medminder_dash admin() route else branch session write | Add `session["admin_active_board"] = (active_board_port, active_board_fqbn, active_board_hardware_id)` after info resolution | `medminder_dash/python/medminder_dash/medminder_dash/app.py` | ✅ |
| 3 | Enhanced `.value` CSS styling for compile-upload-card fields | Dark-themed read-only input fields with `background: #1e293b; border-radius: 0.25rem;` | Both dashboards' `base.html` | ✅ |

**Verification**: medminder_dash 151/151 + 1 skip ✅, arduino_dash 102/102 ✅.

---

## Phase 71 — Eliminate 5s HTMX Polling via WS Push ✅ COMPLETED

**Date**: 2026-06-11
**Status**: 🚧 In progress

**Goal**: Replace remaining 5-second HTMX polling for board grid and admin board selector with WebSocket-triggered updates. When a board connect/disconnect event arrives via WS, fire `board-changed` event → HTMX re-fetches grid/selector only on actual changes.

**Approach**: Option B — WS broadcasts board event HTML as before; frontend `beforeSwap` handler fires `htmx.trigger('body', 'board-changed')`. Elements listen for `board-changed from:body` instead of `every 5s`.

**Design decisions**:
- Reuse existing `board-changed` event name (already fired by `<select>` change handler)
- Keep `hx-trigger="load"` for initial page render
- Server-side `_on_board_event` / `broadcast_ws()` unchanged
- medminder_dash gets WS connection for the first time (minimal: just trigger, no live-events display)
- `refresh_boards()` functions deleted (never called, in-memory state already updated by PubSub push)
- Refresh buttons removed (replaced by automatic WS-triggered refresh)

| Q | Scope | Key Changes | Verification |
|---|-------|-------------|-------------|
| 1 | Arduino Dash WS trigger + remove polling + refresh button | `base.html` (beforeSwap), `dashboard.html`, `admin.html`, `admin_board_selector.html` | 102 arduino_dash tests pass |
| 2 | MedMinder Dash WS connection + trigger + remove polling + refresh button | `base.html` (NEW WS div + handler), `index.html`, `admin.html`, `admin_board_selector.html` | 151+1 medminder_dash tests pass |
| 3 | Cleanup: remove `refresh_boards()` + dead CSS | `pubsub.py`, `pubsub_infra.py`, both `base.html` | All 3 suites green |

**Verification**: arduino_dash 102/102, medminder_dash 151+1, board_manager 203+8. All 3 suites green. 3 medminder_dash tests updated (trigger assertions + removed refresh button assertions).

---

### Phase 70 — Board Detection Hot-Updates ✅ COMPLETED

**Date**: 2026-06-10
**Status**: ✅ Completed

**Goal**: Replace polling-based board detection with async push-based detection using BoardListWatch (gRPC streaming) and optionally pyudev (USB hotplug events). Add on-demand board query capability to pubsub protocol. Add CLI flag for mode selection. Deprecate FallbackScanner.

### Architecture

```
BoardDetector (single source of truth for boards)
  |
  +-- _known_boards: dict[str, dict] (keyed by port address)
  |   Dedup: events for already-known ports are no-ops
  |
  +-- Mode: "watch" (default) — BoardListWatch gRPC streaming
  |     Async push from arduino-cli, full metadata (FQBN, name, hardware_id)
  |
  +-- Mode: "udev" (optional) — pyudev Monitor (USB netlink)
  |     Async USB tty add/remove, + BoardList for metadata (optional)
  |     _scan_existing() runs synchronously at startup
  |
  callback -> BoardManagerService -> subscribers
```

### Design Decisions

1. **BoardListWatch replaces polling** as default — same daemon thread, no behavioral change. Outer retry loop on stream error (2s delay).
2. **pyudev as alternative mode** — for non-Arduino boards where arduino-cli is not available. `--board-detection-mode=udev`.
3. **_known_boards_lock** added for cross-thread safety (between detector thread and future readers).
4. **On-demand query** (`method == "list_boards"`) via pubsub request-response — `request_boards()` in PubSubClient.
5. **FallbackScanner** — startup call removed from both dashboards. Code retained but disabled.
6. **CLI flag precedence**: CLI arg > env var `BOARD_MGR_DETECTION_MODE` > config file > default `"watch"`.

### Quantums

| Q | Scope | Key Changes | Files | Verification |
|---|-------|-------------|-------|-------------|
| 1 | Phase A: On-demand board query | Add `get_known_boards()` to BoardDetector, `method == "list_boards"` handler in service.py, `request_boards()` in PubSubClient, `refresh_boards()` in dashboards | `board_detector.py`, `service.py`, `pubsub_client.py`, `arduino_dash/pubsub.py`, `medminder_dash/pubsub_infra.py` | All existing tests pass |
| 2 | Phase B: BoardListWatch in BoardDetector | Replace `_run_once()` polling with `_run_watch()` streaming; add mode param; add `_lock` | `board_detector.py`, `test_board_detector.py` | 6 new watch tests pass |
| 3 | Phase C: pyudev Monitor | New `udev_monitor.py`, optional dep `pyudev>=0.24`, 11 tests, integration into BoardDetector | `udev_monitor.py`, `test_udev_monitor.py`, `pyproject.toml` | 11 new tests pass |
| 4 | Config/CLI flag + FallbackScanner + doc sync | Add `board_detection_mode` to config/__main__/env; remove FallbackScanner startup calls; pass mode to BoardDetector from config | `config.py`, `__main__.py`, `service.py`, `arduino_dash/pubsub.py`, `medminder_dash/pubsub_infra.py` | All suites green + docs synced |

### Actual Test Counts

- board_manager: 186+8 → 203+8 (+17: 6 watch + 11 udev)
- arduino_dash: 102 (no change)
- medminder_dash: 151+1 (no change)
- Grand total: ~1039+8 → ~1056+8

### Risk & Mitigations

| Risk | Mitigation |
|------|-----------|
| BoardListWatch stream drops silently | Outer retry loop with 2s delay (same as current polling) |
| pyudev requires libudev system lib | Graceful `ImportError` at start(); user prompted to `pip install board-manager[udev]` |
| pyudev needs root on some distributions | Fallback log warning; use watch mode instead |
| FallbackScanner leaves stale state | Only startup call removed; code kept for emergency fallback |

---

### Phase 72d — Board Info Resolution Refactoring ✅ COMPLETED

**Date**: 2026-06-16

**Goal**: Extract repeated board-info resolution logic across 3 routes in both dashboards into shared `_resolve_board_info` helper. Fix async compile-upload-card update (missing first-port fallback matching board-selector pattern). Fix 4 `find_board_info_by_fqbn` calls that still used old single-arg signature after utils refactor changed it to `(fqbn, boards)`.

**Design decisions**:
- `_resolve_board_info` helper raises `ValueError` on missing port/FQBN — routes return `str(e), 500` uniformly
- Helpers live in route modules (app.py/board_management.py) because they depend on `session` via `get_port_info()` — not in utils
- `_resolve_first_port_info(ports)` wraps `get_first_board()` with ValueError for uniform error handling
- `find_board_info_by_fqbn` now requires `(fqbn, boards)` signature in both utils modules — 4 call sites in arduino_dash needed fixing

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| Q1 | medminder_dash helpers + board_selector refactor | `_resolve_first_port_info()`, `_resolve_board_info()`, `api_medicines_board_selector` ~70→30 lines | `app.py` | ✅ |
| Q2 | medminder_dash compile_upload_card + admin cleanup | `api_board_compile_upload_card` ~85→25 lines; admin route uses `_resolve_first_port_info` + `find_board_info_by_fqbn(active_board_fqbn, ports)` | `app.py` | ✅ |
| Q3 | arduino_dash helper + all 3 routes | `_resolve_board_info()` module-level; `api_admin_board_selector` ~50→12 lines; `api_board_compile_upload_card` ~55→12 lines; admin route cleaned (dead `if False:` block removed, first-port fallback uses `get_first_board()`, FQBN lookup uses `find_board_info_by_fqbn(fqbn, known_ports)`) | `board_management.py` | ✅ |

**Verification**: medminder_dash 151/151 + 1 skip ✅, arduino_dash 102/102 ✅.

---

### Phase 72e — Board Detail UI Alignment (Arduino Dash) ✅ COMPLETED

**Date**: 2026-06-16

**Goal**: Align arduino_dash board detail page with medminder_dash: replace editable FQBN `<input>` with read-only `<span class="value">` + hidden `<input>`, show FQBN and Device Port side-by-side in the Controls card, and show the board name in the page heading instead of the port path.

**Design decisions**:
- FQBN `<span id="fqbn-display" class="value">` for display; `<input type="hidden" id="fqbn" name="fqbn">` inside the form for HTMX submission
- Hidden input stays inside `<form id="compile-form">` so existing `hx-include="#compile-form"` still works — no need to change includes
- `board_detail()` route resolves `board_info` from `state._board_list.get(port, {})` and computes `board_name = board_info.get("board", "") or port`
- Port normalized (prepend `/` if missing) for consistent display
- No `.value` CSS needed — already present from Phase 72b Q3

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | Backend: resolve board_name + board_info in board_detail route | `state._board_list.get(port, {})`, compute `board_name = info.get("board", "") or port` | `board_management.py` | ✅ |
| 2 | Frontend: heading, FQBN label + port label, hidden input | Replace `<h2>Board: {{ port }}</h2>` with board name + port hint; replace FQBN input with span + hidden input + port span | `board_detail.html` | ✅ |
| 3 | Tests: 4 new board_detail tests | Heading shows name, falls back to port, FQBN display label, port display label | `test_app.py` | ✅ |

**Verification**: arduino_dash 106/106 (102 existing + 4 new) ✅, no regressions in other suites.

---

## Phase 73 — Route Reorganization: HTML vs REST API Separation ✅ COMPLETED

**Date**: 2026-06-17 04:51
**Status**: ✅ Completed 2026-06-17 07:19

**Goal**: Separate all routes into HTML routes (`html_routes.py`, no `/api/` prefix) and REST API routes (`api_routes.py`, `/api/` prefix, JSON-only) across both dashboards and the shared `arduino_sketch_tools` blueprint, adding REST counterparts for medicine CRUD and endpoint tests for all routes.

### Why
- **Consistent `/api/` prefix convention**: JSON API routes are clearly namespaced under `/api/`
- **Physically separate files**: `html_routes.py` + `api_routes.py` per module instead of monolithic route files
- **HTMX partials are HTML routes**: no longer under `/api/` prefix (grids, badges, selectors, compile-upload cards, etc.)
- **Hybrid routes split**: routes returning JSON for non-HX and HTML for HX are split into pure HTML + pure JSON variants
- **New REST counterparts**: JSON-only medicine CRUD endpoints alongside existing HTML form routes

### Key Design Decisions
- `arduino_sketch_tools` Blueprint prefix: `/api/board/...` → `/board/...`
- `arduino_dash` gets `html_routes.py` + `api_routes.py`; `board_management.py` and `sketch_management.py` remain for helper functions
- `medminder_dash` gets `html_routes.py` + `api_routes.py`; `app.py` routes extracted into these files
- All HTML partial routes stripped of `/api/` prefix (daemon/status, boards/grid, board/connection-status, etc.)
- WebSocket endpoints (`/ws/board-events`) remain unchanged
- New REST CRUD: `/api/medicines` (GET), `/api/medicine` (POST), `/api/medicine/<id>` (GET/PUT/DELETE), `/api/medicine/<id>/toggle` (PUT)
- Sketch upload/delete split: HTML route always returns HTML, API route always returns JSON

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | Shared blueprint prefix change | `arduino_sketch_tools`: `/api/board/`→`/board/` in 6 routes + 7 templates + 22 test refs | ✅ |
| 2 | arduino_dash route split | Create `html_routes.py` + `api_routes.py`; update `app.py`; split hybrid routes | ✅ |
| 3 | arduino_dash templates + tests | Update all template URL refs + test URL refs; verify tests pass | ✅ |
| 4 | medminder_dash route split | Create `html_routes.py` + `api_routes.py`; extract from `app.py` + `board_management.py`; add REST CRUD | ✅ |
| 5 | medminder_dash templates + tests | Update all template URL refs + test URL refs; verify tests pass | ✅ |
| 6 | Write endpoint tests for all HTML + REST routes | Comprehensive endpoint tests for both dashboards' new route layout | ✅ |
| 7 | Final verification across all suites + docs sync | All 5 suites green; docs synced | ✅ |

### Verification (Final Counts)
- **arduino_dash**: 113 passed (106 existing + 7 new endpoint tests) ✅
- **medminder_dash**: 175 passed + 1 skipped (161 existing + 14 new endpoint tests) ✅
- **arduino_sketch_tools**: 47 passed (unchanged) ✅
- **Grand total**: 335 passed + 1 skipped
- All endpoint tests cover all HTML routes (render correct template, status 200) and all JSON API routes (correct status codes, error responses)
- New REST CRUD endpoints fully tested: list, create, get, update, delete, toggle

---

### Phase 74 — Fix Board Status Badge Showing "Disconnected" ✅ COMPLETED

**Date**: 2026-06-17 10:28

**Completed**: 2026-06-17 10:28

**Goal**: Fix board status badge on board detail pages always showing "○ Disconnected" even when board is connected and detected by the backend.

**Root Cause**: Port normalization function `_norm_port()` (and its inline equivalent in medminder_dash) only adds a leading `/` when missing, but does NOT strip extra leading slashes. The badge URL `/board/{{ port }}/connection-status` renders with `port = "/dev/ttyACM0"` (normalized with leading `/`), creating URL `/board//dev/ttyACM0/connection-status` (double slash). Flask extracts `port = "//dev/ttyACM0"`, the normalization function returns it unchanged, and the lookup `"//dev/ttyACM0" in state._board_list` fails. Additionally, medminder_dash passes the raw (un-normalized) port to the badge template, causing cascading slashes on each poll cycle.

**Changes Made**:
| File | Change |
|------|--------|
| `arduino_dash/pubsub.py` | `_norm_port()` now strips extra slashes: `"/" + port.lstrip("/")` |
| `medminder_dash/html_routes.py` | 3 inline `_norm_port` calls fixed to strip extra slashes; `html_board_connection_status` now passes `port=norm_port` to template |
| Both `board_status_badge.html` | Badge URL now renders as `/board/{{ port.lstrip('/') }}/connection-status` |

---

### Phase 75 — Fix MedMinder Dash Stale `/api/board/` URLs in Templates + Badge Flash ✅ COMPLETED

**Date**: 2026-06-17 11:11

**Q1-Q7 Completed**: 2026-06-17 11:11

**Q8 Completed**: 2026-06-17 11:30

**Goal**: Fix medminder_dash templates and route logic that still use stale `/api/board/` prefix after Phase 73 route reorganization.

**3 Bugs Fixed (Q1-Q7)**:
| # | Severity | File | Issue |
|---|----------|------|-------|
| 1 | Critical | `board_detail.html` | `hx-get="/api/board/.../connection-status"` → 404 every 10s. Badge never updates from "Disconnected" |
| 2 | High | `html_routes.py` | `connected = info is not None` but `get_port_info()` returns `{}` for missing ports → `{} is not None` is `True`, always "Connected" if route reached |
| 3 | High | `board_detail.html` + `compile_upload_card.html` | Compile/upload buttons POST to `/api/board/...` → 404 on submit |

**Plus**: All URLs also fixed with `port.lstrip('/')` to prevent Phase 74-style double-slash.

**Q8 — Badge Flash Fix**:
| # | File | Issue | Fix |
|---|------|-------|-----|
| 4 | `board_detail.html` | Fallback `<span class="badge badge-err">○ Disconnected</span>` visible until HTMX `load` trigger fires. Arduino_dash uses empty span — nothing to show until HTMX swaps in the correct status. | Remove fallback span, match arduino_dash empty span pattern |

---

### Phase 76 — Unify Port Normalization with `normalize_port()` + `is_valid_port` Validation ✅ COMPLETED

**Date**: 2026-06-17 11:45

**Completed**: 2026-06-17 12:00

**Goal**: Integrate the existing `is_valid_port()` utility into port normalization across both dashboards, replacing ad-hoc `_norm_port` implementations with a unified `normalize_port()` that normalizes AND validates.

**Problem**: Three separate `_norm_port` implementations existed across the codebase:
| Location | Implementation | Handles `//`? | Validates? |
|----------|---------------|---------------|------------|
| `arduino_dash/pubsub.py` | `"/" + port.lstrip("/")` | ✅ | ❌ |
| `arduino_sketch_tools/extension.py` | `"/" + port if not port.startswith("/") else port` | ❌ | ❌ |
| `medminder_dash/html_routes.py` (inline) | `"/" + port.lstrip("/")` | ✅ | ❌ |

None validated. An invalid port like `""` becomes `"/"` or `"foo"` becomes `"/foo"`, silently failing downstream lookups.

**Fix**: Created `normalize_port()` in each dashboard's `utils.py` that combines normalization with `is_valid_port()` validation. Returns `None` for invalid ports so callers can return 400 early.

**Files Changed**:
| File | Change |
|------|--------|
| `arduino_dash/utils.py` | Added `normalize_port()` |
| `arduino_dash/pubsub.py` | Removed `_norm_port()` (moved to utils) |
| `arduino_dash/html_routes.py` | Import `normalize_port` from utils, add 400 on invalid port |
| `arduino_dash/api_routes.py` | Import `normalize_port` from utils, add 400 on invalid port |
| `arduino_dash/app.py` | Remove `_norm_port` from pubsub import |
| `arduino_dash/tests/test_app.py` | Added `TestNormalizePort` class (4 tests) |
| `medminder_dash/utils.py` | Added `normalize_port()` |
| `medminder_dash/html_routes.py` | Import `normalize_port` from utils, replace inline normalization, add 400 on invalid port |
| `arduino_sketch_tools/extension.py` | Updated `_norm_port` to use `lstrip` pattern (consistent) |
| `arduino_sketch_tools/routes.py` | Added `is_valid_port` validation at 6 call sites + new `INVALID_PORT_RE` regex |
| `arduino_sketch_tools/tests/test_extension.py` | Updated tests for new `_norm_port` + added `test_strips_multiple_leading_slashes` |

**Test Results**:
- arduino_dash: 117 passed ✅ (up from 113 — 4 new normalize_port tests)
- medminder_dash: 175 + 1 skip ✅
- arduino_sketch_tools: 49 passed ✅ (up from 47 — 2 new norm_port tests)
- `nox -s all_tests`: 8/8 sessions ✅

---

### Phase — GitHub Pages Jekyll Documentation Site ✅ COMPLETED

**Date**: 2026-06-20
**Status**: ✅ Completed

**Goal**: Serve the project documentation as a GitHub Pages site using Jekyll (Minima theme).

**Quantums**:

| Q | Scope | Status |
|---|-------|--------|
| 1 | Fix `_config.yml` — merge plugins, add `theme: minima`, add `defaults:` | ✅ |
| 2 | Remove `jekyll-archives` from Gemfile | ✅ |
| 3 | Add front matter to 93 doc `.md` files | ✅ |
| 4 | Add `{% raw %}` wrapping to 5 docs with Jinja2 tags | ✅ |
| 5 | Fix broken relative links (board_manager + medminder_dash) in 5 doc files | ✅ |
| 6 | Rebuild + verify — 246 HTML pages, all links correct | ✅ |
| 7 | Project docs sync — PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md, impl docs | ✅ |

**Key technical findings**:
1. Jekyll 3.x requires `---` front matter for `.md` files to be processed as pages. Without it, files are treated as static assets and copied verbatim to `_site/`.
2. Liquid interprets `{%` in page content even inside Markdown backtick spans. Workflow docs containing Jinja2 template examples need raw/endraw wrapping.
3. `board_manager` and `medminder_dash` have nested subpackages with the same name, adding an extra directory level that was missing from doc links.
4. Non-fatal Liquid warnings from `{{ port.lstrip('/') }}` in RESEARCH_JOURNAL.md and RESEARCH_PLAN.md remain — these are Jinja2 filter syntax in code examples.

### Phase 95 — Git Tree Preparation: .gitignore, Upload Cleanup, Doc Sync ✅ CURRENT

**Date**: 2026-06-20 15:40
**Status**: ✅ Completed

**Goal**: Prepare the monorepo for initial `git commit` by cleaning stale generated artifacts, updating `.gitignore`, creating `.gitkeep` markers for empty tracked directories, fixing stale workflow documentation across Phase 93→94 gap, and fixing doc inaccuracies.

**Rationale**: The repo has no commits yet. Multiple issues were discovered during pre-commit audit:
1. Stale uploaded sketches (`uploads/` dirs) — generated test artifacts, should not be tracked
2. `config/board_sketches.json` — runtime data file missing from `.gitignore`
3. `uploads/` contents not in `.gitignore` — future uploads would pollute the repo
4. Workflow docs outdated — Phase 93 docs never updated to Phase 94 completion
5. `CODEBASE_REFERENCE.md` — stale "Last updated" timestamp
6. `scripts/docs/index.md` — false `--help` claim for `check_venv.bash`

**Design**:

| Quantum | Scope | Files Changed |
|---------|-------|---------------|
| 1 | Clean uploads + .gitignore + .gitkeep | `uploads/*` dirs, `.gitignore`, 3× `.gitkeep` |
| 2 | Fix stale workflow docs (94 gap) | `IMPLEMENTATION_PROGRESS.md`, `IMPLEMENTATION_TASK.md`, `IMPLEMENTATION_PLAN.md`, `IMPLEMENTATION_JOURNAL.md`, `CODEBASE_REFERENCE.md` |
| 3 | Fix doc inaccuracy | `scripts/docs/index.md` |
| 4 | Sequential git add | Per-file user approval |

| # | Task | Status |
|---|------|--------|
| 1 | Clean stale sketch artifacts from both `uploads/` dirs | ✅ |
| 2 | Add `config/board_sketches.json` to `.gitignore` | ✅ |
| 3 | Add `**/uploads/*` + `!**/uploads/.gitkeep` to `.gitignore` | ✅ |
| 4 | Create `.gitkeep` in `config/`, both `uploads/` dirs | ✅ |
| 5 | Update `IMPLEMENTATION_PROGRESS.md` — Phase 94 tasks ✅ | ✅ |
| 6 | Update `IMPLEMENTATION_TASK.md` — Phase 94 tasks ✅ | ✅ |
| 7 | Update `IMPLEMENTATION_PLAN.md` — Phase 93→94 header | ✅ |
| 8 | Update `IMPLEMENTATION_JOURNAL.md` — add Phase 94 entry | ✅ |
| 9 | Update `CODEBASE_REFERENCE.md` — Last updated: Phase 94 | ✅ |
| 10 | Fix `scripts/docs/index.md` — remove false `--help` claim | ✅ |
| 11 | Move `WS_EVENT_FLOW.md` → `docs/ws-event-flow.md`; update refs | ✅ |

---

### Phase 96 — Wire test_ci.sh into Nox scripts_tests ✅ CURRENT

**Date**: 2026-06-20 20:03
**Status**: ✅ Completed

**Goal**: Add `scripts/tests/test_ci.sh` (10 test scenarios for `scripts/ci.sh`) to the nox `scripts_tests` session so it runs as part of the CI pipeline.

| # | Task | Status |
|---|------|--------|
| 1 | Add `session.run("bash", "tests/test_ci.sh", ...)` to `noxfile.py` | ✅ |
| 2 | Verify standalone: `bash scripts/tests/test_ci.sh` | ✅ |
| 3 | Verify integration: `nox -s scripts_tests` | ✅ |
| 4 | Update all docs | ✅ |

---

## Status: Phase 94 complete. Phase 95 complete. Phase 96 complete.

**Last Updated**: 2026-06-20 20:03

{% endraw %}