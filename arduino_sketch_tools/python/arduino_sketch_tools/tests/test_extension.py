"""Tests for ArduinoSketchTools Flask Extension"""

from unittest.mock import MagicMock

import pytest
from flask import Flask

from arduino_sketch_tools import ArduinoSketchTools


@pytest.fixture
def app():
    _app = Flask(__name__)
    _app.config["TESTING"] = True
    return _app


@pytest.fixture(autouse=True)
def _clear_caches(tools):
    with tools._compile_results_lock:
        tools._compile_results.clear()
    with tools._upload_results_lock:
        tools._upload_results.clear()
    with tools._compile_meta_lock:
        tools._compile_meta.clear()
    with tools._upload_meta_lock:
        tools._upload_meta.clear()
    with tools._last_compiled_sketch_lock:
        tools._last_compiled_sketch.clear()
    with tools._last_compile_mtime_lock:
        tools._last_compile_mtime.clear()
    with tools._last_compile_checksum_lock:
        tools._last_compile_checksum.clear()
    with tools._last_uploaded_sketch_lock:
        tools._last_uploaded_sketch.clear()
    with tools._compile_last_pct_lock:
        tools._compile_last_pct.clear()
    yield


@pytest.fixture
def tools(app):
    ext = ArduinoSketchTools(broadcast_ws=lambda h: None, get_board_info=lambda p: {})
    ext.init_app(app)
    return ext


@pytest.fixture
def client(app, tools):
    with app.test_client() as c:
        yield c


class TestArduinoSketchTools:
    def test_init_sets_defaults(self):
        ext = ArduinoSketchTools()
        assert ext.pubsub is None
        assert ext._compile_results == {}
        assert ext._upload_results == {}

    def test_init_app_registers_blueprint(self):
        _app = Flask(__name__)
        ext = ArduinoSketchTools(
            broadcast_ws=lambda h: None, get_board_info=lambda p: {}
        )
        ext.init_app(_app)
        assert "arduino_sketch_tools" in _app.extensions
        assert "arduino_sketch_tools" in _app.blueprints

    def test_init_app_with_pubsub_subscribes(self):
        _app = Flask(__name__)
        mock_pubsub = MagicMock()
        ext = ArduinoSketchTools(
            broadcast_ws=lambda h: None, get_board_info=lambda p: {}
        )
        ext.init_app(_app, pubsub=mock_pubsub)
        mock_pubsub.subscribe.assert_any_call("resp::compile::*", ext._on_compile_resp)
        mock_pubsub.subscribe.assert_any_call("resp::upload::*", ext._on_upload_resp)


class TestOnCompileResp:
    def test_stores_result(self, tools):
        topic = "resp::compile::/dev/ttyACM0"
        tools._on_compile_resp(
            {"topic": topic, "status": "ok", "data": {"output": "ok"}}
        )
        with tools._compile_results_lock:
            cached = tools._compile_results.get("/dev/ttyACM0")
        assert cached is not None
        assert cached["status"] == "ok"

    def test_progress_broadcasts_via_ws(self, tools):
        ws_html = []
        tools._broadcast_ws = lambda h: ws_html.append(h)
        topic = "resp::compile::/dev/ttyACM0::progress"
        tools._on_compile_resp(
            {
                "topic": topic,
                "data": {"output": "Compiling foo.c...\n", "percent": 25.0},
            }
        )
        assert len(ws_html) == 2
        assert "compile-progress" in ws_html[0]
        assert 'value="25"' in ws_html[0]
        assert "compile-line" in ws_html[1]
        assert "foo.c" in ws_html[1]
        assert "[25%]" in ws_html[1]
        assert "/dev/ttyACM0" in ws_html[1]

    def test_progress_no_output_broadcasts_progress_bar(self, tools):
        ws_html = []
        tools._broadcast_ws = lambda h: ws_html.append(h)
        topic = "resp::compile::/dev/ttyACM0::progress"
        tools._on_compile_resp(
            {"topic": topic, "data": {"output": "", "error": "", "percent": 50.0}}
        )
        assert len(ws_html) == 1
        assert "compile-progress" in ws_html[0]

    def test_progress_escapes_html(self, tools):
        ws_html = []
        tools._broadcast_ws = lambda h: ws_html.append(h)
        topic = "resp::compile::/dev/ttyACM0::progress"
        tools._on_compile_resp(
            {
                "topic": topic,
                "data": {"output": "<script>alert('xss')</script>", "percent": 0.0},
            }
        )
        assert len(ws_html) == 2
        assert "compile-progress" in ws_html[0]
        assert "compile-line" in ws_html[1]
        assert "&lt;script&gt;" in ws_html[1]
        assert "<script>" not in ws_html[1]

    def test_ok_stores_last_compiled_state(self, tools, tmp_path):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        (sketch_dir / "main.ino").write_text("void setup() {}")
        topic = "resp::compile::/dev/ttyACM0"
        tools._on_compile_resp(
            {
                "topic": topic,
                "status": "ok",
                "data": {"sketch_path": str(sketch_dir), "output": "ok"},
            }
        )
        with tools._last_compiled_sketch_lock:
            assert tools._last_compiled_sketch.get("/dev/ttyACM0") == str(sketch_dir)
        with tools._last_compile_mtime_lock:
            mtime = tools._last_compile_mtime.get("/dev/ttyACM0")
        assert mtime is not None

    def test_ignores_other_topics(self, tools):
        ws_html = []
        tools._broadcast_ws = lambda h: ws_html.append(h)
        tools._on_compile_resp({"topic": "sys::health", "data": {}})
        assert len(ws_html) == 0
        with tools._compile_results_lock:
            assert tools._compile_results == {}


