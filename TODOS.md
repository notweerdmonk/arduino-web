---
---
{% raw %}
# TODOs

## Completed Phases

| Phase | Scope | Status | Tests |
|-------|-------|--------|-------|
| 93 | GitHub Pages Jekyll Documentation Site | ✅ DONE | 254 HTML pages, 0 errors, 0 warnings |
| 1-43 | All previous phases | ✅ DONE | varied |
| 44 | UI Alignment (board grid, detail, events) | ✅ DONE | 53+ |
| 45 | Sketch directory config + alarm.hpp wiring | ✅ DONE | 59 |
| 46 | Board detection, compile error, session fixes | ✅ DONE | 59 |
| 47 | Reader thread race condition | ✅ DONE | 59 |
| 48 | Thread safety + alarm bootstrap | ✅ DONE | 67 |
| 49 | Stale wheel deployment + namespace fix | ✅ DONE | 72 |
| 50 | alarm bootstrap + compilation status fixes | ✅ DONE | 75 |
| 51 | arduino_dash compile/WS pattern alignment | ✅ DONE | 78 |
| 52 | Phase 51 regression fixes | ✅ DONE | 75 |
| 53 | Remove redundant navbar board status | ✅ DONE | 70 |
| 54 | Align PubSub, WS, Entry Point, Fallback Scanner | ✅ DONE | 70 |
| 55 | WSGI + BMS Lifecycle | ✅ DONE | 78 |
| 56 | Arduino Deps Installer + gRPC Bindings Generator + setup.py | ✅ DONE | 598+10 |
| 57 | Standalone Binaries (PyOxidizer) + Wheel Install Smoke Tests | ✅ DONE | 598+10 |
| 58 | Cleanup, Documentation, Binary Optimization & Packaging | ✅ DONE | 598+10 |
| 59 | medminder_dash Board UI Improvements | ✅ DONE | 28 |
| 60 | Merge `/deploy` + `/admin/sketch-dir` into `/admin` | ✅ DONE | varied |
| 61 | Medicine Management Cards on /admin (with diff detection) | ✅ DONE | 113+ |
| 62 | Hot-Fix: MedMinderV2 Default + Global Board Selector | ✅ DONE | 123+ |
| 62.1-62.4 | /admin Page Fixes (3 User-Reported Issues) | ✅ DONE | 132+ |
| 62.5 | Per-Board Sketch Assignment + Wheel-Packaged Default | ✅ COMPLETE | 152+ |
| 62.6 | Post-Launch Bugfixes | ✅ COMPLETE | 152+ |
| 63 | setup.py Arguments + setup.cfg + Detailed READMEs | ✅ DONE | 548 per-pkg |
| 64 | Drag-and-Drop Overlay (Rounds 1-7) | ✅ DONE | 152+ |
| 65 | Fix Admin Board Selector Polling | ✅ DONE | 152+ |
| 66 | Refresh Button for Board Selector | ✅ DONE | 152+ |
| 67 | HTMX Spinner for Refresh Button | ✅ DONE | 152+ |
| 68 | Instant Board Selector Refresh + XDG Path Fixes | ✅ DONE | 151+1 |
| 69 | XDG Source-Relative Paths (arduino_dash) | ✅ DONE | varied |
| 70 | BoardListWatch gRPC Streaming | ✅ DONE | 1079+10 |
| 71 | Eliminate HTMX Polling via WS | ✅ DONE | varied |
| 72 | Collapsible Live Events Card + Bugfixes | ✅ DONE | varied |
| 72b | admin_active_board Dual-Format Bug | ✅ DONE | 151+1 |
| 72c | Port helper to arduino_dash + .value CSS | ✅ DONE | 5 suites |
| 72d | Board Info Resolution Refactoring | ✅ DONE | 151+1/102 |
| 72e | Board Detail UI Alignment (Arduino Dash) | ✅ DONE | 106 |
| 73 | Route Reorganization (HTML vs REST API) | ✅ DONE | 335+1 |
| 74 | Board Status Badge Fix | ✅ DONE | varied |
| 75 | Fix Stale `/api/board/` URLs + Badge Flash | ✅ DONE | varied |
| 76 | Unify Port Normalization | ✅ DONE | 4 new tests |
| 77 | Template Port Path Cleanup | ✅ DONE | 8/8 nox |
| 78 | daemon_ready Lock + Duplicate Guard | ✅ DONE | 8/8 nox |
| 79 | Light Colorscheme + External CSS | ✅ DONE | varied |
| 79b | init_pubsub Reconnection Fix | ✅ DONE | 8/8 nox |
| 80 | Hardware-ID Fallback Chain + Modal Fixes | ✅ DONE | 8/8 nox |
| 81 | Cleanup: Debug Logs + outerHTML + Docs Sync | ✅ DONE | 8/8 nox |
| 82 | Sorted Upload Registry via bisect.insort | ✅ DONE | 8/8 nox |
| 83 | Unified Sketch Registry (hardware_id + sketch_registry.json) | ✅ DONE | 8/8 nox |
| 84 | Playwright E2E Testing Infrastructure | ✅ DONE | varied |
| 85 | MCP E2E Server Binding + BMS Daemon Support | ✅ DONE | varied |
| 86 | Favicon Links for medminder_dash | ✅ DONE | 8/8 nox |
| 87 | Favicon Links for arduino_dash | ✅ DONE | 8/8 nox |
| 88 | Stale BMS Port Cleanup in boot.py | ✅ DONE | 8/8 nox |
| 89 | Fix Daemon Badge "Disconnected" State | ✅ DONE | 8/8 nox |
| 90 | Fix Double BoardDetector Stop Log | ✅ DONE | 8/8 nox |
| 91 | Align Live Events Card Style with arduino_dash | ✅ DONE | 8/8 nox |
| 92 | Constants Refactor (Enum/IntEnum/StrEnum) | ✅ DONE | 8/8 nox |
| 93 | GitHub Pages Jekyll Documentation Site | ✅ DONE | 8/8 nox |
| 94 | Fix Test NoX Session Post-Jekyll | ✅ DONE | 8/8 nox |
| 95 | Git Tree Preparation Plan | ✅ DONE | 8/8 nox |
| 96 | Wire test_ci.sh into Nox scripts_tests | ✅ DONE | 8/8 nox |
| 97 | Frontend Stack Optimization (Hyperscript→JS, Idiomorph) | ✅ DONE | 8/8 nox |
| 98 | WS Push Migration (Badge/Compile/Upload OOB) | ✅ DONE | 8/8 nox |
| 99 | HTML Template Homogenisation Across Both Dashboards | ✅ DONE | 119 + 186 pass |
| 100 | Server Script Process Lifecycle (Disown & Cleanup) | ✅ DONE | 8/8 nox |

