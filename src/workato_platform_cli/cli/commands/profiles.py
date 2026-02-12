"""Manage Workato profiles for multi-environment configurations"""

import json
import os

from typing import Any

import asyncclick as click
import certifi

from dependency_injector.wiring import Provide, inject

from workato_platform_cli import Workato
from workato_platform_cli.cli.containers import Container
from workato_platform_cli.cli.utils.config import ConfigData, ConfigManager
from workato_platform_cli.cli.utils.config.models import (
    AVAILABLE_REGIONS,
    ProfileData,
    RegionInfo,
)
from workato_platform_cli.cli.utils.exception_handler import handle_cli_exceptions
from workato_platform_cli.client.workato_api.configuration import Configuration


@click.group()
def profiles() -> None:
    """Manage Workato profiles for multi-environment configurations"""
    pass


@profiles.command(name="list")
@click.option(
    "--output-mode",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table (default) or json",
)
@handle_cli_exceptions
@inject
async def list_profiles(
    output_mode: str = "table",
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """List all available profiles"""
    profiles_dict = config_manager.profile_manager.list_profiles()
    current_profile_name = config_manager.profile_manager.get_current_profile_name()

    if output_mode == "json":
        # JSON output mode - return structured data
        output_data: dict[str, Any] = {
            "current_profile": current_profile_name,
            "profiles": {},
        }

        for name, profile_data in profiles_dict.items():
            output_data["profiles"][name] = profile_data.model_dump()
            output_data["profiles"][name]["is_current"] = name == current_profile_name

        click.echo(json.dumps(output_data))
        return

    # Table output mode (default)
    if not profiles_dict:
        click.echo("📋 No profiles configured")
        click.echo("💡 Run 'workato init' to create your first profile")
        return

    click.echo("📋 Available profiles:")
    for name, profile_data in profiles_dict.items():
        current_indicator = " (current)" if name == current_profile_name else ""
        click.echo(f"  • {name}{current_indicator}")
        click.echo(f"    Region: {profile_data.region_name} ({profile_data.region})")
        click.echo(f"    URL: {profile_data.region_url}")
        click.echo(f"    Workspace ID: {profile_data.workspace_id}")
        click.echo()


@profiles.command()
@handle_cli_exceptions
@inject
async def show(
    profile_name: str,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Show details of a specific profile"""
    profile_data = config_manager.profile_manager.get_profile(profile_name)

    if not profile_data:
        click.echo(f"❌ Profile '{profile_name}' not found")
        return

    current_profile_name = config_manager.profile_manager.get_current_profile_name()
    is_current = profile_name == current_profile_name

    click.echo(f"📋 Profile: {profile_name}")
    if is_current:
        click.echo("✅ This is the current active profile")
    click.echo()
    click.echo("🌍 Region Information:")
    click.echo(f"   Code: {profile_data.region}")
    click.echo(f"   Name: {profile_data.region_name}")
    click.echo(f"   URL: {profile_data.region_url}")
    click.echo()
    click.echo("🏢 Workspace:")
    click.echo(f"   ID: {profile_data.workspace_id}")
    click.echo()
    click.echo("🔑 Authentication:")

    # Check if token is available using profile manager resolution
    api_token, _ = config_manager.profile_manager.resolve_environment_variables(
        profile_name
        if profile_name != config_manager.profile_manager.get_current_profile_name()
        else None
    )

    if api_token:
        click.echo("   Status: ✅ Token configured")
        # Show where the token is coming from
        if os.environ.get("WORKATO_API_TOKEN"):
            click.echo("   Source: WORKATO_API_TOKEN environment variable")
        else:
            click.echo("   Source: ~/.workato/profiles")
    else:
        click.echo("   Status: ❌ Token not found")
        click.echo("   💡 Token should be stored in keyring")
        click.echo("   💡 Or set WORKATO_API_TOKEN environment variable")


@profiles.command()
@click.argument("profile_name")
@handle_cli_exceptions
@inject
async def use(
    profile_name: str,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Set the current active profile (context-aware: workspace or global)"""
    profile_data = config_manager.profile_manager.get_profile(profile_name)

    if not profile_data:
        click.echo(f"❌ Profile '{profile_name}' not found")
        click.echo("💡 Use 'workato profiles list' to see available profiles")
        return

    # Check if we're in a workspace context
    try:
        workspace_root = config_manager.get_workspace_root()
        config_data = config_manager.load_config()
    except Exception:
        workspace_root = None
        config_data = ConfigData.model_construct()

    # If we have a workspace config (project_id exists), update workspace profile
    if config_data.project_id and workspace_root:
        config_data.profile = profile_name
        config_manager.save_config(config_data)
        click.echo(f"✅ Set '{profile_name}' as profile for current workspace")
        click.echo(f"   Workspace: {workspace_root}")

        # Also update project config if it exists
        project_dir = config_manager.get_project_directory()
        if project_dir and project_dir != workspace_root:
            project_config_manager = ConfigManager(project_dir, skip_validation=True)
            project_config = project_config_manager.load_config()
            if project_config.project_id:
                project_config.profile = profile_name
                project_config_manager.save_config(project_config)
                project_dir = project_dir.relative_to(workspace_root)
                click.echo(f"   Project config also updated: {project_dir}")
    else:
        # No workspace context, set global profile
        config_manager.profile_manager.set_current_profile(profile_name)
        click.echo(f"✅ Set '{profile_name}' as global default profile")


@profiles.command()
@click.option(
    "--output-mode",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table (default) or json",
)
@handle_cli_exceptions
@inject
async def status(
    output_mode: str = "table",
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Show current profile status and configuration"""
    # Get project config to check for profile override
    config_data = config_manager.load_config()
    project_profile_override = config_data.profile

    # Get effective profile name
    current_profile_name = config_manager.profile_manager.get_current_profile_name(
        project_profile_override
    )

    output_data: dict[str, Any] = {}

    if not current_profile_name:
        if output_mode == "json":
            output_data = {"profile": None, "error": "No active profile configured"}
            click.echo(json.dumps(output_data, indent=2))
        else:
            click.echo("❌ No active profile configured")
            click.echo("💡 Run 'workato init' to create and set a profile")
        return

    # JSON output mode
    if output_mode == "json":
        # Profile information
        profile_source_type = None
        profile_source_location = None
        if project_profile_override:
            profile_source_type = "project_override"
            profile_source_location = ".workatoenv"
        elif os.environ.get("WORKATO_PROFILE"):
            profile_source_type = "environment_variable"
            profile_source_location = "WORKATO_PROFILE"
        else:
            profile_source_type = "global_default"
            profile_source_location = "~/.workato/profiles"

        profile_data = config_manager.profile_manager.get_current_profile_data(
            project_profile_override
        )

        output_data["profile"] = {
            "name": current_profile_name,
            "source": {
                "type": profile_source_type,
                "location": profile_source_location,
            },
        }

        if profile_data:
            output_data["profile"]["configuration"] = {
                "region": {
                    "code": profile_data.region,
                    "name": profile_data.region_name,
                    "url": profile_data.region_url,
                },
                "workspace_id": profile_data.workspace_id,
            }

        # Authentication information
        api_token, _ = config_manager.profile_manager.resolve_environment_variables(
            project_profile_override
        )

        if api_token:
            auth_source_type = None
            auth_source_location = None
            if os.environ.get("WORKATO_API_TOKEN"):
                auth_source_type = "environment_variable"
                auth_source_location = "WORKATO_API_TOKEN"
            else:
                auth_source_type = "keyring"
                auth_source_location = "~/.workato/profiles"

            output_data["authentication"] = {
                "configured": True,
                "source": {"type": auth_source_type, "location": auth_source_location},
            }
        else:
            output_data["authentication"] = {"configured": False}

        # Project information
        try:
            workspace_root = config_manager.get_workspace_root()
            if workspace_root and (config_data.project_id or config_data.project_name):
                project_metadata: dict[str, Any] = {}
                if config_data.project_name:
                    project_metadata["name"] = config_data.project_name
                if config_data.project_id:
                    project_metadata["id"] = config_data.project_id
                if config_data.folder_id:
                    project_metadata["folder_id"] = config_data.folder_id

                project_path = config_manager.get_project_directory()

                if project_path:
                    output_data["project"] = {
                        "configured": True,
                        "path": str(project_path),
                        "metadata": project_metadata,
                    }
                else:
                    output_data["project"] = {"configured": False}
            else:
                output_data["project"] = {"configured": False}
        except Exception:
            output_data["project"] = {"configured": False}

        click.echo(json.dumps(output_data))
        return

    # Table output (existing code)
    click.echo("📊 Profile Status:")
    click.echo(f"   Current Profile: {current_profile_name}")

    # Show source of profile selection
    if project_profile_override:
        click.echo("   Source: Project override (from .workatoenv)")
    else:
        env_profile = os.environ.get("WORKATO_PROFILE")
        if env_profile:
            click.echo("   Source: Environment variable (WORKATO_PROFILE)")
        else:
            click.echo("   Source: Global setting (~/.workato/profiles)")

    click.echo()

    # Show profile details
    profile_data = config_manager.profile_manager.get_current_profile_data(
        project_profile_override
    )

    if profile_data:
        click.echo("🌍 Active Profile Details:")
        click.echo(f"   Region: {profile_data.region_name} ({profile_data.region})")
        click.echo(f"   URL: {profile_data.region_url}")
        click.echo(f"   Workspace ID: {profile_data.workspace_id}")
        click.echo()

        # Check authentication status
        click.echo("🔑 Authentication:")

        # Check if token is available using profile manager resolution
        api_token, _ = config_manager.profile_manager.resolve_environment_variables(
            project_profile_override
        )

        if api_token:
            click.echo("   Status: ✅ Token configured")
            # Show where the token is coming from
            if os.environ.get("WORKATO_API_TOKEN"):
                click.echo("   Source: WORKATO_API_TOKEN environment variable")
            else:
                click.echo("   Source: ~/.workato/profiles")
        else:
            click.echo("   Status: ❌ Token not found")
            click.echo("   💡 Token should be stored in keyring")
            click.echo("   💡 Or set WORKATO_API_TOKEN environment variable")


@profiles.command()
@click.argument("old_name")
@click.argument("new_name")
@handle_cli_exceptions
@inject
async def rename(
    old_name: str,
    new_name: str,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Rename a profile"""
    # Check if old profile exists
    old_profile = config_manager.profile_manager.get_profile(old_name)
    if not old_profile:
        click.echo(f"❌ Profile '{old_name}' not found")
        click.echo("💡 Use 'workato profiles list' to see available profiles")
        return

    # Check if new name already exists
    if config_manager.profile_manager.get_profile(new_name):
        click.echo(f"❌ Profile '{new_name}' already exists")
        click.echo("💡 Choose a different name or delete the existing profile first")
        return

    # Show confirmation prompt
    if not click.confirm(f"Rename profile '{old_name}' to '{new_name}'?"):
        click.echo("❌ Rename cancelled")
        return

    # Get the token from keyring
    old_token = config_manager.profile_manager._get_token_from_keyring(old_name)

    # Create new profile with same data and token
    try:
        config_manager.profile_manager.set_profile(new_name, old_profile, old_token)
    except ValueError as e:
        click.echo(f"❌ Failed to create new profile: {e}")
        return

    # If old profile was current, set new profile as current
    current_profile = config_manager.profile_manager.get_current_profile_name()
    if current_profile == old_name:
        config_manager.profile_manager.set_current_profile(new_name)

    # Delete old profile
    config_manager.profile_manager.delete_profile(old_name)

    # Show success message
    click.echo("✅ Profile renamed successfully")
    if current_profile == old_name:
        click.echo(f"✅ Set '{new_name}' as the active profile")


@profiles.command()
@click.argument("profile_name")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
@handle_cli_exceptions
@inject
async def delete(
    profile_name: str,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Delete a profile"""
    if not config_manager.profile_manager.get_profile(profile_name):
        click.echo(f"❌ Profile '{profile_name}' not found")
        return

    success = config_manager.profile_manager.delete_profile(profile_name)

    if success:
        click.echo(f"✅ Profile '{profile_name}' deleted successfully")
        click.echo("💡 Profile removed from ~/.workato/profiles")
    else:
        click.echo(f"❌ Failed to delete profile '{profile_name}'")


async def _create_profile_non_interactive(
    region: str | None,
    api_token: str | None,
    api_url: str | None,
) -> tuple[ProfileData, str] | None:
    """Create profile data non-interactively.

    Returns (ProfileData, token) on success, or None on error (error already echoed).
    """
    # Validate required parameters
    if not region:
        click.echo("❌ --region is required in non-interactive mode")
        return None
    if not api_token:
        click.echo("❌ --api-token is required in non-interactive mode")
        return None
    if region == "custom" and not api_url:
        click.echo("❌ --api-url is required when region=custom")
        return None

    # Get region info
    if region == "custom":
        region_info = RegionInfo(region="custom", name="Custom", url=api_url)
    else:
        region_info_lookup = AVAILABLE_REGIONS.get(region)
        if not region_info_lookup:
            click.echo(f"❌ Invalid region: {region}")
            return None
        region_info = region_info_lookup

    # Validate credentials and get workspace info
    api_config = Configuration(
        access_token=api_token, host=region_info.url, ssl_ca_cert=certifi.where()
    )
    try:
        async with Workato(configuration=api_config) as workato_api_client:
            user_info = await workato_api_client.users_api.get_workspace_details()
    except Exception as e:
        click.echo(f"❌ Authentication failed: {e}")
        return None

    profile_data = ProfileData(
        region=region_info.region,
        region_url=region_info.url,
        workspace_id=user_info.id,
    )
    return profile_data, api_token


@profiles.command()
@click.argument("profile_name")
@click.option(
    "--region",
    type=click.Choice(["us", "eu", "jp", "au", "sg", "custom"]),
    help="Workato region",
)
@click.option(
    "--api-token",
    help="Workato API token",
)
@click.option(
    "--api-url",
    help="Custom API URL (required when region=custom)",
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Run in non-interactive mode (requires --region and --api-token)",
)
@handle_cli_exceptions
@inject
async def create(
    profile_name: str,
    region: str | None = None,
    api_token: str | None = None,
    api_url: str | None = None,
    non_interactive: bool = False,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Create a new profile with API credentials"""
    # Check if profile already exists
    existing_profile = config_manager.profile_manager.get_profile(profile_name)
    if existing_profile:
        click.echo(f"❌ Profile '{profile_name}' already exists")
        click.echo("💡 Use 'workato profiles use' to switch to it")
        click.echo("💡 Or use 'workato profiles delete' to remove it first")
        return

    # Get profile data and token (either interactively or non-interactively)
    if non_interactive:
        result = await _create_profile_non_interactive(region, api_token, api_url)
        if result is None:
            return
        profile_data, token = result
    else:
        click.echo(f"🔧 Creating profile: {profile_name}")
        click.echo()

        try:
            (
                profile_data,
                token,
            ) = await config_manager.profile_manager.create_profile_interactive(
                profile_name
            )
        except click.ClickException:
            click.echo("❌ Profile creation cancelled")
            return

    # Save profile (common for both modes)
    try:
        config_manager.profile_manager.set_profile(profile_name, profile_data, token)
    except ValueError as e:
        click.echo(f"❌ Failed to save profile: {e}")
        return

    # Set as current profile (common for both modes)
    config_manager.profile_manager.set_current_profile(profile_name)

    # Success message (common for both modes)
    click.echo(f"✅ Profile '{profile_name}' created successfully")
    click.echo(f"✅ Set '{profile_name}' as the active profile")
    click.echo()
    click.echo("💡 You can now use this profile with Workato CLI commands")


# Add show as click argument command
show = click.argument("profile_name")(show)
