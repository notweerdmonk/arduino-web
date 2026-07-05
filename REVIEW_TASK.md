---
layout: default
---
{% raw %}
# Review Tasks — Category 1: Workflow Document Fixes

**Date**: 2026-07-05

## Task Q1 — Fix 1A: Stale Statuses in IMPLEMENTATION_PLAN.md

- [x] Change `🏗️ IN PROGRESS` → `✅ COMPLETED` on Phase 104.2 (line 59)
- [x] Change `🏗️ IN PROGRESS` → `✅ COMPLETED` on Phase 107 (line 98)
- [x] Change all `🔲` → `✅` for Phase 107 Q1-Q6 (lines 108-113)
- [x] Change all `⬜` → `✅` for Phase 111 A-E (lines 176-180)

## Task Q2 — Fix 1B: Missing Phase 109 Entry in JOURNAL.md

- [x] Add Phase 109 entry between Phase 110 and Phase 108 entries

## Task Q3 — Fix 1C: JOURNAL.md Status Marker Gaps

- [x] Add `✅ COMPLETED` to Phase 102 title (line 157)
- [x] Fix Phase 82 title from "(In Progress)" to "✅ COMPLETED" (line 1017) — or whatever matches the body

## Task Q4 — Fix 1D: Stale h1 Document Headings

- [x] IMPLEMENTATION_JOURNAL.md: Update to "Phase 111: Semantic Versioning"
- [x] TESTING_JOURNAL.md: Update to "Phase 111: Semantic Versioning"
- [x] REVIEW_JOURNAL.md: Update to "Phase 111: Semantic Versioning"

## Task Q5 — Fix 1E: PLAN.md Structural Issues

- [x] Move Phases 101-111 before Phase 100 (ordering fix)
- [x] Merge Phase 101 duplicate or nest as Phase 101a
- [x] Add `✅ COMPLETED` marker to Phase 110
- [x] Fix Phase 109 heading level `##` → `###`
- [x] Fix sub-phase ordering: 100 → 100b → 100c

## Task Q6 — Fix 1F: TODOS.md Missing 11 Phases

- [x] Add Phases 104, 104.1, 104.2, 104.3, 105, 106, 107, 108, 109, 110, 111 to the completed table
- [x] Remove Phase 93 duplicate entry (if applicable)

## Task Q7 — Fix 1G: RESEARCH Docs Missing Liquid Protection

- [x] Add Liquid `raw`/`endraw` wrapping to RESEARCH_TASK.md
- [x] Add Liquid `raw`/`endraw` wrapping to RESEARCH_PROGRESS.md

## Task Q8 — Fix 1H: Typos

- [x] RESEARCH_PLAN.md line 28: "Reasearch" → "Research"
- [x] RESEARCH_JOURNAL.md line 165: "Hueristic" → "Heuristic"

## Task Q9 — Fix 1I: IMPLEMENTATION_TASK.md Completion Summary

- [x] Add `## Completed` section with `✅` items for Tasks A-E

## Task Q10 — Fix 1J: BUGS.md Historical Note

- [x] Add historical context header noting Hyperscript was removed in Phase 97

## Task Q11 — Record findings in REVIEW_JOURNAL.md

- [x] Record all fix outcomes and verification results

---

## Category 2: CODEBASE_REFERENCE.md Fixes

**Date**: 2026-07-05 02:12

### Task Q12 — Fix 2A: Stale "Last Updated" Line

- [x] Change `2026-06-24 (Phases 89-100 + Code Review — Linting, ESLint, Playwright, Pipfile)` → `2026-07-04 (Phases 89-111)` on line 7

### Task Q13 — Fix 2B: References to Nonexistent `e2e/docs/index.md`

- [x] Line 3871: `e2e/docs/index.md` → `e2e/index.md`
- [x] Line 3911: `e2e/docs/index.md` → `e2e/index.md`
- [x] Line 3936: `e2e/docs/index.md` → `e2e/index.md`
- [x] Line 3937: `e2e/docs/index.md` → `e2e/index.md`
- [x] Line 3974: `e2e/docs/index.md` → `e2e/index.md`
- [x] Line 4018: `e2e/docs/index.md` → `e2e/index.md`

