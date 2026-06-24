---
---
{% raw %}
# WebSocket Message Flow

This document describes all WebSocket push mechanisms in MedMinder, organized into three tiers:

| Tier | Category | Mechanism | Introduced |
|------|----------|-----------|------------|
| 0 | Board connect/disconnect events | OOB HTML via WS after PubSub event | Phase 74 |
| 1 | Badge updates (daemon + board status) | OOB HTML via WS after PubSub event | Phase 98 |
| 2 | Compile/Upload output streaming | OOB HTML via WS from PubSub progress messages | Phase 98 |
| 3 | Compile progress bar + `[N%]` prefix | OOB `<progress>` + `[N%]` prefix broadcast with progress-only messages | Phase 98 |

All tiers use a single persistent WebSocket connection (`/ws/board-events`) established by HTMX's `ws.js` extension. The server sends raw HTML with `hx-swap-oob` attributes; HTMX swaps the content into the DOM automatically.

## File Index

| # | File | Absolute Path |
|---|------|---------------|
| 1 | `board_event.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/partials/board_event.html` |
| 2 | `board_event.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/partials/board_event.html` |
| 3 | `pubsub.py` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/pubsub.py` |
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
| 22 | `daemon_badge.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/partials/daemon_badge.html` |
| 23 | `daemon_badge.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/partials/daemon_badge.html` |
| 24 | `board_status_badge.html` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/templates/partials/board_status_badge.html` |
| 25 | `board_status_badge.html` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/templates/partials/board_status_badge.html` |
| 26 | `client.py` (arduino_grpc) | `/home/weerdmonk/Projects/medminder/grpc_client/python/arduino_grpc/arduino_grpc/client.py` |
| 27 | `board_worker.py` (board_manager) | `/home/weerdmonk/Projects/medminder/board_manager/python/board_manager/board_manager/board_worker.py` |
| 28 | `html_routes.py` (medminder_dash) | `/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/medminder_dash/html_routes.py` |
| 29 | `html_routes.py` (arduino_dash) | `/home/weerdmonk/Projects/medminder/arduino_dash/python/arduino_dash/arduino_dash/html_routes.py` |

---

## 1. Tier 0 — Board Events: `board_event.html` Templates

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

## 2. Tier 0 — PubSub Infrastructure

### medminder_dash `pubsub.py` (436 lines)

#### `init_pubsub` (lines 154-196)
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

#### `_on_board_event` (lines 237-280) — The Core Handler
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
                event_html = '<div hx-swap-oob="afterbegin:#live-events-card" data-event-port="' + port + '">' + render_template("partials/board_event.html", events=[data]) + '</div>'
            broadcast_ws(event_html)
            # Badge OOB also broadcast here (see Tier 1 section 8)
        except Exception:
            _logger.debug("Failed to broadcast board event via WS", exc_info=True)
```

#### `broadcast_ws` (lines 418-432)
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

#### `add_ws_client` / `remove_ws_client` (lines 397-415)
```python
def add_ws_client(ws) -> None:
    with state._ws_lock:
        state._ws_clients.append(ws)

def remove_ws_client(ws) -> None:
    with state._ws_lock:
        if ws in state._ws_clients:
            state._ws_clients.remove(ws)
```

#### `_on_pubsub_reconnect` (lines 355-374)
```python
def _on_pubsub_reconnect() -> None:
    with state._daemon_ready_lock:
        state._daemon_ready = False
    _broadcast_daemon_badge()           # push "disconnected" badge OOB
    ps = get_pubsub()
    if not ps:
        _logger.info("PubSub reconnected — no pubsub instance yet")
        return
    ps.subscribe(PubSubTopic.DAEMON_READY, _on_daemon_ready)
    ps.subscribe(PubSubTopic.BOARD_EVENT, _on_board_event)
    ps.subscribe(PubSubTopic.RESP, _on_resp)
    ps.subscribe(PubSubTopic.HEALTH, lambda msg: None)
    if state._app is not None:
        tools = state._app.extensions.get("arduino_sketch_tools")
        if tools:
            tools.pubsub = ps
            ps.subscribe(PubSubTopic.RESP_COMPILE, tools._on_compile_resp)
            ps.subscribe(PubSubTopic.RESP_UPLOAD, tools._on_upload_resp)
    _logger.info("PubSub reconnected — all handlers re-registered")
```

