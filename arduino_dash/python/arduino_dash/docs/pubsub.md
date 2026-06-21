---
---
# pubsub (pubsub.py)

PubSub infrastructure — connects to `BoardManagerService`, subscribes to topics, handles board events, broadcasts via WebSocket, and manages request/response patterns.

## Class

### `PubSubTopic(str, Enum)`

Topic constants used for PubSub subscription and publishing.

| Member | Value | Description |
|--------|-------|-------------|
| `DAEMON_READY` | `"sys::daemon/ready"` | Emitted when the Arduino daemon is ready |
| `BOARD_EVENT` | `"board::+::event"` | Board connect/disconnect events (wildcard `+`) |
| `RESP` | `"resp::*"` | All response messages (wildcard `*`) |
| `HEALTH` | `"sys::health"` | Health check pings |
| `RESP_COMPILE` | `"resp::compile::*"` | Compile response messages |
| `RESP_UPLOAD` | `"resp::upload::*"` | Upload response messages |

## Functions

### `init_pubsub(use_uds: bool = True, tcp_host: str = "127.0.0.1", tcp_port: int = 9090, uds_path: str = "/tmp/board_mgr.sock") -> None`

Connect PubSub to `BoardManagerService` and subscribe to all topics.

1. Creates a `PubSubClient` with the given transport parameters
2. Sets `state.pubsub.on_reconnect = _on_pubsub_reconnect`
3. Calls `state.pubsub.connect(retry=True)`
4. Subscribes to all topics:
   - `PubSubTopic.DAEMON_READY` → `_on_daemon_ready`
   - `PubSubTopic.BOARD_EVENT` → `_on_board_event`
   - `PubSubTopic.RESP` → `_on_resp`
   - `PubSubTopic.HEALTH` → `_on_health`
   - `PubSubTopic.RESP_COMPILE` → `tools._on_compile_resp` (if `ArduinoSketchTools` extension registered)
   - `PubSubTopic.RESP_UPLOAD` → `tools._on_upload_resp` (if `ArduinoSketchTools` extension registered)
5. Assigns `state.pubsub` to `tools.pubsub` if extension exists
6. Starts the reader thread via `state.pubsub.start_reader()`

```python
init_pubsub()
init_pubsub(use_uds=False, tcp_host="192.168.1.10", tcp_port=9090)
```

### `_on_daemon_ready(msg: dict) -> None`

Handle the daemon ready event. Sets `state._daemon_ready = True` (idempotent — skips if already set).

### `_on_board_event(msg: dict) -> None`

Handle board connect/disconnect events.

- On `"connected"`: adds board data to `state._board_list` (if not already present)
- On `"disconnected"`: removes from `_board_list`, cleans up per-port sketch state in both `state` and `ArduinoSketchTools` extension
- Renders a `board_event.html` partial and broadcasts it via `_broadcast_ws()` as an OOB swap

### `_on_health(msg: dict) -> None`

Handle health check messages. Currently a no-op.

### `_on_resp(msg: dict) -> None`

Handle response messages and wake waiting callers. If there is a pending waiter for the response topic, stores the message and sets the threading `Event` to wake the waiter.

### `_on_pubsub_reconnect() -> None`

Re-register all PubSub subscriptions after a reconnection. Resets `state._daemon_ready = False`, then re-subscribes all the same handlers as `init_pubsub()`.

### `_wait_for_response(topic: str, timeout: float = 60.0) -> dict | None`

Wait for a response on the given topic with a timeout.

1. Creates a `threading.Event`
2. Registers the event in `state._pending_responses[topic]`
3. Waits for the event to be set (up to `timeout` seconds)
4. On signal: pops, and returns the response dict
5. On timeout: logs a warning and returns `None`
6. Guarantees cleanup in `finally` block

```python
result = _wait_for_response("resp:compile:abc123", timeout=30.0)
if result:
    print(result.get("data"))
```

### `_broadcast_ws(html: str) -> None`

Send HTML to all connected WebSocket clients. Iterates over `state._ws_clients`, attempts `ws.send(html)` on each, and removes disconnected clients on failure.

### `_compute_sketch_checksum(sketch_dir: str) -> str`

Compute a SHA-256 checksum over source files (`.ino`, `.cpp`, `.h`, `.hpp`, `.c`) in a sketch directory. Files are sorted for deterministic checksums. Returns empty string if no source files found.

```python
checksum = _compute_sketch_checksum("/path/to/sketch")
```

### `_get_sketch_mtime(sketch_path: str) -> float | None`

Return the latest modification time among source files in a sketch directory. Only considers `.ino`, `.cpp`, `.h`, `.hpp`, `.c` files. Returns `None` if the directory doesn't exist.

```python
mtime = _get_sketch_mtime("/path/to/sketch")
```

### `_make_meta(port: str, sketch_path: str) -> dict`

Build a metadata dict for a compile or upload operation.

```python
meta = _make_meta("/dev/ttyACM0", "/path/to/sketch")
# Returns:
# {
#     "port": "/dev/ttyACM0",
#     "board": "Arduino Uno",
#     "fqbn": "arduino:avr:uno",
#     "hardware_id": "...",
#     "sketch": "/path/to/sketch",
#     "sketch_name": "sketch",
# }
```

## Fallback Scanner

### `_start_fallback_scanner(ps: PubSubClient) -> None`

Start the background thread that polls for board connections via glob patterns (`/dev/ttyACM*`, `/dev/ttyUSB*`). Sets `state._stop_fallback_scan = False` and starts a daemon thread running `_fallback_scan_loop`.

### `_stop_fallback_scanner() -> None`

Signal the fallback scanner thread to stop.

### `_fallback_scan_loop(ps: PubSubClient) -> None`

Poll for boards via glob patterns and emit connect/disconnect events. Runs every `state._fallback_scan_interval` (default 5.0s) seconds. Skips scanning if `state._daemon_ready` is `True` (daemon mode preferred). On finding new ports or missing ports, calls `_on_board_event` with synthetic events.

### `_broadcast_daemon_badge() -> None`

Broadcast the daemon status badge HTML over WebSocket as an OOB swap. Fetches
the badge from `/daemon/status` via background HTTP GET, wraps it in
`<span id="daemon-badge" hx-swap-oob="true">...</span>`, and sends to all WS
clients. Called from:
- `_on_daemon_ready()` — on daemon ready/reconnect
- `_on_pubsub_reconnect()` — on PubSub reconnection

### Board Badge OOB (in `_on_board_event`)

When a board event is processed, the handler also broadcasts the board status
badge as an OOB swap. The badge targets a per-port ID
(`board-status-badge--{port_safe}`, where `port_safe` is the port path with
`/` replaced by `_`) so each board detail page receives only its own badge
update.

```python
badge = render_template("partials/board_status_badge.html", port=port, connected=connected)
oob = f'<span id="board-status-badge--{port_safe}" hx-swap-oob="true">{badge}</span>'
_broadcast_ws(oob)
```

### `_resolve_board_info(port: str) -> dict`

Resolve board metadata (name, fqbn, hardware_id) via the gRPC client. Creates an `ArduinoGrpcClient`, connects, calls `list_boards()`, and matches by port address. Used by the fallback scanner.
