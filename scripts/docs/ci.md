---
---
# CI Pipeline — `ci.sh`

One-command runner for the full test + build pipeline. Used in CI; also handy locally.

```bash
./scripts/ci.sh              # tests + builds (full pipeline)
./scripts/ci.sh --skip-tests # build only
./scripts/ci.sh --skip-builds # test only
```

## Pipeline Stages

1. **Test** — `nox -s all_tests` runs `scripts_tests` + 6 per-package pytest suites
2. **Build** — `nox -s all_builds` builds all 6 package wheels

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Pipeline succeeded |
| 1 | `nox` not found on PATH |
| 2 | At least one test failed |
| 3 | At least one build failed |
| 4 | Invalid CLI argument |

## Notes

- The script does **not** call `install_arduino_deps.sh` — that is a separate step for flashing boards.
- Equivalent granular nox invocations:

```bash
nox -s all_tests                # all 7 test sessions
nox -s all_builds               # all 6 wheel builds
nox -s scripts_tests            # scripts tests only
nox -s 'tests(arduino_dash)'    # one package's tests
nox -s 'build(arduino_dash)'    # one package's wheel
```
