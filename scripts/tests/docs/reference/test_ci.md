# test_ci.sh

Tests for the `ci.sh` script — validates flag parsing, error handling, nox shim integration, and lint phase.

## Overview

40 bash assertions covering: `--help`, unknown flags, nox-missing handling, `--skip-lint`, `--skip-builds` (runs all_tests), `--skip-tests` (runs all_builds), both flags (skips all nox calls), test failure propagation (exit 2), build failure propagation (exit 3), lint success (exit 0), lint failure (exit 5), and `--no-install` (silently falls through).

Uses fake `nox`, `pipenv`, and `npx` shims in temp dirs — zero external dependencies beyond bash.

## Usage

```bash
# Standalone
bash scripts/tests/test_ci.sh

# Via nox (as part of scripts_tests)
nox -s scripts_tests
```

## Integration

The pre-push Git hook runs `scripts/ci.sh` (not `test_ci.sh`). `test_ci.sh` is a developer tool to verify `ci.sh` changes without touching real nox sessions.
