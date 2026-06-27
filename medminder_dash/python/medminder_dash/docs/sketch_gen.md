---
---
# `sketch_gen.py` — Sketch Generation

**File:** `medminder_dash/sketch_gen.py`

Generate and parse `alarm.hpp` C++ header files from medicine data. Handles
bidirectional conversion between Python `Medicine` objects and the C struct
format used by the Arduino MedMinderV2 firmware.

## Constants

| Name | Description |
|------|-------------|
| `_ENTRY_RE` | Regex for parsing alarm.hpp entries: `{dayOfMonth, dayOfWeek, hour, decade, "text"}` |

## Functions

### `unesc_text(text: str) -> str`

Unescape backslash-escaped quotes and backslashes in text. Performs:
- `\\"` → `"`
- `\\\\` → `\`

| Param | Type | Purpose |
|-------|------|---------|
| `text` | `str` | Escaped string |

Returns: Unescaped string.

```python
unesc_text('hello \\"world\\"')  # hello "world"
```

### `esc_text(text: str) -> str`

Escape backslashes and double-quotes for C string inclusion. Performs:
- `\` → `\\\\`
- `"` → `\\"`

| Param | Type | Purpose |
|-------|------|---------|
| `text` | `str` | Raw string |

Returns: C-safe escaped string.

```python
esc_text('hello "world"')  # hello \"world\"
```

### `minute_to_decade(minute: int) -> int`

Convert minute (0, 10, 20, 30, 40, 50) to a decade index (0–5) for the
firmware's compact representation.

| Param | Type | Purpose |
|-------|------|---------|
| `minute` | `int` | Minute value (must be a multiple of 10 in 0–50) |

Returns: Decade index (`minute // 10`).

```python
minute_to_decade(0)   # 0
minute_to_decade(30)  # 3
minute_to_decade(50)  # 5
minute_to_decade(5)   # ValueError
```

### `validate_hour(hour: int) -> int`

Validate hour is in the 1–24 range.

| Param | Type | Purpose |
|-------|------|---------|
| `hour` | `int` | Hour value to validate |

Returns: The validated hour.

```python
validate_hour(8)   # 8
validate_hour(24)  # 24
validate_hour(0)   # ValueError
validate_hour(25)  # ValueError
```

### `generate_alarm_hpp(medicines: list[Medicine]) -> str`

Generate the full C++ `alarm.hpp` file content from a list of medicine objects.

**Output format:**

```cpp
#ifndef ALARM_HPP
#define ALARM_HPP

struct Medicine {
  uint8_t     dayOfMonth;
  uint8_t     dayOfWeek;
  uint8_t     hour;
  uint8_t     decade;
  const char* text;
};

const Medicine medicines[] = {
  {0, 0, 8, 3, "Aspirin"},
  {0, 1, 14, 0, "Vitamin D"},
};

#define N_MED  (sizeof(medicines) / sizeof(medicines[0]))

#endif  // ALARM_HPP
```

| Param | Type | Purpose |
|-------|------|---------|
| `medicines` | `list[Medicine]` | List of `Medicine` dataclass instances |

Returns: The full `alarm.hpp` file content as a string.

Only enabled medicines are included (skips medicines where `med.enabled` is
`False`).

```python
meds = [
    Medicine(name="Aspirin", hour=8, minute=30, day_of_week=0, day_of_month=0),
    Medicine(name="Vitamin D", hour=14, minute=0, day_of_week=1, day_of_month=0),
]
content = generate_alarm_hpp(meds)
```

### `parse_alarm_hpp(path: str | Path) -> list[dict[str, Any]]`

Parse an `alarm.hpp` file and return a list of medicine dicts, enabling
round-trip conversion (Python → C++ → Python).

| Param | Type | Purpose |
|-------|------|---------|
| `path` | `str | Path` | Path to the `alarm.hpp` file |

Returns: List of dicts with keys `name`, `hour`, `minute`, `day_of_week`,
`day_of_month`.

The minute field is reconstructed by multiplying the decade value by 10.

```python
entries = parse_alarm_hpp("/path/to/alarm.hpp")
# [{"name": "Aspirin", "hour": 8, "minute": 30, "day_of_week": 0, "day_of_month": 0}]
```

## Round-Trip Example

```python
from medminder_dash.medicines_state import Medicine
from medminder_dash.sketch_gen import generate_alarm_hpp, parse_alarm_hpp

# Python -> C++
meds = [
    Medicine(name="Aspirin", hour=8, minute=30, day_of_week=0),
    Medicine(name="Vitamin D", hour=14, minute=0, day_of_week=1),
]
hpp_content = generate_alarm_hpp(meds)

# Write to file
with open("/tmp/alarm.hpp", "w") as f:
    f.write(hpp_content)

# C++ -> Python (round-trip)
parsed = parse_alarm_hpp("/tmp/alarm.hpp")
assert parsed[0]["name"] == "Aspirin"
assert parsed[0]["hour"] == 8
assert parsed[0]["minute"] == 30
```

## C Struct Layout on Firmware

The `alarm.hpp` struct is consumed by the MedMinderV2 Arduino firmware:

```cpp
struct Medicine {
  uint8_t     dayOfMonth;   // 0 = every day, 1-31
  uint8_t     dayOfWeek;    // 0 = every day, 1 = Monday ... 7 = Sunday
  uint8_t     hour;         // 1-24 (24 = midnight/00)
  uint8_t     decade;       // 0-5 (minute / 10)
  const char* text;         // Medicine name (C string)
};
```

`N_MED` is computed at compile time via `sizeof` on the array.
