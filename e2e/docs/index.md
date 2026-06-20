---
---
# E2E Testing — Interactive Browser Tests

End-to-end browser tests for the MedMinder web apps using opencode's Playwright MCP tools.

## Overview

The E2E testing infrastructure provides:
- **Mock server scripts** — start Flask dev servers with fake board/medicine data
- **Test scenario recipes** — step-by-step opencode agent instructions
- **Agent integration** — reusable skill/agent/command definitions for opencode

> **Who is this for?** Developers and QA engineers running manual interactive tests via the opencode agent. Automated `@playwright/test` specs are shelved in `e2e/specs/`.

## Quick Start

```bash
# Terminal 1: Start arduino_dash with mock data
python3 e2e/servers/arduino_dash_server.py --mock --port 8765

# Terminal 2: Start medminder_dash with mock data
python3 e2e/servers/medminder_dash_server.py --mock --port 8766
```

Then in opencode:
> "Test the dashboard at http://localhost:8765"

## Directory Layout

```
e2e/
├── agent_tools/              # opencode skill/agent/command definitions
│   ├── SKILL.md              # MCP testing skill (project-agnostic)
│   ├── AGENT.md              # Sub-agent for @playwright-mcp-testing
│   ├── COMMAND.md            # Command definition
│   └── GUIDE.md              # Project-specific testing guide (419 lines)
├── servers/
│   ├── arduino_dash_server.py    # Mock arduino-dash server
│   └── medminder_dash_server.py  # Mock medminder-dash server
├── fixtures/test-data.ts     # (Shelved) Shared test constants
├── specs/                    # (Shelved) Automated Playwright specs
│   ├── arduino_dash/         # 4 spec files
│   └── medminder_dash/       # 4 spec files
├── package.json              # (Shelved) @playwright/test dev dep
├── playwright.config.ts      # (Shelved) Playwright configuration
└── docs/
    ├── index.md              # This file
    ├── servers.md            # Mock server reference
    ├── scenarios.md          # Test scenario recipes
    └── agent-tools.md        # Agent integration
```

Installed copies of agent_tools live in `.opencode/skills/playwright-mcp-testing/`, `.opencode/agents/playwright-mcp-testing.md`, and `.opencode/commands/playwright-mcp-testing.md`.

## Document Reference

| Doc | Description |
|-----|-------------|
| [servers.md](servers.md) | Mock server scripts, startup flags, --mock data, --bms mode, cleanup |
| [scenarios.md](scenarios.md) | 10 test scenario recipes with step-by-step instructions |
| [agent-tools.md](agent-tools.md) | opencode skill/agent/command integration |

## Related

- [docs/tests.md (top-level)](../../docs/tests.md) — overall testing methodology
- [agent_tools/GUIDE.md](../agent_tools/GUIDE.md) — full MCP testing guide (419 lines)
