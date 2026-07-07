---
layout: default
---
{% raw %}
# Implementation Plan — Phase 104: E2E Documentation Restructure

**Date**: 2026-06-25 16:10
**Status**: ✅ COMPLETED

## Motivation

The `e2e/` directory has accumulated substantial testing infrastructure (mock servers, agent tools, MCP testing skills, Playwright specs) but lacks several documentation pieces that other monorepo modules have:

1. **No `e2e/README.md`** — other top-level dirs (`scripts/`, `dist-test-install/`) have module-level READMEs with quick start, directory layout, and requirements
2. **`.playwright-mcp/test-sketch/` is gitignored** — the minimal Arduino compile/upload sketch used in E2E testing is not version-controlled
3. **`e2e/fixtures/` and `e2e/specs/`** had no usage documentation in the e2e docs
4. **No `e2e/index.md`** — unlike `scripts/docs/index.md`, there's no module-level doc entry point
5. **agent_tools docs don't reference the test-sketch** — no path for compile/upload scenarios

## Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | e2e/README.md | New file — module overview, quick start (MCP interactive + automated specs), directory layout, requirements, related links | ✅ |
| Q2 | e2e/test-sketch/ | Copy from `.playwright-mcp/test-sketch/`, rewrite README with purpose, usage, and sketch content reference | ✅ |
| Q3 | e2e/index.md | New file — doc entry point with quick reference table and directory layout (like `scripts/docs/index.md`) | ✅ |
| Q4 | e2e/docs/index.md | Refocus as MCP testing sub-page; add Automated Playwright Specs section (install, run, webServer, spec summary table) and Test Sketch section | ✅ |
| Q5 | e2e/docs/servers.md | Add webServer auto-management note referencing `playwright.config.ts` | ✅ |
| Q6 | agent_tools docs | COMMAND.md, AGENT.md, GUIDE.md, MCP_TESTING_GUIDE.md — add test-sketch path references for compile/upload scenarios | ✅ |
| Q7 | Project-level docs | `docs/e2e-testing.md`: update quick links. Root `index.md`: update e2e rows | ✅ |
| Q8 | End-to-end verification | Load skill, read guide, start server, navigate, run basic scenario, cleanup | ✅ |

## Design Decisions

1. **`e2e/index.md` as doc entry point**: Fills the same role as `scripts/docs/index.md` — a quick reference table with directory layout. The project-root `index.md` now points here instead of `e2e/docs/index.md`.
2. **e2e/docs/index.md refocused**: Now a sub-page documenting MCP interactive testing specifically, with added sections for automated specs and test-sketch.
3. **No existing doc references `.playwright-mcp/test-sketch`** — grep confirms zero hits in `.md` files. No cross-reference edits needed for the move.
4. **test-sketch README**: Documents the minimal `setup(){} loop(){}` sketch as a "minimal valid Arduino sketch for compile/upload testing."

## Rollback

Each file change is scoped. Revert via `git checkout -- <file>` to undo individual changes.
---

## Phase 104.1 — Document e2e/fixtures/ (2026-06-25 17:53)

**Status**: ✅ COMPLETED

**Motivation**: `fixtures/test-data.ts` was created alongside specs but only appears by name in directory layouts. Its purpose (mirroring `--mock` server state), exports (`MOCK_PORTS`, `MOCK_SKETCH`, `MOCK_MEDICINES`, URL helpers), and import path from specs are undocumented.

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | e2e/docs/index.md | Add "Test Data Fixtures" subsection under Automated Playwright Specs — explain purpose, exported constants, import path, relation to server `--mock` state | ✅ |
| 2 | e2e/index.md, e2e/README.md, docs/e2e-testing.md | Check fixture references are consistent across all docs | ✅ |
---

## Phase 104.2 — Fix shelved-specs activation docs (2026-06-25 18:14)

**Status**: ✅ COMPLETED

**Motivation**: Review of Phase 104.1 identified two remaining gaps in the Automated Playwright Specs docs:
1. Installation section missing `npx playwright install --with-deps` (needed to download browser binaries)
2. No documented alternative for running from project root without `cd e2e`

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | e2e/docs/index.md Installation + Running | Add `npx playwright install --with-deps` after `npm install`; add footnote for `npx playwright test --config e2e/playwright.config.ts` | ✅ |

## Phase 106 — Set up Prettier + eslint-plugin-prettier for JS formatting (2026-06-28 00:54)

**Status**: ✅ COMPLETED

**Motivation**: Standardize JavaScript formatting across all HTML templates (inline JS) and standalone JS files. Prettier provides consistent formatting (quotes, semicolons, indentation) enforced via ESLint.

