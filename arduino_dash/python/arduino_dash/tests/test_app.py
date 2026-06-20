"""Tests for webapp app — response handling, compile/upload endpoints"""

import io
import json
import logging
import os
import threading
from unittest.mock import MagicMock, patch

import pytest

from arduino_dash import app as _app_module
from arduino_dash import state
from arduino_dash.sketch_management import REGISTRY_FILE as _REGISTRY_FILE


@pytest.fixture(autouse=True)
def clear_caches():
    state._daemon_ready = False
    with _app_module._pending_responses_lock:
        _app_module._pending_responses.clear()
    with _app_module._compile_results_lock:
        _app_module._compile_results.clear()
    with _app_module._upload_results_lock:
        _app_module._upload_results.clear()
    with _app_module._last_compiled_sketch_lock:
        _app_module._last_compiled_sketch.clear()
    with _app_module._last_compile_mtime_lock:
        _app_module._last_compile_mtime.clear()
    with _app_module._upload_registry_lock:
        _app_module._upload_registry.clear()
    import os as _os
    _os.path.isfile(_REGISTRY_FILE) and _os.remove(_REGISTRY_FILE)
    _tools = _app_module.app.extensions.get("arduino_sketch_tools")
    if _tools:
        with _tools._compile_results_lock:
            _tools._compile_results.clear()
        with _tools._upload_results_lock:
            _tools._upload_results.clear()
        with _tools._compile_meta_lock:
            _tools._compile_meta.clear()
        with _tools._upload_meta_lock:
            _tools._upload_meta.clear()
        with _tools._last_compiled_sketch_lock:
            _tools._last_compiled_sketch.clear()
        with _tools._last_compile_mtime_lock:
            _tools._last_compile_mtime.clear()
        with _tools._last_compile_checksum_lock:
            _tools._last_compile_checksum.clear()
        with _tools._last_uploaded_sketch_lock:
            _tools._last_uploaded_sketch.clear()
    yield


@pytest.fixture
def tools():
    return _app_module.app.extensions.get("arduino_sketch_tools")


@pytest.fixture
def req_ctx():
    with _app_module.app.test_request_context():
        yield


@pytest.fixture
def client():
    _app_module.app.config["TESTING"] = True
    with _app_module.app.test_client() as c:
        yield c


class TestOnResp:
    # compile/upload result/progress tests moved to test_extension.py (Q5)

    def test_stores_result_and_signals_event(self):
        topic = "resp::compile::/dev/ttyACM0"
        event = threading.Event()
        with _app_module._pending_responses_lock:
            _app_module._pending_responses[topic] = (None, event)

        _app_module._on_resp({"topic": topic, "status": "ok", "data": {"output": "ok"}})

        assert event.is_set()
        with _app_module._pending_responses_lock:
            stored, _ = _app_module._pending_responses[topic]
        assert stored["status"] == "ok"

    def test_no_waiter_does_not_crash(self):
        _app_module._on_resp({"topic": "resp::nobody::listening", "status": "ok"})

    def test_second_response_is_ignored(self):
        topic = "resp::compile::/dev/ttyACM0"
        event = threading.Event()
        with _app_module._pending_responses_lock:
            _app_module._pending_responses[topic] = (None, event)

        _app_module._on_resp({"topic": topic, "status": "ok", "data": {"output": "first"}})
        assert event.is_set()
        _app_module._on_resp({"topic": topic, "status": "ok", "data": {"output": "second"}})

        with _app_module._pending_responses_lock:
            stored = _app_module._pending_responses.get(topic)
        assert stored is not None
        stored_msg, stored_event = stored
        assert stored_msg["data"]["output"] == "first"


class TestWaitForResponse:
    def test_returns_result_on_response(self):
        topic = "resp::compile::/dev/ttyACM0"

        def send_after_delay():
            import time
            time.sleep(0.05)
            with _app_module._pending_responses_lock:
                entry = _app_module._pending_responses.get(topic)
            if entry is not None:
                _, event = entry
                _app_module._pending_responses[topic] = ({"status": "ok", "topic": topic}, event)
                event.set()

        t = threading.Thread(target=send_after_delay, daemon=True)
        t.start()
        result = _app_module._wait_for_response(topic, timeout=5.0)
        assert result is not None
        assert result["status"] == "ok"

    def test_timeout_returns_none(self):
        topic = "resp::upload::/dev/ttyACM0"
        result = _app_module._wait_for_response(topic, timeout=0.1)
        assert result is None

    def test_cleanup_on_timeout(self):
        topic = "resp::compile::/dev/ttyACM1"
        _app_module._wait_for_response(topic, timeout=0.05)
        with _app_module._pending_responses_lock:
            assert topic not in _app_module._pending_responses


