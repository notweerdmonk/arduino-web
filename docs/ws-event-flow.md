---
---
{% raw %}
# WebSocket Message Flow for Board Events

## File Index

| # | File | Absolute Path |
|---|------|---------------|
| 1 | `board_event.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/partials/board_event.html` |
| 2 | `board_event.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/partials/board_event.html` |
| 3 | `pubsub_infra.py` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/pubsub_infra.py` |
| 4 | `pubsub.py` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/pubsub.py` |
| 5 | `base.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/base.html` |
| 6 | `base.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/base.html` |
| 7 | `pubsub_client.py` | `/home/weerdmonk/Projects/medminder/board_manager_client/python/board_manager_client/board_manager_client/pubsub_client.py` |
| 8 | `board_management.py` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/board_management.py` |
| 9 | `board_management.py` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/board_management.py` |
| 10 | `state.py` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/state.py` |
| 11 | `state.py` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/state.py` |
| 12 | `index.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/index.html` |
| 13 | `admin.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/admin.html` |
| 14 | `admin.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/admin.html` |
| 15 | `dashboard.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/dashboard.html` |
| 16 | `admin_board_selector.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/partials/admin_board_selector.html` |
| 17 | `admin_board_selector.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/partials/admin_board_selector.html` |
| 18 | `app.py` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/app.py` |
| 19 | `app.py` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/app.py` |
| 20 | `extension.py` (sketch_tools) | `/home/weerdmonk/Projects/medminder/arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/extension.py` |
| 21 | `utils.py` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/utils.py` |

---

## 1. `board_event.html` Templates

### medminder_dash (17 lines)
```html
{% if events %}
    {% for evt in events[-10:]|reverse %}
    <div class="board-event" ...>
        <div>
            <span style="font-weight: 500;">{{ evt.get('port', '') }}</span>
            <span class="hint" style="margin-left: 0.5rem;">{{ evt.get('event', '') }}</span>
        </div>
        {% if evt.get('board') %}
        <span class="badge badge-ok">{{ evt.get('board') }}</span>
        {% endif %}
    </div>
    {% endfor %}
{% else %}
    <div class="card" style="text-align: center; padding: 1rem; color: #64748b;">
        No board events yet.
    </div>
{% endif %}
```

### arduino_dash (13 lines)
```html
{% if events %}
{% for evt in events %}
<div class="board-event" ...>
    <span class="badge badge-ok">{{ evt.get("event", "unknown") }}</span>
    <span>{{ evt.get("port", "") }}</span>
    <span class="hint">{{ evt.get("board", "") }}</span>
</div>
{% endfor %}
{% else %}
<div class="card" ...>No board events yet.</div>
{% endif %}
```

**Key:** Both render `<div class="board-event">`. The client-side JS checks for `"board-event"` string to trigger `board-changed` (see section 3).

---

## 2. PubSub Infrastructure

### medminder_dash `pubsub_infra.py` (321 lines)

#### `init_pubsub` (lines 116-145)
```python
def init_pubsub(app, use_uds=True, tcp_host="127.0.0.1", tcp_port=9090, uds_path="/tmp/board_mgr.sock"):
    global _pubsub, _app
    state._app = app
    ps = PubSubClient(uds_path=uds_path, use_uds=use_uds, tcp_host=tcp_host, tcp_port=tcp_port)
    ps.on_reconnect = _on_pubsub_reconnect
    with _pubsub_lock:
        _pubsub = ps
    try:
        ps.connect(retry=True)
    except (ConnectionError, OSError) as e:
        _logger.warning("Could not connect to BoardManagerService: %s", e)
    ps.subscribe("board::+::event", _on_board_event)
    ps.subscribe("resp::*", _on_resp)
    ps.subscribe("sys::daemon/ready", _on_daemon_ready)
    ps.subscribe("sys::health", lambda msg: None)
    tools = app.extensions.get("arduino_sketch_tools")
    if tools:
        tools.pubsub = ps
        ps.subscribe("resp::compile::*", tools._on_compile_resp)
        ps.subscribe("resp::upload::*", tools._on_upload_resp)
    ps.start_reader()
    return ps
