"""Initialize Workato CLI for a new project"""

import asyncclick as click

from workato_platform import Workato
from workato_platform.cli.commands.projects.project_manager import ProjectManager
from workato_platform.cli.commands.pull import _pull_project
from workato_platform.cli.utils.config import ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions
from workato_platform.client.workato_api.configuration import Configuration


@click.command()
@click.option("--profile", help="Profile name to use (creates new if doesn't exist)")
@click.option(
    "--region",
    type=click.Choice(["us", "eu", "jp", "au", "sg", "custom"]),
    help="Workato region",
)
@click.option("--api-token", help="Workato API token")
@click.option("--api-url", help="Custom API URL (required when region=custom)")
@click.option(
    "--project-name", help="Project name (creates new project with this name)"
)
@click.option("--project-id", type=int, help="Existing project ID to use")
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Run in non-interactive mode (requires all necessary options)",
)
@handle_api_exceptions
async def init(
    profile: str | None = None,
    region: str | None = None,
    api_token: str | None = None,
    api_url: str | None = None,
    project_name: str | None = None,
    project_id: int | None = None,
    non_interactive: bool = False,
) -> None:
    """Initialize Workato CLI for a new project"""

    if non_interactive:
        # Validate required parameters for non-interactive mode
        if not profile:
            click.echo("❌ --profile is required in non-interactive mode")
            raise click.Abort()
        if not region:
            click.echo("❌ --region is required in non-interactive mode")
            raise click.Abort()
        if not api_token:
            click.echo("❌ --api-token is required in non-interactive mode")
            raise click.Abort()
        if region == "custom" and not api_url:
            click.echo(
                "❌ --api-url is required when region=custom in non-interactive mode"
            )
            raise click.Abort()
        if not project_name and not project_id:
            click.echo(
                "❌ Either --project-name or --project-id is "
                "required in non-interactive mode"
            )
            raise click.Abort()
        if project_name and project_id:
            click.echo("❌ Cannot specify both --project-name and --project-id")
            raise click.Abort()

    config_manager = await ConfigManager.initialize(
        profile_name=profile,
        region=region,
        api_token=api_token,
        api_url=api_url,
        project_name=project_name,
        project_id=project_id,
    )

    # Automatically run pull to set up project structure
    click.echo()

    # Get API credentials from the newly configured profile
    config_data = config_manager.load_config()
    project_profile_override = config_data.profile
    api_token, api_host = config_manager.profile_manager.resolve_environment_variables(
        project_profile_override
    )

    # Create API client configuration
    api_config = Configuration(access_token=api_token, host=api_host)
    api_config.verify_ssl = False

    # Create project manager and run pull
    async with Workato(configuration=api_config) as workato_api_client:
        project_manager = ProjectManager(workato_api_client=workato_api_client)
        await _pull_project(
            config_manager=config_manager,
            project_manager=project_manager,
        )

    # Final completion message
    click.echo("🎉 Project setup complete!")
