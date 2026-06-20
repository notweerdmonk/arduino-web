---
---
{% raw %}
# Implementation Plan — Phase 96: Wire test_ci.sh into Nox scripts_tests

**Date**: 2026-06-20 20:03

---

## Motivation

`scripts/tests/test_ci.sh` is a standalone test for `scripts/ci.sh` that validates:
- File existence and executability
- Bash syntax correctness
- `--help` flag output
- Unknown flag error handling
- Nox-not-found guard message
- `--skip-builds` flag forwards `nox -s all_tests` only
- `--skip-tests` flag forwards `nox -s all_builds` only
- Both `--skip` flags skip nox entirely
- Test failure propagation (exit 2)
- Build failure propagation (exit 3)

It uses a fake `nox` shim in a temp dir and has zero external dependencies beyond bash.
Currently it is not wired into the nox pipeline, so CI may not run it.

## Design

### Quantum 1 — Add to Nox

Add a single line to the `scripts_tests` session in `noxfile.py` to run
`test_ci.sh` after `test_install_arduino_deps.sh`:

```python
session.run("bash", "tests/test_ci.sh", external=True)
```

### Quantum 2 — Test

Run `nox -s scripts_tests` (or at minimum `bash scripts/tests/test_ci.sh`)
to verify the script passes.

## Files Changed

| File | Change |
|------|--------|
| `noxfile.py` | Add `session.run("bash", "tests/test_ci.sh", ...)` in `scripts_tests` |

## Verification

- `bash scripts/tests/test_ci.sh` exits 0 with all tests passing
- `nox -s scripts_tests` includes test_ci.sh and passes
- Commit message infrastructure section mentions test_ci.sh
{% endraw %}
