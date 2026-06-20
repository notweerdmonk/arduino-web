"""
test_setup_py.py — pytest tests for the 6 populated setup.py files.

Covers Q8 through Q14. For each of the 6 packages we verify:

  Q8: arduino_grpc — packages list + package_dir map (cross-source cc/)
  Q9-Q13: All 6 packages have proper setup() arguments
  Q14: all 6 setup.py --name --version return the correct value, and
       each pyproject.toml has the expected console_scripts and
       package_data declarations.

Note: ``setup.py --name/--version`` invokes setuptools' dist metadata
introspection, which for PEP 621 packages requires setuptools >= 61.
The system /usr/bin/python3 ships setuptools 59.6.0, which fails to
parse the pyproject.toml. Each per-package venv ships setuptools
82.0.1, so the tests shell out to ``pipenv run python setup.py ...``
in the appropriate venv.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest


# Per-package expected metadata. Keys use the **dash-form** to match the
# ``PACKAGES`` fixture in conftest.py.
#   - ``name`` is the dist name (what `python setup.py --name` returns)
#   - ``version`` is the same for --version
#   - ``script`` is the console script name declared in [project.scripts]
#     (None if the package has no console script)
#   - ``package_data`` is a list of glob patterns that must appear in
#     [tool.setuptools.package-data]
PACKAGE_EXPECTATIONS = {
    "arduino-grpc": {
        "name": "arduino-grpc",
        "version": "0.1.0",
        "script": None,
        "package_data": [],
    },
    "board-manager": {
        "name": "board-manager",
        "version": "0.1.0",
        "script": "board-manager",
        "package_data": [],
    },
    "board-manager-client": {
        "name": "board-manager-client",
        "version": "0.1.0",
        "script": None,
        "package_data": [],
    },
    "arduino-sketch-tools": {
        "name": "arduino-sketch-tools",
        "version": "0.1.0",
        "script": None,
        "package_data": ["templates/**/*", "static/**/*"],
    },
    "arduino-dash": {
        "name": "arduino-dash",
        "version": "0.1.0",
        "script": "arduino-dash",
        "package_data": ["templates/**/*", "static/**/*"],
    },
    "medminder-dash": {
        "name": "medminder-dash",
        "version": "0.1.0",
        "script": "medminder-dash",
        "package_data": ["templates/**/*", "static/**/*"],
    },
}


# ---------------------------------------------------------------------------
# Q8: arduino_grpc packages/package_dir layout
# ---------------------------------------------------------------------------


class TestQ8ArduinoGrpcLayout:
    def test_setup_py_exists(self, gen_grpc_module, packages):
        arduino_grpc_dir = next(d for n, d in packages if n == "arduino-grpc")
        assert (arduino_grpc_dir / "setup.py").is_file()

    def test_setup_py_declares_packages(self, packages):
        arduino_grpc_dir = next(d for n, d in packages if n == "arduino-grpc")
        text = (arduino_grpc_dir / "setup.py").read_text()
        # All 6 package names must be present in the packages= list
        for pkg in [
            "arduino_grpc",
            "arduino_grpc.cc",
            "arduino_grpc.cc.arduino",
            "arduino_grpc.cc.arduino.cli",
            "arduino_grpc.cc.arduino.cli.commands",
            "arduino_grpc.cc.arduino.cli.commands.v1",
        ]:
            assert f'"{pkg}"' in text, f"setup.py missing package {pkg}"

    def test_setup_py_declares_package_dir(self, packages):
        arduino_grpc_dir = next(d for n, d in packages if n == "arduino-grpc")
        text = (arduino_grpc_dir / "setup.py").read_text()
        # package_dir must map both the main package AND the cc/ subtree
        assert '"arduino_grpc": "arduino_grpc"' in text
        assert '"arduino_grpc.cc": "cc"' in text

    def test_setup_py_includes_package_data(self, packages):
        arduino_grpc_dir = next(d for n, d in packages if n == "arduino-grpc")
        text = (arduino_grpc_dir / "setup.py").read_text()
        assert "include_package_data=True" in text

    def test_setup_py_has_docstring(self, packages):
        arduino_grpc_dir = next(d for n, d in packages if n == "arduino-grpc")
        text = (arduino_grpc_dir / "setup.py").read_text()
        assert text.startswith('"""') or text.startswith("'''")

    def test_has_setup_cfg(self, packages):
        # arduino_grpc now has a setup.cfg with
        # long_description = file: README.md (Phase 63).
        arduino_grpc_dir = next(d for n, d in packages if n == "arduino-grpc")
        assert (arduino_grpc_dir / "setup.cfg").exists()
        text = (arduino_grpc_dir / "setup.cfg").read_text()
        assert "long_description = file:" in text