## Phase 60 — COMPLETED ✅

**Q1** — Port `sketch_management.py` + extend `dash_state.py` ✅
**Q2** — Add 4 medicine sync endpoints + confirm token logic ✅
**Q3** — New `admin.html` + 5 partial templates ✅
**Q4** — Wire it all up (routes, nav, link, delete old templates, delete 6 obsolete tests) ✅
**Q5** — Run all 3 test suites (no regressions) ✅
**Q6** — Update `TESTING_*.md` + `CODEBASE_REFERENCE.md` ✅

**Results**:
- medminder_dash: 82 → 94 pass (+12 net: +18 new - 6 deleted)
- arduino_dash: 96 pass (no change)
- board_manager: 184 + 8 skip (no change)
- Per-package: 374 + 8 (was 362 + 8)
- Grand total: **972 + 8** (was 906 + 8, +66)

**Last Updated**: 2026-06-07 01:30

---

## Phase 61 — COMPLETED ✅

**Q1 — Backend** ✅
- T1.1: `_compute_diff()` helper ✅
- T1.2-T1.6: Modify 5 existing medicine CRUD routes (remove `_require_board()`, return partials) ✅
- T1.7-T1.10: Add 4 new routes ✅
- T1.11: Modify `/admin` to accept `?port=` query param ✅
- T1.12-T1.15: Add 4 new test classes (~13 tests) ✅
- T1.16: Run tests, 94 → 107 ✅

**Q2 — Frontend** ✅
- T2.1-T2.4: Create 4 new partials ✅
- T2.5-T2.6: Modify `admin.html` ✅
- T2.7: 6 frontend tests ✅
- T2.8: Run tests, 107 → 113 ✅

**Q3 — Run all 3 suites + docs** ✅
- T3.1: All 3 suites green ✅
- T3.2-T3.8: All docs updated ✅

**Results**:
- medminder_dash: 94 → 113 (+19 net)
- arduino_dash: 96 (no change)
- board_manager: 184 + 8 skip (no change)
- Per-package: 393 + 8 (was 374 + 8, +19)
- Grand total: **991 + 8** (was 972 + 8, +19)

**Last Updated**: 2026-06-07 03:15

---

## Phase 62 — COMPLETED ✅

**Q1 — `/api/sketches` MedMinderV2 default + 3 tests** ✅
- T1.1: Modify `api_sketches` in `sketch_management.py` ✅
- T1.2: Add `TestMedMinderV2DefaultSketch` (3 tests) ✅
- T1.3: Run tests, verify, sync docs ✅

**Q2 — Global board selector for compile/upload + 7 tests** ✅
- T2.1-T2.3: Backend FQBN resolve + OOB swap ✅
- T2.4-T2.7: Frontend (admin_board_selector + admin.html compile/upload cards + CSS) ✅
- T2.8: JS update (read from global elements) ✅
- T2.9: Add `TestGlobalBoardSelectorForCompileUpload` (7 tests) ✅
- T2.10: Run tests, verify, sync docs ✅

**Q3 — Run all 3 suites + final doc updates** ✅
- T3.1: All 3 test suites green ✅
- T3.2-T3.8: All docs updated ✅

**Results**:
- medminder_dash: 113 → 123 (+10 net: +3 Q1 + +7 Q2)
- arduino_dash: 96 (no change)
- board_manager: 184 + 8 skip (no change)
- Per-package: 403 + 8 (was 393 + 8, +10)
- Grand total: **1001 + 8** (was 991 + 8, +10)

**Last Updated**: 2026-06-07 06:15

---

## Phase 62.1-62.4 — /admin Page Fixes (3 User-Reported Issues) ✅ COMPLETED

**Trigger**: User testing after Phase 62 hot-fix; 3 issues with /admin page:
1. MedMinderV2 default not loaded (Q1/62.1)
2. Board port not visible after connecting (Q2/62.2)
3. Compile/upload doesn't update UI (Q3/62.3)

**Q1 (62.1) — MedMinderV2 default pre-populated in /admin + 3 tests** ✅
- T1.1: Added `include_default: bool = False` param to `_render_sketch_path_selector` ✅
- T1.2: Updated `/admin` route to pass `default_sketch_path=_DEFAULT_SKETCH_DIR` ✅
- T1.3: Added hidden `<input id="sketch_path" value="{{ default_sketch_path }}">` in admin.html ✅
- T1.4: Added 3 tests ✅
- T1.5: Ran medminder_dash tests, verified 123 → 126 ✅

