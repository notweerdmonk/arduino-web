from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LibraryInstallLocation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIBRARY_INSTALL_LOCATION_USER: _ClassVar[LibraryInstallLocation]
    LIBRARY_INSTALL_LOCATION_BUILTIN: _ClassVar[LibraryInstallLocation]

class LibrarySearchStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIBRARY_SEARCH_STATUS_FAILED: _ClassVar[LibrarySearchStatus]
    LIBRARY_SEARCH_STATUS_SUCCESS: _ClassVar[LibrarySearchStatus]

class LibraryLayout(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIBRARY_LAYOUT_FLAT: _ClassVar[LibraryLayout]
    LIBRARY_LAYOUT_RECURSIVE: _ClassVar[LibraryLayout]

class LibraryLocation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LIBRARY_LOCATION_BUILTIN: _ClassVar[LibraryLocation]
    LIBRARY_LOCATION_USER: _ClassVar[LibraryLocation]
    LIBRARY_LOCATION_PLATFORM_BUILTIN: _ClassVar[LibraryLocation]
    LIBRARY_LOCATION_REFERENCED_PLATFORM_BUILTIN: _ClassVar[LibraryLocation]
    LIBRARY_LOCATION_UNMANAGED: _ClassVar[LibraryLocation]
    LIBRARY_LOCATION_PROFILE: _ClassVar[LibraryLocation]
LIBRARY_INSTALL_LOCATION_USER: LibraryInstallLocation
LIBRARY_INSTALL_LOCATION_BUILTIN: LibraryInstallLocation
LIBRARY_SEARCH_STATUS_FAILED: LibrarySearchStatus
LIBRARY_SEARCH_STATUS_SUCCESS: LibrarySearchStatus
LIBRARY_LAYOUT_FLAT: LibraryLayout
LIBRARY_LAYOUT_RECURSIVE: LibraryLayout
LIBRARY_LOCATION_BUILTIN: LibraryLocation
LIBRARY_LOCATION_USER: LibraryLocation
LIBRARY_LOCATION_PLATFORM_BUILTIN: LibraryLocation
LIBRARY_LOCATION_REFERENCED_PLATFORM_BUILTIN: LibraryLocation
LIBRARY_LOCATION_UNMANAGED: LibraryLocation
LIBRARY_LOCATION_PROFILE: LibraryLocation

class LibraryDownloadRequest(_message.Message):
    __slots__ = ("instance", "name", "version")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    name: str
    version: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class LibraryDownloadResponse(_message.Message):
    __slots__ = ("progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    progress: _common_pb2.DownloadProgress
    result: LibraryDownloadResponse.Result
    def __init__(self, progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., result: _Optional[_Union[LibraryDownloadResponse.Result, _Mapping]] = ...) -> None: ...

class LibraryInstallRequest(_message.Message):
    __slots__ = ("instance", "name", "version", "no_deps", "no_overwrite", "install_location")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NO_DEPS_FIELD_NUMBER: _ClassVar[int]
    NO_OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    INSTALL_LOCATION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    name: str
    version: str
    no_deps: bool
    no_overwrite: bool
    install_location: LibraryInstallLocation
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., name: _Optional[str] = ..., version: _Optional[str] = ..., no_deps: _Optional[bool] = ..., no_overwrite: _Optional[bool] = ..., install_location: _Optional[_Union[LibraryInstallLocation, str]] = ...) -> None: ...

class LibraryInstallResponse(_message.Message):
    __slots__ = ("progress", "task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    progress: _common_pb2.DownloadProgress
    task_progress: _common_pb2.TaskProgress
    result: LibraryInstallResponse.Result
    def __init__(self, progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[LibraryInstallResponse.Result, _Mapping]] = ...) -> None: ...

class LibraryUpgradeRequest(_message.Message):
    __slots__ = ("instance", "name", "no_deps")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_DEPS_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    name: str
    no_deps: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., name: _Optional[str] = ..., no_deps: _Optional[bool] = ...) -> None: ...