class TestOnUploadResp:
    def test_stores_result(self, tools):
        topic = "resp::upload::/dev/ttyACM0"
        tools._on_upload_resp(
            {"topic": topic, "status": "ok", "data": {"output": "uploaded"}}
        )
        with tools._upload_results_lock:
            cached = tools._upload_results.get("/dev/ttyACM0")
        assert cached is not None
        assert cached["status"] == "ok"

    def test_progress_broadcasts_via_ws(self, tools):
        ws_html = []
        tools._broadcast_ws = lambda h: ws_html.append(h)
        topic = "resp::upload::/dev/ttyACM0::progress"
        tools._on_upload_resp({"topic": topic, "data": {"output": "Uploading...\n"}})
        assert len(ws_html) == 1
        assert "upload-line" in ws_html[0]
        assert "Uploading" in ws_html[0]
        assert "/dev/ttyACM0" in ws_html[0]

    def test_progress_escapes_html(self, tools):
        ws_html = []
        tools._broadcast_ws = lambda h: ws_html.append(h)
        topic = "resp::upload::/dev/ttyACM0::progress"
        tools._on_upload_resp({"topic": topic, "data": {"output": "<b>bold</b>"}})
        assert len(ws_html) == 1
        assert "&lt;b&gt;" in ws_html[0]

    def test_ignores_other_topics(self, tools):
        tools._on_upload_resp({"topic": "resp::compile::/dev/ttyACM0", "data": {}})
        with tools._upload_results_lock:
            assert tools._upload_results == {}


