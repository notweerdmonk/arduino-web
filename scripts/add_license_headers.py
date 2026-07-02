#!/usr/bin/env python3
"""scripts/add_license_headers.py

add_license_headers module.

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

import ast
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PACKAGE_ROOTS = [
    "board_manager/python/board_manager",
    "board_manager_client/python/board_manager_client",
    "grpc_client/python/arduino_grpc",
    "arduino_sketch_tools/python/arduino_sketch_tools",
    "arduino_dash/python/arduino_dash",
    "medminder_dash/python/medminder_dash",
]

EXTRA_ROOTS = [
    "scripts",
]

EXCLUDE_SUFFIXES = {"__pycache__", ".nox", "node_modules", "_site",
                    ".opencode", ".playwright-mcp", ".ruff_cache",
                    "build", "dist", ".git", ".egg-info"}

LICENSE_BLOCK = """Copyright 2026 notweerdmonk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

# -- Custom descriptions (override auto-generated) -------------------------
# Key = relative path from repo root, Value = description string
DESCRIPTIONS: dict[str, str] = {
    # board_manager
    "board_manager/python/board_manager/tests/__init__.py":
        "Test suite for board_manager.",
    "board_manager/python/board_manager/tests/conftest.py":
        "Pytest fixtures and configuration for board_manager tests.",
    "board_manager/python/board_manager/tests/test_board_detector.py":
        "Tests for board_detector module.",
    "board_manager/python/board_manager/tests/test_board_worker.py":
        "Tests for board_worker module.",
    "board_manager/python/board_manager/tests/test_boot.py":
        "Tests for boot module.",
    "board_manager/python/board_manager/tests/test_config.py":
        "Tests for config module.",
    "board_manager/python/board_manager/tests/test_daemon_manager.py":
        "Tests for daemon_manager module.",
    "board_manager/python/board_manager/tests/test_integration.py":
        "Integration tests for board_manager.",
    "board_manager/python/board_manager/tests/test_pool.py":
        "Tests for pool module.",
    "board_manager/python/board_manager/tests/test_protocol.py":
        "Tests for protocol module.",
    "board_manager/python/board_manager/tests/test_router.py":
        "Tests for router module.",
    "board_manager/python/board_manager/tests/test_service.py":
        "Tests for service module.",
    "board_manager/python/board_manager/tests/test_udev_monitor.py":
        "Tests for udev_monitor module.",

    # board_manager_client
    "board_manager_client/python/board_manager_client/board_manager_client/__init__.py":
        "board_manager_client package.",
    "board_manager_client/python/board_manager_client/tests/__init__.py":
        "Test suite for board_manager_client.",
    "board_manager_client/python/board_manager_client/tests/test_pubsub_client.py":
        "Tests for pubsub_client module.",

    # arduino_grpc (non-generated)
    "grpc_client/python/arduino_grpc/cc/__init__.py":
        "Namespace package for cc.",
    "grpc_client/python/arduino_grpc/cc/arduino/__init__.py":
        "Namespace package for cc.arduino.",
    "grpc_client/python/arduino_grpc/cc/arduino/cli/__init__.py":
        "Namespace package for cc.arduino.cli.",
    "grpc_client/python/arduino_grpc/cc/arduino/cli/commands/__init__.py":
        "Namespace package for cc.arduino.cli.commands.",
    "grpc_client/python/arduino_grpc/cc/arduino/cli/commands/v1/__init__.py":
        "Namespace package for cc.arduino.cli.commands.v1.",
    "grpc_client/python/arduino_grpc/tests/__init__.py":
        "Test suite for arduino_grpc.",
    "grpc_client/python/arduino_grpc/tests/conftest.py":
        "Pytest fixtures and configuration for arduino_grpc tests.",
    "grpc_client/python/arduino_grpc/tests/test_client.py":
        "Tests for client module.",
    "grpc_client/python/arduino_grpc/tests/test_integration.py":
        "Integration tests for arduino_grpc.",

    # arduino_sketch_tools
    "arduino_sketch_tools/python/arduino_sketch_tools/tests/__init__.py":
        "Test suite for arduino_sketch_tools.",
    "arduino_sketch_tools/python/arduino_sketch_tools/tests/test_extension.py":
        "Tests for extension module.",

    # arduino_dash
    "arduino_dash/python/arduino_dash/tests/__init__.py":
        "Test suite for arduino_dash.",
    "arduino_dash/python/arduino_dash/tests/test_app.py":
        "Tests for app module.",
    "arduino_dash/python/arduino_dash/tests/test_gunicorn_conf.py":
        "Tests for gunicorn_conf module.",

    # medminder_dash
    "medminder_dash/python/medminder_dash/tests/__init__.py":
        "Test suite for medminder_dash.",
    "medminder_dash/python/medminder_dash/tests/test_admin.py":
        "Tests for admin routes and templates.",
    "medminder_dash/python/medminder_dash/tests/test_api_medicines.py":
        "Tests for medicine API routes.",
    "medminder_dash/python/medminder_dash/tests/test_board_isolation.py":
        "Tests for board-level data isolation.",
    "medminder_dash/python/medminder_dash/tests/test_bootstrap.py":
        "Tests for app bootstrap and initialization.",
    "medminder_dash/python/medminder_dash/tests/test_deploy.py":
        "Tests for sketch deploy workflow.",
    "medminder_dash/python/medminder_dash/tests/test_e2e_sketch.py":
        "End-to-end tests for sketch generation.",
    "medminder_dash/python/medminder_dash/tests/test_gunicorn_conf.py":
        "Tests for gunicorn_conf module.",
    "medminder_dash/python/medminder_dash/tests/test_pubsub.py":
        "Tests for pubsub module.",
    "medminder_dash/python/medminder_dash/tests/test_routes.py":
        "Tests for HTML and API routes.",
    "medminder_dash/python/medminder_dash/tests/test_sketch_gen.py":
        "Tests for sketch_gen module.",
    "medminder_dash/python/medminder_dash/tests/test_sketch_registry.py":
        "Tests for sketch_registry module.",

    # scripts
    "scripts/tests/conftest.py":
        "Pytest fixtures and configuration for scripts tests.",
    "scripts/tests/test_gen_grpc_bindings.py":
        "Tests for gen_grpc_bindings script.",
    "scripts/tests/test_setup_py.py":
        "Tests for setup.py helper utilities.",
    "scripts/tests/test_ci.sh":
        "Tests for the ci.sh script.",
    "scripts/tests/test_install_arduino_deps.sh":
        "Tests for the install_arduino_deps.sh script.",
    "scripts/ci.sh":
        "Full CI pipeline — tests + builds in one command.",
    "scripts/build_standalone.sh":
        "Build standalone binaries via PyOxidizer.",
    "scripts/install_arduino_deps.sh":
        "Install Arduino libraries required by sketches.",
    "scripts/test_installs.sh":
        "Install wheels into clean venv + smoke test.",
    "scripts/check_venv.bash":
        "Recursively verify pipenv venvs in the project tree.",
    "scripts/gen_grpc_bindings.py":
        "Regenerate Python gRPC stubs from proto files.",

    # noxfile
    "noxfile.py":
        "Nox session definitions for the Arduino Web monorepo.",

    # Key HTML templates
    "arduino_dash/python/arduino_dash/arduino_dash/templates/base.html":
        "Base layout template with nav, WS event feed, and daemon status badge.",
    "arduino_dash/python/arduino_dash/arduino_dash/templates/dashboard.html":
        "Dashboard page with board grid and connection status.",
    "arduino_dash/python/arduino_dash/arduino_dash/templates/board_detail.html":
        "Board detail page with compile/upload controls and live events.",
    "arduino_dash/python/arduino_dash/arduino_dash/templates/admin.html":
        "Admin page with board and sketch management.",
    "medminder_dash/python/medminder_dash/medminder_dash/templates/base.html":
        "Base layout template with nav, WS event feed, and daemon status badge.",
    "medminder_dash/python/medminder_dash/medminder_dash/templates/index.html":
        "Dashboard page with board grid, medicine cards, and quick actions.",
    "medminder_dash/python/medminder_dash/medminder_dash/templates/board_detail.html":
        "Board detail page with medicine management and compile/upload.",
    "medminder_dash/python/medminder_dash/medminder_dash/templates/admin.html":
        "Admin page for board and medicine management.",
    "medminder_dash/python/medminder_dash/medminder_dash/templates/medicines.html":
        "Medicine list and management page.",
    "medminder_dash/python/medminder_dash/medminder_dash/templates/medicine_form.html":
        "Medicine add/edit form page.",
}

