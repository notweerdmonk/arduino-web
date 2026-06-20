"""CLI entry point for medminder_dash.

Run with `python -m medminder_dash`.
"""

import argparse
import logging

from medminder_dash.app import create_app
from medminder_dash.pubsub_infra import init_pubsub, ensure_sketch_dir

logging.basicConfig(level=logging.INFO)


def main():
    """Parse CLI args and run the Flask dev server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--uds", default="/tmp/board_mgr.sock")
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument(
        "--no-uds", action="store_true", default=False, help="Use TCP instead of UDS"
    )
    parser.add_argument(
        "--tcp-host", default="127.0.0.1", help="TCP host for BMS (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--tcp-port", type=int, default=9090, help="TCP port for BMS (default: 9090)"
    )
    args = parser.parse_args()

    ensure_sketch_dir()
    app = create_app()
    try:
        init_pubsub(
            app,
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