**Q2 (62.2) — Board selector polls every 5s + 2 tests** ✅
- T2.1: Updated `admin.html:8-13` `hx-trigger="load"` → `"load, every 5s"` ✅
- T2.2: Added 2 tests ✅
- T2.3: Ran medminder_dash tests, verified 126 → 128 ✅

**Q3 (62.3) — htmx-native compile/upload + 4 tests** ✅
- T3.1: Renamed `id="compile-section"` → `id="compile-output-area"` in 2 compile partials; `id="upload-section"` → `id="upload-output-area"` in 2 upload partials (4 templates total) ✅
- T3.2: `nox -s 'build(arduino_sketch_tools)'` rebuilt wheel; re-locked 2 Pipfile.locks (medminder_dash, arduino_dash) ✅
- T3.3: Converted Compile/Upload buttons to hx-post in admin.html:183-186,203-206 ✅
- T3.4: Removed `compileSketch`/`uploadSketch` JS (28 lines) ✅
- T3.5: Verified arduino_dash `board_detail.html` still works (96/96 tests pass) ✅
- T3.6: Added 4 tests ✅
- T3.7: Ran medminder_dash + arduino_dash tests, verified medminder_dash 128 → 132, arduino_dash 96 unchanged ✅

**Q4 (62.4) — Run all 3 suites + final doc updates** ✅
- T4.1: Ran all 3 test suites, verified 132/96/184+8 ✅
- T4.2-T4.8: Updated all docs (TESTING_*, CODEBASE_REFERENCE, PLAN, JOURNAL, IMPLEMENTATION_PROGRESS, IMPLEMENTATION_JOURNAL, IMPLEMENTATION_PLAN, IMPLEMENTATION_TASK, TODOS) ✅

**Results**:
- medminder_dash: 123 → 132 (+9: +3 Q1 + +2 Q2 + +4 Q3)
- arduino_dash: 96 (no change, Q3 verified)
- board_manager: 184 + 8 skip (no change)
- Per-package: 412 + 8 (was 403 + 8, +9)
- Grand total: 1010 + 8 (was 1001 + 8, +9)

**Last Updated**: 2026-06-07 07:30

---

## Phase 62.5 — Per-Board Sketch Assignment + Wheel-Packaged Default ✅ COMPLETED

**Trigger**: User testing of Phase 62.1-62.4 revealed 3 deeper issues; redesign required.

**Q1 (62.5.1) — Surface `hardware_id` in board info flow + 6 tests** ✅ COMPLETED
- T1.1: Update `pubsub.py:_resolve_board_info` (line 76-93) — return `hardware_id` ✅
- T1.2: Update `board_detector.py:_run_once` (line 112-135) + `_emit` (line 157-167) — include `hardware_id` ✅
- T1.3: Update `pubsub.py:_fallback_scan_loop` (line 34-70) — pass `hardware_id` ✅
- T1.4: Verify `_known_ports` stores `hardware_id` ✅
- T1.5: Add 4 tests in `medminder_dash/tests/test_pubsub.py` ✅
- T1.6: Add 2 tests in `board_manager/tests/test_board_detector.py` ✅
- T1.7: Run tests, medminder_dash 132 → **136**, board_manager 184 → **186** ✅

**Q2 (62.5.2) — Per-board sketch registry + 10 tests** ✅
- T2.1: NEW `medminder_dash/sketch_registry.py` (~120 lines) ✅
- T2.2: Update `sketch_management.py:_render_sketch_path_selector` (add `hardware_id` param) ✅
- T2.3: Update `sketch_management.py:api_sketch_upload` (read `?hardware_id=...` query) ✅
- T2.4: Update `sketch_management.py:api_sketch_delete` (clear assignment) ✅
- T2.5: NEW `medminder_dash/tests/test_sketch_registry.py` (10 tests) ✅
- T2.6: Run tests, expect 136 → 146 ✅

**Q3 (62.5.3) — board_detail uses per-board sketch + 3 tests** ✅
- T3.1: `board_detail` route resolves per-board sketch via `get_assignment(hardware_id)` ✅
- T3.2: `load_sketch_dir()` fallback when no per-board assignment ✅
- T3.3: `hardware_id` empty → global default ✅
- T3.4: 3 tests in `test_routes.py::TestBoardDetailFqbn` ✅
- T3.5: `nox -s 'tests(medminder_dash)'` passes: 143 → 146 ✅

**Q4 (62.5.4) — Admin UX: "Assigned to selected board" + 4 tests** ✅ COMPLETED
- T4.1: `api_last_upload` passes `include_default=True` ✅
- T4.2: Admin route resolves per-board sketch via `get_assignment(hardware_id)` ✅
- T4.3: admin.html shows "Assigned to selected board" badge ✅
- T4.4: Upload modal JS includes `?hardware_id=` in fetch ✅
- T4.5: 4 new tests + 2 existing updated ✅
- T4.6: `nox -s 'tests(medminder_dash)'` passes: 146→150 ✅

**Q5 (62.5.5) — Wheel packaging for MedMinderV2 default sketch + 2 tests** ✅ COMPLETED
- T5.1: Moved MedMinderV2 sketch into package dir ✅
- T5.2: Added `"sketches/MedMinderV2/**/*"` to pyproject.toml package-data ✅
- T5.3: Created `_resolve_default_sketch_dir()` in settings.py ✅
- T5.4: Updated `_DEFAULT_SKETCH_DIR` to use packaged fallback ✅
- T5.5: Added `reset_default_sketch_dir()` for testing ✅
- T5.6: 2 tests in test_sketch_registry.py ✅
- T5.7: medminder_dash tests pass: 150→152 ✅

