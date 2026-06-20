from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlatformInstallRequest(_message.Message):
    __slots__ = ("instance", "platform_package", "architecture", "version", "skip_post_install", "no_overwrite", "skip_pre_uninstall")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_PACKAGE_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SKIP_POST_INSTALL_FIELD_NUMBER: _ClassVar[int]
    NO_OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    SKIP_PRE_UNINSTALL_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    platform_package: str
    architecture: str
    version: str
    skip_post_install: bool
    no_overwrite: bool
    skip_pre_uninstall: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., platform_package: _Optional[str] = ..., architecture: _Optional[str] = ..., version: _Optional[str] = ..., skip_post_install: _Optional[bool] = ..., no_overwrite: _Optional[bool] = ..., skip_pre_uninstall: _Optional[bool] = ...) -> None: ...

class PlatformInstallResponse(_message.Message):
    __slots__ = ("progress", "task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    progress: _common_pb2.DownloadProgress
    task_progress: _common_pb2.TaskProgress
    result: PlatformInstallResponse.Result
    def __init__(self, progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[PlatformInstallResponse.Result, _Mapping]] = ...) -> None: ...

class PlatformLoadingError(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PlatformDownloadRequest(_message.Message):
    __slots__ = ("instance", "platform_package", "architecture", "version")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_PACKAGE_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    platform_package: str
    architecture: str
    version: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., platform_package: _Optional[str] = ..., architecture: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class PlatformDownloadResponse(_message.Message):
    __slots__ = ("progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    progress: _common_pb2.DownloadProgress
    result: PlatformDownloadResponse.Result
    def __init__(self, progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., result: _Optional[_Union[PlatformDownloadResponse.Result, _Mapping]] = ...) -> None: ...

class PlatformUninstallRequest(_message.Message):
    __slots__ = ("instance", "platform_package", "architecture", "skip_pre_uninstall")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_PACKAGE_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    SKIP_PRE_UNINSTALL_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    platform_package: str
    architecture: str
    skip_pre_uninstall: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., platform_package: _Optional[str] = ..., architecture: _Optional[str] = ..., skip_pre_uninstall: _Optional[bool] = ...) -> None: ...

class PlatformUninstallResponse(_message.Message):
    __slots__ = ("task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    task_progress: _common_pb2.TaskProgress
    result: PlatformUninstallResponse.Result
    def __init__(self, task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[PlatformUninstallResponse.Result, _Mapping]] = ...) -> None: ...

class AlreadyAtLatestVersionError(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PlatformUpgradeRequest(_message.Message):
    __slots__ = ("instance", "platform_package", "architecture", "skip_post_install", "skip_pre_uninstall")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_PACKAGE_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    SKIP_POST_INSTALL_FIELD_NUMBER: _ClassVar[int]
    SKIP_PRE_UNINSTALL_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    platform_package: str
    architecture: str
    skip_post_install: bool
    skip_pre_uninstall: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., platform_package: _Optional[str] = ..., architecture: _Optional[str] = ..., skip_post_install: _Optional[bool] = ..., skip_pre_uninstall: _Optional[bool] = ...) -> None: ...

class PlatformUpgradeResponse(_message.Message):
    __slots__ = ("progress", "task_progress", "result")
    class Result(_message.Message):
        __slots__ = ("platform",)
        PLATFORM_FIELD_NUMBER: _ClassVar[int]
        platform: _common_pb2.Platform
        def __init__(self, platform: _Optional[_Union[_common_pb2.Platform, _Mapping]] = ...) -> None: ...
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    progress: _common_pb2.DownloadProgress
    task_progress: _common_pb2.TaskProgress
    result: PlatformUpgradeResponse.Result
    def __init__(self, progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[PlatformUpgradeResponse.Result, _Mapping]] = ...) -> None: ...

class PlatformSearchRequest(_message.Message):
    __slots__ = ("instance", "search_args", "manually_installed")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_ARGS_FIELD_NUMBER: _ClassVar[int]
    MANUALLY_INSTALLED_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    search_args: str
    manually_installed: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., search_args: _Optional[str] = ..., manually_installed: _Optional[bool] = ...) -> None: ...

class PlatformSearchResponse(_message.Message):
    __slots__ = ("search_output",)
    SEARCH_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    search_output: _containers.RepeatedCompositeFieldContainer[_common_pb2.PlatformSummary]
    def __init__(self, search_output: _Optional[_Iterable[_Union[_common_pb2.PlatformSummary, _Mapping]]] = ...) -> None: ...
