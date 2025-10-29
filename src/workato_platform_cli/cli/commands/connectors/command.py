import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform_cli.cli.commands.connectors.connector_manager import (
    ConnectorManager,
)
from workato_platform_cli.cli.containers import Container
from workato_platform_cli.cli.utils.exception_handler import handle_api_exceptions


@click.group()
def connectors() -> None:
    """Manage connectors"""
    pass


@connectors.command(name="list")
@click.option(
    "--platform",
    is_flag=True,
    help="List platform connectors with trigger and action metadata",
)
@click.option("--custom", is_flag=True, help="List custom connectors")
@inject
@handle_api_exceptions
async def list_connectors(
    platform: bool,
    custom: bool,
    connector_manager: ConnectorManager = Provide[Container.connector_manager],
) -> None:
    """List connectors (platform connectors include trigger and action metadata)"""

    # If neither flag is specified, show both
    if not platform and not custom:
        platform = True
        custom = True

    if platform:
        all_connectors = await connector_manager.list_platform_connectors()

        if all_connectors:
            for connector in all_connectors:
                name = connector.name
                title = connector.title
                click.echo(f"  • {title} ({name})")
        else:
            click.echo("  No platform connectors found")

    if custom:
        if platform:
            click.echo()  # Add spacing between sections
        await connector_manager.list_custom_connectors()


@connectors.command()
@click.option("--provider", help="Show parameters for a specific provider")
@click.option("--oauth-only", is_flag=True, help="Show only OAuth-enabled providers")
@click.option("--search", help="Search provider names (case-insensitive)")
@inject
@handle_api_exceptions
async def parameters(
    provider: str,
    oauth_only: bool,
    search: str,
    connector_manager: ConnectorManager = Provide[Container.connector_manager],
) -> None:
    """List connection parameters for connectors

    Shows configuration requirements for creating connections to different services.
    """

    # Load the bundled connection data using the injected manager
    connection_data = connector_manager.load_connection_data()

    if not connection_data:
        click.echo("❌ Connection parameter data not found.")
        click.echo()
        click.echo("💡 This may indicate:")
        click.echo("  • CLI was not installed properly (data files missing)")
        click.echo("  • Development setup needs data generation")
        click.echo()
        click.echo("🔧 To resolve:")
        click.echo(
            "  1. If using installed CLI: try reinstalling with 'pip install "
            "--force-reinstall workato-platform-cli'"
        )
        click.echo(
            "  2. If developing: run 'python scripts/parse_connection_docs.py' "
            "to generate data"
        )
        click.echo(
            "  3. Alternative: use 'workato connectors list --platform' "
            "to see available providers"
        )
        return

    if provider:
        # Show details for specific provider
        if provider not in connection_data:
            click.echo(f"❌ Provider '{provider}' not found")
            # Suggest similar providers
            suggestions = [p for p in connection_data if provider.lower() in p.lower()]
            if suggestions:
                click.echo(f"💡 Did you mean: {', '.join(suggestions[:3])}")
            click.echo(
                "💡 Use 'workato connectors parameters' to see all available providers"
            )
            return

        connector_manager.show_provider_details(provider, connection_data[provider])

    else:
        # Show all providers with optional filtering
        filtered_providers = []
        for k, v in connection_data.items():
            if (not oauth_only or v.oauth) and (
                not search
                or search.lower() in v.name.lower()
                or search.lower() in k.lower()
            ):
                filtered_providers.append((k, v))

        # Show summary
        filter_text = ""
        if oauth_only:
            filter_text += " (OAuth only)"
        if search:
            filter_text += f" (matching '{search}')"

        click.echo(
            f"🔌 Connection Parameters ({len(filtered_providers)} "
            f"providers{filter_text})"
        )
        click.echo()

        if not filtered_providers:
            click.echo("  ℹ️  No providers found matching criteria")
            return

        # Sort by name for better readability
        filtered_providers.sort(key=lambda x: x[1].name)

        # Display providers in a compact format
        for provider_key, provider_data in filtered_providers:
            name = provider_data.name
            param_count = provider_data.parameter_count
            oauth_icon = "🔐" if provider_data.oauth else "🔑"
            tunnel_icon = "🔒" if provider_data.secure_tunnel else ""

            click.echo(f"  {oauth_icon} {name:<40} ({provider_key})")

            if param_count > 0:
                click.echo(
                    f"    📝 {param_count} parameter{'s' if param_count != 1 else ''}"
                )
            else:
                click.echo("    📝 No configuration required")

            if tunnel_icon:
                click.echo(f"    {tunnel_icon} Supports secure tunnel")

            click.echo()

        click.echo("💡 Commands:")
        click.echo(
            "  • View provider details: workato connectors parameters "
            "--provider salesforce"
        )
        click.echo(
            "  • Create connection: workato connections create --provider <PROVIDER> "
            "--name 'My Connection'"
        )
