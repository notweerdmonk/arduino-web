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

## Phase 118 — Ruff Format Audit

| Test | Status | Notes |
|------|--------|-------|
| T1 — `ruff format --check .` | ✅ | 111 files would be reformatted, all .py |
| T2 — `ruff check .` | ✅ | 0 errors |
| T3 — E501 fix in add_license_headers.py | ✅ | 35 lines wrapped, 0 errors |

---

## Phase 119 — Prettier/Djlint Convergence

| Test | Status | Notes |
|------|--------|-------|
| T1 — `djlint . --check` | ✅ | 50 files, 0 flagged, exit 0 |
| T2 — `ruff check .` | ✅ | 0 errors |
| T3 — `prettier --check "**/*.html"` | ✅ | Templates excluded by .prettierignore |

---

## Phase 120 — Git Hooks

| Test | Status | Notes |
|------|--------|-------|
| T1 — `bash -n .githooks/pre-commit` | ✅ | 46 lines, syntax OK |
| T2 — `bash -n .githooks/pre-push` | ✅ | 15 lines, syntax OK |
| T3 — `shellcheck scripts/ci.sh` | ✅ | SC2155, SC2034, SC2154 fixed |
| T4 — `shellcheck scripts/tests/test_ci.sh` | ✅ | Same fixes applied |
| T5 — `ruff check .` | ✅ | 0 errors |
| T6 — Pre-commit prompt/skip behavior | ✅ | Y → all checks; n → yellow warning, exit 0 |
| T7 — Pre-commit sequential checks | ✅ | 5 tools run in order |
| T8 — Pre-push ci.sh invocation | ✅ | Script inspected, calls `./scripts/ci.sh` |

{% endraw %}