```

#### `_on_board_event` (lines 177-206) — The Core Handler
```python
def _on_board_event(msg: dict) -> None:
    data = msg.get("data", {})
    event = data.get("event", "")
    port = data.get("port", "")
    if event == "connected":
        with state._known_ports_lock:
            if port in state._known_ports:
                return
            state._known_ports[port] = data
            _logger.debug("Board connected: %s (total: %d)", port, len(state._known_ports))
    elif event == "disconnected":
        with state._known_ports_lock:
            if port not in state._known_ports:
                return
            state._known_ports.pop(port, None)
            _logger.debug("Board disconnected: %s (total: %d)", port, len(state._known_ports))
        _clear_sketch_tools_state(port)
    if event:
        with state._board_events_lock:
            state._board_events.append(data)
            state._board_events[:] = state._board_events[-100:]
    if state._app and event:
        try:
            from flask import render_template
            with state._app.app_context():
                event_html = '<div hx-swap-oob="afterbegin:#live-events-card">' \
                             + render_template("partials/board_event.html", events=[data]) \
                             + '</div>'
            broadcast_ws(event_html)
        except Exception:
            _logger.debug("Failed to broadcast board event via WS", exc_info=True)
```

#### `broadcast_ws` (lines 301-310)
```python
def broadcast_ws(html: str) -> None:
    with state._ws_lock:
        for ws in list(state._ws_clients):
            try:
                ws.send(html)
            except Exception:
                try:
                    state._ws_clients.remove(ws)
                except ValueError:
                    pass
```

#### `add_ws_client` / `remove_ws_client` (lines 290-298)
```python
def add_ws_client(ws) -> None:
    with state._ws_lock:
        state._ws_clients.append(ws)

def remove_ws_client(ws) -> None:
    with state._ws_lock:
        if ws in state._ws_clients:
            state._ws_clients.remove(ws)
```

#### `_on_pubsub_reconnect` (lines 245-262)
```python
def _on_pubsub_reconnect() -> None:
    with state._daemon_ready_lock:
        state._daemon_ready = False
    ps = get_pubsub()
    if not ps:
        _logger.info("PubSub reconnected -- no pubsub instance yet")
        return
    ps.subscribe("board::+::event", _on_board_event)
    ps.subscribe("resp::*", _on_resp)
    ps.subscribe("sys::daemon/ready", _on_daemon_ready)
    ps.subscribe("sys::health", lambda msg: None)
    if state._app is not None:
        tools = state._app.extensions.get("arduino_sketch_tools")
        if tools:
            tools.pubsub = ps
            ps.subscribe("resp::compile::*", tools._on_compile_resp)
            ps.subscribe("resp::upload::*", tools._on_upload_resp)
    _logger.info("PubSub reconnected -- all handlers re-registered")
```

#### Fallback Scanner (lines 19-77)
```python
def _start_fallback_scanner(ps: PubSubClient) -> None:
    state._stop_fallback_scan = False
    state._fallback_scanner = threading.Thread(target=_fallback_scan_loop, args=(ps,), daemon=True)
    state._fallback_scanner.start()

def _fallback_scan_loop(ps: PubSubClient) -> None:
    while not state._stop_fallback_scan:
        if state._daemon_ready:
            time.sleep(state._fallback_scan_interval)
            continue
        try:
            found = set()
            for pattern in state._fallback_patterns:
                for path in glob.glob(pattern):
                    found.add(path)
            with state._known_ports_lock:
                before = set(state._known_ports.keys())
            added = found - before
            removed = {p for p in before if p.startswith("/dev/tty")} - found
            for port in removed:
                _logger.info("Fallback: board disconnected at %s", port)
                _on_board_event({"data": {"port": port, "event": "disconnected", ...}})
            for port in sorted(added):
                _logger.info("Fallback: board connected at %s", port)
                info = _resolve_board_info(port)
                _on_board_event({"data": {"port": port, "event": "connected", ...}})
        except Exception:
            _logger.exception("Fallback scanner error")
        time.sleep(state._fallback_scan_interval)
```

**Critical:** The fallback scanner calls the exact same `_on_board_event` function that the PubSub handler uses. Every event detected by the fallback scanner goes through `broadcast_ws` and sends HTML to all WS clients.

---

### arduino_dash `pubsub.py` (272 lines)

#### `init_pubsub` (lines 85-103)
```python
def init_pubsub(use_uds=True, tcp_host="127.0.0.1", tcp_port=9090, uds_path="/tmp/board_mgr.sock"):
    state.pubsub = PubSubClient(tcp_host=tcp_host, tcp_port=tcp_port, uds_path=uds_path, use_uds=use_uds)
    state.pubsub.on_reconnect = _on_pubsub_reconnect
    state.pubsub.connect(retry=True)
    state.pubsub.subscribe("board::+::event", _on_board_event)
    state.pubsub.subscribe("resp::*", _on_resp)
    state.pubsub.subscribe("sys::health", _on_health)
    state.pubsub.subscribe("sys::daemon/ready", _on_daemon_ready)
    tools = state._app.extensions.get("arduino_sketch_tools")
    if tools:
        tools.pubsub = state.pubsub
        state.pubsub.subscribe("resp::compile::*", tools._on_compile_resp)
        state.pubsub.subscribe("resp::upload::*", tools._on_upload_resp)
    state.pubsub.start_reader()
