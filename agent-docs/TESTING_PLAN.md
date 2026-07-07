---
layout: default
---
{% raw %}
# Testing Plan — Phase 112: Jekyll Optional Front Matter Plugin

## Scope

Verify that the `jekyll-optional-front-matter` plugin correctly processes all 12 front-matter-less README.md files as Jekyll pages.

## Test Strategy

1. `bundle exec jekyll build` must exit 0 with no errors
2. All 12 README.md paths must render as `.html` files in `_site/`
3. No raw `.md` copies should remain in `_site/` (`remove_originals: true`)
4. Rendered `.html` files must include `<!DOCTYPE html>` (layout `default` applied)

## Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `bundle exec jekyll build` exits 0 | No errors/warnings | ✅ 0 errors, 0 warnings |
| 2 | `_site/README.html` exists | Rendered HTML with layout | ✅ 17 files (incl. extras), layout applied |
| 3 | `_site/scripts/README.html` exists | Rendered HTML with layout | ✅ Present |
| 4 | `_site/e2e/README.html` exists | Rendered HTML with layout | ✅ Present |
| 5 | `_site/board_manager/python/board_manager/README.html` exists | Rendered HTML with layout | ✅ Present |
| 6 | `_site/medminder_dash/python/medminder_dash/README.html` exists | Rendered HTML with layout | ✅ Present |
| 7 | No raw `README.md` in `_site/` | Zero `.md` output files | ✅ 0 raw `.md` copies |

---

## Phase 114: Fix all ruff lint errors

### Scope

Verify that ruff lint fixes don't break tests.

### Test Strategy

1. `ruff check .` must exit 0 with no errors
2. `nox -s all_tests` must pass 8/8 sessions with 0 failures
3. Re-export imports in `arduino_dash/app.py` and `arduino_dash/state.py` must be preserved (F401 noqa)

### Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `ruff check .` | 0 errors | ✅ All checks passed! |
| 2 | `nox -s all_tests` | 8/8 sessions pass | ✅ 8/8, 850+ tests, 0 failures |
| 3 | `arduino_dash/app.py` re-exports | 3 blocks with noqa persist | ✅ Verified |
| 4 | `arduino_dash/state.py` UPLOAD_BASE_DIR | Import with noqa persists | ✅ Verified |


---

## Phase 115: Remove asyncio_mode pytest warning

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `nox -s all_tests` — 0 pytest warnings | 0 `PytestConfigWarning` | ✅ 0 warnings across 8 sessions |
| 2 | All 8 sessions pass | 8/8 success | ✅ 8/8, 850+ tests, 0 failures |

---

## Phase 116 — djlint template reformatting

### Scope

Verify that djlint reformatting produces clean output without affecting
Python tests or functionality.

### Test Strategy

1. `djlint . --check` must exit 0
2. `ruff check .` must exit 0 (template reformat should not affect Python)
3. Templates must render correctly (structural HTML unchanged)

### Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `djlint . --check` exit 0 | 0 files flagged | ✅ |
| 2 | `ruff check .` exit 0 | 0 errors | ✅ |
| 3 | Templates render correctly | structural HTML unchanged | ✅ (cosmetic only) |



---

## Phase 117 — Fix CI Pipeline

### Test Strategy

| # | Test | Method | Expected |
|---|------|--------|----------|
| T1 | ci.sh bash syntax | `bash -n scripts/ci.sh` | Exit 0 |
| T2 | ci.sh flag parsing | `bash scripts/tests/test_ci.sh` | 30/30 assertions pass |
| T3 | ci.yml YAML validity | `python3 -c "import yaml; yaml.safe_load(...)"` | No error |
| T4 | Regression: scripts tests | `nox -s scripts_tests` | 202/202 tests pass (160 pytest + 42 bash) |

### Coverage Notes

- The `test_ci.sh` unit test covers: `--help`, unknown flags, nox-missing guard,
  `--skip-builds`, `--skip-tests`, both flags, test failure exit 2, build
  failure exit 3 — all using a fake nox shim
- Phase label assertions in test_ci.sh were updated from old order (tests first)
  to new order (builds first)

---

## Phase 118 — Ruff Format Audit

| # | Test | Method | Expected |
|---|------|--------|----------|
| T1 | Format idempotency | `pipenv run ruff format --check .` | Exit 0, all formatted |
| T2 | No lint regressions | `pipenv run ruff check .` | Exit 0 |
| T3 | E501 fix | `ruff check scripts/add_license_headers.py` | 0 line-too-long errors |

