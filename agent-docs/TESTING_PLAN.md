---
layout: default
---
{% raw %}
# Testing Plan — Phase 112: Jekyll Optional Front Matter Plugin

## Scope

Verify that the `jekyll-optional-front-matter` plugin correctly processes all 12 front-matter-less README.md files as Jekyll pages.

## Test Strategy

1. `bundle exec jekyll build` must exit 0 with no errors
2. All 12 README.md paths must render as `.html` files in `_site/`
3. No raw `.md` copies should remain in `_site/` (`remove_originals: true`)
4. Rendered `.html` files must include `<!DOCTYPE html>` (layout `default` applied)

## Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `bundle exec jekyll build` exits 0 | No errors/warnings | ✅ 0 errors, 0 warnings |
| 2 | `_site/README.html` exists | Rendered HTML with layout | ✅ 17 files (incl. extras), layout applied |
| 3 | `_site/scripts/README.html` exists | Rendered HTML with layout | ✅ Present |
| 4 | `_site/e2e/README.html` exists | Rendered HTML with layout | ✅ Present |
| 5 | `_site/board_manager/python/board_manager/README.html` exists | Rendered HTML with layout | ✅ Present |
| 6 | `_site/medminder_dash/python/medminder_dash/README.html` exists | Rendered HTML with layout | ✅ Present |
| 7 | No raw `README.md` in `_site/` | Zero `.md` output files | ✅ 0 raw `.md` copies |

---

## Phase 114: Fix all ruff lint errors

### Scope

Verify that ruff lint fixes don't break tests.

### Test Strategy

1. `ruff check .` must exit 0 with no errors
2. `nox -s all_tests` must pass 8/8 sessions with 0 failures
3. Re-export imports in `arduino_dash/app.py` and `arduino_dash/state.py` must be preserved (F401 noqa)

### Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `ruff check .` | 0 errors | ✅ All checks passed! |
| 2 | `nox -s all_tests` | 8/8 sessions pass | ✅ 8/8, 850+ tests, 0 failures |
| 3 | `arduino_dash/app.py` re-exports | 3 blocks with noqa persist | ✅ Verified |
| 4 | `arduino_dash/state.py` UPLOAD_BASE_DIR | Import with noqa persists | ✅ Verified |


---

## Phase 115: Remove asyncio_mode pytest warning

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `nox -s all_tests` — 0 pytest warnings | 0 `PytestConfigWarning` | ✅ 0 warnings across 8 sessions |
| 2 | All 8 sessions pass | 8/8 success | ✅ 8/8, 850+ tests, 0 failures |
{% endraw %}
