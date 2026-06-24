#!/usr/bin/env python3
"""
arduino_board_status.py

Usage examples:
  # list boards
  python arduino_board_status.py --daemon localhost:50051

  # detect (streaming)
  python arduino_board_status.py --daemon localhost:50051 --detect

  # upload sketch to a port (compiles then uploads)
  python arduino_board_status.py --daemon localhost:50051 --upload /path/to/sketch --port /dev/ttyUSB0 --fqbn arduino:avr:uno
"""

import argparse
import grpc
import sys
import os
from cc.arduino.cli.commands.v1 import commands_pb2 as rpc_pb2
from cc.arduino.cli.commands.v1 import commands_pb2_grpc as rpc_pb2_grpc

DEFAULT_DAEMON = "localhost:50051"
DEFAULT_FQBN = "arduino:avr:uno"


def init_instance(stub):
    """Initialise an arduino-cli gRPC instance via Init RPC.

    Args:
        stub: The gRPC ArduinoCoreService stub.

    Returns:
        The InitResponse instance, or None on failure.
    """
    try:
        resp = stub.Init(rpc_pb2.InitRequest())
        return resp.instance
    except Exception as e:
        print(f"Init RPC failed: {e}", file=sys.stderr)
        return None


def list_boards(stub, instance):
    """List connected Arduino boards via BoardList RPC and print results.

    Args:
        stub: The gRPC ArduinoCoreService stub.
        instance: The arduino-cli instance identifier.
    """
    try:
        req = rpc_pb2.BoardListRequest(instance=instance)
        resp = stub.BoardList(req)
        if not resp.boards:
            print("No boards found.")
            return
        for b in resp.boards:
            print(f"Port: {b.port}\tFQBN: {b.fqbn}\tName: {b.name}")
    except Exception as e:
        print(f"BoardList RPC failed: {e}", file=sys.stderr)


def detect_boards(stub, instance):
    """Stream board detection events and print results.

    Args:
        stub: The gRPC ArduinoCoreService stub.
        instance: The arduino-cli instance identifier.
    """
    req = rpc_pb2.BoardDetectRequest(instance=instance)
    try:
        # BoardDetect is a server streaming RPC
        resp_iter = stub.BoardDetect(req)
        for resp in resp_iter:
            print(f"Port: {resp.port}\tFQBN: {resp.fqbn}\tDetected: {resp.detected}")
    except Exception as e:
        print(f"BoardDetect RPC failed: {e}", file=sys.stderr)


def compile_sketch(stub, instance, sketch_path, fqbn):
    """Compile an Arduino sketch via the gRPC Compile RPC.

    Args:
        stub: The gRPC ArduinoCoreService stub.
        instance: The arduino-cli instance identifier.
        sketch_path: Path to the sketch directory.
        fqbn: Fully qualified board name.

    Returns:
        The last CompileResponse on success, or None on failure.
    """
    if not os.path.exists(sketch_path):
        print(f"Sketch path not found: {sketch_path}", file=sys.stderr)
        return None

    req = rpc_pb2.CompileRequest(instance=instance, fqbn=fqbn, sketch_path=sketch_path)
    try:
        # Compile is server streaming; collect all responses
        responses = list(stub.Compile(req))
        if not responses:
            print("No compile response received", file=sys.stderr)
            return None

        last_resp = responses[-1]
        # Check for compilation errors in the final response
        if last_resp.output_stream and "error" in last_resp.output_stream.lower():
            print(f"Compile error: {last_resp.output_stream}", file=sys.stderr)
            return None

        return last_resp
    except Exception as e:
        print(f"Compile RPC failed: {e}", file=sys.stderr)
        return None


def upload_sketch(stub, instance, sketch_path, fqbn, port):
    """Upload a compiled sketch to a board port via the gRPC Upload RPC.

    Args:
        stub: The gRPC ArduinoCoreService stub.
        instance: The arduino-cli instance identifier.
        sketch_path: Path to the sketch directory.
        fqbn: Fully qualified board name.
        port: Serial port (e.g. /dev/ttyUSB0).
    """
    if not os.path.exists(sketch_path):
        print(f"Sketch path not found: {sketch_path}", file=sys.stderr)
        return

    req = rpc_pb2.UploadRequest(
        instance=instance, fqbn=fqbn, sketch_path=sketch_path, port=port
    )
    try:
        # Upload is server streaming
        resp_iter = stub.Upload(req)
        for resp in resp_iter:
            if resp.output_stream:
                print(resp.output_stream.strip())
    except Exception as e:
        print(f"Upload RPC failed: {e}", file=sys.stderr)


def main():
    """Parse CLI args, connect to daemon, and run the requested action."""
    p = argparse.ArgumentParser(
        description="Show/upload Arduino sketches via arduino-cli gRPC"
    )
    p.add_argument(
        "--daemon",
        default=DEFAULT_DAEMON,
        help="Daemon host:port (default %(default)s)",
    )
    p.add_argument(
        "--detect", action="store_true", help="Run board detection (streams updates)"
    )
    p.add_argument(
        "--upload",
        metavar="SKETCH_PATH",
        help="Upload sketch directory (path containing .ino)",
    )
    p.add_argument(
        "--port", help="Serial port to upload to (e.g., /dev/ttyUSB0 or COM3)"
    )
    p.add_argument(
        "--fqbn",
        default=DEFAULT_FQBN,
        help="Fully qualified board name (default %(default)s)",
    )
    args = p.parse_args()

    channel = grpc.insecure_channel(args.daemon)
    try:
        stub = rpc_pb2_grpc.ArduinoCoreServiceStub(channel)

        instance = init_instance(stub)
        if instance is None:
            sys.exit(1)

        if args.detect:
            detect_boards(stub, instance)
        elif args.upload:
            if not args.port:
                print("Upload requires --port to be specified", file=sys.stderr)
                sys.exit(1)
            print("Compiling sketch...")
            comp = compile_sketch(stub, instance, args.upload, args.fqbn)
            if comp is None:
                print("Compile failed; aborting upload", file=sys.stderr)
                sys.exit(1)
            print("Uploading sketch to", args.port)
            upload_sketch(stub, instance, args.upload, args.fqbn, args.port)
        else:
            list_boards(stub, instance)
    finally:
        channel.close()


if __name__ == "__main__":
    main()