**Q6 (62.5.6) — Final sync + verify** ✅ COMPLETED
- T6.1: Run all 3 test suites, confirmed 152/96/186+8 = 434+8 pass — all 3 suites green ✅
- T6.2-T6.8: Update all docs (TESTING_*, CODEBASE_REFERENCE, PLAN, JOURNAL, IMPLEMENTATION_*, TODOS) ✅

## Phase 62.6 — Post-Launch Bugfixes ✅ COMPLETED

**Q1 (62.6.1)** — Fix post-upload refresh target (Bug A) ✅
- [x] T1.1: admin.html `hx-swap="outerHTML"` → `innerHTML`
- [x] T1.2: modal JS refresh target → `innerHTML`
- [x] T1.3: Verify 152 tests pass + manual upload

**Q2 (62.6.2)** — Fix XDG extraction Traversable bug (Bug B) ✅
- [x] T2.1: Replace `shutil.copy2` with `read_bytes/write_bytes`
- [x] T2.2: Remove `import shutil`
- [x] T2.3: Verify 152 pass

**Q3 (62.6.3)** — Fix duplicate id="sketch_path" (Bug C) ✅
- [x] T3.1: Remove hidden `<input id="sketch_path">` from admin.html
- [x] T3.2: Update tests — confirm no inline sketch_path in admin page
- [x] T3.3: Verify 152 pass

**Q4 (62.6.4)** — Fix stale #fqbn on board change (Bug D) ✅
- [x] T4.1: Add `#fqbn` OOB swap in `api_medicines_active_board`
- [x] T4.2: Update tests for `#fqbn` OOB
- [x] T4.3: Verify 152 pass

**Q5 (62.6.5)** — Fix stale compile/upload URLs (Bug E) ✅
- [x] T5.1: Extract compile/upload to `partials/compile_upload_card.html`
- [x] T5.2: Create `GET /api/board/compile-upload-card` route
- [x] T5.3: Wire admin.html with hx-get container + `board-changed` event
- [x] T5.4: Add event trigger to board selector
- [x] T5.5: Update 7 tests for new endpoint
- [x] T5.6: Verify 152 pass

---

## Phase 64 — COMPLETED ✅ (Rounds 1-7)

**Trigger**: User request to replace small dashed `#drop-zone` with viewport-wide overlay.

**Q1 — Add overlay div + `def processDndDrop` to base.html** ✅
...

**Q6 / Round 6 — Eliminate 100ms `dragleave` timer (counter pattern + `window.blur`)** ✅
- Replaced `hideTimer` with `dragCounter` (increment/decrement pattern) ✅
- Removed `clearTimeout` from `showOverlay()`/`hideOverlay()` ✅
- Added `dragover` re-show guard for hidden-but-active-drag case ✅
- Reset `drop` + `visibilitychange` counter to 0 ✅
- Added `window.blur` for immediate alt-tab cleanup ✅
- `mouseenter`/`mousemove` stale-cleanup unchanged ✅
- Research: counter pattern is universal (Google Chrome Labs, Angular CDK, Tailwind) ✅
- All 3 test suites green ✅
- CODEBASE_REFERENCE.md updated with Round 6 ✅

**Q7 / Round 7 — Extract DnD overlay into partial, admin-page only** ✅
- Created `partials/dnd_overlay.html` — self-contained partial with CSS + div + JS ✅
- Removed all DnD code from `base.html` (no DnD on index or board_detail) ✅
- Added `{% include "partials/dnd_overlay.html" %}` to `admin.html` only ✅
- No functional change for admin page — Round 6 behavior preserved ✅
- All 3 test suites green ✅
- CODEBASE_REFERENCE.md updated with Round 7 ✅

**Results**:
- medminder_dash: 152 (no change)
- arduino_dash: 96 (no change)
- board_manager: 186 + 8 skip (no change)
- Grand total: 1032 + 8 (no change)
- **All timers eliminated from DnD code** ✅
- **DnD overlay only on admin page** ✅

## Phase 65 — Fix Admin Board Selector Polling ✅ COMPLETED

**Q1** — Fix swap attribute (`outerHTML` → `innerHTML`) ✅
**Q2** — Run all 3 test suites ✅
**Q3** — Update CODEBASE_REFERENCE + journals ✅

**Results**:
- medminder_dash: 152 (no change)
- arduino_dash: 96 (no change)
- board_manager: 186 + 8 skip (no change)
- Grand total: 1032 + 8

**Last Updated**: 2026-06-09

---

## Phase 66 — Refresh Button for medminder_dash + Fix arduino_dash Refresh Swap ✅ COMPLETED

**Q1** — Add refresh button to medminder_dash `partials/admin_board_selector.html` ✅
**Q2** — Fix arduino_dash `partials/admin_board_selector.html` `hx-swap="outerHTML"` → `"innerHTML"` ✅
**Q3** — Run board_manager tests + final doc sync ✅

**Results**:
- medminder_dash: 152 (no change)
- arduino_dash: 102 (no change)
- board_manager: 186 + 8 skip (no change)
- Grand total: 1032 + 8

## Phase 67 — COMPLETED ✅

**Goal**: Add `hx-indicator`-driven spinner to Refresh button on admin board selector (both dashboards).

