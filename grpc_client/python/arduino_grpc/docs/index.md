---
---
# arduino-grpc

**Version:** 0.1.0

Python gRPC client for the [Arduino CLI](https://github.com/arduino/arduino-cli) daemon. Provides board detection, sketch compilation, firmware upload, and streaming board-watch events over gRPC.

---

## Monorepo Context

`arduino-grpc` lives in the **Arduino Web monorepo** at `grpc_client/python/arduino_grpc/`. It is consumed as a local wheel by sibling packages:

- `board_manager`
- `board_manager_client`
- `arduino_dash`
- `medminder_dash`

Each sibling declares the dependency via its Pipfile using a `file://` index pointing at the built wheel. The gRPC stubs (`cc/` directory) are generated from the arduino-cli `.proto` files by `scripts/gen_grpc_bindings.py`.

---

## Dependencies

Declared in `pyproject.toml`:

| Package | Minimum Version |
|---------|----------------|
| `grpcio` | 1.80.0 |
| `protobuf` | 6.33.6 |
| `googleapis-common-protos` | 1.75.0 |

Python 3.10+ required.

---

## Module Layout

```
arduino_grpc/
├── __init__.py      # Public API surface, version
├── client.py        # ArduinoGrpcClient — core class
├── models.py        # Port, Board, CompileResult, UploadResult dataclasses
└── exceptions.py    # Exception hierarchy (ArduinoError → 6 subclasses)
```

### Module Summary

| Module | Key Exports | Purpose |
|--------|-------------|---------|
| `arduino_grpc` | `ArduinoGrpcClient`, `ArduinoError`, `ConnectionError`, `InitializationError`, `CompileError`, `UploadError`, `BoardError` | Top-level package — version string and re-exports |
| `arduino_grpc.client` | `ArduinoGrpcClient` | gRPC channel management, board ops, compile, upload, streaming |
| `arduino_grpc.models` | `Port`, `Board`, `CompileResult`, `UploadResult` | Immutable data transfer objects with `from_proto()` factory methods |
| `arduino_grpc.exceptions` | `ArduinoError`, `ConnectionError`, `InitializationError`, `CompileError`, `UploadError`, `BoardError`, `InvalidPortError`, `InvalidFqbnError` | Domain-specific exception hierarchy |

---

## Quick Start

```python
from arduino_grpc import ArduinoGrpcClient

with ArduinoGrpcClient() as client:
    client.init()

    # Detect boards
    boards = client.list_boards(timeout=5)
    for b in boards:
        print(f"{b.name} at {b.port.address} ({b.fqbn})")

    # Watch for board events
    for board in client.watch_boards(timeout=10):
        print(f"{'Connected' if board.detected else 'Disconnected'}: {board.name}")

    # Compile + upload
    cr, ur = client.compile_and_upload(
        "sketches/blinky", "arduino:avr:uno", "/dev/ttyACM0"
    )
    print(f"Compile: {'OK' if cr.success else 'FAIL'}")
    print(f"Upload:  {'OK' if ur.success else 'FAIL'}")
```

---

## Daemon Setup

```bash
# Start the arduino-cli daemon before using the client
arduino-cli daemon --port 50051 --daemonize
```
