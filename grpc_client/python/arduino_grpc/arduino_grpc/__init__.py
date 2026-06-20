"""Arduino CLI gRPC Client Python Module"""

from arduino_grpc.client import ArduinoGrpcClient
from arduino_grpc.exceptions import (
    ArduinoError,
    ConnectionError,
    InitializationError,
    CompileError,
    UploadError,
    BoardError,
)

__version__ = "0.1.0"

__all__ = [
    "ArduinoGrpcClient",
    "ArduinoError",
    "ConnectionError",
    "InitializationError",
    "CompileError",
    "UploadError",
    "BoardError",
]
