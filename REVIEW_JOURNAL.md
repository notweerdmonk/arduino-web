---
---
{% raw %}
# Review Journal — Phase 102: Fix Pre-Existing Test Failures

## 2026-06-25 09:10 — Phase 102: Fix Pre-Existing Test Failures

### Review Summary

Two failing nox sessions were fixed: `tests(arduino_dash)` (111 errors → 119 pass) and `tests(medminder_dash)` (1 failure → 186 pass, 1 skip). The fixes touched 5 files across 3 modules.

### Key Findings

1. **Missing re-exports in app.py**: The `Re-export state names for test compatibility` comment at `app.py:77` was incomplete — only 2 names from `sketch_management.py` were re-exported. The test expected 14 state variables, 9 pubsub functions, and 3 more sketch_management functions. All 28 names now properly re-exported.

2. **UPLOAD_BASE_DIR production bug**: Phase 69 (XDG path refactoring) moved `UPLOAD_BASE_DIR` from `state.py` to `settings.py` but left 9 references to `state.UPLOAD_BASE_DIR` in 3 source files. This silently broke all upload/sketch operations in arduino_dash when running outside tests (test mocking hid the issue via `patch`).

3. **Wrong import in api_routes.py:82**: Lazy import `from arduino_dash.html_routes import _warm_upload_registry` pointed to the wrong module. The function is defined in `sketch_management.py:98`.

4. **Brittle test assertions**: 3 assertions across 2 dashboards expected HTML attributes on the same line. Bulk djlint reformatting (commit `3c5fb7c`) split them across lines. Fixed by using id-only checks.

### Files Reviewed

| File | Verdict | Notes |
|------|---------|-------|
| `arduino_dash/.../arduino_dash/app.py` | ✅ | 28 names re-exported, no circular imports |
| `arduino_dash/.../arduino_dash/state.py` | ✅ | `UPLOAD_BASE_DIR` re-exported from settings |
| `arduino_dash/.../arduino_dash/api_routes.py` | ✅ | Import points to correct module |
| `arduino_dash/.../tests/test_app.py` | ✅ | 1 assertion relaxed from full tag to id-only |
| `medminder_dash/.../tests/test_routes.py` | ✅ | 1 redundant assertion removed |

### Verdict

✅ **Phase 102 is approved and complete.** All 8 nox sessions pass with 0 failures and 0 errors. A production bug (missing `UPLOAD_BASE_DIR` in `state.py`) and a wrong import path were discovered and fixed alongside the test-specific issues.

## Previous: Phase 101 Review

... (previous Phase 101 review content preserved in git) ...

### Key Learnings

1. **`__file__` not available** in PyOxidizer's Starlark dialect — `error[CM01]: Variable '__file__' not found`. `load()` from another `.bzl` file also fails (`CP04: IOError: No such file or directory`). Solution: `@REPO_ROOT@` placeholder + `sed -i` in build script.

2. **`pip_download()` only works for PyPI** — local wheel paths require `pip_install()`. Both dashboard configs had `pip_download()` for local wheels that silently produced no results.

3. **RETURN trap** — `trap cleanup RETURN` handles normal function returns, but `exit` inside `die()` skips the RETURN trap. Explicit `git checkout` before `die` calls is required.

4. **Orphan templates remain** — `deploy.html`, `admin_sketch_dir.html` still in medminder-dash dist. Expected — user confirmed they should stay.

### Verification

| Check | Result |
|-------|--------|
| All 3 binaries built (51MB each) | ✅ |
| arduino-dash --help | ✅ Exit 0 |
| medminder-dash --help | ✅ Exit 0 |
| board-manager --help | ✅ Exit 0 |
| 7 modules in arduino-dash bundle | ✅ |
| 7 modules in medminder-dash bundle | ✅ |
| All templates + partials (both dashboards) | ✅ |
| Static files (style.css + favicons, both) | ✅ |
| simple-websocket dep (both dashboards) | ✅ |
| All project & workflow docs updated | ✅ |

### Verdict

✅ **Phase 101 is approved and complete.** All 3 binaries rebuilt from current source. Modules, templates, static files, and `simple-websocket` dep verified. Hardcoded paths replaced with `@REPO_ROOT@` placeholder + `sed` substitution. `pip_download()` → `pip_install()` for local wheels. All documentation updated.
{% endraw %}