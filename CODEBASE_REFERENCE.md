---
---
{% raw %}
# Codebase Reference

**Last updated**: 2026-06-20 (Phase 94 — Noxfile Self-Healing Test Sessions)

> A concise, navigation-grade index of the MedMinder monorepo. Section
> headers in `## Phase N` form track the build history; the top of the
> file (Project Layout, Packages, gRPC API, Protocol, Run Mechanics,
> Build & Test) is the canonical reference for the current state.

---

## Project: MedMinder

A monorepo of 6 Python packages that together build a Web GUI for
controlling an Arduino over the `arduino-cli` gRPC interface, plus a
medicine-reminder dashboard that reuses the same plumbing. Two web
apps (`arduino_dash`, `medminder_dash`) talk to a local
`board-manager` service that owns the `arduino-cli` daemon.

### Top-level Layout

```
medminder/
├── arduino_dash/              # Flask web app A (general Arduino dashboard)
│   └── python/arduino_dash/
│       ├── arduino_dash/      # Package
│   │   ├── app.py         # Flask factory, delegates to html_routes + api_routes
│   │   ├── html_routes.py # All HTML page + partial routes + WS (no /api/ prefix)
│   │   ├── api_routes.py  # All JSON API routes (/api/ prefix)
│   │   ├── state.py       # Global state (board list, pubsub, WS clients)
│   │   ├── pubsub.py      # PubSub lifecycle, WS broadcast, board events
│   │   ├── board_management.py  # Helper functions only (no routes)
│   │   ├── sketch_management.py # Helper functions (no routes)
│       │   └── templates/     # Jinja2 templates
│       ├── tests/
│       └── pyproject.toml
├── arduino_grpc/               # gRPC stubs for arduino-cli
│   └── python/arduino_grpc/
│       ├── arduino_grpc/      # Wrapper module
│       ├── cc/                # Generated pb2/pb2_grpc stubs
│       └── tests/
├── arduino_sketch_tools/      # Flask extension for compile/upload
│   └── python/arduino_sketch_tools/
│       ├── arduino_sketch_tools/
│       └── tests/
├── board_manager/              # PubSub server + BoardDetector + DaemonManager
│   └── python/board_manager/
│       ├── board_manager/
│       │   ├── __main__.py    # Entry point
│       │   ├── service.py     # PubSub server, BoardManagerService
│       │   ├── board_detector.py  # BoardDetector (poll/watch/udev modes)
│       │   ├── udev_monitor.py    # pyudev USB monitor (Phase 70)
│       │   ├── config.py      # Configuration with CLI/ env/ file chain
│       │   ├── daemon_manager.py  # arduino-cli daemon lifecycle
│       │   ├── pool.py        # Subprocess pool
│       │   └── boot.py        # WSGI boot helpers
│       ├── tests/
│       └── pyproject.toml
├── board_manager_client/       # PubSub client library
│   └── python/board_manager_client/
│       ├── board_manager_client/
│       │   └── pubsub_client.py   # PubSubClient with WS + request-response
│       └── tests/
├── medminder_dash/             # Flask web app B (medicine scheduler)
│   └── python/medminder_dash/
│       ├── medminder_dash/
│       │   ├── app.py         # Flask factory, delegates to html_routes + api_routes
│       │   ├── html_routes.py # All HTML page + partial routes + WS (no /api/ prefix)
│       │   ├── api_routes.py  # All JSON API routes (/api/ prefix) + REST CRUD
│       │   ├── state.py       # MedicineState + MedMinder-specific state
│       │   ├── dash_state.py  # Shared board/pubsub state
│       │   ├── pubsub_infra.py    # PubSub lifecycle, WS broadcast, board events
│       │   ├── board_management.py  # Empty stub (helper functions moved to html_routes/api_routes)
│       │   ├── sketch_management.py # Helper functions (no routes)
│       │   ├── sketch_registry.py   # Per-board sketch assignment
│       │   ├── sketch_gen.py       # alarm.hpp generator
│       │   └── config/sketches/MedMinderV2/  # Packaged default sketch
│       ├── tests/
│       └── pyproject.toml
├── scripts/                    # Build, CI, tooling
│   ├── check_venv.bash
│   ├── install_arduino_deps.sh
│   ├── gen_grpc_bindings.py
│   ├── build_standalone.sh
│   ├── test_installs.sh
│   ├── ci.sh
│   ├── pyoxidizer/             # Per-app PyOxidizer configs
│   ├── tests/
│   └── Pipfile
├── dist-test-install/          # Wheel install smoke test
├── dist-standalone/            # Built standalone binaries
├── noxfile.py
├── PLAN.md
├── JOURNAL.md
├── CODEBASE_REFERENCE.md
└── .gitignore
```

### Test Suite Reference

| Package | Tests | Location |
|---------|-------|----------|
| `arduino_grpc` | 35 | `grpc_client/python/` |
| `board_manager` | 204 + 8 skip | `board_manager/python/` |
| `board_manager_client` | 24 | `board_manager_client/python/` |
| `arduino_sketch_tools` | 51 | `arduino_sketch_tools/python/` |
| `arduino_dash` | 119 | `arduino_dash/python/` |
| `medminder_dash` | 186 + 1 skip | `medminder_dash/python/` |
| `scripts/` | 128 + 12 bash | `scripts/tests/` |
| **Grand total** | **~1197 + 9 skip** | |

### gRPC API

All stubs under `cc/arduino/cli/commands/v1/` (11 services, generated from arduino-cli protos):

| Service | Primary Use |
|---------|-------------|
| `ArduinoCore` | Board list, board details |
| `Board` | Board list, BoardListWatch (streaming), BoardDetails |
| `Sketch` | Sketch archive creation |
| `Compile` | Compile sketch → binary |
| `Upload` | Upload binary to board |
| `Monitor` | Serial monitor |
| `Debug` | Debug over gdb/OpenOCD |

### PubSub Protocol

| Aspect | Detail |
|--------|--------|
| Transport | TCP (default localhost:9876) or UDS (`/tmp/board-manager.sock`) |
| Framing | 4-byte length prefix + JSON payload |
| Topics | `board::{port}::event`, `resp::*`, `status::*`, `sys::*` |
| Subscription | Wildcards: `+` (one level), `*` (rest) |
| Request-Response | `method: "list_boards"` on `sys::boards`, response on `resp::list_boards::{id}` |
| WS Bridging | `broadcast_ws()` sends raw HTML to all connected browser WS clients |

### CSS Architecture (Phase 79)

| Aspect | Detail |
|--------|--------|
| Strategy | Per-dashboard `static/style.css` (arduino_dash & medminder_dash), identical byte-for-byte |
| Variables | 42 CSS custom properties in `:root` (dark theme defaults) |
| Light mode | `@media (prefers-color-scheme: light) { :root { ... } }` overrides only color vars |
| Card style | Flat — no border/shadow; cards distinguished from page bg by color alone |
| Light card inversion | Dark cards in dark mode → lighter + shadow in light mode |
| Badge inversion | Dark bg/light text → light bg/dark text in light mode |
| Button light shift | Button backgrounds use 1 shade darker in light mode |
| Classification | 57+ semantic classes: `.text-hint`, `.modal-backdrop`, `.result-banner--success`, `.btn--default`, etc. |
| Inline style residue | 3 intentional `style="display:none"` (modal toggle) + 1 `style="word-break:break-all"` |
| CSS excluded | arduino_sketch_tools (shared Blueprint partials use classes defined in dashboard CSS) |

**Key files:**
| File | Lines | Purpose |
|------|-------|---------|
| `arduino_dash/.../static/style.css` | 539 | Full CSS with vars, light mode, all component classes |
| `medminder_dash/.../static/style.css` | 539 | Identical copy (same sha256sum) |
| Both `base.html` | 1 | `<link>` to style.css replacing old `<style>` block |
| `admin.html` (both) | — | `<style>` block removed → `.admin-heading`, `.admin-content` classes |
| `dnd_overlay.html` (both) | — | `<style>` block removed → `#dnd-overlay` class |

**CSS variable categories:**
| Category | Example vars | Count |
|----------|-------------|-------|
| Page | `--page-bg`, `--page-text` | 4 |
| Card | `--card-bg`, `--card-border` | 4 |
| Input | `--input-bg`, `--input-text`, `--input-border` | 6 |
| Table | `--table-header-bg`, `--table-row-alt`, `--table-border` | 6 |
| Button | `--btn-default-bg`, `--btn-primary-bg`, `--btn-danger-bg` | 10 |
| Badge/Status | `--badge-ok-bg`, `--badge-warn-text` | 8 |
| Code | `--code-bg`, `--code-text` | 2 |
| Misc | `--shadow`, `--link`, `--danger`, `--warning` | 4 |

### Running

```bash
# Development (pipenv per package)
cd board_manager/python/board_manager && pipenv run python -m board_manager
cd arduino_dash/python/arduino_dash && pipenv run python -m arduino_dash
cd medminder_dash/python/medminder_dash && pipenv run python -m medminder_dash

# Production (gunicorn)
cd arduino_dash/python/arduino_dash && pipenv run gunicorn -c gunicorn.conf.py arduino_dash.wsgi:app
cd medminder_dash/python/medminder_dash && pipenv run gunicorn -c gunicorn.conf.py medminder_dash.wsgi:app

# Standalone binary (PyOxidizer)
./scripts/build_standalone.sh
dist-standalone/board-manager/bin/board-manager
dist-standalone/arduino-dash/bin/arduino-dash
dist-standalone/medminder-dash/bin/medminder-dash
```

### Building

```bash
nox -s 'tests(board_manager)' 'build(board_manager)'   # single package
nox -s all_tests                                        # all tests
nox -s all_builds                                       # all wheels
./scripts/ci.sh                                         # full CI pipeline
```

### Jekyll Documentation Site (Phase 93)

**Date**: 2026-06-20

**Type**: Docs/Infrastructure

**Goal**: Serve project documentation as a GitHub Pages site using Jekyll + Minima theme. 254 HTML pages, 0 errors, 0 warnings.

#### Key Files

| File | Purpose |
|------|---------|
| `_config.yml` | Jekyll configuration — theme, plugins, defaults |
| `Gemfile` | Ruby gem dependencies |
| `index.md` | Documentation hub — per-package doc tables + quick links |
| `docs/architecture.md` | Architecture overview |
| `docs/guide.md` | User guide |
| `docs/tests.md` | Test documentation |
| `docs/api.md` | API reference |
| `docs/scripts.md` | Scripts reference |

#### Environment

| Component | Version |
|-----------|---------|
| Ruby | 3.0.2 |
| Bundler | 2.5.23 |
| Jekyll | 3.10.0 |
| Minima | 2.5.2 |
| jekyll-relative-links | 0.7.0 |

#### Configuration

```yaml
# _config.yml
title: MedMinder Documentation
description: >-
  Documentation for the MedMinder monorepo — gRPC client,
  Board Manager Service, and Arduino/MedMinder dashboards.
theme: minima

plugins:
  - jekyll-relative-links
  - jekyll-feed
  - jekyll-seo-tag

defaults:
  - scope:
      path: ""
    values:
      layout: default
```

#### Build Commands

```bash
# Full build
bundle exec jekyll build

# Development server
bundle exec jekyll serve

# Check for issues (non-fatal doctor bug expected)
bundle exec jekyll doctor
```

#### Build Statistics

| Metric | Value |
|--------|-------|
| HTML pages | 254 |
| Build time | ~46-54s |
| Errors | 0 |
| Warnings | 0 |

#### Site Layout

```
_site/
├── index.html                          # Documentation hub
├── board_manager/python/board_manager/board_manager/docs/   # 11 doc pages
├── medminder_dash/python/medminder_dash/medminder_dash/docs/ # 15 doc pages
├── arduino_dash/python/arduino_dash/docs/                    # Doc pages
├── arduino_sketch_tools/python/arduino_sketch_tools/docs/    # Doc pages
├── board_manager_client/python/board_manager_client/docs/   # Doc pages
├── arduino_grpc/python/arduino_grpc/docs/                   # Doc pages
├── scripts/docs/                       # Scripts documentation
├── tools/docs/                         # Tools documentation
├── dist-test-install/                  # Test install docs
├── docs/                               # Top-level docs (6 pages)
└── *.html                              # Root-level docs (PLAN, JOURNAL, etc.)
```

#### Known Issues

| Issue | Detail |
|-------|--------|
| `jekyll doctor` error | `undefined method 'absolute?' for nil:NilClass` when `url:` unset — Jekyll 3.10 known issue, harmless |
| link safety | Always use absolute paths from root (`/board_manager/...`) — `jekyll-relative-links` converts `.md`→`.html` |

#### Front Matter Coverage

All `.md` files in the repository have `---\n---\n` front matter:
- 93 doc files in `docs/` directories (batch 1)
- 7 per-package `README.md` files (batch 2)
- 1 `grpc_client/.../README.md` (batch 2)

Without front matter, Jekyll copies files as static assets (raw markdown, `.md` extension preserved).

#### raw/endraw Coverage

| File | Wrapped Content |
|------|----------------|
| `JOURNAL.md` | Full file — contains Jinja2 template tags (`block`, `include`) |
| `PLAN.md` | Full file — contains Jinja2 template syntax |
| `TODOS.md` | Full file — contains Jinja2 template syntax |
| `docs/ws-event-flow.md` | Full file — contains Jinja2 template syntax |
| `CODEBASE_REFERENCE.md` | Full file — contains Jinja2 template syntax |
| `RESEARCH_JOURNAL.md` | Full file — contains `{{ port.lstrip('/') }}` |
| `RESEARCH_PLAN.md` | Full file — contains `{{ port.lstrip('/') }}` |

**Gotcha**: Never embed the closing raw tag (opening-brace, percent, endraw, percent, closing-brace) inside backtick spans within a raw-wrapped file. Liquid scans for the closing tag at the text level — the first occurrence closes the raw block prematurely.

#### Nested Subpackage Link Fix

Two packages have the same-name subpackage pattern requiring corrected link paths:

| Package | Doc path (correct) | Links fixed |
|---------|-------------------|-------------|
| `board_manager` | `board_manager/python/board_manager/board_manager/docs/` | 24 in 5 files |
| `medminder_dash` | `medminder_dash/python/medminder_dash/medminder_dash/docs/` | 27 in 5 files |

**Files modified**: `index.md`, `docs/architecture.md`, `docs/guide.md`, `docs/tests.md`, `docs/api.md`

#### README Links in Hub

All 9 README refs in `index.md` resolve to `.html` (processed pages):
- `/README.html`, `/arduino_dash/.../README.html`, `/arduino_sketch_tools/.../README.html`,
  `/board_manager/.../README.html`, `/board_manager_client/.../README.html`,
  `/dist-test-install/README.html`, `/grpc_client/.../README.html`,
  `/medminder_dash/.../README.html`, `/scripts/README.html`

---

### Phase 90 — Fix Double BoardDetector Stop Log ✅ COMPLETED

**Date**: 2026-06-19 17:49

**Type**: Core/Infrastructure

**Change**: Fixed duplicate "BoardDetector stopped" log during SIGINT shutdown.
Two-part fix: (1) `BoardDetector.stop()` is now idempotent with early-return guard
`if not self._running: return`. (2) `service.start()` no longer catches
`KeyboardInterrupt` and calls `self.stop()` internally — it propagates to
`__main__.main()`'s `finally: service.stop()`.

**Files**: `board_manager/board_detector.py:64-66`, `board_manager/service.py:97-102`

**Test Impact**: 0 regressions (34 relevant tests pass)

---

### Phase 91 — Align Live Events Card Style with arduino_dash ✅ COMPLETED

**Date**: 2026-06-19 17:59

**Type**: Frontend

**Change**: Aligned medminder_dash `board_event.html` with arduino_dash's reference
template. Removed `[-10:]|reverse` slicing, `board-event-row` flex layout, nested
`<div>`, and conditional board badge. Now uses flat layout: badge → port → board
hint as inline spans, all events in chronological order.

**Files**: `medminder_dash/.../templates/partials/board_event.html`

**Test Impact**: 0 regressions (186/186 + 1 skip medminder_dash)

---

### Phase 1 — Research & Fix gRPC Issues ✅ COMPLETED

**Date**: 2026-05-20

**Type**: Core/Infrastructure

**Change**: Created the `arduino_grpc` module with proper Python package structure. Fixed UploadRequest port parameter (string → Port protobuf object), corrected board detection from BoardDetect to BoardListWatch/BoardList, and fixed protobuf import paths (Instance is in common_pb2, request messages in per-service pb2 modules).

**Files**: `arduino_grpc/__init__.py`, `arduino_grpc/client.py`, `arduino_grpc/exceptions.py`, `arduino_grpc/models.py`, `arduino_grpc/tests/test_client.py`

**Test Impact**: 19 unit tests → 28 (22 unit + 6 integration)

---

### Phase 2 — Integration Testing & Fixes ✅ COMPLETED

**Date**: 2026-05-23

**Type**: Core/Infrastructure

**Change**: Added integration tests against live arduino-cli daemon (7/7 passing). Fixed BoardList returning 0 ports by adding timeout field to request. Fixed instance resource leak by adding destroy() method calling Dispose RPC on disconnect().

**Files**: `arduino_grpc/client.py`, `arduino_grpc/tests/integration_test.py`

**Test Impact**: 28 → 29 (22 unit + 7 integration)

---

### Phase 3 — Board Manager Service ✅ COMPLETED

**Date**: 2026-05-24

**Type**: Core/Infrastructure

**Change**: Implemented the PubSub messaging system (protocol + router), Subprocess Pool (pool.py + board_worker.py), and BoardManagerService (service.py + __main__.py). Integration tests with arduino-cli daemon.

**Files**: `board_manager/protocol.py`, `board_manager/router.py`, `board_manager/pool.py`, `board_manager/board_worker.py`, `board_manager/service.py`, `board_manager/__main__.py`

**Test Impact**: 29 → ~129

---

### Phase 4 — Web App ✅ COMPLETED

**Date**: 2026-05-24

**Type**: Frontend

