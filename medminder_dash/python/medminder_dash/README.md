---
---
# medminder-dash

Medicine reminder web app for the Arduino MedMinderV2. A Flask dashboard
that displays the medicine schedule, manages medication records, and
provides compile/upload/deploy workflows for the MedMinderV2 Arduino
sketch.

## Overview

`medminder-dash` is the primary user-facing dashboard in the MedMinder
ecosystem. It integrates with the BoardManagerService for live board
detection and with the arduino-cli daemon (via `arduino-sketch-tools`)
for sketch compilation and firmware upload.

### Key Features

- **Medicine management** — full CRUD for medication records: name,
  dosage, schedule, alarms. Add, edit, delete, toggle enable/disable.
- **Alarm schedule generation** — generate `alarm.hpp` from the
  medicine database and sync it to the MedMinderV2 Arduino sketch.
- **Board monitoring** — live board connect/disconnect events via
  WebSocket, powered by the BoardManagerService.
- **Sketch compile/upload** — compile the MedMinderV2 sketch and upload
  to a connected board, with live progress streaming.
- **Sketch management** — upload new sketches via drag-and-drop or file
  browser, per-board sketch assignment via USB hardware_id, version
  history.
- **Admin page** — unified `/admin` page combining sketch path
  selection, medicine management, compile, and upload.
- **Standalone deployment** — run with built-in Flask dev server or
  gunicorn for production.

## Architecture

```
┌────────────────────────────────────────────┐
│             medminder-dash                 │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │             Flask App              │    │
│  │                                    │    │
│  │  ┌────────────┐ ┌───────────────┐  │    │
│  │  │ Medicine   │ │  Sketch Mgmt  │  │    │
│  │  │ CRUD       │ │  (upload,     │  │    │
│  │  │ routes     │ │   assign,     │  │    │
│  │  └────────────┘ │   delete)     │  │    │
│  │                 └───────────────┘  │    │
│  │  ┌────────────┐ ┌───────────────┐  │    │
│  │  │  Compile   │ │  Board        │  │    │
│  │  │  / Upload  │ │  Management   │  │    │
│  │  └────────────┘ └───────────────┘  │    │
│  │                                    │    │
│  │  Uses: arduino-sketch-tools        │    │
│  │        (Flask extension)           │    │
│  └────────────────────────────────────┘    │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │  Sketch Generator                  │    │
│  │  (alarm.hpp from medicine DB)      │    │
│  └────────────────────────────────────┘    │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │  Sketch Registry                   │    │
│  │  (per-board assignment via HW ID)  │    │
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
         │
         │ gRPC / PubSub
         ▼
┌─────────────────────┐
│ BoardManagerService │
│ (board-manager)     │
└─────────────────────┘
```

## Installation

### From PyPI

```bash
pip install medminder-dash
```

### From the monorepo (development)

```bash
cd medminder_dash/python/medminder_dash
pipenv install --dev
pipenv run python -m medminder_dash
```

Or via nox:

```bash
nox -s 'tests(medminder_dash)' 'build(medminder_dash)'
```

## Usage

```bash
# Start the dashboard (default port 5000)
python -m medminder_dash

# Or use the console script
medminder-dash

# With gunicorn (production)
gunicorn medminder_dash.wsgi:app -c medminder_dash/gunicorn_conf.py
```

Open `http://localhost:5000` in a browser.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEDMINDER_PORT` | `5000` | Flask server port |
| `MEDMINDER_DEBUG` | `0` | Enable debug mode |
| `MEDMINDER_SKETCH_DIR` | (packaged) | Path to MedMinderV2 sketch source |

## Development

### Setup

```bash
cd medminder_dash/python/medminder_dash
pipenv install --dev
pipenv shell
```

### Running tests

```bash
pipenv run pytest tests/ -v
```

### Building a wheel

```bash
pipenv run python -m build --outdir dist/medminder-dash
```

## Project Structure

```
medminder_dash/python/medminder_dash/
├── medminder_dash/
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── app.py                # Flask app factory + all routes
│   ├── board_management.py   # Board detail + admin routes
│   ├── dash_state.py         # Dashboard-level shared state
│   ├── gunicorn_conf.py      # Gunicorn config hooks
│   ├── utils.py              # Utilites
│   ├── pubsub_infra.py       # PubSub init, fallback scanner, board info resolution helpers
│   ├── settings.py           # Application settings
│   ├── sketch_gen.py         # alarm.hpp generation from medicine DB
│   ├── sketch_management.py  # Sketch CRUD + upload routes
│   ├── sketch_registry.py    # Per-board sketch assignment
│   ├── state.py              # Shared in-memory state
│   ├── wsgi.py               # WSGI entry for gunicorn
│   ├── sketches/
│   │   └── MedMinderV2/      # Packaged default sketch
│   │       ├── MedMinderV2.ino
│   │       └── alarm.hpp
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── admin.html
│   │   ├── board_detail.html
│   │   ├── medicine_form.html
│   │   ├── medicines.html
│   │   └── partials/
│   └── uploads/              # User-uploaded sketch archives
├── tests/
│   ├── __init__.py
│   ├── test_admin.py
│   ├── test_board_isolation.py
│   ├── test_bootstrap.py
│   ├── test_deploy.py
│   ├── test_e2e_sketch.py
│   ├── test_gunicorn_conf.py
│   ├── test_pubsub.py
│   ├── test_routes.py
│   ├── test_sketch_gen.py
│   └── test_sketch_registry.py
├── setup.py
├── setup.cfg
├── pyproject.toml
├── Pipfile
└── Pipfile.lock
```

## Test Suite

medminder-dash has the largest test suite in the monorepo (152 tests):

**test_admin.py** (14 test classes):
`TestSketchUpload`, `TestConfirmModal`, `TestSetMedicinesSync`,
`TestSetMedicinesGenerate`, `TestAdminPage`, `TestMedicinesDiff`,
`TestActiveBoard`, `TestMedicineCardsRender`, `TestSyncButtonsState`,
`TestAdminFrontendStructure`, `TestMedMinderV2DefaultSketch`,
`TestAdminBoardSelectorPolling`, `TestAdminHtmxNativeCompileUpload`,
`TestGlobalBoardSelectorForCompileUpload`, `TestPhase62Q4AdminSketchAssignment`,
`TestPhase62Q5AdminActiveSketch`

**test_routes.py** (15 test classes):
Medicine CRUD routes (index, list, create, edit, update, delete, toggle),
board detail FQBN display.

**test_sketch_gen.py** (6 test classes):
alarm.hpp generation and parsing (minute-to-decade, hour validation,
generate, parse, unescape text).

**test_sketch_registry.py** (1 test class):
Default sketch directory resolution.

**test_gunicorn_conf.py** (4 test classes):
BMS config, when_ready, post_worker_init, on_exit hooks.

**test_deploy.py** (4 test classes):
Deploy-only endpoints, board list.

**test_bootstrap.py**, **test_pubsub.py**, **test_board_isolation.py**,
**test_e2e_sketch.py**: Integration and edge-case coverage.

**Total**: 152 tests across 10 files.

## Dependencies

- **flask** (>=3.0) — web framework
- **gunicorn** (>=20.0) — WSGI server (production)

Runtime dependencies on `arduino-grpc`, `board-manager`,
`board-manager-client`, and `arduino-sketch-tools` are resolved via
`sys.path.insert` in `app.py` (dev mode) or installed as system packages
in the wheel/standalone distribution.

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free

## License

MIT
