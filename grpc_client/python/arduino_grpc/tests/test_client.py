"""grpc_client/python/arduino_grpc/tests/test_client.py

Tests for client module.

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

import unittest
from unittest.mock import MagicMock, patch
import grpc

from cc.arduino.cli.commands.v1 import common_pb2 as common_pb2
from cc.arduino.cli.commands.v1 import port_pb2 as port_pb2
from cc.arduino.cli.commands.v1 import board_pb2 as board_pb2
from cc.arduino.cli.commands.v1 import compile_pb2 as compile_pb2
from cc.arduino.cli.commands.v1 import upload_pb2 as upload_pb2

from arduino_grpc.client import ArduinoGrpcClient
from arduino_grpc.models import CompileResult, UploadResult
from arduino_grpc import exceptions


class TestArduinoGrpcClientInit(unittest.TestCase):
    def test_default_daemon(self):
        client = ArduinoGrpcClient()
        self.assertEqual(client.daemon, ArduinoGrpcClient.DEFAULT_DAEMON)
        self.assertIsNone(client.channel)
        self.assertIsNone(client.stub)

    def test_custom_daemon(self):
        client = ArduinoGrpcClient("192.168.1.100:50051")
        self.assertEqual(client.daemon, "192.168.1.100:50051")


class TestArduinoGrpcClientConnect(unittest.TestCase):
    @patch("arduino_grpc.client.grpc.insecure_channel")
    def test_connect_success(self, mock_channel):
        mock_channel.return_value = MagicMock()
        client = ArduinoGrpcClient()
        client.connect()
        mock_channel.assert_called_once_with("localhost:50051")
        self.assertIsNotNone(client.channel)
        self.assertIsNotNone(client.stub)

    @patch("arduino_grpc.client.grpc.insecure_channel")
    def test_connect_failure(self, mock_channel):
        mock_channel.side_effect = Exception("Connection refused")
        client = ArduinoGrpcClient()
        with self.assertRaises(exceptions.ConnectionError):
            client.connect()

    def test_disconnect(self):
        client = ArduinoGrpcClient()
        mock_channel = MagicMock()
        client.channel = mock_channel
        mock_stub = MagicMock()
        client.stub = mock_stub
        client._instance = common_pb2.Instance(id=7)

        client.disconnect()

        mock_stub.Destroy.assert_called_once()
        mock_channel.close.assert_called_once()
        self.assertIsNone(client.channel)
        self.assertIsNone(client.stub)
        self.assertIsNone(client._instance)


class TestArduinoGrpcClientInitInstance(unittest.TestCase):
    def setUp(self):
        self.client = ArduinoGrpcClient()
        self.client.stub = MagicMock()

    def test_init_success(self):
        mock_instance = common_pb2.Instance(id=1)

        mock_create_resp = MagicMock()
        mock_create_resp.instance = mock_instance

        self.client.stub.Create.return_value = mock_create_resp
        self.client.stub.Init.return_value = iter([])

        result = self.client.init()

        self.assertEqual(result.id, 1)
        self.assertEqual(self.client._instance.id, 1)
        self.client.stub.Create.assert_called_once()
        self.client.stub.Init.assert_called_once()

    def test_init_with_sketch_path(self):
        mock_instance = common_pb2.Instance(id=1)

        mock_create_resp = MagicMock()
        mock_create_resp.instance = mock_instance

        self.client.stub.Create.return_value = mock_create_resp
        self.client.stub.Init.return_value = iter([])

        result = self.client.init(sketch_path="/path/to/sketch")

        self.assertEqual(result.id, 1)

        init_args = self.client.stub.Init.call_args[0][0]
        self.assertEqual(init_args.sketch_path, "/path/to/sketch")

    def test_init_rpc_error(self):
        mock_create_resp = MagicMock()
        mock_create_resp.instance = common_pb2.Instance(id=1)

        self.client.stub.Create.return_value = mock_create_resp
        self.client.stub.Init.side_effect = grpc.RpcError()
        self.client.stub.Init.side_effect._code = lambda: grpc.StatusCode.INTERNAL
        self.client.stub.Init.side_effect.details = lambda: "Internal error"

        with self.assertRaises(exceptions.InitializationError):
            self.client.init()

    def test_instance_property_auto_init(self):
        mock_instance = common_pb2.Instance(id=1)
        mock_create_resp = MagicMock()
        mock_create_resp.instance = mock_instance

        self.client.stub.Create.return_value = mock_create_resp
        self.client.stub.Init.return_value = iter([])

        self.assertEqual(self.client.instance.id, 1)

    def test_init_not_connected(self):
        client = ArduinoGrpcClient()
        with self.assertRaises(exceptions.ConnectionError):
            client.init()


class TestArduinoGrpcClientListBoards(unittest.TestCase):
    def setUp(self):
        self.client = ArduinoGrpcClient()
        self.client._instance = common_pb2.Instance(id=1)
        self.client.stub = MagicMock()

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_list_boards_success(self, mock_ensure_connected):
        mock_port = MagicMock()
        mock_port.address = "/dev/ttyUSB0"
        mock_port.protocol = "serial"
        mock_port.protocol_label = "Serial"
        mock_port.label = "USB Serial"

        mock_mb = MagicMock()
        mock_mb.fqbn = "arduino:avr:uno"
        mock_mb.name = "Arduino Uno"

        mock_dp = MagicMock()
        mock_dp.port = mock_port
        mock_dp.matching_boards = [mock_mb]

        mock_response = MagicMock()
        mock_response.ports = [mock_dp]

        self.client.stub.BoardList.return_value = mock_response

        boards = self.client.list_boards()

        self.assertEqual(len(boards), 1)
        self.assertEqual(boards[0].fqbn, "arduino:avr:uno")
        self.assertEqual(boards[0].name, "Arduino Uno")
        self.assertEqual(boards[0].port.address, "/dev/ttyUSB0")

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_list_boards_empty(self, mock_ensure_connected):
        mock_response = MagicMock()
        mock_response.ports = []

        self.client.stub.BoardList.return_value = mock_response

        boards = self.client.list_boards()
        self.assertEqual(len(boards), 0)


class TestArduinoGrpcClientListAllBoards(unittest.TestCase):
    def setUp(self):
        self.client = ArduinoGrpcClient()
        self.client._instance = common_pb2.Instance(id=1)
        self.client.stub = MagicMock()

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_list_all_boards(self, mock_ensure_connected):
        mock_b1 = MagicMock()
        mock_b1.fqbn = "arduino:avr:uno"
        mock_b1.name = "Arduino Uno"
        mock_b2 = MagicMock()
        mock_b2.fqbn = "arduino:avr:nano"
        mock_b2.name = "Arduino Nano"

        mock_response = MagicMock()
        mock_response.boards = [mock_b1, mock_b2]

        self.client.stub.BoardListAll.return_value = mock_response

        boards = self.client.list_all_boards()

        self.assertEqual(len(boards), 2)
        self.assertEqual(boards[0].fqbn, "arduino:avr:uno")


class TestArduinoGrpcClientWatchBoards(unittest.TestCase):
    def setUp(self):
        self.client = ArduinoGrpcClient()
        self.client._instance = common_pb2.Instance(id=1)
        self.client.stub = MagicMock()

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_watch_boards_streaming(self, mock_ensure_connected):
        mock_response = MagicMock()
        mock_response.error = ""
        mock_response.event_type = "add"
        mock_response.port.matching_boards = []
        mock_response.port.port.address = "/dev/ttyUSB0"
        mock_response.port.port.protocol = "serial"
        mock_response.port.port.protocol_label = "Serial"
        mock_response.port.port.label = "USB"

        mock_response.HasField = lambda f: f == "port"

        self.client.stub.BoardListWatch.return_value = iter([mock_response])

        boards = list(self.client.watch_boards())

        self.assertEqual(len(boards), 1)
        self.assertTrue(boards[0].detected)
        self.assertEqual(boards[0].port.address, "/dev/ttyUSB0")

        self.client.stub.BoardListWatch.assert_called_once()


class TestArduinoGrpcClientCompile(unittest.TestCase):
    def setUp(self):
        self.client = ArduinoGrpcClient()
        self.client._instance = common_pb2.Instance(id=1)
        self.client.stub = MagicMock()

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_compile_success(self, mock_ensure_connected):
        mock_progress = MagicMock()
        mock_progress.message = "Compiling..."
        mock_progress.percent = 100.0

        mock_result = MagicMock()
        mock_result.HasField = lambda f: f in ("out_stream", "progress", "result")
        mock_result.out_stream = b"Done compiling\n"
        mock_result.err_stream = b""
        mock_result.progress = mock_progress
        mock_result.result = MagicMock()

        self.client.stub.Compile.return_value = iter([mock_result])

        result = self.client.compile("/path/to/sketch", "arduino:avr:uno")

        self.assertIsInstance(result, CompileResult)
        self.assertTrue(result.success)
        self.assertIn("Done compiling", result.output)

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_compile_missing_fqbn(self, mock_ensure_connected):
        with self.assertRaises(exceptions.InvalidFqbnError):
            self.client.compile("/path/to/sketch", "")

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_compile_stream_yields_chunks(self, mock_ensure_connected):
        chunk1 = MagicMock()
        chunk1.HasField = lambda f: f in ("out_stream", "progress")
        chunk1.out_stream = b"Compiling foo.c...\n"
        chunk1.err_stream = b""
        chunk1.result = None
        chunk1.progress.percent = 25.0

        chunk2 = MagicMock()
        chunk2.HasField = lambda f: f in ("out_stream", "result")
        chunk2.out_stream = b"Done.\n"
        chunk2.err_stream = b""
        chunk2.result = MagicMock()

        self.client.stub.Compile.return_value = iter([chunk1, chunk2])

        results = list(self.client.compile_stream("/path/to/sketch", "arduino:avr:uno"))

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "Compiling foo.c...\n")
        self.assertFalse(results[0][2])
        self.assertAlmostEqual(results[0][3], 25.0)
        self.assertEqual(results[1][0], "Done.\n")
        self.assertTrue(results[1][2])
        self.assertAlmostEqual(results[1][3], 100.0)

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_compile_stream_missing_fqbn(self, mock_ensure_connected):
        stream = self.client.compile_stream("/path/to/sketch", "")
        with self.assertRaises(exceptions.InvalidFqbnError):
            next(stream)


class TestArduinoGrpcClientUpload(unittest.TestCase):
    def setUp(self):
        self.client = ArduinoGrpcClient()
        self.client._instance = common_pb2.Instance(id=1)
        self.client.stub = MagicMock()

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_upload_with_port_object(self, mock_ensure_connected):
        mock_result = MagicMock()
        mock_result.HasField = lambda f: f in ("out_stream", "result")
        mock_result.out_stream = b"Uploading...\nDone uploading"
        mock_result.err_stream = b""
        mock_result.result = MagicMock()

        self.client.stub.Upload.return_value = iter([mock_result])

        result = self.client.upload(
            "/path/to/sketch", "arduino:avr:uno", "/dev/ttyUSB0"
        )

        self.assertIsInstance(result, UploadResult)
        self.assertTrue(result.success)

        call_args = self.client.stub.Upload.call_args[0][0]
        self.assertIsInstance(call_args.port, port_pb2.Port)
        self.assertEqual(call_args.port.address, "/dev/ttyUSB0")
        self.assertEqual(call_args.port.protocol, "serial")

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_upload_missing_port(self, mock_ensure_connected):
        with self.assertRaises(exceptions.InvalidPortError):
            self.client.upload("/path/to/sketch", "arduino:avr:uno", "")

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_upload_missing_fqbn(self, mock_ensure_connected):
        with self.assertRaises(exceptions.InvalidFqbnError):
            self.client.upload("/path/to/sketch", "", "/dev/ttyUSB0")

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_upload_stream_yields_chunks(self, mock_ensure_connected):
        chunk1 = MagicMock()
        chunk1.HasField = lambda f: f in ("out_stream",)
        chunk1.out_stream = b"Uploading...\n"
        chunk1.err_stream = b""
        chunk1.result = None

        chunk2 = MagicMock()
        chunk2.HasField = lambda f: f in ("out_stream", "result")
        chunk2.out_stream = b"Done.\n"
        chunk2.err_stream = b""
        chunk2.result = MagicMock()

        self.client.stub.Upload.return_value = iter([chunk1, chunk2])

        results = list(
            self.client.upload_stream(
                "/path/to/sketch", "arduino:avr:uno", "/dev/ttyUSB0"
            )
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "Uploading...\n")
        self.assertFalse(results[0][2])
        self.assertEqual(results[1][0], "Done.\n")
        self.assertTrue(results[1][2])

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_upload_stream_missing_port(self, mock_ensure_connected):
        stream = self.client.upload_stream("/path/to/sketch", "arduino:avr:uno", "")
        with self.assertRaises(exceptions.InvalidPortError):
            next(stream)

    @patch.object(ArduinoGrpcClient, "_ensure_connected")
    def test_upload_stream_missing_fqbn(self, mock_ensure_connected):
        stream = self.client.upload_stream("/path/to/sketch", "", "/dev/ttyUSB0")
        with self.assertRaises(exceptions.InvalidFqbnError):
            next(stream)


class TestArduinoGrpcClientCompileAndUpload(unittest.TestCase):
    def setUp(self):
        self.client = ArduinoGrpcClient()
        self.client._instance = common_pb2.Instance(id=1)
        self.client.stub = MagicMock()

    @patch.object(ArduinoGrpcClient, "compile")
    @patch.object(ArduinoGrpcClient, "upload")
    def test_compile_and_upload_success(self, mock_upload, mock_compile):
        compile_result = CompileResult(success=True)
        upload_result = UploadResult(success=True)

        mock_compile.return_value = compile_result
        mock_upload.return_value = upload_result

        c_result, u_result = self.client.compile_and_upload(
            "/path/to/sketch", "arduino:avr:uno", "/dev/ttyUSB0"
        )

        self.assertTrue(c_result.success)
        self.assertTrue(u_result.success)

    @patch.object(ArduinoGrpcClient, "compile")
    @patch.object(ArduinoGrpcClient, "upload")
    def test_compile_and_upload_compile_fails(self, mock_upload, mock_compile):
        compile_result = CompileResult(success=False, error="Compile failed")
        mock_compile.return_value = compile_result

        c_result, u_result = self.client.compile_and_upload(
            "/path/to/sketch", "arduino:avr:uno", "/dev/ttyUSB0"
        )

        self.assertFalse(c_result.success)
        self.assertFalse(u_result.success)
        mock_upload.assert_not_called()


class TestContextManager(unittest.TestCase):
    @patch("arduino_grpc.client.grpc.insecure_channel")
    def test_context_manager(self, mock_channel):
        mock_channel.return_value = MagicMock()

        with ArduinoGrpcClient() as client:
            self.assertIsNotNone(client.channel)

        mock_channel.return_value.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()

