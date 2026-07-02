---
---
# E2E Testing — Interactive Browser Tests

End-to-end browser tests for the Arduino Web web apps using opencode's Playwright MCP tools.

Full documentation hub at [`e2e/index.md`](../e2e/index.md).

## Quick Links

| Document | Description |
|----------|-------------|
| [e2e/index.md](../e2e/index.md) | E2E documentation hub — quick reference + directory layout |
| [e2e/docs/servers.md](../e2e/docs/servers.md) | Mock server scripts, --mock data, --bms mode |
| [e2e/docs/scenarios.md](../e2e/docs/scenarios.md) | 10 test scenario recipes |
| [e2e/docs/agent-tools.md](../e2e/docs/agent-tools.md) | opencode skill/agent/command integration |
| [e2e/agent_tools/GUIDE.md](../e2e/agent_tools/GUIDE.md) | Full 529-line MCP testing guide |
| [e2e/README.md](../e2e/README.md) | Module overview, quick start, requirements |
| [e2e/index.md](../e2e/index.md) | E2E documentation hub — quick reference + directory layout |
| [e2e/test-sketch/README.md](../e2e/test-sketch/README.md) | Minimal Arduino sketch for compile/upload E2E tests |

## Quick Start

```bash
# Terminal 1: Start arduino_dash with mock data
python3 e2e/servers/arduino_dash_server.py --mock --port 8765

# Terminal 2: Start medminder_dash with mock data
python3 e2e/servers/medminder_dash_server.py --mock --port 8766
```

Then in opencode:
> "Test the dashboard at http://localhost:8765"
