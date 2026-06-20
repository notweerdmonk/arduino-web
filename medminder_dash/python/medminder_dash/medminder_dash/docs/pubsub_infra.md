---
---
# `pubsub_infra.py` — PubSub Infrastructure

**File:** `medminder_dash/pubsub_infra.py`

PubSub client lifecycle, board event handling, WebSocket broadcast, response
waiting, and fallback board scanning.

## Class: `PubSubTopic(str, Enum)`

PubSub topic constants for board manager communication.

| Member | Value |
|--------|-------|
| `DAEMON_READY` | `"sys::daemon/ready"` |
| `BOARD_EVENT` | `"board::+::event"` |
| `RESP` | `"resp::*"` |
| `HEALTH` | `"sys::health"` |
| `RESP_COMPILE` | `"resp::compile::*"` |
| `RESP_UPLOAD` | `"resp::upload::*"` |

## Functions

### `init_pubsub(app, use_uds=True, tcp_host="127.0.0.1", tcp_port=9090, uds_path="/tmp/board_mgr.sock") -> PubSubClient`

Initialize PubSub connection to the BoardManagerService.

| Param | Type | Default | Purpose |
|-------|------|---------|---------|
| `app` | `Flask` | — | Flask app instance |
| `use_uds` | `bool` | `True` | Use Unix domain sockets |
| `tcp_host` | `str` | `"127.0.0.1"` | TCP host for BMS |
| `tcp_port` | `int` | `9090` | TCP port for BMS |
| `uds_path` | `str` | `"/tmp/board_mgr.sock"` | UDS path |

Connects, subscribes to all topics, registers handlers, wires up
`ArduinoSketchTools` compile/upload response handlers, starts reader thread.

```python
init_pubsub(app, use_uds=True, uds_path="/tmp/board_mgr.sock")
```

### `get_pubsub() -> Optional[PubSubClient]`

Return the current `PubSubClient` instance, or `None` if not initialized.

### `ensure_sketch_dir() -> None`

Create the sketch directory if it does not exist. Calls `os.makedirs` on the
path returned by `load_sketch_dir()`.

### `_get_alarm_hpp_path() -> str`

Return the full path to the `alarm.hpp` file inside the sketch directory.

### `_on_board_event(msg: dict) -> None`

Handle a board event (connected/disconnected) from PubSub.

- **connected**: Adds port to `state._known_ports` (if not already present).
- **disconnected**: Removes port from `state._known_ports` and calls
  `_clear_sketch_tools_state(port)`.
- Appends event to `state._board_events` (capped at 100).
- Broadcasts rendered event HTML via WebSocket (HTMX `hx-swap-oob`).

| Param | Type | Purpose |
|-------|------|---------|
| `msg` | `dict` | PubSub message with `topic` and `data` |

### `_on_daemon_ready(msg: dict) -> None`

Handle the daemon ready event. Sets `state._daemon_ready = True`.

| Param | Type | Purpose |
|-------|------|---------|
| `msg` | `dict` | PubSub event message |

### `_on_resp(msg: dict) -> None`

Handle a response message. Looks up the topic in `state._pending_responses`,
sets the response data and signals the waiting event.

| Param | Type | Purpose |
|-------|------|---------|
| `msg` | `dict` | Response message with `topic` |

### `_wait_for_response(topic: str, timeout: float = 60.0) -> dict | None`

Wait for a response on a given topic. Creates a `threading.Event`, registers it
in `state._pending_responses`, blocks up to `timeout` seconds.

| Param | Type | Default | Purpose |
|-------|------|---------|---------|
| `topic` | `str` | — | Topic to wait for |
| `timeout` | `float` | `60.0` | Maximum wait time in seconds |

Returns: Response message dict, or `None` on timeout.

```python
resp = _wait_for_response("resp::compile::abc123", timeout=30.0)
```

### `_on_pubsub_reconnect() -> None`

Re-register all PubSub handlers after a reconnection. Resets
`state._daemon_ready = False`, re-subscribes all topic handlers.

### `is_daemon_ready() -> bool`

Return whether the daemon has reported ready (from `state._daemon_ready`).

### `is_connected() -> bool`

Return whether the PubSub client is connected (via `PubSubClient.is_connected`).

### `add_ws_client(ws) -> None`

Register a WebSocket client for broadcast. Appends to `state._ws_clients`
under `state._ws_lock`.

| Param | Type | Purpose |
|-------|------|---------|
| `ws` | WebSocket | WebSocket connection object |

### `remove_ws_client(ws) -> None`

Unregister a WebSocket client. Removes from `state._ws_clients` under lock.

| Param | Type | Purpose |
|-------|------|---------|
| `ws` | WebSocket | WebSocket connection object |

### `broadcast_ws(html: str) -> None`

Send HTML to all connected WebSocket clients. Iterates `state._ws_clients`
under lock, removes dead clients on send failure.

| Param | Type | Purpose |
|-------|------|---------|
| `html` | `str` | HTML string to broadcast |

```python
broadcast_ws('<div class="event">Board connected!</div>')
```

### `_clear_sketch_tools_state(port: str) -> None`

Clear `ArduinoSketchTools` state for a given port. Removes entries from
`_compile_results`, `_upload_results`, `_compile_start`, `_compile_meta`,
`_upload_meta`, `_last_compiled_sketch`, `_last_compile_mtime`,
`_last_compile_checksum`, `_last_uploaded_sketch`.

| Param | Type | Purpose |
|-------|------|---------|
| `port` | `str` | Board port to clear state for |

### Fallback Scanner

#### `_start_fallback_scanner(ps: PubSubClient) -> None`

Start the fallback board scanner thread. Creates a daemon thread running
`_fallback_scan_loop`.

#### `_stop_fallback_scanner() -> None`

Signal the fallback scanner thread to stop (sets `state._stop_fallback_scan`).

#### `_fallback_scan_loop(ps: PubSubClient) -> None`

Continuously scan for boards via glob patterns (`/dev/ttyACM*`, `/dev/ttyUSB*`)
as a fallback when the PubSub daemon has not reported ready. Compares current
scan against `state._known_ports` and synthesizes connect/disconnect events.

#### `_resolve_board_info(port: str) -> dict`

Resolve board name, FQBN, and hardware ID for a port via `ArduinoGrpcClient`.
Returns dict with keys `board`, `fqbn`, `hardware_id`.

## Module-Level Globals

| Variable | Description |
|----------|-------------|
| `_pubsub` | Module-level `PubSubClient` instance (under `_pubsub_lock`) |
| `SKETCH_DIR` | `load_sketch_dir()` at import time |
| `ALARM_HPP_PATH` | `_get_alarm_hpp_path()` at import time |
