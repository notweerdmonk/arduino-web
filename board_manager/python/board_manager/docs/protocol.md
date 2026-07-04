---
layout: default
---
# Protocol Module

## Purpose

Provides the wire-level framing protocol used for communication between clients (web apps) and the `BoardManagerService`, as well as between `BoardManagerService` and board worker subprocesses.

Two framing modes are supported:
- **Newline-framed** (`"newline"`): each JSON message is terminated by `\n`
- **Length-prefixed** (`"length"`): each JSON message is prefixed by a 4-byte big-endian unsigned integer indicating payload length

## Location

`board_manager/protocol.py`

---

## Enums

### `class Handshake(Enum)`

Handshake byte values for protocol detection:

| Member | Value | Description |
|--------|-------|-------------|
| `NEWLINE` | `b"\x01"` | Client wants newline framing |
| `LENGTH` | `b"\x02"` | Client wants length-prefixed framing |

### `class Framing(IntEnum)`

Constants for length-prefixed framing:

| Member | Value | Description |
|--------|-------|-------------|
| `HEADER_LENGTH` | `4` | Size of the length prefix in bytes |

### `class FramingMode(str, Enum)`

| Member | Value | Description |
|--------|-------|-------------|
| `NEWLINE` | `"newline"` | Newline-terminated frames |
| `LENGTH` | `"length"` | Length-prefixed frames |

---

## Functions

### `encode_message(msg: dict) -> bytes`

Encodes a dict as compact JSON bytes (no whitespace separators).

```python
encode_message({"type": "ping"})
# → b'{"type":"ping"}'
```

### `decode_frame(data: bytes) -> dict`

Decodes JSON bytes to a dict.

```python
decode_frame(b'{"type":"pong"}')
# → {"type": "pong"}
```

### `frame_newline(payload: bytes) -> bytes`

Frames a payload with a trailing newline.

```python
frame_newline(b'{"type":"ping"}')
# → b'{"type":"ping"}\n'
```

### `frame_length(payload: bytes) -> bytes`

Frames a payload with a 4-byte big-endian length prefix.

```python
frame_length(b'{"type":"ping"}')
# → b'\\x00\\x00\\x00\\x0e{"type":"ping"}'
```

### `detect_mode_from_handshake(data: bytes) -> Optional[str]`

Detects the framing mode from the first byte of a client handshake.

| Param | Type | Description |
|-------|------|-------------|
| `data` | `bytes` | First byte(s) received from client |

Returns `"newline"`, `"length"`, or `None` if undetermined.

### `encode_and_frame(msg: dict, mode: str = "newline") -> bytes`

Encodes a message dict and frames it for transmission in one call.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `msg` | `dict` | — | Message to encode |
| `mode` | `str` | `"newline"` | Framing mode |

```python
encode_and_frame({"type": "ping"}, "newline")
# → b'{"type":"ping"}\n'

encode_and_frame({"type": "ping"}, "length")
# → b'\\x00\\x00\\x00\\x0e{"type":"ping"}'
```

---

## Class: `FrameReader`

Reads framed messages from a stream (newline or length-prefixed).

### `__init__(self, mode: str = "newline")`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `str` | `"newline"` | Framing mode — `"newline"` or `"length"` |

**Raises:** `ValueError` if mode is unknown.

### `feed(self, data: bytes) -> None`

Feeds raw bytes into the internal buffer.

### `read_one(self) -> Optional[dict]`

Reads and decodes one framed message from the buffer.

Returns the decoded dict, or `None` if no complete frame is available.

### `clear(self) -> None`

Clears the internal read buffer.

### `buffered_bytes` (property) -> `int`

Returns the number of bytes currently buffered.

---

### Usage Examples

```python
from board_manager.protocol import FrameReader, encode_and_frame

# Newline mode
reader = FrameReader("newline")
reader.feed(b'{"type":"ping"}\n{"type":"pong"}\n')
msg1 = reader.read_one()  # → {"type": "ping"}
msg2 = reader.read_one()  # → {"type": "pong"}
msg3 = reader.read_one()  # → None

# Length-prefixed mode
reader = FrameReader("length")
data = encode_and_frame({"type": "ping"}, "length")
reader.feed(data)
msg = reader.read_one()  # → {"type": "ping"}
```

### Edge Cases

- **Empty newline frame:** An empty line (`\n` alone) returns `None` (skips silently)
- **Incomplete length frame:** If fewer bytes than `HEADER_LENGTH` are buffered, `read_one()` returns `None`
- **Partial payload:** If the full payload hasn't arrived yet, `read_one()` returns `None` until enough bytes are fed
- **Handshake detection:** If the first byte doesn't match `\x01` or `\x02`, `detect_mode_from_handshake` returns `None` — the service falls back to newline mode and reads the data as a newline-framed message
