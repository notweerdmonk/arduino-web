---
---
# UdevMonitor

## Purpose

Monitors USB serial port hotplug events via `pyudev`. Detects Arduino board connect/disconnect events by listening to udev netlink events and emits the same event format as `BoardDetector`.

Provides an alternative to the gRPC-based `BoardDetector` for environments where the arduino-cli daemon is not available or where faster, kernel-level hotplug detection is desired.

Gracefully degrades when `pyudev` is not installed.

## Location

`board_manager/udev_monitor.py`

---

## Class: `UdevMonitor`

### `__init__(self, callback: BoardEventCallback, daemon: str = "localhost:50051")`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `callback` | `BoardEventCallback` | — | Called with `(port, msg)` on connect/disconnect |
| `daemon` | `str` | `"localhost:50051"` | Arduino CLI daemon address for board info resolution |

Initialises an empty `_known_boards` dict (thread-safe via `_lock`).

---

### Public Methods

#### `start(self) -> None`

Starts the udev monitor:

1. If already running, returns immediately
2. Calls `_scan_existing()` to discover already-connected boards synchronously
3. Starts a daemon background thread running `_run()`

This two-phase startup ensures subscribers never see an empty board list — existing boards are emitted before async events are processed.

#### `stop(self) -> None`

Sets `_running = False`. The background thread's poll loop will exit on the next iteration.

#### `get_known_boards(self) -> dict[str, dict]`

Returns a thread-safe snapshot of currently known boards.

**Return format:**
```python
{
    "/dev/ttyACM0": {
        "port": "/dev/ttyACM0",
        "fqbn": "arduino:avr:uno",
        "name": "Arduino Uno",
        "hardware_id": "2341:0043",
        "source": "udev",
    },
}
```

---

### Private Methods

#### `_scan_existing(self) -> None`

Scans already-connected tty devices for Arduino-like hardware and emits `"connected"` events for each:

1. Lists all devices in the `"tty"` subsystem via `pyudev.Context().list_devices()`
2. Filters to Arduino-like devices via `_is_arduino_like()`
3. For each matching device, resolves board info via `_resolve_info()` and emits `"connected"`

If `pyudev` is not installed, logs a warning and returns.

#### `_run(self) -> None`

Background thread loop:

1. Creates a `pyudev.Context()` and `pyudev.Monitor.from_netlink()` filtered to the `"tty"` subsystem
2. Polls `monitor.poll()` in a blocking loop
3. For each device event, calls `_handle_device()`
4. Exits when `_running` becomes `False`

If `pyudev` is not installed or monitor creation fails, logs a warning and exits the thread.

#### `_handle_device(self, device: Any) -> None`

Processes a single udev device event:

| Action | Behavior |
|--------|----------|
| `"add"` / `"change"` | Resolves board info; emits `"connected"` if port not already known |
| `"remove"` | Removes from `_known_boards`; emits `"disconnected"` |

Only processes devices that pass `_is_arduino_like()`.

#### `_resolve_info(self, port: str, device: Any) -> dict`

Resolves board information, trying gRPC first as a richer source, then falling back to udev properties.

| Priority | Source | Data |
|----------|--------|------|
| 1 (best) | Arduino gRPC daemon | Full FQBN, name, hardware_id |
| 2 (fallback) | udev properties | `ID_MODEL` for name, `ID_VENDOR_ID:ID_MODEL_ID` for hardware_id |

**Return format:**
```python
{
    "port": "/dev/ttyACM0",
    "fqbn": "arduino:avr:uno",  # or "" if unavailable
    "name": "Arduino Uno",       # or ID_MODEL from udev
    "hardware_id": "2341:0043",
    "source": "udev",
}
```

#### `_is_arduino_like(device: Any) -> bool` (static)

Checks whether a udev device is an Arduino-like serial port.

**Criteria:** The device's `sys_name` must start with `ttyACM` or `ttyUSB`. Other serial devices (`ttyS*`, `ttyAMA*`, etc.) are ignored.

```python
UdevMonitor._is_arduino_like(device)
# → True for ttyACM0, ttyUSB1
# → False for ttyS0, ttyAMA0
```

#### `_emit(self, event: str, info: dict) -> None`

Emits a board event to the registered callback. Uses the same event format as `BoardDetector._emit()`:

```python
{
    "type": "event",
    "topic": "board::/dev/ttyACM0::event",
    "data": {
        "event": "connected",       # or "disconnected"
        "port": "/dev/ttyACM0",
        "board": "Arduino Uno",
        "fqbn": "arduino:avr:uno",
        "hardware_id": "2341:0043",
    },
}
```

---

### Device Filtering

Only devices with `sys_name` starting with `ttyACM` or `ttyUSB` are accepted. This targets modern Arduino boards (Uno, Mega, Due, Zero, etc.) and common USB-serial adapters (FTDI, CP210x, CH340) while excluding:

- `ttyS*` — Built-in serial ports
- `ttyAMA*` — Raspberry Pi serial
- `ttyprintk` — Printer ports
- `ttyVR*` — Various embedded serial ports

---

### Graceful Degradation

If `pyudev` is not installed:

- `_scan_existing()` logs a warning and returns immediately
- `_run()` logs a warning and exits the thread
- The monitor becomes a no-op — board detection is handled by the gRPC-based `BoardDetector` instead

---

### Usage Example

```python
from board_manager.udev_monitor import UdevMonitor

def on_board_event(port: str, msg: dict):
    print(f"Board {msg['data']['event']}: {port}")

monitor = UdevMonitor(callback=on_board_event, daemon="localhost:50051")
monitor.start()

# Boards will be detected as they are plugged/unplugged
time.sleep(60)
monitor.stop()
```
