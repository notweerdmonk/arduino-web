"""medminder_dash/python/medminder_dash/medminder_dash/board_management.py

Board management routes — kept as no-op for import compatibility.

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

import logging

logger = logging.getLogger(__name__)


def init_board_routes(
    app, sock, store, migrate_default_board, load_sketch_dir, get_alarm_hpp_path=None
):
    """Routes moved to html_routes.py — kept as no-op for import compatibility."""
    pass
