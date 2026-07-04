---
layout: default
---
# Data Models

**Module:** `arduino_grpc.models`

Immutable dataclasses returned by `ArduinoGrpcClient` methods. Each model provides a `from_proto()` class method for construction from protobuf messages.

---

## Port

```python
@dataclass
class Port:
    address: str
    protocol: str = "serial"
    protocol_label: str = ""
    label: str = ""
    properties: Optional[Dict[str, str]] = None
    hardware_id: str = ""
```

Represents a serial/USB port where an Arduino board is (or could be) connected.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `address` | `str` | — | Port path, e.g. `"/dev/ttyACM0"`, `"COM3"` |
| `protocol` | `str` | `"serial"` | Transport protocol (`"serial"`, `"network"`, etc.) |
| `protocol_label` | `str` | `""` | Human-readable protocol name |
| `label` | `str` | `""` | Human-readable port label (e.g. `"USB Serial"`) |
| `properties` | `Optional[Dict[str, str]]` | `None` | Key-value metadata from the daemon |
| `hardware_id` | `str` | `""` | Hardware identifier (USB vendor/product ID) |

### Methods

#### `to_proto(port_pb2) -> port_pb2.Port`

Converts back to a protobuf `Port` message. Accepts the `port_pb2` module for construction.

```python
from cc.arduino.cli.commands.v1 import port_pb2

port = Port(address="/dev/ttyACM0", protocol="serial", label="Arduino Uno")
proto = port.to_proto(port_pb2)
# proto.address == "/dev/ttyACM0"
# proto.protocol == "serial"
```

---

## Board

```python
@dataclass
class Board:
    port: Port
    fqbn: str
    name: str
    detected: bool = True
```

Represents an Arduino board (detected or known).

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | `Port` | — | The port the board is connected to (or empty for undetected boards) |
| `fqbn` | `str` | — | Fully Qualified Board Name, e.g. `"arduino:avr:uno"` |
| `name` | `str` | — | Human-readable board name, e.g. `"Arduino Uno"` |
| `detected` | `bool` | `True` | `True` if currently connected; `False` for offline/all-boards listings |

### Class Methods

#### `from_proto(board_proto, port_proto) -> Board`

Constructs a `Board` from a pair of protobuf messages — a `BoardListItem` (or `DetectedPort.BoardListItem`) and a `Port`.

```python
from cc.arduino.cli.commands.v1 import board_pb2, port_pb2

port_proto = port_pb2.Port(address="/dev/ttyACM0", protocol="serial")
board_proto = board_pb2.BoardListItem(fqbn="arduino:avr:uno", name="Arduino Uno")

board = Board.from_proto(board_proto, port_proto)
# board.fqbn  == "arduino:avr:uno"
# board.name  == "Arduino Uno"
# board.port.address == "/dev/ttyACM0"
# board.detected == True (default)
```

---

## CompileResult

```python
@dataclass
class CompileResult:
    success: bool
    output: str = ""
    error: str = ""
    sketch_path: str = ""
```

Returned by `ArduinoGrpcClient.compile()`.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `success` | `bool` | — | Whether compilation completed successfully |
| `output` | `str` | `""` | Concatenated stdout from the compiler |
| `error` | `str` | `""` | Concatenated stderr from the compiler |
| `sketch_path` | `str` | `""` | The sketch path used for compilation (for reference) |

### Class Methods

#### `from_proto(proto, sketch_path="") -> CompileResult`

Constructs from a protobuf `CompileResponse` message.

```python
from cc.arduino.cli.commands.v1 import compile_pb2

# Typically obtained from the final response in a Compile stream
proto = compile_pb2.CompileResponse(
    out_stream=b"Done compiling.\n",
    result=compile_pb2.CompileResponse.Result(),
)
result = CompileResult.from_proto(proto, sketch_path="/home/user/sketches/blinky")
# result.success == True
# result.output == "Done compiling.\n"
```

---

## UploadResult

```python
@dataclass
class UploadResult:
    success: bool
    output: str = ""
    error: str = ""
```

Returned by `ArduinoGrpcClient.upload()`.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `success` | `bool` | — | Whether upload completed successfully |
| `output` | `str` | `""` | Concatenated stdout from the uploader |
| `error` | `str` | `""` | Concatenated stderr from the uploader |

### Class Methods

#### `from_proto(proto) -> UploadResult`

Constructs from a protobuf `UploadResponse` message.

```python
from cc.arduino.cli.commands.v1 import upload_pb2

proto = upload_pb2.UploadResponse(
    out_stream=b"Done uploading.\n",
    result=upload_pb2.UploadResponse.Result(),
)
result = UploadResult.from_proto(proto)
# result.success == True
# result.output == "Done uploading.\n"
```
