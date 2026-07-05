---
layout: default
---
{% raw %}
# Research Plan — Phase 97: Frontend Stack Optimization

**Date**: 2026-06-20 22:17

## Objective

Reduce JS payload, simplify the frontend stack, and optimize HTMX swap targets to minimize bytes over the wire. Evaluate Idiomorph, dropping Hyperscript, and restructure DOM swap targets.

## Research Questions

1. **Current JS payload breakdown** — What does each dependency cost?
2. **Hyperscript usage audit** — Where is it used, what does it do, can it be replaced with vanilla JS?
3. **Idiomorph compatibility** — Can we add `hx-swap="morph"` without breaking existing behavior?
4. **Swap target audit** — Which partials can be made more granular to reduce payload?
5. **WebSocket vs SSE evaluation** — What would SSE change for our real-time board events?
6. **WS → WS+HTMX polling conversion** — daemon status already uses polling via `hx-trigger="every 10s"`; can we make it respond to WS push instead?

## Approach

1. Read HOTWIRE_FEASIBILITY_RESEARCH.md for existing analysis
2. Audit all partial templates and hx-target combos
3. Audit all Hyperscript usages across 10 template files
4. Research Idiomorph API and compatibility
5. Research HTMX SSE extension
6. Document findings and propose phased implementation
{% endraw %}
