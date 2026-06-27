---
---
# Boot Module

## Purpose

Provides lifecycle helpers for managing the Board Manager Service (BMS) as a subprocess from WSGI entry points (e.g., `gunicorn.conf.py` hooks). Includes startup, shutdown, and readiness-waiting utilities, as well as stale resource cleanup.

## Location

`board_manager/boot.py`

---

## Enum: `BmsEnv`

Environment variable names for BMS configuration:

| Member | Value |
|--------|-------|
| `TCP_HOST` | `BOARD_MGR_TCP_HOST` |
| `TCP_PORT` | `BOARD_MGR_TCP_PORT` |
| `UDS_PATH` | `BOARD_MGR_UDS_PATH` |
| `ARDUINO_DAEMON` | `BOARD_MGR_ARDUINO_DAEMON` |
| `DAEMON_BINARY` | `BOARD_MGR_DAEMON_BINARY` |
| `LOG_LEVEL` | `BOARD_MGR_LOG_LEVEL` |

---

## Dataclass: `BmsDefaults`

```python
@dataclass(frozen=True)
class BmsDefaults
```

Default configuration values:

| Field | Type | Default |
|-------|------|---------|
| `UDS_PATH` | `str` | `/tmp/board_mgr.sock` |
| `TCP_HOST` | `str` | `127.0.0.1` |
| `TCP_PORT` | `int` | `9090` |
| `ARDUINO_DAEMON` | `str` | `localhost:50051` |
| `DAEMON_BINARY` | `str` | `arduino-cli` |
| `LOG_LEVEL` | `str` | `INFO` |

---

## Functions

### `_get_bms_env_config() -> dict`

Reads BMS configuration from environment variables with defaults from `BmsDefaults`.

**Returned keys:** `tcp_host`, `tcp_port`, `uds_path`, `arduino_daemon`, `daemon_binary`, `log_level`.

### `_free_bms_resources(tcp_host: str, tcp_port: int, uds_path: str) -> None`

Cleans up stale BMS resources before starting a new instance:

1. **TCP port:** Uses `lsof -ti tcp:<PORT>` to find any process holding the target TCP port and sends `SIGTERM`
2. **UDS socket:** Tests if the UDS path is alive by attempting to connect. If the connection fails (`ConnectionRefusedError`), removes the stale socket file

**Edge cases:**
- If `lsof` is not installed, logs a debug message and skips TCP cleanup
- If `lsof` times out, logs a warning and continues

### `start_bms() -> subprocess.Popen`

Starts the Board Manager Service as a subprocess.

1. Reads config from environment variables via `_get_bms_env_config()`
2. Frees stale resources via `_free_bms_resources()`
3. Constructs the CLI command:
   ```
   python -m board_manager \
     --tcp-host <host> --tcp-port <port> --uds-path <path> \
     --arduino-daemon <addr> --daemon-binary <binary> \
     --log-level <level>
   ```
4. Spawns the subprocess via `subprocess.Popen`

**Returns:** The `Popen` handle for the BMS subprocess.

### `stop_bms(proc: subprocess.Popen | None, timeout: float = 5.0) -> None`

Stops the Board Manager Service subprocess gracefully.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `proc` | `subprocess.Popen \| None` | — | The BMS subprocess handle |
| `timeout` | `float` | `5.0` | Seconds to wait for graceful shutdown |

Sends `SIGTERM` and waits up to `timeout`. If the process doesn't exit, sends `SIGKILL`.

### `wait_for_bms(uds_path: str = "/tmp/board_mgr.sock", tcp_host: str = "127.0.0.1", tcp_port: int = 9090, timeout: float = 10.0) -> bool`

Waits for the BMS to become reachable via UDS or TCP.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `uds_path` | `str` | `/tmp/board_mgr.sock` | UDS socket path |
| `tcp_host` | `str` | `127.0.0.1` | TCP host |
| `tcp_port` | `int` | `9090` | TCP port |
| `timeout` | `float` | `10.0` | Maximum seconds to wait |

Polls every 200ms, checking:
1. If the UDS socket exists and accepts connections → return `True`
2. If TCP port is reachable → return `True`

Returns `True` if BMS became reachable within the timeout, `False` otherwise.

---

## Usage Example

```python
# gunicorn.conf.py or similar WSGI bootstrap
from board_manager.boot import start_bms, stop_bms, wait_for_bms

def when_ready(server):
    global bms_proc
    bms_proc = start_bms()
    if not wait_for_bms(timeout=10.0):
        raise RuntimeError("BMS failed to start")

def on_exit(server):
    stop_bms(bms_proc)
```

### Typical Lifecycle

```
start_bms()
  → _free_bms_resources()  # kill stale BMS, remove stale UDS
  → subprocess.Popen(python -m board_manager ...)

wait_for_bms()
  → polls UDS/TCP until ready (or timeout)

# ... serve requests ...

stop_bms(proc)
  → SIGTERM → wait 5s → SIGKILL (if needed)
```
