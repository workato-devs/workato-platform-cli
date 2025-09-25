"""Initialize Workato CLI for a new project"""

import asyncclick as click

from workato_platform import Workato
from workato_platform.cli.commands.projects.project_manager import ProjectManager
from workato_platform.cli.commands.pull import _pull_project
from workato_platform.cli.utils.config import ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions
from workato_platform.client.workato_api.configuration import Configuration


@click.command()
@handle_api_exceptions
async def init() -> None:
    """Initialize Workato CLI for a new project"""
    # Initialize configuration with simplified setup flow
    config_manager = await ConfigManager.initialize()

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
