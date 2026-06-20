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
    python_config.run_module = "board_manager.__main__"
    python_config.filesystem_importer = True
    python_config.oxidized_importer = True

    exe = dist.to_python_executable(
        name="board-manager",
        packaging_policy=policy,
        config=python_config,
    )

    all_wheels = exe.pip_install([
        "/home/weerdmonk/Projects/medminder/grpc_client/python/arduino_grpc/dist/arduino-grpc/arduino_grpc-0.1.0-py3-none-any.whl",
        "/home/weerdmonk/Projects/medminder/board_manager/python/board_manager/dist/board-manager/board_manager-0.1.0-py3-none-any.whl",
        "grpcio>=1.80.0",
        "protobuf>=6.33.6",
    ])
    exe.add_python_resources(all_wheels)

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
