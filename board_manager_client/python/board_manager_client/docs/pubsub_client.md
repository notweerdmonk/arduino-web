---
---
# PubSubClient

```python
class PubSubClient:
```

Persistent PubSub connection to BoardManagerService. Connects over Unix Domain Socket (primary) or TCP (fallback), auto-reconnects with exponential backoff, and maintains subscriptions across reconnects.

---

## Constructor

```python
def __init__(
    self,
    tcp_host: str = "127.0.0.1",
    tcp_port: int = 9090,
    uds_path: str = "/tmp/board_mgr.sock",
    use_uds: bool = True,
    on_reconnect: Optional[OnReconnect] = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tcp_host` | `str` | `"127.0.0.1"` | TCP hostname for fallback connection. |
| `tcp_port` | `int` | `9090` | TCP port for fallback connection. |
| `uds_path` | `str` | `"/tmp/board_mgr.sock"` | Path to the Unix domain socket. |
| `use_uds` | `bool` | `True` | Whether to attempt UDS connection first. |
| `on_reconnect` | `OnReconnect \| None` | `None` | Optional callback invoked after each reconnect. |

`OnReconnect` is `Callable[[], None]`.

---

## ReconnectConfig

```python
class ReconnectConfig:
```

Reconnection timing configuration. Read at runtime by the client — customize by modifying class attributes.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `RECONNECT_DELAY` | `float` | `2.0` | Seconds to wait before a reconnection attempt after the socket dies. |
| `CONNECT_RETRY_DELAYS` | `list[float]` | `[0.5, 1.0, 2.0]` | Delays (seconds) between successive initial connection attempts. |

### Example

```python
from board_manager_client.pubsub_client import ReconnectConfig

# Customise timing before creating the client
ReconnectConfig.RECONNECT_DELAY = 5.0
ReconnectConfig.CONNECT_RETRY_DELAYS = [1.0, 2.0, 4.0, 8.0]
```

---

## Connection

### `connect`

```python
def connect(self, retry: bool = False) -> None
```

Connect to the BoardManagerService.

- **`retry=False`** — single attempt; raises immediately on failure.
- **`retry=True`** — iterates through `ReconnectConfig.CONNECT_RETRY_DELAYS`, sleeping between attempts. If all fail, raises the last `ConnectionError` or `OSError`.

**Raises:** `ConnectionError`, `OSError`.

Internally calls `_create_socket` → `_send_handshake` → `_resubscribe` → `on_reconnect()`.

### `disconnect`

```python
def disconnect(self) -> None
```

Disconnect from the service and close the socket. Stops the reader loop (sets `_running = False`). Safe to call multiple times.

### `is_connected`

```python
@property
def is_connected(self) -> bool
```

`True` when the client holds an open socket (regardless of whether the reader thread is running).

### Typical startup sequence

```python
client = PubSubClient(uds_path="/tmp/board_mgr.sock")
client.connect(retry=True)
client.start_reader()
```

---

## PubSub Operations

### `subscribe`

```python
def subscribe(self, topic: str, handler: Optional[EventHandler] = None) -> None
```

Subscribe to a topic. Optionally register a callback handler.

- `topic` — Topic pattern. The server receives `{"type": "subscribe", "topic": topic}`. The client stores the topic in `_subscriptions` so it is re-sent on reconnect.
- `handler` — Optional `Callable[[dict], None]` invoked on every message matching this topic (including wildcard patterns).

If the socket is connected and the topic is **new** (not previously subscribed), the subscribe frame is sent immediately.

**Handler dispatch** uses `board_manager.router._match` for pattern matching. The special pattern `"*"` matches all topics.

### `unsubscribe`

```python
def unsubscribe(self, topic: str) -> None
```

Unsubscribe from a topic. Removes the topic from `_subscriptions` and deletes all handlers registered for it. Sends `{"type": "unsubscribe", "topic": topic}` if connected.

### `publish`

```python
def publish(self, topic: str, message: dict, reply_to: str = "") -> None
```

Publish a message on a topic.

Sends:
```json
{"type": "publish", "topic": topic, "body": message, "reply_to": reply_to}
```

### `request_boards`

```python
def request_boards(self, timeout: float = 10.0) -> list[dict] | None
```

Request the list of boards and wait for the response.

- Creates a unique reply topic (`resp::list_boards::<id>::<timestamp>`).
- Subscribes to that topic with a transient handler.
- Publishes `{"method": "list_boards"}` on `sys::boards` with the reply topic.
- Blocks up to `timeout` seconds.
- Returns the list of board dicts, or `None` on timeout.

### Example

```python
client = PubSubClient()
client.connect(retry=True)
client.start_reader()

boards = client.request_boards(timeout=5.0)
if boards is not None:
    for b in boards:
        print(b["name"])
```

---

## Callback Registration

### Constructor callback

The only callback API built into the constructor is `on_reconnect`:

```python
def on_reconnect() -> None:
    print("Reconnected to BoardManagerService")

client = PubSubClient(on_reconnect=on_reconnect)
```

### Topic handlers (subscribe)

All message callbacks are registered through `subscribe()`:

