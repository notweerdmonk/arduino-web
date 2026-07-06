"""medminder_dash/python/medminder_dash/tests/test_sketch_registry.py

Tests for sketch_registry module.

Author: notweerdmonk
SPDX-License-Identifier: Apache-2.0

Copyright 2026 notweerdmonk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os

import pytest

from medminder_dash import state


@pytest.fixture(autouse=True)
def reset_registry():
    """Clear _upload_registry before each test."""
    state._upload_registry.clear()
    yield


def _make_version(path, hardware_ids=None, server_timestamp="2025-01-01T00:00:00"):
    return {
        "path": path,
        "checksum": "abc123",
        "server_timestamp": server_timestamp,
        "hardware_ids": hardware_ids or [],
        "board_timestamps": {},
    }


def test_get_assignment_returns_none_when_empty():
    """get_assignment returns None when no hardware_ids match."""
    from medminder_dash.sketch_registry import get_assignment

    assert get_assignment("USB:123 SER=456") is None


def test_set_and_get_assignment(tmp_path):
    """set_assignment stores and get_assignment retrieves."""
    from medminder_dash.sketch_registry import get_assignment, set_assignment

    sketch_dir = str(tmp_path / "mysketch")
    os.makedirs(sketch_dir, exist_ok=True)
    state._upload_registry[("127.0.0.1", "test-agent")] = {"mysketch": [_make_version(sketch_dir)]}
    hw_id = "USB:123 SER=456"
    set_assignment(hw_id, sketch_dir)
    assert get_assignment(hw_id) == sketch_dir


def test_get_assignment_returns_none_for_nonexistent_dir(tmp_path):
    """get_assignment returns None if the path does not exist on disk."""
    from medminder_dash.sketch_registry import get_assignment

    sketch_dir = str(tmp_path / "nonexistent")
    state._upload_registry[("127.0.0.1", "test-agent")] = {"mysketch": [_make_version(sketch_dir)]}
    state._upload_registry[("127.0.0.1", "test-agent")]["mysketch"][0]["hardware_ids"] = ["HW:001"]
    assert get_assignment("HW:001") is None


def test_clear_assignment(tmp_path):
    """clear_assignment removes hardware_id from the version entry."""
    from medminder_dash.sketch_registry import (
        clear_assignment,
        get_assignment,
        set_assignment,
    )

    sketch_dir = str(tmp_path / "mysketch")
    os.makedirs(sketch_dir, exist_ok=True)
    state._upload_registry[("127.0.0.1", "test-agent")] = {"mysketch": [_make_version(sketch_dir)]}
    hw_id = "USB:123 SER=456"
    set_assignment(hw_id, sketch_dir)
    assert get_assignment(hw_id) == sketch_dir
    clear_assignment(hw_id)
    assert get_assignment(hw_id) is None


def test_clear_assignment_only_removes_target(tmp_path):
    """clear_assignment only removes the specified hardware_id."""
    from medminder_dash.sketch_registry import (
        clear_assignment,
        get_assignment,
        set_assignment,
    )

    sketch_dir = str(tmp_path / "mysketch")
    os.makedirs(sketch_dir, exist_ok=True)
    state._upload_registry[("127.0.0.1", "test-agent")] = {"mysketch": [_make_version(sketch_dir)]}
    set_assignment("HW:001", sketch_dir)
    set_assignment("HW:002", sketch_dir)
    clear_assignment("HW:001")
    assert get_assignment("HW:001") is None
    assert get_assignment("HW:002") == sketch_dir


def test_get_all_assignments(tmp_path):
    """get_all_assignments returns all hardware_id -> path mappings."""
    from medminder_dash.sketch_registry import get_all_assignments, set_assignment

    d1 = str(tmp_path / "sketch1")
    d2 = str(tmp_path / "sketch2")
    os.makedirs(d1)
    os.makedirs(d2)
    state._upload_registry[("ip1", "ua1")] = {"a": [_make_version(d1)]}
    state._upload_registry[("ip2", "ua2")] = {"b": [_make_version(d2)]}
    set_assignment("HW:001", d1)
    set_assignment("HW:002", d2)
    all_a = get_all_assignments()
    assert all_a == {"HW:001": d1, "HW:002": d2}


def test_get_assignment_empty_hardware_id():
    """get_assignment returns None for empty hardware_id."""
    from medminder_dash.sketch_registry import get_assignment

    assert get_assignment("") is None


def test_set_assignment_empty_hardware_id_noop():
    """set_assignment is a no-op with empty hardware_id."""
    from medminder_dash.sketch_registry import get_all_assignments, set_assignment

    set_assignment("", "/path/1")
    assert get_all_assignments() == {}


def test_clear_assignment_empty_hardware_id_noop():
    """clear_assignment is a no-op with empty hardware_id."""
    from medminder_dash.sketch_registry import clear_assignment

    clear_assignment("")  # should not raise


def test_set_assignment_finds_correct_version(tmp_path):
    """set_assignment adds hardware_id to the version with matching path."""
    from medminder_dash.sketch_registry import get_assignment, set_assignment

    sd1 = str(tmp_path / "sketch1")
    sd2 = str(tmp_path / "sketch2")
    os.makedirs(sd1)
    os.makedirs(sd2)
    state._upload_registry[("ip", "ua")] = {"a": [_make_version(sd1), _make_version(sd2)]}
    set_assignment("HW:001", sd2)
    assert get_assignment("HW:001") == sd2


def test_reset_for_tests_does_not_raise():
    """reset_for_tests is a no-op and should not raise."""
    from medminder_dash.sketch_registry import reset_for_tests

    reset_for_tests()


def test_save_and_load_registry(tmp_path, monkeypatch):
    """_save_registry and _load_registry persist and restore state."""
    from medminder_dash.sketch_management import _load_registry, _save_registry

    monkeypatch.setattr("medminder_dash.sketch_management.REGISTRY_DIR", tmp_path)
    monkeypatch.setattr(
        "medminder_dash.sketch_management.REGISTRY_FILE",
        str(tmp_path / "sketch_registry.json"),
    )
    sketch_dir = str(tmp_path / "mysketch")
    os.makedirs(sketch_dir, exist_ok=True)
    state._upload_registry[("127.0.0.1", "test-agent")] = {
        "mysketch": [_make_version(sketch_dir, hardware_ids=["HW:001"])]
    }
    _save_registry()
    state._upload_registry.clear()
    _load_registry()
    assert len(state._upload_registry) == 1
    key = ("127.0.0.1", "test-agent")
    assert key in state._upload_registry
    versions = state._upload_registry[key]["mysketch"]
    assert len(versions) == 1
    assert versions[0]["path"] == sketch_dir
    assert versions[0]["hardware_ids"] == ["HW:001"]


def test_load_registry_no_file(tmp_path, monkeypatch):
    """_load_registry is a no-op when REGISTRY_FILE does not exist."""
    from medminder_dash.sketch_management import _load_registry

    monkeypatch.setattr(
        "medminder_dash.sketch_management.REGISTRY_FILE",
        str(tmp_path / "nonexistent.json"),
    )
    _load_registry()  # should not raise


def test_load_registry_corrupt_file(tmp_path, monkeypatch):
    """_load_registry handles corrupt JSON gracefully."""
    from medminder_dash.sketch_management import _load_registry

    reg_file = tmp_path / "sketch_registry.json"
    reg_file.write_text("not valid json")
    monkeypatch.setattr("medminder_dash.sketch_management.REGISTRY_FILE", str(reg_file))
    _load_registry()  # should not raise
