"""arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/routes.py

Blueprint for compile/upload routes

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

import time

from flask import Blueprint, current_app, jsonify, render_template, request

compile_bp = Blueprint(
    "arduino_sketch_tools",
    __name__,
    template_folder="templates",
)


@compile_bp.route("/board/<path:port>/compile", methods=["POST"])
def api_compile(port: str):
    """Start a sketch compile via pubsub and return an in-progress page."""
    tools = current_app.extensions["arduino_sketch_tools"]
    port = tools._norm_port(port)
    if port is None:
        return jsonify({"error": "Invalid port"}), 400
    if not tools.pubsub.is_connected:
        return render_template(
            "partials/bms_offline.html", section_id="compile-section", action="Compile"
        )
    sketch_path = request.form.get("sketch_path", "")
    fqbn = request.form.get("fqbn", "arduino:avr:uno")
    verbose = request.form.get("verbose", "false").lower() == "true"
    resp_topic = f"resp::compile::{port}"
    with tools._compile_results_lock:
        tools._compile_results[port] = None
    with tools._compile_meta_lock:
        tools._compile_meta[port] = tools._make_meta(port, sketch_path)
    tools.pubsub.publish(
        f"board::{port}::cmd",
        {
            "method": "compile",
            "params": {"sketch_path": sketch_path, "fqbn": fqbn, "verbose": verbose},
        },
        resp_topic,
    )
    return render_template("partials/compile_in_progress.html", port=port)


@compile_bp.route("/board/<path:port>/compile/poll")
def api_compile_poll(port: str):
    """Poll compile status and return the appropriate partial template."""
    tools = current_app.extensions["arduino_sketch_tools"]
    port = tools._norm_port(port)
    if port is None:
        return jsonify({"error": "Invalid port"}), 400
    with tools._compile_results_lock:
        result = tools._compile_results.get(port)
    with tools._compile_meta_lock:
        meta = tools._compile_meta.get(port, {})
    started = meta.get("started_at", 0)
    if result is None:
        if started and time.time() - started > tools.COMPILE_TIMEOUT:
            with tools._compile_meta_lock:
                tools._compile_meta.pop(port, None)
            return render_template(
                "partials/compile_timeout.html", port=port, meta=meta
            )
        return render_template(
            "partials/compile_poll_pending.html", port=port, meta=meta
        )
    if result.get("status") == "ok":
        sketch_path = result.get("data", {}).get("sketch_path", meta.get("sketch", ""))
        if sketch_path:
            with tools._last_compiled_sketch_lock:
                tools._last_compiled_sketch[port] = sketch_path
            with tools._last_compile_mtime_lock:
                tools._last_compile_mtime[port] = tools._get_sketch_mtime(sketch_path)
            with tools._last_compile_checksum_lock:
                tools._last_compile_checksum[port] = tools._compute_sketch_checksum(
                    sketch_path
                )
    compile_warning: str | None = None
    if result.get("status") == "error":
        with tools._last_compiled_sketch_lock:
            last_sketch = tools._last_compiled_sketch.get(port)
        if last_sketch:
            last_mtime: float | None = None
            with tools._last_compile_mtime_lock:
                last_mtime = tools._last_compile_mtime.get(port)
            modified = False
            if last_mtime is not None:
                current_mtime = tools._get_sketch_mtime(last_sketch)
                if current_mtime and current_mtime > last_mtime:
                    modified = True
            if not modified:
                last_checksum = ""
                with tools._last_compile_checksum_lock:
                    last_checksum = tools._last_compile_checksum.get(port, "")
                if last_checksum:
                    current_checksum = tools._compute_sketch_checksum(last_sketch)
                    if current_checksum and current_checksum != last_checksum:
                        modified = True
            if modified:
                compile_warning = "sketch_modified"
    with tools._compile_meta_lock:
        tools._compile_meta.pop(port, None)
    return render_template(
        "partials/compile_result.html",
        result=result,
        port=port,
        meta=meta,
        compile_warning=compile_warning,
    )


@compile_bp.route("/board/<path:port>/upload", methods=["POST"])
def api_upload(port: str):
    """Start a sketch upload via pubsub, checking for warnings first."""
    tools = current_app.extensions["arduino_sketch_tools"]
    port = tools._norm_port(port)
    if port is None:
        return jsonify({"error": "Invalid port"}), 400
    if not tools.pubsub.is_connected:
        return render_template(
            "partials/bms_offline.html", section_id="upload-section", action="Upload"
        )
    sketch_path = request.form.get("sketch_path", "")
    fqbn = request.form.get("fqbn", "arduino:avr:uno")
    verbose = request.form.get("verbose", "false").lower() == "true"

    warnings: list[dict] = []
    with tools._last_compiled_sketch_lock:
        last_sketch = tools._last_compiled_sketch.get(port)
    if last_sketch and last_sketch != sketch_path:
        warnings.append(
            {"type": "sketch_path_changed", "old": last_sketch, "new": sketch_path}
        )
    modified = False
    with tools._last_compile_mtime_lock:
        last_mtime = tools._last_compile_mtime.get(port)
    if last_mtime is not None:
        current_mtime = tools._get_sketch_mtime(sketch_path)
        if current_mtime and current_mtime > last_mtime:
            modified = True
    if not modified:
        last_checksum = ""
        with tools._last_compile_checksum_lock:
            last_checksum = tools._last_compile_checksum.get(port, "")
        if last_checksum:
            current_checksum = tools._compute_sketch_checksum(sketch_path)
            if current_checksum and current_checksum != last_checksum:
                modified = True
    if modified:
        warnings.append({"type": "sketch_modified"})

    if warnings:
        return render_template(
            "partials/upload_confirm.html",
            port=port,
            warnings=warnings,
            sketch_path=sketch_path,
            fqbn=fqbn,
            verbose=verbose,
        )

    with tools._last_uploaded_sketch_lock:
        tools._last_uploaded_sketch[port] = sketch_path

    resp_topic = f"resp::upload::{port}"
    with tools._upload_results_lock:
        tools._upload_results[port] = None
    with tools._upload_meta_lock:
        tools._upload_meta[port] = tools._make_meta(port, sketch_path)
    tools.pubsub.publish(
        f"board::{port}::cmd",
        {
            "method": "upload",
            "params": {
                "sketch_path": sketch_path,
                "fqbn": fqbn,
                "port": port,
                "verbose": verbose,
            },
        },
        resp_topic,
    )
    return render_template("partials/upload_in_progress.html", port=port)


@compile_bp.route("/board/<path:port>/upload/poll")
def api_upload_poll(port: str):
    """Poll upload status and return the appropriate partial template."""
    tools = current_app.extensions["arduino_sketch_tools"]
    port = tools._norm_port(port)
    if port is None:
        return jsonify({"error": "Invalid port"}), 400
    with tools._upload_results_lock:
        result = tools._upload_results.get(port)
    with tools._upload_meta_lock:
        meta = tools._upload_meta.get(port, {})
    if result is None:
        return render_template(
            "partials/upload_poll_pending.html", port=port, meta=meta
        )
    with tools._upload_meta_lock:
        tools._upload_meta.pop(port, None)
    return render_template(
        "partials/upload_result.html", result=result, port=port, meta=meta
    )


@compile_bp.route("/board/<path:port>/upload/confirm", methods=["POST"])
def api_upload_confirm(port: str):
    """Confirm and start an upload after warnings have been acknowledged."""
    tools = current_app.extensions["arduino_sketch_tools"]
    port = tools._norm_port(port)
    if port is None:
        return jsonify({"error": "Invalid port"}), 400
    if not tools.pubsub.is_connected:
        return render_template(
            "partials/bms_offline.html", section_id="upload-section", action="Upload"
        )
    sketch_path = request.form.get("sketch_path", "")
    fqbn = request.form.get("fqbn", "arduino:avr:uno")
    verbose = request.form.get("verbose", "false").lower() == "true"
    with tools._last_uploaded_sketch_lock:
        tools._last_uploaded_sketch[port] = sketch_path
    resp_topic = f"resp::upload::{port}"
    with tools._upload_results_lock:
        tools._upload_results[port] = None
    with tools._upload_meta_lock:
        tools._upload_meta[port] = tools._make_meta(port, sketch_path)
    tools.pubsub.publish(
        f"board::{port}::cmd",
        {
            "method": "upload",
            "params": {
                "sketch_path": sketch_path,
                "fqbn": fqbn,
                "port": port,
                "verbose": verbose,
            },
        },
        resp_topic,
    )
    return render_template("partials/upload_in_progress.html", port=port)


@compile_bp.route("/board/<path:port>/upload/section")
def api_upload_section(port: str):
    """Return the upload section template for a given port."""
    tools = current_app.extensions["arduino_sketch_tools"]
    port = tools._norm_port(port)
    if port is None:
        return jsonify({"error": "Invalid port"}), 400
    return render_template("partials/upload_init.html", port=port)

