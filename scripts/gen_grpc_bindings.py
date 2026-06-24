#!/usr/bin/env python3
"""
gen_grpc_bindings.py — Regenerate Python gRPC stubs for the
arduino-cli gRPC service.

This script walks the arduino-cli `.proto` files and emits the corresponding
`*_pb2.py`, `*_pb2_grpc.py`, and `*_pb2.pyi` files into
``<repo>/grpc_client/python/arduino_grpc/cc/arduino/cli/commands/v1``.

The proto source can come from a local checkout (passed via ``--proto-src``)
or a GitHub release zip (passed via ``--proto-url``).

The script is intentionally venv-aware: it will use the pipenv / poetry / uv
virtualenv that owns the ``arduino_grpc`` package when one is detected,
falling back to the system Python otherwise. ``grpcio-tools`` and
``googleapis-common-protos`` are installed into the chosen environment on
demand (with confirmation unless ``--no-prompt`` or ``--install-deps`` is
supplied).

Examples
--------

Use a local checkout of arduino-cli::

    python3 scripts/gen_grpc_bindings.py \\
        --proto-src /home/weerdmonk/Projects/arduino-cli/rpc

Download the protos from a release zip and prompt before installing deps::

    python3 scripts/gen_grpc_bindings.py \\
        --proto-url https://github.com/arduino/arduino-cli/releases/download/0.35.0/arduino-cli_0.35.0_Linux_64bit.zip

CI usage (no prompts, auto-install)::

    python3 scripts/gen_grpc_bindings.py \\
        --proto-src /opt/arduino-cli/rpc \\
        --install-deps --no-prompt
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
ARDUINO_GRPC_DIR = REPO_ROOT / "grpc_client" / "python" / "arduino_grpc"
# Note: protoc's --python_out/--grpc_python_out/--pyi_out preserve the
# proto's package path relative to --proto_path. Since the arduino-cli
# protos declare their package as cc.arduino.cli.commands.v1 and live at
# <root>/cc/arduino/cli/commands/v1/*.proto, the output must be <root>/ so
# files land at <root>/cc/arduino/cli/commands/v1/*.py.
STUB_OUT = ARDUINO_GRPC_DIR

PROTO_SUBDIR = "cc/arduino/cli/commands/v1"

# Extra well-known proto includes we must point protoc at. The arduino-cli
# rpc imports `google/rpc/status.proto` and `google/protobuf/any.proto`.
# These ship with the grpcio-tools install (under
# grpc_tools/_proto/google/{rpc,protobuf}/) so no extra --googleapis-src is
# needed for the common case. If a user passes --googleapis-src, we add it
# to the include path too.
REQUIRED_PYTHON_PACKAGES = (
    "grpcio-tools",
    "googleapis-common-protos",
)

__all__ = [
    "main",
    "detect_venv",
    "resolve_proto_src",
    "ensure_grpc_tools",
    "generate_stubs",
    "ensure_init_chain",
]


def _run(cmd: Sequence[str], **kw) -> subprocess.CompletedProcess:
    """Run a subprocess, returning the CompletedProcess. Raises on failure."""
    return subprocess.run(list(cmd), check=True, **kw)


def _which_or_none(name: str) -> Optional[str]:
    return shutil.which(name)


def _venv_python_from(venv_dir: Path) -> Path:
    """Return the python interpreter inside a given venv directory."""
    candidates = [
        venv_dir / "bin" / "python",
        venv_dir / "bin" / "python3",
        venv_dir / "Scripts" / "python.exe",
        venv_dir / "Scripts" / "python3.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(f"no python interpreter found in venv at {venv_dir}")


def _detect_pipenv(project_root: Path) -> Optional[Tuple[Path, Path]]:
    """If a Pipfile is present and `pipenv --venv` succeeds, return (python, pip).

    Returns None if pipenv is not installed, no Pipfile is present, or
    `pipenv --venv` fails.
    """
    if not (project_root / "Pipfile").exists():
        return None
    pipenv = _which_or_none("pipenv")
    if pipenv is None:
        return None
    try:
        result = subprocess.run(
            [pipenv, "--venv"],
            cwd=str(project_root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    venv_dir = Path(result.stdout.strip())
    if not venv_dir.exists():
        return None
    python = _venv_python_from(venv_dir)
    pip = venv_dir / "bin" / "pip"
    if not pip.exists():
        pip = venv_dir / "Scripts" / "pip.exe"
    return python, pip


def _detect_poetry(project_root: Path) -> Optional[Tuple[Path, Path]]:
    """If a pyproject.toml with [tool.poetry] is present and `poetry env info`
    succeeds, return (python, pip) for the active environment.

    Returns None if poetry is not installed, no poetry pyproject is present,
    or `poetry env info` fails.
    """
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        text = pyproject.read_text()
    except OSError:
        return None
    if "[tool.poetry]" not in text:
        return None
    poetry = _which_or_none("poetry")
    if poetry is None:
        return None
    try:
        result = subprocess.run(
            [poetry, "env", "info", "-p"],
            cwd=str(project_root),
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    venv_dir = Path(result.stdout.strip())
    if not venv_dir.exists():
        return None
    python = _venv_python_from(venv_dir)
    pip = venv_dir / "bin" / "pip"
    if not pip.exists():
        pip = venv_dir / "Scripts" / "pip.exe"
    return python, pip


def _detect_uv(project_root: Path) -> Optional[Tuple[Path, Path]]:
    """If uv is installed and a .venv exists in the project root, return
    (python, pip) for it.
    """
    uv = _which_or_none("uv")
    if uv is None:
        return None
    venv_dir = project_root / ".venv"
    if not venv_dir.exists():
        return None
    python = _venv_python_from(venv_dir)
    pip = venv_dir / "bin" / "pip"
    if not pip.exists():
        pip = venv_dir / "Scripts" / "pip.exe"
    return python, pip


def _detect_system() -> Tuple[Path, Path]:
    """Fall back to the current Python interpreter and ensure pip is available."""
    python = Path(sys.executable)
    # Find a pip adjacent to the interpreter if possible.
    candidate = python.parent / "pip"
    if candidate.exists():
        return python, candidate
    pip = _which_or_none("pip") or _which_or_none("pip3")
    if pip is None:
        # Best-effort: invoke `python -m pip` via the interpreter path.
        return python, python
    return python, Path(pip)


def detect_venv(
    project_root: Path,
    prefer: str = "auto",
) -> Tuple[str, Path, Path]:
    """Return (kind, python, pip) for the chosen virtual environment.

    ``prefer`` may be one of ``"auto"``, ``"pipenv"``, ``"poetry"``,
    ``"uv"``, ``"system"``.

    Detection order for ``"auto"`` is: pipenv > poetry > uv > system.
    """

    def _system_detector(root: Path) -> Tuple[Path, Path]:
        python, pip = _detect_system()
        return python, pip

    detectors = {
        "pipenv": _detect_pipenv,
        "poetry": _detect_poetry,
        "uv": _detect_uv,
        "system": _system_detector,
    }

    if prefer == "auto":
        order = ("pipenv", "poetry", "uv", "system")
    elif prefer in detectors:
        order = (prefer, "system")  # fall back to system if requested not found
    else:
        raise ValueError(f"unknown venv preference: {prefer!r}")

    for kind in order:
        detector = detectors[kind]
        try:
            if kind == "system":
                python, pip = detector(project_root)
                return "system", python, pip
            result = detector(project_root)
        except (FileNotFoundError, OSError):
            continue
        if result is not None:
            python, pip = result
            return kind, python, pip

    # Auto path with no hits: this means pipenv/poetry/uv all failed and we
    # already returned system in the loop. So we only reach here if a specific
    # preference was requested AND not found AND system was tried and also
    # failed. Treat that as a hard error.
    raise RuntimeError(
        f"could not find a usable virtual environment (prefer={prefer!r}); "
        "install pipenv, poetry, or uv, or pass --venv system"
    )


def _find_proto_dir(root: Path) -> Optional[Path]:
    """Locate the directory containing the arduino-cli `.proto` files.

    The arduino-cli protos use absolute import paths like
    ``cc/arduino/cli/commands/v1/common.proto``, so the include path passed
    to protoc must be the **root** of the checkout, not the v1 subdir.
    Returns the *root* (not the v1 subdir) so protoc can resolve all
    ``cc/arduino/cli/...`` imports.
    """
    candidate = root / PROTO_SUBDIR
    if candidate.is_dir() and any(candidate.glob("*.proto")):
        return root
    if any(root.glob(f"{PROTO_SUBDIR}/**/*.proto")):
        return root
    return None


def _download_proto_archive(url: str, keep_temp: bool) -> Path:
    """Download a zip from ``url`` and return the extracted directory.

    The zip is downloaded into a temporary directory. If ``keep_temp`` is
    true, the parent directory is preserved (returned path itself still
    points at the extracted content).
    """
    tmpdir = tempfile.mkdtemp(prefix="arduino-cli-protos-")
    print(f"downloading {url} -> {tmpdir}/proto.zip")
    zip_path = Path(tmpdir) / "proto.zip"
    try:
        with urllib.request.urlopen(url) as resp, open(zip_path, "wb") as out:
            shutil.copyfileobj(resp, out)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to download {url}: {exc}") from exc

    print(f"extracting {zip_path}")
    extract_dir = Path(tmpdir) / "extracted"
    extract_dir.mkdir()
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)

    # The zip may contain a single top-level directory (common for GitHub
    # release assets); recurse into it if so.
    entries = list(extract_dir.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_dir


def resolve_proto_src(
    args: argparse.Namespace,
) -> Tuple[Path, Optional[Path]]:
    """Return (proto_dir, cleanup_temp_dir_or_None).

    ``proto_dir`` is the directory containing the arduino-cli `.proto`
    files. ``cleanup_temp_dir_or_None`` is a temp directory that the caller
    should clean up (unless ``--keep-temp`` was passed), or None if no
    cleanup is needed.
    """
    if args.proto_src is not None:
        root = args.proto_src.expanduser().resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"--proto-src is not a directory: {root}")
        proto_dir = _find_proto_dir(root)
        if proto_dir is None:
            raise FileNotFoundError(
                f"no .proto files found under {root}/{PROTO_SUBDIR} "
                f"(looked for {root / PROTO_SUBDIR})"
            )
        return proto_dir, None

    if args.proto_url is not None:
        extracted = _download_proto_archive(args.proto_url, args.keep_temp)
        proto_dir = _find_proto_dir(extracted)
        if proto_dir is None:
            raise FileNotFoundError(
                f"downloaded archive at {extracted} does not contain "
                f"{PROTO_SUBDIR}/*.proto"
            )
        # Caller cleans up extracted.parent if --keep-temp is not set.
        return proto_dir, extracted.parent if not args.keep_temp else None

    raise AssertionError("unreachable: caller must ensure proto_src or proto_url")


def _venv_pip_install(python: Path, packages: Sequence[str]) -> None:
    """Run ``python -m pip install`` for the given packages."""
    cmd = [str(python), "-m", "pip", "install", "--upgrade", *packages]
    print(f"running: {' '.join(cmd)}")
    _run(cmd)


def _prompt_yes_no(question: str) -> bool:
    """Prompt the user for a yes/no answer. Returns True for y, False for n."""
    try:
        reply = input(f"{question} [y/N] ").strip().lower()
    except EOFError:
        return False
    return reply in ("y", "yes")


def _check_python_imports(python: Path, modules: Sequence[str]) -> bool:
    """Return True if all modules import cleanly in the given interpreter."""
    code = (
        "import importlib, sys; "
        "sys.exit(0 if all(importlib.util.find_spec(m) for m in "
        "{modules!r}) else 1)"
    ).format(modules=list(modules))
    result = subprocess.run(
        [str(python), "-c", code],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def ensure_grpc_tools(
    python: Path,
    install: bool,
    no_prompt: bool,
) -> None:
    """Make sure ``grpcio-tools`` and ``googleapis-common-protos`` are
    importable in the given interpreter.

    If not, install them — either unconditionally (``install`` is True or
    ``no_prompt`` is True) or after prompting the user.
    """
    if _check_python_imports(python, REQUIRED_PYTHON_PACKAGES):
        print(f"deps present in {python}: {', '.join(REQUIRED_PYTHON_PACKAGES)}")
        return

    if not (install or no_prompt):
        prompt = (
            f"grpcio-tools and/or googleapis-common-protos are missing from "
            f"{python}. Install now?"
        )
        if not _prompt_yes_no(prompt):
            raise RuntimeError(
                "missing required packages and install was declined; "
                "rerun with --install-deps or install manually"
            )

    _venv_pip_install(python, REQUIRED_PYTHON_PACKAGES)


def _find_grpc_tools_proto_root() -> Optional[Path]:
    """Locate the directory containing the well-known `.proto` files that
    ship with ``grpc_tools``. Returns the parent of ``google/protobuf`` (and
    ``google/rpc`` if present) so imports like ``google/protobuf/any.proto``
    and ``google/rpc/status.proto`` resolve.
    """
    try:
        import grpc_tools  # type: ignore[import-not-found]
    except ImportError:
        return None
    grpc_tools_path = Path(grpc_tools.__file__).resolve().parent
    candidate = grpc_tools_path / "_proto"
    if (candidate / "google" / "protobuf").is_dir():
        return candidate
    return None


def _find_googleapis_protos() -> Optional[Path]:
    """Locate the directory containing the .proto files shipped with
    ``googleapis-common-protos`` (e.g. ``google/rpc/status.proto``).
    Returns the directory that has a ``google`` subdir.
    """
    try:
        # `google` is a namespace package, so import a submodule to get
        # a concrete path.
        import google.rpc.status_pb2 as mod  # type: ignore[import-not-found]
    except ImportError:
        return None
    mod_path = Path(mod.__file__).resolve()
    # mod_path is something like site-packages/google/rpc/status_pb2.py
    # We want site-packages/ (the directory containing `google/`).
    rpc_dir = mod_path.parent  # .../google/rpc
    google_dir = rpc_dir.parent  # .../google
    return google_dir.parent  # site-packages/


def generate_stubs(
    proto_dir: Path,
    out_dir: Path,
    googleapis_src: Optional[Path] = None,
) -> int:
    """Invoke ``grpc_tools.protoc`` to generate stubs.

    ``proto_dir`` is the *root* of the arduino-cli rpc checkout (the include
    path). The actual `.proto` files live under
    ``<proto_dir>/cc/arduino/cli/commands/v1/``.

    Returns the number of `.proto` files generated.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    actual_proto_dir = proto_dir / PROTO_SUBDIR
    proto_files = sorted(p for p in actual_proto_dir.glob("*.proto") if p.is_file())
    if not proto_files:
        raise FileNotFoundError(f"no .proto files in {actual_proto_dir}")

    argv = [
        "protoc",
        f"--proto_path={proto_dir}",
        f"--python_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        f"--pyi_out={out_dir}",
    ]

    grpc_tools_proto_root = _find_grpc_tools_proto_root()
    if grpc_tools_proto_root is not None:
        argv.append(f"--proto_path={grpc_tools_proto_root}")
        print(f"include (grpc_tools): {grpc_tools_proto_root}")
    else:
        print(
            "warning: could not locate grpc_tools well-known protos; "
            "google/protobuf/any.proto imports will fail",
            file=sys.stderr,
        )

    googleapis_protos = googleapis_src or _find_googleapis_protos()
    if googleapis_protos is not None:
        argv.append(f"--proto_path={googleapis_protos}")
        print(f"include (googleapis): {googleapis_protos}")
    else:
        print(
            "warning: could not locate googleapis-common-protos .proto files; "
            "google/rpc/status.proto imports will fail",
            file=sys.stderr,
        )

    argv.extend(str(p) for p in proto_files)

    print(f"running: grpc_tools.protoc {' '.join(argv[1:])}")
    # Import lazily so the function can be parsed even if grpc_tools is not
    # installed (the caller should have called ensure_grpc_tools first).
    from grpc_tools import protoc as grpc_protoc  # type: ignore[import-not-found]

    rc = grpc_protoc.main(argv)
    if rc != 0:
        raise RuntimeError(f"grpc_tools.protoc failed with return code {rc}")

    return len(proto_files)


