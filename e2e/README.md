---
---
# E2E Testing

End-to-end browser testing infrastructure for the Arduino Web web apps. Supports interactive MCP-driven testing via opencode and automated Playwright spec execution.

## Quick Start

### Interactive MCP Testing

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

```bash
cd e2e
npm install
npx playwright install --with-deps   # Download browser binaries
```

> Without `npx playwright install --with-deps`, the first run will fail with a "No browser found" error.

### Running Specs

```bash
npx playwright test        # Headless (default)
npx playwright test --ui   # Interactive UI mode
npx playwright test --headed  # Visible browser
```

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

## Requirements

- Python 3.10+ (for mock server scripts)
- Node.js 18+ (for automated Playwright specs, optional)
- opencode with Playwright MCP tools (for interactive testing, optional)

## Related

- [docs/servers.md](docs/servers.md) — Mock server reference
- [docs/scenarios.md](docs/scenarios.md) — Test scenario recipes
- [docs/tests.md](docs/tests.md) — Overall testing methodology
- [docs/agent-tools.md](docs/agent-tools.md) — Agent integration
- [docs/reference/typedoc/](docs/reference/typedoc/) — Fixtures + config API reference (typedoc)
- [docs/reference/specs.md](docs/reference/specs.md) — Playwright spec reference (22 tests across 8 files)
- [agent_tools/GUIDE.md](../agent_tools/GUIDE.md) — full MCP testing guide (529 lines)

## Acknowledgements

Assisted-by: OpenCode:deepseek-v4-flash-free
