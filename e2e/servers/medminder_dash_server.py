"""Standalone Flask dev server for medminder_dash with optional mock state and BMS.

Usage:
    python3 e2e/servers/medminder_dash_server.py                    # empty state, port 8766
    python3 e2e/servers/medminder_dash_server.py --mock              # with mock board + medicine data
    python3 e2e/servers/medminder_dash_server.py --mock --bms        # with mock data + BMS daemon
    python3 e2e/servers/medminder_dash_server.py --port 9000         # custom port
"""

import argparse
import atexit
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Project root is e2e/servers/../../..  (up from script -> servers -> e2e -> root)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
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
    args = parser.parse_args()

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

    print(f"[medminder_dash_server] Listening on http://0.0.0.0:{args.port}")
    try:
        app.run(host="0.0.0.0", port=args.port, debug=not args.bms)
    finally:
        _stop_bms(bms_proc)
        if _temp_data_file.exists():
            _temp_data_file.unlink()


if __name__ == "__main__":
    main()
