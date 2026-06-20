---
---
{% raw %}
# Implementation Journal — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

---

## Entry 1 — Config Fixes (Q1-Q2)

**Date**: 2026-06-20

**Files modified**: `_config.yml`, `Gemfile`

### _config.yml Fixes

1. **Duplicate `plugins:` merged**: The file had `plugins:` listed twice:
   - First: `plugins: [jekyll-relative-links, jekyll-feed, jekyll-seo-tag]`
   - Second: `plugins: [jekyll-feed]`
   
   YAML takes the last duplicate key, so `jekyll-relative-links` and `jekyll-seo-tag` were silently dropped. Merged into a single `plugins:` list with all three.

2. **`theme: minima` added**: Without `theme: minima`, Jekyll's Minima theme was not activated. Pages had no layout, no CSS, no header/footer.

3. **`defaults:` added with `layout: default`**: This applies `layout: default` to all `.md` files (scope: `path: ""`, `type: "pages"`). Minima's `default` layout gives header/footer without wrapping content in `<h1>` (unlike `page` layout, which expects `page.title` in front matter).

4. **`title:` and `description:` added**: `<title>` tag in `_site/index.html` was empty without these.

### Gemfile

Removed `gem "jekyll-archives"` — this plugin requires category/tag front matter and `_layouts/` directory, neither of which exist. Not needed for a flat documentation site.

**Gotcha**: `gem "minima"` without version constraint tries to install from rubygems.org (latest = 2.5.7 at time of writing), bypassing system-installed 2.5.2. Pinned with `"~> 2.5"` to use system gem and avoid write-permission errors to `/var/lib/gems/3.0.0/`.

---

## Entry 2 — Front Matter Bulk Addition (Q3)

**Date**: 2026-06-20

**Files modified**: 93 `.md` files

### Script design

Used a Python script to walk the project tree:

```python
def should_add_fm(filepath, root='.'):
    # Files in /docs directories
    if '/docs' in dirpath or dirpath.endswith('/docs'):
        return True
    # Top-level docs
    return filename in TOP_DOCS
    # All others: skip (READMEs, auto-generated, vendored)
```

The script collected all matching `.md` files, then wrote `---\n---\n` + original content to each.

**Files skipped**: README files outside `docs/` dirs (initially), auto-generated protobuf docs, vendored Flask/sphinx readme files in `dist-standalone/`.

### Batch 1: 93 doc files

- All files in `docs/` directories across all packages
- Root-level doc files: `README.md`, `index.md`, `PLAN.md`, `JOURNAL.md`, `TODOS.md`, `BUGS.md`, `docs/ws-event-flow.md`, `CODEBASE_REFERENCE.md`

### Batch 2: 8 README files (Q8)

Added front matter to 7 per-package `README.md` files + `grpc_client/python/arduino_grpc/README.md`. These were missed in the first pass because they're not in `docs/` directories. Without front matter, Jekyll copies them as static files (`.md` extension), and `jekyll-relative-links` does NOT convert `.md` links to `.html` for static files.

