from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Configuration(_message.Message):
    __slots__ = ("directories", "network", "sketch", "build_cache", "board_manager", "daemon", "output", "logging", "library", "updater", "locale")
    class Directories(_message.Message):
        __slots__ = ("data", "user", "downloads", "builtin")
        class Builtin(_message.Message):
            __slots__ = ("libraries",)
            LIBRARIES_FIELD_NUMBER: _ClassVar[int]
            libraries: str
            def __init__(self, libraries: _Optional[str] = ...) -> None: ...
        DATA_FIELD_NUMBER: _ClassVar[int]
        USER_FIELD_NUMBER: _ClassVar[int]
        DOWNLOADS_FIELD_NUMBER: _ClassVar[int]
        BUILTIN_FIELD_NUMBER: _ClassVar[int]
        data: str
        user: str
        downloads: str
        builtin: Configuration.Directories.Builtin
        def __init__(self, data: _Optional[str] = ..., user: _Optional[str] = ..., downloads: _Optional[str] = ..., builtin: _Optional[_Union[Configuration.Directories.Builtin, _Mapping]] = ...) -> None: ...
    class Network(_message.Message):
        __slots__ = ("extra_user_agent", "proxy")
        EXTRA_USER_AGENT_FIELD_NUMBER: _ClassVar[int]
        PROXY_FIELD_NUMBER: _ClassVar[int]
        extra_user_agent: str
        proxy: str
        def __init__(self, extra_user_agent: _Optional[str] = ..., proxy: _Optional[str] = ...) -> None: ...
    class Sketch(_message.Message):
        __slots__ = ("always_export_binaries",)
        ALWAYS_EXPORT_BINARIES_FIELD_NUMBER: _ClassVar[int]
        always_export_binaries: bool
        def __init__(self, always_export_binaries: _Optional[bool] = ...) -> None: ...
    class BuildCache(_message.Message):
        __slots__ = ("compilations_before_purge", "ttl_secs")
        COMPILATIONS_BEFORE_PURGE_FIELD_NUMBER: _ClassVar[int]
        TTL_SECS_FIELD_NUMBER: _ClassVar[int]
        compilations_before_purge: int
        ttl_secs: int
        def __init__(self, compilations_before_purge: _Optional[int] = ..., ttl_secs: _Optional[int] = ...) -> None: ...
    class BoardManager(_message.Message):
        __slots__ = ("additional_urls",)
        ADDITIONAL_URLS_FIELD_NUMBER: _ClassVar[int]
        additional_urls: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, additional_urls: _Optional[_Iterable[str]] = ...) -> None: ...
    class Daemon(_message.Message):
        __slots__ = ("port",)
        PORT_FIELD_NUMBER: _ClassVar[int]
        port: str
        def __init__(self, port: _Optional[str] = ...) -> None: ...
    class Output(_message.Message):
        __slots__ = ("no_color",)
        NO_COLOR_FIELD_NUMBER: _ClassVar[int]
        no_color: bool
        def __init__(self, no_color: _Optional[bool] = ...) -> None: ...
    class Logging(_message.Message):
        __slots__ = ("level", "format", "file")
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        FORMAT_FIELD_NUMBER: _ClassVar[int]
        FILE_FIELD_NUMBER: _ClassVar[int]
        level: str
        format: str
        file: str
        def __init__(self, level: _Optional[str] = ..., format: _Optional[str] = ..., file: _Optional[str] = ...) -> None: ...
    class Library(_message.Message):
        __slots__ = ("enable_unsafe_install",)
        ENABLE_UNSAFE_INSTALL_FIELD_NUMBER: _ClassVar[int]
        enable_unsafe_install: bool
        def __init__(self, enable_unsafe_install: _Optional[bool] = ...) -> None: ...
    class Updater(_message.Message):
        __slots__ = ("enable_notification",)
        ENABLE_NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
        enable_notification: bool
        def __init__(self, enable_notification: _Optional[bool] = ...) -> None: ...
    DIRECTORIES_FIELD_NUMBER: _ClassVar[int]
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    SKETCH_FIELD_NUMBER: _ClassVar[int]
    BUILD_CACHE_FIELD_NUMBER: _ClassVar[int]
    BOARD_MANAGER_FIELD_NUMBER: _ClassVar[int]
    DAEMON_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    LOGGING_FIELD_NUMBER: _ClassVar[int]
    LIBRARY_FIELD_NUMBER: _ClassVar[int]
    UPDATER_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    directories: Configuration.Directories
    network: Configuration.Network
    sketch: Configuration.Sketch
    build_cache: Configuration.BuildCache
    board_manager: Configuration.BoardManager
    daemon: Configuration.Daemon
    output: Configuration.Output
    logging: Configuration.Logging
    library: Configuration.Library
    updater: Configuration.Updater
    locale: str
    def __init__(self, directories: _Optional[_Union[Configuration.Directories, _Mapping]] = ..., network: _Optional[_Union[Configuration.Network, _Mapping]] = ..., sketch: _Optional[_Union[Configuration.Sketch, _Mapping]] = ..., build_cache: _Optional[_Union[Configuration.BuildCache, _Mapping]] = ..., board_manager: _Optional[_Union[Configuration.BoardManager, _Mapping]] = ..., daemon: _Optional[_Union[Configuration.Daemon, _Mapping]] = ..., output: _Optional[_Union[Configuration.Output, _Mapping]] = ..., logging: _Optional[_Union[Configuration.Logging, _Mapping]] = ..., library: _Optional[_Union[Configuration.Library, _Mapping]] = ..., updater: _Optional[_Union[Configuration.Updater, _Mapping]] = ..., locale: _Optional[str] = ...) -> None: ...

class ConfigurationGetRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("configuration",)
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    configuration: Configuration
    def __init__(self, configuration: _Optional[_Union[Configuration, _Mapping]] = ...) -> None: ...

class ConfigurationSaveRequest(_message.Message):
    __slots__ = ("settings_format",)
    SETTINGS_FORMAT_FIELD_NUMBER: _ClassVar[int]
    settings_format: str
    def __init__(self, settings_format: _Optional[str] = ...) -> None: ...

class ConfigurationSaveResponse(_message.Message):
    __slots__ = ("encoded_settings",)
    ENCODED_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    encoded_settings: str
    def __init__(self, encoded_settings: _Optional[str] = ...) -> None: ...

class ConfigurationOpenRequest(_message.Message):
    __slots__ = ("encoded_settings", "settings_format")
    ENCODED_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FORMAT_FIELD_NUMBER: _ClassVar[int]
    encoded_settings: str
    settings_format: str
    def __init__(self, encoded_settings: _Optional[str] = ..., settings_format: _Optional[str] = ...) -> None: ...

class ConfigurationOpenResponse(_message.Message):
    __slots__ = ("warnings",)
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, warnings: _Optional[_Iterable[str]] = ...) -> None: ...

class SettingsGetValueRequest(_message.Message):
    __slots__ = ("key", "value_format")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    key: str
    value_format: str
    def __init__(self, key: _Optional[str] = ..., value_format: _Optional[str] = ...) -> None: ...

class SettingsGetValueResponse(_message.Message):
    __slots__ = ("encoded_value",)
    ENCODED_VALUE_FIELD_NUMBER: _ClassVar[int]
    encoded_value: str
    def __init__(self, encoded_value: _Optional[str] = ...) -> None: ...

class SettingsSetValueRequest(_message.Message):
    __slots__ = ("key", "encoded_value", "value_format")
    KEY_FIELD_NUMBER: _ClassVar[int]
    ENCODED_VALUE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    key: str
    encoded_value: str
    value_format: str
    def __init__(self, key: _Optional[str] = ..., encoded_value: _Optional[str] = ..., value_format: _Optional[str] = ...) -> None: ...

class SettingsSetValueResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SettingsEnumerateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SettingsEnumerateResponse(_message.Message):
    __slots__ = ("entries",)
    class Entry(_message.Message):
        __slots__ = ("key", "type")
        KEY_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        key: str
        type: str
        def __init__(self, key: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[SettingsEnumerateResponse.Entry]
    def __init__(self, entries: _Optional[_Iterable[_Union[SettingsEnumerateResponse.Entry, _Mapping]]] = ...) -> None: ...
