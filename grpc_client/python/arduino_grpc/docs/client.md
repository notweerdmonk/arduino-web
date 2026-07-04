---
layout: default
---
# ArduinoGrpcClient

**Module:** `arduino_grpc.client`

Central class for all interactions with the arduino-cli gRPC daemon.

```python
from arduino_grpc import ArduinoGrpcClient
```

---

## Constructor

```python
ArduinoGrpcClient(daemon: str = "localhost:50051")
```

| Param | Default | Description |
|-------|---------|-------------|
| `daemon` | `"localhost:50051"` | Host:port of the arduino-cli daemon |

Does **not** open a connection — call `.connect()` or use the context manager.

---

## Connection Lifecycle

### `connect() -> None`

Opens an insecure gRPC channel to the daemon and creates the service stub. The channel is reused until `disconnect()` is called.

**Raises:** `ConnectionError` — daemon unreachable or connection refused.

### `disconnect() -> None`

Calls `destroy()` to release the daemon-side instance, then closes the gRPC channel. Safe to call multiple times.

### `destroy() -> None`

Sends a `Destroy` RPC to free daemon resources on the server side. Failures are silently ignored (daemon may already be gone). Called automatically by `disconnect()`.

---

## Context Manager

The client supports `__enter__` / `__exit__` for automatic connect/disconnect:

```python
with ArduinoGrpcClient() as client:
    client.init()
    boards = client.list_boards()
# channel closed automatically
```

Equivalent to:

```python
client = ArduinoGrpcClient()
client.connect()
try:
    client.init()
finally:
    client.disconnect()
```

---

## Initialization

### `init(sketch_path: Optional[str] = None) -> Instance`

Creates a new Arduino core instance (`Create` RPC) then fully consumes the `Init` streaming response to ensure platform data loads.

| Param | Description |
|-------|-------------|
| `sketch_path` | Optional path to seed the Init context |

**Returns:** A protobuf `Instance` object (from `cc.arduino.cli.commands.v1.common_pb2`).

**Raises:**
- `ConnectionError` — not connected
- `InitializationError` — `Create` or `Init` RPC failed

### `instance` *(property)* -> `Instance`

Returns the initialized instance, lazily calling `init()` if not yet done.

```python
client.connect()
# instance property auto-initializes
inst = client.instance
```

---

## Board Operations

### `list_boards(timeout: int = 5) -> List[Board]`

Detects currently connected boards by probing serial ports.

| Param | Default | Description |
|-------|---------|-------------|
| `timeout` | `5` | Seconds to probe USB/serial devices |

**Returns:** List of `Board` objects for detected ports.

**Raises:** `BoardError` — RPC failure.

```python
boards = client.list_boards(timeout=10)
for b in boards:
    print(b.name, b.fqbn, b.port.address)
```

### `list_all_boards() -> List[Board]`

Returns every known board platform (including offline/undetected boards). All returned boards have `detected=False` and an empty port address.

**Returns:** List of `Board` objects.

**Raises:** `BoardError` — RPC failure.

```python
all_boards = client.list_all_boards()
print(f"{len(all_boards)} board platforms available")
```

### `watch_boards(callback=None, timeout=None) -> Iterator[Board]`

Streams board connect/disconnect events in real time. Blocks until an event arrives or the optional timeout expires.

| Param | Type | Description |
|-------|------|-------------|
| `callback` | `Optional[Callable[[Board], None]]` | Called for each Board event (in addition to yielding) |
| `timeout` | `Optional[float]` | Max seconds to wait for the first event. `None` = block indefinitely |

**Yields:** `Board` objects. `board.detected` is `True` on add events, `False` on remove events.

**Raises:**
- `BoardError` — RPC failure other than `DEADLINE_EXCEEDED`
- Gracefully stops iteration when the timeout expires (does *not* raise)

