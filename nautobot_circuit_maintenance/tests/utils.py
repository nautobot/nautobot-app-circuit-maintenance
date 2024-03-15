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


def assert_called_with_substring(mock, substring):
    """Helper function to check for substrings in mock called args."""
    for call_args in mock.call_args_list:
        args, _ = call_args
        for arg in args:
            if substring in arg:
                return
    raise AssertionError(f"Expected substring '{substring}' not found in any call arguments.")