#### Fallback Scanner (lines 31-104)
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

### arduino_dash `pubsub.py` (330 lines)

#### `init_pubsub` (lines 103-126)
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

#### `_on_board_event` (lines 160-204) — The Core Handler
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
            event_html = '<div hx-swap-oob="afterbegin:#live-events-card" data-event-port="' + port + '">' + render_template("partials/board_event.html", events=[data]) + '</div>'
        _broadcast_ws(event_html)
        # Badge OOB also broadcast here (see Tier 1 section 8)
    except Exception:
        state.logger.exception("Failed to broadcast board event")
```

#### `_broadcast_ws` (lines 320-329)
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

#### `_on_pubsub_reconnect` (lines 140-158)
```python
def _on_pubsub_reconnect() -> None:
    state._daemon_ready = False
    _broadcast_daemon_badge()           # push "disconnected" badge OOB
    ps = state.pubsub
    if not ps:
        return
    ps.subscribe(PubSubTopic.DAEMON_READY, _on_daemon_ready)
    ps.subscribe(PubSubTopic.BOARD_EVENT, _on_board_event)
    ps.subscribe(PubSubTopic.RESP, _on_resp)
    ps.subscribe(PubSubTopic.HEALTH, _on_health)
    tools = state._app.extensions.get("arduino_sketch_tools") if state._app else None
    if tools:
        tools.pubsub = ps
        ps.subscribe(PubSubTopic.RESP_COMPILE, tools._on_compile_resp)
        ps.subscribe(PubSubTopic.RESP_UPLOAD, tools._on_upload_resp)
    state.logger.info("PubSub reconnected — all handlers re-registered")
```

#### Fallback Scanner (lines 27-85)
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

## 3. Tier 0 — Client-Side JS in `base.html` (Both Dashboards, Identical)

Both `base.html` files have the same WS handler JS just before `</body>`:

### medminder_dash `base.html` (lines 90-102)
### arduino_dash `base.html` (lines 92-103)
```javascript
htmx.on("htmx:wsBeforeMessage", function(evt) {
    if (evt.target.id !== "event-feed") return;
    var msg = evt.detail.message;
    var portMatch = msg.match(/data-event-port="([^"]+)"/);
    if (portMatch) {
        var port = portMatch[1];
        var encoded = encodeURIComponent(port);
        htmx.ajax('GET', '/boards/grid/card/' + encoded, {target: '[data-port="' + port + '"]', swap: 'outerHTML'});
        htmx.trigger('body', 'board-changed');
    } else if (msg.includes("board-event")) {
        htmx.trigger('body', 'board-changed');
    }
});
```

**How it works:** The JS listens on the `htmx:wsBeforeMessage` event (fires BEFORE HTMX processes the WS message). When the WS message has a `data-event-port` attribute, it refreshes the specific board card via AJAX and triggers `board-changed` on `<body>`. If the message contains `"board-event"` without a specific port, it still triggers `board-changed` as a fallback. All elements with `board-changed from:body` in their `hx-trigger` then fire their HTTP requests.

---

## 4. Tier 0 — PubSubClient (`pubsub_client.py`) — Key Methods

**File:** `board_manager_client/python/board_manager_client/board_manager_client/pubsub_client.py` (349 lines)

### `__init__` (lines 39-70)
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

### `connect` (lines 72-96)
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

### `_connect_once` (lines 98-105)
```python
def _connect_once(self) -> None:
    self._sock = self._create_socket()
    self._send_handshake()
    self._resubscribe()
    self._reconnect_count = 0
    if self.on_reconnect:
        self.on_reconnect()
