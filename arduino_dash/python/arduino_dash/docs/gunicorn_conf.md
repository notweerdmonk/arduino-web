---
layout: default
---
# gunicorn_conf (gunicorn_conf.py)

Gunicorn configuration for arduino_dash. Starts `BoardManagerService` (BMS) on master start and initializes PubSub in each worker.

## Configuration

```python
bind = os.environ.get(DashEnv.BIND, "0.0.0.0:8080")
workers = int(os.environ.get(DashEnv.WORKERS, "4"))
timeout = int(os.environ.get(DashEnv.TIMEOUT, "120"))
loglevel = os.environ.get(DashEnv.LOG_LEVEL, "info")
preload_app = False
```

## Enums

### `DashEnv(str, Enum)`

Environment variable keys for gunicorn configuration.

| Member | Value | Description |
|--------|-------|-------------|
| `BIND` | `"GUNICORN_BIND"` | Bind address |
| `WORKERS` | `"GUNICORN_WORKERS"` | Number of workers |
| `TIMEOUT` | `"GUNICORN_TIMEOUT"` | Worker timeout in seconds |
| `LOG_LEVEL` | `"GUNICORN_LOG_LEVEL"` | Log level |

## Internal Functions

### `_get_bms_config() -> dict`

Read BMS configuration from environment variables.

```python
config = _get_bms_config()
# Returns:
# {
#     "uds_path": "/tmp/board_mgr.sock",
#     "tcp_host": "127.0.0.1",
#     "tcp_port": 9090,
#     "use_uds": True,
# }
```

## Gunicorn Hooks

### `when_ready(server)`

Start BMS and wait for readiness on server start.

1. Calls `board_manager.boot.start_bms()` to start the BMS process
2. If `BMS_FIRE_AND_FORGET` is not set: calls `wait_for_bms()` with the configured transport and timeout (default 10s)
3. If `BMS_FIRE_AND_FORGET` is `"1"`, `"true"`, or `"yes"`: logs and continues without waiting

### `post_worker_init(worker)`

Initialize PubSub connection in each gunicorn worker.

1. Calls `_get_bms_config()` for transport parameters
2. Calls `arduino_dash.pubsub.init_pubsub()` with those parameters
3. Each worker gets its own independent PubSub connection to BMS

```python
def post_worker_init(worker):
    cfg = _get_bms_config()
    from arduino_dash.pubsub import init_pubsub
    init_pubsub(use_uds=cfg["use_uds"], tcp_host=cfg["tcp_host"],
                tcp_port=cfg["tcp_port"], uds_path=cfg["uds_path"])
```

### `on_exit(server)`

Stop BMS process on server shutdown. Calls `board_manager.boot.stop_bms()` with the stored process reference.
