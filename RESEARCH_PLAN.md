---
---
{% raw %}
# Research Plan — Phase 77: Template Port Path Cleanup

**Date**: 2026-06-17 17:03

## Objective

Remove the scattered `{{ port.lstrip('/') }}` pattern from 9 HTML template locations by computing a `port_path` (URL-safe, no leading `/`) once in Python route context and passing it to templates. This is the natural follow-on to Phase 76's `normalize_port()` integration.

## Research Questions

1. **Where does `port.lstrip('/')` appear in templates?** — Identify all 9 locations across 6 template files.
2. **Which route handlers pass `port` to these templates?** — Trace each template's render context.
3. **What is the data flow?** — Route receives bare port → `normalize_port()` adds `/` → template strips `/` for URLs. Can we break this inversion?
4. **What is the minimal change?** — Compute `port_path = port.lstrip('/')` in Python, pass as context variable.
5. **Risk assessment** — Would any route break if `port` changes format?

## Approach

1. Search templates for `port.lstrip` patterns
2. Search route handlers for `render_template` calls with `port` in context
3. Propose minimal changes
4. Validate with existing test suite
{% endraw %}
