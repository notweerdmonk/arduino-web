---
---
{% raw %}
# Testing Journal — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

## Entry 1 — Overview

**Method**: Per-quantum `bundle exec jekyll build` verification, plus `grep`/`ls` inspection of `_site/` output for href targets, file existence, and page counts.

**Risk**: Low. Changes are to config files, markdown front matter, and static HTML template syntax (raw/endraw). No Python code modified.

## Entry 2 — Build Statistics

| Quantum | Pages | Errors | Warnings | Notes |
|---------|-------|--------|----------|-------|
| Q1-Q2 | 0 (build failed) | Liquid syntax errors | 0 | Before fixes |
| Q3-Q4 | 246 | 0 | 4 (Liquid `{{ }}`) | Front matter + raw/endraw applied |
| Q5-Q6 | 246 | 0 | 4 | Broken links fixed in source |
| Q7 | 246 | 0 | 0 | RESEARCH docs raw-wrapped |
| Q8 | 254 | 0 | 0 | README front matter added (+8 pages) |
| Q9-Q10 | 254 | 0 | 0 | README links added to index.md |

## Entry 3 — Key Findings

1. **Link verification critical**: `jekyll-relative-links` silently converts `.md` links to `.html`. Must grep rendered `_site/` output, not source files, to verify href targets.
2. **README hrefs**: If a `README.md` lacks front matter, Jekyll copies it as a static file (`.md` extension). The `jekyll-relative-links` plugin only converts links to `.html` for pages that Jekyll processes (those with front matter). Without front matter, links in `index.md` resolve to `README.md` in the rendered HTML, not `README.html`.
3. **Warning elimination**: `{{ port.lstrip('/') }}` in RESEARCH docs produces 2 warnings per file. raw/endraw wrapping eliminates all 4 warnings.
4. **Non-fatal doctor issue**: `bundle exec jekyll doctor` reports `undefined method 'absolute?' for nil:NilClass` — known Jekyll 3.10 bug when `url:` is not set. Does not affect build output.

## 2026-06-20 15:40 — Phase 95: Git Tree Preparation Plan — TESTS EXECUTED

**Status**: ✅ COMPLETED — All 5 quantums verified via manual inspection.

### Test Results

| Q | Test | Method | Result |
|---|------|--------|--------|
| Q1 | Stale artifacts removed | `ls _uploads/` | Empty ✅ |
| Q1 | .gitignore updated | `git status --short` | Clean ✅ |
| Q1 | .gitkeep markers | `find ... -name '.gitkeep'` | Present ✅ |
| Q2 | Workflow docs gap filled | grep IMPLEMENTATION_* for Phase 93/94 | Both present ✅ |
| Q3 | --help claim fixed | grep docs/index.md for "usage" | Present ✅ |
| Q4 | Sequential git add | Session log | Approved ✅ |
| Q5 | WS_EVENT_FLOW.md relocated | `test -f docs/ws-event-flow.md` | Present ✅ |
| Q5 | Old path removed | `test ! -f WS_EVENT_FLOW.md` | Removed ✅ |
| Q5 | Cross-refs updated | grep -rn "WS_EVENT_FLOW" | All updated ✅ |

**Gotchas**: None. This was a pure housekeeping phase with no code changes.

## 2026-06-20 20:03 — Phase 96: test_ci.sh wired into scripts_tests

**Change**: Added `test_ci.sh` to the `scripts_tests` nox session (after
`test_install_arduino_deps.sh`). The script tests 10 scenarios for
`scripts/ci.sh` using a fake nox shim — 30 assertions total.

**Results**:
- Standalone run: 30/30 pass ✅
- Nox `scripts_tests`: 128 pytest + 12 bash + 30 bash = 170 total in 24s ✅

