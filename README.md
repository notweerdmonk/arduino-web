# Arduino Web

Arduino board monitoring and management via gRPC, with a pub/sub BoardManagerService and a Flask+HTMX+WebSocket web dashboard. All frontend updates use WebSocket push (no periodic HTMX polling). The frontend stack uses vanilla JS event delegation (no Hyperscript) with Idiomorph for scroll-preserving morphing swaps.

## Recent Enhancements

| Area | Change |
|------|--------|
| **Build** | Noxfile self-healing: auto-regenerates `Pipfile.lock` on each run |
| **CI** | `test_ci.sh` (30 bash assertions) wired into nox `scripts_tests` |
| **Frontend** | Hyperscript (43KB) → centralized JS event delegation; Idiomorph morphing for scroll-preserving swaps |
| **Frontend** | Card-level WS swap targeting (`data-event-port`) — per-event payload from 1-5KB → ~200-500B |
| **Frontend** | All badge updates (daemon, board status) use OOB HTML over WS — no more polling |
| **Frontend** | Compile/upload output OOB targeting — lines appear in correct per-port container |
| **Frontend** | Compile progress bar with `<progress>` element + `[N%]` prefix per output line |
| **gRPC** | `compile_stream()` yields 4-tuple `(out, err, done, percent)` for progress tracking |
| **Docs** | Full Jekyll documentation site (254 pages, 0 errors); `WS_EVENT_FLOW.md` relocated to `docs/` |
| **Tests** | `TestAdminBoardSelectorPolling` renamed to `TestAdminBoardSelector` (stale name after WS push migration) |
| **Templates** | All shared templates homogenised across arduino_dash + medminder_dash (14+ structurally identical) |
| **Templates** | Medicine management extracted to reusable partials (`medicine_management.html`, `admin_medicine_section.html`) |
| **Refactor** | `SketchRegistry` extracted to shared `arduino_sketch_tools/sketch_registry.py` — per-app modules become 10-line wrappers |
| **E2E Servers** | Server process lifecycle: `os.fork()` + `os.setsid()` daemonization; `--pidfile`, `--stop`, `--force`, `--logfile` flags; no shell hacks (`&`, `disown`, `&>/dev/null`) needed |

## Architecture

```
┌─────────────┐   gRPC    ┌──────────────────┐  IPC (UDS)   ┌──────────┐
│ arduino-cli │◄──────────│  BoardManager    │◄─────────────│  WebApp  │
│   daemon    │           │  Service         │              │  Flask   │
│  :50051     │           │  :9090 / UDS     │              │  :8080   │
└─────────────┘           └──────────────────┘              └──────────┘
```

Six Python packages in this repo:

- **[arduino-grpc](grpc_client/python/arduino_grpc/docs/)** — Python gRPC client for arduino-cli daemon (board detection, compile, upload)
- **[board-manager](board_manager/python/board_manager/docs/)** — Pub/sub service that manages one subprocess per Arduino board (console script: `board-manager`)
- **[board-manager-client](board_manager_client/python/board_manager_client/docs/)** — `PubSubClient` (TCP+UDS wrapper)
- **[arduino-sketch-tools](arduino_sketch_tools/python/arduino_sketch_tools/docs/)** — Flask extension with shared compile/upload/board routes
- **[arduino-dash](arduino_dash/python/arduino_dash/docs/)** — Web GUI #1: board + compile dashboard (console script: `arduino-dash`)
- **[medminder-dash](medminder_dash/python/medminder_dash/docs/)** — Web GUI #2: medicine reminder (console script: `medminder-dash`)

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

## Semantic Versioning

