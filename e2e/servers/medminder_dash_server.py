"""Standalone Flask dev server for medminder_dash with optional mock state and BMS.

Usage:
    python3 e2e/servers/medminder_dash_server.py                    # empty state, port 8766
    python3 e2e/servers/medminder_dash_server.py --mock              # with mock board + medicine data
    python3 e2e/servers/medminder_dash_server.py --mock --bms        # with mock data + BMS daemon
    python3 e2e/servers/medminder_dash_server.py --port 9000         # custom port
    python3 e2e/servers/medminder_dash_server.py --stop              # stop a running server
    python3 e2e/servers/medminder_dash_server.py --stop --force      # force-stop
    python3 e2e/servers/medminder_dash_server.py --pidfile /tmp/mypid.pid --stop
"""

import argparse
import atexit
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ── Lifecycle helpers ──────────────────────────────────────────────────────────

def _get_default_pidfile() -> str:
    """Derive a pidfile path from the script name, e.g. /tmp/medminder_dash_server.pid."""
    return f"/tmp/{Path(__file__).stem}.pid"


def _write_pidfile(path: str) -> None:
    """Write current PID to *path*."""
    Path(path).write_text(str(os.getpid()))
    print(f"[server] PID {os.getpid()} written to {path}")


def _remove_pidfile(path: str) -> None:
    """Remove *path* only if it still contains *our* PID (avoid stealing another instance's pidfile)."""
    try:
        current = str(os.getpid())
        if Path(path).read_text().strip() == current:
            Path(path).unlink(missing_ok=True)
    except (OSError, FileNotFoundError, ValueError):
        pass


def _stop_server(pidfile: str, force: bool = False) -> None:
    """Stop a running server by its PID file.

    Sends SIGTERM by default, then polls for up to 5 s. If the process does
    not exit in time, escalates to SIGKILL. With *force*=True, sends SIGKILL
    immediately.
    """
    path = Path(pidfile)
    if not path.exists():
        print(f"[server] No PID file at {pidfile}")
        sys.exit(1)

    pid = int(path.read_text().strip())
    try:
        sig = signal.SIGKILL if force else signal.SIGTERM
        os.kill(pid, sig)
    except ProcessLookupError:
        path.unlink(missing_ok=True)
        print(f"[server] PID {pid} not found — removed stale pidfile")
        sys.exit(0)

    if not force:
        for _ in range(50):          # poll up to 5 s (50 × 100 ms)
            try:
                os.kill(pid, 0)       # check if alive
                time.sleep(0.1)
            except ProcessLookupError:
                break
        else:
            os.kill(pid, signal.SIGKILL)

    path.unlink(missing_ok=True)
    print(f"[server] Stopped PID {pid}")
    sys.exit(0)


def _daemonize(logfile: str | None) -> None:
    """Fork, exit parent, and detach child from the parent session.

    *Parent* — exits immediately (``os._exit(0)``).  The bash tool sees the
    command exit, closes the pipe, and returns.  No timeout → no signal storm.

    *Child*  — calls ``setsid()`` to create a new session, immune from
    SIGHUP when the original shell session leader later dies.  Then redirects
    stdout/stderr to *logfile* (or ``/dev/null``) so Flask output is captured
    and the closed pipe from the parent never triggers SIGPIPE.
    """
    pid = os.fork()
    if pid > 0:
        os._exit(0)
    # ── child continues ─────────────────────────────────────────────────────
    os.setsid()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    dest_path = logfile if logfile else os.devnull
    dest = open(dest_path, "a")
    sys.stdin.close()
    sys.stdout = dest
    sys.stderr = dest
    os.dup2(dest.fileno(), 1)
    os.dup2(dest.fileno(), 2)

    # Log bootstrap messages AFTER redirect so they land in the logfile.
    # The parent's exit above means the terminal saw no output at all —
    # that's expected.


# ── Project paths ─────────────────────────────────────────────────────────────

# Project root is e2e/servers/../..  (up from script -> servers -> e2e -> root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_PYTHON = PROJECT_ROOT / "medminder_dash" / "python"
sys.path.insert(0, str(PACKAGE_PYTHON))

import medminder_dash.state as state
from medminder_dash.app import create_app
from medminder_dash.medicines_state import Medicine, _compute_data_path
from medminder_dash.pubsub_infra import init_pubsub

MOCK_PORT_1 = "/dev/ttyTEST0"
MOCK_PORT_2 = "/dev/ttyTEST1"
MOCK_HW_ID_1 = "HW-TEST-001"
MOCK_HW_ID_2 = "HW-TEST-002"

def _start_bms() -> subprocess.Popen:
    """Start the BMS daemon as a subprocess, return Popen handle."""
    return subprocess.Popen(
        [sys.executable, "-m", "board_manager", "--log-level", "INFO"]
    )


def _stop_bms(proc: subprocess.Popen | None) -> None:
    """Gracefully stop a BMS subprocess, with force fallback."""
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


