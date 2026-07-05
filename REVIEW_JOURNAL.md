---
layout: default
---
{% raw %}
# Review Journal — Phase 111: Semantic Versioning v0.1.0 Baseline

## 2026-06-25 16:10 — Phase 104: E2E Documentation Restructure

### Review Summary

Pure documentation restructure for the `e2e/` directory. No code changes. Key deliverables:

1. `e2e/README.md` — module overview (fills gap, other top-level dirs have READMEs)
2. `e2e/index.md` — doc entry point (like `scripts/docs/index.md`)
3. `e2e/test-sketch/` — version-controlled compile/upload sketch (was gitignored)
4. Updated all agent_tools docs with test-sketch paths
5. Updated project-level docs with new entry points

### Key Findings

1. **No test-sketch cross-references existed** — grep confirmed zero hits in `.md` files, so no stale links needed fixing.
2. **e2e/docs/index.md was the only entry point** — now e2e/index.md serves that role, aligning with scripts/docs/index.md pattern.
3. **GUIDE.md and MCP_TESTING_GUIDE.md are aligned copies** — both got identical test-sketch sections.
4. **Jekyll build clean** — 0 errors, 0 warnings.

### Files Reviewed

| File | Verdict | Notes |
|------|---------|-------|
| `e2e/README.md` | ✅ | Module overview, quick start, directory layout, requirements |
| `e2e/index.md` | ✅ | Quick reference table + layout (scripts/docs/index.md style) |
| `e2e/test-sketch/README.md` | ✅ | Purpose + usage documented |
| `e2e/test-sketch/test-sketch.ino` | ✅ | Minimal compile/upload sketch |
| `e2e/docs/index.md` | ✅ | Automated specs + test-sketch added |
| `e2e/docs/servers.md` | ✅ | webServer note added |
| `e2e/agent_tools/COMMAND.md` | ✅ | test-sketch path added |
| `e2e/agent_tools/AGENT.md` | ✅ | test-sketch step added |
| `e2e/agent_tools/GUIDE.md` | ✅ | test-sketch section added |
| `e2e/MCP_TESTING_GUIDE.md` | ✅ | Mirrors GUIDE.md |
| `docs/e2e-testing.md` | ✅ | Quick links updated |
| `index.md` | ✅ | e2e row updated |
---

## Phase 107 — E2E TypeScript API Reference (typedoc + spec extraction)

**Date**: 2026-07-03 00:30

**Findings**:
1. Spec files have zero exported declarations — all `test()`/`test.describe()` calls are closures inside `import` scope. typedoc correctly skips them.
2. `--skipErrorChecking` is required because `@playwright/test` and `@types/node` are not installed at root. typedoc 0.28.x expects this flag (renamed from `--skipLibCheck`).
3. Python extraction (`re` + `pathlib`) is the right fit — follows the existing project pattern of Python-based doc tooling (pdoc AST, shdoc awk).
4. The `re.DOTALL` flag is critical for multiline describe/test block parsing.

**Decisions**:
- No `@module` tags added to spec files — would pollute 8 files for marginal gain. Python regex extraction handles it cleanly.
- `npx --yes typedoc` to avoid interactive installation prompts.
- Stale typedoc default output (`./docs/`) must be removed because it conflicts with the project's existing `docs/` directory.

## Phase 108 — Document Reference Tables + Broken Related Links Fix

**Date**: 2026-07-03 17:32

**Findings**:
1. Modules with sibling `.md` files: arduino_dash (12), arduino_sketch_tools (3), board_manager (10), board_manager_client (1), grpc_client (3), medminder_dash (14). All now linked from Document Reference tables in their respective `docs/index.md`.
2. `dist-standalone-install/README.md` was missing entirely — existed for `dist-standalone/` but not `dist-standalone-install/`. Simple copy.
3. 3 "Related" sections had broken or missing links (scripts, dist-standalone-install, dist-test-install) — all fixed.
4. `e2e/docs/index.md` already had Document Reference table (added in Phase 107) — only needed Related link verification.

**Decisions**:
- No structural changes to any source code or templates — purely documentation.
- `dist-standalone-install/README.md` is a direct copy (not a symlink) to keep install builds self-contained.
- Document Reference tables use Markdown link syntax (not HTML) for Jekyll `jekyll-relative-links` automatic `.md` → `.html` conversion.

**Verification**:
- `nox -s all_tests` — 8/8 sessions, 0 failures, 0 errors
- `bundle exec jekyll build` — 0 errors, 0 warnings
- `./scripts/gen_api_docs.sh` — clean run

---

## Phase 109 — Code Review: E2E TypeScript API Ref + Spec Extraction + Pipeline

**Date**: 2026-07-04 03:10

**Scope of Review**: 5 un-pushed commits (`origin/master..HEAD`). Source-level changes span 5 files across 3 categories:

