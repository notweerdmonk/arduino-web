"""Subprocess lifecycle manager for per-board workers"""

import errno
import os
import select
import signal
import socket
import subprocess
import sys
import time
from enum import IntEnum
from typing import Any, Optional

from board_manager.protocol import FrameReader, encode_and_frame


class PoolLimits(IntEnum):
    """Limit constants for the board worker pool."""

    MAX_RESTARTS = 3


class BoardProc:
    """State container for a single per-board worker subprocess."""
    def __init__(self, port: str):
        """Initialize a board process state container.

        Args:
            port: The serial port address for this board.
        """
        self.port = port
        self.proc: Optional[subprocess.Popen] = None
        self.parent_sock: Optional[socket.socket] = None
        self.reader = FrameReader("newline")
        self.restart_count = 0
        self.last_error: Optional[str] = None
        self.ready = False


class BoardPool:
    """Manages subprocess lifecycle for per-board gRPC workers"""

    def __init__(self):
        """Initialize the pool with an empty board map."""
        self._boards: dict[str, BoardProc] = {}
        self._worker_path: Optional[str] = None

    def _get_worker_path(self) -> str:
        """Resolve the absolute path to the board_worker module.

        Returns:
            Absolute filesystem path to board_worker.py.
        """
        if self._worker_path is None:
            import board_manager.board_worker

            self._worker_path = os.path.abspath(board_manager.board_worker.__file__)
        return self._worker_path

    def spawn(self, port: str) -> BoardProc:
        """Spawn a new worker subprocess for a board port.

        Args:
            port: The serial port address.

        Returns:
            The BoardProc instance for the new worker.

        Raises:
            RuntimeError: If a worker is already running for this port or
                the max restart limit has been exceeded.
        """
        existing = self._boards.get(port)
        if existing and existing.proc and existing.proc.poll() is None:
            raise RuntimeError(f"Worker for {port} already running")

        if existing and existing.restart_count >= PoolLimits.MAX_RESTARTS:
            raise RuntimeError(
                f"Worker for {port} exceeded max restarts ({PoolLimits.MAX_RESTARTS})"
            )

        parent_sock, child_sock = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_STREAM
        )
        child_fd = child_sock.fileno()

        proc = subprocess.Popen(
            [sys.executable, self._get_worker_path(), str(child_fd)],
            pass_fds=[child_fd],
            close_fds=True,
        )

        child_sock.close()

        bp = existing or BoardProc(port)
        bp.proc = proc
        bp.parent_sock = parent_sock
        bp.reader.clear()
        bp.ready = False
        if existing:
            bp.restart_count += 1
        self._boards[port] = bp
        return bp

    def dispatch(self, port: str, message: dict) -> None:
        """Send a framed message to a board's worker subprocess.

        Args:
            port: The serial port address.
            message: The message dict to send.

        Raises:
            RuntimeError: If no worker exists, has exited, or send fails.
        """
        bp = self._boards.get(port)
        if bp is None or bp.parent_sock is None:
            raise RuntimeError(f"No worker for port {port}")

        if bp.proc and bp.proc.poll() is not None:
            raise RuntimeError(f"Worker for {port} has exited")

        try:
            bp.parent_sock.sendall(encode_and_frame(message, "newline"))
        except (OSError, ConnectionError) as e:
            bp.last_error = str(e)
            raise RuntimeError(f"Failed to send to worker for {port}: {e}")

    def poll(self, timeout: float = 0.01) -> list[tuple[str, dict]]:
        """Poll all worker sockets for incoming messages.

        Args:
            timeout: select() timeout in seconds.

        Returns:
            List of (port, message) tuples from ready workers.
        """
        results: list[tuple[str, dict]] = []
        if not self._boards:
            return results

        socks_to_check = []
        sock_to_port = {}
        for port, bp in self._boards.items():
            if bp.parent_sock is not None and bp.proc and bp.proc.poll() is None:
                socks_to_check.append(bp.parent_sock)
                sock_to_port[id(bp.parent_sock)] = port

        if not socks_to_check:
            return results

        try:
            readable, _, _ = select.select(socks_to_check, [], [], timeout)
        except ValueError:
            return results

        for sock in readable:
            port = sock_to_port.get(id(sock))
            if port is None:
                continue
            bp = self._boards.get(port)
            if bp is None:
                continue
            try:
                data = sock.recv(65536)
            except (OSError, ConnectionError) as e:
                bp.last_error = str(e)
                continue

            if not data:
                bp.last_error = "worker closed connection"
                continue

            bp.reader.feed(data)
            while True:
                msg = bp.reader.read_one()
                if msg is None:
                    break
                if msg.get("type") == "event" and msg.get("topic") == "worker/ready":
                    bp.ready = True
                results.append((port, msg))

        return results

    def remove(self, port: str) -> None:
        """Remove and terminate the worker for a given port."""
        bp = self._boards.pop(port, None)
        if bp is None:
            return
        self._cleanup_proc(bp)

    def _cleanup_proc(self, bp: BoardProc) -> None:
        """Terminate a worker process and close its socket."""
        if bp.proc and bp.proc.poll() is None:
            try:
                bp.proc.send_signal(signal.SIGTERM)
                bp.proc.wait(timeout=3)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    bp.proc.kill()
                    bp.proc.wait(timeout=2)
                except (subprocess.TimeoutExpired, OSError):
                    pass
        if bp.parent_sock:
            try:
                bp.parent_sock.close()
            except OSError:
                pass
            bp.parent_sock = None

    def shutdown_all(self) -> None:
        """Terminate all worker processes and clear the pool."""
        for bp in list(self._boards.values()):
            self._cleanup_proc(bp)
        self._boards.clear()

    def get_port_status(self, port: str) -> Optional[dict]:
        """Get the current status of a board worker.

        Args:
            port: The serial port address.

        Returns:
            Status dict with running, ready, restart_count, etc., or None.
        """
        bp = self._boards.get(port)
        if bp is None:
            return None
        exit_code = bp.proc.poll() if bp.proc else -1
        return {
            "port": port,
            "running": exit_code is None,
            "ready": bp.ready,
            "restart_count": bp.restart_count,
            "exit_code": exit_code,
            "last_error": bp.last_error,
        }

    def list_ports(self) -> list[str]:
        """Return a list of all managed port addresses."""
        return list(self._boards.keys())

    def restart(self, port: str) -> BoardProc:
        """Remove and re-spawn the worker for a given port.

        Args:
            port: The serial port address.

        Returns:
            The new BoardProc instance.
        """
        self.remove(port)
        return self.spawn(port)
