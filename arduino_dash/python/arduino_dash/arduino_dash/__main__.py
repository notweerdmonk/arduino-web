"""arduino_dash/python/arduino_dash/arduino_dash/__main__.py

Entry point: python -m arduino_dash [options]

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


def main():
    """Parse CLI arguments and run the Flask app."""
    parser = argparse.ArgumentParser(description="Arduino Dash")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Bind port (default: 8080)"
    )
    parser.add_argument(
        "--uds", default="/tmp/board_mgr.sock", help="BoardManager UDS path"
    )
    parser.add_argument("--tcp-host", default="127.0.0.1", help="BoardManager TCP host")
    parser.add_argument(
        "--tcp-port", type=int, default=9090, help="BoardManager TCP port"
    )
    parser.add_argument("--no-uds", action="store_true", help="Force TCP (no UDS)")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from arduino_dash.app import create_app, init_pubsub

    app = create_app()
    try:
        init_pubsub(
            use_uds=not args.no_uds,
            tcp_host=args.tcp_host,
            tcp_port=args.tcp_port,
            uds_path=args.uds,
        )
    except (ConnectionError, OSError):
        logging.warning("BoardManagerService not available; compile/upload disabled")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()

