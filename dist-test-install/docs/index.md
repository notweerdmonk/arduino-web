# dist-test-install — Wheel Install Validation Environment

Validation environment for testing that all monorepo wheels resolve, install, and import correctly in a clean venv.

## Purpose

Validate that:
1. All 6 wheels resolve and install together (pip dependency resolution)
2. Every package imports correctly from a clean environment
3. CLI packages (`board-manager`, `arduino-dash`, `medminder-dash`) respond to `--help`

## Usage

```bash
cd dist-test-install
pipenv sync
pipenv run python -c "import board_manager"
pipenv run board-manager --help
```

Or via the convenience script:

```bash
./scripts/test_installs.sh
```

## How It Works

- `Pipfile` lists each monorepo wheel as a `{path = "../relative/path/to/wheel.whl"}` dependency
- `pipenv sync` creates/uses a virtualenv and installs everything
- The environment is a **build artifact** — recreated from scratch on each CI run
- `.venv/` is gitignored; never commit the virtualenv

## Directory Layout

```
dist-test-install/
├── Pipfile              # Wheel path dependencies
├── Pipfile.lock         # Locked dependency tree
├── README.md            # Quick instructions
└── docs/
    └── index.md         # This file
```

## Adding a New Package

1. Build the wheel: `nox -s 'build(<pkg>)'`
2. Add a `{path = ...}` entry to `Pipfile` under `[packages]`
3. Run `pipenv lock` to regenerate `Pipfile.lock`
4. Add smoke test entries in `scripts/test_installs.sh`

## Smoked Packages

| Package | Import | CLI |
|---------|--------|-----|
| `board-manager` | ✅ | ✅ |
| `board-manager-client` | ✅ | — |
| `arduino-sketch-tools` | ✅ | — |
| `arduino-grpc` | ✅ | — |
| `arduino-dash` | ✅ | ✅ |
| `medminder-dash` | ✅ | ✅ |

## Related

- [scripts/docs/test-installs.md](../scripts/docs/test-installs.md) — smoke test script
- [scripts/docs/tests.md](../scripts/docs/tests.md) — scripts test suite
