---
---
# Architecture

> **Per-package docs:** For detailed module-level architecture and design, see:
> - [`board_manager/docs/index.md`](../board_manager/python/board_manager/board_manager/docs/index.md) — BoardManagerService package overview
> - [`board_manager/docs/service.md`](../board_manager/python/board_manager/board_manager/docs/service.md) — event loop, client lifecycle
> - [`board_manager/docs/pool.md`](../board_manager/python/board_manager/board_manager/docs/pool.md) — subprocess pool design
> - [`board_manager/docs/board_detector.md`](../board_manager/python/board_manager/board_manager/docs/board_detector.md) — detection modes
> - [`board_manager/docs/board_worker.md`](../board_manager/python/board_manager/board_manager/docs/board_worker.md) — worker IPC protocol
> - [`board_manager/docs/daemon_manager.md`](../board_manager/python/board_manager/board_manager/docs/daemon_manager.md) — daemon lifecycle
> - [`board_manager/docs/udev_monitor.md`](../board_manager/python/board_manager/board_manager/docs/udev_monitor.md) — USB hotplug monitoring
> - [`arduino_grpc/docs/index.md`](../grpc_client/python/arduino_grpc/docs/index.md) — gRPC client package overview
> - [`arduino_dash/docs/index.md`](../arduino_dash/python/arduino_dash/docs/index.md) — arduino-dash package overview
> - [`arduino_dash/docs/pubsub.md`](../arduino_dash/python/arduino_dash/docs/pubsub.md) — PubSub event handlers
> - [`medminder_dash/docs/index.md`](../medminder_dash/python/medminder_dash/medminder_dash/docs/index.md) — medminder-dash package overview
> - [`medminder_dash/docs/pubsub_infra.md`](../medminder_dash/python/medminder_dash/medminder_dash/docs/pubsub_infra.md) — PubSub infrastructure
> - [`medminder_dash/docs/medicines_state.md`](../medminder_dash/python/medminder_dash/medminder_dash/docs/medicines_state.md) — Medicine data model
> - [`medminder_dash/docs/sketch_gen.md`](../medminder_dash/python/medminder_dash/medminder_dash/docs/sketch_gen.md) — alarm.hpp generation

## System Overview

## System Overview

```
┌─────────────┐   gRPC    ┌──────────────────┐  IPC (UDS/TCP)  ┌──────────────────┐
│ arduino-cli │◄──────────│  BoardManager    │◄───────────────│  Web Apps         │
│   daemon    │           │  Service         │                 │  ┌────────────┐   │
│  :50051     │           │  :9090 / UDS     │                 │  │ arduino-dash│   │
└─────────────┘           │                  │                 │  │ :8080      │   │
                          │  ┌────────────┐  │                 │  └────────────┘   │
                          │  │ Board      │  │                 │  ┌────────────┐   │
                          │  │ Workers    │  │                 │  │medminder-  │   │
                          │  │ (per-port  │  │                 │  │ dash       │   │
                          │  │  subproc)  │  │                 │  │ :8081      │   │
                          │  └────────────┘  │                 │  └────────────┘   │
                          └──────────────────┘                 └──────────────────┘
```

The system consists of three tiers:

1. **Arduino CLI Daemon** — The official Arduino gRPC daemon (`arduino-cli daemon`) that handles board detection, compilation, and upload at the hardware level.
2. **BoardManagerService** — The central pub/sub broker that manages per-board worker subprocesses, routes messages between web apps and workers, and acts as the single point of integration with the Arduino CLI daemon.
3. **Web Applications** — Two Flask-based web UIs (`arduino-dash` and `medminder-dash`) that connect to BoardManagerService via a persistent TCP/UDS pub/sub connection.

## Process Architecture

### BoardManagerService (`board-manager`)

The core service runs as a single-threaded event loop using `select()` for I/O multiplexing:

```
Main Thread (select loop)
│
├── TCP listener (:9090)
├── UDS listener (/tmp/board_mgr.sock)
├── N client connections (TCP or UDS)
│
├── BoardDetector (daemon thread)
│   ├── "watch" mode — gRPC streaming board list
│   └── "poll" mode — periodic list_boards()
│
├── DaemonManager (manages arduino-cli daemon subprocess)
│
└── BoardPool
    ├── Per-port subprocess worker
    ├── Per-port subprocess worker
    └── ... (one per connected board)
```

**Client I/O:**
- New connections are accepted on TCP or UDS listeners.
- Each connection performs a 1-byte handshake to select framing mode.
- Data is read via `select()` in the main loop, framed (newline or length-prefixed), and dispatched to message handlers.
- Messages are routed via `TopicRouter` to subscribers or to board workers via `BoardPool`.

**Design choices:**
- Single-threaded `select()` loop avoids locking complexity.
- Per-board workers in subprocesses isolate crashes and allow parallel gRPC operations.
- `BoardDetector` runs in a daemon thread because gRPC streaming is blocking.

### Board Workers

Each board worker is a separate Python subprocess started by BoardPool. It communicates with the parent process via `socketpair()`:

```
BoardPool (parent)
   │
   ├── socketpair()
   │
   ▼
Board Worker (subprocess)
   │
   ├── Reads framed messages from socketpair
   ├── Makes gRPC calls to arduino-cli daemon
   └── Sends results/progress back via socketpair
```

Workers support these operations:
- `init` — Initialize the gRPC connection
- `list_boards` — List Arduino boards
- `compile` — Compile a sketch
- `upload` — Upload to a board
- `compile_and_upload` — Both in sequence
- `ping` — Health check

Each worker sends progress messages as events (e.g., `resp::compile::<port>::progress`) which the parent routes to subscribers via the topic router.

