"""Manage Workato profiles for multi-environment configurations"""

import json
import os

from typing import Any

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform_cli.cli.containers import Container
from workato_platform_cli.cli.utils.config import ConfigData, ConfigManager


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
@click.argument("profile_name")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
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


# Add show as click argument command
show = click.argument("profile_name")(show)
