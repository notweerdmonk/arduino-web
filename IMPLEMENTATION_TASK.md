---
---
{% raw %}
# Implementation Task — Phase 104: E2E Documentation Restructure

**Date**: 2026-06-25 16:10

## Task Breakdown

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Create e2e/README.md | ✅ | Module overview, quick start, directory layout, requirements |
| Q2 | Create e2e/test-sketch/ with README | ✅ | Copy from `.playwright-mcp/`, proper README |
| Q3 | Create e2e/index.md (doc entry point) | ✅ | Like `scripts/docs/index.md` |
| Q4 | Update e2e/docs/index.md | ✅ | Automated specs + test-sketch + refocus as MCP sub-page |
| Q5 | Update e2e/docs/servers.md | ✅ | webServer auto-management note |
| Q6 | Update agent_tools docs | ✅ | COMMAND.md, AGENT.md, GUIDE.md, MCP_TESTING_GUIDE.md |
| Q7 | Update project-level docs | ✅ | docs/e2e-testing.md, root index.md |
| Q8 | End-to-end verification | ✅ | playwright-mcp-testing command run |

## Detailed Tasks

### Q1 — Create e2e/README.md

- [x] Front matter `---`
- [x] Title + brief overview of E2E testing infrastructure
- [x] Quick Start section (two modes: MCP interactive with opencode agent, automated Playwright specs)
- [x] Directory layout tree
- [x] Requirements (Python 3.10+, Node.js for automated specs)
- [x] Related links to docs/
- [x] `Assisted-by:` acknowledgement

### Q2 — Create e2e/test-sketch/

- [x] Create `e2e/test-sketch/` directory
- [x] Copy `test-sketch.ino` from `.playwright-mcp/test-sketch/`
- [x] Write `README.md` with:
  - What it is (minimal Arduino sketch for compile/upload E2E tests)
  - Purpose: verifies that the compile pipeline accepts `.ino` files and produces valid binary output
  - Usage: upload via admin page or `arduino-cli compile --fqbn ... e2e/test-sketch/`
  - Sketch content reference (`void setup() {} void loop() {}`)

### Q3 — Create e2e/index.md

- [x] Front matter `---`
- [x] Title + brief description
- [x] Quick reference table (subdirectories/features → purpose)
- [x] Directory layout tree (detailed)
- [x] Related links

### Q4 — Update e2e/docs/index.md

- [x] Refocus as MCP interactive testing sub-page
- [x] Add "Automated Playwright Specs" section:
  - [x] Install: `cd e2e && npm install`
  - [x] Run: `npx playwright test` / `--ui` / `--headed`
  - [x] webServer auto-management (playwright.config.ts starts both mock servers)
  - [x] Spec summary table (8 specs, 4 per dashboard)
- [x] Add "Test Sketch" section documenting `e2e/test-sketch/`
- [x] Update directory layout to include test-sketch and index.md
- [x] Add links to `e2e/README.md` and `e2e/index.md`

### Q5 — Update e2e/docs/servers.md

- [x] Add note about `playwright.config.ts` webServer integration

### Q6 — Update agent_tools docs

- [x] COMMAND.md: Add test-sketch path reference for compile/upload scenarios
- [x] AGENT.md: Add step about test-sketch for upload scenarios
- [x] GUIDE.md: Add test-sketch section (purpose, path, usage in scenarios)
- [x] MCP_TESTING_GUIDE.md: Mirror GUIDE.md changes

### Q7 — Update project-level docs

- [x] `docs/e2e-testing.md`: Update quick links to include `e2e/index.md`, `e2e/README.md`, `e2e/test-sketch/`
- [x] Root `index.md`: Update e2e row to point to `e2e/index.md` instead of `e2e/docs/index.md`

### Q8 — End-to-end verification

- [x] Load the playwright-mcp-testing skill: `skill(name="playwright-mcp-testing")`
- [x] Read updated guide: `read(path="e2e/agent_tools/GUIDE.md")`
- [x] Start mock server: `python3 e2e/servers/arduino_dash_server.py --mock`
- [x] Navigate to dashboard: `playwright_browser_navigate(url="http://localhost:8765")`
- [x] Verify dashboard loads: `playwright_browser_snapshot()`
- [x] Clean up: close browser, stop server
---

