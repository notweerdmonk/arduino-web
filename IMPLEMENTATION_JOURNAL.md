---
---
{% raw %}
# Implementation Journal — Phase 98: WS Push Migration (Badge OOB → Compile/Upload OOB → Compile Progress Bar)

**Date**: 2026-06-21 11:55

---

## Entry 1 — Q1: Daemon Badge OOB

**Date**: 2026-06-21 11:55

**Status**: ✅ Complete

**Goal**: Replace HTMX polling (`every 10s`) for the daemon status badge with WS push via OOB HTML fragments.

### Changes Made

**`base.html` (both dashboards)**:
- Changed `hx-trigger="every 10s, load"` → `"load"` — keeps one-shot initial AJAX fill, removes periodic polling
- The wrapper span still has `hx-trigger="load"`, `hx-get="/daemon/status"`, `hx-target="this"`, `hx-swap="outerHTML"` for the initial render

**`daemon_badge.html` (both dashboards)**:
- Stripped all `hx-*` attributes: `hx-get`, `hx-trigger`, `hx-target`, `hx-swap`
- Now a plain HTML fragment rendered with `{% include %}` by server-side routes or broadcast as OOB HTML

**`arduino_dash/pubsub.py`**:
- Added `_broadcast_daemon_badge()` — renders `daemon_badge.html` template with current state, wraps in `<span hx-swap-oob="true" id="daemon-badge">`
- Called from `_on_daemon_ready()` — broadcasts immediately when daemon becomes ready
- Called from `_on_pubsub_reconnect()` — re-broadcasts on reconnect to refresh all clients

**`medminder_dash/pubsub_infra.py`**:
- Same `_broadcast_daemon_badge()` method added with identical behavior

### Gotchas

1. **OOB wrapper must match existing ID**: The OOB `<span>` must use `id="daemon-badge"` to match the existing element in `base.html`. HTMX's OOB swap identifies elements by ID.
2. **Initial render still needs hx-trigger="load"**: We keep the one-shot `hx-trigger="load"` on the wrapper span because the pubsub client may not yet be connected when the page loads. The WS push takes over after initial render.
3. **Reconnect handling**: `_on_pubsub_reconnect()` must re-broadcast the badge state because clients that missed the initial `_on_daemon_ready()` event need to be updated.

---

## Entry 2 — Q2: Board Status Badge OOB

**Date**: 2026-06-21 11:55

**Status**: ✅ Complete

**Goal**: Replace HTMX polling for the board connection status badge with OOB WS push.

### Changes Made

**`board_status_badge.html` (both dashboards)**:
- Stripped all `hx-*` attributes — now a plain HTML fragment
- Badge status (Connected/Disconnected) conveyed via CSS classes only

**`board_detail.html` (both dashboards)**:
- Changed `id="board-status-badge"` → `id="board-status-badge--{{ port | replace('/', '_') }}"`
- Creates unique IDs like `board-status-badge--_dev_ttyACM0`, preventing collisions when multiple board_detail pages are open
- Changed `hx-trigger="every 10s, load"` → `"load"` (one-shot initial fill)

**`arduino_dash/pubsub.py` `_on_board_event()`**:
- After broadcasting the event feed HTML, now also renders and broadcasts the board status badge OOB
- Template context includes `event["port"]` and `event["connected"]` (boolean)
- Uses port-safe ID `board-status-badge--{port_safe}` to target the correct badge element

**`medminder_dash/pubsub_infra.py` `_on_board_event()`**:
- Same addition — badge OOB broadcast after event-feed broadcast

### Gotchas

1. **Port-safe IDs**: The port path `/dev/ttyACM0` must be transformed to `_dev_ttyACM0` using `.replace("/", "_")` to create valid HTML IDs. Both the template (Jinja filter) and Python (`port_safe`) must agree on the transformation.
2. **Badge must be unique per port**: Without per-port IDs, a board detail page showing port A would have its badge replaced by events for port B. The unique ID ensures each page only responds to its own board's events.
3. **Initial load still uses hx-trigger="load"**: Same reasoning as daemon badge — pubsub may not be connected when the page first renders.