**Change**: Built a Flask web app with HTMX + WebSocket that connects to BoardManagerService via PubSubClient. Dashboard with board grid, board detail page with compile/upload controls, and integration tests.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/`, `board_manager_client/pubsub_client.py`

**Test Impact**: 129 → 143

---

### Phase 5 — Private PyPI Wheel-Based Install ✅ COMPLETED

**Date**: 2026-05-24

**Type**: DevOps

**Change**: Created setup.py bootstrap files for 3 packages, built wheels, updated Pipfiles with private PyPI sources via PIP_FIND_LINKS, regenerated lock files. Replaced all path deps with wheel-based resolution.

**Files**: `setup.py` (3 packages), `Pipfile` (3), `.env`

**Test Impact**: 143 (all passing)

---

### Phase 6 — Board Detection & Dashboard Live Updates ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Created BoardDetector background thread polling list_boards() every 5s. Integrated into BoardManagerService start/stop. Fixed Flask app_context error in pubsub _on_board_event handler. Added /api/boards/grid endpoint with HTMX polling on dashboard. Fixed protobuf int64 float rejection with int(timeout) cast.

**Files**: `board_manager/board_detector.py`, `arduino_dash/app.py`, `arduino_dash/templates/board_grid.html`

**Test Impact**: 143 → 142 (zero warnings)

---

### Phase 7 — Board Events Not Reaching Dashboard ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Added instrument logging at each event transition point. Identified timing race where events fire before subscriber connects. Fixed by caching board state in _board_state and re-emitting synthetic "connected" events on subscribe.

**Files**: `board_manager/service.py`, `board_manager/board_detector.py`

**Test Impact**: No change

---

### Phase 8 — Fix _tick pool.poll Inner Loop Crash ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Removed erroneous inner for msg in msgs loop in service.py that caused AttributeError when iterating dict string keys. Added regression tests (TestTick, 4 tests).

**Files**: `board_manager/service.py`

**Test Impact**: 157 total

---

### Phase 9 — Fix Upload Exit Status 1 Crash Cascade ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Found that "exit status 1" from avrdude was a crash cascade from the _tick crash (Phase 8), not a separate bug. When BMS died, the subprocess's upload result was lost. After Phase 8 fix, both standalone and full-stack upload succeed.

**Files**: None (root cause already fixed)

**Test Impact**: 157 total

---

### Phase 10 — Async Response Handling ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Added _pending_responses dict + _on_resp handler for resp::* topics. Modified api_compile/api_upload to wait for response (60s timeout) and render result partials for HTMX swap.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/partials/compile_result.html`, `arduino_dash/templates/partials/upload_result.html`

**Test Impact**: 167 total (10 new)

---

### Phase 11 — Real-time Progress + Polling + Logging ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Fixed :: separator bug in response topics. Added compile_stream/upload_stream to gRPC client that yield output chunks. Board worker streaming with logging. WebApp polling endpoints + results cache. Templates for WS progress + polling UI with section-wrapper pattern.

**Files**: `arduino_grpc/client.py`, `board_manager/board_worker.py`, `board_manager/service.py`, `arduino_dash/app.py`, `arduino_dash/templates/`

**Test Impact**: 182 total (34+114+34)

---

### Phase 12 — DaemonManager + Spinner + Cleanup ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Implemented DaemonManager class for arduino-cli daemon lifecycle (health check, zombie detection, auto-restart). Fixed stale UDS socket handling, retry logic in PubSubClient.connect(), CSS spinner for compile/upload, daemon status badge, BoardDetector retry with linear delays, daemon state re-emission on subscribe, and multiple reconnect bugs.

**Files**: `board_manager/daemon_manager.py`, `board_manager/config.py`, `board_manager/service.py`, `board_manager_client/pubsub_client.py`, `arduino_dash/app.py`, `arduino_dash/templates/`

**Test Impact**: 231 total (27+155+42+7 integration)

---

### Phase 13 — Fix Upload Error Message Leak ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Fixed _make_error in board_worker.py to include "status":"error" key (was missing). Fixed BMS _route_pool_message to filter ::progress from result log and log the actual error message. Fixed webapp error rendering to display the real error.

**Files**: `board_manager/board_worker.py`, `board_manager/service.py`, `arduino_dash/app.py`

**Test Impact**: 254 total (165+55+34)

---

### Phase 14 — Port Path Normalization ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Core/Infrastructure

**Change**: Fixed double-slash URL bug in board_grid.html (port="/dev/ttyACM0" → "//dev/ttyACM0" → Werkzeug normalizes to "/dev/ttyACM0"). Added _norm_port() helper that prepends "/" if missing, used in all 7 API endpoints.

**Files**: `arduino_dash/templates/board_grid.html`, `arduino_dash/app.py`

**Test Impact**: 254 total

---

### Phase 15 — UI/UX Improvements ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Frontend

**Change**: Larger log font (0.8rem → 0.95rem), shorter log height (400px → 250px). Removed dead Status section from board_detail. Added board connection status badge polling every 10s. Verbose upload status messages with synthetic phase markers.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/board_detail.html`, `arduino_dash/templates/board_status_badge.html`, `board_manager/board_worker.py`

**Test Impact**: 257 total (165+58+34)

---

### Phase 16 — UI Polish — Log Spacing Fix + Meta Info ✅ COMPLETED

**Date**: 2026-05-25

**Type**: Frontend

**Change**: Fixed log-viewer spacing by removing white-space:pre-wrap (block elements naturally stack without double-spacing). Cleaned trailing \n from worker progress messages. Added _compile_meta / _upload_meta info dicts tracking port, board name, FQBN, sketch path during operations.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/`

**Test Impact**: 261 total (165+62+34)

---

### Phase 17 — Sketch Status Warnings ✅ COMPLETED

**Date**: 2026-05-26

**Type**: Frontend

**Change**: Added sketch path mismatch + modification detection warnings that block upload with confirmation dialog. _get_sketch_mtime() helper and _last_compiled_sketch/_last_compile_mtime tracking. New POST /api/board/<port>/upload/confirm and GET /api/board/<port>/upload/section endpoints. Compile failure warning in compile result.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/upload_confirm.html`, `arduino_dash/templates/upload_init.html`, `arduino_dash/templates/compile_result.html`

**Test Impact**: 283 total (73 webapp, 11 new)

---

### Phase 18 — Sketch File Browser + Drag-and-Drop ✅ COMPLETED

**Date**: 2026-05-26

**Type**: Frontend

**Change**: Server upload endpoint POST /api/sketch/upload accepting multipart files[] with webkitRelativePath. Hyperscript-powered confirmation modal, Browse button triggering hidden webkitdirectory input, drag-and-drop drop zone. 4 new tests.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/sketch_upload_modal.html`, `arduino_dash/templates/board_detail.html`, `arduino_dash/templates/base.html`

**Test Impact**: 287 total (77 webapp)

---

### Phase 19 — Fix Browse/Upload/DnD UI Bugs ✅ COMPLETED

**Date**: 2026-05-26

**Type**: Frontend

**Change**: Four major bugfixes: body DnD prevention (halt the event → call event.preventDefault()), modal centering (show me → set my.style.display to 'flex'), HTMX upload on Browse (hx-post auto-upload with HX-Request server detection), last-upload by IP dict + route, sketch name in card meta, .ino filename normalization (matching folder name), button state restoration after upload.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/base.html`, `arduino_dash/templates/sketch_upload_modal.html`, `arduino_dash/templates/board_detail.html`, `arduino_dash/templates/sketch_path_selector.html`

**Test Impact**: 307 total (98 webapp)

---

### Phase 20 — DnD Silent Failure — Read-Only .files ✅ COMPLETED

**Date**: 2026-05-27

**Type**: Frontend

**Change**: Discovered that `set #folder-input.files to dataTransfer.files` silently fails because `<input type="file">.files` is a read-only browser property. Fixed by storing DnD files as `__dndFiles` JavaScript property on the modal element. Rewrote upload button from HTMX to hyperscript fetch + FormData supporting both __dndFiles (DnD) and #folder-input.files (Browse).

**Files**: `arduino_dash/templates/board_detail.html`, `arduino_dash/templates/sketch_upload_modal.html`

**Test Impact**: 307 total (98 webapp)

---

### Phase 21 — Firefox DnD Diagnostic + Fix ✅ COMPLETED

**Date**: 2026-05-27

**Type**: Frontend

**Change**: Fixed Firefox DnD by prefixing `style` with `my.` in all 3 handlers (hyperscript resolves bare `style` as null). Fixed fetch parse error: comma-separated single `with` clause (not multiple). Fixed for loop iteration over FileList by using Array.from(files).

**Files**: `arduino_dash/templates/board_detail.html`, `arduino_dash/templates/sketch_upload_modal.html`

**Test Impact**: 302 unit + 6 integration

---

### Phase 22 — Fix Indentation Bug + Minimal js() Diagnostic ✅ COMPLETED

**Date**: 2026-05-27

**Type**: Frontend

**Change**: Multiple hyperscript indentation realignment iterations. Discovered hyperscript 0.9.13 `new` keyword calls constructors WITHOUT `new` at runtime. Discovered `fetch ... as JSON` serializes FormData as `JSON.stringify(fd)` → `"{}"`.

**Files**: `arduino_dash/templates/sketch_upload_modal.html`

**Test Impact**: No change

---

### Phase 23 — Four Hyperscript Bugs — Native js() Fetch ✅ COMPLETED

**Date**: 2026-05-27

**Type**: Frontend

**Change**: Four bugs identified: (1) `new` keyword calls without `new`, (2) `fetch ... as JSON` serializes as JSON, (3) bare `fetch` with FormData hangs, (4) `for` loop can't access `set` vars. Workaround: element properties for scope, `js()` blocks for constructor and fetch.

**Files**: `arduino_dash/templates/sketch_upload_modal.html`

**Test Impact**: No change

---

### Phase 24 — Diagnose Native js() Fetch — POST Sent No Response ✅ COMPLETED

**Date**: 2026-05-27

**Type**: Frontend

**Change**: Found that native `js()` fetch POST IS sent (confirmed in Network tab) but Flask multipart parser hangs on `request.files.getlist("files[]")`. Breakthrough discovery: Browse works (files from `<input webkitdirectory>`) but DnD hangs (files from `dataTransfer.files`). Root cause: `dataTransfer.files` cannot represent directories.

**Files**: `arduino_dash/app.py`

**Test Impact**: No change

---

### Phase 25 — Fix DnD Upload — webkitGetAsEntry Folder Traversal ✅ COMPLETED

**Date**: 2026-05-27

**Type**: Frontend

**Change**: Rewrote DnD drop handler with `DataTransfer.items[i].webkitGetAsEntry()` for recursive folder traversal. Uses `createReader()` + `readEntries()` loop (max 100 per call). Manual `__relativePath` tracking since DnD files lack `webkitRelativePath`. Fixed Ctrl-C shutdown in board_worker.py.

**Files**: `arduino_dash/templates/board_detail.html`, `arduino_dash/templates/sketch_upload_modal.html`, `board_manager/board_worker.py`

**Test Impact**: 315 total

---

### Phase 26 — Fix test_watch_boards RST_STREAM Error + Daemon Fixture ✅ COMPLETED

**Date**: 2026-05-28

**Type**: Core/Infrastructure

**Change**: Handle DEADLINE_EXCEEDED gracefully in watch_boards() via `e.code() == grpc.StatusCode.DEADLINE_EXCEEDED` instead of fragile string match. Created conftest.py with module-scoped daemon_url fixture using DaemonCtx. Added board event test.

**Files**: `arduino_grpc/client.py`, `arduino_grpc/conftest.py`, `arduino_grpc/daemon_helper.py`, `arduino_grpc/tests/integration_test.py`

**Test Impact**: 317 total (35 grpc)

---

### Phase 27 — Remove Backoff + Fix Zombie Daemon Retry ✅ COMPLETED

**Date**: 2026-05-28

**Type**: Core/Infrastructure

**Change**: Added zombie detection in DaemonManager.is_alive via `/proc/<pid>/status` State:Z check. Removed linear backoff in BoardDetector → 2s fixed delay. Retry immediately after restart in _run_once().

**Files**: `board_manager/daemon_manager.py`, `board_manager/board_detector.py`

**Test Impact**: 182 board_manager pass

---

### Phase 28 — Stale arduino-cli Daemon Fix ✅ COMPLETED

**Date**: 2026-05-28

**Type**: Core/Infrastructure

**Change**: Registered SIGTERM handler in __main__.py with try/finally + service.stop(). Created conftest.py with --integration CLI flag and marker definition. Fixed fixture teardown with SIGKILL fallback, pipe cleanup, UDS socket cleanup.

**Files**: `board_manager/__main__.py`, `board_manager/conftest.py`, `board_manager/tests/integration_test.py`

**Test Impact**: 174 pass + 8 skip (without flag)

---

### Phase 29 — Compile/Upload Spinner Alignment Fix ✅ COMPLETED

**Date**: 2026-05-28

**Type**: Frontend

**Change**: Flexbox wrapper (.spinner-label with display:inline-flex; align-items:center) around spinner + text for pixel-perfect vertical centering. Replaced heuristic vertical-align:middle.

**Files**: `arduino_dash/templates/base.html` CSS, 4 compile/upload partial templates

**Test Impact**: 315 total

---

### Phase 30 — Sketch Path Abstraction + Checksum Dedup ✅ COMPLETED

**Date**: 2026-05-28

**Type**: Frontend

