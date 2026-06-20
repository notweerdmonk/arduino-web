---
---
# Agent Integration

opencode skill/agent/command definitions for Playwright MCP E2E testing.

## File Reference

| File | Purpose |
|------|---------|
| `e2e/agent_tools/SKILL.md` | Generic MCP testing skill (project-agnostic) |
| `e2e/agent_tools/AGENT.md` | Sub-agent definition for `@playwright-mcp-testing` |
| `e2e/agent_tools/COMMAND.md` | Command definition for `/playwright-mcp-testing` |
| `e2e/agent_tools/GUIDE.md` | Full 419-line project-specific testing guide |

## Installed Locations

Files are automatically installed to `.opencode/`:

| Source | Installed To |
|--------|-------------|
| `e2e/agent_tools/SKILL.md` | `.opencode/skills/playwright-mcp-testing/SKILL.md` |
| `e2e/agent_tools/AGENT.md` | `.opencode/agents/playwright-mcp-testing.md` |
| `e2e/agent_tools/COMMAND.md` | `.opencode/commands/playwright-mcp-testing.md` |

## Usage

In opencode, invoke with:

```
@playwright-mcp-testing Test the dashboard at http://localhost:8765
```

Or with the command:

```
/playwright-mcp-testing Test the dashboard at http://localhost:8765
```

The agent loads the skill, starts the Playwright browser, and walks through the scenarios.
