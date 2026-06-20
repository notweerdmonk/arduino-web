"""JSON-line and length-prefixed framing protocol"""

import json
import struct
from enum import Enum, IntEnum
from typing import Any, Optional


class Handshake(Enum):
    """Handshake byte values for protocol detection."""

    NEWLINE = b"\x01"
    LENGTH = b"\x02"


class Framing(IntEnum):
    """Constants for length-prefixed framing."""

    HEADER_LENGTH = 4


class FramingMode(str, Enum):
    """Supported framing modes for the protocol."""
    NEWLINE = "newline"
    LENGTH = "length"


def encode_message(msg: dict) -> bytes:
    """Encode a dict as compact JSON bytes."""
    return json.dumps(msg, separators=(",", ":")).encode("utf-8")


def decode_frame(data: bytes) -> dict:
    """Decode JSON bytes to a dict."""
    return json.loads(data.decode("utf-8"))


def frame_newline(payload: bytes) -> bytes:
    """Frame a payload with a trailing newline."""
    return payload + b"\n"


def frame_length(payload: bytes) -> bytes:
    """Frame a payload with a 4-byte big-endian length prefix."""
    return struct.pack("!I", len(payload)) + payload


class FrameReader:
    """Reads framed messages from a stream (newline or length-prefixed)"""

    def __init__(self, mode: str = FramingMode.NEWLINE):
        """Initialize the frame reader.

        Args:
            mode: ``"newline"`` or ``"length"`` framing mode.

        Raises:
            ValueError: If mode is unknown.
        """
        if mode not in (FramingMode.NEWLINE, FramingMode.LENGTH):
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode
        self._buf = bytearray()

    def feed(self, data: bytes) -> None:
        """Feed raw bytes into the reader buffer."""
        self._buf.extend(data)

    def read_one(self) -> Optional[dict]:
        """Read and decode one framed message from the buffer.

        Returns:
            The decoded dict, or None if no complete frame is available.
        """
        if self.mode == "newline":
            return self._read_newline()
        return self._read_length()

    def _read_newline(self) -> Optional[dict]:
        """Read one newline-terminated frame from the buffer."""
        idx = self._buf.find(b"\n")
        if idx == -1:
            return None
        line = bytes(self._buf[:idx])
        del self._buf[: idx + 1]
        return decode_frame(line) if line else None

    def _read_length(self) -> Optional[dict]:
        """Read one length-prefixed frame from the buffer."""
        if len(self._buf) < Framing.HEADER_LENGTH:
            return None
        length = struct.unpack("!I", self._buf[:Framing.HEADER_LENGTH])[0]
        needed = Framing.HEADER_LENGTH + length
        if len(self._buf) < needed:
            return None
        payload = bytes(self._buf[Framing.HEADER_LENGTH:needed])
        del self._buf[:needed]
        return decode_frame(payload)

    def clear(self) -> None:
        """Clear the internal read buffer."""
        self._buf.clear()

    @property
    def buffered_bytes(self) -> int:
        """Return the number of bytes currently buffered."""
        return len(self._buf)


def detect_mode_from_handshake(data: bytes) -> Optional[str]:
    """Detect the framing mode from the first byte of a handshake.

    Args:
        data: The first byte(s) received from the client.

    Returns:
        ``"newline"``, ``"length"``, or None if undetermined.
    """
    if not data:
        return None
    if data[0:1] == Handshake.NEWLINE.value:
        return FramingMode.NEWLINE
    if data[0:1] == Handshake.LENGTH.value:
        return FramingMode.LENGTH
    return None


def encode_and_frame(msg: dict, mode: str = FramingMode.NEWLINE) -> bytes:
    """Encode a message dict and frame it for transmission.

    Args:
        msg: The message dict.
        mode: Framing mode — ``"newline"`` or ``"length"``.

    Returns:
        The framed bytes ready for sending.
    """
    payload = encode_message(msg)
    if mode == FramingMode.LENGTH:
        return frame_length(payload)
    return frame_newline(payload)
