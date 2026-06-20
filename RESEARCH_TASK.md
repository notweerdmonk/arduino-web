---
---
# Research Tasks — Phase 77: Template Port Path Cleanup

**Date**: 2026-06-17 17:03

## Tasks

- [x] Identify all template `port.lstrip('/')` locations (9 in 6 templates)
- [x] Identify all route handlers that pass `port` to these templates
- [x] Trace data flow: route → normalize → template → URL
- [x] Define `port_path` approach
- [x] Assess risk (low — templates already do the same computation)
