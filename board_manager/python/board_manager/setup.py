"""
board-manager — Board Manager Service for the arduino-cli gRPC API.

The service speaks the arduino-cli gRPC protocol, owns the lifecycle of
the ``arduino-cli`` daemon, and forwards compile/upload/board-list
requests from the local dashboard to it. It can also be embedded in
tests via the in-process ``BoardManagerService`` class.

Local-source convention
-----------------------
The dependencies declared in ``pyproject.toml`` (``arduino-grpc``,
``grpcio``, ``protobuf``) use the standard PyPI package names so the
package also works with a normal ``pip install board-manager`` from a
remote index. In this monorepo the ``arduino-grpc`` dependency is
resolved through the local ``file://`` index declared in this
package's Pipfile (and the noxfile builds the matching wheel into
``<repo>/grpc_client/python/arduino_grpc/dist/``).
"""

from setuptools import setup, find_packages

setup(
    name="board-manager",
    version="0.1.0",
    description="Board Manager Service for Arduino gRPC",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="notweerdmonk",
    author_email="wrdmnk@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(include=["board_manager*"]),
    install_requires=[
        "arduino-grpc>=0.1.0",
        "grpcio>=1.80.0",
        "protobuf>=6.33.6",
        "tomli>=1.1.0",
    ],
    entry_points={
        "console_scripts": [
            "board-manager=board_manager.__main__:main",
        ],
    },
    keywords=["arduino", "grpc", "service", "board-detection"],
)
