---
layout: default
---
{% raw %}
# Review Plan — Category 1: Workflow Document Fixes

**Date**: 2026-07-05

**Source**: Comprehensive Document & Codebase Audit (see REVIEW_JOURNAL.md — 2026-07-05 01:04)

## Scope

Fix all 23 issues in Category 1 (Workflow Documents) from the audit, spanning sub-categories 1A through 1J.

## Fix Strategy

| Sub-Category | Description | Severity Mix | Files Affected |
|---|---|---|---|
| 1A | Stale Statuses in IMPLEMENTATION_PLAN.md | HIGH (4) | IMPLEMENTATION_PLAN.md |
| 1B | Missing Phase 109 Entry in JOURNAL.md | HIGH | JOURNAL.md |
| 1C | JOURNAL.md Status Marker Gaps | MEDIUM (2) | JOURNAL.md |
| 1D | Stale h1 Document Headings | MEDIUM (3) | IMPLEMENTATION_JOURNAL.md, TESTING_JOURNAL.md, REVIEW_JOURNAL.md |
| 1E | PLAN.md Structural Issues | HIGH, MEDIUM (2), LOW (2) | PLAN.md |
| 1F | TODOS.md Missing 11 Phases | HIGH | TODOS.md |
| 1G | RESEARCH Docs Missing Liquid Protection | MEDIUM (2) | RESEARCH_TASK.md, RESEARCH_PROGRESS.md |
| 1H | Typos | LOW (2) | RESEARCH_PLAN.md, RESEARCH_JOURNAL.md |
| 1I | IMPLEMENTATION_TASK.md Missing Completion Summary | MEDIUM | IMPLEMENTATION_TASK.md |
| 1J | BUGS.md Documents Removed Technology | LOW | BUGS.md |

## Execution Order

1. 1A — Stale status markers (quick, high-impact)
2. 1B — Missing journal entry (critical gap)
3. 1C — Status markers fix
4. 1D — Document headings update
5. 1E — PLAN.md restructure (most complex)
6. 1F — TODOS.md phase table update
7. 1G — Liquid protection wrapping
8. 1H — Typo fixes
9. 1I — Task completion summary
10. 1J — Historical note

## Verification

Each fix will be verified by:
- Visual inspection of the changed file
- Grep/pattern match to confirm the issue is resolved
- No regressions to document structure (front matter, Liquid tags)

**Verdict**: ✅ Completed — all 23 Category 1 issues fixed across 13 files; verified by V6 pass

---

## Category 2: CODEBASE_REFERENCE.md Fixes

**Date**: 2026-07-05 02:12

**Source**: Comprehensive Document & Codebase Audit (see REVIEW_JOURNAL.md — 2026-07-05 01:04)

### Scope

Fix all 7 issues in Category 2 (CODEBASE_REFERENCE.md) from the audit, spanning sub-categories 2A through 2E.

### Fix Strategy

| Sub-Category | Description | Severity | Files Affected |
|---|---|---|---|
| 2A | Stale "Last Updated" Line | HIGH | CODEBASE_REFERENCE.md |
| 2B | References to Nonexistent `e2e/docs/index.md` (6 refs) | HIGH | CODEBASE_REFERENCE.md |
| 2C | Reference to Nonexistent `dist-test-install/docs/index.md` | HIGH | CODEBASE_REFERENCE.md |
| 2D | Missing Phase Sections (104.3, 105, 106, 109, 110) | MEDIUM | CODEBASE_REFERENCE.md |
| 2E | Stale Line Number References (4 refs) | LOW | CODEBASE_REFERENCE.md |

### Execution Order

1. 2A — Update "Last Updated" line (quick, high-visibility)
2. 2B — Fix 6 e2e/docs/index.md → e2e/index.md references
3. 2C — Fix dist-test-install/docs/index.md → dist-test-install/index.md
4. 2D — Insert missing phase sections between existing entries
5. 2E — Update stale line numbers to current values

### Verification

Each fix will be verified by:
- Grep/pattern match to confirm no stale references remain
- Visual inspection of changed sections
- No regressions to document structure (front matter, Liquid tags)

**Verdict**: ✅ Completed — all 7 Category 2 issues fixed; verified by code review pass

---

## Verification Pass — Post-Fix Review

**Date**: 2026-07-05 02:33

### Scope

Review all applied fixes (Category 1 + Category 2) to confirm correctness, completeness, and absence of regressions. Covers 16 modified files.

### Review Criteria

| Area | Verification Method |
|------|-------------------|
| CODEBASE_REFERENCE.md fixes (2A-2E) | Grep for stale refs; read added phase sections; verify line numbers against actual source |
| Workflow doc status markers (1A) | Read IMPLEMENTATION_PLAN.md — confirm all stale markers updated |
| JOURNAL.md entries (1B, 1C) | Read JOURNAL.md — confirm Phase 109 present; status markers fixed |
| Document headings (1D) | Read h1 of 3 journal files — confirm "Phase 111" |
| PLAN.md restructure (1E) | Read PLAN.md header — confirm 101-111 before 100; heading levels; sub-phase order |
| TODOS.md phase table (1F) | Read TODOS.md — confirm phases 101-111 present |
| Liquid protection (1G) | Grep RESEARCH_TASK.md, RESEARCH_PROGRESS.md for Liquid `raw` tag |
| Typo fixes (1H) | Grep for old strings in RESEARCH_PLAN.md, RESEARCH_JOURNAL.md |
| Task completion summary (1I) | Read IMPLEMENTATION_TASK.md — confirm Completed section |
| BUGS.md note (1J) | Read BUGS.md — confirm historical context header |
| REVIEW doc consistency | Read REVIEW_PLAN.md, REVIEW_TASK.md, REVIEW_PROGRESS.md, REVIEW_JOURNAL.md — verify internal consistency |

