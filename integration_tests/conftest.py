"""
Contains fixture to all tests
"""

from typing import Any
import toml


def integration_test_db_config() -> dict[str, Any]:
    return toml.load("integration_tests/config.toml")["database"]
