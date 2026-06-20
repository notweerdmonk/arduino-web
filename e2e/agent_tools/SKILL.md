---
name: playwright-mcp-testing
description: "Use when the user asks about browser testing, E2E testing, Playwright testing, or interactive UI testing of web apps. Use ONLY when testing with Playwright MCP browser tools (playwright_browser_navigate, playwright_browser_snapshot, etc.). Describes how to set up Flask dev servers with mock data and run interactive browser tests. For project-specific server setup, mock data, and scenario recipes, read e2e/agent_tools/GUIDE.md."
---

# MCP E2E Testing — Generic Web App Testing with Playwright

This skill documents how to run interactive browser-based E2E tests using opencode's Playwright MCP tools (`playwright_browser_navigate`, `playwright_browser_snapshot`, `playwright_browser_click`, `playwright_browser_fill_form`, etc.).

## How to Use This Skill

1. Read the **project-specific guide** at `e2e/agent_tools/GUIDE.md` for:
   - Server startup and shutdown commands
   - Mock data injection details (boards, medicines, sketches)
   - Full scenario recipes with expected output
   - Troubleshooting for this project

2. Then follow the instructions below for the general approach.

## Prerequisites

1. **Server running** — Start the Flask dev server for the app under test (see the project's `e2e/agent_tools/GUIDE.md`)
2. **Browser available** — Playwright MCP tools use an internal Chromium instance

## Playwright MCP Tool Mapping

| App Action | MCP Tool | Parameters |
|-----------|----------|------------|
| Open page | `playwright_browser_navigate` | `url: "http://localhost:<PORT>/..."` |
| Read page content | `playwright_browser_snapshot` | (no params — captures current page) |
| Take screenshot | `playwright_browser_take_screenshot` | `type: "png"` |
| Click element | `playwright_browser_click` | `target: "css selector or text match"` |
| Fill text input | `playwright_browser_type` | `target: "...", text: "..."` |
| Fill form fields | `playwright_browser_fill_form` | `fields: [{target, name, type, value}, ...]` |
| Select dropdown | `playwright_browser_select_option` | `target: "...", values: ["..."]` |
| Hover element | `playwright_browser_hover` | `target: "..."` |
| Run JS | `playwright_browser_evaluate` | `function: "() => document.title"` |
| Wait for text | `playwright_browser_wait_for` | `text: "..."` (appear) or `textGone: "..."` (disappear) |
| Close browser | `playwright_browser_close` | (no params) |
| Handle dialog | `playwright_browser_handle_dialog` | `accept: true/false` |

### How to Find Element Selectors

1. Navigate to the page
2. Call `playwright_browser_snapshot` — returns an accessibility tree with labeled elements
3. Use labels/roles from the snapshot as `target` values in click/type/fill_form calls
4. For complex selectors, use CSS: `"#element-id"`, `".class-name"`, `"button:has-text('Submit')"`

## Assertion Patterns

Since Playwright MCP tools don't have built-in assertions, use these patterns:

### Pattern A: Snapshot Content Check

```python
snapshot = playwright_browser_snapshot()
# Manually inspect snapshot text for expected content
# e.g., check if "TestBoard Uno" appears in the tree
```

### Pattern B: JavaScript Evaluation

```javascript
// Check element text:
→ playwright_browser_evaluate(function="() => document.querySelector('#board-grid').textContent.includes('No boards detected')")

// Check element exists:
→ playwright_browser_evaluate(function="() => document.querySelector('#daemon-badge') !== null")

// Check element classes:
→ playwright_browser_evaluate(function="() => document.querySelector('.daemon-badge').className.includes('daemon-off')")

// Count elements:
→ playwright_browser_evaluate(function="() => document.querySelectorAll('.board-card').length")
```

### Pattern C: HTTP Status via Fetch

```javascript
→ playwright_browser_evaluate(function="() => fetch('/api/sketches').then(r => r.status)")
// Expected: 200
```

## General Test Workflow

1. **Start servers** (per project's GUIDE.md)
2. **Open browser** → navigate to the app URL
3. **Verify page** → capture snapshot, check content
4. **Interact** → click, fill forms, select options
5. **Assert** → snapshot or evaluate to verify results
6. **Cleanup** → close browser, shutdown servers (always, even on failure)

## Cleanup

Always clean up after testing:

```
# Close the Playwright browser
→ playwright_browser_close()

# Shutdown servers by port
→ bash(command="kill $(lsof -ti:<PORT1> -ti:<PORT2>) 2>/dev/null; echo 'done'", timeout=5000)
```

See the project's `e2e/agent_tools/GUIDE.md` for exact port numbers and shutdown commands.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection refused` | Server not started | Run the server script first |
| Mock data not showing | Server started without `--mock` flag | Kill and restart with `--mock` |
| Port already in use | Previous server still running | Kill by port: `kill $(lsof -ti:<PORT>)` |
| Snapshot missing elements | HTMX loaded after snapshot | Wait first: `playwright_browser_wait_for(time=2)` |
