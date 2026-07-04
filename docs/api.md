---
layout: default
---
# API Reference

> **Per-package docs:** For detailed module-level API documentation, see:
> - [`board_manager/docs/protocol.md`](../board_manager/python/board_manager/docs/protocol.md) — framing, handshake, encode/decode
> - [`board_manager/docs/router.md`](../board_manager/python/board_manager/docs/router.md) — pub/sub topic routing
> - [`board_manager/docs/service.md`](../board_manager/python/board_manager/docs/service.md) — BoardManagerService event loop
> - [`arduino_grpc/docs/client.md`](../grpc_client/python/arduino_grpc/docs/client.md) — ArduinoGrpcClient full API
> - [`arduino_grpc/docs/models.md`](../grpc_client/python/arduino_grpc/docs/models.md) — data models
> - [`board_manager_client/docs/pubsub_client.md`](../board_manager_client/python/board_manager_client/docs/pubsub_client.md) — PubSubClient full API
> - [`arduino_dash/docs/html_routes.md`](../arduino_dash/python/arduino_dash/docs/html_routes.md) — arduino-dash routes
> - [`arduino_dash/docs/api_routes.md`](../arduino_dash/python/arduino_dash/docs/api_routes.md) — arduino-dash JSON API
> - [`medminder_dash/docs/html_routes.md`](../medminder_dash/python/medminder_dash/docs/html_routes.md) — medminder-dash routes
> - [`medminder_dash/docs/api_routes.md`](../medminder_dash/python/medminder_dash/docs/api_routes.md) — medminder-dash JSON API

## Pub/Sub Protocol (BoardManager Service)

All packages communicate over a custom JSON-line pub/sub protocol via Unix Domain Socket (primary) or TCP (fallback).

### Connection

1. Client opens a TCP or UDS connection to BoardManagerService.
2. Client sends a single handshake byte to select framing mode:
   - `\x01` — Newline framing (default)
   - `\x02` — Length-prefixed framing

### Framing

**Newline mode:** Each message is a JSON object followed by `\n`. The reader buffers until a newline is found, then parses one JSON message. Multiple messages may arrive in a single TCP segment; the reader handles splitting.

**Length mode:** Each message is prefixed with a 4-byte big-endian unsigned integer (the payload length), followed by that many bytes of JSON. This avoids the need to escape newlines in payloads.

### Message Types

All messages are JSON objects with at minimum a `"type"` field.

#### `subscribe`

```json
{"type": "subscribe", "topic": "board::+::event"}
{"type": "subscribe", "topics": ["board::+::event", "sys::daemon/ready"]}
```

Subscribes the connection to one or more topic patterns. Returns a result message:

```json
{"type": "result", "status": "ok", "topic": "board::+::event"}
```

On first subscribe, the server also emits current board state (synthetic `connected` events) and daemon-ready state. These are sent only once per connection.

#### `unsubscribe`

```json
{"type": "unsubscribe", "topic": "board::+::event"}
```

Removes a subscription.

#### `publish`

```json
{
  "type": "publish",
  "topic": "board::/dev/ttyACM0::cmd",
  "id": "req-001",
  "reply_to": "resp::compile::/dev/ttyACM0",
  "body": {"method": "compile", "params": {"sketch_path": "/tmp/sketch"}}
}
```

Sends a command to a board worker. The `reply_to` topic receives the result. Common methods: `compile`, `upload`, `compile_and_upload`, `init`, `spawn`, `status`, `remove`, `ping`, `health`, `list_boards`, `list_all_boards`.

#### `event`

```json
{"type": "event", "topic": "board::/dev/ttyACM0::event", "data": {"event": "connected", "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno"}}
```

Server-to-client notification. Board connect/disconnect, daemon ready, progress updates.

#### `result`

```json
{"type": "result", "id": "req-001", "topic": "resp::compile::/dev/ttyACM0", "status": "ok", "data": {"success": true, "output": "...", "error": ""}}
```

Response to a `publish` command. Correlation via `id` and `reply_to`/`topic`.

#### `error`

```json
{"type": "error", "id": "req-001", "code": "spawn_failed", "message": "Worker already running for /dev/ttyACM0"}
```

Error response.

#### `pong`

```json
{"type": "pong"}
```

Keep-alive acknowledgement.

### Topic Namespace

Topics use `::` (double colon) as separator to avoid conflicts with serial port paths (`/dev/ttyACM0`).