**Gotchas**: None. The script is fully self-contained (bash-only) and uses
`BASH_SOURCE` for path resolution, so it works correctly when launched from
any CWD (including nox's chdir to `scripts/`).

## 2026-06-21 11:55 — Phase 98: WS Push Migration — TESTS EXECUTED

**Status**: ✅ IMPLEMENTED AND TESTED — All 5 quantums complete.

### Automated Test Sessions

All 8 nox sessions executed and passed:

| Session | Command | Result |
|---------|---------|--------|
| All tests | `nox -s all_tests` | ✅ ALL PASS (~3m) |
| Arduino gRPC | `nox -s arduino_grpc` | ✅ PASS |
| Board manager | `nox -s board_manager` | ✅ PASS |
| Board manager client | `nox -s board_manager_client` | ✅ PASS |
| Arduino sketch tools | `nox -s arduino_sketch_tools` | ✅ PASS |
| Arduino dash | `nox -s arduino_dash` | ✅ PASS |
| Medminder dash | `nox -s medminder_dash` | ✅ PASS |
| Scripts tests | `nox -s scripts_tests` | ✅ PASS |

**Note**: No pre-existing pipenv lock failures remain. The noxfile `PROJECT_ROOT` fix resolved them.

### Test Results Per Quantum

#### Q1 — Daemon Badge OOB ✅

| Check | Method | Result |
|-------|--------|--------|
| base.html hx-trigger = "load" | grep on base.html | `every 10s` removed ✅ |
| daemon_badge.html stripped of hx-* | grep on partial | 0 hx-* attributes ✅ |
| _broadcast_daemon_badge() in arduino_dash/pubsub.py | grep | Method exists ✅ |
| _broadcast_daemon_badge() in medminder_dash/pubsub.py | grep | Method exists ✅ |
| No test regressions | `nox -s all_tests` | All pass ✅ |

#### Q2 — Board Status Badge OOB ✅

| Check | Method | Result |
|-------|--------|--------|
| board_status_badge.html stripped of hx-* | grep on partial | 0 hx-* attributes ✅ |
| board_detail.html unique per-port badge IDs | grep on template | IDs contain port filter ✅ |
| Badge OOB broadcast in arduino_dash _on_board_event() | grep pubsub.py | Present ✅ |
| Badge OOB broadcast in medminder_dash _on_board_event() | grep pubsub.py | Present ✅ |
| No test regressions | `nox -s all_tests` | All pass ✅ |

#### Q3 — Compile/Upload OOB Targeting ✅

| Check | Method | Result |
|-------|--------|--------|
| Compile OOB: `hx-swap-oob="beforeend:#compile-output-"` | grep extension.py:182 | Present ✅ |
| Upload OOB: `hx-swap-oob="beforeend:#upload-output-"` | grep extension.py:214 | Present ✅ |
| No test regressions | `nox -s all_tests` | All pass ✅ |

#### Q4 — Compile Progress Percentage ✅

| Check | Method | Result |
|-------|--------|--------|
| compile_stream() yields 4-tuple `(out, err, done, percent)` | grep client.py | Updated ✅ |
| _make_progress() accepts percent | grep board_worker.py | Present ✅ |
| _compile_last_pct tracking per port_safe | grep extension.py | Dict present ✅ |
| Progress bar `<progress>` in board_detail.html | grep template | Present ✅ |
| [N%] prefix prepended to output | grep extension.py | Present ✅ |
| No test regressions | `nox -s all_tests` | All pass ✅ |

#### Q5 — Noxfile PROJECT_ROOT Fix ✅

| Check | Method | Result |
|-------|--------|--------|
| `env={"PROJECT_ROOT": str(ROOT)}` added | grep noxfile.py | Present ✅ |
| All pipenv sessions now pass | `nox -s all_tests` | All 8 green ✅ |

### Key Findings

1. **compile_stream() 4-tuple clean break**: All consumers of the previous 3-tuple signature were updated: `compile()` method in client.py, board worker compile handler in board_worker.py, and all tests that mock or call `compile_stream()`. No stale 3-tuple unpacking remains.

2. **Upload remains 3-tuple**: Confirmed via gRPC proto analysis that `UploadResponse` has no `TaskProgress` submessage. Upload progress bar is not feasible at the gRPC level.

3. **noxfile PROJECT_ROOT fix resolved pipenv failures**: The 5 pre-existing pipenv lock failures from Phase 97 are now fully resolved. All 8 nox sessions pass cleanly.

4. **Port-safe IDs match between Python and Jinja**: Python `port.replace("/", "_")` produces the same result as Jinja `{{ port | replace('/', '_') }}`. Verified for `/dev/ttyACM0` → `_dev_ttyACM0`.

5. **Compiler sends ~25+ progress updates**: The arduino-cli builder emits frequent `TaskProgress` messages during compilation, providing smooth progress bar animation.

## 2026-06-21 — Phase 98 Q6: Rename TestAdminBoardSelectorPolling — TESTS EXECUTED

**Status**: ✅ COMPLETED — Pure rename, no functional change.

### Test Results

| # | Check | Method | Result |
|---|-------|--------|--------|
| 1 | Class renamed in test_admin.py:811 | `grep 'class TestAdminBoardSelector'` | Renamed ✅ |
| 2 | Docstring updated | `grep -A3 'class TestAdminBoardSelector'` | WS push ref present ✅ |
| 3 | README.md reference updated | `grep TestAdminBoardSelector README.md` | `TestAdminBoardSelector` present ✅ |
| 4 | No stale references in source | `grep -rn 'TestAdminBoardSelectorPolling' medminder_dash/ --exclude-dir=.egg-info --exclude-dir=.pytest_cache` | 0 matches ✅ |
| 5 | Renamed class tests pass | `nox -s 'tests(medminder_dash)' -- -k 'TestAdminBoardSelector' -v` | 3/3 pass ✅ |
| 6 | Full medminder_dash suite | `nox -s 'tests(medminder_dash)'` | 186 pass, 1 skip ✅ |

**Gotchas**: `.egg-info/PKG-INFO` and `.pytest_cache/` retain stale references until rebuild — expected for generated files.

---

## Phase 99 — HTML Template Homogenisation

**Date**: 2026-06-22 12:43

**Status**: ✅ Complete

### Approach

Per-quantum test verification: run `nox -s 'tests(arduino_dash)'` and `nox -s 'tests(medminder_dash)'` after each template change to catch regressions immediately.

### Test Results

| Quantum | arduino_dash | medminder_dash | Notes |
|---------|-------------|----------------|-------|
| Q1a (arduino board_detail) | 119 ✓ | — | No form wrapper, FQBN moved, hx-include changed |
| Q1b+c+d (medminder board_detail + route vars) | 119 ✓ | 186 ✓, 1 skip | htmx /last-upload, guards, medicines partial |
| Q2a+b (admin.html) | 119 ✓ | 186 ✓ | assigned-sketch-info, admin_medicine_section partial |
| Q3a+b (admin_board_selector) | 119 ✓ | 186 ✓ | Template variable convergence |
| Q4a+b (compile_upload_card) | 119 ✓ | 186 ✓ | Step numbers, entity convergence |
| T1+T2+T3 (trivial diffs) | 119 ✓ | 186 ✓ | 3 partials aligned |
| Q6 (base.html DnD) | 119 ✓ | 186 ✓ | Listener convergence |
| **SketchRegistry extract** | 119 ✓ | 186 ✓ | Shared class + per-app wrappers |

### Test Fixes Applied

**3 tests in `medminder_dash/tests/test_routes.py::TestBoardDetailFqbn` updated:**

1. `test_sketch_path_uses_per_board_assignment` — Changed from `assert per_board_path.encode() in resp.data` to asserting htmx container: `assert b'id="sketch-path-container"' in resp.data`, `b'hx-get="/last-upload"'`, `b'hx-include="#active-board-hardware-id"'`, hardware_id value present

2. `test_sketch_path_falls_back_to_default` — Same assertion change (htmx container instead of sketch path value)

3. `test_sketch_path_uses_default_for_no_hardware_id` — Same + confirms `b'id="active-board-hardware-id" value=""'`

**Why**: board_detail.html switched from static `<input id="sketch_path" value="{{ sketch_path }}">` to htmx `/last-upload` which loads the sketch path dynamically. The sketch path is no longer rendered in the initial HTML response.

### Verdict

All template changes verified. No regressions. 119 + 186 = 305 total passing tests.

---

## Entry 3 — Playwright MCP E2E Session (2026-06-22)

**Date**: 2026-06-22

**Goal**: Verify Phase 99 template homogenisation works in real browser via Playwright MCP.

## Root cause analysis — server dying between bash invocations

### The symptom

`curl http://127.0.0.1:8765/` returned HTTP 200 while the bash command was still executing (e.g., within a `sleep 3 && curl` chain), but after the bash tool completed and the next tool invocation ran, `curl` returned 000 (connection refused). `ps aux | grep arduino_dash_server` showed no process.

### Failed attempts

| Approach | Result |
|----------|--------|
| `nohup python3 ... &` | Server died on shell exit |
| `nohup ... & disown` | Same |
| `setsid python3 ... </dev/null &>/dev/null &` | Same |
| `&` combined with `sleep && curl` in same command | Server died when the (longer) bash timeout expired |

### Root cause

1. The bash tool launches a shell session and tracks the **entire process group**.
2. When a command uses `&`, the shell forks a background child that remains in the same process group.
3. When the bash tool's shell command completes (foreground exits) or its timeout expires, the tool sends **SIGHUP → whole process group**.
4. `disown` removes the job from the shell's job table but **does not** protect against the tool's process-group-level signal. The child is still a member of the same process group.
5. `setsid` creates a new session, but if the tool tracks the original session ID, it still kills descendant processes.

### Why short timeout works

`python3 ... &>/dev/null & disown` with `timeout=3000`:
- The foreground `python3 ... &>/dev/null & disown` executes nearly instantly (just forks the child, redirects stdout, removes from job table).
- The bash tool sees the foreground command exit in <100ms, well under the 3s timeout.
- The tool closes the shell **fast**, before it propagates SIGHUP to child processes.
- Race condition: the Flask server has already started its socket listener by then (the fork + socket bind is faster than the tool's teardown).

With longer timeouts or combined commands (`sleep && curl`), the tool waits longer and its teardown cycle is more aggressive, eventually finding and killing the orphaned process.

### The real fix (Phase 99 workaround)

Keep `&>/dev/null & disown` and **keep the bash call short** — never chain additional commands after the `&`. A standalone call with `timeout=3000` reliably lets the server survive.

> **This workaround was superseded in Phase 100.** See Entry 4 below for the proper fix (fork + setsid + redirect).

**Results**:

| Recipe | App | Page | Status |
|--------|-----|------|--------|
| 2 | arduino_dash | Board Grid | ✅ |
| 3 | arduino_dash | Admin | ✅ |
| 6 | arduino_dash | Board Detail | ✅ |
| 7 | medminder_dash | Home | ✅ |
| 8 | medminder_dash | Board Detail + API | ✅ (3 medicines) |
| 9 | medminder_dash | Admin | ✅ |

**Key observations**:
- All homogenised templates render correctly in both apps
- Step numbering (1: Set Medicines, 2: Compile, 3: Upload) correct
- Route paths diverge correctly per-app
- MedMinderV2 sketch pre-selected in medminder admin
- Mock medicines (Aspirin, VitaminD, Ibuprofen) render on both admin and board detail

---

## Entry 4 — Phase 100: Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14

### Goal

Verify that `e2e/servers/arduino_dash_server.py` and `medminder_dash_server.py` survive the bash tool's shell exit without requiring `&`, `&>/dev/null`, `disown`, or special timeouts. Verify `--pidfile`, `--stop`, `--force`, `--logfile` work correctly.

### Approach

Plain command — no shell hacks:
```bash
python3 server.py --mock --production --pidfile /tmp/x.pid --logfile /tmp/x.log
```

Then, in a second bash call:
```bash
curl http://127.0.0.1:<port>/     # verify survival
python3 server.py --stop --pidfile /tmp/x.pid   # clean shutdown
```

### New Root Cause (Phase 100 discovery)

The earlier root-cause analysis (Entry 3) blamed **process group** signals. The real culprit is **session** signals:

| Mechanism | Scope | Protection |
|-----------|-------|------------|
| `os.setpgid(0, 0)` | Changes process GROUP (PGID) | ✗ Tool tracks processes by SESSION |
| `os.setsid()` | Creates new SESSION | ✓ Immune to parent session's SIGHUP |

When the bash tool times out, it kills the shell (session leader). The kernel broadcasts SIGHUP to **every process in that session** — regardless of process group. `os.setpgid()` alone is insufficient because it only changes PGID, not SID. Only `os.setsid()` (which requires `os.fork()`) creates a new session.

### Implementation

`_daemonize(logfile)`:
1. `os.fork()` — parent exits immediately via `os._exit(0)` → bash sees exit → tool returns
2. Child: `os.setsid()` → new session, immune from parent SIGHUP
3. Child: `signal.signal(SIGHUP, SIG_IGN)` → belt-and-suspenders
4. Child: `_redirect_io()` → dup2 stdout/stderr to logfile → captured Flask logs, no SIGPIPE from closed parent pipe

### Test Results

| Test | arduino_dash (port 8765) | medminder_dash (port 8766) |
|------|--------------------------|----------------------------|
| Plain start (no `&`, `disown`) | ✅ Returns immediately | ✅ Returns immediately |
| Survival (curl in next invocation) | ✅ HTTP 200 | ✅ HTTP 200 |
| Log capture (`--logfile`) | ✅ 571 bytes | ✅ 649 bytes |
| `--stop` cleanup | ✅ "Stopped PID X" | ✅ "Stopped PID X" |
| Stale PID handling | ✅ "PID not found — removed stale pidfile" | ✅ No pidfile → exits(1) |

### Key Findings

1. **`os.setpgid()` ≠ protection** — PGID changes don't cross session boundaries; the tool kills by session, not PGID
2. **`os.setsid()` requires a fork** — a process can only call setsid() if it's not a group leader; fork guarantees the child is not a group leader
3. **Redirect must happen in the child** — after fork, before any Flask output; otherwise SIGPIPE from the closed tool pipe kills the server
4. **Bootstrap messages go to logfile** — after redirect, all `print()` calls land in the logfile; the terminal sees no output (expected — the parent already exited)

## 2026-06-23 — Phase 100 Doc Sync: GUIDE Files Updated

**Status**: ✅ Complete.

Both `e2e/MCP_TESTING_GUIDE.md` and `e2e/agent_tools/GUIDE.md` received 3 new sections documenting the Phase 100 server script lifecycle:

| Section | Content |
|---------|---------|
| **Disown and Background Jobs** | Explains `disown` (removes job from shell's job table, not session), documents old fragile workaround (`&>/dev/null & disown` + `timeout=3000`) and why `_daemonize()` replaces it entirely |
| **Script Architecture** | 5 lifecycle helpers (`_get_default_pidfile`, `_write_pidfile`, `_remove_pidfile`, `_stop_server`, `_daemonize`) in a table, all 8 CLI flags, `main()` execution order |
| **Cleanup** (expanded) | SIGTERM→5s poll→SIGKILL escalation, stale pidfile detection via `ProcessLookupError`, lost pidfile recovery, orphaned BMS cleanup |

**Fixes**: Removed duplicate old "Stopping Servers" (lsof/pkill) section from `MCP_TESTING_GUIDE.md`.

---

## 2026-06-24 17:57 — Phase 100c: Fix Console Errors — TESTS EXECUTED

**Status**: ✅ COMPLETED — All verifications pass.

### Test Results

| # | Test | Method | Result |
|---|------|--------|--------|
| 1 | New idiomorph CDN resolves | `curl -sIL https://unpkg.com/idiomorph/dist/idiomorph-ext.js` | HTTP 200 ✅ |
| 2 | Old idiomorph CDN returns 404 | `curl -sIL https://unpkg.com/htmx.org/dist/ext/idiomorph.js` | HTTP 404 ✅ |
| 3 | arduino_dash pyproject.toml has simple-websocket | `grep simple-websocket` | Present at line 14 ✅ |
| 4 | medminder_dash pyproject.toml has simple-websocket | `grep simple-websocket` | Present at line 15 ✅ |
| 5 | arduino_dash base.html uses correct CDN | `grep idiomorph` | `idiomorph/dist/idiomorph-ext.js` ✅ |
| 6 | medminder_dash base.html uses correct CDN | `grep idiomorph` | `idiomorph/dist/idiomorph-ext.js` ✅ |
| 7 | No regressions — arduino_dash tests | `nox -s 'tests(arduino_dash)'` | Same 111 pre-existing errors ✅ |
| 8 | No regressions — medminder_dash tests | `nox -s 'tests(medminder_dash)'` | Same 1 pre-existing failure ✅ |

### Root Cause Summary

**Bug 1 — idiomorph.js 404**:
- htmx 1.x bundled extensions inside `htmx.org/dist/ext/`. htmx 2.x (used by both dashboards) moved extensions to separate packages.
- The URL `https://unpkg.com/htmx.org/dist/ext/idiomorph.js` no longer resolves.
- Fixed by changing to `https://unpkg.com/idiomorph/dist/idiomorph-ext.js`.

**Bug 2 — WS Invalid Frame Header**:
- `flask-sock` needs a WebSocket transport implementation (`simple-websocket` for sync workers).
- Without it, the WS upgrade request gets a garbled/non-101 HTTP response.
- Fixed by adding `simple-websocket>=1.0.0` to both `pyproject.toml` files.

### Pre-existing Test Failures

Both test suites had pre-existing failures unrelated to Phase 100c changes:

| Suite | Pre-existing Failures | Root Cause |
|-------|-----------------------|------------|
| arduino_dash | 111 errors | `_pending_responses_lock`, `_compile_results_lock`, etc. accessed via `app` module but live in `state` module. State was extracted in a prior phase but tests were not updated. |
| medminder_dash | 1 failure | `test_sketch_path_uses_default_for_no_hardware_id` — assertion mismatch likely from Phase 99 template homogenisation. |
---

## 2026-06-24 20:31 — Phase 101: Redesign & Rebuild Standalone Distributions — TESTS EXECUTED

**Status**: ✅ COMPLETED — All verifications pass.

### Key Findings

1. **`__file__` not available in PyOxidizer Starlark** — The initial plan to derive `REPO_ROOT` via `rsplit("/", N)` from `__file__` failed because Starlark has no `__file__` variable. `load()` from another generated `.bzl` file also failed (CP04 error). Solution: `@REPO_ROOT@` placeholder + `sed -i` substitution in `build_standalone.sh`.

2. **`pip_download()` vs `pip_install()`** — Dashboard configs used `pip_download()` for local wheel paths, but `pip_download()` only resolves from PyPI indexes. Changed all local wheel references to `pip_install()`.

3. **Cleanup via RETURN trap** — `build_standalone.sh` uses `trap cleanup RETURN` for normal function return, with explicit `git checkout` before `die` calls (exit skips RETURN trap).

4. **All 3 binaries built and verified** — 51MB each, all modules/templates/static files/deps present.

### Test Results

| # | Test | Result |
|---|------|--------|
| 1 | arduino-dash --help | ✅ Exit 0 |
| 2 | medminder-dash --help | ✅ Exit 0 |
| 3 | board-manager --help | ✅ Exit 0 |
| 4 | arduino-dash modules | ✅ All 7 present |
| 5 | medminder-dash modules | ✅ All 7 present |
| 6 | Templates (arduino-dash) | ✅ All present |
| 7 | Templates (medminder-dash) | ✅ All present |
| 8 | simple-websocket (arduino-dash) | ✅ Present |
| 9 | simple-websocket (medminder-dash) | ✅ Present |
| 10 | Static files (both dashboards) | ✅ style.css + favicons |

### Orphan Templates

`deploy.html` and `admin_sketch_dir.html` are still present in medminder-dash dist. Expected — user confirmed they should remain.

---

## 2026-06-24 20:45 — Standalone Bundle Testing: Infrastructure Survey

**Status**: Research complete — planning next steps.

### Goal

Survey existing testing infrastructure and identify gaps for testing the 3 PyOxidizer standalone binaries (`arduino-dash`, `medminder-dash`, `board-manager`) in `dist-standalone/`.

### Current State: What IS Tested

| Layer | Tests | Scope |
|-------|-------|-------|
| **Per-package unit tests** | ~418+ pytest tests via `nox -s tests(pkg)` | Code logic, not binary |
| **scripts/ test suite** | 170 tests (128 pytest + 42 bash) via `nox -s scripts_tests` | Script behavior, not binary |
| **Wheel installation** | `scripts/test_installs.sh` — import + `--help` smoke | Wheels only, not standalone |
| **PyOxidizer build** | `--help` smoke in `build_standalone.sh` lines 137-145 | Binary responds to `--help` |
| **E2E browser tests** | 10 MCP recipes + 22 Playwright specs | Flask dev servers only |
| **CI pipeline** | `scripts/ci.sh` — tests + builds | No standalone involvement |

### Current Testing Infrastructure

#### E2E Directory

```
e2e/
├── agent_tools/
│   ├── AGENT.md, COMMAND.md, GUIDE.md, SKILL.md
├── docs/
│   ├── index.md              # E2E docs landing page
│   ├── servers.md            # Mock server reference
│   ├── scenarios.md          # 10 test scenario recipes
│   └── agent-tools.md        # Agent integration
├── fixtures/test-data.ts     # Shared test constants
├── servers/
│   ├── arduino_dash_server.py      # Flask dev server (278 lines)
│   └── medminder_dash_server.py    # Flask dev server (316 lines)
├── specs/                         # @playwright/test specs
│   ├── arduino_dash/              # 4 spec files, 12 tests
│   └── medminder_dash/            # 4 spec files, 10 tests
├── MCP_TESTING_GUIDE.md           # 530-line testing guide
└── playwright.config.ts           # Playwright config
```

#### Server Scripts (`e2e/servers/`)

Both scripts provide:
- CLI: `--mock`, `--bms`, `--port`, `--production`, `--pidfile`, `--stop`, `--force`, `--logfile`
- Daemonization: `os.fork()` + `os.setsid()` + `_redirect_io()`
- Mock data: injects into `state` module (boards, sketches, medicines)
- Tested via: `python3 e2e/servers/arduino_dash_server.py --mock` (not standalone binary)

**Both serve Flask dev servers — not standalone binaries.**

#### Standalone Build (`scripts/build_standalone.sh`)

Builds all 3 apps via PyOxidizer. After each build:
1. Copies install dir to `dist-standalone/<app>/`
2. Runs `--help` smoke test (greps for usage/help/options)
3. Packages to `.tar.gz`

**Only `--help` smoke. No HTTP serving test.**

#### Standalone Bundle Structure

```
dist-standalone/arduino-dash/
├── arduino-dash     # ~51 MB compiled binary
├── COPYING.txt
└── prefix/          # ~100 MB sidecar (C extensions)
```

The binary requires `prefix/` adjacent at runtime.

### What is MISSING for Standalone Binary Testing

| # | Gap | Details |
|---|-----|---------|
| 1 | **No start/stop lifecycle** | No script launches `dist-standalone/<app>/<binary>` and manages its lifecycle. No pidfile, no `--stop`, no `--logfile` for standalone. |
| 2 | **No mock data injection** | Standalone binary has no `--mock` flag. Dev servers inject mock data into in-memory state before `app.run()`. The gunicorn entry point in the binary has no injection hook. |
| 3 | **No HTTP smoke tests** | No test verifies the binary actually serves HTTP responses — only `--help` is tested. |
| 4 | **No port binding tests** | No test verifies the binary binds to the expected port or handles port conflicts. |
| 5 | **No E2E recipes for standalone** | All 10 MCP recipes and 22 Playwright specs target dev servers. None target standalone. |
| 6 | **No `test_standalone` nox session** | `noxfile.py` has `build_standalone` (build only). No `test_standalone`. |
| 7 | **No CI integration** | `scripts/ci.sh` excludes standalone build/test. |
| 8 | **No missing `prefix/` handling** | No test verifies graceful error when `prefix/` is absent. |
| 9 | **No daemonization for standalone** | The binary uses gunicorn's daemon model. No MCP guide covers starting/stopping standalone instances. |
| 10 | **No `webServer` in Playwright config** | `playwright.config.ts` points to dev server scripts, not standalone binaries. |

### Specific Gaps per Application

| App | Binary | Current Test | What Should Be Tested |
|-----|--------|-------------|----------------------|
| board-manager | `board-manager` | `--help` only | gRPC port binding, daemon mode, board detection |
| arduino-dash | `arduino-dash` | `--help` only | HTTP serving, dashboard render, admin, sketch upload |
| medminder-dash | `medminder-dash` | `--help` only | HTTP serving, board grid, medicine CRUD, compile/upload |

### Capability Comparison: Dev Server vs Standalone

| Capability | Flask Dev Server | Standalone Binary |
|------------|-----------------|-------------------|
| Start script | `e2e/servers/*_server.py` | None |
| Daemonization | `fork + setsid` (built-in) | Gunicorn handles (different) |
| Mock data | `--mock` flag | Not available |
| Shutdown | `--stop` flag | None |
| MCP recipes | 10 recipes | Zero |
| Playwright specs | 22 specs | Zero |
| Port config | 8765/8766 `--port` | Gunicorn bind config |
| CI integration | `nox -s all_tests` | Not in CI |
| PID file | Built-in | None |
| Log capture | `--logfile` flag | None |

### Options for Filling the Gaps (Not Yet Decided)

1. **Add `--mock` flag to the standalone binary's gunicorn entry point** — enable mock data injection, then all existing MCP recipes work against standalone with the binary's own port.

2. **Create standalone-specific E2E scripts** — bash/Python scripts that start the binary (requires real BMS or other setup), curl-test it, shut it down.

3. **Use real backend services** — run `board-manager` standalone as BMS, point `arduino-dash` standalone at it — full integration test (requires real Arduino for meaningful results).

### Key Files Referenced

| File | Path |
|------|------|
| Build script | `scripts/build_standalone.sh` |
| Arduino dash server | `e2e/servers/arduino_dash_server.py` |
| Medminder dash server | `e2e/servers/medminder_dash_server.py` |
| E2E testing guide | `e2e/agent_tools/GUIDE.md` |
| MCP testing guide | `e2e/MCP_TESTING_GUIDE.md` |
| CI script | `scripts/ci.sh` |
| Noxfile | `noxfile.py` |
| E2E doc index | `e2e/docs/index.md` |
| Scenarios doc | `e2e/docs/scenarios.md` |
| Servers doc | `e2e/docs/servers.md` |

---

## 2026-06-25 09:10 — Phase 102: Fix Pre-Existing Test Failures

### Results

| Session | Before | After |
|---------|--------|-------|
| `tests(arduino_dash)` | 111 errors, 8 pass | 119 pass, 0 errors |
| `tests(medminder_dash)` | 1 failure, 185 pass, 1 skip | 186 pass, 1 skip, 0 failures |
| All other sessions | No change | All pass |

### Findings

1. **Arduino_dash**: The `clear_caches` autouse fixture in `test_app.py:17` accessed state variables via `_app_module.*` but `app.py` didn't re-export them. Fixing this uncovered 53 cascading test failures (missing re-exports for pubsub functions, wrong import path for `_warm_upload_registry`, missing `UPLOAD_BASE_DIR` in `state.py`, and a djlint-brittle assertion).
2. **Medminder_dash**: Single assertion failure due to djlint multi-line attribute reformatting.
3. **UPLOAD_BASE_DIR production bug**: `state.py:6` re-import fixed 8 test failures that were using `patch("arduino_dash.state.UPLOAD_BASE_DIR", ...)`, plus fixed actual broken production code in `sketch_management.py`, `api_routes.py`, and `html_routes.py` (9 references total).
4. **Wrong import in api_routes.py**: `from arduino_dash.html_routes import _warm_upload_registry` should have been `from arduino_dash.sketch_management import ...`.

---

## 2026-06-25 11:57 — Phase 103: API Route Restructure ✅ COMPLETED

### Test Results

`nox -s all_tests` — 8/8 sessions, 0 failures, 0 errors ✅

| Session | Status |
|---------|--------|
| `scripts_tests` | ✅ |
| `tests(board_manager)` | ✅ |
| `tests(board_manager_client)` | ✅ |
| `tests(arduino_sketch_tools)` | ✅ |
| `tests(arduino_dash)` | ✅ (119 pass) |
| `tests(arduino_grpc)` | ✅ |
| `tests(medminder_dash)` | ✅ (186 pass, 1 skip) |
| `tests(arduino_shared)` | ✅ |

### Findings

1. **Parallel agent implementation worked flawlessly**: Both agents produced correct code on first try. No test failures attributable to agent implementation errors.
2. **`TestApiBoardList` class name is now misleading**: Tests `GET /api/pubsub/boards/health` (was `GET /api/boards`), but the class name still references "ApiBoardList". Functionally correct — the URL and method are what matter for test assertions.
3. **No new tests needed**: All new routes are thin wrappers that call existing helper functions. Existing test coverage of those helpers suffices.
4. **Module docs needed 4 file updates**: `state.md`, `utils.md`, `api_routes.md` for both modules — straightforward additions of new symbols and route tables.

---

## 2026-06-25 16:10 — Phase 104: E2E Documentation Restructure ✅ COMPLETED

### Test Strategy

Pure documentation restructure — no code changes. Verification strategy:

1. **Content existence**: 11 grep/file-existence checks across all 11 new + edited files
2. **Cross-reference integrity**: Jekyll build validates all relative links resolve
3. **End-to-end flow**: playwright-mcp-testing command verifies skill/guide/server/navigate work end-to-end

### Test Results

| # | Scenario | Method | Result |
|---|----------|--------|--------|
| 1 | e2e/README.md exists | `test -f e2e/README.md` | ✅ |
| 2 | e2e/index.md exists | `test -f e2e/index.md` | ✅ |
| 3 | e2e/test-sketch/ files | `ls e2e/test-sketch/*` | ✅ Both present |
| 4 | specs section in docs/index.md | grep "Automated Playwright Specs" | ✅ |
| 5 | test-sketch in docs/index.md | grep "Test Sketch" | ✅ |
| 6 | webServer in servers.md | grep -i "webServer" | ✅ |
| 7 | test-sketch in COMMAND.md | grep "test-sketch" | ✅ |
| 8 | test-sketch in AGENT.md | grep "test-sketch" | ✅ |
| 9 | test-sketch in GUIDE.md | grep "Test Sketch" | ✅ |
| 10 | test-sketch in MCP_TESTING_GUIDE.md | grep "Test Sketch" | ✅ |
| 11 | docs/e2e-testing.md links e2e/index.md | grep "e2e/index.md" | ✅ |
| 12 | Root index.md links e2e/index.md | grep "e2e/index.md" | ✅ |
| 13 | Jekyll build | `bundle exec jekyll build` | ✅ 0 errors, 0 warnings |
| 14 | playwright-mcp-testing E2E | Skill→guide→server→navigate→snapshot→cleanup | ✅ |

### Key Findings

1. **Server needs pipenv**: `python3 e2e/servers/arduino_dash_server.py --mock` fails with `ModuleNotFoundError` because `arduino_dash` is installed in pipenv venv, not system Python. Must use `pipenv run python e2e/servers/...`.
2. **No stale cross-references**: `.playwright-mcp/test-sketch` was not referenced by any existing docs — grep confirmed zero hits in `.md` files.
3. **Jekyll passes cleanly**: All new files have front matter, all relative links resolve correctly.

---

## 2026-06-25 17:53 — Phase 104.1: Document e2e/fixtures/ 🏗️ IN PROGRESS

**Gap**: Original Phase 104 plan item "Document e2e/fixtures/ and e2e/specs/" was only half-implemented — specs were documented but fixtures were not.

**Fix**: Add "Test Data Fixtures" subsection to `e2e/docs/index.md` under Automated Playwright Specs covering: purpose (mirrors `--mock` server state), exported constants (MOCK_PORTS, MOCK_SKETCH, MOCK_MEDICINES, URL helpers), import path, and shelf status.

**Test scenarios** (6 checks):
1. Section presence: `grep "Test Data Fixtures" e2e/docs/index.md`
2. Export mention: `grep "MOCK_PORTS" e2e/docs/index.md`
3. Import path: `grep "from.*fixtures/test-data" e2e/docs/index.md`
4. `--mock` relation: grep for fixture+server mock relationship
5. Cross-doc consistency: fixtures mentioned in e2e/README.md + e2e/index.md
6. Jekyll build: 0 errors, 0 warnings

**Results**: All 6 checks pass. Jekyll build: 0 errors, 0 warnings. ✅

---

## 2026-06-25 18:14 — Phase 104.2: Fix shelved-specs activation docs 🏗️ IN PROGRESS

**Gap**: Automated Playwright Specs docs missing two critical items:
1. `npx playwright install --with-deps` browser binary download step — without it, `npx playwright test` fails with missing browser error
2. Project-root run alternative `npx playwright test --config e2e/playwright.config.ts` for users running from monorepo root

These were caught during review of Phase 104.1 by checking against the original spec.

**Fix**: Edit e2e/docs/index.md Installation and Running subsections.

**Results**: All 3 test scenarios pass. Installation section now shows `npx playwright install --with-deps` with a callout explaining the error without it. Running section shows `--config e2e/playwright.config.ts` as a project-root alternative. Jekyll build: 0 errors, 0 warnings. ✅

## Phase 104.3 — Remove shelved labels + strip agent_tools Playwright refs (2026-06-27 19:22)

Removed "(Shelved)" from e2e/docs/index.md, e2e/README.md, e2e/index.md, CODEBASE_REFERENCE.md, and all Phase 100 references. Stripped standalone Playwright file refs from agent_tools/GUIDE.md and MCP_TESTING_GUIDE.md. Jekyll build passes.

## Phase 105 — Relocate medminder_dash and board_manager docs alongside setup.py (2026-06-27 19:22)

Moved both docs/ directories out of importable Python packages. Updated all cross-references. Jekyll build passes.
{% endraw %}
