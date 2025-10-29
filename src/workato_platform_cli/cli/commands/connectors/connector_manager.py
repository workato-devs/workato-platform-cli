"""Connector manager for handling connection parameters and OAuth requirements"""

import json

from pathlib import Path
from typing import Any

import asyncclick as click

from pydantic import BaseModel, Field

from workato_platform_cli import Workato
from workato_platform_cli.cli.utils import Spinner
from workato_platform_cli.client.workato_api.models.platform_connector import (
    PlatformConnector,
)


class ConnectionParameter(BaseModel):
    """Model for a connection parameter/input field"""

    name: str = Field(..., description="Parameter name")
    label: str = Field(..., description="Human-readable label")
    type: str = Field(..., description="Parameter type (string, boolean, etc.)")
    hint: str = Field("", description="Hint text for the parameter")
    pick_list: list[list[str]] | None = Field(
        None, description="Available options for selection"
    )


class ProviderData(BaseModel):
    """Model for provider connection data"""

    name: str = Field(..., description="Provider display name")
    provider: str = Field(..., description="Provider identifier")
    oauth: bool = Field(False, description="Whether the provider supports OAuth")
    personalization: bool = Field(
        False, description="Whether personalization is supported"
    )
    secure_tunnel: bool = Field(False, description="Whether secure tunnel is supported")
    input: list[ConnectionParameter] = Field(
        default_factory=list, description="Connection parameters"
    )

    @property
    def parameter_count(self) -> int:
        """Get the number of parameters for backwards compatibility"""
        return len(self.input)

    def get_oauth_parameters(self) -> list[ConnectionParameter]:
        """Get parameters that are typically needed for OAuth"""
        # For Jira, we know auth_type and host_url are needed for OAuth
        if self.provider == "jira":
            oauth_params = []
            for param in self.input:
                if param.name in ["auth_type", "host_url"]:
                    oauth_params.append(param)
            return oauth_params

        # For other providers, we could add specific logic here
        return []

    def get_parameter_by_name(self, name: str) -> ConnectionParameter | None:
        """Get a specific parameter by name"""
        for param in self.input:
            if param.name == name:
                return param
        return None


