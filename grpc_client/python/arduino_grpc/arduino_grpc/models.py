"""grpc_client/python/arduino_grpc/arduino_grpc/models.py

Data models for Arduino gRPC client

Author: notweerdmonk
SPDX-License-Identifier: Apache-2.0

Copyright 2026 notweerdmonk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class Port:
    """Represents a port where an Arduino board is connected"""

    address: str
    protocol: str = "serial"
    protocol_label: str = ""
    label: str = ""
    properties: Optional[Dict[str, str]] = None
    hardware_id: str = ""

    def to_proto(self, port_pb2):
        """Convert to protobuf Port object"""
        return port_pb2.Port(
            address=self.address,
            protocol=self.protocol,
            protocol_label=self.protocol_label,
            label=self.label,
            properties=self.properties or {},
            hardware_id=self.hardware_id,
        )


@dataclass
class Board:
    """Represents a detected Arduino board"""

    port: Port
    fqbn: str
    name: str
    detected: bool = True

    @classmethod
    def from_proto(cls, board_proto, port_proto):
        """Create Board from protobuf response"""
        port = Port(
            address=port_proto.address,
            protocol=port_proto.protocol,
            protocol_label=port_proto.protocol_label,
            label=port_proto.label,
            properties=dict(port_proto.properties) if port_proto.properties else None,
            hardware_id=port_proto.hardware_id,
        )
        return cls(
            port=port,
            fqbn=board_proto.fqbn,
            name=board_proto.name,
            detected=getattr(board_proto, "detected", True),
        )


@dataclass
class CompileResult:
    """Result of sketch compilation"""

    success: bool
    output: str = ""
    error: str = ""
    sketch_path: str = ""

    @classmethod
    def from_proto(cls, proto, sketch_path: str = ""):
        """Create CompileResult from a protobuf CompileResponse.

        Args:
            proto: A CompileResponse protobuf message.
            sketch_path: The sketch path for reference.

        Returns:
            A CompileResult instance.
        """
        return cls(
            success=proto.result is not None,
            output=proto.out_stream.decode() if proto.out_stream else "",
            error=proto.err_stream.decode() if proto.err_stream else "",
            sketch_path=sketch_path,
        )


@dataclass
class UploadResult:
    """Result of sketch upload"""

    success: bool
    output: str = ""
    error: str = ""

    @classmethod
    def from_proto(cls, proto):
        """Create UploadResult from a protobuf UploadResponse.

        Args:
            proto: An UploadResponse protobuf message.

        Returns:
            An UploadResult instance.
        """
        return cls(
            success=proto.result is not None,
            output=proto.out_stream.decode() if proto.out_stream else "",
            error=proto.err_stream.decode() if proto.err_stream else "",
        )