**Q1** — arduino_dash: `admin_board_selector.html` + `base.html` CSS ✅
**Q2** — medminder_dash: `admin_board_selector.html` + `base.html` CSS ✅
**Q3** — All 3 suites + nox build arduino_dash ✅

**Files modified**:
- `arduino_dash/templates/partials/admin_board_selector.html` — added `refresh-btn` class + spinner span
- `arduino_dash/templates/base.html` — added 4 `.refresh-btn` CSS rules
- `medminder_dash/templates/partials/admin_board_selector.html` — same changes
- `medminder_dash/templates/base.html` — same CSS rules

**Results**:
- medminder_dash: 152 (no change)
- arduino_dash: 102 (no change)
- board_manager: 186 + 8 skip (no change)
- Grand total: 1032 + 8

**Last Updated**: 2026-06-09

---

## Phase 69 — Remove Hardcoded Source-Relative Paths from arduino_dash ✅ COMPLETED

**Date**: 2026-06-10

**Goal**: Replace `Path(__file__).resolve().parents[N]` and `os.path.dirname(os.path.abspath(__file__))` hacks in arduino_dash with XDG config/data dirs, matching the Phase 68 medminder_dash pattern.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Create `settings.py` with XDG paths | ✅ |
| 2 | Update `sketch_registry.py` imports | ✅ |
| 3 | Update `state.py` UPLOAD_BASE_DIR import | ✅ |
| 4 | Verify test patches (no changes needed) | ✅ |
| 5 | Run all 3 test suites | ✅ |
| 6 | Update docs + CODEBASE_REFERENCE | ✅ |

**Files modified**: 3 (1 new `settings.py`, 2 modified)
**Test delta**: 0 (all 20 existing test patches remain valid)
**Results**:
- arduino_dash: 102 (no change)
- medminder_dash: 151 + 1 skip (no change)
- arduino_sketch_tools: 47 (no change)

**Last Updated**: 2026-06-10

---

## Phase 70 — BoardListWatch gRPC streaming + eliminate BoardDetector polling ✅ COMPLETED

**Date**: 2026-06-11

**Goal**: Replace BoardDetector's 5-second polling with gRPC `BoardListWatch` streaming, reducing backend board detection latency from ~5s to near-instant.

**Files modified**: 6 (2 new, 4 modified)
**Test delta**: +8 (board_manager), +1 (medminder_dash), +0 (arduino_dash)

**Results**:
- board_manager: 186 → 193 + 8 skip
- medminder_dash: 151 → 151 + 1 skip
- arduino_dash: 102
- arduino_grpc: 33 + 2 skip
- Grand total: 1079 + 10

---

## Phase 71 — Eliminate 5s HTMX Polling + Board List PubSub via WS ✅ COMPLETED

**Date**: 2026-06-11

**Goal**: Replace HTMX `every 5s` polling on board grid and admin board selector with WS-native events via `htmx:wsBeforeMessage`. Also fix 3 cascading bugs (71a, 71b, 71c) in the WS event processing chain.

**Files modified**: Multiple across both dashboards
**Test delta**: +0 (no new tests needed for JS-level changes; 3 medminder_dash tests updated)

**Results**:
- arduino_dash: 102
- medminder_dash: 151 + 1 skip
- board_manager: 204 + 8 skip
- arduino_sketch_tools: 47
- board_manager_client: 24

---

## Phase 72 — Collapsible Live Events Card + Bugfixes (v1-v4) ✅ COMPLETED

**Date**: 2026-06-14

**Goal**: Add collapsible `<details>/<summary>` Live Events card to admin dashboards showing board connect/disconnect events in real-time via existing WS broadcast. Fix 4 cascading root causes for double events.

**Results**:
- board_manager: 204 + 8 skip
- arduino_dash: 102
- medminder_dash: 151 + 1 skip
- arduino_grpc: 33 + 2 skip

---

## Phase 72b — admin_active_board Dual-Format Bug ✅ COMPLETED

**Date**: 2026-06-14

**Goal**: Fix `session["admin_active_board"]` written in two different formats (3-tuple vs string) across 2 routes, causing raw-tuple display in compile-upload-card.

**Fix**: Add `_get_active_board_info()` helper that normalizes read format.

**Results**: medminder_dash 151/151 + 1 skip ✅

---

## Phase 72c — Port `_get_active_board_info` to arduino_dash + admin route session write + .value CSS ✅ COMPLETED

**Date**: 2026-06-14

**3 quantums**:
- Q1: Port `_get_active_board_info()` helper to arduino_dash board_management.py
- Q2: Fix medminder_dash admin route else-branch missing session write
- Q3: Add `.value` CSS styling for compile-upload-card read-only fields

**Results**: All 5 suites green ✅

---

## Phase 72d — Board Info Resolution Refactoring ✅ COMPLETED

**Date**: 2026-06-16

**Goal**: Extract repeated board-info resolution logic (3 routes × 2 dashboards) into `_resolve_board_info()` helper. Fix async compile-upload-card missing first-port fallback. Fix 4 latent `find_board_info_by_fqbn` single-arg bugs.

**3 quantums**:
- Q1: medminder_dash helpers + board_selector refactor
- Q2: medminder_dash compile_upload_card + admin cleanup
- Q3: arduino_dash helper + all 3 routes + 4 bugfixes

**Results**: medminder_dash 151/151 + 1 skip ✅, arduino_dash 102/102 ✅

---

## Phase 72e — Board Detail UI Alignment (Arduino Dash) ✅ COMPLETED

**Date**: 2026-06-16