```

#### `_on_board_event` (lines 130-164)
```python
def _on_board_event(msg: dict) -> None:
    data = msg.get("data", {})
    event = data.get("event", "")
    port = data.get("port", "")
    state.logger.debug("_on_board_event: event=%s port=%s data=%s", event, port, data)
    with state._board_list_lock:
        if event == "connected":
            if port in state._board_list:
                return
            state._board_list[port] = data
        elif event == "disconnected":
            if port not in state._board_list:
                return
            state._board_list.pop(port, None)
            # ... cleanup compile state ...
    try:
        from flask import render_template
        with state._app.app_context():
            event_html = '<div hx-swap-oob="afterbegin:#live-events-card">' \
                         + render_template("partials/board_event.html", events=[data]) \
                         + '</div>'
        _broadcast_ws(event_html)
    except Exception:
        state.logger.exception("Failed to broadcast board event")
```

#### `_broadcast_ws` (lines 263-272)
```python
def _broadcast_ws(html: str) -> None:
    with state._ws_lock:
        for ws in list(state._ws_clients):
            try:
                ws.send(html)
            except Exception:
                try:
                    state._ws_clients.remove(ws)
                except ValueError:
                    pass
```

#### `_on_pubsub_reconnect` (lines 113-127)
```python
def _on_pubsub_reconnect() -> None:
    state._daemon_ready = False
    ps = state.pubsub
    if not ps:
        return
    ps.subscribe("board::+::event", _on_board_event)
    ps.subscribe("resp::*", _on_resp)
    ps.subscribe("sys::health", _on_health)
    ps.subscribe("sys::daemon/ready", _on_daemon_ready)
    tools = state._app.extensions.get("arduino_sketch_tools") if state._app else None
    if tools:
        tools.pubsub = ps
        ps.subscribe("resp::compile::*", tools._on_compile_resp)
        ps.subscribe("resp::upload::*", tools._on_upload_resp)
    state.logger.info("PubSub reconnected -- all handlers re-registered")
```

#### Fallback Scanner (lines 17-66)
Same pattern as medminder_dash, uses `state._board_list` instead of `state._known_ports`:
```python
def _fallback_scan_loop(ps: PubSubClient) -> None:
    while not state._stop_fallback_scan:
        if state._daemon_ready:
            time.sleep(state._fallback_scan_interval)
            continue
        try:
            found = set()
            for pattern in state._fallback_patterns:
                for path in glob.glob(pattern):
                    found.add(path)
            with state._board_list_lock:
                before = set(state._board_list.keys())
            added = found - before
            removed = {p for p in before if p.startswith("/dev/tty")} - found
            for port in removed:
                _on_board_event({"data": {"port": port, "event": "disconnected", ...}})
            for port in sorted(added):
                info = _resolve_board_info(port)
                _on_board_event({"data": {"port": port, "event": "connected", ...}})
        except Exception:
            state.logger.exception("Fallback scanner error")
        time.sleep(state._fallback_scan_interval)
```

---

## 3. Client-Side JS in `base.html` (Both Dashboards, Identical)

Both `base.html` files have the exact same WS handler JS just before `</body>`:

### medminder_dash `base.html` (lines 67-73)
```javascript
<script>
    htmx.on("htmx:wsBeforeMessage", function(evt) {
        if (evt.target.id !== "event-feed") return;
        if (evt.detail.message.includes("board-event")) {
            htmx.trigger('body', 'board-changed');
        }
    });
</script>
```

### arduino_dash `base.html` (lines 68-73)
```javascript
<script>
    htmx.on("htmx:wsBeforeMessage", function(evt) {
        if (evt.target.id !== "event-feed") return;
        if (evt.detail.message.includes("board-event")) {
            htmx.trigger('body', 'board-changed');
        }
    });
