---
---

# Standalone Binaries — dist-standalone

Standalone binary builds for the 3 CLI apps via PyOxidizer. Each binary bundles the Python interpreter, the application code, and all dependencies into a single executable (with a `prefix/` sidecar for C extensions).

## Quick Links

| Document | Description |
|----------|-------------|
| [dist-standalone-install/docs/index.md](../dist-standalone-install/docs/index.md) | Overview, quick start, bundle layout |
| [dist-standalone-install/docs/architecture.md](../dist-standalone-install/docs/architecture.md) | PyOxidizer bundling, `prefix/` sidecar, `@REPO_ROOT@` placeholder |
| [dist-standalone-install/docs/api.md](../dist-standalone-install/docs/api.md) | CLI flags reference for all 3 binaries |
| [dist-standalone-install/docs/guide.md](../dist-standalone-install/docs/guide.md) | Building, running, deployment, troubleshooting |
| [dist-standalone-install/docs/tests.md](../dist-standalone-install/docs/tests.md) | Testing methodology and known gaps |
| [scripts/docs/build-standalone.md](../scripts/docs/build-standalone.md) | Build script reference (`build_standalone.sh`) |

## Quick Start

```bash
# Build all 3 apps (requires PyOxidizer + pre-built wheels)
./scripts/build_standalone.sh

# Run Board Manager Service
dist-standalone/board-manager/board-manager

# Run Arduino Dashboard (Flask :8080)
dist-standalone/arduino-dash/arduino-dash

# Run MedMinder Dashboard (Flask :8080)
dist-standalone/medminder-dash/medminder-dash
```
