---
---
{% raw %}
# Testing Plan — Phase 104: E2E Documentation Restructure

**Date**: 2026-06-25 16:10

**Status**: ✅ COMPLETED

## Test Strategy

This phase makes no code changes — it's a pure documentation restructure. Testing focuses on verification that:

1. All new files exist with correct content
2. All cross-references between docs resolve correctly
3. The playwright-mcp-testing command still works end-to-end with updated paths
4. Jekyll build succeeds (no broken links, no Liquid errors)

## Test Scenarios

| # | Scenario | Method | Pass Criteria |
|---|----------|--------|--------------|
| 1 | e2e/README.md exists | `test -f e2e/README.md` | File exists |
| 2 | e2e/index.md exists | `test -f e2e/index.md` | File exists |
| 3 | e2e/test-sketch/ exists | `ls e2e/test-sketch/README.md e2e/test-sketch/test-sketch.ino` | Both files present |
| 4 | e2e/docs/index.md has Automated Playwright Specs section | `grep "Automated Playwright Specs" e2e/docs/index.md` | Section present |
| 5 | e2e/docs/index.md has test-sketch mention | `grep "test-sketch" e2e/docs/index.md` | Mention present |
| 6 | e2e/docs/servers.md has webServer note | `grep -i "webServer\|playwright.config" e2e/docs/servers.md` | Note present |
| 7 | COMMAND.md has test-sketch path | `grep "test-sketch" e2e/agent_tools/COMMAND.md` | Path present |
| 8 | GUIDE.md has test-sketch section | `grep "test-sketch" e2e/agent_tools/GUIDE.md` | Section present |
| 9 | MCP_TESTING_GUIDE.md mirrors GUIDE.md | `grep "test-sketch" e2e/MCP_TESTING_GUIDE.md` | Section present |
| 10 | docs/e2e-testing.md has updated links | `grep -E "e2e/(index|README|test-sketch)" docs/e2e-testing.md` | Links present |
| 11 | Root index.md updates e2e entry | `grep "e2e/index.md" index.md` | Points to e2e/index.md |
| 12 | Jekyll build | `bundle exec jekyll build` | 0 errors, 0 warnings |
| 13 | playwright-mcp-testing command | Load skill → read guide → start server → navigate → snapshot → cleanup | All steps succeed |
---

## Phase 104.1 — Document e2e/fixtures/ (2026-06-25 17:53)

**Status**: ✅ COMPLETED

**Test Strategy**: No code changes — pure documentation addition. Testing focuses on:

1. Content existence: new fixtures section present in e2e/docs/index.md
2. Cross-references: fixtures mentioned correctly across all e2e docs
3. Jekyll build: no broken links or Liquid errors

**Test Scenarios**:

| # | Scenario | Method | Pass Criteria |
|---|----------|--------|--------------|
| 1 | e2e/docs/index.md has "Test Data Fixtures" subsection | `grep "Test Data Fixtures" e2e/docs/index.md` | Section present |
| 2 | e2e/docs/index.md mentions MOCK_PORTS | `grep "MOCK_PORTS" e2e/docs/index.md` | Export mentioned |
| 3 | e2e/docs/index.md shows import path | `grep "from.*fixtures/test-data" e2e/docs/index.md` | Import path present |
| 4 | e2e/docs/index.md mentions `--mock` relationship | `grep -i "mock" e2e/docs/index.md \| grep -i "fixture\|server"` | Server mock state relation noted |
| 5 | e2e/README.md, e2e/index.md still mention fixtures | `grep "fixtures" e2e/README.md e2e/index.md` | Present in directory layouts |
| 6 | Jekyll build | `bundle exec jekyll build` | 0 errors, 0 warnings |

## Phase 104.2 — Fix shelved-specs activation docs (2026-06-25 18:14)

**Status**: ✅ COMPLETED

**Test Scenarios**:

| # | Scenario | Method | Pass Criteria |
|---|----------|--------|--------------|
| 1 | Installation section has playwright install step | `grep "playwright install" e2e/docs/index.md` | Step present |
| 2 | Running section has --config flag alternative | `grep "config e2e/playwright.config.ts" e2e/docs/index.md` | Flag present |
| 3 | Jekyll build | `bundle exec jekyll build` | 0 errors, 0 warnings |

## Phase 104.3 — Remove shelved labels + strip agent_tools Playwright refs (2026-06-27 19:22)

## Phase 105 — Relocate medminder_dash and board_manager docs alongside setup.py (2026-06-27 19:22)

## Phase 106 — Set up Prettier + eslint-plugin-prettier for JS formatting (2026-06-28 00:54)

### Prettier Usage

Prettier formats inline JavaScript inside HTML template files. Four files with Jinja2 syntax in tag attributes are excluded via `.prettierignore`.

**Format all HTML files:**
```bash
npx prettier --write "**/*.html"
```

**Check formatting (CI/verify):**
```bash
npx prettier --check "**/*.html"
```

**Lint via ESLint (enforces prettier rules):**
```bash
npx eslint .                          # check
npx eslint . --fix                    # auto-fix
```

**Config**: `.prettierrc` — double quotes, semicolons, 2-space indent, es5 trailing commas. `.prettierignore` excludes build artifacts, TypeScript, and Jinja2-unparseable files.

### Test Scenarios

| # | Scenario | Command | Expected |
|---|----------|---------|----------|
| 1 | Prettier formatting check | `npx prettier --check "**/*.html"` | All matched files use Prettier code style |
| 2 | ESLint prettier enforcement | `npx eslint .` | 0 prettier/prettier errors |
---

## Phase 107 — E2E TypeScript API Reference (typedoc + spec extraction)

**Date**: 2026-07-03 00:30

**Status**: ✅ COMPLETED

**Test Strategy**: Verify no regressions from new/modified files (JSDoc annotations, Python extraction script, shell script update).

**Tests executed**: `nox -s all_tests`

**Test Scenarios**:
| Scenario | What it covers | Result |
|----------|---------------|--------|
| `nox -s all_tests` | 8 sessions: all_tests, scripts_tests, board_manager, board_manager_client, arduino_sketch_tools, arduino_dash, arduino_grpc, medminder_dash | ✅ 186 passed, 1 skipped, 0 failures |

**Verification Notes**:
- JSDoc annotations are comments only — no runtime effect.
- `scripts/gen_e2e_spec_docs.py` is stdlib Python — no new package dependencies.
- `scripts/gen_api_docs.sh` updates follow existing shdoc template pattern.
{% endraw %}
