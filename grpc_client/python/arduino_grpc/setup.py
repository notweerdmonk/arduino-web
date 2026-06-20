"""
arduino-grpc — gRPC client stubs for the arduino-cli gRPC service.

This package contains the Python stubs (and supporting ``__init__`` chain)
generated from the arduino-cli ``.proto`` files by
``scripts/gen_grpc_bindings.py``. It depends only on the official
``grpcio`` / ``protobuf`` / ``googleapis-common-protos`` packages and can
therefore be installed from PyPI without any local source wheels.

Local-source convention
-----------------------
In this monorepo the ``arduino_grpc`` wheel is normally consumed by the
sibling packages (``board_manager``, ``board_manager_client``,
``arduino_dash``, ``medminder_dash``) via the local ``file://`` index
declared in their Pipfiles — see ``<pkg>/python/<pkg>/Pipfile`` and the
noxfile for the wheel build. The ``install_requires`` declared in
``pyproject.toml`` uses standard PyPI package names so the package also
works for a normal ``pip install arduino-grpc`` from a remote index.

Why a setup.py at all
---------------------
``pyproject.toml`` is the source of truth for the package metadata, but
the generated stubs live at ``<pkg>/cc/`` (i.e. *outside* the
``arduino_grpc/`` source directory). We use a small ``setup.py`` here
purely to tell setuptools about the cross-source-directory layout via
``packages`` and ``package_dir``; everything else is read from
``pyproject.toml`` (PEP 621).
"""

from setuptools import setup

setup(
    name="arduino-grpc",
    version="0.1.0",
    description="gRPC client stubs for arduino-cli",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="notweerdmonk",
    author_email="wrdmnk@gmail.com",
    python_requires=">=3.10",
    packages=[
        "arduino_grpc",
        "arduino_grpc.cc",
        "arduino_grpc.cc.arduino",
        "arduino_grpc.cc.arduino.cli",
        "arduino_grpc.cc.arduino.cli.commands",
        "arduino_grpc.cc.arduino.cli.commands.v1",
    ],
    package_dir={
        "arduino_grpc": "arduino_grpc",
        "arduino_grpc.cc": "cc",
    },
    include_package_data=True,
    install_requires=[
        "googleapis-common-protos>=1.75.0",
        "grpcio>=1.80.0",
        "protobuf>=6.33.6",
    ],
    keywords=["arduino", "grpc", "stubs", "protobuf"],
)
