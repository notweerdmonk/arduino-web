---
---
# Standalone Builds — `build_standalone.sh`

Build standalone binaries via [PyOxidizer](https://pyoxidizer.readthedocs.io/) for the 3 CLI apps:
`board-manager`, `arduino-dash`, `medminder-dash`.

```bash
# Build all 3 apps
./scripts/build_standalone.sh

# Build a single app
./scripts/build_standalone.sh board-manager

# Package as .zip instead of .tar.gz
./scripts/build_standalone.sh --zip

# Dry-run
./scripts/build_standalone.sh --dry-run
```

## Requirements

- PyOxidizer — `pipx install pyoxidizer`
- Python 3.10 (bundled by PyOxidizer)
- All 6 monorepo wheels built — `nox -s all_builds`

## Output

```
dist-standalone/<app>/
├── <binary>          # ~51 MB standalone binary
├── prefix/           # ~100 MB filesystem-relative sidecar (C extensions)
└── <app>.tar.gz      # packaged archive (or .zip with --zip)
```

### Running

```bash
dist-standalone/board-manager/board-manager --port 50051
dist-standalone/arduino-dash/arduino-dash
dist-standalone/medminder-dash/medminder-dash
```

All three support `--help`.

## Architecture

Each binary bundles:
- Python 3.10 interpreter
- The monorepo package and its dependencies
- Flask, gunicorn, grpcio, protobuf, etc.

The `prefix/` sidecar contains platform-native C extensions that cannot be statically linked. The binary expects `prefix/` to be adjacent at runtime.

## Via Nox

```bash
nox -s build_standalone
nox -s build_standalone -- board-manager
```

## PyOxidizer Configs

Located in `scripts/pyoxidizer/`:

```
scripts/pyoxidizer/
├── board-manager/pyoxidizer.bzl
├── arduino-dash/pyoxidizer.bzl
└── medminder-dash/pyoxidizer.bzl
```