class TestApiCompile:
    def test_publishes_and_shows_in_progress(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/compile", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
            "verbose": "true",
        })
        assert resp.status_code == 200
        assert b"Compiling" in resp.data
        assert b"/compile/poll" in resp.data
        assert mock_pubsub.publish.called
        with tools._compile_results_lock:
            assert tools._compile_results.get("/dev/ttyACM0") is None

    def test_poll_pending_when_null(self, client, tools):
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = None
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Compiling" in resp.data

    def test_poll_returns_result_when_done(self, client, tools):
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "ok",
                "data": {"output": "built ok"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Compile succeeded" in resp.data


class TestApiUpload:
    def test_publishes_and_shows_in_progress(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
            "verbose": "true",
        })
        assert resp.status_code == 200
        assert b"Uploading" in resp.data
        assert b"/upload/poll" in resp.data
        assert mock_pubsub.publish.called
        with tools._upload_results_lock:
            assert tools._upload_results.get("/dev/ttyACM0") is None

    def test_poll_pending_when_null(self, client, tools):
        with tools._upload_results_lock:
            tools._upload_results["/dev/ttyACM0"] = None
        resp = client.get("/board/dev/ttyACM0/upload/poll")
        assert resp.status_code == 200
        assert b"Uploading" in resp.data

    def test_poll_returns_result_when_done(self, client, tools):
        with tools._upload_results_lock:
            tools._upload_results["/dev/ttyACM0"] = {
                "topic": "resp::upload::/dev/ttyACM0",
                "status": "ok",
                "data": {"output": "uploaded ok"},
            }
        resp = client.get("/board/dev/ttyACM0/upload/poll")
        assert resp.status_code == 200
        assert b"Upload succeeded" in resp.data

    def test_poll_returns_error_when_failed(self, client, tools):
        with tools._upload_results_lock:
            tools._upload_results["/dev/ttyACM0"] = {
                "topic": "resp::upload::/dev/ttyACM0",
                "status": "error",
                "code": "upload_failed",
                "message": "Cannot open serial port /dev/ttyACM0",
                "data": {"code": "upload_failed", "message": "Cannot open serial port /dev/ttyACM0"},
            }
        resp = client.get("/board/dev/ttyACM0/upload/poll")
        assert resp.status_code == 200
        assert b"Upload error" in resp.data
        assert b"Cannot open serial port" in resp.data


class TestInitPubsub:
    """Tests for init_pubsub (aligned with medminder_dash pattern)"""

    def test_connect_failure_does_not_block_init(self, caplog):
        caplog.set_level(logging.WARNING)
        with (
            patch("arduino_dash.pubsub.PubSubClient") as mock_cls,
        ):
            instance = MagicMock()
            instance.connect.side_effect = ConnectionRefusedError("refused")
            mock_cls.return_value = instance

            # Should NOT raise — error caught internally
            _app_module.init_pubsub(
                use_uds=True,
                tcp_host="127.0.0.1",
                tcp_port=9090,
                uds_path="/tmp/test.sock",
            )

            # subscribe and start_reader should still be called after failure
            instance.subscribe.assert_any_call("board::+::event", _app_module._on_board_event)
            instance.subscribe.assert_any_call("sys::daemon/ready", _app_module._on_daemon_ready)
            instance.start_reader.assert_called_once()

            # Warning should be logged
            assert any("Could not connect" in rec.message for rec in caplog.records)

    def test_connect_success_normal_flow(self):
        with (
            patch("arduino_dash.pubsub.PubSubClient") as mock_cls,
        ):
            instance = MagicMock()
            mock_cls.return_value = instance

            _app_module.init_pubsub(
                use_uds=True,
                tcp_host="127.0.0.1",
                tcp_port=9090,
                uds_path="/tmp/test.sock",
            )

            assert instance.on_reconnect == _app_module._on_pubsub_reconnect
            instance.connect.assert_called_once_with(retry=True)
            instance.subscribe.assert_any_call("board::+::event", _app_module._on_board_event)
            instance.subscribe.assert_any_call("sys::daemon/ready", _app_module._on_daemon_ready)
            instance.start_reader.assert_called_once()


