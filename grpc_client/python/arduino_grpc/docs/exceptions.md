---
---
# Exception Hierarchy

**Module:** `arduino_grpc.exceptions`

```
Exception
└── ArduinoError
    ├── ConnectionError
    ├── InitializationError
    ├── CompileError
    ├── UploadError
    ├── BoardError
    └── InvalidPortError    *)
    └── InvalidFqbnError    *)
```

\* `InvalidPortError` and `InvalidFqbnError` are raised from user-facing methods but are **not** exported from the top-level `arduino_grpc.__init__`; import them directly from `arduino_grpc.exceptions`.

All exceptions inherit from `ArduinoError`, so a single `except ArduinoError` catches any domain error.

---

## ArduinoError

```python
class ArduinoError(Exception):
```

Base exception for all Arduino gRPC client errors. Inherits from `Exception`.

```python
from arduino_grpc import ArduinoError

try:
    client.compile("sketch", "arduino:avr:uno")
except ArduinoError as e:
    print(f"Arduino operation failed: {e}")
```

---

## ConnectionError

```python
class ConnectionError(ArduinoError):
```

Raised when the client cannot establish a connection to the arduino-cli daemon.

**Raised by:** `ArduinoGrpcClient.connect()`, and by any method that calls `_ensure_connected()` (all RPC methods) if `connect()` was never called.

```python
client = ArduinoGrpcClient("localhost:9999")
client.connect()  # raises ConnectionError if nothing is listening
```

---

## InitializationError

```python
class InitializationError(ArduinoError):
```

Raised when the `Create` or `Init` RPC fails during instance setup.

**Raised by:** `ArduinoGrpcClient.init()`.

```python
try:
    client.init()
except InitializationError as e:
    print(f"Failed to initialize Arduino core: {e}")
```

---

## CompileError

```python
class CompileError(ArduinoError):
```

Raised when a compile RPC fails (gRPC error) or an unexpected exception occurs during compilation.

**Raised by:** `ArduinoGrpcClient.compile()`, `ArduinoGrpcClient.compile_stream()`.

```python
try:
    result = client.compile("sketch", "arduino:avr:uno")
except CompileError as e:
    print(f"Compilation RPC failed: {e}")
```

---

## UploadError

```python
class UploadError(ArduinoError):
```

Raised when an upload RPC fails (gRPC error) or an unexpected exception occurs during upload.

**Raised by:** `ArduinoGrpcClient.upload()`, `ArduinoGrpcClient.upload_stream()`.

```python
try:
    result = client.upload("sketch", "arduino:avr:uno", "/dev/ttyACM0")
except UploadError as e:
    print(f"Upload RPC failed: {e}")
```

---

## BoardError

```python
class BoardError(ArduinoError):
```

Raised when any board-related RPC (`BoardList`, `BoardListAll`, `BoardListWatch`) fails.

**Raised by:** `ArduinoGrpcClient.list_boards()`, `list_all_boards()`, `watch_boards()`.

Note: `watch_boards()` does **not** raise `BoardError` on `DEADLINE_EXCEEDED` — it gracefully stops iteration instead.

```python
try:
    boards = client.list_boards()
except BoardError as e:
    print(f"Board detection failed: {e}")
```

---

## InvalidPortError

```python
class InvalidPortError(ArduinoError):
```

Raised when an empty or invalid port address is passed to an upload method.

**Raised by:** `ArduinoGrpcClient.upload()`, `ArduinoGrpcClient.upload_stream()`.

Import from the exceptions module directly:

```python
from arduino_grpc.exceptions import InvalidPortError

try:
    client.upload("sketch", "arduino:avr:uno", "")
except InvalidPortError:
    print("A valid port is required")
```

---

## InvalidFqbnError

```python
class InvalidFqbnError(ArduinoError):
```

Raised when an empty FQBN is passed to a compile or upload method.

**Raised by:** `ArduinoGrpcClient.compile()`, `compile_stream()`, `upload()`, `upload_stream()`.

Import from the exceptions module directly:

```python
from arduino_grpc.exceptions import InvalidFqbnError

try:
    client.compile("sketch", "")
except InvalidFqbnError:
    print("A valid FQBN is required")
```