The project follows [Semantic Versioning 2.0](https://semver.org/).
Versions are tracked in `medminder/__init__.py`:

```python
__version__ = "0.1.0"
```

- **Major** — Breaking protocol, API, or CLI changes
- **Minor** — Features, non-breaking enhancements
- **Patch** — Bug fixes, docs, config, CI changes

Run `pipenv run python -c "import medminder; print(medminder.__version__)"`
to query the current version.

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

**Note:** Nox sessions auto-regenerate `Pipfile.lock` on each run — no manual lock management after wheel rebuilds.

## Linting & Formatting

```bash
# Python (root pipenv venv)
pipenv run ruff check .       # lint
pipenv run ruff format .      # format

# Jinja2 templates (root pipenv venv)
pipenv run djlint . --check   # lint
pipenv run djlint . --reformat  # auto-fix

# Non-Jinja HTML (requires npm install)
npx prettier --check "**/*.html"   # check (Jinja templates excluded via .prettierignore)
npx prettier --write "**/*.html"   # format
npx eslint .                        # lint (includes prettier rules)
npx eslint . --fix                  # auto-fix
```

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
./scripts/ci.sh                        # Full CI pipeline (builds → tests)
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
│   ├── dist-standalone.md                   # → dist-standalone-install/docs/ (link)
│   └── reference/                           # Generated API reference (pdoc)
│
├── scripts/
│   └── docs/                                # Scripts documentation (7 files)
│       ├── index.md                         # Overview
│       ├── ci.md                            # CI pipeline
│       ├── build-standalone.md              # Standalone builds
│       ├── test-installs.md                 # Wheel install validation
│       ├── install-arduino-deps.md          # Arduino library installer
│       ├── gen-grpc-bindings.md             # gRPC stub generator
│       ├── tests.md                         # Scripts test suite
│       └── reference/                       # Generated API reference (pdoc + shdoc)
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
│       ├── udev_monitor.md
│       └── reference/                       # Generated API reference (pdoc)
│
├── board_manager_client/python/board_manager_client/
│   └── docs/                                # Per-package docs (1 module)
│       ├── index.md
│       ├── pubsub_client.md
│       └── reference/                       # Generated API reference (pdoc)
│
├── arduino_sketch_tools/python/arduino_sketch_tools/
│   └── docs/                                # Per-package docs (3 modules)
│       ├── index.md
│       ├── extension.md
│       ├── routes.md
│       ├── sketch_registry.md
│       └── reference/                       # Generated API reference (pdoc)
│
├── grpc_client/python/arduino_grpc/
│   └── docs/                                # Per-package docs (3 modules)
│       ├── index.md
│       ├── client.md
│       ├── models.md
│       ├── exceptions.md
│       └── reference/                       # Generated API reference (pdoc)
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
│       ├── gunicorn_conf.md
│       └── reference/                       # Generated API reference (pdoc)
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
        ├── gunicorn_conf.md
        └── reference/                       # Generated API reference (pdoc)
```

### Reference

- [agent-docs/PLAN.md](agent-docs/PLAN.md) — project master plan
- [agent-docs/JOURNAL.md](agent-docs/JOURNAL.md) — development log
- [agent-docs/CODEBASE_REFERENCE.md](agent-docs/CODEBASE_REFERENCE.md) — technical reference
- [index.md](index.md) — full documentation hub (all docs across the monorepo)

### API Reference

- [grpc_client/python/arduino_grpc/docs/reference/](grpc_client/python/arduino_grpc/docs/reference/) — Arduino gRPC API reference
- [board_manager/python/board_manager/docs/reference/](board_manager/python/board_manager/docs/reference/) — Board Manager API reference
- [board_manager_client/python/board_manager_client/docs/reference/](board_manager_client/python/board_manager_client/docs/reference/) — Board Manager Client API reference
- [arduino_sketch_tools/python/arduino_sketch_tools/docs/reference/](arduino_sketch_tools/python/arduino_sketch_tools/docs/reference/) — Arduino Sketch Tools API reference
- [arduino_dash/python/arduino_dash/docs/reference/](arduino_dash/python/arduino_dash/docs/reference/) — Arduino Dash API reference
- [medminder_dash/python/medminder_dash/docs/reference/](medminder_dash/python/medminder_dash/docs/reference/) — MedMinder Dash API reference
- [e2e/docs/reference/](e2e/docs/reference/) — E2E server API reference
- [scripts/docs/reference/gen_grpc_bindings/](scripts/docs/reference/gen_grpc_bindings/) — gen_grpc_bindings.py API reference
- [scripts/tests/docs/reference/test_install_arduino_deps.md](scripts/tests/docs/reference/test_install_arduino_deps.md) — test_install_arduino_deps.sh reference
- [scripts/docs/reference/install_arduino_deps.md](scripts/docs/reference/install_arduino_deps.md) — install_arduino_deps.sh reference
- [scripts/docs/reference/test_installs.md](scripts/docs/reference/test_installs.md) — test_installs.sh reference
- [scripts/tests/docs/reference/test_ci.md](scripts/tests/docs/reference/test_ci.md) — test_ci.sh reference
- [scripts/docs/reference/ci.md](scripts/docs/reference/ci.md) — ci.sh reference
- [scripts/docs/reference/build_standalone.md](scripts/docs/reference/build_standalone.md) — build_standalone.sh reference
- [scripts/docs/reference/check_venv.md](scripts/docs/reference/check_venv.md) — check_venv.bash reference
- [scripts/docs/reference/add_license_headers/](scripts/docs/reference/add_license_headers/) — add_license_headers.py API reference
- [e2e/docs/reference/typedoc/](e2e/docs/reference/typedoc/) — E2E fixtures + config API reference (typedoc)
- [e2e/docs/reference/specs.md](e2e/docs/reference/specs.md) — E2E Playwright spec reference (22 tests across 8 files)
- [docs/reference/noxfile/](docs/reference/noxfile/) — noxfile.py API reference

## Acknowledgements

## Git Hooks

The repository ships with two Git hooks in `.githooks/` to enforce code quality:

- **Pre-commit** (optional): Prompts `[Y/n]` with 10s timeout (default Y). Runs ruff check, ruff format --check, prettier --check, eslint, and djlint --check. If djlint --check fails, run `pipenv run djlint . --reformat` manually then re-stage. Skip with `n` or `git commit --no-verify`.
- **Pre-push** (mandatory): Runs the full CI pipeline (`scripts/ci.sh`) — builds all 6 packages then runs all 8 test sessions (~15-25 min). Skip with `git push --no-verify`.

The pre-push hook runs **unconditionally** (no interactive prompt) — its purpose is to catch failures before they reach upstream CI. Bypass with `--no-verify` for quick pushes. The pre-commit hook's djlint check runs in `--check` mode only (read-only); auto-fix requires a manual `djlint . --reformat` pass which may need a second run due to {% raw %}`{% endblock %}`{% endraw %} convergence quirks.

The `test_ci.sh` script (30 bash assertions) validates `ci.sh` flag parsing, error propagation, and nox-not-found handling using a fake nox shim — all with zero external dependencies beyond bash. It runs as part of `nox -s scripts_tests` (202 tests total).

Enable hooks:

```bash
git config core.hooksPath .githooks
```

Assisted by OpenCode:minimax-m2.5-free and OpenCode:deepseek-v4-flash-free
