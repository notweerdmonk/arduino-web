---
layout: default
---
{% raw %}
# Implementation Tasks — Phase 111: Semantic Versioning v0.1.0

## Task A — Add __version__ to 3 missing packages

Add `__version__ = "0.1.0"` to these files:
1. arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/__init__.py
2. board_manager_client/python/board_manager_client/board_manager_client/__init__.py
3. medminder_dash/python/medminder_dash/medminder_dash/__init__.py

**Done when**: Each package passes `from PKG import __version__; print(__version__)`

## Task B — Standardize setup.py to read version from __init__.py

For all 6 packages, replace `version="0.1.0"` with `version=__version__`:
- arduino_dash/.../setup.py -> from arduino_dash import __version__
- arduino_sketch_tools/.../setup.py -> from arduino_sketch_tools import __version__
- board_manager/.../setup.py -> from board_manager import __version__
- board_manager_client/.../setup.py -> from board_manager_client import __version__
- medminder_dash/.../setup.py -> from medminder_dash import __version__
- grpc_client/.../setup.py -> from arduino_grpc import __version__

**Done when**: `python3 setup.py --version` prints 0.1.0 for each package.

## Task C — Add version to root package.json

Add `"version": "0.1.0"` to /home/weerdmonk/Projects/medminder/package.json.

## Task D — Create root-level VERSION file

Create /home/weerdmonk/Projects/medminder/VERSION with content "0.1.0\n".

## Task E — Test all changes

1. Import verification for all 6 packages
2. scripts tests: `pipenv run pytest tests/`
3. Full suite: `nox -s all_tests`

---

## Completed — 2026-07-04

All Phase 111 implementation tasks verified:
- ✅ Task A: `__version__` added to 3 missing packages
- ✅ Task B: All 6 `setup.py` files import version from `__init__.py`
- ✅ Task C: `"version": "0.1.0"` added to root `package.json`
- ✅ Task D: Root `VERSION` file created
- ✅ Task E: All tests pass — `nox -s all_tests`: 8/8 sessions, 0 failures

## Task F — Add jekyll-optional-front-matter plugin (Phase 112)

Enable the plugin to process front-matter-less markdown files as Jekyll pages.

### Steps

1. Add `gem "jekyll-optional-front-matter"` to Gemfile in `:jekyll_plugins` group
2. Move `jekyll-relative-links` into the same group
3. Add `- jekyll-optional-front-matter` to `_config.yml` plugins list
4. Add `remove_originals: true` to suppress raw `.md` copies
5. `bundle install`
6. `bundle exec jekyll build` — verify 0 errors
7. Confirm all 12 README.md files appear as `.html` in `_site/`

### Verification

- `bundle exec jekyll build` — 0 errors, 0 warnings
- All 12 README.md files render as `.html` with `layout: default`
- No raw `README.md` static copies in `_site/`

## Completed — 2026-07-05

All Phase 112 implementation tasks verified:
- ✅ Steps 1-4: Gemfile + `_config.yml` changes applied
- ✅ Step 5: `bundle install` — success
- ✅ Step 6: `bundle exec jekyll build` — 0 errors
- ✅ Step 7: All 12 README.html files present in `_site/`, zero raw `.md` copies
{% endraw %}