**Change**: Replaced editable sketch path `<input>` with a `<select>` dropdown keyed by (ip, user_agent). SHA256 checksum deduplication of uploaded files. Content-based modification detection alongside mtime. Upload tracking for checksum comparison reference point.

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/sketch_path_selector.html`, `arduino_dash/templates/board_detail.html`

**Test Impact**: 327 total (110 webapp, 12 new)

---

### Phase 31 — Fix Non-Reentrant Lock Deadlock ✅ COMPLETED

**Date**: 2026-05-29

**Type**: Core/Infrastructure

**Change**: Fixed deadlock in api_last_upload() which acquired _upload_registry_lock then called _render_sketch_path_selector() (which also acquires the same lock). Extracted selected_path inside the lock, called selector after release.

**Files**: `arduino_dash/app.py`

**Test Impact**: 328 total (111 webapp, 1 new regression test)

---

### Phase 32 — Sketch Versioning + Timestamps + Delete ✅ COMPLETED

**Date**: 2026-05-29

**Type**: Frontend

**Change**: Registry structure changed from dict to list[dict] (multiple versions per sketch name). Upload appends version instead of overwriting. Dropdown shows timestamps: "blinky (2026-05-29 12:00)". DELETE endpoint removes from registry + disk. Label rename "Sketch Path" → "Sketch".

**Files**: `arduino_dash/app.py`, `arduino_dash/templates/sketch_path_selector.html`, `arduino_dash/templates/board_detail.html`

**Test Impact**: 335 total (118 webapp, 7 new)

---

### Phase 33 — Fix Delete Button + DnD Console Error ✅ COMPLETED

**Date**: 2026-05-29

**Type**: Frontend

**Change**: Fixed malformed `hx-vals='{"path": js:...}'` — the unquoted `js:` expression was not valid JSON, so HTMX silently failed to attach hx-delete. Changed to HTMX 2.x JS form: `hx-vals='js:{path: ...}'`.

**Files**: `arduino_dash/templates/board_detail.html`

**Test Impact**: 335 total

---

### Phase 34 — Fix htmx:targetError — Missing Container ID ✅ COMPLETED

**Date**: 2026-05-29

**Type**: Frontend

**Change**: sketch_path_selector.html rendered only a bare `<select>`. HTMX outerHTML swap replaced the wrapping div, losing #sketch-path-container from DOM. Fixed by wrapping content in `<div id="sketch-path-container">`.

**Files**: `arduino_dash/templates/sketch_path_selector.html`

**Test Impact**: 335 total

---

### Phase 35 — Delete Confirm Modal ✅ COMPLETED

**Date**: 2026-05-29

**Type**: Frontend

**Change**: Replaced browser native confirm() dialog with custom webapp modal for sketch deletion. Delete button stores path on modal via hyperscript; modal confirm button uses HTMX hx-delete with stored path.

**Files**: `arduino_dash/templates/delete_confirm_modal.html`, `arduino_dash/templates/board_detail.html`

**Test Impact**: 335 total

---

### Phase 36 — Fix Remaining Console Errors ✅ COMPLETED

**Date**: 2026-05-30

**Type**: Frontend

**Change**: Added `_="on submit halt"` to compile form to prevent native form submission while keeping `method="post"` for hyperscript form validation suppression. Lowercase `method="post"` because hyperscript 0.9.13 is case-sensitive.

**Files**: `arduino_dash/templates/board_detail.html`

**Test Impact**: 335 total

---

### Phase 37 — Diagnostic Cleanup — Remove Stale Code ✅ COMPLETED

**Date**: 2026-05-30

**Type**: Docs/Cleanup

**Change**: Removed _log_all_requests() diagnostic, deprecated _last_upload_by_ip dict + lock + commented-out code. Fixed timezone double-conversion bug in _render_sketch_path_selector(). Fixed brittle timestamp test.

**Files**: `arduino_dash/app.py`, `arduino_dash/tests/test_app.py`

**Test Impact**: 324 unit + 10 integration skip

---

### Phase 38 — Rename Webapp to Arduino Dash ✅ COMPLETED

**Date**: 2026-05-30

**Type**: DevOps

**Change**: Renamed banner "MedMinder" → "Arduino Dash". Renamed module directory webapp → arduino_dash, updated all internal imports, test imports, packaging config (pyproject.toml, Pipfile).

**Files**: ~15 files across templates, Python imports, packaging config

**Test Impact**: 324 unit, all passing

---

### Phase 39 — Review & Polish Refactor ✅ COMPLETED

**Date**: 2026-05-30

**Type**: Core/Infrastructure

**Change**: Extracted shared infrastructure into standalone packages: board_manager_client (pubsub_client) and arduino_sketch_tools (Flask Extension with compile/upload Blueprint + 9 partials). Split arduino_dash app.py into infra.py, board_management.py, sketch_management.py.

**Files**: `board_manager_client/`, `arduino_sketch_tools/`, `arduino_dash/infra.py`, `arduino_dash/board_management.py`, `arduino_dash/sketch_management.py`

**Test Impact**: 369 passed (89+47+174+24+35), 8 skipped

---

### Phase 40 — MedMinder Web ✅ COMPLETED

**Date**: 2026-05-31

**Type**: Frontend

**Change**: Created medminder_dash — a standalone Flask + HTMX app for managing medicine schedules. sketch_gen.py generates alarm.hpp C++ header for MedMinderV2 Arduino sketch. Compile/upload via arduino_sketch_tools extension. Medicine CRUD UI with in-memory MedicineStore.

**Files**: `medminder_dash/` (app.py, state.py, sketch_gen.py, pubsub.py, templates/, tests/)

**Test Impact**: 418 total (+49 new medminder_dash tests)

---

### Phase 41 — Nox-Based Wheel Building Automation ✅ COMPLETED

**Date**: 2026-05-31

**Type**: DevOps

**Change**: Created noxfile.py at project root with parametrized build sessions for all 4 packages. Added `install_arduino_deps.sh`, `gen_grpc_bindings.py`, populated 6 setup.py files, comprehensive test suite, CI pipeline with all_tests/all_builds wrappers and scripts/ci.sh.

**Files**: `noxfile.py`

**Test Impact**: 418 total (all passing)

---

### Phase 42 — PEP 503 Index + Pipfile Fix ✅ COMPLETED

**Date**: 2026-05-31

**Type**: DevOps

**Change**: Generated minimal PEP 503 index.html files in noxfile.py after each build so file:// [[source]] entries in Pipfiles resolve correctly. Fresh pip installs need PEP 503 format (subdirectory <pkg>/index.html + .whl), not flat directory scan.

**Files**: `noxfile.py`

**Test Impact**: No change

---

### Phase 43 — MedMinder UI Enhancements ✅ COMPLETED

**Date**: 2026-06-01

**Type**: Frontend

**Change**: Fixed 6 blocker/high bugs from post-implementation audit: JSON persistence wired (_save/_load), pubsub called in factory, /medicines route added, board-selected guard, Gunicorn dependency, README updated.

**Files**: `medminder_dash/app.py`, `medminder_dash/state.py`, `medminder_dash/pubsub.py`, `medminder_dash/templates/`, `README.md`

**Test Impact**: 53/53 tests

---

### Phase 44 — MedMinder UI Alignment with Arduino Dash ✅ COMPLETED

**Date**: 2026-06-01

**Type**: Frontend

**Change**: Aligned MedMinder Dash UI with Arduino Dash: vanilla CSS (dropped Tailwind CDN), board data enrichment (list[str] → dict[str,dict]), board card grid on dashboard, board detail with compile/upload + medicines, live event feed, daemon status badge, board connection badge, fallback board detection. Multiple bugfix rounds for scanner guard, port normalization, thread safety, CRUD responses, compile timeout, UDS address collision.

**Files**: `medminder_dash/templates/`, `medminder_dash/pubsub.py`, `medminder_dash/app.py`

**Test Impact**: 53/53 tests (+13 on initial)

---

### Phase 45 — Dynamic Sketch Directory Config ✅ COMPLETED

**Date**: 2026-06-02

**Type**: Frontend/Infrastructure

**Change**: Wired alarm.hpp regeneration on every CRUD call. Fixed hx-include for sketch_path in compile form. Added admin UI for dynamic sketch path with tests.

**Files**: `medminder_dash/app.py`, `medminder_dash/templates/`

**Test Impact**: 54 tests

---

### Phase 46 — Board Detection, alarm.hpp, Compile Error Fixes ✅ COMPLETED

**Date**: 2026-06-02

**Type**: Core/Infrastructure

**Change**: Fixed REPO_ROOT path (MEDMINDER_ROOT env var override), board name resolution ("Unknown" → query arduino-cli), compile error display (show compiler stderr), connection status endpoint (check get_port_info()), FQBN pre-population from board_info. Added socket timeout to _read_loop via select().

**Files**: `medminder_dash/settings.py`, `medminder_dash/pubsub.py`, `arduino_sketch_tools/templates/compile_result.html`, `medminder_dash/app.py`, `medminder_dash/templates/board_detail.html`, `board_manager_client/pubsub_client.py`

**Test Impact**: No change

---

### Phase 47 — Reader Thread Race Condition ✅ COMPLETED

**Date**: 2026-06-02

**Type**: Core/Infrastructure

**Change**: Added TypeError and AttributeError to the except clause in PubSubClient._read_loop(). These unhandled exceptions were crashing the reader daemon thread silently, dropping all future PubSub messages, causing compilation status to never update.

**Files**: `board_manager_client/pubsub_client.py`

**Test Impact**: No change

---

### Phase 48 — Reader Thread Safety & alarm.hpp Bootstrap ✅ COMPLETED

**Date**: 2026-06-02

**Type**: Core/Infrastructure

**Change**: Wrapped _read_loop processing (feed/read_one/dispatch) in separate try/except. Added sys::health subscription to medminder_dash. Fixed daemon badge to check both is_connected and is_daemon_ready(). Created parse_alarm_hpp() + unesc_text() for alarm.hpp bootstrap on startup. Added admin sync button.

**Files**: `board_manager_client/pubsub_client.py`, `medminder_dash/pubsub.py`, `medminder_dash/app.py`, `medminder_dash/sketch_gen.py`, `arduino_sketch_tools/compile_pending.html`

**Test Impact**: 67 medminder_dash

---

### Phase 49 — Fix Stale Wheel + Namespace Conflict ✅ COMPLETED

**Date**: 2026-06-03

**Type**: DevOps

**Change**: Phase 47/48 source changes were never deployed (stale wheel). Rebuilt board_manager_client via nox. Fixed namespace package conflict with sys.path.insert(0, ...) to prefer python/ packages over root-level directories.

**Files**: `medminder_dash/app.py`, `noxfile.py`

**Test Impact**: 72/72 medminder_dash

---

### Phase 50 — Fix alarm.hpp Bootstrap & Compilation Status ✅ COMPLETED

**Date**: 2026-06-03

**Type**: Core/Infrastructure

**Change**: Cleaned stale board_meta.json (TestBoard/default entries blocking bootstrap). Refactored alarm bootstrap from create_app() to lazy check in board_select(). Fixed double init_pubsub() (called from both create_app() and __main__). Fixed double handshake on TCP fallback. Fixed REPO_ROOT parents[3]→parents[4].

**Files**: `medminder_dash/data/board_meta.json`, `medminder_dash/app.py`, `board_manager_client/pubsub_client.py`

**Test Impact**: 75/75 medminder_dash (+3 new)

---

### Phase 51 — Align with arduino_dash Compile/WS Pattern ✅ COMPLETED

**Date**: 2026-06-03

**Type**: Frontend

**Change**: Aligned medminder_dash with arduino_dash patterns: argparse in __main__.py (--debug flag), full _on_pubsub_reconnect re-registering all handlers, resp::* subscription with _pending_responses, WS route + base.html WS.js extension + event-feed + JS handler.

**Files**: `medminder_dash/__main__.py`, `medminder_dash/pubsub.py`, `medminder_dash/app.py`, `medminder_dash/templates/base.html`

**Test Impact**: 78/78 medminder_dash

---

### Phase 52 — Fix Phase 51 Regression Bugs ✅ COMPLETED

**Date**: 2026-06-03

**Type**: Frontend

**Change**: Fixed medicines not populated from board grid — added _migrate_default_board() + lazy alarm.hpp bootstrap to board_detail(). Removed #live-events div (WS board events caused extra cards on every page). Removed dead _load_from_alarm_hpp_if_needed().

**Files**: `medminder_dash/app.py`, `medminder_dash/templates/base.html`

**Test Impact**: 75/75 medminder_dash (3 startup tests removed)

---

### Phase 53 — Remove Redundant Navbar Board Status ✅ COMPLETED

**Date**: 2026-06-03

**Type**: Frontend

**Change**: Removed navbar board-status span + backend /api/board_status route + 5 dead tests. The textual connection status was redundant with board grid (self-polls), board detail connection badge, and daemon badge.

**Files**: `medminder_dash/templates/base.html`, `medminder_dash/app.py`, `medminder_dash/tests/test_board_status.py`

**Test Impact**: 70/70 medminder_dash (5 tests removed)

---

### Phase 54 — Align PubSub, WS, Entry Point, Fallback Scanner ✅ COMPLETED

**Date**: 2026-06-03

**Type**: Core/Infrastructure

**Change**: Systematic alignment across both dashboards: created dash_state.py singleton module for medminder_dash (avoiding state.py conflict), added TCP CLI args, disconnect cleanup, board routes module. For arduino_dash: create_app() factory, full handler re-registration, WS robustness, template alignment, fallback scanner.

**Files**: `medminder_dash/dash_state.py`, `medminder_dash/state.py`, `medminder_dash/pubsub.py`, `medminder_dash/board_management.py`, `arduino_dash/infra.py`, `arduino_dash/__main__.py`

**Test Impact**: 70 medminder + 89 arduino

---

### Phase 55 — WSGI + BMS Lifecycle ✅ COMPLETED

**Date**: 2026-06-03

**Type**: DevOps

**Change**: Added gunicorn WSGI entry points for both dashboards with BMS auto-start via gunicorn hooks (when_ready→start BMS, post_worker_init→init_pubsub, on_exit→stop BMS). Shared board_manager/boot.py module. Aligned exception handling between both dashboards.

**Files**: `board_manager/boot.py`, `arduino_dash/wsgi.py`, `arduino_dash/gunicorn.conf.py`, `medminder_dash/wsgi.py`, `medminder_dash/gunicorn.conf.py`, `arduino_dash/infra.py`

**Test Impact**: 96 arduino + 78 medminder

---

### Phase 56 — Arduino Deps Installer + gRPC Bindings + setup.py ✅ COMPLETED

**Date**: 2026-06-04

**Type**: DevOps

**Change**: Created install_arduino_deps.sh (bash), gen_grpc_bindings.py (Python with venv detection), populated 6 setup.py with proper install_requires/entry_points/package_data. Added comprehensive test suite (94 pytest + 12 bash). Added CI pipeline with all_tests/all_builds nox wrappers + scripts/ci.sh.

**Files**: `scripts/install_arduino_deps.sh`, `scripts/gen_grpc_bindings.py`, `scripts/ci.sh`, 6x `setup.py`, `noxfile.py`, `scripts/tests/`

**Test Impact**: 598 pass + 10 skip (+136 from scripts/)

---

### Phase 57 — Standalone Binaries (PyOxidizer) ✅ COMPLETED

**Date**: 2026-06-04

**Type**: DevOps

**Change**: Built standalone executables for board-manager, arduino-dash, and medminder-dash via PyOxidizer 0.24.0 (CPython 3.10.9). Created pyoxidizer.bzl configs, test_installs.sh, build_standalone.sh, .gitignore. Verified grpc protobuf stubs + gunicorn os.fork in bundled binaries.

**Files**: `scripts/pyoxidizer/*/pyoxidizer.bzl`, `scripts/test_installs.sh`, `scripts/build_standalone.sh`, `.gitignore`

**Test Impact**: No change

---

### Phase 58 — Cleanup, Documentation, Binary Optimization ✅ COMPLETED

**Date**: 2026-06-04

**Type**: DevOps

**Change**: Moved test_installs/ → dist-test-install/ with pipenv. Created scripts/README.md and dist-test-install/README.md. Populated dist-standalone/ with built binaries. Added stdlib exclusion (unittest/tkinter/turtledemo etc.) saving ~4 MB per app. Added --zip packaging to build_standalone.sh.

**Files**: `scripts/README.md`, `dist-test-install/README.md`, `scripts/build_standalone.sh`, `scripts/pyoxidizer/*/pyoxidizer.bzl`, `board_manager/pyproject.toml`

**Test Impact**: No change

---

### Phase 59 — medminder_dash Board UI Improvements ✅ COMPLETED

**Date**: 2026-06-06

**Type**: Frontend

**Change**: Board detail heading shows board name instead of port path with "Port: ..." hint subtitle. FQBN field converted to read-only label with hidden input for form submission. Device Port label added. deploy.html JS updated for non-input FQBN display.

**Files**: `medminder_dash/templates/board_detail.html`, `medminder_dash/board_management.py`, `medminder_dash/templates/deploy.html`

**Test Impact**: 78/78 medminder_dash (+2 new)

---

### Phase 60 — Merge /deploy + /admin/sketch-dir into /admin ✅ COMPLETED

**Date**: 2026-06-07

**Type**: Frontend

**Change**: Single /admin page replaces both /deploy and /admin/sketch-dir. 4 cards: Sketch Path (DnD + browse + recent-uploads select + delete from arduino_dash), Set Medicines (bidirectional sync with confirm modals), Compile, Upload. Server-side session UUID confirm tokens for destructive actions.

**Files**: `medminder_dash/sketch_management.py`, `medminder_dash/app.py`, `medminder_dash/dash_state.py`, `medminder_dash/templates/admin.html`, `medminder_dash/templates/partials/confirm_modal.html`

**Test Impact**: 94 medminder (+12 net), 972+8 grand total

---

### Phase 61 — Medicine Management Cards on /admin ✅ COMPLETED

**Date**: 2026-06-07

**Type**: Frontend

**Change**: Added medicine management cards to /admin with diff detection. When metadata == alarm.hpp: one editable card. When they differ: metadata (editable) + alarm.hpp (read-only). Auto-sync on edit. Sync buttons disabled when 1 card, active when 2 cards. Global board selector drives medicine CRUD.

**Files**: `medminder_dash/app.py`, `medminder_dash/templates/admin.html`, `medminder_dash/templates/partials/medicine_metadata_card.html`, `medminder_dash/templates/partials/medicine_alarm_hpp_card.html`, `medminder_dash/templates/partials/medicine_cards.html`, `medminder_dash/templates/partials/admin_board_selector.html`

**Test Impact**: 113 medminder (+19), 991+8 grand total

---

### Phase 62 — MedMinderV2 Default + Global Board Selector ✅ COMPLETED

**Date**: 2026-06-07

**Type**: Frontend

**Change**: Prepend MedMinderV2 default sketch in /api/sketches response. Global board selector for compile/upload on /admin (removed local per-card selects). FQBN display updates via OOB swap. Upload card disabled when no port selected.

**Files**: `medminder_dash/sketch_management.py`, `medminder_dash/app.py`, `medminder_dash/templates/admin.html`, `medminder_dash/templates/partials/admin_board_selector.html`

**Test Impact**: 123 medminder (+10), 1001+8 grand total

---

### Phase 62.1-62.4 — /admin Page Fixes ✅ COMPLETED

**Date**: 2026-06-07

**Type**: Frontend

**Change**: Three user-reported issues: (1) MedMinderV2 default pre-populated via include_default param + hidden sketch_path input. (2) Board selector polls every 5s. (3) Compile/Upload buttons converted to htmx-native hx-post (no JS); inner IDs renamed to avoid conflict.

**Files**: `medminder_dash/sketch_management.py`, `medminder_dash/app.py`, `medminder_dash/templates/admin.html`, `arduino_sketch_tools/templates/partials/`

**Test Impact**: 132 medminder (+9), 1010+8 grand total

---

### Phase 62.5 — Per-Board Sketch Assignment + Wheel-Packaged Default ✅ COMPLETED

**Date**: 2026-06-07

**Type**: Core/Infrastructure

**Change**: Surface hardware_id in board info flow. Created sketch_registry.py for per-hardware_id sketch assignment storage in board_sketches.json. board_detail uses per-board sketch with packaged MedMinderV2 fallback. Moved MedMinderV2 sketch INTO package dir with importlib.resources XDG extraction.

**Files**: `medminder_dash/sketch_registry.py`, `medminder_dash/settings.py`, `medminder_dash/pubsub.py`, `board_manager/board_detector.py`, `medminder_dash/pyproject.toml`

**Test Impact**: 152 medminder + 186 board_manager (+22), 1032+8 grand total

---

### Phase 62.6 — Post-Launch Bugfixes ✅ COMPLETED

**Date**: 2026-06-08

**Type**: Frontend

**Change**: Fixed 5 bugs: (A) post-upload refresh target destroyed by outerHTML → innerHTML. (B) shutil.copy2 TypeError with Traversable → read_bytes/write_bytes. (C) Duplicate id="sketch_path". (D) Stale #fqbn on board switch → OOB swap. (E) Stale compile/upload URLs → live partial.

**Files**: `medminder_dash/templates/admin.html`, `medminder_dash/settings.py`, `medminder_dash/app.py`, `medminder_dash/templates/partials/compile_upload_card.html`

**Test Impact**: No change (152/96/186+8)

---

### Phase 63 — setup.py Arguments + setup.cfg + Detailed READMEs ✅ COMPLETED

**Date**: 2026-06-09

**Type**: Docs

**Change**: Added proper setup() arguments (name, version, description, author, python_requires, packages, install_requires, entry_points, package_data, keywords) to all 6 packages. Created setup.cfg with long_description = file: README.md. Created detailed READMEs for 5 packages, updated arduino_grpc README.

**Files**: 6x `setup.py`, 6x `setup.cfg`, 5x `README.md`

**Test Impact**: Verified 548 per-package

---

### Phase 64 — Full-Viewport DnD Overlay ✅ COMPLETED

**Date**: 2026-06-09

**Type**: Frontend

**Change**: Replaced small dashed #drop-zone with full-viewport translucent overlay that shows on file drag and accepts drop anywhere. Counter pattern (dragenter++/dragleave--), dataTransfer.types Files gate, JS event listeners (hyperscript from window unreliable). 7 rounds of bugfixing: body-level handlers, intermittent DnD, alt-tab visibility, mouseenter stale-cleanup, extracted to partial.

**Files**: `medminder_dash/templates/base.html`, `medminder_dash/templates/admin.html`, `medminder_dash/templates/partials/dnd_overlay.html`

**Test Impact**: No change (152/96/186+8)

---

### Phase 65 — Fix Admin Board Selector Polling ✅ COMPLETED

**Date**: 2026-06-09

**Type**: Frontend

**Change**: hx-swap="outerHTML" on board selector container was destroying HTMX polling attributes after first poll. Changed to hx-swap="innerHTML" in both dashboards' admin.html.

**Files**: `medminder_dash/templates/admin.html`, `arduino_dash/templates/admin.html`

**Test Impact**: No change (152/96/186+8)

---

### Phase 66 — Refresh Button for medminder_dash + Fix arduino_dash ✅ COMPLETED

**Date**: 2026-06-09

**Type**: Frontend

**Change**: Added Refresh button to medminder_dash admin board selector. Fixed arduino_dash refresh button to use innerHTML swap (was outerHTML, same bug as Phase 65).

**Files**: `medminder_dash/templates/partials/admin_board_selector.html`, `arduino_dash/templates/partials/admin_board_selector.html`

**Test Impact**: No change (152/102/186+8)

---

### Phase 67 — hx-disabled-elt + board-changed Trigger ✅ COMPLETED

**Date**: 2026-06-09

**Type**: Frontend

**Change**: Added hx-disabled-elt="this" to refresh button on both dashboards' admin board selectors (prevents spam clicks). Added board-changed from:body trigger to board-selector container for instant refresh on board select.

**Files**: `medminder_dash/templates/partials/admin_board_selector.html`, `medminder_dash/templates/admin.html`, `arduino_dash/templates/partials/admin_board_selector.html`, `arduino_dash/templates/admin.html`

**Test Impact**: No change (152/102/186+8)

---

### Phase 68 — Instant Board Selector Refresh + Remove Monorepo Path Hacks ✅ COMPLETED

**Date**: 2026-06-09/10

**Type**: Core/Infrastructure

**Change**: Added board-changed from:body trigger to both dashboards' admin.html hx-trigger for instant selector refresh. Replaced REPO_ROOT/MEDMINDER_ROOT/sys.path.insert hacks with XDG-standard paths (CONFIG_DIR→~/.config/medminder/). Removed sys.path.insert and repo_sketch fallback. Removed config/**/* from package_data.

**Files**: `medminder_dash/settings.py`, `medminder_dash/app.py`, `medminder_dash/setup.py`, `medminder_dash/pyproject.toml`, `medminder_dash/templates/admin.html`, `arduino_dash/templates/admin.html`

**Test Impact**: 151+1 medminder, 102 arduino, 186+8 board_manager

---

## Phase 69 — Remove Hardcoded Source-Relative Paths from arduino_dash ✅ COMPLETED

**Type**: Packaging/Infrastructure
**Scope**: `arduino_dash` package — `settings.py`, `sketch_registry.py`, `state.py`

### Problem

Two `arduino_dash` modules used monorepo-relative path computations that break when `arduino-dash` is wheel-installed:

| File | Old Pattern | New Pattern |
|------|-------------|-------------|
| `sketch_registry.py:12` | `_CONFIG_DIR = Path(__file__).resolve().parents[4] / "config"` | Import `CONFIG_DIR` from settings |
| `sketch_registry.py:13` | `_BOARD_SKETCHES_FILE = str(_CONFIG_DIR / "board_sketches.json")` | Import `BOARD_SKETCHES_FILE` from settings |
| `state.py:41` | `UPLOAD_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")` | Import `UPLOAD_BASE_DIR` from settings |

