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

