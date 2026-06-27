---
---
# `wsgi.py` — WSGI Entry Point

**File:** `medminder_dash/wsgi.py`

WSGI entry point for gunicorn. Creates the Flask app and configures BMS
connection parameters from environment variables.

## Usage

```bash
gunicorn -c gunicorn_conf.py medminder_dash.wsgi:app
```

## Module-Level: `app`

The `app` object is a module-level `Flask` instance created by
`create_app()`. After creation, app config is updated with:

| Config Key | Env Variable | Default |
|-----------|--------------|---------|
| `BMS_UDS_PATH` | `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` |
| `BMS_TCP_HOST` | `BOARD_MGR_TCP_HOST` | `127.0.0.1` |
| `BMS_TCP_PORT` | `BOARD_MGR_TCP_PORT` | `9090` |
| `BMS_NO_UDS` | `BMS_NO_UDS` | `""` (parse: `"1"` or `"true"`) |

## Function: `create_app()` (delegated)

The actual Flask app is created by `medminder_dash.app.create_app()`. See
[app.md](app.md) for details.

## Lifecycle

BMS lifecycle (start/stop) is managed by `gunicorn_conf.py` hooks:
- `when_ready(server)` — Starts BMS
- `on_exit(server)` — Stops BMS
- `post_worker_init(worker)` — Initializes PubSub in each worker

```python
# wsgi.py — app is the WSGI callable
from medminder_dash.app import create_app

app = create_app()
app.config.update(
    BMS_UDS_PATH=...,
    BMS_TCP_HOST=...,
    BMS_TCP_PORT=...,
    BMS_NO_UDS=...,
)
```
