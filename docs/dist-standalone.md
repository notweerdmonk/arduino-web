---
---
# Standalone Binaries — dist-standalone

Standalone binary builds for the 3 CLI apps via PyOxidizer.

Full documentation lives in [`dist-standalone-install/docs/`](../dist-standalone-install/docs/index.md).

## Quick Links

| Document | Description |
|----------|-------------|
| [dist-standalone-install/docs/index.md](../dist-standalone-install/docs/index.md) | Binary layout, running requirements |
| [scripts/docs/build-standalone.md](../scripts/docs/build-standalone.md) | Build script reference — `build_standalone.sh` |

## Quick Start

```bash
# Build all 3 apps
./scripts/build_standalone.sh

# Run
dist-standalone/board-manager/board-manager --port 50051
dist-standalone/arduino-dash/arduino-dash
dist-standalone/medminder-dash/medminder-dash
```
