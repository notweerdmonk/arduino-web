---
layout: default
---
# `gunicorn_conf.py` — Gunicorn Configuration

**File:** `medminder_dash/gunicorn_conf.py`

Gunicorn server hooks for the MedMinder dashboard. Handles BoardManagerService
(BMS) lifecycle and PubSub initialization per worker.

## Class: `GunicornEnv(str, Enum)`

Environment variable names for gunicorn configuration.

| Member | Value | Default | Purpose |
|--------|-------|---------|---------|
| `BIND` | `"GUNICORN_BIND"` | `"0.0.0.0:8080"` | Bind address |
| `WORKERS` | `"GUNICORN_WORKERS"` | `"4"` | Number of workers |
| `TIMEOUT` | `"GUNICORN_TIMEOUT"` | `"120"` | Worker timeout (seconds) |
| `LOG_LEVEL` | `"GUNICORN_LOG_LEVEL"` | `"info"` | Log level |

## Module-Level Configuration

| Variable | Source | Default |
|----------|--------|---------|
| `bind` | `GUNICORN_BIND` | `"0.0.0.0:8080"` |
| `workers` | `GUNICORN_WORKERS` | `4` |
| `timeout` | `GUNICORN_TIMEOUT` | `120` |
| `loglevel` | `GUNICORN_LOG_LEVEL` | `"info"` |
| `preload_app` | hardcoded | `False` |
| `_bms_proc` | internal | `None` |

## Functions

### `_get_bms_config() -> dict`

Return BMS connection configuration from environment variables.

Returns: `{"uds_path", "tcp_host", "tcp_port", "use_uds"}`

```python
cfg = _get_bms_config()
# {"uds_path": "/tmp/board_mgr.sock", "tcp_host": "127.0.0.1",
#  "tcp_port": 9090, "use_uds": True}
```

### `when_ready(server)`

Gunicorn hook — called when the master process is ready.

1. Calls `board_manager.boot.start_bms()` to start the BMS process.
2. Checks `BMS_FIRE_AND_FORGET` env var:
   - If truthy, logs "BMS started (fire-and-forget mode)" and returns.
   - Otherwise, calls `wait_for_bms()` with the configured timeout (default 10s)
     from `BMS_WAIT_TIMEOUT`.
3. Logs whether BMS became ready.

| Param | Type | Purpose |
|-------|------|---------|
| `server` | gunicorn server | Server instance for logging |

### `post_worker_init(worker)`

Gunicorn hook — called after each worker process initializes.

1. Calls `_get_bms_config()` to get connection parameters.
2. Calls `medminder_dash.pubsub.init_pubsub(app, ...)` to establish the
   PubSub connection in each worker.

| Param | Type | Purpose |
|-------|------|---------|
| `worker` | gunicorn worker | Worker instance for logging |

### `on_exit(server)`

Gunicorn hook — called when the master process exits.

1. If `_bms_proc` is not `None`, calls `board_manager.boot.stop_bms(_bms_proc)`
   to gracefully shut down the BMS process.
2. Resets `_bms_proc` to `None`.

| Param | Type | Purpose |
|-------|------|---------|
| `server` | gunicorn server | Server instance for logging |
