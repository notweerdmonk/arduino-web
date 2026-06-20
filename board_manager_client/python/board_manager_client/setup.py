"""
board-manager-client — PubSub client for the BoardManagerService.

This package wraps the ``PubSub`` gRPC stream exposed by
``board-manager`` with a friendlier Python API. Consumers (notably
``arduino_dash`` and ``medminder_dash``) instantiate a
``PubSubClient`` to subscribe to command responses and board/port
events without having to deal with the raw gRPC stubs directly.

Local-source convention
-----------------------
The dependencies declared in ``pyproject.toml`` (``arduino-grpc``,
``board-manager``) use the standard PyPI package names so the package
also works with a normal ``pip install board-manager-client`` from a
remote index. In this monorepo the ``*-grpc`` and ``board-manager``
dependencies are resolved through the local ``file://`` index declared
in this package's Pipfile (and the noxfile builds the matching wheels
into the ``dist/`` subdirectories of the relevant packages).
"""

from setuptools import setup, find_packages

setup(
    name="board-manager-client",
    version="0.1.0",
    description="PubSub client for BoardManagerService",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="notweerdmonk",
    author_email="wrdmnk@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(include=["board_manager_client*"]),
    install_requires=[
        "arduino-grpc>=0.1.0",
        "board-manager>=0.1.0",
    ],
    keywords=["arduino", "pubsub", "client"],
)
