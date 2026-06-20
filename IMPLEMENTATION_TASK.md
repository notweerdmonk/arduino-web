---
---
{% raw %}
# Implementation Task — Phase 96: Wire test_ci.sh into Nox scripts_tests

**Date**: 2026-06-20 20:03

## Current Task

Add `scripts/tests/test_ci.sh` to the nox `scripts_tests` session so it runs as part of the CI pipeline.

### Task Breakdown

| # | Task | Status |
|---|------|--------|
| 1 | Add `session.run("bash", "tests/test_ci.sh", external=True)` to `noxfile.py` `scripts_tests` session | ✅ |
| 2 | Run `bash scripts/tests/test_ci.sh` to verify the script passes standalone | ✅ |
| 3 | Run `nox -s scripts_tests` to verify integration with nox pipeline | ✅ |
| 4 | Update all workflow/project docs | ✅ |
{% endraw %}