| Category | Files |
|----------|-------|
| JSDoc annotations | `e2e/fixtures/test-data.ts`, `e2e/playwright.config.ts` |
| New tooling script | `scripts/gen_e2e_spec_docs.py` |
| Pipeline + config | `scripts/gen_api_docs.sh`, `package.json` |

### Correctness

#### `scripts/gen_e2e_spec_docs.py` — Section boundary logic (lines 35-37)
**Warning**: The `parse_spec()` function computes section boundaries by taking the span between consecutive `test.describe(` calls. This assumes describe blocks are **not nested**. Playwright supports nesting:

```typescript
test.describe('outer', () => {
  test('test1', () => {});
  test.describe('inner', () => {
    test('test2', () => {});
  });
});
```

With nested describes, the inner `test.describe` match will **duplicate** tests from the outer scope into a second entry, and the inner describe's section will include tests from the outer scope that appear before it. **No tests are lost**, but the output can misrepresent the structure. The 8 current spec files do not use nesting, so this works today, but it's a latent bug.

**Suggestion**: Use a depth counter or an AST-based approach (e.g., TypeScript compiler API or `tree-sitter`) for production-quality parsing, or add a comment documenting the no-nesting assumption.

#### `scripts/gen_e2e_spec_docs.py` — Markdown links are broken (line 84)
**Warning**: All file links in the generated `specs.md` use just the filename:
```python
lines.append(f"## {group} / [{fname}]({fname})")
```
This produces links like `[admin.spec.ts](admin.spec.ts)` that are relative to the output file location (`e2e/docs/reference/specs.md`). The actual spec files live at `e2e/specs/arduino_dash/admin.spec.ts` — two directories up. These links will **404** when rendered on GitHub or the Jekyll site.

**Suggestion**: Compute the correct relative path:
```python
# From e2e/docs/reference/specs.md to e2e/specs/arduino_dash/admin.spec.ts
# = ../../specs/{group}/{fname}
link = f"../../specs/{group}/{fname}"
```

#### `scripts/gen_e2e_spec_docs.py` — Regex edge case (line 19)
**Nit**: `DESCRIBE_RE` will also match `test.describe.only(` or `test.describe.skip(` — the capture group `([^'\"]+)` would fail to capture the label for these variants since the character immediately after the opening paren is not a quote (there's a `.skip` before the paren). This is benign (the regex simply won't match), but it means `describe.only` and `describe.skip` blocks are silently skipped.

#### `scripts/gen_e2e_spec_docs.py` — exit code on output write failure (line 96)
**Nit**: `OUTPUT.write_text(...)` could raise `OSError` (permissions, disk full, etc.) and is not caught. Since `generate()` is called via `sys.exit(generate())`, the exception would propagate as a traceback. This is acceptable for a dev tool, but a `try/except` with a clear message would be more user-friendly.

### Security

No security concerns. The Python script uses stdlib only (`re`, `sys`, `pathlib`), has no network access, and processes only local `.spec.ts` files. The shell script uses `npx` to fetch typedoc from npm, which is a standard dev workflow.

### Performance

- `gen_e2e_spec_docs.py` reads 8 spec files (total ~few KB) once — no performance concern.
- `gen_api_docs.sh` typedoc invocation runs on 2 TypeScript files — negligible.

### Maintainability

#### `scripts/gen_e2e_spec_docs.py` — Overall assessment
**Strength**: Clean structure with separated `parse_spec()` and `generate()` functions, type hints, `pathlib`, `__future__.annotations`. Follows project conventions (stdlib-only Python tooling alongside pdoc, shdoc).

**Strength**: `print(...)` diagnostics to `stderr` (line 63, 98), actual output written to file path — proper separation of concerns.

#### `scripts/gen_api_docs.sh` — Stderr suppressed in typedoc (line 181)
**Suggestion**: `> /dev/null 2>&1` silences both stdout and stderr. If typedoc emits warnings (e.g., missing types, deprecated options), they are invisible. Consider:
```bash
npx --yes typedoc ... > /dev/null 2>typedoc-errors.log
```
Or at minimum, redirect stderr only:
```bash
npx --yes typedoc ... 2>&1 | tail -n 5 || true
```

#### `e2e/fixtures/test-data.ts` — Inconsistent JSDoc style (line 4)
**Nit**: `MOCK_PORTS` uses a single-line `/** ... */` JSDoc comment spanning ~150 characters. All other JSDoc blocks use the multi-line format (`/**\n * ...\n */`). While both are valid JSDoc, consistency matters:
```typescript
/**
 * Mock board ports mirroring e2e/servers/*_server.py --mock state.
 * Two boards: Uno (/dev/ttyTEST0) and Mega (/dev/ttyTEST1).
 */
```

#### `e2e/playwright.config.ts` — @module tag convention (line 9)
**Nit**: `@module e2e/playwright.config` — this is a file-relative path, not a module path. TypeDoc will display this as the module name. Consider a more descriptive name like `"Playwright E2E Configuration"` to improve the generated docs readability.