**Design decisions**:
- Double quotes (not single) — easier to embed single quotes in strings; double quotes need escaping but are rarer
- Semicolons required (`semi: true`)
- Tab width 2 spaces with `useTabs: false`
- `trailingComma: "es5"` — trailing commas where valid in ES5
- All formatting applied to inline JS in HTML templates via `npx prettier --write "**/*.html"` (190 files)
- `.prettierignore` excludes `_site/`, `node_modules/`, `.nox/`, `__pycache__/`, `.opencode/`, build artifacts, TypeScript files, and `config/eslint.config.mjs`

**Integration**: `eslint-plugin-prettier/recommended` added to `config/eslint.config.mjs`. This runs prettier as an ESLint rule, flagging formatting violations via `eslint_lint-files` MCP tool. `eslint-config-prettier` disables conflicting ESLint rules.

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| 1 | Config files | Create `.prettierrc`, `.prettierignore` | ✅ |
| 2 | ESLint config | Add `eslintPluginPrettierRecommended` to `config/eslint.config.mjs` (already done) | ✅ |
| 3 | Format | Run `npx prettier --write "**/*.html"` on 190 files | ✅ |
| 4 | Docs | Update CODEBASE_REFERENCE.md with prettier section | ✅ |
| 5 | Sync | Update all agent-facing workflow docs with Phase 106 entries | ✅ |

**Key finding — `trailingComma: "all"` vs `"es5"`**: `trailingComma: "all"` adds trailing commas to function parameters and calls, which prettier applies even inside Jinja2 `{{ }}` expressions in HTML templates. This can produce invalid Jinja2 syntax (e.g., `{{ url_for('route', arg=val,) }}`). Prettier has no native Jinja2 parser — it treats `{{ }}` as text, so trailing commas in function call args inside template expressions are silently added but not flagged. Using `trailingComma: "es5"` avoids this entirely since it only adds trailing commas in object literals and arrays, not function calls.

## Phase 107 — E2E TypeScript API Reference (typedoc + spec extraction)

**Date**: 2026-07-03 00:30
**Status**: ✅ COMPLETED

**Motivation**: The `e2e/` directory has TypeScript sources (specs, fixtures, config) with no API reference documentation. Python mock servers are already covered by pdoc, but the `.ts` files have no doc tooling. Two tools now available:
- **typedoc** (root `package.json`) — picks up exported symbols from `test-data.ts` and `playwright.config.ts`
- **Python extraction** (new `scripts/gen_e2e_spec_docs.py`) — parses `.spec.ts` files for `test.describe()` and `test()` labels, generates Markdown

**Design decision**: typedoc alone produces nothing useful for spec files (no exported declarations — all `test()`/`test.describe()` are internal closures). A Python extraction script is the pragmatic solution.

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | JSDoc annotations | Add `/** */` to `test-data.ts` exports + `playwright.config.ts` module header | ✅ |
| Q2 | gen_e2e_spec_docs.py | Write Python stdlib-only script to parse `.spec.ts` files → specs.md | ✅ |
| Q3 | gen_api_docs.sh | Add typedoc + spec extraction targets | ✅ |
| Q4 | Generate + verify | Run full generation, check output, nox test | ✅ |
| Q5 | User-facing docs | README.md + docs/index.md reference links | ✅ |
| Q6 | Agent-facing docs | Sync PLAN, JOURNAL, REVIEW_*, TESTING_*, CODEBASE_REFERENCE | ✅ |

## Phase 108 — Document Reference Tables + Broken Related Links Fix

**Date**: 2026-07-03 17:32
**Status**: ✅ COMPLETED

**Goal**: Add `## Document Reference` tables to all per-module `docs/index.md` files linking sibling `.md` files + `../README.md`. Fix 11 broken "Related" links. Create `dist-standalone-install/README.md`.

### Design

- Per-module `docs/index.md` gets a `## Document Reference` table with 2 columns: Document (link), Description (one-line summary)
- Modules with a "Related" section (scripts, dist-*) get links added to existing Related sections
- dist-standalone-install/README.md is an exact copy of dist-standalone/README.md
- No structural changes to any source code — doc-only phase

### Action Items

| # | Task | Scope | Status |
|---|------|-------|--------|
| 1 | arduino_dash docs/index.md | Document Reference table (13 rows) | ✅ |
| 2 | arduino_sketch_tools docs/index.md | Document Reference table (4 rows) | ✅ |
| 3 | board_manager docs/index.md | Document Reference table (11 rows) | ✅ |
| 4 | board_manager_client docs/index.md | Document Reference table (2 rows) | ✅ |
| 5 | grpc_client docs/index.md | Document Reference table (4 rows) | ✅ |
| 6 | medminder_dash docs/index.md | Document Reference table (15 rows) | ✅ |
| 7 | dist-test-install docs/index.md | Document Reference + Related links | ✅ |
| 8 | dist-standalone-install README.md | New file (copy from dist-standalone/) | ✅ |
| 9 | dist-standalone-install docs/index.md | Related links | ✅ |
| 10 | scripts docs/index.md | Related links | ✅ |
| 11 | All agent-facing docs sync'd | REVIEW_*, TESTING_*, PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md | ✅ |
## 2026-07-04 04:12 — Phase 111: Semantic Versioning — v0.1.0 Baseline

