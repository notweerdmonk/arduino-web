"""HTML page and partial routes — no /api/ prefix"""

import bisect
import datetime
import hashlib
import json
import logging
import os
import shutil
import uuid

from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename

from medminder_dash import state
from medminder_dash.medicines_state import Medicine
from medminder_dash.pubsub import (
    add_ws_client,
    is_connected,
    is_daemon_ready,
    ensure_sketch_dir,
    _get_alarm_hpp_path,
    broadcast_ws,
    remove_ws_client,
)
from medminder_dash.settings import _DEFAULT_SKETCH_DIR, load_sketch_dir
from medminder_dash.sketch_gen import generate_alarm_hpp, parse_alarm_hpp
from medminder_dash.sketch_management import (
    _compute_sketch_checksum,
    _find_existing_version,
    _normalize_ino_filename,
    _resolve_latest_upload,
    _save_registry,
    _update_meta_hw_ids,
    _render_sketch_path_selector,
)
from medminder_dash.sketch_registry import (
    get_assignment as get_board_sketch_assignment,
    set_assignment,
)
from medminder_dash.utils import (
    day_name,
    find_board_info_by_fqbn,
    get_board_events,
    get_first_board,
    get_known_ports,
    get_port_info,
    normalize_port,
    time_display,
    validate_medicine_data,
)

logger = logging.getLogger(__name__)

# module-level store reference — set in init_html_routes
store = None


def _get_active_board_info():
    """Return the active board info tuple from the session.

    Returns:
        Tuple of (port, fqbn, hardware_id).
    """
    raw = session.get("admin_active_board")
    if isinstance(raw, (tuple, list)) and len(raw) >= 3:
        return (str(raw[0]), str(raw[1]), str(raw[2]))
    if isinstance(raw, str):
        return (raw, "", "")
    return ("", "", "")


def _resolve_first_port_info(ports):
    """Resolve the first available board info from a ports list.

    Args:
        ports: List of board info dicts.

    Returns:
        Tuple of (port, fqbn, hardware_id).

    Raises:
        ValueError: If no port or FQBN found.
    """
    result = get_first_board(ports)
    if not result:
        raise ValueError("port missing")
    port, fqbn, hw_id = result
    if not fqbn:
        raise ValueError("fqbn missing")
    return port, fqbn, hw_id


def _resolve_board_info(
    active_board_port, active_board_fqbn, active_board_hardware_id, ports
):
    """Resolve and reconcile board info from session state and known ports.

    Args:
        active_board_port: Current active board port from session.
        active_board_fqbn: Current active board FQBN from session.
        active_board_hardware_id: Current active board hardware ID.
        ports: List of known port info dicts.

    Returns:
        Tuple of (port, fqbn, hardware_id).
    """
    info = get_port_info(active_board_port)
    if not info:
        if active_board_fqbn:
            info = find_board_info_by_fqbn(active_board_fqbn, ports)
        if info:
            active_board_port = info.get("port", "")
            if not active_board_port:
                raise ValueError("port missing")
        elif ports:
            (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                _resolve_first_port_info(ports)
            )
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
            info = find_board_info_by_fqbn(active_board_fqbn, ports)
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


def _write_alarm_hpp(meds):
    """Write the alarm.hpp file from a list of medicines.

    Args:
        meds: List of Medicine instances.
    """
    try:
        ensure_sketch_dir()
        path = _get_alarm_hpp_path()
        content = generate_alarm_hpp(meds)
        with open(path, "w") as f:
            f.write(content)
        logger.info("Wrote alarm.hpp (%d medicines) to %s", len(meds), path)
    except Exception:
        logger.exception("Failed to write alarm.hpp")


def _medicine_to_dict(med):
    """Convert a Medicine object to a serializable dict.

    Args:
        med: Medicine instance.

    Returns:
        Dict with medicine fields.
    """
    return {
        "name": med.name,
        "hour": med.hour,
        "minute": med.minute,
        "day_of_week": med.day_of_week,
        "day_of_month": med.day_of_month,
    }


def _medicine_dict_sort_key(d):
    """Return a sort key for a medicine dict.

    Args:
        d: Medicine dict.

    Returns:
        Tuple for sorting.
    """
    return (d["name"], d["hour"], d["minute"], d["day_of_week"], d["day_of_month"])


