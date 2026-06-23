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
| _broadcast_daemon_badge() in medminder_dash/pubsub_infra.py | grep | Method exists ✅ |
| No test regressions | `nox -s all_tests` | All pass ✅ |

#### Q2 — Board Status Badge OOB ✅

| Check | Method | Result |
|-------|--------|--------|
| board_status_badge.html stripped of hx-* | grep on partial | 0 hx-* attributes ✅ |
| board_detail.html unique per-port badge IDs | grep on template | IDs contain port filter ✅ |
| Badge OOB broadcast in arduino_dash _on_board_event() | grep pubsub.py | Present ✅ |
| Badge OOB broadcast in medminder_dash _on_board_event() | grep pubsub_infra.py | Present ✅ |
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
{% endraw %}
