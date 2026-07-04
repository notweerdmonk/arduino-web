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
{% endraw %}