| Pattern | Purpose |
|---------|---------|
| `board::<port>::cmd` | Send commands to a board worker |
| `board::<port>::event` | Board connect/disconnect events |
| `board::<port>::status` | Board status updates |
| `resp::compile::<port>` | Compile result |
| `resp::compile::<port>::progress` | Compile progress stream |
| `resp::upload::<port>` | Upload result |
| `resp::upload::<port>::progress` | Upload progress stream |
| `sys::daemon/ready` | Arduino CLI daemon readiness |
| `sys::health` | Health check |
| `worker/ready` | Board worker readiness |

### Wildcards

- `+` matches exactly one level: `board::+::event` matches `board::/dev/ttyACM0::event`
- `*` matches the rest of the topic: `board::/dev/ttyACM0::*` matches all sub-topics

### Activity Diagram

```
Client                  BoardManager              Board Worker
  │                         │                         │
  ├── handshake byte ──────►│                         │
  │                         │                         │
  ├── subscribe ───────────►│                         │
  │                         ├── synthetic events      │
  │◄── result ─────────────┤                         │
  │                         │                         │
  ├── publish (compile) ───►│                         │
  │                         ├── dispatch ────────────►│
  │                         │                         ├── gRPC compile()
  │                         │◄── progress ───────────┤
  │◄── progress ───────────┤                         │
  │                         │◄── result ─────────────┤
  │◄── result ─────────────┤                         │
```

---

## gRPC Client — `ArduinoGrpcClient`

**Package:** `arduino-grpc`  
**Module:** `arduino_grpc.client`

### Constructor

```python
client = ArduinoGrpcClient(daemon="localhost:50051")
```

| Arg | Default | Description |
|-----|---------|-------------|
| `daemon` | `"localhost:50051"` | Arduino CLI daemon gRPC address |

### Methods

#### `connect()`
Establish the gRPC channel. Raises `ConnectionError` on failure. Also available as context manager:

```python
with ArduinoGrpcClient("localhost:50051") as client:
    ...
```

#### `disconnect()`
Close the gRPC channel.

#### `init()`
Send `Init` request to the daemon. Must be called before any board operations. Raises `InitializationError` on failure.

#### `list_boards(timeout=5)` → `list[Board]`
List Arduino boards detected on USB. Returns `Board` objects with `.port.address`, `.fqbn`, `.name`, `.detected`.

#### `list_all_boards()` → `list[Board]`
List all boards (including those not detected). Slower but comprehensive.

#### `watch_boards(callback)`
Register a streaming callback for board add/remove events. The callback receives `(action, board)` where action is `"add"` or `"remove"`.

#### `compile(sketch_path, fqbn="arduino:avr:uno", profile=False, source_overrides=None)` → `CompileResult`
Compile a sketch directory.

#### `upload(sketch_path, port, fqbn="arduino:avr:uno", profile=False)` → `UploadResult`
Upload a compiled sketch to a board.

#### `compile_stream(...)` → `Generator[tuple[str,str,bool,float], None, CompileResult]`
Streaming compile that yields `(out, err, done, percent)` 4-tuples (percent is 0.0–100.0 from `TaskProgress`) and returns the final `CompileResult`. The 4-tuple was introduced in Phase 98 — before that it was a 3-tuple without percent.

#### `upload_stream(...)` → `Generator[tuple[str,str,bool], None, UploadResult]`
Streaming upload that yields `(out, err, done)` 3-tuples (no percent — `UploadResponse` has no `TaskProgress`) and returns the final `UploadResult`. Upload remains a 3-tuple because the gRPC `UploadResponse` message has no `TaskProgress` field. 

#### `compile_and_upload(sketch_path, port, fqbn, profile=False, source_overrides=None)` → `tuple[CompileResult, UploadResult]`
Compile then upload in sequence.

### Data Models (`arduino_grpc.models`)

```python
@dataclass
class Port:
    address: str           # "/dev/ttyACM0"
    protocol: str          # "serial"
    protocol_label: str    # "Serial Port (USB)"
    label: str             # "Arduino Uno"
    properties: dict       # USB VID/PID properties
    hardware_id: str       # "USB VID:PID=2341:0043 SER=12345"

@dataclass
class Board:
    port: Port
    fqbn: str              # "arduino:avr:uno"
    name: str              # "Arduino Uno"
    detected: bool

@dataclass
class CompileResult:
    success: bool
    output: str
    error: str
    sketch_path: str

@dataclass
class UploadResult:
    success: bool
    output: str
    error: str
```

### Exceptions (`arduino_grpc.exceptions`)

