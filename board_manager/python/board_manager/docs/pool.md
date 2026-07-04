---
layout: default
---
# BoardPool

## Purpose

Manages the lifecycle of per-board worker subprocesses. Each board gets its own dedicated subprocess that connects to the Arduino CLI daemon via gRPC. Communication between the parent service and the worker happens through `socketpair`-based Unix sockets.

## Location

`board_manager/pool.py`

---

## Enum: `PoolLimits`

| Member | Value | Description |
|--------|-------|-------------|
| `MAX_RESTARTS` | `3` | Maximum number of times a single board worker can be restarted |

---

## Class: `BoardProc`

State container for a single per-board worker subprocess.

### `__init__(self, port: str)`

| Param | Type | Description |
|-------|------|-------------|
| `port` | `str` | The serial port address for this board |

**State attributes:**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `port` | `str` | — | Serial port address |
| `proc` | `Optional[subprocess.Popen]` | `None` | Subprocess handle |
| `parent_sock` | `Optional[socket.socket]` | `None` | Parent end of the socketpair |
| `reader` | `FrameReader` | `FrameReader("newline")` | Frame reader for incoming worker messages |
| `restart_count` | `int` | `0` | Number of times this worker has been restarted |
| `last_error` | `Optional[str]` | `None` | Last error message |
| `ready` | `bool` | `False` | Whether the worker has sent `worker/ready` |

---

## Class: `BoardPool`

Manages subprocess lifecycle for per-board gRPC workers.

### `__init__(self)`

Initialises the pool with an empty board map and no resolved worker path.

---

### Public Methods

#### `spawn(self, port: str) -> BoardProc`

Spawns a new worker subprocess for a board port.

| Param | Type | Description |
|-------|------|-------------|
| `port` | `str` | The serial port address |

**Raises:**
- `RuntimeError` if a worker is already running for this port
- `RuntimeError` if restart limit (`MAX_RESTARTS = 3`) has been exceeded

**Process:**

1. Creates a `socket.socketpair(AF_UNIX, SOCK_STREAM)`
2. Passes the child socket FD to the subprocess via `pass_fds`
3. Launches `python board_worker.py <child_fd>`
4. Closes the child end in the parent process
5. Reuses existing `BoardProc` if available (incrementing `restart_count`)
6. Clears the reader buffer and sets `ready = False`

**Socketpair IPC:**
```
┌─────────────────────┐          ┌─────────────────────┐
│     Parent          │          │     Worker          │
│  BoardManagerService│──────────│  board_worker.py    │
│  parent_sock        │  UNIX    │  socket.fromfd()    │
│                     │  STREAM  │                     │
└─────────────────────┘          └─────────────────────┘
```

#### `dispatch(self, port: str, message: dict) -> None`

Sends a framed message to a board's worker subprocess.

| Param | Type | Description |
|-------|------|-------------|
| `port` | `str` | The serial port address |
| `message` | `dict` | The message dict to send |

**Raises:**
- `RuntimeError` if no worker exists for this port
- `RuntimeError` if the worker process has exited
- `RuntimeError` if the send fails

Messages are framed using `encode_and_frame(message, "newline")`.

#### `poll(self, timeout: float = 0.01) -> list[tuple[str, dict]]`

Polls all worker sockets for incoming messages.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout` | `float` | `0.01` | `select()` timeout in seconds |

Returns a list of `(port, message)` tuples from workers that have data available.

**Special handling:**
- Detects `worker/ready` events and sets `bp.ready = True`
- Catches connection errors and records them in `bp.last_error`
- Returns empty list if no boards or no ready workers

#### `remove(self, port: str) -> None`

Removes and terminates the worker for a given port. Calls `_cleanup_proc`.

#### `shutdown_all(self) -> None`

Terminates all worker processes and clears the pool.

#### `get_port_status(self, port: str) -> Optional[dict]`

Returns status dict for a board worker, or `None` if not found.

**Return format:**
```python
{
    "port": str,
    "running": bool,         # process poll() returns None
    "ready": bool,           # worker/ready received
    "restart_count": int,
    "exit_code": int or None,
    "last_error": str or None,
}
```

#### `list_ports(self) -> list[str]`

Returns a list of all managed port addresses.

#### `restart(self, port: str) -> BoardProc`

Removes and re-spawns the worker for a given port. Combines `remove` + `spawn`.

---

### Private Methods

#### `_get_worker_path(self) -> str`

Resolves the absolute path to `board_worker.py` by inspecting the module's `__file__` attribute. Result is cached in `self._worker_path`.

#### `_cleanup_proc(self, bp: BoardProc) -> None`

Terminates a worker process and closes its socket:

1. Sends `SIGTERM`, waits 3 seconds
2. If still alive, sends `SIGKILL`, waits 2 seconds
3. Closes `parent_sock` and sets it to `None`

---

### Restart Limits

Each board has a `restart_count` tracked in its `BoardProc`. When `restart_count >= MAX_RESTARTS (3)`, `spawn()` raises `RuntimeError`. The counter is incremented on every call to `spawn()` when a `BoardProc` already exists for that port.

---

### Usage Example

```python
from board_manager.pool import BoardPool

pool = BoardPool()

# Spawn workers
pool.spawn("/dev/ttyACM0")
pool.spawn("/dev/ttyACM1")

# Send a compile command
pool.dispatch("/dev/ttyACM0", {
    "id": "req-1",
    "body": {
        "method": "compile",
        "params": {"sketch_path": "/sketches/blink", "fqbn": "arduino:avr:uno"},
    },
})

# Poll for results
for port, msg in pool.poll(timeout=1.0):
    print(f"{port}: {msg}")

# Status
status = pool.get_port_status("/dev/ttyACM0")
# → {"port": "/dev/ttyACM0", "running": True, "ready": True, ...}

# Cleanup
pool.shutdown_all()
```
