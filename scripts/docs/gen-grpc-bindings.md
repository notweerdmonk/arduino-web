---
layout: default
---
# gRPC Stub Generator — `gen_grpc_bindings.py`

Regenerate Python gRPC stubs for the arduino-cli service. Walks `.proto` files and emits `*_pb2.py`, `*_pb2_grpc.py`, `*_pb2.pyi` stubs into `grpc_client/python/arduino_grpc/cc/arduino/cli/commands/v1/`.

## Proto Source Options

1. **Local checkout:**
```bash
pipenv run python scripts/gen_grpc_bindings.py \
    --proto-src /path/to/arduino-cli/rpc \
    --no-prompt
```

2. **GitHub release zip:**
```bash
pipenv run python scripts/gen_grpc_bindings.py \
    --proto-url https://github.com/arduino/arduino-cli/releases/download/0.35.0/arduino-cli_0.35.0_Linux_64bit.zip
```

## Venv Auto-Detection

Detects pipenv/poetry/uv/system venv that owns `arduino_grpc`. Installs `grpcio-tools` + `googleapis-common-protos` on demand.

## Useful Flags

| Flag | Purpose |
|------|---------|
| `--venv {auto,pipenv,poetry,uv,system}` | Override venv detection (default auto) |
| `--install-deps` | Force install dependencies without prompting |
| `--no-prompt` | CI mode — no interactive prompts |
| `--keep-temp` | Keep downloaded zip for inspection |

## Tests

42 tests in `scripts/tests/test_gen_grpc_bindings.py` covering CLI args, proto source handling, venv detection, and error paths. Run via:

```bash
cd scripts && pipenv run pytest tests/test_gen_grpc_bindings.py -v
```
