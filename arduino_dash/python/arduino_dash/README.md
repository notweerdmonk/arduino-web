---
---
# arduino-dash

Web GUI dashboard for the arduino-cli Board Manager. Displays connected
Arduino boards, ports, and live compile/upload status via a WebSocket
channel driven by the BoardManagerService.

## Overview

`arduino-dash` is a Flask application that provides a browser-based
interface for:

- **Board monitoring** — real-time list of connected boards with port,
  FQBN, and connection status, updated via WebSocket events from the
  BoardManagerService.
- **Compile sketches** — select a sketch directory and compile against
  any detected board's FQBN, with live progress streamed to the UI.
- **Upload firmware** — upload compiled binaries to a selected board
  via its serial port.
- **Sketch management** — drag-and-drop upload of new sketches, file
  browser for the sketch directory, version history, and checksum-based
  deduplication.
- **Daemon lifecycle** — start/stop the arduino-cli daemon from the UI
  and monitor its health.

## Architecture

```
┌─────────────────┐     WebSocket      ┌──────────────────┐
│  arduino-dash   │ ◄────────────────► │                  │
│  (Flask app)    │                    │ BoardManagerSvc  │
│                 │    gRPC (via       │  (board-manager  │
│  ┌───────────┐  │    pubsub)         │   package)       │
│  │ WebSocket │  │◄──────────────────►│                  │
│  │  routes   │  │                    │  ┌────────────┐  │
│  ├───────────┤  │                    │  │ arduino-cli│  │
│  │  Compile  │  │                    │  │  daemon    │  │
│  │  / Upload │  │                    │  └────────────┘  │
│  ├───────────┤  │                    └──────────────────┘
│  │  Sketch   │  │
│  │  Mgmt     │  │
│  └───────────┘  │
└─────────────────┘
```

The app uses `arduino-sketch-tools` (Flask extension) for the
compile/upload routes and partials, `board-manager-client` for pubsub
connectivity, and `board-manager` for board detection. All inter-package
dependencies are resolved through the monorepo's local wheel index.

## Installation

### From PyPI

```bash
pip install arduino-dash
```

### From the monorepo (development)

```bash
cd arduino_dash/python/arduino_dash
pipenv install --dev
pipenv run python -m arduino_dash
```

Or via nox:

```bash
nox -s 'tests(arduino_dash)' 'build(arduino_dash)'
```

## Usage

```bash
# Start the dashboard (default port 5000)
python -m arduino_dash

# Or use the console script
arduino-dash

# With gunicorn (production)
gunicorn arduino_dash.wsgi:app -c arduino_dash/gunicorn_conf.py
```

Open `http://localhost:5000` in a browser.

## Development

### Setup

```bash
cd arduino_dash/python/arduino_dash
pipenv install --dev
pipenv shell
```

### Running tests

```bash
pipenv run pytest tests/ -v
```

### Building a wheel

```bash
pipenv run python -m build --outdir dist/arduino-dash
```

## Project Structure

```
arduino_dash/python/arduino_dash/
├── arduino_dash/
│   ├── __init__.py
│   ├── __main__.py          # CLI entry point
│   ├── app.py               # Flask app factory + routes
│   ├── board_management.py  # Board detail + deploy routes
│   ├── gunicorn_conf.py     # Gunicorn config hooks
│   ├── pubsub.py            # PubSub init + fallback scanner
│   ├── utils.py             # Utility functions
│   ├── sketch_management.py # Sketch CRUD + upload routes
│   ├── state.py             # Shared in-memory state
│   ├── wsgi.py              # WSGI entry for gunicorn
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── board_detail.html
│   │   └── partials/
│   └── uploads/             # User-uploaded sketch archives
├── tests/
│   ├── __init__.py
│   ├── test_app.py          # App route + WS tests
│   └── test_gunicorn_conf.py
├── setup.py
├── setup.cfg
├── pyproject.toml
├── Pipfile
└── Pipfile.lock
```

## Test Suite

The test suite covers:

| Test class | Focus |
|-----------|-------|
| `TestOnResp` | Response handler stores results and signals events |
| `TestWaitForResponse` | Async response polling with timeout |
| `TestApiCompile` | Compile endpoint (success, failure, no board) |
| `TestApiUpload` | Upload endpoint (success, failure, missing port) |
| `TestInitPubsub` | PubSub initialization lifecycle |
| `TestCompileMeta` | Compile metadata extraction |
| `TestUploadMeta` | Upload metadata extraction |
| `TestBoardConnectionStatus` | Board connection status endpoint |
| `TestBmsOffline` | BMS offline state handling |
| `TestDaemonStatus` | Daemon status endpoint |
| `TestComputeSketchChecksum` | Checksum computation for dedup |
| `TestGetSketchMtime` | Modification time detection |
| `TestUploadConfirmWarnings` | Upload confirmation warnings |
| `TestCompileWarning` | Compile warning display logic |
| `TestSketchUpload` | Sketch upload with drag-and-drop |
| `TestLastUpload` | Last upload endpoint |
| `TestApiSketches` | Sketch listing endpoint |
| `TestRenderSketchPathSelector` | Path selector HTML rendering |
| `TestMakeMetaSketchName` | Metadata sketch name generation |
| `TestNormalizeInoFilename` | INO filename normalization |
| `TestSketchDelete` | Sketch deletion |
| `TestSketchVersionListing` | Sketch version history |
| `TestDedupAcrossVersions` | Cross-version deduplication |
| `TestGetBmsConfig` | BMS env config defaults |
| `TestWhenReady` | Gunicorn `when_ready` hook |
| `TestPostWorkerInit` | Gunicorn `post_worker_init` hook |
| `TestOnExit` | Gunicorn `on_exit` hook |

**Total**: 96 tests across 2 files.

## Dependencies

- **flask** (>=3.0.0) — web framework
- **flask-sock** (>=0.7.0) — WebSocket support
- **arduino-grpc** (>=0.1.0) — gRPC client stubs
- **board-manager** (>=0.1.0) — board detection service
- **board-manager-client** (>=0.1.0) — pubsub client
- **arduino-sketch-tools** (>=0.1.0) — compile/upload extension
- **gunicorn** (>=20.0) — WSGI server (production)

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free

## License

MIT
