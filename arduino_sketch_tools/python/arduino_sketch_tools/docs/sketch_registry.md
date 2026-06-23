---
---
# SketchRegistry

**Module:** `arduino_sketch_tools.sketch_registry`  
**Since:** Phase 99 — HTML Template Homogenisation (2026-06-22)

## Overview

`SketchRegistry` is a thread-safe class that maps hardware IDs (from connected Arduino boards) to assigned sketch directory paths. It operates on a shared upload registry dict that is managed by the consuming application (either `arduino_dash` or `medminder_dash`).

The upload registry has this structure:

```
{(ip, ua): {sketch_name: [version_dict, ...]}}
```

Each `version_dict` may contain a `"hardware_ids"` list that records which boards were deployed to. `SketchRegistry` searches this structure to find sketch assignments.

## Motivation

Prior to Phase 99, `arduino_dash` and `medminder_dash` each had their own identical `sketch_registry.py` module, differing only in the import path (`from arduino_dash import state` vs `from medminder_dash import state`). Extracting the shared logic to `arduino_sketch_tools` eliminated this code duplication and enabled the `assigned-sketch-info` feature in `arduino_dash`.

## Class API

### Constructor

```python
def __init__(self, registry: dict, lock: threading.Lock) -> None
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `registry` | `dict` | The shared upload registry dict (e.g. `state._upload_registry`) |
| `lock` | `threading.Lock` | Lock protecting the registry (e.g. `state._upload_registry_lock`) |

The instance also creates its own `_op_lock` for per-operation serialization, giving a double-lock pattern: `_op_lock` → caller's `_lock`.

### Methods

#### `get_assignment(hardware_id: str) -> Optional[str]`

Returns the sketch path assigned to a hardware ID, or `None`.

- Searches all entries in the registry for a version whose `"hardware_ids"` list contains the given hardware ID and whose sketch directory exists on disk
- Returns the first matching path
- Thread-safe (acquires `_op_lock` then `_lock`)

#### `set_assignment(hardware_id: str, sketch_dir: str) -> None`

Assigns a sketch directory to a hardware ID.

- Searches the registry for a version with the matching `sketch_dir` path
- If found, appends `hardware_id` to its `"hardware_ids"` list (if not already present)
- No-op if `hardware_id` is empty

#### `clear_assignment(hardware_id: str) -> None`

Removes a hardware ID from all sketch assignments.

- Searches all versions and removes `hardware_id` from any `"hardware_ids"` list
- No-op if `hardware_id` is empty

#### `get_all_assignments() -> dict[str, str]`

Returns all current hardware ID → sketch path mappings as a dict.

- Filters to paths that exist on disk (`os.path.isdir`)
- Returns `{hardware_id: sketch_dir, ...}`

#### `reset_for_tests() -> None`

No-op (provided for test compatibility with the original per-app modules).

## Usage Pattern

Each app creates its own `SketchRegistry` instance backed by its own state:

```python
# arduino_dash
from arduino_sketch_tools.sketch_registry import SketchRegistry
from arduino_dash import state

_registry = SketchRegistry(state._upload_registry, state._upload_registry_lock)

get_assignment = _registry.get_assignment
set_assignment = _registry.set_assignment
clear_assignment = _registry.clear_assignment
get_all_assignments = _registry.get_all_assignments
reset_for_tests = _registry.reset_for_tests
```

The bound methods are aliased at module level so existing importers don't need to change:

```python
# Before (per-app module)
from arduino_dash.sketch_registry import get_assignment

# After (still works — per-app module now re-exports from shared class)
from arduino_dash.sketch_registry import get_assignment
```

## Thread Safety

Two levels of locking:

1. **`_lock`** (caller-provided) — protects the shared `_upload_registry` dict, which may be accessed by multiple threads (WS handlers, API routes, HTMX requests)
2. **`_op_lock`** (instance-level) — serializes `SketchRegistry` operations so that concurrent `get_assignment` / `set_assignment` / `clear_assignment` calls don't interleave during the multi-level iteration over the registry structure

This pattern avoids deadlocks: `_op_lock` is always acquired first, then `_lock`.
