---
---
# utils (utils.py)

Utility functions for board info, port validation, and board lookup from the shared `state._board_list`.

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `PORT_RE` | `r"^/dev/[a-zA-Z0-9_/]+$"` | Regex for validating serial port paths |

## Functions

### `is_valid_port(port: str) -> bool`

Check whether a port string matches the expected `/dev/...` format.

```python
is_valid_port("/dev/ttyACM0")   # True
is_valid_port("/dev/ttyUSB1")   # True
is_valid_port("COM3")           # False
is_valid_port("/invalid/path")  # False
```

### `normalize_port(port: str) -> Optional[str]`

Normalize and validate a port path. Strips extra leading slashes, ensures exactly one `/` prefix, then validates against `PORT_RE`. Returns the normalized port if valid, `None` otherwise.

```python
normalize_port("/dev/ttyACM0")   # "/dev/ttyACM0"
normalize_port("//dev/ttyACM0")  # "/dev/ttyACM0"
normalize_port("COM3")           # None
normalize_port("dev/ttyACM0")    # "/dev/ttyACM0"
```

### `get_known_boards() -> list[dict]`

Return a copy of the known boards list from `state._board_list`.

```python
boards = get_known_boards()
# Returns: [{"port": "/dev/ttyACM0", "fqbn": "arduino:avr:uno", ...}, ...]
```

### `get_board_events() -> list[dict]`

Return a snapshot of recent board events from `state._board_events` (capped at 100, newest first). Each event dict contains `port`, `event` ("connected"/"disconnected"), `board`, `fqbn`, `hardware_id`.

```python
events = get_board_events()
# Returns: [{"port": "/dev/ttyACM0", "event": "connected", ...}, ...]
```

### `get_first_board(boards: list[dict]) -> Tuple[str, str, str]`

Return the `(port, fqbn, hardware_id)` of the first board in the list. Returns an empty tuple of `("", "", "")` if the list is empty or invalid.

```python
port, fqbn, hw_id = get_first_board(known_boards)
# ("/dev/ttyACM0", "arduino:avr:uno", "ABC123")
```

### `get_port_info(port: str) -> Optional[dict]`

Return the board info dict for the given port from `state._board_list`. Returns `{}` if the port is not found.

```python
info = get_port_info("/dev/ttyACM0")
# Returns: {"port": "/dev/ttyACM0", "fqbn": "...", "board": "...", ...}
```

### `find_board_info_by_port(port: str, boards: list[dict]) -> dict`

Find board info by port string from a list of board dicts. Returns the matching board dict or `{}`.

```python
board = find_board_info_by_port("/dev/ttyACM0", boards)
```

### `find_board_info_by_fqbn(fqbn: str, boards: list[dict]) -> dict`

Find board info by FQBN string from a list of board dicts. Returns the matching board dict or `{}`.

```python
board = find_board_info_by_fqbn("arduino:avr:uno", boards)
```
