---
---

# dist-standalone — Standalone Binary Distributions

Standalone binary builds for the 3 CLI apps via [PyOxidizer](https://pyoxidizer.readthedocs.io/). Each binary bundles the Python interpreter, the application code, and all dependencies into a single executable (with a `prefix/` sidecar for C extensions).

## Quick Start

```bash
# Build all 3 apps (requires PyOxidizer + pre-built wheels)
./scripts/build_standalone.sh

# Run the Board Manager Service (gRPC)
dist-standalone/board-manager/board-manager

# Run Arduino Dash (Flask :8080)
dist-standalone/arduino-dash/arduino-dash

# Run MedMinder Dash (Flask :8080)
dist-standalone/medminder-dash/medminder-dash
```

## What You Get

```
dist-standalone/
├── board-manager/
│   ├── board-manager       # ~51 MB standalone binary
│   ├── prefix/             # ~100 MB sidecar (C extensions)
│   └── board-manager.tar.gz
├── arduino-dash/
│   ├── arduino-dash
│   ├── prefix/
│   └── arduino-dash.tar.gz
└── medminder-dash/
    ├── medminder-dash
    ├── prefix/
    └── medminder-dash.tar.gz
```

## Documentation

| Document | Description |
|----------|-------------|
| [architecture.md](architecture.md) | How PyOxidizer bundles apps, the `prefix/` sidecar, `@REPO_ROOT@` placeholder approach |
| [api.md](api.md) | CLI flags reference for all 3 binaries |
| [guide.md](guide.md) | Building, running, deployment, and troubleshooting |
| [tests.md](tests.md) | Testing methodology for standalone binaries |

## Related

- [scripts/docs/build-standalone.md](../../scripts/docs/build-standalone.md) — Build script (`build_standalone.sh`) reference
- [docs/dist-standalone.md](../../docs/dist-standalone.md) — Project-level entry point
