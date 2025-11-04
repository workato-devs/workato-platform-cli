import json
import time
import webbrowser

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform_cli import Workato
from workato_platform_cli.cli.commands.connectors.connector_manager import (
    ConnectorManager,
)
from workato_platform_cli.cli.commands.projects.project_manager import ProjectManager
from workato_platform_cli.cli.containers import Container
from workato_platform_cli.cli.utils import Spinner
from workato_platform_cli.cli.utils.config import ConfigManager
from workato_platform_cli.cli.utils.exception_handler import (
    handle_api_exceptions,
    handle_cli_exceptions,
)
from workato_platform_cli.client.workato_api.models.connection import Connection
from workato_platform_cli.client.workato_api.models.connection_create_request import (
    ConnectionCreateRequest,
)
from workato_platform_cli.client.workato_api.models.connection_update_request import (
    ConnectionUpdateRequest,
)
from workato_platform_cli.client.workato_api.models.picklist_request import (
    PicklistRequest,
)
from workato_platform_cli.client.workato_api.models.runtime_user_connection_create_request import (  # noqa: E501
    RuntimeUserConnectionCreateRequest,
)


OAUTH_TIMEOUT = 60


def _get_callback_url_from_api_host(api_host: str) -> str:
    """Convert API host URL to web callback URL for OAuth

    Args:
        api_host: The API host URL (e.g., "https://www.workato.com")

    Returns:
        The corresponding web callback URL (e.g., "https://app.workato.com/")
    """
    if not api_host:
        return "https://app.workato.com/"

    try:
        parsed = urlparse(api_host)
        hostname = parsed.hostname

        if not hostname:
            return "https://app.workato.com/"

        # Map regional hostnames to their web app URLs
        hostname_mapping = {
            "preview.workato.com": "https://app.preview.workato.com/",
            "www.workato.com": "https://app.workato.com/",
            "eu.workato.com": "https://app.eu.workato.com/",
            "jp.workato.com": "https://app.jp.workato.com/",
            "sg.workato.com": "https://app.sg.workato.com/",
            "au.workato.com": "https://app.au.workato.com/",
            "il.workato.com": "https://app.il.workato.com/",
        }

        # Check for exact hostname match
        if hostname in hostname_mapping:
            return hostname_mapping[hostname]

        # If hostname ends with workato.com but isn't in our mapping, default to main
        if hostname.endswith(".workato.com") or hostname == "workato.com":
            return "https://app.workato.com/"

        # For any other host, default to main app
        return "https://app.workato.com/"

    except Exception:
        # If URL parsing fails, default to main app
        return "https://app.workato.com/"


@click.group()
def connections() -> None:
    """Manage connections"""
    pass


