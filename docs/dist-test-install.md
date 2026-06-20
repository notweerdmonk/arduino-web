---
---
# dist-test-install — Wheel Install Validation

Validation environment for testing that all monorepo wheels resolve, install, and import correctly.

Full documentation lives in [`dist-test-install/docs/`](../dist-test-install/docs/index.md).

## Quick Links

| Document | Description |
|----------|-------------|
| [dist-test-install/docs/index.md](../dist-test-install/docs/index.md) | Environment overview, usage, adding packages |
| [scripts/docs/test-installs.md](../scripts/docs/test-installs.md) | Smoke test script — `test_installs.sh` |

## Quick Start

```bash
cd dist-test-install
pipenv sync
pipenv run python -c "import board_manager"
```
