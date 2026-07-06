"""medminder_dash/python/medminder_dash/medminder_dash/wsgi.py

WSGI entry point for medminder_dash.

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

import os

from medminder_dash.app import create_app

app = create_app()
app.config.update(
    BMS_UDS_PATH=os.environ.get("BOARD_MGR_UDS_PATH", "/tmp/board_mgr.sock"),
    BMS_TCP_HOST=os.environ.get("BOARD_MGR_TCP_HOST", "127.0.0.1"),
    BMS_TCP_PORT=int(os.environ.get("BOARD_MGR_TCP_PORT", "9090")),
    BMS_NO_UDS=os.environ.get("BMS_NO_UDS", "").lower() in ("1", "true"),
)
