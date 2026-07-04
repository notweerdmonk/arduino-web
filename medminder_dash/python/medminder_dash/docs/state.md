---
layout: default
---
# `state.py` — Shared Mutable State

**File:** `medminder_dash/state.py`

Holds all application-level shared mutable state — PubSub client reference, port
registry, board event buffer, pending response events, WebSocket client list,
upload registry, and the fallback scanner control variables.

Every mutable variable has an associated `threading.Lock` to ensure thread-safe
access across gunicorn worker threads and the PubSub reader thread.

## Module-Level Variables

### Application

| Variable | Type | Description |
|----------|------|-------------|
| `_app` | `flask.Flask` | Flask application reference (set by `init_pubsub`) |
| `pubsub` | `Optional[PubSubClient]` | PubSub client reference (set by `init_pubsub`) |

### WebSocket Clients

| Variable | Type | Description |
|----------|------|-------------|
| `_ws_clients` | `list` | Connected WebSocket clients |
| `_ws_lock` | `threading.Lock` | Lock for `_ws_clients` |

### Board Port Registry

| Variable | Type | Description |
|----------|------|-------------|
| `_known_ports` | `dict[str, dict]` | Port path → board info dict mapping |
| `_known_ports_lock` | `threading.Lock` | Lock for `_known_ports` |

Board info dict shape:

```python
{
    "port": "/dev/ttyACM0",
    "board": "Arduino Uno",
    "fqbn": "arduino:avr:uno",
    "hardware_id": "AD8F...",
    "event": "connected"
}
```

### Board Event Buffer

| Variable | Type | Description |
|----------|------|-------------|
| `_board_events` | `list[dict]` | Recent board events (capped at 100 entries) |
| `_board_events_lock` | `threading.Lock` | Lock for `_board_events` |

### Pending Responses (PubSub)

| Variable | Type | Description |
|----------|------|-------------|
| `_pending_responses` | `dict` | Topic → `(msg, threading.Event)` mapping |
| `_pending_responses_lock` | `threading.Lock` | Lock for `_pending_responses` |

### Daemon Ready Flag

| Variable | Type | Description |
|----------|------|-------------|
| `_daemon_ready` | `bool` | Whether the BMS daemon has reported ready |
| `_daemon_ready_lock` | `threading.Lock` | Lock for `_daemon_ready` |

### Fallback Scanner

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `_fallback_scanner` | `Optional[threading.Thread]` | `None` | Fallback scanner thread |
| `_stop_fallback_scan` | `bool` | `False` | Signal to stop fallback scanner |
| `_fallback_patterns` | `list[str]` | `["/dev/ttyACM*", "/dev/ttyUSB*"]` | Glob patterns for fallback scanning |
| `_fallback_scan_interval` | `float` | `5.0` | Interval between fallback scans (seconds) |

### Upload Registry

| Variable | Type | Description |
|----------|------|-------------|
| `UPLOAD_BASE_DIR` | `Path` | Base directory for uploaded sketches (`~/.local/share/medminder/uploads`) |
| `_upload_registry` | `dict` | In-memory upload registry: `(ip, user_agent) -> {name: [version_dict, ...]}` |
| `_upload_registry_lock` | `threading.Lock` | Lock for `_upload_registry` |

Upload version dict keys: `path`, `checksum`, `server_timestamp`, `hardware_ids`,
`board_timestamps`.

```python
# Example structure
_upload_registry = {
    ("192.168.1.5", "Mozilla/5.0 ..."): {
        "MySketch": [
            {
                "path": "/home/user/.local/share/medminder/uploads/.../MySketch",
                "checksum": "abc123...",
                "server_timestamp": "2026-06-20T12:00:00",
                "hardware_ids": ["AD8F..."],
                "board_timestamps": {"AD8F...": "2026-06-20T12:00:00"}
            }
        ]
    }
}
```