```

### `subscribe` (lines 161-176)
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

### `_resubscribe` (lines 264-269)
```python
def _resubscribe(self) -> None:
    with self._lock:
        topics = list(self._subscriptions)
    for topic in topics:
        self._send({"type": "subscribe", "topic": topic})
```

### `start_reader` (lines 271-275)
```python
def start_reader(self) -> None:
    self._running = True
    self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
    self._reader_thread.start()
```

### `_read_loop` (lines 277-313)
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

### `_dispatch` (lines 315-334)
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

### `_reconnect` (lines 336-349)
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

## 5. Tier 0 — WebSocket Connection Initiation

Both dashboards initiate the WebSocket connection identically in `base.html`:

```html
<div id="event-feed" hx-ext="ws" ws-connect="/ws/board-events"></div>
```

This is the only WS connection in the app. It uses the HTMX WebSocket extension (`ws.js`) to open a persistent WS to `/ws/board-events`. The `<div>` is hidden (no content) — its sole purpose is to enable the WS extension. All WS messages arrive as HTMX OOB swaps.

### WS Endpoint Registration

**medminder_dash** `html_routes.py` (lines 771-783):
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

**arduino_dash** `html_routes.py` (lines 396-408):
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

## 6. Tier 0 — Fallback Scanner (Both Dashboards)

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

## 7. Tier 0 — `board-changed` `hx-trigger` Usage

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

## 8. Tier 1 — Badge OOB Updates

### Overview

The daemon badge and board status badges are rendered on page load via `hx-trigger="load"` (one-shot, no polling). Subsequent updates are pushed exclusively over WebSocket as OOB HTML. This eliminates the `hx-trigger="every 10s"` polling that was present in prior versions.

### daemon_badge.html (Both Dashboards, 3 Lines)

```html
<span class="daemon-badge {{ 'daemon-on' if ready else 'daemon-off' }}">
      <span class="badge-circle">{{ '⬤' if ready else '⬤' }}</span> Daemon {{ 'Ready' if ready else 'Disconnected' }}
</span>
```

`base.html` (both dashboards, line 17):
```html
<span id="daemon-badge" class="badge-container" hx-get="/daemon/status" hx-trigger="load" hx-target="this" hx-swap="morph"></span>
```

The initial `hx-trigger="load"` fetches the template via `GET /daemon/status` (rendered by `html_routes.py`), which fills `<span id="daemon-badge">`. After that, no polling occurs — all updates arrive via WS.

### board_status_badge.html (Both Dashboards, 3 Lines)

```html
<span class="badge {{ 'badge-ok' if connected else 'badge-err' }}">
      {{ 'Connected' if connected else 'Disconnected' }}
</span>
```

This tiny template is rendered inline within the board grid (inside each board card) — there is no separate `hx-trigger` endpoint for it. OOB updates replace the badge inside the per-port wrapper span.

### Daemon Badge OOB Broadcasting

**File:** `medminder_dash` `pubsub.py:283-294`, `arduino_dash` `pubsub.py:306-317`

The daemon badge is broadcast via WS when:

1. **Daemon connects** — `_on_daemon_ready()` sets `daemon_ready = True` and calls `_broadcast_daemon_badge()`
2. **Daemon reconnects** — `_on_pubsub_reconnect()` sets `daemon_ready = False` and calls `_broadcast_daemon_badge()`

```python
def _broadcast_daemon_badge() -> None:
    """Broadcast daemon badge OOB update via WebSocket."""
    try:
        from flask import render_template
        with state._daemon_ready_lock:
            ready = state._daemon_ready
        with state._app.app_context():
            badge = render_template("partials/daemon_badge.html", ready=ready)
        oob = f'<span id="daemon-badge" hx-swap-oob="true">{badge}</span>'
        broadcast_ws(oob)    # pubsub.py:292
        # _broadcast_ws(oob)  # pubsub.py:315
    except Exception:
        _logger.exception("Failed to broadcast daemon badge")
