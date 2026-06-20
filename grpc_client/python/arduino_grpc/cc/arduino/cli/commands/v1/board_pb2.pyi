from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from cc.arduino.cli.commands.v1 import port_pb2 as _port_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoardDetailsRequest(_message.Message):
    __slots__ = ("instance", "fqbn", "do_not_expand_build_properties")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    DO_NOT_EXPAND_BUILD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    fqbn: str
    do_not_expand_build_properties: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., fqbn: _Optional[str] = ..., do_not_expand_build_properties: _Optional[bool] = ...) -> None: ...

class BoardDetailsResponse(_message.Message):
    __slots__ = ("fqbn", "name", "version", "properties_id", "alias", "official", "pinout", "package", "platform", "tools_dependencies", "config_options", "programmers", "identification_properties", "build_properties", "default_programmer_id")
    FQBN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_ID_FIELD_NUMBER: _ClassVar[int]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    OFFICIAL_FIELD_NUMBER: _ClassVar[int]
    PINOUT_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    TOOLS_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    CONFIG_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    PROGRAMMERS_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    BUILD_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_PROGRAMMER_ID_FIELD_NUMBER: _ClassVar[int]
    fqbn: str
    name: str
    version: str
    properties_id: str
    alias: str
    official: bool
    pinout: str
    package: Package
    platform: BoardPlatform
    tools_dependencies: _containers.RepeatedCompositeFieldContainer[ToolsDependencies]
    config_options: _containers.RepeatedCompositeFieldContainer[ConfigOption]
    programmers: _containers.RepeatedCompositeFieldContainer[_common_pb2.Programmer]
    identification_properties: _containers.RepeatedCompositeFieldContainer[BoardIdentificationProperties]
    build_properties: _containers.RepeatedScalarFieldContainer[str]
    default_programmer_id: str
    def __init__(self, fqbn: _Optional[str] = ..., name: _Optional[str] = ..., version: _Optional[str] = ..., properties_id: _Optional[str] = ..., alias: _Optional[str] = ..., official: _Optional[bool] = ..., pinout: _Optional[str] = ..., package: _Optional[_Union[Package, _Mapping]] = ..., platform: _Optional[_Union[BoardPlatform, _Mapping]] = ..., tools_dependencies: _Optional[_Iterable[_Union[ToolsDependencies, _Mapping]]] = ..., config_options: _Optional[_Iterable[_Union[ConfigOption, _Mapping]]] = ..., programmers: _Optional[_Iterable[_Union[_common_pb2.Programmer, _Mapping]]] = ..., identification_properties: _Optional[_Iterable[_Union[BoardIdentificationProperties, _Mapping]]] = ..., build_properties: _Optional[_Iterable[str]] = ..., default_programmer_id: _Optional[str] = ...) -> None: ...

class BoardIdentificationProperties(_message.Message):
    __slots__ = ("properties",)
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    properties: _containers.ScalarMap[str, str]
    def __init__(self, properties: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Package(_message.Message):
    __slots__ = ("maintainer", "url", "website_url", "email", "name", "help")
    MAINTAINER_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_URL_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HELP_FIELD_NUMBER: _ClassVar[int]
    maintainer: str
    url: str
    website_url: str
    email: str
    name: str
    help: Help
    def __init__(self, maintainer: _Optional[str] = ..., url: _Optional[str] = ..., website_url: _Optional[str] = ..., email: _Optional[str] = ..., name: _Optional[str] = ..., help: _Optional[_Union[Help, _Mapping]] = ...) -> None: ...

class Help(_message.Message):
    __slots__ = ("online",)
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    online: str
    def __init__(self, online: _Optional[str] = ...) -> None: ...

class BoardPlatform(_message.Message):
    __slots__ = ("architecture", "category", "url", "archive_filename", "checksum", "size", "name")
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    ARCHIVE_FILENAME_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    architecture: str
    category: str
    url: str
    archive_filename: str
    checksum: str
    size: int
    name: str
    def __init__(self, architecture: _Optional[str] = ..., category: _Optional[str] = ..., url: _Optional[str] = ..., archive_filename: _Optional[str] = ..., checksum: _Optional[str] = ..., size: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class ToolsDependencies(_message.Message):
    __slots__ = ("packager", "name", "version", "systems")
    PACKAGER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SYSTEMS_FIELD_NUMBER: _ClassVar[int]
    packager: str
    name: str
    version: str
    systems: _containers.RepeatedCompositeFieldContainer[Systems]
    def __init__(self, packager: _Optional[str] = ..., name: _Optional[str] = ..., version: _Optional[str] = ..., systems: _Optional[_Iterable[_Union[Systems, _Mapping]]] = ...) -> None: ...

class Systems(_message.Message):
    __slots__ = ("checksum", "host", "archive_filename", "url", "size")
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    ARCHIVE_FILENAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    checksum: str
    host: str
    archive_filename: str
    url: str
    size: int
    def __init__(self, checksum: _Optional[str] = ..., host: _Optional[str] = ..., archive_filename: _Optional[str] = ..., url: _Optional[str] = ..., size: _Optional[int] = ...) -> None: ...

class ConfigOption(_message.Message):
    __slots__ = ("option", "option_label", "values")
    OPTION_FIELD_NUMBER: _ClassVar[int]
    OPTION_LABEL_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    option: str
    option_label: str
    values: _containers.RepeatedCompositeFieldContainer[ConfigValue]
    def __init__(self, option: _Optional[str] = ..., option_label: _Optional[str] = ..., values: _Optional[_Iterable[_Union[ConfigValue, _Mapping]]] = ...) -> None: ...

class ConfigValue(_message.Message):
    __slots__ = ("value", "value_label", "selected")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VALUE_LABEL_FIELD_NUMBER: _ClassVar[int]
    SELECTED_FIELD_NUMBER: _ClassVar[int]
    value: str
    value_label: str
    selected: bool
    def __init__(self, value: _Optional[str] = ..., value_label: _Optional[str] = ..., selected: _Optional[bool] = ...) -> None: ...

class BoardListRequest(_message.Message):
    __slots__ = ("instance", "timeout", "fqbn", "skip_cloud_api_for_board_detection")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    SKIP_CLOUD_API_FOR_BOARD_DETECTION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    timeout: int
    fqbn: str
    skip_cloud_api_for_board_detection: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., timeout: _Optional[int] = ..., fqbn: _Optional[str] = ..., skip_cloud_api_for_board_detection: _Optional[bool] = ...) -> None: ...

class BoardListResponse(_message.Message):
    __slots__ = ("ports", "warnings")
    PORTS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    ports: _containers.RepeatedCompositeFieldContainer[DetectedPort]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ports: _Optional[_Iterable[_Union[DetectedPort, _Mapping]]] = ..., warnings: _Optional[_Iterable[str]] = ...) -> None: ...

