---
---
{% raw %}
# Review Journal — Phase 93: GitHub Pages Jekyll Documentation Site

**Date**: 2026-06-20

---

## 2026-06-20 14:24 — Phase 93 Review Complete ✅

### Summary

All Phase 93 changes reviewed and accepted. The Jekyll documentation site builds cleanly with 0 errors, 0 warnings, and 254 HTML pages.

### Key Findings

1. **Config fixes were essential** — Without merged plugins, `jekyll-relative-links` silently dropped, causing `.md`→`.html` link conversion to never work. Without `theme: minima`, pages rendered as bare HTML.

2. **Front matter is all-or-nothing** — Every `.md` file needs front matter, including READMEs outside `docs/` directories. The first batch (93 files) missed 8 README files because the script only targeted `docs/` dirs.

3. **raw/endraw for Jinja2 is simple but fragile** — Works perfectly to prevent Liquid errors, but embedding the closing raw tag (opening-brace, percent, endraw, percent, closing-brace) inside backtick spans prematurely closes the outer raw block. This is a text-level issue: Liquid doesn't understand Markdown backticks.

4. **Nested subpackage structure caused 51 broken links** — `board_manager` and `medminder_dash` both have Python subpackages with the same name as the parent, creating an extra directory level that documentation links missed.

5. **Liquid warnings from `{{ }}` in code blocks** — 4 warnings from Jinja2 filter syntax in RESEARCH docs. Wrapping in a raw block eliminates all warnings.

6. **README links require front matter to resolve as `.html`** — Without front matter, `jekyll-relative-links` treats the target as a static file and preserves the `.md` extension. Adding front matter turns them into proper pages.

### Verification Results

| Check | Result |
|-------|--------|
| `bundle exec jekyll build` exit code | 0 ✅ |
| Errors | 0 ✅ |
| Warnings | 0 ✅ |
| HTML pages | 254 ✅ |
| README hrefs in index.html | 9 ✅ |
| Nested doc dirs exist | ✅ (board_manager + medminder_dash) |
| All hrefs resolve to `.html` | ✅ |

### Phase 93 is closed. Ready for next plan quantum.

---

## Phase 96 — Wire test_ci.sh into Nox scripts_tests

**Review date**: 2026-06-20 20:03

**Change**: `noxfile.py` — added `session.run("bash", "tests/test_ci.sh", external=True)`
to the `scripts_tests` session (1 line).

**Review findings**:
- Code change is minimal and correct
- `test_ci.sh` passes 30/30 assertions standalone and via nox
- No regression in the `scripts_tests` session (170 total, all pass)
- The script is self-contained (bash-only, no external deps)
- Follows the same pattern as the existing `test_install_arduino_deps.sh` call

**Verdict**: ✅ Approved. Phase 96 complete.
{% endraw %}