**Gotcha**: The front matter script used `if '/docs' in dirpath` which correctly excluded README files (they're in package root dirs). Had to add them manually in Q8.

---

## Entry 3 — raw/endraw Wrapping (Q4)

**Date**: 2026-06-20

**Files modified**: 5 workflow docs + 2 research docs

### Jinja2 vs Liquid Conflict

The project workflow documents use Jinja2 template syntax for code examples:
- `{% block extra_head %}{% endblock %}` — Jinja2 block inheritance
- `{% include "partials/..." %}` — Jinja2 partial includes

Jekyll's Liquid templating engine interprets `{% ... %}` as Liquid tags, causing `Liquid syntax error (line N): Unknown tag 'block'`.

### Solution

Wrapped entire Jinja2-containing files in a raw block (opening-brace-percent-raw-percent-closing-brace ... closing-brace-percent-endraw-percent-closing-brace). This tells Liquid to treat everything inside as literal text (no tag/expression processing).

### Critical Gotcha

Never embed the closing raw tag (opening-brace-percent-endraw-percent-closing-brace) inside backtick spans within a raw-wrapped file. Liquid does NOT understand Markdown backticks — it scans for the closing raw tag at the text level. The first closing raw tag it encounters (even inside a code block) closes the outer raw block, and subsequent Jinja2 tag sequences cause Liquid errors.

### Additional: Liquid Warnings (Q7)

Two research docs (`RESEARCH_JOURNAL.md` and `RESEARCH_PLAN.md`) contain `{{ port.lstrip('/') }}` — this is Jinja2 filter syntax that Liquid interprets as expression syntax. Liquid warns: `Liquid Warning: Liquid syntax error (line N): Expected end_of_string but found lstrip in "{{ port.lstrip('/') }}"`.

Wrapping in a raw block eliminated all 4 warnings.

---

## Entry 4 — Broken Link Fixes (Q5)

**Date**: 2026-06-20

**Files modified**: 5 files — `index.md`, `docs/architecture.md`, `docs/guide.md`, `docs/tests.md`, `docs/api.md`

### The Bug

Two packages have a nested Python subpackage with the same name as the parent:

```
board_manager/python/board_manager/
  └── board_manager/             ← package named same as parent
      ├── __init__.py
      ├── service.py
      ├── docs/                    ← actual docs directory
      │   ├── index.md
      │   └── ...
```

Links in documentation files referenced `board_manager/python/board_manager/docs/` (missing the inner `board_manager/` level). This is because the doc writer didn't realize there's an extra directory level.

### Fix

Used `replaceAll` on path prefixes across 5 files:

| File | board_manager | medminder_dash | Total |
|------|--------------|---------------|-------|
| `index.md` | `board_manager/.../docs/` → `board_manager/.../board_manager/docs/` | same pattern | 26 |
| `docs/architecture.md` | 7 links | 4 links | 11 |
| `docs/guide.md` | 2 links | 5 links | 7 |
| `docs/tests.md` | 1 link | 1 link | 2 |
| `docs/api.md` | 3 links | 2 links | 5 |
| **Total** | **24** | **27** | **51** |

### Verification

```bash
# Confirmed board_manager docs at correct path
ls _site/board_manager/python/board_manager/board_manager/docs/
# → 11 HTML doc pages exist

# Confirmed medminder_dash docs at correct path
ls _site/medminder_dash/python/medminder_dash/medminder_dash/docs/
# → 15 HTML doc pages exist

# Grep confirmed all hrefs point to correct paths
grep -o 'href="[^"]*"' _site/index.html | sort
```

---

## Entry 5 — Missing README Links (Q9-Q10)

**Date**: 2026-06-20

**Files modified**: `index.md`

### README links added

| Package | README link | Type |
|---------|-------------|------|
| `board_manager` | `board_manager/python/board_manager/README.md` | Per-package README |
| `board_manager_client` | `board_manager_client/python/board_manager_client/README.md` | Per-package README |
| `arduino_sketch_tools` | `arduino_sketch_tools/python/arduino_sketch_tools/README.md` | Per-package README |
| `arduino_dash` | `arduino_dash/python/arduino_dash/README.md` | Per-package README |
| `medminder_dash` | `medminder_dash/python/medminder_dash/README.md` | Per-package README |
| scripts | `scripts/README.md` | Per-directory README |
| dist-test-install | `dist-test-install/README.md` | Per-directory README |

### Final Build

```bash
$ bundle exec jekyll build
Configuration file: /home/weerdmonk/Projects/medminder/_config.yml
            Source: /home/weerdmonk/Projects/medminder
       Destination: /home/weerdmonk/Projects/medminder/_site
 Incremental build: disabled. Enable with --incremental
      Generating...
       Jekyll Feed: Generating feed for posts
                    done in 54.261 seconds.
 Auto-regeneration: disabled. Use --watch to enable.
EXIT: 0
```

**0 errors, 0 warnings, 254 HTML pages.**

### README href verification

```bash
$ grep -oP 'href="[^"]*README[^"]*"' _site/index.html | sort -u
href="/README.html"
href="/arduino_dash/python/arduino_dash/README.html"
href="/arduino_sketch_tools/python/arduino_sketch_tools/README.html"
href="/board_manager/python/board_manager/README.html"
href="/board_manager_client/python/board_manager_client/README.html"
href="/dist-test-install/README.html"
href="/grpc_client/python/arduino_grpc/README.html"
href="/medminder_dash/python/medminder_dash/README.html"
href="/scripts/README.html"
```

All 9 README references in `index.md` now resolve to `.html` (processed pages), not `.md` (static files).

---

## Entry 6 — Configuration Summary

**Date**: 2026-06-20

### Environment

| Component | Version |
|-----------|---------|
| Ruby | 3.0.2 |
| Bundler | 2.5.23 |
| Jekyll | 3.10.0 |
| Minima | 2.5.2 |
| jekyll-relative-links | 0.7.0 |

### Final _config.yml

```yaml
title: MedMinder Documentation
description: >-
  Documentation for the MedMinder monorepo — gRPC client,
  Board Manager Service, and Arduino/MedMinder dashboards.
theme: minima

plugins:
  - jekyll-relative-links
  - jekyll-feed
  - jekyll-seo-tag

defaults:
  - scope:
      path: ""
    values:
      layout: default
```

### Known Non-Fatal Issue

`bundle exec jekyll doctor` reports: `[jekyll-doctor] ERROR: undefined method 'absolute?' for nil:NilClass`. This is a known Jekyll 3.10 issue when `url:` is not set in `_config.yml`. Since this is a GitHub Pages site (URL assigned by GitHub), `url:` is intentionally left unset. The error is cosmetic and does not affect builds.

---

## Entry 7 — Timeline

| Q | Work | Duration |
|---|------|----------|
| 1-2 | Config + Gemfile fixes | ~2 min |
| 3 | Front matter script + execution | ~5 min |
| 4 | raw/endraw wrapping (5 files) | ~3 min |
| 5 | Link fix analysis + 5 file edits | ~5 min |
| 6 | Build + grep verification | ~1 min |
| 7 | Liquid warning fix (2 files) | ~2 min |
| 8 | README front matter (8 files) | ~1 min |
| 9 | README links in index.md | ~2 min |
| 10 | Final build + full verification | ~1 min |
| 11 | Docs sync (all project + workflow docs) | ~10 min |
| **Total** | | **~32 min** |

---

## Entry 2 — Phase 94: Noxfile Self-Healing Test Sessions

**Date**: 2026-06-20

**Motivation**: After wheel rebuilds (Phase 92 constants refactor), `Pipfile.lock` hashes become stale. The `tests` nox session used `pipenv install --dev` which fails with a hash mismatch error. The `scripts_tests` session used `pipenv sync --dev` which fails silently (lock doesn't match Pipfile → no install).

**Changes**:

| File | Change |
|------|--------|
| `noxfile.py:70` | `tests` session: `install --dev` → `lock --dev` + `sync --dev` |
| `noxfile.py:70` | `scripts_tests` session: `sync --dev` → `install --dev` |

**Design decisions**:
- `pipenv lock --dev` always regenerates `Pipfile.lock` with current wheel hashes
- `pipenv sync --dev` installs from the regenerated lock (faster than `install` when lock is fresh)
- `pipenv install --dev` for scripts_tests auto-regenerates the lock if Pipfile changed (unlike `sync` which requires exact match)

**Verification**: `nox -s all_tests` — all 8 sessions pass, 0 failures, 0 warnings.

---

## Entry 3 — Phase 95: Git Tree Preparation

**Date**: 2026-06-20 15:40

**Motivation**: Pre-commit audit revealed stale artifacts, missing `.gitignore` entries, and stale workflow docs.

**Changes** (see `IMPLEMENTATION_PLAN.md` for full details):

| Quantum | Scope | Status |
|---------|-------|--------|
| 1 | Clean uploads + .gitignore + .gitkeep | ✅ |
| 2 | Fix stale workflow docs | 🔲 |
| 3 | Fix doc inaccuracy | 🔲 |
| 4 | Sequential git add | 🔲 |

**Key decisions**:
- `config/board_sketches.json` is runtime data — ignored via `.gitignore`
- `uploads/` dirs tracked via `.gitkeep` but contents ignored via `**/uploads/*`
- `check_venv.bash` does not support `--help` — `scripts/docs/index.md` claim removed

### 2026-06-20 20:03 — Phase 96: Wire test_ci.sh into Nox scripts_tests

**Change**: Added `session.run("bash", "tests/test_ci.sh", external=True)` to the
`scripts_tests` session in `noxfile.py` (after `test_install_arduino_deps.sh`).

**Rationale**: `scripts/tests/test_ci.sh` tests 10 scenarios for `scripts/ci.sh`
(flag parsing, error propagation, nox-not-found guard) using a fake nox shim.
It had no CI coverage. The script is fully self-contained (bash-only) and was
already passing 30/30 standalone.

**Verification**:
- `bash scripts/tests/test_ci.sh` → 30/30 pass
- `nox -s scripts_tests` → 128 pytest + 12 bash + 30 bash = 170 total, all pass

**Key decisions**:
- `test_ci.sh` placed after `test_install_arduino_deps.sh` in the session (alphabetical order)
- Docstring updated from "bash + pytest" to "pytest + bash" to reflect ordering
{% endraw %}
