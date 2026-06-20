---
---
# Blueprint Routes

**Source:** `arduino_sketch_tools/routes.py`

**Blueprint name:** `arduino_sketch_tools`  
**Blueprint variable:** `compile_bp`  
**Template folder:** `templates/`

All routes are registered on a single `Blueprint` named
`arduino_sketch_tools`. The template folder is set to `templates/`, and all
templates are HTML partials intended for HTMX swap targets.

---

## Route Table

| Method | Path | View Function | Description |
|---|---|---|---|
| POST | `/board/<path:port>/compile` | `api_compile` | Start a sketch compile |
| GET | `/board/<path:port>/compile/poll` | `api_compile_poll` | Poll compile status |
| POST | `/board/<path:port>/upload` | `api_upload` | Start a sketch upload (with warnings check) |
| GET | `/board/<path:port>/upload/poll` | `api_upload_poll` | Poll upload status |
| POST | `/board/<path:port>/upload/confirm` | `api_upload_confirm` | Confirm upload after warnings |
| GET | `/board/<path:port>/upload/section` | `api_upload_section` | Return upload section partial |

---

## Route Details

### `POST /board/<path:port>/compile`

**View function:** `api_compile(port: str)`

Start a sketch compile by publishing a command to the BoardManagerService via
pub/sub. Returns an in-progress partial template immediately.

**Request parameters** (form-encoded):

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sketch_path` | `str` | `""` | Path to the sketch directory on the server |
| `fqbn` | `str` | `arduino:avr:uno` | Fully-qualified board name |
| `verbose` | `bool` | `false` | Enable verbose compiler output |

**Flow:**

1. Normalize and validate `port`. Returns `400` JSON on invalid port.
2. Check pub/sub connection. Returns `bms_offline.html` partial if
   disconnected.
3. Reset `_compile_results[port]` to `None`.
4. Store compile metadata via `_make_meta()`.
5. Publish a pub/sub message on topic `board::{port}::cmd`:
   ```python
   {
       "method": "compile",
       "params": {
           "sketch_path": sketch_path,
           "fqbn": fqbn,
           "verbose": verbose,
       },
   }
   ```
   with response topic `resp::compile::{port}`.
6. Return `compile_in_progress.html` partial.

**Response:** HTML partial (`compile_in_progress.html`).  
**Error response:** `{"error": "Invalid port"}` with status 400.

---

### `GET /board/<path:port>/compile/poll`

**View function:** `api_compile_poll(port: str)`

Poll compile status and return the appropriate partial template. Intended to
be called via HTMX polling (e.g. `hx-trigger="every 2s"`).

**Flow:**

1. Normalize and validate `port`. Returns `400` JSON on invalid port.
2. Retrieve `_compile_results[port]` and `_compile_meta[port]`.
3. **If result is `None`:**
   - Check if `COMPILE_TIMEOUT` (150s) has elapsed since `started_at`.
   - **Timed out:** Clean up metadata and return `compile_timeout.html`.
   - **Still waiting:** Return `compile_poll_pending.html`.
4. **If result is present (compile finished):**
   - **On success (`status == "ok"`):** Record the sketch path, update
     `_last_compile_mtime` and `_last_compile_checksum`.
   - **On error:** Detect whether the sketch was modified since the last
     successful compile (first by mtime, then by SHA-256 checksum as
     fallback). If modified, set `compile_warning = "sketch_modified"`.
   - Clean up compile metadata.
   - Return `compile_result.html` partial with `result`, `port`, `meta`, and
     `compile_warning` variables.

**Response:** One of:
- `compile_poll_pending.html` — compile still running
- `compile_timeout.html` — exceeded 150s timeout
- `compile_result.html` — final result with optional modification warning

**Error response:** `{"error": "Invalid port"}` with status 400.

---

### `POST /board/<path:port>/upload`

**View function:** `api_upload(port: str)`

Start a sketch upload via pub/sub, but first checks for warnings that should
be acknowledged by the user.

**Request parameters** (form-encoded):

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sketch_path` | `str` | `""` | Path to the sketch directory |
| `fqbn` | `str` | `arduino:avr:uno` | Fully-qualified board name |
| `verbose` | `bool` | `false` | Enable verbose upload output |

**Warning detection:**

The route checks two conditions before proceeding:

1. **Sketch path changed:** If `_last_compiled_sketch[port]` differs from the
   requested `sketch_path`, a warning of type `sketch_path_changed` is added
   with `old` and `new` fields.
2. **Sketch modified after last compile:** Detected first by comparing the
   latest source-file mtime against `_last_compile_mtime[port]`. If mtime is
   unchanged, falls back to comparing
   `_compute_sketch_checksum(sketch_path)` against
   `_last_compile_checksum[port]`. A warning of type `sketch_modified` is
   added.

**If warnings exist:**
Return `upload_confirm.html` partial with the warning list. The user must
POST to `/board/<path:port>/upload/confirm` to proceed.

