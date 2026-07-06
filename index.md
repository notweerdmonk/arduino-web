---
layout: default
---

# Arduino Web Documentation

Welcome to the Arduino Web documentation. This index maps all documentation resources across the monorepo.

> **Last updated**: 2026-07-07 — Phases 109-119 complete (Code Review, Security Audit, Semantic Versioning v0.1.0, Config/CI/Docs, Ruff Format Audit, Prettier/Djlint Convergence). See [agent-docs/PLAN.md](agent-docs/PLAN.md) for full phase history.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Project overview, quick start, architecture diagram, how to run each service |
| [docs/architecture.md](docs/architecture.md) | System architecture, process model, data flow, design decisions, technology stack |
| [docs/guide.md](docs/guide.md) | User guide: setup, board selection, medicine management, compile/upload, gunicorn deployment, troubleshooting |
| [docs/api.md](docs/api.md) | API reference: pub/sub protocol, gRPC client, Flask routes, environment variables |
| [docs/tests.md](docs/tests.md) | Testing methodology: framework, categories, running tests, coverage by package |
| [docs/review.md](docs/review.md) | Code review methodology: process, finding classification, review categories, verification |
| [scripts/](scripts/docs/index.md) | Scripts: CI, builds, gRPC stubs, Arduino deps, test suite |
| [e2e/](e2e/index.md) | E2E browser testing: mock servers, scenarios, Playwright MCP |
| [dist-test-install/](dist-test-install/index.md) | Wheel install validation |
| [dist-standalone-install/](dist-standalone-install/index.md) | Standalone binary builds |

---

## Per-Package Documentation

### `arduino-grpc` — Python gRPC client for Arduino CLI daemon

Base: `grpc_client/python/arduino_grpc/`

| Doc | Description |
|-----|-------------|
| [README.md](grpc_client/python/arduino_grpc/README.md) | Package overview |
| [docs/index.md](grpc_client/python/arduino_grpc/docs/index.md) | Package summary, dependencies, monorepo context |
| [docs/client.md](grpc_client/python/arduino_grpc/docs/client.md) | `ArduinoGrpcClient` — all methods with signatures |
| [docs/models.md](grpc_client/python/arduino_grpc/docs/models.md) | `Port`, `Board`, `CompileResult`, `UploadResult` data models |
| [docs/exceptions.md](grpc_client/python/arduino_grpc/docs/exceptions.md) | Exception hierarchy: `ArduinoError` → typed subclasses |
| [docs/reference](grpc_client/python/arduino_grpc/docs/reference) | Arduino gRPC API reference |

### `board-manager` — Pub/sub BoardManagerService

Base: `board_manager/python/board_manager/`

| Doc | Description |
|-----|-------------|
| [README.md](board_manager/python/board_manager/README.md) | Package overview, install, usage |
| [docs/index.md](board_manager/python/board_manager/docs/index.md) | Package overview, module summary, config, env vars |
| [docs/service.md](board_manager/python/board_manager/docs/service.md) | `BoardManagerService` — event loop, client lifecycle, message handling |
| [docs/protocol.md](board_manager/python/board_manager/docs/protocol.md) | Framing, `FrameReader`, `Handshake`, encode/decode |
| [docs/router.md](board_manager/python/board_manager/docs/router.md) | `TopicRouter` — MQTT-style wildcards, subscribe/publish |
| [docs/pool.md](board_manager/python/board_manager/docs/pool.md) | `BoardPool` — subprocess lifecycle, socketpair IPC, restart limits |
| [docs/board_detector.md](board_manager/python/board_manager/docs/board_detector.md) | `BoardDetector` — watch/poll modes, auto-recovery |
| [docs/board_worker.md](board_manager/python/board_manager/docs/board_worker.md) | Worker subprocess entrypoint — all supported methods |
| [docs/daemon_manager.md](board_manager/python/board_manager/docs/daemon_manager.md) | `DaemonManager` — arduino-cli daemon lifecycle, health check |
| [docs/boot.md](board_manager/python/board_manager/docs/boot.md) | WSGI lifecycle helpers — `start_bms`, `stop_bms`, `wait_for_bms` |
| [docs/config.md](board_manager/python/board_manager/docs/config.md) | `Config` dataclass, `load_config` — 3-tier priority |
| [docs/udev_monitor.md](board_manager/python/board_manager/docs/udev_monitor.md) | `UdevMonitor` — USB hotplug via pyudev |
| [docs/reference](board_manager/python/board_manager/docs/reference/) | Board Manager API reference |

