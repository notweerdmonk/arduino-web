---
---
# Test Scenario Recipes

Each recipe lists step-by-step browser actions for the opencode agent.

## Recipe 1: Dashboard Empty State

**Goal:** Verify dashboard shows "No boards detected" when no boards are connected.
**Server:** `arduino_dash_server.py` (without `--mock`)

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_snapshot()

# Expected:
# - Page title contains "Dashboard"
# - #board-grid contains "No boards detected"
# - #daemon-badge shows "Daemon Disconnected"
```

## Recipe 2: Board Grid with Mock Data

**Goal:** Verify board cards show correct information.
**Server:** `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_snapshot()

# Expected cards:
# "TestBoard Uno" — "/dev/ttyTEST0 · arduino:avr:uno" — Connected — Manage
# "TestBoard Mega" — "/dev/ttyTEST1 · arduino:avr:mega" — Connected — Manage
```

## Recipe 3: Admin Page

**Goal:** Verify admin sections load correctly.
**Server:** `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/admin")
→ playwright_browser_snapshot()

# Sections: board selector, sketch upload (drag-drop zone), sketch selector
# ("mysketch"), compile/upload card, live events card
```

## Recipe 4: Sketch Selector Board Label

**Goal:** Verify sketch selector includes board assignment label.
**Server:** `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/admin")
→ playwright_browser_wait_for(text="mysketch")
→ playwright_browser_snapshot()

# Expected option text:
# "mysketch (2026-06-19 05:30:00) [TestBoard Uno (/dev/ttyTEST0)]"
```

## Recipe 5: Daemon Status Badge — Disconnected

**Goal:** Verify "Disconnected" when no BMS running.
**Server:** `arduino_dash_server.py` (with or without --mock, without --bms)

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_snapshot()

# Expected: "○ Daemon Disconnected" with class "daemon-off"
```

## Recipe 5b: Daemon Status Badge — Connected

**Goal:** Verify "Connected" when BMS is running.
**Server:** `arduino_dash_server.py --mock --bms`

```
→ playwright_browser_navigate(url="http://localhost:8765/")
→ playwright_browser_snapshot()

# Expected: "● Daemon Connected" with class "daemon-on" (green)
```

## Recipe 6: Board Detail Page

**Goal:** Verify board detail page layout.
**Server:** `arduino_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8765/board/dev/ttyTEST0")
→ playwright_browser_snapshot()

# Sections: board header ("TestBoard Uno"), port, FQBN, Connected badge,
# compile button, upload button, sketch selector
```

## Recipe 7: medminder_dash Home Page

**Goal:** Verify medminder_dash board grid.
**Server:** `medminder_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8766/")
→ playwright_browser_snapshot()

# Check for: board grid with mock boards, navigation links, daemon badge
```

## Recipe 8: Medicine API

**Goal:** Verify medicine API returns mock data.
**Server:** `medminder_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8766/api/medicines")
→ playwright_browser_evaluate(function="() => JSON.parse(document.body.innerText)")

# Returns: [{name:"Aspirin",hour:8,minute:0}, {name:"VitaminD",hour:12,minute:30},
#            {name:"Ibuprofen",hour:18,minute:0}]
```

## Recipe 9: medminder_dash Admin Page

**Goal:** Verify admin management sections.
**Server:** `medminder_dash_server.py --mock`

```
→ playwright_browser_navigate(url="http://localhost:8766/admin")
→ playwright_browser_snapshot()

# Sections: board selector, medicine list + add, sketch upload, compile/upload
```

## Recipe 10: 404 Error Page

**Goal:** Verify graceful error handling.
**Server:** either, with or without --mock

```
→ playwright_browser_navigate(url="http://localhost:8765/nonexistent")
→ playwright_browser_snapshot()
# Flask's default 404 or custom error template
```

## Cleanup

Always close browser and shutdown servers after tests:

```
→ playwright_browser_close()
→ bash(command="pkill -f arduino_dash_server.py 2>/dev/null; pkill -f medminder_dash_server.py 2>/dev/null")
→ bash(command="kill $(lsof -ti:8765 -ti:8766) 2>/dev/null")
```