---

## Entry 3 — Q3: Compile/Upload OOB Targeting

**Date**: 2026-06-21 11:55

**Status**: ✅ Complete

**Goal**: Make existing WS-delivered compile/upload progress lines visible by wrapping them in `hx-swap-oob` spans.

### Changes Made

**`arduino_sketch_tools/extension.py:182`** (compile progress line):
- Wrapped output lines in: `<span hx-swap-oob="beforeend:#compile-output-{port_safe}">`
- This targets the `#compile-output-{port_safe}` container in `board_detail.html`
- Lines appear immediately without needing HTMX polling

**`arduino_sketch_tools/extension.py:214`** (upload progress line):
- Same wrapping: `<span hx-swap-oob="beforeend:#upload-output-{port_safe}">`
- Targets `#upload-output-{port_safe}` container

### Gotchas

1. **Port transform must match**: The Python `port_safe = port.replace("/", "_")` must match Jinja `{{ port | replace('/', '_') }}`. Using `/dev/ttyACM0` → `_dev_ttyACM0` as the safe form.
2. **OOB beforeend appends, doesn't replace**: Each progress line is appended to the output container. The output containers are cleared on new compile/upload via the section-wrapper pattern (existing behavior).

---

## Entry 4 — Q4: Compile Progress Percentage

**Date**: 2026-06-21 11:55

**Status**: ✅ Complete

**Goal**: Add real-time compile progress bar via `<progress>` element OOB over WS, plus `[N%]` prefix per output line.

### Changes Made

**`arduino_grpc/client.py:compile_stream()`**:
- Changed from 3-tuple `(out, err, done)` to 4-tuple `(out, err, done, percent)`
- Tracks `last_percent` across iterations — reads `resp.progress.percent` from each `CompileResponse`
- Sets `percent = 100.0` when `done = True`
- `percent` is a `float` from gRPC's `TaskProgress.percent` field

**`board_manager/board_worker.py:_make_progress()`**:
- Now accepts `percent: float = 0.0` keyword argument
- Includes `"percent"` key in the progress data dict
- Compile handler: unpacks the 4-tuple `(out, err, done, percent)`, constructs separate messages:
  - Progress-only message (no `out`/`err`) when only `percent` changed
  - Standard output message when `out` or `err` has content
- This avoids sending duplicate output text just to update the progress bar

**`arduino_sketch_tools/extension.py:_on_compile_resp()`**:
- Reads `percent` from message data dict
- Tracks `_compile_last_pct` per port_safe (dict keyed by safe port)
- On percent change: broadcasts `<progress id="compile-progress-{port_safe}" value="{pct}" max="100">{pct}%</progress>` as OOB HTML
- Prepends `[N%] ` prefix to output text lines (e.g., `[42%] Compiling core...`)
- Only broadcasts progress bar when `_compile_last_pct != current_pct` to avoid redundant WS pushes

**`board_detail.html` (both dashboards)**:
- Added `<progress id="compile-progress-{port_safe}" value="0" max="100"></progress>` element
- Placed above the compile output div for visual context
- Hidden by default, updated via OOB WS push

### Gotchas

1. **Clean break for 4-tuple**: Changing `compile_stream()` return signature from 3-tuple to 4-tuple required updating all callers:
   - `compile()` method in `client.py`
   - Board worker compile handler in `board_worker.py`
   - All tests that mock or call `compile_stream()`
   - Upload remains 3-tuple (no `TaskProgress` in `UploadResponse`)
2. **Percent is float from gRPC**: `TaskProgress.percent` is a `float` (0.0–100.0), not an integer. Format as integer for display.
3. **arduino-cli sends ~25+ progress messages**: During a typical compile, the builder emits ~25+ `CompileResponse` messages with varying `TaskProgress.percent` values. This provides smooth progress bar updates.
4. **Progress-only messages reduce WS traffic**: By sending separate messages for percent-only updates, we avoid re-broadcasting output text lines that haven't changed.

---

## Entry 5 — Q5: Noxfile PROJECT_ROOT Fix

**Date**: 2026-06-21 11:55