**Goal**: Align arduino_dash board detail page with medminder_dash: FQBN as read-only label, board name heading, side-by-side FQBN + Port display.

**3 quantums**:
- Q1: Backend — `board_detail()` route resolves board_info via `get_port_info()`, passes board_name + board_info
- Q2: Frontend — heading shows board name, FQBN `<span class="value">` + hidden `<input>`, Device Port `<span class="value">`
- Q3: Tests — 4 new board_detail tests

**Results**: arduino_dash 106/106 ✅

**Last Updated**: 2026-06-18

---

## Phase 73 — Route Reorganization: HTML vs REST API Separation ✅ COMPLETED

**Date**: 2026-06-17 04:51 → 2026-06-17 07:19

**Goal**: Separate all routes into HTML routes (`html_routes.py`, no `/api/` prefix) and REST API routes (`api_routes.py`, `/api/` prefix, JSON-only) across both dashboards and the shared `arduino_sketch_tools` blueprint, adding REST counterparts for medicine CRUD and endpoint tests for all routes.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Shared blueprint prefix change: `/api/board/`→`/board/` | ✅ |
| 2 | arduino_dash route split (html_routes.py + api_routes.py) | ✅ |
| 3 | arduino_dash templates + tests updated | ✅ |
| 4 | medminder_dash route split + REST CRUD endpoints | ✅ |
| 5 | medminder_dash templates + tests updated | ✅ |
| 6 | Endpoint tests for all HTML + REST routes | ✅ |
| 7 | Final verification across all suites + docs sync | ✅ |

**Verification**: arduino_dash 113 ✅, medminder_dash 175+1 ✅, arduino_sketch_tools 47 ✅, Grand total 335+1 ✅

---

## Phase 74 — Fix Board Status Badge Showing "Disconnected" ✅ COMPLETED

**Date**: 2026-06-17 10:28

**Goal**: Fix board status badge on board detail pages always showing "○ Disconnected" even when board is connected.

**Root Cause**: `_norm_port()` only adds leading `/` when missing but doesn't strip extra slashes → `/board//dev/ttyACM0/` (double slash) → Flask extracts `port = "//dev/ttyACM0"` → lookup in `_board_list` fails.

**Fix**: `_norm_port()` now strips extra slashes via `"/" + port.lstrip("/")`.

---

## Phase 75 — Fix MedMinder Dash Stale `/api/board/` URLs + Badge Flash ✅ COMPLETED

**Date**: 2026-06-17 11:11 → 2026-06-17 11:30

**Goal**: Fix medminder_dash templates and route logic still using stale `/api/board/` prefix after Phase 73 route reorganization.

**3 Bugs Fixed (Q1-Q7)**:
| # | Severity | Issue |
|---|----------|-------|
| 1 | Critical | `board_detail.html` `hx-get="/api/board/.../connection-status"` → 404 every 10s |
| 2 | High | `connected = info is not None` but `get_port_info()` returns `{}` → `{} is not None` is `True` |
| 3 | High | Compile/upload buttons POST to `/api/board/...` → 404 on submit |

**Q8 — Badge Flash Fix**: Replace fallback badge `<span>` (visible until HTMX load) with empty span (matches arduino_dash pattern).

---

## Phase 76 — Unify Port Normalization with `normalize_port()` + `is_valid_port` Validation ✅ COMPLETED

**Date**: 2026-06-17 11:45 → 2026-06-17 12:00

**Goal**: Integrate `is_valid_port()` into port normalization, replacing ad-hoc `_norm_port` implementations (3 existed across codebase) with unified `normalize_port()` that normalizes AND validates. Returns `None` for invalid ports so callers can return 400 early.

**Files Changed**: Both `utils.py`, both `html_routes.py`, both `api_routes.py`, `arduino_dash/pubsub.py`, `arduino_dash/app.py`, `arduino_dash/tests/test_app.py` (4 new tests)

---

## Phase 77 — Template Port Path Cleanup ✅ COMPLETED

**Date**: 2026-06-17 17:03

**Goal**: Remove scattered `{{ port.lstrip('/') }}` pattern from 7 template locations by computing `port_path` once in Python route context.

| Q | Scope | Status |
|---|-------|--------|
| 1 | arduino_dash — 3 routes + 3 templates | ✅ |
| 2 | medminder_dash — 3 routes + 3 templates | ✅ |
| 3 | Tests + nox — `nox -s all_tests` green | ✅ |
| 4 | Docs sync | ✅ |

**Verification**: arduino_dash 119 ✅, medminder_dash 181+1 ✅, arduino_sketch_tools 51 ✅, nox 8/8 ✅

---

## Phase 78 — Fix `_daemon_ready` Unprotected Access + Duplicate Log Spam ✅ COMPLETED

**Date**: 2026-06-17 17:15

**Goal**: Add `_daemon_ready_lock` to arduino_dash, protect all reads/writes to `_daemon_ready` across both dashboards, add duplicate-event guard.

**Details**: 4 access sites lock-protected in arduino_dash, 1 in medminder_dash, duplicate-event guard in both `_on_daemon_ready` handlers.

| Q | Scope | Status |
|---|-------|--------|
| 1 | arduino_dash — Add lock, protect 4 access sites, add guard | ✅ |
| 2 | medminder_dash — Fix `_fallback_scan_loop` read, add guard | ✅ |
| 3 | Tests — `nox -s all_tests` green | ✅ |
| 4 | Docs sync | ✅ |

---

## Phase 79 — Light Colorscheme + External CSS ✅ COMPLETED

