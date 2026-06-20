"""Standalone Flask dev server for arduino_dash with optional mock state and BMS.

Usage:
    python e2e/servers/arduino_dash_server.py                    # empty state, port 8765
    python e2e/servers/arduino_dash_server.py --mock              # with mock board data
    python e2e/servers/arduino_dash_server.py --mock --bms        # with mock data + BMS daemon
    python e2e/servers/arduino_dash_server.py --port 9000         # custom port
"""

import argparse
import atexit
import os
import subprocess
import sys
from pathlib import Path

# Project root is e2e/servers/../../..  (up from script -> servers -> e2e -> root)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PYTHON = PROJECT_ROOT / "arduino_dash" / "python"
sys.path.insert(0, str(PACKAGE_PYTHON))

import arduino_dash.state as state
from arduino_dash.app import app
from arduino_dash.pubsub import init_pubsub


def _start_bms() -> subprocess.Popen:
    """Start the BMS daemon as a subprocess, return Popen handle."""
    bms_proc = subprocess.Popen(
        [sys.executable, "-m", "board_manager", "--log-level", "INFO"]
    )
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
    args = parser.parse_args()

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

    print(f"[arduino_dash_server] Listening on http://0.0.0.0:{args.port}")
    try:
        app.run(host="0.0.0.0", port=args.port, debug=not args.bms)
    finally:
        _stop_bms(bms_proc)


if __name__ == "__main__":
    main()
