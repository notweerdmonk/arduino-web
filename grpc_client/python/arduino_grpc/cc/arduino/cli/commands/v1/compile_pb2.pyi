from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from cc.arduino.cli.commands.v1 import lib_pb2 as _lib_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CompileRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "sketch_path", "show_properties", "preprocess", "build_cache_path", "build_path", "build_properties", "warnings", "verbose", "quiet", "jobs", "libraries", "optimize_for_debug", "export_dir", "clean", "create_compilation_database_only", "source_override", "export_binaries", "library", "keys_keychain", "sign_key", "encrypt_key", "skip_libraries_discovery", "do_not_expand_build_properties", "build_cache_extra_paths")
    class SourceOverrideEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    SHOW_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PREPROCESS_FIELD_NUMBER: _ClassVar[int]
    BUILD_CACHE_PATH_FIELD_NUMBER: _ClassVar[int]
    BUILD_PATH_FIELD_NUMBER: _ClassVar[int]
    BUILD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    QUIET_FIELD_NUMBER: _ClassVar[int]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZE_FOR_DEBUG_FIELD_NUMBER: _ClassVar[int]
    EXPORT_DIR_FIELD_NUMBER: _ClassVar[int]
    CLEAN_FIELD_NUMBER: _ClassVar[int]
    CREATE_COMPILATION_DATABASE_ONLY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    EXPORT_BINARIES_FIELD_NUMBER: _ClassVar[int]
    LIBRARY_FIELD_NUMBER: _ClassVar[int]
    KEYS_KEYCHAIN_FIELD_NUMBER: _ClassVar[int]
    SIGN_KEY_FIELD_NUMBER: _ClassVar[int]
    ENCRYPT_KEY_FIELD_NUMBER: _ClassVar[int]
    SKIP_LIBRARIES_DISCOVERY_FIELD_NUMBER: _ClassVar[int]
    DO_NOT_EXPAND_BUILD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    BUILD_CACHE_EXTRA_PATHS_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    sketch_path: str
    show_properties: bool
    preprocess: bool
    build_cache_path: str
    build_path: str
    build_properties: _containers.RepeatedScalarFieldContainer[str]
    warnings: str
    verbose: bool
    quiet: bool
    jobs: int
    libraries: _containers.RepeatedScalarFieldContainer[str]
    optimize_for_debug: bool
    export_dir: str
    clean: bool
    create_compilation_database_only: bool
    source_override: _containers.ScalarMap[str, str]
    export_binaries: bool
    library: _containers.RepeatedScalarFieldContainer[str]
    keys_keychain: str
    sign_key: str
    encrypt_key: str
    skip_libraries_discovery: bool
    do_not_expand_build_properties: bool
    build_cache_extra_paths: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., sketch_path: _Optional[str] = ..., show_properties: _Optional[bool] = ..., preprocess: _Optional[bool] = ..., build_cache_path: _Optional[str] = ..., build_path: _Optional[str] = ..., build_properties: _Optional[_Iterable[str]] = ..., warnings: _Optional[str] = ..., verbose: _Optional[bool] = ..., quiet: _Optional[bool] = ..., jobs: _Optional[int] = ..., libraries: _Optional[_Iterable[str]] = ..., optimize_for_debug: _Optional[bool] = ..., export_dir: _Optional[str] = ..., clean: _Optional[bool] = ..., create_compilation_database_only: _Optional[bool] = ..., source_override: _Optional[_Mapping[str, str]] = ..., export_binaries: _Optional[bool] = ..., library: _Optional[_Iterable[str]] = ..., keys_keychain: _Optional[str] = ..., sign_key: _Optional[str] = ..., encrypt_key: _Optional[str] = ..., skip_libraries_discovery: _Optional[bool] = ..., do_not_expand_build_properties: _Optional[bool] = ..., build_cache_extra_paths: _Optional[_Iterable[str]] = ...) -> None: ...

