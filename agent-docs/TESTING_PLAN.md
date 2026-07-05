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
{% endraw %}
