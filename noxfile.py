"""Nox session definitions for the medminder monorepo.

Provides build, test, install, and standalone-binary sessions for all 6
Python sub-packages.  Run ``nox --list`` to see available sessions.
"""

import nox
from pathlib import Path

ROOT = Path(__file__).parent

PACKAGES = [
    (
        "board_manager",
        "board-manager",
        ROOT / "board_manager/python/board_manager",
        ROOT / "board_manager/python/board_manager/dist"
    ),
    (
        "board_manager_client",
        "board-manager-client",
        ROOT / "board_manager_client/python/board_manager_client",
        ROOT / "board_manager_client/python/board_manager_client/dist"
    ),
    (
        "arduino_sketch_tools",
        "arduino-sketch-tools",
        ROOT / "arduino_sketch_tools/python/arduino_sketch_tools",
        ROOT / "arduino_sketch_tools/python/arduino_sketch_tools/dist"
    ),
    (
        "arduino_dash",
        "arduino-dash",
        ROOT / "arduino_dash/python/arduino_dash",
        ROOT / "arduino_dash/python/arduino_dash/dist"
    ),
    (
        "arduino_grpc",
        "arduino-grpc",
        ROOT / "grpc_client/python/arduino_grpc/",
        ROOT / "grpc_client/python/arduino_grpc/dist"
    ),
    (
        "medminder_dash",
        "medminder-dash",
        ROOT / "medminder_dash/python/medminder_dash",
        ROOT / "medminder_dash/python/medminder_dash/dist"
    ),
]


@nox.session
@nox.parametrize("name,pip_name,src,outdir", PACKAGES, ids=[p[0] for p in PACKAGES])
def tests(session, name, pip_name, src, outdir):
    """Run the per-package pytest suite (Phase 56 Q17)."""
    with session.chdir(src):
        session.run("pipenv", "lock", "--dev", external=True)
        session.run("pipenv", "sync", "--dev", external=True)
        pytest_args = ["tests/"]
        if name == "board_manager":
            pytest_args.append("--integration")
        session.run("pipenv", "run", "pytest", *pytest_args, external=True)


@nox.session
def scripts_tests(session):
    """Run the scripts/ test suite (pytest + bash) (Phase 56 Q17, Phase 96)."""
    scripts_dir = ROOT / "scripts"
    with session.chdir(scripts_dir):
        session.run("pipenv", "install", "--dev", external=True)
        session.run("pipenv", "run", "pytest", "tests/", external=True)
        session.run("bash", "tests/test_install_arduino_deps.sh", external=True)
        session.run("bash", "tests/test_ci.sh", external=True)


@nox.session(tags=["build"])
@nox.parametrize("name,pip_name,src,outdir", PACKAGES, ids=[p[0] for p in PACKAGES])
def build(session, name, pip_name, src, outdir):
    """Build the wheel. (Phase 56 Q17)

    Note: ``nox`` 2026.4.10 does not support ``@nox.session(depends=[...])``,
    so the build session does not automatically run the test session first.
    The recommended workflow is:

        nox -s 'tests(arduino_dash)' 'build(arduino_dash)'

    which runs them in order. nox exits non-zero if any session fails.
    For CI, use ``nox -s all_tests all_builds`` or ``scripts/ci.sh`` (Phase 56 Q18).
    """
    pkg_outdir = outdir / pip_name
    pkg_outdir.mkdir(parents=True, exist_ok=True)
    session.install("build")
    session.run("python", "-m", "build", str(src), "--outdir", str(pkg_outdir))
    _write_index_html(pkg_outdir, pip_name)


@nox.session
def all_tests(session):
    """Run all test suites (Phase 56 Q18). Wrapper around ``scripts_tests`` +
    all 6 per-package ``tests`` sessions, using ``session.notify`` so they
    run in the same nox process (no recursive nox invocation).

    Fail-fast: if any session fails, the remaining ones still run (nox
    default), and the final exit code is the count of failed sessions.
    """
    session.notify("scripts_tests")
    for name, _pip_name, _src, _outdir in PACKAGES:
        session.notify(f"tests({name})")


@nox.session
def all_builds(session):
    """Build all 6 packages (Phase 56 Q18). Does NOT run tests first.

    Use ``scripts/ci.sh`` (or the explicit workflow
    ``nox -s all_tests all_builds``) to run tests before builds.
    """
    for name, _pip_name, _src, _outdir in PACKAGES:
        session.notify(f"build({name})")


@nox.session
def test_installs(session):
    """Install all monorepo wheels into a fresh venv and run smoke tests.

    Wraps ``scripts/test_installs.sh``. Validates that every package
    can be installed (pip dependency resolution) and imported from a
    clean environment.

    Extra arguments are forwarded, e.g.:
        nox -s test_installs -- --skip-install
    """
    with session.chdir(ROOT):
        session.run("bash", "scripts/test_installs.sh", *session.posargs,
                     external=True)


@nox.session
def build_standalone(session):
    """Build standalone binaries for all 3 apps via PyOxidizer.

    Wraps ``scripts/build_standalone.sh``. Result goes to
    ``dist-standalone/<app>/`` (gitignored).

    Extra arguments are forwarded, e.g.:
        nox -s build_standalone -- --dry-run
        nox -s build_standalone -- board-manager
    """
    with session.chdir(ROOT):
        session.run("bash", "scripts/build_standalone.sh", *session.posargs,
                     external=True,
                     env={"PYOXIDIZER": "pyoxidizer"})


def _write_index_html(pkg_outdir: Path, pip_name: str):
    """Generate index.html files for the package dist directory and its parent.

    Args:
        pkg_outdir: The output dist directory for the package.
        pip_name: The pip-installable package name.
    """
    dist_root = pkg_outdir.parent
    files = sorted(f.name for f in pkg_outdir.iterdir() if f.name.endswith(".whl") or f.name.endswith(".tar.gz"))
    pkg_html = "<!DOCTYPE html>\n<html><body>\n"
    pkg_html += "".join(f'<a href="{f}">{f}</a><br>\n' for f in files)
    pkg_html += "</body></html>\n"
    pkg_outdir.joinpath("index.html").write_text(pkg_html)

    root_html = f'<!DOCTYPE html>\n<html><body>\n<a href="{pip_name}/">{pip_name}</a><br>\n</body></html>\n'
    dist_root.joinpath("index.html").write_text(root_html)