| Exception | Base | Raised When |
|-----------|------|-------------|
| `ArduinoError` | `Exception` | Base for all custom exceptions |
| `ConnectionError` | `ArduinoError` | gRPC channel cannot connect |
| `InitializationError` | `ArduinoError` | `Init` RPC fails |
| `CompileError` | `ArduinoError` | Compilation fails |
| `UploadError` | `ArduinoError` | Upload fails |
| `BoardError` | `ArduinoError` | Board not found |
| `InvalidPortError` | `BoardError` | Port path is invalid |
| `InvalidFqbnError` | `BoardError` | FQBN is invalid |

---

## PubSubClient

**Package:** `board_manager_client`  
**Module:** `board_manager_client.pubsub_client`

### Constructor

```python
client = PubSubClient(
    uds_path="/tmp/board_mgr.sock",
    tcp_host="127.0.0.1",
    tcp_port=9090,
    reconnect_config=ReconnectConfig(max_attempts=5, base_delay=0.5, max_delay=5.0),
)
```

### Methods

#### `connect()`
Establish connection with handshake.

#### `close()`
Close the connection.

#### `subscribe(topic)` / `unsubscribe(topic)`
Subscribe or unsubscribe from a topic.

#### `publish(topic, body=None, reply_to=None, timeout=10)` → `dict`
Publish a message and wait for response. Returns the response dict. Raises `TimeoutError` if no response within `timeout`.

#### `request_boards(timeout=10)` → `list[dict]`
Convenience method: publishes `list_boards` request and returns the board list.

### Callbacks

```python
client.on_message = lambda msg: print(msg)
client.on_board_event = lambda port, event, data: print(port, event)
client.on_daemon_ready = lambda: print("daemon ready")
client.on_reconnect = lambda: print("reconnected")
```

### ReconnectConfig

| Field | Default | Description |
|-------|---------|-------------|
| `max_attempts` | `5` | Maximum reconnection attempts |
| `base_delay` | `0.5` | Initial retry delay (seconds) |
| `max_delay` | `5.0` | Maximum retry delay (seconds) |

---

## Flask HTML Routes

### arduino-dash (`arduino_dash.html_routes`)

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Dashboard: board grid, compile/upload cards |
| `/board/<port>` | GET | Board detail: status, compile/upload, event log |
| `/board/<port>/connection-status` | GET | Board connection status badge partial |
| `/boards/grid` | GET | Grid view of all boards |
| `/admin` | GET | Admin page: board selector, sketch management |
| `/admin/board-selector` | GET | Board selector partial (HTMX) |
| `/admin/active-board` | POST | Set active board in session |
| `/board/compile-upload-card` | GET | Compile/upload card partial (HTMX) |
| `/daemon/status` | GET | Daemon status badge partial |
| `/last-upload` | GET | Last upload info partial |
| `/sketch/upload` | POST | Upload a sketch archive |
| `/sketch` | DELETE | Delete a sketch version |
| `/ws/board-events` | WS | WebSocket endpoint for live board events |

### medminder-dash (`medminder_dash.html_routes`)

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page with board selector |
| `/board` | GET | Board detail: medicine CRUD, compile/upload |
| `/board/<port>` | GET | Board detail page for a specific port |
| `/board/<port>/connection-status` | GET | Board connection status badge partial |
| `/board/select/<port>` | GET | Select a board, redirects to board detail |
| `/boards` | GET | All boards overview |
| `/boards/grid` | GET | Grid view of all boards |
| `/admin` | GET | Admin page: board selector, sketch management |
| `/admin/board-selector` | GET | Board selector partial (HTMX) |
| `/admin/active-board` | POST | Set active board in session |
| `/board/compile-upload-card` | GET | Compile/upload card partial (HTMX) |
| `/daemon/status` | GET | Daemon status badge partial |
| `/medicines` | GET | Medicine list page |
| `/medicine/new` | GET | Medicine creation form |
| `/medicines/board-selector` | GET | Board selector dropdown partial |
| `/medicines/active-board-card` | GET | Active board medicine cards partial |
| `/medicines/confirm-modal` | GET | Confirm modal partial |
| `/medicines/generate-hpp` | POST | Generate alarm.hpp from medicines |
| `/medicines/sync-from-hpp` | POST | Sync medicines from alarm.hpp |
| `/last-upload` | GET | Last upload info partial |
| `/sketch/upload` | POST | Upload a sketch archive |
| `/sketch` | DELETE | Delete a sketch version |
| `/ws/board-events` | WS | WebSocket endpoint for live board events |

