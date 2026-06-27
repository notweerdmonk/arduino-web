---
---
# E2E Testing

End-to-end browser testing infrastructure for the MedMinder web apps. Supports interactive MCP-driven testing via opencode and automated Playwright spec execution.

## Quick Reference

| Resource | Description |
|----------|-------------|
| [`README.md`](README.md) | Module overview, quick start, requirements |
| [`docs/index.md`](docs/index.md) | Detailed MCP interactive testing guide (servers, scenarios, agent integration) |
| [`docs/servers.md`](docs/servers.md) | Mock server CLI reference, daemonization, mock data details |
| [`docs/scenarios.md`](docs/scenarios.md) | 10 test scenario recipes with step-by-step instructions |
| [`docs/agent-tools.md`](docs/agent-tools.md) | opencode skill/agent/command integration |
| [`fixtures/test-data.ts`](fixtures/test-data.ts) | Shared Playwright test constants |
| [`specs/`](specs/) | Automated Playwright spec files (8 specs, 22 tests) |
| [`test-sketch/`](test-sketch/) | Minimal Arduino sketch for compile/upload E2E tests |
| [`MCP_TESTING_GUIDE.md`](MCP_TESTING_GUIDE.md) | Aligned copy of agent_tools/GUIDE.md |

## Directory Layout

```
e2e/
├── README.md                   # This file
├── index.md                    # Doc entry point (quick reference)
├── agent_tools/                # opencode skill/agent/command definitions
│   ├── SKILL.md, AGENT.md, COMMAND.md, GUIDE.md
├── docs/                       # Detailed documentation
│   ├── index.md                # MCP interactive testing guide
│   ├── servers.md              # Mock server reference
│   ├── scenarios.md            # Test scenario recipes
│   └── agent-tools.md          # Agent integration
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

## Related

- [docs/tests.md](../docs/tests.md) (top-level)
- [README.md](README.md)
