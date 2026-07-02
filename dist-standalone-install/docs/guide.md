---
---

# Standalone Binary User Guide

## Prerequisites

To build standalone binaries, you need:

1. **PyOxidizer** — install via `pipx install pyoxidizer`
2. **All 6 monorepo wheels** — build with `nox -s all_builds`
3. **git** — required for the `@REPO_ROOT@` placeholder restore mechanism

## Building

### All 3 Apps

```bash
./scripts/build_standalone.sh
```

This builds `board-manager`, `arduino-dash`, and `medminder-dash` sequentially. Each binary takes several minutes to build (PyOxidizer compiles the embedded Python interpreter). Total time: ~15-30 minutes.

### Single App

```bash
./scripts/build_standalone.sh arduino-dash
./scripts/build_standalone.sh board-manager
./scripts/build_standalone.sh medminder-dash
```

### Via Nox

```bash
nox -s build_standalone
nox -s build_standalone -- board-manager
nox -s build_standalone -- --dry-run
```

### Package Format

By default, archives are `.tar.gz`. Use `--zip` for `.zip`:

```bash
./scripts/build_standalone.sh --zip
```

### Dry Run

```bash
./scripts/build_standalone.sh --dry-run
```

Prints what would be done without actually building.

## Running

### Minimal Setup (Dashboard + BMS)

```bash
# Terminal 1: Start Board Manager Service
dist-standalone/board-manager/board-manager

# Terminal 2: Start Arduino Dashboard
dist-standalone/arduino-dash/arduino-dash

# Open browser at http://localhost:8080
```

### Full Stack

The full system requires:

1. **arduino-cli daemon** — must be running on `localhost:50051`
2. **Board Manager Service** — connects to arduino-cli daemon, exposes pub/sub on UDS + TCP
3. **Dashboard** — connects to BMS, provides web UI

```bash
# Step 1: Start arduino-cli daemon
nohup arduino-cli daemon --port 50051 --daemonize > /dev/null 2>&1

# Step 2: Start Board Manager Service
dist-standalone/board-manager/board-manager &
# Listens on /tmp/board_mgr.sock (UDS) and 127.0.0.1:9090 (TCP)

# Step 3: Start Arduino Dash
dist-standalone/arduino-dash/arduino-dash &
# Opens http://localhost:8080

# Step 4 (optional): Start MedMinder Dash
dist-standalone/medminder-dash/medminder-dash --port 8081 &
```

## Deployment

### Directory Layout

Each standalone binary expects this layout:

```
/opt/medminder/
├── board-manager/
│   ├── board-manager
│   └── prefix/
├── arduino-dash/
│   ├── arduino-dash
│   └── prefix/
└── medminder-dash/
    ├── medminder-dash
    └── prefix/
```

Extract the archives:

```bash
cd /opt/medminder
tar xzf dist-standalone/board-manager.tar.gz
tar xzf dist-standalone/arduino-dash.tar.gz
tar xzf dist-standalone/medminder-dash.tar.gz
```

### Systemd Service Example

```ini
# /etc/systemd/system/board-manager.service
[Unit]
Description=Arduino Board Manager Service
After=network.target

[Service]
Type=simple
ExecStart=/opt/medminder/board-manager/board-manager
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/arduino-dash.service
[Unit]
Description=Arduino Dash
After=board-manager.service
Requires=board-manager.service

[Service]
Type=simple
ExecStart=/opt/medminder/arduino-dash/arduino-dash
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'grpc'"

The `prefix/` directory is missing or not adjacent to the binary.

**Fix:** Ensure `prefix/` is in the same directory as the binary:

```
dist-standalone/arduino-dash/
├── arduino-dash
└── prefix/          # ← must be here
```

### Binary fails to start silently

Check if `prefix/` exists. Run with `--debug` (dashboard apps) or `--log-level DEBUG` (board-manager) to see diagnostic output.

### Build fails with Starlark errors

The `pyoxidizer.bzl` file may still contain absolute paths instead of `@REPO_ROOT@` placeholders. Check if `git checkout` restored the placeholder (the file in git should have `@REPO_ROOT@` but on disk may have substituted paths after a partial build).

**Fix:** Run `git checkout -- scripts/pyoxidizer/*/pyoxidizer.bzl` to restore all placeholders.

### Build fails with "error[CM01]: Variable '__file__' not found"

If you see this, the `.bzl` file has a reference to `__file__`. PyOxidizer's Starlark does not support `__file__`. Replace with `@REPO_ROOT@` placeholder + `sed` substitution pattern.

### "Permission denied" when running binary

Ensure the binary is executable:

```bash
chmod +x dist-standalone/*/arduino-dash
```

### "Address already in use"

Another instance is already running on the same port. Use a different port:

```bash
dist-standalone/arduino-dash/arduino-dash --port 8082
```