</script>
```

**How it works:** The JS listens on the `htmx:wsBeforeMessage` event (fires BEFORE HTMX processes the WS message). When the WS message contains `"board-event"` (always true because `board_event.html` renders `<div class="board-event">`), it triggers `board-changed` on `<body>`. All elements with `board-changed from:body` in their `hx-trigger` then fire their HTTP requests.

---

## 4. PubSubClient (`pubsub_client.py`) — Key Methods

**File:** `board_manager_client/python/board_manager_client/board_manager_client/pubsub_client.py` (271 lines)

### `__init__` (lines 37-59)
```python
def __init__(self, tcp_host="127.0.0.1", tcp_port=9090, uds_path="/tmp/board_mgr.sock", use_uds=True, on_reconnect=None):
    self._sock = None
    self._reader = FrameReader("newline")
    self._subscriptions: set[str] = set()
    self._handlers: dict[str, list[EventHandler]] = {}
    self._running = False
    self._reconnect_count = 0
    self._lock = threading.Lock()
    self.on_reconnect = on_reconnect
```

### `connect` (lines 61-76)
```python
def connect(self, retry=False) -> None:
    if retry:
        for attempt, delay in enumerate(_CONNECT_RETRY_DELAYS):
            try:
                self._connect_once()
                return
            except (ConnectionError, OSError) as e:
                time.sleep(delay)
        raise last_error
    self._connect_once()
```

### `_connect_once` (lines 78-84)
```python
def _connect_once(self) -> None:
    self._sock = self._create_socket()
    self._send_handshake()
    self._resubscribe()
    self._reconnect_count = 0
    if self.on_reconnect:
        self.on_reconnect()
```

### `subscribe` (lines 129-138)
```python
def subscribe(self, topic: str, handler=None) -> None:
    with self._lock:
        is_new = topic not in self._subscriptions
        self._subscriptions.add(topic)
        if handler:
            hlist = self._handlers.setdefault(topic, [])
            if handler not in hlist:
                hlist.append(handler)
    if self._sock and is_new:
        self._send({"type": "subscribe", "topic": topic})
```

### `_resubscribe` (lines 195-199)
```python
def _resubscribe(self) -> None:
    with self._lock:
        topics = list(self._subscriptions)
    for topic in topics:
        self._send({"type": "subscribe", "topic": topic})
```

### `start_reader` (lines 201-204)
```python
def start_reader(self) -> None:
    self._running = True
    self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
    self._reader_thread.start()
```

### `_read_loop` (lines 206-241)
```python
def _read_loop(self) -> None:
    while self._running:
        if not self._sock:
            self._reconnect()
            time.sleep(0.1)
            continue
        try:
            data = sock.recv(65536)
        except (OSError, ConnectionError, ...):
            if self._running:
                self._reconnect()
            continue
        if not data:
            if self._running:
                self._reconnect()
            continue
        self._reader.feed(data)
        while True:
            msg = self._reader.read_one()
            if msg is None:
                break
            self._dispatch(msg)
```

### `_dispatch` (lines 243-257)
```python
def _dispatch(self, msg: dict) -> None:
    topic = msg.get("topic", "")
    with self._lock:
        matched = []
        for pattern, hlist in self._handlers.items():
            if pattern == "*" or _match(topic, pattern):
                matched.extend(hlist)
    for h in matched:
        try:
            h(msg)
        except Exception as e:
            logger.error("Handler error: %s", e)
```

### `_reconnect` / `on_reconnect` (lines 259-271)
```python
def _reconnect(self) -> None:
    self._reconnect_count += 1
    if self._sock:
        try:
            self._sock.close()
        except OSError:
            pass
        self._sock = None
    time.sleep(_RECONNECT_DELAY)
    try:
        self.connect()
    except (ConnectionError, OSError) as e:
        logger.warning("Reconnect failed (%s), retrying in %.1fs...", e, _RECONNECT_DELAY)
```

---

## 5. WebSocket Connection Initiation

Both dashboards initiate the WebSocket connection identically in `base.html`:

```html
<div id="event-feed" hx-ext="ws" ws-connect="/ws/board-events"></div>
```

This is the only WS connection in the app. It uses the HTMX WebSocket extension (`ws.js`) to open a persistent WS to `/ws/board-events`. The `<div>` is hidden (no content) — its sole purpose is to enable the WS extension. All WS messages arrive as HTMX OOB swaps.

### WS Endpoint Registration

**medminder_dash** `board_management.py` (lines 107-120):
```python
if sock is not None:
    @sock.route("/ws/board-events")
    def ws_board_events(ws):
        add_ws_client(ws)
        try:
            while True:
                ws.receive(timeout=30)
        except:
            pass
        finally:
            remove_ws_client(ws)
