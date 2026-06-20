from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Instance(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DownloadProgress(_message.Message):
    __slots__ = ("start", "update", "end")
    START_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    start: DownloadProgressStart
    update: DownloadProgressUpdate
    end: DownloadProgressEnd
    def __init__(self, start: _Optional[_Union[DownloadProgressStart, _Mapping]] = ..., update: _Optional[_Union[DownloadProgressUpdate, _Mapping]] = ..., end: _Optional[_Union[DownloadProgressEnd, _Mapping]] = ...) -> None: ...

class DownloadProgressStart(_message.Message):
    __slots__ = ("url", "label")
    URL_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    url: str
    label: str
    def __init__(self, url: _Optional[str] = ..., label: _Optional[str] = ...) -> None: ...

class DownloadProgressUpdate(_message.Message):
    __slots__ = ("downloaded", "total_size")
    DOWNLOADED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    downloaded: int
    total_size: int
    def __init__(self, downloaded: _Optional[int] = ..., total_size: _Optional[int] = ...) -> None: ...

class DownloadProgressEnd(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class TaskProgress(_message.Message):
    __slots__ = ("name", "message", "completed", "percent")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    PERCENT_FIELD_NUMBER: _ClassVar[int]
    name: str
    message: str
    completed: bool
    percent: float
    def __init__(self, name: _Optional[str] = ..., message: _Optional[str] = ..., completed: _Optional[bool] = ..., percent: _Optional[float] = ...) -> None: ...

class Programmer(_message.Message):
    __slots__ = ("platform", "id", "name")
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    platform: str
    id: str
    name: str
    def __init__(self, platform: _Optional[str] = ..., id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class MissingProgrammerError(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Platform(_message.Message):
    __slots__ = ("metadata", "release")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RELEASE_FIELD_NUMBER: _ClassVar[int]
    metadata: PlatformMetadata
    release: PlatformRelease
    def __init__(self, metadata: _Optional[_Union[PlatformMetadata, _Mapping]] = ..., release: _Optional[_Union[PlatformRelease, _Mapping]] = ...) -> None: ...

class PlatformSummary(_message.Message):
    __slots__ = ("metadata", "releases", "installed_version", "latest_version")
    class ReleasesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PlatformRelease
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PlatformRelease, _Mapping]] = ...) -> None: ...
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RELEASES_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_VERSION_FIELD_NUMBER: _ClassVar[int]
    LATEST_VERSION_FIELD_NUMBER: _ClassVar[int]
    metadata: PlatformMetadata
    releases: _containers.MessageMap[str, PlatformRelease]
    installed_version: str
    latest_version: str
    def __init__(self, metadata: _Optional[_Union[PlatformMetadata, _Mapping]] = ..., releases: _Optional[_Mapping[str, PlatformRelease]] = ..., installed_version: _Optional[str] = ..., latest_version: _Optional[str] = ...) -> None: ...

class PlatformMetadata(_message.Message):
    __slots__ = ("id", "maintainer", "website", "email", "manually_installed", "deprecated", "indexed")
    ID_FIELD_NUMBER: _ClassVar[int]
    MAINTAINER_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    MANUALLY_INSTALLED_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    INDEXED_FIELD_NUMBER: _ClassVar[int]
    id: str
    maintainer: str
    website: str
    email: str
    manually_installed: bool
    deprecated: bool
    indexed: bool
    def __init__(self, id: _Optional[str] = ..., maintainer: _Optional[str] = ..., website: _Optional[str] = ..., email: _Optional[str] = ..., manually_installed: _Optional[bool] = ..., deprecated: _Optional[bool] = ..., indexed: _Optional[bool] = ...) -> None: ...

class PlatformRelease(_message.Message):
    __slots__ = ("name", "version", "types", "installed", "boards", "help", "missing_metadata", "deprecated", "compatible")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_FIELD_NUMBER: _ClassVar[int]
    BOARDS_FIELD_NUMBER: _ClassVar[int]
    HELP_FIELD_NUMBER: _ClassVar[int]
    MISSING_METADATA_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    COMPATIBLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    types: _containers.RepeatedScalarFieldContainer[str]
    installed: bool
    boards: _containers.RepeatedCompositeFieldContainer[Board]
    help: HelpResources
    missing_metadata: bool
    deprecated: bool
    compatible: bool
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., types: _Optional[_Iterable[str]] = ..., installed: _Optional[bool] = ..., boards: _Optional[_Iterable[_Union[Board, _Mapping]]] = ..., help: _Optional[_Union[HelpResources, _Mapping]] = ..., missing_metadata: _Optional[bool] = ..., deprecated: _Optional[bool] = ..., compatible: _Optional[bool] = ...) -> None: ...

class InstalledPlatformReference(_message.Message):
    __slots__ = ("id", "version", "install_dir", "package_url")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTALL_DIR_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: str
    install_dir: str
    package_url: str
    def __init__(self, id: _Optional[str] = ..., version: _Optional[str] = ..., install_dir: _Optional[str] = ..., package_url: _Optional[str] = ...) -> None: ...