```python
# With callback
def on_board(b):
    logging.info(f"Board event: {b.name} {'connected' if b.detected else 'disconnected'}")

for board in client.watch_boards(callback=on_board, timeout=30):
    print(board)

# With timeout (stops after 10s)
for board in client.watch_boards(timeout=10):
    print(board)
```

---

## Compilation

### `compile_stream(sketch_path, fqbn, verbose=False, quiet=False) -> Iterator[tuple[str, str, bool, float]]`

Streams compiler output as it arrives from the gRPC stream — yields progress
percentage from `TaskProgress` messages for progress bar display.

| Param | Default | Description |
|-------|---------|-------------|
| `sketch_path` | — | Path to sketch directory (containing the `.ino` file) |
| `fqbn` | — | Fully Qualified Board Name (e.g. `"arduino:avr:uno"`) |
| `verbose` | `False` | Enable verbose compiler output |
| `quiet` | `False` | Suppress non-error output |

**Yields:** `(out: str, err: str, done: bool, percent: float)` 4-tuples.

| Field | Description |
|-------|-------------|
| `out` | Decoded stdout text chunk (may be empty) |
| `err` | Decoded stderr text chunk (may be empty) |
| `done` | `True` on the *last* response that carries the compile result |
| `percent` | Compilation progress percentage (0.0–100.0) from `resp.progress.percent` in gRPC `TaskProgress`. Reset to 0.0 before the first response and set to 100.0 on the final result |

```python
for out, err, done, percent in client.compile_stream("sketches/blinky", "arduino:avr:uno", verbose=True):
    if out:
        sys.stdout.write(out)
    if percent > 0:
        print(f"\rProgress: {percent:.0f}%", end="", flush=True)
    if done:
        print("\nCompilation finished")
```

**Raises:**
- `InvalidFqbnError` — FQBN is empty
- `CompileError` — RPC failure

### `compile(sketch_path, fqbn, verbose=False, quiet=False) -> CompileResult`

Convenience wrapper over `compile_stream()` that collects all output and returns a `CompileResult`. Iterates the 4-tuple stream internally, discarding the `percent` field.

| Param | Default | Description |
|-------|---------|-------------|
| `sketch_path` | — | Path to sketch directory |
| `fqbn` | — | Fully Qualified Board Name |
| `verbose` | `False` | Enable verbose output |
| `quiet` | `False` | Suppress non-error output |

**Returns:** `CompileResult(success, output, error, sketch_path)`.

**Raises:**
- `InvalidFqbnError` — FQBN is empty
- `CompileError` — RPC failure

```python
result = client.compile("sketches/blinky", "arduino:avr:uno")
if result.success:
    print("Compilation OK")
else:
    print(f"Compilation failed:\n{result.error}")
```

---

## Upload

### `upload_stream(sketch_path, fqbn, port, verbose=False, verify=True) -> Iterator[tuple[str, str, bool]]`

Streams upload output as it arrives from the gRPC stream.

| Param | Default | Description |
|-------|---------|-------------|
| `sketch_path` | — | Path to sketch directory |
| `fqbn` | — | Fully Qualified Board Name |
| `port` | — | Serial port address (e.g. `"/dev/ttyACM0"`, `"COM3"`) |
| `verbose` | `False` | Enable verbose avrdude output |
| `verify` | `True` | Verify upload after writing |

**Yields:** `(out: str, err: str, done: bool)` tuples (same pattern as `compile_stream`).

**Raises:**
- `InvalidFqbnError` — FQBN is empty
- `InvalidPortError` — Port is empty
- `UploadError` — RPC failure

```python
for out, err, done in client.upload_stream("sketches/blinky", "arduino:avr:uno", "/dev/ttyACM0"):
    if out:
        print(out, end="")
```

### `upload(sketch_path, fqbn, port, verbose=False, verify=True) -> UploadResult`

Convenience wrapper over `upload_stream()` that collects all output and returns an `UploadResult`.

| Param | Default | Description |
|-------|---------|-------------|
| `sketch_path` | — | Path to sketch directory |
| `fqbn` | — | Fully Qualified Board Name |
| `port` | — | Serial port address |
| `verbose` | `False` | Enable verbose output |
| `verify` | `True` | Verify upload after writing |

