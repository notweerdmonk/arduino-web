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

{% endraw %}
