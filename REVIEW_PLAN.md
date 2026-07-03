---
---
{% raw %}
# Review Plan — Phase 104: E2E Documentation Restructure

**Date**: 2026-06-25 16:10

**Status**: ✅ COMPLETED

## Review Criteria

### File Existence
- [x] `e2e/README.md` exists, has front matter, well-formed
- [x] `e2e/index.md` exists, has quick reference table + directory layout
- [x] `e2e/test-sketch/README.md` exists with purpose/usage documentation
- [x] `e2e/test-sketch/test-sketch.ino` exists with minimal sketch

### Content Completeness
- [x] e2e/README.md: Quick Start (MCP + automated), directory layout, requirements, related links
- [x] e2e/index.md: Quick reference table, directory layout, related links
- [x] e2e/docs/index.md: Automated Playwright Specs section with install/run/webserver/spec-summary
- [x] e2e/docs/index.md: Test Sketch section
- [x] e2e/docs/servers.md: webServer auto-management note
- [x] agent_tools/COMMAND.md: test-sketch path reference
- [x] agent_tools/AGENT.md: test-sketch step
- [x] agent_tools/GUIDE.md: test-sketch section
- [x] e2e/MCP_TESTING_GUIDE.md: mirrors GUIDE.md test-sketch content
- [x] docs/e2e-testing.md: updated quick links
- [x] Root index.md: updated e2e row

### Cross-Reference Integrity
- [x] All paths resolve (no broken relative links)
- [x] e2e/index.md links to e2e/README.md and e2e/docs/
- [x] e2e/docs/index.md links to e2e/README.md and e2e/index.md

### Verification
- [x] Jekyll build — 0 errors, 0 warnings
- [x] playwright-mcp-testing command — all steps succeed
---

## Phase 107 — E2E TypeScript API Reference (typedoc + spec extraction)

**Date**: 2026-07-03 00:30

**Status**: ✅ COMPLETED

### Review Criteria

#### File Existence
- [x] `scripts/gen_e2e_spec_docs.py` exists and is executable
- [x] `e2e/docs/reference/specs.md` exists and is well-formed
- [x] `e2e/docs/reference/typedoc/index.html` exists

#### JSDoc Annotations
- [x] `e2e/fixtures/test-data.ts`: All 5 exports have `/** */` block comments
- [x] `e2e/playwright.config.ts`: Has `@module` file-level JSDoc block

#### Script Correctness
- [x] `scripts/gen_e2e_spec_docs.py` parses all 8 spec files correctly
- [x] `scripts/gen_e2e_spec_docs.py` outputs correct test counts (22 total)
- [x] `scripts/gen_api_docs.sh` runs cleanly end-to-end (pdoc + shdoc + typedoc + specs)

#### Output Verification
- [x] typedoc output has pages for all 5 fixtures exports (3 vars + 2 functions)
- [x] typedoc output has page for playwright config default export
- [x] specs.md lists all 22 tests across 8 files
- [x] No stale typedoc output in root `./docs/`

#### Cross-Reference Integrity
- [x] README.md: "API Reference" section has links to typedoc/ and specs.md
- [x] `index.md`: "Reference Documents" table has typedoc + specs.md entries
- [x] `e2e/docs/index.md`: Document Reference includes typedoc + specs.md
- [x] `e2e/index.md`: Quick reference + directory layout updated
- [x] `e2e/README.md`: Related links + directory layout updated

#### Verification
- [x] `nox -s all_tests` — 8/8 sessions pass, 0 failures
## Phase 108 — Document Reference Tables + Broken Related Links Fix

**Date**: 2026-07-03 17:32
**Status**: ✅ COMPLETED

### Review Criteria

#### Document Reference Tables
- [x] Every module with sibling `.md` docs has a `## Document Reference` table in its `docs/index.md`
- [x] Table has 2 columns: Document (link) and Description (one-line summary)
- [x] First row is always `README -> ../README.md`
- [x] All sibling `.md` files are listed
- [x] All links resolve correctly in Jekyll build

#### Related Links
- [x] `scripts/docs/index.md` — links to tests.md, dist-test-install, dist-standalone-install
- [x] `dist-standalone-install/docs/index.md` — links to build-standalone.md + README
- [x] `dist-test-install/docs/index.md` — links to test-installs.md + tests.md

#### New Files
- [x] `dist-standalone-install/README.md` — identical to `dist-standalone/README.md`

#### Verification
- [x] `nox -s all_tests` — 8/8 sessions pass, 0 failures
- [x] `bundle exec jekyll build` — 0 errors, 0 warnings
- [x] `./scripts/gen_api_docs.sh` — clean run
{% endraw %}
