"""arduino_sketch_tools/python/arduino_sketch_tools/setup.py

arduino-sketch-tools — Flask extension for compile/upload to the

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

from arduino_sketch_tools import __version__

from setuptools import setup, find_packages

setup(
    name="arduino-sketch-tools",
    version=__version__,
    description="Flask Extension for Arduino sketch compile/upload",
    long_description=open("README.md", encoding="utf-8").read(),
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
        ],
    },
    include_package_data=True,
    keywords=["arduino", "flask-extension", "compile", "upload"],
)