**If no warnings:**
Proceed directly to upload:
1. Record `_last_uploaded_sketch[port]`.
2. Reset `_upload_results[port]` to `None`.
3. Store upload metadata via `_make_meta()`.
4. Publish a pub/sub message on topic `board::{port}::cmd`:
   ```python
   {
       "method": "upload",
       "params": {
           "sketch_path": sketch_path,
           "fqbn": fqbn,
           "port": port,
           "verbose": verbose,
       },
   }
   ```
   with response topic `resp::upload::{port}`.
5. Return `upload_in_progress.html` partial.

**Response:** HTML partial — either `upload_confirm.html` or
`upload_in_progress.html`.  
**Error response:** `{"error": "Invalid port"}` with status 400.

---

### `GET /board/<path:port>/upload/poll`

**View function:** `api_upload_poll(port: str)`

Poll upload status and return the appropriate partial template. Intended to be
called via HTMX polling.

**Flow:**

1. Normalize and validate `port`. Returns `400` JSON on invalid port.
2. Retrieve `_upload_results[port]` and `_upload_meta[port]`.
3. **If result is `None`:** Return `upload_poll_pending.html`.
4. **If result is present:** Clean up metadata and return
   `upload_result.html` partial with `result`, `port`, and `meta` variables.

**Response:** One of:
- `upload_poll_pending.html` — upload still running
- `upload_result.html` — final result

**Error response:** `{"error": "Invalid port"}` with status 400.

---

### `POST /board/<path:port>/upload/confirm`

**View function:** `api_upload_confirm(port: str)`

Confirm and start an upload after warnings have been acknowledged by the user.
This route skips the warning checks and proceeds directly to publish the
upload command.

**Request parameters** (form-encoded):

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sketch_path` | `str` | `""` | Path to the sketch directory |
| `fqbn` | `str` | `arduino:avr:uno` | Fully-qualified board name |
| `verbose` | `bool` | `false` | Enable verbose upload output |

**Flow:**

1. Normalize and validate `port`. Returns `400` JSON on invalid port.
2. Check pub/sub connection. Returns `bms_offline.html` partial if
   disconnected.
3. Record `_last_uploaded_sketch[port]`.
4. Reset `_upload_results[port]` to `None`.
5. Store upload metadata via `_make_meta()`.
6. Publish the same pub/sub upload command as `api_upload`.
7. Return `upload_in_progress.html` partial.

**Response:** HTML partial (`upload_in_progress.html`).  
**Error response:** `{"error": "Invalid port"}` with status 400.

---

### `GET /board/<path:port>/upload/section`

**View function:** `api_upload_section(port: str)`

Return the upload section partial template for a given port. Used for
rendering the initial upload UI for a board.

**Flow:**

1. Normalize and validate `port`. Returns `400` JSON on invalid port.
2. Return `upload_init.html` partial with `port` variable.

**Response:** HTML partial (`upload_init.html`).  
**Error response:** `{"error": "Invalid port"}` with status 400.

---

## HTMX Partial Templates

All partials live under `templates/partials/`. They are designed as HTMX swap
targets, not full HTML documents.

| Template | Context Variables | Rendered When |
|---|---|---|
| `bms_offline.html` | `section_id`, `action` | Pub/sub is disconnected |
| `compile_in_progress.html` | `port` | Compile command published |
| `compile_poll_pending.html` | `port`, `meta` | Compile still running |
| `compile_timeout.html` | `port`, `meta` | Compile exceeded 150s timeout |
| `compile_result.html` | `result`, `port`, `meta`, `compile_warning` | Compile finished |
| `upload_confirm.html` | `port`, `warnings`, `sketch_path`, `fqbn`, `verbose` | Upload warnings detected |
| `upload_in_progress.html` | `port` | Upload command published |
| `upload_poll_pending.html` | `port`, `meta` | Upload still running |
| `upload_result.html` | `result`, `port`, `meta` | Upload finished |
| `upload_init.html` | `port` | Initial upload section render |

---

## Compile Timeout

The compile timeout is set to **150 seconds** (`ArduinoSketchTools.COMPILE_TIMEOUT`).
When the poll route detects that a compile has been running longer than this
threshold and no result has arrived, it returns the `compile_timeout.html`
partial and removes the compile metadata for that port.

---

## Sketch Modification Detection

Both the upload and compile-poll routes detect whether a sketch has been
modified since the last successful compile. The detection uses a two-tier
strategy:

1. **mtime check (fast):** Compare the latest source-file modification time
   (`os.path.getmtime`) against `_last_compile_mtime[port]`.
2. **Checksum check (accurate):** If mtime is unchanged (e.g. git checkout
   that preserves timestamps), compute a SHA-256 checksum of all source files
   via `_compute_sketch_checksum()` and compare against
   `_last_compile_checksum[port]`.

When a modification is detected, `compile_warning` is set to
`"sketch_modified"` in the compile result template, and an upload warning of
type `sketch_modified` is added to force user confirmation.