```

**arduino_dash** `board_management.py` (lines 232-244):
```python
if sock:
    @sock.route("/ws/board-events")
    def ws_board_events(ws):
        with state._ws_lock:
            state._ws_clients.append(ws)
        try:
            while True:
                data = ws.receive(timeout=30)
                if data is None:
                    break
        finally:
            with state._ws_lock:
                if ws in state._ws_clients:
                    state._ws_clients.remove(ws)
```

Note the slight difference: medminder_dash uses helper functions `add_ws_client`/`remove_ws_client` while arduino_dash manipulates `state._ws_clients` directly. Functionally identical. The WS connection is purely server-to-client — the server sends HTML (via `broadcast_ws`/`_broadcast_ws`) and the client never sends meaningful data (it just `ws.receive()` in a loop to detect disconnection).

The `Sock` object (Flask-Sock) is created in `app.py`:
```python
try:
    from flask_sock import Sock
    sock = Sock(app)
except ImportError:
    sock = None
```

---

## 6. Fallback Scanner (Both Dashboards)

Both dashboards have the identical fallback scanner pattern. The scanner is started by the WSGI entry point (not in `create_app()`).

### State Variables (both `state.py` files)
```python
_fallback_scanner: Optional[threading.Thread] = None
_stop_fallback_scan: bool = False
_fallback_patterns = ["/dev/ttyACM*", "/dev/ttyUSB*"]
_fallback_scan_interval = 5.0
```

### Behavior
- Polls `/dev/ttyACM*` and `/dev/ttyUSB*` globs every 5 seconds
- Compares current glob results against `_known_ports`/`_board_list` keys
- Calls `_on_board_event()` for any `connected` or `disconnected` detected ports
- `_on_board_event()` then calls `broadcast_ws()` which sends the event HTML to all WS clients

### Critical Race Condition
The fallback scanner and the PubSub handler both call `_on_board_event()`, which:
1. Updates `_known_ports`/`_board_list` under lock
2. Appends to `_board_events` list
3. Renders the `board_event.html` template
4. Calls `broadcast_ws()` to send HTML to ALL WS clients

If a board event arrives via PubSub AND the fallback scanner detects it before the PubSub handler has updated the port state, the event is processed TWICE.

The race window in `_fallback_scan_loop`:
```python
with state._known_ports_lock:
    before = set(state._known_ports.keys())     # (A) snapshot
# LOCK RELEASED — pubsub handler could update _known_ports HERE
added = found - before                           # (B) computed after lock release
removed = {p for p in before if p.startswith("/dev/tty")} - found  # (C)
```

Between (A) and (B), a PubSub `connected` event could add the port to `_known_ports`. The snapshot `before` would be stale (missing the port), so `added` would include it, triggering a duplicate `_on_board_event()` call.

---

## 7. `board-changed` `hx-trigger` Usage

The `board-changed` event is the lynchpin connecting WS messages to UI updates.

### medminder_dash

| Template | Element | Line | Trigger | Action |
|----------|---------|------|---------|--------|
| `index.html` | `#board-grid` | 8 | `load, board-changed from:body` | `GET /api/boards/grid` |
| `admin.html` | `#admin-board-selector-container` | 27 | `load, board-changed from:body` | `GET /api/medicines/board-selector` |
| `admin.html` | `#compile-upload-card` | 124 | `load, board-changed from:body` | `GET /api/board/compile-upload-card` |

**Sources of `board-changed` events:**

| Template | Element | Line | Mechanism |
|----------|---------|------|-----------|
| `base.html` | `<script>` | 71 | `htmx:wsBeforeMessage` handler checks for `"board-event"` in WS message, triggers `htmx.trigger('body', 'board-changed')` |
| `admin_board_selector.html` | `<select>` | 12 | `hx-on::after-request="htmx.trigger('body', 'board-changed')"` — fires after user changes board |

### arduino_dash

| Template | Element | Line | Trigger | Action |
|----------|---------|------|---------|--------|
| `dashboard.html` | `#board-grid` | 9 | `load, board-changed from:body` | `GET /api/boards/grid` |
| `admin.html` | `#admin-board-selector-container` | 27 | `load, board-changed from:body` | `GET /api/admin/board-selector` |
| `admin.html` | `#sketch-path-container` | 40 | `load, board-changed from:body` | `GET /api/last-upload` |
| `admin.html` | `#compile-upload-card` | 81 | `load, board-changed from:body` | `GET /api/board/compile-upload-card` |

