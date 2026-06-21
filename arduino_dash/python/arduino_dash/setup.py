"""
arduino-dash — Web GUI for the arduino-cli Board Manager.

A small Flask app that renders a list of connected boards and ports,
shows compile / upload status, and exposes a WebSocket channel for
live updates from the BoardManagerService. It is the dashboard that
``scripts/arduino-dash`` (or ``python -m arduino_dash``) starts.

Local-source convention
-----------------------
The dependencies declared in ``pyproject.toml`` (``flask``,
``flask-sock``, ``arduino-grpc``, ``board-manager``,
``board-manager-client``, ``arduino-sketch-tools``, ``gunicorn``) use
the standard PyPI package names so the package also works with a
normal ``pip install arduino-dash`` from a remote index. In this
monorepo the ``arduino-grpc`` / ``board-manager`` /
``board-manager-client`` / ``arduino-sketch-tools`` dependencies are
resolved through the local ``file://`` index declared in this
package's Pipfile (and the noxfile builds the matching wheels into
the ``dist/`` subdirectories of the relevant packages).
"""

from setuptools import setup, find_packages

setup(
    name="arduino-dash",
    version="0.1.0",
    description="Web GUI for Arduino gRPC Board Manager",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="notweerdmonk",
    author_email="wrdmnk@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(include=["arduino_dash*"]),
    install_requires=[
        "flask>=3.0.0",
        "flask-sock>=0.7.0",
        "arduino-grpc>=0.1.0",
        "board-manager>=0.1.0",
        "board-manager-client>=0.1.0",
        "arduino-sketch-tools>=0.1.0",
        "gunicorn>=20.0",
    ],
    entry_points={
        "console_scripts": [
            "arduino-dash=arduino_dash.__main__:main",
        ],
    },
    package_data={
        "arduino_dash": [
            "templates/**/*",
            "static/**/*",
        ],
    },
    include_package_data=True,
    keywords=["arduino", "dashboard", "web-gui", "flask"],
)
