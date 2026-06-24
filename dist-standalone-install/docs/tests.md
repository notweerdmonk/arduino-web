---
---

# Standalone Binary Testing

## Current Test Coverage

Standalone binary testing is currently limited. The primary verification is a `--help` smoke test that runs as part of the build process.

### Build-time Smoke Test

Each binary is tested immediately after build in `build_standalone.sh`:

```bash
help_out="$("${binary}" --help 2>&1 || true)"
if echo "${help_out}" | grep -qi "usage\|help\|options"; then
    echo "Smoke test: ${binary} --help OK"
fi
```

This verifies:
- The binary executes without crash (no missing dependencies)
- The argument parser is functional

### Bundle Integrity Verification (Manual)

After building, you can verify the bundle contents manually:

```bash
# List bundled Python modules for a dashboard
ls dist-standalone/arduino-dash/prefix/arduino_dash/

# Check templates
ls dist-standalone/arduino-dash/prefix/arduino_dash/templates/

# Check static files
ls dist-standalone/arduino-dash/prefix/arduino_dash/static/

# Check simple-websocket dependency
ls dist-standalone/arduino-dash/prefix/simple_websocket/
```

Expected modules in dashboard bundles:
- `html_routes.py`, `api_routes.py`, `pubsub.py`, `settings.py`, `state.py`, `utils.py`, `sketch_registry.py`

Expected templates (both dashboards):
- `base.html`, `admin.html`, `board_detail.html`
- All partials under `partials/`

### Build Script Verification

The build pipeline (`scripts/ci.sh`) runs `nox -s all_tests` and `nox -s all_builds` but does **not** run standalone binary tests. Standalone builds are a separate manual step (`./scripts/build_standalone.sh` or `nox -s build_standalone`).

## Testing Gaps

| Gap | Description | Priority |
|-----|-------------|----------|
| **HTTP serving** | No automated test starts a standalone binary and verifies it serves HTTP | High |
| **E2E browser tests** | All 10 Playwright MCP recipes target Flask dev servers, not standalone binaries | High |
| **Mock data injection** | Standalone binaries lack a `--mock` flag for test data | Medium |
| **Server lifecycle** | No `--pidfile`, `--stop`, `--logfile` flags in standalone binaries | Medium |
| **Daemonization** | The `fork() + setsid()` pattern exists for dev servers but not standalone | Low |
| **CI integration** | `scripts/ci.sh` does not include standalone build or test steps | Low |
| **Cross-platform** | Only `x86_64-unknown-linux-gnu` builds are produced | Low |

## Related

- [scripts/docs/tests.md](../../scripts/docs/tests.md) — Scripts test suite
- [docs/tests.md](../../docs/tests.md) — Project-wide testing methodology
- [e2e/docs/scenarios.md](../../e2e/docs/scenarios.md) — E2E MCP test scenarios
