---
description: "Run MCP Playwright E2E browser tests. Starts test servers, runs scenarios against the web UI, and cleans up. Args: comma-separated module paths (relative to project root). If a path has no directory component, it's relative to the project root."
agent: build
subtask: true
---

## MCP E2E Test Run

Load the skill: `skill(name="playwright-mcp-testing")`

Then read the project guide: `read(path="e2e/agent_tools/GUIDE.md")`

The user provided these arguments: $ARGUMENTS

Parse `$ARGUMENTS` as a comma-separated list of module paths. For each module:
- If the path contains a `/`, treat it as relative to project root (e.g., `e2e/servers/medminder_dash_server.py`)
- If the path has no `/`, assume it's at the project root (e.g., a `server.py` in the top-level directory)

Example invocations:
- `/playwright-mcp-testing e2e/servers/arduino_dash_server.py` — start one server
- `/playwright-mcp-testing e2e/servers/arduino_dash_server.py,e2e/servers/medminder_dash_server.py` — start both
- `/playwright-mcp-testing server.py` — start `server.py` from project root

Follow this procedure:
1. For each module path in the comma-separated list, determine the full path and start it with bash
2. Wait for each server to be ready (curl health check)
3. Navigate to the app's main page with `playwright_browser_navigate`
4. Capture snapshot to verify it loaded correctly
5. Run 2-3 key scenarios from the guide (dashboard, admin page, API endpoint)
6. For compile/upload scenarios, reference the test-sketch at `e2e/test-sketch/`:
   - Navigate to admin page, select a board, compile the test-sketch, verify success
   - Upload the compiled sketch to the board
7. Report results to the user
8. Close browser with `playwright_browser_close`
9. Shutdown all started servers with bash