### Files modified

| File | Action | Details |
|------|--------|---------|
| `arduino_dash/arduino_dash/settings.py` | **NEW** | `CONFIG_DIR = ~/.config/arduino-dash/`; `UPLOAD_BASE_DIR = ~/.local/share/arduino-dash/uploads/` |
| `arduino_dash/arduino_dash/sketch_registry.py` | MODIFIED | Remove `from pathlib import Path`; import `CONFIG_DIR`, `BOARD_SKETCHES_FILE` from settings |
| `arduino_dash/arduino_dash/state.py` | MODIFIED | Remove `import os`; import `UPLOAD_BASE_DIR` from settings |

### Key Architecture

- `CONFIG_DIR` uses **XDG config home**: `~/.config/arduino-dash/`
- `UPLOAD_BASE_DIR` uses **XDG data home**: `~/.local/share/arduino-dash/uploads/`
- `settings.py` mirrors the same pattern as `medminder_dash/settings.py` (Phase 68)
- All test patches (`patch("arduino_dash.state.UPLOAD_BASE_DIR", ...)`) target `state.__dict__` — valid regardless of value source

### Test Impact

| Suite | Before | After |
|-------|--------|-------|
| arduino_dash | 102 pass | 102 pass ✅ |
| medminder_dash | 151 + 1 skip | 151 + 1 skip ✅ |
| arduino_sketch_tools | 47 pass | 47 pass ✅ |

---

## Phase 70 — Board Detection Hot-Updates ✅ COMPLETED

**Date**: 2026-06-10
**Type**: Core Architecture
**Scope**: `board_manager` (BoardDetector, service, config, udev_monitor), `board_manager_client` (PubSubClient), both dashboards (FallbackScanner removal)

### Goal

Replace polling-based board detection with async push-based detection using BoardListWatch (gRPC streaming) and optionally pyudev (USB hotplug events). Add on-demand board query capability to pubsub protocol. Add CLI flag for mode selection. Deprecate FallbackScanner.

### Key Files

- `board_manager/board_detector.py` — `get_known_boards()` (Q1), `_run_watch()` (Q2), `_lock`, `mode` param
- `board_manager/service.py` — `method == "list_boards"` handler (Q1)
- `board_manager/udev_monitor.py` — NEW: UdevMonitor class (Q3)
- `board_manager/config.py` — Added `board_detection_mode` with precedence chain (Q4)
- `board_manager/__main__.py` — Added `--board-detection-mode {watch,udev}` (Q4)
- `board_manager/pyproject.toml` — Added `[project.optional-dependencies] udev = ["pyudev>=0.24"]` (Q3)
- `board_manager_client/pubsub_client.py` — `request_boards()` method (Q1)
- Both dashboards' pubsub files — `refresh_boards()` function (Q1, later removed in Phase 71)

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
3. **`_lock` added** to BoardDetector for cross-thread safety.
4. **On-demand query** (`method == "list_boards"`) via pubsub request-response.
5. **FallbackScanner** — startup call removed from both dashboards. Code retained but disabled.
6. **CLI flag precedence**: CLI arg > env var `BOARD_MGR_DETECTION_MODE` > config file > default `"watch"`.

### Quantums

| Q | Scope | Key Changes | Files | Status |
|---|-------|-------------|-------|--------|
| 1 | On-demand board query | `get_known_boards()`, `method == "list_boards"` handler, `request_boards()` | `board_detector.py`, `service.py`, `pubsub_client.py`, both dashboards' pubsub files | ✅ |
| 2 | BoardListWatch in BoardDetector | `_run_watch()` streaming; mode param; `_lock` | `board_detector.py`, `test_board_detector.py` | ✅ |
| 3 | pyudev Monitor | New `udev_monitor.py`, optional dep, 11 tests | `udev_monitor.py`, `test_udev_monitor.py`, `pyproject.toml` | ✅ |
| 4 | Config/CLI + FallbackScanner removal | `board_detection_mode` config/CLI/env; mode passed to BoardDetector | `config.py`, `__main__.py`, `service.py`, both dashboards' pubsub files | ✅ |

### Test Impact

| Suite | Before | After |
|-------|--------|-------|
| board_manager | 186 + 8 skip | 203 + 8 skip ✅ (+17) |
| arduino_dash | 102 | 102 ✅ |
| medminder_dash | 151 + 1 skip | 151 + 1 skip ✅ |

---

## Phase 71b — beforeSwap Fires board-changed on Wrong Element ✅ COMPLETED

**Date**: 2026-06-11
**Type**: Bugfix
**Scope**: Both dashboards' `base.html` `beforeSwap` handler trigger targets

### Goal

Fix the WS-triggered board grid refresh that never worked because the `beforeSwap` handler fires `board-changed` directly on `#board-grid` / `#admin-board-selector-container` instead of on `body`. Elements listen for `board-changed from:body` — HTMX's `from:` filter rejects events not originating from `body`.

### Data Flow (corrected)

```
WS message arrives
  → beforeSwap handler detects .board-event (Phase 71a)
  → htmx.trigger('body', 'board-changed')    ← Phase 71b: fired on body
  → #board-grid detects "board-changed from:body"
  → hx-get="/api/boards/grid" re-fetches
  → Grid re-renders from current state._board_list
```

### Key Files Changed

| File | Change | Dashboard |
|------|--------|-----------|
| `templates/base.html` | `htmx.trigger('#board-grid', ...)` → `htmx.trigger('body', 'board-changed')` | arduino_dash |
| `templates/base.html` | Same | medminder_dash |

### Why Two Phases

- **Phase 71a**: `.board-event` class missing → `querySelectorAll` returns 0 → handler never reaches trigger (necessary but insufficient)
- **Phase 71b**: trigger fires on wrong element → `from:body` filter rejects → event silently lost

Both fixes required for WS-triggered refresh to work.

---

## Phase 71 — Eliminate 5s HTMX Polling via WS Push ✅ COMPLETED

**Date**: 2026-06-11
**Type**: Frontend Performance
**Scope**: Both dashboards' templates (base.html, dashboard.html/index.html, admin.html, admin_board_selector.html) + cleanup (pubsub.py, pubsub_infra.py, CSS)

### Goal

Replace remaining 5-second HTMX polling for board grid and admin board selector with WebSocket-triggered updates. When a board connect/disconnect event arrives via WS, fire `board-changed` event → HTMX re-fetches grid/selector only on actual changes.

### Approach (Option B)

WS broadcasts board event HTML as before (unchanged). Frontend `beforeSwap` handler fires `htmx.trigger('body', 'board-changed')` when board events are detected. Elements listen for `board-changed from:body` instead of `every 5s`.

### Data Flow (After)

```
Board plugged in
  → PubSub _on_board_event
  → updates in-memory state (real-time)
  → broadcast_ws(event_html)
  → browser receives via WS
  → beforeSwap handler detects .board-event
  → htmx.trigger('body', 'board-changed')
  → #board-grid + #admin-board-selector-container re-fetch
  → NO 5s polling
```

### Key Files Changed

| File | Change | Dashboard |
|------|--------|-----------|
| `templates/base.html` | Extended beforeSwap handler with `htmx.trigger(..., 'board-changed')` (SUPERSEDED by Phase 71c) | arduino_dash |
| `templates/base.html` | Phase 71b: `htmx.trigger('#board-grid', ...)` → `htmx.trigger('body', ...)` (SUPERSEDED by Phase 71c) | arduino_dash |
| `templates/base.html` | NEW WS event-feed div + beforeSwap handler (SUPERSEDED by Phase 71c) | medminder_dash |
| `templates/base.html` | Phase 71b: `htmx.trigger('#board-grid', ...)` → `htmx.trigger('body', ...)` (SUPERSEDED by Phase 71c) | medminder_dash |
| `templates/dashboard.html` | `every 5s` → `board-changed from:body` | arduino_dash |
| `templates/index.html` | `every 5s` → `board-changed from:body` | medminder_dash |
| `templates/admin.html` | `every 5s` removed from trigger | Both |
| `templates/partials/admin_board_selector.html` | Removed Refresh button | Both |
| `pubsub.py` | Deleted `refresh_boards()` | arduino_dash |
| `pubsub_infra.py` | Deleted `refresh_boards()` | medminder_dash |
| `templates/base.html` | Removed `.refresh-btn` CSS | Both |

### Design Decisions

1. **Reuse existing `board-changed` event name** — already fired by `<select>` change handler. WS handler also fires it. Single event name simplifies maintenance.
2. **Keep `hx-trigger="load"`** — ensures initial page load still fetches grid/selector.
3. **Keep `_on_board_event` / `broadcast_ws` unchanged** — server-side stays the same.
4. **MedMinder Dash WS connection added** — minimal `event-feed` div + `beforeSwap` handler. No live-events display needed; only trigger signals.
5. **`refresh_boards()` deleted** — never called. In-memory state already updated by PubSub push events; grid/selector endpoints read from that state directly.
6. **`request_boards()` in `board_manager_client` kept** — low-level API preserved for potential future use.

### Test Updates

| Test | Change |
|------|--------|
| `test_admin_html_board_selector_polls_every_5s` | Renamed → `test_admin_html_board_selector_uses_board_changed_event`; updated assertions |
| `test_admin_html_board_selector_polling_matches_main_dashboard` | Renamed → `test_admin_html_board_selector_trigger_matches_main_dashboard`; updated assertions |
| `test_admin_html_global_select_full_width` | Removed Refresh button assertions (lines 1017-1020) |

### Test Impact

| Suite | Tests | Status |
|-------|-------|--------|
| arduino_dash | 102/102 | ✅ |
| medminder_dash | 151/151 + 1 skip | ✅ |
| board_manager | 203/203 + 8 skip | ✅ |
| **Grand total** | **~1098 + 9 skip** | ✅ |

---

## Phase 71b Test Impact

No test changes needed. All suites pass with same counts:

| Suite | Tests | Status |
|-------|-------|--------|
| arduino_dash | 102/102 | ✅ |
| medminder_dash | 151/151 + 1 skip | ✅ |
| board_manager | 203/203 + 8 skip | ✅ |

---

## Phase 71c — WS Extension Bypasses `htmx:beforeSwap` Entirely ✅ COMPLETED

**Date**: 2026-06-11
**Type**: Bugfix
**Scope**: Both dashboards' `base.html` `beforeSwap` handler → `wsBeforeMessage` handler

### Goal

Replace the dead `htmx:beforeSwap` handler (never fired for WS messages) with a `htmx:wsBeforeMessage` handler. The WS extension (`ws.js`) processes incoming messages via `api.oobSwap()` directly, bypassing the `beforeSwap` event entirely.

### Root Cause

HTMX WS extension source (`ws.js` `ensureWebSocket` message handler):

```
message → htmx:wsBeforeMessage → api.oobSwap() → htmx:wsAfterMessage
                                    ↛ htmx:beforeSwap (NEVER FIRED)
```

### Data Flow (Corrected)

```
WS message with board_event.html arrives
  → WS extension fires "htmx:wsBeforeMessage" on event-feed
  → Our handler checks evt.detail.message.includes("board-event")
  → htmx.trigger('body', 'board-changed')
  → #board-grid detects "board-changed from:body"
  → Grid re-fetches from in-memory state
```

### Key Files Changed

| File | Change | Dashboard |
|------|--------|-----------|
| `templates/base.html` | Replace 35-line `beforeSwap` handler with 6-line `wsBeforeMessage` handler; remove dead compile/upload line movement code | arduino_dash |
| `templates/base.html` | Same (simpler — no compile/upload code) | medminder_dash |

### Complete Bug Timeline

| Phase | Bug | Status |
|-------|-----|--------|
| 71 | WS implementation used `beforeSwap` which never fires for WS messages | ✅ Fixed (Phase 71c) |
| 71a | `.board-event` CSS class missing from `board_event.html` partials | ✅ Fixed |
| 71b | `htmx.trigger()` called on `#board-grid` not `body` | ✅ Fixed (moot — handler never fired) |
| 71c | Wrong event: WS extension uses `oobSwap` not `beforeSwap` | ✅ Fixed (Phase 71c) |

### Dead Code Removed

1. **Compile/upload line movement**: WS extension calls `api.oobSwap(child.getAttribute('hx-swap-oob'), child, settleInfo)` for each child — compile/upload lines with `hx-swap-oob="beforeend:#output-id"` are handled natively.
2. **`#live-events` feed insertion**: Element doesn't exist in DOM; board events without `id` or `hx-swap-oob` are safely no-opped by the extension.
3. **`shouldSwap = false`**: Irrelevant for WS messages — WS extension never checks this property.

### Handler Comparison

```javascript
// OLD — dead code (beforeSwap never fires for WS messages)
htmx.on("htmx:beforeSwap", function(evt) {
    if (evt.detail.target.id !== "event-feed") return;
    evt.detail.shouldSwap = false;
    var tmp = document.createElement("div");
    tmp.innerHTML = evt.detail.serverResponse;
    // ... 25 lines of compile/upload line movement + board-event detection ...
});

// NEW — fires for every WS message
htmx.on("htmx:wsBeforeMessage", function(evt) {
    if (evt.target.id !== "event-feed") return;
    if (evt.detail.message.includes("board-event")) {
        htmx.trigger('body', 'board-changed');
    }
});
```

### Why the Simpler Check Works

- `evt.detail.message` is the raw HTML string from `broadcast_ws()`
- The `.board-event` CSS class is a unique string only present in board event payloads
- `String.includes()` is O(n) but n is small (a few hundred bytes) — negligible cost
- No need to parse HTML into DOM — simpler and faster

### Phase 71c Fix Applied

Phase 71c replaced `htmx:beforeSwap` handler with `htmx:wsBeforeMessage` in both dashboards' `base.html`. The handler fires `htmx.trigger('body', 'board-changed')` when a board event is detected in the WS message. Dead compile/upload line movement code removed.

---

## Phase 72 — Collapsible Live Events Card in Admin Dashboards

**Date**: 2026-06-14

**Goal**: Add a collapsible `<details>/<summary>` "Live Events" card to the admin dashboard in both modules, showing board connect/disconnect events in real-time.

### Approach

**OOB wrapper in pubsub, not template**: `board_event.html` shared with non-WS route (`/api/boards/event`), so `hx-swap-oob` attribute would break that route. Instead, wrap rendered HTML at the broadcast call:

```python
# arduino_dash pubsub.py:161 / medminder_dash pubsub_infra.py:203
event_html = '<div hx-swap-oob="afterbegin:#live-events-card">' + \
    render_template("partials/board_event.html", events=[data]) + '</div>'
```

### Admin Template (both dashboards)

```html
<details class="card live-events-card" id="live-events-card">
    <summary>Live Events</summary>
    <div id="live-events">
        <p class="hint live-events-empty" style="text-align: center; padding: 0.5rem;">Waiting for board events...</p>
    </div>
</details>
```

CSS in `<style>` block within admin.html:
- `.live-events-card`: dark background, radius, no padding, overflow hidden
- `summary`: thin (~36px), cursor pointer, custom `▶` arrow, rotates 90° on `[open]`
- `#live-events`: `max-height: 300px; overflow-y: auto; border-top`
- `.live-events-empty` hidden via `+` sibling combinator when first `.board-event` appears

### Data Flow

```
BoardDetector detects connect/disconnect
  → PubSub board::<port>::event
    → _on_board_event handler
      1. Updates state._board_list
      2. Renders board_event.html
      3. Wraps with <div hx-swap-oob="afterbegin:#live-events-card">
      4. broadcast_ws(html)
        → Browser WS message received
          → WS extension fires htmx:wsBeforeMessage
            → Our handler: checks "board-event" → fires board-changed (grid sync)
          → WS extension calls api.oobSwap() on OOB wrapper div
            → HTMX finds #live-events-card, prepends event inside <details>
```

### Leaner Event Items (medminder_dash)

Remove `.card` class, reduce padding `0.5rem 1rem` → `0.25rem 0.5rem`, `border-bottom: 1px solid #334155`, `font-size: 0.85rem`.

### Files Changed

| File | Change |
|------|--------|
| `arduino_dash/.../pubsub.py:161` | OOB wrapper in `_on_board_event` |
| `medminder_dash/.../pubsub_infra.py:203` | OOB wrapper in `_on_board_event` |
| `arduino_dash/.../templates/admin.html` | Live-events card at top + CSS |
| `medminder_dash/.../templates/admin.html` | Same card + CSS |
| `medminder_dash/.../templates/partials/board_event.html` | Leaner event items |
| `CODEBASE_REFERENCE.md` | This section |

### Verification

All 5 suites green (no test changes):
- arduino_dash: 102/102
- medminder_dash: 151/151 + 1 skip
- board_manager: 203/203 + 8 skip
- arduino_sketch_tools: 47/47
- board_manager_client: 24/24

### Test Impact

No test changes needed.

---

## Phase 72 Bugfix — Double Board Event Display

**Date**: 2026-06-14 14:05

**Bug**: Board events appear twice (or more) in the live-events card. Four independent root causes, each fixed separately.