**Returns:** `UploadResult(success, output, error)`.

**Raises:**
- `InvalidFqbnError` — FQBN is empty
- `InvalidPortError` — Port is empty
- `UploadError` — RPC failure

```python
result = client.upload("sketches/blinky", "arduino:avr:uno", "/dev/ttyACM0")
print(f"Upload {'succeeded' if result.success else 'failed'}")
```

---

## Combined Compile + Upload

### `compile_and_upload(sketch_path, fqbn, port, verbose=False, verify=True) -> tuple[CompileResult, UploadResult]`

Compiles a sketch then uploads to the board. **Skips upload** if compilation fails.

| Param | Default | Description |
|-------|---------|-------------|
| `sketch_path` | — | Path to sketch directory |
| `fqbn` | — | Fully Qualified Board Name |
| `port` | — | Serial port address |
| `verbose` | `False` | Enable verbose output |
| `verify` | `True` | Verify upload after writing |

**Returns:** `(CompileResult, UploadResult)`. If compile fails, `UploadResult` has `success=False` and `error="Compile failed"`.

**Raises:** Same as `compile()` + `upload()`.

```python
cr, ur = client.compile_and_upload("sketches/blinky", "arduino:avr:uno", "/dev/ttyACM0")
print(f"Compile: {'OK' if cr.success else 'FAIL'}")
if cr.success:
    print(f"Upload:  {'OK' if ur.success else 'FAIL'}")
```

---

## Progress Streaming Pattern

`compile_stream()` and `upload_stream()` use a similar streaming protocol, with
the key difference that `compile_stream()` returns a **4-tuple** (includes
`percent`) and `upload_stream()` returns a **3-tuple** (no percent —
`UploadResponse` has no `TaskProgress`):

### `compile_stream()` — 4-tuple with percent

```
Iterator[tuple[str, str, bool, float]]
              │     │    │      │
              │     │    │      └── progress percentage (0.0–100.0)
              │     │    └───────── done flag (True on the final response)
              │     └────────────── stderr text chunk
              └──────────────────── stdout text chunk
```

### `upload_stream()` — 3-tuple (no percent)

```
Iterator[tuple[str, str, bool]]
              │     │    │
              │     │    └── done flag (True on the final response)
              │     └──────── stderr text chunk
              └────────────── stdout text chunk
```

Typical usage for a progress UI:

```python
with ArduinoGrpcClient() as client:
    client.init()

    last_out = ""
    last_pct = 0.0
    for out, err, done, percent in client.compile_stream("sketch", "arduino:avr:uno"):
        if out:
            last_out = out.rstrip()
            print(f"\r[{percent:.0f}%] {last_out}", end="", flush=True)
        if err:
            print(f"\n[stderr] {err.rstrip()}")
        if done:
            print(f"\n{'Done!' if last_out else 'Failed.'}")
```

---

## Error Handling

Every public method wraps gRPC `RpcError` exceptions into the domain-specific hierarchy:

| Method | Exception on Failure |
|--------|---------------------|
| `connect()` | `ConnectionError` |
| `init()` | `InitializationError` |
| `list_boards()`, `list_all_boards()` | `BoardError` |
| `watch_boards()` | `BoardError` (except `DEADLINE_EXCEEDED` which stops iteration) |
| `compile()`, `compile_stream()` | `CompileError`, `InvalidFqbnError` |
| `upload()`, `upload_stream()` | `UploadError`, `InvalidFqbnError`, `InvalidPortError` |

All domain exceptions inherit from `ArduinoError`, which inherits from `Exception`.

```python
from arduino_grpc import ArduinoGrpcClient, ArduinoError

try:
    client = ArduinoGrpcClient()
    client.connect()
    client.init()
    result = client.compile("sketch", "arduino:avr:uno")
except ArduinoError as e:
    print(f"Arduino operation failed: {e}")
```
