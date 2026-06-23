---
---
{% raw %}
# Implementation Task — Phase 100: Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14

## Task Breakdown

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1a | arduino_dash — `_daemonize(logfile)`, `--logfile`, `--pidfile`, `--stop`, `--force` | ✅ | |
| Q1b | arduino_dash — setsid + redirect in daemonize() | ✅ | |
| Q1c | arduino_dash — stale pidfile + ProcessLookupError handling | ✅ | |
| Q2 | medminder_dash — same changes + fix `--stop` ordering | ✅ | |
| Q3a | Test: arduino_dash survival | ✅ | HTTP 200 |
| Q3b | Test: `--stop` cleanup | ✅ | |
| Q3c | Test: `--logfile` capture | ✅ | 571 bytes |
| Q3d | Test: medminder_dash | ✅ | survival, log, --stop |
| D1 | Update CODEBASE_REFERENCE.md | ✅ | Add Phase 100 section |
| D2 | Update JOURNAL.md | ✅ | Brief entry |
| D3 | Update IMPLEMENTATION_JOURNAL.md | ✅ | Detailed entry |
| D4 | Update TESTING docs | ✅ | Results in TESTING_JOURNAL.md + PROGRESS.md |

## Detailed Tasks

### Q1 — arduino_dash_server.py

- [ ] Remove `_daemonize()` function (fork-based, superseded by setpgid + redirect)
- [ ] Add `_redirect_io(logfile)` function — closes stdin, dup2 stdout/stderr
- [ ] Add `--logfile` CLI argument
- [ ] Replace `_daemonize()` call with: `os.setpgid(0, 0)` (try/except) + `signal.signal()` + `_redirect_io()`
- [ ] Verify `--stop` runs before setpgid/redirect (already correct)

### Q2 — medminder_dash_server.py

- [ ] Same changes as Q1
- [ ] Fix ordering: `--stop` check should come before setpgid (currently reversed)

### Q3 — Integration Tests

- [ ] Kill any leftover servers
- [ ] Start arduino_dash with `python3 script.py --mock --production`, verify HTTP 200 in next invocation
- [ ] Test `--logfile` capture
- [ ] Test `--stop` cleanup
- [ ] Repeat for medminder_dash on port 8766
{% endraw %}
