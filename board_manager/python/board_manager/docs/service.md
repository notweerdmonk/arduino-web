---
---
# BoardManagerService

## Purpose

`BoardManagerService` is the main event loop of the board_manager package. It manages TCP and Unix Domain Socket (UDS) listeners, accepts client connections, routes pub/sub messages via `TopicRouter`, and orchestrates the `BoardDetector`, `DaemonManager`, and `BoardPool` subcomponents.

## Location

`board_manager/service.py`

---

## Class: `SysTopic`

An `str` Enum of system-level pub/sub topic constants.

#### `DAEMON_READY = "sys::daemon/ready"`

Published when the arduino-cli daemon has started successfully.

---

## Class: `ClientConn`

State container for a single TCP or UDS client connection.

#### `__init__(self, sock: socket.socket, addr: str)`

| Param | Type | Description |
|-------|------|-------------|
| `sock` | `socket.socket` | The client socket |
| `addr` | `str` | Human-readable client address string |

**State attributes:**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `reader` | `FrameReader` | `FrameReader("newline")` | Per-connection frame reader |
| `framing_mode` | `str` | `"newline"` | `"newline"` or `"length"` |
| `handshake_done` | `bool` | `False` | Whether initial handshake completed |
| `initial_state_sent` | `bool` | `False` | Whether initial board/daemon state was sent to this client |

#### `fileno(self) -> int`

Returns the socket file descriptor number.

#### `close(self) -> None`

Closes the client socket, swallowing `OSError`.

---

## Class: `BoardManagerService`

Main service: TCP+UDS listener, message routing, subprocess management.

### Constructor

#### `__init__(self, config: Config)`

| Param | Type | Description |
|-------|------|-------------|
| `config` | `Config` | Service configuration dataclass |

**Initialises:**
- `self.pool` — a `BoardPool` instance
- `self.router` — a `TopicRouter` instance
- `self._clients` — empty dict mapping fd → `ClientConn`
- `self._board_state` — empty dict mapping port → board info dict
- `self._daemon_ready` — `False`
- All internal sockets and thread handles to `None`

---

### Public Methods

#### `start(self) -> None`

Starts the service:

1. Binds TCP and UDS listening sockets via `_bind_tcp()` / `_bind_uds()`
2. Creates and starts `DaemonManager`; on success publishes `sys::daemon/ready`
3. Creates and starts `BoardDetector` with `_on_detector_event` callback
4. Enters the main event loop calling `_tick()` until `_running` is `False`

**Edge cases:**
- If the daemon fails to start, the error is logged but the service continues — the `BoardDetector` will retry daemon connection on each detection cycle.
- `SIGINT` will exit the loop.

#### `stop(self) -> None`

Graceful shutdown:

1. Sets `_running = False` (event loop exits)
2. Stops the `BoardDetector`
3. Shuts down all board worker subprocesses via `pool.shutdown_all()`
4. Stops the `DaemonManager`

---

### Private Methods

#### `_publish_daemon_ready(self) -> None`

Publishes a `sys::daemon/ready` event to all subscribers of `SysTopic.DAEMON_READY`. Sets `_daemon_ready = True`.

#### `_on_detector_event(self, port: str, msg: dict) -> None`

Callback invoked by `BoardDetector` on board connect/disconnect.

| Param | Type | Description |
|-------|------|-------------|
| `port` | `str` | The serial port address |
| `msg` | `dict` | The event message dict |

Updates `_board_state` and calls `_route_pool_message` to forward the event to subscribers.

#### `_tick(self) -> None`

Single event loop iteration:

1. Builds the read socket list (listener sockets + all client sockets)
2. Calls `select.select()` with a 100ms timeout
3. Accepts new TCP or UDS connections on listener sockets
4. Reads and processes data on client sockets
5. Polls `BoardPool` for worker messages and routes them

#### `_accept_tcp(self) -> None`

Accepts a new TCP client connection. Performs protocol handshake by reading the first byte:

- `\x01` → `"newline"` framing mode
- `\x02` → `"length"` framing mode
- Any other byte → treated as the start of a newline-framed message (fallback)

Creates a `ClientConn` and adds it to `_clients`.

#### `_accept_uds(self) -> None`