### Task Q14 — Fix 2C: Reference to Nonexistent `dist-test-install/docs/index.md`

- [x] Line 4026: `dist-test-install/docs/index.md` → `dist-test-install/index.md`

### Task Q15 — Fix 2D: Missing Phase Sections

- [x] Insert Phase 104.3 section between Phase 104.2 and Phase 107
- [x] Insert Phase 105 section after Phase 104.3
- [x] Insert Phase 106 section after Phase 105
- [x] Insert Phase 109 section between Phase 108 and Phase 111
- [x] Insert Phase 110 section after Phase 109

### Task Q16 — Fix 2E: Stale Line Number References

- [x] Update `arduino_dash_server.py main()` line ref from 208-237 to 184
- [x] Update `medminder_dash_server.py main()` line ref from 237-266 to 220
- [x] Update `base.html` idiomorph line — arduino_dash from 9 to 32
- [x] Update `base.html` idiomorph line — medminder_dash from 13 to 40

### Task Q17 — Record findings in REVIEW_JOURNAL.md

- [x] Record all fix outcomes and verification results

---

## Verification Pass — Post-Fix Review (2026-07-05 02:33)

### Task V1 — Verify 2A: Stale "Last Updated" Line

- [x] Confirm line 7 reads `**Last updated**: 2026-07-04 (Phases 89-111)`
- [x] Confirm no remaining stale `2026-06-24 (Phases 89-100` pattern

### Task V2 — Verify 2B: e2e/docs/index.md → e2e/index.md (6 refs)

- [x] Confirm zero occurrences of `e2e/docs/index.md` remain (excluding historical records)
- [x] Confirm replaced refs use correct `e2e/index.md` path

### Task V3 — Verify 2C: dist-test-install/docs/index.md

- [x] Confirm zero occurrences of `dist-test-install/docs/index.md` remain

### Task V4 — Verify 2D: Missing Phase Sections

- [x] Confirm Phase 104.3 section present between Phase 104.2 and Phase 107
- [x] Confirm Phase 105 section present after Phase 104.3
- [x] Confirm Phase 106 section present after Phase 105
- [x] Confirm Phase 109 section present between Phase 108 and Phase 111
- [x] Confirm Phase 110 section present after Phase 109
- [x] Verify content is accurate (no fabricated claims)

### Task V5 — Verify 2E: Stale Line Number References

- [x] Confirm `base.html` arduino_dash idiomorph line ref = 32
- [x] Confirm `base.html` medminder_dash idiomorph line ref = 40
- [x] Confirm `arduino_dash_server.py main()` line ref = 184
- [x] Confirm `medminder_dash_server.py main()` line ref = 220
- [x] Verify against actual source files

### Task V6 — Verify Category 1 Workflow Doc Fixes

- [x] Confirm 4 stale status markers updated in IMPLEMENTATION_PLAN.md
- [x] Confirm Phase 109 entry present in JOURNAL.md
- [x] Confirm JOURNAL.md status marker gaps fixed (Phase 102, Phase 82)
- [x] Confirm 3 journal h1 headings reference Phase 111
- [x] Confirm PLAN.md structural fixes applied
- [x] Confirm TODOS.md has phases 101-111
- [x] Confirm RESEARCH_TASK.md and RESEARCH_PROGRESS.md have Liquid `raw`/`endraw` wrapping
- [x] Confirm typos fixed: "Reasearch" → "Research", "Hueristic" → "Heuristic"
- [x] Confirm IMPLEMENTATION_TASK.md has Completed section
- [x] Confirm BUGS.md has historical note header

### Task V7 — Verify REVIEW Workflow Doc Self-Consistency