def _compute_diff(active_board):
    """Compute the difference between store medicines and alarm.hpp entries.

    Args:
        active_board: Active board port string.

    Returns:
        Diff dict with metadata, alarm_hpp, differ flag, and active_board.
    """
    metadata_list = sorted(
        [_medicine_to_dict(m) for m in store.only_enabled()],
        key=_medicine_dict_sort_key,
    )
    path = _get_alarm_hpp_path()
    if not os.path.exists(path):
        return {
            "metadata": metadata_list,
            "alarm_hpp": [],
            "differ": True,
            "alarm_hpp_exists": False,
            "alarm_hpp_error": None,
            "active_board": active_board,
        }
    try:
        parsed = parse_alarm_hpp(path)
        alarm_hpp_list = sorted(
            [
                {
                    "name": e["name"],
                    "hour": e["hour"],
                    "minute": e["minute"],
                    "day_of_week": e["day_of_week"],
                    "day_of_month": e["day_of_month"],
                }
                for e in parsed
            ],
            key=_medicine_dict_sort_key,
        )
        differ = metadata_list != alarm_hpp_list
        return {
            "metadata": metadata_list,
            "alarm_hpp": alarm_hpp_list,
            "differ": differ,
            "alarm_hpp_exists": True,
            "alarm_hpp_error": None,
            "active_board": active_board,
        }
    except Exception as e:
        return {
            "metadata": metadata_list,
            "alarm_hpp": [],
            "differ": True,
            "alarm_hpp_exists": True,
            "alarm_hpp_error": str(e),
            "active_board": active_board,
        }


def _issue_confirm_token():
    """Generate and store a confirmation token in the session.

    Returns:
        Token string.
    """
    token = uuid.uuid4().hex
    session["medicine_confirm_token"] = token
    return token


def _validate_and_consume_confirm_token():
    """Validate and consume the confirmation token from the session.

    Returns:
        Tuple of (success_bool, error_message).
    """
    sent = request.form.get("confirm_token", "")
    expected = session.pop("medicine_confirm_token", None)
    if not expected or sent != expected:
        return False, "Confirmation required, please reload the page"
    return True, ""


def _require_board():
    """Return the board_port from session, or None."""
    return session.get("board_port")


def _require_any_board():
    """Return any available board port from session or active board info."""
    port = session.get("board_port")
    if port:
        return port
    return _get_active_board_info()[0]