class LibraryUpgradeResponse(_message.Message):
    __slots__ = ("progress", "task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    progress: _common_pb2.DownloadProgress
    task_progress: _common_pb2.TaskProgress
    result: LibraryUpgradeResponse.Result
    def __init__(self, progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[LibraryUpgradeResponse.Result, _Mapping]] = ...) -> None: ...

class LibraryUninstallRequest(_message.Message):
    __slots__ = ("instance", "name", "version")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    name: str
    version: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class LibraryUninstallResponse(_message.Message):
    __slots__ = ("task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    task_progress: _common_pb2.TaskProgress
    result: LibraryUninstallResponse.Result
    def __init__(self, task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[LibraryUninstallResponse.Result, _Mapping]] = ...) -> None: ...

class LibraryUpgradeAllRequest(_message.Message):
    __slots__ = ("instance",)
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ...) -> None: ...

class LibraryUpgradeAllResponse(_message.Message):
    __slots__ = ("progress", "task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    progress: _common_pb2.DownloadProgress
    task_progress: _common_pb2.TaskProgress
    result: LibraryUpgradeAllResponse.Result
    def __init__(self, progress: _Optional[_Union[_common_pb2.DownloadProgress, _Mapping]] = ..., task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[LibraryUpgradeAllResponse.Result, _Mapping]] = ...) -> None: ...

class LibraryResolveDependenciesRequest(_message.Message):
    __slots__ = ("instance", "name", "version", "do_not_update_installed_libraries")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DO_NOT_UPDATE_INSTALLED_LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    name: str
    version: str
    do_not_update_installed_libraries: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., name: _Optional[str] = ..., version: _Optional[str] = ..., do_not_update_installed_libraries: _Optional[bool] = ...) -> None: ...

class LibraryResolveDependenciesResponse(_message.Message):
    __slots__ = ("dependencies",)
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    dependencies: _containers.RepeatedCompositeFieldContainer[LibraryDependencyStatus]
    def __init__(self, dependencies: _Optional[_Iterable[_Union[LibraryDependencyStatus, _Mapping]]] = ...) -> None: ...

class LibraryDependencyStatus(_message.Message):
    __slots__ = ("name", "version_required", "version_installed")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    VERSION_INSTALLED_FIELD_NUMBER: _ClassVar[int]
    name: str
    version_required: str
    version_installed: str
    def __init__(self, name: _Optional[str] = ..., version_required: _Optional[str] = ..., version_installed: _Optional[str] = ...) -> None: ...

class LibrarySearchRequest(_message.Message):
    __slots__ = ("instance", "omit_releases_details", "search_args")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    OMIT_RELEASES_DETAILS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_ARGS_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    omit_releases_details: bool
    search_args: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., omit_releases_details: _Optional[bool] = ..., search_args: _Optional[str] = ...) -> None: ...

class LibrarySearchResponse(_message.Message):
    __slots__ = ("libraries", "status")
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    libraries: _containers.RepeatedCompositeFieldContainer[SearchedLibrary]
    status: LibrarySearchStatus
    def __init__(self, libraries: _Optional[_Iterable[_Union[SearchedLibrary, _Mapping]]] = ..., status: _Optional[_Union[LibrarySearchStatus, str]] = ...) -> None: ...

class SearchedLibrary(_message.Message):
    __slots__ = ("name", "releases", "latest", "available_versions")
    class ReleasesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: LibraryRelease
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[LibraryRelease, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    RELEASES_FIELD_NUMBER: _ClassVar[int]
    LATEST_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    releases: _containers.MessageMap[str, LibraryRelease]
    latest: LibraryRelease
    available_versions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., releases: _Optional[_Mapping[str, LibraryRelease]] = ..., latest: _Optional[_Union[LibraryRelease, _Mapping]] = ..., available_versions: _Optional[_Iterable[str]] = ...) -> None: ...

