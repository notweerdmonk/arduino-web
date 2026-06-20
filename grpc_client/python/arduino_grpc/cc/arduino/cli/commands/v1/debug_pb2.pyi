from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from cc.arduino.cli.commands.v1 import port_pb2 as _port_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DebugRequest(_message.Message):
    __slots__ = ("debug_request", "data", "send_interrupt")
    DEBUG_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SEND_INTERRUPT_FIELD_NUMBER: _ClassVar[int]
    debug_request: GetDebugConfigRequest
    data: bytes
    send_interrupt: bool
    def __init__(self, debug_request: _Optional[_Union[GetDebugConfigRequest, _Mapping]] = ..., data: _Optional[bytes] = ..., send_interrupt: _Optional[bool] = ...) -> None: ...

class DebugResponse(_message.Message):
    __slots__ = ("data", "result")
    class Result(_message.Message):
        __slots__ = ("error",)
        ERROR_FIELD_NUMBER: _ClassVar[int]
        error: str
        def __init__(self, error: _Optional[str] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    result: DebugResponse.Result
    def __init__(self, data: _Optional[bytes] = ..., result: _Optional[_Union[DebugResponse.Result, _Mapping]] = ...) -> None: ...

class IsDebugSupportedRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "port", "interpreter", "programmer", "debug_properties")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    INTERPRETER_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    DEBUG_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    port: _port_pb2.Port
    interpreter: str
    programmer: str
    debug_properties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ..., interpreter: _Optional[str] = ..., programmer: _Optional[str] = ..., debug_properties: _Optional[_Iterable[str]] = ...) -> None: ...

class IsDebugSupportedResponse(_message.Message):
    __slots__ = ("debugging_supported", "debug_fqbn")
    DEBUGGING_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FQBN_FIELD_NUMBER: _ClassVar[int]
    debugging_supported: bool
    debug_fqbn: str
    def __init__(self, debugging_supported: _Optional[bool] = ..., debug_fqbn: _Optional[str] = ...) -> None: ...

class GetDebugConfigRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "sketch_path", "port", "interpreter", "import_dir", "programmer", "debug_properties")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    INTERPRETER_FIELD_NUMBER: _ClassVar[int]
    IMPORT_DIR_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    DEBUG_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    sketch_path: str
    port: _port_pb2.Port
    interpreter: str
    import_dir: str
    programmer: str
    debug_properties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., sketch_path: _Optional[str] = ..., port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ..., interpreter: _Optional[str] = ..., import_dir: _Optional[str] = ..., programmer: _Optional[str] = ..., debug_properties: _Optional[_Iterable[str]] = ...) -> None: ...

class GetDebugConfigResponse(_message.Message):
    __slots__ = ("executable", "toolchain", "toolchain_path", "toolchain_prefix", "server", "server_path", "toolchain_configuration", "server_configuration", "custom_configs", "svd_file", "programmer")
    class CustomConfigsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    EXECUTABLE_FIELD_NUMBER: _ClassVar[int]
    TOOLCHAIN_FIELD_NUMBER: _ClassVar[int]
    TOOLCHAIN_PATH_FIELD_NUMBER: _ClassVar[int]
    TOOLCHAIN_PREFIX_FIELD_NUMBER: _ClassVar[int]
    SERVER_FIELD_NUMBER: _ClassVar[int]
    SERVER_PATH_FIELD_NUMBER: _ClassVar[int]
    TOOLCHAIN_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SERVER_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    SVD_FILE_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    executable: str
    toolchain: str
    toolchain_path: str
    toolchain_prefix: str
    server: str
    server_path: str
    toolchain_configuration: _any_pb2.Any
    server_configuration: _any_pb2.Any
    custom_configs: _containers.ScalarMap[str, str]
    svd_file: str
    programmer: str
    def __init__(self, executable: _Optional[str] = ..., toolchain: _Optional[str] = ..., toolchain_path: _Optional[str] = ..., toolchain_prefix: _Optional[str] = ..., server: _Optional[str] = ..., server_path: _Optional[str] = ..., toolchain_configuration: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., server_configuration: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., custom_configs: _Optional[_Mapping[str, str]] = ..., svd_file: _Optional[str] = ..., programmer: _Optional[str] = ...) -> None: ...

class DebugGCCToolchainConfiguration(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DebugOpenOCDServerConfiguration(_message.Message):
    __slots__ = ("path", "scripts_dir", "scripts")
    PATH_FIELD_NUMBER: _ClassVar[int]
    SCRIPTS_DIR_FIELD_NUMBER: _ClassVar[int]
    SCRIPTS_FIELD_NUMBER: _ClassVar[int]
    path: str
    scripts_dir: str
    scripts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, path: _Optional[str] = ..., scripts_dir: _Optional[str] = ..., scripts: _Optional[_Iterable[str]] = ...) -> None: ...
