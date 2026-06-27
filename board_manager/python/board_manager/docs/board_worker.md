---
---
# Board Worker (Subprocess Entrypoint)

## Purpose

The board worker is a child process spawned by `BoardPool` for each detected Arduino board. It connects to the Arduino CLI daemon via gRPC and handles method dispatch for compile, upload, and board listing operations.

Communication with the parent process (`BoardManagerService`) happens over a Unix socketpair. Messages are framed using newline-delimited JSON.

## Location

`board_manager/board_worker.py`

---

## Entrypoint: `main()`

```python
def main() -> None
```

The subprocess entry point:

1. Reads the child socket FD from `sys.argv[1]`
2. Creates a socket object via `socket.fromfd(fd, AF_UNIX, SOCK_STREAM)`
3. Creates an `ArduinoGrpcClient`, calls `connect()` and `init()`
4. If init fails, sends an error message and exits
5. Sends a `worker/ready` event to the parent
6. Enters the main loop: reads framed messages from the socket, dispatches to `_handle_message`
7. On exit, disconnects the gRPC client and closes the socket

**Startup sequence:**
```
Worker starts → connect() → init() → send "worker/ready"
                                    → enter message loop
```

---

## Message Dispatch: `_handle_message(msg: dict, client: Any, sock: socket.socket)`

Dispatches a single request message to the appropriate arduino-cli method.

### Supported Methods

#### `init`

Re-initialises the gRPC client connection.

**Response:** `ok` result, or `"init_failed"` error.

#### `list_boards`

Lists boards via `client.list_boards()`.

**Params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout` | `int` | `5` | gRPC call timeout |

**Response:** Array of `{port, fqbn, name}` dicts.

#### `compile`

Compiles a sketch via `client.compile_stream()` (streaming output).

**Params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `sketch_path` | `str` | `""` | Path to the sketch directory |
| `fqbn` | `str` | `""` | Fully qualified board name |
| `verbose` | `bool` | `False` | Enable verbose output |

**Streaming output:** Sends `::progress` events for each chunk of stdout/stderr.
Each progress event includes a `percent` field (0.0–100.0) from the gRPC
`TaskProgress` message. When only the percentage advances (no output text),
a progress-only message is sent to update the progress bar without adding a
blank output line.

**Final response:** `ok` or `error` result with `{success, output, error, sketch_path}`.

#### `upload`

Uploads a compiled sketch via `client.upload_stream()` (streaming output).

**Params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `sketch_path` | `str` | `""` | Path to the sketch directory |
| `fqbn` | `str` | `""` | Fully qualified board name |
| `port` | `str` | `""` | Target serial port |
| `verbose` | `bool` | `False` | Enable verbose output |

**Streaming output:** Initial progress messages with connection info, followed by streaming stdout/stderr via `::progress` events.

**Final response:** `ok` or `error` result with `{success, output, error}`.

#### `compile_and_upload`

Performs a combined compile followed by upload via `client.compile_and_upload()`.

**Params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `sketch_path` | `str` | `""` | Path to the sketch directory |
| `fqbn` | `str` | `""` | Fully qualified board name |
| `port` | `str` | `""` | Target serial port |
| `verbose` | `bool` | `False` | Enable verbose output |

**Response:** `ok` if both compile and upload succeeded, `error` otherwise. Returns `{compile: {success, output, error}, upload: {success, output, error}}`.

#### `ping`

Returns a simple health check response.

**Response:** `ok` result with `{"pong": True}`.

---

### Helper Functions

#### `_make_error(msg: dict, code: str, text: str) -> dict`

Builds an error response dict.

**Return format:**
```python
{
    "type": "error",
    "id": msg["id"],
    "topic": msg.get("reply_to", ""),
    "status": "error",
    "code": code,
    "message": text,
    "data": {"code": code, "message": text},
}
```

#### `_make_result(msg: dict, status: str, data: Any = None) -> dict`

Builds a success response dict.

**Return format:**
```python
{
    "type": "result",
    "id": msg["id"],
    "topic": msg.get("reply_to", ""),
    "status": status,
    "data": data,
}
```

#### `_make_progress(msg: dict, out: str, err: str, percent: float = 0.0) -> dict`

Builds a progress event dict for streaming compile/upload output.

| Param | Default | Description |
|-------|---------|-------------|
| `percent` | `0.0` | Compilation progress percentage (0.0–100.0). Only used for compile — upload always passes `0.0` (no `TaskProgress` in upload gRPC responses) |

**Return format:**
```python
{
    "type": "event",
    "topic": msg["reply_to"] + "::progress",
    "data": {"output": out, "error": err, "percent": percent},
}
```

The `percent` field is consumed by `arduino_sketch_tools` to broadcast a
`<progress>` OOB element over WebSocket. The board worker sends
progress-only messages (empty `out`/`err`, only `percent` changed) to update
the progress bar when no output text is available. This prevents redundant
empty output lines in the compile log while keeping the progress bar
up-to-date.

#### `_make_event(topic: str, data: Any) -> dict`

Builds a generic event dict.

```python
{"type": "event", "topic": topic, "data": data}
```

---

### IPC Protocol

Messages are framed with newline-delimited JSON over the socketpair:

```
Parent → Worker:  {"id": "req-1", "body": {"method": "compile", "params": {...}}}\n
Worker → Parent:  {"type": "event", "topic": "resp::compile::req-1::progress", "data": {...}}\n
Worker → Parent:  {"type": "result", "id": "req-1", "status": "ok", "data": {...}}\n
```

---

### Usage

The worker is never invoked directly — it is spawned by `BoardPool`:

```python
# In BoardPool.spawn():
proc = subprocess.Popen(
    [sys.executable, worker_path, str(child_fd)],
    pass_fds=[child_fd],
)
```
