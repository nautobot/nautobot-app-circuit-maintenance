# pylint: disable=logging-fstring-interpolation
"""Test utilities."""
from unittest.mock import Mock
import logging


def _add(level):
    def side_effect(*args, **kwargs):
        logging.warning(f"MockedLogger.{level} called with args: {args} and kwargs: {kwargs}")

    return Mock(side_effect=side_effect)


class MockedLogger:
    """Mocked logger for testing."""

    def __init__(self):
        self.debug = _add("debug")
        self.info = _add("info")
        self.warning = _add("warning")
        self.error = _add("error")


class MockedJob:
    """Mocked job for testing."""

    def __init__(self):
        self.job_result = Mock()
        self.logger = MockedLogger()
