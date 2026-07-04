# board-manager

Board Manager Service for arduino-cli. A standalone gRPC service that
wraps the arduino-cli daemon, provides pubsub-based board detection,
and routes compile/upload/list requests to the daemon on behalf of one
or more dashboard consumers.

## Overview

`board-manager` is the central service in the Arduino Web architecture.
It owns the lifecycle of the `arduino-cli daemon` process and
coordinates all interaction with it:

- **Daemon lifecycle** — spawn, monitor, and gracefully stop the
  arduino-cli daemon. Automatically restart on crash.
- **Board detection** — poll the daemon's `BoardList` RPC every 5
  seconds, detect connect/disconnect events, and emit pubsub
  notifications to all subscribed clients.
- **Command routing** — accept compile, upload, board-list, and
  port-list requests from clients over a local TCP or UDS pubsub
  channel, forward to the daemon, and stream responses back. Per-board
  workers send progress events with percent (0.0–100.0) from gRPC
  `TaskProgress` for real-time progress bar updates in the UI.
- **Port management** — detect and kill stale processes holding the
  daemon's port, validate port availability before spawning.
- **In-process embedding** — the `BoardManagerService` class can be
  instantiated directly in tests or for embedding, without needing a
  separate process.

## Architecture

```
┌─────────────────────────────────────────────┐
│              board-manager                   │
│                                             │
│  ┌──────────────┐    ┌──────────────────┐   │
│  │ BoardDetector │───►│  PubSub Router   │   │
│  │ (polls daemon)│    │  (topic-based)   │   │
│  └──────┬───────┘    └────────┬─────────┘   │
│         │                     │             │
│         ▼                     ▼             │
│  ┌──────────────────────────────────┐       │
│  │        DaemonManager             │       │
│  │  (spawn, monitor, kill port)     │       │
│  └──────────────┬───────────────────┘       │
│                 │                           │
│                 ▼                           │
│  ┌──────────────────────────────────┐       │
│  │       arduino-cli daemon          │       │
│  │       (gRPC :50051)               │       │
│  └──────────────────────────────────┘       │
└─────────────────────────────────────────────┘
         │
         │ PubSub (TCP / UDS)
         ▼
┌─────────────────────┐
│  Dashboard consumer  │
│  (arduino-dash,      │
│   medminder-dash)    │
└─────────────────────┘
```

## Installation

### From PyPI

```bash
pip install board-manager
```

### From the monorepo (development)

```bash
cd board_manager/python/board_manager
pipenv install --dev
pipenv run python -m board_manager
```

Or via nox:

```bash
nox -s 'tests(board_manager)' 'build(board_manager)'
```

## Usage

### Standalone service

```bash
# Start with default port (50051)
board-manager

# With explicit port
board-manager --port 50051

# Or via Python
python -m board_manager --port 50051
```

### Embedded in tests / code

```python
from board_manager.service import BoardManagerService
from board_manager.config import load_config

config = load_config()
service = BoardManagerService(config)
service.start()

# ... use the service ...

service.stop()
```

### Environment configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BOARD_MGR_DAEMON_PORT` | `50051` | arduino-cli daemon gRPC port |
| `BOARD_MGR_PUBSUB_PORT` | `50052` | PubSub TCP port |
| `BOARD_MGR_UDS_PATH` | `/tmp/bms.sock` | PubSub UDS path (used if set) |
| `BOARD_MGR_LOG_LEVEL` | `INFO` | Logging level |

## Development

### Setup

```bash
cd board_manager/python/board_manager
pipenv install --dev
pipenv shell
```

### Running tests

```bash
pipenv run pytest tests/ -v
```

### Building a wheel

```bash
pipenv run python -m build --outdir dist/board-manager
```

## Project Structure

```
board_manager/python/board_manager/
├── board_manager/
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── board_detector.py     # Board detection + event emission
│   ├── board_worker.py       # Background worker for board ops
│   ├── boot.py               # BMS subprocess lifecycle helpers
│   ├── config.py             # Environment-based configuration
│   ├── daemon_manager.py     # arduino-cli daemon spawn + monitor
│   ├── pool.py               # In-process board pool
│   ├── protocol.py           # PubSub frame protocol (newline/length)
│   ├── router.py             # Topic-based pubsub message router
│   └── service.py            # BoardManagerService core
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_board_detector.py
│   ├── test_board_worker.py
│   ├── test_boot.py
│   ├── test_config.py
│   ├── test_daemon_manager.py
│   ├── test_integration.py
│   ├── test_pool.py
│   ├── test_protocol.py
│   ├── test_router.py
│   └── test_service.py
├── setup.py
├── setup.cfg
├── pyproject.toml
├── Pipfile
└── Pipfile.lock
```

## Test Suite

The test suite covers (212 tests, including integration tests, across 10 files):

**board_detector**: BoardDetector polling, connect/disconnect events,
no-change detection, run loop, restart daemon.

**boot**: BMS environment configuration, start/stop subprocess,
wait-for-socket helpers.

**config**: Config defaults, TOML file loading.

**daemon_manager**: Init, start, stop, ensure-alive, check-port,
find-port-pid, kill-port-owner.

**integration**: Full service lifecycle with real sockets.

**pool**: BoardPool spawn, dispatch, poll, lifecycle, status, spawn
args.

**protocol**: FrameReader newline/length mode, encode/frame,
detect-mode, invalid-mode.

**router**: Topic match, topic router subscribe/unsubscribe/dispatch.

**service**: Client connect, message handling, route pool messages,
client lifecycle, send, read client, tick, service start/stop, daemon
state re-emission.

## Dependencies

- **arduino-grpc** (>=0.1.0) — gRPC client stubs
- **grpcio** (>=1.80.0) — gRPC framework
- **protobuf** (>=6.33.6) — Protocol Buffers
- **tomli** (>=1.1.0) — TOML parsing (Python <3.11)

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free

## License

MIT
