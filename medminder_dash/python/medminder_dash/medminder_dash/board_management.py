"""Board management routes — kept as no-op for import compatibility."""

import logging

logger = logging.getLogger(__name__)


def init_board_routes(
    app, sock, store, migrate_default_board, load_sketch_dir, get_alarm_hpp_path=None
):
    """Routes moved to html_routes.py — kept as no-op for import compatibility."""
    pass