```

**Key:** The OOB wrapper `<span id="daemon-badge" hx-swap-oob="true">` matches the `id` of the placeholder in `base.html`. HTMX sees `hx-swap-oob="true"` and replaces `<span id="daemon-badge">` in the DOM.

### Board Status Badge OOB Broadcasting

**File:** `medminder_dash` `pubsub.py:274-278`, `arduino_dash` `pubsub.py:198-202`

The board status badge is broadcast as part of `_on_board_event()` — the same handler that pushes board connect/disconnect events (Section 2). After broadcasting the board event HTML, it renders and broadcasts the badge OOB:

```python
# Inside _on_board_event(), after broadcasting event_html:
port_safe = port.replace("/", "_")
connected = (event == "connected")
badge = render_template("partials/board_status_badge.html", port=port, port_path=port.lstrip("/"), connected=connected)
oob = f'<span id="board-status-badge--{port_safe}" hx-swap-oob="true">{badge}</span>'
broadcast_ws(oob)
```

**Per-port unique ID:** `board-status-badge--{port_safe}` where `port_safe = port.replace("/", "_")` (e.g., `/dev/ttyACM0` → `_dev_ttyACM0`). This ensures each board card's badge gets the correct update.

### Comparison: Old Polling vs New WS Push

| Aspect | Old Approach (pre-Phase 98) | New Approach (Phase 98+) |
|--------|----------------------------|--------------------------|
| Daemon badge refresh | `hx-trigger="every 10s"` on `#daemon-badge` | `hx-trigger="load"` initial fill, then WS OOB push |
| Board status badge refresh | `hx-trigger="every 10s"` on each `#board-status-badge--*` | WS OOB push from `_on_board_event()` |
| Latency | Up to 10 seconds | Sub-second (PubSub → WS) |
| Server load | Constant polling requests | Zero idle requests |

---

## 9. Tier 2 — Compile/Upload OOB Output Streaming

### Overview

Compile and upload progress messages arrive via PubSub on topics `resp::compile::<port>::progress` / `resp::compile::<port>` and `resp::upload::<port>::progress` / `resp::upload::<port>`. The `ArduinoSketchTools` extension (`extension.py`) handles these messages and broadcasts HTML over WebSocket with `hx-swap-oob` targeting.

### Port Safety Transform

All per-port IDs use `port_safe = port.replace("/", "_")` to avoid CSS selector issues with `/` characters. For example:
- Port `/dev/ttyACM0` → `_dev_ttyACM0`
- Compiled output container: `compile-output--dev_ttyACM0`
- Upload output container: `upload-output--dev_ttyACM0`
- Compile progress bar: `compile-progress--dev_ttyACM0`

### Compile Output OOB

**File:** `extension.py:183-195`

```python
port_safe = port.replace("/", "_")
if out or err:
    text = (out + err).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    pct_prefix = f"[{pct_int}%] " if percent >= 0 else ""
    html = f'<span hx-swap-oob="beforeend:#compile-output-{port_safe}"><div class="compile-line" data-port="{port}">{pct_prefix}{text}</div></span>'
    self._broadcast_ws(html)
```

**Mechanism:**
1. Each compile output line is wrapped in `<span hx-swap-oob="beforeend:#compile-output--dev_ttyACM0">`
2. `beforeend:` tells HTMX to append the content as the last child of `#compile-output--dev_ttyACM0`
3. The `<div class="compile-line">` preserves line breaks and carries `data-port` for client-side filtering

### Upload Output OOB

**File:** `extension.py:226-228`

```python
port_safe = port.replace("/", "_")
html = f'<span hx-swap-oob="beforeend:#upload-output-{port_safe}"><div class="upload-line" data-port="{port}">{text}</div></span>'
self._broadcast_ws(html)
```