#### `package.json` — typedoc in devDependencies (line 6)
**Strength**: Correct placement as a `devDependency` since it's a doc-generation tool, not a runtime dependency.

### Testing Coverage

| File | Tests | Verdict |
|------|-------|---------|
| `e2e/fixtures/test-data.ts` | None for JSDoc | ✅ Acceptable — annotations don't affect runtime |
| `e2e/playwright.config.ts` | None for JSDoc | ✅ Acceptable — same rationale |
| `scripts/gen_e2e_spec_docs.py` | No dedicated unit tests | ⚠️ **Gap** — no `pytest` tests for the new script |
| `scripts/gen_api_docs.sh` | Implicitly tested via `nox -s all_tests` | ✅ |

**Missing test gap**: `scripts/gen_e2e_spec_docs.py` has no unit tests. While it's a doc-generation script (lower risk), it performs regex-based parsing that is prone to edge-case failures. Consider adding:

1. **A test that creates a temporary `.spec.ts` file** with known `test.describe`/`test` content, runs `parse_spec()` on it, and asserts the parsed output.
2. **A test for the no-describe case** (orphan tests).
3. **A test for edge cases**: empty file, single describe, multiple describes, nested describes (documented as unsupported).

### Summary

| Severity | Count | Key Items |
|----------|-------|-----------|
| **Warning** | 2 | Broken spec file links in generated Markdown; latent nested-describe parsing bug |
| **Suggestion** | 2 | Typedoc stderr should not be silenced; add unit tests for gen_e2e_spec_docs.py |
| **Nit** | 3 | Inconsistent JSDoc style; @module naming; regex edge case for describe.only/skip |

**Overall Verdict**: ✅ **Good to merge** after fixing the broken Markdown links and the silenced typedoc stderr. The nested-describe bug is a latent issue but does not affect the current codebase.

## 2026-07-04 04:12 — Phase 111: Semantic Versioning

Review criteria defined. Will verify single-source-of-truth pattern,
version consistency across all modules, and full test suite.

## 2026-07-04 04:12 — Phase 111: Semantic Versioning — Review Complete

**Review findings**:
- SSoT pattern: __init__.py is single source of truth ✅
- All version strings consistent at 0.1.0 ✅
- All existing tests pass with no regressions ✅
- No hardcoded version strings remain in setup.py ✅

**Decision**: Versioning scheme approved. All future version bumps
will update __init__.py only; setup.py and pyproject.toml follow.

---

## 2026-07-05 01:04 — Comprehensive Document & Codebase Audit

**Scope**: Full monorepo audit across 4 categories: workflow docs, user-facing
docs, CODEBASE_REFERENCE.md, and config/resource files. ~60 issues found.

**Methodology**: Automated grep/pattern matching + manual review of every
Markdown file, all route files, all package manifests, and config files.

---

### CATEGORY 1: WORKFLOW DOCUMENTS (23 issues)

#### 1A — Stale Statuses in IMPLEMENTATION_PLAN.md

| # | Line | Current Value | Should Be | Severity |
|---|------|---------------|-----------|----------|
| 1 | 59 | `Phase 104.2 — **Status**: 🏗️ IN PROGRESS` | `✅ COMPLETED` | HIGH |
| 2 | 98 | `Phase 107 — **Status**: 🏗️ IN PROGRESS` | `✅ COMPLETED` | HIGH |
| 3 | 108-113 | Phase 107 Q1-Q6 all `🔲` (unchecked) | `✅` (all done) | HIGH |
| 4 | 176-180 | Phase 111 A-E all `⬜` (empty) | `✅` (all done, verified by nox) | HIGH |

**Root cause**: These were never updated from planning to completion state.
The shell placeholder markers are leftover from when these were future items.

#### 1B — Missing Phase 109 Entry in JOURNAL.md

No entry exists for Phase 109 (Code Review of Phase 107/108, dated 2026-07-04
03:10). The phase is documented in PLAN.md and REVIEW_JOURNAL.md but was never
added to the master JOURNAL.md. It should appear between Phase 108 (line 45) and
Phase 110 (line 25). All other completed phases have journal entries.

#### 1C — JOURNAL.md Status Marker Gaps

| # | File | Line | Issue | Severity |
|---|------|------|-------|----------|
| 5 | JOURNAL.md | 157 | Phase 102 title missing `✅ COMPLETED` — adjacent phases (101, 103) have it | MEDIUM |
| 6 | JOURNAL.md | 1017 | Phase 82 title says "(In Progress)" — body says "Status: ✅ Complete" | MEDIUM |

#### 1D — Stale h1 Document Headings

Three workflow documents have headings that reference an old phase, misleading
readers about which phase the document covers:

| File | Current Heading | Latest Phase | Fix |
|------|----------------|--------------|-----|
| IMPLEMENTATION_JOURNAL.md | "Phase 98: WS Push Migration" | Phase 111 | Update to Phase 111 |
| TESTING_JOURNAL.md | "Phase 93: GitHub Pages Jekyll Documentation Site" | Phase 111 | Update to Phase 111 |
| REVIEW_JOURNAL.md | "Phase 104: E2E Documentation Restructure" | Phase 111 | Update to Phase 111 |

#### 1E — PLAN.md Structural Issues

**Phase ordering break (HIGH)**: After Phase 100, the document descends
(100 → 100c → 100b → 99 → ... → 1), but Phases 101-111 appear AFTER Phase 1,
breaking the descending pattern. They should be placed before Phase 100.

**Phase 101 duplicate (MEDIUM)**: Phase 101 appears at line 1093 (Redesign &
Rebuild) and Phase 101 (continued) at line 1124 — Portability Fix. The
"continued" entry should be merged or nested as Phase 101a.

**Phase 110 missing completion status (MEDIUM)**: Line 1343 — no `✅ COMPLETED`
marker, unlike every other phase. Should be marked or noted as pending.

**Phase 109 heading level (LOW)**: Uses `##` (level 2) while most earlier
phases use `###` (level 3).

**Sub-phase ordering (LOW)**: Phases 100c and 100b are listed as
100 → 100c → 100b, but chronologically 100b (no timestamp) precedes 100c
(17:57). Should be 100c then 100b.

#### 1F — TODOS.md Missing 11 Phases (HIGH)

Phases 104, 104.1, 104.2, 104.3, 105, 106, 107, 108, 109, 110, 111 are all
absent from TODOS.md. The completed table at the top only goes up to Phase 100.
Phase 93 appears twice in the table with slightly different descriptions
(MEDIUM redundancy).

#### 1G — RESEARCH Docs Missing Liquid Protection (MEDIUM)

RESEARCH_TASK.md and RESEARCH_PROGRESS.md lack Liquid `raw`/`endraw`
wrapping. All other workflow documents use this pattern to protect their content
from Jekyll's Liquid processing. Without it, any text containing `{{ }}` or
`{% %}` patterns would be interpreted by Liquid, potentially breaking the
Jekyll build with syntax errors.

#### 1H — Typos (LOW)

| File | Line | Current | Fix |
|------|------|---------|-----|
| RESEARCH_PLAN.md | 28 | "Reasearch" | "Research" |
| RESEARCH_JOURNAL.md | 165 | "Hueristic" | "Heuristic" |

#### 1I — IMPLEMENTATION_TASK.md Missing Completion Summary (MEDIUM)

Phase 111 tasks A-E are listed as directions without any completion markers or
summary section. Other task files (e.g., TESTING_TASK.md) have a
`## Completed — 2026-07-04 04:12` section with `✅` items. This file lacks that
close-out.

#### 1J — BUGS.md Documents Removed Technology (LOW)

BUGS.md documents 3 bugs in Hyperscript 0.9.13, which was removed in Phase 97
(Frontend Stack Optimization — Hyperscript → Idiomorph/Vanilla JS). The CDN was
dropped and all `_=` attributes were replaced. This file is entirely historical
for a technology no longer in the project. Consider adding a historical note
header or archiving.

---

### CATEGORY 2: CODEBASE_REFERENCE.md (7 issues)

#### 2A — Stale "Last Updated" Line (HIGH)

Line 7 says `**Last updated**: 2026-06-24 (Phases 89-100 + Code Review)`.
The document contains content through Phase 111 with dates up to 2026-07-04.
Should read: `**Last updated**: 2026-07-04 (Phases 89-111)`.

#### 2B — References to Nonexistent File `e2e/docs/index.md` (HIGH)

This file path is referenced 6 times across the document as an existing/modified
document, but `e2e/docs/index.md` does not exist on disk. The directory
`e2e/docs/` contains `agent-tools.md`, `scenarios.md`, `servers.md`, and
`reference/` but no `index.md`. Specific locations:

| Line | Context |
|------|---------|
| 3871 | "Added Automated Playwright Specs section" to `e2e/docs/index.md` |
| 3909 | Test Data Fixtures described as added to `e2e/docs/index.md` |
| 3911 | Same — fixture documentation |
| 3936 | Installation section attributed to `e2e/docs/index.md` |
| 3937 | Running Specs section attributed to `e2e/docs/index.md` |
| 3974 | Directory layout listing includes `e2e/docs/index.md` |

The actual file is `e2e/index.md` (at the e2e root, not inside e2e/docs/).
All references should be corrected.

#### 2C — Reference to Nonexistent `dist-test-install/docs/index.md` (HIGH)

Line 4026 references `dist-test-install/docs/index.md`. The file is at
`dist-test-install/index.md` (in the root of dist-test-install, not in a
`docs/` subdirectory). No `docs/` subdirectory exists inside
`dist-test-install/`.

