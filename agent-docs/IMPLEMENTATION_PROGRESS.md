---
layout: default
---
{% raw %}
# Implementation Progress — Phase 112: Jekyll Optional Front Matter

## Past Phases

### Phase 111: Semantic Versioning v0.1.0

| # | Task | Status | Notes |
|---|------|--------|-------|
| A | Add __version__ to 3 missing packages | ✅ | arduino_sketch_tools, board_manager_client, medminder_dash |
| B | Standardize setup.py to import version | ✅ | All 6 setup.py files use version=__version__ |
| C | Add version to root package.json | ✅ | "version": "0.1.0" added |
| D | Create root-level VERSION file | ✅ | VERSION: 0.1.0 |
| E | Test all changes | ✅ | 160 scripts tests passed, nox 8/8 sessions passed |

### Phase 112: Jekyll Optional Front Matter Plugin

| # | Task | Status | Notes |
|---|------|--------|-------|
| A | Add gem to Gemfile + plugin to `_config.yml` | ✅ | `:jekyll_plugins` group created |
| B | `bundle install` + `jekyll build` | ✅ | 0 errors |
| C | Verify 12 README.md → `.html` with layout | ✅ | All 12 appear as `.html` in `_site/` |


### Phase 113: Fix setup.py isolated build failure

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | board_manager setup.py | ✅ | `_read_version()` helper with `ast.literal_eval` |
| 2 | board_manager_client setup.py | ✅ | Same pattern |
| 3 | arduino_sketch_tools setup.py | ✅ | Same pattern |
| 4 | arduino_dash setup.py | ✅ | Same pattern |
| 5 | arduino_grpc setup.py | ✅ | Same pattern |
| 6 | medminder_dash setup.py | ✅ | Same pattern |
| 7 | Verify single build | ✅ | `nox -s 'build(board_manager)'` — success |
| 8 | Verify all builds | ✅ | `nox -s all_builds` — 7/7 sessions in 56s |
| 9 | Sync all agent-facing docs | ✅ | All docs updated with Phase 113 entries |


### Phase 114: Fix all ruff lint errors

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | pyproject.toml config | ✅ | select → lint.select |
| 2 | Auto-fix 138 errors | ✅ | ruff check --fix (I001, W293, F401, F541) |
| 3 | Fix 6 E402 in setup.py | ✅ | All 6 setup.py files fixed |
| 4 | Fix 17 E501 in 11 files | ✅ | Long lines wrapped |
| 5 | Fix 1 F841 | ✅ | Dead variable removed |
| 6 | Restore re-exports | ✅ | app.py + state.py with noqa |
| 7 | Verify ruff | ✅ | 0 errors |
| 8 | Verify tests | ✅ | nox -s all_tests — 8/8 sessions |


### Phase 115: Remove asyncio_mode pytest warning

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Remove asyncio_mode from pyproject.toml | ✅ | `asyncio_mode = "auto"` removed |
| 2 | Verify no warnings | ✅ | nox -s all_tests — 0 pytest warnings, 8/8 sessions |


### Phase 116: djlint template reformatting

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | pyproject.toml extend_exclude | ✅ | Added `_site|dist-standalone|docs/reference|scratch` |
| 2 | djlint --reformat on 50 templates | 🔄 | 25 medminder_dash + 15 arduino_dash + 10 arduino_sketch_tools |
| 3 | djlint --check passes (exit 0) | Pending | |
| 4 | All agent-facing docs updated | Pending | |
| 5 | User-facing docs updated | Pending | |


---

### Phase 117 — Fix CI Pipeline

| Q | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Swap build/test order in ci.sh | ✅ | Phase 1 = builds, Phase 2 = tests; updated --help, docblock, echo messages |
| Q2 | Add nox install to ci.yml | ✅ | `pip install nox` before ./scripts/ci.sh |
| Q3 | Verify changes | ✅ | bash syntax ✅, test_ci.sh 30/30 ✅, YAML valid ✅, nox -s scripts_tests 202/202 ✅ |
| Q4 | Update all agent-facing docs (16) | ✅ | All project + workflow docs updated |
| Q5 | Update user-facing docs | ✅ | Documentation skill applied |

