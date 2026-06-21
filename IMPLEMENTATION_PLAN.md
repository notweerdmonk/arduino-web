---
---
{% raw %}
# Implementation Plan — Phase 98: WS Push Migration (Badge OOB → Compile/Upload OOB → Compile Progress Bar)

**Date**: 2026-06-21 11:55

**Status**: IMPLEMENTED — 5 quantums original; 1 additional quantum (Q6).

---

## Motivation

Two periodic HTMX polls (`every 10s`) remain after Phase 97's frontend stack optimization: the daemon status badge in `base.html` and the board connection status badge in `board_detail.html`. These produce unnecessary HTTP requests on every page. Meanwhile, compile/upload progress is already pushed via WebSocket but rendered invisibly (no `hx-swap-oob` targeting). By using OOB HTML fragments over WS for badge updates and compile/upload output, we eliminate polling entirely and make existing WS-delivered content visible without extra HTTP round-trips.

## Architecture

### Before
```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  base.html      │ ──> │ /daemon/     │     │ Daemon Badge│
│  hx-trigger="   │     │ status       │ <── │ Partial     │
│  every 10s,load"│     └──────────────┘     └─────────────┘
└─────────────────┘
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│ board_detail    │ ──> │ /board/<port>│     │ Board Status│
│ .html           │     │ /connection- │ <── │ Badge       │
│ hx-trigger="    │     │ status       │     │ Partial     │
│ every 10s,load" │     └──────────────┘     └─────────────┘
└─────────────────┘
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│ WS Compile Line │ ──> │ WS -> HTMX   │     │ Invisible   │
│ (from BMS)      │     │ htmx:wsBefore│     │ (no OOB)    │
└─────────────────┘     └──────────────┘     └─────────────┘
```

### After
```
┌─────────────────┐     ┌─────────────────────────────┐
│ PubSub OOB      │ ──> │ WS broadcast with           │
│ Daemon Badge    │     │ hx-swap-oob="true"           │
└─────────────────┘     └─────────────────────────────┘
┌─────────────────┐     ┌─────────────────────────────┐
│ PubSub OOB      │ ──> │ WS broadcast with badge     │
│ Board Badge     │     │ HTML + OOB targeting        │
└─────────────────┘     └─────────────────────────────┘
┌─────────────────┐     ┌─────────────────────────────┐
│ WS Compile Line │ ──> │ hx-swap-oob="beforeend:     │
│ (from BMS)      │     │ #compile-output-{port_safe}"│
└─────────────────┘     └─────────────────────────────┘
┌─────────────────┐     ┌─────────────────────────────┐
│ WS Progress Bar │ ──> │ <progress> element OOB      │
│ (percent change)│     │ + [N%] prefix per line      │
└─────────────────┘     └─────────────────────────────┘
```

## Quantums

### Quantum 1 — Daemon Badge OOB (Tier 1)

**Goal**: Replace HTMX polling for the daemon status badge with WS push via OOB HTML.

**Files changed**:
- Both `templates/base.html` — `hx-trigger="every 10s, load"` → `"load"` (one-shot initial fill)
- Both `templates/partials/daemon_badge.html` — strip `hx-get`, `hx-trigger`, `hx-target`, `hx-swap` (rendered as plain HTML fragment)
- `arduino_dash/python/.../pubsub.py` — add `_broadcast_daemon_badge()`, call from `_on_daemon_ready()` and `_on_pubsub_reconnect()`
- `medminder_dash/python/.../pubsub_infra.py` — same changes

### Quantum 2 — Board Status Badge OOB (Tier 1)

**Goal**: Replace HTMX polling for the board connection status badge with WS push.

**Files changed**:
- Both `templates/partials/board_status_badge.html` — strip all `hx-*` attributes
- Both `templates/board_detail.html` — `id="board-status-badge"` → `id="board-status-badge--{{ port | replace('/', '_') }}"` (unique per port); `hx-trigger="every 10s, load"` → `"load"`
- Both pubsub modules — `_on_board_event()` adds badge OOB WS broadcast after event-feed broadcast

### Quantum 3 — Compile/Upload OOB Targeting (Tier 2)

**Goal**: Make existing WS-delivered compile/upload progress lines visible by adding `hx-swap-oob` targeting.

**Files changed**:
- `arduino_sketch_tools/extension.py:182` — compile progress line: wrap in `<span hx-swap-oob="beforeend:#compile-output-{port_safe}">`
- `arduino_sketch_tools/extension.py:214` — upload progress line: wrap in `<span hx-swap-oob="beforeend:#upload-output-{port_safe}">`

### Quantum 4 — Compile Progress Percentage (Tier 3)

**Goal**: Add real-time compile progress bar via `<progress>` element OOB over WS, plus `[N%]` prefix per output line.

**Files changed**:
- `arduino_grpc/client.py:compile_stream()` — yields 4-tuple `(out, err, done, percent)`; tracks last `percent` from `resp.progress.percent`; sets 100.0 on done
- `board_manager/board_worker.py:_make_progress()` — accepts `percent: float = 0.0`; includes `"percent"` in data dict; compile handler unpacks 4-tuple, sends progress-only messages on percent change
- `arduino_sketch_tools/extension.py:_on_compile_resp()` — reads `percent` from data; tracks `_compile_last_pct` per port_safe; broadcasts `<progress id="compile-progress-{port_safe}" value="{pct}" max="100">` OOB on change; prepends `[N%]` prefix to output text
- Both `board_detail.html` — add `<progress id="compile-progress-{port_safe}" value="0" max="100">` before compile output div