class ConnectorManager:
    """Manager class for connector data and OAuth parameter handling"""

    def __init__(self, workato_api_client: Workato):
        self.workato_api_client = workato_api_client
        self._data_cache: dict[str, ProviderData] | None = None

    @property
    def data_file_path(self) -> Path:
        """Get the path to the connection data file"""
        return (
            Path(__file__).parent.parent.parent
            / "resources"
            / "data"
            / "connection-data.json"
        )

    def load_connection_data(self) -> dict[str, ProviderData]:
        """Load and cache connection parameter data"""
        if self._data_cache is not None:
            return self._data_cache

        if not self.data_file_path.exists():
            self._data_cache = {}
            return self._data_cache

        try:
            with open(self.data_file_path) as f:
                raw_data = json.load(f)

            self._data_cache = {}
            for provider_key, provider_data in raw_data.items():
                self._data_cache[provider_key] = ProviderData(**provider_data)

            return self._data_cache
        except (json.JSONDecodeError, ValueError):
            self._data_cache = {}
            return self._data_cache

    def get_provider_data(self, provider: str) -> ProviderData | None:
        """Get connection parameters for a specific provider"""
        data = self.load_connection_data()
        return data.get(provider)

    def get_oauth_providers(self) -> dict[str, ProviderData]:
        """Get all providers that support OAuth"""
        data = self.load_connection_data()
        return {key: provider for key, provider in data.items() if provider.oauth}

    def get_oauth_required_parameters(self, provider: str) -> list[ConnectionParameter]:
        """Get OAuth-specific required parameters for a provider"""
        provider_data = self.get_provider_data(provider)
        if not provider_data:
            return []

        return provider_data.get_oauth_parameters()

    async def prompt_for_oauth_parameters(
        self, provider: str, existing_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Prompt user for OAuth-required parameters that are missing"""
        existing_input = existing_input or {}
        oauth_params = self.get_oauth_required_parameters(provider)

        if not oauth_params:
            return existing_input

        updated_input = existing_input.copy()
        missing_params = []

        # Check which OAuth parameters are missing
        for param in oauth_params:
            param_name = param.name
            if param_name not in updated_input:
                missing_params.append(param)

        if not missing_params:
            return updated_input

        # Prompt for missing OAuth parameters
        provider_data = self.get_provider_data(provider)
        provider_name = provider_data.name if provider_data else provider.title()

        click.echo(f"🔧 {provider_name} OAuth requires additional parameters:")
        click.echo()

        for param in missing_params:
            param_name = param.name
            label = param.label
            hint = param.hint

            click.echo(f"📝 {label} ({param_name})")
            if hint:
                click.echo(f"   💡 {hint}")

            # Special handling for known OAuth parameters
            if param_name == "auth_type" and provider == "jira":
                value = "oauth"
                click.echo(f"   ✓ Setting to: {value}")
            elif param_name == "host_url" and provider == "jira":
                default_url = "https://your-domain.atlassian.net"
                value = await click.prompt(
                    f"   Enter {label}", default=default_url, show_default=True
                )
            else:
                value = await click.prompt(f"   Enter {label}")

            updated_input[param_name] = value
            click.echo()

        return updated_input

    def show_provider_details(
        self, provider_key: str, provider_data: ProviderData
    ) -> None:
        """Show detailed information about a specific provider"""
        name = provider_data.name
        param_count = provider_data.parameter_count

        click.echo(f"🔌 {name} ({provider_key})")
        click.echo()

        # Show provider characteristics
        click.echo("📋 Provider Information:")
        click.echo(f"  🔐 OAuth: {'Yes' if provider_data.oauth else 'No'}")
        personalization = (
            "Supported" if provider_data.personalization else "Not supported"
        )
        click.echo(f"  👤 Personalization: {personalization}")
        if provider_data.secure_tunnel:
            click.echo("  🔒 Secure Tunnel: Supported")
        click.echo()

        # Show parameters
        if param_count == 0:
            click.echo("✅ No configuration parameters required")
            click.echo("   This connector can be used without additional setup.")
        else:
            click.echo(f"📝 Configuration Parameters ({param_count} available):")
            click.echo()

            for i, param in enumerate(provider_data.input, 1):
                param_name = param.name
                param_type = param.type
                hint = param.hint

                type_display = f"Type: {param_type}"

                click.echo(f"   {i}. {param_name}")
                click.echo(f"      📝 Label: {param.label}")
                click.echo(f"      📊 {type_display}")

                if hint:
                    # Clean up HTML tags and truncate long hints
                    clean_hint = hint.replace("<b>", "").replace("</b>", "")
                    clean_hint = clean_hint.replace("<br>", " ")
                    if len(clean_hint) > 100:
                        clean_hint = clean_hint[:100] + "..."
                    click.echo(f"      💡 Hint: {clean_hint}")

                if param.pick_list:
                    options = [
                        (
                            option[1]
                            if isinstance(option, list) and len(option) > 1
                            else (option[0] if isinstance(option, list) else option)
                        )
                        for option in param.pick_list
                    ]
                    click.echo(f"      🔽 Options: {', '.join(options[:3])}")
                    if len(options) > 3:
                        click.echo(f"           ... and {len(options) - 3} more")

                click.echo()

        # Show usage examples
        click.echo("💡 Usage Examples:")
        click.echo("  # Basic usage:")
        click.echo(
            f"  workato connections create --provider {provider_key} "
            f"--name 'My {name}' --input '{{...}}'"
        )
        click.echo()
        click.echo("  # With configuration file:")
        click.echo(
            f"  workato connections create --provider {provider_key} "
            f"--name 'My {name}' --input-file config.json"
        )
        click.echo()

        if param_count > 0:
            click.echo("  # Sample configuration (config.json):")
            sample_config = {}
            for param in provider_data.input[:5]:  # Show first 5 params
                sample_config[param.name] = "your_value_here"

            config_json = json.dumps(sample_config, indent=2)
            for line in config_json.split("\n"):
                click.echo(f"  {line}")

    async def list_platform_connectors(self) -> list[PlatformConnector]:
        """List all platform connectors with pagination"""
        all_connectors = []
        page = 1
        per_page = 100

        spinner = Spinner("Fetching platform connectors")
        spinner.start()

        connectors_api = self.workato_api_client.connectors_api

        try:
            while True:
                response = await connectors_api.list_platform_connectors(
                    page=page,
                    per_page=per_page,
                )

                connectors = response.items

                if not connectors:
                    break

                all_connectors.extend(connectors)

                # If we got fewer than per_page results, we're on the last page
                if len(connectors) < per_page:
                    break

                page += 1
                spinner.update_message(f"Fetching platform connectors (page {page})")
        finally:
            elapsed = spinner.stop()

        click.echo(
            f"🔌 Platform Connectors ({len(all_connectors)} total) - ({elapsed:.1f}s)"
        )

        return all_connectors

    async def list_custom_connectors(self) -> None:
        """List all custom connectors"""
        spinner = Spinner("Fetching custom connectors")
        spinner.start()

        try:
            response = (
                await self.workato_api_client.connectors_api.list_custom_connectors()
            )
            connectors = response.result
        finally:
            elapsed = spinner.stop()

        click.echo(f"🛠️  Custom Connectors ({len(connectors)} total) - ({elapsed:.1f}s)")

        if connectors:
            for connector in connectors:
                name = connector.name
                version = getattr(connector, "version", "Unknown")

                click.echo(f"  • {name} (v{version})")
                if hasattr(connector, "description") and connector.description:
                    # Truncate long descriptions
                    desc = connector.description
                    if len(desc) > 100:
                        desc = desc[:100] + "..."
                    click.echo(f"    {desc}")
        else:
            click.echo("  No custom connectors found")

        click.echo()
        click.echo("💡 Commands:")
        click.echo(
            "  • View connector details: workato connectors get --id <CONNECTOR_ID>"
        )
        click.echo("  • Create connector: workato connectors create")
        click.echo(
            "  • Deploy connector: workato connectors deploy --id <CONNECTOR_ID>"
        )

        click.echo("-" * 50)
