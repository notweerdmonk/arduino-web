EXCLUDED_STDLIB = [
    "turtledemo",
    "turtle",
    "tkinter",
    "_tkinter",
    "distutils",
    "lib2to3",
    "pydoc",
    "doctest",
    "unittest",
]

def _exclude_stdlib(policy, resource):
    name = getattr(resource, "name", "") or ""
    pkg = getattr(resource, "package", "") or ""
    for excl in EXCLUDED_STDLIB:
        if name == excl or name.startswith(excl + "."):
            resource.add_include = False
            return
        if pkg == excl or pkg.startswith(excl + "."):
            resource.add_include = False
            return

def make_exe():
    dist = default_python_distribution()
    policy = dist.make_python_packaging_policy()
    policy.resources_location = "filesystem-relative:prefix"
    policy.include_test = False
    policy.include_distribution_sources = True
    policy.include_distribution_resources = True
    policy.include_non_distribution_sources = True
    policy.register_resource_callback(_exclude_stdlib)

    python_config = dist.make_python_interpreter_config()
    python_config.run_module = "medminder_dash.__main__"
    python_config.filesystem_importer = True
    python_config.oxidized_importer = True

    exe = dist.to_python_executable(
        name="medminder-dash",
        packaging_policy=policy,
        config=python_config,
    )

    local_wheels = exe.pip_download([
        "/home/weerdmonk/Projects/medminder/grpc_client/python/arduino_grpc/dist/arduino-grpc/arduino_grpc-0.1.0-py3-none-any.whl",
        "/home/weerdmonk/Projects/medminder/board_manager/python/board_manager/dist/board-manager/board_manager-0.1.0-py3-none-any.whl",
        "/home/weerdmonk/Projects/medminder/board_manager_client/python/board_manager_client/dist/board_manager_client-0.1.0-py3-none-any.whl",
        "/home/weerdmonk/Projects/medminder/arduino_sketch_tools/python/arduino_sketch_tools/dist/arduino-sketch-tools/arduino_sketch_tools-0.1.0-py3-none-any.whl",
        "/home/weerdmonk/Projects/medminder/medminder_dash/python/medminder_dash/dist/medminder-dash/medminder_dash-0.1.0-py3-none-any.whl",
    ])
    exe.add_python_resources(local_wheels)

    pypi_pkgs = exe.pip_install([
        "flask>=3.0",
        "gunicorn>=20.0",
        "flask-sock>=0.7.0",
        "grpcio>=1.80.0",
        "protobuf>=6.33.6",
    ])
    exe.add_python_resources(pypi_pkgs)

    return exe

def make_embedded_resources(exe):
    return exe.to_embedded_resources()

def make_install(exe):
    files = FileManifest()
    files.add_python_resource(".", exe)
    return files

register_target("exe", make_exe)
register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)
register_target("install", make_install, depends=["exe"], default=True)

resolve_targets()
