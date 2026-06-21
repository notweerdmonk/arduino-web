---
---
{% raw %}
# ArduinoSketchTools Extension

**Source:** `arduino_sketch_tools/extension.py`

## Class: `ArduinoSketchTools`

```python
class ArduinoSketchTools(pubsub=None, broadcast_ws=None, get_board_info=None, record_deploy=None)
```

Flask Extension managing Arduino sketch compile/upload state. Encapsulates all
compile/upload results, metadata, and pub/sub response handling. Registers a
Blueprint with compile/upload routes via `init_app()`. As of Phase 98, all
compile output is streamed over WebSocket OOB pushes with real-time `<progress>`
bar updates and per-line `[N%]` progress prefixes.

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pubsub` | PubSubClient or None | `None` | Pub/sub client for publishing commands and subscribing to responses |
| `broadcast_ws` | callable | `lambda html: None` | Callable accepting an HTML string to broadcast over WebSocket |
| `get_board_info` | callable | `lambda port: {}` | Callable accepting a port string, returning a dict with `board`, `fqbn`, `hardware_id` keys |
| `record_deploy` | callable | `lambda port, sketch_path: None` | Callable accepting port and sketch path to persist a deployment record |

### Class Constants

| Constant | Value | Description |
|---|---|---|
| `COMPILE_TIMEOUT` | `150` | Seconds after which a compile is considered timed out |

### Usage Example

```python
from flask import Flask
from arduino_sketch_tools import ArduinoSketchTools