class LibraryRelease(_message.Message):
    __slots__ = ("author", "version", "maintainer", "sentence", "paragraph", "website", "category", "architectures", "types", "resources", "license", "provides_includes", "dependencies")
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    MAINTAINER_FIELD_NUMBER: _ClassVar[int]
    SENTENCE_FIELD_NUMBER: _ClassVar[int]
    PARAGRAPH_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURES_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    LICENSE_FIELD_NUMBER: _ClassVar[int]
    PROVIDES_INCLUDES_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    author: str
    version: str
    maintainer: str
    sentence: str
    paragraph: str
    website: str
    category: str
    architectures: _containers.RepeatedScalarFieldContainer[str]
    types: _containers.RepeatedScalarFieldContainer[str]
    resources: DownloadResource
    license: str
    provides_includes: _containers.RepeatedScalarFieldContainer[str]
    dependencies: _containers.RepeatedCompositeFieldContainer[LibraryDependency]
    def __init__(self, author: _Optional[str] = ..., version: _Optional[str] = ..., maintainer: _Optional[str] = ..., sentence: _Optional[str] = ..., paragraph: _Optional[str] = ..., website: _Optional[str] = ..., category: _Optional[str] = ..., architectures: _Optional[_Iterable[str]] = ..., types: _Optional[_Iterable[str]] = ..., resources: _Optional[_Union[DownloadResource, _Mapping]] = ..., license: _Optional[str] = ..., provides_includes: _Optional[_Iterable[str]] = ..., dependencies: _Optional[_Iterable[_Union[LibraryDependency, _Mapping]]] = ...) -> None: ...

class LibraryDependency(_message.Message):
    __slots__ = ("name", "version_constraint")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_CONSTRAINT_FIELD_NUMBER: _ClassVar[int]
    name: str
    version_constraint: str
    def __init__(self, name: _Optional[str] = ..., version_constraint: _Optional[str] = ...) -> None: ...

class DownloadResource(_message.Message):
    __slots__ = ("url", "archive_filename", "checksum", "size", "cache_path")
    URL_FIELD_NUMBER: _ClassVar[int]
    ARCHIVE_FILENAME_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CACHE_PATH_FIELD_NUMBER: _ClassVar[int]
    url: str
    archive_filename: str
    checksum: str
    size: int
    cache_path: str
    def __init__(self, url: _Optional[str] = ..., archive_filename: _Optional[str] = ..., checksum: _Optional[str] = ..., size: _Optional[int] = ..., cache_path: _Optional[str] = ...) -> None: ...

class LibraryListRequest(_message.Message):
    __slots__ = ("instance", "all", "updatable", "name", "fqbn")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    UPDATABLE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    all: bool
    updatable: bool
    name: str
    fqbn: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., all: _Optional[bool] = ..., updatable: _Optional[bool] = ..., name: _Optional[str] = ..., fqbn: _Optional[str] = ...) -> None: ...

class LibraryListResponse(_message.Message):
    __slots__ = ("installed_libraries",)
    INSTALLED_LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    installed_libraries: _containers.RepeatedCompositeFieldContainer[InstalledLibrary]
    def __init__(self, installed_libraries: _Optional[_Iterable[_Union[InstalledLibrary, _Mapping]]] = ...) -> None: ...

class InstalledLibrary(_message.Message):
    __slots__ = ("library", "release")
    LIBRARY_FIELD_NUMBER: _ClassVar[int]
    RELEASE_FIELD_NUMBER: _ClassVar[int]
    library: Library
    release: LibraryRelease
    def __init__(self, library: _Optional[_Union[Library, _Mapping]] = ..., release: _Optional[_Union[LibraryRelease, _Mapping]] = ...) -> None: ...

