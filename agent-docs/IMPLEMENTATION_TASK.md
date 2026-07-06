---
layout: default
---
{% raw %}
# Implementation Tasks — Phase 116: djlint template reformatting

## Task A — Update pyproject.toml extend_exclude

Add `_site|dist-standalone|docs/reference|scratch` to `[tool.djlint]`
`extend_exclude` in `pyproject.toml`.

**Done when**: `extend_exclude` includes all generated directories.

## Task B — Run djlint --reformat

Run `pipenv run djlint . --reformat` to auto-format the 50 source templates
(25 medminder_dash, 15 arduino_dash, 10 arduino_sketch_tools).

**Done when**: Command completes without errors.

## Task C — Verify with djlint --check

Run `pipenv run djlint . --check` — must exit 0.

**Done when**: Exit code 0, no files flagged.

## Task D — Update all 16 agent-facing workflow documents

Add Phase 116 entries to:
- PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md
- All 4 IMPLEMENTATION_* docs
- All 4 TESTING_* docs
- All 4 REVIEW_* docs
- TODOS.md

**Done when**: grep "Phase 116" returns 16 hits across agent-docs/.

## Task E — Update user-facing docs

Apply documentation skill to update docs/tests.md if needed.

**Done when**: docs/tests.md reflects djlint reformat.

---

### Current Status

| Task | Status |
|------|--------|
| A — pyproject.toml extend_exclude | ✅ COMPLETED |
| B — djlint --reformat | 🔄 IN PROGRESS |
| C — djlint --check verify | Pending |
| D — All agent-facing docs updated | Pending |
| E — User-facing docs updated | Pending |

---

## Phase 117 — Fix CI Pipeline

### Task A — Swap build/test order in scripts/ci.sh

Swap the Phase 1/Phase 2 execution order in `scripts/ci.sh` so that builds run
before tests. Update phase labels in echo messages and `--help` text.

**Done when**: `bash -n scripts/ci.sh` passes, `bash scripts/tests/test_ci.sh`
passes (30/30 assertions).

### Task B — Add nox install to .github/workflows/ci.yml

Insert a new step `Install nox` after the djlint step and before the
`Full CI pipeline` step in `.github/workflows/ci.yml`.

**Done when**: YAML syntax is valid. Step reads: `run: pip install nox`.

### Task C — Verify all changes

1. Bash syntax check: `bash -n scripts/ci.sh` → exit 0
2. Unit test: `bash scripts/tests/test_ci.sh` → 30/30 assertions pass
3. YAML check: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` → no error
4. Full test: `nox -s all_tests` → 8/8 sessions pass

**Done when**: All 4 checks pass.

### Task D — Update all agent-facing docs

- PLAN.md — add Phase 117 entry
- JOURNAL.md — add journal entry
- IMPLEMENTATION_PLAN.md — mark Phase 117 quantums complete
- IMPLEMENTATION_TASK.md — mark tasks complete
- IMPLEMENTATION_PROGRESS.md — mark milestones complete
- IMPLEMENTATION_JOURNAL.md — add detailed journal entry
- TESTING_PLAN.md — add test plan entry
- TESTING_TASK.md — add test task entry
- TESTING_PROGRESS.md — update progress
- TESTING_JOURNAL.md — add test results
- REVIEW_PLAN.md — add review plan
- REVIEW_TASK.md — add review task
- REVIEW_PROGRESS.md — update progress
- REVIEW_JOURNAL.md — add journal entry
- TODOS.md — update master todo
- CODEBASE_REFERENCE.md — update with ci.sh/ci.yml references

**Done when**: All 16 docs updated.

### Task E — Update user-facing docs

Apply documentation skill to update docs/ directory for CI pipeline changes.

**Done when**: User-facing docs reflect the new CI pipeline.

---

### Current Status

| Task | Status |
|------|--------|
| A — Swap build/test order in ci.sh | ✅ |
| B — Add nox install to ci.yml | ✅ |
| C — Verify all changes | ✅ |
| D — Update all agent-facing docs (16) | ✅ |
| E — Update user-facing docs | ✅ |

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

## Phase 119 — Prettier/Djlint Convergence

| Task | Scope | Status |
|------|-------|--------|
| A | `pyproject.toml` — set `[tool.djlint]` `indent = 2` | ✅ |
| B | `.prettierignore` — add `**/templates/` | ✅ |
| C | Run `djlint . --reformat` with indent=2 on 50 templates | ✅ |
| D | Verify `djlint . --check` exit 0 | ✅ |
| E | Verify `ruff check .` exit 0 | ✅ |

{% endraw %}