**Date**: 2026-06-17 17:30 → 2026-06-18

**Goal**: Add light color scheme via `@media (prefers-color-scheme: light)`, refactor all CSS from inline `<style>` blocks and `style=""` attributes into per-dashboard `static/style.css` using CSS custom properties.

**Design**: 42 CSS variables, 57 new semantic classes, flat cards, symmetric dark-to-light progression.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Create style.css + link (~540 lines per dashboard) | ✅ |
| 2 | Move `<style>` blocks from admin.html + dnd_overlay.html | ✅ |
| 3-5 | Inline → classes (35 templates across 3 packages) | ✅ |
| 6 | Tests + docs sync | ✅ |

---

## Phase 79b — arduino_dash `init_pubsub` Reconnection Fix ✅ COMPLETED

**Date**: 2026-06-18 13:02

**Goal**: Fix arduino_dash `init_pubsub` to handle transient BMS unavailability — match medminder_dash's pattern of catching `connect()` failure internally so `start_reader()` always runs.

**Root cause**: `pubsub.py:97` — `connect()` not wrapped in try/except; on failure `start_reader()` never called.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Fix + test: try/except in pubsub.py + test assertions | ✅ |
| 2 | Docs sync | ✅ |

**Test results**: arduino_dash 119 ✅, medminder_dash 181+1 ✅ (1 Phase 79 regression fix), nox 8/8 sessions ✅

---

## Phase 80 — Hardware-ID Fallback Chain + Modal Fixes ✅ COMPLETED

**Date**: 2026-06-18

**Goal**: Homogenize sketch-selection fallback chain: `hardware_id → _resolve_latest_upload() → default/empty`. Fix arduino_dash modal `r.json()` bug and missing `hardware_id`.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Helper extraction + refactor (both `sketch_management.py`) | ✅ |
| 2 | medminder_dash routes (hardware_id + board_detail fallback) | ✅ |
| 3 | Template changes (hidden inputs, hx-include, dead code) | ✅ |
| 4 | Modal fixes (r.json→r.text, hardware_id, refresh callbacks) | ✅ |
| 5 | Full test run + docs sync | ✅ |

**Test results**: arduino_dash 119 ✅, medminder_dash 181+1 ✅, nox 8/8 ✅

---

## Phase 81 — Cleanup: Debug Logs + outerHTML Fix + Docs Sync ✅ COMPLETED

**Date**: 2026-06-18 17:58

**Goal**: Remove 4 noisy `logger.debug` calls from arduino_dash `html_routes.py` (3 with incorrect `exc_info=True`), fix `swap: 'outerHTML'` → `'innerHTML'` in arduino_dash modal, sync all stale docs.

| Q | Scope | Status |
|---|-------|--------|
| 1 | Remove debug logs (html_routes.py:107,135,182,207) | ✅ |
| 2 | Fix swap outerHTML→innerHTML (sketch_upload_modal.html:49) | ✅ |
| 3 | Update stale docs (TODOS, REVIEW, PLAN, JOURNAL, CODEBASE_REFERENCE) | ✅ |
| 4 | `nox -s all_tests` green | ✅ |

**Test results**: arduino_dash 119 ✅, medminder_dash 181+1 ✅, nox 8/8 ✅

---

## Phase 82 — Sorted Upload Registry via bisect.insort ✅ COMPLETED

**Date**: 2026-06-18

**Goal**: Use `bisect.insort()` to maintain each per-sketch `list[dict]` in `_upload_registry` sorted by timestamp on insert, eliminating redundant `.sort()` calls at read time.

| Q | Scope | Status |
|---|-------|--------|
| 1 | bisect.insort in warmup + simplify _resolve_latest_upload (2 × sketch_management.py) | ✅ |
| 2 | bisect.insort in 4 upload routes (2 × html_routes.py, 2 × api_routes.py) | ✅ |
| 3 | Cross-sketch `.sort()` retained for selector + api_sketches (Timsort O(n) on near-sorted) | ✅ |
| 4 | Delete routes simplified — manual `elif latest` tracking → post-loop `max()` | ✅ |
| 5 | `nox -s all_tests` 8/8 green + full docs sync | ✅ |

**Files changed**: 6 source files across arduino_dash & medminder_dash. No new dependencies.
**Test results**: arduino_dash 119 ✅, medminder_dash 181+1 ✅, nox 8/8 ✅

---

### Phase 85 — MCP E2E Server Binding + BMS Daemon Support ✅

**Date**: 2026-06-19

**Goal**: Fix server binding for MCP browser container, add `--bms` flag for BMS daemon.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | Change host to 0.0.0.0 in both server scripts | ✅ |
| 2 | Add --bms flag to arduino_dash_server.py | ✅ |
| 3 | Add --bms flag to medminder_dash_server.py | ✅ |
| 4 | Document in GUIDE.md (container note, BMS lifecycle, Recipe 5b) | ✅ |
| 5 | Verify — MCP browser shows "● Daemon Ready" with --bms | ✅ |

### Phase 88 — Stale BMS Port Cleanup in boot.py ✅

**Date**: 2026-06-19 16:40

**Goal**: Fix `OSError: [Errno 98] Address already in use` when starting BMS after unclean shutdown.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | Add `_free_bms_resources()` to boot.py — kills stale BMS on TCP port, cleans stale UDS socket | ✅ |
| 2 | Wire into `start_bms()` — called before subprocess.Popen() | ✅ |
| 3 | Verify — stale BMS killed, port freed, new BMS starts cleanly | ✅ |

---

### Phase 87 — Favicon Links for arduino_dash ✅

