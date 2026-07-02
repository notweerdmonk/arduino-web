---
---
# Scripts

Utility scripts for building, testing, and deploying the Arduino Web monorepo.

Full documentation lives in [`scripts/docs/`](../scripts/docs/index.md).

## Quick Links

| Document | Description |
|----------|-------------|
| [scripts/docs/index.md](../scripts/docs/index.md) | Scripts overview and index |
| [scripts/docs/ci.md](../scripts/docs/ci.md) | CI pipeline — `ci.sh` |
| [scripts/docs/build-standalone.md](../scripts/docs/build-standalone.md) | PyOxidizer standalone builds — `build_standalone.sh` |
| [scripts/docs/test-installs.md](../scripts/docs/test-installs.md) | Wheel install validation — `test_installs.sh` |
| [scripts/docs/install-arduino-deps.md](../scripts/docs/install-arduino-deps.md) | Arduino library installer — `install_arduino_deps.sh` |
| [scripts/docs/gen-grpc-bindings.md](../scripts/docs/gen-grpc-bindings.md) | gRPC stub generation — `gen_grpc_bindings.py` |
| [scripts/docs/check-venv.md](../scripts/docs/check-venv.md) | Pipenv venv checker — `check_venv.bash` |
| [scripts/docs/tests.md](../scripts/docs/tests.md) | Scripts test suite (136 tests) |

## Directory

```
scripts/
├── ci.sh                         # CI pipeline runner
├── build_standalone.sh           # Standalone binary builds
├── test_installs.sh              # Wheel install smoke tests
├── install_arduino_deps.sh       # Arduino library installer
├── check_venv.bash               # Recursive pipenv venv checker
├── gen_grpc_bindings.py          # gRPC stub generator
├── pyoxidizer/                   # PyOxidizer build configs
├── tests/                        # 136-test suite
└── docs/                         # Full documentation
```
