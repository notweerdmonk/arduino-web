#!/usr/bin/env bash
# @file test_installs.sh
# @brief Install monorepo wheels and run smoke tests.
# @description Create a clean pipenv venv, sync all 6 monorepo wheels
# from Pipfile, and run import + --help smoke tests on each package.
# @option --dry-run        Print what would be done without making changes.
# @option --skip-install   Skip pipenv sync, re-run smoke tests only.
# @option --help           Show usage and exit.
# @env TEST_INSTALLS_DIR  Working directory (default: dist-test-install).
# @env PIP_INDEX_URL      Passed through to pipenv (default: pypi.org).
# @exitcode 0 All smoke tests passed.
# @exitcode 1 pipenv not found or Pipfile missing.
# @exitcode 2 One or more wheels missing (run nox -s all_builds).
# @exitcode 3 One or more smoke tests failed.
# @exitcode 4 Invalid CLI argument.

# scripts/test_installs.sh
#
# Install wheels into clean venv + smoke test.
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

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# ---------------------------------------------------------------------------
# Overridable paths
# ---------------------------------------------------------------------------
TEST_INSTALLS_DIR="${TEST_INSTALLS_DIR:-${REPO_ROOT}/dist-test-install}"

# ---------------------------------------------------------------------------
# Monorepo wheel paths (6 packages). Used only for prerequisite checking —
# actual installation is driven by Pipfile via pipenv.
# ---------------------------------------------------------------------------
readonly WHEELS=(
    "${REPO_ROOT}/board_manager/python/board_manager/dist/board-manager/board_manager-0.1.0-py3-none-any.whl"
    "${REPO_ROOT}/board_manager_client/python/board_manager_client/dist/board-manager-client/board_manager_client-0.1.0-py3-none-any.whl"
    "${REPO_ROOT}/arduino_sketch_tools/python/arduino_sketch_tools/dist/arduino-sketch-tools/arduino_sketch_tools-0.1.0-py3-none-any.whl"
    "${REPO_ROOT}/grpc_client/python/arduino_grpc/dist/arduino-grpc/arduino_grpc-0.1.0-py3-none-any.whl"
    "${REPO_ROOT}/arduino_dash/python/arduino_dash/dist/arduino-dash/arduino_dash-0.1.0-py3-none-any.whl"
    "${REPO_ROOT}/medminder_dash/python/medminder_dash/dist/medminder-dash/medminder_dash-0.1.0-py3-none-any.whl"
)

# ---------------------------------------------------------------------------
# Package smoke tests
# ---------------------------------------------------------------------------
# Each entry:  <pypi_name>  <import_name>  <has_cli>
SMOKE_TESTS=(
    "board-manager       board_manager       yes"
    "board-manager-client board_manager_client no"
    "arduino-sketch-tools arduino_sketch_tools no"
    "arduino-grpc         arduino_grpc        no"
    "arduino-dash         arduino_dash        yes"
    "medminder-dash       medminder_dash      yes"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { printf '[%s] %s\n' "${SCRIPT_NAME}" "$*"; }
die()  { printf '[%s] ERROR: %s\n' "${SCRIPT_NAME}" "$*" >&2; exit "${2:-1}"; }

usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS]

Create a reproducible venv via pipenv, install all monorepo wheels from
Pipfile, and run smoke tests (import + --help) on each package.

Options:
  --dry-run        Print what would be done without making changes
  --skip-install   Skip pipenv sync (re-run smoke tests only)
  --help           Show this help and exit

Environment:
  TEST_INSTALLS_DIR  Working directory (default: <repo-root>/test_installs)
  PIP_INDEX_URL      Passed through to pipenv (default: pypi.org)
EOF
}

check_prerequisites() {
    if ! command -v pipenv >/dev/null 2>&1; then
        cat >&2 <<EOF
pipenv is required but not found on PATH.

Install pipenv:
  pip install --user pipenv
  (or use your system package manager)

Or activate a pipx/shiv environment that provides pipenv.
EOF
        exit 1
    fi

    if [[ ! -f "${TEST_INSTALLS_DIR}/Pipfile" ]]; then
        die "Pipfile not found: ${TEST_INSTALLS_DIR}/Pipfile" 1
    fi

    for w in "${WHEELS[@]}"; do
        if [[ ! -f "$w" ]]; then
            die "wheel not found: ${w}"$'\n'"       Run: nox -s all_builds" 2
        fi
    done
}