- [x] Confirm REVIEW_PLAN.md has Verification Pass section
- [x] Confirm REVIEW_TASK.md has verification tasks
- [x] Confirm REVIEW_PROGRESS.md shows review progress
- [x] Confirm REVIEW_JOURNAL.md records findings

### Task V8 — Record findings in REVIEW_JOURNAL.md

- [x] Record all verification outcomes

---

## Code Review — Category 2 CODEBASE_REFERENCE.md Fixes (2026-07-05 03:57)

### Task R1 — Verify 2A: Stale "Last Updated" Line

- [x] Confirm line 7 reads `**Last updated**: 2026-07-04 (Phases 89-111)`
- [x] Confirm no remaining `2026-06-24 (Phases 89-100` pattern

### Task R2 — Verify 2B: e2e/docs/index.md → e2e/index.md (6 refs)

- [x] Grep confirm zero stale `e2e/docs/index.md` refs remain (excluding historical records)
- [x] Verify each replacement uses correct `e2e/index.md` path

### Task R3 — Verify 2C: dist-test-install/docs/index.md → dist-test-install/index.md

- [x] Grep confirm zero remaining `dist-test-install/docs/index.md` refs

### Task R4 — Verify 2D: Missing Phase Sections (5 sections)

- [x] Confirm Phase 104.3 present after 104.2, content matches PLAN.md
- [x] Confirm Phase 105 present after 104.3, content matches PLAN.md
- [x] Confirm Phase 106 present after 105, content matches PLAN.md
- [x] Confirm Phase 109 present between 108 and 110, content matches PLAN.md
- [x] Confirm Phase 110 present after 109, content matches PLAN.md

### Task R5 — Verify 2E: Stale Line Number References (4 refs)

- [x] arduino_dash base.html idiomorph: verify actual source line = 32
- [x] medminder_dash base.html idiomorph: verify actual source line = 40
- [x] arduino_dash_server.py main(): verify actual source line = 184
- [x] medminder_dash_server.py main(): verify actual source line = 220

### Task R6 — Content Accuracy & Structure Integrity

- [x] Spot-check Phase 111 version table against actual codebase
- [x] Check for unintended side effects from replaceAll (e.g., duplicate entries)
- [x] Verify front matter and Liquid raw/endraw blocks intact
- [x] Check for code block balance issues (stray backticks)

### Task R7 — Regression Verification

- [x] Run `nox -s all_tests` — confirm 8/8 sessions, 0 failures

### Task R8 — Record findings in REVIEW_JOURNAL.md

- [x] Record all code review findings and verification outcomes

---

## Category 4: Config/Resource File Fixes (2026-07-05 03:31)

### Task C1 — CI Workflow (4A)
- [x] Create `.github/workflows/ci.yml` — ruff lint, format check, djlint, full CI pipeline
- [x] Verify CI triggers on push/PR to master

### Task C2 — Dependency Manifests — medminder_dash (4B)
- [x] Add `flask-sock>=0.7.0`, `simple-websocket>=1.0.0`, `arduino-sketch-tools>=0.1.0`, `board-manager-client>=0.1.0` to `install_requires`

### Task C3 — Dependency Manifests — arduino_dash (4B)
- [x] Add `simple-websocket>=1.0.0` to `install_requires`

### Task C4 — Dependency Manifests — grpc_client (4B)
- [x] Move `grpcio`, `protobuf`, `googleapis-common-protos` from `[dev-packages]` to `[packages]`
- [x] Remove `grpcio-tools` from `[dev-packages]`

### Task C5 — Git/Config — .gitattributes (4C)
- [x] Create `.gitattributes` — `* text=auto`, shell/Bat EOL, export-ignore patterns

### Task C6 — Git/Config — .editorconfig (4C)
- [x] Create `.editorconfig` — indent rules, charset, trimming whitespace

### Task C7 — Git/Config — .gitignore (4C)
- [x] Add missing patterns: `__pycache__`, `*.pyc`, `.eggs/`, `.mypy_cache/`, `htmlcov/`, `.coverage*`, `*.swp`, `.Python`, `pip-wheel-metadata/`, `.DS_Store`, `Thumbs.db`

