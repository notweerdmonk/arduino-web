#!/usr/bin/env bash
# @file test_ci.sh
# @brief Tests for the ci.sh script.
# @description Verify --help, unknown flags, nox-missing handling,
# --skip-lint, --skip-builds, --skip-tests, both flags, test failure
# propagation, build failure propagation, lint success/failure,
# --no-install flag.

# scripts/tests/test_ci.sh
#
# Tests for the ci.sh script.
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

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../ci.sh"

PASS=0
FAIL=0

# Pre-declare for shellcheck; assigned by run_script via printf -v nameref
out_stdout=""
out_stderr=""
out_code=""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

assert_eq() {
    local label="$1"
    local expected="$2"
    local actual="$3"
    if [[ "${expected}" == "${actual}" ]]; then
        printf '  PASS  %s\n' "${label}"
        PASS=$((PASS + 1))
    else
        printf '  FAIL  %s\n' "${label}"
        printf '        expected: %q\n' "${expected}"
        printf '        actual:   %q\n' "${actual}"
        FAIL=$((FAIL + 1))
    fi
}

assert_contains() {
    local label="$1"
    local haystack="$2"
    local needle="$3"
    if [[ "${haystack}" == *"${needle}"* ]]; then
        printf '  PASS  %s\n' "${label}"
        PASS=$((PASS + 1))
    else
        printf '  FAIL  %s\n' "${label}"
        printf '        needle:    %q\n' "${needle}"
        printf '        haystack:  %q\n' "${haystack}"
        FAIL=$((FAIL + 1))
    fi
}

# Make a private temp dir with a fake `nox` shim. The shim records every
# invocation (one line per call) into a log file, exits 0, and prints a
# marker. Echoes the temp dir path.
#
# The shim's exit code can be controlled via the env var FAKE_NOX_RC
# (default 0). To simulate a test failure, set FAKE_NOX_RC=2 before
# calling the script under test.
make_fake_nox() {
    local tmpdir
    tmpdir="$(mktemp -d -t nox-shim.XXXXXX)"
    cat >"${tmpdir}/nox" <<'SHIM'
#!/bin/sh
# Fake nox for testing. Records invocations and exits FAKE_NOX_RC (default 0).
echo "$@" >>"${FAKE_NOX_LOG:-/dev/null}"
echo "FAKE_NOX_RAN $@"
exit "${FAKE_NOX_RC:-0}"
SHIM
    chmod +x "${tmpdir}/nox"
    printf '%s' "${tmpdir}"
}

# Make a private temp dir with fake `pipenv` and `npx` shims for testing
# the lint phase. Each shim's exit code is controlled via environment
# variables (default 0). Echoes the temp dir path.
make_fake_lint_tools() {
    local tmpdir
    tmpdir="$(mktemp -d -t lint-shim.XXXXXX)"

    cat >"${tmpdir}/pipenv" <<'SHIM'
#!/bin/sh
# Fake pipenv for testing. Exits FAKE_PIPENV_RC (default 0).
exit "${FAKE_PIPENV_RC:-0}"
SHIM
    chmod +x "${tmpdir}/pipenv"

    cat >"${tmpdir}/npx" <<'SHIM'
#!/bin/sh
# Fake npx for testing. Exits FAKE_NPX_RC (default 0).
exit "${FAKE_NPX_RC:-0}"
SHIM
    chmod +x "${tmpdir}/npx"

    printf '%s' "${tmpdir}"
}

