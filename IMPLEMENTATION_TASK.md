---
---
{% raw %}
# Implementation Task — Phase 100c: Fix Console Errors

**Date**: 2026-06-24 17:57

## Task Breakdown

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Fix idiomorph CDN URL in arduino_dash base.html | ✅ | `htmx.org/dist/ext/idiomorph.js` → `idiomorph/dist/idiomorph-ext.js` |
| Q2 | Fix idiomorph CDN URL in medminder_dash base.html | ✅ | Same URL change |
| Q3 | Add `simple-websocket>=1.0.0` to arduino_dash pyproject.toml | ✅ | Inserted after `flask-sock>=0.7.0` |
| Q4 | Add `simple-websocket>=1.0.0` to medminder_dash pyproject.toml | ✅ | Inserted after `flask-sock>=0.7.0` |
| T1 | Verify idiomorph CDN resolves (HTTP 200) | ✅ | `curl -sIL` → HTTP 200 |
| T2 | Verify old CDN returns 404 | ✅ | `curl -sIL` → HTTP 404 |
| T3 | Verify pyproject.toml deps | ✅ | Both files have `simple-websocket>=1.0.0` |
| T4 | Run nox tests for regressions | ✅ | Same pre-existing failures (no new regressions) |
| D1 | Update IMPLEMENTATION_JOURNAL.md | ✅ | Detailed entry |
| D2 | Update JOURNAL.md | ✅ | Brief entry |
| D3 | Update CODEBASE_REFERENCE.md | ✅ | Phase 100c section |
| D4 | Update TESTING docs (JOURNAL, PROGRESS, TASK, PLAN) | ✅ | All 4 docs updated |
| D5 | Run documentation skill | ⬜ | User-facing docs |

## Detailed Tasks

### Q1 — arduino_dash base.html idiomorph URL

- [ ] Change script `src` from `https://unpkg.com/htmx.org/dist/ext/idiomorph.js` to `https://unpkg.com/idiomorph/dist/idiomorph-ext.js`

### Q2 — medminder_dash base.html idiomorph URL

- [ ] Same change as Q1

### Q3 — arduino_dash pyproject.toml

- [ ] Add `"simple-websocket>=1.0.0",` after `"flask-sock>=0.7.0",`

### Q4 — medminder_dash pyproject.toml

- [ ] Add `"simple-websocket>=1.0.0",` after `"flask-sock>=0.7.0",`

### T1-T4 — Verification

- [ ] T1: New idiomorph CDN returns HTTP 200
- [ ] T2: Old idiomorph CDN returns HTTP 404
- [ ] T3: simple-websocket appears in both pyproject.toml files
- [ ] T4: nox tests pass (no regressions)
{% endraw %}
