---
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

**Status**: 🏗️ IN PROGRESS

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
{% endraw %}