**Goal**: Establish consistent semantic versioning across the monorepo. All 6 Python packages plus
the E2E package already declare `0.1.0` — the work is to fill gaps and standardize the single
source of truth pattern.

**Scope**: 6 Python packages (`arduino-dash`, `arduino-sketch-tools`, `board-manager`,
`board-manager-client`, `arduino-grpc`, `medminder-dash`) + root `package.json` + `e2e/package.json`.

### Architecture

```
Version Single Source of Truth (SSoT) Pattern:
  ┌──────────────────────┐
  │  __init__.py          │  ← __version__ = "0.1.0" (single source)
  └──────┬───────────────┘
         │
    ┌────┴────┐
    ▼         ▼
  setup.py   pyproject.toml
  (import)   (redundant but kept
              for PEP 621 compliance)
```

Each Python package declares `__version__` in its `__init__.py`. The `setup.py` imports
`__version__` from the package rather than hardcoding it. `pyproject.toml` retains the
version string for PEP 621 tooling compatibility.

### Tasks

| # | Task | Scope | Files Changed | Status |
|---|------|-------|---------------|--------|
| A | Add `__version__` to 3 missing packages | `arduino-sketch-tools`, `board-manager-client`, `medminder-dash` | 3 `__init__.py` files | ✅ |
| B | Standardize setup.py to import version | All 6 Python packages | 6 `setup.py` files | ✅ |
| C | Add version to root package.json | Root `package.json` | 1 file | ✅ |
| D | Create root-level VERSION file | Root directory | 1 file | ✅ |
| E | Test all changes | scripts tests, module imports | — | ✅ |

### Existing References (unchanged)

- `arduino_dash/.../__init__.py`: `__version__ = "0.1.0"` ✅
- `board_manager/.../__init__.py`: `__version__ = "0.1.0"` ✅
- `grpc_client/.../__init__.py`: `__version__ = "0.1.0"` ✅
- `e2e/package.json`: `version: "0.1.0"` ✅
- All `pyproject.toml` files: `version = "0.1.0"` ✅ (kept as-is)

## 2026-07-05 04:35 — Phase 112: Jekyll Optional Front Matter Plugin

**Status**: ✅ COMPLETED

### Motivation

Front matter was stripped from all 12 README.md files during the document audit (Category 1/2). Without front matter, Jekyll treats them as static files — served as raw `.md` without layout rendering. The `jekyll-optional-front-matter` plugin processes markdown files without front matter as pages, converting them to `.html` with the site layout.

### Quantums

| Q | Description | Changes | Status |
|---|-------------|---------|--------|
| 1 | Add gem to Gemfile + plugin to `_config.yml` | `Gemfile`, `_config.yml` | ✅ |
| 2 | `bundle install` + `jekyll build` | Environment | ✅ |
| 3 | Verify 12 README.md → `.html` in `_site/` | Verification | ✅ |

### Key Details

- Plugin blacklists `README` as a common meta filename (case-insensitive, any path depth). The `include` list overrides this.
- All 12 README.md paths were already added to `include` in Category 5.
- Added `remove_originals: true` to suppress raw `.md` static copies from output.

### Existing References

- Plugin docs: https://github.com/benbalter/jekyll-optional-front-matter
- Blacklist source: `lib/jekyll-optional-front-matter.rb` — `FILENAME_BLACKLIST = %w(README LICENSE LICENCE COPYING CODE_OF_CONDUCT CONTRIBUTING ISSUE_TEMPLATE PULL_REQUEST_TEMPLATE)`


## Phase 113 — Fix setup.py isolated build failure

**Date**: 2026-07-06
**Status**: ✅ COMPLETED

### Motivation

`python -m build` (used by nox `build()` sessions and `scripts/ci.sh`) creates an
isolated build environment where the package being built is not on `sys.path`. All 6
`setup.py` files do `from <pkg> import __version__` which fails with:
`ModuleNotFoundError: No module named '<pkg>'`.

The fix replaces the direct import with an `ast.literal_eval` helper that reads
`__version__` from the package's `__init__.py` file without importing the module.
This preserves the single-source-of-truth pattern (version still lives in `__init__.py`)
while working in isolated build environments.

### Design

Pattern for each `setup.py`:

