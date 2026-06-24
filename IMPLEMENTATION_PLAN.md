---
---
{% raw %}
# Implementation Plan — Phase 100: Server Script Process Lifecycle (Disown & Cleanup)

**Date**: 2026-06-22 16:14
**Status**: ✅ Complete

## Motivation

The E2E test servers (`e2e/servers/arduino_dash_server.py` and `medminder_dash_server.py`) die between bash tool invocations because:
1. The tool sends SIGHUP to the entire process group when a shell command exits
2. `disown` removes the job from bash's job table but does NOT protect against process-group-level signals
3. The previous workaround (`&>/dev/null & disown` with `timeout=3000`) is fragile and race-condition dependent

**Goal**: Run any of these without shell hacks:
```bash
python3 script.py --mock --production                         # survives bash exit
python3 script.py --mock --production --logfile /tmp/log.txt  # same, with logs
python3 script.py --stop                                       # clean shutdown
python3 script.py --stop --force                               # force kill
```

## Root Cause (from TESTING_JOURNAL.md — Entry 3)

1. The bash tool launches a shell session and tracks the **entire process group**.
2. When a command uses `&`, the shell forks a background child that remains in the same process group.
3. When the bash tool's shell command completes or its timeout expires, the tool sends **SIGHUP → whole process group**.
4. `disown` removes the job from the shell's job table but does **not** protect against the tool's process-group-level signal.
5. The short-timeout workaround relied on a race condition where the foreground exited before SIGHUP propagated.

## Architecture Evolution

### Iteration 1: `os.setpgid(0, 0)` + shell hacks (rejected)
- User wants no `&`, `disown`, `&>/dev/null`, or special timeouts

### Iteration 2: `os.setpgid(0, 0)` + `_redirect_io()` (rejected)
- `os.setpgid(0, 0)` changes process GROUP but not SESSION
- The bash tool tracks processes by SESSION, not PGID
- When the shell session exits, SIGHUP is sent to ALL processes in the session regardless of PGID
- The server still dies between bash invocations

### Iteration 3 (final): `os.fork()` + `os.setsid()` + `_redirect_io()` ✅

```
┌──────────────────────────────────────────────────────────┐
│                  Process Model                           │
│                                                          │
│  bash tool (session leader)                              │
│    │ SIGHUP on exit (to entire session)                  │
│    └── bash (shell session)                              │
│          └── python3 (our script)                        │
│                ├── fork                                  │
│                ├── parent: os._exit(0) ──▶ tool returns  │
│                └── child: os.setsid() ──▶ new session    │
│                      ├── SIGHUP ignored (new session)    │
│                      ├── _redirect_io() → file|/dev/null │
│                      ├── Flask serves forever            │
│                      └── logs captured in --logfile      │
└──────────────────────────────────────────────────────────┘
```

Key insight: `os.setpgid(0, 0)` changes only the process GROUP, but the tool tracks by SESSION. When the session leader (bash) dies, SIGHUP reaches every process in the session. Only `os.setsid()` (which requires a prior `fork()`) creates a new session. The fork's parent exits immediately so the tool's pipe closes and the command returns. The child redirects stdout/stderr to capture logs.

## CLI Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--pidfile` | str | `/tmp/<script>.pid` | Path to write PID on startup |
| `--logfile` | str | (none → /dev/null) | Path to redirect Flask stdout/stderr |
| `--stop` | flag | — | Stop a running server by its PID file |
| `--force` | flag | — | With `--stop`: skip SIGTERM, send SIGKILL immediately |

## Stop Flow

```
--stop --force?
  ├─ YES → os.kill(pid, SIGKILL)
  └─ NO  → os.kill(pid, SIGTERM)
            └─ poll os.kill(pid, 0) every 100ms, max 5s
               ├─ process gone → ok
               └─ timeout → os.kill(pid, SIGKILL)
            └─ remove pidfile, exit(0)
```

## Startup Flow

```
1. Parse args
2. --stop? → handle and exit(0)
3. os.fork()
4. Parent: os._exit(0)        ← immediate exit → pipe closes → tool returns
5. Child:  os.setsid()        ← new session, immune to parent SIGHUP
6. signal(SIGHUP, SIG_IGN)    ← belt-and-suspenders
7. _redirect_io(logfile)      ← dup2 stdout/stderr to file
8. Inject mock state (if --mock)
9. Start BMS (if --bms)
10. Write pidfile
11. app.run()                  ← Flask serves forever
```

## Quantums

| Q | Scope | Files | Key Changes |
|---|-------|-------|-------------|
| Q1 | arduino_dash server | `arduino_dash_server.py` | Remove `_daemonize()`, add `_redirect_io()`, `--logfile`, `os.setpgid()`, fix `--stop` ordering |
| Q2 | medminder_dash server | `medminder_dash_server.py` | Same changes as Q1 |
| Q3 | Integration test | — | Start both servers, verify survival, `--stop` cleanup, log capture |

## Test Plan

| Test | Method | Pass Criteria |
|------|--------|--------------|
| Server survives bash exit | `python3 script.py --mock --production` then `curl` in next invocation | HTTP 200 |
| Log capture | `python3 script.py --logfile /tmp/x.log` then check file | Log file exists and contains Flask output |
| --stop kills server | `python3 script.py --stop` after starting | Server no longer reachable |
| --force kills stuck server | Same, but with unresponsive process | Process terminated (os.kill with SIGKILL) |
| PID file cleanup | Check after --stop | PID file removed |
| No stale pidfile on fresh start | Start twice | Second start succeeds |
{% endraw %}