# -- File discovery -----------------------------------------------------

def is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_SUFFIXES:
            return True
    return False


def discover_files() -> list[Path]:
    files: list[Path] = []
    roots = [REPO_ROOT / r for r in PACKAGE_ROOTS]
    for r in EXTRA_ROOTS:
        p = REPO_ROOT / r
        if p.is_dir():
            roots.append(p)
    extra_files = [REPO_ROOT / "noxfile.py"]

    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if is_excluded(path):
                continue
            if not path.is_file():
                continue
            if path.suffix in (".py", ".sh", ".bash", ".html", ".css"):
                # Skip gRPC generated files
                if "_pb2" in path.name:
                    continue
                files.append(path)

    for f in extra_files:
        if f.exists():
            files.append(f)

    # Deduplicate and sort
    files = sorted(set(files))
    return files


def relative_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


# -- Description resolution ----------------------------------------------

def has_header_already(path: Path) -> bool:
    """Check if file already has a license header."""
    try:
        content = path.read_text(encoding="utf-8")
        return "SPDX-License-Identifier: Apache-2.0" in content
    except Exception:
        return False


def _git_original_docstring(rel: str) -> str | None:
    """Extract original module docstring from git HEAD."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            content = result.stdout
            try:
                tree = ast.parse(content)
                doc = ast.get_docstring(tree)
                return doc
            except (SyntaxError, Exception):
                pass
    except Exception:
        pass
    return None


def describe(path: Path) -> str:
    rel = relative_path(path)
    if rel in DESCRIPTIONS:
        return DESCRIPTIONS[rel]

    # Extract original docstring from git HEAD (only for clean, un-patched files)
    if path.suffix == ".py" and not has_header_already(path):
        doc = _git_original_docstring(rel)
        if doc:
            return doc.strip().split("\n")[0]

    # Auto-generate from path
    stem = path.stem
    if path.suffix in (".sh", ".bash"):
        return f"{stem} - shell script for the Arduino Web monorepo."
    if path.suffix == ".html":
        name = stem.replace("_", " ").replace("-", " ").title()
        return f"{name} template."
    if path.suffix == ".css":
        return "Stylesheet for the Arduino Web dashboard."
    return f"{stem} module."


# -- Header generation --------------------------------------------------

def py_header(rel: str, desc: str) -> str:
    return (f'"""{rel}\n'
            f'\n'
            f'{desc}\n'
            f'\n'
            f'Author: notweerdmonk\n'
            f'SPDX-License-Identifier: Apache-2.0\n'
            f'\n'
            f'{LICENSE_BLOCK}\n'
            f'"""')


