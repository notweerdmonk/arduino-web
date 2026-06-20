---
---
# Scripts Test Suite

Tests for the utility scripts under `scripts/tests/`.

## Test Files

| File | Type | Tests | Description |
|------|------|-------|-------------|
| `test_gen_grpc_bindings.py` | pytest | 42 | gRPC stub generation: CLI args, proto sources, venv detection, error paths |
| `test_setup_py.py` | pytest | 52 | setup.py compatibility checks |
| `test_install_arduino_deps.sh` | bash | 12 | Arduino library installer: missing `arduino-cli`, install success/failure |
| `test_ci.sh` | bash | 30 | CI pipeline: skip flags, exit codes, nox invocation |

**Total:** 136 tests (94 pytest + 42 bash)

## Running

### Via nox

```bash
nox -s scripts_tests    # runs all 136 tests
```

### Directly

```bash
cd scripts
pipenv install --dev
pipenv run pytest tests/                              # 94 pytest tests
pipenv run bash tests/test_install_arduino_deps.sh    # 12 bash tests
pipenv run bash tests/test_ci.sh                      # 30 bash tests
```

## Fixtures

`scripts/tests/conftest.py` provides:
- `fake_arduino_cli` — a shell script that simulates `arduino-cli` for testing the installer
- `tmp_pkg_dir` — temporary directory for testing package operations
