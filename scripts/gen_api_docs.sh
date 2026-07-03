#!/usr/bin/env bash
# @file gen_api_docs.sh
# @brief Generate API reference docs for the Arduino Web monorepo.
# @description Generate pdoc HTML for all Python sources and shdoc
# Markdown for all shell scripts. Output goes to each module's
# docs/reference/ directory.
# @option --help  Show usage and exit.
# @exitcode 0 All docs generated successfully.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_NAME="$(basename "$0")"
SHOW_HELP=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) SHOW_HELP=1; shift ;;
        *) echo "error: unknown argument: $1" >&2; exit 4 ;;
    esac
done

usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS]

Generate API reference docs for all modules and scripts.

pdoc HTML is generated for all Python sources:
  - 6 monorepo packages
  - 2 standalone scripts (gen_grpc_bindings, add_license_headers)
  - noxfile.py
  - e2e/ test servers

shdoc Markdown is generated for all shell scripts under scripts/.

typedoc HTML is generated for e2e TypeScript sources (fixtures, config).

A Python extraction script generates a spec reference Markdown file
from Playwright .spec.ts files.

Output: docs/reference/ under each module's own docs/ directory.
EOF
}

if [[ ${SHOW_HELP} -eq 1 ]]; then
    usage
    exit 0
fi

cd "${REPO_ROOT}"

echo "==> ${SCRIPT_NAME}: generating API reference docs"
echo

# ---------------------------------------------------------------------------
# pdoc — Python sources
# ---------------------------------------------------------------------------
echo "--- pdoc: Python packages ---"

pdoc_gen() {
    local label="$1"
    local output="$2"
    local source="$3"
    shift 3
    echo "  [pdoc] ${label}"
    mkdir -p "${output}"
    pipenv run pdoc --docformat google -o "${output}" "${source}" "$@"
}

# 6 monorepo packages
pdoc_gen "arduino_dash" \
    "arduino_dash/python/arduino_dash/docs/reference" \
    "./arduino_dash/python/arduino_dash/arduino_dash/"

pdoc_gen "board_manager" \
    "board_manager/python/board_manager/docs/reference" \
    "./board_manager/python/board_manager/board_manager/"

pdoc_gen "board_manager_client" \
    "board_manager_client/python/board_manager_client/docs/reference" \
    "./board_manager_client/python/board_manager_client/board_manager_client/"

pdoc_gen "arduino_grpc" \
    "grpc_client/python/arduino_grpc/docs/reference" \
    "./grpc_client/python/arduino_grpc/arduino_grpc/"

pdoc_gen "arduino_sketch_tools" \
    "arduino_sketch_tools/python/arduino_sketch_tools/docs/reference" \
    "./arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/"

pdoc_gen "medminder_dash" \
    "medminder_dash/python/medminder_dash/docs/reference" \
    "./medminder_dash/python/medminder_dash/medminder_dash/"

# Standalone scripts
pdoc_gen "gen_grpc_bindings" \
    "scripts/docs/reference/gen_grpc_bindings" \
    "./scripts/gen_grpc_bindings.py"

pdoc_gen "add_license_headers" \
    "scripts/docs/reference/add_license_headers" \
    "./scripts/add_license_headers.py"

# e2e test servers
pdoc_gen "e2e" \
    "e2e/docs/reference" \
    "./e2e/"

# noxfile.py (needs PDOC_ALLOW_EXEC for nox's uv detection)
echo "  [pdoc] noxfile.py"
mkdir -p docs/reference/noxfile
PDOC_ALLOW_EXEC=1 pipenv run pdoc --docformat google \
    -o docs/reference/noxfile ./noxfile.py

echo
echo "--- pdoc: done ---"
echo

# ---------------------------------------------------------------------------
# shdoc — shell scripts
# ---------------------------------------------------------------------------
echo "--- shdoc: shell scripts ---"

shdoc_gen() {
    local label="$1"
    local script="$2"
    local output="$3"
    echo "  [shdoc] ${label}"
    mkdir -p "$(dirname "${output}")"
    ./scripts/shdoc "${script}" > "${output}"
}

shdoc_gen "ci.sh" \
    "scripts/ci.sh" \
    "scripts/docs/reference/ci.md"

shdoc_gen "build_standalone.sh" \
    "scripts/build_standalone.sh" \
    "scripts/docs/reference/build_standalone.md"

shdoc_gen "check_venv.bash" \
    "scripts/check_venv.bash" \
    "scripts/docs/reference/check_venv.md"

shdoc_gen "install_arduino_deps.sh" \
    "scripts/install_arduino_deps.sh" \
    "scripts/docs/reference/install_arduino_deps.md"

shdoc_gen "test_installs.sh" \
    "scripts/test_installs.sh" \
    "scripts/docs/reference/test_installs.md"

shdoc_gen "test_ci.sh" \
    "scripts/tests/test_ci.sh" \
    "scripts/tests/docs/reference/test_ci.md"

shdoc_gen "test_install_arduino_deps.sh" \
    "scripts/tests/test_install_arduino_deps.sh" \
    "scripts/tests/docs/reference/test_install_arduino_deps.md"

echo
echo "--- shdoc: done ---"
echo

# ---------------------------------------------------------------------------
# typedoc — TypeScript sources (e2e fixtures + config)
# ---------------------------------------------------------------------------
echo "--- typedoc: e2e TypeScript sources ---"

echo "  [typedoc] e2e fixtures + config"
mkdir -p e2e/docs/reference/typedoc
# --skipErrorChecking needed because @playwright/test and @types/node
# aren't installed at the project root level (only in e2e/).
npx --yes typedoc --skipErrorChecking \
    --name "Arduino Web E2E" \
    --out e2e/docs/reference/typedoc \
    --entryPointStrategy expand \
    --entryPoints e2e/fixtures/test-data.ts \
    --entryPoints e2e/playwright.config.ts \
    > /dev/null 2>&1

echo "  [typedoc] done"

echo
echo "--- typedoc: done ---"
echo

# ---------------------------------------------------------------------------
# e2e spec reference (Python extraction)
# ---------------------------------------------------------------------------
echo "--- e2e spec reference: Playwright .spec.ts files ---"

python3 scripts/gen_e2e_spec_docs.py

echo
echo "--- e2e spec reference: done ---"
echo

# ---------------------------------------------------------------------------
# Cleanup — remove stale typedoc output from ./docs/ (default output dir)
# ---------------------------------------------------------------------------
if [[ -d docs/assets ]] && [[ -f docs/modules.html ]]; then
    rm -rf docs/assets docs/functions docs/hierarchy.html docs/index.html \
           docs/media docs/modules docs/modules.html docs/variables \
           2>/dev/null || true
    echo "  [cleanup] removed stale typedoc output from ./docs/"
fi

echo "==> ${SCRIPT_NAME}: all API docs generated successfully"