MOCK_MEDICINES = [
    dict(name="Aspirin", hour=8, minute=0, day_of_week=0, day_of_month=0, enabled=True),
    dict(name="VitaminD", hour=12, minute=30, day_of_week=0, day_of_month=0, enabled=True),
    dict(name="Ibuprofen", hour=18, minute=0, day_of_week=0, day_of_month=0, enabled=True),
]

# Point MedicineStore at a temp file so mock data never pollutes production data
_temp_data_file = Path(tempfile.mkstemp(suffix="board_meta.json")[1])
_temp_data_file.write_text("{}")
_original_data_path = _compute_data_path()

import medminder_dash.medicines_state as ms
ms._compute_data_path = lambda: _temp_data_file

app = create_app()


def _inject_mock_state():
    """Populate known ports, upload registry, and app's medicine store with test data."""
    with state._known_ports_lock:
        state._known_ports[MOCK_PORT_1] = {
            "port": MOCK_PORT_1,
            "board": "TestBoard Uno",
            "fqbn": "arduino:avr:uno",
            "hardware_id": MOCK_HW_ID_1,
        }
        state._known_ports[MOCK_PORT_2] = {
            "port": MOCK_PORT_2,
            "board": "TestBoard Mega",
            "fqbn": "arduino:avr:mega",
            "hardware_id": MOCK_HW_ID_2,
        }

    with state._upload_registry_lock:
        state._upload_registry[("127.0.0.1", "playwright-test")] = {
            "MedMinderV2": [
                {
                    "path": "/tmp/e2e-test/sketches/MedMinderV2",
                    "checksum": "abc123def456",
                    "server_timestamp": "2026-06-19T00:00:00",
                    "hardware_ids": [MOCK_HW_ID_1],
                    "board_timestamps": {MOCK_HW_ID_1: "2026-06-19T01:00:00"},
                },
            ],
        }

    state._daemon_ready = False

    # Inject medicines into the app's store (created by create_app() above)
    import medminder_dash.app as medminder_app
    app_store = medminder_app.store
    app_store._board_meta = {}
    app_store._medicines = []
    app_store._current_port = None
    app_store._data_file = _temp_data_file
    app_store.load_board(MOCK_PORT_1)
    for med_data in MOCK_MEDICINES:
        app_store.add(Medicine(**med_data))
    print(f"[medminder_dash_server] {len(MOCK_MEDICINES)} sample medicines injected for {MOCK_PORT_1}")


def main():
    """Parse args, optionally inject mock state and start BMS, then run the Flask dev server."""
    parser = argparse.ArgumentParser(
        description="Start medminder_dash Flask dev server with optional mock state and BMS"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Inject mock board data, sketch entries, and sample medicines",
    )
    parser.add_argument(
        "--bms",
        action="store_true",
        help="Start the BMS daemon (arduino-cli daemon + board_manager service)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8766,
        help="Port to bind (default: 8766)",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Disable Flask debug mode and reloader (keeps server alive in background)",
    )
    parser.add_argument(
        "--pidfile",
        default=_get_default_pidfile(),
        help="PID file path (default: %(default)s)",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop a running server by its PID file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --stop: send SIGKILL immediately (no graceful SIGTERM)",
    )
    parser.add_argument(
        "--logfile",
        default=None,
        help="Redirect stdout/stderr to this file (captures Flask logs). "
             "Omit to send to /dev/null.",
    )
    args = parser.parse_args()

    # --stop exits immediately; no daemonization needed.
    if args.stop:
        _stop_server(args.pidfile, force=args.force)

    # Fork + setsid + redirect: parent exits → tool returns immediately;
    # child continues in a new session with logs captured to --logfile.
    _daemonize(args.logfile)

    if args.mock:
        _inject_mock_state()
        print(f"[medminder_dash_server] Mock state injected ({MOCK_PORT_1}, {MOCK_PORT_2})")
    else:
        print("[medminder_dash_server] Starting with empty state (no --mock)")

    bms_proc = None
    if args.bms:
        print("[medminder_dash_server] Starting BMS daemon...")
        bms_proc = _start_bms()
        atexit.register(_stop_bms, bms_proc)
        print("[medminder_dash_server] BMS started, initializing PubSub...")
        init_pubsub()
        with state._daemon_ready_lock:
            state._daemon_ready = True
        print("[medminder_dash_server] PubSub connected, daemon ready")

    debug_mode = not (args.bms or args.production)
    use_reloader = not (args.bms or args.production)

    pidfile = args.pidfile
    _write_pidfile(pidfile)
    atexit.register(_remove_pidfile, pidfile)

    print(f"[medminder_dash_server] Listening on http://0.0.0.0:{args.port}")
    try:
        app.run(host="0.0.0.0", port=args.port, debug=debug_mode, use_reloader=use_reloader)
    finally:
        _remove_pidfile(pidfile)
        _stop_bms(bms_proc)
        if _temp_data_file.exists():
            _temp_data_file.unlink()


if __name__ == "__main__":
    main()
