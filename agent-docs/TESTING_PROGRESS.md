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

## Phase 116 — djlint template reformatting

| Test | Status | Notes |
|------|--------|-------|
| T1 — `djlint . --check` exit 0 | ✅ | 50/50 files checked, 0 flagged |
| T2 — `ruff check .` exit 0 | ✅ | 0 errors (no Python files affected) |
| T3 — Templates render correctly | ✅ | Structural HTML unchanged, cosmetic only |



## Phase 117 — Fix CI Pipeline

| Test | Status | Notes |
|------|--------|-------|
| T1 — `bash -n scripts/ci.sh` | ✅ | Syntax OK |
| T2 — `bash scripts/tests/test_ci.sh` | ✅ | 30/30 assertions |
| T3 — YAML validity | ✅ | `yaml.safe_load` OK |
| T4 — `nox -s scripts_tests` | ✅ | 202/202 tests pass |

---

## Phase 120 — Git Hooks

| Test | Status | Notes |
|------|--------|-------|
| T1 — pre-commit bash syntax | ✅ | `bash -n .githooks/pre-commit` |
| T2 — pre-push bash syntax | ✅ | `bash -n .githooks/pre-push` |
| T3 — pre-commit dry run | ✅ | ruff check, ruff format --check, djlint --check all pass |
| T4 — pre-push dry run | ✅ | scripts_tests passes |

## Phase 119 — Prettier/Djlint Convergence

| Test | Status | Notes |
|------|--------|-------|
| T1 — `djlint . --check` | ✅ | 50 files, 0 flagged, exit 0 |
| T2 — `ruff check .` | ✅ | 0 errors |
| T3 — `prettier --check "**/*.html"` | ✅ | Templates excluded by .prettierignore |

{% endraw %}