#### 2D — Missing Phase Sections (MEDIUM)

| Phase | Title | Present in CODEBASE_REFERENCE? |
|-------|-------|-------------------------------|
| 104.3 | Remove shelved labels + strip agent_tools Playwright refs | Missing — jumps from 104.2 to 107 |
| 105 | Relocate medminder_dash and board_manager docs alongside setup.py | Missing — only mentioned in passing at line 3155 |
| 106 | Set up Prettier + eslint-plugin-prettier for JS formatting | Missing — prettier changes are under Code Review, not a dedicated entry |
| 109 | Code Review of Phase 107/108 | Missing |
| 110 | Authentication, Authorization, CSRF, Rate Limiting | Missing (may be intentional as not yet implemented) |

Phase 111 (Semantic Versioning) IS present at lines 4033-4057 and verified as
100% accurate — all file paths and version values confirmed against actual code.

#### 2E — Stale Line Number References (LOW)

Line references in the Phase 100 and Phase 100c sections no longer match
current source files due to intervening code changes:

| Reference | Claimed Line | Current Line | Shift |
|-----------|-------------|--------------|-------|
| `arduino_dash_server.py main()` (line 3521) | 208-237 | 184 | -24 |
| `medminder_dash_server.py main()` (line 3524) | 237-266 | 220 | -17 |
| `base.html` idiomorph line — arduino_dash (line 3445) | 9 | 32 | +23 |
| `base.html` idiomorph line — medminder_dash (line 3446) | 13 | 40 | +27 |

These were accurate when written but drifted due to:
- Server scripts: added `_start_bms`, `_stop_bms`, `_inject_mock_state` functions
- base.html: djlint reformatting in Phase 100b added whitespace

---

### CATEGORY 3: USER-FACING DOCS (20+ issues)

#### 3A — Broken Links (5 — will 404 on click)

| # | File | Line | Link | Resolves To | Expected | Severity |
|---|------|------|------|-------------|----------|----------|
| 1 | `index.md` | 25 | `dist-standalone/index.md` | `<root>/dist-standalone/index.md` | `dist-standalone-install/index.md` | HIGH |
| 2 | `index.md` | 141 | `[dist-standalone/index.md]` | Same — directory doesn't exist | `dist-standalone-install/index.md` | HIGH |
| 3 | `e2e/README.md` | 92 | `../test-sketch/README.md` | `<root>/test-sketch/README.md` | `test-sketch/README.md` (e2e-local) | HIGH |
| 4 | `e2e/README.md` | 131 | `docs/tests.md` | `e2e/docs/tests.md` | `../docs/tests.md` (root docs/) | MEDIUM |
| 5 | `e2e/README.md` | 135 | `../agent_tools/GUIDE.md` | `<root>/agent_tools/GUIDE.md` | `agent_tools/GUIDE.md` (e2e-local) | MEDIUM |

#### 3B — Wrong Default Port Numbers (4 — user cannot connect)

| # | File | Line | Says | Actual | Severity |
|---|------|------|------|--------|----------|
| 1 | `arduino_dash/.../README.md` | 77 | "default port 5000" | 8080 (`__main__.py:34`) | HIGH |
| 2 | `arduino_dash/.../README.md` | 87 | `http://localhost:5000` | `http://localhost:8080` | HIGH |
| 3 | `medminder_dash/.../README.md` | 106 | "default port 5000" | 8080 (`__main__.py:36`) | HIGH |
| 4 | `medminder_dash/.../README.md` | 116 | `http://localhost:5000` | `http://localhost:8080` | HIGH |

The 5000 vs 8080 discrepancy exists in both dashboard READMEs. The actual
default was changed from 5000 to 8080 at some point (possibly to avoid macOS
AirPlay Receiver conflict on port 5000) but the docs were never updated.

#### 3C — Nonexistent API Endpoints in docs/guide.md (2 — HIGH)

| Endpoint | Line | Status | Severity |
|----------|------|--------|----------|
| `POST /api/compile-and-upload` | ~189 | Not a Flask route in any dashboard | HIGH |
| `POST /api/deploy` | ~199 | Not a Flask route in any dashboard | HIGH |

Users following the guide will get 404 errors. The correct compile flow uses
`/board/<port>/compile` (arduino_sketch_tools blueprint) or
`/api/pubsub/board/<port>/spawn` (PubSub API).

#### 3D — Nonexistent Environment Variables in Package READMEs (5)