### Task C8 — Git/Config — MANIFEST.in (4C)
- [x] Create `MANIFEST.in` for `arduino_sketch_tools`, `arduino_dash`, `medminder_dash`
- [x] Fix `arduino_sketch_tools/setup.py` — remove stale `"config/**/*"` from `package_data`

### Task C9 — Tooling — Root pyproject.toml (4D)
- [x] Create root `pyproject.toml` with `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.djlint]`

### Task C10 — Tooling — .ruby-version (4D)
- [x] Create `.ruby-version` (3.1)

### Task C11 — Polish — encoding in setup.py (4E)
- [x] Add `encoding="utf-8"` to all 6 `setup.py` files

### Task C12 — Polish — .prettierignore (4E)
- [x] Add `eslint.config.mjs` to `.prettierignore`

### Task C13 — Polish — noxfile.py reuse_venv (4E)
- [x] Add `nox.options.reuse_existing_virtualenvs = True`

### Task C14 — Verify — nox all_tests (4F)
- [x] Run `nox -s all_tests` — 8/8 sessions, 0 failures

### Task C15 — Record findings in REVIEW_JOURNAL.md
- [x] Record all Category 4 fix outcomes and verification results

---

## Code Review — Category 3: User-Facing Docs Fixes (2026-07-05 04:51)

### Task U1 — Verify 3A: Broken Links (5 issues)

- [x] `index.md` line 25: `dist-standalone/index.md` → `dist-standalone-install/index.md` — ✅ resolves
- [x] `index.md` line 141: `dist-standalone/index.md` → `dist-standalone-install/index.md` — ✅ resolves
- [x] `e2e/README.md` line 92: `../test-sketch/README.md` → `test-sketch/README.md` — ✅ resolves
- [x] `e2e/README.md` line 131: `docs/tests.md` → `../docs/tests.md` — ✅ resolves
- [x] `e2e/README.md` line 135: `../agent_tools/GUIDE.md` → `agent_tools/GUIDE.md` — ✅ resolves

### Task U2 — Verify 3B: Wrong Default Port Numbers (4 issues)

- [x] `arduino_dash/README.md`: "default port 5000" → "default port 8080" — ✅ `__main__.py:34` default=8080
- [x] `arduino_dash/README.md`: `http://localhost:5000` → `http://localhost:8080` — ✅ correct
- [x] `medminder_dash/README.md`: "default port 5000" → "default port 8080" — ✅ `__main__.py:36` default=8080
- [x] `medminder_dash/README.md`: `http://localhost:5000` → `http://localhost:8080` — ✅ correct

### Task U3 — Verify 3C: Nonexistent API Endpoints (2 issues)

- [x] `docs/guide.md`: `POST /api/compile-and-upload` → `POST /api/pubsub/board/ttyACM0/spawn` — ⚠️ route exists but spawns monitor, not compile
- [x] `docs/guide.md`: `POST /api/deploy` → `POST /api/pubsub/board/ttyACM0/compile` — ❌ route does not exist (see findings in REVIEW_JOURNAL.md)

### Task U4 — Verify 3D: Nonexistent Environment Variables (5 issues)

- [x] `board_manager/README.md`: `BOARD_MGR_DAEMON_PORT` → clarified description — ✅ actual vars in `boot.py` use different names
- [x] `board_manager/README.md`: `BOARD_MGR_PUBSUB_PORT` → `BOARD_MGR_TCP_PORT` — ✅ matches actual `BmsEnv` class
- [x] `medminder_dash/README.md`: `MEDMINDER_PORT` removed — ✅ no such env var in code
- [x] `medminder_dash/README.md`: `MEDMINDER_DEBUG` removed — ✅ no such env var in code
- [x] `medminder_dash/README.md`: `MEDMINDER_SKETCH_DIR` removed — ✅ no such env var in code

### Task U5 — Verify 3E: Stale CLI Flags and Paths (2 issues)

