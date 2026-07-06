"""arduino_dash/python/arduino_dash/setup.py

arduino-dash — Web GUI for the arduino-cli Board Manager.

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

import ast
from pathlib import Path

from setuptools import find_packages, setup


def _read_version():
    init_path = Path(__file__).parent / 'arduino_dash' / '__init__.py'
    with open(init_path) as f:
        for line in f:
            if line.startswith('__version__'):
                return ast.literal_eval(line.split('=')[1].strip())
    return '0.0.0'

setup(
    name="arduino-dash",
    version=_read_version(),
    description="Web GUI for Arduino gRPC Board Manager",
    long_description=open("README.md", encoding="utf-8").read(),
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
        "simple-websocket>=1.0.0",
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

