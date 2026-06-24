---
---
# medminder_dash — Package Overview

`medminder_dash` is a Flask web dashboard for managing medicine reminders on
Arduino MedMinderV2 boards. It is part of the **MedMinder monorepo**.

## Console Script

Defined in `setup.py` (`setup.cfg` at line 39):

```
medminder-dash=medminder_dash.__main__:main
```

Invoked as:

```bash
medminder-dash [--host 0.0.0.0] [--port 8080] [--uds /tmp/board_mgr.sock]
               [--debug] [--no-uds] [--tcp-host 127.0.0.1] [--tcp-port 9090]
```

Or via module:

```bash
python -m medminder_dash [--host 0.0.0.0] [--port 8080] ...
```

## Architecture within the Monorepo

The MedMinder monorepo contains several sibling packages:

| Package | Role |
|---------|------|
| `medminder-dash` | Flask dashboard (this package) |
| `board-manager` | BoardManagerService — manages Arduino board lifecycle |
| `board-manager-client` | Client library + PubSub client for BMS communication |
| `arduino-sketch-tools` | Flask extension for compile/upload orchestration |
| `*-grpc` | gRPC protobuf definitions and stubs |

`medminder_dash` communicates with `board-manager` via the `board-manager-client`
PubSub protocol over Unix domain sockets (default `/tmp/board_mgr.sock`) or TCP
(127.0.0.1:9090).

## Module Summary

| Module | File | Description |
|--------|------|-------------|
| `__main__` | `__main__.py` | CLI entry point (argparse + dev server) |
| `app` | `app.py` | Flask app factory + deployment tracking |
| `api_routes` | `api_routes.py` | JSON API routes (`/api/...`) |
| `html_routes` | `html_routes.py` | HTML page and partial routes |
| `pubsub` | `pubsub.py` | PubSub client lifecycle, WebSocket broadcast, board event handling |
| `state` | `state.py` | Shared mutable state (ports, WS clients, pending responses, locks) |
| `utils` | `utils.py` | Port validation, board lookup, medicine validation, display helpers |
| `settings` | `settings.py` | Sketch directory configuration and persistence |
| `wsgi` | `wsgi.py` | WSGI entry point for gunicorn |
| `gunicorn_conf` | `gunicorn_conf.py` | Gunicorn server hooks (BMS start/stop, PubSub init per worker) |
| `medicines_state` | `medicines_state.py` | `Medicine` dataclass and `MedicineStore` (persistent per-board CRUD) |
| `sketch_gen` | `sketch_gen.py` | Generate/parse `alarm.hpp` C++ header from medicine data |
| `sketch_registry` | `sketch_registry.py` | Per-hardware-ID sketch assignment registry |
| `sketch_management` | `sketch_management.py` | Sketch upload, checksum, dedup, registry persistence |
| `board_management` | `board_management.py` | Placeholder — routes moved to `html_routes.py` |

## Environment Variables

| Variable | Default | Used By | Purpose |
|----------|---------|---------|---------|
| `FLASK_SECRET_KEY` | `dev-secret` | `app.py` | Flask session signing key |
| `GUNICORN_BIND` | `0.0.0.0:8080` | `gunicorn_conf.py` | Gunicorn bind address |
| `GUNICORN_WORKERS` | `4` | `gunicorn_conf.py` | Number of gunicorn worker processes |
| `GUNICORN_TIMEOUT` | `120` | `gunicorn_conf.py` | Gunicorn worker timeout (seconds) |
| `GUNICORN_LOG_LEVEL` | `info` | `gunicorn_conf.py` | Gunicorn log level |
| `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` | `wsgi.py`, `gunicorn_conf.py` | UDS path for BMS |
| `BOARD_MGR_TCP_HOST` | `127.0.0.1` | `wsgi.py`, `gunicorn_conf.py` | TCP host for BMS |
| `BOARD_MGR_TCP_PORT` | `9090` | `wsgi.py`, `gunicorn_conf.py` | TCP port for BMS |
| `BMS_NO_UDS` | `""` | `wsgi.py`, `gunicorn_conf.py` | Force TCP-only when `"1"` or `"true"` |
| `BMS_FIRE_AND_FORGET` | `""` | `gunicorn_conf.py` | Skip wait-for-BMS when `"1"`/`"true"`/`"yes"` |
| `BMS_WAIT_TIMEOUT` | `10` | `gunicorn_conf.py` | BMS ready wait timeout (seconds) |

## Key Dependencies (runtime)

- `flask >= 3.0` — Web framework
- `gunicorn >= 20.0` — Production WSGI server
- `board-manager-client` — PubSub client for BMS communication
- `arduino-sketch-tools` — Flask extension for compile/upload orchestration
- `flask-sock` — WebSocket support (optional, for live event streaming)
