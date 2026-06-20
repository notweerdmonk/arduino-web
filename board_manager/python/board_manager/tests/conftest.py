"""pytest configuration: skip integration tests unless --integration flag is passed"""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests (require real arduino-cli daemon)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: integration test requiring real arduino-cli daemon")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--integration"):
        return
    skip_integration = pytest.mark.skip(reason="use --integration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