app = Flask(__name__)
tools = ArduinoSketchTools(
    pubsub=pubsub_client,
    broadcast_ws=lambda html: socketio.emit("output", html),
    get_board_info=my_board_info_lookup,
    record_deploy=my_deploy_recorder,
)
tools.init_app(app)
```

---

## Method: `init_app()`

```python
def init_app(self, app, pubsub=None) -> None
```

Register the extension with a Flask application.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `app` | `flask.Flask` | The Flask application instance |
| `pubsub` | PubSubClient or None | Optional pub/sub client; overrides `self.pubsub` if given |

**Behaviour:**

1. Stores the extension instance in `app.extensions["arduino_sketch_tools"]`.
2. If a pub/sub client is available (either from the constructor or the
   `pubsub` argument), subscribes to two topic patterns:
   - `resp::compile::*` — handled by `_on_compile_resp`
   - `resp::upload::*` — handled by `_on_upload_resp`
3. Imports `compile_bp` from `arduino_sketch_tools.routes` and registers it
   with the app via `app.register_blueprint(compile_bp)`.

---

## Method: `_norm_port()`

```python
def _norm_port(self, port: str) -> str | None
```

Normalize and validate a port path. Strips extra leading slashes, ensures
exactly one `/` prefix, then validates against the pattern
`^/dev/[a-zA-Z0-9_/]+$`.

| Returns | Description |
|---|---|
| `str` | Normalized port (e.g. `/dev/ttyACM0`) if valid |
| `None` | If the port string is invalid |

---

## Compile / Upload State Management

The extension maintains several thread-safe dictionaries for per-port state.
Each dict is protected by its own `threading.Lock`.

### State Dictionaries

| Attribute | Key Type | Value Type | Description |
|---|---|---|---|
| `_compile_results` | `str` (port) | `dict \| None` | Final compile result message from pub/sub, or `None` while in-flight |
| `_upload_results` | `str` (port) | `dict \| None` | Final upload result message from pub/sub, or `None` while in-flight |
| `_compile_start` | `str` (port) | `float` | `time.time()` when the compile was initiated |
| `_compile_meta` | `str` (port) | `dict` | Metadata dict for in-progress compile (see `_make_meta`) |
| `_upload_meta` | `str` (port) | `dict` | Metadata dict for in-progress upload |
| `_compile_last_pct` | `str` (port_safe) | `float` | Last broadcast progress percentage — used to suppress duplicate progress bar OOB updates |
| `_last_compiled_sketch` | `str` (port) | `str` | Sketch path of the most recent successful compile |
| `_last_compile_mtime` | `str` (port) | `float \| None` | Latest source-file mtime after the last successful compile |
| `_last_compile_checksum` | `str` (port) | `str` | SHA-256 hex digest of source files after the last successful compile |
| `_last_uploaded_sketch` | `str` (port) | `str` | Sketch path of the most recent upload attempt |

---

## Metadata Builder: `_make_meta()`

```python
def _make_meta(self, port: str, sketch_path: str) -> dict
```

Build a metadata dict for a compile or upload operation.

**Returns:**

```python
{
    "port": "/dev/ttyACM0",
    "board": "Arduino Uno",
    "fqbn": "arduino:avr:uno",
    "hardware_id": "2341:0043",
    "sketch": "/home/user/sketches/blink",
    "sketch_name": "blink",
    "started_at": 1715000000.0,   # time.time()
}
```

The `board`, `fqbn`, and `hardware_id` values come from the `get_board_info`
callback. The `sketch_name` is the basename of the normalized sketch path.

---

## Pub/Sub Response Handlers

### `_on_compile_resp()`

```python
def _on_compile_resp(self, msg: dict) -> None
```

Handle a compile response message from pub/sub. The `topic` field is
inspected:

- **Progress messages** — topics ending with `::progress` (format
  `resp::compile::{port}::progress`). The `output` and `error` fields from
  the message data are processed as follows:

  1. **Progress bar OOB** — If the message contains a `percent` field, a
     `<progress id="compile-progress-{port_safe}" value="{percent}" max="100">`
     element is wrapped in an `<span hx-swap-oob="true">` and broadcast via
     WebSocket. The broadcast is suppressed if the percentage hasn't changed
     since the last message (tracked by `_compile_last_pct`).
  2. **`[N%]` prefix** — If the output text is non-empty, a `[33%]` prefix
     is prepended to display the current progress alongside the text.
  3. **Output wrapping** — The text (with optional `[N%]` prefix) is
     HTML-escaped, wrapped in a
     `<span hx-swap-oob="beforeend:#compile-output-{port_safe}">`
     containing a `<div class="compile-line">` element, and sent to
     `_broadcast_ws`.

- **Final messages** — topic `resp::compile::{port}`. The message dict is
  stored in `_compile_results[port]`. If `status == "ok"`, the sketch path
  from the response data is recorded in `_last_compiled_sketch` and the
  latest source-file mtime is stored in `_last_compile_mtime`.

  Output is wrapped in an `<span hx-swap-oob="beforeend:#compile-output-{port_safe}">`
  element so WS-delivered lines appear in the correct output container on the
  board detail page. The `port_safe` value is derived from the port path by
  replacing `/` with `_` (e.g., `/dev/ttyACM0` → `_dev_ttyACM0`), matching
  the Jinja2 `{{ port | replace('/', '_') }}` template filter.

The `_compile_last_pct` dictionary tracks the last broadcast progress
percentage per `port_safe`. This prevents redundant `<progress>` OOB HTML
from being sent to the browser when the percentage hasn't changed between
messages.

**Pure progress-only messages:** When the board worker sends a message with
output text AND the progress has advanced, the text is broadcast with the
`[N%]` prefix AND a separate `<progress>` OOB is sent. When the board worker
sends a progress-only message (no output text, only percent changed), only
the `<progress>` OOB is sent — no output line is broadcast.

### `_on_upload_resp()`

```python
def _on_upload_resp(self, msg: dict) -> None
```

Handle an upload response message from pub/sub. The `topic` field is
inspected:

- **Progress messages** — topics ending with `::progress` (format
  `resp::upload::{port}::progress`). HTML-escaped output is wrapped in
  `<div class="upload-line">` and sent to `_broadcast_ws`. The output is
  wrapped in an `<span hx-swap-oob="beforeend:#upload-output-{port_safe}">`
  element so WS-delivered lines appear in the correct upload output container
  on the board detail page. Unlike compile messages, upload outputs have no
  `[N%]` prefix or progress bar — `UploadResponse` has no `TaskProgress`
  field.
- **Final messages** — topic `resp::upload::{port}`. Stored in
  `_upload_results[port]`. If `status == "ok"`, the `record_deploy` callback
  is invoked with the port and sketch path.

---

## Progress Callback

The `_broadcast_ws` callable (set via the constructor) receives HTML strings
for real-time output. Typical usage with Flask-SocketIO:

```python
tools = ArduinoSketchTools(
    broadcast_ws=lambda html: socketio.emit("compile-output", html, room=port),
)
```

The HTML strings are sent as **OOB (Out-of-Band)** swaps so they target the
correct output container on the page without requiring the HTMX WS extension
to parse routing instructions:

- **Compile output:** `<span hx-swap-oob="beforeend:#compile-output-{port_safe}"><div class="compile-line" data-port="{port}">{pct_prefix}escaped text</div></span>`
- **Compile progress bar:** `<span hx-swap-oob="true"><progress id="compile-progress-{port_safe}" value="{percent}" max="100"></progress></span>`
- **Upload output:** `<span hx-swap-oob="beforeend:#upload-output-{port_safe}"><div class="upload-line" data-port="{port}">escaped text</div></span>`

Where `port_safe` is the port path with `/` replaced by `_` (e.g.,
`/dev/ttyACM0` → `_dev_ttyACM0`), matching the Jinja2 template filter
`{{ port | replace('/', '_') }}`.

The compile progress bar OOB is only broadcast when the percentage actually
changes (tracked by `_compile_last_pct` per `port_safe`). Pure progress-only
messages (no output text, only percent change) send only the progress bar OOB
without any output line.

---

## SHA-256 Checksum Computation

### `_compute_sketch_checksum()`

```python
def _compute_sketch_checksum(self, sketch_dir: str) -> str
```

Compute a SHA-256 checksum over all source files in a sketch directory.

**Algorithm:**

1. Walk the directory recursively (`os.walk`).
2. Collect all files ending with `.ino`, `.cpp`, `.h`, `.hpp`, or `.c`.
3. Sort the file paths alphabetically for deterministic ordering.
4. Feed each file's content (in 64 KiB chunks) into a `hashlib.sha256()`
   hasher.
5. Return the hex digest.

| Returns | Description |
|---|---|
| `str` | 64-character hex digest |
| `""` | Empty string if no source files found or the directory does not exist |

### `_get_sketch_mtime()`

```python
def _get_sketch_mtime(self, sketch_path: str) -> float | None
```

Return the latest modification time (`os.path.getmtime`) among all source
files (`.ino`, `.cpp`, `.h`, `.hpp`, `.c`) in a sketch directory.

| Returns | Description |
|---|---|
| `float` | Latest mtime (Unix timestamp) |
| `None` | If the directory is empty, missing, or contains no matching files |

---

## Module-Level Helpers

### `_normalize_port()`

```python
def _normalize_port(port: str) -> str | None
```

Standalone function (not on the class) that normalizes and validates a port
path. Strips extra leading slashes, prefixes with a single `/`, then matches
against the regex `^/dev/[a-zA-Z0-9_/]+$`.

---

## Thread Safety

All shared state dictionaries use dedicated `threading.Lock` instances.
Every read or write to these dicts is performed inside a `with
self._<name>_lock` block. The compile and upload response handlers run on
pub/sub subscriber threads and must be safe for concurrent access with Flask
request threads.
{% endraw %}
