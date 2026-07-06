"""arduino_dash/python/arduino_dash/arduino_dash/utils.py

Utility functions for board info, port validation, and board lookup.

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

import re
from typing import Optional, Tuple

from arduino_dash import state

PORT_RE = re.compile(r"^/dev/[a-zA-Z0-9_/]+$")


def is_valid_port(port: str) -> bool:
    """Check whether a port string matches the expected /dev/... format."""
    return bool(PORT_RE.match(port))


def normalize_port(port: str) -> Optional[str]:
    """Normalize and validate a port path.

    Strips extra leading slashes, ensures exactly one / prefix,
    then validates against PORT_RE. Returns the normalized port
    if valid, None otherwise.
    """
    normed = "/" + port.lstrip("/")
    return normed if is_valid_port(normed) else None


def get_known_boards() -> list[dict]:
    """Return a copy of the known boards list."""
    with state._board_list_lock:
        return list(state._board_list.values())


def get_board_events() -> list[dict]:
    """Return a snapshot of recent board events."""
    with state._board_events_lock:
        return list(state._board_events)


def get_first_board(boards: list[dict]) -> Tuple[str, str, str]:
    """Return the (port, fqbn, hardware_id) of the first board in the list."""
    if isinstance(boards, list) and boards:
        first = boards[0]
        return (
            first.get("port", ""),
            first.get("fqbn", ""),
            first.get("hardware_id", ""),
        )


def get_port_info(port: str) -> Optional[dict]:
    """Return the board info dict for the given port."""
    with state._board_list_lock:
        return state._board_list.get(port, {})


def find_board_info_by_port(port: str, boards: list[dict]) -> dict:
    """Find board info by port string."""
    return next(
        (
            b
            for b in boards
            if (b.get("port", "") if isinstance(b, dict) else "") == port
        ),
        {},
    )


def find_board_info_by_fqbn(fqbn: str, boards: list[dict]) -> dict:
    """Find board info by FQBN string."""
    return next(
        (
            b
            for b in boards
            if (b.get("fqbn", "") if isinstance(b, dict) else "") == fqbn
        ),
        {},
    )

