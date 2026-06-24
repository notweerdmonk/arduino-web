"""Integration tests for BoardManagerService with live daemon"""

import os
import socket
import subprocess
import sys
import time

import pytest

from board_manager.protocol import FrameReader, Handshake, encode_and_frame

UDS_PATH = "/tmp/board_mgr_inttest.sock"
TCP_PORT = 9559


@pytest.fixture(scope="module")
def board_manager_service():
    """Start BoardManagerService in a subprocess"""
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "board_manager",
            "--tcp-port",
            str(TCP_PORT),
            "--uds-path",
            UDS_PATH,
            "--log-level",
            "DEBUG",
        ],
        env={
            **os.environ,
            "PYTHONPATH": "/home/weerdmonk/Projects/medminder/board_manager/python",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(1)

    # Verify it started
    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        pytest.fail(f"BoardManagerService failed to start:\n{stderr.decode()}")

    try:
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        for pipe in (proc.stdout, proc.stderr):
            if pipe:
                pipe.close()
        if os.path.exists(UDS_PATH):
            os.unlink(UDS_PATH)


@pytest.mark.integration
class TestBoardManagerIntegration:
    def test_connect_tcp(self, board_manager_service):
        """Can connect via TCP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", TCP_PORT))
        sock.sendall(Handshake.NEWLINE.value)
        sock.close()

    def test_connect_uds(self, board_manager_service):
        """Can connect via UDS"""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(UDS_PATH)
        sock.close()

    def test_subscribe_and_receive_response(self, board_manager_service):
        """Subscribe returns a result"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", TCP_PORT))
        sock.sendall(Handshake.NEWLINE.value)

        reader = FrameReader("newline")
        sock.sendall(
            encode_and_frame(
                {"type": "subscribe", "topic": "board::+::event"}, "newline"
            )
        )

        data = sock.recv(4096)
        reader.feed(data)
        response = reader.read_one()

        assert response is not None
        assert response.get("status") == "ok"
        sock.close()

    def test_health_check(self, board_manager_service):
        """Health check returns running status"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", TCP_PORT))
        sock.sendall(Handshake.NEWLINE.value)
        reader = FrameReader("newline")

        # Wait for any initial data
        time.sleep(0.2)
        try:
            sock.setblocking(False)
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                except BlockingIOError:
                    break
        finally:
            sock.setblocking(True)

        sock.sendall(
            encode_and_frame(
                {
                    "type": "publish",
                    "topic": "sys::health",
                    "id": "h1",
                    "reply_to": "resp::h1",
                    "body": {"method": "health", "params": {}},
                },
                "newline",
            )
        )

        time.sleep(0.2)
        try:
            data = sock.recv(4096)
        except socket.timeout:
            pytest.fail("No response to health check")

        reader.feed(data)
        response = reader.read_one()
        assert response is not None
        assert response.get("data", {}).get("status") == "running"
        sock.close()

    def test_publish_unknown_topic(self, board_manager_service):
        """Publishing to unknown topic returns a response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", TCP_PORT))
        sock.sendall(Handshake.NEWLINE.value)
        reader = FrameReader("newline")

        time.sleep(0.2)
        # Drain any initial data
        try:
            sock.setblocking(False)
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                except BlockingIOError:
                    break
        finally:
            sock.setblocking(True)

        sock.sendall(
            encode_and_frame(
                {
                    "type": "publish",
                    "topic": "unknown::topic",
                    "id": "r1",
                    "reply_to": "resp::r1",
                    "body": {"method": "list_all_boards", "params": {}},
                },
                "newline",
            )
        )

        time.sleep(0.3)
        try:
            data = sock.recv(4096)
        except socket.timeout:
            pytest.fail("No response to publish")

        reader.feed(data)
        response = reader.read_one()
        assert response is not None
        assert response.get("status") == "ok"
        assert "ports" in response.get("data", {})
        sock.close()

    def test_unsubscribe(self, board_manager_service):
        """Unsubscribe works correctly"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", TCP_PORT))
        sock.sendall(Handshake.NEWLINE.value)
        reader = FrameReader("newline")

        time.sleep(0.1)
        # Drain
        try:
            sock.setblocking(False)
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                except BlockingIOError:
                    break
        finally:
            sock.setblocking(True)

        sock.sendall(
            encode_and_frame({"type": "subscribe", "topic": "test::unsub"}, "newline")
        )
        time.sleep(0.1)
        data = sock.recv(4096)
        reader.feed(data)
        assert reader.read_one() is not None

        sock.sendall(
            encode_and_frame({"type": "unsubscribe", "topic": "test::unsub"}, "newline")
        )
        time.sleep(0.1)
        data = sock.recv(4096)
        reader = FrameReader("newline")
        reader.feed(data)
        response = reader.read_one()
        assert response is not None
        assert response.get("status") == "ok"
        sock.close()

    def test_multiple_clients(self, board_manager_service):
        """Multiple clients can connect simultaneously"""
        socks = []
        for i in range(5):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("127.0.0.1", TCP_PORT))
            sock.sendall(Handshake.NEWLINE.value)
            socks.append(sock)

        for sock in socks:
            sock.sendall(
                encode_and_frame(
                    {"type": "subscribe", "topic": "board::+::event"}, "newline"
                )
            )

        time.sleep(0.2)
        for sock in socks:
            try:
                data = sock.recv(4096)
                assert len(data) > 0
            except socket.timeout:
                pass
            sock.close()

    def test_publish_board_cmd_status(self, board_manager_service):
        """Publishing a status command returns board status"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", TCP_PORT))
        sock.sendall(Handshake.NEWLINE.value)
        reader = FrameReader("newline")

        self._drain(sock)

        sock.sendall(
            encode_and_frame(
                {
                    "type": "publish",
                    "topic": "board::/dev/ttyINT1::cmd",
                    "id": "r2",
                    "reply_to": "resp::r2",
                    "body": {"method": "status", "params": {}},
                },
                "newline",
            )
        )

        time.sleep(1)
        data = self._recv_all(sock)
        if data:
            reader.feed(data)
            while True:
                msg = reader.read_one()
                if msg is None:
                    break
                if msg.get("id") == "r2":
                    assert msg.get("status") == "ok"
                    break
        sock.close()

    def _drain(self, sock):
        """Drain any initial data from the socket"""
        time.sleep(0.2)
        try:
            sock.setblocking(False)
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                except BlockingIOError:
                    break
        finally:
            sock.setblocking(True)

    def _recv_all(self, sock, timeout=2):
        """Receive all available data with timeout"""
        try:
            sock.settimeout(timeout)
            data = sock.recv(65536)
            return data
        except socket.timeout:
            return b""