---

## Phase 119 — Prettier/Djlint Convergence

### Test Strategy

| # | Test | Method | Expected |
|---|------|--------|----------|
| T1 | djlint --check | `pipenv run djlint . --check` | Exit 0, 0 files flagged |
| T2 | ruff check | `pipenv run ruff check .` | Exit 0 |
| T3 | prettier check | `npx prettier --check "**/*.html"` | Only non-Jinja files checked |

---

## Phase 120 — Git Hooks

### Test Strategy

| # | Test | Method | Expected |
|---|------|--------|----------|
| T1 | pre-commit hook syntax | `bash -n .githooks/pre-commit` | Exit 0 |
| T2 | pre-push hook syntax | `bash -n .githooks/pre-push` | Exit 0 |
| T3 | pre-commit dry run | `bash .githooks/pre-commit` | Exit 0 (all checks pass) |
| T4 | pre-push dry run | `bash .githooks/pre-push` | Exit 0 (scripts_tests passes) |

### Test Strategy

1. **Syntax validation**: `bash -n` on both `.githooks/pre-commit` and `.githooks/pre-push` — must exit 0
2. **Static analysis**: `shellcheck` on `scripts/ci.sh` and `scripts/tests/test_ci.sh` — must pass cleanly with SC2155/SC2034/SC2154 fixed
3. **Ruff check**: `ruff check .` — 0 errors
4. **Pre-commit behavioral tests**:
   - Non-interactive mode (all tools present): runs ruff check, ruff format --check, prettier --check, eslint, djlint --check sequentially
   - Skip mode (respond `n` at prompt): prints yellow warning, exits 0
   - Tool-missing behavior (missing executable): skips that check gracefully
5. **Pre-push behavioral test**: invokes `scripts/ci.sh` (full nox all_builds + all_tests)

### Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| 1 | `bash -n .githooks/pre-commit` | Exit 0 | ✅ |
| 2 | `bash -n .githooks/pre-push` | Exit 0 | ✅ |
| 3 | `shellcheck scripts/ci.sh` | Clean pass | ✅ (SC2155, SC2034, SC2154 fixed) |
| 4 | `shellcheck scripts/tests/test_ci.sh` | Clean pass | ✅ (same 3 categories fixed) |
| 5 | `ruff check .` | 0 errors | ✅ |
| 6 | Pre-commit non-interactive mode | All checks run, exit 0 | ✅ |
| 7 | Pre-commit skip mode (n) | Yellow warning, exit 0 | ✅ |
| 8 | Pre-commit tool missing | Graceful skip, exit 0 | ✅ |
| 9 | Pre-push calls `scripts/ci.sh` | Script invoked at `$REPO_ROOT` | ✅ (verified via script inspection) |

---

## Phase 121 — ESLint Generated-Docs Ignore + Source Fix

### Test Strategy

| # | Test | Method | Expected |
|---|------|--------|----------|
| T1 | ESLint 0 errors, 0 warnings | `npx eslint . --max-warnings 0` | Exit 0 |
| T2 | Ruff no regressions | `pipenv run ruff check .` | Exit 0 |
| T3 | Prettier no regressions | `npx prettier --check "**/*.html"` | Exit 0 |

### Coverage Notes

- ESLint now ignores generated docs/reference, scratch, typedoc, search.js, and the root eslint.config.mjs passthrough
- Source template fixes use `/* exported */` comment which is more precise than blanket `eslint-disable`
- Pre-commit hook's eslint step will no longer fail on generated docs

---

## Phase 122 — CI Restructure: Lint Phase + Nox Prompt + Standalone CI YAML

### Test Strategy