## Phase 104.1 — Document e2e/fixtures/ (2026-06-25 17:53) ✅ COMPLETED

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Add Test Data Fixtures section to e2e/docs/index.md | ✅ | Purpose, exports, import path, relation to --mock state documented |
| Q2 | Verify fixtures consistency across all e2e docs | ✅ | All cross-doc checks pass |

### Q1 — Add Test Data Fixtures to e2e/docs/index.md

- [x] Add "Test Data Fixtures" subsection under Automated Playwright Specs
- [x] Explain what fixtures contain: mock ports, sketch, medicines, URL helpers
- [x] Show import path from specs (`import { ... } from '../fixtures/test-data'`)
- [x] Note that fixtures mirror `--mock` server state from e2e/servers/
- [x] Clarify shelf status (available for future/refactored specs)

### Q2 — Verify fixtures consistency

- [x] Check e2e/index.md quick reference has fixture entry
- [x] Check e2e/README.md directory layout mentions fixtures
- [x] Check docs/e2e-testing.md for stale fixture references
---

## Phase 104.2 — Fix shelved-specs activation docs (2026-06-25 18:14) ✅ COMPLETED

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Add browser binary install step + project-root run config to e2e/docs/index.md | ✅ | playwright install --with-deps added, --config flag documented |

### Q1 — Update e2e/docs/index.md Installation section
- [x] Add `npx playwright install --with-deps` after `npm install` in Installation
- [x] Add project-root alternative: `npx playwright test --config e2e/playwright.config.ts`
- [x] Verified: 3/3 test scenarios pass + Jekyll build 0 errors

## Phase 104.3 — Remove shelved labels + strip agent_tools Playwright refs (2026-06-27 19:22) ✅ COMPLETED

## Phase 105 — Relocate medminder_dash and board_manager docs alongside setup.py (2026-06-27 19:22) ✅ COMPLETED

## Phase 106 — Set up Prettier + eslint-plugin-prettier for JS formatting (2026-06-28 00:54)

**Goal**: Standardize JS formatting with prettier across all HTML templates, enforce via ESLint.

**Quanta**:

1. **Config** — Create `.prettierrc` (singleQuote: false, semi: true, tabWidth: 2, useTabs: false, trailingComma: "es5") and `.prettierignore` (exclude _site, node_modules, .nox, __pycache__, .opencode, build artifacts, *.ts, *.tsx, config/eslint.config.mjs)
   - [x] Done
2. **Format** — Run `npx prettier --write "**/*.html"` across 190 HTML template files
   - [x] Done
3. **Verify** — Run `npx prettier --check "**/*.html"` to confirm all files formatted; run `npx eslint .` to confirm no new lint violations
   - [x] Done
4. **Docs** — Update CODEBASE_REFERENCE.md: directory layout, ESLint section → ESLint + Prettier, key files table with .prettierrc/.prettierignore
   - [x] Done
5. **Sync** — Update all agent-facing docs (JOURNAL.md, IMPLEMENTATION_JOURNAL.md, TESTING_*, etc.)
   - [x] Done

## Phase 107 — E2E TypeScript API Reference (typedoc + spec extraction)

**Date**: 2026-07-03 00:30

**Goal**: Generate API reference docs for `e2e/` TypeScript sources — typedoc for exported symbols (fixtures, config), Python extraction for spec test descriptions.

| # | Task | Status | Notes |
|---|------|--------|-------|
| Q1 | Add JSDoc annotations to test-data.ts + playwright.config.ts | 🔲 | @param, @returns, @module comments |
| Q2 | Write scripts/gen_e2e_spec_docs.py | 🔲 | Parse .spec.ts → specs.md |
| Q3 | Update scripts/gen_api_docs.sh | 🔲 | Add typedoc + spec extraction targets |
| Q4 | Run gen + verify output | 🔲 | Check e2e/docs/reference/ |
| Q5 | Update README.md + docs/index.md links | 🔲 | Add reference entries |
| Q6 | Sync all agent-facing docs | 🔲 | PLAN, JOURNAL, REVIEW_*, TESTING_*, CODEBASE_REFERENCE |

