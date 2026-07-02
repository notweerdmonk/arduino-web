---
---
# E2E Testing

End-to-end browser testing infrastructure for the Arduino Web web apps. Supports interactive MCP-driven testing via opencode and automated Playwright spec execution.

## Quick Start

### Interactive MCP Testing

```bash
# Terminal 1: Start arduino_dash with mock data
python3 e2e/servers/arduino_dash_server.py --mock

# Terminal 2: Start medminder_dash with mock data
python3 e2e/servers/medminder_dash_server.py --mock
```

Then in opencode: `"Test the dashboard at http://localhost:8765"`

### Automated Playwright Specs

```bash
cd e2e && npm install
npx playwright test          # headless
npx playwright test --ui     # UI mode
npx playwright test --headed # headed
```

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

## Requirements

- Python 3.10+ (for mock server scripts)
- Node.js 18+ (for automated Playwright specs, optional)
- opencode with Playwright MCP tools (for interactive testing, optional)

## Related

- [docs/index.md](docs/index.md) — MCP interactive testing guide
- [docs/servers.md](docs/servers.md) — Mock server reference
- [docs/scenarios.md](docs/scenarios.md) — Test scenario recipes
- [docs/agent-tools.md](docs/agent-tools.md) — Agent integration

## Acknowledgements

Assisted-by: OpenCode:deepseek-v4-flash-free