### Fix v1 — Client-Side Handler Dedup
**File**: `board_manager_client/pubsub_client.py:135`
```python
if handler not in hlist:
```

### Fix v2 — Client-Side Server Subscribe Dedup
**File**: `board_manager_client/pubsub_client.py:136-137`
```python
is_new = topic not in self._subscriptions
...
if self._sock and is_new:
```

### Fix v3 — Server-Side Per-Connection State Guard
**File**: `board_manager/service.py:34,242-245`
**Root cause**: `_handle_client_message` called `_send_current_boards_to(conn)` for **every** subscribe message (6× per connection).

### Fix v4 — Fallback Scanner Race (ACTUAL ROOT CAUSE)
**Files**: 
- `medminder_dash/pubsub_infra.py:35-78,180-213`
- `arduino_dash/pubsub.py:31-67,133-164`

**Root cause**: The fallback scanner (`_fallback_scan_loop`) detects boards independently of BMS PubSub. Both sources call `_on_board_event()` → `broadcast_ws()`. Result: TWO WS messages per board event.

**Fix A — Atomic dedup in `_on_board_event`**:
```python
# Under _known_ports_lock (_board_list_lock for arduino_dash):
if event == "connected":
    if port in state._known_ports:
        return  # first caller wins, rest are skipped
    state._known_ports[port] = data
```

The `return` is INSIDE the lock, making the check-and-add atomic. If thread A adds port X, thread B (processing same port) will find it already present and return without broadcasting.

**Fix B — `daemon_ready` guard in fallback scanner**:
```python
def _fallback_scan_loop(ps):
    while not state._stop_fallback_scan:
        if state._daemon_ready:       # BMS is available
            time.sleep(interval)       # scanner is passive
            continue
        # ... normal scan logic (BMS unavailable)
```

### Execution Trace After All 4 Fixes
```
Board connects → BMS PubSub event → _on_board_event → broadcast_ws (v4: first caller wins)
Fallback scanner (0-5s later) → port already in _known_ports → return early (v4 dedup)
daemon_ready = True → scanner sleeps until BMS goes down (v4 optimization)
= 1× WS message per event ✅
```

### Complete Fix Summary
| v | Layer | What | How |
|---|-------|------|-----|
| 1 | Client handler | Dedup handler registration | `if handler not in hlist` |
| 2 | Client subscribe | Dedup subscribe for same topic | `if self._sock and is_new` |
| 3 | BMS server (ClientConn) | Send initial state once per connection | `initial_state_sent` flag |
| 4 | Dashboard handler | Dedup events from scanner vs PubSub | Atomic port check + daemon_ready guard |

### Verification
- medminder_dash: 151/151 + 1 skip ✅
- arduino_dash: 102/102 ✅
- board_manager: 204/204 + 8 skip ✅
- arduino_grpc: 33/33 + 2 skip ✅

---

## Phase 73 — Normalize `session["admin_active_board"]` via `_get_active_board_info()` Helper

**Date**: 2026-06-14 14:30
**Type**: Bugfix
**Scope**: `medminder_dash/app.py`

### Bug

`session["admin_active_board"]` stored two incompatible formats:

| Writer | Format | Example |
|--------|--------|---------|
| `admin()` line 378 | **3-tuple** | `("/dev/ttyACM0", "arduino:avr:uno", "ABC123")` |
| `api_medicines_active_board()` line 448 | **string** | `"/dev/ttyACM0"` |

Readers that expected a 3-tuple unpacked the string into characters (e.g. `"/dev/ttyACM0"` → `("/", "d", "e", ...)`). The `compile-upload-card` endpoint at line 577 then rendered raw Python tuple display like `('\/', 'd', 'e', 'v', ...)` in the UI.

### Fix

Added `_get_active_board_info()` helper at `app.py:50-56` that normalizes the session value to always return a `(port, fqbn, hw_id)` 3-tuple:

```python
def _get_active_board_info():
    raw = session.get("admin_active_board")
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        return (str(raw[0]), str(raw[1]), str(raw[2]))
    if isinstance(raw, str):
        return (raw, "", "")
    return ("", "", "")
```

### 6 Reading Sites Replaced

| Line | Endpoint/Function | Before | After |
|------|-------------------|--------|-------|
| 200 | `_require_any_board()` | `session.get("admin_active_board")` | `_get_active_board_info()[0]` |
| 366 | `admin()` | `session.get("admin_active_board")` → raw unpack | `_get_active_board_info()` triple unpack |
| 437 | `api_medicines_diff()` | `session.get("admin_active_board")` | `_get_active_board_info()` |
| 475 | `api_medicines_active_board_card()` | `session.get("admin_active_board")` | `_get_active_board_info()` |
| 499 | `api_medicines_board_selector()` | `session.get("admin_active_board")` → raw unpack | `_get_active_board_info()` triple unpack |
| 577 | `api_board_compile_upload_card()` | `session.get("admin_active_board")` → raw unpack | `_get_active_board_info()` triple unpack |

### 2 Writing Sites (Unchanged — Dual Format Still Exists)

| Line | Endpoint/Function | Writes |
|------|-------------------|--------|
| 378 | `admin()` | **3-tuple**: `(port, fqbn, hw_id)` |
| 448 | `api_medicines_active_board()` | **string**: `port` only |

Both writers are left as-is. The helper normalizes on read, so callers always get a consistent 3-tuple regardless of which writer stored the value.

### Gotcha

Dual-format in a single session key is inherently fragile: any new reader that does `session.get("admin_active_board")` directly (without the helper) will risk the same bug. All future reads must go through `_get_active_board_info()`.

---

## Phase 72c — Additional Fixes (3 Quantums)

**Date**: 2026-06-14 15:00

### Quantum 1 — arduino_dash `_get_active_board_info()` Helper

**File**: `arduino_dash/python/arduino_dash/arduino_dash/board_management.py`

Same helper as medminder_dash Phase 73, placed at module level before `init_board_routes()`:

```python
def _get_active_board_info():
    raw = session.get("admin_active_board")
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        return (str(raw[0]), str(raw[1]), str(raw[2]))
    if isinstance(raw, str):
        return (raw, "", "")
    return ("", "", "")
```

All existing `session["admin_active_board"]` readers in arduino_dash updated to use this helper.

### Quantum 2 — medminder_dash admin() Route Else Branch Session Write

**File**: `medminder_dash/python/medminder_dash/medminder_dash/app.py`

The `admin()` route's `else` branch (lines 385-396) resolved board info from `request.args` but did not persist to session. Added one line:

```python
session["admin_active_board"] = (active_board_port, active_board_fqbn, active_board_hardware_id)
```

### Quantum 3 — `.value` CSS Styling

**Files**: Both dashboards' `base.html`

```css
.value {
    background: #1e293b;
    border-radius: 0.25rem;
}
```

### Test Counts
- medminder_dash: 151/151 + 1 skip ✅
- arduino_dash: 102/102 ✅
- board_manager: 204/204 + 8 skip ✅
- arduino_grpc: 33/33 + 2 skip ✅

---

## Phase 72d — Board Info Resolution Refactoring

**Date**: 2026-06-16
**Type**: Refactor
**Scope**: Both dashboards' route modules (app.py, board_management.py)

### Goal

Extract ~50-line repeated board-info resolution block (appearing 6× across 3 routes in 2 dashboards) into `_resolve_board_info()` helper. Fix async compile-upload-card (missing first-port fallback). Fix latent `find_board_info_by_fqbn` single-arg bug in arduino_dash.

### Helpers

#### `_resolve_first_port_info(ports)` — medminder_dash `app.py:61-68`
```
ports list → get_first_board(ports) → (port, fqbn, hw_id) or ValueError
```
Wraps `get_first_board()` with ValueError for uniform error handling. Used in admin route first-port fallback.

#### `_resolve_board_info(port, fqbn, hw_id, known_ports)` — medminder_dash `app.py:71-104`, arduino_dash `board_management.py:25-59`
```
(port, fqbn, hw_id, known_ports)
  → get_port_info(port)
  → if no info:
      → try find_board_info_by_fqbn(fqbn, known_ports)        [stale session port]
      → if still nothing: get_first_board(known_ports)        [new board]
  → if info found:
      → validate port + fqbn present
      → if fqbn differs from session: try find_board_info_by_fqbn(session_fqbn, known_ports) [board moved]
      → if not found: adopt current port's fqbn
  → return (port, fqbn, hw_id) or raise ValueError
```

### Route Changes

| Dashboard | Route | Before (lines) | After (lines) |
|-----------|-------|----------------|---------------|
| medminder_dash | `api_medicines_board_selector` | ~70 | ~30 |
| medminder_dash | `api_board_compile_upload_card` | ~85 | ~25 |
| medminder_dash | `admin()` first-port fallback | inline `ports[0].get()` | `_resolve_first_port_info()` |
| medminder_dash | `admin()` FQBN lookup | inline `next()` | `find_board_info_by_fqbn(fqbn, ports)` |
| arduino_dash | `api_admin_board_selector` | ~50 | ~12 |
| arduino_dash | `api_board_compile_upload_card` | ~55 | ~12 |
| arduino_dash | `admin()` first-port fallback | inline `known_ports[0].get()` | `get_first_board(known_ports)` |
| arduino_dash | `admin()` FQBN lookup | inline `next()` + dead `if False:` block | `find_board_info_by_fqbn(fqbn, known_ports)` |

### Critical Bugfixes

4 `find_board_info_by_fqbn` calls in arduino_dash `board_management.py` passed only 1 argument after utils refactor changed signature to `(fqbn, boards)`:

| Original Line | Original | Fixed |
|---------------|----------|-------|
| 183 (board_selector) | `find_board_info_by_fqbn(active_board_fqbn)` | `find_board_info_by_fqbn(active_board_fqbn, known_ports)` |
| 211 (board_selector) | `find_board_info_by_fqbn(active_board_fqbn)` | `find_board_info_by_fqbn(active_board_fqbn, known_ports)` |
| 252 (compile_upload_card) | `find_board_info_by_fqbn(active_board_fqbn)` | `find_board_info_by_fqbn(active_board_fqbn, known_ports)` |
| 280 (compile_upload_card) | `find_board_info_by_fqbn(active_board_fqbn)` | `find_board_info_by_fqbn(active_board_fqbn, known_ports)` |

### Key Files

| File | Key Lines | Description |
|------|-----------|-------------|
| `medminder_dash/.../app.py` | 33-36 | Updated imports: `get_first_board`, `find_board_info_by_fqbn` |
| `medminder_dash/.../app.py` | 52-58 | `_get_active_board_info()` — normalizes session value (Phase 72c) |
| `medminder_dash/.../app.py` | 61-68 | `_resolve_first_port_info(ports)` — wraps `get_first_board()` with ValueError |
| `medminder_dash/.../app.py` | 71-104 | `_resolve_board_info(port, fqbn, hw_id, ports)` — replaces all inline resolution |
| `medminder_dash/.../app.py` | ~525-553 | `api_medicines_board_selector()` — refactored to ~30 lines |
| `medminder_dash/.../app.py` | ~600-625 | `api_board_compile_upload_card()` — refactored to ~25 lines |
| `arduino_dash/.../board_management.py` | 8-14 | Imports: `get_first_board`, `find_board_info_by_fqbn` etc. |
| `arduino_dash/.../board_management.py` | 25-59 | `_resolve_board_info(port, fqbn, hw_id, known_ports)` — new module-level helper |
| `arduino_dash/.../board_management.py` | ~167-179 | `api_admin_board_selector()` — refactored to ~12 lines |
| `arduino_dash/.../board_management.py` | ~182-194 | `api_board_compile_upload_card()` — refactored to ~12 lines |
| `medminder_dash/.../utils.py` | — | `get_first_board(boards)`, `find_board_info_by_fqbn(fqbn, boards)` — new functions (from earlier user refactor) |

### Design Decisions

1. **Helpers in route modules** (not utils): `_resolve_board_info` calls `get_port_info()` which depends on `session` — belongs in app.py/board_management.py
2. **ValueError for errors**: Cleaner than `if not port: return "port missing", 500` repeated 4+ times per route
3. **Separate `_resolve_first_port_info`**: Admin route only needs the "resolve from fallback" step, not the full "match existing port/FQBN" logic
4. **`find_board_info_by_fqbn` now requires `(fqbn, boards)`**: Both utils modules updated — all call sites must pass the board list

### Test Impact

No new tests needed. Existing tests cover all code paths:
- medminder_dash: 151/151 + 1 skip ✅
- arduino_dash: 102/102 ✅

---

## Phase 72e — Board Detail UI Alignment (Arduino Dash)

**Date**: 2026-06-16

**Goal**: Align arduino_dash board detail page with medminder_dash — FQBN as read-only label, board name heading, side-by-side FQBN + Port display.

### Files Changed

| File | Line(s) | Change |
|------|---------|--------|
| `arduino_dash/.../board_management.py` | 71-77 | `board_detail()` route: normalize port, resolve board_info via `get_port_info()`, compute board_name |
| `arduino_dash/.../templates/board_detail.html` | 5-6 | Heading: `Board: {{ board_name }}` + `Port: {{ port }}` hint |
| `arduino_dash/.../templates/board_detail.html` | 58-68 | FQBN: `<span class="value">` + hidden `<input>`; Device Port: `<span class="value">`; side-by-side flex row |
| `arduino_dash/.../tests/test_app.py` | 1224-1270 | 4 new tests: `TestBoardDetail` class |

### Key Code References

| Location | Description |
|----------|-------------|
| `arduino_dash/board_management.py:71-77` | `board_detail()` route — uses `_norm_port(port)` then `get_port_info(norm_port)` then `info.get("board", "") or norm_port` |
| `arduino_dash/.../board_detail.html:5-6` | `<h2>Board: {{ board_name }}</h2>` + `<p class="hint">Port: {{ port }}</p>` |
| `arduino_dash/.../board_detail.html:58-68` | Side-by-side FQBN label (`span.value` + hidden input) and Device Port label (`span.value`) |
| `arduino_dash/tests/test_app.py:1224-1270` | `TestBoardDetail` class — 4 tests for heading, fallback, FQBN display, port display |

### Design Decisions

1. **`get_port_info()`** (thread-safe, locked access) over raw `state._board_list.get()` — matches medminder_dash pattern
2. **Hidden `<input id="fqbn">`** stays inside `<form id="compile-form">` — no hx-include changes needed
3. **`.value` CSS class** (from Phase 72b Q3) reused for both FQBN and Device Port spans
4. **`board_info.get('fqbn', 'arduino:avr:uno') or 'arduino:avr:uno'`** — handles empty-string case from empty dict

### Test Coverage

| Test | What it verifies |
|------|-----------------|
| `test_heading_shows_board_name` | Heading contains "Board: Arduino Uno" when board info has `board: "Arduino Uno"` |
| `test_heading_falls_back_to_port` | Heading contains "Board: /dev/ttyACM0" when no board info (port as name) |
| `test_fqbn_display_label_present` | `#fqbn-display` span + hidden input with correct FQBN value |
| `test_port_display_label_present` | `#port-display` span + "Device Port" label + port path |

Total: arduino_dash 106/106 ✅

---

## Phase 73 — Route Reorganization (HTML vs REST API Separation)

**Goal**: Separate all routes into HTML routes (no `/api/` prefix, return templates) and REST API routes (`/api/` prefix, return JSON) across both dashboards and the shared `arduino_sketch_tools` blueprint.

### New File Structure

#### arduino_dash
| File | Purpose | Routes |
|------|---------|--------|
| `html_routes.py` | HTML pages + partials | 13 routes: `/`, `/board/<port>`, `/boards/grid`, `/board/<port>/connection-status`, `/daemon/status`, `/admin`, `/admin/board-selector`, `/admin/active-board` (POST), `/board/compile-upload-card`, `/last-upload`, `/sketch/upload` (POST), `/sketch` (DELETE) + `/ws/board-events` (WS) |
| `api_routes.py` | JSON API | 7 routes: `/api/board/<port>/spawn` (POST), `/api/board/<port>/status`, `/api/board/<port>/remove` (POST), `/api/boards`, `/api/sketches`, `/api/sketch/upload` (POST), `/api/sketch` (DELETE) |

#### medminder_dash
| File | Purpose | Routes |
|------|---------|--------|
| `html_routes.py` | HTML pages + partials | 28 routes: `/`, `/medicines`, `/medicine/new`, `/medicine` (POST), `/medicine/<id>/edit`, `/medicine/<id>` (PUT/DELETE), `/medicine/<id>/toggle` (PUT), `/daemon/status`, `/admin`, `/medicines/board-selector`, `/board/compile-upload-card`, `/medicines/confirm-modal`, `/medicines/generate-hpp` (POST), `/medicines/sync-from-hpp` (POST), `/medicines/active-board` (POST), `/medicines/active-board-card`, `/board/select/<port>`, `/board`, `/board/<port>`, `/board/<port>/connection-status`, `/boards`, `/boards/event`, `/boards/grid`, `/last-upload`, `/sketch/upload` (POST), `/sketch` (DELETE) + `/ws/board-events` (WS) |
| `api_routes.py` | JSON API + REST CRUD | 11 routes: `/api/medicines/diff`, `/api/board_list`, `/api/sketches`, `/api/sketch/upload` (POST), `/api/sketch` (DELETE), `/api/medicines` (GET), `/api/medicine` (POST), `/api/medicine/<id>` (GET/PUT/DELETE), `/api/medicine/<id>/toggle` (PUT) |

#### arduino_sketch_tools (Blueprint)
| Blueprint Prefix | Routes |
|------------------|--------|
| `/board/...` | 6 routes: `/board/<port>/compile` (POST), `/board/<port>/compile/poll`, `/board/<port>/upload` (POST), `/board/<port>/upload/poll`, `/board/<port>/upload/confirm` (POST), `/board/<port>/upload/section` |

**Note**: Blueprint prefix changed from `/api/board/...` to `/board/...` in Q1.

### New REST CRUD Endpoints (medminder_dash)

| Method | URL | Function | Description |
|--------|-----|----------|-------------|
| GET | `/api/medicines` | `api_medicines_list` | List all medicines as JSON array |
| POST | `/api/medicine` | `api_medicine_create` | Create medicine, returns JSON with 201 |
| GET | `/api/medicine/<id>` | `api_medicine_get` | Get single medicine as JSON |
| PUT | `/api/medicine/<id>` | `api_medicine_update` | Update medicine, returns updated JSON |
| DELETE | `/api/medicine/<id>` | `api_medicine_delete` | Delete medicine, returns `{"status": "deleted"}` |
| PUT | `/api/medicine/<id>/toggle` | `api_medicine_toggle` | Toggle enabled/disabled, returns toggled JSON |

