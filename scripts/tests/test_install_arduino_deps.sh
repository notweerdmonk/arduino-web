#!/usr/bin/env bash
# @file test_install_arduino_deps.sh
# @brief Tests for the install_arduino_deps.sh script.
# @description Verify file checks, bash syntax, missing arduino-cli
# handling, and successful execution with a fake arduino-cli shim.

# scripts/tests/test_install_arduino_deps.sh
#
# Tests for the install_arduino_deps.sh script.
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
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/../install_arduino_deps.sh"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Assert two strings are equal. If not, print a diff and increment FAIL.
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

# Assert that $1 contains the substring $2.
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

# Make a private temp dir with a fake arduino-cli that just records its
# invocations and exits 0. Echoes the temp dir path.
make_fake_arduino_cli() {
    local tmpdir
    tmpdir="$(mktemp -d -t arduino-cli-shim.XXXXXX)"
    cat >"${tmpdir}/arduino-cli" <<'SHIM'
#!/bin/sh
# Fake arduino-cli for testing. Records invocations and exits 0.
echo "$@" >>"${FAKE_LOG:-/dev/null}"
case "$1" in
    core)
        # `core update-index` — nothing to do
        ;;
    lib)
        case "$2" in
            install) echo "Installing library: $3" ;;
            list)
                # Emit a fake lib list (one entry per line, name first)
                cat <<'LIBS'
RTClib 1.4.3
TM1637TinyDisplay 1.3.0
Adafruit Unified Sensor 1.1.14
LIBS
                ;;
        esac
        ;;
esac
exit 0
SHIM
    chmod +x "${tmpdir}/arduino-cli"
    printf '%s' "${tmpdir}"
}

# Run the script under test, capturing stdout, stderr, and exit code.
run_script() {
    local path="$1"
    local stdout_var="$2"
    local stderr_var="$3"
    local code_var="$4"
    shift 4
    local out err code
    out="$(mktemp)"
    err="$(mktemp)"
    set +e
    "$@" "${path}" >"${out}" 2>"${err}"
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
echo "== Q1: install_arduino_deps.sh file checks =="

# Q1.1: file exists
if [[ -f "${SCRIPT_UNDER_TEST}" ]]; then
    printf '  PASS  file exists: %s\n' "${SCRIPT_UNDER_TEST}"
    PASS=$((PASS + 1))
else
    printf '  FAIL  file missing: %s\n' "${SCRIPT_UNDER_TEST}"
    FAIL=$((FAIL + 1))
    echo "Cannot continue without the script. Aborting."
    exit 1
fi

# Q1.2: file is executable
if [[ -x "${SCRIPT_UNDER_TEST}" ]]; then
    printf '  PASS  file is executable\n'
    PASS=$((PASS + 1))
else
    printf '  FAIL  file is NOT executable\n'
    FAIL=$((FAIL + 1))
fi

echo
echo "== Q2: bash syntax check =="

# Q2.1: bash -n passes
set +e
bash -n "${SCRIPT_UNDER_TEST}"
syntax_rc=$?
set -e
assert_eq "bash -n exit code" "0" "${syntax_rc}"

echo
echo "== Q2: arduino-cli missing -> exit 1 =="

# Q2.2: when arduino-cli is NOT on PATH, script exits 1
fake_dir="$(make_fake_arduino_cli)"
# Save the real PATH, strip the fake dir, run the script
saved_path="${PATH}"
# Add only the system paths (no /home/weerdmonk/bin where the real
# arduino-cli lives). Use a minimal PATH that does NOT contain arduino-cli.
export PATH="/usr/bin:/bin"
run_script "${SCRIPT_UNDER_TEST}" out_stdout out_stderr out_code env
assert_eq "exit code with no arduino-cli" "1" "${out_code}"
assert_contains "stderr contains install URL" "${out_stderr}" "https://arduino.github.io/arduino-cli/installation/"
assert_contains "stderr contains install hint" "${out_stderr}" "arduino-cli is not installed"
export PATH="${saved_path}"
rm -rf "${fake_dir}"

echo
echo "== Q2: arduino-cli present -> exit 0 + correct calls =="

# Q2.3: when arduino-cli IS on PATH (via fake shim), script exits 0
# and invokes core update-index + lib install for each library.
fake_dir="$(make_fake_arduino_cli)"
fake_log="$(mktemp -t arduino-cli-shim-log.XXXXXX)"
saved_path="${PATH}"
export PATH="${fake_dir}:${saved_path}"
export FAKE_LOG="${fake_log}"
run_script "${SCRIPT_UNDER_TEST}" out_stdout out_stderr out_code env
assert_eq "exit code with fake arduino-cli" "0" "${out_code}"

# Check the log for the expected invocations
if [[ -f "${fake_log}" ]]; then
    log_contents="$(cat "${fake_log}")"
    assert_contains "core update-index called"  "${log_contents}" "core update-index"
    assert_contains "lib install RTClib called"  "${log_contents}" "lib install RTClib"
    assert_contains "lib install TM1637TinyDisplay called" "${log_contents}" "lib install TM1637TinyDisplay"
else
    printf '  FAIL  fake arduino-cli log missing\n'
    FAIL=$((FAIL + 1))
fi
assert_contains "stdout announces RTClib install"  "${out_stdout}" "RTClib"
assert_contains "stdout announces TM1637 install"  "${out_stdout}" "TM1637TinyDisplay"
rm -f "${fake_log}"
unset FAKE_LOG
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

