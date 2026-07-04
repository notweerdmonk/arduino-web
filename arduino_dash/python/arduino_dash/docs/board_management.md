---
layout: default
---
# board_management (board_management.py)

Board management helpers. Routes have moved to `html_routes.py` and `api_routes.py`; this module retains helper functions for session-based active board resolution.

> **Note:** Both `_get_active_board_info()` and `_resolve_board_info()` have duplicate implementations in `html_routes.py`. The `board_management.py` versions may be removed in a future refactor.

## Functions

### `_get_active_board_info() -> tuple[str, str, str]`

Return the active board (port, fqbn, hardware_id) from the Flask session.

Reads the `"admin_active_board"` session key. Supports both tuple/list format (3+ elements) and legacy string format. Returns `("", "", "")` if no active board is set.

```python
port, fqbn, hardware_id = _get_active_board_info()
```

### `_resolve_board_info(active_board_port: str, active_board_fqbn: str, active_board_hardware_id: str, known_ports: list[dict]) -> tuple[str, str, str]`

Resolve board info, falling back to known ports if needed.

Resolution priority:
1. Look up `active_board_port` in `state._board_list` via `get_port_info()`
2. If not found, try `find_board_info_by_fqbn()` using `active_board_fqbn`
3. If still not found, use `get_first_board(known_ports)`
4. Raises `ValueError("port missing")` or `ValueError("fqbn missing")` if unresolvable

```python
try:
    port, fqbn, hw_id = _resolve_board_info("", "", "", known_boards)
except ValueError as e:
    # handle missing port/fqbn
```
