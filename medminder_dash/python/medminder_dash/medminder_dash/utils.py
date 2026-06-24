"""Utility functions for port management, validation, and display."""

import re

from typing import Optional, Tuple

from medminder_dash import state

VALID_MINUTES = {0, 10, 20, 30, 40, 50}
PORT_RE = re.compile(r"^/dev/[a-zA-Z0-9_/]+$")


def is_valid_port(port: str) -> bool:
    """Check whether a port path matches the expected /dev/... pattern."""
    return bool(PORT_RE.match(port))


def normalize_port(port: str) -> Optional[str]:
    """Normalize and validate a port path.

    Strips extra leading slashes, ensures exactly one / prefix,
    then validates against PORT_RE. Returns the normalized port
    if valid, None otherwise.
    """
    normed = "/" + port.lstrip("/")
    return normed if is_valid_port(normed) else None


def get_known_ports() -> list[dict]:
    """Return a snapshot of all known board ports.

    Returns:
        List of port info dicts.
    """
    with state._known_ports_lock:
        return list(state._known_ports.values())


def get_first_board(boards: list[dict]) -> Tuple[str, str, str]:
    """Return (port, fqbn, hardware_id) of the first board in the list.

    Args:
        boards: List of board info dicts.

    Returns:
        Tuple of (port, fqbn, hardware_id) or (empty strings) if list is empty.
    """
    if isinstance(boards, list) and boards:
        first = boards[0]
        return (
            first.get("port", ""),
            first.get("fqbn", ""),
            first.get("hardware_id", ""),
        )


def get_board_events() -> list[dict]:
    """Return a snapshot of recent board events.

    Returns:
        List of board event dicts.
    """
    with state._board_events_lock:
        return list(state._board_events)


def get_port_info(port: str) -> Optional[dict]:
    """Return info dict for a specific port, or empty dict if unknown.

    Args:
        port: Port path string.

    Returns:
        Board info dict or empty dict if not found.
    """
    with state._known_ports_lock:
        return state._known_ports.get(port, {})


def find_board_info_by_port(port: str, boards: list[dict]) -> dict:
    """Find board info dict by port in a list of boards.

    Args:
        port: Port path to match.
        boards: List of board info dicts.

    Returns:
        Matching board dict or empty dict.
    """
    return next(
        (
            b
            for b in boards
            if (b.get("port", "") if isinstance(b, dict) else "") == port
        ),
        {},
    )


def find_board_info_by_fqbn(fqbn: str, boards: list[dict]) -> dict:
    """Find board info dict by FQBN in a list of boards.

    Args:
        fqbn: Fully-qualified board name to match.
        boards: List of board info dicts.

    Returns:
        Matching board dict or empty dict.
    """
    return next(
        (
            b
            for b in boards
            if (b.get("fqbn", "") if isinstance(b, dict) else "") == fqbn
        ),
        {},
    )


def validate_medicine_data(data: dict) -> list[str]:
    """Validate medicine form data.

    Args:
        data: Dict containing name, hour, minute, day_of_week, day_of_month.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []
    name = data.get("name", "").strip()
    if not name:
        errors.append("Name is required")
    elif len(name) > 10:
        errors.append("Name must be 10 characters or fewer")
    hour_str = data.get("hour", "")
    try:
        hour = int(hour_str)
        if not (1 <= hour <= 24):
            errors.append("Hour must be 1-24")
    except (ValueError, TypeError):
        errors.append("Hour must be a number")
    minute_str = data.get("minute", "")
    try:
        minute = int(minute_str)
        if minute not in VALID_MINUTES:
            errors.append("Minute must be 0, 10, 20, 30, 40, or 50")
    except (ValueError, TypeError):
        errors.append("Minute must be a number")
    day_of_week_str = data.get("day_of_week", "0")
    try:
        dow = int(day_of_week_str)
        if not (0 <= dow <= 7):
            errors.append("Day of week must be 0-7")
    except (ValueError, TypeError):
        errors.append("Day of week must be a number")
    day_of_month_str = data.get("day_of_month", "0")
    try:
        dom = int(day_of_month_str)
        if not (0 <= dom <= 31):
            errors.append("Day of month must be 0-31")
    except (ValueError, TypeError):
        errors.append("Day of month must be a number")
    return errors


def day_name(dow: int) -> str:
    """Return the display name for a day-of-week value (0-7).

    Args:
        dow: Day of week (0 = Every day, 1 = Monday ... 7 = Sunday).

    Returns:
        Human-readable day name string.
    """
    names = {
        0: "Every day",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }
    return names.get(dow, f"Day {dow}")


def hour_display(hour: int) -> str:
    """Format hour as a zero-padded two-digit string (1-24).

    Args:
        hour: Hour value (24 is displayed as "00").

    Returns:
        Two-digit hour string.
    """
    if hour == 24:
        return "00"
    return str(hour).zfill(2)


def minute_display(minute: int) -> str:
    """Format minute as a zero-padded two-digit string.

    Args:
        minute: Minute value.

    Returns:
        Two-digit minute string.
    """
    return str(minute).zfill(2)


def time_display(hour: int, minute: int) -> str:
    """Format hour and minute as HH:MM display string.

    Args:
        hour: Hour value (1-24).
        minute: Minute value.

    Returns:
        Formatted time string.
    """
    return f"{hour_display(hour)}:{minute_display(minute)}"
