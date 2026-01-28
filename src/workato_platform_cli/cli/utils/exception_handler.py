"""Exception handler decorator for user-friendly error messages."""

import asyncio
import functools
import json
import ssl

from collections.abc import Callable
from json import JSONDecodeError
from typing import Any, TypeVar, cast

import aiohttp
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
                raise SystemExit(1) from None
            except UnauthorizedException as e:
                _handle_auth_error(e)
                raise SystemExit(1) from None
            except ForbiddenException as e:
                _handle_forbidden_error(e)
                raise SystemExit(1) from None
            except NotFoundException as e:
                _handle_not_found_error(e)
                raise SystemExit(1) from None
            except ConflictException as e:
                _handle_conflict_error(e)
                raise SystemExit(1) from None
            except ServiceException as e:
                _handle_server_error(e)
                raise SystemExit(1) from None
            except ApiException as e:
                _handle_generic_api_error(e)
                raise SystemExit(1) from None

        return cast(F, async_wrapper)
    else:

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except (BadRequestException, UnprocessableEntityException) as e:
                _handle_client_error(e)
                raise SystemExit(1) from None
            except UnauthorizedException as e:
                _handle_auth_error(e)
                raise SystemExit(1) from None
            except ForbiddenException as e:
                _handle_forbidden_error(e)
                raise SystemExit(1) from None
            except NotFoundException as e:
                _handle_not_found_error(e)
                raise SystemExit(1) from None
            except ConflictException as e:
                _handle_conflict_error(e)
                raise SystemExit(1) from None
            except ServiceException as e:
                _handle_server_error(e)
                raise SystemExit(1) from None
            except ApiException as e:
                _handle_generic_api_error(e)
                raise SystemExit(1) from None

        return cast(F, sync_wrapper)


