---
---

# Pipenv Venv Checker — `check_venv.bash`

Recursively traverse directories and verify that pipenv virtual environments exist in each. Useful for diagnosing missing or broken venvs after a fresh clone or a failed `pipenv install`.

```bash
# Check the entire monorepo
./scripts/check_venv.bash .

# Check specific directories
./scripts/check_venv.bash board_manager scripts
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All venvs found |
| 1 | At least one `pipenv --venv` call failed (venv missing/broken) |

## How It Works

The function recursively walks the given directories. In each directory it runs `pipenv --venv` — if the pipenv environment is missing, `pipenv --venv` exits non-zero and the overall script exits 1.

## Typical Use Cases

- **Fresh clone** — verify all subpackages have their venvs created after running `nox -s all_builds` or individual `pipenv install` commands
- **Debugging** — quickly identify which package's venv is stale or missing when `pytest` fails with import errors
- **CI** — validate environment setup before running tests

## Related

- [Scripts index](index.md) — all utility scripts
- [Install Arduino deps](install-arduino-deps.md) — Arduino library installer
