---
---
# TopicRouter

## Purpose

An MQTT-style pub/sub topic router that maps topic patterns to subscriber IDs. Uses `::` (double colon) as the topic separator — chosen because it never appears in serial port paths like `/dev/ttyACM0`.

Supports two wildcards:
- `+` — matches exactly one level
- `*` — matches any remaining levels (must be the last segment)

## Location

`board_manager/router.py`

---

## Module-Level Constants

| Name | Value | Description |
|------|-------|-------------|
| `_SEP` | `"::"` | Topic level separator |

## Type Aliases

```python
SubscriberId = str
EventHandler = Callable[[dict], None]
```

---

## Module-Level Function

### `_match(topic: str, pattern: str) -> bool`

Matches a concrete topic string against a wildcard pattern.

| Param | Type | Description |
|-------|------|-------------|
| `topic` | `str` | The concrete topic to match |
| `pattern` | `str` | The wildcard pattern |

Returns `True` if the topic matches the pattern.

**Matching rules:**
- `+` matches exactly one level (any value)
- `*` matches any number of remaining levels (must be last)
- Literal segments must match exactly

```python
_match("board::/dev/ttyACM0::event", "board::+::event")     # → True
_match("board::/dev/ttyACM0::event", "board::*")            # → True
_match("board::/dev/ttyACM0::event", "board::+::status")    # → False
_match("board::/dev/ttyACM0::event", "board::+::+")         # → True
_match("sys::daemon/ready", "+::daemon/ready")              # → True
_match("sys::daemon/ready", "*")                             # → True
```

---

## Class: `TopicRouter`

Topic-based pub/sub router with wildcard support.

### `__init__(self)`

Initialises with empty subscriptions (`defaultdict(set)`) and handlers dict.

### `subscribe(self, subscriber_id: SubscriberId, topic_pattern: str, handler: Optional[EventHandler] = None) -> None`

Subscribes a client to a topic pattern.

| Param | Type | Description |
|-------|------|-------------|
| `subscriber_id` | `SubscriberId` | Unique client identifier (e.g., `"tcp:127.0.0.1:54321"`) |
| `topic_pattern` | `str` | Topic pattern with optional `+`/`*` wildcards |
| `handler` | `Optional[EventHandler]` | Optional callback invoked on publish |

```python
router.subscribe("client-1", "board::+::event")
router.subscribe("client-1", "sys::daemon/ready")
router.subscribe("client-2", "board::*", handler=my_on_message)
```

### `unsubscribe(self, subscriber_id: SubscriberId, topic_pattern: str) -> None`

Removes a subscription for a client on a specific pattern. Cleans up the pattern entry if no subscribers remain.

### `unsubscribe_all(self, subscriber_id: SubscriberId) -> None`

Removes all subscriptions for a client across all patterns. Also removes any registered handler for that subscriber.

### `publish(self, topic: str, message: dict) -> list[SubscriberId]`

Publishes a message to all subscribers whose patterns match the topic.

| Param | Type | Description |
|-------|------|-------------|
| `topic` | `str` | The concrete topic string |
| `message` | `dict` | The message dict to deliver |

Returns a list of subscriber IDs that received the message.

Calls any registered `EventHandler` callbacks synchronously.

### `subscribers_for(self, topic: str) -> set[SubscriberId]`

Returns all subscriber IDs matching a given topic without publishing a message.

| Param | Type | Description |
|-------|------|-------------|
| `topic` | `str` | The concrete topic string |

Returns a `set[SubscriberId]`.

### `patterns` (property) -> `list[str]`

Returns all registered topic patterns.

---

### Usage Examples

```python
from board_manager.router import TopicRouter

router = TopicRouter()

# Subscribe
router.subscribe("webapp-1", "board::+::event")
router.subscribe("webapp-1", "board::+::status")
router.subscribe("admin-ui", "board::*")

# Publish
router.publish("board::/dev/ttyACM0::event", {
    "type": "event",
    "data": {"event": "connected", "port": "/dev/ttyACM0"},
})
# → Delivers to both webapp-1 and admin-ui

# Check subscribers
subs = router.subscribers_for("board::/dev/ttyACM0::status")
# → {"webapp-1", "admin-ui"}
```

### Edge Cases

- **Duplicate subscribers:** Each subscriber ID is stored in a `set` per pattern, so duplicate subscriptions are idempotent
- **Handler per subscriber:** Only one handler per `subscriber_id` is stored; calling `subscribe` again with a new handler replaces the old one
- **Empty subscriptions:** Publishing to a topic with no subscribers returns an empty list (no error)
- **Wildcard at non-terminal position:** `*` must be the last segment; `+` can appear anywhere
