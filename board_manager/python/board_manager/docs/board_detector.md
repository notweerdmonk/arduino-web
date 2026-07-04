---
layout: default
---
# BoardDetector

## Purpose

Runs in a background thread to detect Arduino board connect/disconnect events. Supports two detection modes and provides automatic daemon recovery on connection failures.

Emits events to a registered callback as boards are connected or disconnected, allowing `BoardManagerService` to track board state and route events to subscribers.

## Location

`board_manager/board_detector.py`

---

## Type Aliases

```python
BoardEventCallback = Callable[[str, dict], None]
```

Callback signature: `(port, message_dict) -> None`

---

## Enum: `DetectorDefaults`

| Member | Value | Description |
|--------|-------|-------------|
| `POLL_INTERVAL` | `5.0` | Seconds between poll iterations (poll mode) |
| `LIST_TIMEOUT` | `3` | Timeout in seconds for `list_boards` gRPC call |

---

## Class: `BoardDetector`

Detects board connect/disconnect events in a background thread.

### Detection Modes

| Mode | Description |
|------|-------------|
| `"watch"` | Uses `arduino-cli`'s `BoardListWatch` streaming RPC for real-time events. **Default.** |
| `"poll"` | Legacy periodic polling via `list_boards()` every `poll_interval` seconds |

### `__init__(self, callback: BoardEventCallback, daemon: str = "localhost:50051", poll_interval: float = 5.0, list_timeout: float = 3.0, daemon_manager: Any = None, mode: str = "watch")`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `callback` | `BoardEventCallback` | — | Called with `(port, msg)` on connect/disconnect |
| `daemon` | `str` | `"localhost:50051"` | Arduino CLI daemon gRPC address |
| `poll_interval` | `float` | `5.0` | Seconds between poll iterations |
| `list_timeout` | `float` | `3.0` | Timeout for `list_boards` gRPC call |
| `daemon_manager` | `Any` (optional) | `None` | `DaemonManager` instance for auto-recovery |
| `mode` | `str` | `"watch"` | Detection mode — `"watch"` or `"poll"` |

Initialises an internal `_known_boards` dict (thread-safe via `_lock`).

---

### Public Methods

#### `start(self) -> None`

Starts the detector background thread. Starts a daemon-thread for either watch mode (`_run_watch`) or poll mode (`_run`). No-op if already running.

#### `stop(self) -> None`

Stops the detector by setting `_running = False`. The background thread will exit on its next iteration.

#### `get_known_boards(self) -> dict[str, dict]`

Returns a thread-safe snapshot of currently known boards. Maps port address → board info dict.

**Return format:**
```python
{
    "/dev/ttyACM0": {
        "port": "/dev/ttyACM0",
        "fqbn": "arduino:avr:uno",
        "name": "Arduino Uno",
        "hardware_id": "2341:0043",
    },
}
```

---

### Private Methods

#### `_run(self) -> None`

Poll loop (for `"poll"` mode):
1. Calls `_run_once()` to perform a single poll cycle
2. On success: sleeps for `poll_interval`
3. On failure: sleeps for 2 seconds before retrying

#### `_run_once(self) -> bool`

Single poll cycle:
1. Connects to the daemon via `_connect_or_restart()`
2. Calls `client.list_boards()`
3. Compares current board list with `_known_boards`
4. Emits `"connected"` events for new boards and `"disconnected"` for removed boards
5. Disconnects the client
6. Returns `True` on success, `False` on connection error

#### `_run_watch(self) -> None`

Watch loop (for `"watch"` mode):
1. Continuously reconnects via `_connect_or_restart()`
2. Calls `client.watch_boards(timeout=None)` — a blocking streaming iterator
3. For each board event:
   - If `board.detected` and not in `_known_boards`: emits `"connected"`
   - If not `board.detected` and in `_known_boards`: emits `"disconnected"`
4. On stream error: logs warning, disconnects, sleeps 2s, retries

#### `_connect_or_restart(self, silent: bool = False) -> Optional[ArduinoGrpcClient]`

Attempts to connect to and initialise the gRPC client. On failure:

1. If `daemon_manager` is available, calls `ensure_alive()` to restart the daemon
2. Retries the connection once
3. Returns the client on success, `None` on failure

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `silent` | `bool` | `False` | Suppress warning logs on first failure |

#### `_restart_daemon(self) -> bool`

Restarts the arduino-cli daemon via `daemon_manager.ensure_alive()`. Returns `True` if the daemon was successfully restarted.

#### `_emit(self, event: str, info: dict) -> None`

Emits a board event to the registered callback.

| Param | Type | Description |
|-------|------|-------------|
| `event` | `str` | `"connected"` or `"disconnected"` |
| `info` | `dict` | Board info dict (port, fqbn, name, hardware_id) |

**Event message format:**
```python
{
    "type": "event",
    "topic": "board::/dev/ttyACM0::event",
    "data": {
        "event": "connected",
        "port": "/dev/ttyACM0",
        "board": "Arduino Uno",
        "fqbn": "arduino:avr:uno",
        "hardware_id": "2341:0043",
    },
}
```

---

### Auto-Recovery

When a connection to the arduino-cli daemon fails:

1. A warning is logged
2. If `daemon_manager` is configured, `ensure_alive()` is called to restart the daemon
3. One retry attempt is made
4. If still failing, the detector sleeps for 2 seconds and retries on the next cycle

---

### Usage Example

```python
from board_manager.board_detector import BoardDetector
from board_manager.daemon_manager import DaemonManager

def on_board_event(port: str, msg: dict):
    print(f"Event on {port}: {msg['data']['event']}")

daemon_mgr = DaemonManager()
detector = BoardDetector(
    callback=on_board_event,
    daemon="localhost:50051",
    daemon_manager=daemon_mgr,
    mode="watch",
)

detector.start()
# Boards connecting/disconnecting will trigger on_board_event
time.sleep(30)
detector.stop()
```