Same pattern as compile, but targets `#upload-output--dev_ttyACM0` and uses `upload-line` class.

### Data Flow

```
Board Manager Daemon
    └── compile_stream() → (out, err, done, percent)         (arduino_grpc client.py:264-308)
         ↓
    board_worker.py:155-172
    └── _make_progress(msg, out, err, percent)               (board_worker.py:39-44)
         ↓  PubSub message: resp::compile::/dev/ttyACM0::progress
    PubSubClient._dispatch()
         ↓  matches "resp::compile::*"
    extension.py:_on_compile_resp() → _on_compile_progress()
         ↓
    HTML: <span hx-swap-oob="beforeend:#compile-output--dev_ttyACM0">...
         ↓  WS broadcast
    HTMX WS Extension → OOB swap into #compile-output--dev_ttyACM0
```

**Key differences between compile and upload:**
- `compile_stream()` yields 4-tuples `(out, err, done, percent)` — includes progress percentage
- `upload_stream()` yields 3-tuples `(out, err, done)` — no progress percentage
- Therefore, upload has no `[N%]` prefix and no `<progress>` bar

---

## 10. Tier 3 — Compile Progress Bar + `[N%]` Prefix

### Overview

Tier 3 extends Tier 2 with visible progress indication for compile operations. Two mechanisms work together:

1. **`<progress>` bar** — Broadcast as standalone OOB `<progress>` element, targeted by per-port ID
2. **`[N%]` prefix** — Prepended to each compile output line that has a progress percentage

### `compile_stream()` 4-Tuple

**File:** `client.py:264-308`

```python
def compile_stream(self, sketch_path, fqbn, verbose=False, quiet=False) -> Iterator[tuple[str, str, bool, float]]:
    # ...
    # Yields (out, err, done, percent) tuples
    percent = 0.0
    for resp in self.stub.Compile(request, timeout=120):
        out = resp.out_stream.decode() if resp.HasField("out_stream") else ""
        err = resp.err_stream.decode() if resp.HasField("err_stream") else ""
        # ...
        yield (out, err, done, percent)
```

The `percent` field comes from `TaskProgress` in the gRPC response and ranges from 0.0 to 100.0.

### `board_worker.py`: Progress-Only Messages

**File:** `board_worker.py:155-173`

```python
for out, err, done, percent in client.compile_stream(...):
    if out:
        sock.sendall(encode_and_frame(_make_progress(msg, out, "", percent)))
        last_pct = percent
    if err:
        sock.sendall(encode_and_frame(_make_progress(msg, "", err, percent)))
        last_pct = percent
    elif percent != last_pct:
        # Progress-only message (no output text)
        sock.sendall(encode_and_frame(_make_progress(msg, "", "", percent)))
        last_pct = percent
```

When `percent` changes but there's no new output text, a progress-only message (empty `out` and `err`) is sent. This causes the extension to broadcast the `<progress>` bar without appending an output line.

### `extension.py`: Progress Bar + Prefix

**File:** `extension.py:42-43`, `extension.py:183-195`

```python
# Class init (extension.py:42-43):
self._compile_last_pct: dict[str, float] = {}
self._compile_last_pct_lock = threading.Lock()
```

```python
# Inside _on_compile_progress():
port_safe = port.replace("/", "_")
with self._compile_last_pct_lock:
    last = self._compile_last_pct.get(port_safe, -1.0)
    if percent != last:
        pct_int = int(round(percent))
        self._compile_last_pct[port_safe] = percent
        bar = f'<progress id="compile-progress-{port_safe}" value="{pct_int}" max="100" hx-swap-oob="true"></progress>'
        self._broadcast_ws(bar)

if out or err:
    ... = f'...{pct_prefix}{text}...</span>'
```

