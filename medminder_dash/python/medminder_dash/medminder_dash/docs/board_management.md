---
---
# `board_management.py` — Board Management (Placeholder)

**File:** `medminder_dash/board_management.py`

Placeholder module — all board management routes have been moved to
`html_routes.py`.

## Function: `init_board_routes(app, sock, store, migrate_default_board, load_sketch_dir, get_alarm_hpp_path=None) -> None`

No-op function kept for import compatibility with existing callers.

All board-related routes (board selection, board detail, board list, board
events, connection status) are now registered in `html_routes.py:init_html_routes()`.

## Import Compatibility

Code that previously did:

```python
from medminder_dash.board_management import init_board_routes
init_board_routes(app, sock, store, migrate_default_board, ...)
```

Still works without errors — the function simply does nothing.