**Date**: 2026-06-19 16:19

**Goal**: Add favicon `<link>` tags to `dashboard.html`, `admin.html`, and `board_detail.html` in arduino_dash.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | Add `{% block extra_head %}{% endblock %}` to base.html | ✅ |
| 2 | Add favicon links to dashboard.html | ✅ |
| 3 | Add favicon links to admin.html | ✅ |
| 4 | Add favicon links to board_detail.html | ✅ |
| 5 | Update built copies (pyoxidizer: base/dashboard/board_detail) | ✅ |
| 6 | Update dist-standalone copies | ✅ |
| 7 | Verify — MCP browser confirms 5 links in <head> on all 3 pages | ✅ |

---

### Phase 86 — Favicon Links for medminder_dash ✅

**Date**: 2026-06-19 15:55

**Goal**: Add favicon `<link>` tags to `admin.html`, `board_detail.html`, and `index.html`.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | Add `{% block extra_head %}{% endblock %}` to base.html | ✅ |
| 2 | Add favicon links to admin.html | ✅ |
| 3 | Add favicon links to board_detail.html | ✅ |
| 4 | Add favicon links to index.html | ✅ |
| 5 | Verify — MCP browser confirms 5 links in <head> on all 3 pages | ✅ |

---

### Phase 91 — Align Live Events Card Style with arduino_dash ✅

**Date**: 2026-06-19 17:59

**Goal**: Align medminder_dash's `board_event.html` template with arduino_dash's
flat reference layout.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | `board_event.html` — remove `[-10:]|reverse`, `board-event-row`, nested div, conditional badge | ✅ |
| 2 | Verify — 186/186 + 1 skip medminder_dash, 0 regressions | ✅ |
| 3 | Docs — journals, CODEBASE_REFERENCE, TODOS | ✅ |

**Files changed**: `medminder_dash/.../templates/partials/board_event.html`

---

### Phase 90 — Fix Double BoardDetector Stop Log ✅

**Date**: 2026-06-19 17:49

**Goal**: Eliminate duplicate "BoardDetector stopped" log during SIGINT shutdown.

**Root cause**: `service.start()` catches `KeyboardInterrupt` and calls `stop()`,
then `__main__.main()`'s `finally` block calls `stop()` again.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | `board_detector.py` — idempotent `stop()` (early-return guard) | ✅ |
| 2 | `service.py` — remove `KeyboardInterrupt` catch from `start()` | ✅ |
| 3 | Tests — 34 relevant pass, 0 regressions | ✅ |
| 4 | Docs — journals, CODEBASE_REFERENCE, TODOS | ✅ |

**Files changed**: `board_detector.py:64-66`, `service.py:97-102`

---

### Phase 89 — Fix Daemon Badge "Disconnected" State ✅

**Date**: 2026-06-19 17:15

**Goal**: Fix daemon badge always showing "○ Disconnected" in both dashboards despite `arduino-cli daemon` running.

**Root cause**: Subscribe-order race condition — `sys::daemon/ready` only emitted on the first subscribe (server-side guard), but clients subscribe board events first.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | `service.py` — Move `_send_daemon_state_to` outside `initial_state_sent` guard | ✅ |
| 2 | `service.py` — Improve daemon failure log (binary + addr context) | ✅ |
| 3 | `arduino_dash/pubsub.py` — Reorder subscribes (`sys::daemon/ready` first) | ✅ |
| 4 | `medminder_dash/pubsub.py` — Same reorder | ✅ |
| 5 | Syntax verification — `python3 -m py_compile` passes on all 3 files | ✅ |

**Q5-6 — WS Handler SystemExit Silence** (2026-06-19 17:35):

| Q | Scope | Status |
|---|-------|--------|
| 5 | `arduino_dash/html_routes.py` — Add `except SystemExit:` with log | ✅ |
| 6 | `medminder_dash/html_routes.py` — Replace bare `except:` with `except SystemExit:` + log + None check | ✅ |
| — | Syntax + test verification (`py_compile` + 119 + 186) | ✅ |

### Phase 93 — GitHub Pages Jekyll Documentation Site ✅

**Date**: 2026-06-20 14:24

**Goal**: Serve project documentation as a GitHub Pages site using Jekyll (Minima theme). Fix config/build issues, broken links, Liquid warnings, and missing README links.

**Changes**:
| Q | Scope | Status |
|---|-------|--------|
| 1 | Fix `_config.yml` — merge plugins, add theme, add defaults | ✅ |
| 2 | Remove `jekyll-archives` from Gemfile | ✅ |
| 3 | Add front matter to 93 doc `.md` files | ✅ |
| 4 | raw/endraw wrapping for 5 workflow docs with Jinja2 | ✅ |
| 5 | Fix broken relative links (24 board_manager + 27 medminder_dash) | ✅ |
| 6 | Rebuild — 246 HTML pages, 0 errors | ✅ |
| 7 | Wrap RESEARCH docs — fix 4 Liquid warnings | ✅ |
| 8 | Add front matter to 8 missing README files | ✅ |
| 9 | Add missing README links to index.md (7 packages) | ✅ |
| 10 | Final build — 0 errors, 0 warnings, 254 HTML pages | ✅ |
| 11 | Docs sync — all project + workflow documents | ✅ |

**Files modified**: `_config.yml`, `Gemfile`, `index.md`, 4 `docs/*.md`, 7 workflow/research docs, 101 `.md` files with front matter

**Build**: 0 errors, 0 warnings, 254 HTML pages, ~46-54s build time.

{% endraw %}