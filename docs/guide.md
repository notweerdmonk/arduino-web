---
layout: default
---
# User Guide

> **Per-package docs:** For detailed module-level guides, see:
> - [`board_manager/docs/boot.md`](../board_manager/python/board_manager/docs/boot.md) — BMS start/stop/wait lifecycle
> - [`board_manager/docs/config.md`](../board_manager/python/board_manager/docs/config.md) — configuration loading
> - [`arduino_dash/docs/gunicorn_conf.md`](../arduino_dash/python/arduino_dash/docs/gunicorn_conf.md) — arduino-dash gunicorn config
> - [`arduino_dash/docs/sketch_management.md`](../arduino_dash/python/arduino_dash/docs/sketch_management.md) — sketch upload/management
> - [`arduino_dash/docs/sketch_registry.md`](../arduino_dash/python/arduino_dash/docs/sketch_registry.md) — sketch assignment
> - [`medminder_dash/docs/gunicorn_conf.md`](../medminder_dash/python/medminder_dash/docs/gunicorn_conf.md) — medminder-dash gunicorn config
> - [`medminder_dash/docs/medicines_state.md`](../medminder_dash/python/medminder_dash/docs/medicines_state.md) — medicine CRUD
> - [`medminder_dash/docs/sketch_gen.md`](../medminder_dash/python/medminder_dash/docs/sketch_gen.md) — alarm.hpp generation
> - [`medminder_dash/docs/sketch_management.md`](../medminder_dash/python/medminder_dash/docs/sketch_management.md) — sketch management
> - [`medminder_dash/docs/settings.md`](../medminder_dash/python/medminder_dash/docs/settings.md) — sketch directory config

## Quick Start

### Prerequisites