Accepts a new UDS client connection. UDS clients skip the handshake byte (assumed `handshake_done = True`). Each UDS client gets an incrementing numeric ID (`uds:0`, `uds:1`, etc.).

#### `_bind_tcp(self) -> socket.socket`

Creates a `TCP` listener socket:

- `socket.AF_INET` + `SOCK_STREAM`
- `SO_REUSEADDR` enabled
- Binds to `config.tcp_host:config.tcp_port`
- Backlog of 10 connections
- Blocking mode

Returns the bound socket.

#### `_bind_uds(self) -> socket.socket`

Creates a UDS listener socket:

- `socket.AF_UNIX` + `SOCK_STREAM`
- Unlinks existing socket file at `config.uds_path`
- Binds and listens (backlog 10)
- Sets permissions to `0o666` (world-accessible)
- Blocking mode

Returns the bound socket.

#### `_read_client(self, sock: socket.socket) -> None`

Reads up to 65536 bytes from a client socket. Feeds data into the connection's `FrameReader` and processes all complete messages via `_handle_client_message`. Removes the client on connection close or error.

#### `_handle_client_message(self, conn: ClientConn, msg: dict) -> None`

Routes a parsed client message by its `type` field:

| `type` | Action |
|--------|--------|
| `"subscribe"` | Calls `router.subscribe()` for each topic; sends initial board state and daemon state on first subscribe |
| `"unsubscribe"` | Calls `router.unsubscribe()` for each topic |
| `"publish"` | Dispatches to board command handler (`board::<port>::cmd`), `list_all_boards`, `list_boards`, `health`, or returns port list |
| `"pong"` | Ignored |
| other | Logged as warning |

#### `_handle_board_command(self, conn: ClientConn, port: str, msg: dict) -> None`

Handles a board-specific command message. Supported methods:

| Method | Action |
|--------|--------|
| `"spawn"` | Calls `pool.spawn(port)` |
| `"status"` | Returns `pool.get_port_status(port)` |
| `"remove"` | Calls `pool.remove(port)` |
| other | Auto-spawns worker if not running, then dispatches the method via `pool.dispatch(port, msg)` |

**Edge case:** If spawn fails, an `"error"` response is sent with code `"spawn_failed"`.

#### `_handle_list_all_boards(self, conn: ClientConn, msg: dict) -> None`

Returns status for every port managed by the pool.

#### `_route_pool_message(self, port: str, msg: dict, topic: str) -> None`

Routes a message from a board worker to subscribers:

1. Skips messages with empty topic
2. Logs compile/upload result summaries
3. Builds subscriber set from three topics:
   - The exact topic
   - `board::<port>::event`
   - `board::<port>::status`
4. Sends the message to all matching subscribers via `_send()`

#### `_send_current_boards_to(self, conn: ClientConn) -> None`

Sends synthetic `"connected"` events for all currently known boards to a newly subscribed client. Matches against the client's subscriptions.

#### `_send_daemon_state_to(self, conn: ClientConn) -> None`

Sends a synthetic `sys::daemon/ready` event if the daemon is ready and the client is subscribed.

#### `_find_client(self, addr: str) -> Optional[ClientConn]`

Linear search through `_clients` for a connection matching the given address string. Returns the `ClientConn` or `None`.

#### `_send(self, conn: ClientConn, msg: dict) -> None`

Encodes and frames a message dict using the connection's framing mode and sends it via `sendall()`. Removes the client on send failure.

#### `_remove_client(self, conn: ClientConn) -> None`

Removes a client: unsubscribes all topic patterns, removes from `_clients` dict, closes the socket.

---

### Client Lifecycle

```
TCP Client:          connect → _accept_tcp → handshake byte → FrameReader mode
UDS Client:          connect → _accept_uds → handshake_done=True

Both:
  → _handle_client_message (subscribe/unsubscribe/publish)
  → On disconnect: _remove_client → unsubscribe_all → close()
```

---

### Daemon State Re-emission

When a client subscribes for the first time (`initial_state_sent == False`), the service automatically sends:

1. **Current board state** — synthetic `"connected"` events for every board in `_board_state`
2. **Daemon state** — synthetic `sys::daemon/ready` event if the daemon is running

This ensures clients never see an empty board list after connecting.
