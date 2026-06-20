# MCP E2E Testing Guide — MedMinder Interactive Browser Tests

This guide explains how to run interactive browser-based E2E tests on the MedMinder web apps using opencode's Playwright MCP tools. It covers server setup, mock data injection, and step-by-step testing recipes.

> **Who is this for?** Developers and QA engineers running tests manually via the opencode agent. For automated `@playwright/test` specs, see the shelved files in `e2e/specs/`.

> **Always clean up after tests:** close the browser and shutdown servers (see [Cleanup](#cleanup)).

> **OpenCode integration:** This guide is also available as a project skill + agent + command. See `e2e/agent_tools/` for the source files, `.opencode/skills/playwright-mcp-testing/`, `.opencode/agents/playwright-mcp-testing.md`, and `.opencode/commands/playwright-mcp-testing.md` for installed copies.

---

## Quick Start

```bash
# Terminal 1: Start arduino_dash with mock data
cd /home/weerdmonk/Projects/medminder
python3 e2e/servers/arduino_dash_server.py --mock --port 8765

# Terminal 2: Start medminder_dash with mock data
python3 e2e/servers/medminder_dash_server.py --mock --port 8766
```

Then in opencode, tell the agent:
> "Test the dashboard at http://127.0.0.1:8765"

The agent will load the `mcp-e2e-testing` skill and walk through the scenarios.

---

## Server Lifecycle

### Starting Servers

Both server scripts accept `--mock` and `--port` flags:

```bash
# arduino_dash — empty state (no boards/sketches)
python3 e2e/servers/arduino_dash_server.py
# → http://127.0.0.1:8765 (default port)

# arduino_dash — with mock boards + sketch
python3 e2e/servers/arduino_dash_server.py --mock

# Custom port
python3 e2e/servers/arduino_dash_server.py --mock --port 9000

# medminder_dash — with mock boards + medicines
python3 e2e/servers/medminder_dash_server.py --mock
# → http://127.0.0.1:8766
```

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

### Stopping Servers

```bash
# By port
kill $(lsof -ti:8765) 2>/dev/null
kill $(lsof -ti:8766) 2>/dev/null

# By process name
pkill -f arduino_dash_server.py
pkill -f medminder_dash_server.py

# Verify no test servers remain
lsof -i:8765 -i:8766
```

---

## Test Scenario Recipes

Each recipe below lists the exact opencode tool calls to make. The agent will execute these when you ask it to test.

### Recipe 1: Dashboard Empty State

**Goal**: Verify the dashboard loads and shows "No boards detected" when no boards are connected.

**Server**: `arduino_dash_server.py` (without `--mock`)

```
# Step 1: Navigate to dashboard
→ playwright_browser_navigate(url="http://127.0.0.1:8765/")

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
→ playwright_browser_navigate(url="http://127.0.0.1:8765/")
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
→ playwright_browser_navigate(url="http://127.0.0.1:8765/admin")
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
→ playwright_browser_navigate(url="http://127.0.0.1:8765/admin")
→ playwright_browser_wait_for(text="mysketch")
→ playwright_browser_snapshot()

# The <option> should show:
# "mysketch (2026-06-19 05:30:00) [TestBoard Uno (/dev/ttyTEST0)]"
```

### Recipe 5: Daemon Status Badge

**Goal**: Verify the daemon status badge shows "Disconnected" when no BMS is running.

**Server**: `arduino_dash_server.py` (with or without `--mock`)

```
→ playwright_browser_navigate(url="http://127.0.0.1:8765/")
→ playwright_browser_snapshot()

# The daemon badge in the navbar should show:
# "○ Daemon Disconnected"
# With CSS class "daemon-off" (red/gray styling)

# Alternatively, fetch the badge directly:
→ playwright_browser_navigate(url="http://127.0.0.1:8765/daemon/status")
→ playwright_browser_snapshot()
# Shows: <span class="daemon-badge daemon-off">○ Daemon Disconnected</span>
```

### Recipe 6: Board Detail Page

**Goal**: Verify board detail page shows port info, compile/upload sections.

**Server**: `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://127.0.0.1:8765/board/dev/ttyTEST0")
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
→ playwright_browser_navigate(url="http://127.0.0.1:8766/")
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
→ playwright_browser_navigate(url="http://127.0.0.1:8766/api/medicines")
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
→ playwright_browser_navigate(url="http://127.0.0.1:8766/admin")
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
→ playwright_browser_navigate(url="http://127.0.0.1:8765/nonexistent")
→ playwright_browser_snapshot()

# Flask's default 404 page is shown, or a custom error template.
```

---

## Cleanup

Always close the browser and shutdown servers after tests — even if a test fails or is interrupted.

```
# Close the Playwright browser
→ playwright_browser_close()

# Shutdown servers (by port)
→ bash(command="kill $(lsof -ti:8765 -ti:8766) 2>/dev/null; echo 'done'", timeout=5000)

# Or shutdown a specific server:
→ bash(command="kill $(lsof -ti:8765) 2>/dev/null; echo 'done'", timeout=5000)
```

> **Why?** Leftover servers block ports on the next run, and an open browser page holds stale page state. Always clean up.

---

## Advanced: WebSocket Testing

> Requires `flask-sock` installed (optional dependency).

The WebSocket endpoint at `/ws/board-events` pushes board events to connected clients. Without BMS running, the WS will connect but receive no events.

```
→ playwright_browser_navigate(url="http://127.0.0.1:8765/")
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

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection refused` | Server not started | Run the server script first |
| Mock boards not showing | Started without `--mock` | Kill and restart with `--mock` |
| Empty sketch selector | UA mismatch | The mock uses IP `127.0.0.1` + UA `playwright-test` |
| `flask_sock` import error | Package not installed | `pip install flask-sock` (optional, WS tests only) |
| Port already in use | Previous server still running | `kill $(lsof -ti:8765) $(lsof -ti:8766)` |
| Debug restart looping | Flask debug mode | Expected; wait briefly after start |
| Snapshot missing elements | HTMX loaded after snapshot | Wait first: `playwright_browser_wait_for(time=2)` |

---

## File Reference

| File | Purpose |
|------|---------|
| `e2e/agent_tools/GUIDE.md` | Project-specific testing guide (source of this doc) |
| `e2e/agent_tools/SKILL.md` | Generic MCP testing skill (project-agnostic) |
| `e2e/agent_tools/AGENT.md` | Sub-agent definition for `@playwright-mcp-testing` |
| `e2e/agent_tools/COMMAND.md` | Command definition for `/playwright-mcp-testing` |
| `e2e/servers/arduino_dash_server.py` | Start arduino_dash with `--mock` |
| `e2e/servers/medminder_dash_server.py` | Start medminder_dash with `--mock` |
| `.opencode/skills/playwright-mcp-testing/SKILL.md` | Installed skill (copy of agent_tools/SKILL.md) |
| `.opencode/agents/playwright-mcp-testing.md` | Installed agent (copy of agent_tools/AGENT.md) |
| `.opencode/commands/playwright-mcp-testing.md` | Installed command (copy of agent_tools/COMMAND.md) |
| `e2e/package.json` | (Shelved) `@playwright/test` dev dep |
| `e2e/playwright.config.ts` | (Shelved) Playwright config |
| `e2e/fixtures/test-data.ts` | (Shelved) Shared test constants |
| `e2e/specs/arduino_dash/` | (Shelved) 4 spec files |
| `e2e/specs/medminder_dash/` | (Shelved) 4 spec files |
