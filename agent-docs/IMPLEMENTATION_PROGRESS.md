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


### Phase 113: Fix setup.py isolated build failure

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | board_manager setup.py | ✅ | `_read_version()` helper with `ast.literal_eval` |
| 2 | board_manager_client setup.py | ✅ | Same pattern |
| 3 | arduino_sketch_tools setup.py | ✅ | Same pattern |
| 4 | arduino_dash setup.py | ✅ | Same pattern |
| 5 | arduino_grpc setup.py | ✅ | Same pattern |
| 6 | medminder_dash setup.py | ✅ | Same pattern |
| 7 | Verify single build | ✅ | `nox -s 'build(board_manager)'` — success |
| 8 | Verify all builds | ✅ | `nox -s all_builds` — 7/7 sessions in 56s |
| 9 | Sync all agent-facing docs | ✅ | All docs updated with Phase 113 entries |


### Phase 114: Fix all ruff lint errors

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | pyproject.toml config | ✅ | select → lint.select |
| 2 | Auto-fix 138 errors | ✅ | ruff check --fix (I001, W293, F401, F541) |
| 3 | Fix 6 E402 in setup.py | ✅ | All 6 setup.py files fixed |
| 4 | Fix 17 E501 in 11 files | ✅ | Long lines wrapped |
| 5 | Fix 1 F841 | ✅ | Dead variable removed |
| 6 | Restore re-exports | ✅ | app.py + state.py with noqa |
| 7 | Verify ruff | ✅ | 0 errors |
| 8 | Verify tests | ✅ | nox -s all_tests — 8/8 sessions |


### Phase 115: Remove asyncio_mode pytest warning

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Remove asyncio_mode from pyproject.toml | ✅ | `asyncio_mode = "auto"` removed |
| 2 | Verify no warnings | ✅ | nox -s all_tests — 0 pytest warnings, 8/8 sessions |


### Phase 116: djlint template reformatting

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | pyproject.toml extend_exclude | ✅ | Added `_site|dist-standalone|docs/reference|scratch` |
| 2 | djlint --reformat on 50 templates | 🔄 | 25 medminder_dash + 15 arduino_dash + 10 arduino_sketch_tools |
| 3 | djlint --check passes (exit 0) | Pending | |
| 4 | All agent-facing docs updated | Pending | |
| 5 | User-facing docs updated | Pending | |

{% endraw %}
