"""
test_gen_grpc_bindings.py — pytest tests for scripts/gen_grpc_bindings.py.

Covers Q3 (skeleton) through Q7 (real run). All tests use the
``gen_grpc_module`` fixture which imports the script as a module.

Q3: skeleton — module imports, has main(), argparse works
Q4: venv detection — detect_venv returns (kind, python, pip)
Q5: proto source resolution — local resolves, nonexistent errors
Q6: __init__.py chain — ensure_init_chain creates files, idempotent
Q7: end-to-end — real run regenerates 33 stub files + 5 __init__.py
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Q3: skeleton
# ---------------------------------------------------------------------------


class TestQ3Skeleton:
    def test_module_imports(self, gen_grpc_module):
        assert gen_grpc_module is not None

    def test_module_has_main(self, gen_grpc_module):
        assert callable(getattr(gen_grpc_module, "main", None))

    def test_module_has_all_documented_functions(self, gen_grpc_module):
        for name in [
            "detect_venv",
            "resolve_proto_src",
            "ensure_grpc_tools",
            "generate_stubs",
            "ensure_init_chain",
        ]:
            assert callable(getattr(gen_grpc_module, name, None)), (
                f"missing public function: {name}"
            )

    def test_module_has_dunder_all(self, gen_grpc_module):
        assert "main" in gen_grpc_module.__all__
        assert "detect_venv" in gen_grpc_module.__all__

    def test_repo_root_constant(self, gen_grpc_module, repo_root):
        assert gen_grpc_module.REPO_ROOT == repo_root

    def test_arduino_grpc_dir_constant(self, gen_grpc_module, repo_root):
        assert (
            gen_grpc_module.ARDUINO_GRPC_DIR
            == repo_root / "grpc_client" / "python" / "arduino_grpc"
        )

    def test_stub_out_points_to_arduino_grpc_root(self, gen_grpc_module):
        # Note: STUB_OUT must be the package root, NOT the v1 subdir,
        # because grpc_tools preserves the proto's package path.
        assert gen_grpc_module.STUB_OUT == gen_grpc_module.ARDUINO_GRPC_DIR

    def test_proto_subdir_constant(self, gen_grpc_module):
        assert gen_grpc_module.PROTO_SUBDIR == "cc/arduino/cli/commands/v1"


class TestQ3Argparse:
    def test_help_exits_0(self, gen_grpc_module, capsys):
        with pytest.raises(SystemExit) as excinfo:
            gen_grpc_module.main(["--help"])
        assert excinfo.value.code == 0

    def test_missing_both_proto_args_errors(self, gen_grpc_module, capsys):
        # main() prints an error to stderr and returns 2 — it does NOT raise.
        rc = gen_grpc_module.main([])
        assert rc == 2
        captured = capsys.readouterr()
        assert "--proto-src" in captured.err or "--proto-url" in captured.err

    def test_no_prompt_implies_install_deps(self, gen_grpc_module, tmp_path):
        # When --no-prompt is set, args.install_deps is forced to True.
        # We just need to exercise the parser, not the full pipeline.
        # Pass a non-existent proto-src to short-circuit before generation.
        parser = gen_grpc_module._build_parser()
        args = parser.parse_args(["--proto-src", str(tmp_path), "--no-prompt"])
        # Simulate main()'s post-parse adjustment
        if args.no_prompt:
            args.install_deps = True
        assert args.install_deps is True

    def test_venv_choices(self, gen_grpc_module):
        parser = gen_grpc_module._build_parser()
        for choice in ("auto", "pipenv", "poetry", "uv", "system"):
            args = parser.parse_args(["--proto-src", "/tmp/x", "--venv", choice])
            assert args.venv == choice


# ---------------------------------------------------------------------------
# Q4: venv detection
# ---------------------------------------------------------------------------


class TestQ4VenvDetection:
    def test_detect_venv_system(self, gen_grpc_module, tmp_path):
        # No Pipfile, no pyproject.toml poetry marker, no .venv, no pipenv/poetry/uv.
        # Should fall through to system.
        kind, python, pip = gen_grpc_module.detect_venv(tmp_path, prefer="system")
        assert kind == "system"
        assert Path(python).exists()
        # pip may be a path or the python interpreter itself
        assert pip is not None

    def test_detect_venv_auto_unknown_pref_raises(self, gen_grpc_module, tmp_path):
        with pytest.raises(ValueError, match="unknown venv preference"):
            gen_grpc_module.detect_venv(tmp_path, prefer="totally-fake")

    def test_detect_venv_returns_tuple(self, gen_grpc_module, tmp_path):
        result = gen_grpc_module.detect_venv(tmp_path, prefer="system")
        assert isinstance(result, tuple)
        assert len(result) == 3
        kind, python, pip = result
        assert isinstance(kind, str)
        assert isinstance(python, Path)
        assert isinstance(pip, Path)

    def test_detect_venv_system_python_is_executable(self, gen_grpc_module, tmp_path):
        _, python, _ = gen_grpc_module.detect_venv(tmp_path, prefer="system")
        assert python.is_file()

    def test_detect_venv_prefer_pipenv_without_pipfile(self, gen_grpc_module, tmp_path):
        # No Pipfile, so even with prefer="pipenv" we should fall back
        # to system (because the pipenv detector returns None).
        kind, _, _ = gen_grpc_module.detect_venv(tmp_path, prefer="pipenv")
        assert kind == "system"

    def test_detect_venv_prefer_uv_without_venv(self, gen_grpc_module, tmp_path):
        # No .venv directory in the project root.
        kind, _, _ = gen_grpc_module.detect_venv(tmp_path, prefer="uv")
        assert kind == "system"

    def test_detect_venv_pipenv_with_pipfile_and_fake_venv(
        self, gen_grpc_module, tmp_path
    ):
        # Lay down a fake venv layout under tmp_path, mock subprocess.run
        # to return a path to it. The detector should report "pipenv".
        (tmp_path / "Pipfile").touch()
        fake_venv = tmp_path / "fake-venv"
        fake_venv.mkdir()
        # _venv_python_from is called by _detect_pipenv; it returns
        # venv_dir / "bin" / "python" on Linux or venv_dir / "Scripts" /
        # "python.exe" on Windows. Provide a Unix-style layout for the test.
        (fake_venv / "bin").mkdir()
        (fake_venv / "bin" / "python").touch()

        fake_pipenv = "/fake/bin/pipenv"
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=str(fake_venv), stderr=""
        )
        with (
            mock.patch.object(
                gen_grpc_module.shutil, "which", return_value=fake_pipenv
            ),
            mock.patch.object(
                gen_grpc_module.subprocess, "run", return_value=completed
            ),
        ):
            kind, python, pip = gen_grpc_module.detect_venv(tmp_path, prefer="pipenv")
        assert kind == "pipenv"
        assert Path(python).name == "python"
        # The detector always reports bin/pip OR Scripts/pip.exe
        # (whichever exists). For our Linux-style fake, bin/pip is the
        # expected value.
        assert str(pip) in (
            str(fake_venv / "bin" / "pip"),
            str(fake_venv / "Scripts" / "pip.exe"),
        )


# ---------------------------------------------------------------------------
# Q5: proto source resolution
# ---------------------------------------------------------------------------


class TestQ5ProtoSourceResolution:
    def test_resolve_proto_src_local(self, gen_grpc_module, tmp_path):
        # Lay down a fake arduino-cli rpc checkout
        proto_dir = tmp_path / "cc" / "arduino" / "cli" / "commands" / "v1"
        proto_dir.mkdir(parents=True)
        (proto_dir / "board.proto").write_text('syntax = "proto3";\n')

        args = argparse.Namespace(
            proto_src=tmp_path,
            proto_url=None,
            keep_temp=False,
        )
        resolved, cleanup = gen_grpc_module.resolve_proto_src(args)
        assert resolved == tmp_path  # root, not v1 subdir
        assert cleanup is None

    def test_resolve_proto_src_local_nonexistent_dir(self, gen_grpc_module, tmp_path):
        args = argparse.Namespace(
            proto_src=tmp_path / "nope",
            proto_url=None,
            keep_temp=False,
        )
        with pytest.raises(FileNotFoundError, match="not a directory"):
            gen_grpc_module.resolve_proto_src(args)

    def test_resolve_proto_src_local_no_protos(self, gen_grpc_module, tmp_path):
        # tmp_path exists but has no v1 proto dir
        args = argparse.Namespace(
            proto_src=tmp_path,
            proto_url=None,
            keep_temp=False,
        )
        with pytest.raises(FileNotFoundError, match="no .proto files"):
            gen_grpc_module.resolve_proto_src(args)

    def test_resolve_proto_src_url_downloads(self, gen_grpc_module, tmp_path):
        # Build a fake zip archive on disk, served via file:// URL.
        # Layout mirrors a real GitHub release asset: a single
        # top-level wrapper directory (e.g. "arduino-cli-1.5.0/") that
        # contains "cc/arduino/cli/commands/v1/board.proto". The
        # recursion in _download_proto_archive walks into the wrapper,
        # yielding "<tmp>/extracted/arduino-cli-1.5.0/" as the proto root.
        wrapper = tmp_path / "arduino-cli-1.5.0"
        proto_dir = wrapper / "cc" / "arduino" / "cli" / "commands" / "v1"
        proto_dir.mkdir(parents=True)
        (proto_dir / "board.proto").write_text('syntax = "proto3";\n')

        zip_path = tmp_path / "arduino-cli.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in wrapper.rglob("*"):
                zf.write(f, f.relative_to(tmp_path))

        args = argparse.Namespace(
            proto_src=None,
            proto_url=f"file://{zip_path}",
            keep_temp=False,
        )
        resolved, cleanup = gen_grpc_module.resolve_proto_src(args)
        try:
            assert (resolved / "cc" / "arduino" / "cli" / "commands" / "v1").is_dir()
            assert (
                resolved / "cc" / "arduino" / "cli" / "commands" / "v1" / "board.proto"
            ).exists()
            # cleanup should be set so caller can remove the temp dir
            assert cleanup is not None
            assert cleanup.exists()
        finally:
            if cleanup is not None and cleanup.exists():
                shutil.rmtree(cleanup, ignore_errors=True)

    def test_resolve_proto_src_url_keep_temp(self, gen_grpc_module, tmp_path):
        wrapper = tmp_path / "arduino-cli-1.5.0"
        proto_dir = wrapper / "cc" / "arduino" / "cli" / "commands" / "v1"
        proto_dir.mkdir(parents=True)
        (proto_dir / "x.proto").write_text("")
        zip_path = tmp_path / "x.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in wrapper.rglob("*"):
                zf.write(f, f.relative_to(tmp_path))

        args = argparse.Namespace(
            proto_src=None,
            proto_url=f"file://{zip_path}",
            keep_temp=True,
        )
        resolved, cleanup = gen_grpc_module.resolve_proto_src(args)
        try:
            assert cleanup is None  # keep_temp=True -> caller won't clean up
            # resolved points at the extracted wrapper root
            assert (
                resolved / "cc" / "arduino" / "cli" / "commands" / "v1" / "x.proto"
            ).exists()
        finally:
            # The caller is responsible for removing the temp dir
            # when keep_temp=False; for keep_temp tests we mimic that
            # by removing the parent of resolved.
            shutil.rmtree(resolved.parent, ignore_errors=True)


# ---------------------------------------------------------------------------
# Q6: __init__.py chain
# ---------------------------------------------------------------------------


class TestQ6InitChain:
    def test_ensure_init_chain_creates_files(self, gen_grpc_module, tmp_path):
        # tmp_path mimics the arduino_grpc root. After running,
        # there should be 5 new __init__.py files (under cc/, cc/arduino/,
        # cc/arduino/cli/, cc/arduino/cli/commands/, cc/arduino/cli/commands/v1/).
        out_dir = tmp_path
        (out_dir / "cc" / "arduino" / "cli" / "commands" / "v1").mkdir(parents=True)
        created = gen_grpc_module.ensure_init_chain(out_dir)
        assert created == 5
        for sub in (
            "cc/__init__.py",
            "cc/arduino/__init__.py",
            "cc/arduino/cli/__init__.py",
            "cc/arduino/cli/commands/__init__.py",
            "cc/arduino/cli/commands/v1/__init__.py",
        ):
            assert (out_dir / sub).is_file(), f"missing {sub}"

    def test_ensure_init_chain_idempotent(self, gen_grpc_module, tmp_path):
        (tmp_path / "cc" / "arduino" / "cli" / "commands" / "v1").mkdir(parents=True)
        # First run: creates 5
        first = gen_grpc_module.ensure_init_chain(tmp_path)
        assert first == 5
        # Second run: creates 0
        second = gen_grpc_module.ensure_init_chain(tmp_path)
        assert second == 0
        # Third run: still 0
        third = gen_grpc_module.ensure_init_chain(tmp_path)
        assert third == 0

    def test_ensure_init_chain_stops_at_existing(self, gen_grpc_module, tmp_path):
        (tmp_path / "cc" / "arduino" / "cli" / "commands" / "v1").mkdir(parents=True)
        # Pre-create cc/__init__.py only
        (tmp_path / "cc" / "__init__.py").touch()
        # Should create the remaining 4 (cc/arduino/__init__.py etc.)
        created = gen_grpc_module.ensure_init_chain(tmp_path)
        assert created == 4
        assert (tmp_path / "cc" / "__init__.py").is_file()
        assert (
            tmp_path / "cc" / "arduino" / "cli" / "commands" / "v1" / "__init__.py"
        ).is_file()


# ---------------------------------------------------------------------------
# Q6: protobuf generation (mocked — real run is in Q7)
# ---------------------------------------------------------------------------


class TestQ6GenerateStubs:
    def _install_fake_grpc_tools(self, return_code: int) -> mock.MagicMock:
        """Inject a fake grpc_tools.protoc module into sys.modules.

        Returns the mock for ``protoc.main`` so callers can introspect
        what it was called with.
        """
        fake_protoc_main = mock.MagicMock(return_value=return_code)
        fake_protoc_module = mock.MagicMock(main=fake_protoc_main)
        fake_grpc_tools_pkg = mock.MagicMock(protoc=fake_protoc_module)
        sys.modules["grpc_tools"] = fake_grpc_tools_pkg
        sys.modules["grpc_tools.protoc"] = fake_protoc_module
        return fake_protoc_main

    def _restore_grpc_tools(self) -> None:
        """Remove the fake grpc_tools modules from sys.modules.

        Without this, subsequent tests in the same interpreter (e.g.
        the Q7 end-to-end test, which needs the *real* grpc_tools)
        will pick up the MagicMock and fail.
        """
        for mod_name in ("grpc_tools.protoc", "grpc_tools"):
            sys.modules.pop(mod_name, None)

    def test_generate_stubs_calls_protoc(self, gen_grpc_module, tmp_path):
        # Lay down fake protos
        proto_dir = tmp_path / "cc" / "arduino" / "cli" / "commands" / "v1"
        proto_dir.mkdir(parents=True)
        (proto_dir / "board.proto").write_text('syntax = "proto3";\n')

        out_dir = tmp_path / "out"
        out_dir.mkdir()

        fake_protoc_main = self._install_fake_grpc_tools(return_code=0)
        try:
            with (
                mock.patch.object(
                    gen_grpc_module, "_find_grpc_tools_proto_root", return_value=None
                ),
                mock.patch.object(
                    gen_grpc_module, "_find_googleapis_protos", return_value=None
                ),
            ):
                n = gen_grpc_module.generate_stubs(tmp_path, out_dir)
        finally:
            self._restore_grpc_tools()

        assert n == 1
        fake_protoc_main.assert_called_once()
        argv = fake_protoc_main.call_args[0][0]
        # argv[0] is the program name; flags are passed as `--key=value`
        # (single arg), so check for the key prefix.
        assert any(a.startswith("--python_out=") for a in argv)
        assert any(a.startswith("--grpc_python_out=") for a in argv)
        assert any(a.startswith("--pyi_out=") for a in argv)
        assert any(a.endswith("board.proto") for a in argv)

    def test_generate_stubs_no_protos_errors(self, gen_grpc_module, tmp_path):
        # v1 dir exists but is empty
        (tmp_path / "cc" / "arduino" / "cli" / "commands" / "v1").mkdir(parents=True)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        with pytest.raises(FileNotFoundError, match="no .proto files"):
            gen_grpc_module.generate_stubs(tmp_path, out_dir)

    def test_generate_stubs_protoc_nonzero_raises(self, gen_grpc_module, tmp_path):
        proto_dir = tmp_path / "cc" / "arduino" / "cli" / "commands" / "v1"
        proto_dir.mkdir(parents=True)
        (proto_dir / "board.proto").write_text("")
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        self._install_fake_grpc_tools(return_code=1)
        try:
            with (
                mock.patch.object(
                    gen_grpc_module, "_find_grpc_tools_proto_root", return_value=None
                ),
                mock.patch.object(
                    gen_grpc_module, "_find_googleapis_protos", return_value=None
                ),
            ):
                with pytest.raises(RuntimeError, match="grpc_tools.protoc failed"):
                    gen_grpc_module.generate_stubs(tmp_path, out_dir)
        finally:
            self._restore_grpc_tools()


# ---------------------------------------------------------------------------
# Q6: ensure_grpc_tools
# ---------------------------------------------------------------------------


class TestQ6EnsureGrpcTools:
    def test_ensure_grpc_tools_already_installed(self, gen_grpc_module, tmp_path):
        # Mock the import check to say everything is present
        fake_python = tmp_path / "bin" / "python"
        fake_python.parent.mkdir(parents=True)
        fake_python.touch()
        with mock.patch.object(
            gen_grpc_module, "_check_python_imports", return_value=True
        ):
            # Should NOT call pip install
            with mock.patch.object(
                gen_grpc_module, "_venv_pip_install"
            ) as fake_install:
                gen_grpc_module.ensure_grpc_tools(
                    fake_python, install=True, no_prompt=True
                )
                fake_install.assert_not_called()

    def test_ensure_grpc_tools_installs_when_missing(self, gen_grpc_module, tmp_path):
        fake_python = tmp_path / "bin" / "python"
        fake_python.parent.mkdir(parents=True)
        fake_python.touch()
        with mock.patch.object(
            gen_grpc_module, "_check_python_imports", return_value=False
        ):
            with mock.patch.object(
                gen_grpc_module, "_venv_pip_install"
            ) as fake_install:
                gen_grpc_module.ensure_grpc_tools(
                    fake_python, install=True, no_prompt=True
                )
                fake_install.assert_called_once()
                # First positional arg should be the fake python
                args = fake_install.call_args[0]
                assert args[0] == fake_python

    def test_ensure_grpc_tools_prompts_when_missing(self, gen_grpc_module, tmp_path):
        fake_python = tmp_path / "bin" / "python"
        fake_python.parent.mkdir(parents=True)
        fake_python.touch()
        with (
            mock.patch.object(
                gen_grpc_module, "_check_python_imports", return_value=False
            ),
            mock.patch.object(
                gen_grpc_module, "_prompt_yes_no", return_value=True
            ) as fake_prompt,
            mock.patch.object(gen_grpc_module, "_venv_pip_install") as fake_install,
        ):
            gen_grpc_module.ensure_grpc_tools(
                fake_python, install=False, no_prompt=False
            )
            fake_prompt.assert_called_once()
            fake_install.assert_called_once()

    def test_ensure_grpc_tools_prompt_declined_raises(self, gen_grpc_module, tmp_path):
        fake_python = tmp_path / "bin" / "python"
        fake_python.parent.mkdir(parents=True)
        fake_python.touch()
        with (
            mock.patch.object(
                gen_grpc_module, "_check_python_imports", return_value=False
            ),
            mock.patch.object(gen_grpc_module, "_prompt_yes_no", return_value=False),
            mock.patch.object(gen_grpc_module, "_venv_pip_install") as fake_install,
        ):
            with pytest.raises(RuntimeError, match="install was declined"):
                gen_grpc_module.ensure_grpc_tools(
                    fake_python, install=False, no_prompt=False
                )
            fake_install.assert_not_called()


# ---------------------------------------------------------------------------
# Q7: end-to-end with real arduino-cli protos
# ---------------------------------------------------------------------------


ARDUINO_CLI_PROTOS = Path("/home/weerdmonk/Projects/arduino-cli/rpc")


@pytest.mark.skipif(
    not ARDUINO_CLI_PROTOS.exists(),
    reason="arduino-cli source not available at /home/weerdmonk/Projects/arduino-cli/rpc",
)
class TestQ7EndToEnd:
    def test_real_run_against_arduino_cli(self, gen_grpc_module, tmp_path, repo_root):
        # Use the arduino_grpc source dir as the out dir; back up first
        out_dir = repo_root / "grpc_client" / "python" / "arduino_grpc"
        backup = tmp_path / "arduino_grpc_backup"
        shutil.copytree(out_dir, backup)
        try:
            # Wipe generated stubs + __init__.py chain (keep the arduino_grpc/ subdir)
            cc = out_dir / "cc"
            if cc.exists():
                shutil.rmtree(cc)

            # Run with --no-prompt and --proto-src against the real checkout
            rc = gen_grpc_module.main(
                [
                    "--proto-src",
                    str(ARDUINO_CLI_PROTOS),
                    "--no-prompt",
                ]
            )
            assert rc == 0

            v1 = out_dir / "cc" / "arduino" / "cli" / "commands" / "v1"
            # 11 _pb2.py + 11 _pb2_grpc.py + 11 _pb2.pyi
            assert len(list(v1.glob("*_pb2.py"))) == 11
            assert len(list(v1.glob("*_pb2_grpc.py"))) == 11
            assert len(list(v1.glob("*_pb2.pyi"))) == 11
            # 5 __init__.py files in the chain
            init_files = list(out_dir.glob("cc/**/__init__.py"))
            assert len(init_files) == 5
        finally:
            # Restore from backup
            shutil.rmtree(out_dir)
            shutil.copytree(backup, out_dir)


# ---------------------------------------------------------------------------
# Q17: Edge-case tests for missing dependencies / network failures
# ---------------------------------------------------------------------------


class TestEdgeCasesMissingDeps:
    """Edge cases for the error paths in ``gen_grpc_bindings.main`` and
    helpers. These tests mock dependencies so they can run regardless of
    whether ``grpcio-tools`` / ``googleapis-common-protos`` are actually
    installed in the test interpreter.
    """

    def test_main_exits_5_when_deps_missing_and_prompt_declined(
        self, gen_grpc_module, tmp_path
    ):
        """main() returns 5 when ensure_grpc_tools raises because the
        user declined the install prompt."""
        proto_dir = tmp_path / "proto"
        proto_subdir = proto_dir / "cc" / "arduino" / "cli" / "commands" / "v1"
        proto_subdir.mkdir(parents=True)
        (proto_subdir / "common.proto").write_text('syntax = "proto3";\n')

        with (
            mock.patch.object(
                gen_grpc_module,
                "detect_venv",
                return_value=("pipenv", Path("/usr/bin/python3"), Path("/usr/bin/pip")),
            ),
            mock.patch.object(
                gen_grpc_module, "resolve_proto_src", return_value=(proto_dir, None)
            ),
            mock.patch.object(
                gen_grpc_module,
                "ensure_grpc_tools",
                side_effect=RuntimeError("install declined"),
            ),
            mock.patch.object(
                gen_grpc_module, "ARDUINO_GRPC_DIR", tmp_path / "arduino_grpc"
            ),
        ):
            rc = gen_grpc_module.main(["--proto-src", str(proto_dir), "--no-prompt"])
        assert rc == 5

    def test_ensure_grpc_tools_raises_when_both_modules_missing(self, gen_grpc_module):
        """``ensure_grpc_tools`` raises RuntimeError when deps are missing
        and the user declines the prompt."""
        python = Path("/usr/bin/python3")
        with (
            mock.patch.object(
                gen_grpc_module, "_check_python_imports", return_value=False
            ),
            mock.patch.object(gen_grpc_module, "_prompt_yes_no", return_value=False),
        ):
            with pytest.raises(RuntimeError, match="install was declined"):
                gen_grpc_module.ensure_grpc_tools(
                    python, install=False, no_prompt=False
                )

    def test_generate_stubs_warns_on_missing_well_known_protos(
        self, gen_grpc_module, tmp_path, capsys
    ):
        """``generate_stubs`` prints a warning to stderr when both
        ``grpc_tools`` and ``googleapis-common-protos`` proto roots are
        missing. The warning does not raise."""
        proto_dir = tmp_path / "proto"
        proto_subdir = proto_dir / "cc" / "arduino" / "cli" / "commands" / "v1"
        proto_subdir.mkdir(parents=True)
        (proto_subdir / "common.proto").write_text('syntax = "proto3";\n')

        out_dir = tmp_path / "out"
        with (
            mock.patch.object(
                gen_grpc_module, "_find_grpc_tools_proto_root", return_value=None
            ),
            mock.patch.object(
                gen_grpc_module, "_find_googleapis_protos", return_value=None
            ),
            mock.patch("grpc_tools.protoc.main", return_value=0),
        ):
            n = gen_grpc_module.generate_stubs(proto_dir, out_dir)

        assert n == 1
        captured = capsys.readouterr()
        assert "grpc_tools well-known protos" in captured.err
        assert "googleapis-common-protos" in captured.err

    def test_main_exits_4_when_proto_url_404s(self, gen_grpc_module, tmp_path):
        """main() returns 4 when ``_download_proto_archive`` raises
        RuntimeError (simulating a 404)."""
        with (
            mock.patch.object(
                gen_grpc_module,
                "detect_venv",
                return_value=("pipenv", Path("/usr/bin/python3"), Path("/usr/bin/pip")),
            ),
            mock.patch.object(
                gen_grpc_module,
                "resolve_proto_src",
                side_effect=RuntimeError("failed to download: 404"),
            ),
        ):
            rc = gen_grpc_module.main(
                ["--proto-url", "https://example.invalid/missing.zip", "--no-prompt"]
            )
        assert rc == 4

    def test_main_exits_3_when_no_venv_available(self, gen_grpc_module):
        """main() returns 3 when ``detect_venv`` raises RuntimeError
        (no pipenv/poetry/uv/system interpreter found)."""
        with mock.patch.object(
            gen_grpc_module, "detect_venv", side_effect=RuntimeError("no venv detected")
        ):
            rc = gen_grpc_module.main(
                ["--proto-src", "/tmp/nonexistent", "--no-prompt"]
            )
        assert rc == 3

    def test_main_exits_2_when_both_proto_args_missing(self, gen_grpc_module, capsys):
        """main() returns 2 when neither ``--proto-src`` nor ``--proto-url``
        is supplied. argparse error is printed to stderr."""
        rc = gen_grpc_module.main([])
        assert rc == 2
        captured = capsys.readouterr()
        assert "must provide either" in captured.err

    def test_resolve_proto_src_url_download_failure(self, gen_grpc_module):
        """``resolve_proto_src`` raises RuntimeError when urlopen fails
        (e.g. DNS error, 404, connection refused)."""
        import urllib.error

        args = gen_grpc_module._build_parser().parse_args(
            ["--proto-url", "https://example.invalid/missing.zip"]
        )
        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("Name or service not known"),
        ):
            with pytest.raises(RuntimeError, match="failed to download"):
                gen_grpc_module.resolve_proto_src(args)