def handle_cli_exceptions(func: F) -> F:
    """Handle CLI initialization and network errors with friendly messages.

    This decorator catches errors that occur during dependency injection and CLI
    initialization, such as missing credentials, network failures, and configuration
    errors. It should be placed above @inject in the decorator stack.

    Supports both sync and async functions.

    Usage:
        @click.command()
        @handle_cli_exceptions
        @inject
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
            except (
                aiohttp.ClientConnectorError,
                aiohttp.ClientConnectionError,
            ) as e:
                _handle_network_error(e)
                raise SystemExit(1) from None
            except TimeoutError as e:
                _handle_timeout_error(e)
                raise SystemExit(1) from None
            except aiohttp.ServerDisconnectedError as e:
                _handle_server_disconnect_error(e)
                raise SystemExit(1) from None
            except (aiohttp.ClientSSLError, ssl.SSLError) as e:
                _handle_ssl_error(e)
                raise SystemExit(1) from None
            except click.Abort:
                # Let Click handle Abort - don't catch it
                raise
            except click.ClickException as e:
                # Handle ClickException specifically - show message without error type
                _handle_click_exception(e)
                raise SystemExit(1) from None
            except Exception as e:
                # Catch-all for any exceptions during initialization
                _handle_generic_cli_error(e)
                raise SystemExit(1) from None

        return cast(F, async_wrapper)
    else:

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except (
                aiohttp.ClientConnectorError,
                aiohttp.ClientConnectionError,
            ) as e:
                _handle_network_error(e)
                raise SystemExit(1) from None
            except TimeoutError as e:
                _handle_timeout_error(e)
                raise SystemExit(1) from None
            except aiohttp.ServerDisconnectedError as e:
                _handle_server_disconnect_error(e)
                raise SystemExit(1) from None
            except (aiohttp.ClientSSLError, ssl.SSLError) as e:
                _handle_ssl_error(e)
                raise SystemExit(1) from None
            except click.Abort:
                # Let Click handle Abort - don't catch it
                raise
            except click.ClickException as e:
                # Handle ClickException specifically - show message without error type
                _handle_click_exception(e)
                raise SystemExit(1) from None
            except Exception as e:
                # Catch-all for any exceptions during initialization
                _handle_generic_cli_error(e)
                raise SystemExit(1) from None

        return cast(F, sync_wrapper)


def _get_output_mode() -> str:
    """Get the output mode from Click context."""
    ctx = click.get_current_context(silent=True)
    if ctx and hasattr(ctx, "params"):
        output_mode: str = ctx.params.get("output_mode", "table")
        return output_mode
    return "table"


def _get_required_permissions(ctx: click.Context) -> list[str]:
    """Get required Workato permissions for a CLI command.

    Args:
        ctx: Click context object

    Returns:
        List of required permission strings
    """
    # Map CLI command names to required Workato permissions
    permission_map = {
        "init": [
            "Projects → Projects & folders",
            "Projects → Connections",
            "Projects → Recipes",
            "Projects → Recipe Versions",
            "Projects → Recipe lifecycle management",
            "Projects → Export manifests",
            "Tools → Collections & endpoints",
            "Admin → Workspace details",
        ],
        "recipes": [
            "Projects → Export manifests",
            "Projects → Recipes",
        ],
        "pull": [
            "Projects → Recipe lifecycle management",
            "Projects → Export manifests",
        ],
        "push": [
            "Projects → Recipe lifecycle management",
        ],
        "api-clients": [
            "Tools → Clients & access profiles",
        ],
        "api-collections": [
            "Tools → Collections & endpoints",
        ],
        "assets": [
            "Projects → Export manifests",
        ],
        "connections": [
            "Projects → Connections",
        ],
        "connectors": [
            "Tools → Connector SDKs",
            "Tools → Connectors",
        ],
        "data-tables": [
            "Tools → Data tables",
        ],
        "properties": [
            "Tools → Environment properties",
        ],
        "workspace": [
            "Admin → Workspace details",
        ],
    }

    # Get command name from context
    # For nested commands like "workato recipes list", check parent context
    command_name = ctx.info_name
    if ctx.parent and ctx.parent.info_name and ctx.parent.info_name not in ("workato",):
        # If parent is not root, use parent's name (the command group)
        command_name = ctx.parent.info_name

    if not command_name:
        return []

    return permission_map.get(command_name, [])


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
    """Handle 401 Unauthorized errors.

    For 'workato init' command: Shows both authentication and authorization
    possibilities since we cannot distinguish between them at this stage.

    For other commands: Shows only authorization error, assuming the token
    was already validated during initialization. A 401 error is treated as
    missing permissions.

    TODO: This is a temporary solution. The API should return distinct error
    codes for authentication vs authorization failures. Track progress at:
    https://github.com/workato-devs/workato-platform-cli-issues/issues/106
    """
    output_mode = _get_output_mode()
    ctx = click.get_current_context(silent=True)

    # Check if this is the init command (top-level init, not subcommands)
    is_init_command = False
    if ctx and ctx.command:
        is_init_command = (
            ctx.command.name == "init"
            and ctx.parent
            and ctx.parent.info_name == "workato"
        )

    # Get required permissions for this command
    required_permissions = []
    if ctx:
        required_permissions = _get_required_permissions(ctx)

    if output_mode == "json":
        if is_init_command:
            error_msg = (
                "Authentication failed - invalid or missing API token "
                "or insufficient permissions"
            )
        else:
            error_msg = "Authorization failed - insufficient permissions"

        error_data = {
            "status": "error",
            "error": error_msg,
            "error_code": "UNAUTHORIZED",
        }
        click.echo(json.dumps(error_data))
        return

    command_info = f" (command: {ctx.command_path})" if ctx else ""

    if is_init_command:
        # For init command: Show both possibilities since we can't distinguish
        click.echo(f"❌ Authentication failed{command_info}")
        click.echo("   This could be due to:")
        click.echo("   • Invalid or expired API token")
        click.echo("   • API client lacking required permissions")
        click.echo()

        # Show required permissions if available
        if required_permissions:
            click.echo("🔐 Required permissions for this command:")
            for permission in required_permissions:
                click.echo(f"   • {permission}")
            click.echo()

        click.echo("🔧 To resolve:")
        click.echo("   • Verify your API token is correct")
        click.echo(
            "   • Ensure your API client has all required permissions "
            "in Workato"
        )
        click.echo("   • Run 'workato profiles list' to check your profile")
        click.echo(
            "   • Run 'workato profiles use' to update your credentials"
        )
        click.echo()
        click.echo("📚 Learn more about authentication and permissions")
        click.echo("   https://docs.workato.com/en/platform-cli.html#authentication")
    else:
        # For non-init commands: Show only authorization error
        # Assumption: Token validity was already verified during init when
        # the profile was created. If they're using an existing profile and
        # getting 401, it's an authorization issue (missing permissions).
        click.echo(f"❌ Authorization failed{command_info}")
        click.echo(
            "   Your API client lacks the required permissions for "
            "this operation"
        )
        click.echo()

        # Show required permissions if available
        if required_permissions:
            click.echo("🔐 Required permissions for this command:")
            for permission in required_permissions:
                click.echo(f"   • {permission}")
            click.echo()

        click.echo("🔧 To resolve:")
        click.echo("   • Update your API client permissions in Workato")
        click.echo("   • Ensure the permissions listed above are enabled")
        click.echo(
            "   • Run 'workato profiles use' if you need to switch to "
            "a different API client"
        )
        click.echo()
        click.echo("📚 Learn more about permissions required for API client")
        click.echo("   https://docs.workato.com/en/platform-cli.html#authentication")


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


def _handle_network_error(
    e: aiohttp.ClientConnectorError | aiohttp.ClientConnectionError,
) -> None:
    """Handle network connection errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": "Cannot connect to Workato API",
            "error_code": "NETWORK_ERROR",
            "details": str(e),
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Cannot connect to Workato API")
    click.echo(f"   {str(e)}")
    click.echo("💡 Please check:")
    click.echo("   • Your internet connection is working")
    click.echo("   • The Workato API is accessible")
    click.echo("   • Your firewall/proxy settings allow the connection")