def init_html_routes(
    app: Flask,
    sock,
    store_param,
    migrate_default_board,
    load_sketch_dir_param=None,
    get_alarm_hpp_path_param=None,
):
    """Register all HTML page and partial routes on the Flask app.

    Args:
        app: Flask application instance.
        sock: Flask-Sock instance (or None).
        store_param: MedicineStore instance.
        migrate_default_board: Callable to migrate default board data.
        load_sketch_dir_param: Callable to load sketch directory (unused).
        get_alarm_hpp_path_param: Callable to get alarm.hpp path (unused).
    """
    global store
    store = store_param
    # load_sketch_dir_param and get_alarm_hpp_path_param are kept for
    # compatibility with existing callers but routes use the module-level
    # imports from pubsub / settings directly.

    # ------------------------------------------------------------------ #
    #  Routes from app.py create_app() — HTML pages and partials          #
    # ------------------------------------------------------------------ #

    @app.route("/")
    def index():
        """Render the index/home page."""
        return render_template(
            "index.html", count=len(store.all()), sketch_path=load_sketch_dir()
        )

    @app.route("/medicines")
    def medicines():
        """Render the medicines list page."""
        meds = store.all()
        return render_template(
            "medicines.html",
            medicines=meds,
            day_name=day_name,
            time_display=time_display,
        )

    @app.route("/medicine/new")
    def medicine_new_form():
        """Render the medicine creation form."""
        return render_template(
            "medicine_form.html", medicine=None, errors=[], day_name=day_name
        )

    @app.route("/medicine", methods=["POST"])
    def medicine_create():
        """Handle medicine creation form submission."""
        if not _require_any_board():
            return "Select a board first", 400
        errors = validate_medicine_data(request.form)
        if errors:
            return render_template(
                "medicine_form.html", medicine=None, errors=errors, day_name=day_name
            ), 400
        med = Medicine(
            name=request.form["name"].strip(),
            hour=int(request.form["hour"]),
            minute=int(request.form["minute"]),
            day_of_week=int(request.form.get("day_of_week", "0")),
            day_of_month=int(request.form.get("day_of_month", "0")),
        )
        store.add(med)
        _write_alarm_hpp(store.only_enabled())
        return render_template(
            "medicines.html",
            medicines=store.all(),
            day_name=day_name,
            time_display=time_display,
        )

    @app.route("/medicine/<med_id>/edit")
    def medicine_edit_form(med_id):
        """Render the medicine edit form for a given ID."""
        med = store.get(med_id)
        if med is None:
            return "", 404
        return render_template(
            "medicine_form.html", medicine=med, errors=[], day_name=day_name
        )

    @app.route("/medicine/<med_id>", methods=["PUT"])
    def medicine_update(med_id):
        """Handle medicine update form submission."""
        if not _require_any_board():
            return "Select a board first", 400
        med = store.get(med_id)
        if med is None:
            return "", 404
        errors = validate_medicine_data(request.form)
        if errors:
            return render_template(
                "medicine_form.html", medicine=med, errors=errors, day_name=day_name
            ), 400
        store.update(
            med_id,
            name=request.form["name"].strip(),
            hour=int(request.form["hour"]),
            minute=int(request.form["minute"]),
            day_of_week=int(request.form.get("day_of_week", "0")),
            day_of_month=int(request.form.get("day_of_month", "0")),
        )
        _write_alarm_hpp(store.only_enabled())
        return render_template(
            "medicines.html",
            medicines=store.all(),
            day_name=day_name,
            time_display=time_display,
        )

    @app.route("/medicine/<med_id>", methods=["DELETE"])
    def medicine_delete(med_id):
        """Handle medicine deletion."""
        if not _require_any_board():
            return "Select a board first", 400
        if not store.delete(med_id):
            return "", 404
        _write_alarm_hpp(store.only_enabled())
        return render_template(
            "medicines.html",
            medicines=store.all(),
            day_name=day_name,
            time_display=time_display,
        )

    @app.route("/medicine/<med_id>/toggle", methods=["PUT"])
    def medicine_toggle(med_id):
        """Handle medicine enabled state toggle."""
        if not _require_any_board():
            return "Select a board first", 400
        store.toggle(med_id)
        _write_alarm_hpp(store.only_enabled())
        return render_template(
            "medicines.html",
            medicines=store.all(),
            day_name=day_name,
            time_display=time_display,
        )

    @app.route("/daemon/status")
    def html_daemon_status():
        """Render the daemon status badge partial."""
        ready = is_connected() and is_daemon_ready()
        return render_template("partials/daemon_badge.html", ready=ready)

    @app.route("/admin")
    def admin():
        """Render the admin page."""
        ports = get_known_ports()
        active_board_port = request.args.get("port", "").strip()
        active_board_fqbn = ""
        active_board_hardware_id = ""
        active_board_sketch = ""

        if not active_board_port:
            (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                _get_active_board_info()
            )

        if not active_board_port:
            if ports:
                try:
                    (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                        _resolve_first_port_info(ports)
                    )
                except ValueError as e:
                    return str(e), 500
                session["admin_active_board"] = (
                    active_board_port,
                    active_board_fqbn,
                    active_board_hardware_id,
                )

        else:
            info = get_port_info(active_board_port)
            if not info:
                if active_board_fqbn:
                    info = find_board_info_by_fqbn(active_board_fqbn, ports)
                elif ports:
                    info = ports[0]

            if info:
                active_board_port = info.get("port", "")
                active_board_fqbn = info.get("fqbn", "")
                active_board_hardware_id = info.get("hardware_id", "")
            else:
                active_board_port = ""
                active_board_fqbn = ""
                active_board_hardware_id = ""
            session["admin_active_board"] = (
                active_board_port,
                active_board_fqbn,
                active_board_hardware_id,
            )

        if not active_board_fqbn:
            active_board_fqbn = "arduino:avr:uno"

        if active_board_port:
            store.load_board(active_board_port)
        diff = _compute_diff(active_board_port)

        if active_board_hardware_id:
            active_board_sketch = (
                get_board_sketch_assignment(active_board_hardware_id) or ""
            )

        return render_template(
            "admin.html",
            ports=ports,
            active_board_port=active_board_port,
            active_board_fqbn=active_board_fqbn,
            active_board_hardware_id=active_board_hardware_id,
            active_board_sketch=active_board_sketch,
            default_sketch_path=_DEFAULT_SKETCH_DIR,
            initial_diff=diff,
            day_name=day_name,
            time_display=time_display,
        )

    @app.route("/medicines/board-selector")
    def html_medicines_board_selector():
        """Render the board selector partial."""
        ports = get_known_ports()
        (active_board_port, active_board_fqbn, _) = _get_active_board_info()
        if not active_board_port and ports:
            try:
                (active_board_port, active_board_fqbn, _) = _resolve_first_port_info(
                    ports
                )
            except ValueError as e:
                return str(e), 500
        try:
            (active_board_port, active_board_fqbn, _) = _resolve_board_info(
                active_board_port, active_board_fqbn, "", ports
            )
        except ValueError as e:
            return str(e), 500
        return render_template(
            "partials/admin_board_selector.html",
            ports=ports,
            active_board=active_board_port,
            active_board_fqbn=active_board_fqbn,
            board_selector_label="Active Board (for medicine management, compile, and upload)",
            board_selector_hx_post="/medicines/active-board",
            board_selector_hx_target="#medicine-cards-container",
            board_selector_hx_swap="outerHTML",
        )

    @app.route("/board/compile-upload-card")
    def html_board_compile_upload_card():
        """Render the compile/upload card partial."""
        (active_board_port, active_board_fqbn, active_board_hardware_id) = (
            _get_active_board_info()
        )
        ports = get_known_ports()
        if not active_board_port and ports:
            try:
                (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                    _resolve_first_port_info(ports)
                )
            except ValueError as e:
                return str(e), 500
        try:
            (active_board_port, active_board_fqbn, active_board_hardware_id) = (
                _resolve_board_info(
                    active_board_port,
                    active_board_fqbn,
                    active_board_hardware_id,
                    ports,
                )
            )
        except ValueError as e:
            return str(e), 500
        active_board_path = (active_board_port or "").lstrip("/")
        return render_template(
            "partials/compile_upload_card.html",
            active_board=active_board_port,
            active_board_path=active_board_path,
            active_board_fqbn=active_board_fqbn,
        )

    @app.route("/medicines/confirm-modal", methods=["GET"])
    def html_medicines_confirm_modal():
        """Render the confirmation modal for generate/sync actions."""
        action = request.args.get("action", "")
        if action not in ("generate", "sync"):
            return "Unknown action", 400
        confirm_token = _issue_confirm_token()
        if action == "generate":
            title = "Generate alarm.hpp"
            warning = (
                "This will overwrite the existing alarm.hpp file with the current "
                "medicine schedule. Any hand-edits to alarm.hpp will be lost."
            )
            post_url = "/medicines/generate-hpp"
            confirm_label = "Generate alarm.hpp"
        else:
            title = "Sync FROM alarm.hpp"
            warning = (
                "This will replace the current medicine schedule in metadata with "
                "the contents of alarm.hpp. Any medicines not yet written to alarm.hpp "
                "will be lost."
            )
            post_url = "/medicines/sync-from-hpp"
            confirm_label = "Sync from alarm.hpp"
        return render_template(
            "partials/confirm_modal.html",
            title=title,
            warning=warning,
            post_url=post_url,
            confirm_token=confirm_token,
            confirm_label=confirm_label,
        )

    @app.route("/medicines/generate-hpp", methods=["POST"])
    def html_medicines_generate_hpp():
        """Generate alarm.hpp from the current medicine store."""
        ok, err = _validate_and_consume_confirm_token()
        if not ok:
            return err, 403
        ensure_sketch_dir()
        meds = store.only_enabled()
        content = generate_alarm_hpp(meds)
        with open(_get_alarm_hpp_path(), "w") as f:
            f.write(content)
        logger.info(
            "Generated alarm.hpp with %d medicines to %s",
            len(meds),
            _get_alarm_hpp_path(),
        )
        return (
            f'<div class="log-viewer">Generated alarm.hpp with {len(meds)} enabled medicine(s).</div>',
            200,
        )

    @app.route("/medicines/sync-from-hpp", methods=["POST"])
    def html_medicines_sync_from_hpp():
        """Sync the medicine store from alarm.hpp contents."""
        ok, err = _validate_and_consume_confirm_token()
        if not ok:
            return err, 403
        path = _get_alarm_hpp_path()
        entries = parse_alarm_hpp(path)
        for med in list(store.all()):
            store.delete(med.id)
        for e in entries:
            store.add(Medicine(**e))
        logger.info("Synced %d medicines from %s into store", len(entries), path)
        return (
            f'<div class="log-viewer">Loaded {len(entries)} medicine(s) from alarm.hpp.</div>',
            200,
        )

    @app.route("/medicines/active-board", methods=["POST"])
    def html_medicines_active_board():
        """Set the active board and render the medicine cards partial."""
        port = request.form.get("port", "").strip()
        if not port:
            return "port required", 400
        session["admin_active_board"] = port
        store.load_board(port)
        diff = _compute_diff(port)
        info = get_port_info(port) or {}
        fqbn = info.get("fqbn", "") or "arduino:avr:uno"
        oob = (
            f'<span id="global-fqbn-display" hx-swap-oob="true">{fqbn}</span>'
            f'<input type="hidden" id="global-fqbn" value="{fqbn}" hx-swap-oob="true">'
            f'<input type="hidden" id="fqbn" name="fqbn" value="{fqbn}" hx-swap-oob="true">'
        )
        return (
            render_template(
                "partials/medicine_cards.html",
                diff=diff,
                day_name=day_name,
                time_display=time_display,
            )
            + oob
        )

    @app.route("/medicines/active-board-card")
    def html_medicines_active_board_card():
        """Render the active board medicine cards partial."""
        active_board, _, _ = _get_active_board_info()
        if active_board:
            store.load_board(active_board)
        diff = _compute_diff(active_board)
        return render_template(
            "partials/medicine_cards.html",
            diff=diff,
            day_name=day_name,
            time_display=time_display,
        )

    # ------------------------------------------------------------------ #
    #  Routes from board_management.py init_board_routes()                #
    # ------------------------------------------------------------------ #

    @app.route("/board/select/<path:port>")
    def board_select(port):
        """Select a board by port and redirect to its detail page."""
        norm_port = normalize_port(port)
        if norm_port is None:
            return "Invalid port", 400
        session["board_port"] = norm_port
        store.load_board(norm_port)
        migrate_default_board()
        return redirect(url_for("board_detail", port=norm_port.lstrip("/")))

    @app.route("/board")
    def board_redirect():
        """Redirect to the selected board's detail page."""
        port = _require_board()
        if not port:
            return "<p>No board selected. Please select a board.</p>", 400
        return redirect(url_for("board_detail", port=port))

    @app.route("/board/<path:port>")
    def board_detail(port):
        """Render the board detail page."""
        norm_port = normalize_port(port)
        if norm_port is None:
            return "Invalid port", 400
        session["board_port"] = norm_port
        store.load_board(norm_port)
        migrate_default_board()
        if not store.all():
            path = _get_alarm_hpp_path()
            entries = parse_alarm_hpp(path)
            for e in entries:
                store.add(Medicine(**e))
            if entries:
                logger.info(
                    "Loaded %d medicine(s) from %s into board %s",
                    len(entries),
                    path,
                    norm_port,
                )
        board_info = get_port_info(norm_port)
        board_name = (board_info or {}).get("board", "") or norm_port
        hardware_id = (board_info or {}).get("hardware_id", "")
        sketch_path = get_board_sketch_assignment(hardware_id) if hardware_id else None
        if not sketch_path:
            sketch_path = _resolve_latest_upload()
        if not sketch_path:
            sketch_path = load_sketch_dir()
        port_path = norm_port.lstrip("/")
        return render_template(
            "board_detail.html",
            port=norm_port,
            port_path=port_path,
            board_name=board_name,
            board_info=board_info,
            sketch_path=sketch_path,
            hardware_id=hardware_id,
            show_sketch_tools=False,
            show_medicines_section=True,
        )

    @app.route("/board/<path:port>/connection-status")
    def html_board_connection_status(port):
        """Render the board connection status badge partial."""
        norm_port = normalize_port(port)
        if norm_port is None:
            return "Invalid port", 400
        info = get_port_info(norm_port)
        connected = bool(info)
        port_path = norm_port.lstrip("/")
        return render_template(
            "partials/board_status_badge.html",
            port=norm_port,
            port_path=port_path,
            connected=connected,
        )

    @app.route("/boards")
    def html_boards():
        """Render the board list partial."""
        ports = get_known_ports()
        return render_template("partials/board_list.html", ports=ports)

    @app.route("/boards/event")
    def html_boards_event():
        """Render the board events partial."""
        events = get_board_events()
        return render_template("partials/board_event.html", events=events)

    @app.route("/boards/grid")
    def html_boards_grid():
        """Render the board grid partial."""
        boards = get_known_ports()
        return render_template("partials/board_grid.html", boards=boards)

    @app.route("/boards/grid/card/<path:port>")
    def html_boards_grid_card(port: str):
        """Render a single board card partial."""
        norm_port = normalize_port(port)
        if norm_port is None:
            return "", 400
        boards = get_known_ports()
        for b in boards:
            if b.get("port") == norm_port:
                return render_template("partials/board_card.html", b=b)
        return "", 404

    # ------------------------------------------------------------------ #
    #  WebSocket — stays with HTML routes                                 #
    # ------------------------------------------------------------------ #

    if sock is not None:

        @sock.route("/ws/board-events")
        def ws_board_events(ws):
            """Handle WebSocket connections for board event streaming."""
            add_ws_client(ws)
            try:
                while True:
                    data = ws.receive(timeout=30)
                    if data is None:
                        break
            except SystemExit:
                logger.info("WebSocket handler interrupted — gunicorn shutting down")
            finally:
                remove_ws_client(ws)

        logger.info("WebSocket endpoint /ws/board-events registered")

    # ------------------------------------------------------------------ #
    #  Routes from sketch_management.py init_sketch_routes() — HTML only  #
    # ------------------------------------------------------------------ #

    @app.route("/last-upload")
    def html_last_upload():
        """Render the last uploaded sketch path selector."""
        hardware_id = request.args.get("hardware_id", "").strip()
        if hardware_id:
            assigned = get_board_sketch_assignment(hardware_id)
            if assigned and os.path.isdir(assigned):
                return _render_sketch_path_selector(
                    assigned, include_default=True, hardware_id=hardware_id
                )
        selected_path = _resolve_latest_upload()
        if selected_path is None:
            return _render_sketch_path_selector(
                include_default=True, hardware_id=hardware_id
            )
        return _render_sketch_path_selector(
            selected_path, include_default=True, hardware_id=hardware_id
        )

    @app.route("/sketch/upload", methods=["POST"])
    def html_sketch_upload():
        """Handle sketch file upload."""
        request.get_data()
        files = request.files.getlist("files[]")
        hardware_id = request.args.get("hardware_id", "")
        if not files:
            return _render_sketch_path_selector()

        first_rel = files[0].filename or ""
        parts = first_rel.replace("\\", "/").split("/")
        root_name = parts[0] if parts else "sketch"

        server_ts = datetime.datetime.utcnow().isoformat()
        ts_dir = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = secure_filename(root_name) or "sketch"
        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "unknown")
        salt = hashlib.sha256(f"{ip}:{ua}".encode()).hexdigest()[:16]
        upload_dir = os.path.join(state.UPLOAD_BASE_DIR, f"{salt}_{ts_dir}_{safe_name}")
        os.makedirs(upload_dir, exist_ok=True)

        total_size = 0
        file_count = 0
        for f in files:
            rel_path = f.filename or ""
            if not rel_path:
                continue
            file_count += 1
            rel_parts = rel_path.replace("\\", "/").split("/")
            safe_parts = [secure_filename(p) or p for p in rel_parts]
            safe_rel = os.path.join(*safe_parts)
            dest = os.path.join(upload_dir, safe_rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            f.save(dest)
            total_size += os.path.getsize(dest)

        sketch_dir = os.path.join(upload_dir, safe_name)
        _normalize_ino_filename(sketch_dir, safe_name)

        checksum = _compute_sketch_checksum(sketch_dir)
        key = (ip, ua)

        with state._upload_registry_lock:
            user_sketches = state._upload_registry.setdefault(key, {})
            versions = user_sketches.setdefault(safe_name, [])
            existing = _find_existing_version(user_sketches, checksum)
            if existing:
                shutil.rmtree(upload_dir, ignore_errors=True)
                sketch_dir = existing["path"]
                if hardware_id and hardware_id not in existing["hardware_ids"]:
                    existing["hardware_ids"].append(hardware_id)
                    existing["board_timestamps"][hardware_id] = server_ts
                    _update_meta_hw_ids(
                        existing["path"],
                        existing["hardware_ids"],
                        existing["board_timestamps"],
                    )
                    _save_registry()
                    broadcast_ws(
                        '<div class="sketch-event">Sketch deduplicated <!-- board-event --></div>'
                    )
            else:
                meta = {
                    "ip": ip,
                    "user_agent": ua,
                    "server_timestamp": server_ts,
                    "file_count": len(files),
                    "total_size": total_size,
                    "root_name": safe_name,
                    "checksum": checksum,
                    "hardware_ids": [hardware_id] if hardware_id else [],
                    "board_timestamps": {hardware_id: server_ts} if hardware_id else {},
                }
                with open(os.path.join(upload_dir, ".meta"), "w") as mf:
                    json.dump(meta, mf)
                bisect.insort(
                    versions,
                    {
                        "path": sketch_dir,
                        "checksum": checksum,
                        "server_timestamp": server_ts,
                        "hardware_ids": meta["hardware_ids"],
                        "board_timestamps": meta["board_timestamps"],
                    },
                    key=lambda v: v["server_timestamp"],
                )
                _save_registry()
                broadcast_ws(
                    '<div class="sketch-event">Sketch updated <!-- board-event --></div>'
                )

        if hardware_id:
            set_assignment(hardware_id, sketch_dir)

        return _render_sketch_path_selector(sketch_dir, hardware_id=hardware_id)

    @app.route("/sketch", methods=["DELETE"])
    def html_sketch_delete():
        """Handle sketch deletion."""
        sketch_path = request.args.get("path", "")
        hardware_id = request.args.get("hardware_id", "")
        if not sketch_path:
            return _render_sketch_path_selector(hardware_id=hardware_id)
        norm_path = os.path.normpath(sketch_path)
        norm_base = os.path.normpath(state.UPLOAD_BASE_DIR)
        if not norm_path.startswith(norm_base):
            return _render_sketch_path_selector(hardware_id=hardware_id)

        ip = request.remote_addr or "unknown"
        ua = request.headers.get("User-Agent", "unknown")
        key = (ip, ua)
        removed = False
        with state._upload_registry_lock:
            entries = state._upload_registry.get(key, {})
            for name, versions in list(entries.items()):
                for i, v in enumerate(versions):
                    if not removed and v["path"] == norm_path:
                        versions.pop(i)
                        removed = True
                        if not versions:
                            del entries[name]
                        break
            if removed:
                all_latest = [vs[-1] for vs in entries.values() if vs]
                latest = (
                    max(all_latest, key=lambda v: v["server_timestamp"])
                    if all_latest
                    else None
                )
        if removed:
            _save_registry()
            broadcast_ws(
                '<div class="sketch-event">Sketch deleted <!-- board-event --></div>'
            )
            shutil.rmtree(os.path.dirname(norm_path), ignore_errors=True)
            if latest is not None:
                return _render_sketch_path_selector(
                    latest.get("path", ""), hardware_id=hardware_id
                )
            return _render_sketch_path_selector(hardware_id=hardware_id)
        return _render_sketch_path_selector(hardware_id=hardware_id)
