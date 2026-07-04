---
layout: default
---
# Wheel Install Validation — `test_installs.sh`

Create a reproducible pipenv venv from `dist-test-install/Pipfile`, install all 6 monorepo wheels, and run smoke tests.

```bash
./scripts/test_installs.sh               # full pipeline
./scripts/test_installs.sh --dry-run     # show what would be done
./scripts/test_installs.sh --skip-install  # re-test only (no pipenv sync)
```

## Smoke Tests (per package)

1. **Import check** — `python -c "import <package>"`
2. **CLI `--help`** — for `board-manager`, `arduino-dash`, `medminder-dash`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All packages installed and smoke-tested |
| 1 | pipenv not found or Pipfile missing |
| 2 | pipenv sync failed |
| 3 | Smoke test(s) failed |
| 4 | Invalid CLI argument |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_INSTALLS_DIR` | `dist-test-install/` | Override working directory |
| `PIP_INDEX_URL` | — | Passed through to pipenv |

## Smoked Packages

| Package | Import | CLI |
|---------|--------|-----|
| `board-manager` | ✅ | ✅ |
| `board-manager-client` | ✅ | — |
| `arduino-sketch-tools` | ✅ | — |
| `arduino-grpc` | ✅ | — |
| `arduino-dash` | ✅ | ✅ |
| `medminder-dash` | ✅ | ✅ |

## Related

- [dist-test-install/index.md](../dist-test-install/index.md) — validation environment details
