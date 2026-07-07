#!/usr/bin/env bash
# @file ci.sh
# @brief Full CI pipeline — builds + tests in one command.
# @description Build all packages via nox -s all_builds (creates dist/ wheels),
# then run all test suites via nox -s all_tests. Builds first so that dist/
# directories exist when per-package tests resolve file:// dependency sources.
# @option --skip-builds Skip the build phase, test only.
# @option --skip-tests  Skip the test phase, build only.
# @option --help        Show usage and exit.
# @exitcode 0 Pipeline succeeded.
# @exitcode 1 nox not found on PATH.
# @exitcode 2 At least one test session failed.
# @exitcode 3 At least one build session failed.
# @exitcode 4 Invalid CLI argument.

# scripts/ci.sh
#
# Full CI pipeline — builds + tests in one command.
#
# Author: notweerdmonk
# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2026 notweerdmonk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPO_ROOT

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
  --skip-builds    Skip the build phase (still run all_tests)
  --skip-tests     Skip the test phase (still run all_builds)
  --help           Show this help and exit

Default: run all_builds then all_tests. Exits non-zero on the first failure.
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

if [[ $run_builds -eq 1 ]]; then
    echo "==> Phase 1: building all packages"
    if ! nox -s all_builds; then
        echo "error: at least one build session failed" >&2
        exit 3
    fi
else
    echo "==> Phase 1: skipped (--skip-builds)"
fi

if [[ $run_tests -eq 1 ]]; then
    echo "==> Phase 2: running all test suites"
    if ! nox -s all_tests; then
        echo "error: at least one test session failed" >&2
        exit 2
    fi
else
    echo "==> Phase 2: skipped (--skip-tests)"
fi

echo "==> CI pipeline complete"

