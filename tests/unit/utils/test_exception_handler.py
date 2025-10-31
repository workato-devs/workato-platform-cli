"""Tests for exception handling utilities."""

from unittest.mock import MagicMock, patch

import pytest

from workato_platform_cli.cli.utils.exception_handler import (
    _extract_error_details,
    handle_api_exceptions,
    handle_cli_exceptions,
)
from workato_platform_cli.client.workato_api.exceptions import (
    ApiException,
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
        def successful_function() -> str:
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_api_exceptions_with_async_function(self) -> None:
        """Test decorator with async function."""

        @handle_api_exceptions
        async def async_successful_function() -> str:
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
        assert documented_function.__doc__ is not None
        assert "documentation" in documented_function.__doc__

    def test_handle_api_exceptions_with_parameters(self) -> None:
        """Test decorator works with functions that have parameters."""

        @handle_api_exceptions
        def function_with_params(param1: str, param2: str = "default") -> str:
            return f"{param1}-{param2}"

        result = function_with_params("test", param2="value")
        assert result == "test-value"

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_handles_generic_exception(
        self, mock_echo: MagicMock
    ) -> None:
        """Test that decorator handles API exceptions."""
        from workato_platform_cli.client.workato_api.exceptions import ApiException

        @handle_api_exceptions
        def failing_function() -> None:
            raise ApiException(status=500, reason="Test error")

        # Should handle exception and exit with code 1
        with pytest.raises(SystemExit) as exc_info:
            failing_function()
        assert exc_info.value.code == 1

        # Should have displayed error message
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_with_http_error(self, mock_echo: MagicMock) -> None:
        """Test handling of HTTP-like errors."""
        from workato_platform_cli.client.workato_api.exceptions import (
            UnauthorizedException,
        )

        @handle_api_exceptions
        def http_error_function() -> None:
            # Simulate an HTTP 401 error
            raise UnauthorizedException(status=401, reason="Unauthorized")

        # Should handle exception and exit with code 1
        with pytest.raises(SystemExit) as exc_info:
            http_error_function()
        assert exc_info.value.code == 1

        mock_echo.assert_called()

    @pytest.mark.parametrize(
        "exc_cls, expected",
        [
            (NotFoundException, "Resource not found"),
            (ConflictException, "Conflict detected"),
            (ServiceException, "Server error"),
        ],
    )
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_specific_http_errors(
        self,
        mock_echo: MagicMock,
        exc_cls: type[ApiException],
        expected: str,
    ) -> None:
        @handle_api_exceptions
        def failing() -> None:
            raise exc_cls(status=exc_cls.__name__, reason="error")

        with pytest.raises(SystemExit) as exc_info:
            failing()
        assert exc_info.value.code == 1
        assert any(expected in call.args[0] for call in mock_echo.call_args_list)

    def test_handle_api_exceptions_with_keyboard_interrupt(self) -> None:
        """Test handling of KeyboardInterrupt."""

        # Use unittest.mock to patch KeyboardInterrupt in the exception handler
        with patch(
            "workato_platform_cli.cli.utils.exception_handler.KeyboardInterrupt",
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

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_api_exceptions_error_formatting(self, mock_echo: MagicMock) -> None:
        """Test that error messages are formatted appropriately."""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        @handle_api_exceptions
        def error_function() -> None:
            # Use a proper Workato API exception that the handler actually catches
            raise BadRequestException(status=400, reason="Invalid request parameters")

        # The function should exit with code 1 when API exceptions are handled
        with pytest.raises(SystemExit) as exc_info:
            error_function()
        assert exc_info.value.code == 1

        # Should have called click.echo with formatted error
        mock_echo.assert_called()
        call_args = mock_echo.call_args[0]
        assert len(call_args) > 0

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_handles_forbidden_error(
        self,
        mock_echo: MagicMock,
    ) -> None:
        from workato_platform_cli.client.workato_api.exceptions import (
            ForbiddenException,
        )

        @handle_api_exceptions
        async def failing_async() -> None:
            raise ForbiddenException(status=403, reason="Forbidden")

        with pytest.raises(SystemExit) as exc_info:
            await failing_async()
        assert exc_info.value.code == 1
        mock_echo.assert_any_call("❌ Access forbidden")

    def test_extract_error_details_from_message(self) -> None:
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        exc = BadRequestException(status=400, body='{"message": "Invalid data"}')
        assert _extract_error_details(exc) == "Invalid data"

    def test_extract_error_details_from_errors_list(self) -> None:
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        body = '{"errors": ["Field is required"]}'
        exc = BadRequestException(status=400, body=body)
        assert _extract_error_details(exc) == "Validation error: Field is required"

    def test_extract_error_details_from_errors_dict(self) -> None:
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        body = '{"errors": {"field": ["must be unique"]}}'
        exc = BadRequestException(status=400, body=body)
        assert _extract_error_details(exc) == "field: must be unique"

    def test_extract_error_details_fallback_to_raw(self) -> None:
        from workato_platform_cli.client.workato_api.exceptions import ServiceException

        exc = ServiceException(status=500, body="<!DOCTYPE html>")
        assert _extract_error_details(exc).startswith("<!DOCTYPE html>")

    # Additional tests for missing sync exception handler coverage
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_bad_request(self, mock_echo: MagicMock) -> None:
        """Test sync handler with BadRequestException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        @handle_api_exceptions
        def sync_bad_request() -> None:
            raise BadRequestException(status=400, reason="Bad request")

        with pytest.raises(SystemExit) as exc_info:
            sync_bad_request()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_unprocessable_entity(self, mock_echo: MagicMock) -> None:
        """Test sync handler with UnprocessableEntityException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            UnprocessableEntityException,
        )

        @handle_api_exceptions
        def sync_unprocessable() -> None:
            raise UnprocessableEntityException(status=422, reason="Unprocessable")

        with pytest.raises(SystemExit) as exc_info:
            sync_unprocessable()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_unauthorized(self, mock_echo: MagicMock) -> None:
        """Test sync handler with UnauthorizedException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            UnauthorizedException,
        )

        @handle_api_exceptions
        def sync_unauthorized() -> None:
            raise UnauthorizedException(status=401, reason="Unauthorized")

        with pytest.raises(SystemExit) as exc_info:
            sync_unauthorized()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_forbidden(self, mock_echo: MagicMock) -> None:
        """Test sync handler with ForbiddenException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            ForbiddenException,
        )

        @handle_api_exceptions
        def sync_forbidden() -> None:
            raise ForbiddenException(status=403, reason="Forbidden")

        with pytest.raises(SystemExit) as exc_info:
            sync_forbidden()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_not_found(self, mock_echo: MagicMock) -> None:
        """Test sync handler with NotFoundException"""
        from workato_platform_cli.client.workato_api.exceptions import NotFoundException

        @handle_api_exceptions
        def sync_not_found() -> None:
            raise NotFoundException(status=404, reason="Not found")

        with pytest.raises(SystemExit) as exc_info:
            sync_not_found()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_conflict(self, mock_echo: MagicMock) -> None:
        """Test sync handler with ConflictException"""
        from workato_platform_cli.client.workato_api.exceptions import ConflictException

        @handle_api_exceptions
        def sync_conflict() -> None:
            raise ConflictException(status=409, reason="Conflict")

        with pytest.raises(SystemExit) as exc_info:
            sync_conflict()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_service_error(self, mock_echo: MagicMock) -> None:
        """Test sync handler with ServiceException"""
        from workato_platform_cli.client.workato_api.exceptions import ServiceException

        @handle_api_exceptions
        def sync_service_error() -> None:
            raise ServiceException(status=500, reason="Service error")

        with pytest.raises(SystemExit) as exc_info:
            sync_service_error()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_sync_handler_generic_api_error(self, mock_echo: MagicMock) -> None:
        """Test sync handler with generic ApiException"""
        from workato_platform_cli.client.workato_api.exceptions import ApiException

        @handle_api_exceptions
        def sync_generic_error() -> None:
            raise ApiException(status=418, reason="I'm a teapot")

        with pytest.raises(SystemExit) as exc_info:
            sync_generic_error()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    # Additional async tests for missing coverage
    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_bad_request(self, mock_echo: MagicMock) -> None:
        """Test async handler with BadRequestException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        @handle_api_exceptions
        async def async_bad_request() -> None:
            raise BadRequestException(status=400, reason="Bad request")

        with pytest.raises(SystemExit) as exc_info:
            await async_bad_request()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_unprocessable_entity(
        self, mock_echo: MagicMock
    ) -> None:
        """Test async handler with UnprocessableEntityException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            UnprocessableEntityException,
        )

        @handle_api_exceptions
        async def async_unprocessable() -> None:
            raise UnprocessableEntityException(status=422, reason="Unprocessable")

        with pytest.raises(SystemExit) as exc_info:
            await async_unprocessable()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_unauthorized(self, mock_echo: MagicMock) -> None:
        """Test async handler with UnauthorizedException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            UnauthorizedException,
        )

        @handle_api_exceptions
        async def async_unauthorized() -> None:
            raise UnauthorizedException(status=401, reason="Unauthorized")

        with pytest.raises(SystemExit) as exc_info:
            await async_unauthorized()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_not_found(self, mock_echo: MagicMock) -> None:
        """Test async handler with NotFoundException"""
        from workato_platform_cli.client.workato_api.exceptions import NotFoundException

        @handle_api_exceptions
        async def async_not_found() -> None:
            raise NotFoundException(status=404, reason="Not found")

        with pytest.raises(SystemExit) as exc_info:
            await async_not_found()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_conflict(self, mock_echo: MagicMock) -> None:
        """Test async handler with ConflictException"""
        from workato_platform_cli.client.workato_api.exceptions import ConflictException

        @handle_api_exceptions
        async def async_conflict() -> None:
            raise ConflictException(status=409, reason="Conflict")

        with pytest.raises(SystemExit) as exc_info:
            await async_conflict()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_service_error(self, mock_echo: MagicMock) -> None:
        """Test async handler with ServiceException"""
        from workato_platform_cli.client.workato_api.exceptions import ServiceException

        @handle_api_exceptions
        async def async_service_error() -> None:
            raise ServiceException(status=500, reason="Service error")

        with pytest.raises(SystemExit) as exc_info:
            await async_service_error()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handler_generic_api_error(self, mock_echo: MagicMock) -> None:
        """Test async handler with generic ApiException"""
        from workato_platform_cli.client.workato_api.exceptions import ApiException

        @handle_api_exceptions
        async def async_generic_error() -> None:
            raise ApiException(status=418, reason="I'm a teapot")

        with pytest.raises(SystemExit) as exc_info:
            await async_generic_error()
        assert exc_info.value.code == 1
        mock_echo.assert_called()

    def test_extract_error_details_invalid_json(self) -> None:
        """Test error details extraction with invalid JSON"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        exc = BadRequestException(status=400, body="invalid json {")
        # Should fallback to raw body when JSON parsing fails
        assert _extract_error_details(exc) == "invalid json {"

    def test_extract_error_details_no_message_or_errors(self) -> None:
        """Test error details extraction with valid JSON but no message/errors"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        exc = BadRequestException(status=400, body='{"other": "data"}')
        # Should fallback to raw body when no message/errors found
        assert _extract_error_details(exc) == '{"other": "data"}'

    def test_extract_error_details_empty_errors_list(self) -> None:
        """Test error details extraction with empty errors list"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        exc = BadRequestException(status=400, body='{"errors": []}')
        # Should fallback to raw body when errors list is empty
        assert _extract_error_details(exc) == '{"errors": []}'

    def test_extract_error_details_non_string_errors(self) -> None:
        """Test error details extraction with non-string errors"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        exc = BadRequestException(status=400, body='{"errors": [123, null]}')
        # Should handle non-string errors gracefully
        result = _extract_error_details(exc)
        assert "Validation error:" in result

    # JSON output mode tests
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_bad_request(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for BadRequestException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        # Mock Click context to return json output mode
        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def bad_request_json() -> None:
            raise BadRequestException(status=400, reason="Bad request")

        with pytest.raises(SystemExit) as exc_info:
            bad_request_json()
        assert exc_info.value.code == 1

        # Should output JSON
        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('{"status": "error"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_unauthorized(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for UnauthorizedException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            UnauthorizedException,
        )

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def unauthorized_json() -> None:
            raise UnauthorizedException(status=401, reason="Unauthorized")

        with pytest.raises(SystemExit) as exc_info:
            unauthorized_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "UNAUTHORIZED"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_forbidden(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for ForbiddenException"""
        from workato_platform_cli.client.workato_api.exceptions import (
            ForbiddenException,
        )

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def forbidden_json() -> None:
            raise ForbiddenException(status=403, reason="Forbidden")

        with pytest.raises(SystemExit) as exc_info:
            forbidden_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "FORBIDDEN"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_not_found(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for NotFoundException"""
        from workato_platform_cli.client.workato_api.exceptions import NotFoundException

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def not_found_json() -> None:
            raise NotFoundException(status=404, reason="Not found")

        with pytest.raises(SystemExit) as exc_info:
            not_found_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "NOT_FOUND"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_conflict(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for ConflictException"""
        from workato_platform_cli.client.workato_api.exceptions import ConflictException

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def conflict_json() -> None:
            raise ConflictException(status=409, reason="Conflict")

        with pytest.raises(SystemExit) as exc_info:
            conflict_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "CONFLICT"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_server_error(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for ServiceException"""
        from workato_platform_cli.client.workato_api.exceptions import ServiceException

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def server_error_json() -> None:
            raise ServiceException(status=500, reason="Server error")

        with pytest.raises(SystemExit) as exc_info:
            server_error_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "SERVER_ERROR"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_generic_api_error(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for generic ApiException"""
        from workato_platform_cli.client.workato_api.exceptions import ApiException

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def generic_error_json() -> None:
            raise ApiException(status=418, reason="I'm a teapot")

        with pytest.raises(SystemExit) as exc_info:
            generic_error_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "API_ERROR"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_with_error_details(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output includes error details from body"""
        from workato_platform_cli.client.workato_api.exceptions import (
            BadRequestException,
        )

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_api_exceptions
        def with_details_json() -> None:
            raise BadRequestException(
                status=400, body='{"message": "Field validation failed"}'
            )

        with pytest.raises(SystemExit) as exc_info:
            with_details_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any("Field validation failed" in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_get_output_mode_no_context(self, mock_get_context: MagicMock) -> None:
        """Test _get_output_mode returns 'table' when no context"""
        from workato_platform_cli.cli.utils.exception_handler import _get_output_mode

        mock_get_context.return_value = None

        result = _get_output_mode()
        assert result == "table"

    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_get_output_mode_no_params(self, mock_get_context: MagicMock) -> None:
        """Test _get_output_mode returns 'table' when context has no params"""
        from workato_platform_cli.cli.utils.exception_handler import _get_output_mode

        mock_ctx = MagicMock()
        del mock_ctx.params  # Remove params attribute
        mock_get_context.return_value = mock_ctx

        result = _get_output_mode()
        assert result == "table"


class TestCLIExceptionHandler:
    """Test the handle_cli_exceptions decorator for initialization and CLI errors."""

    def test_handle_cli_exceptions_decorator_exists(self) -> None:
        """Test that handle_cli_exceptions decorator can be imported."""
        assert handle_cli_exceptions is not None
        assert callable(handle_cli_exceptions)

    def test_handle_cli_exceptions_with_successful_function(self) -> None:
        """Test decorator with function that succeeds."""

        @handle_cli_exceptions
        def successful_function() -> str:
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_cli_exceptions_preserves_function_metadata(self) -> None:
        """Test that decorator preserves original function metadata."""

        @handle_cli_exceptions
        def documented_function() -> str:
            """This function has documentation."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ is not None
        assert "documentation" in documented_function.__doc__

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_cli_exceptions_with_value_error(self, mock_echo: MagicMock) -> None:
        """Test that decorator handles ValueError with generic handler."""

        @handle_cli_exceptions
        def failing_function() -> None:
            raise ValueError(
                "Could not resolve API credentials. Please run 'workato init'"
            )

        with pytest.raises(SystemExit) as exc_info:
            failing_function()
        assert exc_info.value.code == 1

        # Should display the error with the message from the exception
        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("ValueError" in arg for arg in call_args)
        assert any("workato init" in arg for arg in call_args)

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handle_cli_exceptions_with_value_error(
        self, mock_echo: MagicMock
    ) -> None:
        """Test async decorator handles ValueError with generic handler."""

        @handle_cli_exceptions
        async def async_failing() -> None:
            raise ValueError("API credentials not found")

        with pytest.raises(SystemExit) as exc_info:
            await async_failing()
        assert exc_info.value.code == 1

        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("ValueError" in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_cli_exceptions_with_network_error(
        self, mock_echo: MagicMock
    ) -> None:
        """Test that decorator handles network connection errors."""
        import aiohttp

        @handle_cli_exceptions
        def network_error_function() -> None:
            raise aiohttp.ClientConnectorError(
                connection_key=MagicMock(), os_error=OSError("Connection refused")
            )

        with pytest.raises(SystemExit) as exc_info:
            network_error_function()
        assert exc_info.value.code == 1

        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("Cannot connect to Workato API" in arg for arg in call_args)

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handle_cli_exceptions_with_timeout(
        self, mock_echo: MagicMock
    ) -> None:
        """Test async decorator handles timeout errors."""

        @handle_cli_exceptions
        async def timeout_function() -> None:
            raise TimeoutError()

        with pytest.raises(SystemExit) as exc_info:
            await timeout_function()
        assert exc_info.value.code == 1

        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("Request timed out" in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_cli_exceptions_with_ssl_error(self, mock_echo: MagicMock) -> None:
        """Test that decorator handles SSL certificate errors."""
        import ssl

        @handle_cli_exceptions
        def ssl_error_function() -> None:
            raise ssl.SSLError("certificate verify failed")

        with pytest.raises(SystemExit) as exc_info:
            ssl_error_function()
        assert exc_info.value.code == 1

        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("SSL certificate error" in arg for arg in call_args)

    # JSON output mode tests for CLI exceptions
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_initialization_error(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for ValueError with generic handler."""
        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_cli_exceptions
        def init_error_json() -> None:
            raise ValueError("Could not resolve API credentials")

        with pytest.raises(SystemExit) as exc_info:
            init_error_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "CLI_ERROR"' in arg for arg in call_args)
        assert any('"error_type": "ValueError"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_network_error(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for network connection errors."""
        import aiohttp

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_cli_exceptions
        def network_error_json() -> None:
            raise aiohttp.ClientConnectorError(
                connection_key=MagicMock(), os_error=OSError("Connection refused")
            )

        with pytest.raises(SystemExit) as exc_info:
            network_error_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "NETWORK_ERROR"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_timeout_error(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for timeout errors."""

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_cli_exceptions
        def timeout_error_json() -> None:
            raise TimeoutError()

        with pytest.raises(SystemExit) as exc_info:
            timeout_error_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "TIMEOUT_ERROR"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_ssl_error(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for SSL errors."""
        import ssl

        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_cli_exceptions
        def ssl_error_json() -> None:
            raise ssl.SSLError("certificate verify failed")

        with pytest.raises(SystemExit) as exc_info:
            ssl_error_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "SSL_ERROR"' in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_cli_exceptions_catches_non_init_value_error_generically(
        self, mock_echo: MagicMock
    ) -> None:
        """Test decorator catches non-init ValueError with generic handler."""

        @handle_cli_exceptions
        def non_init_value_error() -> None:
            raise ValueError("Some other validation error")

        with pytest.raises(SystemExit) as exc_info:
            non_init_value_error()
        assert exc_info.value.code == 1

        # Should be handled by generic error handler
        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("ValueError" in arg for arg in call_args)
        assert any("Some other validation error" in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    def test_handle_cli_exceptions_catches_unexpected_exception(
        self, mock_echo: MagicMock
    ) -> None:
        """Test that decorator catches unexpected exceptions with generic handler."""

        @handle_cli_exceptions
        def unexpected_error() -> None:
            raise RuntimeError("Something unexpected happened")

        with pytest.raises(SystemExit) as exc_info:
            unexpected_error()
        assert exc_info.value.code == 1

        # Should be handled by generic error handler
        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("RuntimeError" in arg for arg in call_args)
        assert any("Something unexpected happened" in arg for arg in call_args)

    @pytest.mark.asyncio
    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    async def test_async_handle_cli_exceptions_catches_unexpected_exception(
        self, mock_echo: MagicMock
    ) -> None:
        """Test async decorator catches unexpected exceptions with generic handler."""

        @handle_cli_exceptions
        async def async_unexpected_error() -> None:
            raise KeyError("Missing key")

        with pytest.raises(SystemExit) as exc_info:
            await async_unexpected_error()
        assert exc_info.value.code == 1

        # Should be handled by generic error handler
        call_args = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert any("KeyError" in arg for arg in call_args)
        assert any("Missing key" in arg for arg in call_args)

    @patch("workato_platform_cli.cli.utils.exception_handler.click.echo")
    @patch("workato_platform_cli.cli.utils.exception_handler.click.get_current_context")
    def test_json_output_generic_cli_error(
        self, mock_get_context: MagicMock, mock_echo: MagicMock
    ) -> None:
        """Test JSON output for generic CLI errors."""
        mock_ctx = MagicMock()
        mock_ctx.params = {"output_mode": "json"}
        mock_get_context.return_value = mock_ctx

        @handle_cli_exceptions
        def generic_error_json() -> None:
            raise RuntimeError("Unexpected error")

        with pytest.raises(SystemExit) as exc_info:
            generic_error_json()
        assert exc_info.value.code == 1

        call_args = [call[0][0] for call in mock_echo.call_args_list]
        assert any('"error_code": "CLI_ERROR"' in arg for arg in call_args)
        assert any('"error_type": "RuntimeError"' in arg for arg in call_args)
