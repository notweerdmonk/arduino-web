# AGENTS.md

## Repository structure

Monorepo with 6 Python packages. No root `medminder/` namespace package.

| Package | Directory | Console script | Entry point |
|---------|-----------|----------------|-------------|
| `arduino-grpc` | `grpc_client/python/arduino_grpc/` | — | `ArduinoGrpcClient` |
| `board-manager` | `board_manager/python/board_manager/` | `board-manager` | `board_manager.__main__:main` |
| `board-manager-client` | `board_manager_client/python/board_manager_client/` | — | `PubSubClient` |
| `arduino-sketch-tools` | `arduino_sketch_tools/python/arduino_sketch_tools/` | — | Flask extension |
| `arduino-dash` | `arduino_dash/python/arduino_dash/` | `arduino-dash` | Flask app |
| `medminder-dash` | `medminder_dash/python/medminder_dash/` | `medminder-dash` | Flask app |

Generated gRPC stubs live in `arduino_grpc/cc/` — excluded from ruff.

Shared scripts at `scripts/`: CI pipeline, PyOxidizer builds, install validation, gRPC stub generation.

**Architecture**: `arduino-cli daemon :50051` ↔ `BoardManagerService :9090 + UDS` ↔ `Flask app :8080` (pub/sub over TCP+UDS, no polling).

## Dependency and environment model

**Dual venv**: root `pipenv` (linting, docs, dev tools) + per-package `pipenv` (runtime deps). Nox orchestrates all test/build sessions.

Root `Pipfile` sources monorepo wheels from local `dist/` dirs via `file://${PROJECT_ROOT}/...` extra indexes. Per-package `Pipfile`s also reference sibling packages from their `dist/`.

After `pipenv install`, run `pipenv run pip install -e ./python/` once for editable dev mode (re-apply after new packages added).

All packages publish a `__version__` attribute in their `__init__.py` (currently `"0.1.0"`). Root `VERSION` file mirrors it.

## Commands

### Lint / format (root pipenv)

```
pipenv run ruff check .
pipenv run ruff format .
pipenv run djlint . --check
pipenv run djlint . --reformat
npx prettier --check "**/*.html"
npx prettier --write "**/*.html"
npx eslint .
npx eslint . --fix
```

### Test

```
nox -s all_tests                          # all 8 sessions (~830 tests)
nox -s 'tests(board_manager)'             # single package
nox -s scripts_tests                      # scripts suite (170 tests)
```

Per-package directly: `cd <pkg>/python/<pkg> && pipenv run pytest tests/`

**Integration tests** gated by `--integration` flag (requires `arduino-cli daemon`).
**Board-dependent tests** skip with `pytest.skip("No board detected")`.
Mock at import level: `@patch("module.path.ClassName")`.

### Build

```
./scripts/ci.sh                           # builds → tests (flags: --skip-builds, --skip-tests)
nox -s all_builds all_tests               # build then test all 6 packages
nox -s 'build(board_manager)'             # single package
nox -s test_installs                      # wheel install smoke tests
```

### Docs

```
bundle exec jekyll build                  # builds _site/ (~255 pages)
```

### gRPC regeneration

```
pipenv run python scripts/gen_grpc_bindings.py
```

### Git hooks

Pre-commit and pre-push hooks live in `.githooks/` (version-controlled). Enable with:

```
git config core.hooksPath .githooks
```

- **`pre-commit`**: Optional lint/format checks with `[Y/n]` prompt (10s timeout, default Y). Runs ruff check, ruff format --check, prettier --check, eslint, djlint --check. Skip with `n` or `git commit --no-verify`.
- **`pre-push`**: Mandatory — runs `scripts/ci.sh` (full `nox -s all_builds` + `all_tests`, ~15-25 min). Skip with `git push --no-verify`.

### Version query

```python
pipenv run python -c "import medminder_dash; print(medminder_dash.__version__)"
```

## OpenCode workflow conventions

This project follows a structured 4-phase cycle: **RESEARCH → IMPLEMENTATION → TESTING → REVIEW**. Each phase uses prefixed workflow documents in the project root:

- `RESEARCH_*` — planning, exploration
- `IMPLEMENTATION_*` — coding, architecture
- `TESTING_*` — verification
- `REVIEW_*` — code/document review

The master plan is at `PLAN.md` (append-only). `JOURNAL.md` is the append-only log. `CODEBASE_REFERENCE.md` stores code snippets and declarations with line numbers.

**Commit style**: past tense, non-imperative, 50/72 rule, categorized paragraphs, `Assisted-by` and `Signed-off-by` tags.

**Timestamping**: all log/plan entries prefixed with `YYYY-MM-DD HH:MM` via `date +"%Y-%m-%d %H:%M"`.

**README.md is GitHub-facing** — not processed by Jekyll. Root `index.md` is the Jekyll documentation hub.