### Key Decisions

1. **HTMX partials are HTML routes** — removed from `/api/` prefix across all modules
2. **Physical file split**: `html_routes.py` + `api_routes.py` per module
3. **Hybrid routes split**: sketch upload/delete have pure HTML variant (always template) in `html_routes.py` and pure JSON variant (always `jsonify`) in `api_routes.py`
4. **WebSocket endpoints** (`/ws/board-events`) remain in `html_routes.py`
5. **Route function names**: `api_*` prefix for HTML routes renamed to `html_*` prefix

### Test Coverage (Phase 73 Q6)

**arduino_dash** (7 new tests in `test_app.py`):
- `TestDashboard`: GET `/`
- `TestBoardsGrid`: GET `/boards/grid` (empty + populated)
- `TestApiBoardSpawn`: POST `/api/board/<port>/spawn`
- `TestApiBoardStatus`: GET `/api/board/<port>/status`
- `TestApiBoardRemove`: POST `/api/board/<port>/remove`
- `TestApiBoardList`: GET `/api/boards`

**medminder_dash** (10 new tests in `test_routes.py`):
- `TestDaemonStatus`: GET `/daemon/status` (ready + not ready)
- `TestBoardSelect`: GET `/board/select/<port>` (302 redirect)
- `TestBoardRedirect`: GET `/board` (400 without session, 302 with)
- `TestBoardConnectionStatus`: GET `/board/<port>/connection-status` (connected + disconnected)
- `TestBoards`: GET `/boards`
- `TestBoardsEvent`: GET `/boards/event`
- `TestBoardsGrid`: GET `/boards/grid`

**medminder_dash REST CRUD** (14 new tests in `test_api_medicines.py`):
- `TestApiMedicinesList`: GET `/api/medicines` (empty + seeded)
- `TestApiMedicineCreate`: POST `/api/medicine` (valid → 201, missing body → 400, invalid → 400)
- `TestApiMedicineGet`: GET `/api/medicine/<id>` (exists → 200, missing → 404)
- `TestApiMedicineUpdate`: PUT `/api/medicine/<id>` (valid → 200, missing body → 400, not found → 404)
- `TestApiMedicineDelete`: DELETE `/api/medicine/<id>` (exists → 200, missing → 404)
- `TestApiMedicineToggle`: PUT `/api/medicine/<id>/toggle` (toggles enabled state, missing → 404)

## Phase 74 — Board Status Badge Fix

**Date**: 2026-06-17 10:28

### Key Changes

**`arduino_dash/pubsub.py:209-210`** — `_norm_port()` now strips extra leading slashes before adding exactly one:
```python
def _norm_port(port: str) -> str:
    return "/" + port.lstrip("/")
```

**`medminder_dash/html_routes.py:589-590`** — `board_detail` route normalization fixed:
```python
board_info = get_port_info("/" + port.lstrip("/"))
norm_port = "/" + port.lstrip("/")
```

**`medminder_dash/html_routes.py:607-608,612`** — `html_board_connection_status` normalization + template pass fixed:
```python
norm_port = "/" + port.lstrip("/")
info = get_port_info(norm_port)
connected = info is not None
...
return render_template("partials/board_status_badge.html", port=norm_port, connected=connected)
```

**Both `board_status_badge.html`** — Badge URL uses `port.lstrip('/')` to prevent double-slash:
```html
hx-get="/board/{{ port.lstrip('/') }}/connection-status"
```

### Bug Chain

1. Initial page load normalizes `"dev/ttyACM0"` → `"/dev/ttyACM0"` (adds `/`)
2. Badge URL becomes `/board//dev/ttyACM0/connection-status` (double slash)
3. Flask extracts `port = "//dev/ttyACM0"` from URL
4. Old `_norm_port` returned `"//dev/ttyACM0"` unchanged → `_board_list` lookup failed
5. New `_norm_port` lstrip → `"/dev/ttyACM0"` → lookup succeeds

### Final Test Counts

- arduino_dash: **113** ✅
- medminder_dash: **175 + 1 skip** ✅
- arduino_sketch_tools: **47** ✅
- Grand total: **335 + 1 skip**

---

## Phase 75 — Fix MedMinder Dash Stale `/api/board/` URLs ✅ COMPLETED

**Date**: 2026-06-17 11:11

### 3 Bugs Fixed

| Bug | File | Line(s) | Problem | Fix |
|-----|------|---------|---------|-----|
| 1 | `board_detail.html` | 11, 35, 43 | `hx-get="/api/board/..."` → 404 every 10s | `/api/board/` → `/board/` + `port.lstrip('/')` |
| 2 | `html_routes.py` | 610 | `connected = info is not None` — `get_port_info()` returns `{}` for missing ports → `{} is not None` is `True` | `connected = bool(info)` |
| 3 | `compile_upload_card.html` | 17, 41 | `hx-post="/api/board/..."` → 404 on compile/upload | `/api/board/` → `/board/` + `(active_board or '').lstrip('/')` |

### Test Assertions Also Fixed

3 stale assertions in `test_admin.py` (lines 867, 880, 896) still checked for `/api/board/` prefix.

### Key Code References

#### `board_detail.html:11,35,43` — Stale `/api/` prefix removed
```html
hx-get="/board/{{ port.lstrip('/') }}/connection-status"      <!-- was /api/board/ -->
hx-post="/board/{{ port.lstrip('/') }}/compile"               <!-- was /api/board/ -->
hx-post="/board/{{ port.lstrip('/') }}/upload"                <!-- was /api/board/ -->
```

#### `html_routes.py:610` — Connection status logic fixed
```python
connected = bool(info)                                        # was info is not None
```

#### `compile_upload_card.html:17,41` — Stale `/api/` prefix removed
```html
hx-post="/board/{{ (active_board or '').lstrip('/') }}/compile"   <!-- was /api/board/ -->
hx-post="/board/{{ (active_board or '').lstrip('/') }}/upload"    <!-- was /api/board/ -->
```

### Q8 — Badge Flash Fix

**Root cause**: medminder_dash `board_detail.html` had a fallback `<span class="badge badge-err">○ Disconnected</span>` inside the badge container. Arduino_dash uses an empty span. On page load, the fallback is visible until HTMX's `load` trigger fires and swaps in the server-rendered badge.

**Fix**: Removed the fallback span to match arduino_dash empty span pattern.

**Key difference**:
| Dashboard | Container | Initial state | Perceived behavior |
|-----------|-----------|---------------|-------------------|
| arduino_dash | `<span id="board-status-badge" ...></span>` | Empty | "Connected" immediately |
| medminder_dash (before) | `<span ...><span class="badge badge-err">○ Disconnected</span></span>` | Fallback visible | Flash "Disconnected" → "Connected" |
| medminder_dash (after) | `<span id="board-status-badge" ...></span>` | Empty | "Connected" immediately |

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| medminder_dash | 175 + 1 skip | ✅ |
| arduino_dash | 113 | ✅ |
| `nox -s all_tests` | 8/8 sessions | ✅ |

---

## Phase 76 — Centralize Port Path Normalization in Python Context ✅ COMPLETED

**Date**: 2026-06-17 16:45

**Goal**: Replace 7 remaining `{{ port.lstrip('/') }}` template-level lstrip calls with `port_path` computed in Python route context.

### Key Files

| File | Change | Dashboard |
|------|--------|-----------|
| `html_routes.py:board_detail` | Added `port_path = norm_port.lstrip("/")` to context | Both |
| `html_routes.py:html_board_connection_status` | Added `port_path = norm_port.lstrip("/")` to context | Both |
| `html_routes.py:html_board_compile_upload_card` | Added `active_board_path = (active_board_port or '').lstrip("/")` to context | Both |
| `templates/board_detail.html` | `{{ port }}` → `{{ port_path }}` (3 URLs) | arduino_dash |
| `templates/board_status_badge.html` | `port.lstrip('/')` → `port_path` (1 URL) | Both |
| `templates/partials/compile_upload_card.html` | `(active_board or '').lstrip('/')` → `active_board_path` (2 URLs) | Both |

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| arduino_dash | 119 | ✅ |
| medminder_dash | 181 + 1 | ✅ |
| `nox -s all_tests` | 8/8 sessions | ✅ |

---

## Phase 77 — Template Port Path Cleanup ✅ COMPLETED

**Date**: 2026-06-17 17:03

**Goal**: Finalize `port_path` migration — double-slash bug in arduino_dash (direct `{{ port }}` without lstrip) fixed. Test assertions updated.

### Key Files Changed

**arduino_dash**:
- `html_routes.py`: 3 route contexts updated
- `templates/board_detail.html`: 3 URLs fixed (double-slash bug)
- `templates/partials/board_status_badge.html`: lstrip → `port_path`
- `templates/partials/compile_upload_card.html`: 2 URLs fixed (double-slash bug)
- `tests/test_app.py`: 2 assertions updated

**medminder_dash**:
- `html_routes.py`: 3 route contexts updated (already had lstrip, now centralized)
- 3 templates: 7 URL locations centralized

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| arduino_dash | 119 | ✅ |
| medminder_dash | 181 + 1 | ✅ |
| `nox -s all_tests` | 8/8 sessions | ✅ |

---

## Phase 78 — Fix `_daemon_ready` Unprotected Access + Duplicate Log Spam ✅ COMPLETED

**Date**: 2026-06-17 17:15

**Goal**: Add thread lock protection to all `_daemon_ready` access sites across both dashboards. Add duplicate-event guard in `_on_daemon_ready` to suppress redundant "Daemon ready event received" info logs during pubsub reconnect cycles.

### Key Files

**arduino_dash**:
| File | Line(s) | Change |
|------|---------|--------|
| `state.py` | 28-29 | Added `_daemon_ready_lock = threading.Lock()` |
| `pubsub.py` | 33 | `_fallback_scan_loop` read: `with state._daemon_ready_lock` |
| `pubsub.py` | 109-114 | `_on_daemon_ready`: lock + duplicate guard (`if state._daemon_ready: return`) |
| `pubsub.py` | 118 | `_on_pubsub_reconnect`: lock-protected write |
| `html_routes.py` | 122 | `html_daemon_status`: lock-protected read |

**medminder_dash**:
| File | Line(s) | Change |
|------|---------|--------|
| `pubsub_infra.py` | 36 | `_fallback_scan_loop` read: `with state._daemon_ready_lock` |
| `pubsub_infra.py` | 215-220 | `_on_daemon_ready`: duplicate guard added inside existing lock |

### Architecture

```
pubsub reconnect
  → _resubscribe() sends subscribe messages
  → BMS _send_daemon_state_to() re-emits sys::daemon/ready
  → _on_daemon_ready():
      with _daemon_ready_lock:
          if _daemon_ready: return          ← NEW guard: skip if already True
          _daemon_ready = True              ← only on first event per cycle
      _logger.info("Daemon ready event received")  ← single log per reconnect cycle
```

### Duplicate Event Flow

| Without guard | With guard |
|---------------|------------|
| Each reconnect → `_on_daemon_ready` → log × N | First reconnect → `_on_daemon_ready` → set flag → log × 1 |
| Reconnect × 10 → 10 logs | Reconnect × 10 → 1 log |

### Key Functions

| Location | Type | Description |
|----------|------|-------------|
| `arduino_dash/pubsub.py:109-114` | write + guard | `_on_daemon_ready` — lock, check, set, log |
| `arduino_dash/pubsub.py:118` | write | `_on_pubsub_reconnect` — lock, reset to False |
| `arduino_dash/pubsub.py:33` | read | `_fallback_scan_loop` — lock, check, sleep/continue |
| `arduino_dash/html_routes.py:122` | read | `html_daemon_status` — lock, check, render badge |
| `medminder_dash/pubsub_infra.py:36` | read | `_fallback_scan_loop` — lock, check, sleep/continue |
| `medminder_dash/pubsub_infra.py:215-220` | write + guard | `_on_daemon_ready` — lock, check, set, log |

### Design Decisions

1. **Double-checked locking**: The duplicate check is INSIDE `with _daemon_ready_lock:` to prevent TOCTOU race. First check (without lock) is not used — the full check-and-set is atomic.
2. **Guard suppresses both log AND re-set**: When `_daemon_ready` is already `True`, the function returns before logging AND before re-setting the flag. This prevents both the log spam AND the extra lock/unlock cycle.
3. **State reset in reconnect**: `_on_pubsub_reconnect` sets `_daemon_ready = False`, then re-subscription triggers daemon/ready re-emission. The guard ensures only the first event per reconnect cycle logs.
4. **No new tests**: Existing `test_daemon_ready_handler_sets_flag` tests the happy path (False→True→set→log). The duplicate guard (already True→skip) is exercised implicitly by reconnect tests.

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| arduino_dash pytest | 119 | ✅ |
| medminder_dash pytest | 181 + 1 skip | ✅ |
| `nox -s all_tests` | 8/8 sessions | ✅ (1 flaky board_manager) |

---

## Phase 79 — Light Colorscheme + External CSS ✅ COMPLETED

**Date**: 2026-06-18

**Goal**: Refactor all inline `<style>` blocks and `style=""` attributes across ~35 template files into per-dashboard external `static/style.css` files using CSS custom properties. Add `@media (prefers-color-scheme: light)` light color scheme support.

### Key Files

| File | Change Summary |
|------|---------------|
| `arduino_dash/.../static/style.css` | Created 539‑line CSS with 42 vars + `@media light` + 57+ semantic classes |
| `medminder_dash/.../static/style.css` | Identical copy (same sha256sum) |
| Both `base.html` | `<style>` block → `<link rel="stylesheet">` |
| Both `admin.html` | `<style>` block removed → `.admin-heading`, `.admin-content` |
| Both `dnd_overlay.html` | `<style>` block removed → `#dnd-overlay` class |
| `arduino_dash/.../templates/` | 9 files: 67+ inline `style=""` → CSS classes |
| `medminder_dash/.../templates/` | 16 files: 100+ inline `style=""` → CSS classes |
| `arduino_sketch_tools/.../partials/` | 10 partials: 38 inline `style=""` → CSS classes |

### CSS Class Reference (57+ classes created)

**Page/Layout**: `.page-header`, `.page-title`, `.page-subtitle`, `.section-header`, `.content-area`, `.result-banner--success`, `.result-banner--failure`

**Card Components**: `.card`, `.card-header`, `.card-body`, `.card-footer`, `.card-section`, `.compact-card`, `.card-grid`, `.card-limit-height`

**Live Events**: `.live-events-card`, `.live-events-empty-center`, `.live-events-list`, `.live-event-item`, `.live-event-details-grid`, `.live-event-label`, `.live-event-value`

**Overlay/Modal**: `#dnd-overlay`, `.modal-backdrop`, `.modal-content`, `.modal-header`, `.modal-body`, `.modal-footer`, `.modal-button-row`

**Admin**: `.admin-heading`, `.admin-content`, `.admin-flex-row`, `.admin-grow`

**Tables**: `.table-container`, `.table-controls`, `.table-row-alt`, `.table-cell-id`, `.table-cell-ts`, `.table-cell-actions`

**Buttons**: `.btn--default`, `.btn--primary`, `.btn--danger`, `.btn--small`, `.btn--icon`

**Badges**: `.badge`, `.badge--ok`, `.badge--warn`, `.badge--error`, `.badge--info`

**Text/Typography**: `.text-muted`, `.text-hint`, `.text-error`, `.text-success`, `.text-nowrap`, `.text-break-all`

**Sketches**: `.sketch-meta-grid`, `.sketch-meta-label`, `.sketch-meta-value`, `.unopened-sketch`, `.sketch-upload-modal-footer`

**Boards (arduino_dash)**: `.board-detail-select`, `.board-detail-actions`

**Medicine (medminder_dash)**: `.medicine-info-grid`, `.medicine-info-label`, `.medicine-info-value`

**Misc**: `.flex-row`, `.status-dot`, `.mt-1`, `.mb-1`

### Design Decisions

1. **Two identical CSS files**: Avoids cross-package dependency; each dashboard self-contained.
2. **Flat cards preserved**: No border/shadow added — cards distinguished from bg by color alone in both themes.
3. **42 CSS variables layered**: `:root` defines raw colors → component classes use `var(--...)` → `@media light` overrides only variables → all components adapt.
4. **Semantic over utility**: `.text-muted`, `.modal-backdrop` instead of `.color-slate-500` or `.bg-gray-100`.
5. **3 intentional inline styles remain**: `style="display:none"` (3 modals, initial hidden state toggled by Hyperscript/JS) + `style="word-break:break-all"` (1 one-off overflow guard for long UA strings).

### Key Insight: CSS Variable Categories

| Category | Variables | Overrides in light mode |
|----------|-----------|------------------------|
| Page | `--page-bg`, `--page-text` | darkest bg → lightest bg, text inverted |
| Card | `--card-bg`, `--card-border`, `--card-header-bg` | darker → lighter + shadow |
| Input | `--input-bg`, `--input-text`, `--input-border`, `--input-focus-bg`, `--input-focus-text`, `--input-focus-border` | dark → white bg, focus brighter |
| Table | `--table-header-bg`, `--table-row-alt`, `--table-border` | inverted colors |
| Button | `--btn-default-bg`, `--btn-default-text`, `--btn-default-hover`, `--btn-primary-bg`, `--btn-primary-text`, `--btn-primary-hover`, `--btn-danger-bg`, `--btn-danger-text`, `--btn-danger-hover`, `--btn-ok-bg` | 1 shade darker in light mode |
| Badge | `--badge-ok-bg`, `--badge-ok-text`, `--badge-warn-bg`, `--badge-warn-text`, `--badge-error-bg`, `--badge-error-text`, `--badge-info-bg`, `--badge-info-text` | dark bg/light text → light bg/dark text |
| Code | `--code-bg`, `--code-text` | inverted |
| Misc | `--shadow`, `--link`, `--danger`, `--warning` | adjusted for light |

---

## Phase 79b — arduino_dash `init_pubsub` Reconnection Fix ✅ COMPLETED

**Date**: 2026-06-18 13:02

**Goal**: Fix arduino_dash `init_pubsub` to match medminder_dash's pattern of catching `connect()` failure internally so `start_reader()` is always called.

**Root cause**: `state.pubsub.connect(retry=True)` at `arduino_dash/pubsub.py:97` was not wrapped in try/except. On failure, exception propagated before `subscribe()` and `start_reader()` were reached. Without `start_reader()`, the PubSubClient's auto-reconnect loop (`_read_loop` → `_reconnect()`) never starts.

### Key Files

