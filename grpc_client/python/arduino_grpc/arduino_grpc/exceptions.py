"""Custom exceptions for Arduino gRPC client"""


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