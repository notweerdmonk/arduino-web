# test_ci.sh

Tests for the `ci.sh` script — validates flag parsing, error handling, and nox shim integration.

## Overview

30 bash assertions covering: `--help`, unknown flags, nox-missing handling, `--skip-builds` (runs all_tests), `--skip-tests` (runs all_builds), both flags (skips all nox calls), test failure propagation (exit 2), build failure propagation (exit 3).

Uses a fake `nox` shim in a temp dir — zero external dependencies beyond bash.

## Usage

```bash
# Standalone
bash scripts/tests/test_ci.sh

# Via nox (as part of scripts_tests)
nox -s scripts_tests
```

## Integration

The pre-push Git hook runs `scripts/ci.sh` (not `test_ci.sh`). `test_ci.sh` is a developer tool to verify `ci.sh` changes without touching real nox sessions.
