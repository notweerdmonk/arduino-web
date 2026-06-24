"""Tests for board worker subprocess"""

import socket

import pytest

from board_manager.protocol import FrameReader


@pytest.fixture
def mock_socketpair():
    parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    yield parent, child
    parent.close()
    child.close()


class FakeClient:
    def __init__(self):
        self._connected = False
        self._inited = False
        self.boards = []
        self.compile_result = None
        self.upload_result = None

    def connect(self):
        self._connected = True

    def init(self):
        self._inited = True

    def list_boards(self, timeout=5):
        return self.boards

    def compile(self, sketch_path="", fqbn="", verbose=False):
        return self.compile_result

    def compile_stream(self, sketch_path="", fqbn="", verbose=False):
        if self.compile_result:
            out = self.compile_result.output or ""
            err = self.compile_result.error or ""
            yield out, err, True, 100.0

    def upload(self, sketch_path="", fqbn="", port="", verbose=False):
        return self.upload_result

    def upload_stream(self, sketch_path="", fqbn="", port="", verbose=False):
        if hasattr(self, "upload_error") and self.upload_error:
            raise self.upload_error
        if self.upload_result:
            out = self.upload_result.output or ""
            err = self.upload_result.error or ""
            yield out, err, True

    def compile_and_upload(self, sketch_path="", fqbn="", port="", verbose=False):
        return (self.compile_result, self.upload_result)