class TestCompileMeta:
    def test_compile_stores_meta(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        with _app_module._board_list_lock:
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno",
            }
        resp = client.post("/board/dev/ttyACM0/compile", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        with tools._compile_meta_lock:
            meta = tools._compile_meta.get("/dev/ttyACM0")
        assert meta is not None
        assert meta["port"] == "/dev/ttyACM0"
        assert meta["board"] == "Arduino Uno"
        assert meta["fqbn"] == "arduino:avr:uno"
        assert meta["sketch"] == "/tmp/sketch"

    def test_compile_meta_cleared_on_poll(self, client, tools):
        with tools._compile_meta_lock:
            tools._compile_meta["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "sketch": "/tmp/sketch",
            }
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "ok",
                "data": {"output": "ok"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        with tools._compile_meta_lock:
            assert "/dev/ttyACM0" not in tools._compile_meta


class TestUploadMeta:
    def test_upload_stores_meta(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        with _app_module._board_list_lock:
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno",
            }
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        with tools._upload_meta_lock:
            meta = tools._upload_meta.get("/dev/ttyACM0")
        assert meta is not None
        assert meta["port"] == "/dev/ttyACM0"
        assert meta["board"] == "Arduino Uno"
        assert meta["fqbn"] == "arduino:avr:uno"
        assert meta["sketch"] == "/tmp/sketch"

    def test_upload_meta_cleared_on_poll(self, client, tools):
        with tools._upload_meta_lock:
            tools._upload_meta["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "sketch": "/tmp/sketch",
            }
        with tools._upload_results_lock:
            tools._upload_results["/dev/ttyACM0"] = {
                "topic": "resp::upload::/dev/ttyACM0",
                "status": "ok",
                "data": {"output": "uploaded ok"},
            }
        resp = client.get("/board/dev/ttyACM0/upload/poll")
        assert resp.status_code == 200
        with tools._upload_meta_lock:
            assert "/dev/ttyACM0" not in tools._upload_meta


class TestBoardConnectionStatus:
    def test_connected_when_port_in_board_list(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list["/dev/ttyACM0"] = {"port": "/dev/ttyACM0", "board": "Arduino Uno"}
        resp = client.get("/board/dev/ttyACM0/connection-status")
        assert resp.status_code == 200
        assert b"Connected" in resp.data
        assert b"badge-ok" in resp.data

    def test_disconnected_when_port_not_in_board_list(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
        resp = client.get("/board/dev/ttyACM0/connection-status")
        assert resp.status_code == 200
        assert b"Disconnected" in resp.data
        assert b"badge-err" in resp.data

    def test_normalizes_port(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list["/dev/ttyACM1"] = {"port": "/dev/ttyACM1"}
        # Different port, not in list
        resp = client.get("/board/dev/ttyACM0/connection-status")
        assert b"Disconnected" in resp.data


class TestBmsOffline:
    def test_compile_returns_offline_msg_when_disconnected(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = False
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/compile", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"offline" in resp.data
        assert b"BoardManagerService" in resp.data
        mock_pubsub.publish.assert_not_called()

    def test_upload_returns_offline_msg_when_disconnected(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = False
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"offline" in resp.data
        assert b"BoardManagerService" in resp.data
        mock_pubsub.publish.assert_not_called()

    def test_compile_proceeds_when_connected(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/compile", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"Compiling" in resp.data
        mock_pubsub.publish.assert_called_once()

    def test_upload_proceeds_when_connected(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"Uploading" in resp.data
        mock_pubsub.publish.assert_called_once()


class TestDaemonStatus:
    def test_daemon_ready_handler_sets_flag(self):
        assert state._daemon_ready is False
        _app_module._on_daemon_ready({"type": "event", "topic": "sys::daemon/ready"})
        assert state._daemon_ready is True

    def test_daemon_ready_handler_ignores_result_messages(self):
        state._daemon_ready = False
        _app_module._on_daemon_ready({"type": "result", "topic": "sys::daemon/ready"})
        assert state._daemon_ready is False

    def test_daemon_ready_handler_ignores_unknown_type(self):
        state._daemon_ready = False
        _app_module._on_daemon_ready({"type": "heartbeat", "topic": "sys::daemon/ready"})
        assert state._daemon_ready is False

    def test_pubsub_reconnect_resets_flag(self):
        state._daemon_ready = True
        _app_module._on_pubsub_reconnect()
        assert state._daemon_ready is False

    def test_api_daemon_status_returns_off_when_not_ready(self, client):
        state._daemon_ready = False
        resp = client.get("/daemon/status")
        assert resp.status_code == 200
        assert b"daemon-off" in resp.data
        assert b"Disconnected" in resp.data

    def test_api_daemon_status_returns_off_when_disconnected(self, client):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = False
        with patch("arduino_dash.state.pubsub", mock_pubsub):
            state._daemon_ready = True
            resp = client.get("/daemon/status")
            assert resp.status_code == 200
            assert b"daemon-off" in resp.data
            assert b"Disconnected" in resp.data

    def test_api_daemon_status_returns_on_when_ready(self, client):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        with patch("arduino_dash.state.pubsub", mock_pubsub):
            state._daemon_ready = True
            resp = client.get("/daemon/status")
            assert resp.status_code == 200
            assert b"daemon-on" in resp.data
            assert b"Ready" in resp.data


class TestComputeSketchChecksum:
    def test_returns_deterministic_hash(self, tmp_path):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        (sketch_dir / "main.ino").write_text("void setup() {}")
        (sketch_dir / "src").mkdir()
        (sketch_dir / "src" / "lib.cpp").write_text("int x = 1;")
        h1 = _app_module._compute_sketch_checksum(str(sketch_dir))
        h2 = _app_module._compute_sketch_checksum(str(sketch_dir))
        assert h1 == h2
        assert len(h1) == 64

    def test_empty_dir_returns_empty(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        assert _app_module._compute_sketch_checksum(str(empty_dir)) == ""

    def test_nonexistent_dir_returns_empty(self):
        assert _app_module._compute_sketch_checksum("/nonexistent/path") == ""


class TestGetSketchMtime:
    def test_returns_mtime(self, tmp_path):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        mtime = _app_module._get_sketch_mtime(str(sketch_dir))
        assert mtime is not None
        assert mtime > 0

    def test_missing_dir_returns_none(self):
        mtime = _app_module._get_sketch_mtime("/nonexistent/path")
        assert mtime is None

    def test_empty_dir_returns_none(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        mtime = _app_module._get_sketch_mtime(str(empty_dir))
        assert mtime is None


class TestUploadConfirmWarnings:
    def test_sketch_path_change_returns_confirm(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = "/old/sketch"
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": "/new/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"Warnings detected" in resp.data
        assert b"Sketch path changed" in resp.data
        assert b"Upload Anyway" in resp.data
        assert b"Cancel" in resp.data
        mock_pubsub.publish.assert_not_called()

    def test_sketch_modified_returns_confirm(self, client, tmp_path, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = 1000000
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": str(sketch_dir),
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"Warnings detected" in resp.data
        mock_pubsub.publish.assert_not_called()

    def test_confirm_endpoint_starts_upload_directly(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/upload/confirm", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"Uploading" in resp.data
        mock_pubsub.publish.assert_called_once()

    def test_section_endpoint_returns_init(self, client):
        resp = client.get("/board/dev/ttyACM0/upload/section")
        assert resp.status_code == 200
        assert b"Ready" in resp.data
        assert b"upload-section" in resp.data

    def test_confirm_offline_returns_offline_msg(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = False
        tools.pubsub = mock_pubsub
        resp = client.post("/board/dev/ttyACM0/upload/confirm", data={
            "sketch_path": "/tmp/sketch",
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"offline" in resp.data
        assert b"BoardManagerService" in resp.data

    def test_upload_warns_on_checksum_mismatch(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = 99999999
        checksum = tools._compute_sketch_checksum(str(sketch_dir))
        with tools._last_compile_checksum_lock:
            tools._last_compile_checksum["/dev/ttyACM0"] = "different" + checksum[6:]
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": str(sketch_dir),
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"Warnings detected" in resp.data
        mock_pubsub.publish.assert_not_called()

    def test_upload_tracks_sketch_path(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch.pop("/dev/ttyACM0", None)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime.pop("/dev/ttyACM0", None)
        with tools._last_compile_checksum_lock:
            tools._last_compile_checksum.pop("/dev/ttyACM0", None)
        resp = client.post("/board/dev/ttyACM0/upload", data={
            "sketch_path": str(sketch_dir),
            "fqbn": "arduino:avr:uno",
        })
        assert resp.status_code == 200
        assert b"Uploading" in resp.data
        with tools._last_uploaded_sketch_lock:
            tracked = tools._last_uploaded_sketch.get("/dev/ttyACM0")
        assert tracked == str(sketch_dir)


class TestCompileWarning:
    def test_poll_sets_warning_on_error_when_sketch_modified(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = 1000000
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "compile_failed",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Sketch modified on disk" in resp.data

    def test_poll_no_warning_when_sketch_not_modified(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        current_mtime = tools._get_sketch_mtime(str(sketch_dir))
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = current_mtime + 1000
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "compile_failed",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Sketch modified on disk" not in resp.data

    def test_poll_no_warning_when_no_history(self, client, tools):
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "compile_failed",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Sketch modified on disk" not in resp.data

    def test_poll_sets_warning_on_checksum_mismatch(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = 99999999
        checksum = tools._compute_sketch_checksum(str(sketch_dir))
        with tools._last_compile_checksum_lock:
            tools._last_compile_checksum["/dev/ttyACM0"] = "different" + checksum[6:]
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "compile_failed",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Sketch modified on disk" in resp.data

    def test_poll_no_warning_when_checksum_matches(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        ino = sketch_dir / "main.ino"
        ino.write_text("void setup() {}")
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        current_mtime = tools._get_sketch_mtime(str(sketch_dir))
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = (current_mtime or 0) + 100000
        checksum = tools._compute_sketch_checksum(str(sketch_dir))
        with tools._last_compile_checksum_lock:
            tools._last_compile_checksum["/dev/ttyACM0"] = checksum
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "compile_failed",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Sketch modified on disk" not in resp.data


class TestSketchUpload:
    def test_upload_accepts_files(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data = {
                "files[]": [
                    (io.BytesIO(b"void setup() {}"), "blinky/blinky.ino"),
                    (io.BytesIO(b"int main() {}"), "blinky/src/main.cpp"),
                ],
            }
            resp = client.post("/api/sketch/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        result = resp.get_json()
        assert result is not None
        sketch_dir = result["path"]
        assert os.path.isdir(sketch_dir)
        assert sketch_dir.endswith("/blinky")
        ino_path = os.path.join(sketch_dir, "blinky.ino")
        cpp_path = os.path.join(sketch_dir, "src", "main.cpp")
        assert os.path.isfile(ino_path)
        assert os.path.isfile(cpp_path)
        with open(ino_path) as f:
            assert f.read() == "void setup() {}"

    def test_upload_creates_meta(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data = {
                "files[]": [
                    (io.BytesIO(b"void setup() {}"), "blinky/blinky.ino"),
                ],
            }
            resp = client.post("/api/sketch/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        result = resp.get_json()
        sketch_dir = result["path"]
        upload_root = os.path.dirname(sketch_dir)
        meta_path = os.path.join(upload_root, ".meta")
        assert os.path.isfile(meta_path)
        with open(meta_path) as f:
            meta = json.load(f)
        assert "ip" in meta
        assert "user_agent" in meta
        assert "server_timestamp" in meta
        assert "hardware_ids" in meta
        assert "board_timestamps" in meta
        assert meta["file_count"] == 1
        assert meta["total_size"] > 0
        assert meta["root_name"] == "blinky"

    def test_upload_returns_path(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data = {
                "files[]": [
                    (io.BytesIO(b"void setup() {}"), "sketch/sketch.ino"),
                ],
            }
            resp = client.post("/api/sketch/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        result = resp.get_json()
        assert "path" in result
        assert result["path"].startswith(str(tmp_path))
        assert result["path"].endswith("/sketch")
        assert os.path.isdir(result["path"])

    def test_upload_rejects_empty(self, client):
        resp = client.post("/api/sketch/upload", data={}, content_type="multipart/form-data")
        assert resp.status_code == 400
        result = resp.get_json()
        assert result is not None
        assert "error" in result

    def test_upload_htmx_returns_html(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data = {"files[]": [(io.BytesIO(b"void setup() {}"), "blinky/blinky.ino")]}
            resp = client.post(
                "/sketch/upload", data=data,
                content_type="multipart/form-data",
                headers={"HX-Request": "true"},
            )
        assert resp.status_code == 200
        assert resp.content_type == "text/html; charset=utf-8"
        html = resp.data.decode()
        assert '<select name="sketch_path" id="sketch_path">' in html
        assert "blinky" in html

    def test_upload_htmx_empty_returns_html(self, client):
        resp = client.post(
            "/sketch/upload", data={},
            content_type="multipart/form-data",
            headers={"HX-Request": "true"},
        )
        assert resp.status_code == 200
        assert resp.content_type == "text/html; charset=utf-8"
        html = resp.data.decode()
        assert '<select name="sketch_path" id="sketch_path">' in html
        assert "Select a sketch..." in html

    def test_dedup_same_content_returns_same_path(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data1 = {"files[]": [(io.BytesIO(b"void setup() {}"), "blinky/blinky.ino")]}
            resp1 = client.post("/api/sketch/upload", data=data1, content_type="multipart/form-data")
            path1 = resp1.get_json()["path"]
            data2 = {"files[]": [(io.BytesIO(b"void setup() {}"), "blinky/blinky.ino")]}
            resp2 = client.post("/api/sketch/upload", data=data2, content_type="multipart/form-data")
            path2 = resp2.get_json()["path"]
        assert path1 == path2
        assert os.path.isdir(path1)

    def test_dedup_new_version_on_content_change(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data1 = {"files[]": [(io.BytesIO(b"void setup() {}"), "blinky/blinky.ino")]}
            path1 = client.post("/api/sketch/upload", data=data1, content_type="multipart/form-data").get_json()["path"]
            data2 = {"files[]": [(io.BytesIO(b"void setup() { pinMode(13, OUTPUT); }"), "blinky/blinky.ino")]}
            path2 = client.post("/api/sketch/upload", data=data2, content_type="multipart/form-data").get_json()["path"]
        assert path1 != path2
        assert os.path.isdir(path1)
        assert os.path.isdir(path2)
        assert path1.endswith("/blinky")
        assert path2.endswith("/blinky")

    def test_dedup_fresh_name_creates_new(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data_a = {"files[]": [(io.BytesIO(b"// a"), "a/a.ino")]}
            data_b = {"files[]": [(io.BytesIO(b"// b"), "b/b.ino")]}
            path_a = client.post("/api/sketch/upload", data=data_a, content_type="multipart/form-data").get_json()["path"]
            path_b = client.post("/api/sketch/upload", data=data_b, content_type="multipart/form-data").get_json()["path"]
        assert path_a != path_b
        assert path_a.endswith("/a")
        assert path_b.endswith("/b")


class TestLastUpload:
    def setup_method(self):
        _app_module._upload_registry.clear()

    def test_returns_empty_when_no_history(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            resp = client.get("/last-upload")
        assert resp.status_code == 200
        assert resp.content_type == "text/html; charset=utf-8"
        html = resp.data.decode()
        assert '<select name="sketch_path" id="sketch_path">' in html
        assert "Select a sketch..." in html

    def test_returns_path_from_meta_scan_with_root_name(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            upload_root = os.path.join(str(tmp_path), "20260526_120000_blinky")
            sketch_dir = os.path.join(upload_root, "blinky")
            os.makedirs(sketch_dir)
            meta = {"ip": "127.0.0.1", "timestamp": "2026-05-26T12:00:00",
                    "file_count": 1, "root_name": "blinky",
                    "user_agent": "Werkzeug/3.1.8"}
            with open(os.path.join(upload_root, ".meta"), "w") as mf:
                json.dump(meta, mf)
            resp = client.get("/last-upload")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert f'value="{sketch_dir}"' in html

    def test_returns_path_from_meta_scan_fallback(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            upload_root = os.path.join(str(tmp_path), "20260526_120000_other")
            sketch_dir = os.path.join(upload_root, "other")
            os.makedirs(sketch_dir)
            meta = {"ip": "127.0.0.1", "timestamp": "2026-05-26T12:00:00",
                    "file_count": 1, "root_name": "other",
                    "user_agent": "Werkzeug/3.1.8"}
            with open(os.path.join(upload_root, ".meta"), "w") as mf:
                json.dump(meta, mf)
            resp = client.get("/last-upload")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert f'value="{sketch_dir}"' in html

    def test_skips_meta_with_mismatched_ip(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            upload_root = os.path.join(str(tmp_path), "20260526_120000_other")
            os.makedirs(upload_root)
            meta = {"ip": "10.0.0.1", "file_count": 1}
            with open(os.path.join(upload_root, ".meta"), "w") as mf:
                json.dump(meta, mf)
            resp = client.get("/last-upload")
            html = resp.data.decode()
            assert '<select name="sketch_path" id="sketch_path">' in html
            assert "Select a sketch..." in html

    def test_chooses_newest_meta_when_multiple_match(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            older_root = os.path.join(str(tmp_path), "20260525_120000_old")
            older_sketch = os.path.join(older_root, "old")
            os.makedirs(older_sketch)
            with open(os.path.join(older_root, ".meta"), "w") as mf:
                json.dump({"ip": "127.0.0.1", "timestamp": "2026-05-25T12:00:00",
                           "root_name": "old", "user_agent": "Werkzeug/3.1.8"}, mf)
            newer_root = os.path.join(str(tmp_path), "20260526_120000_new")
            newer_sketch = os.path.join(newer_root, "new")
            os.makedirs(newer_sketch)
            with open(os.path.join(newer_root, ".meta"), "w") as mf:
                json.dump({"ip": "127.0.0.1", "timestamp": "2026-05-26T12:00:00",
                           "root_name": "new", "user_agent": "Werkzeug/3.1.8"}, mf)
            resp = client.get("/last-upload")
            html = resp.data.decode()
            assert f'value="{newer_sketch}"' in html
            assert f'value="{older_sketch}"' in html

    def test_skips_corrupt_meta(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            upload_root = os.path.join(str(tmp_path), "20260526_120000_corrupt")
            os.makedirs(upload_root)
            with open(os.path.join(upload_root, ".meta"), "w") as mf:
                mf.write("not json")
            resp = client.get("/last-upload")
            html = resp.data.decode()
            assert '<select name="sketch_path" id="sketch_path">' in html
            assert "Select a sketch..." in html

    def test_returns_200_when_registry_populated(self, client, tmp_path):
        sketch_dir = os.path.join(str(tmp_path), "mysketch")
        os.makedirs(sketch_dir)
        _app_module._upload_registry[("127.0.0.1", "test-agent")] = {
            "mysketch": [{
                "path": sketch_dir,
                "checksum": "abc123",
                "server_timestamp": "2026-05-29T12:00:00",
                "hardware_ids": [],
                "board_timestamps": {},
            }]
        }
        resp = client.get("/last-upload", headers={"User-Agent": "test-agent"})
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "mysketch" in html


class TestApiSketches:
    def test_returns_sketches_for_ip_ua(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data = {"files[]": [(io.BytesIO(b"void setup() {}"), "blinky/blinky.ino")]}
            client.post("/api/sketch/upload", data=data, content_type="multipart/form-data")
            data2 = {"files[]": [(io.BytesIO(b"int x = 1;"), "other/other.ino")]}
            client.post("/api/sketch/upload", data=data2, content_type="multipart/form-data")
            resp = client.get("/api/sketches")
        assert resp.status_code == 200
        sketches = resp.get_json()
        assert isinstance(sketches, list)
        names = [s["name"] for s in sketches]
        assert "blinky" in names
        assert "other" in names
        assert all("path" in s for s in sketches)

    def test_returns_empty_list_when_no_entries(self, client, tmp_path):
        _app_module._upload_registry.clear()
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            resp = client.get("/api/sketches")
        assert resp.status_code == 200
        assert resp.get_json() == []


class TestRenderSketchPathSelector:
    def test_renders_empty_selector(self, req_ctx):
        html = _app_module._render_sketch_path_selector()
        assert 'name="sketch_path"' in html
        assert 'id="sketch_path"' in html
        assert "Select a sketch..." in html

    def test_renders_with_selected_path(self, req_ctx, tmp_path):
        sketch_dir = os.path.join(str(tmp_path), "mysketch")
        html = _app_module._render_sketch_path_selector(sketch_dir)
        assert f'value="{sketch_dir}"' in html

    def test_escapes_html_in_path(self, req_ctx, tmp_path):
        bad_path = '/path/<script>alert(1)</script>'
        html = _app_module._render_sketch_path_selector(bad_path)
        assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html


class TestMakeMetaSketchName:
    def test_includes_sketch_name(self):
        meta = _app_module._make_meta("/dev/ttyACM0", "/path/to/sketches/blinky")
        assert meta["sketch_name"] == "blinky"

    def test_empty_sketch_path(self):
        meta = _app_module._make_meta("/dev/ttyACM0", "")
        assert meta["sketch_name"] == ""

    def test_root_path_sketch_name(self):
        meta = _app_module._make_meta("/dev/ttyACM0", "/blinky")
        assert meta["sketch_name"] == "blinky"


class TestNormalizeInoFilename:
    def test_renames_mismatched_ino(self, tmp_path):
        sketch_dir = tmp_path / "mysketch"
        sketch_dir.mkdir()
        (sketch_dir / "other.ino").write_text("void setup() {}")
        _app_module._normalize_ino_filename(str(sketch_dir), "mysketch")
        assert not (sketch_dir / "other.ino").exists()
        assert (sketch_dir / "mysketch.ino").exists()
        assert (sketch_dir / "mysketch.ino").read_text() == "void setup() {}"

    def test_skips_already_correct(self, tmp_path):
        sketch_dir = tmp_path / "mysketch"
        sketch_dir.mkdir()
        (sketch_dir / "mysketch.ino").write_text("void setup() {}")
        _app_module._normalize_ino_filename(str(sketch_dir), "mysketch")
        assert (sketch_dir / "mysketch.ino").exists()
        assert len(list(sketch_dir.iterdir())) == 1

    def test_skips_no_ino_files(self, tmp_path):
        sketch_dir = tmp_path / "mysketch"
        sketch_dir.mkdir()
        (sketch_dir / "README.txt").write_text("readme")
        _app_module._normalize_ino_filename(str(sketch_dir), "mysketch")
        assert (sketch_dir / "README.txt").exists()
        assert len(list(sketch_dir.iterdir())) == 1

    def test_skips_multiple_ino_files(self, tmp_path):
        sketch_dir = tmp_path / "mysketch"
        sketch_dir.mkdir()
        (sketch_dir / "a.ino").write_text("// a")
        (sketch_dir / "b.ino").write_text("// b")
        _app_module._normalize_ino_filename(str(sketch_dir), "mysketch")
        assert (sketch_dir / "a.ino").exists()
        assert (sketch_dir / "b.ino").exists()

    def test_handles_nested_ino(self, tmp_path):
        sketch_dir = tmp_path / "mysketch"
        sub = sketch_dir / "src"
        sub.mkdir(parents=True)
        (sub / "lib.ino").write_text("// lib")
        _app_module._normalize_ino_filename(str(sketch_dir), "mysketch")
        assert (sub / "lib.ino").exists()

    def test_handles_nonexistent_dir(self, tmp_path):
        sketch_dir = tmp_path / "nonexistent"
        _app_module._normalize_ino_filename(str(sketch_dir), "mysketch")
        assert not sketch_dir.exists()


class TestSketchDelete:
    def setup_method(self):
        _app_module._upload_registry.clear()

    def test_delete_existing_sketch(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            upload_root = os.path.join(str(tmp_path), "20260529_120000_blinky")
            sketch_dir = os.path.join(upload_root, "blinky")
            os.makedirs(sketch_dir)
            open(os.path.join(sketch_dir, "blinky.ino"), "w").close()
            meta_path = os.path.join(upload_root, ".meta")
            with open(meta_path, "w") as f:
                json.dump({"ip": "127.0.0.1", "timestamp": "2026-05-29T12:00:00",
                           "root_name": "blinky", "user_agent": "Werkzeug/3.1.8"}, f)
            _app_module._warm_upload_registry()
            resp = client.delete("/api/sketch", query_string={"path": sketch_dir})
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "deleted"}
        assert not os.path.isdir(sketch_dir)
        assert not os.path.isfile(meta_path)

    def test_delete_missing_path(self, client):
        resp = client.delete("/api/sketch")
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Missing path"}

    def test_delete_invalid_path(self, client):
        resp = client.delete("/api/sketch", query_string={"path": "/etc/passwd"})
        assert resp.status_code == 403
        assert resp.get_json() == {"error": "Invalid path"}

    def test_delete_not_found(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            sketch_dir = os.path.join(str(tmp_path), "blinky")
            os.makedirs(sketch_dir)
            resp = client.delete("/api/sketch", query_string={"path": sketch_dir})
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Not found"}


class TestSketchVersionListing:
    def setup_method(self):
        _app_module._upload_registry.clear()

    def test_selector_shows_timestamp(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            upload_root = os.path.join(str(tmp_path), "20260529_120000_blinky")
            sketch_dir = os.path.join(upload_root, "blinky")
            os.makedirs(sketch_dir)
            with open(os.path.join(upload_root, ".meta"), "w") as f:
                json.dump({"ip": "127.0.0.1", "timestamp": "2026-05-29T12:00:00",
                           "root_name": "blinky", "user_agent": "Werkzeug/3.1.8"}, f)
            _app_module._warm_upload_registry()
            resp = client.get("/last-upload")
        html = resp.data.decode()
        import re
        assert re.search(r"blinky \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\)", html)

    def test_api_sketches_returns_all_versions(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data = {"files[]": [(io.BytesIO(b"void setup() {}"), "blinky/blinky.ino")]}
            client.post("/api/sketch/upload", data=data, content_type="multipart/form-data")
            resp = client.get("/api/sketches")
        sketches = resp.get_json()
        assert isinstance(sketches, list)
        assert len(sketches) >= 1
        assert all("name" in s and "path" in s and "timestamp" in s for s in sketches)


class TestDedupAcrossVersions:
    def setup_method(self):
        _app_module._upload_registry.clear()

    def test_same_content_dedup_across_names(self, client, tmp_path):
        with patch("arduino_dash.state.UPLOAD_BASE_DIR", str(tmp_path)):
            data = {"files[]": [(io.BytesIO(b"void setup() {}"), "blinky/blinky.ino")]}
            resp1 = client.post("/api/sketch/upload", data=data, content_type="multipart/form-data")
            path1 = resp1.get_json()["path"]
            data2 = {"files[]": [(io.BytesIO(b"void setup() {}"), "other/other.ino")]}
            resp2 = client.post("/api/sketch/upload", data=data2, content_type="multipart/form-data")
            path2 = resp2.get_json()["path"]
        assert path1 == path2
        assert os.path.isdir(path1)
        assert not os.path.isdir(os.path.join(os.path.dirname(path1), "other"))


class TestAdminRoutes:
    def test_admin_page_returns_200(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "hardware_id": "HWB-123",
            }
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"Admin" in resp.data

    def test_admin_active_board_swaps_fqbn_and_hardware_id(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "hardware_id": "HWB-123",
            }
        with client.session_transaction() as sess:
            sess["admin_active_board"] = "/dev/ttyACM0"
        resp = client.post("/admin/active-board", data={"port": "/dev/ttyACM0"})
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'hx-swap-oob="true"' in html
        assert "arduino:avr:uno" in html
        assert "HWB-123" in html

    def test_admin_board_selector_renders_no_boards(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
        resp = client.get("/admin/board-selector")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'admin-board-selector-card' in html or 'id="admin-board-selector-card"' in html
        assert 'admin-active-board' in html or 'id="admin-active-board"' in html

    def test_board_compile_upload_card_renders(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno", "hardware_id": "HWB-123",
            }
        with client.session_transaction() as sess:
            sess["admin_active_board"] = ("/dev/ttyACM0", "arduino:avr:uno", "HWB-123")
        resp = client.get("/board/compile-upload-card")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "/board/dev/ttyACM0/compile" in html
        assert "/board/dev/ttyACM0/upload" in html

    def test_admin_page_auto_selects_first_board(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno",
            }
            _app_module._board_list["/dev/ttyACM1"] = {
                "port": "/dev/ttyACM1", "board": "Arduino Mega", "fqbn": "arduino:avr:mega",
            }
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"compile-upload-card" in resp.data
        assert b"admin-board-selector-container" in resp.data

    def test_admin_page_no_boards_still_renders(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert b"Admin" in resp.data


class TestBoardDetail:
    def test_heading_shows_board_name(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno",
            }
        resp = client.get("/board/dev/ttyACM0")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Board: Arduino Uno" in html

    def test_heading_falls_back_to_port(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
        resp = client.get("/board/dev/ttyACM0")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Board: /dev/ttyACM0" in html

    def test_fqbn_display_label_present(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno",
            }
        resp = client.get("/board/dev/ttyACM0")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'id="fqbn-display"' in html
        assert 'class="value"' in html
        assert "arduino:avr:uno" in html
        assert '<input type="hidden" id="fqbn" name="fqbn"' in html

    def test_port_display_label_present(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno",
            }
        resp = client.get("/board/dev/ttyACM0")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'id="port-display"' in html
        assert "Device Port" in html
        assert "/dev/ttyACM0" in html


class TestDashboard:
    def test_dashboard_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200


class TestBoardsGrid:
    def test_empty_board_list(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
        resp = client.get("/boards/grid")
        assert resp.status_code == 200

    def test_with_boards(self, client):
        with _app_module._board_list_lock:
            _app_module._board_list.clear()
            _app_module._board_list["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0", "board": "Arduino Uno", "fqbn": "arduino:avr:uno",
            }
            _app_module._board_list["/dev/ttyACM1"] = {
                "port": "/dev/ttyACM1", "board": "Arduino Mega", "fqbn": "arduino:avr:mega",
            }
        resp = client.get("/boards/grid")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "/dev/ttyACM0" in html
        assert "/dev/ttyACM1" in html
        assert "Arduino Uno" in html
        assert "Arduino Mega" in html


class TestApiBoardSpawn:
    def test_spawn_returns_accepted(self, client):
        mock_pubsub = MagicMock()
        with patch("arduino_dash.state.pubsub", mock_pubsub):
            resp = client.post("/api/board/dev/ttyACM0/spawn")
            assert resp.status_code == 200
            assert resp.get_json() == {"status": "accepted"}


class TestApiBoardStatus:
    def test_status_returns_accepted(self, client):
        mock_pubsub = MagicMock()
        with patch("arduino_dash.state.pubsub", mock_pubsub):
            resp = client.get("/api/board/dev/ttyACM0/status")
            assert resp.status_code == 200
            assert resp.get_json() == {"status": "accepted"}


class TestApiBoardRemove:
    def test_remove_returns_accepted(self, client):
        mock_pubsub = MagicMock()
        with patch("arduino_dash.state.pubsub", mock_pubsub):
            resp = client.post("/api/board/dev/ttyACM0/remove")
            assert resp.status_code == 200
            assert resp.get_json() == {"status": "accepted"}


class TestApiBoardList:
    def test_list_returns_accepted(self, client):
        mock_pubsub = MagicMock()
        with patch("arduino_dash.state.pubsub", mock_pubsub):
            resp = client.get("/api/boards")
            assert resp.status_code == 200
            assert resp.get_json() == {"status": "accepted"}


class TestNormalizePort:
    def test_normalizes_with_dev_prefix(self):
        from arduino_dash.utils import normalize_port
        assert normalize_port("dev/ttyACM0") == "/dev/ttyACM0"

    def test_strips_extra_slashes(self):
        from arduino_dash.utils import normalize_port
        assert normalize_port("//dev/ttyACM0") == "/dev/ttyACM0"

    def test_keeps_valid(self):
        from arduino_dash.utils import normalize_port
        assert normalize_port("/dev/ttyACM0") == "/dev/ttyACM0"

    def test_rejects_empty(self):
        from arduino_dash.utils import normalize_port
        assert normalize_port("") is None

    def test_rejects_bare_port(self):
        from arduino_dash.utils import normalize_port
        assert normalize_port("ttyACM0") is None  # /ttyACM0 doesn't match /dev/...

    def test_rejects_non_dev_path(self):
        from arduino_dash.utils import normalize_port
        assert normalize_port("COM1") is None
        assert normalize_port("/random/path") is None