install_wheels() {
    local dry_run="$1"
    log "Syncing monorepo wheels via pipenv"
    if [[ "${dry_run}" -eq 1 ]]; then
        log "  (dry-run) PIPENV_PIPFILE=${TEST_INSTALLS_DIR}/Pipfile pipenv sync"
        return 0
    fi
    PIPENV_PIPFILE="${TEST_INSTALLS_DIR}/Pipfile" pipenv sync
    log "All wheels installed via pipenv sync"
}

check_installed_packages() {
    local dry_run="$1"
    log "Verifying installed packages"
    if [[ "${dry_run}" -eq 1 ]]; then
        log "  (dry-run) PIPENV_PIPFILE=${TEST_INSTALLS_DIR}/Pipfile pipenv run pip list --format=columns"
        return 0
    fi
    PIPENV_PIPFILE="${TEST_INSTALLS_DIR}/Pipfile" pipenv run pip list --format=columns \
        | grep -E "board-manager|arduino|medminder" || true
}

# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

run_smoke_tests() {
    local dry_run="$1"
    local failed=0
    local passed=0

    log "Running smoke tests (${#SMOKE_TESTS[@]} packages)"

    while IFS=' ' read -r pip_name import_name has_cli; do
        [[ -z "${pip_name}" ]] && continue

        # ---- import test ----
        if [[ "${dry_run}" -eq 1 ]]; then
            log "  (dry-run) [${pip_name}] python -c 'import ${import_name}'"
            passed=$((passed + 1))
            continue
        fi

        if PIPENV_PIPFILE="${TEST_INSTALLS_DIR}/Pipfile" \
            pipenv run python -c "import ${import_name}" 2>/dev/null; then
            log "  PASS  [${pip_name}] import ${import_name}"
            passed=$((passed + 1))
        else
            log "  FAIL  [${pip_name}] import ${import_name}"
            failed=$((failed + 1))
            continue
        fi

        # ---- CLI --help test ----
        if [[ "${has_cli}" == "yes" ]]; then
            if PIPENV_PIPFILE="${TEST_INSTALLS_DIR}/Pipfile" \
                pipenv run python -m "${import_name}" --help >/dev/null 2>&1; then
                log "  PASS  [${pip_name}] --help"
            else
                # Fallback: try as console_script entry point
                if PIPENV_PIPFILE="${TEST_INSTALLS_DIR}/Pipfile" \
                    pipenv run "${pip_name}" --help >/dev/null 2>&1; then
                    log "  PASS  [${pip_name}] --help (entry point)"
                else
                    log "  FAIL  [${pip_name}] --help"
                    failed=$((failed + 1))
                fi
            fi
        fi
    done < <(printf '%s\n' "${SMOKE_TESTS[@]}")

    echo
    log "Smoke test results: ${passed} passed, ${failed} failed"

    return "${failed}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    local dry_run=0
    local skip_install=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                dry_run=1
                shift
                ;;
            --skip-install)
                skip_install=1
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

    echo "==> test_installs.sh"
    echo "    TEST_INSTALLS_DIR = ${TEST_INSTALLS_DIR}"
    echo "    Dry run           = $([ "${dry_run}" -eq 1 ] && echo yes || echo no)"
    echo "    Skip install      = $([ "${skip_install}" -eq 1 ] && echo yes || echo no)"
    echo

    if [[ "${dry_run}" -eq 0 ]]; then
        check_prerequisites
    fi

    if [[ "${skip_install}" -eq 0 ]]; then
        install_wheels "${dry_run}"

        if [[ "${dry_run}" -eq 0 ]]; then
            check_installed_packages "${dry_run}"
        fi
    else
        log "Skipping pipenv sync (--skip-install)"
        if [[ "${dry_run}" -eq 0 ]]; then
            check_prerequisites
        fi
    fi

    echo
    run_smoke_tests "${dry_run}"
    local smoke_exit=$?

    echo
    if [[ "${smoke_exit}" -eq 0 ]]; then
        if [[ "${dry_run}" -eq 1 ]]; then
            log "Dry-run complete (no changes made)"
        else
            log "All smoke tests passed"
        fi
        exit 0
    else
        die "${smoke_exit} smoke test(s) failed" 3
    fi
}

main "$@"

