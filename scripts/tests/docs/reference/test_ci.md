# test_ci.sh

Tests for the `ci.sh` script — validates flag parsing, error handling, nox shim integration, lint phase, and lock file handling.

## Overview

49 bash assertions covering: `--help`, unknown flags, nox-missing handling, `--skip-lint`, `--skip-builds` (runs all_tests), `--skip-tests` (runs all_builds), both flags (skips all nox calls), test failure propagation (exit 2), build failure propagation (exit 3), lint success (exit 0), lint failure (exit 5), `--no-install` (silently falls through), and lock file pre-check/post-check (3 scenarios).

Uses fake `nox`, `pipenv`, `npx`, and `git` shims in temp dirs — zero external dependencies beyond bash. The fake `git` shim uses a counter-based state machine (`FAKE_GIT_COUNT_FILE`) to return different output for pre-check (call 0 → FAKE_GIT_PRE_DIRTY) and post-check (call 1 → FAKE_GIT_POST_DIRTY), enabling control of both sides of the lock file handling flow.

## Usage

```bash
# Standalone
bash scripts/tests/test_ci.sh

# Via nox (as part of scripts_tests)
nox -s scripts_tests
```

## Integration

The pre-push Git hook runs `scripts/ci.sh` (not `test_ci.sh`). `test_ci.sh` is a developer tool to verify `ci.sh` changes without touching real nox sessions.
