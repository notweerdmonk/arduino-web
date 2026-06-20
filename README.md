---
---
# MedMinder

Arduino board monitoring and management via gRPC, with a pub/sub BoardManagerService and a Flask+HTMX+WebSocket web dashboard.

## Architecture

```
┌─────────────┐   gRPC    ┌──────────────────┐  IPC (UDS)   ┌──────────┐
│ arduino-cli │◄──────────│  BoardManager    │◄─────────────│  WebApp  │
│   daemon    │           │  Service         │              │  Flask   │
│  :50051     │           │  :9090 / UDS     │              │  :8080   │
└─────────────┘           └──────────────────┘              └──────────┘
```

Six Python packages in this repo:

- **[arduino-grpc](grpc_client/python/arduino_grpc/)** — Python gRPC client for arduino-cli daemon (board detection, compile, upload)
- **[board-manager](board_manager/python/board_manager/)** — Pub/sub service that manages one subprocess per Arduino board (console script: `board-manager`)
- **[board-manager-client](board_manager_client/python/board_manager_client/)** — `PubSubClient` (TCP+UDS wrapper)
- **[arduino-sketch-tools](arduino_sketch_tools/python/arduino_sketch_tools/)** — Flask extension with shared compile/upload/board routes
- **[arduino-dash](arduino_dash/python/arduino_dash/)** — Web GUI #1: board + compile dashboard (console script: `arduino-dash`)
- **[medminder-dash](medminder_dash/python/medminder_dash/)** — Web GUI #2: medicine reminder (console script: `medminder-dash`)

## How to run

### Prerequisite

arduino-cli daemon must be running:

```bash
nohup arduino-cli daemon --port 50051 --daemonize > /dev/null 2>&1 & disown
```

### 1. Start BoardManagerService (TCP :9090 + UDS /tmp/board_mgr.sock)

```bash
cd board_manager
pipenv run python -m board_manager
```

Optional flags: `--tcp-port 9091`, `--uds-path /tmp/custom.sock`, `--log-level DEBUG`

### 2. Start arduino-dash (Flask :8080)

```bash
cd arduino_dash
pipenv run python -m arduino_dash
```

arduino-dash auto-connects to BoardManager's UDS at `/tmp/board_mgr.sock`. Optional flags:
`--port 8081`, `--tcp-host 10.0.0.1 --tcp-port 9090`, `--no-uds` (force TCP), `--debug`

### 3. Open the dashboard

