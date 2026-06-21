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
{% endraw %}
