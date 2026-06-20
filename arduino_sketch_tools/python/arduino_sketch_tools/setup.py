"""
arduino-sketch-tools — Flask extension for compile/upload to the
arduino-cli daemon via the BoardManagerService.

Provides ``ArduinoSketchTools``, a Flask extension that registers the
compile, upload, board-list, port-list and related routes, and exposes
helpers for the dashboard front-ends. It is consumed by both
``arduino_dash`` (board + compile dashboard) and ``medminder_dash``
(medicine reminder dashboard).

Local-source convention
-----------------------
The dependencies declared in ``pyproject.toml`` (``flask``,
``arduino-grpc``, ``board-manager``, ``board-manager-client``) use the
standard PyPI package names so the package also works with a normal
``pip install arduino-sketch-tools`` from a remote index. In this
monorepo the ``arduino-grpc`` / ``board-manager`` /
``board-manager-client`` dependencies are resolved through the local
``file://`` index declared in this package's Pipfile (and the noxfile
builds the matching wheels into the ``dist/`` subdirectories of the
relevant packages).
"""

from setuptools import setup, find_packages

setup(
    name="arduino-sketch-tools",
    version="0.1.0",
    description="Flask Extension for Arduino sketch compile/upload",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="notweerdmonk",
    author_email="wrdmnk@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(include=["arduino_sketch_tools*"]),
    install_requires=[
        "flask>=3.0.0",
        "arduino-grpc>=0.1.0",
        "board-manager>=0.1.0",
        "board-manager-client>=0.1.0",
    ],
    package_data={
        "arduino_sketch_tools": [
            "templates/**/*",
            "static/**/*",
            "config/**/*",
        ],
    },
    include_package_data=True,
    keywords=["arduino", "flask-extension", "compile", "upload"],
)