Browse to [http://localhost:8080](http://localhost:8080)

### (Optional) Start medminder-dash (Flask :8081)

```bash
cd medminder_dash
pipenv run python -m medminder_dash --port 8081
```

## Running tests

```bash
cd board_manager/python/board_manager && pipenv run python -m pytest tests/ -v
cd arduino_dash/python/arduino_dash && pipenv run python -m pytest tests/ -v
cd medminder_dash/python/medminder_dash && pipenv run python -m pytest tests/ -v
cd arduino_sketch_tools/python/arduino_sketch_tools && pipenv run python -m pytest tests/ -v
cd board_manager_client/python/board_manager_client && pipenv run python -m pytest tests/ -v
cd grpc_client/python/arduino_grpc && pipenv run python -m pytest tests/ -v
```

Or build all wheels and run every test in one go:

```bash
nox            # builds 6 wheels into their respective dist/ dirs
for p in grpc_client arduino_sketch_tools board_manager_client board_manager arduino_dash medminder_dash; do
    (cd "$p/python/$p" && pipenv run python -m pytest tests/ -q)
done
```

## Editable dev mode

After `pipenv install`, run once for live code reloading:

```bash
pipenv run pip install -e ./python/
```

## MedMinder Dash (board‑centric web app)

The `medminder_dash` Flask app provides a board‑centric UI for managing medicine schedules and deploying to Arduino boards.

### Board Selection

1. Open the app → the landing page shows a board selector dropdown (auto‑populated via `/api/board_list`).
2. Select a board → the app stores it in the session and redirects to the board detail view (`/board`).
3. The navbar shows a status badge (polls `/api/board_status` every 5s).
4. Medicine CRUD operations are scoped to the selected board.

### Running with Gunicorn

```bash
cd medminder_dash/python/medminder_dash
gunicorn -b 0.0.0.0:8080 -c medminder_dash/gunicorn_conf.py medminder_dash.wsgi:app
```

The `-c medminder_dash/gunicorn_conf.py` config sets up `post_worker_init` to wire up pubsub. Override worker count and secret via env vars.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GUNICORN_WORKERS` | `4` | Number of Gunicorn worker processes (read by `gunicorn_conf.py`) |
| `FLASK_SECRET_KEY` | `dev-secret` | Secret key for Flask sessions (read by `app.py`) |

### Metadata Persistence

Per‑board medicine data is stored in `medminder_dash/python/data/board_meta.json`. Each board key maps to its own list of `Medicine` objects. The file is read on app startup and written after every mutation (add/update/delete/toggle).

```json
{
  "/dev/ttyACM0": {
    "medicines": [
      { "id": "...", "name": "Ibup", "hour": 8, "minute": 30, "enabled": true }
    ]
  }
}
```

### Running Tests

```bash
cd medminder_dash/python/medminder_dash
pipenv run python -m pytest medminder_dash/tests/ tests/ -v
```

## Scripts

Full documentation: [`scripts/docs/index.md`](scripts/docs/index.md)

```bash
./scripts/ci.sh                        # Full CI pipeline (tests + builds)
./scripts/build_standalone.sh          # Standalone binaries via PyOxidizer
./scripts/test_installs.sh             # Wheel install validation + smoke tests
./scripts/install_arduino_deps.sh      # Install Arduino libraries (RTClib, TM1637)
pipenv run python scripts/gen_grpc_bindings.py  # Regenerate gRPC stubs
```

136-test suite at `scripts/tests/`: `nox -s scripts_tests`

## Documentation Structure

```
medminder/
├── docs/                                    # Top-level holistic docs
│   ├── architecture.md                      # System architecture
│   ├── guide.md                             # User guide
│   ├── api.md                               # API reference
│   ├── tests.md                             # Testing methodology
│   ├── index.md                             # Documentation hub
│   ├── scripts.md                           # → scripts/docs/ (link)
│   ├── e2e-testing.md                       # → e2e/docs/ (link)
│   ├── dist-test-install.md                 # → dist-test-install/docs/ (link)
│   └── dist-standalone.md                   # → dist-standalone-install/docs/ (link)
│
├── scripts/
│   └── docs/                                # Scripts documentation (7 files)
│       ├── index.md                         # Overview
│       ├── ci.md                            # CI pipeline
│       ├── build-standalone.md              # Standalone builds
│       ├── test-installs.md                 # Wheel install validation
│       ├── install-arduino-deps.md          # Arduino library installer
│       ├── gen-grpc-bindings.md             # gRPC stub generator
│       └── tests.md                         # Scripts test suite
│
├── e2e/
│   └── docs/                                # E2E testing documentation (4 files)
│       ├── index.md                         # Overview
│       ├── servers.md                       # Mock server reference
│       ├── scenarios.md                     # Test scenario recipes
│       └── agent-tools.md                   # Agent integration
│
├── dist-test-install/
│   └── docs/
│       └── index.md                         # Wheel install validation environment
│
├── dist-standalone-install/
│   └── docs/
│       └── index.md                         # Standalone binary distribution
│
├── board_manager/python/board_manager/
│   └── docs/                                # Per-package docs (11 modules)
│       ├── index.md                         # Package overview
│       ├── service.md
│       ├── protocol.md
│       ├── router.md
│       ├── pool.md
│       ├── board_detector.md
│       ├── board_worker.md
│       ├── daemon_manager.md
│       ├── boot.md
│       ├── config.md
│       └── udev_monitor.md
│
├── board_manager_client/python/board_manager_client/
│   └── docs/                                # Per-package docs (1 module)
│       ├── index.md
│       └── pubsub_client.md
│
├── arduino_sketch_tools/python/arduino_sketch_tools/
│   └── docs/                                # Per-package docs (2 modules)
│       ├── index.md
│       ├── extension.md
│       └── routes.md
│
├── grpc_client/python/arduino_grpc/
│   └── docs/                                # Per-package docs (3 modules)
│       ├── index.md
│       ├── client.md
│       ├── models.md
│       └── exceptions.md
│
├── arduino_dash/python/arduino_dash/
│   └── docs/                                # Per-package docs (12 modules)
│       ├── index.md
│       ├── app.md
│       ├── pubsub.md
│       ├── html_routes.md
│       ├── api_routes.md
│       ├── sketch_management.md
│       ├── sketch_registry.md
│       ├── state.md
│       ├── utils.md
│       ├── settings.md
│       ├── wsgi.md
│       └── gunicorn_conf.md
│
└── medminder_dash/python/medminder_dash/
    └── docs/                                # Per-package docs (14 modules)
        ├── index.md
        ├── app.md
        ├── pubsub_infra.md
        ├── html_routes.md
        ├── api_routes.md
        ├── medicines_state.md
        ├── sketch_gen.md
        ├── sketch_management.md
        ├── sketch_registry.md
        ├── state.md
        ├── utils.md
        ├── settings.md
        ├── wsgi.md
        └── gunicorn_conf.md
```

### Reference

- [PLAN.md](PLAN.md) — project master plan
- [JOURNAL.md](JOURNAL.md) — development log
- [CODEBASE_REFERENCE.md](CODEBASE_REFERENCE.md) — technical reference
- [index.md](index.md) — full documentation hub (all docs across the monorepo)

### Sub-Directory Documentation

- [scripts/docs/index.md](scripts/docs/index.md) — scripts reference
- [e2e/docs/index.md](e2e/docs/index.md) — E2E browser testing
- [dist-test-install/docs/index.md](dist-test-install/docs/index.md) — wheel install validation
- [dist-standalone-install/docs/index.md](dist-standalone-install/docs/index.md) — standalone binary distribution

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free