# Run the script under test, capturing stdout, stderr, and exit code.
# Usage: run_script <stdout_var> <stderr_var> <code_var> [stdin_var] [tty_var] [args...]
#
# Positional parameters after code_var:
#   stdin_var  — optional: text piped to the child's stdin. Omit or pass ""
#                if not needed.
#   tty_var    — optional: text fed to the child's /dev/tty via script(1)
#                (creates a pty). Omit or pass "" if not needed.
#   args...    — remaining arguments forwarded to the script.
#
# stdin_var and tty_var are detected by not starting with "-". To pass
# tty_var without stdin_var, use "" for stdin_var. When both are provided,
# tty_var takes precedence (script(1) handles both tty and stdin).
run_script() {
    local stdout_var="$1" stderr_var="$2" code_var="$3"
    shift 3
    local stdin_var="" tty_var="" args=()
    if [[ $# -gt 0 && "$1" != -* ]]; then
        stdin_var="$1"; shift
        if [[ $# -gt 0 && "$1" != -* ]]; then
            tty_var="$1"; shift
        fi
    fi
    args=("$@")
    local out err code
    out="$(mktemp)"; err="$(mktemp)"
    set +e
    if [[ -n "$tty_var" && -x /usr/bin/script ]]; then
        # Use script(1) to create a pty. The child's /dev/tty resolves to
        # the pty slave. tty_var content is piped to the pty master via
        # script's stdin. Session output (child's stdout via pty) goes to
        # a temp file. Child's stderr is redirected to the real $err file
        # via 2> redirect inside the -c command string.
        local sce cmd_str
        sce="$(mktemp)"
        cmd_str="bash ${SCRIPT_UNDER_TEST}${args[@]/#/ }"
        cmd_str+=" 2>${err}"
        printf '%s\n' "$tty_var" | script -q -e -c "$cmd_str" "$sce" >/dev/null 2>/dev/null
        code=$?
        cat "$sce" >"$out"
        rm -f "$sce"
    elif [[ -n "$stdin_var" ]]; then
        printf '%s' "$stdin_var" | bash "${SCRIPT_UNDER_TEST}" "${args[@]}" >"$out" 2>"$err"
        code=$?
    else
        bash "${SCRIPT_UNDER_TEST}" "${args[@]}" >"$out" 2>"$err"
        code=$?
    fi
    set -e
    printf -v "$stdout_var" '%s' "$(cat "$out")"
    printf -v "$stderr_var" '%s' "$(cat "$err")"
    printf -v "$code_var" '%s' "$code"
    rm -f "$out" "$err"
}

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

echo
echo "== Q18.1: ci.sh file checks =="

if [[ -f "${SCRIPT_UNDER_TEST}" ]]; then
    printf '  PASS  file exists: %s\n' "${SCRIPT_UNDER_TEST}"
    PASS=$((PASS + 1))
else
    printf '  FAIL  file missing: %s\n' "${SCRIPT_UNDER_TEST}"
    FAIL=$((FAIL + 1))
    echo "Cannot continue without the script. Aborting."
    exit 1
fi

if [[ -x "${SCRIPT_UNDER_TEST}" ]]; then
    printf '  PASS  file is executable\n'
    PASS=$((PASS + 1))
else
    printf '  FAIL  file is NOT executable\n'
    FAIL=$((FAIL + 1))
fi

echo
echo "== Q18.2: bash syntax check =="

set +e
bash -n "${SCRIPT_UNDER_TEST}"
syntax_rc=$?
set -e
assert_eq "bash -n exit code" "0" "${syntax_rc}"

echo
echo "== Q18.3: --help exits 0 with usage =="

run_script out_stdout out_stderr out_code --help
assert_eq "--help exit code" "0" "${out_code}"
assert_contains "stdout contains Usage" "${out_stdout}" "Usage:"
assert_contains "stdout mentions skip-lint" "${out_stdout}" "--skip-lint"
assert_contains "stdout mentions skip-builds" "${out_stdout}" "--skip-builds"
assert_contains "stdout mentions skip-tests" "${out_stdout}" "--skip-tests"

echo
echo "== Q18.4: unknown flag exits 4 =="

run_script out_stdout out_stderr out_code --bogus
assert_eq "unknown flag exit code" "4" "${out_code}"
assert_contains "stderr says unknown argument" "${out_stderr}" "unknown argument"

echo
echo "== Q18.5: nox missing -> exit 1 =="

saved_path="${PATH}"
export PATH="/usr/bin:/bin"
run_script out_stdout out_stderr out_code "" "0" --skip-lint
assert_eq "nox-missing exit code" "1" "${out_code}"
# Interactive path: prompt goes to stdout (ptty), ci.sh reads "0" → abort → exit 1
assert_contains "stdout says nox not found" "${out_stdout}" "nox not found"
assert_contains "stdout offers pipx install" "${out_stdout}" "pipx"
export PATH="${saved_path}"

echo
echo "== Q18.6: --skip-builds runs all_tests =="

fake_dir="$(make_fake_nox)"
fake_log="$(mktemp -t nox-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${fake_dir}:${saved_path}"
export FAKE_NOX_LOG="${fake_log}"
run_script out_stdout out_stderr out_code --skip-lint --skip-builds
assert_eq "exit code with --skip-builds" "0" "${out_code}"

if [[ -f "${fake_log}" ]]; then
    log_contents="$(cat "${fake_log}")"
    assert_contains "called nox -s all_tests" "${log_contents}" "-s all_tests"
    if [[ "${log_contents}" == *"-s all_builds"* ]]; then
        printf '  FAIL  all_builds should NOT have been called with --skip-builds\n'
        FAIL=$((FAIL + 1))
    else
        printf '  PASS  all_builds not called (--skip-builds worked)\n'
        PASS=$((PASS + 1))
    fi
else
    printf '  FAIL  fake nox log missing\n'
    FAIL=$((FAIL + 1))
fi
assert_contains "stdout announces Phase 1 skipped" "${out_stdout}" "Phase 1: skipped"
assert_contains "stdout announces Phase 2 runs tests" "${out_stdout}" "Phase 2: running all test suites"
rm -f "${fake_log}"
unset FAKE_NOX_LOG
export PATH="${saved_path}"
rm -rf "${fake_dir}"

echo
echo "== Q18.7: --skip-tests runs all_builds =="

fake_dir="$(make_fake_nox)"
fake_log="$(mktemp -t nox-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${fake_dir}:${saved_path}"
export FAKE_NOX_LOG="${fake_log}"
run_script out_stdout out_stderr out_code --skip-lint --skip-tests
assert_eq "exit code with --skip-tests" "0" "${out_code}"

if [[ -f "${fake_log}" ]]; then
    log_contents="$(cat "${fake_log}")"
    assert_contains "called nox -s all_builds" "${log_contents}" "-s all_builds"
    if [[ "${log_contents}" == *"-s all_tests"* ]]; then
        printf '  FAIL  all_tests should NOT have been called with --skip-tests\n'
        FAIL=$((FAIL + 1))
    else
        printf '  PASS  all_tests not called (--skip-tests worked)\n'
        PASS=$((PASS + 1))
    fi
else
    printf '  FAIL  fake nox log missing\n'
    FAIL=$((FAIL + 1))
fi
assert_contains "stdout announces Phase 1 runs builds" "${out_stdout}" "Phase 1: building all packages"
assert_contains "stdout announces Phase 2 skipped" "${out_stdout}" "Phase 2: skipped"
rm -f "${fake_log}"
unset FAKE_NOX_LOG
export PATH="${saved_path}"
rm -rf "${fake_dir}"

echo
echo "== Q18.8: both flags -> no nox calls =="

fake_dir="$(make_fake_nox)"
fake_log="$(mktemp -t nox-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${fake_dir}:${saved_path}"
export FAKE_NOX_LOG="${fake_log}"
run_script out_stdout out_stderr out_code --skip-lint --skip-tests --skip-builds
assert_eq "exit code with both --skip" "0" "${out_code}"

if [[ -f "${fake_log}" ]] && [[ -s "${fake_log}" ]]; then
    printf '  FAIL  nox should NOT have been called when both phases skipped\n'
    printf '        log: %q\n' "$(cat "${fake_log}")"
    FAIL=$((FAIL + 1))
else
    printf '  PASS  nox not called (both phases skipped)\n'
    PASS=$((PASS + 1))
fi
assert_contains "stdout announces Phase 1 skipped" "${out_stdout}" "Phase 1: skipped"
assert_contains "stdout announces Phase 2 skipped" "${out_stdout}" "Phase 2: skipped"
rm -f "${fake_log}"
unset FAKE_NOX_LOG
export PATH="${saved_path}"
rm -rf "${fake_dir}"

echo
echo "== Q18.9: test failure propagates as exit 2 =="

fake_dir="$(make_fake_nox)"
fake_log="$(mktemp -t nox-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${fake_dir}:${saved_path}"
export FAKE_NOX_LOG="${fake_log}"
export FAKE_NOX_RC=2
run_script out_stdout out_stderr out_code --skip-lint --skip-builds
assert_eq "exit code with failing tests" "2" "${out_code}"
assert_contains "stderr says test session failed" "${out_stderr}" "test session failed"
unset FAKE_NOX_RC
rm -f "${fake_log}"
unset FAKE_NOX_LOG
export PATH="${saved_path}"
rm -rf "${fake_dir}"

echo
echo "== Q18.10: build failure propagates as exit 3 =="

fake_dir="$(make_fake_nox)"
fake_log="$(mktemp -t nox-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${fake_dir}:${saved_path}"
export FAKE_NOX_LOG="${fake_log}"
export FAKE_NOX_RC=2
run_script out_stdout out_stderr out_code --skip-lint --skip-tests
assert_eq "exit code with failing builds" "3" "${out_code}"
assert_contains "stderr says build session failed" "${out_stderr}" "build session failed"
unset FAKE_NOX_RC
rm -f "${fake_log}"
unset FAKE_NOX_LOG
export PATH="${saved_path}"
rm -rf "${fake_dir}"

echo
echo "== Q18.11: lint success =="

lint_tools_dir="$(make_fake_lint_tools)"
fake_dir="$(make_fake_nox)"
fake_log="$(mktemp -t nox-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${lint_tools_dir}:${fake_dir}:${saved_path}"
export FAKE_NOX_LOG="${fake_log}"
export FAKE_PIPENV_RC=0
export FAKE_NPX_RC=0
run_script out_stdout out_stderr out_code --skip-builds --skip-tests
assert_eq "lint success exit code" "0" "${out_code}"
assert_contains "stdout announces Phase 0 lint" "${out_stdout}" "Phase 0: running lint checks"
assert_contains "stdout announces pipeline complete" "${out_stdout}" "CI pipeline complete"
unset FAKE_PIPENV_RC
unset FAKE_NPX_RC
rm -f "${fake_log}"
unset FAKE_NOX_LOG
export PATH="${saved_path}"
rm -rf "${fake_dir}" "${lint_tools_dir}"

echo
echo "== Q18.12: lint failure (pipenv fails) =="

lint_tools_dir="$(make_fake_lint_tools)"
fake_dir="$(make_fake_nox)"
saved_path="${PATH}"
export PATH="${lint_tools_dir}:${fake_dir}:${saved_path}"
export FAKE_PIPENV_RC=1
run_script out_stdout out_stderr out_code
assert_eq "lint failure exit code" "5" "${out_code}"
assert_contains "stderr says lint check failed" "${out_stderr}" "lint check failed"
unset FAKE_PIPENV_RC
export PATH="${saved_path}"
rm -rf "${fake_dir}" "${lint_tools_dir}"

echo
echo "== Q18.13: --no-install without nox =="

saved_path="${PATH}"
export PATH="/usr/bin:/bin"
run_script out_stdout out_stderr out_code --skip-lint --no-install
assert_eq "no-install exit code" "0" "${out_code}"
assert_contains "stderr warns nox not found" "${out_stderr}" "nox"
assert_contains "stdout announces Phase 1 skipped" "${out_stdout}" "Phase 1: skipped"
assert_contains "stdout announces Phase 2 skipped" "${out_stdout}" "Phase 2: skipped"
export PATH="${saved_path}"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo
echo "================================="
printf '  %d passed, %d failed\n' "${PASS}" "${FAIL}"
echo "================================="

if [[ "${FAIL}" -ne 0 ]]; then
    exit 1
fi
exit 0
