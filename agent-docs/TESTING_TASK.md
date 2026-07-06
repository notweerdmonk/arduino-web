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

{% endraw %}