| # | Test | Method | Expected |
|---|------|--------|----------|
| T1 | test_ci.sh full suite | `bash scripts/tests/test_ci.sh` | 40/40 assertions pass |
| T2 | ruff no regressions | `pipenv run ruff check .` | Exit 0 |
| T3 | ruff format consistency | `pipenv run ruff format --check .` | Exit 0 |
| T4 | bash syntax ci.sh | `bash -n scripts/ci.sh` | Exit 0 |
| T5 | bash syntax test_ci.sh | `bash -n scripts/tests/test_ci.sh` | Exit 0 |
| T6 | Lint success (Q18.11) | Fake pipenv/npx exit 0, `--skip-builds --skip-tests` | Exit 0, "Phase 0: running lint checks" |
| T7 | Lint failure (Q18.12) | FAKE_PIPENV_RC=1 | Exit 5, "lint check failed" |
| T8 | `--no-install` (Q18.13) | PATH stripped, `--skip-lint --no-install` | Exit 0, warning, both phases skipped |
| T9 | Non-interactive nox missing (Q18.5) | PATH `/usr/bin:/bin`, `--skip-lint` | Exit 1, "pipx" in stderr |
| T10 | `--skip-lint` on flag tests (Q18.6–Q18.10) | Fake nox with `--skip-lint` | All pass, correct phase labels |

### Coverage Notes

- Lint phase (Phase 0) tested via fake pipenv/npx shims — no real lint tools needed
- Nox prompt tested implicitly: non-interactive fallback tested (Q18.5), `--no-install` tested (Q18.13), interactive prompt not testable in CI (requires real terminal)
- All existing flag tests updated with `--skip-lint` — lint phase would fail without real pipenv/npx

---


---

## Phase 122c — Lock File Handling in ci.sh

### Scope

Verify the pre-check (warn/abort on dirty lock files before nox) and post-check (offer git restore of newly-dirtied lock files after nox) in ci.sh.

### Test Strategy

Test the new behavior using `make_fake_git()` shim with controlled pre/post dirty file state and user input via `tty_var`. Existing tests isolated from real git via `FAKE_GIT_DIRTY_LOCK_FILES=""`.

### Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| T1 | Pre-check abort: dirty lock files + user says "n" (Q18.14) | Exit 1, warns "uncommitted changes", stderr "aborting" | ✅ |
| T2 | Post-check restore: newly dirty locks + user says "y" (Q18.15) | Exit 0, "restored:" in stdout, git restore logged | ✅ |
| T3 | Post-check skip: newly dirty locks + user says "n" (Q18.16) | Exit 0, "left in working tree" in stdout | ✅ |
| T4 | Existing tests Q18.6–Q18.10 isolated from git | All pass with FAKE_GIT_DIRTY_LOCK_FILES="" | ✅ |



---

## Phase 122d — CI YAML: Node.js Setup + Jekyll Build Fix

**Date**: 2026-07-07
**Status**: ✅ Complete

**Scope**: Verify `.github/workflows/ci.yml` edits (setup-node + npm ci steps) and Jekyll build fix (raw/endraw wrapping).

### Test Scenarios

| # | Scenario | Expected | Actual |
|---|----------|----------|--------|
| T1 | `bundle exec jekyll build` | Exit 0, no Liquid errors | ✅ "done in 93.331 seconds" |
| T2 | `bash scripts/tests/test_ci.sh` | 49/49 | ✅ |
| T3 | `bash -n scripts/ci.sh` | Exit 0 | ✅ |
| T4 | `bash -n scripts/tests/test_ci.sh` | Exit 0 | ✅ |



## Phase 122e — Fix `tests(arduino_grpc)` CI Failure

**Date**: 2026-07-07 18:17
**Status**: ✅ COMPLETED

**Scope**: Verify that integration tests in `tests(arduino_grpc)` are correctly gated by `--integration` marker, and that CI installs `arduino-cli` so they run in CI.

### Test Strategy

| # | Test | Method | Expected |
|---|------|--------|----------|
| T1 | `ruff check .` | `pipenv run ruff check .` | Exit 0, 0 errors |
| T2 | Integration tests skip without `--integration` | `pipenv run pytest tests/` from `grpc_client/python/arduino_grpc/` | All 8 integration tests skip, unit tests pass |
| T3 | Integration tests run with `--integration` | `pipenv run pytest tests/ --integration` from package dir + `arduino-cli` on PATH | Integration tests execute (may skip with "No board detected") |
| T4 | noxfile passes `--integration` for arduino_grpc | `nox -s 'tests(arduino_grpc)'` with `arduino-cli` on PATH | Integration tests execute |
| T5 | ci.yml has arduino-cli install step | Inspect `.github/workflows/ci.yml` | curl → GITHUB_PATH → export PATH → core update + core install arduino:avr step present |
| T6 | `nox -s all_tests` without `arduino-cli` | `nox -s all_tests` on a system without arduino-cli | All sessions pass (arduino_grpc integration tests skip) |

{% endraw %}
