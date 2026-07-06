---
layout: default
---
{% raw %}
# Testing Progress — Phase 112: Jekyll Optional Front Matter Plugin

## Phase 112: Jekyll Optional Front Matter Plugin

| Test | Status | Notes |
|------|--------|-------|
| T1 — `bundle exec jekyll build` | ✅ | Exit code 0, no errors/warnings |
| T2 — `_site/README.html` exists | ✅ | Rendered HTML with layout |
| T3 — `_site/scripts/README.html` exists | ✅ | Rendered HTML with layout |
| T4 — `_site/e2e/README.html` exists | ✅ | Rendered HTML with layout |
| T5 — `_site/board_manager/python/board_manager/README.html` exists | ✅ | Rendered HTML with layout |
| T6 — `_site/medminder_dash/python/medminder_dash/README.html` exists | ✅ | Rendered HTML with layout |
| T7 — No raw `README.md` in `_site/` | ✅ | Zero `.md` output files |

## Phase 114: Fix all ruff lint errors

| Test | Status | Notes |
|------|--------|-------|
| T1 — `ruff check .` | ✅ | All checks passed! |
| T2 — `nox -s all_tests` (8 sessions) | ✅ | 850+ tests, 0 failures |
| T3 — Re-export imports preserved | ✅ | app.py + state.py with noqa |


## Phase 115: Remove asyncio_mode pytest warning

| Test | Status | Notes |
|------|--------|-------|
| T1 — 0 pytest warnings | ✅ | No PytestConfigWarning in any session |
| T2 — 8/8 sessions pass | ✅ | 850+ tests, 0 failures |
{% endraw %}