> **Note:** The `/boards/event` HTML route was removed in Phase 103. Board events are now served via `GET /api/boards/events` and pushed via WebSocket.

---

## Flask JSON API Routes

### arduino-dash (`arduino_dash.api_routes`)

#### PubSub Board Commands (sent to BoardManagerService via PubSub)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/pubsub/board/<port>/spawn` | POST | Publish board spawn command to PubSub |
| `/api/pubsub/board/<port>/status` | GET | Publish board status request to PubSub |
| `/api/pubsub/board/<port>/remove` | POST | Publish board remove command to PubSub |
| `/api/pubsub/boards/health` | POST | Publish boards health check to PubSub |

#### Local CRUD (from cached state)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/daemon/status` | GET | Daemon ready + connected status |
| `/api/board/<port>/status` | GET | Board connection status from local state (`get_port_info()`) |
| `/api/boards/list` | GET | List all known boards from local state |
| `/api/boards/events` | GET | Recent board connect/disconnect events (capped at 100) |

#### Sketch Management

| Route | Method | Description |
|-------|--------|-------------|
| `/api/sketches` | GET | List uploaded sketches (optional `?hardware_id=X` filter) |
| `/api/sketches/last-upload` | GET | Latest sketch upload (returns dict + 200 or null + 404) |
| `/api/sketch/upload` | POST | Upload sketch archive (multipart, optional `?hardware_id=...`) |
| `/api/sketch` | DELETE | Delete a sketch version |

### medminder-dash (`medminder_dash.api_routes`)

#### PubSub Board Commands (sent to BoardManagerService via PubSub)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/pubsub/board/<port>/spawn` | POST | Publish board spawn command to PubSub |
| `/api/pubsub/board/<port>/status` | GET | Publish board status request to PubSub |
| `/api/pubsub/board/<port>/remove` | POST | Publish board remove command to PubSub |
| `/api/pubsub/boards/health` | POST | Publish boards health check to PubSub |

#### Local CRUD (from cached state)

| Route | Method | Description |
|-------|--------|-------------|
| `/api/daemon/status` | GET | Daemon ready + connected status |
| `/api/board/<port>/status` | GET | Board connection status from local state (`get_port_info()`) |
| `/api/boards/list` | GET | List all known boards from local state |
| `/api/boards/events` | GET | Recent board connect/disconnect events |

#### Medicine CRUD

| Route | Method | Description |
|-------|--------|-------------|
| `/api/medicines/diff` | GET | Diff between store and alarm.hpp |
| `/api/medicines` | GET | List all medicines |
| `/api/medicine` | POST | Create a medicine (returns 201) |
| `/api/medicine/<id>` | GET | Get a single medicine (or 404) |
| `/api/medicine/<id>` | PUT | Update a medicine |
| `/api/medicine/<id>` | DELETE | Delete a medicine (or 404) |
| `/api/medicine/<id>/toggle` | PUT | Toggle medicine enabled/disabled |

#### Sketch Management

| Route | Method | Description |
|-------|--------|-------------|
| `/api/sketches` | GET | List uploaded sketches (optional `?hardware_id=X` filter) |
| `/api/sketches/last-upload` | GET | Latest sketch upload (returns dict + 200 or null + 404) |
| `/api/sketch/upload` | POST | Upload sketch archive (multipart, optional `?hardware_id=...`) |
| `/api/sketch` | DELETE | Delete a sketch version |

---

## Board Worker Progress Protocol

**Package:** `board_manager`  
**Module:** `board_manager.board_worker`

The `_make_progress()` helper constructs progress event dicts for compile/upload streaming output:

```python
def _make_progress(msg: dict, out: str, err: str, percent: float = 0.0) -> dict
```

Returns a dict with `topic` set to `resp::compile::<port>::progress` (or `resp::upload::<port>::progress`) and `data` containing `output`, `error`, and `percent` fields. The board worker's compile loop iterates the 4-tuple from `compile_stream()`, sending each `(out, err, done, percent)` as a progress event via the socketpair IPC. When only the percentage changes (no output), a progress-only event is sent to drive the progress bar without duplicating output lines.

---

## WebSocket OOB Broadcast Pattern

All frontend updates use a single persistent WebSocket connection established by HTMX's `ws.js` extension:

```html
<div id="event-feed" hx-ext="ws" ws-connect="/ws/board-events"></div>
```

> **Transport dependency**: `flask-sock` needs a WebSocket transport implementation. Both dashboards depend on `simple-websocket>=1.0.0` which provides WS transport for sync WSGI servers (Flask dev server, gunicorn sync workers). Without it, WS upgrade fails with `"Invalid frame header"`.