def _handle_timeout_error(e: TimeoutError) -> None:
    """Handle timeout errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": "Request timed out",
            "error_code": "TIMEOUT_ERROR",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Request timed out")
    click.echo("   The request took too long to complete")
    click.echo("💡 Please try:")
    click.echo("   • Retry the operation")
    click.echo("   • Check your network connection")
    click.echo("   • The Workato API may be experiencing high load")


def _handle_server_disconnect_error(e: aiohttp.ServerDisconnectedError) -> None:
    """Handle server disconnection errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": "Server disconnected unexpectedly",
            "error_code": "SERVER_DISCONNECT",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ Server disconnected")
    click.echo("   The connection to Workato API was lost")
    click.echo("💡 Please try:")
    click.echo("   • Retry the operation")
    click.echo("   • Check Workato status page for outages")


def _handle_ssl_error(e: aiohttp.ClientSSLError | ssl.SSLError) -> None:
    """Handle SSL/certificate errors."""
    output_mode = _get_output_mode()

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": "SSL certificate verification failed",
            "error_code": "SSL_ERROR",
            "details": str(e),
        }
        click.echo(json.dumps(error_data))
        return

    click.echo("❌ SSL certificate error")
    click.echo("   Could not verify the SSL certificate")
    click.echo(f"   {str(e)}")
    click.echo("💡 Please check:")
    click.echo("   • Your system clock is set correctly")
    click.echo("   • You have the latest CA certificates installed")
    click.echo("   • Your network is not intercepting HTTPS connections")


def _handle_click_exception(e: click.ClickException) -> None:
    """Handle click.ClickException with clean error message."""
    output_mode = _get_output_mode()

    error_msg = str(e)

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": error_msg,
            "error_code": "CLI_ERROR",
        }
        click.echo(json.dumps(error_data))
        return

    click.echo(f"❌ {error_msg}")


def _handle_generic_cli_error(e: Exception) -> None:
    """Handle any other unexpected CLI errors with a generic message."""
    output_mode = _get_output_mode()

    error_type = type(e).__name__
    error_msg = str(e)

    if output_mode == "json":
        error_data = {
            "status": "error",
            "error": error_msg,
            "error_code": "CLI_ERROR",
            "error_type": error_type,
        }
        click.echo(json.dumps(error_data))
        return

    click.echo(f"❌ {error_type}")
    click.echo(f"   {error_msg}")