- [x] `board_manager/README.md`: `--port 50051` → `--tcp-port 9090` — ✅ flag exists in `__main__.py:33`
- [x] `grpc_client/README.md`: `cd gRPC_client/python` → `cd grpc_client/python/arduino_grpc` — ✅ path exists

### Task U6 — Verify 3F: Incorrect Protocol Descriptions (2 issues)

- [x] `board_manager/README.md`: "gRPC service" → "pub/sub service" — ✅ correct protocol
- [x] `board_manager_client/README.md`: "PubSub gRPC stream" → "pubsub stream" — ✅ correct protocol
- [x] `board_manager_client/README.md`: Default port 50052 → 9090 — ✅ matches `BmsDefaults.TCP_PORT`
- [x] `board_manager_client/README.md`: UDS path `/tmp/bms.sock` → `/tmp/board_mgr.sock` — ✅ matches `BmsDefaults.UDS_PATH`

### Task U7 — Verify 3G: Stale Route Documentation (4 issues)

- [x] `arduino_sketch_tools/README.md`: Removed stale `GET /board/<port>/list` — ❌ route still listed (NOT removed) — see findings
- [x] `arduino_sketch_tools/README.md`: Removed stale `GET /board/<port>/ports` — ❌ route still listed (NOT removed) — see findings
- [x] `arduino_sketch_tools/README.md`: Updated `/board/<port>/compile-result` → `/board/<port>/compile/poll` — ✅ exists
- [x] `arduino_sketch_tools/README.md`: Updated `/board/<port>/upload-result` → `/board/<port>/upload/poll` — ✅ exists
- [x] `arduino_sketch_tools/README.md`: Added missing routes — ⚠️ 2 correct, 2 fabricated (see findings)

### Task U8 — Verify 3H: Architecture Doc Issues (2 issues)

- [x] `docs/architecture.md`: Remove duplicate `## System Overview` header — ✅ confirmed (1 occurrence)
- [x] `docs/architecture.md`: Remove phase references (Phase 97, 98, 99) from user-facing text — ✅ confirmed (zero remaining)

### Task U9 — Verify 3I: Missing Routes in api.md (3 issues)

- [x] `docs/api.md`: Added `GET /boards/grid/card/<port>` to arduino-dash table — ✅ exists in `html_routes.py:145`
- [x] `docs/api.md`: Added `GET /boards/grid/card/<port>` to medminder-dash table — ✅ exists in `html_routes.py:806`
- [x] `docs/api.md`: Added medicine CRUD routes (POST, PUT, DELETE, toggle) — ✅ all verified against `html_routes.py`
- [x] `docs/api.md`: Fixed `/admin/active-board` → `/medicines/active-board` — ✅ confirmed in `html_routes.py:666`

### Task U10 — Verify 3J: Phase Numbers in External Docs (6+ locations)

- [x] `README.md`: Remove Phase column from "Recent Enhancements" table — ✅ confirmed removed
- [x] `README.md`: Remove "Phase N" references from descriptions — ✅ confirmed removed
- [x] `README.md`: Remove "Phase 94" reference in nox section — ⚠️ NOT removed (line 100: "(Phase 94)")
- [x] `index.md`: Remove phase range from "Last updated" line — ✅ confirmed removed
- [x] `docs/architecture.md`: Remove phase numbers from sections — ✅ confirmed zero remaining
- [x] `docs/guide.md`: Remove "Phase 94" reference — ✅ confirmed removed

### Task U11 — Jekyll Build Verification

- [x] Run `bundle exec jekyll build` — ✅ 0 errors, 0 warnings
- [x] Verify REVIEW docs (PLAN, TASK, PROGRESS, JOURNAL) are included in Jekyll output — ✅ all 4 generated

### Task U12 — Regression Verification

- [x] Run `nox -s all_tests` — ✅ 8/8 sessions, 0 failures

### Task U13 — Record findings in REVIEW_JOURNAL.md

- [x] Record all review findings and outcomes — ✅ full entry added
{% endraw %}