---

### Phase 118 — Ruff Format Audit

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Run `ruff format .` | ✅ | 111 files reformatted, cosmetic only |
| 2 | Verify idempotency | ✅ | Second `--check` confirms all formatted |
| 3 | Fix E501 in add_license_headers.py | ✅ | 35 lines wrapped, 0 ruff errors |

---

### Phase 119 — Prettier/Djlint Convergence

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | djlint indent = 2 in pyproject.toml | ✅ | Matches prettier tabWidth |
| 2 | Add `**/templates/` to .prettierignore | ✅ | Exclude Jinja2 from prettier |
| 3 | Reformatted 50 templates with djlint | ✅ | 25 medminder_dash + 15 arduino_dash + 10 arduino_sketch_tools |
| 4 | Verify djlint --check exit 0 | ✅ | |
| 5 | Verify ruff check . exit 0 | ✅ | |

---

### Phase 120 — Git Hooks

| # | Task | Status | Notes |
|---|------|--------|-------|
| A | Create .githooks/pre-commit | ✅ | 5 lint checks, [Y/n] prompt, missing-tool graceful handling |
| B | Create .githooks/pre-push | ✅ | Runs `bash scripts/ci.sh`, blocks push on failure |
| C | Update AGENTS.md | ✅ | hooksPath setup added |
| D | Fix shellcheck issues | ✅ | ci.sh (SC2155) + test_ci.sh (SC2034, SC2154) — both clean |
| E | Update all agent-facing docs | ✅ | All project + workflow docs updated |
| F | Verify — ruff 0, shellcheck clean | ✅ | `ruff check .` 0 errors, both scripts shellcheck-clean |

---

### Phase 121 — ESLint Generated-Docs Ignore + Source Fix

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Add generated-path ignores to ESLint config | ✅ | 5 patterns: docs/reference, scratch, typedoc, search.js, eslint.config.mjs |
| 2 | Fix arduino_dash base.html unused vars | ✅ | `/* exported handleFolderInput, uploadSketch */` |
| 3 | Fix medminder_dash base.html unused vars | ✅ | Same annotation |
| 4 | Verify npx eslint . — 0 errors, 0 warnings | ✅ | Down from 2201 problems |

---

### Phase 122 — CI Restructure: Lint Phase + Nox Prompt + Standalone CI YAML

| Q | Task | Status | Notes |
|---|------|--------|-------|
| 1 | ci.sh — lint Phase 0 (5 checks, exit 5) | ✅ | ruff check, ruff format --check, prettier, eslint, djlint |
| 2 | ci.sh — `--skip-lint`, `--no-install` flags | ✅ | Parsed in arg-handling loop |
| 3 | ci.sh — interactive nox install prompt | ✅ | 5 options, `/dev/tty` subshell detection |
| 4 | ci.yml — standalone (no ci.sh call) | ✅ | Explicit lint/build/test steps |
| 5 | test_ci.sh — update 6 tests with `--skip-lint` | ✅ | Q18.5–Q18.10 all use `--skip-lint` |
| 6 | test_ci.sh — 3 new tests (lint fail, lint pass, --no-install) | ✅ | Q18.11, Q18.12, Q18.13; `make_fake_lint_tools()` helper |
| 7 | Update user-facing docs | ✅ | ci.md, reference/ci.md, test_ci.md, scripts/README.md, docs/tests.md, docs/guide.md, docs/architecture.md |
| 8 | Update agent-facing docs | ✅ | PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md, IMPLEMENTATION_PROGRESS.md |
| 9 | Verify — test_ci.sh + ruff | ✅ | 40/40 tests pass, ruff check 0 errors, ruff format OK |

{% endraw %}
