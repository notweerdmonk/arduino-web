---
---
{% raw %}
# Implementation Task — Phase 101 (cont.): Standalone Build Portability Fix

**Date**: 2026-06-24 21:00

## Task Breakdown

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Fix & commit pyoxidizer.bzl (3 files) + clean stale artifacts | ✅ | @REPO_ROOT@, pip_install, simple-websocket — committed as e98b878 |
| Q2 | Build wheels + standalone binaries | ✅ | `nox -s all_builds` → `./scripts/build_standalone.sh` |
| Q3 | Verify bundles | ✅ | Smoke test + module/template/dep audit |
| D1 | Update IMPLEMENTATION_JOURNAL.md | ✅ | Appended Q2+Q3 continuation entry |
| D2 | Update JOURNAL.md | ✅ | Appended Phase 101 continuation entry |
| D3 | Update CODEBASE_REFERENCE.md | ✅ | Added continuation note with commit `e98b878` ref |
| D4 | Update IMPLEMENTATION_PLAN / TASK / PROGRESS | ✅ | All Q2-Q4/D1-D6 marked complete |
| D5 | Update TESTING_* docs | ✅ | Already complete |
| D6 | Update REVIEW_* docs | ✅ | Already complete |

## Detailed Tasks

### Q1 — Fix pyoxidizer.bzl files

- [x] arduino-dash/pyoxidizer.bzl: replace hardcoded paths with @REPO_ROOT@ prefix
- [x] arduino-dash/pyoxidizer.bzl: change `pip_download()` → `pip_install()`
- [x] arduino-dash/pyoxidizer.bzl: add `"simple-websocket>=1.0.0"`
- [x] medminder-dash/pyoxidizer.bzl: replace hardcoded paths with @REPO_ROOT@ prefix
- [x] medminder-dash/pyoxidizer.bzl: change `pip_download()` → `pip_install()`
- [x] medminder-dash/pyoxidizer.bzl: add `"simple-websocket>=1.0.0"`
- [x] board-manager/pyoxidizer.bzl: replace hardcoded paths with @REPO_ROOT@ prefix
- [x] Delete stale `scripts/pyoxidizer/board-manager/_repo_root.bzl`
- [x] git add + commit .bzl changes (user committed as e98b878)

### Q2 — Build wheels + standalone binaries

- [ ] `nox -s all_builds` — exit 0
- [ ] Check all 6 wheels exist in their dist dirs
- [ ] `./scripts/build_standalone.sh` — all 3 apps built successfully
- [ ] dist-standalone/ has all 3 app dirs with binaries

### Q3 — Verification

- [ ] Smoke test: `<binary> --help` for all 3 apps
- [ ] New modules present in arduino-dash dist
- [ ] New modules present in medminder-dash dist
- [ ] Templates present in both dashboard dists
- [ ] simple-websocket present in both dashboard dists
- [ ] Static files (style.css, favicons) present in both dashboard dists
- [ ] Orphan templates (deploy.html, admin_sketch_dir.html) present in medminder-dash (expected)
{% endraw %}
