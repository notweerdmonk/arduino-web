# Scripts

Utility scripts for building, testing, and deploying the medminder monorepo.

## Build Standalone Binaries

```bash
# Build all 3 apps (output: .tar.gz archives)
./scripts/build_standalone.sh

# Build a single app
./scripts/build_standalone.sh board-manager

# Package as .zip instead of .tar.gz
./scripts/build_standalone.sh --zip

# Dry-run
./scripts/build_standalone.sh --dry-run

# Via nox
nox -s build_standalone
nox -s build_standalone -- board-manager
```

Output goes to `dist-standalone/<app>/` (binary + `prefix/` sidecar) plus `<app>.tar.gz` (or `<app>.zip` with `--zip`).

### Requirements

- [PyOxidizer](https://pyoxidizer.readthedocs.io/) — `pipx install pyoxidizer`
- Python 3.10 (bundled by PyOxidizer)
- All 6 monorepo wheels built (`nox -s all_builds`)

### Binary Layout

```
dist-standalone/<app>/
  <binary>          # ~51 MB standalone binary
  prefix/           # ~100 MB filesystem-relative sidecar (C extensions)
```

## Run a Standalone Binary

```bash
# Board manager (needs a port)
dist-standalone/board-manager/board-manager --port 50051

# Arduino dashboard
dist-standalone/arduino-dash/arduino-dash

# Medminder dashboard
dist-standalone/medminder-dash/medminder-dash
```

`--help` is available on all three.

## Test Wheel Installation

```bash
./scripts/test_installs.sh
```

Installs all 6 monorepo wheels into a pipenv-managed venv and runs
import + CLI smoke tests. See `../dist-test-install/README.md` for details.

## CI Pipeline

```bash
./scripts/ci.sh                         # builds → tests
./scripts/ci.sh --skip-tests            # builds only
./scripts/ci.sh --skip-builds           # tests only
```

Or via nox:

```bash
nox -s all_tests
nox -s all_builds
```

## Check Pipenv Virtual Environments

```bash
# Verify all pipenv venvs in the project tree
./scripts/check_venv.bash .

# Check specific directories
./scripts/check_venv.bash board_manager
```

Recursively walks directories and runs `pipenv --venv` in each. Exits non-zero if any venv is missing or broken.

## Build Wheels

```bash
nox -s all_builds
```

Each package's wheel lands in `<pkg>/python/<pkg>/dist/<pip-name>/<wheel>.whl`.

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free
