"""Board management helpers — routes moved to html_routes.py and api_routes.py"""

from flask import session

from arduino_dash.utils import (
    get_first_board,
    get_port_info,
    find_board_info_by_fqbn,
)


def _get_active_board_info():
    """Return the active board (port, fqbn, hardware_id) from the session."""
    raw = session.get("admin_active_board")
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        return (str(raw[0]), str(raw[1]), str(raw[2]))
    if isinstance(raw, str):
        return (raw, "", "")
    return ("", "", "")


def _resolve_board_info(
    active_board_port, active_board_fqbn, active_board_hardware_id, known_ports
):
    """Resolve board info, falling back to known ports if needed."""
    info = get_port_info(active_board_port)
    if not info:
        if active_board_fqbn:
            info = find_board_info_by_fqbn(active_board_fqbn, known_ports)
        if info:
            active_board_port = info.get("port", "")
            if not active_board_port:
                raise ValueError("port missing")
        elif known_ports:
            result = get_first_board(known_ports)
            if not result:
                raise ValueError("port missing")
            (active_board_port, active_board_fqbn, active_board_hardware_id) = result
            if not active_board_fqbn:
                raise ValueError("fqbn missing")
    else:
        port = info.get("port", "")
        if not port:
            raise ValueError("port missing")
        fqbn = info.get("fqbn", "")
        if not fqbn:
            raise ValueError("fqbn missing")
        if not active_board_fqbn:
            active_board_fqbn = fqbn
        elif fqbn != active_board_fqbn:
            info = find_board_info_by_fqbn(active_board_fqbn, known_ports)
            if info:
                active_board_port = info.get("port", "")
                if not active_board_port:
                    raise ValueError("port missing")
                active_board_fqbn = info.get("fqbn", "")
                if not active_board_fqbn:
                    raise ValueError("fqbn missing")
            else:
                active_board_fqbn = fqbn
    return active_board_port, active_board_fqbn, active_board_hardware_id
