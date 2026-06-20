---
---
# Scripts

Utility scripts for building, testing, and deploying the MedMinder monorepo. Located under `scripts/`.

## Quick Reference

| Script | Purpose |
|--------|---------|
| [`ci.sh`](ci.md) | Full CI pipeline — tests + builds in one command |
| [`build_standalone.sh`](build-standalone.md) | Build standalone binaries via PyOxidizer |
| [`test_installs.sh`](test-installs.md) | Install wheels into clean venv + smoke test |
| [`install_arduino_deps.sh`](install-arduino-deps.md) | Install Arduino libraries for MedMinder sketches |
| [`gen_grpc_bindings.py`](gen-grpc-bindings.md) | Regenerate Python gRPC stubs from proto files |
| [`check_venv.bash`](check-venv.md) | Recursively verify pipenv venvs in the project tree |
| [Tests](tests.md) | Scripts test suite (136 tests) |

Most scripts support `--help` for detailed usage.

## Directory Layout

```
scripts/
├── ci.sh                         # CI pipeline runner
├── build_standalone.sh           # PyOxidizer standalone builds
├── test_installs.sh              # Wheel install smoke tests
├── install_arduino_deps.sh       # Arduino library installer
├── check_venv.bash               # Recursive pipenv venv checker
├── gen_grpc_bindings.py          # gRPC stub generator
├── pyoxidizer/                   # PyOxidizer build configs per app
│   ├── board-manager/pyoxidizer.bzl
│   ├── arduino-dash/pyoxidizer.bzl
│   └── medminder-dash/pyoxidizer.bzl
├── tests/                        # Scripts test suite
│   ├── test_gen_grpc_bindings.py
│   ├── test_setup_py.py
│   ├── test_install_arduino_deps.sh
│   ├── test_ci.sh
│   └── conftest.py
└── docs/                         # This documentation
    ├── index.md
    ├── ci.md
    ├── build-standalone.md
    ├── test-installs.md
    ├── install-arduino-deps.md
    ├── check-venv.md
    ├── gen-grpc-bindings.md
    └── tests.md
```

## Related

- [docs/tests.md](tests.md) — scripts test suite reference
- [dist-test-install/docs/index.md](../dist-test-install/docs/index.md) — wheel install validation environment
- [dist-standalone-install/docs/index.md](../dist-standalone-install/docs/index.md) — standalone binary deployment
- [docs/guide.md  (top-level)](../docs/guide.md) — full user guide
- [docs/api.md (top-level)](../docs/api.md) — API reference
