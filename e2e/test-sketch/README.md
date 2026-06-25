
---
---

# Test Sketch — Minimal Arduino Compile/Upload Sketch

A minimal valid Arduino sketch used for end-to-end compile and upload testing.

## Purpose

This sketch is the simplest possible Arduino program (`setup(){} loop(){}`).
Its purpose is to verify that the compile pipeline accepts `.ino` files and
produces valid binary output — without any board-specific logic that could
introduce test failures unrelated to the compile/upload system.

## Usage

### Upload via Admin Page

1. Start either mock server: `python3 e2e/servers/arduino_dash_server.py --mock`
2. Navigate to the admin page at `http://localhost:8765/admin`
3. Select a board in the "Active Board" selector
4. Under "Step 2: Compile", click Compile — sketch compiles successfully
5. Under "Step 3: Upload", click Upload — sketch uploads to the selected board

### Compile via arduino-cli directly

```bash
arduino-cli compile --fqbn arduino:avr:uno e2e/test-sketch/
arduino-cli upload --fqbn arduino:avr:uno -p /dev/ttyACM0 e2e/test-sketch/
```

## Sketch Content

```cpp
void setup() {} void loop() {}
```

The sketch does nothing — it is a compile-only verification target.

## Location

```
e2e/test-sketch/
├── README.md          # This file
└── test-sketch.ino    # Minimal Arduino sketch
```

## Verification

```bash
test -f e2e/test-sketch/README.md && echo "README exists"
test -f e2e/test-sketch/test-sketch.ino && echo "sketch exists"
```

