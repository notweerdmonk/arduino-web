"""Subprocess entrypoint for per-board gRPC client"""

import json
import logging
import socket
import sys
import traceback
from typing import Any

from board_manager.protocol import FrameReader, encode_and_frame

logger = logging.getLogger("board_worker")


def _make_error(msg: dict, code: str, text: str) -> dict:
    """Build an error response dict from a request message."""
    return {
        "type": "error",
        "id": msg.get("id"),
        "topic": msg.get("reply_to", ""),
        "status": "error",
        "code": code,
        "message": text,
        "data": {"code": code, "message": text},
    }


def _make_result(msg: dict, status: str, data: Any = None) -> dict:
    """Build a success result response dict from a request message."""
    return {
        "type": "result",
        "id": msg.get("id"),
        "topic": msg.get("reply_to", ""),
        "status": status,
        "data": data,
    }


def _make_progress(msg: dict, out: str, err: str, percent: float = 0.0) -> dict:
    """Build a progress event dict for compile/upload streaming output."""
    return {
        "type": "event",
        "topic": msg.get("reply_to", "") + "::progress",
        "data": {"output": out, "error": err, "percent": percent},
    }


def _make_event(topic: str, data: Any) -> dict:
    """Build a generic event dict."""
    return {"type": "event", "topic": topic, "data": data}


def main() -> None:
    """Subprocess entrypoint: connect to arduino-cli daemon and handle messages over a Unix socket."""
    fd = int(sys.argv[1])
    sock = socket.fromfd(fd, socket.AF_UNIX, socket.SOCK_STREAM)
    reader = FrameReader("newline")

    from arduino_grpc.client import ArduinoGrpcClient
    from arduino_grpc.exceptions import ArduinoError

    client = ArduinoGrpcClient()
    try:
        client.connect()
        client.init()
    except ArduinoError as e:
        sock.sendall(
            encode_and_frame(
                {
                    "type": "error",
                    "code": "init_failed",
                    "message": str(e),
                }
            )
        )
        sock.close()
        return

    sock.sendall(
        encode_and_frame({"type": "event", "topic": "worker/ready", "data": {}})
    )

    try:
        while True:
            try:
                data = sock.recv(4096)
            except (OSError, ConnectionError):
                break
            if not data:
                break
            reader.feed(data)
            while True:
                msg = reader.read_one()
                if msg is None:
                    break
                _handle_message(msg, client, sock)
    except KeyboardInterrupt:
        logger.info("shutdown: received SIGINT")
    finally:
        try:
            client.disconnect()
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass


def _handle_message(msg: dict, client: Any, sock: socket.socket) -> None:
    """Dispatch a single message to the appropriate arduino-cli method.

    Args:
        msg: The parsed request message dict.
        client: The ArduinoGrpcClient instance.
        sock: The Unix socket to write responses to.
    """
    from arduino_grpc.exceptions import ArduinoError

    method = (msg.get("body") or {}).get("method")
    params = (msg.get("body") or {}).get("params") or {}

    if method == "init":
        try:
            client.init()
            sock.sendall(encode_and_frame(_make_result(msg, "ok")))
        except ArduinoError as e:
            sock.sendall(encode_and_frame(_make_error(msg, "init_failed", str(e))))

    elif method == "list_boards":
        try:
            boards = client.list_boards(timeout=params.get("timeout", 5))
            sock.sendall(
                encode_and_frame(
                    _make_result(
                        msg,
                        "ok",
                        [{"port": b.port.address, "fqbn": b.fqbn, "name": b.name} for b in boards],
                    )
                )
            )
        except ArduinoError as e:
            sock.sendall(encode_and_frame(_make_error(msg, "board_list_failed", str(e))))

    elif method == "compile":
        try:
            sketch_path = params.get("sketch_path", "")
            fqbn = params.get("fqbn", "")
            verbose = params.get("verbose", False)
            logger.info("compile: starting sketch=%s fqbn=%s", sketch_path, fqbn)
            out_lines: list[str] = []
            err_lines: list[str] = []
            success = False
            last_pct = -1.0
            for out, err, done, percent in client.compile_stream(
                sketch_path=sketch_path,
                fqbn=fqbn,
                verbose=verbose,
            ):
                if out:
                    out_lines.append(out)
                    sock.sendall(encode_and_frame(_make_progress(msg, out, "", percent)))
                    last_pct = percent
                    logger.debug("compile: received %d output bytes (%.0f%%)", len(out), percent)
                if err:
                    err_lines.append(err)
                    sock.sendall(encode_and_frame(_make_progress(msg, "", err, percent)))
                    last_pct = percent
                if done:
                    success = True
                elif percent != last_pct:
                    sock.sendall(encode_and_frame(_make_progress(msg, "", "", percent)))
                    last_pct = percent
            logger.info("compile: done success=%s output_len=%d", success, sum(len(l) for l in out_lines))
            sock.sendall(
                encode_and_frame(
                    _make_result(
                        msg,
                        "ok" if success else "error",
                        {
                            "success": success,
                            "output": "".join(out_lines),
                            "error": "".join(err_lines),
                            "sketch_path": sketch_path,
                        },
                    )
                )
            )
        except ArduinoError as e:
            sock.sendall(encode_and_frame(_make_error(msg, "compile_failed", str(e))))

    elif method == "upload":
        try:
            sketch_path = params.get("sketch_path", "")
            fqbn = params.get("fqbn", "")
            port = params.get("port", "")
            verbose = params.get("verbose", False)
            logger.info("upload: starting sketch=%s port=%s fqbn=%s", sketch_path, port, fqbn)
            sock.sendall(encode_and_frame(_make_progress(msg, f"Starting upload to {port}...", "")))
            sock.sendall(encode_and_frame(_make_progress(msg, f"  Sketch: {sketch_path}", "")))
            sock.sendall(encode_and_frame(_make_progress(msg, f"  Board:  {fqbn}", "")))
            if verbose:
                sock.sendall(encode_and_frame(_make_progress(msg, "  Verbose mode enabled", "")))
            out_lines: list[str] = []
            err_lines: list[str] = []
            success = False
            for out, err, done in client.upload_stream(
                sketch_path=sketch_path,
                fqbn=fqbn,
                port=port,
                verbose=verbose,
            ):
                if out:
                    out_lines.append(out)
                    sock.sendall(encode_and_frame(_make_progress(msg, out, "")))
                    logger.debug("upload: received %d output bytes", len(out))
                if err:
                    err_lines.append(err)
                    sock.sendall(encode_and_frame(_make_progress(msg, "", err)))
                if done:
                    success = True
            logger.info("upload: done success=%s output_len=%d", success, sum(len(l) for l in out_lines))
            if success:
                sock.sendall(encode_and_frame(_make_progress(msg, "Upload completed successfully.", "")))
            else:
                err_text = "".join(err_lines) or "Unknown error during upload"
                sock.sendall(encode_and_frame(_make_progress(msg, "", f"Upload failed: {err_text}")))
            sock.sendall(
                encode_and_frame(
                    _make_result(
                        msg,
                        "ok" if success else "error",
                        {
                            "success": success,
                            "output": "".join(out_lines),
                            "error": "".join(err_lines),
                        },
                    )
                )
            )
        except ArduinoError as e:
            error_msg = str(e)
            sock.sendall(encode_and_frame(_make_progress(msg, "", f"Upload failed: {error_msg}")))
            sock.sendall(encode_and_frame(_make_error(msg, "upload_failed", error_msg)))

    elif method == "compile_and_upload":
        try:
            sketch_path = params.get("sketch_path", "")
            fqbn = params.get("fqbn", "")
            port = params.get("port", "")
            verbose = params.get("verbose", False)
            logger.info("compile_and_upload: starting sketch=%s fqbn=%s port=%s", sketch_path, fqbn, port)
            compile_result, upload_result = client.compile_and_upload(
                sketch_path=sketch_path,
                fqbn=fqbn,
                port=port,
                verbose=verbose,
            )
            success = compile_result.success and upload_result.success
            logger.info("compile_and_upload: done success=%s", success)
            sock.sendall(
                encode_and_frame(
                    _make_result(
                        msg,
                        "ok" if success else "error",
                        {
                            "compile": {
                                "success": compile_result.success,
                                "output": compile_result.output,
                                "error": compile_result.error,
                            },
                            "upload": {
                                "success": upload_result.success,
                                "output": upload_result.output,
                                "error": upload_result.error,
                            },
                        },
                    )
                )
            )
        except ArduinoError as e:
            sock.sendall(encode_and_frame(_make_error(msg, "op_failed", str(e))))

    elif method == "ping":
        sock.sendall(encode_and_frame(_make_result(msg, "ok", {"pong": True})))

    else:
        sock.sendall(
            encode_and_frame(_make_error(msg, "unknown_method", f"Unknown method: {method}"))
        )


if __name__ == "__main__":
    main()