class Board(_message.Message):
    __slots__ = ("name", "fqbn")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    name: str
    fqbn: str
    def __init__(self, name: _Optional[str] = ..., fqbn: _Optional[str] = ...) -> None: ...

class HelpResources(_message.Message):
    __slots__ = ("online",)
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    online: str
    def __init__(self, online: _Optional[str] = ...) -> None: ...

class Sketch(_message.Message):
    __slots__ = ("main_file", "location_path", "other_sketch_files", "additional_files", "root_folder_files", "default_fqbn", "default_port", "default_protocol", "profiles", "default_profile", "default_programmer", "default_port_config")
    MAIN_FILE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_PATH_FIELD_NUMBER: _ClassVar[int]
    OTHER_SKETCH_FILES_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_FILES_FIELD_NUMBER: _ClassVar[int]
    ROOT_FOLDER_FILES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FQBN_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PORT_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PROFILES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROFILE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PORT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    main_file: str
    location_path: str
    other_sketch_files: _containers.RepeatedScalarFieldContainer[str]
    additional_files: _containers.RepeatedScalarFieldContainer[str]
    root_folder_files: _containers.RepeatedScalarFieldContainer[str]
    default_fqbn: str
    default_port: str
    default_protocol: str
    profiles: _containers.RepeatedCompositeFieldContainer[SketchProfile]
    default_profile: SketchProfile
    default_programmer: str
    default_port_config: MonitorPortConfiguration
    def __init__(self, main_file: _Optional[str] = ..., location_path: _Optional[str] = ..., other_sketch_files: _Optional[_Iterable[str]] = ..., additional_files: _Optional[_Iterable[str]] = ..., root_folder_files: _Optional[_Iterable[str]] = ..., default_fqbn: _Optional[str] = ..., default_port: _Optional[str] = ..., default_protocol: _Optional[str] = ..., profiles: _Optional[_Iterable[_Union[SketchProfile, _Mapping]]] = ..., default_profile: _Optional[_Union[SketchProfile, _Mapping]] = ..., default_programmer: _Optional[str] = ..., default_port_config: _Optional[_Union[MonitorPortConfiguration, _Mapping]] = ...) -> None: ...

class MonitorPortConfiguration(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _containers.RepeatedCompositeFieldContainer[MonitorPortSetting]
    def __init__(self, settings: _Optional[_Iterable[_Union[MonitorPortSetting, _Mapping]]] = ...) -> None: ...

class MonitorPortSetting(_message.Message):
    __slots__ = ("setting_id", "value")
    SETTING_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    setting_id: str
    value: str
    def __init__(self, setting_id: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class SketchProfile(_message.Message):
    __slots__ = ("name", "fqbn", "programmer", "port", "port_config", "protocol", "platforms", "libraries")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMER_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    PORT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PLATFORMS_FIELD_NUMBER: _ClassVar[int]
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    fqbn: str
    programmer: str
    port: str
    port_config: MonitorPortConfiguration
    protocol: str
    platforms: _containers.RepeatedCompositeFieldContainer[ProfilePlatformReference]
    libraries: _containers.RepeatedCompositeFieldContainer[ProfileLibraryReference]
    def __init__(self, name: _Optional[str] = ..., fqbn: _Optional[str] = ..., programmer: _Optional[str] = ..., port: _Optional[str] = ..., port_config: _Optional[_Union[MonitorPortConfiguration, _Mapping]] = ..., protocol: _Optional[str] = ..., platforms: _Optional[_Iterable[_Union[ProfilePlatformReference, _Mapping]]] = ..., libraries: _Optional[_Iterable[_Union[ProfileLibraryReference, _Mapping]]] = ...) -> None: ...

class ProfilePlatformReference(_message.Message):
    __slots__ = ("id", "version", "index_url")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INDEX_URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    version: str
    index_url: str
    def __init__(self, id: _Optional[str] = ..., version: _Optional[str] = ..., index_url: _Optional[str] = ...) -> None: ...

class ProfileLibraryReference(_message.Message):
    __slots__ = ("index_library", "local_library")
    class IndexLibrary(_message.Message):
        __slots__ = ("name", "version", "is_dependency")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VERSION_FIELD_NUMBER: _ClassVar[int]
        IS_DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
        name: str
        version: str
        is_dependency: bool
        def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., is_dependency: _Optional[bool] = ...) -> None: ...
    class LocalLibrary(_message.Message):
        __slots__ = ("path",)
        PATH_FIELD_NUMBER: _ClassVar[int]
        path: str
        def __init__(self, path: _Optional[str] = ...) -> None: ...
    INDEX_LIBRARY_FIELD_NUMBER: _ClassVar[int]
    LOCAL_LIBRARY_FIELD_NUMBER: _ClassVar[int]
    index_library: ProfileLibraryReference.IndexLibrary
    local_library: ProfileLibraryReference.LocalLibrary
    def __init__(self, index_library: _Optional[_Union[ProfileLibraryReference.IndexLibrary, _Mapping]] = ..., local_library: _Optional[_Union[ProfileLibraryReference.LocalLibrary, _Mapping]] = ...) -> None: ...
