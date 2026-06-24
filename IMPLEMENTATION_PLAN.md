---
---
{% raw %}
# Implementation Plan — Phase 100c: Fix Console Errors (idiomorph.js 404 + WS Invalid Frame Header)

**Date**: 2026-06-24 17:57
**Status**: Completed

## Motivation

During Playwright E2E testing, two non-blocking console errors were observed:

1. **idiomorph.js 404** — `<script src="https://unpkg.com/htmx.org/dist/ext/idiomorph.js">` returns HTTP 404. The idiomorph JS is a separate npm package (`idiomorph`) and is no longer bundled inside `htmx.org` since htmx 2.x.
2. **WebSocket "Invalid frame header"** — `ws://localhost:8766/ws/board-events` fails because `flask-sock` lacks a WebSocket transport implementation. `simple-websocket` provides WS support for Flask dev server and gunicorn sync workers.

## Root Cause Analysis

### Bug 1: idiomorph.js 404

```
Current (broken):     https://unpkg.com/htmx.org/dist/ext/idiomorph.js  → 404
Correct:              https://unpkg.com/idiomorph/dist/idiomorph-ext.js → 200
```

- htmx 1.x bundled extensions inside `htmx.org/dist/ext/`. htmx 2.x moved all extensions to separate npm packages.
- The idiomorph extension is now published as the `idiomorph` npm package.
- The htmx extension file is at `idiomorph/dist/idiomorph-ext.js`.
- Both dashboards load the wrong URL identically (copy-pasted during Phase 97 Q2).

### Bug 2: WS Invalid Frame Header

```
Browser → ws://localhost:8766/ws/board-events
  → flask-sock middleware (no simple-websocket installed)
  → Werkzeug/gunicorn sync worker returns non-101 HTTP response
  → Browser: "Invalid frame header"
```

- `flask-sock` creates a `Sock(app)` instance wrapping `app.wsgi_app` with a middleware.
- The middleware intercepts WebSocket upgrade requests and needs a WS transport:
  - `simple-websocket` — works with sync servers (Flask dev, gunicorn sync)
  - `gevent-websocket` — works with gunicorn gevent worker
- Without either, the middleware doesn't properly handle the upgrade, returning a garbled response.
- `simple-websocket` is the right choice: zero-config, no worker class change needed.
- Neither `pyproject.toml` listed this dependency — it was only accidentally installed via transitive deps in some envs.

## Architecture

Minimal change — no architectural impact:
- **idiomorph**: Just a URL string swap in 2 template files.
- **simple-websocket**: Just a line addition in 2 `pyproject.toml` files (runtime dep).

### CDN URL Diff

```
- src="https://unpkg.com/htmx.org/dist/ext/idiomorph.js"
+ src="https://unpkg.com/idiomorph/dist/idiomorph-ext.js"
```

### Dependency Diff

```toml
dependencies = [
    ...
    "flask-sock>=0.7.0",
+   "simple-websocket>=1.0.0",
    ...
]
```

## Quantums

| Q | Scope | Files | Key Change |
|---|-------|-------|------------|
| 1 | arduino_dash base.html | `arduino_dash/.../templates/base.html:9` | Fix idiomorph CDN URL |
| 2 | medminder_dash base.html | `medminder_dash/.../templates/base.html:13` | Fix idiomorph CDN URL |
| 3 | arduino_dash pyproject.toml | `arduino_dash/.../pyproject.toml:13` | Add `simple-websocket>=1.0.0` |
| 4 | medminder_dash pyproject.toml | `medminder_dash/.../pyproject.toml:14` | Add `simple-websocket>=1.0.0` |

## Test Plan

| Test | Method | Pass Criteria |
|------|--------|--------------|
| Idiomorph CDN resolves | `webfetch https://unpkg.com/idiomorph/dist/idiomorph-ext.js` | HTTP 200 |
| Old CDN returns 404 | `webfetch https://unpkg.com/htmx.org/dist/ext/idiomorph.js` | HTTP 404 |
| Pyproject deps | `grep simple-websocket */python/*/pyproject.toml` | 2 matches |
| No regressions | `nox -s all_tests` | All sessions pass |

## Rollback

Each change is atomic and easily reversible:
- **Q1/Q2**: Revert the URL string in the two base.html files.
- **Q3/Q4**: Remove the `simple-websocket` line from the two pyproject.toml files.
{% endraw %}