# ---------------------------------------------------------------------------
# Q9-Q13: setup.py has proper setup() arguments for all 6 packages
# ---------------------------------------------------------------------------


ALL_PACKAGES = [
    "arduino-grpc",
    "board-manager",
    "board-manager-client",
    "arduino-sketch-tools",
    "arduino-dash",
    "medminder-dash",
]


class TestQ9ToQ13SetupArgs:
    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_exists(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        assert (d / "setup.py").is_file()

    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_has_setup_call(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        # Must contain a setup() call
        assert re.search(r"\bsetup\(", text), (
            f"{import_name}/setup.py should contain a setup() call"
        )

    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_has_name_arg(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        # Must pass name= to setup()
        assert 'name="' in text or "name='" in text, (
            f"{import_name}/setup.py should pass name= to setup()"
        )

    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_has_author(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        assert "notweerdmonk" in text, (
            f"{import_name}/setup.py should contain author info"
        )

    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_has_long_description(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        assert "long_description=open" in text or "long_description =" in text, (
            f"{import_name}/setup.py should have long_description"
        )

    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_has_docstring(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        assert text.startswith('"""') or text.startswith("'''"), (
            f"{import_name}/setup.py should start with a docstring"
        )

    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_has_keywords(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        assert "keywords=" in text, (
            f"{import_name}/setup.py should have keywords="
        )

    @pytest.mark.parametrize("import_name", ALL_PACKAGES)
    def test_setup_py_has_install_requires(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        assert "install_requires" in text, (
            f"{import_name}/setup.py should have install_requires"
        )

    @pytest.mark.parametrize("import_name", [
        "board-manager",
        "arduino-dash",
        "medminder-dash",
    ])
    def test_setup_py_has_entry_points(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        assert "entry_points" in text, (
            f"{import_name}/setup.py should declare entry_points"
        )

    @pytest.mark.parametrize("import_name", [
        "arduino-grpc",
        "board-manager-client",
        "arduino-sketch-tools",
    ])
    def test_setup_py_no_entry_points(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        text = (d / "setup.py").read_text()
        assert "entry_points" not in text, (
            f"{import_name}/setup.py should not declare entry_points; "
            "entry_points are in pyproject.toml [project.scripts]"
        )


# ---------------------------------------------------------------------------
# Q14: setup.py --name --version + pyproject.toml declarations
# ---------------------------------------------------------------------------


def _pipenv_python(d: Path) -> Optional[Path]:
    """Return the path to the venv python for the package at ``d``.

    Runs ``pipenv --venv`` in ``d`` and appends ``/bin/python``. Returns
    None if pipenv is not installed or no venv exists.
    """
    pipenv = shutil.which("pipenv")
    if pipenv is None:
        return None
    result = subprocess.run(
        [pipenv, "--venv"],
        cwd=str(d),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    venv = result.stdout.strip().splitlines()[-1]
    candidate = Path(venv) / "bin" / "python"
    if candidate.exists():
        return candidate
    return None


def _setup_py_python(d: Path) -> Path:
    """Return the python interpreter to use for setup.py introspection.

    Prefers the per-package pipenv venv python (setuptools >= 61),
    falling back to sys.executable (system python). Returns the path.
    """
    venv_py = _pipenv_python(d)
    if venv_py is not None:
        return venv_py
    return Path(sys.executable)


_PIPENV_AVAILABLE = shutil.which("pipenv") is not None


requires_pipenv = pytest.mark.skipif(
    not _PIPENV_AVAILABLE,
    reason=(
        "pipenv not installed; setup.py metadata introspection needs "
        "setuptools >= 61 (provided by the per-package pipenv venv)"
    ),
)


def _run_setup_py(d: Path, *args: str) -> str:
    """Run ``python setup.py <args>`` in ``d`` and return stdout.

    Uses the per-package pipenv venv python when available (system
    setuptools 59.6.0 cannot parse PEP 621 pyproject.toml).
    """
    python = _setup_py_python(d)
    result = subprocess.run(
        [str(python), "setup.py", *args],
        cwd=str(d),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"setup.py {args} failed in {d} (python={python}):\n"
            f"  stdout: {result.stdout}\n"
            f"  stderr: {result.stderr}"
        )
    return result.stdout.strip()


class TestQ14Metadata:
    @requires_pipenv
    @pytest.mark.parametrize("import_name", PACKAGE_EXPECTATIONS.keys())
    def test_setup_py_name(self, packages, import_name):
        expected = PACKAGE_EXPECTATIONS[import_name]["name"]
        d = next(d for n, d in packages if n == import_name)
        actual = _run_setup_py(d, "--name")
        assert actual == expected

    @requires_pipenv
    @pytest.mark.parametrize("import_name", PACKAGE_EXPECTATIONS.keys())
    def test_setup_py_version(self, packages, import_name):
        expected = PACKAGE_EXPECTATIONS[import_name]["version"]
        d = next(d for n, d in packages if n == import_name)
        actual = _run_setup_py(d, "--version")
        assert actual == expected

    @pytest.mark.parametrize("import_name,expected", [
        (n, e["script"])
        for n, e in PACKAGE_EXPECTATIONS.items()
        if e["script"] is not None
    ])
    def test_console_script_declared(self, packages, import_name, expected):
        d = next(d for n, d in packages if n == import_name)
        toml_text = (d / "pyproject.toml").read_text()
        # Look for [project.scripts] table with the expected entry
        m = re.search(
            r"\[project\.scripts\]\s*\n((?:\S+\s*=\s*\"[^\"]+\"\s*\n)+)",
            toml_text,
        )
        assert m is not None, f"no [project.scripts] table in {import_name}/pyproject.toml"
        entries = m.group(1)
        assert f'{expected} =' in entries, (
            f"{import_name}/pyproject.toml [project.scripts] missing {expected!r}; "
            f"found entries:\n{entries}"
        )
        # The script target must be "<pkg>.__main__:main"
        m2 = re.search(rf'{expected}\s*=\s*"([^"]+)"', entries)
        assert m2 is not None
        target = m2.group(1)
        assert target.endswith(":main") or target.endswith(".__main__"), (
            f"{import_name} console script {expected!r} should target "
            f"a :main entry; got {target!r}"
        )

    @pytest.mark.parametrize("import_name", [
        n for n, e in PACKAGE_EXPECTATIONS.items() if e["script"] is None
    ])
    def test_no_console_script(self, packages, import_name):
        d = next(d for n, d in packages if n == import_name)
        toml_text = (d / "pyproject.toml").read_text()
        # [project.scripts] should be absent OR empty
        m = re.search(
            r"\[project\.scripts\]\s*\n((?:\S+\s*=\s*\"[^\"]+\"\s*\n)*)",
            toml_text,
        )
        if m is not None:
            assert m.group(1).strip() == "", (
                f"{import_name} should not declare [project.scripts]"
            )

    @pytest.mark.parametrize("import_name,expected_globs", [
        (n, e["package_data"])
        for n, e in PACKAGE_EXPECTATIONS.items()
        if e["package_data"]
    ])
    def test_package_data_globs_present(self, packages, import_name, expected_globs):
        d = next(d for n, d in packages if n == import_name)
        toml_text = (d / "pyproject.toml").read_text()
        # Look for [tool.setuptools.package-data] table
        m = re.search(
            r"\[tool\.setuptools\.package-data\]\s*\n((?:\S+\s*=\s*\[[^\]]*\]\s*\n)+)",
            toml_text,
        )
        assert m is not None, (
            f"no [tool.setuptools.package-data] in {import_name}/pyproject.toml"
        )
        block = m.group(1)
        for glob in expected_globs:
            assert glob in block, (
                f"{import_name}/pyproject.toml package-data missing {glob!r}; "
                f"found:\n{block}"
            )

    @pytest.mark.parametrize("import_name,expected_globs", [
        (n, e["package_data"])
        for n, e in PACKAGE_EXPECTATIONS.items()
        if e["package_data"]
    ])
    def test_package_data_targets_correct_package(
        self, packages, import_name, expected_globs
    ):
        d = next(d for n, d in packages if n == import_name)
        toml_text = (d / "pyproject.toml").read_text()
        m = re.search(
            r"\[tool\.setuptools\.package-data\]\s*\n(\S+)\s*=",
            toml_text,
        )
        assert m is not None
        target_pkg = m.group(1).strip('"').strip("'")
        # The package-data key must match the distribution's main package
        expected_pkg = import_name.replace("-", "_")
        assert target_pkg == expected_pkg, (
            f"{import_name}/pyproject.toml package-data targets {target_pkg!r} "
            f"but should target {expected_pkg!r}"
        )

    def test_all_6_packages_have_pyproject_toml(self, packages):
        for import_name, d in packages:
            assert (d / "pyproject.toml").is_file(), (
                f"{import_name} missing pyproject.toml"
            )
            assert (d / "Pipfile").is_file(), (
                f"{import_name} missing Pipfile"
            )

    def test_all_6_pyproject_toml_have_pep621_metadata(self, packages):
        # Every package's pyproject.toml must declare [project] with a
        # name and version.
        for import_name, d in packages:
            text = (d / "pyproject.toml").read_text()
            assert "[project]" in text, (
                f"{import_name}/pyproject.toml missing [project] table"
            )
            assert "name" in text
            assert "version" in text