def sh_header(rel: str, desc: str) -> str:
    lines = [f"# {rel}", "#", f"# {desc}", "#",
             "# Author: notweerdmonk",
             "# SPDX-License-Identifier: Apache-2.0", "#"]
    for li in LICENSE_BLOCK.split("\n"):
        if li.strip():
            lines.append(f"# {li}")
        else:
            lines.append("#")
    return "\n".join(lines)


def html_header(rel: str, desc: str) -> str:
    lines = [f"<!--", f"    {rel}", "", f"    {desc}", "",
             "    Author: notweerdmonk",
             "    SPDX-License-Identifier: Apache-2.0", ""]
    for li in LICENSE_BLOCK.split("\n"):
        if li.strip():
            lines.append(f"    {li}")
        else:
            lines.append("")
    lines.append("-->")
    return "\n".join(lines)


def css_header(rel: str, desc: str) -> str:
    lines = [f"/*", f" * {rel}", " *", f" * {desc}", " *",
             " * Author: notweerdmonk",
             " * SPDX-License-Identifier: Apache-2.0", " *"]
    for li in LICENSE_BLOCK.split("\n"):
        if li.strip():
            lines.append(f" * {li}")
        else:
            lines.append(" *")
    lines.append(" */")
    return "\n".join(lines)