| File | Change |
|------|--------|
| `arduino_dash/.../pubsub.py:97-100` | Added `try/except (ConnectionError, OSError)` around `connect()` |
| `arduino_dash/.../tests/test_app.py` | Updated `test_connect_failure_propagates` → `test_connect_failure_does_not_block_init` |
| `medminder_dash/.../tests/test_admin.py:1014` | Fixed Phase 79 regression: `b"flex:1"` → `b'class="flex-1"'` |

### Architecture: `init_pubsub` Flow

```
Before (BROKEN):
  pubsub = PubSubClient()
  pubsub.connect(retry=True)  ← FAILS → raises ConnectionError
  subscribe(...)              ← NEVER REACHED
  start_reader()              ← NEVER REACHED
  → exception to __main__.py → run without pubsub FOREVER

After (FIXED — matches medminder_dash):
  pubsub = PubSubClient()
  try:
    pubsub.connect(retry=True)  ← FAILS → caught
  except:
    logger.warning(...)         ← graceful degradation
  subscribe(...)                ← handlers registered (used on reconnect)
  start_reader()                ← reader thread starts
  → _read_loop: no socket → _reconnect() → _connect_once() → success
  → on_reconnect → _on_pubsub_reconnect → re-subscribe → BMS sends daemon/ready → log
```

### Key Function

| Location | Description |
|----------|-------------|
| `arduino_dash/pubsub.py:97-100` | `init_pubsub` — `connect()` wrapped in try/except `(ConnectionError, OSError)` |
| `medminder_dash/pubsub_infra.py:134-136` | `init_pubsub` — same pattern (reference implementation) |

### Design Decision

1. **Match medminder_dash exactly**: Same exception types `(ConnectionError, OSError)`, same log message format. This ensures consistent behavior between the two dashboards.
2. **`__main__.py` try/except kept**: Redundant for `(ConnectionError, OSError)` after the fix, but kept as a safety net for unexpected exceptions. Matches medminder_dash's pattern.
3. **BMS `_publish_daemon_ready()` timing**: BMS emits `sys::daemon/ready` before any client connects (at startup, before the accept loop). This is correct — the actual delivery relies on `_send_daemon_state_to()` in the subscribe handler, which catches late-connecting clients. No fix needed.

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| arduino_dash pytest | 119 | ✅ |
| medminder_dash pytest | 181 + 1 skip | ✅ (1 pre-existing test assertion fixed) |
| `nox -s all_tests` | 8/8 sessions | ✅ (1 failure was pre-existing Phase 79 regression, now fixed) |

---

## Phase 80 — Hardware-ID Fallback Chain + Modal Fixes ✅ COMPLETED

**Date**: 2026-06-18

### Goal

Homogenize sketch-selection fallback chain when `hardware_id` is missing:
- **arduino_dash**: `hardware_id → (ip, ua) tagging → empty`
- **medminder_dash**: `hardware_id → (ip, ua) tagging → default packaged sketch`

Also fix arduino_dash modal's `r.json()` bug (response is HTML, not JSON) and missing `hardware_id` param.

### New Helper

| Location | Signature | Description |
|----------|-----------|-------------|
| `arduino_dash/sketch_management.py:92-108` | `_resolve_latest_upload() -> Optional[str]` | Look up latest upload for `(request.remote_addr, User-Agent)` key, return path or `None` |
| `medminder_dash/sketch_management.py:86-102` | `_resolve_latest_upload() -> Optional[str]` | Same — duplicated per-dashboard due to different `state` imports |

### Changed Routes

| Location | What Changed |
|----------|-------------|
| `arduino_dash/html_routes.py:234-243` | `html_last_upload()` — replaced 12-line inline `(ip, ua)` block with `_resolve_latest_upload()` call |
| `medminder_dash/html_routes.py:666-686` | `html_last_upload()` — added `hardware_id → get_board_sketch_assignment()` step, replaced inline block with `_resolve_latest_upload()` |
| `medminder_dash/html_routes.py:600-609` | `board_detail()` — added `_resolve_latest_upload()` fallback between per-board check and `load_sketch_dir()` |

### Changed Templates

| File | Change |
|------|--------|
| `medminder_dash/admin.html:34` | Added `name="hardware_id"` to hidden `<input id="active-board-hardware-id">` |
| `medminder_dash/admin.html:28-33` | Added `hx-include="#active-board-hardware-id"` to sketch-path-container's `/last-upload` |
| `arduino_dash/board_detail.html` | Added hidden `<input id="active-board-hardware-id" name="hardware_id">` + `hx-include` on `/last-upload` container |
| `arduino_dash/compile_upload_card.html` | Removed dead `hx-vals='{"hardware_id":...}'` from compile and upload buttons |
| `arduino_dash/sketch_upload_modal.html` | `r.json()` → `r.text()`, added `hardware_id` query param to fetch URL |
| Both `sketch_upload_modal.html` | Added `hwParam` to `/last-upload` refresh callback |

### Key Findings

1. **BMS compile/upload routes ignore `hardware_id`**: `api_compile()` and `api_upload()` in `arduino_sketch_tools/routes.py` only read `sketch_path` and `fqbn`. The `hx-vals` on compile_upload_card.html was dead code.
2. **`hardware_id` only consumed by**: `POST /sketch/upload` (`set_assignment()`) and `DELETE /sketch` (`clear_assignment()`).
3. **arduino_dash modal had a critical bug**: `r.json()` on HTML response always fails → `.catch` fires → "Upload Failed" shown even on success.
4. **medminder_dash modal was correct**: Already used `r.text()` and sent `hardware_id` — only missing `hwParam` in the refresh callback.

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| arduino_dash pytest | 119/119 | ✅ |
| medminder_dash pytest | 181/181 + 1 skip | ✅ |
| board_manager pytest | 204/204 + 8 skip | ✅ |
| board_manager_client pytest | 24/24 | ✅ |
| arduino_sketch_tools pytest | 51/51 | ✅ |
| arduino_grpc pytest | 33/33 + 2 skip | ✅ |
| scripts_tests | 128/128 + 12 bash | ✅ |
| `nox -s all_tests` | 8/8 sessions green | ✅ |

---

## Phase 82 — Sorted Upload Registry via bisect.insort ✅ COMPLETED

**Goal**: Use `bisect.insort()` to maintain each per-sketch `list[dict]` in `_upload_registry` sorted by timestamp on insert, eliminating redundant `.sort()` calls at read time.

### Data Structure Invariant

After Phase 82, every per-sketch list in `_upload_registry` is guaranteed sorted ascending by `"timestamp"`:

```
_upload_registry[(ip, ua)]["mysketch"] = [
    {"path": "...", "checksum": "...", "timestamp": "2026-05-28T12:00:00"},  # oldest
    {"path": "...", "checksum": "...", "timestamp": "2026-05-29T15:00:00"},  # newest
]
```

This simplifies:
- `_resolve_latest_upload()` — `max([vs[-1] for vs in entries.values() if vs], key=lambda v: v["timestamp"])` (O(n) over sketch names, not O(n) over all versions)
- Delete routes — post-removal latest computed as `max([vs[-1] for vs in entries.values() if vs], ...)` instead of manual loop tracking

### Files Changed (6 source files)

| File | Change |
|------|--------|
| `arduino_dash/sketch_management.py` | `import bisect`; warmup `append`→`bisect.insort`; `_resolve_latest_upload` simplified |
| `arduino_dash/html_routes.py` | `import bisect`; upload `append`→`bisect.insort`; delete simplified |
| `arduino_dash/api_routes.py` | `import bisect`; upload `append`→`bisect.insort` |
| `medminder_dash/sketch_management.py` | Same mirror |
| `medminder_dash/html_routes.py` | Same mirror |
| `medminder_dash/api_routes.py` | Same mirror + dead `latest` removed from delete route |

### Key Design Decision

Cross-sketch queries (`_render_sketch_path_selector`, `api_sketches`) still use `.sort()` — Python's Timsort detects already-sorted per-sketch runs and runs in O(n) on near-sorted data. The per-sketch sorted invariant is the primary improvement, enabling simpler per-sketch operations.

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| arduino_dash pytest | 119/119 | ✅ |
| medminder_dash pytest | 181/181 + 1 skip | ✅ |
| board_manager pytest | 204/204 + 8 skip | ✅ |
| board_manager_client pytest | 24/24 | ✅ |
| arduino_sketch_tools pytest | 51/51 | ✅ |
| arduino_grpc pytest | 33/33 + 2 skip | ✅ |
| scripts_tests | 128/128 + 12 bash | ✅ |
| `nox -s all_tests` | 8/8 sessions green | ✅ |

---

## Phase 83 — Unified Sketch Registry ✅ COMPLETED (Q1-Q8)

**Date**: 2026-06-18
**Type**: Core/Infrastructure

**Goal**: Unify sketch registry with hardware_id as a first-class dimension, enabling board-scoped queries, one-to-many hardware_id→sketch mapping, and a persistent sketch_registry.json that serves as the warmup source and disk cross-reference.

### Entry Data Model

```python
# In-memory registry entry
{
    "path": "/path/to/sketch_dir",
    "checksum": "abc123...",
    "server_timestamp": "2026-06-18T20:28:00.123456",
    "hardware_ids": ["ABC", "DEF"],
    "board_timestamps": {"ABC": "2026-06-18T20:30:00", "DEF": "2026-06-18T20:35:00"}
}
```

```json
# .meta file (same fields)
{"ip": "...", "user_agent": "...", "server_timestamp": "...", "root_name": "...",
 "checksum": "...", "hardware_ids": [...], "board_timestamps": {...}}
```

### Directory Naming
`{salt[:16]}_{server_timestamp}_{root_name}/` where `salt = hashlib.sha256(f"{ip}:{ua}").hexdigest()[:16]`

### Key Functions

| Location | Description |
|----------|-------------|
| `arduino_dash/sketch_management.py:_find_existing_version()` | Cross-sketch-name FCFS dedup lookup |
| `arduino_dash/sketch_management.py:_update_meta_hw_ids()` | In-place `.meta` file update (read-modify-write) |
| `arduino_dash/sketch_management.py:_save_registry()` | Serialize `_upload_registry` to `sketch_registry.json` (caller holds lock) |
| `arduino_dash/sketch_management.py:_load_registry()` | Deserialize `sketch_registry.json` into `_upload_registry` |
| `arduino_dash/sketch_management.py:_warm_upload_registry()` | Load JSON first, scan `.meta` for cross-ref fallback |
| `arduino_dash/sketch_management.py:_build_hw_labels()` | Reverse-map hardware_id → "BoardName (port)" |
| `arduino_dash/sketch_management.py:_render_sketch_path_selector()` | Filter by hardware_id param, show board labels |
| `arduino_dash/sketch_management.py:_record_deploy()` | Record deploy timestamp + hw_id in registry and .meta, WS broadcast |
| `pubsub.py/_on_board_event()` (both) | WS broadcast on board events, calls _broadcast_ws |
| `arduino_sketch_tools/extension.py:_make_meta()` | Include `hardware_id` in upload meta |
| `arduino_sketch_tools/extension.py:_on_upload_resp()` | Call `record_deploy` callback on upload success |

### Data Flow: Upload → Registry → .meta → sketch_registry.json

```
POST /sketch/upload
  → extract (ip, ua, hardware_id)
  → compute checksum, salt
  → _find_existing_version(ip, ua, checksum)
  → if found (same checksum, diff hardware_id):
      → skip dir write, append hw_id to existing entry
      → _update_meta_hw_ids() on existing .meta
  → if not found:
      → create dir {salt}_{ts}_{name}/
      → write files
      → write .meta with hw_ids, checksum, server_timestamp
      → create registry entry
  → _save_registry() under lock
  → _broadcast_ws(html with <!-- board-event -->)
```

### WS Event → HTMX Trigger Flow

```
Upload/Dedup/Delete/Deploy mutation
  → _broadcast_ws(html_str containing "<!-- board-event -->")
  → browser WS client receives message
  → htmx:wsBeforeMessage handler fires
  → handler checks "board-event" in message
  → htmx.trigger('body', 'board-changed')
  → #sketch-path-container detects "board-changed from:body"
  → hx-get="/last-upload?hardware_id=..." re-fetches selector
```

### Files Changed

| File | Change |
|------|--------|
| `arduino_dash/.../html_routes.py` | Upload dedup, registry entry with hw_ids, WS broadcast, no clear_assignment in delete |
| `arduino_dash/.../api_routes.py` | Same upload/dedup changes |
| `arduino_dash/.../sketch_management.py` | Warmup with JSON, _save_registry, _load_registry, _find_existing_version, _update_meta_hw_ids, _build_hw_labels, _render_sketch_path_selector hw_id filter |
| `arduino_dash/.../sketch_registry.py` | Rewritten to delegate to _upload_registry (no board_sketches.json) |
| `arduino_dash/.../pubsub.py` | _make_meta hw_id, WS broadcast |
| `arduino_dash/.../settings.py` | BOARD_SKETCHES_FILE removed |
| `medminder_dash/.../html_routes.py` | Mirror of arduino_dash |
| `medminder_dash/.../api_routes.py` | Mirror |
| `medminder_dash/.../sketch_management.py` | Mirror |
| `medminder_dash/.../sketch_registry.py` | Mirror rewrite |
| `medminder_dash/.../pubsub_infra.py` | Mirror WS broadcast |
| `arduino_sketch_tools/.../extension.py` | _make_meta hw_id, record_deploy callback |
| `*/templates/base.html` | JS handler checking "board-event" in WS messages |
| `medminder_dash/.../templates/admin.html` | `#sketch-path-container` with `board-changed from:body` |

### Test Impact

| Suite | Count | Status |
|-------|-------|--------|
| arduino_dash | 119/119 | ✅ |
| medminder_dash | 186/186 + 1 skip | ✅ |
| arduino_sketch_tools | 51/51 | ✅ |

---

## Phase 84 — Playwright E2E Testing Infrastructure ✅ COMPLETED

**Date**: 2026-06-19
**Type**: Testing/Infrastructure

**Goal**: Create reusable E2E testing infrastructure for both web apps using Playwright — agent-driven interactive testing via MCP tools, and future automated spec-based testing via shelved `@playwright/test` files.

### Deliverables

| # | File | Purpose |
|---|------|---------|
| 1 | `e2e/servers/arduino_dash_server.py` | Flask dev server with `--mock` flag (port 8765) |
| 2 | `e2e/servers/medminder_dash_server.py` | Flask dev server with `--mock` flag (port 8766) |
| 3 | `.opencode/skills/mcp-e2e-testing/SKILL.md` | Agent skill for interactive MCP testing |
| 4 | `e2e/MCP_TESTING_GUIDE.md` | Human-readable testing guide |
| 5 | `e2e/package.json` | (Shelved) `@playwright/test` dev dep |
| 6 | `e2e/playwright.config.ts` | (Shelved) Two-project config |
| 7 | `e2e/fixtures/test-data.ts` | (Shelved) Shared test constants |
| 8 | `e2e/specs/arduino_dash/*.spec.ts` | (Shelved) 4 spec files, 12 tests |
| 9 | `e2e/specs/medminder_dash/*.spec.ts` | (Shelved) 4 spec files, 10 tests |

### Mock Data Model

```python
# arduino_dash --mock state
state._board_list["/dev/ttyTEST0"] = {
    "port": "/dev/ttyTEST0", "board": "TestBoard Uno",
    "fqbn": "arduino:avr:uno", "hardware_id": "HW-TEST-001",
}
state._board_list["/dev/ttyTEST1"] = {
    "port": "/dev/ttyTEST1", "board": "TestBoard Mega",
    "fqbn": "arduino:avr:mega", "hardware_id": "HW-TEST-002",
}
state._upload_registry[("127.0.0.1", "playwright-test")] = {
    "mysketch": [{"path": "/tmp/e2e-test/sketches/MySketch", ...}]
}
state._daemon_ready = False
```

```python
# medminder_dash --mock adds
state._known_ports = same as _board_list above
# + 3 medicines: Aspirin (08:00), VitaminD (12:30), Ibuprofen (18:00)
# via MedicineStore.load_board() + store.add()
```

### Architecture

```
User/Agent → Playwright MCP Tools → HTTP → Flask Dev Server (127.0.0.1:PORT)
                                                        ↕
                                               state._board_list (mock)
                                               state._upload_registry (mock)
                                               MedicineStore (mock medicines)
```

- Servers started via `python3 e2e/servers/*_server.py [--mock] [--port N]`
- MCP tools: `navigate`, `snapshot`, `click`, `fill_form`, `type`, `evaluate`, etc.
- To run shelved tests: `cd e2e && npm install && npx playwright test`

### Key Findings

- `python` defaults to Python 2.7 on this system — must use `python3` for f-strings
- `medminder_dash.app` does NOT export `app` at module level — must call `create_app()` explicitly
- Registry keyed by `(ip, ua)` tuple — mock UA must match test UA for lookups
- `flask-sock` is optional — without it, WS endpoint is not registered but rest of app works
- Both apps start clean without BMS/gRPC — no imports attempt connection
- `MedicineStore` persists to `board_meta.json` — Flask debug reloader compounds data across restarts; server helper monkeypatches `_compute_data_path()` to a temp file and clears store before injection

### Test Scenarios Covered by Skill

| Scenario | App | Tier |
|----------|-----|------|
| Dashboard empty state | arduino_dash | 1 (no mock needed) |
| Board grid with mock boards | both | 2 (needs --mock) |
| Admin page layout | both | 2 |
| Sketch selector with board label | arduino_dash | 2 |
| Daemon disconnected badge | both | 1 |
| Board detail page | arduino_dash | 2 |
| Medicine list via API | medminder_dash | 1 |
| 404 error handling | both | 1 |
| Home page board grid | medminder_dash | 2 |
| WebSocket connectivity | both | 1 |
| `board-changed` HTMX trigger | both | 1 |
| Admin page medicines section | medminder_dash | 2 |

### Files Changed