- Python 3.10+
- `pipenv` (`pip install pipenv`)
- [arduino-cli](https://arduino.github.io/arduino-cli/) installed and on `PATH`

### 1. Start the Arduino CLI daemon

```bash
nohup arduino-cli daemon --port 50051 --daemonize > /dev/null 2>&1 & disown
```

Verify it's running:

```bash
arduino-cli board list
```

### 2. Install Arduino libraries

```bash
./scripts/install_arduino_deps.sh
```

This installs `RTClib` (for DS3231 RTC) and `TM1637TinyDisplay` (for 7-segment display).

### 3. Start BoardManagerService

```bash
cd board_manager/python/board_manager
pipenv install
pipenv run python -m board_manager
```

This starts the pub/sub service on:
- **TCP** — `127.0.0.1:9090`
- **UDS** — `/tmp/board_mgr.sock`

### 4. Start a web dashboard

**arduino-dash** (board management + compile):

```bash
cd arduino_dash/python/arduino_dash
pipenv install
pipenv run python -m arduino_dash --port 8080
```

Open [http://localhost:8080](http://localhost:8080)

**medminder-dash** (medicine reminder + compile/upload):

```bash
cd medminder_dash/python/medminder_dash
pipenv install
pipenv run python -m medminder_dash --port 8081
```

Open [http://localhost:8081](http://localhost:8081)

### 5. Run the full test suite

```bash
nox -s all_tests          # 8 sessions: all 6 packages + scripts
./scripts/ci.sh           # full CI pipeline (builds → tests)
```

The nox sessions auto-regenerate Pipfile.lock on each run (Phase 94), so there is
no manual lock management needed after wheel rebuilds or Pipfile changes.

## Board Selection (medminder-dash)

The medminder-dash app is board-centric — most operations are scoped to a specific Arduino board.

### Selecting a board

1. Open the app — the landing page shows a board selector dropdown (auto-populated from BoardManagerService).
2. Select a board — the app stores it in the session and redirects to the board detail view (`/board`).
3. The navbar shows a daemon status badge updated in real time via WebSocket push (no polling).

### Board detail view

The `/board` page shows:
- **Connection status** — green/red indicator
- **Compile/Upload card** — compile the MedMinder sketch and upload to the board
- **Medicine list** — CRUD table for medicine schedule entries
- **Event log** — live board connect/disconnect events via WebSocket
- **Sketch selector** — choose which sketch version is deployed to this board

## Managing Medicines

Medicine schedules are stored per-board in `board_meta.json`.

### Add a medicine

```json
POST /api/medicines
{
  "name": "Aspirin",
  "hour": 8,
  "minute": 30,
  "day_of_week": "1,3,5",
  "day_of_month": "",
  "enabled": true
}
```

### Update a medicine

```json
PUT /api/medicines/<id>
{
  "name": "Ibuprofen",
  "hour": 12,
  "minute": 0,
  "enabled": true
}
```

### Delete a medicine

```bash
DELETE /api/medicines/<id>
```

### Toggle enabled/disabled

```bash
POST /api/medicines/<id>/toggle
```

### Time slots

Minutes are restricted to 0, 10, 20, 30, 40, 50 (6-minute resolution for the TM1637 display). Hours use 1-24 format matching the DS3231 RTC.

### Day of week / day of month

- `day_of_week` — comma-separated numbers (0=Sunday, 1=Monday, ..., 6=Saturday). Empty = all days.
- `day_of_month` — comma-separated numbers (1-31). Empty = all days.
- If both are set, the schedule runs when EITHER matches (OR logic).

## Compiling and Uploading

### Via the web UI

1. Select a board.
2. Click "Compile & Upload" on the board detail page.
3. The compile card shows progress in real time via WebSocket push (no polling):
   - **Progress bar**: A `<progress>` element fills from 0% to 100% as the
     Arduino CLI daemon emits `TaskProgress` gRPC messages (~25+ updates per
     typical compile). The bar updates only on percentage change (redundant
     updates are suppressed).
   - **Output lines**: Each compile output line arrives via OOB HTML swap,
     prefixed with `[N%]` progress percentage (e.g., `[42%] Compiling core...`).
     Lines are appended to the compile output container in real time.
   - **How it works**: The gRPC `compile_stream()` yields 4-tuples of
     `(out, err, done, percent)`. The board worker sends progress-only messages
     when only the percentage changes. The ArduinoSketchTools extension wraps
     each line in `<span hx-swap-oob="beforeend:#compile-output-{port_safe}">`
     and broadcasts over the WS connection.
4. On success, the sketch is uploaded to the board:
   - Upload output is also streamed in real time via the same OOB pattern,
     but without a progress bar — the gRPC `UploadResponse` has no
     `TaskProgress` field, so upload remains a 3-tuple `(out, err, done)`.
   - After a successful upload, the deploy timestamp is recorded to the
     sketch registry.

### Via the API

```bash
# Compile only
curl -X POST /board/ttyACM0/compile \
  -H "Content-Type: application/json" \
  -d '{"fqbn": "arduino:avr:uno"}'

# Compile + upload
curl -X POST /board/ttyACM0/upload \
  -H "Content-Type: application/json" \
  -d '{"fqbn": "arduino:avr:uno"}'
```

### Via arduino-cli directly

```bash
cd /path/to/sketch
arduino-cli compile --fqbn arduino:avr:uno .
arduino-cli upload --fqbn arduino:avr:uno --port /dev/ttyACM0 .
```

## Sketch Upload and Management

### Upload a sketch archive

```bash
curl -X POST /api/sketch/upload \
  -F "file=@medminder.zip" \
  -F "port=/dev/ttyACM0"
```

The archive is extracted, deduplicated by SHA-256 checksum, and registered. Boards are automatically assigned to sketches by hardware ID.

### List uploaded sketches

```bash
GET /api/sketches
```

### Delete a sketch version

```bash
DELETE /api/sketch
{
  "path": "/path/to/sketch/version"
}
```

## Sketch Registry

The sketch registry maps hardware IDs to sketch paths, enabling board-scoped sketch selection:

- **Upload** — a new sketch is registered and assigned to the board's hardware ID.
- **Dedup** — same checksum + different hardware ID → appends HW ID to existing entry.
- **Assignment** — `hardware_id → sketch_path` mapping persisted in `sketch_registry.json`.
- **Deploy** — compile + upload + record the deploy timestamp.

## Running with Gunicorn

For production deployment, use Gunicorn with the provided configuration:

```bash
# arduino-dash
gunicorn -b 0.0.0.0:8080 -c arduino_dash/gunicorn_conf.py arduino_dash.wsgi:app

# medminder-dash
gunicorn -b 0.0.0.0:8081 -c medminder_dash/gunicorn_conf.py medminder_dash.wsgi:app
```

The gunicorn config handles:
- **`when_ready`** — starts BoardManagerService as a subprocess before workers fork
- **`post_worker_init`** — initializes PubSub connection per worker
- **`on_exit`** — stops BoardManagerService on shutdown

Override worker count and timeout via environment variables:

```bash
GUNICORN_WORKERS=8 GUNICORN_TIMEOUT=300 gunicorn -b 0.0.0.0:8080 ...
```

## Environment Variables

### BoardManager Service

| Variable | Default | Description |
|----------|---------|-------------|
| `BOARD_MGR_TCP_HOST` | `127.0.0.1` | TCP bind host |
| `BOARD_MGR_TCP_PORT` | `9090` | TCP bind port |
| `BOARD_MGR_UDS_PATH` | `/tmp/board_mgr.sock` | Unix domain socket path |
| `BOARD_MGR_ARDUINO_DAEMON` | `localhost:50051` | Arduino CLI daemon gRPC address |
| `BOARD_MGR_DAEMON_BINARY` | `arduino-cli` | Arduino CLI binary path |
| `BOARD_MGR_LOG_LEVEL` | `INFO` | Log level |
| `BOARD_MGR_CONFIG` | `""` | Path to TOML config file |
| `BOARD_MGR_DETECTION_MODE` | `watch` | Detection mode (`watch` / `poll`) |

### Web Apps

| Variable | Default | Description |
|----------|---------|-------------|
| `BMS_NO_UDS` | `false` | Force TCP-only transport |
| `BMS_FIRE_AND_FORGET` | `false` | Don't wait for BMS readiness |
| `BMS_WAIT_TIMEOUT` | `10` | BMS readiness wait (seconds) |
| `GUNICORN_BIND` | `0.0.0.0:8080` | Gunicorn bind address |
| `GUNICORN_WORKERS` | `4` | Number of workers |
| `GUNICORN_TIMEOUT` | `120` | Worker timeout (seconds) |
| `GUNICORN_LOG_LEVEL` | `info` | Log level |
| `FLASK_SECRET_KEY` | `dev-secret` | Session secret (medminder-dash) |
| `ARDUINO_DASH_SECRET` | `dev-secret-arduino` | Session secret (arduino-dash) |

## GPIO Wiring (MedMinderV2 Sketch)

The MedMinderV2 Arduino sketch expects:

| Component | Pin |
|-----------|-----|
| DS3231 RTC | I2C (SDA, SCL) — typically A4, A5 on Uno |
| TM1637 Display CLK | D2 |
| TM1637 Display DIO | D3 |
| Buzzer | D4 |
| Button 1 (next) | D5 |
| Button 2 (confirm) | D6 |

## Troubleshooting

### "Address already in use" error

A stale BoardManagerService is holding port 9090. The `_free_bms_resources()` function in `boot.py` tries to kill it automatically; if that fails:

```bash
lsof -ti tcp:9090 | xargs kill -15
rm -f /tmp/board_mgr.sock
```

### "No board detected" in tests

The arduino-grpc integration tests for `test_watch_boards_event` and `test_upload` require a physical Arduino board connected via USB. Other tests only need the daemon running.

### BMS not connecting

If the web app cannot connect to BoardManagerService:

1. Verify BMS is running: `ps aux | grep board_manager`
2. Check the UDS socket exists: `ls -la /tmp/board_mgr.sock`
3. Try TCP mode: set `BMS_NO_UDS=true`
4. Check daemon: `arduino-cli board list`

### pyudev not available

Board hotplug detection via `pyudev` is optional. If it's not installed, a warning is logged and the system falls back to gRPC-based board detection (watching via `BoardListWatch` RPC or polling). Install it for better detection:

```bash
pip install pyudev
```

### Compile/upload fails

1. Check Arduino CLI daemon is running.
2. Verify the sketch compiles standalone: `arduino-cli compile --fqbn arduino:avr:uno /path/to/sketch`
3. Check board is connected: `arduino-cli board list`
4. Check the FQBN matches the board type.
5. Increase Gunicorn timeout: `GUNICORN_TIMEOUT=300`

### Medicine data not persisting

Medicine data is stored in `board_meta.json`. Check:
- The file is writable by the Flask process.
- The sketch directory is configured correctly.
- Board is selected (operations are scoped to active board).

## Code Quality

All commands run from the project root. See [`docs/tests.md`](tests.md#code-quality) for full documentation.

| Tool | Scope | Command |
|------|-------|---------|
| ruff | Python sources | `pipenv run ruff check .` / `ruff format .` |
| djlint | Jinja2 templates | `pipenv run djlint . --check` / `--reformat` |
| prettier | Non-Jinja HTML | `npx prettier --check "**/*.html"` / `--write` (Jinja `**/templates/` excluded) |
| ESLint | JS linting + prettier enforcement | `npx eslint .` / `--fix` |