class CompileResponse(_message.Message):
    __slots__ = ("out_stream", "err_stream", "progress", "result")
    OUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    ERR_STREAM_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    out_stream: bytes
    err_stream: bytes
    progress: _common_pb2.TaskProgress
    result: BuilderResult
    def __init__(self, out_stream: _Optional[bytes] = ..., err_stream: _Optional[bytes] = ..., progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[BuilderResult, _Mapping]] = ...) -> None: ...

class InstanceNeedsReinitializationError(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BuilderResult(_message.Message):
    __slots__ = ("build_path", "used_libraries", "executable_sections_size", "board_platform", "build_platform", "build_properties", "diagnostics")
    BUILD_PATH_FIELD_NUMBER: _ClassVar[int]
    USED_LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    EXECUTABLE_SECTIONS_SIZE_FIELD_NUMBER: _ClassVar[int]
    BOARD_PLATFORM_FIELD_NUMBER: _ClassVar[int]
    BUILD_PLATFORM_FIELD_NUMBER: _ClassVar[int]
    BUILD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DIAGNOSTICS_FIELD_NUMBER: _ClassVar[int]
    build_path: str
    used_libraries: _containers.RepeatedCompositeFieldContainer[_lib_pb2.Library]
    executable_sections_size: _containers.RepeatedCompositeFieldContainer[ExecutableSectionSize]
    board_platform: _common_pb2.InstalledPlatformReference
    build_platform: _common_pb2.InstalledPlatformReference
    build_properties: _containers.RepeatedScalarFieldContainer[str]
    diagnostics: _containers.RepeatedCompositeFieldContainer[CompileDiagnostic]
    def __init__(self, build_path: _Optional[str] = ..., used_libraries: _Optional[_Iterable[_Union[_lib_pb2.Library, _Mapping]]] = ..., executable_sections_size: _Optional[_Iterable[_Union[ExecutableSectionSize, _Mapping]]] = ..., board_platform: _Optional[_Union[_common_pb2.InstalledPlatformReference, _Mapping]] = ..., build_platform: _Optional[_Union[_common_pb2.InstalledPlatformReference, _Mapping]] = ..., build_properties: _Optional[_Iterable[str]] = ..., diagnostics: _Optional[_Iterable[_Union[CompileDiagnostic, _Mapping]]] = ...) -> None: ...

class ExecutableSectionSize(_message.Message):
    __slots__ = ("name", "size", "max_size")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    name: str
    size: int
    max_size: int
    def __init__(self, name: _Optional[str] = ..., size: _Optional[int] = ..., max_size: _Optional[int] = ...) -> None: ...

class CompileDiagnostic(_message.Message):
    __slots__ = ("severity", "message", "file", "line", "column", "context", "notes")
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    severity: str
    message: str
    file: str
    line: int
    column: int
    context: _containers.RepeatedCompositeFieldContainer[CompileDiagnosticContext]
    notes: _containers.RepeatedCompositeFieldContainer[CompileDiagnosticNote]
    def __init__(self, severity: _Optional[str] = ..., message: _Optional[str] = ..., file: _Optional[str] = ..., line: _Optional[int] = ..., column: _Optional[int] = ..., context: _Optional[_Iterable[_Union[CompileDiagnosticContext, _Mapping]]] = ..., notes: _Optional[_Iterable[_Union[CompileDiagnosticNote, _Mapping]]] = ...) -> None: ...

class CompileDiagnosticContext(_message.Message):
    __slots__ = ("message", "file", "line", "column")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    message: str
    file: str
    line: int
    column: int
    def __init__(self, message: _Optional[str] = ..., file: _Optional[str] = ..., line: _Optional[int] = ..., column: _Optional[int] = ...) -> None: ...

class CompileDiagnosticNote(_message.Message):
    __slots__ = ("message", "file", "line", "column")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    message: str
    file: str
    line: int
    column: int
    def __init__(self, message: _Optional[str] = ..., file: _Optional[str] = ..., line: _Optional[int] = ..., column: _Optional[int] = ...) -> None: ...
