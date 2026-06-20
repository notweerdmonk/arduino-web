---
---
# board_manager Package Overview

## Purpose

`board_manager` is the core pub/sub service within the MedMinder monorepo responsible for managing Arduino board detection, per-board worker subprocesses, and message routing between web apps and the Arduino CLI daemon.

It acts as a central hub that:
- Detects Arduino board connect/disconnect events (via gRPC streaming or udev hotplug)
- Spawns and manages per-board gRPC worker subprocesses
- Routes JSON messages between clients (web apps) and board workers using MQTT-style topic wildcards
- Manages the `arduino-cli daemon` lifecycle (start, health check, auto-recovery)

## Architecture Within the Monorepo

```
                         ┌──────────────────────┐
                         │   Web Apps (clients)  │
                         │   (TCP / UDS)         │
                         └──────────┬───────────┘
                                    │ JSON pub/sub
                                    ▼
┌─────────────────────────────────────────────────────────┐
│              BoardManagerService (service.py)            │
│  Main event loop: select()-based TCP + UDS listener     │
│  TopicRouter (router.py) for pub/sub routing            │
│  BoardPool (pool.py) for subprocess lifecycle           │
│  BoardDetector (board_detector.py) for board events     │
│  DaemonManager (daemon_manager.py) for arduino-cli      │
└─────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
         ┌───────────────────┐          ┌─────────────────────┐
         │  Board Workers    │          │  arduino-cli daemon │
         │  (board_worker.py)│          │  (gRPC :50051)      │
         │  Per-board        │          │                     │
         │  socketpair IPC   │          │                     │
         └───────────────────┘          └─────────────────────┘
```

## Key Modules Summary

| Module | File | Purpose |
|--------|------|---------|
| `BoardManagerService` | `service.py` | Main event loop: TCP+UDS listeners, message routing, subprocess orchestration |
| `protocol` | `protocol.py` | Framing protocol (newline and length-prefixed), `FrameReader`, encode/decode utilities |
| `TopicRouter` | `router.py` | MQTT-style pub/sub topic router with `::` separator and `+`/`*` wildcards |
| `BoardPool` | `pool.py` | Per-board worker subprocess lifecycle manager with socketpair IPC |
| `BoardDetector` | `board_detector.py` | Background thread for board connect/disconnect detection (watch or poll mode) |
| `board_worker` | `board_worker.py` | Subprocess entrypoint: per-board gRPC client with method dispatch |
| `DaemonManager` | `daemon_manager.py` | `arduino-cli daemon` subprocess lifecycle, health check, auto-recovery |
| `boot` | `boot.py` | WSGI lifecycle helpers: `start_bms`, `stop_bms`, `wait_for_bms` |
| `config` | `config.py` | Configuration dataclass and 3-tier loader (TOML → env vars → CLI args) |
| `UdevMonitor` | `udev_monitor.py` | USB hotplug monitor via pyudev with gRPC fallback for board info resolution |
| `__main__` | `__main__.py` | CLI entry point (`python -m board_manager`) |

## Configuration Overview

Configuration is resolved through a 3-tier priority system (later overrides earlier):

1. **TOML file** — pointed to by `--config` / `-c` CLI arg or `BOARD_MGR_CONFIG` env var; expects a `[service]` table
2. **Environment variables** — each option has a corresponding `BOARD_MGR_*` variable
3. **CLI arguments** — `--tcp-host`, `--tcp-port`, `--uds-path`, `--arduino-daemon`, `--daemon-binary`, `--log-level`, `--board-detection-mode`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOARD_MGR_TCP_HOST` | `127.0.0.1` | TCP bind address |
| `BOARD_MGR_TCP_PORT` | `9090` | TCP bind port |
| `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` | Unix domain socket path |
| `BOARD_MGR_ARDUINO_DAEMON` | `localhost:50051` | Arduino CLI daemon address |
| `BOARD_MGR_DAEMON_BINARY` | `arduino-cli` | Arduino CLI binary path/name |
| `BOARD_MGR_LOG_LEVEL` | `INFO` | Logging level |
| `BOARD_MGR_DETECTION_MODE` | `watch` | Board detection mode (`watch` or `poll`) |
| `BOARD_MGR_CONFIG` | — | Path to TOML config file |

## Version

Current version: `0.1.0`
