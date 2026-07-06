"""board_manager/python/board_manager/board_manager/__main__.py

Entry point: python -m board_manager [options]

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

import argparse
import logging
import signal
import sys


def main():
    """Parse CLI args, load config, and run the service."""
    parser = argparse.ArgumentParser(description="Board Manager Service")
    parser.add_argument("--tcp-host", help="TCP bind host (default: 127.0.0.1)")
    parser.add_argument("--tcp-port", type=int, help="TCP bind port (default: 9090)")
    parser.add_argument("--uds-path", help="Unix domain socket path (default: /tmp/board_mgr.sock)")
    parser.add_argument(
        "--arduino-daemon", help="Arduino CLI daemon address (default: localhost:50051)"
    )
    parser.add_argument("--daemon-binary", help="Arduino CLI binary path (default: arduino-cli)")
    parser.add_argument("--log-level", help="Log level (default: INFO)")
    parser.add_argument(
        "--board-detection-mode",
        choices=["watch", "udev"],
        help="Board detection mode (default: watch)",
    )
    parser.add_argument("-c", "--config", dest="config_file", help="Config file path")
    args = vars(parser.parse_args())

    args = {k: v for k, v in args.items() if v is not None}

    from board_manager.config import load_config

    config = load_config(args)

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from board_manager.service import BoardManagerService

    service = BoardManagerService(config)
    try:
        service.start()
    except KeyboardInterrupt:
        pass
    finally:
        service.stop()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))
    main()
