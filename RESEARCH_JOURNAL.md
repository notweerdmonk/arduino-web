---
layout: default
---
{% raw %}
# Research Journal — Phase 98: WS Push Migration (Badge OOB → Compile/Upload OOB → Compile Progress Bar)

**Date**: 2026-06-21 11:55

---

## Contents

1. [Context](#1-context)
2. [Current Polling Surface](#2-current-polling-surface)
3. [WS OOB Pattern Study](#3-ws-oob-pattern-study)
4. [compile_stream() Signature Analysis](#4-compile_stream-signature-analysis)
5. [gRPC TaskProgress Field Study](#5-grpc-taskprogress-field-study)
6. [UploadResponse Capability Check](#6-uploadresponse-capability-check)
7. [Summary of Findings](#7-summary-of-findings)

---

## 1. Context

Research conducted to plan Phase 98 of the MedMinder monorepo. After Phase 97 eliminated Hyperscript (43KB JS saving), two periodic HTMX polls remain: the daemon status badge (`every 10s` in `base.html`) and the board connection status badge (`every 10s` in `board_detail.html`). Meanwhile, compile/upload progress lines are already pushed via WebSocket by `ArduinoSketchTools` but rendered invisibly — they lack `hx-swap-oob` targeting.

The goal is to eliminate all remaining periodic polling and make WS-delivered content visible by using OOB HTML fragments over WS.

## 2. Current Polling Surface

| Endpoint | Trigger | Partial | Render Type |
|----------|---------|---------|-------------|
| `/daemon/status` | `every 10s, load` | `daemon_badge.html` | HTMX AJAX |
| `/board/<port>/connection-status` | `every 10s, load` | `board_status_badge.html` | HTMX AJAX |

Both are small partials (~150-200 bytes) but produce unnecessary HTTP requests on every open page.

### WS-Delivered Content (Currently Invisible)

The `ArduinoSketchTools` Flask extension broadcasts compile/upload progress lines via WebSocket through `broadcast_ws()`. These lines are rendered as HTML but without `hx-swap-oob` targeting — they arrive at the WS client but HTMX doesn't know where to insert them.

## 3. WS OOB Pattern Study

### Existing WS OOB Pattern (Board Events)

The board event feed already uses a working WS OOB pattern:

```python
# pubsub.py: _on_board_event()
html = render_template('partials/board_event.html', event=event)
broadcast_ws(f'<div hx-swap-oob="beforeend:#live-events">{html}</div>')
```

This pattern works because:
1. `broadcast_ws()` sends HTML to all connected WebSocket clients
2. HTMX WS extension receives the message and parses `hx-swap-oob` attributes
3. HTMX performs the swap on the target element

### Proposed Pattern for Badge OOB

```python
# pubsub.py: _broadcast_daemon_badge()
html = render_template('partials/daemon_badge.html', is_ready=state._daemon_ready)
broadcast_ws(f'<span hx-swap-oob="true" id="daemon-badge">{html}</span>')
```

Key differences from board events:
- `hx-swap-oob="true"` replaces the element entirely (not `beforeend`)
- The OOB wrapper must have `id="daemon-badge"` to match the existing element
- The partial is stripped of all `hx-*` attributes (rendered as plain HTML)

## 4. compile_stream() Signature Analysis

### Current Signature (Phase 11/12)

```python
def compile_stream(self, ...) -> Generator[tuple[str, str, bool], None, None]:
    """Yields (out, err, done) tuples."""
```

The 3-tuple is consumed by:
1. `compile()` method in `client.py` — collects into single result
2. `board_worker.py` compile handler — iterates stream, sends progress messages
3. Unit tests — mock `compile_stream()` returns

### Proposed 4-Tuple Signature

```python
def compile_stream(self, ...) -> Generator[tuple[str, str, bool, float], None, None]:
    """Yields (out, err, done, percent) tuples.
    
    percent is 0.0–100.0 from CompileResponse.progress.percent.
    Set to 100.0 when done=True.
    """
```

The `percent` field comes from `CompileResponse.progress.percent` which is a `TaskProgress` message:
```protobuf
message TaskProgress {
    string message = 1;
    float percent = 2;
}
```

### All Callers to Update

| File | Function | Change |
|------|----------|--------|
| `client.py` | `compile()` | Unpack 4-tuple, ignore percent |
| `board_worker.py` | compile handler | Unpack 4-tuple, send percent in progress messages |
| `tests/test_client.py` | mock returns | Update expected tuple |
| `tests/test_board_worker.py` | mock returns | Update expected tuple |

## 5. gRPC TaskProgress Field Study

### CompileResponse

Source: `~/Projects/arduino-cli/rpc/cc/arduino/cli/commands/v1/compile.proto`

```protobuf
message CompileResponse {
    bytes out_stream = 1;
    bytes err_stream = 2;
    TaskProgress progress = 3;
    bool done = 4;
}

message TaskProgress {
    string message = 1;
    float percent = 2;
}
```

The `percent` field represents 0.0–100.0 as a float. The arduino-cli builder emits ~25+ `CompileResponse` messages during a typical compile, with `percent` incrementing from 0 to 100.

### UploadResponse

Source: `~/Projects/arduino-cli/rpc/cc/arduino/cli/commands/v1/upload.proto`

```protobuf
message UploadResponse {
    bytes out_stream = 1;
    bytes err_stream = 2;
    bool done = 3;
}
```

**No `TaskProgress` field.** Upload progress bar is NOT feasible at the gRPC level. Upload consists of only `out_stream`, `err_stream`, and `done` — the same 3-tuple as the current compile signature.

## 6. UploadResponse Capability Check

### Proto Analysis

The upload.proto file was examined at the same location as compile.proto. Confirmed:
- No `progress` field in `UploadResponse`
- No `TaskProgress` submessage
- Only `out_stream`, `err_stream`, `done` fields

### Conclusion

Upload progress bar cannot be implemented at the gRPC/arduino-cli level. The arduino-cli does not report upload progress. Tier 3 of Phase 98 applies only to compilation.

If upload progress is needed in the future, it would require:
1. Parsing avrdude output for percentage patterns (`"Writing | ################################################## | 100% 0.48s"`)
2. Hueristic/synthetic progress based on upload phases (binary size, erase time, write time, verify time)

## 7. Summary of Findings

### Phase 98 Quanta

| Q | Task | Effort | Risk | Dependencies |
|---|------|--------|------|-------------|
| 1 | Daemon badge OOB | ~30min | Low | Existing WS broadcast infrastructure |
| 2 | Board status badge OOB | ~30min | Low | Existing `_on_board_event` handler |
| 3 | Compile/upload OOB targeting | ~15min | Low | Existing WS progress lines |
| 4 | Compile progress percentage | ~1h | Low | `compile_stream()` 4-tuple clean break |
| 5 | Noxfile `PROJECT_ROOT` fix | ~5min | None | Pre-existing pipenv lock failures |

### Key Decisions

1. **OOB HTML over WS**: Direct HTML fragments with `hx-swap-oob` over WS eliminates extra HTTP round-trips. Proven pattern from existing board event pushes.
2. **Keep `hx-trigger="load"`**: The one-shot `load` trigger on wrapper spans is retained for initial render (pubsub may not be connected when page loads). WS push takes over after initial render.
3. **Unique per-port badge IDs**: `board-status-badge--{port_safe}` prevents badge collisions when multiple board_detail pages are open.
4. **Clean break for 4-tuple**: Update all callers of `compile_stream()` simultaneously rather than adding a separate method or optional parameter. Upload remains 3-tuple.
5. **Progress-only messages**: Board worker sends messages containing only percent (no output text) when only the progress bar advances. This avoids redundant WS pushes of unchanged content.
6. **Track `_compile_last_pct`**: Only broadcast progress bar OOB when percent value changes. Prevents ~25+ progress bar updates per compile from degenerating into `_compile_last_pct` tracking avoids redundant broadcasts when percent doesn't advance between consecutive gRPC messages.

### Files to Modify

| File | Change |
|------|--------|
| `arduino_dash/.../templates/base.html:17` | `hx-trigger="every 10s, load"` → `"load"` |
| `medminder_dash/.../templates/base.html:17` | Same |
| Both `templates/partials/daemon_badge.html` | Strip hx-* attributes |
| Both `templates/partials/board_status_badge.html` | Strip hx-* attributes |
| Both `templates/board_detail.html` | Unique badge IDs, add progress bar |
| `arduino_dash/.../pubsub.py` | `_broadcast_daemon_badge()`, board badge OOB |
| `medminder_dash/.../pubsub.py` | Same |
| `arduino_sketch_tools/.../extension.py:180-214` | OOB targeting + progress tracking |
| `arduino_grpc/.../client.py:305` | `compile_stream()` yields 4-tuple |
| `board_manager/.../board_worker.py:39-154` | `_make_progress()` with percent |
| `noxfile.py:57` | `env={"PROJECT_ROOT": str(ROOT)}` |
{% endraw %}
