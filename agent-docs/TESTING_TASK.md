---
layout: default
---
{% raw %}
# Testing Tasks — Phase 112: Jekyll Optional Front Matter Plugin

## Phase 112: Jekyll Optional Front Matter Plugin

| Task | Description | Status |
|------|-------------|--------|
| T1 | `bundle exec jekyll build` exits 0 | ✅ |
| T2 | `_site/README.html` exists with layout | ✅ |
| T3 | `_site/scripts/README.html` exists | ✅ |
| T4 | `_site/e2e/README.html` exists | ✅ |
| T5 | `_site/board_manager/python/board_manager/README.html` exists | ✅ |
| T6 | `_site/medminder_dash/python/medminder_dash/README.html` exists | ✅ |
| T7 | No raw `README.md` in `_site/` | ✅ |

## Completed — 2026-07-05

All Phase 112 tests verified:
- ✅ T1: `bundle exec jekyll build` — 0 errors
- ✅ T2-T6: All 12 README.html files present in `_site/` with layout
- ✅ T7: Zero raw `.md` copies in `_site/`

---

## Phase 114 — Fix all ruff lint errors

| Task | Scope | Status |
|------|-------|--------|
| T1 | `ruff check .` — 0 errors | ✅ |
| T2 | `nox -s all_tests` — 8/8 sessions pass | ✅ |
| T3 | Verify re-export imports preserved | ✅ |


---

## Phase 115 — Remove asyncio_mode pytest warning

| Task | Scope | Status |
|------|-------|--------|
| T1 | `nox -s all_tests` — 0 pytest warnings | ✅ |
| T2 | 8/8 sessions pass | ✅ |

## Phase 116 — djlint template reformatting

| Task | Scope | Status |
|------|-------|--------|
| T1 | `djlint . --check` exit 0 | ✅ |
| T2 | `ruff check .` exit 0 | ✅ |
| T3 | Templates render correctly (no structural changes) | ✅ |



---

## Phase 117 — Fix CI Pipeline

| # | Test Task | Status | Notes |
|---|-----------|--------|-------|
| T1 | `bash -n scripts/ci.sh` | ✅ | Exit 0, syntax OK |
| T2 | `bash scripts/tests/test_ci.sh` | ✅ | 30/30 assertions pass |
| T3 | YAML validity check | ✅ | `yaml.safe_load` no error |
| T4 | `nox -s scripts_tests` | ✅ | 202/202 tests pass |

---

## Phase 118 — Ruff Format Audit

| # | Test Task | Status | Notes |
|---|-----------|--------|-------|
| T1 | `ruff format --check .` | ✅ | Verify idempotency (all files already formatted) |
| T2 | `ruff check .` | ✅ | 0 errors |
| T3 | E501 fix in add_license_headers.py | ✅ | 35 lines wrapped, parenthetical continuation |

---

## Phase 119 — Prettier/Djlint Convergence

| # | Test Task | Status | Notes |
|---|-----------|--------|-------|
| T1 | `djlint . --check` exit 0 | ✅ | 50 files, 0 flagged |
| T2 | `ruff check .` exit 0 | ✅ | No regressions |
| T3 | `prettier --check "**/*.html"` | ✅ | No Jinja files checked |

---

## Phase 120 — Git Hooks

| # | Test Task | Status | Notes |
|---|-----------|--------|-------|
| T1 | `bash -n .githooks/pre-commit` | ✅ | Exit 0, syntax OK (46 lines) |
| T2 | `bash -n .githooks/pre-push` | ✅ | Exit 0, syntax OK (15 lines) |
| T3 | `shellcheck scripts/ci.sh` | ✅ | Clean, SC2155/SC2034/SC2154 fixed |
| T4 | `shellcheck scripts/tests/test_ci.sh` | ✅ | Same 3 categories fixed |
| T5 | `ruff check .` — 0 errors | ✅ | All checks passed |
| T6 | Pre-commit prompt/skip behavior | ✅ | Y runs all checks; n prints yellow warning, exits 0 |
| T7 | Pre-commit sequential checks | ✅ | ruff check → ruff format --check → prettier --check → eslint → djlint --check |
| T8 | Pre-push ci.sh invocation | ✅ | Script inspection confirms `./scripts/ci.sh` call |

---

## Phase 121 — ESLint Generated-Docs Ignore + Source Fix

| Task | Scope | Status |
|------|-------|--------|
| A | Verify ESLint 0 errors 0 warnings | ✅ |
| B | Verify ruff check exits 0 | ✅ |
| C | Verify prettier check exits 0 | ✅ |

---

## Phase 122 — CI Restructure: Lint Phase + Nox Prompt + Standalone CI YAML

| Task | Scope | Status |
|------|-------|--------|
| T1 | `bash scripts/tests/test_ci.sh` 40/40 | ✅ |
| T2 | `ruff check .` exit 0 | ✅ |
| T3 | `ruff format --check .` all formatted | ✅ |
| T4 | `bash -n scripts/ci.sh` syntax OK | ✅ |
| T5 | `bash -n scripts/tests/test_ci.sh` syntax OK | ✅ |
| T6 | Lint success (Q18.11) — exit 0, Phase 0 labels | ✅ |
| T7 | Lint failure (Q18.12) — exit 5, stderr message | ✅ |
| T8 | `--no-install` (Q18.13) — exit 0, warning, phases skipped | ✅ |

---


---

## Phase 122c — Lock File Handling in ci.sh

| Task | Scope | Status |
|------|-------|--------|
| T1 | Pre-check abort (Q18.14) — dirty locks + user declines → exit 1, warning + abort message | ✅ |
| T2 | Post-check restore (Q18.15) — newly dirty + user accepts → restored, git restore called | ✅ |
| T3 | Post-check skip (Q18.16) — newly dirty + user declines → left dirty, no git restore | ✅ |
| T4 | Existing tests isolated — Q18.6–Q18.10 pass with FAKE_GIT_DIRTY_LOCK_FILES="" | ✅ |

{% endraw %}
