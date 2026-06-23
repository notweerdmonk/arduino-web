---
---
# `sketch_registry.py` — Sketch Assignment Registry

**File:** `medminder_dash/sketch_registry.py`

Per-board sketch assignment registry keyed by hardware ID. Backed by
`state._upload_registry` in-memory dict.

## Shared `SketchRegistry` Class (Phase 99)

This module is now a thin **10-line wrapper** around the shared `SketchRegistry` class in
`arduino_sketch_tools/sketch_registry.py`. The module-level functions (`get_assignment`,
`set_assignment`, etc.) are bound methods of a module-level `SketchRegistry` instance:

```python
from arduino_sketch_tools import SketchRegistry
from medminder_dash import state

_registry = SketchRegistry(state._upload_registry, state._upload_registry_lock)

get_assignment = _registry.get_assignment
set_assignment = _registry.set_assignment
clear_assignment = _registry.clear_assignment
get_all_assignments = _registry.get_all_assignments
reset_for_tests = _registry.reset_for_tests
```

Existing importers (`from medminder_dash.sketch_registry import get_assignment`) require **no changes**.

## Functions (re-exported from `SketchRegistry`)

All functions are thread-safe (protected by `_op_lock` and
`state._upload_registry_lock`).

### `get_assignment(hardware_id: str) -> Optional[str]`

Return the sketch path assigned to a hardware ID, or `None` if no assignment
exists.

| Param | Type | Purpose |
|-------|------|---------|
| `hardware_id` | `str` | Board hardware ID |

Searches all entries in `state._upload_registry` for a version whose
`hardware_ids` list contains the given ID and whose `path` is a valid directory.

```python
path = get_assignment("AD8F...")
# "/home/user/.local/share/medminder/uploads/.../MySketch"
```

### `set_assignment(hardware_id: str, sketch_dir: str) -> None`

Assign a sketch path to a hardware ID. Finds the version entry matching
`sketch_dir` in the upload registry and appends the `hardware_id` to its
`hardware_ids` list if not already present.

| Param | Type | Purpose |
|-------|------|---------|
| `hardware_id` | `str` | Board hardware ID |
| `sketch_dir` | `str` | Sketch directory path to assign |

```python
set_assignment("AD8F...", "/path/to/sketch")
```

### `clear_assignment(hardware_id: str) -> None`

Remove the sketch assignment for a hardware ID. Finds and removes the
`hardware_id` from the `hardware_ids` list of any version entry.

| Param | Type | Purpose |
|-------|------|---------|
| `hardware_id` | `str` | Board hardware ID |

```python
clear_assignment("AD8F...")
```

### `get_all_assignments() -> dict[str, str]`

Return all hardware ID → sketch path assignments as a dict.

```python
assignments = get_all_assignments()
# {"AD8F...": "/path/to/sketch", "BEEF...": "/path/to/other"}
```

### `reset_for_tests() -> None`

Reset internal state for testing. Currently a no-op.

## Thread Safety

Two levels of locking within the `SketchRegistry` class:
1. **`_op_lock`** (instance-level) — serializes registry operations
2. **`state._upload_registry_lock`** (caller-provided) — protects the shared `_upload_registry` dict