```python
import ast
from pathlib import Path

def _read_version():
    init_path = Path(__file__).parent / '<pkg_name>' / '__init__.py'
    with open(init_path) as f:
        for line in f:
            if line.startswith('__version__'):
                return ast.literal_eval(line.split('=')[1].strip())
    return '0.0.0'
```

Replace `from <pkg> import __version__` and `version=__version__` with the helper.

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | board_manager setup.py | Replace import with _read_version() | ✅ |
| Q2 | board_manager_client setup.py | Replace import with _read_version() | ✅ |
| Q3 | arduino_sketch_tools setup.py | Replace import with _read_version() | ✅ |
| Q4 | arduino_dash setup.py | Replace import with _read_version() | ✅ |
| Q5 | arduino_grpc setup.py | Replace import with _read_version() | ✅ |
| Q6 | medminder_dash setup.py | Replace import with _read_version() | ✅ |
| Q7 | Verify single build | `nox -s 'build(board_manager)'` — success | ✅ |
| Q8 | Verify all builds | `nox -s all_builds` — 7/7 sessions in 56s | ✅ |
| Q9 | Update all agent-facing docs | Sync PLAN, JOURNAL, IMPLEMENTATION_*, TESTING_*, REVIEW_*, CODEBASE_REFERENCE | ✅ |

### Design Decisions

1. **`ast.literal_eval` over `exec` / regex**: `ast.literal_eval` safely evaluates the
   version string literal without executing arbitrary code. Regex would be fragile
   (whitespace, quoting variations). `exec` would be unsafe.
2. **`Path(__file__).parent` over fixed paths**: Relative to `setup.py` itself, so
   the same pattern works regardless of where the build command is invoked from.
3. **`startswith('__version__')` over regex**: Simple, fast, and catches
   `__version__ = "0.1.0"` regardless of spacing around `=`.
4. **Fallback `'0.0.0'`**: Prevents silent failures. If parsing ever fails, the
   version degrades to `0.0.0` rather than raising an opaque build error.

### Rollback

Each setup.py change is independent. Revert via `git checkout -- <file>` for
individual files or `git revert` for the entire phase.

### Existing Version Process (unchanged)

- `__init__.py`: `__version__ = "0.1.0"` — single source of truth
- `setup.py`: `version=_read_version()` — reads from `__init__.py` without import
- `pyproject.toml`: `version = "0.1.0"` — PEP 621 compliance (redundant)
- `VERSION` (root): `0.1.0` — project-wide reference
- `package.json`: `"version": "0.1.0"` — npm tooling

## Phase 114 — Fix all ruff lint errors

**Date**: 2026-07-06
**Status**: ✅ COMPLETED

### Motivation

162 ruff lint errors across 70+ files after running `ruff check .` for the first time in a while.

### Scope

| Category | Count | Auto-fixable | Description |
|----------|-------|-------------|-------------|
| E402 | 6 | ❌ | Import not at top of file (setup.py) |
| E501 | 17 | ❌ | Line too long (>100) |
| F841 | 1 | ❌ | Unused variable |
| F401 | 30 | ✅ | Unused imports |
| I001 | 66 | ✅ | Unsorted imports |
| W293 | 37 | ✅ | Blank line whitespace |
| F541 | 5 | ✅ | f-string no placeholders |
| Config | 1 | — | select → lint.select deprecation |

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | pyproject.toml config | Migrate `select` to `[tool.ruff.lint]` | ✅ |
| Q2 | Auto-fix 138 errors | `ruff check --fix` (I001, W293, F401, F541) | ✅ |
| Q3 | E402 in setup.py (6 files) | Move `from setuptools import setup` above `_read_version()` | ✅ |
| Q4 | E501 in 11 files (17 lines) | Wrap long f-strings, docstrings, expressions | ✅ |
| Q5 | F841 | Remove dead `pattern` variable in `add_license_headers.py` | ✅ |
| Q6 | Restore re-exports | Add `# noqa: F401` to app.py (3 blocks) and state.py re-exports | ✅ |
| Q7 | Verify | `ruff check .` → 0 errors, `nox -s all_tests` → 8/8 sessions | ✅ |

### Files Modified

70 files changed, 473 insertions(+), 219 deletions(-). Key files:

- `pyproject.toml` — config migration
- 6 × `setup.py` — E402 fix (import order)
- `arduino_dash/app.py` — restored re-export blocks with `# noqa: F401`
- `arduino_dash/state.py` — restored `UPLOAD_BASE_DIR` import with `# noqa: F401`
- `scripts/add_license_headers.py` — removed dead `pattern` variable
- `arduino_dash/html_routes.py`, `extension.py`, `board_worker.py`, `test_daemon_manager.py`, `arduino_dash_server.py`, `medminder_dash_server.py`, `arduino_upload.py`, `medminder_dash/html_routes.py`, `test_admin.py`, `noxfile.py`, `docstring_audit.py`, `gen_e2e_spec_docs.py` — E501 wraps
- `scripts/tests/*`, `board_manager/tests/*`, `board_manager_client/tests/*`, `arduino_dash/tests/*`, `medminder_dash/tests/*` — auto-fixed imports/whitespace

