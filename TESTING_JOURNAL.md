---
---
{% raw %}
# Testing Journal — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

## Entry 1 — Overview

**Method**: Per-quantum `bundle exec jekyll build` verification, plus `grep`/`ls` inspection of `_site/` output for href targets, file existence, and page counts.

**Risk**: Low. Changes are to config files, markdown front matter, and static HTML template syntax (raw/endraw). No Python code modified.

## Entry 2 — Build Statistics

| Quantum | Pages | Errors | Warnings | Notes |
|---------|-------|--------|----------|-------|
| Q1-Q2 | 0 (build failed) | Liquid syntax errors | 0 | Before fixes |
| Q3-Q4 | 246 | 0 | 4 (Liquid `{{ }}`) | Front matter + raw/endraw applied |
| Q5-Q6 | 246 | 0 | 4 | Broken links fixed in source |
| Q7 | 246 | 0 | 0 | RESEARCH docs raw-wrapped |
| Q8 | 254 | 0 | 0 | README front matter added (+8 pages) |
| Q9-Q10 | 254 | 0 | 0 | README links added to index.md |

## Entry 3 — Key Findings

1. **Link verification critical**: `jekyll-relative-links` silently converts `.md` links to `.html`. Must grep rendered `_site/` output, not source files, to verify href targets.
2. **README hrefs**: If a `README.md` lacks front matter, Jekyll copies it as a static file (`.md` extension). The `jekyll-relative-links` plugin only converts links to `.html` for pages that Jekyll processes (those with front matter). Without front matter, links in `index.md` resolve to `README.md` in the rendered HTML, not `README.html`.
3. **Warning elimination**: `{{ port.lstrip('/') }}` in RESEARCH docs produces 2 warnings per file. raw/endraw wrapping eliminates all 4 warnings.
4. **Non-fatal doctor issue**: `bundle exec jekyll doctor` reports `undefined method 'absolute?' for nil:NilClass` — known Jekyll 3.10 bug when `url:` is not set. Does not affect build output.
## 2026-06-20 20:03 — Phase 96: test_ci.sh wired into scripts_tests

**Change**: Added `test_ci.sh` to the `scripts_tests` nox session (after
`test_install_arduino_deps.sh`). The script tests 10 scenarios for
`scripts/ci.sh` using a fake nox shim — 30 assertions total.

**Results**:
- Standalone run: 30/30 pass ✅
- Nox `scripts_tests`: 128 pytest + 12 bash + 30 bash = 170 total in 24s ✅

**Gotchas**: None. The script is fully self-contained (bash-only) and uses
`BASH_SOURCE` for path resolution, so it works correctly when launched from
any CWD (including nox's chdir to `scripts/`).
{% endraw %}
