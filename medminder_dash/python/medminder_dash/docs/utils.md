---
layout: default
---
# `utils.py` — Utility Functions

**File:** `medminder_dash/utils.py`

Utility functions for port management, board info lookup, medicine data
validation, and time/day display formatting.

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `VALID_MINUTES` | `{0, 10, 20, 30, 40, 50}` | Allowed minute values (10-minute increments) |
| `PORT_RE` | `r"^/dev/[a-zA-Z0-9_/]+$"` | Regex for valid port paths |

## Port Functions

### `is_valid_port(port: str) -> bool`

Check whether a port path matches the expected `/dev/...` pattern.

```python
is_valid_port("/dev/ttyACM0")   # True
is_valid_port("/invalid/path")  # False
```

### `normalize_port(port: str) -> Optional[str]`

Normalize and validate a port path. Strips extra leading slashes, ensures
exactly one `/` prefix, validates against `PORT_RE`.

```python
normalize_port("dev/ttyACM0")   # "/dev/ttyACM0"
normalize_port("//dev/ttyACM0") # "/dev/ttyACM0"
normalize_port("invalid")       # None
```

### `get_known_ports() -> list[dict]`

Return a snapshot of all known board ports as a list of info dicts. Thread-safe
(snapshot under `state._known_ports_lock`).

```python
ports = get_known_ports()
# [{"port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", ...}]
```

### `get_first_board(boards: list[dict]) -> Tuple[str, str, str]`

Return `(port, fqbn, hardware_id)` of the first board in the list, or
`("", "", "")` if the list is empty.

### `get_board_events() -> list[dict]`

Return a snapshot of recent board events (thread-safe copy under
`state._board_events_lock`).

### `get_port_info(port: str) -> Optional[dict]`

Return info dict for a specific port, or empty dict if unknown.

```python
info = get_port_info("/dev/ttyACM0")
# {"port": "/dev/ttyACM0", "board": "Arduino Uno", ...}
```

### `find_board_info_by_port(port: str, boards: list[dict]) -> dict`

Find board info dict by port in a list of boards, or empty dict.

### `find_board_info_by_fqbn(fqbn: str, boards: list[dict]) -> dict`

Find board info dict by FQBN in a list of boards, or empty dict.

```python
info = find_board_info_by_fqbn("arduino:avr:uno", get_known_ports())
```

## Validation

### `validate_medicine_data(data: dict) -> list[str]`

Validate medicine form/JSON data. Returns a list of error messages (empty if
valid).

| Field | Rule |
|-------|------|
| `name` | Required, max 10 characters |
| `hour` | Must be integer, 1–24 |
| `minute` | Must be integer, one of {0, 10, 20, 30, 40, 50} |
| `day_of_week` | Must be integer, 0–7 |
| `day_of_month` | Must be integer, 0–31 |

```python
errors = validate_medicine_data({"name": "Aspirin", "hour": 8, "minute": 30})
# []  (valid)

errors = validate_medicine_data({"name": "", "hour": 25, "minute": 5})
# ["Name is required", "Hour must be 1-24", "Minute must be 0, 10, 20, 30, 40, or 50"]
```

## Display Helpers

### `day_name(dow: int) -> str`

Return the display name for a day-of-week value (0–7).

| Value | Returns |
|-------|---------|
| 0 | `"Every day"` |
| 1–7 | `"Monday"`–`"Sunday"` |

### `hour_display(hour: int) -> str`

Format hour as a zero-padded two-digit string (24 → `"00"`).

```python
hour_display(8)   # "08"
hour_display(24)  # "00"
```

### `minute_display(minute: int) -> str`

Format minute as a zero-padded two-digit string.

```python
minute_display(0)   # "00"
minute_display(30)  # "30"
```

### `time_display(hour: int, minute: int) -> str`

Format hour and minute as `HH:MM` display string.

```python
time_display(8, 30)   # "08:30"
time_display(24, 0)   # "00:00"
```
