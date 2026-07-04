---
layout: default
---
# `medicines_state.py` — Medicine Data Model and Store

**File:** `medminder_dash/medicines_state.py`

## Class: `Medicine`

A single medicine entry with schedule fields. Implemented as a `@dataclass`.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `""` | UUID hex string (auto-generated in `__post_init__` if empty) |
| `name` | `str` | `""` | Medicine name |
| `hour` | `int` | `0` | Hour (1–24, 24 = midnight) |
| `minute` | `int` | `0` | Minute (0, 10, 20, 30, 40, or 50) |
| `day_of_week` | `int` | `0` | Day of week (0 = every day, 1 = Monday ... 7 = Sunday) |
| `day_of_month` | `int` | `0` | Day of month (0 = every day, 1–31) |
| `enabled` | `bool` | `True` | Whether the medicine is active |

### `__post_init__(self)`

Generates a UUID hex string via `uuid.uuid4().hex` if `self.id` is empty.

```python
med = Medicine(name="Aspirin", hour=8, minute=30)
# med.id -> "a1b2c3d4e5f6..."
```

## Function: `_compute_data_path() -> Path`

Return the filesystem path to the `board_meta.json` data file.

Location: `<package_root>/data/board_meta.json` (parent of `medminder_dash/` directory)

## Class: `MedicineStore`

Thread-safe persistent store for medicine data per board port. Backed by a JSON
file (`data/board_meta.json`).

### Constructor: `__init__(self)`

```python
store = MedicineStore()
```

Initializes:
- `_lock` — `threading.Lock()` for thread safety
- `_data_file` — path from `_compute_data_path()`
- `_board_meta` — dict of board → `{"medicines": [...]}`
- `_medicines` — list of `Medicine` for the current board
- Calls `_load()` to populate `_board_meta` from disk

### `_load(self) -> None`

Load board meta data from the JSON data file. If the file doesn't exist or
can't be parsed, initializes empty `_board_meta`.

### `_save(self) -> None`

Persist board meta data to the JSON data file. If a `_current_port` is set,
saves the current medicines under that port's key. Serializes all boards'
medicines as dicts.

### `load_board(self, port: Optional[str]) -> None`

Load medicines for a given board port. Sets `_current_port` and populates
`_medicines` from `_board_meta[port]["medicines"]`. Exising medicines are
replaced.

| Param | Type | Purpose |
|-------|------|---------|
| `port` | `Optional[str]` | Board port string, or `None` to load nothing |

```python
store.load_board("/dev/ttyACM0")
```

### `all(self) -> list`

Return a thread-safe copy of all medicines.

```python
meds = store.all()
# [Medicine(name="Aspirin", ...), Medicine(name="Vitamin D", ...)]
```

### `only_enabled(self) -> list`

Return a thread-safe list of only enabled medicines.

```python
enabled = store.only_enabled()
# [Medicine(name="Aspirin", ..., enabled=True)]
```

### `add(self, medicine: Medicine) -> str`

Add a medicine to the store and persist.

| Param | Type | Purpose |
|-------|------|---------|
| `medicine` | `Medicine` | Medicine instance to add |

Returns: The medicine's ID.

```python
med = Medicine(name="Aspirin", hour=8, minute=30)
store.add(med)
```

### `get(self, med_id: str) -> Optional[Medicine]`

Retrieve a copy of a medicine by ID.

| Param | Type | Purpose |
|-------|------|---------|
| `med_id` | `str` | The medicine's unique ID |

Returns: A copy of the `Medicine`, or `None` if not found.

```python
med = store.get("a1b2c3d4")
```

### `update(self, med_id: str, **kwargs) -> None`

Update fields on a medicine by ID and persist.

| Param | Type | Purpose |
|-------|------|---------|
| `med_id` | `str` | The medicine's unique ID |
| `**kwargs` | `dict` | Field name/value pairs to update |

```python
store.update(med.id, name="Baby Aspirin", hour=9)
```

### `delete(self, med_id: str) -> bool`

Delete a medicine by ID and persist.

| Param | Type | Purpose |
|-------|------|---------|
| `med_id` | `str` | The medicine's unique ID |

Returns: `True` if deleted, `False` if not found.

```python
if store.delete(med.id):
    print("Deleted")
```

### `toggle(self, med_id: str) -> None`

Toggle the enabled state of a medicine by ID and persist.

| Param | Type | Purpose |
|-------|------|---------|
| `med_id` | `str` | The medicine's unique ID |

```python
store.toggle(med.id)  # enabled -> disabled (or vice versa)
```

## Persistence Format

The `board_meta.json` file has the following structure:

```json
{
  "/dev/ttyACM0": {
    "medicines": [
      {
        "id": "a1b2c3d4e5f6...",
        "name": "Aspirin",
        "hour": 8,
        "minute": 30,
        "day_of_week": 0,
        "day_of_month": 0,
        "enabled": true
      }
    ]
  }
}
```
