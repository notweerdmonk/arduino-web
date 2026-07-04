---
layout: default
---
# E2E Testing — Interactive Browser Tests

End-to-end browser tests for the Arduino Web web apps using opencode's Playwright MCP tools.

> **Note:** This page covers interactive MCP-driven testing via the opencode agent. For automated Playwright spec execution, see the sections below.

## Overview

The E2E testing infrastructure provides:
- **Mock server scripts** — start Flask dev servers with fake board/medicine data
- **Test scenario recipes** — step-by-step opencode agent instructions
- **Agent integration** — reusable skill/agent/command definitions for opencode

> **Who is this for?** Developers and QA engineers running manual interactive tests via the opencode agent. Automated `@playwright/test` specs live in `e2e/specs/`.

## Quick Reference

| Resource | Description |
|----------|-------------|
| [`README.md`](README.md) | Module overview, quick start, requirements |
| [`docs/index.md`](docs/index.md) | Detailed MCP interactive testing guide (servers, scenarios, agent integration) |
| [`docs/servers.md`](docs/servers.md) | Mock server CLI reference, daemonization, mock data details |
| [`docs/scenarios.md`](docs/scenarios.md) | 10 test scenario recipes with step-by-step instructions |
| [`docs/agent-tools.md`](docs/agent-tools.md) | opencode skill/agent/command integration |
| [`docs/reference/typedoc/`](docs/reference/typedoc/) | E2E fixtures + config API reference (typedoc) |
| [`docs/reference/specs.md`](docs/reference/specs.md) | Playwright spec reference (22 tests across 8 files) |
| [`fixtures/test-data.ts`](fixtures/test-data.ts) | Shared Playwright test constants |
| [`specs/`](specs/) | Automated Playwright spec files (8 specs, 22 tests) |
| [`test-sketch/`](test-sketch/) | Minimal Arduino sketch for compile/upload E2E tests |
| [`MCP_TESTING_GUIDE.md`](MCP_TESTING_GUIDE.md) | Aligned copy of agent_tools/GUIDE.md |

## Directory Layout

```
e2e/
├── README.md                   # Overview of E2E testing
├── index.md                    # This file
├── agent_tools/                # opencode skill/agent/command definitions
│   ├── SKILL.md, AGENT.md, COMMAND.md, GUIDE.md
├── docs/                       # Detailed documentation
│   ├── index.md                # MCP interactive testing guide
│   ├── servers.md              # Mock server reference
│   ├── scenarios.md            # Test scenario recipes
│   ├── agent-tools.md          # Agent integration
│   └── reference/              # Generated API reference (pdoc + typedoc + specs)
├── fixtures/test-data.ts       # Shared Playwright test constants
├── servers/                    # Mock Flask dev server scripts
│   ├── arduino_dash_server.py
│   └── medminder_dash_server.py
├── specs/                      # Automated Playwright specs
│   ├── arduino_dash/           # 4 spec files (12 tests)
│   └── medminder_dash/         # 4 spec files (10 tests)
├── test-sketch/                # Minimal Arduino sketch for compile/upload tests
├── MCP_TESTING_GUIDE.md        # Aligned copy of agent_tools/GUIDE.md
├── package.json                # @playwright/test dev dependency
└── playwright.config.ts        # Playwright configuration with webServer auto-management
```

Installed copies of agent_tools live in `.opencode/skills/playwright-mcp-testing/`, `.opencode/agents/playwright-mcp-testing.md`, and `.opencode/commands/playwright-mcp-testing.md`.

## Document Reference

| Doc | Description |
|-----|-------------|
| [README.md](README.md) | E2E overview |
| [docs/servers.md](docs/servers.md) | Mock server scripts, startup flags, --mock data, --bms mode, cleanup |
| [docs/scenarios.md](docs/scenarios.md) | Test scenario recipes with step-by-step instructions |
| [docs/agent-tools.md](docs/agent-tools.md) | Agent integration skill/command/agent |
| [docs/reference/typedoc/](docs/reference/typedoc/) | E2E fixtures + config API reference (typedoc) |
| [docs/reference/specs.md](docs/reference/specs.md) | Playwright spec reference — 22 tests across 8 files |