---

## Code Review — Category 2 CODEBASE_REFERENCE.md Fixes (Verification Pass)

**Date**: 2026-07-05 03:57

### Scope

Perform comprehensive code review of the 7 applied fixes (2A-2E) in CODEBASE_REFERENCE.md,
covering 131 insertions / 12 deletions across the file. Verify correctness, content accuracy,
line number validity, and absence of regressions.

### Review Criteria

| Area | Method |
|------|--------|
| 2A — Stale "Last Updated" | Read line 7; confirm date + phase range correct |
| 2B — e2e/docs/index.md → e2e/index.md (6 refs) | Grep for stale refs; verify each replacement |
| 2C — dist-test-install/docs/index.md fix | Grep for stale ref; verify zero remaining |
| 2D — Missing Phase Sections (5 sections) | Read each added section; verify content matches PLAN.md history |
| 2E — Stale Line Number References (4 refs) | Verify against actual source files: base.html, server scripts |
| Content accuracy spot-check | Verify Phase 111 version table, no fabricated claims |
| Document structure integrity | Check front matter, Liquid tags, code block balance |
| Side-effect check | Look for unintended changes from bulk replaceAll operations |
| Regression check | `nox -s all_tests` — 8/8 sessions pass |

### Findings Summary

| Check | Status | Notes |
|-------|--------|-------|
| 2A | ✅ | "2026-07-04 (Phases 89-111)" — correct |
| 2B | ✅ | 6 refs corrected; 1 historical ref in Phase 104.3 (legitimate) |
| 2C | ✅ | Zero stale refs remaining |
| 2D | ✅ | All 5 sections present, accurate content |
| 2E | ✅ | All 4 line numbers verified against source |
| Content accuracy | ✅ | Phase 111 versions match actual codebase |
| Structure integrity | ⚠️ | Pre-existing stray triple-backtick at line 3692 opens unclosed code block (cosmetic only) |
| Side effects | ✅ | No unintended changes from replaceAll |
| Regression | ✅ | `nox -s all_tests` — 8/8 sessions, 0 failures |

**Verdict**: ✅ All Category 2 fixes are correct and verified. One pre-existing structural nit (stray code fence at line 3692) noted but not introduced by this work.

## Category 3: User-Facing Docs Fixes (Batch 5)

**Date**: 2026-07-05 04:51

**Source**: Comprehensive Document & Codebase Audit (see REVIEW_JOURNAL.md — 2026-07-05 01:04, sections 3A–3J)

### Scope

Fix **20+ issues** across **10 sub-categories** (3A–3J) in user-facing documentation:
broken links, wrong port numbers, nonexistent API endpoints, stale env vars,
incorrect CLI flags, incorrect protocol descriptions, stale route documentation,
duplicate headers, missing routes, and phase numbers leaking into external docs.

### Changes in Working Tree (Already Applied)

| Sub-Cat | Description | Severity | Files Changed |
|---------|-------------|----------|---------------|
| 3A | Broken links (5 issues) | HIGH | `index.md`, `e2e/README.md` |
| 3B | Wrong default port 5000→8080 (4 issues) | HIGH | `arduino_dash/README.md`, `medminder_dash/README.md` |
| 3C | Nonexistent API endpoints in guide (2 issues) | HIGH | `docs/guide.md` |
| 3D | Nonexistent env vars in package READMEs (5 issues) | MEDIUM | `board_manager/README.md`, `medminder_dash/README.md` |
| 3E | Stale CLI flags and paths (2 issues) | HIGH | `board_manager/README.md`, `grpc_client/README.md` |
| 3F | Incorrect protocol descriptions (2 issues) | MEDIUM | `board_manager/README.md`, `board_manager_client/README.md` |
| 3G | Stale route docs in arduino_sketch_tools (4 issues) | MEDIUM | `arduino_sketch_tools/README.md` |
| 3H | Duplicate header + phase numbers in architecture.md | LOW | `docs/architecture.md` |
| 3I | Missing routes in api.md (3 issues) | MEDIUM | `docs/api.md` |
| 3J | Phase numbers in external docs (6+ locations) | LOW | `README.md`, `index.md`, `docs/architecture.md`, `docs/guide.md` |

### Review Criteria

| Check | Method |
|-------|--------|
| 3A — Broken links | Verify each link resolves to an actual file on disk |
| 3B — Port numbers | grep for remaining `5000` in READMEs; verify actual default=8080 in source |
| 3C — API endpoints | Verify endpoints match actual Flask routes in code |
| 3D — Env vars | grep for removed vars; verify actual env var names from `boot.py`/CLI |
| 3E — CLI flags/paths | Verify `--tcp-port` exists in CLI; verify `grpc_client/` path is correct |
| 3F — Protocol descriptions | Verify "pub/sub" wording matches actual protocol (not gRPC) |
| 3G — Route documentation | Verify routes match actual `routes.py` |
| 3H — Architecture docs | Verify no duplicate headers; no phase references remain in user-facing text |
| 3I — Missing routes | Verify added routes match actual route definitions |
| 3J — Phase numbers | grep for phase references in external docs; verify removed from user-facing text |
| Jekyll build | `bundle exec jekyll build` — 0 errors, 0 warnings |
| Regression | `nox -s all_tests` — 8/8 sessions pass |

**Verdict**: ⚠️ In progress — 19/22 fixes verified; 3 issues found (nonexistent compile endpoint in guide.md, stale/fabricated routes in arduino_sketch_tools README.md, remaining phase reference in README.md:100)
{% endraw %}
