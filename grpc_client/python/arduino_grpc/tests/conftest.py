"""grpc_client/python/arduino_grpc/tests/conftest.py

Pytest fixtures and configuration for arduino_grpc tests.

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

from typing import Generator

import pytest

from .daemon_helper import DaemonCtx


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests (require real arduino-cli daemon)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: integration test requiring real arduino-cli daemon"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--integration"):
        return
    skip_integration = pytest.mark.skip(reason="use --integration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture(scope="module")
def daemon_url() -> Generator[str, None, None]:
    with DaemonCtx() as url:
        yield url