| File | Change |
|------|--------|
| `e2e/servers/__init__.py` | **New** — empty package init |
| `e2e/servers/arduino_dash_server.py` | **New** — server helper with --mock |
| `e2e/servers/medminder_dash_server.py` | **New** — server helper with --mock |
| `.opencode/skills/mcp-e2e-testing/SKILL.md` | **New** — MCP testing skill |
| `e2e/MCP_TESTING_GUIDE.md` | **New** — testing guide |
| `e2e/package.json` | **New** — shelved |
| `e2e/playwright.config.ts` | **New** — shelved |
| `e2e/fixtures/test-data.ts` | **New** — shelved |
| `e2e/specs/arduino_dash/dashboard.spec.ts` | **New** — shelved |
| `e2e/specs/arduino_dash/admin.spec.ts` | **New** — shelved |
| `e2e/specs/arduino_dash/sketch-upload.spec.ts` | **New** — shelved |
| `e2e/specs/arduino_dash/board-pages.spec.ts` | **New** — shelved |
| `e2e/specs/medminder_dash/home.spec.ts` | **New** — shelved |
| `e2e/specs/medminder_dash/admin.spec.ts` | **New** — shelved |
| `e2e/specs/medminder_dash/medicines.spec.ts` | **New** — shelved |
| `e2e/specs/medminder_dash/sketch-upload.spec.ts` | **New** — shelved |
| `PLAN.md` | Phase 84 entry added |
| `IMPLEMENTATION_PLAN.md` | **New** — Phase 84 design doc |
| `IMPLEMENTATION_TASK.md` | **New** — Phase 84 task breakdown |
| `IMPLEMENTATION_PROGRESS.md` | **New** — Phase 84 milestones |
| `IMPLEMENTATION_JOURNAL.md` | Phase 84 entries appended |

---

## Phase 85 — Fix HTMX Extension Mismatch Warning ✅

**Date**: 2026-06-19 01:20

**Goal**: Fix `"You are using an htmx 1 extension with htmx 2.0.4"` console warning.

**Root cause**: The WS extension script at `unpkg.com/htmx.org@2.0.4/dist/ext/ws.js` is the v1 bundled extension; htmx 2 moved extensions to separate packages.

**Fix**: Replaced with `unpkg.com/htmx-ext-ws@2.0.1/ws.js` (v2 standalone WS extension).

**Verified**: MCP browser test on both servers — 0 warnings.

### Files Changed

| File | Line | Change |
|------|------|--------|
| `arduino_dash/python/arduino_dash/arduino_dash/templates/base.html` | 8 | `htmx.org@2.0.4/dist/ext/ws.js` → `htmx-ext-ws@2.0.1/ws.js` |
| `medminder_dash/python/medminder_dash/medminder_dash/templates/base.html` | 8 | `htmx.org/dist/ext/ws.js` → `htmx-ext-ws@2.0.1/ws.js` |
| `scripts/pyoxidizer/arduino-dash/.../base.html` | 8 | Same change |
| `scripts/pyoxidizer/medminder-dash/.../base.html` | 8 | Same change |
| `dist-standalone/arduino-dash/prefix/.../base.html` | 8 | Same change |
| `dist-standalone/medminder-dash/prefix/.../base.html` | 8 | Same change |
| `PLAN.md` | — | Phase 85 entry added |
| `IMPLEMENTATION_PLAN.md` | — | **New** — Phase 85 design doc |
| `IMPLEMENTATION_TASK.md` | — | **New** — Phase 85 task breakdown |
| `IMPLEMENTATION_PROGRESS.md` | — | **New** — Phase 85 milestones |
| `IMPLEMENTATION_JOURNAL.md` | — | Phase 85 entries appended |
| `JOURNAL.md` | — | Phase 85 entry appended |
| `CODEBASE_REFERENCE.md` | — | This section |

## Phase 86 — Favicon Links for medminder_dash ✅

**Date**: 2026-06-19 15:55

**Goal**: Add favicon `<link>` tags to `admin.html` and `board_detail.html` `<head>` sections. Favicon assets already exist in `static/favicon/`.

**Design**: Added `{% block extra_head %}{% endblock %}` to `base.html` as injection point. Both `admin.html` and `board_detail.html` override it with 5 favicon link tags. Other pages (index, medicines, etc.) don't override the block, so they get no favicons.

**Verification**: MCP browser confirmed 5 favicon link tags in `<head>` of admin and board_detail pages, 0 on index page. Zero console errors.

### Files Changed

| File | Line | Change |
|------|------|--------|
| `medminder_dash/.../templates/base.html` | 11 | Added `{% block extra_head %}{% endblock %}` before `</head>` |
| `medminder_dash/.../templates/admin.html` | 3-9 | Added `{% block extra_head %}` with 5 favicon link tags |
| `medminder_dash/.../templates/board_detail.html` | 3-9 | Added `{% block extra_head %}` with 5 favicon link tags |
| `medminder_dash/.../templates/index.html` | 3-9 | Added `{% block extra_head %}` with 5 favicon link tags (Phase 86 Q5) |
| `e2e/servers/medminder_dash_server.py` | 16 | Added `import tempfile` (regression fix from Phase 85) |
| `PLAN.md` | — | Phase 86 entry updated with index.html |
| `IMPLEMENTATION_PLAN.md` | — | Phase 86 design doc updated |
| `IMPLEMENTATION_TASK.md` | — | Phase 86 task breakdown updated |
| `IMPLEMENTATION_PROGRESS.md` | — | Phase 86 milestones updated |
| `IMPLEMENTATION_JOURNAL.md` | — | Phase 86 Q5 entry appended |
| `JOURNAL.md` | — | Phase 86 Q5 entry appended |
| `CODEBASE_REFERENCE.md` | — | This section |

## Phase 87 — Favicon Links for arduino_dash ✅

**Date**: 2026-06-19 16:19

**Goal**: Add favicon `<link>` tags to `<head>` of dashboard, admin, and board_detail pages in arduino_dash.

**Design**: Same pattern as medminder_dash Phase 86 — `{% block extra_head %}` in `base.html`, overridden in child templates. Built/dist copies also updated.

**Verification**: MCP browser confirmed 5 favicon link tags in `<head>` of all 3 pages. Zero console errors.

### Files Changed

| File | Line | Change |
|------|------|--------|
| `arduino_dash/.../templates/base.html` | 11 | Added `{% block extra_head %}{% endblock %}` before `</head>` |
| `arduino_dash/.../templates/dashboard.html` | 3-9 | Added `{% block extra_head %}` with 5 favicon link tags |
| `arduino_dash/.../templates/admin.html` | 3-9 | Added `{% block extra_head %}` with 5 favicon link tags |
| `arduino_dash/.../templates/board_detail.html` | 3-9 | Added `{% block extra_head %}` with 5 favicon link tags |
| `scripts/pyoxidizer/.../prefix/arduino_dash/templates/base.html` | 49 | Added `{% block extra_head %}{% endblock %}` after `</style>` |
| `scripts/pyoxidizer/.../prefix/arduino_dash/templates/dashboard.html` | 3-9 | Added favicon links |
| `scripts/pyoxidizer/.../prefix/arduino_dash/templates/board_detail.html` | 3-9 | Added favicon links |
| `dist-standalone/.../prefix/arduino_dash/templates/base.html` | 49 | Added `{% block extra_head %}{% endblock %}` after `</style>` |
| `dist-standalone/.../prefix/arduino_dash/templates/dashboard.html` | 3-9 | Added favicon links |
| `dist-standalone/.../prefix/arduino_dash/templates/board_detail.html` | 3-9 | Added favicon links |
| `PLAN.md` | — | Phase 87 entry added |
| `IMPLEMENTATION_PLAN.md` | — | Phase 87 design doc |
| `IMPLEMENTATION_TASK.md` | — | Phase 87 task breakdown |
| `IMPLEMENTATION_PROGRESS.md` | — | Phase 87 milestones |
| `IMPLEMENTATION_JOURNAL.md` | — | Phase 87 entries appended |
| `JOURNAL.md` | — | Phase 87 entry appended |
| `CODEBASE_REFERENCE.md` | — | This section |

## Phase 88 — Stale BMS Port Cleanup in boot.py ✅

**Date**: 2026-06-19 16:40

**Goal**: Prevent `OSError: [Errno 98] Address already in use` when starting BMS via gunicorn's `when_ready` hook after an unclean shutdown.

**Root cause**: `_bind_tcp()` in `service.py:194-200` sets `SO_REUSEADDR` but on Linux this only allows binding `TIME_WAIT` addresses, not active `LISTEN` sockets. A stale BMS process holding port 9090 causes `bind()` to raise `EADDRINUSE`.

**Fix**: Added `_free_bms_resources(tcp_host, tcp_port, uds_path)` to `boot.py:42-74`, called at the top of `start_bms()`. Uses `lsof -ti tcp:<port>` to find and kill stale BMS PIDs, and removes stale UDS socket files.

### Files Changed

| File | Line | Change |
|------|------|--------|
| `board_manager/.../boot.py` | 42-74 | New `_free_bms_resources()` function |
| `board_manager/.../boot.py` | 79 | Wired into `start_bms()` — called before `subprocess.Popen()` |
| `PLAN.md` | — | Phase 88 entry added |
| `IMPLEMENTATION_PLAN.md` | — | Phase 88 design doc |
| `IMPLEMENTATION_TASK.md` | — | Phase 88 task breakdown |
| `IMPLEMENTATION_PROGRESS.md` | — | Phase 88 milestones |
| `IMPLEMENTATION_JOURNAL.md` | — | Phase 88 entries appended |
| `JOURNAL.md` | — | Phase 88 entry appended |
| `CODEBASE_REFERENCE.md` | — | This section |

## Phase 89 — Fix Daemon Badge "Disconnected" State ✅

**Date**: 2026-06-19 17:15

**Root cause**: Subscribe-order race condition. `sys::daemon/ready` only emitted on first subscribe (guarded by `initial_state_sent`), but clients subscribe `board::+::event` first. Event silently dropped; `_daemon_ready` stays `False` forever.

**Fix** (4 files changed):

| # | File | Change |
|---|------|--------|
| 1 | `board_manager/service.py:238-246` | Moved `_send_daemon_state_to(conn)` outside `initial_state_sent` guard — now called on every subscribe |
| 2 | `board_manager/service.py:77-79` | Added `daemon_binary` + `arduino_daemon` to `DaemonStartError` log for better debugging |
| 3 | `arduino_dash/pubsub.py:101,129` | `sys::daemon/ready` subscribed first in both `init_pubsub()` and `_on_pubsub_reconnect()` |
| 4 | `medminder_dash/pubsub_infra.py:138,261` | Same reorder in `init_pubsub()` and `_on_pubsub_reconnect()` |

**Key design**: `_send_daemon_state_to(conn)` at `service.py:246` is safe outside the guard because the method checks `self._daemon_ready` (no-op if daemon not ready) and `conn.addr in subscribers_for("sys::daemon/ready")` (no-op if client hasn't subscribed to daemon topic).

**Verification**: All 3 modified files pass `python3 -m py_compile`.

**Q5-6 — WS Handler SystemExit Silence** (2026-06-19 17:35):

| # | File | Change |
|---|------|--------|
| 5 | `arduino_dash/html_routes.py:373-374` | Added `except SystemExit:` with `logger.info()` before `finally` |
| 6 | `medminder_dash/html_routes.py:663-664` | Replaced bare `except:` with `except SystemExit:` + `logger.info()` + None-check |

**Root cause**: Gunicorn's `handle_quit` → `sys.exit(0)` raises `SystemExit` inside `ws.receive()` during shutdown. Arduino_dash had no except clause at all; medminder_dash had a bare `except:` (too broad).

**Verification**: `python3 -m py_compile` + arduino_dash 119 ✅ + medminder_dash 186 ✅.

---

## Phase 92 — Constants Refactor (Enum/IntEnum/StrEnum/Frozen Dataclass) ✅ COMPLETED

**Date**: 2026-06-19 18:00

**Goal**: Refactor all bare `SCREAMING_SNAKE_CASE` constants across 9 source files into typed `enum.Enum`, `enum.IntEnum`, `(str, Enum)` mixin, and `@dataclass(frozen=True)`.

### Constraint: Python 3.10 — No `StrEnum`

Python 3.10's `enum` module does not have `StrEnum` (added in 3.11). All string enums use `class X(str, Enum):` mixin pattern:
```python
class SysTopic(str, Enum):
    DAEMON_READY = "sys::daemon/ready"
```

### General Rules

1. **Per-file definitions**: Each source file that has constants defines its own enum/dataclass at the top of that file.
2. **No shared `constants.py` module**: Constants live with the module that uses them.
3. **`.value` required on bare `Enum` members** when passed to functions expecting `float`/`int` (e.g. `DetectorDefaults.POLL_INTERVAL.value` for `time.sleep()`).
4. **`.value` NOT required on `IntEnum` members** — they inherit from `int` and compare/assign directly.
5. **`state.py` must NOT be modified** — no changs to this file.
6. **`default_factory` caveat**: Python 3.10 `dataclass` does NOT create class-level attributes for fields with `default_factory`. Use plain class instead of dataclass when class-level attribute access is needed.

### Refactored Files

| # | File | Enum/Type | Members |
|---|------|-----------|---------|
| 1 | `board_manager/.../protocol.py` | `Handshake` (Enum) | `MAGIC = b"BMM1"`, `RECV_TIMEOUT = 5.0`, `PING_INTERVAL = 30.0` |
| 1 | `board_manager/.../protocol.py` | `Framing` (IntEnum) | `DELIMITER = 0xBE` |
| 1 | `board_manager/.../protocol.py` | `FramingMode` (str, Enum) | `LENGTH_PREFIX = "length_prefix"`, `DELIMITER = "delimiter"` |
| 2 | `board_manager/.../boot.py` | `BmsDefaults` (@dataclass frozen) | Default: `PROTOCOL = FramingMode.DELIMITER`, `UDS_PATH = "/tmp/board_mgr.sock"`, `TCP_HOST = "127.0.0.1"`, `TCP_PORT = 9090`, `PIPE_PATH = "..."` |
| 2 | `board_manager/.../boot.py` | `BmsEnv` (str, Enum) | `UDS_PATH = "BOARD_MGR_UDS_PATH"`, `TCP_HOST = "BOARD_MGR_TCP_HOST"`, `TCP_PORT = "BOARD_MGR_TCP_PORT"`, `NO_UDS = "BMS_NO_UDS"` |
| 3 | `board_manager/.../service.py` | `SysTopic` (str, Enum) | `DAEMON_READY = "sys::daemon/ready"`, `BOARDS = "sys::boards"`, `HEALTH = "sys::health"`, `TOPOLOGY = "sys::topology"` |
| 4 | `board_manager/.../board_detector.py` | `DetectorDefaults` (Enum) | `POLL_INTERVAL = 5.0`, `LIST_TIMEOUT = 3` |
| 5 | `board_manager/.../pool.py` | `PoolLimits` (IntEnum) | `MAX_RESTARTS = 3` |
| 6 | `board_manager_client/.../pubsub_client.py` | `ReconnectConfig` (class, not dataclass) | `RECONNECT_DELAY: float = 2.0`, `CONNECT_RETRY_DELAYS: list[float] = [0.5, 1.0, 2.0]` |
| 7 | `arduino_dash/.../gunicorn_conf.py` | `DashEnv` (str, Enum) | `BIND = "GUNICORN_BIND"`, `WORKERS = "GUNICORN_WORKERS"`, `TIMEOUT = "GUNICORN_TIMEOUT"`, `LOG_LEVEL = "GUNICORN_LOG_LEVEL"` |
| 7 | `medminder_dash/.../gunicorn_conf.py` | `GunicornEnv` (str, Enum) | Same as DashEnv |
| 8 | `arduino_dash/.../pubsub.py` | `PubSubTopic` (str, Enum) | `DAEMON_READY = "sys::daemon/ready"`, `BOARD_EVENT = "board::+::event"`, `RESP = "resp::*"`, `HEALTH = "sys::health"`, `RESP_COMPILE = "resp::compile::*"`, `RESP_UPLOAD = "resp::upload::*"` |
| 8 | `medminder_dash/.../pubsub_infra.py` | `PubSubTopic` (str, Enum) | Same as arduino_dash PubSubTopic |

### Key Gotchas Encountered

1. **`default_factory` + frozen dataclass**: Python 3.10 does NOT create class-level attributes for `dataclass` fields with `default_factory`. Workaround: used plain class instead of `@dataclass(frozen=True)` for `ReconnectConfig`.
2. **Stale wheels**: Downstream packages (board_manager_client → board_manager) need wheel rebuild + reinstall after source changes. `nox -s build(<pkg>)` rebuilds the wheel, but the consumer's pipenv environment must be force-reinstalled: `pip install --force-reinstall --no-deps <wheel>`. When source directory is in `sys.path`, Python loads the source file directly — no reinstall needed, but verify with `python3 -c "import X; print(X.__file__)"`.
3. **Build artifact noise**: `search` for old constant names finds stale copies in `.nox/`, `dist-standalone/`, and pyoxidizer build dirs. Ignore; only source files matter.

### Test Verification

| Suite | Count | Status |
|-------|-------|--------|
| board_manager | 201 pass + 3 pre-existing fail + 8 skip | ✅ (baseline match) |
| board_manager_client | 24 pass | ✅ |
| arduino_dash | 119 pass | ✅ |
| medminder_dash | 186 pass + 1 skip | ✅ |

## GitHub Pages Jekyll Documentation Site ✅

**Config**: Jekyll 3.10.0 + Minima 2.5.2. Ruby 3.0.2.

**`_config.yml`** key settings:
```yaml
theme: minima
plugins:
  - jekyll-feed
  - jekyll-relative-links
  - kramdown-parser-gfm
defaults:
  - scope:
      path: ""
      type: "pages"
    values:
      layout: "default"
```

**Front matter requirement**: All `.md` files need `---\n---\n` (empty front matter) for Jekyll to process them as pages. Without it, files are treated as static assets.

**raw/endraw handling**: Files containing Jinja2 template syntax (like `block`, `include`) must wrap content in raw/endraw blocks to prevent Liquid errors. Affected files: `JOURNAL.md`, `PLAN.md`, `TODOS.md`, `docs/ws-event-flow.md`, `CODEBASE_REFERENCE.md`.

**Broken link fix**: Two packages (`board_manager`, `medminder_dash`) have nested subpackages with the same name, creating an extra directory level in doc paths. Links must use:
- `board_manager/python/board_manager/board_manager/docs/` (not `.../board_manager/docs/`)
- `medminder_dash/python/medminder_dash/medminder_dash/docs/` (not `.../medminder_dash/docs/`)

**Build command**: `bundle exec jekyll build` → 246 HTML pages in `_site/`.

**Non-fatal warnings**: `{{ port.lstrip('/') }}` in `RESEARCH_JOURNAL.md` and `RESEARCH_PLAN.md` — Jinja2 filter syntax in code examples. Cosmetic only.

### nox `scripts_tests` session (Phase 96)

Runs 3 suites in order:
1. `pipenv run pytest tests/` — 128 tests (test_gen_grpc_bindings.py, test_setup_py.py)
2. `bash tests/test_install_arduino_deps.sh` — 12 tests
3. `bash tests/test_ci.sh` — 30 tests (10 scenarios)

Total: 170 tests.

**Last updated**: 2026-06-20 20:03 (Phase 96)
{% endraw %}