**Progress bar behavior:**
- `<progress id="compile-progress--dev_ttyACM0" value="42" max="100" hx-swap-oob="true">`
- Broadcast even when `out` and `err` are both empty (progress-only messages from board_worker)
- `hx-swap-oob="true"` (no `beforeend:`) — replaces the entire `<progress>` element in the DOM
- The `<progress>` element is rendered initially in the compile-upload card template

**`[N%]` prefix behavior:**
- `pct_prefix = f"[{pct_int}%] " if percent >= 0 else ""`
- Preprended to the output text inside the `<div class="compile-line">`
- Only appears when there's actual output text (not on progress-only messages)
- Format: `[42%] Compiling core...`

### `_compile_last_pct` Deduplication

The `_compile_last_pct` dict tracks the last-broadcast percentage per port to avoid redundant broadcasts. When `percent` matches the last value for that port, no new OOB HTML is broadcast. This prevents browser re-renders when the board_worker sends repeated messages with the same percentage.

### Visual Output Example

```
┌──────────────────────────────────────────┐
│ #compile-upload-card for /dev/ttyACM0     │
│                                          │
│  ┌─ compile-output--dev_ttyACM0 ───────┐ │
│  │ [0%] Compiling sketch...            │ │
│  │ [35%] Compiling core libraries...   │ │
│  │ [72%] Linking...                    │ │
│  │ [100%] Compilation complete.        │ │
│  └────────────────────────────────────┘ │
│  ┌─ compile-progress--dev_ttyACM0 ────┐ │
│  │ ████████████████░░░░░░  72%        │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

---

## 11. Complete Event Flow Diagram (All Tiers)

```
                                                    BOARD EVENTS (Tier 0)
                                                    =====================

Board Manager Service ─── PubSub: board::/dev/ttyACM0::event ──► PubSubClient._read_loop()
         │                                                          → _dispatch(msg)
         │                                                          → matches "board::+::event"
         │                                                                    │
         │  ┌─────────────────────────────────────────────────────────────────┘
         │  │
         │  ▼
         │  ┌──────────────────────────────────┐     ┌───────────────────────────────┐
         │  │  _on_board_event(msg)            │     │  Fallback Scanner (5s daemon) │
         │  │                                  │     │                               │
         │  │  1. Updates _known_ports (lock)  │     │  glob("/dev/ttyACM*")         │
         │  │  2. Appends to _board_events     │     │  → computes added/removed     │
         │  │  3. Renders board_event.html     │     │  → _on_board_event(msg) ───────┤
         │  │  4. Renders board_status_badge   │     └───────────────────────────────┘
         │  │  5. Calls broadcast_ws(html      │           (^^^ Possible duplicate!)
         │  │     + badge OOB)                 │
         │  └──────────┬───────────────────────┘
         │             │  WS: <div hx-swap-oob="afterbegin:#live-events-card" data-event-port="...">...
         │             │  WS: <span id="board-status-badge--{port_safe}" hx-swap-oob="true">...
         │             ▼
         │  ┌──────────────────────────────────┐
         │  │  HTMX WS Extension               │
         │  │  1. OOB swap: prepend to          │
         │  │     #live-events-card             │
         │  │  2. OOB swap: replace badge in    │
         │  │     #board-status-badge--{ps}     │
         │  │  3. Fires htmx:wsBeforeMessage    │
         │  └──────────┬───────────────────────┘
         │             │
         │             ▼
         │  ┌─────────────────────────────────────┐
         │  │  Client JS: checks data-event-port │
         │  │  → refreshes specific board card   │
         │  │  → htmx.trigger('body',            │
         │  │    'board-changed')                │
         │  └──────────┬─────────────────────────┘
         │             │
         │  ┌──────────┴───────────────────┬───────────────────┐
         │  ▼                              ▼                   ▼
         │  #board-grid              #admin-board-selector  #compile-upload-card
         │  GET /api/boards/grid     GET /api/.../selector  GET /api/.../compile-card
         │  (re-render board cards)  (re-render select)     (re-render buttons)
         │
         │
         │                        BADGE OOB (Tier 1)
         │                        =================
         │
         │  _on_daemon_ready()           _on_pubsub_reconnect()
         │      │                             │
         │      │ set daemon_ready=True        │ set daemon_ready=False
         │      └─────┬────────────────────────┘
         │            │
         │            ▼
         │  _broadcast_daemon_badge()
         │      │
         │      │ render_template("partials/daemon_badge.html")
         │      │ → <span id="daemon-badge" hx-swap-oob="true">...
         │      ▼
         │  WS broadcast → HTMX replaces #daemon-badge in DOM
         │
         │
         │                  COMPILE/UPLOAD OOB (Tier 2 + Tier 3)
         │                  =====================================
         │
         │  Board Manager Daemon
         │    └── compile_stream() → (out, err, done, percent)
         │    └── upload_stream() → (out, err, done)
         │         │
         │         ▼
         │    board_worker.py
         │    └── _make_progress(msg, out, err, percent)
         │    └── PubSub: resp::compile::/dev/ttyACM0::progress
         │    └── PubSub: resp::upload::/dev/ttyACM0::progress
         │         │
         │         ▼
         │    PubSubClient._dispatch()
         │    → matches "resp::compile::*" / "resp::upload::*"
         │         │
         │         ▼
         │    extension.py:_on_compile_resp()
         │    → _on_compile_progress() or _on_compile_done()
         │    extension.py:_on_upload_resp()
         │         │
         │         ├── Compile: <progress id="compile-progress--{ps}" ... hx-swap-oob="true">
         │         │            (broadcast even when out+err empty — progress-only messages)
         │         │
         │         ├── Compile: <span hx-swap-oob="beforeend:#compile-output--{ps}">
         │         │            [N%] prefix prepended to output text
         │         │
         │         └── Upload:  <span hx-swap-oob="beforeend:#upload-output--{ps}">
         │                      (no progress bar, no [N%] prefix)
         │         │
         │         ▼
         │    WS broadcast → HTMX appends/replaces in DOM
         │
         └──────────────────────────────────────────────────────────
