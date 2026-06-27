---
---
# MCP E2E Testing Guide — MedMinder Interactive Browser Tests

This guide explains how to run interactive browser-based E2E tests on the MedMinder web apps using opencode's Playwright MCP tools. It covers server setup, mock data injection, and step-by-step testing recipes.

> **Who is this for?** Developers and QA engineers running tests manually via the opencode agent.

> **Always clean up after tests:** close the browser and shutdown servers (see [Cleanup](#cleanup)).

> **Playwright MCP browser runs in a container.** The server must bind to `0.0.0.0` (not `127.0.0.1`) so the browser can reach it. Both server scripts already bind to `0.0.0.0`. Use `http://localhost:<PORT>` when navigating.

---

## Quick Start

```bash
# Terminal 1: Start arduino_dash with mock data (no BMS — daemon shows Disconnected)
cd /home/weerdmonk/Projects/medminder
python3 e2e/servers/arduino_dash_server.py --mock --port 8765

# Terminal 2: Start arduino_dash with mock data + BMS daemon (daemon shows Connected)
python3 e2e/servers/arduino_dash_server.py --mock --bms --port 8765

# Terminal 3: Start medminder_dash with mock data
python3 e2e/servers/medminder_dash_server.py --mock --port 8766
```

Then in opencode, tell the agent:
> "Test the dashboard at http://localhost:8765"

The agent will load the `playwright-mcp-testing` skill and walk through the scenarios.

---

## Server Lifecycle

The Playwright MCP browser runs in an isolated container. It can only reach servers listening on `0.0.0.0` (all interfaces), not `127.0.0.1` (loopback only). Both server scripts bind to `0.0.0.0` so they work out of the box with MCP testing.

### Starting Servers

Both server scripts accept `--mock`, `--bms`, and `--port` flags:

```bash
# arduino_dash — empty state (no boards/sketches, no BMS)
python3 e2e/servers/arduino_dash_server.py
# → http://0.0.0.0:8765 (default port), daemon: Disconnected

# arduino_dash — with mock boards + sketch, no BMS
python3 e2e/servers/arduino_dash_server.py --mock
# → daemon badge shows "Daemon Disconnected"

# arduino_dash — with mock boards + BMS daemon
python3 e2e/servers/arduino_dash_server.py --mock --bms
# → daemon badge shows "Daemon Connected" (BMS auto-starts arduino-cli daemon)

# Custom port
python3 e2e/servers/arduino_dash_server.py --mock --port 9000

# medminder_dash — with mock boards + medicines, no BMS
python3 e2e/servers/medminder_dash_server.py --mock
# → http://0.0.0.0:8766

# medminder_dash — with mock boards + BMS
python3 e2e/servers/medminder_dash_server.py --mock --bms
```

### BMS Daemon (`--bms`)

The `--bms` flag starts the Board Management Service alongside the Flask dev server:

1. BMS spawns `arduino-cli daemon` (gRPC on `localhost:50051`) via `DaemonManager`
2. BMS listens on TCP `127.0.0.1:9090` and UDS `/tmp/board_mgr.sock`
3. The Flask app's PubSub connects to BMS and sets `_daemon_ready = True`
4. The UI daemon badge updates to show "Connected"

**Note:** `--bms` disables Flask debug mode (`use_reloader=False`) to prevent orphaned BMS processes on reloader forks. Changes to templates require a manual server restart.

**Cleanup:** The BMS subprocess is automatically terminated when the server exits (via `atexit` and `try/finally`).

### What `--mock` Injects

**arduino_dash:**

| Board | Port | FQBN | Hardware ID |
|-------|------|------|-------------|
| TestBoard Uno | `/dev/ttyTEST0` | `arduino:avr:uno` | `HW-TEST-001` |
| TestBoard Mega | `/dev/ttyTEST1` | `arduino:avr:mega` | `HW-TEST-002` |

Plus: one sketch entry (`mysketch`) in the upload registry, deployed to HW-TEST-001.

**medminder_dash:** Same boards plus three medicines:

| Medicine | Time | Enabled |
|----------|------|---------|
| Aspirin | 08:00 | ✅ |
| VitaminD | 12:30 | ✅ |
| Ibuprofen | 18:00 | ✅ |

### Why Daemonization?

The opencode agent runs commands via a **bash tool** that tracks processes by **session ID**. When a shell command completes or its timeout fires, the tool sends `SIGHUP` to every process in that session — regardless of process group. This means:

```bash
python3 server.py --mock
# → After tool timeout: session killed, server dies with it
```

The server scripts solve this with `_daemonize()`:

1. **`os.fork()`** — parent exits immediately (`os._exit(0)`). The bash tool sees a completed command and returns.
2. **`os.setsid()`** — child creates a **new session**, immune from the parent session's `SIGHUP`.
3. **`_redirect_io(logfile)`** — `dup2` stdout/stderr to a file (or `/dev/null`). The closed parent pipe never triggers `SIGPIPE`.

```
┌─ Tool session ───────────────────────────────────┐
│  bash (session leader)                            │
│    └── python3 server.py                          │
│          ├── fork ──► parent os._exit(0) ──►      │
│          │              tool returns OK           │
│          └── child (new session)                  │
│                os.setsid() ──► immune to SIGHUP   │
│                _redirect_io() ──► logs→file       │
│                Flask runs ──► serves forever      │
└───────────────────────────────────────────────────┘
```

Result: a plain `python3 server.py --mock` returns immediately and the server survives any bash tool timeout.

### Stopping Servers

Use the built-in `--stop` flag. No `lsof`, `kill`, or `pkill` needed.

```bash
# Stop arduino_dash (default pidfile: /tmp/arduino_dash_server.pid)
python3 e2e/servers/arduino_dash_server.py --stop

# Force-stop (SIGKILL, skip graceful SIGTERM)
python3 e2e/servers/arduino_dash_server.py --stop --force

# Custom pidfile
python3 e2e/servers/arduino_dash_server.py --stop --pidfile /tmp/my.pid

# Stop medminder_dash
python3 e2e/servers/medminder_dash_server.py --stop
```

The stop mechanism:
1. Reads PID from `/tmp/<script>.pid`
2. Sends SIGTERM
3. Polls every 100ms for up to 5s
4. Escalates to SIGKILL if process doesn't exit
5. Removes pidfile

### Disown and Background Jobs

The **`disown`** shell builtin removes a job from the shell's job table so it doesn't receive SIGHUP when the shell exits. Before daemonization, a common opencode workaround was:

```bash
bash(command="python3 server.py --mock &>/dev/null & disown", timeout=3000)
```

This was fragile:
- **`&`** backgrounds the process but keeps it in the same session — the bash tool's timeout still kills it
- **`&>/dev/null`** discards all output so you can't debug failures
- **`disown`** only removes the job from the *shell's* job table, not from the session — with session-based tracking it's ineffective
- **`timeout=3000`** gives a 3s window before SIGHUP kills everything — racing against the tool's process cleanup

The `_daemonize()` approach (fork + setsid + redirect) eliminates all of these: no `&`, no `disown`, no `&>/dev/null`, no special timeout needed.

### Script Architecture

Both server scripts are self-contained with identical lifecycle helpers and a CLI generated by `argparse`:

**Lifecycle helpers (duplicated in each script for zero dependencies):**

| Function | Role |
|----------|------|
| `_get_default_pidfile()` | Derives `/tmp/<script_name>.pid` from `__file__` |
| `_write_pidfile(path)` | Writes `os.getpid()` to the pidfile |
| `_remove_pidfile(path)` | Removes pidfile only if it still contains *our* PID (prevents stealing another instance's lock) |
| `_stop_server(pidfile, force)` | Reads PID, sends SIGTERM (or SIGKILL), polls 5s, escalates, cleans pidfile |
| `_daemonize(logfile)` | `os.fork()` → parent `os._exit(0)` → child `os.setsid()` + `SIGHUP_IGN` + `dup2` redirect |

**CLI flags:**

| Flag | Default | Purpose |
|------|---------|---------|
| `--mock` | off | Inject mock boards, sketches, medicines |
| `--bms` | off | Start Board Management Service daemon |
| `--port` | 8765 / 8766 | Bind port |
| `--production` | off | Disable Flask debug mode & reloader |
| `--pidfile` | `/tmp/<script>.pid` | Custom pidfile path |
| `--stop` | off | Stop a running server by pidfile |
| `--force` | off | With `--stop`: send SIGKILL immediately |
| `--logfile` | `/dev/null` | Capture stdout/stderr (Flask logs) |

**Execution order in `main()`:**

```
1. Parse args
2. --stop? → _stop_server(), exit
3. _daemonize() → parent exits, child continues (new session)
4. --mock? → inject mock state
5. --bms? → start BMS daemon, init PubSub
6. _write_pidfile()
7. atexit.register(_remove_pidfile)
8. app.run()
```

---

## Test Scenario Recipes

Each recipe below lists the exact opencode tool calls to make. The agent will execute these when you ask it to test.

### Recipe 1: Dashboard Empty State

**Goal**: Verify the dashboard loads and shows "No boards detected" when no boards are connected.

**Server**: `arduino_dash_server.py` (without `--mock`)

```
# Step 1: Navigate to dashboard
→ playwright_browser_navigate(url="http://localhost:8765/")

# Step 2: Capture page snapshot
→ playwright_browser_snapshot()

# Expected output:
# - Page title contains "Dashboard"
# - Navigation bar has "Dashboard" and "Admin" links
# - #board-grid contains "No boards detected" text
# - #daemon-badge shows "Daemon Disconnected"
```

### Recipe 2: Board Grid with Mock Data

**Goal**: Verify the board grid shows mock board cards with correct information.

**Server**: `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_snapshot()

# Check for:
# - Card with title "TestBoard Uno"
# - Subtitle "/dev/ttyTEST0"
# - Badge "Connected"
# - "Manage" link
# - A second card for "TestBoard Mega"
```

**Snapshots show:**
```
board-card:
  title: "TestBoard Uno"
  subtitle: "/dev/ttyTEST0 · arduino:avr:uno"
  badge: "Connected"
  link: "Manage" → /board/dev/ttyTEST0

board-card:
  title: "TestBoard Mega"
  subtitle: "/dev/ttyTEST1 · arduino:avr:mega"
  badge: "Connected"
  link: "Manage" → /board/dev/ttyTEST1
```

### Recipe 3: Admin Page

**Goal**: Verify the admin page loads with all sections.

**Server**: `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/admin")
→ playwright_browser_snapshot()

# Sections that should be visible:
# 1. Active Board selector (dropdown)
# 2. Sketch Upload card (with drag-drop zone labeled "Drop sketch files here")
# 3. Sketch selector (dropdown showing "mysketch")
# 4. Compile/Upload card
# 5. Live events card (collapsible)
```

### Recipe 4: Sketch Selector Shows Board Label

**Goal**: Verify the sketch selector includes the board assignment label.

**Server**: `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/admin")
→ playwright_browser_wait_for(text="mysketch")
→ playwright_browser_snapshot()

# The <option> should show:
# "mysketch (2026-06-19 05:30:00) [TestBoard Uno (/dev/ttyTEST0)]"
```

### Recipe 5: Daemon Status Badge — Disconnected

**Goal**: Verify the daemon status badge shows "Disconnected" when no BMS is running.

**Server**: `arduino_dash_server.py` (with or without `--mock`, without `--bms`)

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_snapshot()

# The daemon badge in the navbar should show:
# "○ Daemon Disconnected"
# With CSS class "daemon-off" (red/gray styling)

# Alternatively, fetch the badge directly:
→ playwright_browser_navigate(url="http://localhost:8765/daemon/status")
→ playwright_browser_snapshot()
# Shows: <span class="daemon-badge daemon-off">○ Daemon Disconnected</span>
```

### Recipe 5b: Daemon Status Badge — Connected (with BMS)

**Goal**: Verify the daemon status badge shows "Connected" when BMS is running.

**Server**: `arduino_dash_server.py --mock --bms`

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_snapshot()

# The daemon badge in the navbar should show:
# "● Daemon Connected"
# With CSS class "daemon-on" (green styling)

→ playwright_browser_navigate(url="http://localhost:8765/daemon/status")
→ playwright_browser_snapshot()
# Shows: <span class="daemon-badge daemon-on">● Daemon Connected</span>
```

### Recipe 6: Board Detail Page

**Goal**: Verify board detail page shows port info, compile/upload sections.

**Server**: `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/board/dev/ttyTEST0")
→ playwright_browser_snapshot()

# Expected sections:
# - Board header: "TestBoard Uno"
# - Port: "/dev/ttyTEST0"
# - FQBN: "arduino:avr:uno"
# - Connection status badge: "Connected"
# - Compile button (POST /board/dev/ttyTEST0/compile)
# - Upload button (POST /board/dev/ttyTEST0/upload)
# - Sketch selector
```

### Recipe 7: medminder_dash Home Page

**Goal**: Verify medminder_dash home page shows board grid.

**Server**: `medminder_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8766/")
→ playwright_browser_snapshot()

# Check for:
# - Board grid with mock boards
# - Navigation links
# - Daemon status badge
```

### Recipe 8: medminder_dash Medicine List via API

**Goal**: Verify the medicine API returns mock data.

**Server**: `medminder_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8766/api/medicines")
→ playwright_browser_evaluate(function="() => JSON.parse(document.body.innerText)")

# Should return:
# [
#   { "name": "Aspirin", "hour": 8, "minute": 0, "enabled": true },
#   { "name": "VitaminD", "hour": 12, "minute": 30, "enabled": true },
#   { "name": "Ibuprofen", "hour": 18, "minute": 0, "enabled": true },
# ]
```

### Recipe 9: medminder_dash Admin Page

**Goal**: Verify admin page has all management sections.

**Server**: `medminder_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8766/admin")
→ playwright_browser_snapshot()

# Sections:
# 1. Board selector
# 2. Medicine management (list + add button)
# 3. Sketch upload area
# 4. Compile/Upload card
```

### Recipe 10: 404 Error Page

**Goal**: Verify the app handles unknown routes gracefully.

**Server**: either, with or without `--mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/nonexistent")
→ playwright_browser_snapshot()

# Flask's default 404 page is shown, or a custom error template.
```

---

## Cleanup

Always close the browser and shutdown servers after tests — even if a test fails or is interrupted.

```
# Close the Playwright browser
→ playwright_browser_close()

# Shutdown both servers (using built-in --stop flag)
→ bash(command="python3 e2e/servers/arduino_dash_server.py --stop; python3 e2e/servers/medminder_dash_server.py --stop")

# Or shutdown a specific server:
→ bash(command="python3 e2e/servers/arduino_dash_server.py --stop")
```

The `--stop` flag handles all cleanup:
1. Reads PID from `/tmp/<script>.pid`
2. Sends SIGTERM (graceful shutdown) or SIGKILL (`--force`)
3. Polls every 100ms for up to 5s to confirm exit
4. Escalates to SIGKILL if process doesn't respond to SIGTERM
5. Removes the pidfile
6. BMS subprocess terminates automatically via `atexit` + `try/finally` handlers

**If the server was force-killed** (SIGKILL or `kill -9`) and the pidfile was left behind, running `--stop` will detect the stale PID via `ProcessLookupError`, remove the pidfile, and report the cleanup.

**If pidfile was lost** (e.g. `/tmp` was cleaned), run `--stop` to confirm no stale pidfile exists, then restart.

**Orphaned BMS cleanup:** If the server was killed before its BMS cleanup handler ran, orphaned `board_manager` processes can be cleaned:
```bash
pkill -f "python -m board_manager"
```

---

## Advanced: WebSocket Testing

> Requires `flask-sock` installed (optional dependency).

The WebSocket endpoint at `/ws/board-events` pushes board events to connected clients. Without BMS running, the WS will connect but receive no events.

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_wait_for(time=2)
# WS connection is established automatically via HTMX WS extension
```

The connection is initiated by `<div id="event-feed" hx-ext="ws" ws-connect="/ws/board-events">` in `base.html`.

---

## Advanced: Triggering `board-changed` Event

The `board-changed` custom event triggers HTMX reloads of board grid, sketch selector, compile-upload card, and board selector. Simulate it:

```
→ playwright_browser_evaluate(function="() => {
    htmx.trigger('body', 'board-changed');
    return 'Event fired';
}")
```

Then verify partials re-fetched via snapshot or network activity.

---

## Test Sketch for Compile/Upload Scenarios

A minimal Arduino sketch lives at `e2e/test-sketch/` for end-to-end compile
and upload verification. See [`e2e/test-sketch/README.md`](../test-sketch/README.md).

### Purpose

The sketch contains only `void setup() {} void loop() {}` — no board-specific
logic. It validates that the compile pipeline accepts `.ino` files and produces
valid binary output.

### Usage in Scenarios

```
# Step 1: Navigate to admin page
→ playwright_browser_navigate(url="http://localhost:8765/admin")

# Step 2: Select a board in the Active Board selector
# Step 3: Click Compile (sketch path is pre-filled or available via admin)

# Step 4: Verify compile success via snapshot
→ playwright_browser_snapshot()

# Step 5: Click Upload to deploy to the selected board
```

### Path

```
e2e/test-sketch/
├── README.md          # Full documentation
└── test-sketch.ino    # Minimal Arduino sketch
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection refused` | Server not started | Run the server script first |
| `net::ERR_CONNECTION_REFUSED` from Playwright browser | Server bound to `127.0.0.1` — MCP browser (container) can't reach loopback | Use `0.0.0.0` (already set in both server scripts). Navigate with `localhost` not `127.0.0.1` |
| Mock boards not showing | Started without `--mock` | Kill and restart with `--mock` |
| Daemon badge shows "Disconnected" when BMS is running | BMS takes a moment to start; PubSub hasn't connected yet | Wait a few seconds, then refresh or wait for `--bms` flag to complete |
| Daemon badge shows "Disconnected" without `--bms` | Expected — no BMS running | This is the correct state when testing without BMS. Start with `--bms` to test connected state |
| BMS fails to start | `arduino-cli` not found or gRPC port 50051 in use | Ensure `arduino-cli` is on PATH. Kill any stale `arduino-cli daemon` processes |
| Orphaned BMS process after force-kill | Server was killed before BMS cleanup handler ran | `pkill -f "python -m board_manager"` to clean up |
| Empty sketch selector | UA mismatch | The mock uses IP `127.0.0.1` + UA `playwright-test` |
| `flask_sock` import error | Package not installed | `pip install flask-sock` (optional, WS tests only) |
| Port already in use | Previous server still running | `python3 e2e/servers/arduino_dash_server.py --stop` |
| Debug restart looping | Flask debug mode | Expected; wait briefly after start. Use `--bms` to disable debug reloader |
| Snapshot missing elements | HTMX loaded after snapshot | Wait first: `playwright_browser_wait_for(time=2)` |

---

## File Reference

| File | Purpose |
|------|---------|
| `e2e/agent_tools/GUIDE.md` | This file — project-specific testing guide |
| `e2e/agent_tools/SKILL.md` | Generic MCP testing skill (project-agnostic) |
| `e2e/agent_tools/AGENT.md` | Sub-agent definition for `@playwright-mcp-testing` |
| `e2e/agent_tools/COMMAND.md` | Command definition for `/playwright-mcp-testing` |
| `e2e/servers/arduino_dash_server.py` | Start arduino_dash with `--mock` |
| `e2e/servers/medminder_dash_server.py` | Start medminder_dash with `--mock` |
| `.opencode/skills/playwright-mcp-testing/SKILL.md` | Installed skill (copy of agent_tools/SKILL.md) |
| `.opencode/agents/playwright-mcp-testing.md` | Installed agent (copy of agent_tools/AGENT.md) |
| `.opencode/commands/playwright-mcp-testing.md` | Installed command (copy of agent_tools/COMMAND.md) |
| `e2e/test-sketch/` | Minimal Arduino sketch for compile/upload E2E tests |
