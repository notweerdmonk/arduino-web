---
---
# `html_routes.py` — HTML Routes

**File:** `medminder_dash/html_routes.py`

All HTML page and partial routes (no `/api/` prefix). Registered via
`init_html_routes()`. Supports session-based board selection, medicine CRUD
forms with HTMX partials, compile/upload cards, and live event streaming via
WebSocket.

## Function: `init_html_routes(app, sock, store_param, migrate_default_board, load_sketch_dir_param=None, get_alarm_hpp_path_param=None)`

| Param | Type | Purpose |
|-------|------|---------|
| `app` | `Flask` | Application instance |
| `sock` | `Sock` or `None` | Flask-Sock instance for WebSocket |
| `store_param` | `MedicineStore` | Medicine store instance |
| `migrate_default_board` | `callable` | Migrate default board data |
| `load_sketch_dir_param` | `callable` | (unused, kept for compat) |
| `get_alarm_hpp_path_param` | `callable` | (unused, kept for compat) |

## Route Table

### Index / Home

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/` | `index()` | Home page, renders `index.html` with medicine count and sketch path |

### Medicines — CRUD (HTML forms)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/medicines` | `medicines()` | Medicine list page, renders `medicines.html` |
| GET | `/medicine/new` | `medicine_new_form()` | Medicine creation form, renders `medicine_form.html` |
| POST | `/medicine` | `medicine_create()` | Create a medicine from form data, renders `medicines.html` |
| GET | `/medicine/<med_id>/edit` | `medicine_edit_form(med_id)` | Edit form for a medicine, renders `medicine_form.html` |
| PUT | `/medicine/<med_id>` | `medicine_update(med_id)` | Update a medicine from form data |
| DELETE | `/medicine/<med_id>` | `medicine_delete(med_id)` | Delete a medicine |
| PUT | `/medicine/<med_id>/toggle` | `medicine_toggle(med_id)` | Toggle enabled state |

### Board Selection

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/board/select/<path:port>` | `board_select(port)` | Select a board, redirects to board detail |
| GET | `/board` | `board_redirect()` | Redirect to selected board's detail |
| GET | `/board/<path:port>` | `board_detail(port)` | Board detail page, loads medicines + alarm.hpp |
| GET | `/board/<path:port>/connection-status` | `html_board_connection_status(port)` | Board connection status badge partial |

### Board List / Events

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/boards` | `html_boards()` | Board list partial (`partials/board_list.html`) |
| GET | `/boards/event` | `html_boards_event()` | Board events partial (`partials/board_event.html`) |
| GET | `/boards/grid` | `html_boards_grid()` | Board grid partial (`partials/board_grid.html`) |

### Admin

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/admin` | `admin()` | Admin page with board selector, compile/upload, diff view |
| POST | `/medicines/active-board` | `html_medicines_active_board()` | Set active board, render `medicine_cards.html` partial |
| GET | `/medicines/active-board-card` | `html_medicines_active_board_card()` | Active board medicine cards partial |
| GET | `/medicines/board-selector` | `html_medicines_board_selector()` | Board selector dropdown partial |
| GET | `/board/compile-upload-card` | `html_board_compile_upload_card()` | Compile/upload card partial |
| GET | `/daemon/status` | `html_daemon_status()` | Daemon status badge partial |

### alarm.hpp Sync / Generate

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/medicines/confirm-modal` | `html_medicines_confirm_modal()` | Confirmation modal for generate/sync |
| POST | `/medicines/generate-hpp` | `html_medicines_generate_hpp()` | Generate `alarm.hpp` from medicines (confirmation token required) |
| POST | `/medicines/sync-from-hpp` | `html_medicines_sync_from_hpp()` | Sync store from `alarm.hpp` (confirmation token required) |

### Sketch Upload / Management

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/last-upload` | `html_last_upload()` | Last uploaded sketch path selector partial |
| POST | `/sketch/upload` | `html_sketch_upload()` | Upload sketch files (multipart), renders path selector |
| DELETE | `/sketch` | `html_sketch_delete()` | Delete uploaded sketch |

### WebSocket

| Route | Description |
|-------|-------------|
| `WS /ws/board-events` | Live board event streaming via WebSocket (Flask-Sock). Calls `add_ws_client` on connect, `remove_ws_client` on disconnect. |

## Private Helpers

| Function | Purpose |
|----------|---------|
| `_get_active_board_info()` | Return `(port, fqbn, hardware_id)` from session `admin_active_board` |
| `_resolve_first_port_info(ports)` | Return first available `(port, fqbn, hw_id)`, raises `ValueError` |
| `_resolve_board_info(port, fqbn, hw_id, ports)` | Reconcile board info from session + known ports |
| `_write_alarm_hpp(meds)` | Write `alarm.hpp` from medicine list |
| `_medicine_to_dict(med)` | Convert `Medicine` to serializable dict |
| `_medicine_dict_sort_key(d)` | Sort key for medicine dicts |
| `_compute_diff(active_board)` | Compare store medicines vs `alarm.hpp` entries |
| `_issue_confirm_token()` | Generate UUID-based confirmation token in session |
| `_validate_and_consume_confirm_token()` | Validate/consume the confirmation token from form |
| `_require_board()` | Return `board_port` from session, or `None` |
| `_require_any_board()` | Return any available board port from session or active board info |
