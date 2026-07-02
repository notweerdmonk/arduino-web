"""grpc_client/python/arduino_grpc/arduino_grpc/exceptions.py

Custom exceptions for Arduino gRPC client

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

class ArduinoError(Exception):
    """Base exception for all Arduino gRPC errors"""

    pass


class ConnectionError(ArduinoError):
    """Raised when unable to connect to arduino-cli daemon"""

    pass


class InitializationError(ArduinoError):
    """Raised when instance initialization fails"""

    pass


class CompileError(ArduinoError):
    """Raised when sketch compilation fails"""

    pass


class UploadError(ArduinoError):
    """Raised when sketch upload fails"""

    pass


class BoardError(ArduinoError):
    """Raised when board operations fail"""

    pass


class InvalidPortError(ArduinoError):
    """Raised when port parameter is invalid"""

    pass


class InvalidFqbnError(ArduinoError):
    """Raised when FQBN is invalid"""

    pass

