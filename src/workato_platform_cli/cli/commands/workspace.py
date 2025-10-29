import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform_cli import Workato
from workato_platform_cli.cli.containers import Container
from workato_platform_cli.cli.utils.config import ConfigManager
from workato_platform_cli.cli.utils.exception_handler import handle_api_exceptions


@click.command()
@inject
@handle_api_exceptions
async def workspace(
    config_manager: ConfigManager = Provide[Container.config_manager],
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Show current workspace, user, and project details"""

    # Get user/workspace info
    user_info = await workato_api_client.users_api.get_workspace_details()

    click.echo("👤 Current User:")
    click.echo(f"   Name: {user_info.name}")
    click.echo(f"   Email: {user_info.email}")
    click.echo(f"   ID: {user_info.id}")
    click.echo()
    click.echo("🏢 Workspace Details:")
    click.echo(f"   Plan: {user_info.plan_id}")
    click.echo(f"   Recipes: {user_info.recipes_count}")
    click.echo(f"   Active Recipes: {user_info.active_recipes_count}")
    click.echo(f"   Last Seen: {user_info.last_seen}")

    # Show current region
    click.echo()
    click.echo("🌍 Current Region:")

    # Get current profile data for region info
    config_data = config_manager.load_config()
    current_profile_data = config_manager.profile_manager.get_current_profile_data(
        config_data.profile
    )

    if current_profile_data:
        click.echo(
            f"   Region: {current_profile_data.region_name} "
            f"({current_profile_data.region})"
        )
        click.echo(f"   API URL: {current_profile_data.region_url}")

        # Show which profile is being used
        current_profile_name = config_manager.profile_manager.get_current_profile_name(
            config_data.profile
        )
        click.echo(f"   Profile: {current_profile_name}")
    else:
        click.echo("   No active profile configured")

    # Load project metadata
    meta_data = config_manager.load_config()
    if meta_data.project_id:
        click.echo("\n📁 Current Project:")
        click.echo(f"   Name: {meta_data.project_name}")
        click.echo(f"   ID: {meta_data.project_id}")
        click.echo(f"   Folder ID: {meta_data.folder_id}")
    else:
        click.echo(
            "\n📁 No project configured. Run 'workato init' to select a project."
        )
