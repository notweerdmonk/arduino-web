#!/usr/bin/env python3
"""Integration test script for arduino_grpc module with real arduino-cli daemon"""

import sys
import os
import time

import pytest

from arduino_grpc.client import ArduinoGrpcClient
from arduino_grpc.exceptions import ArduinoError
from .daemon_helper import DaemonCtx


def test_connection(daemon_url):
    print("\n=== Test 1: Connection ===")
    client = ArduinoGrpcClient(daemon=daemon_url)
    try:
        client.connect()
        print("SUCCESS: Connected to daemon")
    except Exception as e:
        print(f"FAILED: {e}")
        raise
    finally:
        client.disconnect()


def test_init(daemon_url):
    print("\n=== Test 2: Instance Initialization ===")
    client = ArduinoGrpcClient(daemon=daemon_url)
    try:
        with client:
            instance = client.init()
            print(f"SUCCESS: Instance initialized with id={instance.id}")
            assert instance is not None
    except Exception as e:
        print(f"FAILED: {e}")
        raise


def test_list_boards(daemon_url):
    print("\n=== Test 3: List Boards ===")
    client = ArduinoGrpcClient(daemon=daemon_url)
    try:
        with client:
            boards = client.list_boards()
            print(f"SUCCESS: Found {len(boards)} board(s)")
            for b in boards:
                print(f"  - {b.name} at {b.port.address} ({b.fqbn})")
            assert boards is not None
    except Exception as e:
        print(f"FAILED: {e}")
        raise


def test_list_all_boards(daemon_url):
    print("\n=== Test 4: List All Boards ===")
    client = ArduinoGrpcClient(daemon=daemon_url)
    try:
        with client:
            boards = client.list_all_boards()
            print(f"SUCCESS: Found {len(boards)} board(s)")
            for b in boards[:3]:
                print(f"  - {b.fqbn}: {b.name}")
            if len(boards) > 3:
                print(f"  ... and {len(boards)-3} more")
            assert len(boards) > 0
    except Exception as e:
        print(f"FAILED: {e}")
        raise


def test_watch_boards(daemon_url):
    print("\n=== Test 5: Watch Boards (4 second timeout) ===")
    client = ArduinoGrpcClient(daemon=daemon_url)
    with client:
        count = 0
        start = time.time()
        gen = client.watch_boards(timeout=4)
        for board in gen:
            count += 1
            print(f"  Board event: {board.name} at {board.port.address}")
        elapsed = time.time() - start
        print(f"SUCCESS: Watch ended after {elapsed:.1f}s, detected {count} event(s)")


def test_watch_boards_event(daemon_url):
    print("\n=== Test 8: Watch Boards — Board Events ===")
    client = ArduinoGrpcClient(daemon=daemon_url)
    with client:
        boards = client.list_boards()
        if not boards:
            print("  No board found (connect an Arduino via USB to test)")
            pytest.skip("No board detected")
        board = boards[0]
        print(f"  Board detected: {board.name} at {board.port.address}")
        count = 0
        gen = client.watch_boards(timeout=4)
        for detected in gen:
            count += 1
            print(f"  Event: {detected.name} detected={detected.detected}")
            assert detected.port.address, "Event missing port address"
            assert detected.name, "Event missing board name"
        print(f"SUCCESS: Watch ended, detected {count} event(s) for {board.name}")


def test_compile(daemon_url):
    print("\n=== Test 6: Compile Sketch ===")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sketch_path = os.path.normpath(os.path.join(script_dir, "..", "..", "..", "..", "sketches", "blinky"))
    if not os.path.exists(sketch_path):
        pytest.skip(f"Sketch not found at {sketch_path}")

    client = ArduinoGrpcClient(daemon=daemon_url)
    with client:
        print(f"Compiling {sketch_path}...")
        result = client.compile(sketch_path, "arduino:avr:uno", verbose=True)
        status = "SUCCESS" if result.success else "FAILED"
        print(f"{status}: Compilation {'succeeded' if result.success else 'failed'}")
        for line in result.output.split("\n"):
            line = line.strip()
            if line and "Progress" not in line:
                print(f"  {line}")
        assert result.success, f"Compilation failed: {result.error}"


def test_upload(daemon_url):
    print("\n=== Test 7: Upload Sketch ===")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sketch_path = os.path.normpath(os.path.join(script_dir, "..", "..", "..", "..", "sketches", "blinky"))
    if not os.path.exists(sketch_path):
        pytest.skip(f"Sketch not found at {sketch_path}")

    client = ArduinoGrpcClient(daemon=daemon_url)
    with client:
        client.init()
        boards = client.list_boards()
        if not boards:
            print("  No board found (connect an Arduino via USB to test upload)")
            pytest.skip("No board detected")

        board = boards[0]
        print(f"Using board: {board.name} at {board.port.address} ({board.fqbn})")

        print(f"Compiling {sketch_path}...")
        compile_result = client.compile(sketch_path, board.fqbn, verbose=False)
        assert compile_result.success, f"Compilation failed before upload: {compile_result.error[:200]}"
        print(f"Compile OK ({len(compile_result.output)} bytes of output)")

        print(f"Uploading to {board.port.address}...")
        upload_result = client.upload(sketch_path, board.fqbn, board.port.address, verbose=True)
        assert upload_result.success, f"Upload failed: {upload_result.error[:300]}"

        print("SUCCESS: Upload completed")
        for line in upload_result.output.split("\n"):
            line = line.strip()
            if line and "Progress" not in line:
                print(f"  {line}")


def main():
    with DaemonCtx() as daemon_url:
        _run_all(daemon_url)


def _run_all(daemon_url: str):
    print("=" * 50)
    print("Arduino gRPC Integration Tests")
    print("=" * 50)

    test_funcs = [
        ("Connection", test_connection),
        ("Init", test_init),
        ("List Boards", test_list_boards),
        ("List All Boards", test_list_all_boards),
        ("Watch Boards", test_watch_boards),
        ("Watch Boards - Events", test_watch_boards_event),
        ("Compile", test_compile),
        ("Upload", test_upload),
    ]

    passed = 0
    skipped = 0
    failed = 0

    for name, func in test_funcs:
        try:
            func(daemon_url)
            status = "PASS"
            passed += 1
        except pytest.skip.Exception:
            status = "SKIP"
            skipped += 1
        except Exception:
            status = "FAIL"
            failed += 1

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  Total: {passed} passed, {failed} failed, {skipped} skipped")


if __name__ == "__main__":
    main()
