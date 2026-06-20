---
---
# wsgi (wsgi.py)

WSGI entry point for gunicorn. Creates the Flask app and configures BMS connection parameters from environment variables.

## Module-Level App

```python
app = create_app()
app.config.update(
    BMS_UDS_PATH=os.environ.get("BOARD_MGR_UDS_PATH", "/tmp/board_mgr.sock"),
    BMS_TCP_HOST=os.environ.get("BOARD_MGR_TCP_HOST", "127.0.0.1"),
    BMS_TCP_PORT=int(os.environ.get("BOARD_MGR_TCP_PORT", "9090")),
    BMS_NO_UDS=os.environ.get("BMS_NO_UDS", "").lower() in ("1", "true"),
)
```

## Usage

```bash
gunicorn -c gunicorn_conf.py arduino_dash.wsgi:app
```

## Configuration

BMS lifecycle is managed by `gunicorn_conf.py` hooks (`when_ready` / `on_exit`). The app instance itself only stores the configuration; PubSub initialization happens per-worker in the `post_worker_init` hook.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` | UDS path for BoardManagerService |
| `BOARD_MGR_TCP_HOST` | `127.0.0.1` | TCP host for BoardManagerService |
| `BOARD_MGR_TCP_PORT` | `9090` | TCP port for BoardManagerService |
| `BMS_NO_UDS` | `""` | Set to `"1"` or `"true"` to force TCP only |