### Gotchas

1. `ruff --fix` removes re-export imports (F401) even when tests depend on them via `patch()`. Always check test files after auto-fix.
2. `# noqa: E402` alone doesn't protect against F401 removal. Use `# noqa: E402, F401` for intentional re-exports.
---

## Phase 115 — Remove asyncio_mode pytest warning

**Date**: 2026-07-06
**Status**: ✅ COMPLETED

### Motivation

`PytestConfigWarning: Unknown config option: asyncio_mode` appeared in all 8 nox test sessions. The `asyncio_mode = "auto"` option requires `pytest-asyncio` to be installed — no package in the monorepo uses async tests.

### Scope

| File | Change | Impact |
|------|--------|--------|
| `pyproject.toml` | Remove `asyncio_mode = "auto"` from `[tool.pytest.ini_options]` | Eliminates 8 pytest warnings |

### Verification

`nox -s all_tests` — 8/8 sessions, 0 pytest warnings, 850+ tests, 0 failures.

---

## Phase 116 — djlint template reformatting

**Date**: 2026-07-06 19:42
**Status**: 🔄 IN PROGRESS

### Motivation

`djlint . --check` exits 1 with 384 files needing reformatting. However,
334 of those files are generated build output (`_site/`, `dist-standalone/`,
`docs/reference/`, `scratch/`) and only 50 are actual Jinja source templates.
The fix involves excluding generated directories and reformatting only the
real templates.

### Scope

| Quantum | Scope | Key Changes | Status |
|---------|-------|-------------|--------|
| Q1 | pyproject.toml | Add `_site|dist-standalone|docs/reference|scratch` to `extend_exclude` | 🔄 |
| Q2 | 50 templates | `djlint . --reformat` auto-formats source templates | Pending |
| Q3 | Verification | `djlint . --check` must exit 0 | Pending |

### Changes by category

| Category | Files | Action |
|----------|-------|--------|
| `pyproject.toml` | 1 | Update `[tool.djlint]` `extend_exclude` |
| `medminder_dash/.../templates/` | 25 | Auto-reformat |
| `arduino_dash/.../templates/` | 15 | Auto-reformat |
| `arduino_sketch_tools/.../templates/` | 10 | Auto-reformat |

### Verification

`pipenv run djlint . --check` — must exit 0.

## Phase 117 — Fix CI Pipeline: Install nox + swap build/test order

**Date**: 2026-07-06 20:22
**Status**: ✅ COMPLETED

### Motivation

The GitHub CI workflow (`.github/workflows/ci.yml`) calls `./scripts/ci.sh` but
two issues prevent it from succeeding in a fresh CI environment:

1. **`nox` not installed**: The workflow installs `pipenv` and root dev deps but
   never installs `nox`. The `ci.sh` script's first action is guarding for `nox`
   and it exits with error if not found.
2. **Test-before-build dependency ordering**: `ci.sh` runs `nox -s all_tests`
   before `nox -s all_builds`. The per-package test sessions call
   `pipenv lock --dev` which resolves `file://${PROJECT_ROOT}/../dist` sources
   referencing sibling monorepo packages. In a fresh CI checkout, these `dist/`
   directories don't exist (gitignored), so `pipenv lock --dev` fails with a
   resolution error.

**Fix order**: Build must precede test so that wheel files in `dist/` directories
exist when pipenv resolves dependencies during the test sessions.

### Scope

| File | Change | Impact |
|------|--------|--------|
| `.github/workflows/ci.yml` | Add `pip install nox` step before `./scripts/ci.sh` | Installs nox in CI runner |
| `scripts/ci.sh` | Swap Phase 1 (builds) and Phase 2 (tests) order | Builds create dist/ wheels before tests resolve from them |

### Dependency Chain Context

```
build(arduino-grpc)       → creates grpc_client/.../dist/   (no local deps)
build(board-manager)      → needs arduino-grpc dist/        ← depends on #1
build(board-mgr-client)   → needs arduino-grpc + bm dist/   ← depends on #1, #2
build(arduino-sketch-tools)→ needs above 3 dist/            ← depends on #1-3
build(arduino-dash)       → needs above 4 dist/             ← depends on #1-4
build(medminder-dash)     → needs above 5 dist/             ← depends on #1-5

all_builds: 7 sessions (6 packages + test_installs session)
all_tests:  7 sessions (scripts_tests + 6 per-package tests)
```

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | `scripts/ci.sh` — swap build/test order | Phase 1 = builds, Phase 2 = tests; update `--help`, docblock, echo messages | ✅ |
| Q2 | `.github/workflows/ci.yml` — add nox install | Insert `pip install nox` step before `./scripts/ci.sh` | ✅ |
| Q3 | Verification | `bash -n scripts/ci.sh` ✅, `test_ci.sh` 30/30 ✅, YAML valid ✅, `nox -s scripts_tests` 202/202 ✅ | ✅ |
| Q4 | Docs sync | All 16 agent-facing docs + user-facing docs | ✅ |

