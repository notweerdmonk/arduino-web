---
---
# arduino-dash

**Version:** 0.1.0

A Flask web dashboard for board management, compile/upload UI, and live WebSocket events. Part of the Arduino Web monorepo. It connects to `BoardManagerService` via PubSub and provides HTML routes, JSON API routes, sketch management, and WebSocket live events.

## Console Script

Installed as the `arduino-dash` console script (defined in `pyproject.toml` and `setup.py`):

```
arduino-dash [--host HOST] [--port PORT] [--uds PATH] [--tcp-host HOST] [--tcp-port PORT] [--no-uds] [--debug]
```

Also invocable via `python -m arduino_dash` (see `__main__.py`).

## Architecture (Monorepo Context)

```
Arduino Web Monorepo
├── arduino_dash/python/arduino_dash    ← this package
│   ├── arduino_dash/                    (Python source)
│   └── docs/                            (this documentation)
├── arduino_grpc/                        (gRPC client library)
├── board_manager/                       (BoardManagerService boot/management)
├── board_manager_client/                (PubSub client to BMS)
└── arduino_sketch_tools/               (Sketch compile/upload logic)
```

The dashboard is a Flask webapp that:

1. Connects to `BoardManagerService` via a **PubSub** (ZeroMQ) channel (`pubsub.py`)
2. Exposes **HTML routes** (`html_routes.py`) with HTMX partials and server-sent OOB swaps
3. Exposes **JSON API routes** (`api_routes.py`) for programmatic access
4. Provides a **WebSocket** endpoint (`/ws/board-events`) via `flask-sock` for live board event streaming
5. Manages **sketch upload/registry** (`sketch_management.py`, `sketch_registry.py`) with deduplication by SHA-256 checksum
6. Delegates compile/upload to `ArduinoSketchTools` extension (`arduino_sketch_tools`)

## Modules Summary

| Module | File | Description |
|--------|------|-------------|
| `__init__` | `__init__.py` | Package metadata (`__version__`) |
| `__main__` | `__main__.py` | CLI entry point, argparse, `init_pubsub()` then `app.run()` |
| `app` | `app.py` | Flask app factory `create_app()`, re-exports state symbols |
| `pubsub` | `pubsub.py` | PubSub init, topic handlers, WebSocket broadcast, fallback scanner, response waiting |
| `html_routes` | `html_routes.py` | All HTML/HTMX route handlers, sketch upload/delete via forms, WebSocket endpoint |
| `api_routes` | `api_routes.py` | All `/api/` JSON route handlers, sketch upload/delete via JSON |
| `state` | `state.py` | Shared module-level state: locks, board list, compile/upload results, registry, WS clients |
| `utils` | `utils.py` | Port validation, normalization, board lookup helpers |
| `settings` | `settings.py` | `CONFIG_DIR`, `UPLOAD_BASE_DIR` path constants |
| `wsgi` | `wsgi.py` | WSGI entry point for gunicorn |
| `gunicorn_conf` | `gunicorn_conf.py` | Gunicorn configuration: BMS lifecycle hooks, worker PubSub init |
| `sketch_management` | `sketch_management.py` | Sketch registry persistence, version lookups, path selector rendering |
| `sketch_registry` | `sketch_registry.py` | Per-board assignment registry keyed by `hardware_id` |
| `board_management` | `board_management.py` | Board helpers for session-based active board (routes in html/api files) |

## Environment Variables

| Variable | Default | Used In | Purpose |
|----------|---------|---------|---------|
| `ARDUINO_DASH_SECRET` | `dev-secret-arduino` | `app.py` | Flask `secret_key` |
| `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` | `wsgi.py`, `gunicorn_conf.py` | UDS path for BMS |
| `BOARD_MGR_TCP_HOST` | `127.0.0.1` | `wsgi.py`, `gunicorn_conf.py` | TCP host for BMS |
| `BOARD_MGR_TCP_PORT` | `9090` | `wsgi.py`, `gunicorn_conf.py` | TCP port for BMS |
| `BMS_NO_UDS` | `""` | `wsgi.py`, `gunicorn_conf.py` | Force TCP only when `"1"` or `"true"` |
| `BMS_FIRE_AND_FORGET` | `""` | `gunicorn_conf.py` | Skip BMS readiness wait when `"1"`, `"true"`, or `"yes"` |
| `BMS_WAIT_TIMEOUT` | `10` | `gunicorn_conf.py` | Seconds to wait for BMS readiness |
| `GUNICORN_BIND` | `0.0.0.0:8080` | `gunicorn_conf.py` | Gunicorn bind address |
| `GUNICORN_WORKERS` | `4` | `gunicorn_conf.py` | Number of gunicorn workers |
| `GUNICORN_TIMEOUT` | `120` | `gunicorn_conf.py` | Gunicorn worker timeout |
| `GUNICORN_LOG_LEVEL` | `info` | `gunicorn_conf.py` | Gunicorn log level |

## Document Reference

| Document | Description |
|----------|-------------|
| [README](../README.md) | Package overview, install, usage |
| [app.md](app.md) | Flask app factory `create_app()` |
| [pubsub.md](pubsub.md) | PubSub event handlers, `PubSubTopic` enum |
| [html_routes.md](html_routes.md) | All HTML routes with method + description |
| [api_routes.md](api_routes.md) | JSON API endpoints and request/response formats |
| [state.md](state.md) | Shared module state |
| [utils.md](utils.md) | Utility functions |
| [settings.md](settings.md) | Configuration paths |
| [wsgi.md](wsgi.md) | WSGI entry point for gunicorn |
| [gunicorn_conf.md](gunicorn_conf.md) | Gunicorn configuration hooks |
| [sketch_management.md](sketch_management.md) | Sketch upload/management functions |
| [sketch_registry.md](sketch_registry.md) | Hardware ID → sketch assignment registry |
| [board_management.md](board_management.md) | Board helpers for session-based active board |

## Key Dependencies (runtime)

- `flask >= 3.0` — Web framework
- `gunicorn >= 20.0` — Production WSGI server
- `board-manager-client` — PubSub client for BMS communication
- `arduino-sketch-tools` — Flask extension for compile/upload orchestration
- `flask-sock` — WebSocket support (for live event streaming)
- `simple-websocket` — WebSocket transport for flask-sock (sync WSGI servers)
