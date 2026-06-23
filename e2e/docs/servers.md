---
---
# Mock Servers

Flask dev servers with optional mock data injection for E2E testing. No shell hacks (`&`, `disown`, `&>/dev/null`) required — the server daemonizes itself.

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

# With log capture
python3 e2e/servers/arduino_dash_server.py --mock --logfile /tmp/arduino.log
```

### `medminder_dash_server.py`

Starts the medminder-dash Flask app with optional mock data.

```bash
# With mock boards + medicines
python3 e2e/servers/medminder_dash_server.py --mock
# → http://0.0.0.0:8766

# With BMS daemon
python3 e2e/servers/medminder_dash_server.py --mock --bms

# With log capture
python3 e2e/servers/medminder_dash_server.py --mock --logfile /tmp/medminder.log
```

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--mock` | — | Inject test data (boards, sketches, medicines) |
| `--bms` | — | Start BMS daemon (arduino-cli gRPC) |
| `--port PORT` | 8765 / 8766 | TCP port to bind |
| `--production` | — | Disable Flask debug + reloader |
| `--pidfile PATH` | `/tmp/<script>.pid` | PID file path |
| `--stop` | — | Stop a running server via its pidfile |
| `--force` | — | With `--stop`: immediate SIGKILL |
| `--logfile PATH` | /dev/null | Redirect stdout/stderr to file |

## Why Daemonization?

The bash tool tracks processes by session ID. A simple `os.setpgid(0, 0)` changes the process group but leaves the process in the same session — when the bash tool exits, the entire session receives SIGHUP and the server dies. `os.setsid()` creates a new session, making the process immune to SIGHUP from the tool. But `setsid()` requires the caller not be a process group leader, so the server forks first: the parent (group leader) exits immediately, and the child calls `setsid()` to start a fresh session.

After `setsid()`, stdout/stderr are redirected to the logfile (or `/dev/null`). This means `python3 script.py --mock` returns instantly and the server lives independently — no `&`, no `disown`, no `&>/dev/null`.

## Lifecycle

### Starting

The server daemonizes automatically: it forks, the parent exits immediately (the bash tool sees a completed command), and the child continues in a new session with stdout/stderr redirected.

```bash
python3 e2e/servers/arduino_dash_server.py --mock
# Command returns immediately. Server is running in background.
```

### Stopping

Use the built-in `--stop` flag (no `lsof`, no `kill`, no `pkill`):

```bash
# Stop arduino_dash (default pidfile: /tmp/arduino_dash_server.pid)
python3 e2e/servers/arduino_dash_server.py --stop

# Force-stop (skip graceful SIGTERM)
python3 e2e/servers/arduino_dash_server.py --stop --force

# Custom pidfile
python3 e2e/servers/arduino_dash_server.py --pidfile /tmp/my.pid --stop

# Stop medminder_dash
python3 e2e/servers/medminder_dash_server.py --stop
```

The stop flow:
1. Reads PID from pidfile
2. Sends SIGTERM
3. Polls every 100ms for up to 5s
4. Escalates to SIGKILL if process doesn't exit
5. Removes pidfile
6. Exits with status 0

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

## Playwright MCP Note

The Playwright MCP browser runs in a container and must reach servers on `0.0.0.0` (all interfaces), not `127.0.0.1` (loopback only). Both server scripts bind to `0.0.0.0` by default.
