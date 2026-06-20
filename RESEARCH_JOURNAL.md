---
---
{% raw %}
# Research Journal — Phase 77: Template Port Path Cleanup

## 2026-06-17 17:03 — Research Complete

### Findings

**9 template locations** use `{{ port.lstrip('/') }}` across 6 template files:

| Template | Lines | Dashboard | Purpose |
|----------|-------|-----------|---------|
| `partials/board_grid.html` | 13 | Both | URL href |
| `partials/board_status_badge.html` | 2 | Both | hx-get URL |
| `partials/compile_upload_card.html` | 17, 41 | medminder_dash | hx-post URLs |
| `board_detail.html` | 11, 33, 41 | medminder_dash | hx-get/hx-post URLs |

**Data flow**:
1. Flask route receives `port` via `<path:port>` (no leading `/`)
2. Route calls `normalize_port(port)` which returns port WITH `/` (e.g., `/dev/ttyACM0`)
3. Template renders `<a href="/board/{{ port.lstrip('/') }}">` producing `/board/dev/ttyACM0`
4. Flask matches this back to the `<path:port>` route

**The inversion**: `normalize_port()` adds `/`, then template removes it for URL construction. This is because:
- gRPC requires the full path (`/dev/ttyACM0`)
- Flask routing with `<path:port>` strips the leading `/`
- URL construction in templates needs the bare form

**`port_path` approach**:
- Route computes `port_path = port.lstrip('/')` once after normalization
- Passes `port_path` in render context alongside `port`
- Templates use `{{ port_path }}` instead of `{{ port.lstrip('/') }}`
- This centralizes the URL-safe port computation

**Risk**: Very low. The templates already do this exact computation. We're just moving it to Python to have a single point of definition. Existing tests validate all URL paths.

**Recommendation**: Proceed with implementation. Phase 77 continues Phase 76's consolidation trajectory.

---

# Research Journal — Phase 79b: arduino_dash init_pubsub Does Not Reconnect After Transient BMS Failure

## 2026-06-18 13:02 — Bug Analysis

### Discovery

User reported no `_on_daemon_ready` logs for both dashboards. Investigation revealed:

**Observed behavior (arduino_dash logs)**:
```
12:47:18  arduino_dash starts → connect(retry=True) to BMS (3 retries over 3.5s)
12:47:21  BMS still not up → ConnectionError → propagate to __main__.py
12:47:21  __main__.py except → "BMS not available; compile/upload disabled"
         pubsub NEVER initialized: no subscribe(), no start_reader(), no reconnection
12:47:24  BMS finally starts → nobody connects → arduino_dash permanently disconnected
```

### Root Cause

Two problems, the first critical, the second cosmetic:

1. **Primary: arduino_dash `init_pubsub` does not catch `connect()` failure internally.**
   - `arduino_dash/.../pubsub.py:97`: `state.pubsub.connect(retry=True)` raises on failure
   - Exception propagates to `__main__.py:33` which catches and logs — but `start_reader()` is NEVER called
   - Without `start_reader()`, there is no `_read_loop` → no `_reconnect()` → no reconnection

2. **Secondary: BMS `_publish_daemon_ready()` emits before any client connects.**
   - `service.py:76`: `_publish_daemon_ready()` is called right after daemon starts
   - At that point, NO clients have connected yet → `subscribers_for("sys::daemon/ready")` returns empty set
   - The event reaches nobody. The actual delivery relies on `_send_daemon_state_to()` in the subscribe handler.

### Architecture Comparison: arduino_dash vs medminder_dash

| Aspect | arduino_dash | medminder_dash |
|--------|-------------|----------------|
| `init_pubsub` catches `connect()` failure | ❌ — propagates to caller | ✅ — caught internally |
| `start_reader()` called after failure | ❌ — never reached | ✅ — always called |
| Reconnection possible | ❌ — no reader thread | ✅ — `_read_loop` → `_reconnect()` |
| `__main__.py` try/except redundant? | No (only safety net) | Yes (safety net, never fires) |

### Flow Comparison

**arduino_dash (BROKEN)**:
```
init_pubsub:
  pubsub = PubSubClient()
  pubsub.connect(retry=True)  ← FAILS → raises ConnectionError
  pubsub.subscribe(...)       ← NEVER REACHED
  pubsub.start_reader()       ← NEVER REACHED
  → exception to __main__.py → warning logged → run without pubsub FOREVER
```

**medminder_dash (WORKS)**:
```
init_pubsub:
  ps = PubSubClient()
  try:
    ps.connect(retry=True)    ← FAILS → caught internally
  except:
    logger.warning(...)
  ps.subscribe(...)           ← STILL REACHED
  ps.start_reader()           ← STILL REACHED
  → reader thread starts → _read_loop → _reconnect() → eventually connects
```

### Fix

Wrap `state.pubsub.connect(retry=True)` in try/except in `arduino_dash/pubsub.py:init_pubsub`, matching the medminder_dash pattern exactly:

```python
try:
    state.pubsub.connect(retry=True)
except (ConnectionError, OSError) as e:
    state.logger.warning("Could not connect to BoardManagerService: %s", e)
```

This ensures `start_reader()` is always called, enabling the reader thread's auto-reconnect loop.

### Test Impact

Existing test `test_connect_failure_propagates` expects `ConnectionRefusedError` to propagate. After the fix, the exception is caught internally, so the test must be updated:

- Remove `pytest.raises(ConnectionRefusedError)` assertion
- Verify that `subscribe()` and `start_reader()` ARE called even when `connect()` fails
- Add assertion that the warning was logged (via `assert_log` or `caplog`)

### Secondary Issue: BMS `_publish_daemon_ready()` Timing

The secondary issue (BMS emits daemon/ready before any client subscribes) is harmless after the primary fix — the reader thread reconnects, subscriptions are re-sent, and `_send_daemon_state_to()` delivers the event on the subscribe response. However, it means the **first client to connect after BMS starts will always get the daemon/ready event** via the subscribe handler, not from the initial broadcast. No fix needed for this — it's correct behavior.
{% endraw %}
