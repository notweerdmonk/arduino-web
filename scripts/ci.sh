#!/usr/bin/env bash
# @file ci.sh
# @brief Full CI pipeline — lint + builds + tests in one command.
# @description Run lint checks (Phase 0), build all packages via nox -s all_builds
# (Phase 1), then run all test suites via nox -s all_tests (Phase 2). Builds first
# so that dist/ directories exist when per-package tests resolve file://
# dependency sources.
# @option --skip-lint   Skip the lint phase (Phase 0).
# @option --skip-builds Skip the build phase (Phase 1).
# @option --skip-tests  Skip the test phase (Phase 2).
# @option --no-install  Don't prompt to install nox — silently skip nox phases if missing.
# @option --help        Show usage and exit.
# @exitcode 0 Pipeline succeeded.
# @exitcode 1 nox not found on PATH and non-interactive or abort; or pre-check abort.
# @exitcode 2 At least one test session failed.
# @exitcode 3 At least one build session failed.
# @exitcode 4 Invalid CLI argument.
# @exitcode 5 At least one lint check failed.

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Get list of dirty Pipfile.lock files. When FAKE_GIT_DIRTY_LOCK_FILES is
# set (even to empty), its value is used instead of running git — this
# enables controlled testing of the pre-check / post-check prompts without
# requiring actual dirty lock files in the working tree.
_get_dirty_lock_files() {
    if [[ -n "${FAKE_GIT_DIRTY_LOCK_FILES+x}" ]]; then
        printf '%s\n' "$FAKE_GIT_DIRTY_LOCK_FILES"
    else
        git diff --name-only -- '**/Pipfile.lock' 2>/dev/null || true
    fi
}

# scripts/ci.sh
#
# Full CI pipeline — lint + builds + tests in one command.
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

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --skip-lint      Skip the lint phase (Phase 0)
  --skip-builds    Skip the build phase (Phase 1)
  --skip-tests     Skip the test phase (Phase 2)
  --no-install     Don't prompt to install nox; silently skip nox phases if missing
  --help           Show this help and exit

Default: run all phases. Exits non-zero on the first failure.
EOF
}

run_lint=1
run_builds=1
run_tests=1
no_install=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-lint)
            run_lint=0
            shift
            ;;
        --skip-builds)
            run_builds=0
            shift
            ;;
        --skip-tests)
            run_tests=0
            shift
            ;;
        --no-install)
            no_install=1
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

# ---------------------------------------------------------------------------
# Phase 0 — Lint
# ---------------------------------------------------------------------------
if [[ $run_lint -eq 1 ]]; then
    echo "==> Phase 0: running lint checks"
    lint_failed=0

    if ! command -v pipenv >/dev/null 2>&1; then
        echo "error: pipenv not found" >&2
        lint_failed=1
    else
        pipenv run ruff check . || lint_failed=1
        pipenv run ruff format --check . || lint_failed=1
        pipenv run djlint . --check || lint_failed=1
    fi

    if ! command -v npx >/dev/null 2>&1; then
        echo "error: npx not found" >&2
        lint_failed=1
    else
        npx prettier --check "**/*.html" || lint_failed=1
        npx eslint . || lint_failed=1
    fi

    if [[ $lint_failed -eq 1 ]]; then
        echo "error: at least one lint check failed" >&2
        exit 5
    fi
else
    echo "==> Phase 0: skipped (--skip-lint)"
fi