### Rollback

Each change is scoped to one file. Revert via `git checkout -- <file>`.

---

## Phase 118 — Ruff Format Audit

**Date**: 2026-07-07
**Status**: ✅ COMPLETED

**Scope**: Run `pipenv run ruff format .` across the entire monorepo.

**Result**: 111 files reformatted, 1 left unchanged. All changes cosmetic
(line wrapping, quote normalization, trailing blank lines, adjacent string
merging). Idempotency confirmed: second `--check` run reports all formatted.

**Follow-up — E501 fix**: Post-formatting `ruff check .` revealed 35 E501
errors in `scripts/add_license_headers.py` DESCRIPTIONS dict. Restructured
35 values with parenthetical line continuation. Dict type and consumer code
unchanged. Verified: `ruff check .` → 0 errors.

---

## Phase 119 — Prettier/Djlint Convergence

**Date**: 2026-07-07 02:02
**Status**: ✅ COMPLETED

**Root cause**: `.prettierrc` tabWidth=2 vs djlint default indent=4. Prettier doesn't understand Jinja2.

**Resolution**: Split formatter responsibilities — ruff (Python), prettier (non-Jinja), djlint (Jinja2), ESLint (JS).

**Changes**:
- `pyproject.toml`: `[tool.djlint]` `indent = 2`
- `.prettierignore`: Add `**/templates/`
- 50 templates reformatted with djlint indent=2

**Verification**: `djlint . --check` exit 0 ✅, `ruff check .` exit 0 ✅

---

## Phase 120 — Git Hooks

**Date**: 2026-07-06 23:04
**Status**: ✅ COMPLETED

**Goal**: Add pre-commit and pre-push git hooks to enforce code quality gates.

**Scope**:
- `.githooks/pre-commit` — ruff check, ruff format --check, djlint --check
- `.githooks/pre-push` — nox -s scripts_tests (smoke test)
- AGENTS.md — add hook setup instructions
- README.md — add quick start section
- scripts/ci.sh — add core.hooksPath reference

**Verification**: `git config core.hooksPath .githooks` ✅, `bash .githooks/pre-commit` — 0 errors ✅

### Motivation

Standardise git workflow with pre-commit lint checks and pre-push CI guard. Previously,
lint/format checks (ruff, prettier, eslint, djlint) were only run manually or in CI,
and CI failures (full `nox all_builds + all_tests`) weren't caught before pushing.

### File Structure

```
.githooks/
├── pre-commit     # Optional lint checks with [Y/n] prompt
└── pre-push       # Full CI pipeline (bash scripts/ci.sh)
```

### Pre-Commit Hook Design

- **Prompt**: `[Y/n]` with 10-second timeout, default `Y` (run checks)
- **5 checks in order**: `ruff check .` → `ruff format --check .` → `npx prettier --check "**/*.html"` → `eslint .` → `pipenv run djlint . --check`
- **Missing-tool handling**: Each check uses `command -v <tool>` to detect availability.
  If not found, prints `⚠ <tool> not found, skipping` and continues.
- **Djlint specific**: Runs `--check` only (not `--reformat`). This is a lint gate,
  not a formatter.
- **Skip with**: `n` at prompt, or `git commit --no-verify`.

### Pre-Push Hook Design

- Runs `bash scripts/ci.sh` (full `nox -s all_builds` + `all_tests`)
- **No prompt** — mandatory check
- **Blocks push** on non-zero exit (build failure or test failure)
- **Skip with**: `git push --no-verify`

### AGENTS.md Update

Added `git config core.hooksPath .githooks` setup instruction to AGENTS.md hooks section.

### Shellcheck Fixes

- `scripts/ci.sh` — fixed SC2155 (declare and assign separately)
- `scripts/tests/test_ci.sh` — fixed SC2034 (unused variable) and SC2154 (referenced but not assigned)
- Both scripts now shellcheck-clean with zero warnings
- No source logic changes — ci.sh and test_ci.sh behavior is identical

### Cleanup

`GIT_HOOKS_PLAN.md` deleted — superseded by `REVIEW_PLAN.md`.

### Verification

- `ruff check .` — 0 errors ✅
- Shellcheck on ci.sh — 0 warnings ✅
- Shellcheck on test_ci.sh — 0 warnings ✅
- hooksPath configured — `git config core.hooksPath` returns `.githooks` ✅

