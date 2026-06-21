---
---
# arduino-sketch-tools

Flask extension that provides compile, upload, board-list, and port-list
routes for Arduino sketches. Consumed by both `arduino-dash` (board +
compile dashboard) and `medminder-dash` (medicine reminder dashboard).

## Overview

`arduino-sketch-tools` is a Flask extension (following the standard
`app.ext` pattern) that encapsulates all arduino-cli interaction:

- **Compile** — POST a sketch path + FQBN, stream compile progress
  back to the front-end via WebSocket push (Phase 98) with real-time `<progress>` bar updates
  and per-output-line `[N%]` prefix, detect result success/failure.
- **Upload** — POST a sketch path + FQBN + port, upload the compiled
  binary, stream progress (no progress bar — gRPC `UploadResponse` has no `TaskProgress`), detect result.
- **Board list** — list all connected boards with port and FQBN.
- **Port list** — list all available serial ports.
- **Sketch metadata** — checksum computation, modification time
  detection, upload confirmation warnings, compile warning extraction.

The extension registers a Flask Blueprint (`sketch_tools`) with all
routes namespaced under `/board/...`, making it easy to mount in
any Flask app that has access to a BoardManagerService pubsub channel.

## Architecture

```
┌─────────────────────────────────────────────┐
│              Consumer Flask App             │
│  (arduino-dash / medminder-dash)            │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │    ArduinoSketchTools extension      │   │
│  │                                     │   │
│  │  ┌───────────┐  ┌────────────────┐  │   │
│  │  │ Blueprint  │  │  Response mgmt │  │   │
│  │  │ /api/board │  │  (wait/notify) │  │   │
│  │  └───────────┘  └────────────────┘  │   │
│  │                                     │   │
│  │  Depends on: board-manager-client    │   │
│  │              board-manager           │   │
│  │              arduino-grpc            │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Installation

### From PyPI

```bash
pip install arduino-sketch-tools
```

### From the monorepo (development)

```bash
cd arduino_sketch_tools/python/arduino_sketch_tools
pipenv install --dev
pipenv run pytest tests/ -v
```

Or via nox:

```bash
nox -s 'tests(arduino_sketch_tools)' 'build(arduino_sketch_tools)'
```

## Usage

```python
from flask import Flask
from arduino_sketch_tools import ArduinoSketchTools

app = Flask(__name__)
sketch_tools = ArduinoSketchTools(app)

# Now /board/compile, /board/upload, /board/list, etc.
# are available on the app.
```

The extension auto-registers all routes on `init_app`. It expects a
`pubsub` attribute on the Flask app (the `board-manager-client`
PubSubClient instance) — if found, it subscribes to compile/upload
response topics automatically. Compile progress messages trigger OOB
(Out-of-Band) HTML swaps over WebSocket: output lines are wrapped in
`<span hx-swap-oob="beforeend:#compile-output-{port_safe}">`, progress
percentage drives a `<progress>` OOB element broadcast only on change,
and upload output uses `<span hx-swap-oob="beforeend:#upload-output-{port_safe}">`.

### Exposed Routes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/board/<port>/compile` | Compile a sketch |
| POST | `/board/<port>/upload` | Upload compiled binary |
| GET | `/board/<port>/list` | List connected boards |
| GET | `/board/<port>/ports` | List serial ports |
| GET | `/board/<port>/compile-result` | Poll compile status |
| GET | `/board/<port>/upload-result` | Poll upload status |

## Development

### Setup

```bash
cd arduino_sketch_tools/python/arduino_sketch_tools
pipenv install --dev
pipenv shell
```

### Running tests

```bash
pipenv run pytest tests/ -v
```

### Building a wheel

```bash
pipenv run python -m build --outdir dist/arduino-sketch-tools
```

## Project Structure

```
arduino_sketch_tools/python/arduino_sketch_tools/
├── arduino_sketch_tools/
│   ├── __init__.py          # ArduinoSketchTools extension class
│   ├── extension.py         # Extension init + route registration
│   ├── routes.py            # Compile, upload, board-list, port-list
│   └── templates/
│       └── partials/
│           ├── compile_in_progress.html
│           ├── compile_result.html
│           ├── compile_timeout.html
│           ├── upload_confirm.html
│           ├── upload_init.html
│           ├── upload_in_progress.html
│           ├── upload_poll_pending.html
│           ├── upload_result.html
│           ├── bms_offline.html
│           └── compile_poll_pending.html
├── tests/
│   ├── __init__.py
│   └── test_extension.py
├── setup.py
├── setup.cfg
├── pyproject.toml
├── Pipfile
└── Pipfile.lock
```

## Test Suite

| Test class | Focus |
|-----------|-------|
| `TestArduinoSketchTools` | Extension init, defaults, blueprint registration, pubsub subscription |
| `TestOnCompileResp` | Compile response handler (success, failure, output parsing) |
| `TestOnUploadResp` | Upload response handler (success, failure, output parsing) |
| `TestApiCompile` | Compile endpoint (valid, missing params, board offline) |
| `TestApiUpload` | Upload endpoint (valid, missing params, board offline) |
| `TestCompileMeta` | Compile metadata extraction from response protos |
| `TestUploadMeta` | Upload metadata extraction from response protos |
| `TestUploadConfirmWarnings` | Upload confirmation warnings (no verify, modified sketch) |
| `TestCompileWarning` | Compile warning extraction from stderr |
| `TestCompileChecksum` | Sketch checksum computation |
| `TestGetSketchMtime` | Sketch modification time detection |
| `TestMakeMeta` | Metadata JSON generation |
| `TestNormPort` | Port normalization |

**Total**: 51 tests across 1 file.

## Dependencies

- **flask** (>=3.0.0) — web framework
- **arduino-grpc** (>=0.1.0) — gRPC client stubs
- **board-manager** (>=0.1.0) — board detection service
- **board-manager-client** (>=0.1.0) — pubsub client

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free

## License

MIT