class DetectedPort(_message.Message):
    __slots__ = ("matching_boards", "port")
    MATCHING_BOARDS_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    matching_boards: _containers.RepeatedCompositeFieldContainer[BoardListItem]
    port: _port_pb2.Port
    def __init__(self, matching_boards: _Optional[_Iterable[_Union[BoardListItem, _Mapping]]] = ..., port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ...) -> None: ...

class BoardListAllRequest(_message.Message):
    __slots__ = ("instance", "search_args", "include_hidden_boards")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_ARGS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_BOARDS_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    search_args: _containers.RepeatedScalarFieldContainer[str]
    include_hidden_boards: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., search_args: _Optional[_Iterable[str]] = ..., include_hidden_boards: _Optional[bool] = ...) -> None: ...

class BoardListAllResponse(_message.Message):
    __slots__ = ("boards",)
    BOARDS_FIELD_NUMBER: _ClassVar[int]
    boards: _containers.RepeatedCompositeFieldContainer[BoardListItem]
    def __init__(self, boards: _Optional[_Iterable[_Union[BoardListItem, _Mapping]]] = ...) -> None: ...

class BoardListWatchRequest(_message.Message):
    __slots__ = ("instance", "skip_cloud_api_for_board_detection")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SKIP_CLOUD_API_FOR_BOARD_DETECTION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    skip_cloud_api_for_board_detection: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., skip_cloud_api_for_board_detection: _Optional[bool] = ...) -> None: ...

class BoardListWatchResponse(_message.Message):
    __slots__ = ("event_type", "port", "error")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    port: DetectedPort
    error: str
    def __init__(self, event_type: _Optional[str] = ..., port: _Optional[_Union[DetectedPort, _Mapping]] = ..., error: _Optional[str] = ...) -> None: ...

class BoardListItem(_message.Message):
    __slots__ = ("name", "fqbn", "is_hidden", "platform")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    IS_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    name: str
    fqbn: str
    is_hidden: bool
    platform: _common_pb2.Platform
    def __init__(self, name: _Optional[str] = ..., fqbn: _Optional[str] = ..., is_hidden: _Optional[bool] = ..., platform: _Optional[_Union[_common_pb2.Platform, _Mapping]] = ...) -> None: ...

class BoardSearchRequest(_message.Message):
    __slots__ = ("instance", "search_args", "include_hidden_boards")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_ARGS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_HIDDEN_BOARDS_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    search_args: str
    include_hidden_boards: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., search_args: _Optional[str] = ..., include_hidden_boards: _Optional[bool] = ...) -> None: ...

class BoardSearchResponse(_message.Message):
    __slots__ = ("boards",)
    BOARDS_FIELD_NUMBER: _ClassVar[int]
    boards: _containers.RepeatedCompositeFieldContainer[BoardListItem]
    def __init__(self, boards: _Optional[_Iterable[_Union[BoardListItem, _Mapping]]] = ...) -> None: ...

class BoardIdentifyRequest(_message.Message):
    __slots__ = ("instance", "properties", "use_cloud_api_for_unknown_board_detection")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    USE_CLOUD_API_FOR_UNKNOWN_BOARD_DETECTION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    properties: _containers.ScalarMap[str, str]
    use_cloud_api_for_unknown_board_detection: bool
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., properties: _Optional[_Mapping[str, str]] = ..., use_cloud_api_for_unknown_board_detection: _Optional[bool] = ...) -> None: ...

class BoardIdentifyResponse(_message.Message):
    __slots__ = ("boards",)
    BOARDS_FIELD_NUMBER: _ClassVar[int]
    boards: _containers.RepeatedCompositeFieldContainer[BoardListItem]
    def __init__(self, boards: _Optional[_Iterable[_Union[BoardListItem, _Mapping]]] = ...) -> None: ...
