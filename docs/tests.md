---
layout: default
---
# Testing Methodology

> **Per-package docs:** For detailed per-module testing, see:
> - [`board_manager/docs/index.md`](../board_manager/python/board_manager/docs/index.md) — board_manager test structure
> - [`arduino_grpc/docs/index.md`](../grpc_client/python/arduino_grpc/docs/index.md) — arduino_grpc test structure
> - [`arduino_dash/docs/index.md`](../arduino_dash/python/arduino_dash/docs/index.md) — arduino_dash test structure
> - [`medminder_dash/docs/index.md`](../medminder_dash/python/medminder_dash/docs/index.md) — medminder_dash test structure

## Framework

All packages use **pytest** as the test runner with standard configuration via `pyproject.toml`.

## Test Categories

### Unit Tests

Unit tests mock external dependencies (gRPC, sockets, subprocesses, pyudev) and test individual components in isolation. They make up the vast majority of the test suite.

**Pattern:** Each module has a corresponding test file using `MagicMock` from `unittest.mock` to isolate the unit under test.

```python
# test_protocol.py
def test_encode_and_frame_newline():
    msg = {"type": "ping"}
    data = encode_and_frame(msg, "newline")
    assert data.endswith(b"\n")
```

### Integration Tests

Integration tests require a running `arduino-cli daemon` and are gated by a `--integration` pytest flag. They test end-to-end message flow through BoardManagerService as a subprocess.

**Location:**
- `board_manager/tests/test_integration.py` — 8 tests (TCP/UDS connect, subscribe, health, publish, unsubscribe, multiple clients, board_cmd_status)
- `arduino_grpc/tests/test_integration.py` — 7 tests (connection, init, list_boards, watch_boards, compile) — 2 skip when no physical board is plugged in

**Invocation:**
```bash
cd board_manager/python/board_manager
pipenv run pytest tests/ --integration
```

Integration tests spawn the full BoardManagerService as a subprocess, connect over TCP or UDS, and verify end-to-end message flow. They are included automatically in `nox -s all_tests` for the `board_manager` package.

### Board-Dependent Tests

Some tests require a physical Arduino board connected via USB:

| Test | Package | Reason |
|------|---------|--------|
| `test_watch_boards_event` | arduino-grpc | Streams board add/remove events from live USB |
| `test_upload` | arduino-grpc | Uploads a compiled sketch to a physical board |

These tests skip gracefully when no board is detected (message: `"No board detected"`). The remaining arduino-grpc tests (connection, init, list_boards, compile) pass with just the daemon running.

## Running Tests

### Per-package (pipenv)

```bash
cd board_manager/python/board_manager          && pipenv run pytest tests/    # 212 tests
cd board_manager_client/python/board_manager_client && pipenv run pytest tests/  # 24 tests
cd arduino_sketch_tools/python/arduino_sketch_tools && pipenv run pytest tests/  # 51 tests
cd arduino_dash/python/arduino_dash             && pipenv run pytest tests/    # 119 tests
cd medminder_dash/python/medminder_dash         && pipenv run pytest tests/    # 186 passed, 1 skipped
cd grpc_client/python/arduino_grpc              && pipenv run pytest tests/    # 35 tests
```

### All packages (nox)

Nox is configured with `reuse_existing_virtualenvs = True` in
`noxfile.py`, so virtualenvs created on the first run are reused
on subsequent runs rather than being deleted and recreated:

```bash
nox -s all_tests          # all 6 packages + scripts (8 sessions)
nox -s scripts_tests      # scripts/tests only (pytest + bash)
nox -s 'tests(board_manager)'  # single package
```

### CI pipeline

```bash
./scripts/ci.sh               # full pipeline (lint → builds → tests)
./scripts/ci.sh --skip-lint     # builds → tests (skip lint)
./scripts/ci.sh --skip-builds   # tests only
./scripts/ci.sh --skip-tests    # builds only
./scripts/ci.sh --no-install    # skip nox phases if nox missing (no prompt)
```

