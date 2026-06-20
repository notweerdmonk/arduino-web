from cc.arduino.cli.commands.v1 import common_pb2 as _common_pb2
from cc.arduino.cli.commands.v1 import port_pb2 as _port_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MonitorRequest(_message.Message):
    __slots__ = ("open_request", "tx_data", "updated_configuration", "close")
    OPEN_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TX_DATA_FIELD_NUMBER: _ClassVar[int]
    UPDATED_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    open_request: MonitorPortOpenRequest
    tx_data: bytes
    updated_configuration: _common_pb2.MonitorPortConfiguration
    close: bool
    def __init__(self, open_request: _Optional[_Union[MonitorPortOpenRequest, _Mapping]] = ..., tx_data: _Optional[bytes] = ..., updated_configuration: _Optional[_Union[_common_pb2.MonitorPortConfiguration, _Mapping]] = ..., close: _Optional[bool] = ...) -> None: ...

class MonitorPortOpenRequest(_message.Message):
    __slots__ = ("instance", "port", "fqbn", "port_configuration")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    PORT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    port: _port_pb2.Port
    fqbn: str
    port_configuration: _common_pb2.MonitorPortConfiguration
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., port: _Optional[_Union[_port_pb2.Port, _Mapping]] = ..., fqbn: _Optional[str] = ..., port_configuration: _Optional[_Union[_common_pb2.MonitorPortConfiguration, _Mapping]] = ...) -> None: ...

class MonitorResponse(_message.Message):
    __slots__ = ("error", "rx_data", "applied_settings", "success")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RX_DATA_FIELD_NUMBER: _ClassVar[int]
    APPLIED_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: str
    rx_data: bytes
    applied_settings: _common_pb2.MonitorPortConfiguration
    success: bool
    def __init__(self, error: _Optional[str] = ..., rx_data: _Optional[bytes] = ..., applied_settings: _Optional[_Union[_common_pb2.MonitorPortConfiguration, _Mapping]] = ..., success: _Optional[bool] = ...) -> None: ...

class EnumerateMonitorPortSettingsRequest(_message.Message):
    __slots__ = ("instance", "port_protocol", "fqbn")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PORT_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    FQBN_FIELD_NUMBER: _ClassVar[int]
    instance: _common_pb2.Instance
    port_protocol: str
    fqbn: str
    def __init__(self, instance: _Optional[_Union[_common_pb2.Instance, _Mapping]] = ..., port_protocol: _Optional[str] = ..., fqbn: _Optional[str] = ...) -> None: ...

class EnumerateMonitorPortSettingsResponse(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _containers.RepeatedCompositeFieldContainer[MonitorPortSettingDescriptor]
    def __init__(self, settings: _Optional[_Iterable[_Union[MonitorPortSettingDescriptor, _Mapping]]] = ...) -> None: ...

class MonitorPortSettingDescriptor(_message.Message):
    __slots__ = ("setting_id", "label", "type", "enum_values", "value")
    SETTING_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    setting_id: str
    label: str
    type: str
    enum_values: _containers.RepeatedScalarFieldContainer[str]
    value: str
    def __init__(self, setting_id: _Optional[str] = ..., label: _Optional[str] = ..., type: _Optional[str] = ..., enum_values: _Optional[_Iterable[str]] = ..., value: _Optional[str] = ...) -> None: ...