@connections.command()
@click.option(
    "--name",
    required=True,
    help='Name of the connection (e.g., "Prod JIRA connection")',
)
@click.option(
    "--provider",
    required=True,
    help='The application type/provider (e.g., "jira", "salesforce")',
)
@click.option(
    "--parent-id",
    type=int,
    help="ID of the parent connection (must be same provider type)",
)
@click.option(
    "--folder-id",
    type=int,
    help="ID of the project/folder (uses current project if not specified)",
)
@click.option("--external-id", help="External ID assigned to the connection")
@click.option(
    "--shell-connection",  # noboost
    is_flag=True,
    help="Create as shell connection (no authentication test)",  # noboost
)
@click.option("--input", "input_params", help="Connection parameters as JSON string")
@handle_cli_exceptions
@inject
@handle_api_exceptions
async def create(
    name: str,
    provider: str,
    parent_id: int | None = None,
    folder_id: int | None = None,
    external_id: str | None = None,
    shell_connection: bool | None = None,
    input_params: str | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
    config_manager: ConfigManager = Provide[Container.config_manager],
    connector_manager: ConnectorManager = Provide[Container.connector_manager],
) -> None:
    """Create a new connection

    Connection input parameters vary by provider. Use 'workato connectors parameters'
    to discover what parameters are required for each provider.

    Examples:

    # Find parameters for a provider
    workato connectors parameters --provider salesforce

    # Create connection with inline JSON
    workato connections create --provider salesforce --name "My Salesforce"
      --input '{"security_token": "token"}'

    # Create shell connection (no authentication test)
    workato connections create --provider jira --name "Dev JIRA" --shell-connection
    """

    if not provider or not name:
        click.echo("❌ Provider and name are required")
        click.echo("💡 Use 'workato connectors list' to see available providers")
        return

    # Get folder ID from parameter or meta file
    if not folder_id:
        meta_data = config_manager.load_config()

        if not meta_data.folder_id:
            click.echo("❌ No folder ID provided and no project configured.")
            click.echo("💡 Either specify --folder-id or run 'workato init' first.")
            return

        folder_id = meta_data.folder_id

    # Parse input parameters
    connection_input = parse_connection_input(input_params)
    if connection_input is None and input_params:
        return  # Error already displayed by parse function

    # Check if this is an OAuth provider that needs special handling
    oauth_required = await requires_oauth_flow(provider)

    # Also check using connector manager data for OAuth providers
    provider_data = connector_manager.get_provider_data(provider)
    is_oauth_provider = provider_data.oauth if provider_data else False

    # For OAuth providers, prompt for missing OAuth parameters
    if (oauth_required or is_oauth_provider) and not shell_connection:
        connection_input = await connector_manager.prompt_for_oauth_parameters(
            provider, connection_input
        )
        # Update oauth_required if we detected OAuth via connector manager
        oauth_required = oauth_required or is_oauth_provider

    connection_create_request = ConnectionCreateRequest(
        name=name,
        provider=provider,
        parent_id=parent_id,
        folder_id=folder_id,
        external_id=external_id,
        shell_connection=shell_connection or oauth_required,
        input=connection_input,
    )

    # Create the connection
    connection_data = await workato_api_client.connections_api.create_connection(
        connection_create_request=connection_create_request,
    )
    connection_id = connection_data.id

    # Display creation success
    click.echo("✅ Connection created successfully")
    click.echo(f"  📄 Name: {connection_data.name}")
    click.echo(f"  🆔 Connection ID: {connection_id}")
    click.echo(f"  🔌 Provider: {connection_data.provider}")

    if oauth_required:
        # Try to get OAuth URL for OAuth providers
        click.echo("🔐 OAuth provider detected - attempting to get OAuth URL...")
        try:
            await get_connection_oauth_url(
                connection_id,
                open_browser=True,
            )
            # Poll for OAuth completion
            await poll_oauth_connection_status(connection_id)
        except Exception:
            # If OAuth URL fails, fall back to manual authorization
            click.echo(
                "⚠️  Automatic OAuth URL retrieval not available for this provider"
            )
            click.echo("🔗 Opening connection page for manual authorization...")

            # Use the existing config_manager from DI
            web_base_url = config_manager.api_host
            connection_url = f"{web_base_url}/connections/{connection_id}"

            click.echo(f"📋 Connection URL: {connection_url}")

            # Open in browser
            try:
                webbrowser.open(connection_url)
                click.echo("🌐 Opening connection page in browser...")
            except OSError as e:
                click.echo(f"⚠️  Could not open browser: {str(e)}")
                click.echo(
                    "💡 Please copy and paste the connection URL into your browser"
                )

            click.echo()
            click.echo("💡 Manual authorization steps:")
            click.echo("  1. Complete OAuth authorization in the opened browser page")
            click.echo("  2. Follow the on-screen prompts to authenticate")
            click.echo(
                f"  3. Use connection ID {connection_id} in recipes once authorized"
            )

            # Poll for OAuth completion in manual flow too
            await poll_oauth_connection_status(connection_id)
        return


