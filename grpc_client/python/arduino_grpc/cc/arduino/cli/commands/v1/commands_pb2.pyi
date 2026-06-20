from cc.arduino.cli.commands.v1 import board_pb2 as _board_pb2
from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from cc.arduino.cli.commands.v1 import compile_pb2 as _compile_pb2
from cc.arduino.cli.commands.v1 import core_pb2 as _core_pb2
from cc.arduino.cli.commands.v1 import debug_pb2 as _debug_pb2
from cc.arduino.cli.commands.v1 import lib_pb2 as _lib_pb2
from cc.arduino.cli.commands.v1 import monitor_pb2 as _monitor_pb2
from cc.arduino.cli.commands.v1 import settings_pb2 as _settings_pb2
from cc.arduino.cli.commands.v1 import upload_pb2 as _upload_pb2
from google.rpc import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FailedInstanceInitReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FAILED_INSTANCE_INIT_REASON_UNSPECIFIED: _ClassVar[FailedInstanceInitReason]
    FAILED_INSTANCE_INIT_REASON_INVALID_INDEX_URL: _ClassVar[FailedInstanceInitReason]
    FAILED_INSTANCE_INIT_REASON_INDEX_LOAD_ERROR: _ClassVar[FailedInstanceInitReason]
    FAILED_INSTANCE_INIT_REASON_TOOL_LOAD_ERROR: _ClassVar[FailedInstanceInitReason]
    FAILED_INSTANCE_INIT_REASON_INDEX_DOWNLOAD_ERROR: _ClassVar[FailedInstanceInitReason]
FAILED_INSTANCE_INIT_REASON_UNSPECIFIED: FailedInstanceInitReason
FAILED_INSTANCE_INIT_REASON_INVALID_INDEX_URL: FailedInstanceInitReason
FAILED_INSTANCE_INIT_REASON_INDEX_LOAD_ERROR: FailedInstanceInitReason
FAILED_INSTANCE_INIT_REASON_TOOL_LOAD_ERROR: FailedInstanceInitReason
FAILED_INSTANCE_INIT_REASON_INDEX_DOWNLOAD_ERROR: FailedInstanceInitReason

class CreateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateResponse(_message.Message):
    __slots__ = ("instance",)
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ...) -> None: ...

class InitRequest(_message.Message):
    __slots__ = ("instance", "profile", "sketch_path")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    profile: str
    sketch_path: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., profile: _Optional[str] = ..., sketch_path: _Optional[str] = ...) -> None: ...

class InitResponse(_message.Message):
    __slots__ = ("init_progress", "error", "profile")
    class Progress(_message.Message):
        __slots__ = ("download_progress", "task_progress")
        DOWNLOAD_PROGRESS_FIELD_NUMBER: _ClassVar[int]
        TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
        download_progress: _common_pb2.DownloadProgress
        task_progress: _common_pb2.TaskProgress
        def __init__(self, download_progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ...) -> None: ...
    INIT_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    init_progress: InitResponse.Progress
    error: _status_pb2.Status
    profile: _common_pb2.SketchProfile
    def __init__(self, init_progress: _Optional[_Union[InitResponse.Progress, _Mapping]] = ..., error: _Optional[_Union[_status_pb2.Status, _Mapping]] = ..., profile: _Optional[_Union[_common_pb2.SketchProfile, _Mapping]] = ...) -> None: ...

class FailedInstanceInitError(_message.Message):
    __slots__ = ("reason", "message")
    REASON_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    reason: FailedInstanceInitReason
    message: str
    def __init__(self, reason: _Optional[_Union[FailedInstanceInitReason, str]] = ..., message: _Optional[str] = ...) -> None: ...

class DestroyRequest(_message.Message):
    __slots__ = ("instance",)
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ...) -> None: ...

class DestroyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateIndexRequest(_message.Message):
    __slots__ = ("instance", "ignore_custom_package_indexes", "update_if_older_than_secs")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    IGNORE_CUSTOM_PACKAGE_INDEXES_FIELD_NUMBER: _ClassVar[int]
    UPDATE_IF_OLDER_THAN_SECS_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    ignore_custom_package_indexes: bool
    update_if_older_than_secs: int
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., ignore_custom_package_indexes: _Optional[bool] = ..., update_if_older_than_secs: _Optional[int] = ...) -> None: ...

class UpdateIndexResponse(_message.Message):
    __slots__ = ("download_progress", "result")
    class Result(_message.Message):
        __slots__ = ("updated_indexes",)
        UPDATED_INDEXES_FIELD_NUMBER: _ClassVar[int]
        updated_indexes: _containers.RepeatedCompositeFieldContainer[IndexUpdateReport]
        def __init__(self, updated_indexes: _Optional[_Iterable[_Union[IndexUpdateReport, _Mapping]]] = ...) -> None: ...
    DOWNLOAD_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    download_progress: _common_pb2.DownloadProgress
    result: UpdateIndexResponse.Result
    def __init__(self, download_progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., result: _Optional[_Union[UpdateIndexResponse.Result, _Mapping]] = ...) -> None: ...