```python
def on_message(msg: dict) -> None:
    print(f"Got message on {msg['topic']}: {msg['body']}")

def on_board_event(msg: dict) -> None:
    print(f"Board event: {msg['body']}")

def on_daemon_ready(msg: dict) -> None:
    print("Daemon is ready")

client.subscribe("*", handler=on_message)
client.subscribe("sys::board_event", handler=on_board_event)
client.subscribe("sys::daemon_ready", handler=on_daemon_ready)
```

Topic patterns support glob-style matching via `board_manager.router._match`. The special pattern `"*"` matches all topics. When no handler is provided for a subscription, the topic is still tracked for re-subscription on reconnect but no local dispatch occurs.

**Event handler signature:** `Callback[[dict], None]` — receives the full parsed message dict (with keys `type`, `topic`, `body`, `reply_to`, etc.).

Handler errors are caught individually and logged; a failing handler never crashes the reader thread.

---

## Handshake Flow

The handshake is only performed for **TCP connections** (i.e. when UDS is disabled or the UDS socket does not exist):

```python
def _send_handshake(self) -> None:
    if not self.use_uds or not os.path.exists(self.uds_path):
        self._sock.sendall(Handshake.NEWLINE.value)
```

`Handshake.NEWLINE` (from `board_manager.protocol`) is sent as the first bytes on the TCP socket to identify the connection as a PubSub client. UDS connections skip the handshake — the transport itself implies the identity.

### Handshake sequence

```
Client                         Server
  │                               │
  │  ── Handshake.NEWLINE ──►     │   (TCP only)
  │  ── subscribe frame    ──►    │
  │  ◄── framed messages ────     │
```

---

## Auto-Resubscribe on Reconnect

All topics added via `subscribe()` are tracked in `_subscriptions` (a `set[str]`). When a connection is (re)established, `_resubscribe()` iterates over every tracked topic and re-sends the subscribe frame:

```python
def _resubscribe(self) -> None:
    with self._lock:
        topics = list(self._subscriptions)
    for topic in topics:
        self._send({"type": "subscribe", "topic": topic})
```

This ensures that after a temporary disconnect the client automatically recovers all subscriptions without application-level intervention. Topics remain in the set until explicitly `unsubscribe()` is called.

---

## Background Reader Thread

### `start_reader`

```python
def start_reader(self) -> None
```

Starts a daemon `threading.Thread` that runs `_read_loop`. Idempotent-safe — does not check if a thread is already running (caller should manage this).

### Reader loop (`_read_loop`)

```
while _running:
    if no socket → _reconnect(), sleep 0.1s, continue
    select([sock], [], [], 1.0)
    if timeout → loop again
    if OSError/ConnectionError → _reconnect(), continue
    if empty data (closed) → _reconnect(), continue
    reader.feed(data)
    while msg = reader.read_one():
        _dispatch(msg)
```

Key behaviours:
- Uses `select()` with a 1-second timeout so `_running` is checked at least once per second.
- On socket errors or closed connections, calls `_reconnect()` which closes the old socket, sleeps `ReconnectConfig.RECONNECT_DELAY` seconds, and calls `connect()` (single attempt). If the reconnect itself fails, the loop continues and retries on the next iteration.
- Incoming framed JSON messages are dispatched to all matching topic handlers via `_dispatch`.
- Malformed messages are caught by a blanket `except Exception` — the loop logs the error and continues.

### Full lifecycle example

```python
import time
from board_manager_client import PubSubClient

client = PubSubClient(
    uds_path="/tmp/board_mgr.sock",
    use_uds=True,
)

def on_connect():
    print("Connected / reconnected")

client.on_reconnect = on_connect  # not supported — must be passed in constructor

# Correct way — pass on_reconnect in constructor:
client = PubSubClient(
    uds_path="/tmp/board_mgr.sock",
    use_uds=True,
    on_reconnect=lambda: print("Connected / reconnected"),
)

client.connect(retry=True)       # initial connection with retries
client.start_reader()            # spawn reader daemon thread

# Register handlers
def handle_board_event(msg):
    print(f"Board event: {msg['body']}")

def handle_all(msg):
    print(f"Any message: {msg['topic']}")

client.subscribe("sys::board_event", handler=handle_board_event)
client.subscribe("*", handler=handle_all)

# Publish
client.publish("my::topic", {"temp": 22.5})

# Request boards
boards = client.request_boards(timeout=5.0)

# Cleanup
client.disconnect()
```

---

## Wire Protocol

All messages are JSON-encoded and framed with newline delimiters (via `board_manager.protocol.encode_and_frame` and `FrameReader`).

### Outgoing frames

| Type | Payload |
|------|---------|
| subscribe | `{"type": "subscribe", "topic": "<pattern>"}` |
| unsubscribe | `{"type": "unsubscribe", "topic": "<pattern>"}` |
| publish | `{"type": "publish", "topic": "<topic>", "body": {...}, "reply_to": "<topic>"}` |

### Incoming frames

The reader thread expects the same newline-delimited JSON format. Each frame is dispatched to matching topic handlers based on the `"topic"` field.

---

## Thread Safety

- `_subscriptions` and `_handlers` are guarded by `self._lock` (`threading.Lock`).
- `_pending_responses` is guarded by `self._resp_lock`.
- The reader thread runs `_read_loop` — all handler callbacks are invoked from this thread.
- `subscribe` / `unsubscribe` / `publish` are designed to be called from any thread.
- `disconnect` sets `_running = False` and closes the socket, which causes `select()` in the reader to wake up and exit.
