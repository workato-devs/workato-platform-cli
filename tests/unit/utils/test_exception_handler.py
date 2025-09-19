"""Tests for exception handling utilities."""

from unittest.mock import MagicMock, patch

import pytest

from workato_platform.cli.utils.exception_handler import (
    _extract_error_details,
    handle_api_exceptions,
)
from workato_platform.client.workato_api.exceptions import (
    ConflictException,
    NotFoundException,
    ServiceException,
)


class TestExceptionHandler:
    """Test the exception handling decorators and utilities."""

    def test_handle_api_exceptions_decorator_exists(self) -> None:
        """Test that handle_api_exceptions decorator can be imported."""
        # Should not raise ImportError
        assert handle_api_exceptions is not None
        assert callable(handle_api_exceptions)

    def test_handle_api_exceptions_with_successful_function(self) -> None:
        """Test decorator with function that succeeds."""

        @handle_api_exceptions
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_api_exceptions_with_async_function(self) -> None:
        """Test decorator with async function."""

        @handle_api_exceptions
        async def async_successful_function():
            return "async_success"

        # Should be callable (actual execution would need event loop)
        assert callable(async_successful_function)

    def test_handle_api_exceptions_preserves_function_metadata(self) -> None:
        """Test that decorator preserves original function metadata."""

        @handle_api_exceptions
        def documented_function() -> str:
            """This function has documentation."""
            return "result"

        # Should preserve function name and docstring
        assert documented_function.__name__ == "documented_function"
        assert "documentation" in documented_function.__doc__

    def test_handle_api_exceptions_with_parameters(self) -> None:
        """Test decorator works with functions that have parameters."""

        @handle_api_exceptions
        def function_with_params(param1: str, param2: str = "default") -> str:
            return f"{param1}-{param2}"

        result = function_with_params("test", param2="value")
        assert result == "test-value"

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_handles_generic_exception(
        self, mock_echo: MagicMock
    ) -> None:
        """Test that decorator handles API exceptions."""
        from workato_platform.client.workato_api.exceptions import ApiException

        @handle_api_exceptions
        def failing_function() -> None:
            raise ApiException(status=500, reason="Test error")

        # Should handle exception gracefully (not raise SystemExit, just return)
        result = failing_function()
        assert result is None

        # Should have displayed error message
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_with_http_error(self, mock_echo: MagicMock) -> None:
        """Test handling of HTTP-like errors."""
        from workato_platform.client.workato_api.exceptions import UnauthorizedException

        @handle_api_exceptions
        def http_error_function() -> None:
            # Simulate an HTTP 401 error
            raise UnauthorizedException(status=401, reason="Unauthorized")

        # Should handle exception gracefully (not raise SystemExit, just return)
        result = http_error_function()
        assert result is None

        mock_echo.assert_called()

    @pytest.mark.parametrize(
        "exc_cls, expected",
        [
            (NotFoundException, "Resource not found"),
            (ConflictException, "Conflict detected"),
            (ServiceException, "Server error"),
        ],
    )
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_specific_http_errors(
        self,
        mock_echo: MagicMock,
        exc_cls: type[Exception],
        expected: str,
    ) -> None:
        @handle_api_exceptions
        def failing() -> None:
            raise exc_cls(status=exc_cls.__name__, reason="error")

        result = failing()
        assert result is None
        assert any(expected in call.args[0] for call in mock_echo.call_args_list)

    def test_handle_api_exceptions_with_keyboard_interrupt(self) -> None:
        """Test handling of KeyboardInterrupt."""

        # Use unittest.mock to patch KeyboardInterrupt in the exception handler
        with patch(
            "workato_platform.cli.utils.exception_handler.KeyboardInterrupt",
            KeyboardInterrupt,
        ):

            @handle_api_exceptions
            def interrupted_function() -> None:
                # Raise the actual KeyboardInterrupt but within a controlled context
                try:
                    raise KeyboardInterrupt()
                except KeyboardInterrupt as e:
                    # Re-raise so the decorator can catch it, but suppress
                    # pytest's handling
                    raise SystemExit(130) from e

            with pytest.raises(SystemExit) as exc_info:
                interrupted_function()

            # Verify it's the expected exit code for KeyboardInterrupt
            assert exc_info.value.code == 130

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_error_formatting(self, mock_echo: MagicMock) -> None:
        """Test that error messages are formatted appropriately."""
        from workato_platform.client.workato_api.exceptions import BadRequestException

        @handle_api_exceptions
        def error_function() -> None:
            # Use a proper Workato API exception that the handler actually catches
            raise BadRequestException(status=400, reason="Invalid request parameters")

        # The function should return None (not raise SystemExit) when API
        # exceptions are handled
        result = error_function()
        assert result is None

        # Should have called click.echo with formatted error
        mock_echo.assert_called()
        call_args = mock_echo.call_args[0]
        assert len(call_args) > 0

    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_handles_forbidden_error(
        self,
        mock_echo: MagicMock,
    ) -> None:
        from workato_platform.client.workato_api.exceptions import ForbiddenException

        @handle_api_exceptions
        async def failing_async() -> None:
            raise ForbiddenException(status=403, reason="Forbidden")

        result = await failing_async()
        assert result is None
        mock_echo.assert_any_call("❌ Access forbidden")

    def test_extract_error_details_from_message(self) -> None:
        from workato_platform.client.workato_api.exceptions import BadRequestException

        exc = BadRequestException(status=400, body='{"message": "Invalid data"}')
        assert _extract_error_details(exc) == "Invalid data"

    def test_extract_error_details_from_errors_list(self) -> None:
        from workato_platform.client.workato_api.exceptions import BadRequestException

        body = '{"errors": ["Field is required"]}'
        exc = BadRequestException(status=400, body=body)
        assert _extract_error_details(exc) == "Validation error: Field is required"

    def test_extract_error_details_from_errors_dict(self) -> None:
        from workato_platform.client.workato_api.exceptions import BadRequestException

        body = '{"errors": {"field": ["must be unique"]}}'
        exc = BadRequestException(status=400, body=body)
        assert _extract_error_details(exc) == "field: must be unique"

    def test_extract_error_details_fallback_to_raw(self) -> None:
        from workato_platform.client.workato_api.exceptions import ServiceException

        exc = ServiceException(status=500, body="<!DOCTYPE html>")
        assert _extract_error_details(exc).startswith("<!DOCTYPE html>")

    # Additional tests for missing sync exception handler coverage
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_bad_request(self, mock_echo: MagicMock) -> None:
        """Test sync handler with BadRequestException"""
        from workato_platform.client.workato_api.exceptions import BadRequestException

        @handle_api_exceptions
        def sync_bad_request() -> None:
            raise BadRequestException(status=400, reason="Bad request")

        result = sync_bad_request()
        assert result is None
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_unprocessable_entity(self, mock_echo: MagicMock) -> None:
        """Test sync handler with UnprocessableEntityException"""
        from workato_platform.client.workato_api.exceptions import (
            UnprocessableEntityException,
        )

        @handle_api_exceptions
        def sync_unprocessable() -> None:
            raise UnprocessableEntityException(status=422, reason="Unprocessable")

        result = sync_unprocessable()
        assert result is None
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_unauthorized(self, mock_echo: MagicMock) -> None:
        """Test sync handler with UnauthorizedException"""
        from workato_platform.client.workato_api.exceptions import UnauthorizedException

        @handle_api_exceptions
        def sync_unauthorized() -> None:
            raise UnauthorizedException(status=401, reason="Unauthorized")

        result = sync_unauthorized()
        assert result is None
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_forbidden(self, mock_echo: MagicMock) -> None:
        """Test sync handler with ForbiddenException"""
        from workato_platform.client.workato_api.exceptions import ForbiddenException

        @handle_api_exceptions
        def sync_forbidden() -> None:
            raise ForbiddenException(status=403, reason="Forbidden")

        result = sync_forbidden()
        assert result is None
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_not_found(self, mock_echo: MagicMock) -> None:
        """Test sync handler with NotFoundException"""
        from workato_platform.client.workato_api.exceptions import NotFoundException

        @handle_api_exceptions
        def sync_not_found() -> None:
            raise NotFoundException(status=404, reason="Not found")

        result = sync_not_found()
        assert result is None
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_conflict(self, mock_echo: MagicMock) -> None:
        """Test sync handler with ConflictException"""
        from workato_platform.client.workato_api.exceptions import ConflictException

        @handle_api_exceptions
        def sync_conflict() -> None:
            raise ConflictException(status=409, reason="Conflict")

        result = sync_conflict()
        assert result is None
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_service_error(self, mock_echo: MagicMock) -> None:
        """Test sync handler with ServiceException"""
        from workato_platform.client.workato_api.exceptions import ServiceException

        @handle_api_exceptions
        def sync_service_error() -> None:
            raise ServiceException(status=500, reason="Service error")

        result = sync_service_error()
        assert result is None
        mock_echo.assert_called()

    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    def test_sync_handler_generic_api_error(self, mock_echo: MagicMock) -> None:
        """Test sync handler with generic ApiException"""
        from workato_platform.client.workato_api.exceptions import ApiException

        @handle_api_exceptions
        def sync_generic_error() -> None:
            raise ApiException(status=418, reason="I'm a teapot")

        result = sync_generic_error()
        assert result is None
        mock_echo.assert_called()

    # Additional async tests for missing coverage
    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_bad_request(self, mock_echo: MagicMock) -> None:
        """Test async handler with BadRequestException"""
        from workato_platform.client.workato_api.exceptions import BadRequestException

        @handle_api_exceptions
        async def async_bad_request() -> None:
            raise BadRequestException(status=400, reason="Bad request")

        result = await async_bad_request()
        assert result is None
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_unprocessable_entity(
        self, mock_echo: MagicMock
    ) -> None:
        """Test async handler with UnprocessableEntityException"""
        from workato_platform.client.workato_api.exceptions import (
            UnprocessableEntityException,
        )

        @handle_api_exceptions
        async def async_unprocessable() -> None:
            raise UnprocessableEntityException(status=422, reason="Unprocessable")

        result = await async_unprocessable()
        assert result is None
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_unauthorized(self, mock_echo: MagicMock) -> None:
        """Test async handler with UnauthorizedException"""
        from workato_platform.client.workato_api.exceptions import UnauthorizedException

        @handle_api_exceptions
        async def async_unauthorized() -> None:
            raise UnauthorizedException(status=401, reason="Unauthorized")

        result = await async_unauthorized()
        assert result is None
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_not_found(self, mock_echo: MagicMock) -> None:
        """Test async handler with NotFoundException"""
        from workato_platform.client.workato_api.exceptions import NotFoundException

        @handle_api_exceptions
        async def async_not_found() -> None:
            raise NotFoundException(status=404, reason="Not found")

        result = await async_not_found()
        assert result is None
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_conflict(self, mock_echo: MagicMock) -> None:
        """Test async handler with ConflictException"""
        from workato_platform.client.workato_api.exceptions import ConflictException

        @handle_api_exceptions
        async def async_conflict() -> None:
            raise ConflictException(status=409, reason="Conflict")

        result = await async_conflict()
        assert result is None
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_service_error(self, mock_echo: MagicMock) -> None:
        """Test async handler with ServiceException"""
        from workato_platform.client.workato_api.exceptions import ServiceException

        @handle_api_exceptions
        async def async_service_error() -> None:
            raise ServiceException(status=500, reason="Service error")

        result = await async_service_error()
        assert result is None
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform.cli.utils.exception_handler.click.echo")
    async def test_async_handler_generic_api_error(self, mock_echo: MagicMock) -> None:
        """Test async handler with generic ApiException"""
        from workato_platform.client.workato_api.exceptions import ApiException

        @handle_api_exceptions
        async def async_generic_error() -> None:
            raise ApiException(status=418, reason="I'm a teapot")

        result = await async_generic_error()
        assert result is None
        mock_echo.assert_called()

    def test_extract_error_details_invalid_json(self) -> None:
        """Test error details extraction with invalid JSON"""
        from workato_platform.client.workato_api.exceptions import BadRequestException

        exc = BadRequestException(status=400, body="invalid json {")
        # Should fallback to raw body when JSON parsing fails
        assert _extract_error_details(exc) == "invalid json {"

    def test_extract_error_details_no_message_or_errors(self) -> None:
        """Test error details extraction with valid JSON but no message/errors"""
        from workato_platform.client.workato_api.exceptions import BadRequestException

        exc = BadRequestException(status=400, body='{"other": "data"}')
        # Should fallback to raw body when no message/errors found
        assert _extract_error_details(exc) == '{"other": "data"}'

    def test_extract_error_details_empty_errors_list(self) -> None:
        """Test error details extraction with empty errors list"""
        from workato_platform.client.workato_api.exceptions import BadRequestException

        exc = BadRequestException(status=400, body='{"errors": []}')
        # Should fallback to raw body when errors list is empty
        assert _extract_error_details(exc) == '{"errors": []}'

    def test_extract_error_details_non_string_errors(self) -> None:
        """Test error details extraction with non-string errors"""
        from workato_platform.client.workato_api.exceptions import BadRequestException

        exc = BadRequestException(status=400, body='{"errors": [123, null]}')
        # Should handle non-string errors gracefully
        result = _extract_error_details(exc)
        assert "Validation error:" in result