```

---

## 12. Summary: All WS Message Types

| Tier | Trigger | Source Function | WS HTML Sent | DOM Target | OOB Strategy |
|------|---------|----------------|--------------|------------|--------------|
| 0 | PubSub `board::+::event` | `_on_board_event()` | `<div hx-swap-oob="afterbegin:#live-events-card"><div class="board-event">...</div></div>` | `#live-events-card` | `afterbegin:` — prepend event card |
| 1 | Daemon ready/reconnect | `_broadcast_daemon_badge()` | `<span id="daemon-badge" hx-swap-oob="true">...</span>` | `#daemon-badge` | Replace by `id` |
| 1 | PubSub `board::+::event` | `_on_board_event()` | `<span id="board-status-badge--{ps}" hx-swap-oob="true">...</span>` | `#board-status-badge--{ps}` | Replace by per-port `id` |
| 2 | PubSub `resp::compile::*::progress` | `_on_compile_progress()` | `<span hx-swap-oob="beforeend:#compile-output--{ps}"><div class="compile-line">...</div></span>` | `#compile-output--{ps}` | `beforeend:` — append output line |
| 2 | PubSub `resp::upload::*::progress` | `_on_upload_resp()` | `<span hx-swap-oob="beforeend:#upload-output--{ps}"><div class="upload-line">...</div></span>` | `#upload-output--{ps}` | `beforeend:` — append output line |
| 3 | PubSub `resp::compile::*::progress` (percent change) | `_on_compile_progress()` | `<progress id="compile-progress--{ps}" value="N" max="100" hx-swap-oob="true">` | `#compile-progress--{ps}` | Replace by per-port `id` |

*(ps = port_safe = port.replace("/", "_"))*

## 13. Summary: Potential Sources of Double Events (Tier 0)

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