## Pub/Sub Communication Protocol

All inter-process communication uses a custom JSON-line pub/sub protocol over Unix Domain Sockets (primary) or TCP (fallback).

**Key design decisions:**

1. **`::` topic separator** — Double colon avoids conflicts with serial port paths (`/dev/ttyACM0`).
2. **Dual framing** — Newline-delimited for simplicity, length-prefixed for binary-safe payloads. Selected by a 1-byte handshake.
3. **MQTT-style wildcards** — `+` matches one level, `*` matches remaining levels.
4. **Re-emission on subscribe** — When a client subscribes, the server re-emits current board state and daemon state, ensuring the client never sees an empty board list.

## Board Detection

Two modes controlled by `BOARD_MGR_DETECTION_MODE`:

### "watch" mode (default)

Uses `pyudev.Monitor` to listen for USB hotplug events. At startup, scans all existing `ttyACM*` / `ttyUSB*` devices, then streams `add` / `remove` events. Gracefully degrades if `pyudev` is not installed.

```
Startup: scan existing devices → emit "connected" for each
Runtime: poll udev monitor → emit "connected"/"disconnected" on add/remove
```

Also integrates with the Arduino CLI daemon via `BoardListWatch` RPC for live board list updates.

### "poll" mode

Periodically calls `arduino-cli board list` via gRPC, compares with the previous snapshot, and emits connect/disconnect events on delta. Slower but more reliable.

## Configuration Precedence

Configuration is resolved with 3-tier priority (highest to lowest):

1. **CLI arguments** — Parsed by `argparse` in `__main__.py`
2. **Environment variables** — `BOARD_MGR_*` variables
3. **TOML config file** — Loaded from path in `BOARD_MGR_CONFIG` env var
4. **Hardcoded defaults** — `BmsDefaults` dataclass in `boot.py`

## Data Flow: Compile & Upload

```
User clicks "Compile" in web UI
       │
       ▼
Web app publishes to board::<port>::cmd (via PubSubClient)
       │
       ▼
BoardManager routes to BoardPool → Board Worker socketpair
       │
       ▼
Worker sends gRPC compile_stream() to arduino-cli daemon
       │
       ├── Progress events → socketpair → topic router → WebSocket
       │
       ▼
CompileResult → socketpair → topic router → Web UI
```

## Medicine Data Model (medminder-dash)

Medicine schedules are stored per-board in `board_meta.json`:

```
board_meta.json
├── /dev/ttyACM0
│   ├── medicines: [
│   │   { id, name, hour, minute, day_of_week, day_of_month, enabled },
│   │   ...
│   │ ]
│   └── sketch_dir: "/path/to/MedMinderV2"
└── /dev/ttyUSB0
    └── ...
```

The `medicine_state.py` module provides a thread-safe `MedicineStore` class with CRUD operations. On every mutation, the store persists to disk.

## Sketch Generation

When medicines are modified, the app generates `alarm.hpp` — a C++ header compiled into the Arduino sketch:

```
Medicine list
       │
       ▼
generate_alarm_hpp()
       │
       ▼
alarm.hpp (C++ header with alarm array)
       │
       ▼
compile → upload to board
```

The `sketch_gen.py` module handles both generation (`generate_alarm_hpp()`) and parsing (`parse_alarm_hpp()`) for round-trip fidelity.

## Sketch Registry

Each web app maintains an upload registry that maps sketches to hardware IDs:

- **Hardware ID** — Derived from USB VID:PID + serial number, uniquely identifies a physical board.
- **FCFS dedup** — Same checksum, different hardware ID → appends hardware ID to existing entry.
- **Sketch assignment** — A persistent mapping of hardware_id → sketch path, enabling board-scoped sketch selection.
- **persistence** — `sketch_registry.json` is serialized to disk and warmed up on startup.

## State Management

### BoardManager

- **Known boards** — `_known_boards: dict[str, dict]` (thread-safe via `_lock`)
- **Client connections** — `_clients: dict[int, ClientConn]` (main thread only)
- **Board pool** — `_boards: dict[str, BoardProcess]` (main thread only)
- **Daemon ready** — `_daemon_ready: bool` (main thread only)
- **Subscriptions** — `TopicRouter` (main thread only)

### Web Apps

- **Shared module state** — `state.py` modules hold `pubsub`, `_known_ports`, `_board_events`, `_pending_responses`
- **Session state** — Board selection, active board stored in Flask session
- **Medicine data** — Per-board JSON file, loaded on startup, persisted on every mutation

## Technology Stack

| Component | Technology |
|-----------|------------|
| gRPC client | `grpcio`, `protobuf` |
| Core service | Python 3.10 `select()`, `socket`, `subprocess` |
| Web framework | Flask |
| Real-time UI | HTMX + flask-sock WebSocket |
| Templates | Jinja2 |
| WSGI server | Gunicorn |
| Board detection | pyudev (optional) |
| Build | setuptools, nox |
| Testing | pytest, unittest.mock |
| Standalone binary | PyOxidizer |
| Arduino libs | RTClib, TM1637TinyDisplay |

## Error Handling Strategy

1. **gRPC errors** — Caught and wrapped in typed exceptions (`CompileError`, `UploadError`, etc.)
2. **Socket errors** — Logged at DEBUG level; client connection removed on send failure
3. **Daemon failures** — `DaemonManager` retries connection; board operations wait for daemon ready
4. **Stale BMS** — `_free_bms_resources()` in `boot.py` kills stale processes holding the TCP port and cleans stale UDS sockets
5. **pyudev not available** — Board detection logs a warning and continues without hotplug support
6. **Missing arduino-cli** — Prints install URL and exits 1
