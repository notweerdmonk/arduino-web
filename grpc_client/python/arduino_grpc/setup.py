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