class UpdateLibrariesIndexRequest(_message.Message):
    __slots__ = ("instance", "update_if_older_than_secs")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_IF_OLDER_THAN_SECS_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    update_if_older_than_secs: int
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., update_if_older_than_secs: _Optional[int] = ...) -> None: ...

class UpdateLibrariesIndexResponse(_message.Message):
    __slots__ = ("download_progress", "result")
    class Result(_message.Message):
        __slots__ = ("libraries_index",)
        LIBRARIES_INDEX_FIELD_NUMBER: _ClassVar[int]
        libraries_index: IndexUpdateReport
        def __init__(self, libraries_index: _Optional[_Union[IndexUpdateReport, _Mapping]] = ...) -> None: ...
    DOWNLOAD_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    download_progress: _common_pb2.DownloadProgress
    result: UpdateLibrariesIndexResponse.Result
    def __init__(self, download_progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., result: _Optional[_Union[UpdateLibrariesIndexResponse.Result, _Mapping]] = ...) -> None: ...

class IndexUpdateReport(_message.Message):
    __slots__ = ("index_url", "status")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[IndexUpdateReport.Status]
        STATUS_UPDATED: _ClassVar[IndexUpdateReport.Status]
        STATUS_ALREADY_UP_TO_DATE: _ClassVar[IndexUpdateReport.Status]
        STATUS_FAILED: _ClassVar[IndexUpdateReport.Status]
        STATUS_SKIPPED: _ClassVar[IndexUpdateReport.Status]
    STATUS_UNSPECIFIED: IndexUpdateReport.Status
    STATUS_UPDATED: IndexUpdateReport.Status
    STATUS_ALREADY_UP_TO_DATE: IndexUpdateReport.Status
    STATUS_FAILED: IndexUpdateReport.Status
    STATUS_SKIPPED: IndexUpdateReport.Status
    INDEX_URL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    index_url: str
    status: IndexUpdateReport.Status
    def __init__(self, index_url: _Optional[str] = ..., status: _Optional[_Union[IndexUpdateReport.Status, str]] = ...) -> None: ...

class VersionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VersionResponse(_message.Message):
    __slots__ = ("version",)
    VERSION_FIELD_NUMBER: _ClassVar[int]
    version: str
    def __init__(self, version: _Optional[str] = ...) -> None: ...

class NewSketchRequest(_message.Message):
    __slots__ = ("sketch_name", "sketch_dir", "overwrite")
    SKETCH_NAME_FIELD_NUMBER: _ClassVar[int]
    SKETCH_DIR_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    sketch_name: str
    sketch_dir: str
    overwrite: bool
    def __init__(self, sketch_name: _Optional[str] = ..., sketch_dir: _Optional[str] = ..., overwrite: _Optional[bool] = ...) -> None: ...

class NewSketchResponse(_message.Message):
    __slots__ = ("main_file",)
    MAIN_FILE_FIELD_NUMBER: _ClassVar[int]
    main_file: str
    def __init__(self, main_file: _Optional[str] = ...) -> None: ...

class LoadSketchRequest(_message.Message):
    __slots__ = ("sketch_path",)
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    sketch_path: str
    def __init__(self, sketch_path: _Optional[str] = ...) -> None: ...

class LoadSketchResponse(_message.Message):
    __slots__ = ("sketch",)
    SKETCH_FIELD_NUMBER: _ClassVar[int]
    sketch: _common_pb2.Sketch
    def __init__(self, sketch: _Optional[_Union[_common_pb2.Sketch, _Mapping]] = ...) -> None: ...

class ArchiveSketchRequest(_message.Message):
    __slots__ = ("sketch_path", "archive_path", "include_build_dir", "overwrite")
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    ARCHIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_BUILD_DIR_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    sketch_path: str
    archive_path: str
    include_build_dir: bool
    overwrite: bool
    def __init__(self, sketch_path: _Optional[str] = ..., archive_path: _Optional[str] = ..., include_build_dir: _Optional[bool] = ..., overwrite: _Optional[bool] = ...) -> None: ...

class ArchiveSketchResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetSketchDefaultsRequest(_message.Message):
    __slots__ = ("sketch_path", "default_fqbn", "default_port_address", "default_port_protocol", "default_programmer")
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FQBN_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PORT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PORT_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    sketch_path: str
    default_fqbn: str
    default_port_address: str
    default_port_protocol: str
    default_programmer: str
    def __init__(self, sketch_path: _Optional[str] = ..., default_fqbn: _Optional[str] = ..., default_port_address: _Optional[str] = ..., default_port_protocol: _Optional[str] = ..., default_programmer: _Optional[str] = ...) -> None: ...

class SetSketchDefaultsResponse(_message.Message):
    __slots__ = ("default_fqbn", "default_port_address", "default_port_protocol", "default_programmer")
    DEFAULT_FQBN_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PORT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PORT_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    default_fqbn: str
    default_port_address: str
    default_port_protocol: str
    default_programmer: str
    def __init__(self, default_fqbn: _Optional[str] = ..., default_port_address: _Optional[str] = ..., default_port_protocol: _Optional[str] = ..., default_programmer: _Optional[str] = ...) -> None: ...

