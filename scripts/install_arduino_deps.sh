#!/usr/bin/env bash
#
# install_arduino_deps.sh — Install Arduino libraries required by the
# MedMinder project (RTClib for the DS3231 RTC, TM1637TinyDisplay for the
# 7-segment display).
#
# Assumes `arduino-cli` is already installed and on PATH. Does NOT install
# ESP32 core — only the libraries the MedMinder sketches actually use.
#
# Usage:
#   ./scripts/install_arduino_deps.sh
#
# Exit codes:
#   0 — all libraries installed (or already present)
#   1 — arduino-cli not found
#   2 — a library failed to install
#

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
