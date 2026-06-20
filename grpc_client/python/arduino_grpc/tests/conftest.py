"""pytest fixtures for arduino_grpc integration tests"""

from typing import Generator

import pytest

from .daemon_helper import DaemonCtx


@pytest.fixture(scope="module")
def daemon_url() -> Generator[str, None, None]:
    with DaemonCtx() as url:
        yield url