class Library(_message.Message):
    __slots__ = ("name", "author", "maintainer", "sentence", "paragraph", "website", "category", "architectures", "types", "install_dir", "source_dir", "utility_dir", "container_platform", "dot_a_linkage", "precompiled", "ld_flags", "is_legacy", "version", "license", "properties", "location", "layout", "examples", "provides_includes", "compatible_with", "in_development")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class CompatibleWithEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bool] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    MAINTAINER_FIELD_NUMBER: _ClassVar[int]
    SENTENCE_FIELD_NUMBER: _ClassVar[int]
    PARAGRAPH_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURES_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    INSTALL_DIR_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DIR_FIELD_NUMBER: _ClassVar[int]
    UTILITY_DIR_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_PLATFORM_FIELD_NUMBER: _ClassVar[int]
    DOT_A_LINKAGE_FIELD_NUMBER: _ClassVar[int]
    PRECOMPILED_FIELD_NUMBER: _ClassVar[int]
    LD_FLAGS_FIELD_NUMBER: _ClassVar[int]
    IS_LEGACY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    LICENSE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    LAYOUT_FIELD_NUMBER: _ClassVar[int]
    EXAMPLES_FIELD_NUMBER: _ClassVar[int]
    PROVIDES_INCLUDES_FIELD_NUMBER: _ClassVar[int]
    COMPATIBLE_WITH_FIELD_NUMBER: _ClassVar[int]
    IN_DEVELOPMENT_FIELD_NUMBER: _ClassVar[int]
    name: str
    author: str
    maintainer: str
    sentence: str
    paragraph: str
    website: str
    category: str
    architectures: _containers.RepeatedScalarFieldContainer[str]
    types: _containers.RepeatedScalarFieldContainer[str]
    install_dir: str
    source_dir: str
    utility_dir: str
    container_platform: str
    dot_a_linkage: bool
    precompiled: bool
    ld_flags: str
    is_legacy: bool
    version: str
    license: str
    properties: _containers.ScalarMap[str, str]
    location: LibraryLocation
    layout: LibraryLayout
    examples: _containers.RepeatedScalarFieldContainer[str]
    provides_includes: _containers.RepeatedScalarFieldContainer[str]
    compatible_with: _containers.ScalarMap[str, bool]
    in_development: bool
    def __init__(self, name: _Optional[str] = ..., author: _Optional[str] = ..., maintainer: _Optional[str] = ..., sentence: _Optional[str] = ..., paragraph: _Optional[str] = ..., website: _Optional[str] = ..., category: _Optional[str] = ..., architectures: _Optional[_Iterable[str]] = ..., types: _Optional[_Iterable[str]] = ..., install_dir: _Optional[str] = ..., source_dir: _Optional[str] = ..., utility_dir: _Optional[str] = ..., container_platform: _Optional[str] = ..., dot_a_linkage: _Optional[bool] = ..., precompiled: _Optional[bool] = ..., ld_flags: _Optional[str] = ..., is_legacy: _Optional[bool] = ..., version: _Optional[str] = ..., license: _Optional[str] = ..., properties: _Optional[_Mapping[str, str]] = ..., location: _Optional[_Union[LibraryLocation, str]] = ..., layout: _Optional[_Union[LibraryLayout, str]] = ..., examples: _Optional[_Iterable[str]] = ..., provides_includes: _Optional[_Iterable[str]] = ..., compatible_with: _Optional[_Mapping[str, bool]] = ..., in_development: _Optional[bool] = ...) -> None: ...

class ZipLibraryInstallRequest(_message.Message):
    __slots__ = ("instance", "path", "overwrite")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    path: str
    overwrite: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., path: _Optional[str] = ..., overwrite: _Optional[bool] = ...) -> None: ...

class ZipLibraryInstallResponse(_message.Message):
    __slots__ = ("task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    task_progress: _common_pb2.TaskProgress
    result: ZipLibraryInstallResponse.Result
    def __init__(self, task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[ZipLibraryInstallResponse.Result, _Mapping]] = ...) -> None: ...

class GitLibraryInstallRequest(_message.Message):
    __slots__ = ("instance", "url", "overwrite")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    url: str
    overwrite: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., url: _Optional[str] = ..., overwrite: _Optional[bool] = ...) -> None: ...

class GitLibraryInstallResponse(_message.Message):
    __slots__ = ("task_progress", "result")
    class Result(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    TASK_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    task_progress: _common_pb2.TaskProgress
    result: GitLibraryInstallResponse.Result
    def __init__(self, task_progress: _Optional[_Union[_common_pb2.TaskProgress, _Mapping]] = ..., result: _Optional[_Union[GitLibraryInstallResponse.Result, _Mapping]] = ...) -> None: ...
