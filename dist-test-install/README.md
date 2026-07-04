# dist-test-install

Wheel install validation environment for the medminder monorepo.

## What

This directory contains a `Pipfile` that declares all 6 monorepo packages
as local wheel file dependencies plus their PyPI transitive deps.
It is used by `scripts/test_installs.sh` to validate that:

1. All wheels resolve and install together (pip dependency resolution)
2. Every package imports correctly from a clean environment
3. CLI packages (`board-manager`, `arduino-dash`, `medminder-dash`) respond to `--help`

## Usage

```bash
# Manual validation
cd dist-test-install
pipenv sync
pipenv run python -c "import board_manager"  # repeat for all 6
pipenv run board-manager --help
```

Or use the convenience script:

```bash
./scripts/test_installs.sh
```

## How it works

- `Pipfile` lists each monorepo wheel via `{path = "../relative/path/to/wheel.whl"}`
- `pipenv sync` creates/uses a virtualenv and installs everything
- The env is a **build artifact** — recreated from scratch on each CI run
- `.venv/` is gitignored; never commit the virtualenv

## Adding a new monorepo package

1. Add a `{path = ...}` entry to `Pipfile` under `[packages]`
2. Run `pipenv lock` to regenerate `Pipfile.lock`
3. Add the corresponding smoke test entries in `scripts/test_installs.sh`

## Acknowledgements

Assisted-by: OpenCode:minimax-m2.5-free OpenCode:deepseek-v4-flash-free