def ensure_init_chain(out_dir: Path) -> int:
    """Create empty ``__init__.py`` files in every parent directory of
    ``out_dir``'s actual generated package and inside the package itself,
    so the generated stubs can be imported as ``cc.arduino.cli.commands.v1``.

    ``out_dir`` is the root passed to protoc. The actual generated package
    lives at ``<out_dir>/cc/arduino/cli/commands/v1``. We ensure
    ``__init__.py`` files in each segment of the package path, and stop
    at the first existing ``__init__.py`` on the way up.

    Returns the number of ``__init__.py`` files created.
    """
    pkg_dir = out_dir / PROTO_SUBDIR
    created = 0

    # Make the leaf package importable.
    init_in_pkg = pkg_dir / "__init__.py"
    if not init_in_pkg.exists():
        init_in_pkg.touch()
        created += 1

    # Walk upward through parent directories until we hit an existing
    # __init__.py, escape ``out_dir``, or run out of parents.
    parent = pkg_dir.parent
    while parent.exists() and parent != out_dir and parent != parent.parent:
        candidate = parent / "__init__.py"
        if candidate.exists():
            break
        candidate.touch()
        created += 1
        parent = parent.parent

    return created


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gen_grpc_bindings",
        description=(
            "Regenerate Python gRPC stubs for the arduino-cli gRPC service. "
            "Provide either --proto-src (local checkout of arduino-cli/rpc) "
            "or --proto-url (URL to a release zip)."
        ),
    )
    p.add_argument(
        "--proto-src",
        type=Path,
        default=None,
        help="Path to a local arduino-cli checkout (the directory containing "
        "the `cc/arduino/cli/commands/v1/*.proto` files).",
    )
    p.add_argument(
        "--proto-url",
        type=str,
        default=None,
        help="URL to a zip archive that contains the arduino-cli rpc protos "
        "(e.g. a GitHub release asset).",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=STUB_OUT,
        help=f"Output directory for generated stubs (default: {STUB_OUT}).",
    )
    p.add_argument(
        "--googleapis-src",
        type=Path,
        default=None,
        help="Path to a local googleapis checkout. If not provided, "
        "googleapis-common-protos is used for well-known types.",
    )
    p.add_argument(
        "--venv",
        choices=("auto", "pipenv", "poetry", "uv", "system"),
        default="auto",
        help="Which virtual environment to use (default: auto-detect).",
    )
    p.add_argument(
        "--install-deps",
        action="store_true",
        help="Install grpcio-tools and googleapis-common-protos into the "
        "chosen environment if missing.",
    )
    p.add_argument(
        "--no-prompt",
        action="store_true",
        help="Never prompt for confirmation. Implies --install-deps.",
    )
    p.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary directory used for downloaded proto archives.",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.proto_src and not args.proto_url:
        print(
            "error: must provide either --proto-src or --proto-url",
            file=sys.stderr,
        )
        return 2

    if args.no_prompt:
        args.install_deps = True

    try:
        kind, python, pip = detect_venv(ARDUINO_GRPC_DIR, prefer=args.venv)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    try:
        proto_dir, cleanup = resolve_proto_src(args)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4

    print(f"repo root:        {REPO_ROOT}")
    print(f"arduino_grpc dir: {ARDUINO_GRPC_DIR}")
    print(f"output dir:       {args.out}")
    print(f"proto dir:        {proto_dir}")
    print(f"venv preference:  {args.venv}")
    print(f"detected venv:    {kind} (python={python}, pip={pip})")
    print(f"install deps:     {args.install_deps}")
    print(f"no-prompt:        {args.no_prompt}")
    sys.stdout.flush()

    try:
        ensure_grpc_tools(python, args.install_deps, args.no_prompt)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        if cleanup is not None:
            shutil.rmtree(cleanup, ignore_errors=True)
        return 5

    try:
        n = generate_stubs(proto_dir, args.out, args.googleapis_src)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        if cleanup is not None:
            shutil.rmtree(cleanup, ignore_errors=True)
        return 6

    n_init = ensure_init_chain(args.out)

    print(f"generated stubs for {n} .proto file(s) into {args.out}")
    print(f"created {n_init} __init__.py file(s)")

    if cleanup is not None:
        try:
            shutil.rmtree(cleanup)
            print(f"cleaned up temp:   {cleanup}")
        except OSError as exc:
            print(f"warning: failed to remove {cleanup}: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
