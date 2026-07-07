---
layout: default
---
# CI Pipeline — `ci.sh`

One-command runner for the full lint + build + test pipeline. Used in CI; also handy locally.

```bash
./scripts/ci.sh                               # lint + builds + tests (full pipeline)
./scripts/ci.sh --skip-lint                   # builds + tests (skip lint phase)
./scripts/ci.sh --skip-builds                 # test only (skip the build phase)
./scripts/ci.sh --skip-tests                  # build only (skip the test phase)
./scripts/ci.sh --no-install                  # skip nox phases if nox is missing (no prompt)
```

## Pipeline Stages

Builds precede tests so that wheel files exist in `dist/` directories when
per-package test sessions resolve monorepo `file://` dependency sources.

0. **Lint** — 5 checks before any build/test work begins (ruff check, ruff format --check, prettier --check, eslint, djlint --check)
1. **Build** — `nox -s all_builds` builds all 6 package wheels (creates `dist/`)
2. **Test** — `nox -s all_tests` runs `scripts_tests` + 6 per-package pytest suites

If `nox` is missing and no `--no-install` flag is given, an interactive prompt
offers to install nox or skip the build/test phases.

If uncommitted `Pipfile.lock` changes are detected before the build phase,
a pre-check warns and asks whether to overwrite them (the nox test session
calls `pipenv lock --dev` which regenerates lock files). After the pipeline
completes, a post-check lists any newly-dirtied lock files and offers to
`git restore` them.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Pipeline succeeded |
| 1 | `nox` not found on PATH and non-interactive (or user aborted) |
| 2 | At least one test failed |
| 3 | At least one build failed |
| 4 | Invalid CLI argument |
| 5 | At least one lint check failed |

## Notes

- The `--no-install` flag suppresses the nox install prompt; if nox is missing, build and test phases are silently skipped.
- The script does **not** call `install_arduino_deps.sh` — that is a separate step for flashing boards.
- This script is invoked by the **pre-push Git hook** (`.githooks/pre-push`) as a mandatory gate. Skip the hook with `git push --no-verify`.
- Equivalent granular nox invocations:

```bash
nox -s all_tests                # all 7 test sessions
nox -s all_builds               # all 6 wheel builds
nox -s scripts_tests            # scripts tests only
nox -s 'tests(arduino_dash)'    # one package's tests
nox -s 'build(arduino_dash)'    # one package's wheel
```
