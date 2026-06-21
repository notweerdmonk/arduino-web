---
---
{% raw %}
# Testing Plan — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

## Scope

Static analysis and build verification for Jekyll documentation site. No Python code changes — only config files, markdown content, and static file metadata (front matter).

## Test Strategy

| Quantum | What to Test | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| Q1-Q2 | Config fixes | `bundle exec jekyll build` | Exit 0, no "Liquid syntax error" |
| Q3-Q4 | Front matter + raw/endraw | `bundle exec jekyll build` | Exit 0, no syntax errors |
| Q5 | Broken links | `grep` href targets in `_site/` | All hrefs point to existing `.html` files |
| Q6 | Final build | `bundle exec jekyll build` | Exit 0, 0 errors, 0 warnings |
| Q7 | Liquid warnings | `bundle exec jekyll build 2>&1 | grep -i warning` | 0 warnings |
| Q8 | README files | `grep` href targets in `_site/index.html` | All README hrefs resolve to `.html` |
| Q9 | index.md README links | `grep -oP 'href="[^"]*README[^"]*"' _site/index.html` | 9+ README hrefs present |
| Q10 | Final build + page count | `find _site -name "*.html" | wc -l` | 254 HTML pages |

## Verification Steps

1. `bundle exec jekyll build` — exit 0, no errors, no warnings
2. `grep` spot-check all new href targets in `_site/index.html`
3. Verify README links resolve to `.html` (not `.md`)
4. Count total HTML pages (expect 254)
5. Verify nested subpackage doc directories exist in `_site/`

## Key Files to Verify

| File in _site | Expected | Verification |
|---------------|----------|--------------|
| `_site/index.html` | Documentation hub with README links | `grep` href README |
| `_site/board_manager/python/board_manager/board_manager/docs/` | 11 doc pages | `ls` directory |
| `_site/medminder_dash/python/medminder_dash/medminder_dash/docs/` | 15 doc pages | `ls` directory |
| `_site/README.html` | Processed README | File exists |
| All README `.html` files | Processed pages at expected paths | `find _site -name "README.html"` |

---

## Phase 95 — Git Tree Preparation Plan

**Date**: 2026-06-20 15:40
**Status**: ✅ COMPLETED — Git tree cleaned and staged.

### Test Strategy

No code changes — only file staging, `.gitignore` updates, doc fixes, and file moves. Verification is manual inspection and build smoke tests.

| Q | What to Test | Method | Pass Criteria | Status |
|---|-------------|--------|---------------|--------|
| 1 | Stale upload sketches removed | `ls _uploads/ 2>/dev/null` | No stale files | ✅ |
| 1 | .gitignore patterns correct | `git status --short` | No dirty generated-artifact entries | ✅ |
| 1 | .gitkeep markers present | `find */python/*/data -name '.gitkeep'` | All empty dirs have markers | ✅ |
| 2 | Workflow docs gap filled | `grep 'Phase 93\|Phase 94' IMPLEMENTATION_*.md` | Both phases referenced in sequence | ✅ |
| 3 | docs/index.md --help claim fixed | `grep -c 'usage' scripts/docs/index.md` | At least 1 usage reference present | ✅ |
| 4 | Sequential git add approved | Manual session log | User approved each group | ✅ |
| 5 | WS_EVENT_FLOW.md relocated | `test -f docs/ws-event-flow.md && test ! -f WS_EVENT_FLOW.md` | New path exists, old path gone | ✅ |
| 5 | All cross-refs updated | `grep -rn 'WS_EVENT_FLOW' * --include='*.md'` | All refs point to `docs/ws-event-flow.md` | ✅ |

---

## Phase 96 — Wire test_ci.sh into Nox scripts_tests

**Date**: 2026-06-20 20:03
**Status**: ✅ COMPLETED — test_ci.sh wired and verified.

### Test Strategy

| # | What to Test | Method | Pass Criteria | Status |
|---|-------------|--------|---------------|--------|
| 1 | Standalone test_ci.sh | `bash scripts/tests/test_ci.sh` | Exit 0, 30/30 pass | ✅ |
| 2 | pytest suite in scripts_tests | `nox -s scripts_tests` | 128 pytest pass | ✅ |
| 3 | test_install_arduino_deps.sh in scripts_tests | `nox -s scripts_tests` | 12 bash pass | ✅ |
| 4 | test_ci.sh in scripts_tests | `nox -s scripts_tests` | 30 bash pass | ✅ |
| 5 | scripts_tests total | `nox -s scripts_tests` | All 170 pass in 24s | ✅ |

