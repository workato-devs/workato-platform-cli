"""Manage Workato profiles for multi-environment configurations"""

import os

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform.cli.containers import Container
from workato_platform.cli.utils.config import ConfigManager


@click.group()
def profiles() -> None:
    """Manage Workato profiles for multi-environment configurations"""
    pass


@profiles.command(name="list")
@inject
async def list_profiles(
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """List all available profiles"""
    profiles_dict = config_manager.profile_manager.list_profiles()
    current_profile_name = config_manager.profile_manager.get_current_profile_name()

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
            click.echo("   Source: ~/.workato/credentials")
    else:
        click.echo("   Status: ❌ Token not found")
        click.echo("   💡 Token should be stored in ~/.workato/credentials")
        click.echo("   💡 Or set WORKATO_API_TOKEN environment variable")


@profiles.command()
@click.argument("profile_name")
@inject
async def use(
    profile_name: str,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Set the current active profile"""
    profile_data = config_manager.profile_manager.get_profile(profile_name)

    if not profile_data:
        click.echo(f"❌ Profile '{profile_name}' not found")
        click.echo("💡 Use 'workato profiles list' to see available profiles")
        return

    config_manager.profile_manager.set_current_profile(profile_name)
    click.echo(f"✅ Set '{profile_name}' as current profile")


@profiles.command()
@inject
async def status(
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

    if not current_profile_name:
        click.echo("❌ No active profile configured")
        click.echo("💡 Run 'workato init' to create and set a profile")
        return

    click.echo("📊 Profile Status:")
    click.echo(f"   Current Profile: {current_profile_name}")

    # Show source of profile selection
    if project_profile_override:
        click.echo("   Source: Project override (from .workato/config.json)")
    else:
        env_profile = os.environ.get("WORKATO_PROFILE")
        if env_profile:
            click.echo("   Source: Environment variable (WORKATO_PROFILE)")
        else:
            click.echo("   Source: Global setting (~/.workato/credentials)")

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
                click.echo("   Source: ~/.workato/credentials")
        else:
            click.echo("   Status: ❌ Token not found")
            click.echo("   💡 Token should be stored in ~/.workato/credentials")
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
        click.echo("💡 Credentials removed from ~/.workato/credentials")
    else:
        click.echo(f"❌ Failed to delete profile '{profile_name}'")


# Add show as click argument command
show = click.argument("profile_name")(show)
