# ci.sh

Full CI pipeline — lint + builds + tests in one command.

## Overview

Run lint checks (Phase 0), build all packages via nox -s all_builds (creates
dist/ wheels), then run all test suites via nox -s all_tests (Phase 2). Builds
first so that dist/ directories exist when per-package tests resolve file://
dependency sources.

## Options

| Flag | Description |
|------|-------------|
| `--skip-lint` | Skip the lint phase (Phase 0) |
| `--skip-builds` | Skip the build phase (Phase 1) |
| `--skip-tests` | Skip the test phase (Phase 2) |
| `--no-install` | Don't prompt to install nox; silently skip nox phases if missing |
| `--help` | Show usage and exit |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Pipeline succeeded |
| 1 | nox not found on PATH and non-interactive, or user aborted |
| 2 | At least one test session failed |
| 3 | At least one build session failed |
| 4 | Invalid CLI argument |
| 5 | At least one lint check failed |