### Rollback

```bash
git config --unset core.hooksPath
rm .githooks/pre-commit .githooks/pre-push
```

## Phase 121 — ESLint Generated-Docs Ignore + Source Fix

**Date**: 2026-07-07 05:53
**Status**: ✅ COMPLETED

### Motivation

ESLint flagged 2201 problems (737 errors, 1464 warnings) across the monorepo. 99%+ of these were from generated documentation files (`**/docs/reference/**`, `**/scratch/**`, `**/typedoc/**`, `**/search.js`) containing large vendored JS bundles (lunr search indices, TypeDoc scripts). The remaining 6 problems were:
- 2 parsing errors: root `eslint.config.mjs` (ESM passthrough) matched the `**/*.mjs` glob with `sourceType: "script"` instead of `"module"`
- 4 `no-unused-vars` warnings: `handleFolderInput` and `uploadSketch` functions in both `base.html` templates — these are global functions called from htmx attributes that ESLint's html plugin cannot see

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | config/eslint.config.mjs ignores | Add `**/docs/reference/**`, `**/scratch/**`, `**/typedoc/**`, `**/search.js`, `eslint.config.mjs` | ✅ |
| Q2 | arduino_dash base.html | Add `/* exported handleFolderInput, uploadSketch */` for htmx callback suppression | ✅ |
| Q3 | medminder_dash base.html | Same `/* exported */` annotation | ✅ |

### Verification

`npx eslint .` — 0 errors, 0 warnings. (`--max-warnings 0` gate passes.)

### Files Modified

| File | Change |
|------|--------|
| `config/eslint.config.mjs` | 5 ignores added |
| `arduino_dash/templates/base.html` | 1 comment added |
| `medminder_dash/templates/base.html` | 1 comment added |

---

## Phase 122 — CI Restructure: Lint Phase + Nox Prompt + Standalone CI YAML

**Date**: 2026-07-07
**Status**: ✅ COMPLETED

### Motivation

Add lint Phase 0 to `ci.sh`, interactive nox install prompt, make `ci.yml` a standalone GitHub workflow independent from `ci.sh`.

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | `scripts/ci.sh` lint Phase 0 | 5 lint checks (ruff check, ruff format --check, prettier, eslint, djlint), `--skip-lint` flag, exit 5 | ✅ |
| Q2 | `scripts/ci.sh` nox prompt | Interactive 5-option nox install prompt, `--no-install` flag, non-interactive nox-missing → exit 1 | ✅ |
| Q3 | `.github/workflows/ci.yml` | Standalone with explicit steps — no `ci.sh` call | ✅ |
| Q4 | `scripts/tests/test_ci.sh` | 3 new tests, 6 updated with `--skip-lint`, 40 assertions total | ✅ |
| Q5 | User-facing docs | Updated: ci.md, reference/ci.md, test_ci.md, scripts/README.md, docs/tests.md, docs/guide.md, docs/architecture.md | ✅ |

### Verification

`bash scripts/tests/test_ci.sh` 40/40 ✅, `ruff check .` 0 errors ✅, `ruff format --check .` all formatted ✅.

---

---

## Phase 122c — Lock File Handling in ci.sh

**Date**: 2026-07-07 07:43
**Status**: 🔄 IN PROGRESS

**Motivation**: The nox `tests` session runs `pipenv lock --dev` for each package,
which modifies `Pipfile.lock` files (wheel hashes for local dependencies change
after rebuild). This leaves dirty lock files in the working tree after every CI
run. The 5 dependent packages (arduino_dash, arduino_sketch_tools, board_manager,
board_manager_client, medminder_dash) are affected. `arduino_grpc` has no local
deps so stays clean.

**Approach**: Add two interactive checks to ci.sh:
1. **Pre-check** (before Phase 1): If dirty lock files exist, warn and prompt
   to proceed (overwrite them) or abort.
2. **Post-check** (after Phase 2 completes): If lock files were newly dirtied by
   nox, list them and offer to `git restore` them selectively.

**Key decision**: Both prompts are tty-gated (`(</dev/tty)`) — skipped silently
in non-interactive contexts. Newly-dirtied files are computed by diffing the
pre-nox state against the post-nox state, so pre-existing user modifications
are preserved.

**Testing strategy**: Add `FAKE_GIT_DIRTY_LOCK_FILES` env-var bypass to ci.sh
so tests can simulate dirty lock files without touching real git. Three new
test scenarios: pre-check abort, post-check restore, post-check skip.

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | ci.sh | Pre-check (warn/abort before Phase 1), post-check (restore after Phase 2), `FAKE_GIT_DIRTY_LOCK_FILES` bypass | ✅ |
| Q2 | test_ci.sh | 3 new tests (Q18.14–Q18.16), FAKE_GIT env-var in existing tests, all pass | ✅ |
| Q3 | Docs sync | PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md, IMPLEMENTATION_*, TESTING_* | ✅ |
| Q4 | Lint + final verify | `bash -n`, ruff, `test_ci.sh` 43/43 | ✅ |