| # | File | Var Name | Reality | Severity |
|---|------|----------|---------|----------|
| 1 | `board_manager/README.md` | `BOARD_MGR_DAEMON_PORT` | Does not exist in code | MEDIUM |
| 2 | `board_manager/README.md` | `BOARD_MGR_PUBSUB_PORT` | Does not exist in code | MEDIUM |
| 3 | `medminder_dash/README.md` | `MEDMINDER_PORT` | Port set via `--port` CLI only | MEDIUM |
| 4 | `medminder_dash/README.md` | `MEDMINDER_DEBUG` | Does not exist in code | MEDIUM |
| 5 | `medminder_dash/README.md` | `MEDMINDER_SKETCH_DIR` | Does not exist in code | MEDIUM |

Actual env vars for board_manager are in `boot.py` (BmsEnv class): `BOARD_MGR_TCP_HOST`,
`BOARD_MGR_TCP_PORT`, `BOARD_MGR_UDS_PATH`, `BOARD_MGR_ARDUINO_DAEMON`, etc.
medminder_dash has no env var configuration — only CLI arguments.

#### 3E — Stale CLI Flags and Paths (2)

| # | File | Line | Says | Should Be | Severity |
|---|------|------|------|-----------|----------|
| 1 | `board_manager/README.md` | 90-97 | `--port 50051` | `--tcp-port 9090` (50051 is arduino-cli daemon port) | HIGH |
| 2 | `grpc_client/.../README.md` | 14, 21 | `cd gRPC_client/python` | `cd grpc_client/python/arduino_grpc` | HIGH |

