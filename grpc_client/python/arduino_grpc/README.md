# arduino-grpc

Python gRPC client for [arduino-cli](https://github.com/arduino/arduino-cli). Detects boards, compiles sketches, and uploads to Arduino boards via the arduino-cli daemon.

## Requirements

- Python 3.10+
- arduino-cli 1.5.0 ([install guide](https://arduino.github.io/arduino-cli/installation/))
- pipenv (or pip)

## Installation

```bash
cd grpc_client/python
pip install -e .
```

Or with pipenv:

```bash
cd grpc_client/python
pipenv install
pipenv shell
```

## Daemon Setup

Start the arduino-cli daemon before using the client:

```bash
arduino-cli daemon --port 50051 --daemonize
```

The daemon runs in the background. Stop it with `pkill arduino-cli`.

## Quick Start

```python
from arduino_grpc.client import ArduinoGrpcClient

client = ArduinoGrpcClient(daemon="localhost:50051")
client.connect()
client.init()

# List connected boards (probes serial ports for 5 seconds)
boards = client.list_boards()
for b in boards:
    print(f"{b.name} at {b.port.address} ({b.fqbn})")

# List all available boards (27+)
all_boards = client.list_all_boards()
print(f"{len(all_boards)} boards available")

# Compile a sketch
result = client.compile("sketches/blinky", "arduino:avr:uno")
print(f"Compile {'OK' if result.success else 'FAILED'}")

# Upload to a board
result = client.upload("sketches/blinky", "arduino:avr:uno", "/dev/ttyACM0")
print(f"Upload {'OK' if result.success else 'FAILED'}")

# Watch for board connect/disconnect (with timeout)
for board in client.watch_boards(timeout=10):
    print(f"{'Connected' if board.detected else 'Disconnected'}: {board.name}")

client.disconnect()
```

## API Reference

### ArduinoGrpcClient

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `connect()` | — | `None` | Connect to arduino-cli daemon |
| `disconnect()` | — | `None` | Close the gRPC channel (calls `destroy()` automatically) |
| `destroy()` | — | `None` | Destroy the instance on the daemon (free resources) |
| `init()` | `sketch_path` (optional) | `Instance` | Initialize Arduino core; call before any board/compile/upload operation |
| `list_boards(timeout)` | `timeout` (int, default 5s) | `List[Board]` | Get currently connected boards (probes serial ports for N seconds) |
| `list_all_boards()` | — | `List[Board]` | Get all available board platforms |
| `watch_boards()` | `callback`, `timeout` | `Iterator[Board]` | Stream board connect/disconnect events |
| `compile()` | `sketch_path`, `fqbn`, `verbose` | `CompileResult` | Compile a sketch |
| `upload()` | `sketch_path`, `fqbn`, `port`, `verbose`, `verify` | `UploadResult` | Upload a compiled sketch |
| `compile_stream()` | `sketch_path`, `fqbn`, `verbose`, `quiet` | `Iterator[tuple[str,str,bool,float]]` | Streaming compile with 4-tuple `(out, err, done, percent)` progress — drives real-time `<progress>` bar in the UI |
| `upload_stream()` | `sketch_path`, `fqbn`, `port`, `verbose`, `verify` | `Iterator[tuple[str,str,bool]]` | Streaming upload with 3-tuple `(out, err, done)` — no percent because `UploadResponse` lacks `TaskProgress` |
| `compile_and_upload()` | `sketch_path`, `fqbn`, `port`, `verbose`, `verify` | `tuple[CompileResult, UploadResult]` | Compile then upload |

### Data Models

**`Port`**: `address`, `protocol`, `protocol_label`, `label`, `properties`, `hardware_id`

**`Board`**: `port` (Port), `fqbn` (str), `name` (str), `detected` (bool)

**`CompileResult`**: `success` (bool), `output` (str), `error` (str), `sketch_path` (str)

**`UploadResult`**: `success` (bool), `output` (str), `error` (str)

### Exceptions

- `ArduinoError` — base class
- `ConnectionError` — daemon unreachable
- `InitializationError` — init RPC failed
- `CompileError` — compilation failed
- `UploadError` — upload failed
- `BoardError` — board operation failed
- `InvalidPortError` / `InvalidFqbnError` — missing required parameters

### Context Manager

The client supports `with` for automatic cleanup:

```python
with ArduinoGrpcClient() as client:
    client.init()
    boards = client.list_boards()
```

## Testing

```bash
# Unit tests (mocked, no daemon needed)
pipenv run python -m pytest arduino_grpc/tests/test_client.py -v

# Integration tests (requires running daemon)
pipenv run python -m arduino_grpc.tests.integration_test
```

Integration tests: Connection, Init, List Boards, List All Boards, Watch Boards (with timeout), Compile, Upload (full compile + upload to detected board).

## Project Structure

```
grpc_client/python/
├── arduino_grpc/
│   ├── __init__.py
│   ├── client.py          # ArduinoGrpcClient
│   ├── exceptions.py      # Custom exceptions
│   ├── models.py          # Data models
│   └── tests/
│       ├── __init__.py
│       ├── test_client.py        # 27 unit tests
│       └── integration_test.py   # 8 integration tests
├── cc/                    # Generated gRPC stubs
├── Pipfile
└── pyproject.toml
```

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free
