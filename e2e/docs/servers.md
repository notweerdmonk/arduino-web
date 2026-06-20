---
---
# Mock Servers

Flask dev servers with optional mock data injection for E2E testing.

## Server Scripts

### `arduino_dash_server.py`

Starts the arduino-dash Flask app with optional mock data.

```bash
# Empty state (no boards/sketches)
python3 e2e/servers/arduino_dash_server.py
# → http://0.0.0.0:8765 (default), daemon badge: Disconnected

# With mock boards + sketch
python3 e2e/servers/arduino_dash_server.py --mock

# With mock data + real BMS daemon
python3 e2e/servers/arduino_dash_server.py --mock --bms

# Custom port
python3 e2e/servers/arduino_dash_server.py --mock --port 9000
```

### `medminder_dash_server.py`

Starts the medminder-dash Flask app with optional mock data.

```bash
# With mock boards + medicines
python3 e2e/servers/medminder_dash_server.py --mock
# → http://0.0.0.0:8766

# With BMS daemon
python3 e2e/servers/medminder_dash_server.py --mock --bms
```

## `--mock` Data

### arduino_dash

| Board | Port | FQBN | Hardware ID |
|-------|------|------|-------------|
| TestBoard Uno | `/dev/ttyTEST0` | `arduino:avr:uno` | `HW-TEST-001` |
| TestBoard Mega | `/dev/ttyTEST1` | `arduino:avr:mega` | `HW-TEST-002` |

Plus one sketch entry (`mysketch`) in the upload registry, deployed to `HW-TEST-001`.

### medminder_dash

Same two boards plus three medicines:

| Medicine | Time | Enabled |
|----------|------|---------|
| Aspirin | 08:00 | ✅ |
| VitaminD | 12:30 | ✅ |
| Ibuprofen | 18:00 | ✅ |

## `--bms` Mode

The `--bms` flag starts the Board Management Service alongside the Flask dev server:

1. BMS spawns `arduino-cli daemon` (gRPC on `localhost:50051`)
2. BMS listens on TCP `127.0.0.1:9090` and UDS `/tmp/board_mgr.sock`
3. The Flask app's PubSub connects and sets `_daemon_ready = True`
4. UI daemon badge updates to "Connected"

**Note:** `--bms` disables Flask debug mode (`use_reloader=False`). BMS subprocess terminates automatically on server exit.

## Stopping Servers

```bash
# By port
kill $(lsof -ti:8765) 2>/dev/null
kill $(lsof -ti:8766) 2>/dev/null

# By name
pkill -f arduino_dash_server.py
pkill -f medminder_dash_server.py

# Verify
lsof -i:8765 -i:8766
```

## Playwright MCP Note

The Playwright MCP browser runs in a container and must reach servers on `0.0.0.0` (all interfaces), not `127.0.0.1` (loopback only). Both server scripts bind to `0.0.0.0` by default.
