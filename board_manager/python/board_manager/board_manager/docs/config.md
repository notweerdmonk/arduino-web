---
---
# Config Module

## Purpose

Provides the `Config` dataclass and a 3-tier configuration loader that merges settings from a TOML file, environment variables, and CLI arguments (each tier overriding the previous).

## Location

`board_manager/config.py`

---

## Dataclass: `Config`

```python
@dataclass
class Config
```

All fields use defaults from `BmsDefaults` (see `boot` module):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tcp_host` | `str` | `"127.0.0.1"` | TCP bind host |
| `tcp_port` | `int` | `9090` | TCP bind port |
| `uds_path` | `str` | `"/tmp/board_mgr.sock"` | UDS socket path |
| `arduino_daemon` | `str` | `"localhost:50051"` | Arduino CLI daemon gRPC address |
| `daemon_binary` | `str` | `"arduino-cli"` | Arduino CLI binary path/name |
| `log_level` | `str` | `"INFO"` | Logging level |
| `config_file` | `str` | `""` | Path to TOML config file |
| `board_detection_mode` | `str` | `"watch"` | Board detection mode (`"watch"` or `"poll"`) |

---

## Function: `load_config(args: Optional[dict] = None) -> Config`

Loads and merges configuration from three sources with increasing priority.

### Priority Order (later overrides earlier)

1. **TOML file** (lowest priority)
2. **Environment variables**
3. **CLI arguments** (highest priority)

### TOML File

Determined by:
1. `args.get("config_file")` (from `--config` / `-c`)
2. `os.environ.get("BOARD_MGR_CONFIG")`
3. Empty string (no file)

If a config file path is set and exists, it is loaded as TOML using `tomllib` (Python 3.11+) with a fallback to `tomli`.

Expected TOML structure:

```toml
[service]
tcp_host = "0.0.0.0"
tcp_port = 9090
uds_path = "/tmp/board_mgr.sock"
arduino_daemon = "localhost:50051"
daemon_binary = "/usr/local/bin/arduino-cli"
log_level = "DEBUG"
board_detection_mode = "watch"
```

### Environment Variables

| Env Var | Overrides Field |
|---------|----------------|
| `BOARD_MGR_TCP_HOST` | `tcp_host` |
| `BOARD_MGR_TCP_PORT` | `tcp_port` |
| `BOARD_MGR_UDS_PATH` | `uds_path` |
| `BOARD_MGR_ARDUINO_DAEMON` | `arduino_daemon` |
| `BOARD_MGR_DAEMON_BINARY` | `daemon_binary` |
| `BOARD_MGR_LOG_LEVEL` | `log_level` |
| `BOARD_MGR_DETECTION_MODE` | `board_detection_mode` |

### CLI Arguments

The `args` dict (from `argparse.parse_args()`) can override any field. Only truthy values are applied — empty strings or `None` are ignored.

### Usage Example

```python
from board_manager.config import load_config

# No args → defaults only
config = load_config()
print(config.tcp_host)  # "127.0.0.1"

# With CLI args
config = load_config({"tcp_port": 8080, "log_level": "DEBUG"})

# Precedence: CLI overrides env var overrides TOML
```

### Edge Cases

- If the TOML file is specified but does not exist, it is silently ignored (no error)
- If `tomllib` is not available (Python < 3.11), falls back to the `tomli` third-party package
- CLI values of empty string or `None` are skipped (allows partial override)
- `board_detection_mode` defaults to `"watch"` — no validation is performed on the value
