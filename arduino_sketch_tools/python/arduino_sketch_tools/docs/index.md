---
---
# arduino-sketch-tools

**Version:** 0.1.0  
**Python:** >= 3.10  
**Package name:** `arduino-sketch-tools` (import as `arduino_sketch_tools`)

## Overview

`arduino-sketch-tools` is a Flask extension that provides compile and upload
routes for Arduino sketches via a pub/sub-based BoardManagerService daemon. It
is consumed by both `arduino_dash` (board + compile dashboard) and
`medminder_dash` (medicine reminder dashboard) in the Arduino Web monorepo.

The extension wraps an `ArduinoSketchTools` class that registers a Flask
blueprint, subscribes to pub/sub response topics for compile/upload progress
and results, broadcasts real-time output over WebSockets, and tracks per-port
state (results, metadata, sketch checksums, modification times) under
thread-safe locks.

## Flask Extension Pattern

`ArduinoSketchTools` follows the standard Flask extension pattern:

```python
from flask import Flask
from arduino_sketch_tools import ArduinoSketchTools

app = Flask(__name__)
tools = ArduinoSketchTools(pubsub=my_pubsub, broadcast_ws=my_broadcaster)
tools.init_app(app)
```

After `init_app()`, the extension instance is available at
`app.extensions["arduino_sketch_tools"]` and the blueprint routes are
registered on the app.

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flask` | >= 3.0.0 | Web framework |
| `arduino-grpc` | >= 0.1.0 | gRPC definitions for the arduino-cli daemon |
| `board-manager` | >= 0.1.0 | BoardManagerService daemon |
| `board-manager-client` | >= 0.1.0 | Client library for BoardManagerService |

### Optional dependencies

| Group | Package | Purpose |
|---|---|---|
| `test` | `pytest>=7` | Test runner |

## Module Layout

```
arduino_sketch_tools/
  __init__.py        # Public API: exports ArduinoSketchTools, SketchRegistry
  extension.py       # ArduinoSketchTools class, state management, checksums
  routes.py          # Flask blueprint with compile/upload routes
  sketch_registry.py # SketchRegistry class — per-board sketch assignment lookup
  templates/
    partials/        # 10 HTMX partial templates for progress/result rendering
```

## Import

```python
from arduino_sketch_tools import ArduinoSketchTools, SketchRegistry
```

- `ArduinoSketchTools` — Flask extension for compile/upload routes, WS broadcast, state management
- `SketchRegistry` — Thread-safe registry mapping hardware IDs to assigned sketch paths, operating on a shared upload registry dict
