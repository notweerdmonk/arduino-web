---
---
# MedMinder

Arduino board monitoring and management via gRPC, with a pub/sub BoardManagerService and a Flask+HTMX+WebSocket web dashboard. All frontend updates use WebSocket push (no periodic HTMX polling). The frontend stack uses vanilla JS event delegation (no Hyperscript) with Idiomorph for scroll-preserving morphing swaps.

## Recent Enhancements (Phases 94-100)

| Area | Change | Phase |
|------|--------|-------|
| **Build** | Noxfile self-healing: auto-regenerates `Pipfile.lock` on each run | 94 |
| **CI** | `test_ci.sh` (30 bash assertions) wired into nox `scripts_tests` | 96 |
| **Frontend** | Hyperscript (43KB) → centralized JS event delegation; Idiomorph morphing for scroll-preserving swaps | 97 |
| **Frontend** | Card-level WS swap targeting (`data-event-port`) — per-event payload from 1-5KB → ~200-500B | 97 |
| **Frontend** | All badge updates (daemon, board status) use OOB HTML over WS — no more polling | 98 |
| **Frontend** | Compile/upload output OOB targeting — lines appear in correct per-port container | 98 |
| **Frontend** | Compile progress bar with `<progress>` element + `[N%]` prefix per output line | 98 |
| **gRPC** | `compile_stream()` yields 4-tuple `(out, err, done, percent)` for progress tracking | 98 |
| **Docs** | Full Jekyll documentation site (254 pages, 0 errors); `WS_EVENT_FLOW.md` relocated to `docs/` | 93, 95 |
| **Tests** | `TestAdminBoardSelectorPolling` renamed to `TestAdminBoardSelector` (stale name after WS push migration) | 98(Q6) |
| **Templates** | All shared templates homogenised across arduino_dash + medminder_dash (14+ structurally identical) | 99 |
| **Templates** | Medicine management extracted to reusable partials (`medicine_management.html`, `admin_medicine_section.html`) | 99 |
| **Refactor** | `SketchRegistry` extracted to shared `arduino_sketch_tools/sketch_registry.py` — per-app modules become 10-line wrappers | 99 |
| **E2E Servers** | Server process lifecycle: `os.fork()` + `os.setsid()` daemonization; `--pidfile`, `--stop`, `--force`, `--logfile` flags; no shell hacks (`&`, `disown`, `&>/dev/null`) needed | 100 |

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
# All 8 test sessions via nox (6 package suites + scripts pytest + scripts bash)
nox -s all_tests

# Single package
nox -s 'tests(medminder_dash)'

# Full CI pipeline
./scripts/ci.sh
./scripts/ci.sh --skip-builds    # tests only
./scripts/ci.sh --skip-tests     # builds only
```

**Package counts:** board_manager ~212, board_manager_client 24, arduino_sketch_tools 51, arduino_dash 119, medminder_dash 186 (+1 skip), arduino_grpc 33 (+2 skip), scripts 170.

**Note:** Nox sessions auto-regenerate `Pipfile.lock` (Phase 94) — no manual lock management after wheel rebuilds.

## Editable dev mode

After `pipenv install`, run once for live code reloading:

```bash
pipenv run pip install -e ./python/
```

## MedMinder Dash (board‑centric web app)

The `medminder_dash` Flask app provides a board‑centric UI for managing medicine schedules and deploying to Arduino boards.

### Board Selection

1. Open the app → the landing page shows a board selector dropdown (auto‑populated via `/api/boards/list`).
2. Select a board → the app stores it in the session and redirects to the board detail view (`/board`).
3. The navbar shows a daemon status badge updated in real time via WebSocket push (no polling).
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

170-test suite at `scripts/tests/` (128 pytest + 12 bash + 30 bash `test_ci.sh`): `nox -s scripts_tests`

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
│   └── docs/                                # Standalone binary distribution (5 files)
│       ├── index.md                         # Overview + quick start
│       ├── architecture.md                  # PyOxidizer bundling design
│       ├── api.md                           # CLI flags reference
│       ├── guide.md                         # User guide + deployment
│       └── tests.md                         # Testing methodology
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
│   └── docs/                                # Per-package docs (3 modules)
│       ├── index.md
│       ├── extension.md
│       ├── routes.md
│       └── sketch_registry.md
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
        ├── pubsub.md
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
- [dist-standalone-install/docs/architecture.md](dist-standalone-install/docs/architecture.md) — PyOxidizer bundling design
- [dist-standalone-install/docs/api.md](dist-standalone-install/docs/api.md) — CLI flags reference
- [dist-standalone-install/docs/guide.md](dist-standalone-install/docs/guide.md) — user guide + deployment
- [dist-standalone-install/docs/tests.md](dist-standalone-install/docs/tests.md) — testing methodology

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free
