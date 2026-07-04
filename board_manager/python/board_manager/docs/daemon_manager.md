---
layout: default
---
# DaemonManager

## Purpose

Manages the lifecycle of the `arduino-cli daemon` subprocess. Handles spawning, health checking, and auto-recovery. On startup, checks if the configured port is already in use — if a valid arduino-cli daemon is already running, it reuses it instead of starting a new one.

## Location

`board_manager/daemon_manager.py`

---

## Exception: `DaemonStartError`

```python
class DaemonStartError(Exception)
```

Raised when the arduino-cli daemon fails to start or does not become ready within the timeout.

---

## Class: `DaemonManager`

### `__init__(self, binary: str = "arduino-cli", daemon_addr: str = "localhost:50051")`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `binary` | `str` | `"arduino-cli"` | Path or name of the arduino-cli binary |
| `daemon_addr` | `str` | `"localhost:50051"` | Host:port address for the daemon |

Parses the address into `_host` and `_port`. Initialises `_process` and `_daemon_pid` to `None`.

---

### Public Methods

#### `is_alive` (property) -> `bool`

Checks whether the daemon process is still running:

1. If `_daemon_pid` is set, sends signal 0 (existence check) and verifies the process isn't a zombie
2. If that fails, falls back to checking `_process.poll()`

Returns `True` if the daemon is alive.

#### `start(self, timeout: float = 15.0) -> None`

Starts the arduino-cli daemon or reuses an existing one.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout` | `float` | `15.0` | Seconds to wait for the daemon to become ready |

**Logic:**

1. If `is_alive` → return immediately (already running)
2. If `_port_is_listening()`:
   - If `_health_check()` passes → reuse existing daemon (return)
   - Otherwise → `_kill_port_owner()` and continue
3. Spawns: `arduino-cli daemon --port <PORT> --daemonize`
4. Waits up to `timeout` seconds for the port to be listening and the health check to pass
5. Finds the actual daemon PID (forked child) via `_find_port_pid()`

**Raises:** `DaemonStartError` if the binary is not found or daemon doesn't become ready.

#### `stop(self) -> None`

Stops the daemon:

1. Kills the actual daemon PID (`_daemon_pid`) with `SIGTERM`, then `SIGKILL` if still alive after 1s
2. Cleans up the parent process (may be a zombie after `--daemonize`)
3. Waits with timeout for parent to exit

#### `ensure_alive(self) -> bool`

Checks daemon health and restarts if necessary.

| Returns | Description |
|---------|-------------|
| `True` | Daemon is running after the check |
| `False` | Daemon could not be recovered |

**Logic:**

1. If `is_alive` → return `True`
2. If port is listening:
   - If health check passes → recover (update `_daemon_pid`) → return `True`
   - Otherwise → `_kill_port_owner()`
3. Call `start(timeout=10.0)`
4. Return result

---

### Private Methods

#### `_is_zombie(pid: int) -> bool` (static)

Checks if a process is a zombie by reading `/proc/<pid>/status` for `State: Z (zombie)`.

#### `_parse_addr(addr: str) -> tuple[str, int]` (static)

Parses a `host:port` string into a `(host, port)` tuple.

**Raises:** `DaemonStartError` if the format is invalid or port is out of range.

#### `_port_is_listening(self) -> bool`

Checks if something is listening on the configured daemon port using `socket.create_connection()` with a 1-second timeout.

#### `_health_check(self) -> bool`

Performs a gRPC health check against the daemon:

1. Creates an insecure gRPC channel
2. Calls `ArduinoCoreServiceStub.Create()` with a 3-second timeout
3. If `Create` returns a valid `instance`, calls `Destroy()` and returns `True`
4. Returns `False` on any exception

#### `_kill_port_owner(self) -> None`

Finds the PID holding the configured port via `_find_port_pid()` and kills it with `SIGTERM`, then `SIGKILL` if still alive after 1 second.

#### `_find_port_pid(self) -> Optional[int]`

Finds the PID of the process listening on the configured port. Tries three tools in order:

| Tool | Command | Priority |
|------|---------|----------|
| `fuser` | `fuser <PORT>/tcp` | First |
| `ss` | `ss -tlnp` | Second |
| `lsof` | `lsof -ti :<PORT> -s TCP:LISTEN` | Third |

Returns the PID as `int`, or `None` if not found or all tools fail.

---

### Port Detection

The daemon manager uses a cascading approach to detect the process holding a TCP port:

1. **`fuser`** — fastest, port-specific query
2. **`ss`** — parses the full socket listing for `pid=` entries
3. **`lsof`** — fallback, file-descriptor-based lookup

This ensures port detection works across a range of Linux distributions.

---

### Auto-Recovery Flow

```
ensure_alive()
  ├── is_alive? → True (done)
  ├── Port listening?
  │     ├── Health check passes? → reuse, update PID
  │     └── Health check fails → kill port owner
  └── start(timeout=10)
        ├── Success → True
        └── Failure → False
```

---

### Usage Example

```python
from board_manager.daemon_manager import DaemonManager

mgr = DaemonManager(binary="arduino-cli", daemon_addr="localhost:50051")

# Start daemon
try:
    mgr.start(timeout=15.0)
except DaemonStartError as e:
    print(f"Failed: {e}")

# Check health
if mgr.is_alive:
    print("Daemon is running")

# Ensure alive (auto-restart if needed)
mgr.ensure_alive()

# Cleanup
mgr.stop()
```
