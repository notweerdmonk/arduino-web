# board-manager-client

PubSub client library for the BoardManagerService. Wraps the raw
pubsub stream exposed by `board-manager` with a simple Python API
for subscribing to command responses and board/port events.

## Overview

`board-manager-client` provides the `PubSubClient` class that
dashboard consumers (notably `arduino-dash` and `medminder-dash`) use
to communicate with the BoardManagerService without dealing with raw
gRPC stubs or the pubsub frame protocol directly.

### Features

- **Topic-based subscription** — subscribe to specific topics
  (`board:events`, `compile:resp`, `upload:resp`, etc.) with callback
  handlers.
- **Automatic reconnection** — if the pubsub connection drops, the
  client retries with configurable backoff.
- **Stale socket cleanup** — detect and remove stale UDS socket files
  before connecting.
- **Thread-safe** — internal locking for concurrent subscribe/
  unsubscribe/publish operations.
- **Context manager support** — `with PubSubClient() as c: ...`
  for automatic cleanup.

## Architecture

```
┌─────────────────────┐      PubSub gRPC stream     ┌──────────────────┐
│  Consumer app       │◄──────────────────────────►  │  board-manager   │
│                     │                              │                  │
│  ┌───────────────┐  │   Topics:                    │  ┌────────────┐  │
│  │ PubSubClient  │  │   - board:events             │  │  PubSub    │  │
│  │               │  │   - compile:resp             │  │  Router    │  │
│  │ - subscribe() │  │   - upload:resp              │  └────────────┘  │
│  │ - unsubscribe │  │   - daemon:status            │                  │
│  │ - connect()   │  │                              │                  │
│  │ - close()     │  │                              │                  │
│  └───────────────┘  │                              └──────────────────┘
└─────────────────────┘
```

## Installation

### From PyPI

```bash
pip install board-manager-client
```

### From the monorepo (development)

```bash
cd board_manager_client/python/board_manager_client
pipenv install --dev
pipenv run pytest tests/ -v
```

Or via nox:

```bash
nox -s 'tests(board_manager_client)' 'build(board_manager_client)'
```

## Usage

```python
from board_manager_client import PubSubClient

client = PubSubClient()

# Subscribe to board events
def on_board_event(event):
    print(f"Board {event['type']}: {event['port']}")

client.subscribe("board:events", on_board_event)

# Subscribe to compile responses
def on_compile_resp(response):
    print(f"Compile {'OK' if response['success'] else 'FAILED'}")

client.subscribe("compile:resp", on_compile_resp)

# Connect to the service
client.connect()

# ... app runs ...

# Clean up
client.unsubscribe("board:events", on_board_event)
client.close()
```

### With context manager

```python
with PubSubClient() as client:
    client.subscribe("board:events", on_board_event)
    client.connect()
    # ... auto-closes on exit ...
```

### Connection modes

The client supports both TCP and Unix Domain Socket connections:

```python
# TCP (default port 9090)
client.connect(host="localhost", port=9090)

# Unix Domain Socket
client.connect(uds_path="/tmp/board_mgr.sock")
```

## Development

### Setup

```bash
cd board_manager_client/python/board_manager_client
pipenv install --dev
pipenv shell
```

### Running tests

```bash
pipenv run pytest tests/ -v
```

### Building a wheel

```bash
pipenv run python -m build --outdir dist/board-manager-client
```

## Project Structure

```
board_manager_client/python/board_manager_client/
├── board_manager_client/
│   ├── __init__.py          # PubSubClient + exports
│   └── pubsub_client.py     # Core client implementation
├── tests/
│   ├── __init__.py
│   └── test_pubsub_client.py
├── setup.py
├── setup.cfg
├── pyproject.toml
├── Pipfile
└── Pipfile.lock
```

## Test Suite

| Test class | Focus |
|-----------|-------|
| `TestPubSubClient` | Initial state, subscribe/unsubscribe topics, subscribe without handler |
| `TestPubSubClientConnect` | TCP connection, UDS connection, connection failure |
| `TestStaleUdsSocket` | Stale UDS socket cleanup before connect |
| `TestConnectRetry` | Reconnection with backoff on connection drop |
| `TestPubSubClientReconnect` | Full reconnection lifecycle |

**Total**: 24 tests across 1 file.

## Dependencies

- **arduino-grpc** (>=0.1.0) — gRPC client stubs
- **board-manager** (>=0.1.0) — board detection service

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free

## License

MIT
