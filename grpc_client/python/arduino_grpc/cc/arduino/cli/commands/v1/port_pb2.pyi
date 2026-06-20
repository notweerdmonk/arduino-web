from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Port(_message.Message):
    __slots__ = ("address", "label", "protocol", "protocol_label", "properties", "hardware_id")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_LABEL_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_ID_FIELD_NUMBER: _ClassVar[int]
    address: str
    label: str
    protocol: str
    protocol_label: str
    properties: _containers.ScalarMap[str, str]
    hardware_id: str
    def __init__(self, address: _Optional[str] = ..., label: _Optional[str] = ..., protocol: _Optional[str] = ..., protocol_label: _Optional[str] = ..., properties: _Optional[_Mapping[str, str]] = ..., hardware_id: _Optional[str] = ...) -> None: ...
