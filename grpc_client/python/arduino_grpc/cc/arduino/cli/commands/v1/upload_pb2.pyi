from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from cc.arduino.cli.commands.v1 import port_pb2 as _port_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UploadRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "sketch_path", "port", "verbose", "verify", "import_file", "import_dir", "programmer", "dry_run", "user_fields", "upload_properties")
    class UserFieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    VERIFY_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FILE_FIELD_NUMBER: _ClassVar[int]
    IMPORT_DIR_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    USER_FIELDS_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    sketch_path: str
    port: _port_pb2.Port
    verbose: bool
    verify: bool
    import_file: str
    import_dir: str
    programmer: str
    dry_run: bool
    user_fields: _containers.ScalarMap[str, str]
    upload_properties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., sketch_path: _Optional[str] = ..., port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ..., verbose: _Optional[bool] = ..., verify: _Optional[bool] = ..., import_file: _Optional[str] = ..., import_dir: _Optional[str] = ..., programmer: _Optional[str] = ..., dry_run: _Optional[bool] = ..., user_fields: _Optional[_Mapping[str, str]] = ..., upload_properties: _Optional[_Iterable[str]] = ...) -> None: ...

class UploadResponse(_message.Message):
    __slots__ = ("out_stream", "err_stream", "result")
    OUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    ERR_STREAM_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    out_stream: bytes
    err_stream: bytes
    result: UploadResult
    def __init__(self, out_stream: _Optional[bytes] = ..., err_stream: _Optional[bytes] = ..., result: _Optional[_Union[UploadResult, _Mapping]] = ...) -> None: ...

class UploadResult(_message.Message):
    __slots__ = ("updated_upload_port",)
    UPDATED_UPLOAD_PORT_FIELD_NUMBER: _ClassVar[int]
    updated_upload_port: _port_pb2.Port
    def __init__(self, updated_upload_port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ...) -> None: ...

class ProgrammerIsRequiredForUploadError(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UploadUsingProgrammerRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "sketch_path", "port", "verbose", "verify", "import_file", "import_dir", "programmer", "dry_run", "user_fields", "upload_properties")
    class UserFieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    VERIFY_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FILE_FIELD_NUMBER: _ClassVar[int]
    IMPORT_DIR_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    USER_FIELDS_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    sketch_path: str
    port: _port_pb2.Port
    verbose: bool
    verify: bool
    import_file: str
    import_dir: str
    programmer: str
    dry_run: bool
    user_fields: _containers.ScalarMap[str, str]
    upload_properties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., sketch_path: _Optional[str] = ..., port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ..., verbose: _Optional[bool] = ..., verify: _Optional[bool] = ..., import_file: _Optional[str] = ..., import_dir: _Optional[str] = ..., programmer: _Optional[str] = ..., dry_run: _Optional[bool] = ..., user_fields: _Optional[_Mapping[str, str]] = ..., upload_properties: _Optional[_Iterable[str]] = ...) -> None: ...

class UploadUsingProgrammerResponse(_message.Message):
    __slots__ = ("out_stream", "err_stream")
    OUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    ERR_STREAM_FIELD_NUMBER: _ClassVar[int]
    out_stream: bytes
    err_stream: bytes
    def __init__(self, out_stream: _Optional[bytes] = ..., err_stream: _Optional[bytes] = ...) -> None: ...

class BurnBootloaderRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "port", "verbose", "verify", "programmer", "dry_run", "user_fields", "upload_properties")
    class UserFieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    VERIFY_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    DRY_RUN_FIELD_NUMBER: _ClassVar[int]
    USER_FIELDS_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    port: _port_pb2.Port
    verbose: bool
    verify: bool
    programmer: str
    dry_run: bool
    user_fields: _containers.ScalarMap[str, str]
    upload_properties: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ..., verbose: _Optional[bool] = ..., verify: _Optional[bool] = ..., programmer: _Optional[str] = ..., dry_run: _Optional[bool] = ..., user_fields: _Optional[_Mapping[str, str]] = ..., upload_properties: _Optional[_Iterable[str]] = ...) -> None: ...

class BurnBootloaderResponse(_message.Message):
    __slots__ = ("out_stream", "err_stream")
    OUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    ERR_STREAM_FIELD_NUMBER: _ClassVar[int]
    out_stream: bytes
    err_stream: bytes
    def __init__(self, out_stream: _Optional[bytes] = ..., err_stream: _Optional[bytes] = ...) -> None: ...

class ListProgrammersAvailableForUploadRequest(_message.Message):
    __slots__ = ("instance", "fqbn")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ...) -> None: ...

class ListProgrammersAvailableForUploadResponse(_message.Message):
    __slots__ = ("programmers",)
    PROGRAMMERS_FIELD_NUMBER: _ClassVar[int]
    programmers: _containers.RepeatedCompositeFieldContainer[_common_pb2.Programmer]
    def __init__(self, programmers: _Optional[_Iterable[_Union[_common_pb2.Programmer, _Mapping]]] = ...) -> None: ...

class SupportedUserFieldsRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "protocol")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    protocol: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., protocol: _Optional[str] = ...) -> None: ...

class UserField(_message.Message):
    __slots__ = ("tool_id", "name", "label", "secret")
    TOOL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    tool_id: str
    name: str
    label: str
    secret: bool
    def __init__(self, tool_id: _Optional[str] = ..., name: _Optional[str] = ..., label: _Optional[str] = ..., secret: _Optional[bool] = ...) -> None: ...

class SupportedUserFieldsResponse(_message.Message):
    __slots__ = ("user_fields",)
    USER_FIELDS_FIELD_NUMBER: _ClassVar[int]
    user_fields: _containers.RepeatedCompositeFieldContainer[UserField]
    def __init__(self, user_fields: _Optional[_Iterable[_Union[UserField, _Mapping]]] = ...) -> None: ...