@connections.command(name="create-oauth")
@click.option(
    "--parent-id",
    required=True,
    help="ID of the parent OAuth connection (must be established/authorized)",
)
@click.option("--name", help="Name of the runtime user connection (optional)")
@click.option(
    "--folder-id",
    type=int,
    help="ID of the project/folder (uses current project if not specified)",
)
@click.option("--external-id", help="End user string ID for identifying the connection")
@click.option(
    "--callback-url",
    help="URL called back after successful token acquisition (optional)",
)
@click.option(
    "--redirect-url",
    help="URL to redirect user after successful token acquisition (optional)",
)
@handle_cli_exceptions
@inject
@handle_api_exceptions
async def create_oauth(
    parent_id: int,
    external_id: str,
    name: str | None = None,
    folder_id: int | None = None,
    callback_url: str | None = None,
    redirect_url: str | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Create an OAuth runtime user connection

    This command creates a runtime user connection for OAuth-enabled providers.
    The parent connection must be an established OAuth connection. This initiates
    the OAuth flow and provides a URL for end user authorization.

    Parameters:
    - parent_id: ID of parent OAuth connector (connection must be established)
    - name: Optional name for the runtime user connection
    - folder_id: Folder to put connection (uses current project if not specified)
    - external_id: End user string ID for identifying the connection
    - callback_url: Optional URL called back after successful token acquisition
    - redirect_url: Optional URL where user is redirected after successful authorization

    Examples:

    # Create OAuth connection with minimal parameters
    workato connections create-oauth --parent-id 12345 --external-id "user@example.com"

    # Create with custom name and URLs
    workato connections create-oauth --parent-id 12345 --name "John's Google Drive"
      --external-id "john.doe@company.com" --callback-url "https://myapp.com/oauth/callback"
      --redirect-url "https://myapp.com/success"
    """

    # Get folder ID from parameter or meta file
    if not folder_id:
        meta_data = config_manager.load_config()
        folder_id = meta_data.folder_id

        if not folder_id:
            click.echo("❌ No folder ID provided and no project configured.")
            click.echo("💡 Either specify --folder-id or run 'workato init' first.")
            return

    # Set default callback URL if not provided
    if not callback_url:
        base_url = config_manager.api_host or ""
        callback_url = _get_callback_url_from_api_host(base_url)

    # Create the runtime user connection
    response = await workato_api_client.connections_api.create_runtime_user_connection(
        runtime_user_connection_create_request=RuntimeUserConnectionCreateRequest(
            parent_id=parent_id,
            name=name,
            folder_id=folder_id,
            external_id=external_id,
            callback_url=callback_url,
            redirect_url=redirect_url,
        ),
    )

    # Display creation success
    click.echo("✅ Runtime user connection created successfully")
    click.echo(f"  🆔 Connection ID: {response.data.id}")
    click.echo(f"  🔗 URL: {response.data.url}")

    click.echo()

    try:
        webbrowser.open(response.data.url)
        click.echo("  🌐 Opening OAuth URL in browser...")
    except OSError as e:
        click.echo(f"  ⚠️  Could not open browser: {str(e)}")
        click.echo(
            "  💡 Please copy and paste the OAuth URL into your browser manually"
        )
    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  1. Complete OAuth authorization in the opened browser page")
    click.echo("  2. Follow the on-screen prompts to authenticate")
    click.echo(
        f"  3. Use connection ID {response.data.id} in your recipes once authorized"
    )
    await poll_oauth_connection_status(response.data.id)


@connections.command()
@click.option(
    "--connection-id", required=True, type=int, help="ID of the connection to update"
)
@click.option("--name", help="New name for the connection")
@click.option(
    "--parent-id", help="ID of the parent connection (must be same provider type)"
)
@click.option(
    "--folder-id", type=int, help="ID of the project/folder to move connection to"
)
@click.option("--external-id", help="External ID assigned to the connection")
@click.option(
    "--shell-connection", type=bool, help="Set as shell connection (true/false)"
)
@click.option(
    "--input", "input_params", help="Updated connection parameters as JSON string"
)
@click.option(
    "--input-file", help="Path to JSON file containing updated connection parameters"
)
@handle_cli_exceptions
@handle_api_exceptions
async def update(
    connection_id: int,
    name: str | None = None,
    parent_id: int | None = None,
    folder_id: int | None = None,
    external_id: str | None = None,
    shell_connection: bool | None = None,
    input_params: str | None = None,
) -> None:
    """Update an existing connection

    Update connection properties like name, folder, parent, or authentication parameters.
    Use 'workato connectors parameters' to discover what parameters are available.

    Examples:

    # Update connection name
    workato connections update --connection-id 123 --name "Updated Salesforce"

    # Move connection to different folder
    workato connections update --connection-id 123 --folder-id 456

    # Update authentication parameters
    workato connections update --connection-id 123 --input '{"username": "new@example.com", "password": "newpass"}'

    # Update from configuration file
    workato connections update --connection-id 123 --input-file updated-config.json

    # Convert to shell connection
    workato connections update --connection-id 123 --shell-connection true
    """  # noqa: E501

    # Parse input parameters
    connection_input = parse_connection_input(input_params)
    if connection_input is None and input_params:
        return  # Error already displayed by parse function

    # Build the request payload (only include fields that are being updated)
    connection_update_request = ConnectionUpdateRequest(
        name=name,
        parent_id=parent_id,
        folder_id=folder_id,
        external_id=external_id,
        shell_connection=shell_connection,
        input=connection_input,
    )

    # Update the connection
    await update_connection(connection_id, connection_update_request)


def parse_connection_input(input_params: str | None = None) -> dict[str, Any] | None:
    """Parse connection input parameters from JSON string"""
    if not input_params:
        return None  # No input provided, which is valid

    try:
        # Parse JSON string
        connection_input = json.loads(input_params)

        if not isinstance(connection_input, dict):
            click.echo("❌ Connection input must be a JSON object")
            return None

        return connection_input

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON in connection input: {str(e)}")
        return None


@inject
async def update_connection(
    connection_id: int,
    connection_update_request: ConnectionUpdateRequest,
    workato_api_client: Workato = Provide[Container.workato_api_client],
    project_manager: ProjectManager = Provide[Container.project_manager],
) -> None:
    """Update the connection using the Workato API"""
    connection_name = connection_update_request.name
    spinner = Spinner(f"Updating connection '{connection_name}'")
    spinner.start()

    try:
        connection_data = await workato_api_client.connections_api.update_connection(
            connection_id=connection_id,
            connection_update_request=connection_update_request,
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ Connection updated successfully ({elapsed:.1f}s)")

    # Display updated connection details
    click.echo(f"  📄 Name: {connection_data.name}")
    click.echo(f"  🆔 ID: {connection_data.id}")
    click.echo(f"  🔌 Provider: {connection_data.provider}")
    click.echo(f"  📁 Folder ID: {connection_data.folder_id}")

    # Show connection status
    authorization_status = connection_data.authorization_status
    if authorization_status == "success":
        click.echo("  ✅ Status: Authorized")
    else:
        click.echo("  ⚠️  Status: Not authorized")

    # Show parent connection if specified
    if connection_data.parent_id:
        click.echo(f"  🔗 Parent ID: {connection_data.parent_id}")

    # Show external ID if specified
    if connection_data.external_id:
        click.echo(f"  🏷️  External ID: {connection_data.external_id}")

    # Show what was updated
    updated_fields = []
    if connection_update_request.name:
        updated_fields.append("name")
    if connection_update_request.folder_id:
        updated_fields.append("folder location")
    if connection_update_request.input:
        updated_fields.append("authentication parameters")
    if connection_update_request.shell_connection:
        updated_fields.append("connection type")
    if connection_update_request.parent_id:
        updated_fields.append("parent connection")
    if connection_update_request.external_id:
        updated_fields.append("external ID")

    if updated_fields:
        click.echo(f"  🔄 Updated: {', '.join(updated_fields)}")

    click.echo()
    click.echo("💡 Next steps:")
    if connection_update_request.input:
        click.echo("  • Test the connection with updated credentials")
    if connection_update_request.shell_connection:
        click.echo("  • Complete authentication setup for shell connection")
    click.echo("  • Verify connection works in recipes")

    # Handle post-update sync
    await project_manager.handle_post_api_sync()


@connections.command(name="list")
@click.option("--folder-id", type=int, help="Filter by folder ID")
@click.option("--parent-id", type=int, help="Filter by parent connection ID")
@click.option("--external-id", help="Filter by external ID")
@click.option(
    "--include-runtime", is_flag=True, help="Include runtime user connections"
)
@click.option("--tags", help="Filter by connection tags")
@click.option("--provider", help="Filter by provider type (e.g., salesforce, jira)")
@click.option("--unauthorized", is_flag=True, help="Show only authorized connections")
@handle_cli_exceptions
@inject
@handle_api_exceptions
async def list_connections(
    folder_id: int | None = None,
    parent_id: int | None = None,
    external_id: str | None = None,
    include_runtime: bool | None = None,
    tags: str | None = None,
    provider: str | None = None,
    unauthorized: bool | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """List connections with filtering options

    Discover and manage connections in your workspace with detailed information
    about authorization status, providers, and relationships.

    Examples:

    # List all connections
    workato connections list

    # Filter by provider
    workato connections list --provider salesforce

    # Show only unauthorized connections
    workato connections list --unauthorized

    # List connections in specific folder
    workato connections list --folder-id 123

    # Find child connections of a parent
    workato connections list --parent-id 456

    # Include tags and runtime connections
    workato connections list --include-tags --include-runtime
    """
    # Build filter description for display
    filter_parts = []
    if folder_id:
        filter_parts.append(f"folder {folder_id}")
    if parent_id:
        filter_parts.append(f"parent {parent_id}")
    if external_id:
        filter_parts.append(f"external ID '{external_id}'")
    if provider:
        filter_parts.append(f"provider '{provider}'")
    if unauthorized:
        filter_parts.append("unauthorized only")
    if include_runtime:
        filter_parts.append("including runtime connections")

    filter_text = f" ({', '.join(filter_parts)})" if filter_parts else ""

    spinner = Spinner(f"Fetching connections{filter_text}")
    spinner.start()

    try:
        connections = await workato_api_client.connections_api.list_connections(
            folder_id=folder_id,
            parent_id=parent_id,
            external_id=external_id,
            include_runtime_connections=include_runtime,
            includes=tags.split(",") if tags else None,
        )
    finally:
        elapsed = spinner.stop()

    # Apply client-side filters (for options not supported by API)
    if provider:
        connections = [
            c
            for c in connections
            if c.application and c.application.lower() == provider.lower()
        ]

    if unauthorized:
        connections = [c for c in connections if c.authorization_status != "success"]

    click.echo(
        f"🔗 Connections ({len(connections)} found{filter_text}) - ({elapsed:.1f}s)"
    )

    if not connections:
        click.echo("  ℹ️  No connections found matching criteria")
        if filter_parts:
            click.echo("  💡 Try removing some filters to see more connections")
        else:
            click.echo(
                "  💡 Create one: workato connections create --provider <PROVIDER> "
                "--name 'My Connection'"
            )
        return

    click.echo()

    # Group connections for better display
    grouped = group_connections_by_provider(connections)

    # Display connections by provider
    for provider_name, provider_connections in grouped.items():
        click.echo(
            f"📦 {provider_name} ({len(provider_connections)} connection"
            f"{'s' if len(provider_connections) != 1 else ''})"
        )

        for connection in provider_connections:
            display_connection_summary(connection)

        click.echo()

    # Show summary statistics
    show_connection_statistics(connections)

    click.echo("💡 Commands:")
    click.echo(
        "  • View parameters: workato connectors parameters --provider <PROVIDER>"
    )
    click.echo("  • Update connection: workato connections update --connection-id <ID>")
    click.echo(
        "  • Create connection: workato connections create --provider <PROVIDER>"
    )

    # Add recipe integration guidance
    click.echo()
    click.echo("🔗 Recipe Integration:")
    click.echo("  • To use connections in recipes, update recipe config or use:")
    click.echo(
        "    workato recipes update-connection <RECIPE_ID> --adapter-name <PROVIDER> "
        "--connection-id <CONNECTION_ID>"
    )
    click.echo("  • Ensure recipe config section includes the connector provider")


def group_connections_by_provider(
    connections: list[Connection],
) -> dict[str, list[Connection]]:
    """Group connections by provider for organized display"""
    grouped: dict[str, list[Connection]] = {}

    for connection in connections:
        application = connection.application
        provider_display = application.replace("_", " ").title()

        if provider_display not in grouped:
            grouped[provider_display] = []

        grouped[provider_display].append(connection)

    # Sort each group by name
    for provider_connections in grouped.values():
        provider_connections.sort(key=lambda x: x.name.lower())

    # Return sorted by provider name
    return dict(sorted(grouped.items()))


def display_connection_summary(connection: Connection) -> None:
    """Display a summary of a connection"""
    name = connection.name
    connection_id = connection.id

    # Fix: Use authorization_status instead of authorized field
    authorization_status = connection.authorization_status

    # Status icons and text
    if authorization_status == "success":
        status_icon = "✅"
        status_text = "Authorized"
    else:
        status_icon = "❌"
        status_text = "Not authorized"

    click.echo(f"  {status_icon} {name}")
    click.echo(f"    🆔 ID: {connection_id}")
    click.echo(f"    📊 Status: {status_text}")

    # Show folder information
    if connection.folder_id:
        click.echo(f"    📁 Folder ID: {connection.folder_id}")

    # Show parent connection if available
    if connection.parent_id:
        click.echo(f"    🔗 Parent ID: {connection.parent_id}")

    # Show external ID if available
    if connection.external_id:
        click.echo(f"    🏷️  External ID: {connection.external_id}")

    # Show tags if requested and available
    if connection.tags:
        tag_list = (
            ", ".join(connection.tags)
            if len(connection.tags) <= 3
            else f"{', '.join(connection.tags[:3])} +{len(connection.tags) - 3} more"
        )
        click.echo(f"    🏷️  Tags: {tag_list}")

    # Show creation/update time if available
    if connection.created_at:
        click.echo(
            f"    🕐 Created: {connection.created_at.strftime('%Y-%m-%d')}"
        )  # Just the date part

    click.echo()


@connections.command(name="get-oauth-url")
@click.option(
    "--id",
    "connection_id",
    required=True,
    help="OAuth connection ID",
)
@click.option(
    "--open-browser",
    is_flag=True,
    default=True,
    help="Automatically open OAuth URL in browser",
)
@handle_cli_exceptions
@handle_api_exceptions
async def get_oauth_url(
    connection_id: int,
    open_browser: bool | None = None,
) -> None:
    """Get OAuth authorization URL for a OAuth connection

    This command retrieves the OAuth authorization URL for an existing OAuth connection.
    Use this if you need to re-authorize or get a fresh OAuth URL.

    Examples:

    # Get OAuth URL and open in browser
    workato connections get-oauth-url --id 73389

    # Get OAuth URL without opening browser
    workato connections get-oauth-url --id 73389 --no-open-browser
    """

    # Get the OAuth URL
    await get_connection_oauth_url(connection_id, open_browser)


@inject
async def get_connection_oauth_url(
    connection_id: int,
    open_browser: bool | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Get OAuth authorization URL for a runtime user connection"""
    spinner = Spinner(f"Getting OAuth URL for connection {connection_id}")
    spinner.start()

    try:
        response = await workato_api_client.connections_api.get_connection_oauth_url(
            connection_id=connection_id,
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ OAuth URL retrieved successfully ({elapsed:.1f}s)")

    # Display OAuth URL
    oauth_url = response.data.url

    click.echo(f"  🆔 Connection ID: {connection_id}")
    click.echo()
    click.echo("🔐 OAuth Authorization URL:")
    click.echo(f"  📋 OAuth URL: {oauth_url}")

    if open_browser and oauth_url:
        try:
            webbrowser.open(oauth_url)
            click.echo("  🌐 Opening OAuth URL in browser...")
        except OSError as e:
            click.echo(f"  ⚠️  Could not open browser: {str(e)}")
            click.echo(
                "  💡 Please copy and paste the OAuth URL into your browser manually"
            )
    else:
        click.echo("  💡 Copy and paste the OAuth URL into your browser to authorize")

    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  1. Complete OAuth authorization in your browser")
    click.echo("  2. The connection will be automatically authorized")
    click.echo(f"  3. Use connection ID {connection_id} in your recipes")


def show_connection_statistics(connections: list[Connection]) -> None:
    """Show summary statistics about the connections"""
    total = len(connections)

    # Count authorized connections using the correct field
    authorized = 0
    for c in connections:
        if c.authorization_status == "success":
            authorized += 1

    unauthorized = total - authorized

    # Provider breakdown
    providers: dict[str, int] = {}
    for connection in connections:
        provider = connection.provider or connection.application
        providers[provider] = providers.get(provider, 0) + 1

    click.echo("📊 Summary:")
    click.echo(f"  ✅ Authorized: {authorized}")
    if unauthorized > 0:
        click.echo(f"  ❌ Unauthorized: {unauthorized}")

    if len(providers) > 1:
        click.echo(f"  🔌 Providers: {len(providers)} different types")

    click.echo()


@connections.command(name="pick-list")
@click.option("--id", required=True, type=int, help="Connection ID")
@click.option("--pick-list-name", required=True, help="Name of the pick list")
@click.option(
    "--params",
    help='Pick list params as JSON string (e.g. \'{"sobject_name": "Invoice__c"}\')',
)
@handle_cli_exceptions
@inject
@handle_api_exceptions
async def pick_list(
    id: int,
    pick_list_name: str,
    params: str,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Get pick list values from a connection"""

    # Parse params if provided
    pick_list_params: dict[str, Any] = {}
    if params:
        try:
            pick_list_params = json.loads(params)
        except json.JSONDecodeError as e:
            click.echo(f"❌ Invalid JSON in --params: {str(e)}")
            click.echo('  Example: --params \'{"sobject_name": "Invoice__c"}\'')
            return

    spinner = Spinner(f"Fetching pick list '{pick_list_name}' from connection {id}")
    spinner.start()

    picklist_request = PicklistRequest(
        pick_list_name=pick_list_name,
        pick_list_params=pick_list_params,
    )

    try:
        response = await workato_api_client.connections_api.get_connection_picklist(
            connection_id=id,
            picklist_request=picklist_request,
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"📋 Pick List Results ({elapsed:.1f}s)")
    click.echo(f"  🔗 Connection ID: {id}")
    click.echo(f"  📝 Pick List: {pick_list_name}")

    if pick_list_params:
        click.echo(
            f"  ⚙️  Parameters: {json.dumps(pick_list_params, separators=(',', ':'))}"
        )

    # Display the pick list results
    if not response.data:
        click.echo("  No results found")
        return

    click.echo(f"\n📄 Results ({len(response.data)} items):")
    for i, item in enumerate(response.data, 1):
        click.echo(f"  {i:3d}. {item}")


@connections.command(name="pick-lists")
@click.option("--adapter", help="Show pick lists for a specific adapter/connector")
def pick_lists(adapter: str | None = None) -> None:
    """List available pick lists by adapter"""

    # Load the bundled picklist data
    data_file = Path(__file__).parent.parent / "data" / "picklist-data.json"

    if not data_file.exists():
        click.echo(
            "❌ Picklist data not found. Run 'python scripts/parse_picklist_docs.py' "
            "to generate it."
        )
        return

    try:
        with open(data_file) as f:
            picklist_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        click.echo(f"❌ Failed to load picklist data: {str(e)}")
        return

    if adapter:
        # Show pick lists for specific adapter
        if adapter not in picklist_data:
            click.echo(f"❌ Adapter '{adapter}' not found")
            click.echo("💡 Use 'workato connectors list' to see all available adapters")
            return

        picklists = picklist_data[adapter]
        click.echo(f"📋 Pick Lists for '{adapter}' ({len(picklists)} available)")
        click.echo()

        for i, picklist in enumerate(picklists, 1):
            click.echo(f"  {i:2d}. {picklist['name']}")
            if picklist["parameters"]:
                params_str = ", ".join(picklist["parameters"])
                click.echo(f"      📝 Parameters: {params_str}")
            else:
                click.echo("      📝 No parameters required")
            click.echo()

        click.echo("💡 Usage example:")
        first_picklist = picklists[0]
        if first_picklist["parameters"]:
            params_example = (
                "{"
                + ", ".join(
                    [f'"{p}": "value"' for p in first_picklist["parameters"][:2]]
                )
                + "}"
            )
            click.echo(
                "   workato connections pick-list --id CONNECTION_ID --pick-list-name "
                f"{first_picklist['name']} --params '{params_example}'"
            )
        else:
            click.echo(
                "   workato connections pick-list --id CONNECTION_ID --pick-list-name "
                f"{first_picklist['name']}"
            )

    else:
        # Show all adapters
        total_picklists = sum(len(picklists) for picklists in picklist_data.values())
        click.echo(
            f"📋 Available Adapters ({len(picklist_data)} adapters, {total_picklists} "
            "total pick lists)"
        )
        click.echo()

        # Sort by picklist count
        adapter_counts = [
            (name, len(picklists)) for name, picklists in picklist_data.items()
        ]
        adapter_counts.sort(key=lambda x: x[1], reverse=True)

        for adapter, count in adapter_counts:
            click.echo(f"  📦 {adapter:<30} ({count:2d} pick lists)")

        click.echo()
        click.echo("💡 To see pick lists for a specific adapter:")
        click.echo("   workato connections pick-lists --adapter salesforce")


async def requires_oauth_flow(provider: str) -> bool:
    """Determine if OAuth flow is required for this connection"""
    if not provider:
        return False

    return await is_platform_oauth_provider(
        provider
    ) or await is_custom_connector_oauth(provider)


@inject
async def is_platform_oauth_provider(
    provider: str,
    connector_manager: ConnectorManager = Provide[Container.connector_manager],
) -> bool:
    """Check if a provider is a platform OAuth provider using the API"""
    all_connectors = await connector_manager.list_platform_connectors()
    return any(
        connector.name == provider and connector.oauth for connector in all_connectors
    )


@inject
async def is_custom_connector_oauth(
    provider: str,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> bool:
    """Check if a custom connector requires OAuth by examining its code"""
    response = await workato_api_client.connectors_api.list_custom_connectors()
    connectors = response.result

    # Find connector by name/provider
    target_connector = None
    for connector in connectors:
        if connector.name == provider:
            target_connector = connector
            break

    if not target_connector:
        return False

    # Get the connector code
    connector_id = target_connector.id
    if not connector_id:
        return False

    code_response = await workato_api_client.connectors_api.get_custom_connector_code(
        id=connector_id,
    )
    code_data = code_response.data

    # Look for OAuth indicators in the code
    oauth_indicators = [
        "oauth",
        "authorization_url",
        "acquire_access_token",
        "refresh_token",
        "client_id",
        "client_secret",
        "redirect_uri",
    ]

    code_lower = code_data.code.lower()

    return any(indicator in code_lower for indicator in oauth_indicators)


@inject
async def poll_oauth_connection_status(
    connection_id: int,
    external_id: str | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
    project_manager: ProjectManager = Provide[Container.project_manager],
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Poll connection list to check if OAuth connection is authorized"""
    start_time = time.time()
    poll_interval = 5  # Check every 5 seconds

    spinner = Spinner("Waiting for OAuth authorization")
    spinner.start()

    try:
        while time.time() - start_time < OAUTH_TIMEOUT:
            elapsed_time = int(time.time() - start_time)
            remaining_time = OAUTH_TIMEOUT - elapsed_time
            spinner.update_message(
                f"Waiting for OAuth authorization ({remaining_time}s remaining)"
            )

            # Get connections filtered by external_id
            connections = await workato_api_client.connections_api.list_connections(
                external_id=external_id,
                include_runtime_connections=True,
            )

            # Find our connection
            our_connection = None
            for conn in connections:
                if conn.id == connection_id:
                    our_connection = conn
                    break

            if not our_connection:
                click.echo(f"❌ Connection with ID {connection_id} not found")
                return

            # Check authorization status using the correct field
            authorization_status = our_connection.authorization_status
            is_authorized = authorization_status == "success"

            if is_authorized:
                # Connection is now authorized!
                elapsed = spinner.stop()
                click.echo(
                    f"✅ OAuth authorization completed successfully! ({elapsed:.1f}s)"
                )
                click.echo()

                # Display final connection details
                click.echo("🎉 OAuth Base Connection Ready:")
                click.echo(f"  📄 Name: {our_connection.name}")
                click.echo(f"  🆔 Connection ID: {our_connection.id}")
                click.echo(f"  🔌 Provider: {our_connection.provider}")
                click.echo("  ✅ Status: Authorized")
                click.echo(f"  📁 Folder ID: {our_connection.folder_id}")

                click.echo()
                click.echo("💡 Next steps:")
                click.echo(
                    "  • Use this connection as a parent for runtime user connections"
                )
                click.echo(
                    "  • Create runtime connections: workato connections create-oauth "
                    f"--parent-id {connection_id}"
                )
                click.echo("  • Test the connection in your recipes")

                # Add recipe connection update guidance
                provider = our_connection.provider
                click.echo()
                click.echo("🔗 Recipe Integration:")
                click.echo(
                    "  • To use this connection in recipes, update recipe config with:"
                )
                click.echo(f"    'account_id': {connection_id}")
                click.echo(
                    f"  • Or use: workato recipes update-connection <RECIPE_ID> "
                    f"--adapter-name {provider} --connection-id {connection_id}"
                )
                click.echo(
                    "  • Ensure recipe config section includes the connector provider"
                )

                # Handle post-creation sync
                await project_manager.handle_post_api_sync()
                return

            # Wait before next poll
            time.sleep(poll_interval)

        # Timeout reached
        elapsed = spinner.stop()
        click.echo(f"⏰ Timeout reached after {OAUTH_TIMEOUT} seconds")
        click.echo()
        click.echo("❌ OAuth authorization was not completed within the timeout period")
        click.echo()
        click.echo("💡 What to do next:")
        click.echo(
            "  • Check if the connection is authorized: workato connections list "
            f"--external-id {external_id}"
        )
        click.echo(
            "  • Complete authorization manually: "
            f"{config_manager.api_host}/connections/{connection_id}"
        )

    except KeyboardInterrupt:
        elapsed = spinner.stop()
        click.echo()
        click.echo("⚠️  Polling interrupted by user")
        click.echo()
        click.echo("💡 The shell connection has been created. You can:")
        click.echo(
            "  • Complete authorization manually: "
            f"{config_manager.api_host}/connections/{connection_id}"
        )
        click.echo(
            f"  • Check status: workato connections list --external-id {external_id}"
        )
