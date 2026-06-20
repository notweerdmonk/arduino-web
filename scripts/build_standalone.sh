#!/usr/bin/env bash
#
# build_standalone.sh — Build all 3 monorepo apps into standalone binaries
# via PyOxidizer, then copy the results to dist-standalone/.
#
# Usage:
#   ./scripts/build_standalone.sh                    # build all 3 apps, .tar.gz
#   ./scripts/build_standalone.sh board-manager      # build a single app
#   ./scripts/build_standalone.sh --zip              # build + .zip archives
#   ./scripts/build_standalone.sh --dry-run          # show what would be done
#   ./scripts/build_standalone.sh --help             # show help
#
# Exit codes:
#   0 — all builds succeeded
#   1 — pyoxidizer not found on PATH
#   2 — a build failed
#   4 — invalid CLI argument
#
# Environment:
#   PYOXIDIZER  — pyoxidizer binary path (default: pyoxidizer from PATH)
#

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# ---------------------------------------------------------------------------
# App configs
# ---------------------------------------------------------------------------
# Each entry:  <app_name>  <config_dir>  <binary_name>
readonly APPS=(
    "board-manager  board-manager  board-manager"
    "arduino-dash   arduino-dash   arduino-dash"
    "medminder-dash medminder-dash medminder-dash"
)

PYOXIDIZER="${PYOXIDIZER:-pyoxidizer}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { printf '[%s] %s\n' "${SCRIPT_NAME}" "$*"; }
die()  { printf '[%s] ERROR: %s\n' "${SCRIPT_NAME}" "$*" >&2; exit "${2:-1}"; }

usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS] [APP ...]

Build standalone binaries via PyOxidizer and package into archives
(.tar.gz by default, .zip with --zip).

Options:
  --dry-run     Print what would be done without building
  --zip         Package as .zip instead of .tar.gz
  --help        Show this help and exit

Arguments:
  APP           One or more app names to build (default: all 3).
                Valid: board-manager, arduino-dash, medminder-dash

Environment:
  PYOXIDIZER    Path to pyoxidizer binary (default: "pyoxidizer" from PATH)
EOF
}

check_prerequisites() {
    if ! command -v "${PYOXIDIZER}" >/dev/null 2>&1; then
        cat >&2 <<EOF
PyOxidizer is required but not found.
Install with:  pipx install pyoxidizer
EOF
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Build one app
# ---------------------------------------------------------------------------

build_app() {
    local app_name="$1"
    local config_dir="$2"
    local binary_name="$3"
    local dry_run="$4"
    local use_zip="$5"

    local config_path="${REPO_ROOT}/scripts/pyoxidizer/${config_dir}"
    local install_dir="${config_path}/build/x86_64-unknown-linux-gnu/release/install"
    local output_dir="${REPO_ROOT}/dist-standalone/${app_name}"

    log "Building ${app_name} from ${config_path}"

    if [[ "${dry_run}" -eq 1 ]]; then
        log "  (dry-run) ${PYOXIDIZER} build --path ${config_path} --release"
        log "  (dry-run) mkdir -p ${output_dir}"
        log "  (dry-run) cp -a ${install_dir}/. ${output_dir}/"
        if [[ "${use_zip}" -eq 1 ]]; then
            log "  (dry-run) (cd ${REPO_ROOT}/dist-standalone && zip -r ${app_name}.zip ${app_name}/)"
        else
            log "  (dry-run) (cd ${REPO_ROOT}/dist-standalone && tar czf ${app_name}.tar.gz ${app_name}/)"
        fi
        return 0
    fi

    # PyOxidizer build
    if ! "${PYOXIDIZER}" build --path "${config_path}" --release 2>&1 | while IFS= read -r line; do
        printf '  [pyoxidizer] %s\n' "${line}"
    done; then
        die "build failed for ${app_name}" 2
    fi

    # Verify binary exists
    local binary_path="${install_dir}/${binary_name}"
    if [[ ! -f "${binary_path}" ]]; then
        die "binary not found after build: ${binary_path}" 2
    fi

    # Copy to dist-standalone/
    mkdir -p "${output_dir}"
    cp -a "${install_dir}/." "${output_dir}/"
    log "  Copied to ${output_dir}"

    # Quick smoke test
    if [[ -x "${output_dir}/${binary_name}" ]]; then
        local help_out
        help_out="$("${output_dir}/${binary_name}" --help 2>&1 || true)"
        if echo "${help_out}" | grep -qi "usage\|help\|options"; then
            log "  Smoke test: ${binary_name} --help OK"
        else
            log "  WARNING: ${binary_name} --help did not produce expected output"
        fi
    fi

    # Package into archive
    local archive_name="${app_name}.$([[ "${use_zip}" -eq 1 ]] && echo zip || echo tar.gz)"
    log "  Packaging ${archive_name} ..."
    if [[ "${use_zip}" -eq 1 ]]; then
        (cd "${REPO_ROOT}/dist-standalone" && rm -f "${archive_name}" && zip -r "${archive_name}" "${app_name}/")
    else
        (cd "${REPO_ROOT}/dist-standalone" && rm -f "${archive_name}" && tar czf "${archive_name}" "${app_name}/")
    fi
    log "  Created ${REPO_ROOT}/dist-standalone/${archive_name}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    local dry_run=0
    local use_zip=0
    local requested_apps=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                dry_run=1
                shift
                ;;
            --zip)
                use_zip=1
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            -*)
                echo "error: unknown option: $1" >&2
                usage >&2
                exit 4
                ;;
            *)
                requested_apps+=("$1")
                shift
                ;;
        esac
    done

    if [[ "${dry_run}" -eq 0 ]]; then
        check_prerequisites
    fi

    # Determine which apps to build
    local build_list=()
    if [[ ${#requested_apps[@]} -gt 0 ]]; then
        for req in "${requested_apps[@]}"; do
            local found=0
            while IFS=' ' read -r app_name config_dir binary_name; do
                [[ -z "${app_name}" ]] && continue
                if [[ "${req}" == "${app_name}" ]]; then
                    build_list+=("${app_name}|${config_dir}|${binary_name}")
                    found=1
                    break
                fi
            done < <(printf '%s\n' "${APPS[@]}")
            if [[ "${found}" -eq 0 ]]; then
                die "unknown app: ${req}"$'\n'"Valid: board-manager, arduino-dash, medminder-dash" 4
            fi
        done
    else
        while IFS=' ' read -r app_name config_dir binary_name; do
            [[ -z "${app_name}" ]] && continue
            build_list+=("${app_name}|${config_dir}|${binary_name}")
        done < <(printf '%s\n' "${APPS[@]}")
    fi

    local pack_fmt="$([[ "${use_zip}" -eq 1 ]] && echo zip || echo tar.gz)"
    echo "==> build_standalone.sh"
    echo "    Apps to build: ${#build_list[@]}"
    echo "    Dry run       = $([ "${dry_run}" -eq 1 ] && echo yes || echo no)"
    echo "    Package fmt   = ${pack_fmt}"
    echo

    local failed=0
    for entry in "${build_list[@]}"; do
        IFS='|' read -r app_name config_dir binary_name <<< "${entry}"
        echo "----------------------------------------"
        build_app "${app_name}" "${config_dir}" "${binary_name}" "${dry_run}" "${use_zip}"
        echo "----------------------------------------"
    done

    echo
    if [[ "${dry_run}" -eq 1 ]]; then
        log "Dry-run complete (no changes made)"
    elif [[ "${failed}" -eq 0 ]]; then
        log "All builds completed successfully"
    fi

    exit "${failed}"
}

main "$@"
