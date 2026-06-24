"""
conftest.py — shared fixtures for the scripts/tests/ pytest suite.

The tests exercise scripts/install_arduino_deps.sh and
scripts/gen_grpc_bindings.py (both at the repo's scripts/ root), and
the populated setup.py files under each of the 6 Python packages
(each at <pkg>/python/<pkg>/setup.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
GEN_GRPC_SCRIPT = SCRIPTS_DIR / "gen_grpc_bindings.py"
INSTALL_DEPS_SCRIPT = SCRIPTS_DIR / "install_arduino_deps.sh"


# The 6 Python packages. Each entry is (importable_name, setup_py_dir).
# setup_py_dir is the directory that contains both setup.py and Pipfile.
PACKAGES = [
    ("arduino-grpc", REPO_ROOT / "grpc_client" / "python" / "arduino_grpc"),
    ("board-manager", REPO_ROOT / "board_manager" / "python" / "board_manager"),
    (
        "board-manager-client",
        REPO_ROOT / "board_manager_client" / "python" / "board_manager_client",
    ),
    (
        "arduino-sketch-tools",
        REPO_ROOT / "arduino_sketch_tools" / "python" / "arduino_sketch_tools",
    ),
    ("arduino-dash", REPO_ROOT / "arduino_dash" / "python" / "arduino_dash"),
    ("medminder-dash", REPO_ROOT / "medminder_dash" / "python" / "medminder_dash"),
]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def scripts_dir() -> Path:
    return SCRIPTS_DIR


@pytest.fixture(scope="session")
def gen_grpc_script() -> Path:
    return GEN_GRPC_SCRIPT


@pytest.fixture(scope="session")
def install_deps_script() -> Path:
    return INSTALL_DEPS_SCRIPT


@pytest.fixture
def gen_grpc_module():
    """Import the gen_grpc_bindings module.

    sys.path is mutated to make the script importable. The mutation is
    scoped to the test and reverted on teardown.
    """
    saved = list(sys.path)
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        import gen_grpc_bindings  # type: ignore[import-not-found]

        return gen_grpc_bindings
    finally:
        sys.path[:] = saved


@pytest.fixture
def packages() -> list[tuple[str, Path]]:
    return list(PACKAGES)