**Sources of `board-changed` events:** Identical to medminder_dash (see above).

**Key difference:** arduino_dash `admin.html` has `board-changed` on `#sketch-path-container` (line 40), while medminder_dash `admin.html` has only `hx-trigger="load"` on `#sketch-path-container` (line 40-41). This means in arduino_dash, when the board is changed, the sketch path selector also refreshes.

---

## Complete Event Flow Diagram

```
Board Manager Service
        │
        │ PubSub message: board::/dev/ttyACM0::event
        │ {"data": {"port": "/dev/ttyACM0", "event": "connected", ...}}
        ▼
┌────────────────────────────────┐
│   PubSubClient._read_loop()    │  (separate daemon thread)
│   → _dispatch(msg)             │
│   → matches "board::+::event"  │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐     ┌──────────────────────────────┐
│  _on_board_event(msg)          │     │  Fallback Scanner Thread     │
│                                │     │  (every 5s, daemon thread)   │
│  1. Updates _known_ports       │     │                              │
│     (under lock)               │     │  glob("/dev/ttyACM*")        │
│  2. Appends to _board_events   │     │  → finds /dev/ttyACM0        │
│  3. Renders board_event.html   │     │  → computes added/removed    │
│  4. Calls broadcast_ws(html)   │     │  → _on_board_event(msg) ──────┤
└────────┬───────────────────────┘     └──────────────────────────────┘
         │                                   (^^^ POSSIBLE DUPLICATE!)
         │  WS send(html)
         ▼
┌────────────────────────────────┐
│  HTMX WS Extension             │
│  Receives: <div hx-swap-oob=   │
│    "afterbegin:#live-events-   │
│     card"><div class="board-   │
│     event">...</div></div>     │
│                                │
│  1. OOB swap: prepends to      │
│     #live-events-card          │
│  2. Fires htmx:wsBeforeMessage │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  Client JS handler             │
│  Checks: "board-event" in msg  │
│  → htmx.trigger('body',        │
│    'board-changed')            │
└────────┬───────────────────────┘
         │
         │  Multiple elements respond:
         ├──────────────────────────────────────────────┐
         │                                              │
         ▼                                              ▼
┌──────────────────────┐              ┌──────────────────────────┐
│ #board-grid          │              │ #admin-board-selector-   │
│ GET /api/boards/grid │              │ container                │
│                      │              │ GET /api/.../board-      │
│ Re-renders board     │              │ selector                 │
│ cards with new data  │              │                          │
└──────────────────────┘              │ Re-renders select with   │
                                      │ updated port list        │
                                      └──────────────────────────┘
                                      ┌──────────────────────────┐
                                      │ #compile-upload-card     │
                                      │ GET /api/board/compile-  │
                                      │ upload-card              │
                                      │                          │
                                      │ Re-renders compile/      │
                                      │ upload buttons with      │
                                      │ fresh URLs               │
                                      └──────────────────────────┘
```

---

## Summary: Potential Sources of Double Events

1. **Fallback Scanner vs PubSub race (MOST LIKELY):**
   - When a board connects/disconnects, the PubSub message arrives (real-time) AND the fallback scanner detects it (within 5 seconds)
   - Both call `_on_board_event()` which calls `broadcast_ws()`
   - There's a TOCTOU race window between the fallback scanner's snapshot of `_known_ports` and the actual state update
   - Result: TWO WS messages sent to client, TWO `board-changed` triggers

2. **Reconnect storm:**
   - `_on_pubsub_reconnect()` re-subscribes `board::+::event` handler
   - `_resubscribe()` sends subscribe to server (could trigger replay of existing board state)
   - Server might replay all active board connections on subscribe

3. **Multiple WS clients:**
   - If there are multiple `#event-feed` elements on the page (possible with HTMX swapping), each would open a WS connection, and `broadcast_ws` would send to all of them
   - But the JS handler filters by `evt.target.id !== "event-feed"`, so multiple WS connections shouldn't cause double triggers

4. **Simultaneous dashboards:**
   - If both medminder_dash and arduino_dash are running (each with `init_pubsub`), they each subscribe to the same PubSub topic and each have their own fallback scanner
   - If a user has both open, they'd get duplicate events from both dashboards

{% endraw %}