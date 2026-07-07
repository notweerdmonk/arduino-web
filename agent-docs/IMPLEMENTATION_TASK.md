---
layout: default
---
{% raw %}
## Phase 118 — Ruff Format Audit

| Task | Scope | Status |
|------|-------|--------|
| A | Run `ruff format .` on all Python source | ✅ | 111 files reformatted, cosmetic only |
| B | Verify idempotency | ✅ | Second `--check` run reports all formatted |
| C | Fix E501 errors in `add_license_headers.py` | ✅ | 35 lines wrapped with parenthetical continuation |
| D | Verify `ruff check .` exit 0 | ✅ | No regressions |

---

## Phase 119 — Prettier/Djlint Convergence

| Task | Scope | Status |
|------|-------|--------|
| A | `pyproject.toml` — set `[tool.djlint]` `indent = 2` | ✅ |
| B | `.prettierignore` — add `**/templates/` | ✅ |
| C | Run `djlint . --reformat` with indent=2 on 50 templates | ✅ |
| D | Verify `djlint . --check` exit 0 | ✅ |
| E | Verify `ruff check .` exit 0 | ✅ |

---

## Phase 120 — Git Hooks

| Task | Scope | Status |
|------|-------|--------|
| A | Create `.githooks/pre-commit` — ruff check, ruff format --check, djlint --check | ✅ |
| B | Create `.githooks/pre-push` — nox -s scripts_tests | ✅ |
| C | Update AGENTS.md with hook setup instructions | ✅ |
| D | Add README.md quick start section | ✅ |
| E | Update scripts/ci.sh docblock | ✅ |

---

## Phase 121 — ESLint Generated-Docs Ignore + Source Fix

| Task | Scope | Status |
|------|-------|--------|
| A | Add generated-path ignores to `config/eslint.config.mjs` (5 patterns) | ✅ |
| B | Fix `no-unused-vars` in arduino_dash base.html (htmx callbacks) | ✅ |
| C | Fix `no-unused-vars` in medminder_dash base.html (htmx callbacks) | ✅ |
| D | Verify `npx eslint .` — 0 errors, 0 warnings | ✅ |

---

## Phase 122 — CI Restructure: Lint Phase + Nox Prompt + Standalone CI YAML

| Task | Scope | Status |
|------|-------|--------|
| A | ci.sh — lint Phase 0 (5 checks, exit 5) | ✅ |
| B | ci.sh — `--skip-lint`, `--no-install` flags | ✅ |
| C | ci.sh — interactive nox install prompt (5 options) | ✅ |
| D | ci.yml — standalone (no ci.sh call) | ✅ |
| E | test_ci.sh — 3 new tests, 6 updated (40 total) | ✅ |
| F | User-facing docs updated | ✅ |
| G | Agent-facing docs updated | ✅ |
| H | Verify: `test_ci.sh` 40/40 ✅, `ruff check .` OK ✅ | ✅ |


## Phase 122c — Lock File Handling in ci.sh

| Task | Scope | Status |
|------|-------|--------|
| A | ci.sh — pre-check: warn/abort on dirty lock files before Phase 1 | ✅ |
| B | ci.sh — post-check: list newly-dirtied lock files after Phase 2, offer git restore | ✅ |
| C | ci.sh — `FAKE_GIT_DIRTY_LOCK_FILES` env-var bypass for test isolation | ✅ |
| D | test_ci.sh — `make_fake_git()` helper for lock-file test scenarios | ✅ |
| E | test_ci.sh — Q18.14: pre-check abort (dirty files + user says "n" → exit 1) | ✅ |
| F | test_ci.sh — Q18.15: post-check restore (newly dirty + user says "y" → restored) | ✅ |
| G | test_ci.sh — Q18.16: post-check skip (newly dirty + user says "n" → leave dirty) | ✅ |
| H | test_ci.sh — Add `FAKE_GIT_DIRTY_LOCK_FILES=""` to Q18.6–Q18.10 for isolation | ✅ |
| I | Run all tests 49/49 | ✅ |
| J | Sync all agent-facing docs | ✅ |
| K | Lint + final verify | ✅ |

{% endraw %}