The server sends raw HTML with `hx-swap-oob` attributes; HTMX swaps the content into the DOM. Four tiers of OOB broadcasts exist:

### Tier 1 — Badge OOB

Daemon status badge broadcasts on daemon state change from `_broadcast_daemon_badge()`:

```python
oob = '<span id="daemon-badge" hx-swap-oob="true">Connected</span>'
broadcast_ws(oob)
```

Board status badge uses per-port unique IDs (`board-status-badge--{port_safe}`) to target individual board detail pages:

```python
port_safe = port.replace("/", "_")
oob = f'<span id="board-status-badge--{port_safe}" hx-swap-oob="true">{badge}</span>'
```

### Tier 2 — Compile/Upload OOB

Output lines from `_on_compile_resp()` / `_on_upload_resp()` in the ArduinoSketchTools extension are wrapped in targeted OOB spans:

```python
html = f'<span hx-swap-oob="beforeend:#compile-output-{port_safe}">'
html += f'<div class="compile-line">{pct_prefix}{text}</div></span>'
broadcast_ws(html)
```

### Tier 3 — Compile Progress Bar OOB

Progress percentage drives a `<progress>` element broadcast only on change (suppressed via `_compile_last_pct` tracking per port):

```python
bar = f'<progress id="compile-progress-{port_safe}" value="{pct_int}" max="100" hx-swap-oob="true"></progress>'
broadcast_ws(bar)
```

All three tiers share the same `broadcast_ws(html)` function that iterates connected WS clients and sends each one the raw HTML string.

---

## ArduinoSketchTools Flask Extension

**Package:** `arduino_sketch_tools`  

### `ArduinoSketchTools` (extension.py)

**Module:** `arduino_sketch_tools.extension`

```python
from arduino_sketch_tools import ArduinoSketchTools

tools = ArduinoSketchTools()
tools.init_app(app)
```

Registers a Flask blueprint with compile/upload routes and subscribes to `resp::compile::*` and `resp::upload::*` pub/sub topics. Progress messages are broadcast via WebSocket.

### `SketchRegistry` (sketch_registry.py)

**Module:** `arduino_sketch_tools.sketch_registry`

```python
from arduino_sketch_tools import SketchRegistry

_registry = SketchRegistry(state._upload_registry, state._upload_registry_lock)
```

Thread-safe registry mapping `hardware_id → sketch_path`. Extracted to the shared package in Phase 99; per-app `sketch_registry.py` modules re-export bound methods from a module-level instance. API: `get_assignment()`, `set_assignment()`, `clear_assignment()`, `get_all_assignments()`. See [`arduino_sketch_tools/docs/sketch_registry.md`](../arduino_sketch_tools/python/arduino_sketch_tools/docs/sketch_registry.md) for full reference.

---

## Environment Variables

### BoardManager Service

| Variable | Default | Description |
|----------|---------|-------------|
| `BOARD_MGR_TCP_HOST` | `127.0.0.1` | TCP bind host |
| `BOARD_MGR_TCP_PORT` | `9090` | TCP bind port |
| `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` | Unix domain socket path |
| `BOARD_MGR_ARDUINO_DAEMON` | `localhost:50051` | Arduino CLI daemon address |
| `BOARD_MGR_DAEMON_BINARY` | `arduino-cli` | Arduino CLI binary path |
| `BOARD_MGR_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `BOARD_MGR_CONFIG` | `""` | Path to TOML config file |
| `BOARD_MGR_DETECTION_MODE` | `watch` | Board detection mode (`watch` or `poll`) |

### Web Apps

| Variable | Default | Description |
|----------|---------|-------------|
| `BMS_NO_UDS` | `false` | Force TCP-only transport |
| `BMS_FIRE_AND_FORGET` | `false` | Don't wait for BMS readiness |
| `BMS_WAIT_TIMEOUT` | `10` | BMS readiness wait timeout (seconds) |
| `GUNICORN_BIND` | `0.0.0.0:8080` | Gunicorn bind address |
| `GUNICORN_WORKERS` | `4` | Number of Gunicorn workers |
| `GUNICORN_TIMEOUT` | `120` | Gunicorn worker timeout (seconds) |
| `GUNICORN_LOG_LEVEL` | `info` | Gunicorn log level |
| `FLASK_SECRET_KEY` | `dev-secret` | Flask session secret key (medminder-dash) |
| `ARDUINO_DASH_SECRET` | `dev-secret-arduino` | Flask session secret key (arduino-dash) |
