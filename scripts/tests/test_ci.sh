#!/usr/bin/env bash
#
# test_ci.sh — tests for scripts/ci.sh.
#
# Q18 verification: file exists, is executable, has valid bash syntax,
# parses CLI flags, has the nox-not-found guard, and forwards the right
# arguments to `nox` in each mode.
#
# Strategy: write a fake `nox` shim into a private temp dir, prepend that
# dir to PATH, and run ci.sh. The shim records the call args + exit codes
# and emits a marker on stdout that the test asserts on.
#
# Usage:  bash scripts/tests/test_ci.sh
# Exit:   0 on all-pass, 1 on any failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../ci.sh"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PASS=0
FAIL=0

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

# Run the script under test, capturing stdout, stderr, and exit code.
# Usage: run_script <stdout_var> <stderr_var> <code_var> [args...]
# where [args...] is the script args. The script is invoked as
# `bash ${SCRIPT_UNDER_TEST} "$@"`.
run_script() {
    local stdout_var="$1"
    local stderr_var="$2"
    local code_var="$3"
    shift 3
    local out err code
    out="$(mktemp)"
    err="$(mktemp)"
    set +e
    bash "${SCRIPT_UNDER_TEST}" "$@" >"${out}" 2>"${err}"
    code=$?
    set -e
    printf -v "${stdout_var}" '%s' "$(cat "${out}")"
    printf -v "${stderr_var}" '%s' "$(cat "${err}")"
    printf -v "${code_var}" '%s' "${code}"
    rm -f "${out}" "${err}"
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
assert_contains "stdout mentions all_tests" "${out_stdout}" "all_tests"
assert_contains "stdout mentions all_builds" "${out_stdout}" "all_builds"

echo
echo "== Q18.4: unknown flag exits 4 =="

run_script out_stdout out_stderr out_code --bogus
assert_eq "unknown flag exit code" "4" "${out_code}"
assert_contains "stderr says unknown argument" "${out_stderr}" "unknown argument"

echo
echo "== Q18.5: nox missing -> exit 1 =="

saved_path="${PATH}"
export PATH="/usr/bin:/bin"
run_script out_stdout out_stderr out_code
assert_eq "nox-missing exit code" "1" "${out_code}"
assert_contains "stderr mentions nox" "${out_stderr}" "nox"
assert_contains "stderr mentions pipx" "${out_stderr}" "pipx"
export PATH="${saved_path}"

echo
echo "== Q18.6: --skip-builds runs all_tests =="

fake_dir="$(make_fake_nox)"
fake_log="$(mktemp -t nox-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${fake_dir}:${saved_path}"
export FAKE_NOX_LOG="${fake_log}"
run_script out_stdout out_stderr out_code --skip-builds
assert_eq "exit code with --skip-builds" "0" "${out_code}"

if [[ -f "${fake_log}" ]]; then
    log_contents="$(cat "${fake_log}")"
    assert_contains "called nox -s all_tests" "${log_contents}" "-s all_tests"
    # Should NOT have run all_builds
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
assert_contains "stdout announces Phase 1" "${out_stdout}" "Phase 1"
assert_contains "stdout announces Phase 2 skipped" "${out_stdout}" "Phase 2: skipped"
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
run_script out_stdout out_stderr out_code --skip-tests
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
assert_contains "stdout announces Phase 1 skipped" "${out_stdout}" "Phase 1: skipped"
assert_contains "stdout announces Phase 2" "${out_stdout}" "Phase 2: building all packages"
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
run_script out_stdout out_stderr out_code --skip-tests --skip-builds
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
# FAKE_NOX_RC=2 simulates the nox session exiting 2 (test failure)
export FAKE_NOX_RC=2
run_script out_stdout out_stderr out_code --skip-builds
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
run_script out_stdout out_stderr out_code --skip-tests
# The tests phase is skipped, so we hit Phase 2 with FAKE_NOX_RC=2 -> exit 3
assert_eq "exit code with failing builds" "3" "${out_code}"
assert_contains "stderr says build session failed" "${out_stderr}" "build session failed"
unset FAKE_NOX_RC
rm -f "${fake_log}"
unset FAKE_NOX_LOG
export PATH="${saved_path}"
rm -rf "${fake_dir}"

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
