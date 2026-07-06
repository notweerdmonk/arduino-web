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

---

## Phase 113 — Fix setup.py isolated build failure

All tasks verified:

| Task | Package | File | Status |
|------|---------|------|--------|
| A | board_manager | `board_manager/python/board_manager/setup.py` | ✅ |
| B | board_manager_client | `board_manager_client/python/board_manager_client/setup.py` | ✅ |
| C | arduino_sketch_tools | `arduino_sketch_tools/python/arduino_sketch_tools/setup.py` | ✅ |
| D | arduino_dash | `arduino_dash/python/arduino_dash/setup.py` | ✅ |
| E | arduino_grpc | `grpc_client/python/arduino_grpc/setup.py` | ✅ |
| F | medminder_dash | `medminder_dash/python/medminder_dash/setup.py` | ✅ |
| G | Verify single build | `nox -s 'build(board_manager)'` — success | ✅ |
| H | Verify all builds | `nox -s all_builds` — 7/7 sessions passed | ✅ |
| I | Sync all agent-facing docs | PLAN, JOURNAL, IMPLEMENTATION_*, TESTING_*, REVIEW_*, CODEBASE_REFERENCE | ✅ |

### Completed — 2026-07-06

All Phase 113 implementation tasks verified:
- ✅ Tasks A-F: All 6 setup.py files use `_read_version()` pattern with `ast.literal_eval`
- ✅ Task G: `nox -s 'build(board_manager)'` — success
- ✅ Task H: `nox -s all_builds` — 7/7 sessions in 56s
- ✅ Task I: All agent-facing docs synced

### Verification Summary

```
$ nox -s all_builds
nox > Ran 7 sessions in 56 seconds:
nox > * all_builds: success
nox > * build(board_manager): success, took 7 seconds
nox > * build(board_manager_client): success, took 9 seconds
nox > * build(arduino_sketch_tools): success, took 10 seconds
nox > * build(arduino_dash): success, took 10 seconds
nox > * build(arduino_grpc): success, took 9 seconds
nox > * build(medminder_dash): success, took 8 seconds
```

### Task A — Fix board_manager/setup.py

Replace `from board_manager import __version__` with `_read_version()` helper.

**Package directory**: `board_manager/python/board_manager/`
**Done when**: `setup.py` parses without import error in isolated mode.

### Task B — Fix board_manager_client/setup.py

Replace `from board_manager_client import __version__` with `_read_version()` helper.

**Package directory**: `board_manager_client/python/board_manager_client/`
**Done when**: `setup.py` parses without import error in isolated mode.

### Task C — Fix arduino_sketch_tools/setup.py

Replace `from arduino_sketch_tools import __version__` with `_read_version()` helper.

**Package directory**: `arduino_sketch_tools/python/arduino_sketch_tools/`
**Done when**: `setup.py` parses without import error in isolated mode.

### Task D — Fix arduino_dash/setup.py

Replace `from arduino_dash import __version__` with `_read_version()` helper.

**Package directory**: `arduino_dash/python/arduino_dash/`
**Done when**: `setup.py` parses without import error in isolated mode.

### Task E — Fix arduino_grpc/setup.py

Replace `from arduino_grpc import __version__` with `_read_version()` helper.

**Package directory**: `grpc_client/python/arduino_grpc/`
**Done when**: `setup.py` parses without import error in isolated mode.

### Task F — Fix medminder_dash/setup.py

Replace `from medminder_dash import __version__` with `_read_version()` helper.

**Package directory**: `medminder_dash/python/medminder_dash/`
**Done when**: `setup.py` parses without import error in isolated mode.

### Task G — Verify single package build

Run `nox -s 'build(board_manager)'` and confirm it produces a `.whl`.

### Task H — Verify all packages build

Run `nox -s all_builds` and confirm all 6 packages produce wheels.

### Task I — Sync all agent-facing docs

Update PLAN.md, JOURNAL.md, IMPLEMENTATION_*, TESTING_*, REVIEW_*, CODEBASE_REFERENCE.md
with Phase 113 entries.


---

## Phase 114 — Fix all ruff lint errors

All tasks verified:

| Task | Scope | File/Location | Status |
|------|-------|---------------|--------|
| A | pyproject.toml config | `select` → `lint.select` migration | ✅ |
| B | Auto-fix 138 errors | `ruff check --fix` (I001, W293, F401, F541) | ✅ |
| C | E402 — board_manager setup.py | Move `from setuptools import setup` above `_read_version()` | ✅ |
| D | E402 — board_manager_client setup.py | Same | ✅ |
| E | E402 — arduino_sketch_tools setup.py | Same | ✅ |
| F | E402 — arduino_dash setup.py | Same | ✅ |
| G | E402 — arduino_grpc setup.py | Same | ✅ |
| H | E402 — medminder_dash setup.py | Same | ✅ |
| I | E501 — 17 lines in 11 files | Wrap f-strings, docstrings, expressions | ✅ |
| J | F841 — add_license_headers.py | Remove dead `pattern` variable | ✅ |
| K | Restore re-exports | `app.py` (3 blocks), `state.py` (UPLOAD_BASE_DIR) | ✅ |
| L | Verify ruff | `ruff check .` → 0 errors | ✅ |
| M | Verify all tests | `nox -s all_tests` → 8/8 sessions | ✅ |

### Completed — 2026-07-06

All Phase 114 tasks verified:
- ✅ Ruff check: 0 errors (E, F, I, W)
- ✅ Tests: 8/8 nox sessions, 850+ tests, 0 failures
- ✅ All agent-facing docs synced


---

## Phase 115 — Remove asyncio_mode pytest warning

| Task | Scope | Status |
|------|-------|--------|
| A | Remove `asyncio_mode = "auto"` from pyproject.toml | ✅ |
| B | Verify nox -s all_tests — 0 warnings, 8/8 sessions | ✅ |

### Completed — 2026-07-06

- ✅ Removed `asyncio_mode = "auto"` from root pyproject.toml
- ✅ 8/8 nox sessions, 0 pytest warnings, 850+ tests, 0 failures
- ✅ All agent-facing docs synced

{% endraw %}
