"""Exception handler decorator for user-friendly error messages."""

import asyncio
import functools
import json

from collections.abc import Callable
from json import JSONDecodeError
from typing import Any, TypeVar, cast

import asyncclick as click

from workato_platform_cli.client.workato_api.exceptions import (
    ApiException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ServiceException,
    UnauthorizedException,
    UnprocessableEntityException,
)


F = TypeVar("F", bound=Callable[..., Any])


def handle_api_exceptions(func: F) -> F:
    """Decorator to handle workato_api exceptions with user-friendly messages.

    This decorator catches HTTP exceptions from the Workato API client and
    displays user-friendly error messages instead of raw stack traces.

    Supports both sync and async functions.

    Usage:
        @handle_api_exceptions
        async def my_command():
            # Your command logic here
            pass
    """

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except (BadRequestException, UnprocessableEntityException) as e:
                _handle_client_error(e)
                return
            except UnauthorizedException as e:
                _handle_auth_error(e)
                return
            except ForbiddenException as e:
                _handle_forbidden_error(e)
                return
            except NotFoundException as e:
                _handle_not_found_error(e)
                return
            except ConflictException as e:
                _handle_conflict_error(e)
                return
            except ServiceException as e:
                _handle_server_error(e)
                return
            except ApiException as e:
                _handle_generic_api_error(e)
                return

        return cast(F, async_wrapper)
    else:

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except (BadRequestException, UnprocessableEntityException) as e:
                _handle_client_error(e)
                return
            except UnauthorizedException as e:
                _handle_auth_error(e)
                return
            except ForbiddenException as e:
                _handle_forbidden_error(e)
                return
            except NotFoundException as e:
                _handle_not_found_error(e)
                return
            except ConflictException as e:
                _handle_conflict_error(e)
                return
            except ServiceException as e:
                _handle_server_error(e)
                return
            except ApiException as e:
                _handle_generic_api_error(e)
                return

        return cast(F, sync_wrapper)


def _get_output_mode() -> str:
    """Get the output mode from Click context."""
    ctx = click.get_current_context(silent=True)
    if ctx and hasattr(ctx, "params"):
        output_mode: str = ctx.params.get("output_mode", "table")
        return output_mode
    return "table"


def _handle_client_error(
    e: BadRequestException | UnprocessableEntityException,
) -> None:
    """Handle 400 Bad Request and 422 Unprocessable Entity errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_details = _extract_error_details(e)
        error_data = {
            "status": "error",
            "error": error_details
            or e.reason
            or "Bad request - check your input parameters",
            "error_code": "BAD_REQUEST"
            if isinstance(e, BadRequestException)
            else "UNPROCESSABLE_ENTITY",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Invalid request")

    # Try to extract error details from response body
    error_details = _extract_error_details(e)
    if error_details:
        click.echo(f"   {error_details}")
    else:
        click.echo(f"   {e.reason or 'Bad request - check your input parameters'}")

    click.echo("💡 Please check your input and try again")


def _handle_auth_error(e: UnauthorizedException) -> None:
    """Handle 401 Unauthorized errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": "Authentication failed - invalid or missing API token",
            "error_code": "UNAUTHORIZED",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Authentication failed")
    click.echo("   Your API token may be invalid")
    click.echo("💡 Please check your authentication:")
    click.echo("   • Verify your API token is correct")
    click.echo("   • Run 'workato profiles list' to check your profile")
    click.echo("   • Run 'workato profiles use' to update your credentials")


def _handle_forbidden_error(e: ForbiddenException) -> None:
    """Handle 403 Forbidden errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_details = _extract_error_details(e)
        error_data = {
            "status": "error",
            "error": error_details or "Access forbidden - insufficient permissions",
            "error_code": "FORBIDDEN",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Access forbidden")
    click.echo("   You don't have permission to perform this action")

    error_details = _extract_error_details(e)
    if error_details:
        click.echo(f"   {error_details}")

    click.echo("💡 Please check:")
    click.echo("   • Your account has the required permissions")
    click.echo("   • You're working in the correct workspace/folder")
    click.echo("   • The resource exists and is accessible to you")


def _handle_not_found_error(e: NotFoundException) -> None:
    """Handle 404 Not Found errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_details = _extract_error_details(e)
        error_data = {
            "status": "error",
            "error": error_details or "Resource not found",
            "error_code": "NOT_FOUND",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Resource not found")
    click.echo("   The requested resource could not be found")

    error_details = _extract_error_details(e)
    if error_details:
        click.echo(f"   {error_details}")

    click.echo("💡 Please check:")
    click.echo("   • The ID or name is correct")
    click.echo("   • The resource exists in your workspace")
    click.echo("   • You have permission to access the resource")


def _handle_conflict_error(e: ConflictException) -> None:
    """Handle 409 Conflict errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_details = _extract_error_details(e)
        error_data = {
            "status": "error",
            "error": error_details or "Request conflicts with current state",
            "error_code": "CONFLICT",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Conflict detected")
    click.echo("   The request conflicts with the current state")

    error_details = _extract_error_details(e)
    if error_details:
        click.echo(f"   {error_details}")

    click.echo("💡 This usually means:")
    click.echo("   • A resource with the same name already exists")
    click.echo("   • The resource is being used by another process")
    click.echo("   • There's a version conflict")


def _handle_server_error(e: ServiceException) -> None:
    """Handle 5xx Server errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": "Server error - Workato API is experiencing issues",
            "error_code": "SERVER_ERROR",
            "http_status": e.status,
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Server error")
    click.echo("   The Workato API is experiencing issues")
    click.echo(f"   Status: {e.status}")

    click.echo("💡 Please try:")
    click.echo("   • Wait a few moments and retry")
    click.echo("   • Check Workato status page for outages")
    click.echo("   • Contact support if the issue persists")


def _handle_generic_api_error(e: ApiException) -> None:
    """Handle other API errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_details = _extract_error_details(e)
        error_data = {
            "status": "error",
            "error": error_details or e.reason or "API error occurred",
            "error_code": "API_ERROR",
        }
        if e.status:
            error_data["http_status"] = e.status
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ API error occurred")

    if e.status:
        click.echo(f"   Status: {e.status}")
    if e.reason:
        click.echo(f"   Reason: {e.reason}")

    error_details = _extract_error_details(e)
    if error_details:
        click.echo(f"   Details: {error_details}")

    click.echo("💡 Please check your request and try again")


def _extract_error_details(e: ApiException) -> str:
    """Extract meaningful error details from API exception response."""
    if not (e.body or e.data):
        return ""

    try:
        # Try to parse JSON error response
        import json

        error_data = json.loads(e.body) if e.body else e.data

        # Common error message patterns
        if isinstance(error_data, dict):
            # Look for common error message fields
            for field in ["message", "error", "detail", "description"]:
                if field in error_data:
                    return str(error_data[field])

            # Look for validation errors
            if "errors" in error_data:
                errors = error_data["errors"]
                if isinstance(errors, list) and errors:
                    return f"Validation error: {errors[0]}"
                elif isinstance(errors, dict):
                    # Format field-specific errors
                    error_msgs = []
                    for field, msgs in errors.items():
                        if isinstance(msgs, list):
                            error_msgs.append(f"{field}: {', '.join(msgs)}")
                        else:
                            error_msgs.append(f"{field}: {msgs}")
                    return "; ".join(error_msgs)

    except JSONDecodeError:
        # If we can't parse the error, fall back to raw response
        pass

    # Return first 200 chars of raw response as fallback
    raw_response = str(e.body or e.data)
    return raw_response[:200] + ("..." if len(raw_response) > 200 else "")
