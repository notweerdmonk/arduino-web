---
---

# dist-standalone — Standalone Binary Distributions

Standalone binary builds for the 3 CLI apps via [PyOxidizer](https://pyoxidizer.readthedocs.io/). Each binary bundles the Python interpreter, the application code, and all dependencies into a single executable with a `prefix/` sidecar for C extensions.

## Layout

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

## Quick Start

```bash
# Start Board Manager Service (gRPC daemon)
./board-manager/board-manager

# Start Arduino Dashboard (Flask :8080)
./arduino-dash/arduino-dash

# Start MedMinder Dashboard (Flask :8081)
./medminder-dash/medminder-dash --port 8081
```

All three support `--help`.

## Building

```bash
# From repo root: build all 3 apps
./scripts/build_standalone.sh

# Build a single app
./scripts/build_standalone.sh arduino-dash

# Via nox
nox -s build_standalone
```

## Documentation

Full documentation is at [`dist-standalone-install/docs/`](../dist-standalone-install/docs/index.md):

| Document | Description |
|----------|-------------|
| [architecture.md](../dist-standalone-install/docs/architecture.md) | PyOxidizer bundling, `prefix/` sidecar, `@REPO_ROOT@` placeholder |
| [api.md](../dist-standalone-install/docs/api.md) | CLI flags reference for all 3 binaries |
| [guide.md](../dist-standalone-install/docs/guide.md) | Building, running, deployment, troubleshooting |
| [tests.md](../dist-standalone-install/docs/tests.md) | Testing methodology and known gaps |

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free
