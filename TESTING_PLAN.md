---
---
# Testing Plan — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

## Scope

Static analysis and build verification for Jekyll documentation site. No Python code changes — only config files, markdown content, and static file metadata (front matter).

## Test Strategy

| Quantum | What to Test | Method | Pass Criteria |
|---------|-------------|--------|---------------|
| Q1-Q2 | Config fixes | `bundle exec jekyll build` | Exit 0, no "Liquid syntax error" |
| Q3-Q4 | Front matter + raw/endraw | `bundle exec jekyll build` | Exit 0, no syntax errors |
| Q5 | Broken links | `grep` href targets in `_site/` | All hrefs point to existing `.html` files |
| Q6 | Final build | `bundle exec jekyll build` | Exit 0, 0 errors, 0 warnings |
| Q7 | Liquid warnings | `bundle exec jekyll build 2>&1 | grep -i warning` | 0 warnings |
| Q8 | README files | `grep` href targets in `_site/index.html` | All README hrefs resolve to `.html` |
| Q9 | index.md README links | `grep -oP 'href="[^"]*README[^"]*"' _site/index.html` | 9+ README hrefs present |
| Q10 | Final build + page count | `find _site -name "*.html" | wc -l` | 254 HTML pages |

## Verification Steps

1. `bundle exec jekyll build` — exit 0, no errors, no warnings
2. `grep` spot-check all new href targets in `_site/index.html`
3. Verify README links resolve to `.html` (not `.md`)
4. Count total HTML pages (expect 254)
5. Verify nested subpackage doc directories exist in `_site/`

## Key Files to Verify

| File in _site | Expected | Verification |
|---------------|----------|--------------|
| `_site/index.html` | Documentation hub with README links | `grep` href README |
| `_site/board_manager/python/board_manager/board_manager/docs/` | 11 doc pages | `ls` directory |
| `_site/medminder_dash/python/medminder_dash/medminder_dash/docs/` | 15 doc pages | `ls` directory |
| `_site/README.html` | Processed README | File exists |
| All README `.html` files | Processed pages at expected paths | `find _site -name "README.html"` |