### `board-manager-client` — PubSubClient

Base: `board_manager_client/python/board_manager_client/`

| Doc | Description |
|-----|-------------|
| [README.md](board_manager_client/python/board_manager_client/README.md) | Package overview, install, usage |
| [docs/index.md](board_manager_client/python/board_manager_client/docs/index.md) | Package overview, exports, dependencies |
| [docs/pubsub_client.md](board_manager_client/python/board_manager_client/docs/pubsub_client.md) | `PubSubClient` — connect, subscribe, publish, reconnect, callbacks |
| [docs/reference](board_manager_client/python/board_manager_client/docs/reference) | Board Manager Client API reference |

### `arduino-sketch-tools` — Flask extension for compile/upload

Base: `arduino_sketch_tools/python/arduino_sketch_tools/`

| Doc | Description |
|-----|-------------|
| [README.md](arduino_sketch_tools/python/arduino_sketch_tools/README.md) | Package overview, install, usage |
| [docs/index.md](arduino_sketch_tools/python/arduino_sketch_tools/docs/index.md) | Package overview, Flask extension pattern |
| [docs/extension.md](arduino_sketch_tools/python/arduino_sketch_tools/docs/extension.md) | `ArduinoSketchTools` — `init_app`, blueprint registration, state management |
| [docs/routes.md](arduino_sketch_tools/python/arduino_sketch_tools/docs/routes.md) | Compile/upload Flask routes, request/response formats |
| [docs/sketch_registry.md](arduino_sketch_tools/python/arduino_sketch_tools/docs/sketch_registry.md) | `SketchRegistry` — hardware ID → sketch assignment, thread safety |
| [docs/reference](arduino_sketch_tools/python/arduino_sketch_tools/docs/reference) | Arduino Sketch Tools API reference |

### `arduino-dash` — Board + compile web dashboard

Base: `arduino_dash/python/arduino_dash/`

| Doc | Description |
|-----|-------------|
| [README.md](arduino_dash/python/arduino_dash/README.md) | Package overview, install, usage |
| [docs/index.md](arduino_dash/python/arduino_dash/docs/index.md) | Package overview, module summary, env vars |
| [docs/app.md](arduino_dash/python/arduino_dash/docs/app.md) | Flask app factory `create_app()` |
| [docs/board_management.md](arduino_dash/python/arduino_dash/docs/board_management.md) | Board helpers for session-based active board |
| [docs/pubsub.md](arduino_dash/python/arduino_dash/docs/pubsub.md) | PubSub event handlers, `PubSubTopic` enum |
| [docs/html_routes.md](arduino_dash/python/arduino_dash/docs/html_routes.md) | All HTML routes with method + description |
| [docs/api_routes.md](arduino_dash/python/arduino_dash/docs/api_routes.md) | JSON API endpoints and request/response formats |
| [docs/state.md](arduino_dash/python/arduino_dash/docs/state.md) | Shared module state |
| [docs/utils.md](arduino_dash/python/arduino_dash/docs/utils.md) | Utility functions |
| [docs/settings.md](arduino_dash/python/arduino_dash/docs/settings.md) | Configuration paths |
| [docs/wsgi.md](arduino_dash/python/arduino_dash/docs/wsgi.md) | WSGI entry point for gunicorn |
| [docs/gunicorn_conf.md](arduino_dash/python/arduino_dash/docs/gunicorn_conf.md) | Gunicorn configuration hooks |
| [docs/sketch_management.md](arduino_dash/python/arduino_dash/docs/sketch_management.md) | Sketch upload/management functions |
| [docs/sketch_registry.md](arduino_dash/python/arduino_dash/docs/sketch_registry.md) | Hardware ID → sketch assignment registry |
| [docs/reference](arduino_dash/python/arduino_dash/docs/reference) | Arduino Dash API reference |

