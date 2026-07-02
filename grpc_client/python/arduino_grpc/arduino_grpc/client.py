"""grpc_client/python/arduino_grpc/arduino_grpc/client.py

Core gRPC client for Arduino CLI

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

import grpc
from typing import Optional, List, Iterator, Callable

from cc.arduino.cli.commands.v1 import commands_pb2 as rpc_pb2
from cc.arduino.cli.commands.v1 import commands_pb2_grpc as rpc_pb2_grpc
from cc.arduino.cli.commands.v1 import common_pb2 as common_pb2
from cc.arduino.cli.commands.v1 import port_pb2 as port_pb2
from cc.arduino.cli.commands.v1 import board_pb2 as board_pb2
from cc.arduino.cli.commands.v1 import compile_pb2 as compile_pb2
from cc.arduino.cli.commands.v1 import upload_pb2 as upload_pb2

from arduino_grpc import exceptions
from arduino_grpc.models import Port, Board, CompileResult, UploadResult


class ArduinoGrpcClient:
    """Client for Arduino CLI gRPC service"""

    DEFAULT_DAEMON = "localhost:50051"

    def __init__(self, daemon: str = DEFAULT_DAEMON):
        """Initialize the client.

        Args:
            daemon: Host:port of the arduino-cli daemon (default: localhost:50051).
        """
        self.daemon = daemon
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[rpc_pb2_grpc.ArduinoCoreServiceStub] = None
        self._instance: Optional[common_pb2.Instance] = None

    def connect(self) -> None:
        """Connect to the arduino-cli daemon.

        Creates an insecure gRPC channel to the configured daemon address.
        The channel is reused until disconnect() is called.

        Raises:
            ConnectionError: If the daemon is unreachable or connection fails.
        """
        try:
            self.channel = grpc.insecure_channel(self.daemon)
            self.stub = rpc_pb2_grpc.ArduinoCoreServiceStub(self.channel)
        except Exception as e:
            raise exceptions.ConnectionError(f"Failed to connect to {self.daemon}: {e}")

    def destroy(self) -> None:
        """Destroy the Arduino core instance on the daemon.

        Each Create() should be paired with a Destroy() to free daemon-side
        resources. Called automatically by disconnect(). Failures are silently
        ignored (daemon may already be gone).
        """
        if self.stub and self._instance:
            try:
                self.stub.Destroy(rpc_pb2.DestroyRequest(instance=self._instance))
            except grpc.RpcError:
                pass
        self._instance = None

    def disconnect(self) -> None:
        """Disconnect from the daemon and free resources.

        Calls destroy() to release the daemon-side instance, then closes the
        gRPC channel. Safe to call multiple times.
        """
        self.destroy()
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None

    def __enter__(self):
        """Enter context manager, connecting to the daemon."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, disconnecting from the daemon."""
        self.disconnect()

    def _ensure_connected(self):
        """Raise ConnectionError if not connected to the daemon."""
        if not self.stub:
            raise exceptions.ConnectionError("Not connected. Call connect() first.")

    def _ensure_instance(self):
        """Return initialized instance, lazily initializing if needed."""
        if not self._instance:
            self._instance = self.init()
        return self._instance

    def init(self, sketch_path: Optional[str] = None) -> common_pb2.Instance:
        """Initialize Arduino core instance

        Creates a new instance via Create RPC, then initializes it via Init RPC.
        The Init streaming response is fully consumed to ensure platform data loads.

        Args:
            sketch_path: Optional sketch path for Init context

        Returns:
            Initialized Instance object

        Raises:
            InitializationError: If initialization fails
        """
        self._ensure_connected()
        try:
            create_resp = self.stub.Create(rpc_pb2.CreateRequest())
            inst = create_resp.instance

            init_req = rpc_pb2.InitRequest(instance=inst)
            if sketch_path:
                init_req.sketch_path = sketch_path

            for _ in self.stub.Init(init_req):
                pass

            self._instance = inst
            return self._instance

        except grpc.RpcError as e:
            raise exceptions.InitializationError(f"Init RPC failed: {e.details()}")

    @property
    def instance(self) -> common_pb2.Instance:
        """Return the initialized Arduino core instance.

        Lazily initializes if not already done.

        Returns:
            The current Instance protobuf object.
        """
        return self._ensure_instance()

    def list_boards(self, timeout: int = 5) -> List[Board]:
        """List currently connected boards

        Args:
            timeout: Seconds to probe serial ports (default 5). The daemon
                     needs time to enumerate USB/serial devices.

        Returns:
            List of Board objects from detected ports
        """
        self._ensure_connected()
        instance = self._ensure_instance()

        try:
            request = board_pb2.BoardListRequest(
                instance=instance, timeout=int(timeout)
            )
            response = self.stub.BoardList(request)

            boards = []
            for dp in response.ports:
                port_addr = dp.port.address if dp.port else ""
                port_proto = dp.port.protocol if dp.port else ""
                for mb in dp.matching_boards:
                    board = Board(
                        port=Port(address=port_addr, protocol=port_proto),
                        fqbn=mb.fqbn,
                        name=mb.name,
                        detected=True,
                    )
                    boards.append(board)
            return boards

        except grpc.RpcError as e:
            raise exceptions.BoardError(f"BoardList RPC failed: {e.details()}")

    def list_all_boards(self) -> List[Board]:
        """List all known boards (including offline)

        Returns:
            List of all available Board objects
        """
        self._ensure_connected()
        instance = self._ensure_instance()

        try:
            request = board_pb2.BoardListAllRequest(instance=instance)
            response = self.stub.BoardListAll(request)

            boards = []
            for b in response.boards:
                board = Board(
                    port=Port(address=""),
                    fqbn=b.fqbn,
                    name=b.name,
                    detected=False,
                )
                boards.append(board)
            return boards

        except grpc.RpcError as e:
            raise exceptions.BoardError(f"BoardListAll RPC failed: {e.details()}")

    def watch_boards(
        self,
        callback: Optional[Callable[[Board], None]] = None,
        timeout: Optional[float] = None,
    ) -> Iterator[Board]:
        """Stream board connect/disconnect events.

        Yields Board objects as boards are connected or disconnected.
        Blocks until an event arrives or the optional timeout expires.

        Args:
            callback: Optional function to call for each board event (in
                      addition to yielding).
            timeout: Maximum seconds to wait for the first event. When the
                     deadline passes, gRPC raises DEADLINE_EXCEEDED which is
                     handled gracefully (stops iteration) rather than raised
                     as an error.

        Yields:
            Board objects representing the detected port and matching board.

        Raises:
            BoardError: If the BoardListWatch RPC fails with an error other
                        than DEADLINE_EXCEEDED.
        """
        self._ensure_connected()
        instance = self._ensure_instance()

        try:
            request = board_pb2.BoardListWatchRequest(instance=instance)
            kwargs = {"request": request}
            if timeout is not None:
                kwargs["timeout"] = timeout
            for response in self.stub.BoardListWatch(**kwargs):
                if response.error:
                    raise exceptions.BoardError(f"Board watch error: {response.error}")

                if response.HasField("port") and response.port.port.address:
                    fqbn = ""
                    name = ""
                    if response.port.matching_boards:
                        fb = response.port.matching_boards[0]
                        fqbn = fb.fqbn
                        name = fb.name
                    board = Board(
                        port=Port(
                            address=response.port.port.address,
                            protocol=response.port.port.protocol,
                            protocol_label=response.port.port.protocol_label,
                            label=response.port.port.label,
                        ),
                        fqbn=fqbn,
                        name=name,
                        detected=response.event_type == "add",
                    )
                    if callback:
                        callback(board)
                    yield board

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                return
            raise exceptions.BoardError(f"BoardListWatch RPC failed: {e.details()}")

    def compile_stream(
        self,
        sketch_path: str,
        fqbn: str,
        verbose: bool = False,
        quiet: bool = False,
    ) -> Iterator[tuple[str, str, bool, float]]:
        """Stream compile output as it arrives from the gRPC stream.

        Yields ``(out, err, done, percent)`` tuples for each response from the
        Compile RPC.  *out* and *err* are decoded text chunks (may be empty).
        *done* is True on the final response that contains the result.
        *percent* is a 0.0–100.0 progress percentage from TaskProgress.

        Args:
            sketch_path: Path to the sketch directory containing the .ino file.
            fqbn: Fully Qualified Board Name (e.g. "arduino:avr:uno").
            verbose: Enable verbose compiler output.
            quiet: Suppress non-error output.

        Yields:
            ``(out: str, err: str, done: bool, percent: float)`` tuples.

        Raises:
            InvalidFqbnError: If fqbn is empty.
            CompileError: If the Compile RPC fails.
        """
        self._ensure_connected()
        instance = self._ensure_instance()

        if not fqbn:
            raise exceptions.InvalidFqbnError("FQBN is required")

        try:
            request = compile_pb2.CompileRequest(
                instance=instance,
                fqbn=fqbn,
                sketch_path=sketch_path,
                verbose=verbose,
                quiet=quiet,
            )

            percent = 0.0
            for resp in self.stub.Compile(request, timeout=120):
                out = resp.out_stream.decode() if resp.HasField("out_stream") else ""
                err = resp.err_stream.decode() if resp.HasField("err_stream") else ""
                done = resp.HasField("result") and resp.result
                if resp.HasField("progress"):
                    percent = resp.progress.percent
                if done:
                    percent = 100.0
                yield out, err, done, percent

        except grpc.RpcError as e:
            raise exceptions.CompileError(f"Compile RPC failed: {e.details()}")
        except Exception as e:
            raise exceptions.CompileError(f"Compile failed: {e}")

    def compile(
        self,
        sketch_path: str,
        fqbn: str,
        verbose: bool = False,
        quiet: bool = False,
    ) -> CompileResult:
        """Compile an Arduino sketch.

        Args:
            sketch_path: Path to the sketch directory containing the .ino file.
            fqbn: Fully Qualified Board Name (e.g. "arduino:avr:uno").
            verbose: Enable verbose compiler output.
            quiet: Suppress non-error output.

        Returns:
            CompileResult with success flag, output, and error messages.

        Raises:
            InvalidFqbnError: If fqbn is empty.
            CompileError: If the Compile RPC fails.
        """
        out_lines = []
        err_lines = []
        success = False

        for out, err, done, percent in self.compile_stream(
            sketch_path, fqbn, verbose, quiet
        ):
            if out:
                out_lines.append(out)
            if err:
                err_lines.append(err)
            if done:
                success = True

        return CompileResult(
            success=success,
            output="".join(out_lines),
            error="".join(err_lines),
            sketch_path=sketch_path,
        )

    def upload_stream(
        self,
        sketch_path: str,
        fqbn: str,
        port: str,
        verbose: bool = False,
        verify: bool = True,
    ) -> Iterator[tuple[str, str, bool]]:
        """Stream upload output as it arrives from the gRPC stream.

        Yields ``(out, err, done)`` tuples for each response from the Upload
        RPC.  *out* and *err* are decoded text chunks (may be empty).  *done*
        is True on the final response that contains the result.

        Args:
            sketch_path: Path to the sketch directory.
            fqbn: Fully Qualified Board Name (e.g. "arduino:avr:uno").
            port: Serial port address (e.g. "/dev/ttyACM0").
            verbose: Enable verbose avrdude output.
            verify: Verify upload after writing.

        Yields:
            ``(out: str, err: str, done: bool)`` tuples.

        Raises:
            InvalidFqbnError: If fqbn is empty.
            InvalidPortError: If port is empty.
            UploadError: If the Upload RPC fails.
        """
        self._ensure_connected()
        instance = self._ensure_instance()

        if not fqbn:
            raise exceptions.InvalidFqbnError("FQBN is required")

        if not port:
            raise exceptions.InvalidPortError("Port is required")

        try:
            port_proto = port_pb2.Port(address=port, protocol="serial")

            request = upload_pb2.UploadRequest(
                instance=instance,
                fqbn=fqbn,
                sketch_path=sketch_path,
                port=port_proto,
                verbose=verbose,
                verify=verify,
            )

            for resp in self.stub.Upload(request):
                out = resp.out_stream.decode() if resp.HasField("out_stream") else ""
                err = resp.err_stream.decode() if resp.HasField("err_stream") else ""
                done = resp.HasField("result") and resp.result
                yield out, err, done

        except grpc.RpcError as e:
            raise exceptions.UploadError(f"Upload RPC failed: {e.details()}")
        except Exception as e:
            raise exceptions.UploadError(f"Upload failed: {e}")

    def upload(
        self,
        sketch_path: str,
        fqbn: str,
        port: str,
        verbose: bool = False,
        verify: bool = True,
    ) -> UploadResult:
        """Upload a compiled sketch to a board.

        Args:
            sketch_path: Path to the sketch directory.
            fqbn: Fully Qualified Board Name (e.g. "arduino:avr:uno").
            port: Serial port address (e.g. "/dev/ttyACM0").
            verbose: Enable verbose avrdude output.
            verify: Verify upload after writing.

        Returns:
            UploadResult with success flag, output, and error messages.

        Raises:
            InvalidFqbnError: If fqbn is empty.
            InvalidPortError: If port is empty.
            UploadError: If the Upload RPC fails.
        """
        out_lines = []
        err_lines = []
        success = False

        for out, err, done in self.upload_stream(
            sketch_path, fqbn, port, verbose, verify
        ):
            if out:
                out_lines.append(out)
            if err:
                err_lines.append(err)
            if done:
                success = True

        return UploadResult(
            success=success,
            output="".join(out_lines),
            error="".join(err_lines),
        )

    def compile_and_upload(
        self,
        sketch_path: str,
        fqbn: str,
        port: str,
        verbose: bool = False,
        verify: bool = True,
    ) -> tuple[CompileResult, UploadResult]:
        """Compile a sketch then upload it to a board.

        Skips upload if compilation fails.

        Args:
            sketch_path: Path to the sketch directory.
            fqbn: Fully Qualified Board Name.
            port: Serial port address.
            verbose: Enable verbose output.
            verify: Verify upload after writing.

        Returns:
            Tuple of (CompileResult, UploadResult). If compile fails, the
            UploadResult will have success=False with an error message.
        """
        compile_result = self.compile(sketch_path, fqbn, verbose)

        if not compile_result.success:
            return compile_result, UploadResult(success=False, error="Compile failed")

        upload_result = self.upload(sketch_path, fqbn, port, verbose, verify)
        return compile_result, upload_result

