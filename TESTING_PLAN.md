---
layout: default
---
{% raw %}
# Testing Plan — Phase 111: Semantic Versioning v0.1.0

## Scope

Verify that version strings are consistent across all 6 Python packages,
the E2E package, and the root VERSION file.

## Test Strategy

1. **Import test** — Each package's `__version__` attribute reads correctly
2. **Setup.py test** — Each `setup.py` correctly imports `__version__`
3. **Consistency test** — All version strings equal `"0.1.0"`
4. **Root files** — `package.json` and `VERSION` contain `"0.1.0"`
5. **Existing tests** — Full `nox -s all_tests` must still pass
{% endraw %}