---

## Phase 122d — CI YAML: Node.js Setup for Prettier/ESLint

**Date**: 2026-07-07
**Status**: 🔄 IN PROGRESS

**Motivation**: The GitHub Actions workflow (`.github/workflows/ci.yml`) runs
`npx prettier --check` and `npx eslint .` in its lint steps, but the runner
image (ubuntu-latest) does not have Node.js pre-installed with `npx`
available. The lint steps silently fail or error out, making CI unreliable.

**Approach**: Add `actions/setup-node@v4` to install Node.js and its npm
ecosystem, followed by `npm ci` to install prettier/eslint from the root
`package-lock.json`. Place these steps right after the pipenv install step.

Also fix Jekyll build failure caused by bare `{% endblock %}` in
`docs/guide.md:366` (and `README.md:362`), which Liquid parser treats as
an unknown tag. Wrap in `{% raw %}...{% endraw %}`.

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | ci.yml | Add setup-node + npm ci steps | ✅ |
| Q2 | Jekyll fix | Wrap `{% endblock %}` in raw/endraw in docs/guide.md + README.md | 🏠 done by user |
| Q3 | Verify | Jekyll build, test_ci.sh | ✅ |
| Q4 | Docs sync | All agent-facing + user-facing docs | ✅ |

---

## Phase 122e — Fix `tests(arduino_grpc)` CI Failure

**Date**: 2026-07-07 18:17
**Status**: ✅ COMPLETED

### Motivation

`nox -s all_tests` fails in the `tests(arduino_grpc)` session because the 8 integration tests in `test_integration.py` require `arduino-cli` on PATH. The `daemon_url` fixture in `conftest.py` creates a `DaemonCtx` which runs `subprocess.Popen(['arduino-cli', 'daemon', ...])`, raising `FileNotFoundError` when the binary is absent. This happens in CI runners where `arduino-cli` is not pre-installed.

### Approach

Two-part fix:
1. **Gate with `--integration` marker** — Mirror the exact pattern from `board_manager/tests/conftest.py`: `pytest_addoption` registers `--integration`, `pytest_configure` adds the marker, `pytest_collection_modifyitems` skips integration-marked tests unless `--integration` is passed.
2. **Install `arduino-cli` in CI** — Add a step in `.github/workflows/ci.yml` that downloads and installs the Arduino CLI binary, adds it to PATH, runs `arduino-cli core update` and `arduino-cli core install arduino:avr` (required for compiles).

This keeps direct `pipenv run pytest tests/` safe locally (skips integration tests) while CI always runs the full suite with `--integration`.

### Quantums

| Q | Scope | Key Changes | Status |
|---|-------|-------------|--------|
| Q1 | `conftest.py` | Add `pytest_addoption`/`configure`/`collection_modifyitems` with `--integration` flag | ✅ |
| Q2 | `test_integration.py` | Add `@pytest.mark.integration` to all 8 test functions | ✅ |
| Q3 | `noxfile.py` | Extend `--integration` condition to include `arduino_grpc` alongside `board_manager` | ✅ |
| Q4 | `.github/workflows/ci.yml` | Add `arduino-cli` install step (curl → GITHUB_PATH → export PATH → core update + core install arduino:avr) before `nox -s all_tests` | ✅ |

### Verification

- `ruff check .` — 0 errors, 0 warnings
- `nox -s 'tests(arduino_grpc)'` — passes with `--integration` when `arduino-cli` is present, skips without it
- `nox -s all_tests` — all sessions pass
- Direct `pipenv run pytest tests/` from package dir — skips integration tests cleanly

### Design Decisions

1. **Exact board_manager pattern**: The `pytest_addoption`/`configure`/`collection_modifyitems` triple is copied verbatim from `board_manager/tests/conftest.py:26-47`. Consistent behavior across packages.
2. **`arduino-cli install` in ci.yml**: Placed right before `nox -s all_tests` (after all builds). Installing in a pre-test step ensures the binary is on PATH when nox spawns pipenv → pytest. Also installs the `arduino:avr` core platform for sketch compilation.
3. **No `--integration` passed in ci.yml**: The `ci.yml` nox step already runs `nox -s all_tests` which triggers `tests()` sessions. Since ci.yml adds `arduino-cli` to PATH, the noxfile must pass `--integration` for `arduino_grpc` (same as `board_manager`). This is done by extending the noxfile condition.

### Rollback

Each quantum is scoped to one file. Revert individual changes with `git checkout -- <file>`.

{% endraw %}
