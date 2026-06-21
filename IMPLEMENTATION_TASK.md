---
---
{% raw %}
# Implementation Task — Phase 98: WS Push Migration (Badge OOB → Compile/Upload OOB → Compile Progress Bar)

**Date**: 2026-06-21 11:55 | **Completed**: 2026-06-21 11:55 (Q1-Q5); Q6 added 2026-06-21

## Current Task

Phase 98: Q1-Q5 complete. Q6 (rename) complete.

### Task Breakdown

| # | Task | Status |
|---|------|--------|
| 1 | Tier 1 — Daemon badge OOB | ✅ Done |
| 2 | Tier 1 — Board status badge OOB | ✅ Done |
| 3 | Tier 2 — Compile/upload OOB targeting | ✅ Done |
| 4 | Tier 3 — Compile progress percentage | ✅ Done |
| 5 | Noxfile PROJECT_ROOT fix | ✅ Done |
| 6 | Rename TestAdminBoardSelectorPolling → TestAdminBoardSelector | ✅ Done |

### Detailed Tasks

#### Q1 — Daemon Badge OOB

- [x] Both `base.html`: `hx-trigger="every 10s, load"` → `"load"` (one-shot initial fill)
- [x] Both `daemon_badge.html`: strip `hx-get`, `hx-trigger`, `hx-target`, `hx-swap` (plain HTML fragment)
- [x] `arduino_dash/pubsub.py`: add `_broadcast_daemon_badge()` method, call from `_on_daemon_ready()` and `_on_pubsub_reconnect()`
- [x] `medminder_dash/pubsub_infra.py`: same changes

#### Q2 — Board Status Badge OOB

- [x] Both `board_status_badge.html`: strip all `hx-*` attributes
- [x] Both `board_detail.html`: `id="board-status-badge"` → `id="board-status-badge--{{ port | replace('/', '_') }}"`
- [x] Both `board_detail.html`: `hx-trigger="every 10s, load"` → `"load"`
- [x] `arduino_dash/pubsub.py` `_on_board_event()`: add badge OOB WS broadcast after event-feed broadcast
- [x] `medminder_dash/pubsub_infra.py` `_on_board_event()`: same addition

#### Q3 — Compile/Upload OOB Targeting

- [x] `extension.py:182` compile line: wrap in `<span hx-swap-oob="beforeend:#compile-output-{port_safe}">`
- [x] `extension.py:214` upload line: wrap in `<span hx-swap-oob="beforeend:#upload-output-{port_safe}">`

#### Q4 — Compile Progress Percentage

- [x] `client.py:compile_stream()`: yield 4-tuple `(out, err, done, percent)`, track last `percent` from `resp.progress.percent`, set 100.0 on done
- [x] `board_worker.py:_make_progress()`: accept `percent: float = 0.0`, include `"percent"` in data dict; compile handler unpacks 4-tuple, sends progress-only messages on percent change
- [x] `extension.py:_on_compile_resp()`: read `percent` from data; track `_compile_last_pct` per port_safe; broadcast `<progress id="compile-progress-{port_safe}">` OOB on change; prepend `[N%]` prefix to output text
- [x] Both `board_detail.html`: add `<progress id="compile-progress-{port_safe}" value="0" max="100">` before compile output div
- [x] Update all callers of 3-tuple `compile_stream()` to handle 4-tuple

#### Q5 — Noxfile PROJECT_ROOT Fix

- [x] `noxfile.py`: add `env={"PROJECT_ROOT": str(ROOT)}` to all pipenv calls in `tests()` session
- [x] Verify `scripts_tests` unaffected

#### Q6 — Rename TestAdminBoardSelectorPolling → TestAdminBoardSelector

- [x] `test_admin.py:811`: `class TestAdminBoardSelectorPolling` → `class TestAdminBoardSelector`
- [x] Update class docstring: remove "polls every 5s" language, replace with "refreshes via WS push on board-changed events"
- [x] `README.md:205`: `TestAdminBoardSelectorPolling` → `TestAdminBoardSelector`
- [x] Run `nox -s 'tests(medminder_dash)' -- -k 'TestAdminBoardSelector' -v` — 3 tests collected and pass
- [x] Verify no stale `TestAdminBoardSelectorPolling` references in code (grep)
{% endraw %}
