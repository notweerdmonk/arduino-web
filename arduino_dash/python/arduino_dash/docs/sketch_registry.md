---
---
# sketch_registry (sketch_registry.py)

Per-board sketch assignment registry keyed by `hardware_id`. Backed by the `_upload_registry` in-memory dict from `state.py`.

## Internal Lock

```python
_lock = threading.Lock()
```

A module-level lock protects the assignment operations. All operations acquire `_lock` first, then `state._upload_registry_lock`.

## Functions

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
