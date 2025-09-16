"""Tests for exception handling utilities."""

from unittest.mock import patch

import pytest

from workato_platform.cli.utils.exception_handler import handle_api_exceptions


class TestExceptionHandler:
    """Test the exception handling decorators and utilities."""

    def test_handle_api_exceptions_decorator_exists(self):
        """Test that handle_api_exceptions decorator can be imported."""
        # Should not raise ImportError
        assert handle_api_exceptions is not None
        assert callable(handle_api_exceptions)

    def test_handle_api_exceptions_with_successful_function(self):
        """Test decorator with function that succeeds."""

        @handle_api_exceptions
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_api_exceptions_with_async_function(self):
        """Test decorator with async function."""

        @handle_api_exceptions
        async def async_successful_function():
            return "async_success"

        # Should be callable (actual execution would need event loop)
        assert callable(async_successful_function)

    def test_handle_api_exceptions_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""

        @handle_api_exceptions
        def documented_function():
            """This function has documentation."""
            return "result"

        # Should preserve function name and docstring
        assert documented_function.__name__ == "documented_function"
        assert "documentation" in documented_function.__doc__

    def test_handle_api_exceptions_with_parameters(self):
        """Test decorator works with functions that have parameters."""

        @handle_api_exceptions
        def function_with_params(param1, param2="default"):
            return f"{param1}-{param2}"

        result = function_with_params("test", param2="value")
        assert result == "test-value"

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_handles_generic_exception(self, mock_echo):
        """Test that decorator handles API exceptions."""
        from workato_platform.client.workato_api.exceptions import ApiException

        @handle_api_exceptions
        def failing_function():
            raise ApiException(status=500, reason="Test error")

        # Should handle exception gracefully (not raise SystemExit, just return)
        result = failing_function()
        assert result is None

        # Should have displayed error message
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_with_http_error(self, mock_echo):
        """Test handling of HTTP-like errors."""
        from workato_platform.client.workato_api.exceptions import UnauthorizedException

        @handle_api_exceptions
        def http_error_function():
            # Simulate an HTTP 401 error
            raise UnauthorizedException(status=401, reason="Unauthorized")

        # Should handle exception gracefully (not raise SystemExit, just return)
        result = http_error_function()
        assert result is None

        mock_echo.assert_called()

    def test_handle_api_exceptions_with_keyboard_interrupt(self):
        """Test handling of KeyboardInterrupt."""

        @handle_api_exceptions
        def interrupted_function():
            raise KeyboardInterrupt()

        with pytest.raises(SystemExit):
            interrupted_function()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_error_formatting(self, mock_echo):
        """Test that error messages are formatted appropriately."""

        @handle_api_exceptions
        def error_function():
            raise ConnectionError("Failed to connect to API")

        with pytest.raises(SystemExit):
            error_function()

        # Should have called click.echo with formatted error
        mock_echo.assert_called()
        call_args = mock_echo.call_args[0]
        assert len(call_args) > 0
        assert (
            "error" in str(call_args[0]).lower()
            or "failed" in str(call_args[0]).lower()
        )
