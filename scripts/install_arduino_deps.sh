#!/usr/bin/env bash
# @file install_arduino_deps.sh
# @brief Install Arduino libraries required by sketches.
# @description Refresh the Arduino library index, then install RTClib
# and TM1637TinyDisplay via arduino-cli.
# @exitcode 0 All libraries installed successfully.
# @exitcode 1 arduino-cli not found on PATH.
# @exitcode 2 A library installation failed.

# scripts/install_arduino_deps.sh
#
# Install Arduino libraries required by sketches.
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

readonly INSTALL_URL="https://arduino.github.io/arduino-cli/installation/"

readonly LIBRARIES=(
    "RTClib"
    "TM1637TinyDisplay"
)

log() {
    printf '[install_arduino_deps] %s\n' "$*"
}

die() {
    printf '[install_arduino_deps] ERROR: %s\n' "$*" >&2
    exit "${2:-1}"
}

if ! command -v arduino-cli >/dev/null 2>&1; then
    cat >&2 <<EOF
arduino-cli is not installed or not on PATH.

Install it from: ${INSTALL_URL}

On Linux/macOS:
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

On Arch:
    sudo pacman -S arduino-cli
EOF
    exit 1
fi

log "Refreshing Arduino library index"
arduino-cli core update-index

for lib in "${LIBRARIES[@]}"; do
    log "Installing library: ${lib}"
    if ! arduino-cli lib install "${lib}"; then
        die "failed to install library '${lib}'" 2
    fi
done

log "Installed libraries:"
arduino-cli lib list | grep -E "^(RTClib|TM1637TinyDisplay)" || true

log "Done."

