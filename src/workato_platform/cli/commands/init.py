"""Initialize Workato CLI for a new project"""

import json

from typing import Any

import asyncclick as click
import certifi

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
@click.option(
    "--output-mode",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table (default) or json (only with --non-interactive)",
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
    output_mode: str = "table",
) -> None:
    """Initialize Workato CLI for a new project"""

    # Validate that --output-mode json requires --non-interactive
    if output_mode == "json" and not non_interactive:
        # Return JSON error for consistency
        error_data: dict[str, Any] = {
            "status": "error",
            "error": "--output-mode json can only be used with --non-interactive flag",
            "error_code": "INVALID_OPTIONS",
        }
        click.echo(json.dumps(error_data))
        return

    if non_interactive:
        # Validate required parameters for non-interactive mode
        error_msg = None
        error_code = None

        # Either profile OR individual attributes (region, api_token) are required
        if not profile and not (region and api_token):
            error_msg = (
                "Either --profile or both --region and --api-token are required "
                "in non-interactive mode"
            )
            error_code = "MISSING_REQUIRED_OPTIONS"
        elif region == "custom" and not api_url:
            error_msg = (
                "--api-url is required when region=custom in non-interactive mode"
            )
            error_code = "MISSING_REQUIRED_OPTIONS"
        elif not project_name and not project_id:
            error_msg = (
                "Either --project-name or --project-id is required in "
                "non-interactive mode"
            )
            error_code = "MISSING_REQUIRED_OPTIONS"
        elif project_name and project_id:
            error_msg = "Cannot specify both --project-name and --project-id"
            error_code = "CONFLICTING_OPTIONS"

        if error_msg:
            if output_mode == "json":
                error_data = {
                    "status": "error",
                    "error": error_msg,
                    "error_code": error_code,
                }
                click.echo(json.dumps(error_data))
                return
            else:
                click.echo(f"❌ {error_msg}")
                raise click.Abort()  # For non-JSON mode, keep the normal abort behavior

    # Initialize JSON output data structure if in JSON mode
    # Since we've already validated that json mode requires non-interactive,
    # we can use output_data existence as our flag throughout the code
    output_data = None
    if output_mode == "json":
        output_data = {
            "status": "success",
            "profile": {},
            "project": {},
        }

    config_manager = await ConfigManager.initialize(
        profile_name=profile,
        region=region,
        api_token=api_token,
        api_url=api_url,
        project_name=project_name,
        project_id=project_id,
        output_mode=output_mode,
        non_interactive=non_interactive,
    )

    # Check if project directory exists and is non-empty
    # Exclude CLI-managed files from the check
    cli_managed_files = {".workatoenv", ".gitignore", ".workato-ignore"}
    project_dir = config_manager.get_project_directory()
    has_user_files = False
    if project_dir and project_dir.exists():
        # Check for files that are not CLI-managed
        has_user_files = any(
            item.name not in cli_managed_files for item in project_dir.iterdir()
        )

    if has_user_files:
        # Directory is non-empty
        if non_interactive:
            # In non-interactive mode, fail with error
            error_msg = (
                f"Directory '{project_dir}' is not empty. "
                "Please use an empty directory or remove existing files."
            )
            if output_mode == "json":
                error_data = {
                    "status": "error",
                    "error": error_msg,
                    "error_code": "DIRECTORY_NOT_EMPTY",
                }
                click.echo(json.dumps(error_data))
                return
            else:
                click.echo(f"❌ {error_msg}")
                raise click.Abort()
        else:
            # Interactive mode - ask for confirmation
            click.echo(f"⚠️  Directory '{project_dir}' is not empty.")
            if not click.confirm(
                "Proceed with initialization? This may overwrite or delete files.",
                default=False,
            ):
                click.echo("❌ Initialization cancelled")
                return

    # Automatically run pull to set up project structure
    if not output_data:
        click.echo()

    # Get API credentials from the newly configured profile
    config_data = config_manager.load_config()
    project_profile_override = config_data.profile
    api_token, api_host = config_manager.profile_manager.resolve_environment_variables(
        project_profile_override
    )

    # Populate profile data for JSON output
    if output_data:
        profile_data = config_manager.profile_manager.get_profile(
            project_profile_override
            or config_manager.profile_manager.get_current_profile_name()
            or "",
        )
        if profile_data:
            output_data["profile"] = {
                "name": project_profile_override
                or config_manager.profile_manager.get_current_profile_name(),
                "region": profile_data.region,
                "region_name": profile_data.region_name,
                "api_url": profile_data.region_url,
                "workspace_id": profile_data.workspace_id,
            }

    # Create API client configuration
    api_config = Configuration(
        access_token=api_token, host=api_host, ssl_ca_cert=certifi.where()
    )

    # Create project manager and run pull
    async with Workato(configuration=api_config) as workato_api_client:
        project_manager = ProjectManager(workato_api_client=workato_api_client)
        await _pull_project(
            config_manager=config_manager,
            project_manager=project_manager,
            non_interactive=non_interactive,
        )

        # Populate project data for JSON output
        if output_data:
            meta_data = config_manager.load_config()
            project_path = config_manager.get_project_directory()
            output_data["project"] = {
                "name": meta_data.project_name or "project",
                "id": meta_data.project_id,
                "folder_id": meta_data.folder_id,
                "path": str(project_path) if project_path else None,
            }

    # Output final result
    if output_data:
        click.echo(json.dumps(output_data))
    else:
        click.echo("🎉 Project setup complete!")