### `medminder-dash` — Medicine reminder web dashboard

Base: `medminder_dash/python/medminder_dash/`

| Doc | Description |
|-----|-------------|
| [README.md](medminder_dash/python/medminder_dash/README.md) | Package overview, install, usage |
| [docs/index.md](medminder_dash/python/medminder_dash/docs/index.md) | Package overview, module summary, env vars |
| [docs/app.md](medminder_dash/python/medminder_dash/docs/app.md) | Flask app factory `create_app()`, `_migrate_default_board` |
| [docs/pubsub.md](medminder_dash/python/medminder_dash/docs/pubsub.md) | PubSub infrastructure, event handlers, WS broadcast |
| [docs/html_routes.md](medminder_dash/python/medminder_dash/docs/html_routes.md) | All HTML routes with method + description |
| [docs/api_routes.md](medminder_dash/python/medminder_dash/docs/api_routes.md) | JSON API endpoints, medicine CRUD, deploy |
| [docs/medicines_state.md](medminder_dash/python/medminder_dash/docs/medicines_state.md) | `Medicine` dataclass, `MedicineStore` CRUD, persistence |
| [docs/sketch_gen.md](medminder_dash/python/medminder_dash/docs/sketch_gen.md) | `generate_alarm_hpp`, `parse_alarm_hpp` |
| [docs/state.md](medminder_dash/python/medminder_dash/docs/state.md) | Shared module state |
| [docs/utils.md](medminder_dash/python/medminder_dash/docs/utils.md) | Utility functions |
| [docs/settings.md](medminder_dash/python/medminder_dash/docs/settings.md) | Sketch directory configuration |
| [docs/wsgi.md](medminder_dash/python/medminder_dash/docs/wsgi.md) | WSGI entry point for gunicorn |
| [docs/gunicorn_conf.md](medminder_dash/python/medminder_dash/docs/gunicorn_conf.md) | Gunicorn configuration hooks |
| [docs/sketch_management.md](medminder_dash/python/medminder_dash/docs/sketch_management.md) | Sketch upload/management functions |
| [docs/sketch_registry.md](medminder_dash/python/medminder_dash/docs/sketch_registry.md) | Hardware ID → sketch assignment registry |
| [docs/board_management.md](medminder_dash/python/medminder_dash/docs/board_management.md) | Board management (placeholder) |
| [docs/reference](medminder_dash/python/medminder_dash/docs/reference) | MedMinder Dash API reference |

---

## Top-Level System Documentation

| Document | Description | Full Docs |
|----------|-------------|-----------|
| [dist-test-install/index.md](dist-test-install/index.md) | Wheel install validation | [`README.md`](dist-test-install/README.md) |
| [dist-standalone-install/index.md](dist-standalone-install/index.md) | Standalone binary builds | [`dist-standalone-install/index.md`](dist-standalone-install/index.md) |

## Reference Documents

| Document | Description |
|----------|-------------|
| [agent-docs/PLAN.md](agent-docs/PLAN.md) | Project master plan (append-only, per-phase) |
| [agent-docs/JOURNAL.md](agent-docs/JOURNAL.md) | Development log (append-only) |
| [agent-docs/CODEBASE_REFERENCE.md](agent-docs/CODEBASE_REFERENCE.md) | Technical reference, code snippets, declarations |
| [agent-docs/BUGS.md](agent-docs/BUGS.md) | Known issues and regressions |
| [agent-docs/TODOS.md](agent-docs/TODOS.md) | Active task checklist |
| [docs/ws-event-flow.md](docs/ws-event-flow.md) | WebSocket event flow documentation |
| [e2e/docs/reference/typedoc/](e2e/docs/reference/typedoc/) | E2E fixtures + config API reference (typedoc) |
| [e2e/docs/reference/specs.md](e2e/docs/reference/specs.md) | E2E Playwright spec reference (22 tests across 8 files) |
