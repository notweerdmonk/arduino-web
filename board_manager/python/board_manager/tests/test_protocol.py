"""Tests for protocol framing"""

import json
import struct
import pytest

from board_manager.protocol import (
    FrameReader,
    Handshake,
    encode_and_frame,
    decode_frame,
    detect_mode_from_handshake,
)


class TestFrameReaderNewline:
    def test_read_single_message(self):
        reader = FrameReader("newline")
        msg = {"type": "ping"}
        reader.feed(encode_and_frame(msg, "newline"))
        result = reader.read_one()
        assert result == msg

    def test_read_multiple_messages(self):
        reader = FrameReader("newline")
        reader.feed(
            encode_and_frame({"a": 1}, "newline")
            + encode_and_frame({"b": 2}, "newline")
        )
        assert reader.read_one() == {"a": 1}
        assert reader.read_one() == {"b": 2}

    def test_partial_frame_returns_none(self):
        reader = FrameReader("newline")
        reader.feed(b'{"type": "ping"}')
        assert reader.read_one() is None

    def test_empty_frame_skipped(self):
        reader = FrameReader("newline")
        reader.feed(b"\n")
        assert reader.read_one() is None

    def test_extra_data_after_newline(self):
        reader = FrameReader("newline")
        reader.feed(b'{"a":1}\n{"b":2}')
        assert reader.read_one() == {"a": 1}
        assert reader.read_one() is None

    def test_clear_buf(self):
        reader = FrameReader("newline")
        reader.feed(b'{"a":1}\n')
        reader.clear()
        assert reader.read_one() is None


class TestFrameReaderLength:
    def test_read_single_message(self):
        reader = FrameReader("length")
        payload = json.dumps({"type": "ping"}, separators=(",", ":")).encode()
        framed = struct.pack("!I", len(payload)) + payload
        reader.feed(framed)
        result = reader.read_one()
        assert result == {"type": "ping"}

    def test_read_multiple_messages(self):
        reader = FrameReader("length")
        data = b""
        for m in ({"a": 1}, {"b": 2}):
            payload = json.dumps(m, separators=(",", ":")).encode()
            data += struct.pack("!I", len(payload)) + payload
        reader.feed(data)
        assert reader.read_one() == {"a": 1}
        assert reader.read_one() == {"b": 2}

    def test_partial_header_returns_none(self):
        reader = FrameReader("length")
        reader.feed(b"\x00\x00")
        assert reader.read_one() is None

    def test_partial_body_returns_none(self):
        reader = FrameReader("length")
        payload = json.dumps({"x": 1}, separators=(",", ":")).encode()
        framed = struct.pack("!I", len(payload)) + payload
        reader.feed(framed[:3])
        assert reader.read_one() is None

    def test_clear_buf(self):
        reader = FrameReader("length")
        payload = json.dumps({"a": 1}, separators=(",", ":")).encode()
        framed = struct.pack("!I", len(payload)) + payload
        reader.feed(framed)
        reader.clear()
        assert reader.read_one() is None


class TestEncodeAndFrame:
    def test_newline_mode(self):
        result = encode_and_frame({"a": 1}, "newline")
        assert result.endswith(b"\n")
        assert decode_frame(result.rstrip(b"\n")) == {"a": 1}

    def test_length_mode(self):
        result = encode_and_frame({"a": 1}, "length")
        length = struct.unpack("!I", result[:4])[0]
        assert length == len(result) - 4
        assert decode_frame(result[4:]) == {"a": 1}

    def test_default_newline(self):
        result = encode_and_frame({"a": 1})
        assert result.endswith(b"\n")


class TestDetectMode:
    def test_newline_handshake(self):
        assert detect_mode_from_handshake(Handshake.NEWLINE.value) == "newline"

    def test_length_handshake(self):
        assert detect_mode_from_handshake(Handshake.LENGTH.value) == "length"

    def test_empty_data(self):
        assert detect_mode_from_handshake(b"") is None

    def test_invalid_handshake(self):
        assert detect_mode_from_handshake(b"\x03") is None


class TestFrameReaderInvalidMode:
    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown mode"):
            FrameReader("invalid")

    def test_buffered_bytes_property(self):
        reader = FrameReader("newline")
        assert reader.buffered_bytes == 0
        reader.feed(b"hello")
        assert reader.buffered_bytes == 5
