#!/usr/bin/env bash
#
# ci.sh — Run the full Phase 56 CI pipeline for the MedMinder monorepo.
#
# Pipeline:
#   1. Run all test suites (scripts/ bash + pytest, plus all 6 per-package
#      pytest suites) via `nox -s all_tests`. Exits 1 on any failure.
#   2. Build all 6 packages via `nox -s all_builds`. Exits 2 on any failure.
#
# Usage:
#   ./scripts/ci.sh              # run full pipeline
#   ./scripts/ci.sh --skip-tests # build only
#   ./scripts/ci.sh --skip-builds # test only
#   ./scripts/ci.sh --help       # show help
#
# Exit codes:
#   0  — pipeline succeeded
#   1  — nox not found on PATH
#   2  — at least one test failed
#   3  — at least one build failed
#   4  — invalid CLI argument
#
# Note: this script does NOT call `install_arduino_deps.sh` — that step
# downloads and installs Arduino libraries (RTClib, TM1637TinyDisplay) and
# is unrelated to the Python test/build pipeline. Run it manually if you
# need to flash the MedMinder sketches to a board.

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO_ROOT"

if ! command -v nox >/dev/null 2>&1; then
    echo "error: 'nox' not found on PATH" >&2
    echo "       install with: pipx install nox" >&2
    echo "       or:         pip install --user nox" >&2
    exit 1
fi

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --skip-tests     Skip the test phase (still run all_builds)
  --skip-builds    Skip the build phase (still run all_tests)
  --help           Show this help and exit

Default: run all_tests then all_builds. Exits non-zero on the first failure.
EOF
}

run_tests=1
run_builds=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-tests)
            run_tests=0
            shift
            ;;
        --skip-builds)
            run_builds=0
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "error: unknown argument: $1" >&2
            usage >&2
            exit 4
            ;;
    esac
done

if [[ $run_tests -eq 1 ]]; then
    echo "==> Phase 1: running all test suites"
    if ! nox -s all_tests; then
        echo "error: at least one test session failed" >&2
        exit 2
    fi
else
    echo "==> Phase 1: skipped (--skip-tests)"
fi

if [[ $run_builds -eq 1 ]]; then
    echo "==> Phase 2: building all packages"
    if ! nox -s all_builds; then
        echo "error: at least one build session failed" >&2
        exit 3
    fi
else
    echo "==> Phase 2: skipped (--skip-builds)"
fi

echo "==> CI pipeline complete"
