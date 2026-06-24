---
---

# Standalone Binary CLI Reference

All three binaries support `--help` for usage information.

## board-manager

**Binary:** `dist-standalone/board-manager/board-manager`

Entry point: `board_manager.__main__` — runs the Board Manager Service (gRPC daemon).

```
usage: board-manager [-h] [--tcp-host TCP_HOST] [--tcp-port TCP_PORT]
                     [--uds-path UDS_PATH] [--arduino-daemon ARDUINO_DAEMON]
                     [--daemon-binary DAEMON_BINARY] [--log-level LOG_LEVEL]
                     [--board-detection-mode {watch,udev}]
                     [-c CONFIG_FILE]

Board Manager Service
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--tcp-host` | `127.0.0.1` | TCP bind host for the pub/sub service |
| `--tcp-port` | `9090` | TCP bind port |
| `--uds-path` | `/tmp/board_mgr.sock` | Unix domain socket path |
| `--arduino-daemon` | `localhost:50051` | Arduino CLI daemon address (gRPC) |
| `--daemon-binary` | `arduino-cli` | Path to the arduino-cli binary |
| `--log-level` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `--board-detection-mode` | `watch` | Board detection: `watch` (polling) or `udev` (udev monitor) |
| `-c` / `--config` | — | Path to YAML config file (overrides CLI flags) |

### Example

```bash
dist-standalone/board-manager/board-manager \
    --tcp-port 9091 \
    --uds-path /tmp/my_sock.sock \
    --log-level DEBUG
```

---

## arduino-dash

**Binary:** `dist-standalone/arduino-dash/arduino-dash`

Entry point: `arduino_dash.__main__` — runs the Arduino Dashboard (Flask web app).

```
usage: arduino-dash [-h] [--host HOST] [--port PORT] [--uds UDS]
                    [--tcp-host TCP_HOST] [--tcp-port TCP_PORT]
                    [--no-uds] [--debug]

Arduino Dash
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `0.0.0.0` | Flask bind host |
| `--port` | `8080` | Flask bind port |
| `--uds` | `/tmp/board_mgr.sock` | BoardManager UDS path (auto-connect) |
| `--tcp-host` | `127.0.0.1` | BoardManager TCP host (fallback) |
| `--tcp-port` | `9090` | BoardManager TCP port |
| `--no-uds` | `false` | Force TCP connection (skip UDS) |
| `--debug` | `false` | Enable Flask debug mode |

### Connection Order

1. If `--no-uds` is not set, try connecting via UDS at `--uds` path
2. If UDS fails or `--no-uds` is set, connect via TCP at `--tcp-host`:`--tcp-port`
3. If both fail, the app starts but compile/upload features are disabled (logged as warning)

### Example

```bash
# Default: UDS at /tmp/board_mgr.sock
dist-standalone/arduino-dash/arduino-dash

# Custom port + TCP only
dist-standalone/arduino-dash/arduino-dash \
    --port 8081 \
    --no-uds \
    --tcp-host 10.0.0.1 \
    --tcp-port 9090
```

---

## medminder-dash

**Binary:** `dist-standalone/medminder-dash/medminder-dash`

Entry point: `medminder_dash.__main__` — runs the MedMinder Dashboard (Flask web app).

```
usage: medminder-dash [-h] [--host HOST] [--port PORT] [--uds UDS]
                      [--debug] [--no-uds] [--tcp-host TCP_HOST]
                      [--tcp-port TCP_PORT]
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `0.0.0.0` | Flask bind host |
| `--port` | `8080` | Flask bind port |
| `--uds` | `/tmp/board_mgr.sock` | BoardManager UDS path |
| `--debug` | `false` | Enable Flask debug mode |
| `--no-uds` | `false` | Force TCP connection (skip UDS) |
| `--tcp-host` | `127.0.0.1` | BoardManager TCP host |
| `--tcp-port` | `9090` | BoardManager TCP port |

### Connection Order

Same as arduino-dash: UDS first, TCP fallback, degraded mode if both fail.

### Example

```bash
dist-standalone/medminder-dash/medminder-dash --port 8081
```