**Status**: ✅ Complete

**Goal**: Fix `file://${PROJECT_ROOT}` expansion failure in pipenv-based nox sessions.

### Root Cause

The `tests()` session in `noxfile.py` calls `pipenv install` and `pipenv sync` which read `Pipfile` entries like:
```
[[source]]
url = "file://${PROJECT_ROOT}/dist"
```
The `${PROJECT_ROOT}` variable is defined in `.env` files but pipenv spawned by nox inherits nox's environment — not the per-package `.env`. Without `PROJECT_ROOT` set, the file URL resolves to `file:///dist` which doesn't exist, causing lock resolution failure.

### Change Made

`noxfile.py:57`:
- Added `env={"PROJECT_ROOT": str(ROOT)}` to all `session.run("pipenv", ...)` calls in the `tests()` session
- `ROOT` is `Path(__file__).resolve().parent` — the project root
- This ensures pipenv sees the correct `PROJECT_ROOT` for `file://` source resolution

### Gotchas

1. **`scripts_tests` session unaffected**: The `scripts_tests` session doesn't use pipenv with `file://` sources — it runs tests directly. No fix needed.
2. **`env` parameter is nox-specific**: The `session.run(..., env=...)` injection is the correct way to pass env vars to subprocesses in nox. Setting `os.environ` in the session function has no effect on subprocesses.

---

## Entry 6 — Test Results

**Date**: 2026-06-21 11:55

**Status**: ✅ All 8 nox sessions pass

### Test Results

| Test Suite | Command | Result |
|-----------|---------|--------|
| All tests | `nox -s all_tests` | ✅ All 8 sessions pass |
| Arduino gRPC | `nox -s arduino_grpc` | ✅ Passed |
| Board manager | `nox -s board_manager` | ✅ Passed |
| Board manager client | `nox -s board_manager_client` | ✅ Passed |
| Arduino sketch tools | `nox -s arduino_sketch_tools` | ✅ Passed |
| Arduino dash | `nox -s arduino_dash` | ✅ Passed |
| Medminder dash | `nox -s medminder_dash` | ✅ Passed |
| Scripts tests | `nox -s scripts_tests` | ✅ Passed |

**Total duration**: ~3 minutes

### Verification Notes

- All 8 sessions pass with zero failures
- Previous pipenv lock failures (Phase 97 era) are resolved by the noxfile fix
- No new test regressions introduced
- Manual verification of compile progress bar OOB via WS broadcast confirmed working

---

## Entry 7 — Implementation Summary

**Date**: 2026-06-21 11:55

**Status**: ✅ Phase 98 complete

### Summary

Phase 98 successfully migrated all PubSub-driven frontend updates from HTMX polling to WS push:

| Tier | Feature | Before | After |
|------|---------|--------|-------|
| 1 | Daemon badge | HTMX poll every 10s | WS push OOB on state change |
| 1 | Board status badge | HTMX poll every 10s | WS push OOB on board event |
| 2 | Compile output | WS-delivered but invisible | OOB targeted to output container |
| 2 | Upload output | WS-delivered but invisible | OOB targeted to output container |
| 3 | Compile progress | No progress bar | `<progress>` OOB + `[N%]` prefix |

### Key Metrics

| Metric | Value |
|--------|-------|
| Periodic polls eliminated | 2 (daemon badge + board status badge) |
| WS message types added | 3 (daemon OOB, badge OOB, progress bar OOB) |
| Signatures changed | `compile_stream()` 3-tuple → 4-tuple |
| gRPC fields used | `TaskProgress.percent` from `CompileResponse` |
| Files modified | ~12 source + 2 template groups |

### Files Modified

