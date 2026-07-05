---
layout: default
---
{% raw %}
# Implementation Progress — Phase 112: Jekyll Optional Front Matter

## Past Phases

### Phase 111: Semantic Versioning v0.1.0

| # | Task | Status | Notes |
|---|------|--------|-------|
| A | Add __version__ to 3 missing packages | ✅ | arduino_sketch_tools, board_manager_client, medminder_dash |
| B | Standardize setup.py to import version | ✅ | All 6 setup.py files use version=__version__ |
| C | Add version to root package.json | ✅ | "version": "0.1.0" added |
| D | Create root-level VERSION file | ✅ | VERSION: 0.1.0 |
| E | Test all changes | ✅ | 160 scripts tests passed, nox 8/8 sessions passed |

### Phase 112: Jekyll Optional Front Matter Plugin

| # | Task | Status | Notes |
|---|------|--------|-------|
| A | Add gem to Gemfile + plugin to `_config.yml` | ✅ | `:jekyll_plugins` group created |
| B | `bundle install` + `jekyll build` | ✅ | 0 errors |
| C | Verify 12 README.md → `.html` with layout | ✅ | All 12 appear as `.html` in `_site/` |
{% endraw %}