class TestApiCompile:
    def test_publishes_and_shows_in_progress(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        tools.pubsub = mock_pubsub
        resp = client.post(
            "/board/dev/ttyACM0/compile",
            data={
                "sketch_path": "/tmp/sketch",
                "fqbn": "arduino:avr:uno",
                "verbose": "true",
            },
        )
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

    def test_poll_returns_error(self, client, tools):
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "fail",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Compile error" in resp.data

    def test_offline_returns_offline_msg(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = False
        tools.pubsub = mock_pubsub
        resp = client.post(
            "/board/dev/ttyACM0/compile",
            data={
                "sketch_path": "/tmp/sketch",
                "fqbn": "arduino:avr:uno",
            },
        )
        assert resp.status_code == 200
        assert b"offline" in resp.data
        mock_pubsub.publish.assert_not_called()


class TestApiUpload:
    def test_publishes_and_shows_in_progress(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        tools.pubsub = mock_pubsub
        resp = client.post(
            "/board/dev/ttyACM0/upload",
            data={
                "sketch_path": "/tmp/sketch",
                "fqbn": "arduino:avr:uno",
                "verbose": "true",
            },
        )
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

    def test_poll_returns_error(self, client, tools):
        with tools._upload_results_lock:
            tools._upload_results["/dev/ttyACM0"] = {
                "topic": "resp::upload::/dev/ttyACM0",
                "status": "error",
                "code": "fail",
                "message": "Cannot open port",
                "data": {"error": "upload failed"},
            }
        resp = client.get("/board/dev/ttyACM0/upload/poll")
        assert resp.status_code == 200
        assert b"Upload error" in resp.data


class TestCompileMeta:
    def test_stores_meta_on_compile(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        tools._get_board_info = lambda p: {
            "port": p,
            "board": "Arduino Uno",
            "fqbn": "arduino:avr:uno",
        }
        resp = client.post(
            "/board/dev/ttyACM0/compile",
            data={
                "sketch_path": "/tmp/sketch",
                "fqbn": "arduino:avr:uno",
            },
        )
        assert resp.status_code == 200
        with tools._compile_meta_lock:
            meta = tools._compile_meta.get("/dev/ttyACM0")
        assert meta is not None
        assert meta["port"] == "/dev/ttyACM0"
        assert meta["board"] == "Arduino Uno"

    def test_meta_cleared_on_poll(self, client, tools):
        with tools._compile_meta_lock:
            tools._compile_meta["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "avr:uno",
                "sketch": "/s",
            }
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "ok",
                "data": {"output": "ok"},
            }
        client.get("/board/dev/ttyACM0/compile/poll")
        with tools._compile_meta_lock:
            assert "/dev/ttyACM0" not in tools._compile_meta


class TestUploadMeta:
    def test_stores_meta_on_upload(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.publish.return_value = None
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        tools._get_board_info = lambda p: {
            "port": p,
            "board": "Uno",
            "fqbn": "arduino:avr:uno",
        }
        resp = client.post(
            "/board/dev/ttyACM0/upload",
            data={
                "sketch_path": "/tmp/sketch",
                "fqbn": "arduino:avr:uno",
            },
        )
        assert resp.status_code == 200
        with tools._upload_meta_lock:
            meta = tools._upload_meta.get("/dev/ttyACM0")
        assert meta is not None
        assert meta["port"] == "/dev/ttyACM0"
        assert meta["board"] == "Uno"

    def test_meta_cleared_on_poll(self, client, tools):
        with tools._upload_meta_lock:
            tools._upload_meta["/dev/ttyACM0"] = {
                "port": "/dev/ttyACM0",
                "board": "Uno",
                "fqbn": "avr:uno",
                "sketch": "/s",
            }
        with tools._upload_results_lock:
            tools._upload_results["/dev/ttyACM0"] = {
                "topic": "resp::upload::/dev/ttyACM0",
                "status": "ok",
                "data": {"output": "ok"},
            }
        client.get("/board/dev/ttyACM0/upload/poll")
        with tools._upload_meta_lock:
            assert "/dev/ttyACM0" not in tools._upload_meta


class TestUploadConfirmWarnings:
    def test_sketch_path_change_returns_confirm(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = "/old/sketch"
        resp = client.post(
            "/board/dev/ttyACM0/upload",
            data={
                "sketch_path": "/new/sketch",
                "fqbn": "arduino:avr:uno",
            },
        )
        assert resp.status_code == 200
        assert b"Warnings detected" in resp.data
        assert b"Sketch path changed" in resp.data
        mock_pubsub.publish.assert_not_called()

    def test_confirm_endpoint_starts_upload(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        resp = client.post(
            "/board/dev/ttyACM0/upload/confirm",
            data={
                "sketch_path": "/tmp/sketch",
                "fqbn": "arduino:avr:uno",
            },
        )
        assert resp.status_code == 200
        assert b"Uploading" in resp.data
        mock_pubsub.publish.assert_called_once()

    def test_section_endpoint_returns_init(self, client, tools):
        resp = client.get("/board/dev/ttyACM0/upload/section")
        assert resp.status_code == 200
        assert b"Ready" in resp.data

    def test_confirm_offline_returns_offline_msg(self, client, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = False
        tools.pubsub = mock_pubsub
        resp = client.post(
            "/board/dev/ttyACM0/upload/confirm",
            data={
                "sketch_path": "/tmp/sketch",
                "fqbn": "arduino:avr:uno",
            },
        )
        assert resp.status_code == 200
        assert b"offline" in resp.data

    def test_sketch_modified_returns_confirm(self, client, tmp_path, tools):
        mock_pubsub = MagicMock()
        mock_pubsub.is_connected = True
        tools.pubsub = mock_pubsub
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        (sketch_dir / "main.ino").write_text("void setup() {}")
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = 1000000
        resp = client.post(
            "/board/dev/ttyACM0/upload",
            data={
                "sketch_path": str(sketch_dir),
                "fqbn": "arduino:avr:uno",
            },
        )
        assert resp.status_code == 200
        assert b"Warnings detected" in resp.data
        mock_pubsub.publish.assert_not_called()


class TestCompileWarning:
    def test_poll_shows_warning_when_sketch_modified(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        (sketch_dir / "main.ino").write_text("void setup() {}")
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = 1000000
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "fail",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Sketch modified on disk" in resp.data

    def test_poll_no_warning_when_not_modified(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        (sketch_dir / "main.ino").write_text("void setup() {}")
        mtime = tools._get_sketch_mtime(str(sketch_dir))
        with tools._last_compiled_sketch_lock:
            tools._last_compiled_sketch["/dev/ttyACM0"] = str(sketch_dir)
        with tools._last_compile_mtime_lock:
            tools._last_compile_mtime["/dev/ttyACM0"] = (mtime or 0) + 1000
        with tools._compile_results_lock:
            tools._compile_results["/dev/ttyACM0"] = {
                "topic": "resp::compile::/dev/ttyACM0",
                "status": "error",
                "code": "fail",
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
                "code": "fail",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert b"Sketch modified on disk" not in resp.data

    def test_poll_warning_on_checksum_mismatch(self, client, tmp_path, tools):
        sketch_dir = tmp_path / "sketch"
        sketch_dir.mkdir()
        (sketch_dir / "main.ino").write_text("void setup() {}")
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
                "code": "fail",
                "message": "Build failed",
                "data": {"error": "compilation error"},
            }
        resp = client.get("/board/dev/ttyACM0/compile/poll")
        assert resp.status_code == 200
        assert b"Sketch modified on disk" in resp.data


class TestCompileChecksum:
    def test_returns_deterministic_hash(self, tmp_path, tools):
        d = tmp_path / "s"
        d.mkdir()
        (d / "main.ino").write_text("void setup() {}")
        h1 = tools._compute_sketch_checksum(str(d))
        h2 = tools._compute_sketch_checksum(str(d))
        assert h1 == h2
        assert len(h1) == 64

    def test_empty_dir_returns_empty(self, tmp_path, tools):
        d = tmp_path / "empty"
        d.mkdir()
        assert tools._compute_sketch_checksum(str(d)) == ""

    def test_nonexistent_dir_returns_empty(self, tools):
        assert tools._compute_sketch_checksum("/nonexistent") == ""


class TestGetSketchMtime:
    def test_returns_mtime_for_source_files(self, tmp_path, tools):
        d = tmp_path / "s"
        d.mkdir()
        f = d / "main.ino"
        f.write_text("void setup() {}")
        mtime = tools._get_sketch_mtime(str(d))
        assert mtime is not None
        assert mtime > 0

    def test_missing_dir_returns_none(self, tools):
        assert tools._get_sketch_mtime("/nonexistent") is None

    def test_empty_dir_returns_none(self, tmp_path, tools):
        d = tmp_path / "empty"
        d.mkdir()
        assert tools._get_sketch_mtime(str(d)) is None


class TestMakeMeta:
    def test_includes_sketch_name(self, tools):
        meta = tools._make_meta("/dev/ttyACM0", "/path/to/sketches/blinky")
        assert meta["sketch_name"] == "blinky"

    def test_empty_sketch_path(self, tools):
        meta = tools._make_meta("/dev/ttyACM0", "")
        assert meta["sketch_name"] == ""

    def test_root_path_sketch_name(self, tools):
        meta = tools._make_meta("/dev/ttyACM0", "/blinky")
        assert meta["sketch_name"] == "blinky"

    def test_calls_board_info_callback(self, tools):
        tools._get_board_info = lambda p: {"board": "Uno", "fqbn": "arduino:avr:uno"}
        meta = tools._make_meta("/dev/ttyACM0", "/s")
        assert meta["board"] == "Uno"
        assert meta["fqbn"] == "arduino:avr:uno"


class TestNormPort:
    def test_adds_leading_slash(self, tools):
        assert tools._norm_port("dev/ttyACM0") == "/dev/ttyACM0"

    def test_keeps_existing_slash(self, tools):
        assert tools._norm_port("/dev/ttyACM0") == "/dev/ttyACM0"

    def test_strips_extra_slashes(self, tools):
        assert tools._norm_port("//dev/ttyACM0") == "/dev/ttyACM0"

    def test_rejects_empty(self, tools):
        assert tools._norm_port("") is None

    def test_rejects_bare_port(self, tools):
        assert tools._norm_port("ttyACM0") is None

    def test_rejects_non_dev_path(self, tools):
        assert tools._norm_port("COM1") is None
        assert tools._norm_port("/random/path") is None
