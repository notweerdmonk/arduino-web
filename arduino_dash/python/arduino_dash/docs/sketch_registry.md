---
---
# sketch_registry (sketch_registry.py)

Per-board sketch assignment registry keyed by `hardware_id`. Backed by the `_upload_registry` in-memory dict from `state.py`.

## Shared `SketchRegistry` Class (Phase 99)

This module is now a thin **10-line wrapper** around the shared `SketchRegistry` class in
`arduino_sketch_tools/sketch_registry.py`. The module-level functions (`get_assignment`,
`set_assignment`, etc.) are bound methods of a module-level `SketchRegistry` instance:

```python
from arduino_sketch_tools import SketchRegistry
from arduino_dash import state

_registry = SketchRegistry(state._upload_registry, state._upload_registry_lock)

get_assignment = _registry.get_assignment
set_assignment = _registry.set_assignment
clear_assignment = _registry.clear_assignment
get_all_assignments = _registry.get_all_assignments
reset_for_tests = _registry.reset_for_tests
```

Existing importers (`from arduino_dash.sketch_registry import get_assignment`) require **no changes**.

## Functions (re-exported from `SketchRegistry`)

### `get_assignment(hardware_id: str) -> Optional[str]`

Return the sketch path assigned to the given hardware ID.

Searches all entries in `_upload_registry` for a version that contains the `hardware_id` in its `hardware_ids` list and whose sketch directory exists on disk. Returns the first matching path, or `None` if no assignment is found.

```python
path = get_assignment("ABC123")
if path:
    print(f"Assigned sketch: {path}")
```

### `set_assignment(hardware_id: str, sketch_dir: str) -> None`

Assign a sketch directory to a hardware ID. Searches all registry entries for a version matching `sketch_dir`. If found and the `hardware_id` is not already in the version's `hardware_ids` list, appends it.

```python
set_assignment("ABC123", "/path/to/sketch")
```

### `clear_assignment(hardware_id: str) -> None`

Remove the sketch assignment for a hardware ID. Searches all registry entries and removes the `hardware_id` from the version's `hardware_ids` list.

```python
clear_assignment("ABC123")
```

### `get_all_assignments() -> dict[str, str]`

Return all hardware ID to sketch path assignments. Returns a dict mapping `hardware_id` → `sketch_path` for all registered assignments where the sketch directory exists on disk.

```python
assignments = get_all_assignments()
# Returns: {"ABC123": "/path/to/sketch", "DEF456": "/path/to/other"}
```

### `reset_for_tests() -> None`

Reset the registry for test isolation. Currently a no-op (implementation deliberately empty). Provided as a hook for test fixtures.

## Thread Safety

Two levels of locking within the `SketchRegistry` class:
1. **`_op_lock`** (instance-level) — serializes registry operations
2. **`_lock`** (caller-provided `state._upload_registry_lock`) — protects the shared `_upload_registry` dict
