---
---
{% raw %}
# Implementation Plan — Phase 101 (cont.): Standalone Build Portability Fix

**Date**: 2026-06-24 21:00
**Status**: 🔄 In Progress

## Motivation

Phase 101 replaced hardcoded paths in `pyoxidizer.bzl` with `@REPO_ROOT@` placeholders, fixed `pip_download()` → `pip_install()`, and added `simple-websocket` dep. However, those changes were **never committed to git**. The `build_standalone.sh` RETURN trap runs `git checkout -- <bzl_file>` after each build, restoring the original hardcoded-path versions. Three issues remain in the tracked files:

1. **Non-portable absolute paths** — `/home/weerdmonk/Projects/medminder/...` hardcoded in all 3 `.bzl` files
2. **`pip_download()` for local wheels** — Both dashboard configs use `pip_download()` which only works with PyPI indexes; local `.whl` files are likely silently skipped
3. **Missing `simple-websocket>=1.0.0`** — Dashboard configs don't bundle the WebSocket transport dependency

## Changes per File

### `scripts/pyoxidizer/arduino-dash/pyoxidizer.bzl`
- Prefix all 5 local wheel paths with `@REPO_ROOT@/` + relative path
- Change `pip_download()` → `pip_install()` for local wheels
- Add `"simple-websocket>=1.0.0"` to the PyPI `pip_install()` block

### `scripts/pyoxidizer/medminder-dash/pyoxidizer.bzl`
- Same 3 changes as arduino-dash

### `scripts/pyoxidizer/board-manager/pyoxidizer.bzl`
- Prefix both local wheel paths with `@REPO_ROOT@/` + relative path
- Already uses `pip_install()` — no change needed
- No `simple-websocket` — not a dashboard app

### `scripts/pyoxidizer/board-manager/_repo_root.bzl` (stale artifact)
- Delete — created during Phase 101 experimentation with `load()`, which failed with CP04

## Build Script is Already Correct

`scripts/build_standalone.sh` already has:
- `sed -i "s|@REPO_ROOT@|${REPO_ROOT}|g"` — substitutes placeholder before each build
- `trap cleanup RETURN` — runs `git checkout` to restore placeholders after each build
- Explicit `git checkout` before `die()` — catches exit paths (RETURN trap skipped on exit)

No changes needed to the build script itself.

## Quantums

| Q | Scope | Key Change | Status |
|---|-------|------------|--------|
| Q1 | 3 pyoxidizer.bzl files | @REPO_ROOT@ + pip_install + simple-websocket; committed as e98b878 | ✅ |
| Q2 | Build standalone binaries | `nox -s all_builds` + `./scripts/build_standalone.sh` | ✅ |
| Q3 | Verification | Smoke test + module/template/dep audit for all 3 binaries | ✅ |
| Q4 | Agent-facing docs | Update IMPLEMENTATION_*, JOURNAL, CODEBASE_REFERENCE | ✅ |

## Rollback

Before committing: `git checkout -- scripts/pyoxidizer/*/pyoxidizer.bzl` restores hardcoded paths. After committing: `git revert HEAD` undoes the commit.
{% endraw %}
