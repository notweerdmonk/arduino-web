---
layout: default
---
# Arduino Library Installer — `install_arduino_deps.sh`

Install Arduino libraries required by the MedMinderV2 sketches.

```bash
./scripts/install_arduino_deps.sh
```

## Libraries Installed

| Library | Purpose |
|---------|---------|
| `RTClib` | DS3231 RTC driver |
| `TM1637TinyDisplay` | 7-segment display driver |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All libraries installed (or already present) |
| 1 | `arduino-cli` not found on PATH |
| 2 | A library failed to install |

## Process

1. Runs `arduino-cli core update-index` to refresh the library index
2. Runs `arduino-cli lib install` for each library
3. Verifies with `arduino-cli lib list`

If `arduino-cli` is not installed, prints a helpful install URL:
```
https://arduino.github.io/arduino-cli/installation/
```
