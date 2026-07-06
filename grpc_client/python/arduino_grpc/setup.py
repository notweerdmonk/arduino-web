"""grpc_client/python/arduino_grpc/setup.py

arduino-grpc — gRPC client stubs for the arduino-cli gRPC service.

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
from setuptools import setup


def _read_version():
    init_path = Path(__file__).parent / "arduino_grpc" / "__init__.py"
    with open(init_path) as f:
        for line in f:
            if line.startswith("__version__"):
                return ast.literal_eval(line.split("=")[1].strip())
    return "0.0.0"


setup(
    name="arduino-grpc",
    version=_read_version(),
    description="gRPC client stubs for arduino-cli",
    long_description=open("README.md", encoding="utf-8").read(),
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
