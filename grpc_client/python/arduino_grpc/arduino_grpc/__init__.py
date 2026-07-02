"""grpc_client/python/arduino_grpc/arduino_grpc/__init__.py

Arduino CLI gRPC Client Python Module

Author: notweerdmonk
SPDX-License-Identifier: Apache-2.0

Copyright 2026 notweerdmonk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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