| File | Q | Change |
|------|---|--------|
| `arduino_dash/pubsub.py` | 1,2 | `_broadcast_daemon_badge()`, board badge OOB |
| `medminder_dash/pubsub_infra.py` | 1,2 | Same as above |
| Both `base.html` | 1 | `hx-trigger="every 10s, load"` → `"load"` |
| Both `daemon_badge.html` | 1 | Stripped hx-* attributes |
| Both `board_status_badge.html` | 2 | Stripped hx-* attributes |
| Both `board_detail.html` | 2,4 | Unique badge IDs, progress bar |
| `arduino_sketch_tools/extension.py` | 3,4 | OOB targeting, progress tracking |
| `arduino_grpc/client.py` | 4 | 4-tuple compile_stream() |
| `board_manager/board_worker.py` | 4 | `_make_progress()` with percent |
| `noxfile.py` | 5 | `env={"PROJECT_ROOT": str(ROOT)}` |

---
## Entry 5 — Phase 95: Git Tree Preparation Plan

**Date**: 2026-06-20 15:40

**Status**: ✅ Complete

**Trigger**: Pre-commit audit revealed stale generated artifacts, missing `.gitignore` entries, stale workflow docs (Phase 93→94 gap), and doc inaccuracies.

**Quantums**:
1. **Q1 — Clean stale artifacts**: Removed stale upload sketches from working tree; updated `.gitignore` with new patterns; created `.gitkeep` markers for empty directories.
2. **Q2 — Fix stale workflow docs**: Filled the Phase 93→94 gap across 5 IMPLEMENTATION_* files that were out of sync after Phase 94's noxfile changes.
3. **Q3 — Fix false `--help` claim**: `scripts/docs/index.md` claimed `ci.sh --help` outputs help text, but the script actually outputs usage information. Fixed the doc to match actual behavior.
4. **Q4 — Sequential staging**: Staged files in logical groups with user approval per group to avoid accidental commits of unrelated changes.
5. **Q5 — WS_EVENT_FLOW.md relocation**: Moved `WS_EVENT_FLOW.md` → `docs/ws-event-flow.md`; updated all cross-references in documentation and table of contents.

**Files changed**: `.gitignore`, `scripts/docs/index.md`, `WS_EVENT_FLOW.md` (moved), `docs/ws-event-flow.md` (new), various `.gitkeep` files, 5 IMPLEMENTATION_* workflow docs.

---
## Entry 6 — Phase 96: Wire test_ci.sh into Nox scripts_tests

**Date**: 2026-06-20 20:03

**Status**: ✅ Complete

**Type**: Infrastructure — test automation wiring

**Background**: `scripts/tests/test_ci.sh` was written to validate `scripts/ci.sh` with 10 scenarios (file existence, bash syntax, `--help`, unknown flags, nox-not-found guard, `--skip-builds`, `--skip-tests`, both skip flags, test failure exit 2, build failure exit 3). It uses a fake `nox` shim in a temp dir and has zero external dependencies beyond bash. Previously it was only runnable manually — not wired into the nox pipeline.

**Changes Made**:
- `noxfile.py` — added `session.run("bash", "tests/test_ci.sh", external=True)` to the `scripts_tests` session, after the existing `test_install_arduino_deps.sh` call.

**Verification**:
- Standalone: `bash scripts/tests/test_ci.sh` — 30/30 assertions pass ✅
- Integration: `nox -s scripts_tests` — 128 pytest + 12 bash (`test_install_arduino_deps.sh`) + 30 bash (`test_ci.sh`) = 170 total in 24s ✅