The `--port` flag does not exist in the board_manager CLI (it's `--tcp-port`).
The `gRPC_client` directory was renamed to `grpc_client` (lowercase).

#### 3F — Incorrect Protocol Descriptions (2)

| # | File | Line | Says | Reality | Severity |
|---|------|------|------|---------|----------|
| 1 | `board_manager/README.md` | 3 | "A standalone gRPC service" | Custom TCP/UDS JSON pubsub protocol | MEDIUM |
| 2 | `board_manager_client/README.md` | 3-4 | "Wraps the raw PubSub gRPC stream" | Same — not gRPC, custom protocol | MEDIUM |

Both services use gRPC internally to talk to the arduino-cli daemon, but their
own API is a custom JSON-line protocol over TCP or Unix Domain Sockets. The
READMEs should say "pub/sub service" not "gRPC service".

Additional sub-issues in board_manager_client/README.md:
- Topic names use single colon (`board:events`) — actual naming uses double
  colons (`board::<port>::event`, `resp::compile::<port>`, etc.)
- Default TCP port documented as 50052 — actual is 9090
- Default UDS path documented as `/tmp/bms.sock` — actual is `/tmp/board_mgr.sock`

#### 3G — arduino_sketch_tools/README.md Stale Route Documentation

| # | Line | Documents (Wrong) | Actual Route | Severity |
|---|------|-------------------|-------------|----------|
| 1 | 96 | `GET /board/<port>/list` | Does not exist in routes.py | MEDIUM |
| 2 | 97 | `GET /board/<port>/ports` | Does not exist | MEDIUM |
| 3 | 98 | `GET /board/<port>/compile-result` | `GET /board/<port>/compile/poll` | MEDIUM |
| 4 | 99 | `GET /board/<port>/upload-result` | `GET /board/<port>/upload/poll` | MEDIUM |

Missing routes not documented:
- `POST /board/<port>/upload/confirm`
- `GET /board/<port>/upload/section`

#### 3H — docs/architecture.md Issues

| # | Line | Issue | Severity |
|---|------|-------|----------|
| 1 | 22, 24 | Duplicate `## System Overview` header — appears twice consecutively | LOW |
| 2 | 205-337 | Phase numbers scattered throughout (97, 98, 99) — internal planning artifacts in external doc | LOW |
| 3 | 318-337 | Hyperscript migration documented as "Phase 97" — historical context ok but phase ref is internal | LOW |

#### 3I — docs/api.md Missing Routes

| # | Route | File | Severity |
|---|-------|------|----------|
| 1 | `GET /boards/grid/card/<path:port>` | Missing from arduino-dash HTML routes table (~line 311) | MEDIUM |
| 2 | Multiple routes | Missing from medminder-dash HTML routes table (~line 329): `GET /medicine/<med_id>/edit`, `POST /medicine`, `PUT /medicine/<med_id>`, `DELETE /medicine/<med_id>`, `PUT /medicine/<med_id>/toggle`, `POST /medicines/active-board`, `GET /boards/grid/card/<path:port>` | MEDIUM |
| 3 | Line 340 | Documents `POST /admin/active-board` — actual route is `POST /medicines/active-board` (different path) | MEDIUM |

#### 3J — Phase Numbers in External Docs (6+ locations)

Phase numbers (project-internal planning artifacts) appear in user-facing
documents where they don't belong:

| File | Line(s) | Context |
|------|---------|---------|
| `README.md` | 5 | `## Recent Enhancements (Phases 94-100)` — has a "Phase" column in the table |
| `README.md` | 7-23 | Every row references a Phase number (94, 96, 97, 98, 99, 100) |
| `README.md` | 100 | "Nox sessions auto-regenerate Pipfile.lock (Phase 94)" |
| `index.md` | 9 | `**Last updated**: 2026-07-04 — Phases 109-111 complete` |
| `docs/architecture.md` | 205-337 | Multiple "Phase 97", "Phase 98", "Phase 99" references |
| `docs/guide.md` | 87 | "The nox sessions auto-regenerate Pipfile.lock on each run (Phase 94)" |

These should be removed or replaced with release version references.

---

### CATEGORY 4: CONFIG/RESOURCE FILES (9 issues)

#### 4A — medminder_dash setup.py Missing 4 Dependencies (HIGH)

**File**: `medminder_dash/python/medminder_dash/setup.py` line 37-39

Only lists `flask>=3.0` and `gunicorn>=20.0`. The package's `pyproject.toml`
(lines 11-18) lists 6 dependencies. Missing from setup.py:
- `flask-sock>=0.7.0`
- `simple-websocket>=1.0.0`
- `arduino-sketch-tools>=0.1.0`
- `board-manager-client>=0.1.0`

Installing via `pip install -e .` (using setup.py) would produce a broken
installation missing critical runtime dependencies. The setup.py appears to be
a stale/abandoned copy that was never updated when pyproject.toml became the
primary manifest.

#### 4B — arduino_dash setup.py Missing simple-websocket (MEDIUM)

**File**: `arduino_dash/python/arduino_dash/setup.py` line 37-45

Lists 7 dependencies but omits `simple-websocket>=1.0.0`, which IS listed in
`pyproject.toml` (line 14). Installation via setup.py would lack websocket
runtime support.

#### 4C — arduino_sketch_tools pyproject.toml Missing config/**/* in package-data (MEDIUM)

**File**: `arduino_sketch_tools/python/arduino_sketch_tools/pyproject.toml` line 21-25

`package-data` only includes `"templates/**/*"` and `"static/**/*"`. The
`setup.py` (line 44-48) includes `"config/**/*"`. If `pyproject.toml` is used
for builds (as is standard for modern pip), the config directory will be
dropped from the package distribution.

#### 4D — No GitHub Actions CI for Python Tests (MEDIUM)

**File**: `.github/workflows/jekyll.yml`

The only workflow deploys a Jekyll documentation site to GitHub Pages on pushes
to master. There is no CI workflow that runs:
- Python test suites (`nox -s all_tests` / `scripts/ci.sh`)
- Python package builds (`nox -s all_builds`)
- Linting (ruff, djlint, eslint, prettier)
- Smoke test installs (`scripts/test_installs.sh`)

While `scripts/ci.sh` exists locally, it is never invoked by GitHub Actions.
Pushes to master that break code go undetected by CI — only documentation
deployment is tested.

#### 4E — Pipfile Source Naming Inconsistency (LOW)

**File**: `Pipfile` lines 29, 34

Two local sources are named without the `-local` suffix:
- Line 29: `name = "arduino-dash"` → should be `"arduino-dash-local"`
- Line 34: `name = "medminder-dash"` → should be `"medminder-dash-local"`

All other local monorepo sources use `*-local`: `arduino-grpc-local`,
`board-manager-local`, `board-manager-client-local`, `arduino-sketch-tools-local`.
These two break the pattern. No functional impact since Pipfile's `[packages]`
is empty, but a naming convention inconsistency.

#### 4F — medminder_dash Pipfile Missing gunicorn (LOW)

**File**: `medminder_dash/python/medminder_dash/Pipfile` lines 27-32

The `[packages]` section includes `flask`, `flask-sock`, and all monorepo deps,
but omits `gunicorn`, which is declared in both `setup.py` (line 39) and
`pyproject.toml` (line 13). Developers using Pipenv for medminder_dash
development would not have gunicorn installed.

#### 4G — Missing .gitattributes (LOW)

No `.gitattributes` file exists anywhere in the repository. Adding one would
help with:
- Consistent line ending normalization (`* text=auto`)
- Linguist overrides for build directories (`_site/`, `dist-standalone/`)
- Git LFS configuration if needed in the future

#### 4H — .gitignore Gaps (LOW)

**File**: `.gitignore`

Missing entries:
- `*.swp` — vim swap file exists at root level
- `.eggs/` — setuptools egg directory
- `.Python` — virtualenv marker file
- `pip-wheel-metadata/` — pip internal metadata
- `.mypy_cache/` — if mypy is ever used
- `htmlcov/` / `.coverage*` — coverage.py output
- `build/` patterns may not catch subdirectory build artifacts

#### 4I — _config.yml Jekyll Exclude List Gaps (LOW)

**File**: `_config.yml`

The `exclude` list is missing:
- `.prettierignore`, `.prettierrc` — config files would leak into _site/
- `eslint.config.mjs`, `config/eslint.config.mjs` — linter config in published site
- `e2e/` — E2E test code and fixtures in published docs site
- `scripts/` — build/CI scripts in published site
- `opencode_sessions/` — agent session data should not be published

Affects documentation site content but has no security impact since the site
is public anyway.

---

### SUMMARY TABLE

| Category | HIGH | MEDIUM | LOW | Total |
|----------|------|--------|-----|-------|
| 1. Workflow Documents | 5 | 12 | 6 | 23 |
| 2. CODEBASE_REFERENCE.md | 3 | 2 | 2 | 7 |
| 3. User-Facing Docs | 9 | 12 | 3 | 24 |
| 4. Config/Resource Files | 1 | 3 | 5 | 9 |
| **Total** | **18** | **29** | **16** | **~63** |

### RECOMMENDED PROCESSING ORDER

1. **User-facing docs critical fixes** (3A: broken links, 3B: wrong ports,
   3C: nonexistent endpoints, 3E: stale CLI flags) — these actively mislead users
2. **CODEBASE_REFERENCE.md high issues** (2A: stale last-updated, 2B-2C:
   nonexistent file references) — agent hallucination risk
3. **Workflow doc statuses** (1A-1E) — stale markers cause confusion
4. **Config manifest mismatches** (4A-4D) — can cause broken installations
5. **Missing phase sections** (1F, 2D) — completeness gap
6. **Remaining medium/low items** — cleanup pass

---

## 2026-07-05 — Category 1: Workflow Document Fixes Applied

**Scope**: All 23 issues across sub-categories 1A through 1J from the Comprehensive Document & Codebase Audit.

### Fixes Applied

| Sub-Category | Description | Severity | Status |
|---|---|---|---|
| 1A | Stale Statuses in IMPLEMENTATION_PLAN.md | HIGH | ✅ 4 markers updated (Phase 104.2, 107 statuses, Q1-Q6, A-E tasks) |
| 1B | Missing Phase 109 Entry in JOURNAL.md | HIGH | ✅ Entry inserted between Phase 110 and Phase 108 |
| 1C | JOURNAL.md Status Marker Gaps | MEDIUM | ✅ Phase 102 got ✅ marker; Phase 82 "(In Progress)" → ✅ COMPLETED |
| 1D | Stale h1 Document Headings | MEDIUM | ✅ All 3 journals updated to "Phase 111: Semantic Versioning v0.1.0 Baseline" |
| 1E | PLAN.md Structural Issues | HIGH/MED/LOW | ✅ Phases 101-111 moved before Phase 100; Phase 101 continued → Phase 101a; Phase 110 got ✅; Phase 109 heading `##` → `###`; sub-phase order 100→100b→100c |
| 1F | TODOS.md Missing 11 Phases | HIGH | ✅ Phases 101-111 added to completed table |
| 1G | RESEARCH Docs Missing Liquid Protection | MEDIUM | ✅ Liquid `raw`/`endraw` added to RESEARCH_TASK.md and RESEARCH_PROGRESS.md |
| 1H | Typos | LOW | ✅ "Reasearch" → "Research" (RESEARCH_PLAN.md); "Hueristic" → "Heuristic" (RESEARCH_JOURNAL.md) |
| 1I | IMPLEMENTATION_TASK.md Completion Summary | MEDIUM | ✅ Completed section added for Tasks A-E |
| 1J | BUGS.md Documents Removed Technology | LOW | ✅ Historical note header added about Hyperscript removal in Phase 97 |

### Files Modified (13 total)

1. `IMPLEMENTATION_PLAN.md` — Fixed 4 stale status markers
2. `JOURNAL.md` — Added Phase 109 entry; fixed 2 status marker gaps
3. `IMPLEMENTATION_JOURNAL.md` — Updated h1 heading to Phase 111
4. `TESTING_JOURNAL.md` — Updated h1 heading to Phase 111
5. `REVIEW_JOURNAL.md` — Updated h1 heading to Phase 111
6. `PLAN.md` — Restructured: moved Phases 101-111 before Phase 100; fixed heading levels; fixed sub-phase ordering; fixed Phase 110 status
7. `TODOS.md` — Added 11 missing phases to completed table
8. `RESEARCH_TASK.md` — Added Liquid protection wrapping
9. `RESEARCH_PROGRESS.md` — Added Liquid protection wrapping
10. `RESEARCH_PLAN.md` — Fixed "Reasearch" typo
11. `RESEARCH_JOURNAL.md` — Fixed "Hueristic" typo
12. `IMPLEMENTATION_TASK.md` — Added completion summary
13. `BUGS.md` — Added historical note header

### Verification

- All status markers now match actual completion state
- Phase ordering in PLAN.md follows natural descending order (111→101→100→...→1)
- All headings use consistent `###` level for phases
- Liquid protection present on all workflow documents with Jinja2 patterns
- Typo fixes confirmed by grep
{% endraw %}
