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

{% endraw %}