class TestHandleMessage:
    def test_ping(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            import board_manager.board_worker as bw

            client = FakeClient()
            msg = {"id": "r1", "body": {"method": "ping"}, "reply_to": "resp:r1"}
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            data = parent.recv(4096)
            reader.feed(data)
            response = reader.read_one()

            assert response["status"] == "ok"
            assert response["data"]["pong"] is True
        finally:
            parent.close()
            child.close()

    def test_unknown_method(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            import board_manager.board_worker as bw

            client = FakeClient()
            msg = {"id": "r1", "body": {"method": "nonexistent"}, "reply_to": "resp:r1"}
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            data = parent.recv(4096)
            reader.feed(data)
            response = reader.read_one()

            assert response["type"] == "error"
            assert response["code"] == "unknown_method"
        finally:
            parent.close()
            child.close()

    def test_init(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            import board_manager.board_worker as bw

            client = FakeClient()
            msg = {"id": "r1", "body": {"method": "init"}, "reply_to": "resp:r1"}
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            data = parent.recv(4096)
            reader.feed(data)
            response = reader.read_one()

            assert response["status"] == "ok"
            assert client._inited
        finally:
            parent.close()
            child.close()

    def test_list_boards_with_mocked_data(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            from unittest.mock import MagicMock
            import board_manager.board_worker as bw

            client = FakeClient()

            mock_board = MagicMock()
            mock_board.port.address = "/dev/ttyACM0"
            mock_board.fqbn = "arduino:avr:uno"
            mock_board.name = "Arduino Uno"
            client.boards = [mock_board]

            msg = {
                "id": "r1",
                "body": {"method": "list_boards", "params": {"timeout": 3}},
                "reply_to": "resp:r1",
            }
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            data = parent.recv(4096)
            reader.feed(data)
            response = reader.read_one()

            assert response["status"] == "ok"
            assert len(response["data"]) == 1
            assert response["data"][0]["port"] == "/dev/ttyACM0"
        finally:
            parent.close()
            child.close()

    def test_compile_success(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            from unittest.mock import MagicMock
            import board_manager.board_worker as bw

            client = FakeClient()

            mock_result = MagicMock()
            mock_result.success = True
            mock_result.output = "Compilation successful"
            mock_result.error = ""
            mock_result.sketch_path = "/tmp/sketch"
            client.compile_result = mock_result

            msg = {
                "id": "r1",
                "body": {
                    "method": "compile",
                    "params": {"sketch_path": "/tmp/sketch", "fqbn": "arduino:avr:uno"},
                },
                "reply_to": "resp:r1",
            }
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            data = parent.recv(4096)
            reader.feed(data)
            # Read all messages — progress first, then result
            msgs = []
            while True:
                m = reader.read_one()
                if m is None:
                    break
                msgs.append(m)

            assert len(msgs) >= 1
            result = [m for m in msgs if m.get("type") == "result"][0]
            assert result["status"] == "ok"
            assert result["data"]["success"] is True
            assert result["data"]["output"] == "Compilation successful"
            # Should also have a progress message
            progress = [
                m
                for m in msgs
                if m.get("type") == "event"
                and m.get("topic", "").endswith("::progress")
            ]
            assert len(progress) >= 1
        finally:
            parent.close()
            child.close()

    def test_upload_success(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            from unittest.mock import MagicMock
            import board_manager.board_worker as bw

            client = FakeClient()

            mock_result = MagicMock()
            mock_result.success = True
            mock_result.output = "Upload successful"
            mock_result.error = ""
            client.upload_result = mock_result

            msg = {
                "id": "r1",
                "body": {
                    "method": "upload",
                    "params": {
                        "sketch_path": "/tmp/sketch",
                        "fqbn": "arduino:avr:uno",
                        "port": "/dev/ttyACM0",
                    },
                },
                "reply_to": "resp:r1",
            }
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            data = parent.recv(4096)
            reader.feed(data)
            msgs = []
            while True:
                m = reader.read_one()
                if m is None:
                    break
                msgs.append(m)

            assert len(msgs) >= 1
            result = [m for m in msgs if m.get("type") == "result"][0]
            assert result["status"] == "ok"
            assert result["data"]["success"] is True
            assert result["data"]["output"] == "Upload successful"
            progress = [
                m
                for m in msgs
                if m.get("type") == "event"
                and m.get("topic", "").endswith("::progress")
            ]
            assert len(progress) >= 1
        finally:
            parent.close()
            child.close()

    def test_upload_failure_sends_error_dict_with_status(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            from arduino_grpc.exceptions import UploadError
            import board_manager.board_worker as bw

            client = FakeClient()
            client.upload_error = UploadError(
                "Wrong port or board not in bootloader mode"
            )

            msg = {
                "id": "r1",
                "body": {
                    "method": "upload",
                    "params": {
                        "sketch_path": "/tmp/sketch",
                        "fqbn": "arduino:avr:uno",
                        "port": "/dev/ttyACM0",
                    },
                },
                "reply_to": "resp:r1",
            }
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            raw = parent.recv(4096)
            reader.feed(raw)
            msgs = []
            while True:
                m = reader.read_one()
                if m is None:
                    break
                msgs.append(m)

            # First messages are progress (starting upload...), then the error
            progress = [
                m
                for m in msgs
                if m.get("type") == "event"
                and m.get("topic", "").endswith("::progress")
            ]
            assert len(progress) >= 3
            assert any(
                "Starting upload to" in m.get("data", {}).get("output", "")
                for m in progress
            )
            assert any(
                "Upload failed" in m.get("data", {}).get("error", "") for m in progress
            )

            error = [m for m in msgs if m.get("type") == "error"][-1]
            assert error["status"] == "error"
            assert error["code"] == "upload_failed"
            assert "Wrong port" in error["message"]
            assert error["data"]["code"] == "upload_failed"
            assert "Wrong port" in error["data"]["message"]
        finally:
            parent.close()
            child.close()

    def test_compile_and_upload(self):
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            from unittest.mock import MagicMock
            import board_manager.board_worker as bw

            client = FakeClient()

            mock_c = MagicMock()
            mock_c.success = True
            mock_c.output = "Compiled"
            mock_c.error = ""
            mock_c.sketch_path = "/tmp/sketch"

            mock_u = MagicMock()
            mock_u.success = True
            mock_u.output = "Uploaded"
            mock_u.error = ""

            client.compile_result = mock_c
            client.upload_result = mock_u

            msg = {
                "id": "r1",
                "body": {
                    "method": "compile_and_upload",
                    "params": {
                        "sketch_path": "/tmp/sketch",
                        "fqbn": "arduino:avr:uno",
                        "port": "/dev/ttyACM0",
                    },
                },
                "reply_to": "resp:r1",
            }
            bw._handle_message(msg, client, child)

            reader = FrameReader("newline")
            data = parent.recv(4096)
            reader.feed(data)
            response = reader.read_one()

            assert response["status"] == "ok"
            assert response["data"]["compile"]["success"] is True
            assert response["data"]["upload"]["success"] is True
        finally:
            parent.close()
            child.close()
