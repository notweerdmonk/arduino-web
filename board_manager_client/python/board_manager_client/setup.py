"""board_manager_client/python/board_manager_client/setup.py

board-manager-client — PubSub client for the BoardManagerService.

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
    init_path = Path(__file__).parent / 'board_manager_client' / '__init__.py'
    with open(init_path) as f:
        for line in f:
            if line.startswith('__version__'):
                return ast.literal_eval(line.split('=')[1].strip())
    return '0.0.0'

setup(
    name="board-manager-client",
    version=_read_version(),
    description="PubSub client for BoardManagerService",
    long_description=open("README.md", encoding="utf-8").read(),
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

