---
---
# board-manager-client

Persistent PubSub client for BoardManagerService — connects over Unix Domain Socket (primary) or TCP (fallback), with automatic reconnection and subscription recovery.

## Package

`board_manager_client` (namespace package under the MedMinder monorepo).

### Exports

| Symbol | Source | Description |
|--------|--------|-------------|
| `PubSubClient` | `board_manager_client.pubsub_client` | Persistent PubSub client with auto-reconnect |
| `protocol` | `board_manager.protocol` | Wire protocol primitives (frame reader, handshake, encoding) |
| `router` | `board_manager.router` | Topic pattern-matching utilities (`_match`) |

### Dependencies

- **`board_manager.protocol`** — Provides `FrameReader`, `Handshake`, `encode_and_frame`.
- **`board_manager.router`** — Provides `_match` for wildcard topic routing.

Core Python dependencies (stdlib only): `socket`, `threading`, `select`, `json`, `time`, `os`, `logging`, `typing`.

## Architecture

```
                     ┌──────────────────┐
                     │  PubSubClient    │
                     │  ┌────────────┐  │
                     │  │ Reader     │  │  Daemon thread
                     │  │ Thread     │  │  (select loop)
                     │  └─────┬──────┘  │
                     │        │ reads   │
                     │  ┌─────┴──────┐  │
                     │  │ Socket     │  │  UDS → TCP fallback
                     │  │ (framed)   │  │
                     │  └─────┬──────┘  │
                     │        │         │
                     │  ┌─────┴──────┐  │
                     │  │ Handlers   │  │  topic → [callbacks]
                     │  │ Subscripts │  │  persisted across
                     │  │            │  │  reconnects
                     │  └────────────┘  │
                     └──────────────────┘
                              │
                    framed JSON (newline)
                              │
               ┌──────────────┴──────────────┐
               │   BoardManagerService        │
               │   (UDS / TCP)                │
               └─────────────────────────────┘
```

The client maintains a persistent connection to BoardManagerService. All messages are framed JSON with newline delimiters. A single background reader thread runs a `select()`-based read loop; when the socket breaks it automatically reconnects and re-sends all active subscriptions.