---

## Phase 98 — WS Push Migration (Badge OOB → Compile/Upload OOB → Compile Progress Bar)

**Date**: 2026-06-21 11:55

**Status**: IMPLEMENTED — All tests executed.

## Scope

Migrate PubSub-driven frontend updates from HTMX polling to WS push across 3 tiers: daemon badge OOB, board status badge OOB, compile/upload OOB targeting, and compile progress percentage.

## Test Strategy — Actual Results

| Q | What to Test | Method | Pass Criteria | Result |
|---|-------------|--------|---------------|--------|
| 1 | Daemon badge — base.html hx-trigger updated | grep on base templates | `hx-trigger="every 10s, load"` not present | ✅ Changed to `"load"` |
| 1 | Daemon badge — partial stripped of hx-* | grep on daemon_badge.html | No `hx-get`, `hx-trigger`, `hx-target`, `hx-swap` | ✅ Stripped |
| 1 | Daemon badge — pubsub _broadcast_daemon_badge() | grep on pubsub modules | Method exists | ✅ Both dashboards |
| 2 | Board badge — partial stripped of hx-* | grep on board_status_badge.html | No hx-* attributes | ✅ Stripped |
| 2 | Board badge — unique per-port IDs | grep on board_detail.html | IDs contain `{{ port \| replace('/', '_') }}` | ✅ Present |
| 2 | Board badge — pubsub OOB broadcast | grep on pubsub modules | Badge OOB in `_on_board_event()` | ✅ Both dashboards |
| 3 | Compile/upload OOB targeting | grep on extension.py | `hx-swap-oob="beforeend:#...-output-{port_safe}"` | ✅ Present |
| 4 | compile_stream() 4-tuple | grep on client.py | Yields `(out, err, done, percent)` | ✅ Updated |
| 4 | Progress bar element in templates | grep on board_detail.html | `<progress id="compile-progress-"` | ✅ Present |
| 4 | _compile_last_pct tracking | grep on extension.py | Dict for per-port percent tracking | ✅ Present |
| 5 | Noxfile env fix | grep on noxfile.py | `env={"PROJECT_ROOT": str(ROOT)}` | ✅ Added |
| 6 | Rename TestAdminBoardSelectorPolling → TestAdminBoardSelector | `grep` on test_admin.py + README.md | Class renamed, docstring updated, README ref updated | ✅ Done |
| 6 | No stale references in code | `grep -rn 'TestAdminBoardSelectorPolling' medminder_dash/ --exclude-dir=.egg-info --exclude-dir=.pytest_cache` | 0 matches in source | ✅ Done |
| All | All nox sessions pass | `nox -s all_tests` | All 8 sessions pass | ✅ All pass |

## Automated Test Sessions

| Session | Command | Result | Details |
|---------|---------|--------|---------|
| Core pytest | `nox -s all_tests` | ✅ PASS | All 8 sessions pass |
| Arduino gRPC | `nox -s arduino_grpc` | ✅ PASS | Passed |
| Board manager | `nox -s board_manager` | ✅ PASS | Passed |
| Board manager client | `nox -s board_manager_client` | ✅ PASS | Passed |
| Arduino sketch tools | `nox -s arduino_sketch_tools` | ✅ PASS | Passed |
| Arduino dash | `nox -s arduino_dash` | ✅ PASS | Passed |
| Medminder dash | `nox -s medminder_dash` | ✅ PASS | Passed |
| Scripts tests | `nox -s scripts_tests` | ✅ PASS | Passed |

## Manual Verification Steps (performed, cannot run in automated CI)

1. `grep -rn 'every 10s' */templates/base.html` → 0 matches → periodic polling removed
2. `grep -rn 'hx-get' */templates/partials/daemon_badge.html` → 0 matches → partial stripped
3. `grep -rn 'hx-get' */templates/partials/board_status_badge.html` → 0 matches → partial stripped
4. `grep -rn 'hx-swap-oob="beforeend:#compile-output-' */extension.py` → matches → OOB targeting present
5. `grep -rn 'hx-swap-oob="beforeend:#upload-output-' */extension.py` → matches → OOB targeting present
6. `grep -rn 'compile-progress-' */board_detail.html` → matches → progress bar element present
{% endraw %}
7. `grep -rn 'percent' */client.py` → matches → 4-tuple with percent