The CI pipeline supports `--skip-lint`, `--skip-builds`, `--skip-tests`, and `--no-install` flags. The `test_ci.sh` script (40 bash assertions) validates flag parsing, error propagation (exit 2 for test failure, exit 3 for build failure, exit 5 for lint failure), the nox-not-found guard, and lint phase success/failure — all using fake nox/pipenv/npx shims with zero external dependencies (Phase 96). Run it standalone: `bash scripts/tests/test_ci.sh`.

### Git Hooks Gate

Two Git hooks integrate the CI pipeline into your local workflow (enable with `git config core.hooksPath .githooks`):

| Hook | Gate | Skip | Notes |
|------|------|------|-------|
| Pre-commit | Optional lint checks (ruff, prettier, eslint, djlint) | `git commit --no-verify` or press `n` at prompt | djlint runs `--check` only; auto-fix with `pipenv run djlint . --reformat` |
| Pre-push | `scripts/ci.sh` — full lint + build + test | `git push --no-verify` | ~15-25 min; catches failures before upstream CI |

### Expected Results

| Session | Tests | Notes |
|---------|-------|-------|
| `scripts_tests` | **212 passed** (160 pytest + 12 bash + **40 bash**) | pytest + `test_install_arduino_deps.sh` + `test_ci.sh` |
| `all_tests` | **8/8 sessions** | all packages + scripts |
| `tests(board_manager)` | 212 passed | includes integration tests |
| `tests(board_manager_client)` | 24 passed | |
| `tests(arduino_sketch_tools)` | 51 passed | |
| `tests(arduino_dash)` | 119 passed | |
| `tests(arduino_grpc)` | 33 passed, 2 skipped | board-dependent (watch, upload) |
| `tests(medminder_dash)` | 186 passed, 1 skipped | route change (admin URL query) |

## Test Coverage Areas

### board_manager (13 test files)

| Module | Test File | Area |
|--------|-----------|------|
| `protocol.py` | `test_protocol.py` | Framing modes, handshake, encode/decode |
| `router.py` | `test_router.py` | Subscribe/unsubscribe, wildcard matching, patterns |
| `service.py` | `test_service.py` | Client lifecycle, message handling, routing, daemon state |
| `pool.py` | `test_pool.py` | Spawn, dispatch, poll, restart limits, cleanup |
| `boot.py` | `test_boot.py` | Env config, start/stop/wait |
| `config.py` | `test_config.py` | TOML/env/CLI priority, defaults |
| `board_detector.py` | `test_board_detector.py` | Watch/poll modes, events, auto-recovery |
| `board_worker.py` | `test_board_worker.py` | Worker IPC, message dispatch |
| `daemon_manager.py` | `test_daemon_manager.py` | Daemon lifecycle, health check, recovery |
| `udev_monitor.py` | `test_udev_monitor.py` | Hotplug events, device filtering, resolve info |
| integration | `test_integration.py` | End-to-end BMS as subprocess |

### board_manager_client (1 test file)

| Module | Test File | Area |
|--------|-----------|------|
| `pubsub_client.py` | `test_pubsub_client.py` | Connect, subscribe, publish, reconnect, timeouts |

### arduino_sketch_tools (1 test file)

| Module | Test File | Area |
|--------|-----------|------|
| `extension.py` | `test_extension.py` | Flask integration, blueprint routes, compile/upload state |

### arduino_grpc (2 test files)

| Module | Test File | Area |
|--------|-----------|------|
| `client.py` | `test_client.py` | gRPC methods, error handling, context manager |
| integration | `test_integration.py` | Live daemon: connection, init, list, compile, upload |

### arduino_dash (2 test files)

| Module | Test File | Area |
|--------|-----------|------|
| `app.py` | `test_app.py` | Flask app factory, secret key, extensions |
| `gunicorn_conf.py` | `test_gunicorn_conf.py` | BMS lifecycle hooks, env var config |

### medminder_dash (12 test files)