class CheckForArduinoCLIUpdatesRequest(_message.Message):
    __slots__ = ("force_check",)
    FORCE_CHECK_FIELD_NUMBER: _ClassVar[int]
    force_check: bool
    def __init__(self, force_check: _Optional[bool] = ...) -> None: ...

class CheckForArduinoCLIUpdatesResponse(_message.Message):
    __slots__ = ("newest_version",)
    NEWEST_VERSION_FIELD_NUMBER: _ClassVar[int]
    newest_version: str
    def __init__(self, newest_version: _Optional[str] = ...) -> None: ...

class CleanDownloadCacheDirectoryRequest(_message.Message):
    __slots__ = ("instance",)
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ...) -> None: ...

class CleanDownloadCacheDirectoryResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProfileCreateRequest(_message.Message):
    __slots__ = ("instance", "sketch_path", "profile_name", "fqbn", "default_profile")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROFILE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    sketch_path: str
    profile_name: str
    fqbn: str
    default_profile: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., sketch_path: _Optional[str] = ..., profile_name: _Optional[str] = ..., fqbn: _Optional[str] = ..., default_profile: _Optional[bool] = ...) -> None: ...

class ProfileCreateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProfileLibAddRequest(_message.Message):
    __slots__ = ("instance", "sketch_path", "profile_name", "library", "add_dependencies", "no_overwrite")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    LIBRARY_FIELD_NUMBER: _ClassVar[int]
    ADD_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    NO_OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    sketch_path: str
    profile_name: str
    library: _common_pb2.ProfileLibraryReference
    add_dependencies: bool
    no_overwrite: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., sketch_path: _Optional[str] = ..., profile_name: _Optional[str] = ..., library: _Optional[_Union[_common_pb2.ProfileLibraryReference, _Mapping]] = ..., add_dependencies: _Optional[bool] = ..., no_overwrite: _Optional[bool] = ...) -> None: ...

class ProfileLibAddResponse(_message.Message):
    __slots__ = ("added_libraries", "skipped_libraries", "profile_name")
    ADDED_LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    SKIPPED_LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    added_libraries: _containers.RepeatedCompositeFieldContainer[_common_pb2.ProfileLibraryReference]
    skipped_libraries: _containers.RepeatedCompositeFieldContainer[_common_pb2.ProfileLibraryReference]
    profile_name: str
    def __init__(self, added_libraries: _Optional[_Iterable[_Union[_common_pb2.ProfileLibraryReference, _Mapping]]] = ..., skipped_libraries: _Optional[_Iterable[_Union[_common_pb2.ProfileLibraryReference, _Mapping]]] = ..., profile_name: _Optional[str] = ...) -> None: ...

class ProfileLibRemoveRequest(_message.Message):
    __slots__ = ("instance", "sketch_path", "profile_name", "library", "remove_dependencies")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    LIBRARY_FIELD_NUMBER: _ClassVar[int]
    REMOVE_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    sketch_path: str
    profile_name: str
    library: _common_pb2.ProfileLibraryReference
    remove_dependencies: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., sketch_path: _Optional[str] = ..., profile_name: _Optional[str] = ..., library: _Optional[_Union[_common_pb2.ProfileLibraryReference, _Mapping]] = ..., remove_dependencies: _Optional[bool] = ...) -> None: ...

class ProfileLibRemoveResponse(_message.Message):
    __slots__ = ("removed_libraries", "profile_name")
    REMOVED_LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    removed_libraries: _containers.RepeatedCompositeFieldContainer[_common_pb2.ProfileLibraryReference]
    profile_name: str
    def __init__(self, removed_libraries: _Optional[_Iterable[_Union[_common_pb2.ProfileLibraryReference, _Mapping]]] = ..., profile_name: _Optional[str] = ...) -> None: ...

class ProfileLibListRequest(_message.Message):
    __slots__ = ("sketch_path", "profile_name")
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    sketch_path: str
    profile_name: str
    def __init__(self, sketch_path: _Optional[str] = ..., profile_name: _Optional[str] = ...) -> None: ...

class ProfileLibListResponse(_message.Message):
    __slots__ = ("libraries", "profile_name")
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    libraries: _containers.RepeatedCompositeFieldContainer[_common_pb2.ProfileLibraryReference]
    profile_name: str
    def __init__(self, libraries: _Optional[_Iterable[_Union[_common_pb2.ProfileLibraryReference, _Mapping]]] = ..., profile_name: _Optional[str] = ...) -> None: ...

class ProfileSetDefaultRequest(_message.Message):
    __slots__ = ("sketch_path", "profile_name")
    SKETCH_PATH_FIELD_NUMBER: _ClassVar[int]
    PROFILE_NAME_FIELD_NUMBER: _ClassVar[int]
    sketch_path: str
    profile_name: str
    def __init__(self, sketch_path: _Optional[str] = ..., profile_name: _Optional[str] = ...) -> None: ...

class ProfileSetDefaultResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