### Q1 — Add JSDoc annotations

- [ ] `fixtures/test-data.ts`: `/** @description */` on `MOCK_PORTS`, `MOCK_SKETCH`, `MOCK_MEDICINES`, `daemonStatusUrl()`, `boardDetailUrl()` with `@param`/`@returns`
- [ ] `playwright.config.ts`: `/** @module e2e/playwright.config */` file header with `@description`

### Q2 — Write gen_e2e_spec_docs.py

- [ ] Parse all `.spec.ts` under `e2e/specs/` using regex (stdlib `re`)
- [ ] Extract `test.describe('...', ...)` and `test('...', ...)` labels
- [ ] Output Markdown at `e2e/docs/reference/specs.md`
- [ ] Include file path, test count, describe block, test list

### Q3 — Update gen_api_docs.sh

- [ ] Add typedoc section: `npx typedoc --skipErrorChecking --out e2e/docs/reference/typedoc ...`
- [ ] Add spec extraction section: `python3 scripts/gen_e2e_spec_docs.py`
- [ ] Remove stale test output in `./docs/` (clean up typedoc's default output)

### Q4 — Generate + verify

- [ ] Run `pipenv run python3 scripts/gen_e2e_spec_docs.py` — check specs.md content
- [ ] Run typedoc target — check typedoc/ output
- [ ] Run `scripts/gen_api_docs.sh` end-to-end — clean output
- [ ] Verify `e2e/docs/reference/specs.md` lists all 22 tests across 8 spec files
- [ ] Verify typedoc picks up all 5 exports from fixtures

### Q5 — README/docs/index.md

- [ ] Add `e2e/docs/reference/specs.md` link to README.md API Reference section
- [ ] Add `e2e/docs/reference/typedoc/` link to README.md API Reference section
- [ ] Sync docs/index.md with same links

### Q6 — Agent-facing docs

- [ ] PLAN.md: Add Phase 107 entry
- [ ] JOURNAL.md: Append Phase 107 summary
- [ ] REVIEW_PLAN.md: New review checklist
- [ ] REVIEW_TASK.md: New review task items
- [ ] REVIEW_PROGRESS.md: Track review items
- [ ] REVIEW_JOURNAL.md: Record review findings
- [ ] TESTING_PLAN.md: New test scenarios
- [ ] TESTING_PROGRESS.md: Track test results
- [ ] CODEBASE_REFERENCE.md: Add typedoc + gen_e2e_spec_docs.py entries

## Phase 108 — Document Reference Tables + Broken Related Links Fix

**Date**: 2026-07-03 17:32
**Status**: ✅ COMPLETED

### Task Items

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Document Reference table | arduino_dash docs/index.md — 13 rows | ✅ |
| 2 | Document Reference table | arduino_sketch_tools docs/index.md — 4 rows | ✅ |
| 3 | Document Reference table | board_manager docs/index.md — 11 rows | ✅ |
| 4 | Document Reference table | board_manager_client docs/index.md — 2 rows | ✅ |
| 5 | Document Reference table | grpc_client docs/index.md — 4 rows | ✅ |
| 6 | Document Reference table | medminder_dash docs/index.md — 15 rows | ✅ |
| 7 | Document Reference + Related links | dist-test-install docs/index.md | ✅ |
| 8 | Create README.md | dist-standalone-install/README.md (copy) | ✅ |
| 9 | Related links | dist-standalone-install docs/index.md | ✅ |
| 10 | Related links | scripts/docs/index.md | ✅ |
| 11 | Verify nox | `nox -s all_tests` — 8/8 sessions pass | ✅ |
| 12 | Verify jekyll | `bundle exec jekyll build` — 0 errors | ✅ |
| 13 | Agent-facing docs sync | PLAN.md, JOURNAL.md, CODEBASE_REFERENCE.md, REVIEW_*, TESTING_* | ✅ |
{% endraw %}