### Quantum 5 — Noxfile Fix

**Goal**: Fix `file://${PROJECT_ROOT}` expansion failure in pipenv calls within nox sessions.

**Files changed**:
- `noxfile.py:57` — added `env={"PROJECT_ROOT": str(ROOT)}` to all pipenv calls in `tests()` session

### Quantum 6 — Rename TestAdminBoardSelectorPolling → TestAdminBoardSelector

**Goal**: Rename stale test class `TestAdminBoardSelectorPolling` to `TestAdminBoardSelector`. The class was created in Phase 62.2 to verify `hx-trigger="load, every 5s"` polling behavior on the admin board selector, but was updated in Phase 71 to use WS push (`board-changed from:body`). The "Polling" suffix became a stale misnomer — the tests were already correct, only the name was misleading.

**Files changed**:
- `medminder_dash/tests/test_admin.py:811` — `class TestAdminBoardSelectorPolling` → `class TestAdminBoardSelector`; docstring updated to reflect Phase 71 WS push behavior instead of Phase 62.2 polling
- `medminder_dash/README.md:205` — `TestAdminBoardSelectorPolling` → `TestAdminBoardSelector` (class reference in doc index)

**Test impact**: No functional change. Pure rename — 0 test delta. The class is discovered by pytest via its name; all 3 test methods and their assertions are unaffected.

**Verification**:
| Check | Command | Result |
|-------|---------|--------|
| Renamed class discovered | `nox -s 'tests(medminder_dash)' -- -k 'TestAdminBoardSelector' -v` | 3 tests collected and pass |
| No stale reference errors | `grep -rn 'TestAdminBoardSelectorPolling' medminder_dash/` | 0 matches in code (except archival in docs) |
| All medminder_dash tests pass | `nox -s 'tests(medminder_dash)'` | 186 pass, 1 skip |

## Key Design Decisions

1. **OOB HTML over WS** — Direct HTML fragments with `hx-swap-oob` over WS eliminates the need for extra HTTP round-trips. Proven pattern from existing board event pushes.
2. **Per-port badge IDs** — `board-status-badge--{port_safe}` ensures board_detail pages with multiple boards (theoretical) get correct badge updates.
3. **Strip hx-* from partials** — Partials rendered as plain HTML; no need for `hx-trigger="load"` when the wrapper span's `hx-trigger="load"` handles initial AJAX fill.
4. **Clean break for 4-tuple** — `compile_stream()` yields `(out, err, done, percent)` instead of 3-tuple. All callers updated: `compile()`, `board_worker`, tests.
5. **Upload remains 3-tuple** — `UploadResponse` has no `TaskProgress` at the gRPC level.
6. **Track `_compile_last_pct`** — Only broadcast progress bar OOB when the percent value changes, avoiding redundant WS pushes.
7. **Progress-only messages** — Board worker sends messages containing only percent (no output text) when only the progress bar advances.

## Verification

| Command | Result |
|---------|--------|
| `nox -s all_tests` | ✅ All 8 sessions pass (~3m) |
| `nox -s arduino_grpc` | ✅ Passes |
| `nox -s board_manager` | ✅ Passes |
| `nox -s arduino_dash` | ✅ Passes |
| `nox -s medminder_dash` | ✅ Passes |
| `nox -s arduino_sketch_tools` | ✅ Passes |
| `nox -s scripts_tests` | ✅ Passes |

## Relevant Files

| File | Line(s) | Change |
|------|---------|--------|
| `arduino_dash/.../templates/base.html` | 17 | daemon badge wrapper `hx-trigger="every 10s, load"` → `"load"` |
| `arduino_dash/.../templates/board_detail.html` | 17,85 | board badge id+trigger; compile progress bar |
| `arduino_dash/.../templates/partials/daemon_badge.html` | — | stripped of hx-* attributes |
| `arduino_dash/.../templates/partials/board_status_badge.html` | — | stripped of hx-* attributes |
| `arduino_dash/.../pubsub.py` | — | `_broadcast_daemon_badge()` + board badge OOB |
| `medminder_dash/.../pubsub_infra.py` | — | same as above |
| `medminder_dash/.../templates/board_detail.html` | 59 | compile progress bar added |
| `arduino_sketch_tools/.../extension.py` | 180,212 | compile/upload WS OOB targets; percent tracking + progress bar + `[N%]` prefix |
| `arduino_grpc/.../client.py` | 305 | `compile_stream()` yields 4-tuple with percent |
| `board_manager/.../board_worker.py` | 39,154 | `_make_progress()` with percent; compile progress-only messages |
| `noxfile.py` | 57 | `env={"PROJECT_ROOT": str(ROOT)}` added |
| `medminder_dash/tests/test_admin.py` | 811 | `class TestAdminBoardSelectorPolling` → `TestAdminBoardSelector` + docstring update |
| `medminder_dash/README.md` | 205 | `TestAdminBoardSelectorPolling` → `TestAdminBoardSelector` |
{% endraw %}
