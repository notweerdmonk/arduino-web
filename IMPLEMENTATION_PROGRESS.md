---
---
{% raw %}
# Implementation Progress — Phase 100c: Fix Console Errors

**Date**: 2026-06-24 17:57

## Phase 100c — ✅ COMPLETED

## Milestones

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Fix idiomorph CDN in arduino_dash base.html | ✅ | `idiomorph/dist/idiomorph-ext.js` |
| Q2 | Fix idiomorph CDN in medminder_dash base.html | ✅ | Same URL change |
| Q3 | Add simple-websocket to arduino_dash pyproject.toml | ✅ | Line 14 |
| Q4 | Add simple-websocket to medminder_dash pyproject.toml | ✅ | Line 15 |
| T1 | Verify idiomorph CDN resolves (HTTP 200) | ✅ | `curl -sIL` → HTTP 200 |
| T2 | Verify old CDN returns 404 | ✅ | `curl -sIL` → HTTP 404 |
| T3 | Verify pyproject.toml deps | ✅ | Both files have dep |
| T4 | Run nox tests for regressions | ✅ | Same pre-existing failures (no regressions) |
| D1 | IMPLEMENTATION_JOURNAL.md update | ✅ | Detailed entry |
| D2 | JOURNAL.md update | ✅ | Brief entry |
| D3 | CODEBASE_REFERENCE.md update | ✅ | Phase 100c section |
| D4 | TESTING docs update | ✅ | All 4 docs updated |
| D5 | Documentation skill | ⬜ | |

## Key Decisions

1. **idiomorph CDN path**: Use `idiomorph/dist/idiomorph-ext.js` (the htmx extension file from the idiomorph package) rather than embedding the idiomorph core directly. The `-ext.js` suffix registers itself as `htmx.defineExtension("morph", ...)`, which is what the templates use via `hx-ext="morph"`.
2. **simple-websocket over gevent-websocket**: `simple-websocket` works with sync WSGI servers (Flask dev server + gunicorn sync workers) without changing `worker_class` in gunicorn config. `gevent-websocket` would require switching to `gevent` workers.
3. **Minimal version pin**: `>=1.0.0` is sufficient — flask-sock 0.7.x requires simple-websocket 1.0+.
{% endraw %}
