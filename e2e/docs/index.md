---
---
# E2E Testing — Interactive Browser Tests

End-to-end browser tests for the MedMinder web apps using opencode's Playwright MCP tools.

> **Note:** This page covers interactive MCP-driven testing via the opencode agent. For automated Playwright spec execution, see the sections below.

## Overview

The E2E testing infrastructure provides:
- **Mock server scripts** — start Flask dev servers with fake board/medicine data
- **Test scenario recipes** — step-by-step opencode agent instructions
- **Agent integration** — reusable skill/agent/command definitions for opencode

> **Who is this for?** Developers and QA engineers running manual interactive tests via the opencode agent. Automated `@playwright/test` specs live in `e2e/specs/`.

## Quick Start

```bash
# Terminal 1: Start arduino_dash with mock data
python3 e2e/servers/arduino_dash_server.py --mock --port 8765

# Terminal 2: Start medminder_dash with mock data
python3 e2e/servers/medminder_dash_server.py --mock --port 8766
```

Then in opencode:
> "Test the dashboard at http://localhost:8765"

## Automated Playwright Specs

### Installation

\`\`\`bash
cd e2e
npm install
npx playwright install --with-deps   # Download browser binaries
\`\`\`

> Without `npx playwright install --with-deps`, the first run will fail with a "No browser found" error.

### Running Specs

\`\`\`bash
npx playwright test        # Headless (default)
npx playwright test --ui   # Interactive UI mode
npx playwright test --headed  # Visible browser
\`\`\`

> Alternative — run from project root without changing directory:
> `npx playwright test --config e2e/playwright.config.ts`

### Server Auto-Management

\`playwright.config.ts\` uses Playwright's \`webServer[]\` configuration to auto-start both mock servers before tests and auto-shutdown after. The config starts \`arduino_dash_server.py --mock --port 8765\` and \`medminder_dash_server.py --mock --port 8766\`.

### Spec Summary

| Spec File | Dashboard | Tests | What It Covers |
|-----------|-----------|-------|----------------|
| \`specs/arduino_dash/dashboard.spec.ts\` | arduino_dash | 3 | Empty state, mock board cards, Manage link navigation |
| \`specs/arduino_dash/admin.spec.ts\` | arduino_dash | 3 | Admin sections, board selector, disabled compile/upload |
| \`specs/arduino_dash/board-pages.spec.ts\` | arduino_dash | 3 | Board detail pages |
| \`specs/arduino_dash/sketch-upload.spec.ts\` | arduino_dash | 3 | Sketch upload flow |
| \`specs/medminder_dash/home.spec.ts\` | medminder_dash | 3 | Board grid load, mock boards, daemon badge |
| \`specs/medminder_dash/admin.spec.ts\` | medminder_dash | 2 | Admin page sections |
| \`specs/medminder_dash/medicines.spec.ts\` | medminder_dash | 3 | Medicine list CRUD |
| \`specs/medminder_dash/sketch-upload.spec.ts\` | medminder_dash | 2 | Sketch upload flow |

> Standalone — no opencode or MCP needed.

### Test Data Fixtures

Location: `e2e/fixtures/test-data.ts`

Exports constants that mirror the mock state injected by `e2e/servers/*_server.py --mock`:

| Export | Type | Description |
|--------|------|-------------|
| `MOCK_PORTS` | object | Port paths (`/dev/ttyTEST0`), board names (`TestBoard Uno`), FQBNs (`arduino:avr:uno`), hardware IDs for 2 boards (Uno, Mega) |
| `MOCK_SKETCH` | object | Sketch name, path, checksum, timestamp, and associated hardware_id |
| `MOCK_MEDICINES` | array | 3 medicine entries with name, hour, minute dosage schedule |
| `daemonStatusUrl(baseURL)` | function | Returns `/daemon/status` URL |
| `boardDetailUrl(baseURL, port)` | function | Returns `/board/<port>` URL with encoded port path |

Import from specs:

```typescript
import { MOCK_PORTS, MOCK_SKETCH, MOCK_MEDICINES } from '../fixtures/test-data';
```

Currently specs use inline literals — fixtures are available for future or refactored specs that need to reference the same mock data as the server scripts.

## Test Sketch

A minimal Arduino sketch for compile/upload E2E testing.

Location: \`e2e/test-sketch/\` — contains \`README.md\` and \`test-sketch.ino\`

Purpose: minimal \`setup(){}\` \`loop(){}\` sketch that validates the compile pipeline without board-specific logic

See [e2e/test-sketch/README.md](../test-sketch/README.md)

## Directory Layout

\`\`\`
e2e/
├── README.md
├── index.md                 # This file (index redirect/landing)
├── agent_tools/             # opencode skill/agent/command definitions
├── servers/
│   ├── arduino_dash_server.py    # Mock arduino-dash server
│   └── medminder_dash_server.py  # Mock medminder-dash server
├── fixtures/test-data.ts     # Shared test constants
├── specs/                    # Automated Playwright specs
│   ├── arduino_dash/
│   └── medminder_dash/
├── test-sketch/
│   ├── README.md
│   └── test-sketch.ino
├── MCP_TESTING_GUIDE.md
├── package.json              # @playwright/test dev dep
├── playwright.config.ts      # Playwright configuration
└── docs/
    ├── index.md
    ├── servers.md
    ├── scenarios.md
    └── agent-tools.md
\`\`\`

Installed copies of agent_tools live in \`.opencode/skills/playwright-mcp-testing/\`, \`.opencode/agents/playwright-mcp-testing.md\`, and \`.opencode/commands/playwright-mcp-testing.md\`.

## Document Reference

| Doc | Description |
|-----|-------------|
| [servers.md](servers.md) | Mock server scripts, startup flags, --mock data, --bms mode, cleanup |
| [scenarios.md](scenarios.md) | 10 test scenario recipes with step-by-step instructions |
| [agent-tools.md](agent-tools.md) | opencode skill/agent/command integration |

## Related

- [e2e/README.md](../README.md) — E2E overview
- [e2e/index.md](index.md) — This document
- [docs/tests.md (top-level)](../../docs/tests.md) — overall testing methodology
- [agent_tools/GUIDE.md](../agent_tools/GUIDE.md) — full MCP testing guide (529 lines)
