---
---
{% raw %}
# Review Plan — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

## Review Criteria

### Configuration Correctness
- [x] `_config.yml` — single `plugins:` list with all 3 plugins
- [x] `_config.yml` — `theme: minima` set
- [x] `_config.yml` — `defaults:` with `layout: default` for all pages
- [x] `Gemfile` — `jekyll-archives` removed
- [x] `Gemfile` — `gem "minima", "~> 2.5"` pinned

### Build Verification
- [x] `bundle exec jekyll build` — exit 0
- [x] 0 Liquid syntax errors
- [x] 0 Liquid warnings
- [x] 254 HTML pages generated

### Front Matter Coverage
- [x] 93 doc files in `docs/` directories have `---\n---\n`
- [x] 7 per-package README files have front matter
- [x] `grpc_client/.../README.md` has front matter

### raw/endraw Coverage
- [x] 5 workflow docs with Jinja2 wrapped (JOURNAL.md, PLAN.md, TODOS.md, docs/ws-event-flow.md, CODEBASE_REFERENCE.md)
- [x] 2 research docs with `{{ }}` wrapped (RESEARCH_JOURNAL.md, RESEARCH_PLAN.md)
- [x] No literal closing raw tag inside backtick spans in raw-wrapped files

### Link Correctness
- [x] 24 board_manager links fixed across 5 files
- [x] 27 medminder_dash links fixed across 5 files
- [x] All hrefs in `_site/` resolve to existing `.html` files
- [x] Nested subpackage doc directories exist: `board_manager/python/board_manager/board_manager/docs/`

### README Links
- [x] 9 README hrefs in `_site/index.html`
- [x] All README hrefs resolve to `.html` (not `.md`)
- [x] 8 README `.html` files exist in `_site/`

### Documentation Sync
- [x] PLAN.md — Phase 93 entry added
- [x] JOURNAL.md — Phase 93 entry updated
- [x] CODEBASE_REFERENCE.md — Jekyll section added
- [x] IMPLEMENTATION_* docs — all updated
- [x] TESTING_* docs — all updated
- [x] REVIEW_* docs — all updated (this file)
- [x] TODOS.md — Phase 93 entry added
{% endraw %}