# -- File patching ------------------------------------------------------

def strip_shebang(content: str) -> tuple[str, str]:
    """Separate shebang line from content."""
    if content.startswith("#!/"):
        idx = content.index("\n")
        return content[:idx], content[idx + 1:]
    return "", content


def patch_file(path: Path) -> bool:
    rel = relative_path(path)
    desc = describe(path)
    content = path.read_text(encoding="utf-8")
    orig = content

    if path.suffix == ".py":
        shebang, rest = strip_shebang(content)
        # Strip existing docstring if present
        try:
            tree = ast.parse(rest)
            doc = ast.get_docstring(tree)
            if doc:
                # Remove the existing docstring
                # Find it by looking for the first triple-quoted string
                # Simple heuristic: remove leading docstring if it matches
                rest = _strip_existing_docstring(rest, doc)
        except SyntaxError:
            pass
        header = py_header(rel, desc)
        if shebang:
            content = f"{shebang}\n{header}\n\n{rest.lstrip()}\n"
        else:
            content = f"{header}\n\n{rest.lstrip()}\n"

    elif path.suffix in (".sh", ".bash"):
        shebang, rest = strip_shebang(content)
        # Strip existing comment header if first line is a comment
        rest = _strip_shell_header(rest)
        header = sh_header(rel, desc)
        if shebang:
            content = f"{shebang}\n{header}\n\n{rest.lstrip()}\n"
        else:
            content = f"{header}\n\n{rest.lstrip()}\n"

    elif path.suffix == ".html":
        # For Jinja2 templates, strip any leading {% raw %} or existing header
        # Prepend header after leading {% raw %} if present
        rest = content
        trailer = ""
        if rest.lstrip().startswith("{%"):
            # Find the end of the first Jinja2 block
            m = re.match(r'(\s*\{%[^%]*%\}\s*)', rest)
            if m:
                trailer = m.group(1)
                rest = rest[m.end():]
        # Strip existing HTML comment header at top
        rest = re.sub(r'^\s*<!--.*?-->\s*', '', rest, count=1, flags=re.DOTALL)
        header = html_header(rel, desc)
        content = f"{trailer}{header}\n\n{rest.lstrip()}\n"

    elif path.suffix == ".css":
        # Strip existing CSS comment header at top
        rest = re.sub(r'^\s*/\*.*?\*/\s*', '', content, count=1, flags=re.DOTALL)
        header = css_header(rel, desc)
        content = f"{header}\n\n{rest.lstrip()}\n"

    else:
        return False

    if content != orig:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def _strip_existing_docstring(content: str, doc: str) -> str:
    """Remove the first docstring occurrence from Python source."""
    # Try triple-double-quotes
    escaped = re.escape(doc)
    # Match """doc""" or '''doc''' with possible whitespace
    pattern = r'(^|\s)"""\s*' + escaped.replace(r'\/\/', r'//') + r'\s*"""'
    # Simpler approach: just find and remove the first triple-quoted string
    for q in ('"""', "'''"):
        idx = content.find(q)
        if idx != -1:
            end = content.find(q, idx + 3)
            if end != -1:
                return content[:idx] + content[end + 3:]
    return content


def _strip_shell_header(content: str) -> str:
    """Remove leading #-comment block from shell scripts."""
    lines = content.split("\n")
    idx = 0
    while idx < len(lines) and lines[idx].startswith("#"):
        idx += 1
    return "\n".join(lines[idx:])


# -- Main ----------------------------------------------------------------

def main():
    files = discover_files()
    changed = []
    skipped = []
    print(f"Found {len(files)} files to process.")

    for f in files:
        try:
            if patch_file(f):
                changed.append(f)
                print(f"  + {relative_path(f)}")
            else:
                skipped.append(f)
        except Exception as e:
            print(f"  ! {relative_path(f)}: {e}", file=sys.stderr)

    print(f"\nPatched: {len(changed)} files")
    print(f"Skipped (no change): {len(skipped)} files")

    if changed:
        print(f"\nFiles modified: {len(changed)}")


if __name__ == "__main__":
    main()






