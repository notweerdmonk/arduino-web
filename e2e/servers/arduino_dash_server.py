"""Standalone Flask dev server for arduino_dash with optional mock state and BMS.

Usage:
    python e2e/servers/arduino_dash_server.py                    # empty state, port 8765
    python e2e/servers/arduino_dash_server.py --mock              # with mock board data
    python e2e/servers/arduino_dash_server.py --mock --bms        # with mock data + BMS daemon
    python e2e/servers/arduino_dash_server.py --port 9000         # custom port
    python e2e/servers/arduino_dash_server.py --stop              # stop a running server
    python e2e/servers/arduino_dash_server.py --stop --force      # force-stop a running server
    python e2e/servers/arduino_dash_server.py --pidfile /tmp/mypid.pid --stop
"""

import argparse
import atexit
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# ── Lifecycle helpers ──────────────────────────────────────────────────────────


def _get_default_pidfile() -> str:
    """Derive a pidfile path from the script name, e.g. /tmp/arduino_dash_server.pid."""
    return f"/tmp/{Path(__file__).stem}.pid"


def _write_pidfile(path: str) -> None:
    """Write current PID to *path*."""
    Path(path).write_text(str(os.getpid()))
    print(f"[server] PID {os.getpid()} written to {path}")


def _remove_pidfile(path: str) -> None:
    """Remove *path* only if it still contains *our* PID (avoid stealing another's pidfile)."""
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
        for _ in range(50):  # poll up to 5 s (50 × 100 ms)
            try:
                os.kill(pid, 0)  # check if alive
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
PACKAGE_PYTHON = PROJECT_ROOT / "arduino_dash" / "python"
sys.path.insert(0, str(PACKAGE_PYTHON))

import arduino_dash.state as state  # noqa: E402
from arduino_dash.app import app  # noqa: E402
from arduino_dash.pubsub import init_pubsub  # noqa: E402


def _start_bms() -> subprocess.Popen:
    """Start the BMS daemon as a subprocess, return Popen handle."""
    bms_proc = subprocess.Popen([sys.executable, "-m", "board_manager", "--log-level", "INFO"])
    return bms_proc


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


MOCK_PORT_1 = "/dev/ttyTEST0"
MOCK_PORT_2 = "/dev/ttyTEST1"
MOCK_HW_ID_1 = "HW-TEST-001"
MOCK_HW_ID_2 = "HW-TEST-002"


def _inject_mock_state():
    """Populate board list and upload registry with test data."""
    with state._board_list_lock:
        state._board_list[MOCK_PORT_1] = {
            "port": MOCK_PORT_1,
            "board": "TestBoard Uno",
            "fqbn": "arduino:avr:uno",
            "hardware_id": MOCK_HW_ID_1,
        }
        state._board_list[MOCK_PORT_2] = {
            "port": MOCK_PORT_2,
            "board": "TestBoard Mega",
            "fqbn": "arduino:avr:mega",
            "hardware_id": MOCK_HW_ID_2,
        }

    with state._upload_registry_lock:
        state._upload_registry[("127.0.0.1", "playwright-test")] = {
            "mysketch": [
                {
                    "path": "/tmp/e2e-test/sketches/MySketch",
                    "checksum": "abc123def456",
                    "server_timestamp": "2026-06-19T00:00:00",
                    "hardware_ids": [MOCK_HW_ID_1],
                    "board_timestamps": {},
                },
            ]
        }

    with state._daemon_ready_lock:
        state._daemon_ready = False


def main():
    """Parse args, optionally inject mock state and start BMS, then run the Flask dev server."""
    parser = argparse.ArgumentParser(
        description="Start arduino_dash Flask dev server with optional mock state and BMS"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Inject mock board data and sketch registry entries",
    )
    parser.add_argument(
        "--bms",
        action="store_true",
        help="Start the BMS daemon (arduino-cli daemon + board_manager service)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to bind (default: 8765)",
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
        print(f"[arduino_dash_server] Mock state injected ({MOCK_PORT_1}, {MOCK_PORT_2})")
    else:
        print("[arduino_dash_server] Starting with empty state (no --mock)")

    bms_proc = None
    if args.bms:
        print("[arduino_dash_server] Starting BMS daemon...")
        bms_proc = _start_bms()
        atexit.register(_stop_bms, bms_proc)
        print("[arduino_dash_server] BMS started, initializing PubSub...")
        init_pubsub()
        with state._daemon_ready_lock:
            state._daemon_ready = True
        print("[arduino_dash_server] PubSub connected, daemon ready")

    debug_mode = not (args.bms or args.production)
    use_reloader = not (args.bms or args.production)

    pidfile = args.pidfile
    _write_pidfile(pidfile)
    atexit.register(_remove_pidfile, pidfile)

    print(f"[arduino_dash_server] Listening on http://0.0.0.0:{args.port}")
    try:
        app.run(host="0.0.0.0", port=args.port, debug=debug_mode, use_reloader=use_reloader)
    finally:
        _remove_pidfile(pidfile)
        _stop_bms(bms_proc)


if __name__ == "__main__":
    main()
