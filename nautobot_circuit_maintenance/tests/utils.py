"""Test utilities."""


def assert_called_with_substring(mock, substring):
    """Helper function to check for substrings in mock called args."""
    for call_args in mock.call_args_list:
        if substring in call_args.kwargs.get("message", ""):
            return
    raise AssertionError(f"Expected substring '{substring}' not found in any call arguments.")