# ---------------------------------------------------------------------------
# Nox check — only if builds or tests will run
# ---------------------------------------------------------------------------
if [[ $run_builds -eq 1 || $run_tests -eq 1 ]]; then
    if ! command -v nox >/dev/null 2>&1; then
        if [[ $no_install -eq 1 ]]; then
            echo "warning: 'nox' not found -- skipping build and test phases (--no-install)" >&2
            run_builds=0
            run_tests=0
        elif (</dev/tty) 2>/dev/null; then
            echo "nox not found on PATH."
            echo "Options:"
            echo "  1) pip install nox          (respects active venv, else global)"
            echo "  2) pipx install nox         (isolated venv via pipx)"
            echo "  3) custom command            (e.g., pipenv install nox, uv tool install nox)"
            echo "  4) skip nox phases           (continue without builds/tests)"
            echo "  0) abort                     (exit 1)"
            printf "Enter choice [0-4]: "
            read -r choice </dev/tty
            case "$choice" in
                1) pip install nox ;;
                2) pipx install nox ;;
                3) printf "Enter command: "; read -r cmd </dev/tty; eval "$cmd" ;;
                4) run_builds=0; run_tests=0 ;;
                0) exit 1 ;;
                *) echo "Invalid choice" >&2; exit 1 ;;
            esac
            if [[ $run_builds -eq 1 || $run_tests -eq 1 ]]; then
                if ! command -v nox >/dev/null 2>&1; then
                    echo "error: 'nox' still not found on PATH after install" >&2
                    exit 1
                fi
            fi
        else
            echo "error: 'nox' not found on PATH" >&2
            echo "       install with: pip install nox" >&2
            echo "       or:         pipx install nox" >&2
            exit 1
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Lock file pre-check — warn if Pipfile.lock files are dirty before nox
# ---------------------------------------------------------------------------
if [[ $run_builds -eq 1 || $run_tests -eq 1 ]]; then
    lock_dirty_pre=$(_get_dirty_lock_files)
    if [[ -n "$lock_dirty_pre" ]]; then
        echo "warning: uncommitted changes in Pipfile.lock files:"
        echo "$lock_dirty_pre"
        echo "The nox build/test phases will call pipenv lock and overwrite these."
        if (</dev/tty) 2>/dev/null; then
            printf "Continue and overwrite? [y/N]: "
            read -r response </dev/tty
            if [[ $response != [yY] ]]; then
                echo "aborting" >&2
                exit 1
            fi
        else
            echo "warning: non-interactive — proceeding will overwrite dirty lock files" >&2
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Phase 1 — Build
# ---------------------------------------------------------------------------
if [[ $run_builds -eq 1 ]]; then
    echo "==> Phase 1: building all packages"
    if ! nox -s all_builds; then
        echo "error: at least one build session failed" >&2
        exit 3
    fi
else
    echo "==> Phase 1: skipped"
fi

# ---------------------------------------------------------------------------
# Phase 2 — Test
# ---------------------------------------------------------------------------
if [[ $run_tests -eq 1 ]]; then
    echo "==> Phase 2: running all test suites"
    if ! nox -s all_tests; then
        echo "error: at least one test session failed" >&2
        exit 2
    fi
else
    echo "==> Phase 2: skipped"
fi

# ---------------------------------------------------------------------------
# Lock file post-check — offer to restore newly-dirtied lock files
# ---------------------------------------------------------------------------
if [[ $run_builds -eq 1 || $run_tests -eq 1 ]]; then
    lock_dirty_post=$(_get_dirty_lock_files)
    # Compute files that are dirty now but were not dirty before
    new_dirty=""
    while IFS= read -r f; do
        if [[ -z "$f" ]]; then continue; fi
        case "$lock_dirty_pre" in
            *"$f"*) ;;
            *) new_dirty="${new_dirty}${f}"$'\n' ;;
        esac
    done <<< "$lock_dirty_post"
    new_dirty="${new_dirty%$'\n'}"
    if [[ -n "$new_dirty" ]]; then
        echo ""
        echo "The following Pipfile.lock files were modified by the CI pipeline:"
        echo "$new_dirty"
        if (</dev/tty) 2>/dev/null; then
            printf "Restore them with git restore? [y/N]: "
            read -r response </dev/tty
            if [[ $response == [yY] ]]; then
                while IFS= read -r f; do
                    if [[ -z "$f" ]]; then continue; fi
                    if [[ ! -v FAKE_GIT_DIRTY_LOCK_FILES ]]; then
                        git restore "$f"
                    fi
                    echo "  restored: $f"
                done <<< "$new_dirty"
            else
                echo "note: Pipfile.lock changes left in working tree"
            fi
        else
            echo "warning: Pipfile.lock files were modified (non-interactive, leaving them dirty)" >&2
        fi
    fi
fi

echo "==> CI pipeline complete"
