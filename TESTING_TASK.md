---
---
{% raw %}
# Testing Task — Phase 93: GitHub Pages Jekyll Documentation Site

**Status**: ✅ COMPLETED — All 10 quantums verified.

| Q | Test | Result |
|---|------|--------|
| Q1-Q2 | Config + Gemfile — `bundle exec jekyll build` exit 0 | ✅ Exit 0, build succeeds |
| Q3-Q4 | Front matter + raw/endraw — no Liquid errors | ✅ 0 errors |
| Q5 | Broken links — grep href targets | ✅ All 51 fixed links resolve to `.html` |
| Q6 | Initial build — 246 HTML pages | ✅ 0 errors |
| Q7 | RESEARCH docs raw/endraw — Liquid warnings | ✅ 0 warnings (4 eliminated) |
| Q8 | README front matter — hrefs resolve to `.html` | ✅ All 8 README `.md` → `.html` |
| Q9 | index.md README links — 9 hrefs verified | ✅ 9 README hrefs in `_site/index.html` |
| Q10 | Final build — 0 errors 0 warnings, 254 pages | ✅ |

---

# Testing Task — Phase 95: Git Tree Preparation Plan

**Status**: ✅ COMPLETED — All 5 quantums verified.

| Q | Test | Result |
|---|------|--------|
| Q1 | Stale upload sketches removed — `ls _uploads` empty | ✅ |
| Q1 | .gitignore updated — `git status` shows only intended files | ✅ |
| Q1 | .gitkeep markers in empty data dirs — `find ... -name '.gitkeep'` | ✅ |
| Q2 | Workflow docs gap (Phase 93→94) filled — grep 5 files | ✅ |
| Q3 | `scripts/docs/index.md --help` claim fixed — `usage` present | ✅ |
| Q4 | Sequential git add — user approved each group | ✅ |
| Q5 | WS_EVENT_FLOW.md → `docs/ws-event-flow.md` — moved + cross-refs updated | ✅ |

---

# Testing Task — Phase 96: Wire test_ci.sh into Nox scripts_tests

**Status**: ✅ COMPLETED

| # | Test | Result |
|---|------|--------|
| 1 | Standalone `bash scripts/tests/test_ci.sh` — 30/30 pass | ✅ |
| 2 | `nox -s scripts_tests` — 128 pytest pass | ✅ |
| 3 | `nox -s scripts_tests` — 12 bash (test_install_arduino_deps) pass | ✅ |
| 4 | `nox -s scripts_tests` — 30 bash (test_ci.sh) pass | ✅ |
| 5 | `nox -s scripts_tests` — 170 total, all pass in 24s | ✅ |

---

# Testing Task — Phase 98: WS Push Migration (Badge OOB → Compile/Upload OOB → Compile Progress Bar)

**Status**: ✅ COMPLETED

## Completed Tasks

| Q | Task | Status | Actual Result |
|---|------|--------|---------------|
| Q1 | Daemon badge — verify base.html hx-trigger = "load" | ✅ | `hx-trigger="every 10s, load"` → `"load"` in both base.html |
| Q1 | Daemon badge — verify partial stripped of hx-* | ✅ | daemon_badge.html: 0 hx-* attributes |
| Q1 | Daemon badge — verify pubsub _broadcast_daemon_badge() | ✅ | Method present in both arduino_dash/pubsub.py and medminder_dash/pubsub_infra.py |
| Q2 | Board badge — verify partial stripped of hx-* | ✅ | board_status_badge.html: 0 hx-* attributes |
| Q2 | Board badge — verify unique per-port IDs | ✅ | `id="board-status-badge--{{ port \| replace('/', '_') }}"` in both board_detail.html |
| Q2 | Board badge — verify pubsub OOB broadcast | ✅ | Badge OOB broadcast in `_on_board_event()` in both dashboards |
| Q3 | Compile OOB — verify hx-swap-oob targeting | ✅ | `<span hx-swap-oob="beforeend:#compile-output-{port_safe}">` in extension.py:182 |
| Q3 | Upload OOB — verify hx-swap-oob targeting | ✅ | `<span hx-swap-oob="beforeend:#upload-output-{port_safe}">` in extension.py:214 |
| Q4 | compile_stream() 4-tuple — verify all callers updated | ✅ | client.py, board_worker.py, tests all updated |
| Q4 | Progress bar — verify element in templates | ✅ | `<progress id="compile-progress-{port_safe}">` in both board_detail.html |
| Q4 | Progress bar — verify _compile_last_pct tracking | ✅ | Dict per port_safe tracks last broadcast percent |
| Q4 | [N%] prefix — verify prepended to output lines | ✅ | extension.py prepends `[N%]` before output text |
| Q5 | Noxfile — verify PROJECT_ROOT env added | ✅ | `env={"PROJECT_ROOT": str(ROOT)}` in noxfile.py |
| Q6 | Rename class in test_admin.py:811 | ✅ | `TestAdminBoardSelectorPolling` → `TestAdminBoardSelector` |
| Q6 | Class docstring updated | ✅ | References Phase 71 WS push instead of Phase 62.2 polling |
| Q6 | README.md:205 reference updated | ✅ | `TestAdminBoardSelectorPolling` → `TestAdminBoardSelector` |
| Q6 | All medminder_dash tests pass | ✅ | 186 pass, 1 skip (no regression) |
| Q6 | No stale `TestAdminBoardSelectorPolling` in source | ✅ | Only in auto-generated `.egg-info` and `.pytest_cache` |
| All | All 8 nox sessions pass | ✅ | No pre-existing failures — all green |
{% endraw %}