**Gotchas**: None. The script uses `BASH_SOURCE` for path resolution, so it works from any CWD (including nox's `chdir` to `scripts/`).

---
## Entry 7 — Phase 98 Q6: Rename TestAdminBoardSelectorPolling → TestAdminBoardSelector

**Date**: 2026-06-21

**Status**: ✅ Complete

**Type**: Cosmetic rename (Phase 98 Quantum 6)

**Background**: The `TestAdminBoardSelectorPolling` class was created in Phase 62.2 to verify `hx-trigger="load, every 5s"` polling on the admin board selector. In Phase 71, the trigger was changed to `board-changed from:body` (WS push), making the "Polling" suffix a stale misnomer. The tests were already accurate — only the name was misleading. This rename is included as an additional quantum within Phase 98 (WS Push Migration) since that phase eliminated the polling behavior that the suffix referred to.

**Changes Made**:
- `medminder_dash/tests/test_admin.py:811` — `class TestAdminBoardSelectorPolling` → `class TestAdminBoardSelector`; docstring updated to reflect WS push behavior from Phase 71
- `medminder_dash/README.md:205` — `TestAdminBoardSelectorPolling` → `TestAdminBoardSelector`

**Verification**:
- `nox -s 'tests(medminder_dash)' -- -k 'TestAdminBoardSelector' -v`: 3 tests collected and pass ✅
- `nox -s 'tests(medminder_dash)'`: 186 passed, 1 skipped (5.09s) ✅
- No stale `TestAdminBoardSelectorPolling` references in source code ✅

**Gotchas**: `.egg-info/PKG-INFO` and `.pytest_cache/` contain stale references — these are auto-generated and rebuild on next install/test run.
---

## Phase 99 — HTML Template Homogenisation Across Both Dashboards

**Date**: 2026-06-22 12:43
**Status**: ✅ Complete

**Goal**: Make all 14 shared templates structurally identical, extracting medicine-specific sections into separate partials and using template variables for route-path divergence.

### Q1 — board_detail.html homogenisation

**Changes made:**

**arduino_dash `board_detail.html`:**
1. Removed `<form id="compile-form">` wrapper (was `onsubmit="return false" method="post" enctype="multipart/form-data"`)
2. Moved FQBN/Port `.flex-row-wide` block above the sketch selector section
3. Changed compile/upload buttons `hx-include="#compile-form"` → `hx-include="#sketch_path, #fqbn"`
4. Added `href="/admin"` Admin Page button in the flex-row action bar
5. Changed `board_info.get('hardware_id', '')` → `(board_info or {}).get('hardware_id', '')` (defensive)
6. Changed `board_info.get('fqbn', ...)` → `(board_info or {}).get('fqbn', ...)` (defensive)
7. Added `show_sketch_tools` and `show_medicines_section` guards

**medminder_dash `board_detail.html`:**
1. Replaced hidden `<input id="sketch_path" value="{{ sketch_path }}">` with htmx `/last-upload` container:
   ```html
   <div id="sketch-path-container" class="container-grow"
       hx-get="/last-upload"
       hx-trigger="load"
       hx-target="this"
       hx-swap="innerHTML"
       hx-include="#active-board-hardware-id">
   </div>
   ```
2. Added `#active-board-hardware-id` hidden input
3. Guarded DnD overlay, Browse button, Delete button, and both modals (sketch_upload_modal, delete_confirm_modal) behind `{% if show_sketch_tools %}`
4. Added `{% if show_medicines_section %}` guard around `{% include "partials/medicine_management.html" %}`
5. FQBN changed to defensive `(board_info or {}).get('fqbn', ...)`

**New file created:** `medminder_dash/.../templates/partials/medicine_management.html`
- Contains the Medicines card (Add Medicine button, medicine-form-container, medicine-list with hx-get="/medicines")
- Included from board_detail.html behind `{% if show_medicines_section %}` guard

**Route context changes:**
- `arduino_dash/html_routes.py:109` — `board_detail()` now passes `show_sketch_tools=True, show_medicines_section=False`
- `medminder_dash/html_routes.py:712` — `board_detail()` now passes `show_sketch_tools=False, show_medicines_section=True`

### Q2 — admin.html homogenisation

**arduino_dash changes:**
- Added `active_board_sketch = ""` variable in `admin()` route
- Added `get_assignment()` lookup: `if active_board_hardware_id: active_board_sketch = get_assignment(...) or ""`
- Passed `active_board_sketch` in `render_template` context
- Added `assigned-sketch-info` div:
  ```html
  {% if active_board_hardware_id and active_board_sketch %}
  <div class="assigned-sketch-info">
      &#9889; Assigned to selected board: <code>{{ active_board_sketch }}</code>
  </div>
  {% endif %}
  ```

**medminder_dash changes:**
- Extracted medicine management "Step 1: Set Medicines" card (admin.html lines 65-105) to new partial `partials/admin_medicine_section.html`
- Replaced extracted block with `{% include "partials/admin_medicine_section.html" %}`

### Q3 — admin_board_selector.html homogenisation

Both partials now identical. Route-dependent attributes passed as template variables from Python route handlers:

| Variable | arduino_dash | medminder_dash |
|----------|-------------|----------------|
| `board_selector_label` | `"Active Board (for compile and upload)"` | `"Active Board (for medicine management, compile, and upload)"` |
| `board_selector_hx_post` | `"/admin/active-board"` | `"/medicines/active-board"` |
| `board_selector_hx_target` | `"#compile-upload-card"` | `"#medicine-cards-container"` |
| `board_selector_hx_swap` | `"innerHTML"` | `"outerHTML"` |

Route handler changes:
- `arduino_dash html_admin_board_selector()` (html_routes.py:209): passes 4 board_selector variables
- `medminder_dash html_medicines_board_selector()` (html_routes.py:496): passes 4 board_selector variables

### Q4 — compile_upload_card.html homogenisation

Both files now identical:
- arduino_dash: added `Step 2:` / `Step 3:` prefixes to card section titles
- medminder_dash: changed "Compile the MedMinderV2 sketch..." → "Compile the selected sketch..."
- medminder_dash: changed Unicode `…` → HTML entity `&#8230;`

### T1-T3 — Trivial diff fixes

| # | File | Fix |
|---|------|-----|
| T1 | `medminder_dash/.../partials/dnd_overlay.html` | Added trailing `\n` after `</script>` (was 0 trailing newlines, now 1 — matches arduino_dash) |
| T2 | `arduino_dash/.../partials/board_card.html:4` | `b.get('board', 'Unknown')` → `b.get('board', 'Unknown') or 'Unknown'` |
| T3 | `medminder_dash/.../partials/delete_confirm_modal.html:9` | Added `hardware_id: ...` to `hx-vals` |

### Q6 — base.html DnD listeners

Added to medminder_dash `base.html` (before existing click listener):
```js
document.addEventListener('dragover', function(e) { e.preventDefault(); });
document.addEventListener('drop', function(e) { e.preventDefault(); });
```
Matches arduino_dash `base.html:76-77`.

### Shared SketchRegistry Extraction (post-plan addition)

**Motivation**: Enabling the `assigned-sketch-info` block in arduino_dash required `get_board_sketch_assignment()`, which was previously only available in medminder_dash. Rather than duplicating code or creating a cross-package import, the shared logic was extracted to `arduino_sketch_tools`.

**New file:** `arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/sketch_registry.py`
- `SketchRegistry` class accepts `registry: dict` and `lock: threading.Lock` at init
- Methods: `get_assignment()`, `set_assignment()`, `clear_assignment()`, `get_all_assignments()`, `reset_for_tests()`
- Thread-safe: uses instance-level `_op_lock` then acquires the registry `_lock`
- Logic identical to the original per-app modules (same triple-nested loop over upload_registry structure)

**Updated:** `arduino_sketch_tools/__init__.py` — exports `SketchRegistry`

**Updated per-app wrappers:**
- `arduino_dash/.../sketch_registry.py` (73→10 lines): creates `SketchRegistry(state._upload_registry, state._upload_registry_lock)` and re-exports bound methods
- `medminder_dash/.../sketch_registry.py` (93→10 lines): same pattern

**Build:** `arduino_sketch_tools` wheel rebuilt via `nox -s 'build(arduino_sketch_tools)'`; both Pipfile.locks updated via `PROJECT_ROOT=... pipenv lock`

### Deviations from Plan

1. **Q2/Q3 implementation route**: Original plan specified `{% set %}` template variables in `admin.html` for board_selector attributes. Implemented as Python `render_template` kwargs from route handlers instead. This keeps the template simpler and avoids the `{% set %}` scope issue (variables set in the parent template don't propagate to htmx-loaded partials).

2. **Shared SketchRegistry**: Not in the original plan. Added when Q2a required `active_board_sketch` in arduino_dash and neither code duplication nor cross-package import was acceptable.

### Verification

| Command | Result |
|---------|--------|
| `nox -s 'tests(arduino_dash)'` | 119 passed, 0 failed |

---

## Entry 2 — Phase 100: Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14
**Status**: ✅ Complete

### Goal

Make `e2e/servers/arduino_dash_server.py` and `medminder_dash_server.py` survive the bash tool's shell exit without requiring `&`, `&>/dev/null`, `disown`, or special timeouts. Add `--pidfile`, `--stop`, `--force`, `--logfile` flags.

### Problem

The bash tool tracks processes by session. When a shell command times out or exits, the tool sends SIGHUP to all processes in the session. The previous workaround (`&>/dev/null & disown` with `timeout=3000`) relied on a race condition.

### Architecture Evolution

Three iterations before arriving at the final design:

| Iteration | Approach | Problem |
|-----------|----------|---------|
| 1 | `os.setpgid(0, 0)` + `disown` | User wants no shell hacks |
| 2 | `os.setpgid(0, 0)` + `_redirect_io()` — no fork | `setpgid` changes PGID but not session; tool still tracks and kills via session |
| 3 (final) | `os.fork()` + `os.setsid()` + `_redirect_io()` | **Works** — parent exits → tool returns; child in new session, immune; stdout/stderr redirected to logfile |

### Final Architecture

```
bash tool (session leader)
  │ SIGHUP on exit (to session's PGID)
  └── bash (shell session)
        └── python3 (our script)
              ├── fork
              ├── parent: os._exit(0) ──▶ bash exits ──▶ tool returns
              └── child: os.setsid() ──▶ new session, immune to SIGHUP
                    ├── _redirect_io(logfile) ──▶ stdout/stderr → file
                    ├── Flask runs
                    └── logs captured in --logfile
```

Key insight: `os.setpgid(0, 0)` changes process GROUP but not SESSION. The tool tracks processes by SESSION. When the session leader (bash) dies, the kernel sends SIGHUP to ALL processes in that session, regardless of process group. Only `os.setsid()` (which requires a fork) creates a new session.

### Changes per file

**Both `arduino_dash_server.py` and `medminder_dash_server.py`**:

| Component | Change |
|-----------|--------|
| Imports | Added `import signal`, `import time` |
| `_get_default_pidfile()` | New — derives path from script name |
| `_write_pidfile()` | New — writes PID to file |
| `_remove_pidfile()` | New — safe removal (checks PID matches) |
| `_stop_server()` | New — SIGTERM → 5s poll → SIGKILL; handles stale PID |
| `_daemonize(logfile)` | New — fork + setsid + redirect |
| `--pidfile` arg | New — custom PID path |
| `--stop` arg | New — shutdown via pidfile |
| `--force` arg | New — immediate SIGKILL |
| `--logfile` arg | New — Flask log capture |
| `main()` order | --stop before daemonize |
| Docstring | Updated with new usage examples |

### Stale PID handling

A second server instance that fails to start (e.g., port in use) could delete the first instance's pidfile in its `finally` block. Fixed: `_remove_pidfile()` verifies the pidfile still contains OUR PID before deleting.

Similarly, `--stop` handles stale PIDs gracefully: if `os.kill()` raises `ProcessLookupError`, it cleans up the pidfile and exits with status 0.

### Verification

| Test | Commands | Result |
|------|----------|--------|
| arduino_dash survival | `python3 script.py --mock --production` then `curl` | ✅ HTTP 200 |
| arduino_dash log | `--logfile /tmp/x.log` | ✅ 571 bytes captured |
| arduino_dash --stop | `python3 script.py --stop` | ✅ "Stopped PID X" |
| medminder_dash survival | Same pattern | ✅ HTTP 200 |
| medminder_dash log | `--logfile /tmp/x.log` | ✅ 649 bytes captured |
| medminder_dash --stop | `python3 script.py --stop` | ✅ "Stopped PID X" |
| Stale PID handling | `--stop` on non-existent PID | ✅ Cleaned up pidfile |
| No shell hacks | No `&`, `disown`, `&>/dev/null`, or timeout tricks | ✅ |
| `nox -s 'tests(medminder_dash)'` | 186 passed, 1 skipped |

---
{% endraw %}