| Module | Test File | Area |
|--------|-----------|------|
| `api_routes.py` | `test_api_medicines.py` | Medicine CRUD, validation |
| `html_routes.py` | `test_admin.py` | Admin pages, board selector |
| `html_routes.py` | `test_routes.py` | Board routes, connection status, sketch path |
| `pubsub.py` | `test_pubsub.py` | Hardware ID flow, port info |
| `sketch_gen.py` | `test_sketch_gen.py` | alarm.hpp generation/parsing |
| `sketch_registry.py` | `test_sketch_registry.py` | Assignment CRUD |
| `sketch_management.py` | `test_e2e_sketch.py` | End-to-end sketch upload flow |
| `utils.py` | `test_bootstrap.py` | Port normalization, config resolution |
| `app.py` | `test_deploy.py` | Deploy flow, sketch_dir.json |
| `html_routes.py` | `test_board_isolation.py` | Board-scoped medicine isolation |

## Testing Conventions

1. **Mock at the import level** — use `@patch("module.path.ClassName")` rather than `@patch("ClassName")` to mock the reference as seen by the module under test.
2. **Fixture pattern** — use `@pytest.fixture` for shared setup (e.g., `mock_service` creates a pre-configured `BoardManagerService`).
3. **Integration tests** — require a `--integration` flag to avoid false negatives in environments without `arduino-cli`.
4. **Board-dependent tests** — skip with `pytest.skip("No board detected")` when no USB Arduino is found.
5. **Cleanup** — all tests clean up mocks and state (`_known_ports`, `_known_boards`, etc.) to avoid cross-test pollution.
6. **Edge cases** — cover empty topic, duplicate add, remove unknown, timeout, connection error, malformed data.

## Code Quality

Four tools enforce code style across the monorepo. All commands run from the project root.

### ruff (Python)

Ruff lints and formats all Python source. Uses the root `pipenv` venv:

```bash
pipenv run ruff check .       # lint (select E, F, I, W)
pipenv run ruff check --fix . # auto-fix sortable/removable issues
pipenv run ruff format .      # format (112 files, 0 diffs when clean)
```

Config is in `pyproject.toml` under `[tool.ruff]`. Lint rule selection lives under `[tool.ruff.lint]`. Generated protobuf stubs (`cc/arduino/cli/commands/v1/`) are excluded.

### djlint (Jinja2 templates)

Djlint checks HTML/Jinja2 template formatting across all 50 source
templates (25 medminder_dash, 15 arduino_dash, 10 arduino_sketch_tools).
Generated HTML output (`_site/`, `docs/reference/`, etc.) is excluded
via `extend_exclude` in `pyproject.toml`. Uses the root `pipenv` venv:

```bash
pipenv run djlint . --check      # check formatting (exit 0 = clean)
pipenv run djlint . --reformat   # auto-fix formatting
```

### prettier (non-Jinja HTML)

Prettier formats inline JavaScript in HTML files that don't contain Jinja2 syntax. Requires Node.js:

```bash
npx prettier --check "**/*.html"   # check formatting
npx prettier --write "**/*.html"  # auto-format
```

Config is in `.prettierrc` — double quotes, semicolons, 2-space indent, es5 trailing commas. All Jinja2 templates (`**/templates/`) are excluded from prettier via `.prettierignore` — djlint is the authoritative formatter for Jinja2 HTML.

### ESLint (JavaScript linting)

ESLint enforces JS best practices and prettier formatting rules via `eslint-plugin-prettier`:

```bash
npx eslint .            # check (includes prettier/prettier errors)
npx eslint . --fix      # auto-fix (prettier + JS corrections)
```

Config is in `config/eslint.config.mjs`. See `agent-docs/CODEBASE_REFERENCE.md` for known edge cases (two `base.html` files under `**/templates/` — excluded from standalone prettier, eslint-plugin-prettier may still trigger on long-line wrapping within `npx eslint .`).

## Related Documentation

| Document | Description |
|----------|-------------|
| [`scripts/docs/tests.md`](../scripts/docs/tests.md) | Scripts test suite (136 tests for gRPC stub generation, installers, CI pipeline) |
| [`e2e/`](../e2e/index.md) | E2E browser testing with Playwright MCP (mock servers, scenario recipes) — [`README.md`](../e2e/README.md) |
