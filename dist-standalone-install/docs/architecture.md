---
---

# Standalone Binary Architecture

## Overview

Each standalone binary is produced by [PyOxidizer](https://pyoxidizer.readthedocs.io/), which takes a Python application and its dependencies and produces a single native executable. The result is a **self-contained distribution** that does not require a system Python installation.

## How Bundling Works

### PyOxidizer Configurations

Three PyOxidizer config files live under `scripts/pyoxidizer/`:

```
scripts/pyoxidizer/
├── board-manager/pyoxidizer.bzl     # Board Manager Service (gRPC daemon)
├── arduino-dash/pyoxidizer.bzl      # Arduino Dash (Flask + gunicorn)
└── medminder-dash/pyoxidizer.bzl    # MedMinder Dash (Flask + gunicorn)
```

Each config defines:

| Component | Description |
|-----------|-------------|
| **Python distribution** | A Python 3.10 interpreter is bundled statically |
| **Packaging policy** | Controls what gets included: stdlib exclusions, resource location, test stripping |
| **Python config** | Sets the entry point module (`run_module`) and importer settings |
| **Resources** | Local monorepo wheels + PyPI dependencies installed into the bundle |

### Entry Points

| Binary | Module | Description |
|--------|--------|-------------|
| `board-manager` | `board_manager.__main__` | gRPC Board Manager Service |
| `arduino-dash` | `arduino_dash.__main__` | Flask web app (Arduino dashboard) |
| `medminder-dash` | `medminder_dash.__main__` | Flask web app (MedMinder dashboard) |

### Bundled Dependencies

All three binaries bundle:
- Python 3.10 standard library (excluding turtle, tkinter, distutils, pydoc, doctest, unittest)
- Monorepo wheels: `arduino-grpc`, `board-manager`, `board-manager-client`, `arduino-sketch-tools`
- The application package itself

Dashboard binaries (`arduino-dash`, `medminder-dash`) additionally bundle:
- `flask`, `gunicorn`, `flask-sock`, `grpcio`, `protobuf`
- Templates, static files, and `simple-websocket` (WebSocket transport)

The `board-manager` binary bundles only:
- `grpcio`, `protobuf`

## The `prefix/` Sidecar

The binaries use `resources_location = "filesystem-relative:prefix"`. This means:

```
dist-standalone/<app>/
├── <binary>          # Standalone Python interpreter + application
└── prefix/           # ~100 MB: C extensions + dynamic libraries
```

The `prefix/` directory contains platform-native C extensions (`grpcio`, `protobuf` C bindings, etc.) that cannot be statically linked into the binary. **The `prefix/` directory must be present and adjacent to the binary at runtime.**

If `prefix/` is missing or moved, the binary will fail with import errors for C extension modules.

## The `@REPO_ROOT@` Placeholder

PyOxidizer's Starlark dialect does not provide `__file__` (the config file path) and `load()` cannot import variables from other `.bzl` files. To make `pyoxidizer.bzl` configs portable, the build script uses a placeholder substitution strategy:

1. **`@REPO_ROOT@`** placeholders are embedded in the `.bzl` files at the locations where absolute paths would be needed (wheel paths)
2. **`build_standalone.sh`** runs `sed -i "s|@REPO_ROOT@|${REPO_ROOT}|g"` on the `.bzl` file before invoking PyOxidizer
3. After the build completes, a **`trap cleanup RETURN`** runs `git checkout -- <bzl_file>` to restore the placeholder
4. If the build fails (`die`), an explicit `git checkout` runs before the error exit (since `exit` skips the RETURN trap)

This approach keeps the tracked `.bzl` files portable while allowing runtime path resolution.

## Packaging

After each build, the script:

1. Copies the install directory to `dist-standalone/<app>/`
2. Runs a `--help` smoke test on the binary
3. Creates a `.tar.gz` archive (or `.zip` with `--zip`)

The archives are gitignored via `.gitignore` patterns:
- `dist-standalone/`
- `dist-standalone/*.tar.gz`
- `dist-standalone/*.zip`

## Build Flow

```
nox -s all_builds
  └── Build 6 monorepo wheels (pip wheel with python -m build)

./scripts/build_standalone.sh
  ├── board-manager
  │   ├── sed @REPO_ROOT@ → actual path
  │   ├── pyoxidizer build --release
  │   ├── git checkout (restore @REPO_ROOT@)
  │   ├── copy to dist-standalone/board-manager/
  │   ├── --help smoke test
  │   └── tar czf board-manager.tar.gz
  ├── arduino-dash (same pattern)
  └── medminder-dash (same pattern)
```
