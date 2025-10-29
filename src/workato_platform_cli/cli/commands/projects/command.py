"""Manage Workato projects"""

import json

from typing import Any

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform_cli import Workato
from workato_platform_cli.cli.commands.projects.project_manager import ProjectManager
from workato_platform_cli.cli.containers import (
    Container,
    create_profile_aware_workato_config,
)
from workato_platform_cli.cli.utils.config import ConfigData, ConfigManager
from workato_platform_cli.cli.utils.exception_handler import (
    handle_api_exceptions,
    handle_cli_exceptions,
)
from workato_platform_cli.client.workato_api.models.project import Project


@click.group()
def projects() -> None:
    """Manage Workato projects"""
    pass


@projects.command(name="list")
@click.option(
    "--profile",
    help="Profile to use for authentication and region settings",
    default=None,
)
@click.option(
    "--source",
    type=click.Choice(["local", "remote", "both"]),
    default="local",
    help="Source of projects to list: local (default), remote (server), or both",
)
@click.option(
    "--output-mode",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table (default) or json",
)
@handle_api_exceptions
@inject
async def list_projects(
    profile: str | None = None,
    source: str = "local",
    output_mode: str = "table",
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """List available projects from local workspace and/or server"""

    # Gather projects based on source
    local_projects: list[tuple[Any, str, ConfigData | None]] = []
    remote_projects: list[Project] = []

    if source in ["local", "both"]:
        local_projects = await _get_local_projects(config_manager)

    if source in ["remote", "both"]:
        workato_api_configuration = create_profile_aware_workato_config(
            config_manager=config_manager,
            cli_profile=profile,
        )
        workato_api_client = Workato(configuration=workato_api_configuration)
        async with workato_api_client as workato_api_client:
            project_manager = ProjectManager(workato_api_client=workato_api_client)
            remote_projects = await project_manager.get_all_projects()

    # Output based on mode
    if output_mode == "json":
        await _output_json(source, local_projects, remote_projects, config_manager)
    else:
        await _output_table(source, local_projects, remote_projects, config_manager)


@projects.command()
@click.argument("project_name")
@handle_cli_exceptions
@inject
async def use(
    project_name: str,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Switch to a specific project by name"""
    # Find workspace root to search for projects
    workspace_root = config_manager.get_workspace_root()

    # Use the new config system to find all projects in workspace
    all_projects = config_manager._find_all_projects(workspace_root)

    # Find the project by name
    target_project = None
    for project_path, discovered_project_name in all_projects:
        if discovered_project_name == project_name:
            target_project = (project_path, discovered_project_name)
            break

    if not target_project:
        click.echo(f"❌ Project '{project_name}' not found")
        click.echo("💡 Use 'workato projects list' to see available projects")
        return

    project_path, _ = target_project

    # Load project configuration
    try:
        project_config_manager = ConfigManager(project_path, skip_validation=True)
        project_config = project_config_manager.load_config()
    except Exception as e:
        click.echo(f"❌ Project '{project_name}' has configuration errors: {e}")
        click.echo("💡 Navigate to the project directory and run 'workato init'")
        return

    # Update workspace-level config to point to this project
    try:
        workspace_config = config_manager.load_config()

        # Calculate relative project path for workspace config
        relative_project_path = str(project_path.relative_to(workspace_root))

        # Copy project-specific data to workspace config
        workspace_config.project_id = project_config.project_id
        workspace_config.project_name = project_config.project_name
        workspace_config.project_path = relative_project_path
        workspace_config.folder_id = project_config.folder_id
        workspace_config.profile = project_config.profile

        config_manager.save_config(workspace_config)

        click.echo(f"✅ Switched to project '{project_name}'")

        # Show project details
        if project_config.project_name:
            click.echo(f"   Name: {project_config.project_name}")
        if project_config.folder_id:
            click.echo(f"   Folder ID: {project_config.folder_id}")
        if project_config.profile:
            click.echo(f"   Profile: {project_config.profile}")
        click.echo(f"   Directory: {relative_project_path}")

    except Exception as e:
        click.echo(f"❌ Failed to switch to project '{project_name}': {e}")


@projects.command()
@handle_cli_exceptions
@inject
async def switch(
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Interactively switch to a different project"""
    import inquirer

    # Find workspace root to search for projects
    workspace_root = config_manager.get_workspace_root()

    # Use the new config system to find all projects in workspace
    all_projects = config_manager._find_all_projects(workspace_root)

    if not all_projects:
        click.echo("❌ No projects found")
        click.echo("💡 Run 'workato init' to create your first project")
        return

    # Get current project for context
    current_project_name = config_manager.get_current_project_name()

    # Build project choices with configuration
    project_choices: list[tuple[str, str, ConfigData | None]] = []

    for project_path, project_name in all_projects:
        try:
            project_config_manager = ConfigManager(project_path, skip_validation=True)
            config_data = project_config_manager.load_config()

            # Create display name
            display_name = project_name
            if config_data.project_name and config_data.project_name != project_name:
                display_name = f"{project_name} ({config_data.project_name})"

            if project_name == current_project_name:
                display_name += " (current)"

            project_choices.append((display_name, project_name, config_data))
        except Exception:
            # Still include projects with configuration errors
            display_name = f"{project_name} (configuration error)"
            if project_name == current_project_name:
                display_name += " (current)"
            project_choices.append((display_name, project_name, None))

    if not project_choices:
        click.echo("❌ No configured projects found")
        click.echo("💡 Run 'workato init' to create your first project")
        return

    if len(project_choices) == 1 and project_choices[0][1] == current_project_name:
        click.echo("✅ Only one project available and it's already current")
        return

    # Create interactive selection
    choices = [choice[0] for choice in project_choices]

    questions = [
        inquirer.List(
            "project",
            message="Select a project to switch to",  # noboost
            choices=choices,
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        click.echo("❌ No project selected")
        return

    # Find the selected project
    selected_project_name: str | None = None
    selected_config: ConfigData | None = None

    for display_name, project_name, project_config_data in project_choices:
        if display_name == answers["project"]:
            selected_project_name = project_name
            selected_config = project_config_data
            break

    if not selected_project_name:
        click.echo("❌ Failed to identify selected project")
        return

    if selected_project_name == current_project_name:
        click.echo("✅ Project is already current")
        return

    if not selected_config:
        click.echo(f"❌ Project '{selected_project_name}' has configuration errors")
        return

    # Find the project path
    selected_project_path = None
    for project_path, project_name in all_projects:
        if project_name == selected_project_name:
            selected_project_path = project_path
            break

    if not selected_project_path:
        click.echo(f"❌ Failed to find path for project '{selected_project_name}'")
        return

    # Switch to the selected project
    try:
        workspace_config = config_manager.load_config()

        # Calculate relative project path for workspace config
        relative_project_path = str(selected_project_path.relative_to(workspace_root))

        # Copy project-specific data to workspace config
        workspace_config.project_id = selected_config.project_id
        workspace_config.project_name = selected_config.project_name
        workspace_config.project_path = relative_project_path
        workspace_config.folder_id = selected_config.folder_id
        workspace_config.profile = selected_config.profile

        config_manager.save_config(workspace_config)

        click.echo(f"✅ Switched to project '{selected_project_name}'")

        # Show project details
        if selected_config.project_name:
            click.echo(f"   Name: {selected_config.project_name}")
        if selected_config.folder_id:
            click.echo(f"   Folder ID: {selected_config.folder_id}")
        if selected_config.profile:
            click.echo(f"   Profile: {selected_config.profile}")
        click.echo(f"   Directory: {relative_project_path}")

    except Exception as e:
        click.echo(f"❌ Failed to switch to project '{selected_project_name}': {e}")


async def _get_local_projects(
    config_manager: ConfigManager,
) -> list[tuple[Any, str, ConfigData | None]]:
    """Get local projects with their configurations"""
    workspace_root = config_manager.get_workspace_root()
    all_projects = config_manager._find_all_projects(workspace_root)

    local_projects: list[tuple[Any, str, ConfigData | None]] = []
    for project_path, project_name in all_projects:
        try:
            project_config_manager = ConfigManager(project_path, skip_validation=True)
            config_data = project_config_manager.load_config()
            local_projects.append((project_path, project_name, config_data))
        except Exception:
            local_projects.append((project_path, project_name, None))

    return local_projects


async def _output_json(
    source: str,
    local_projects: list[tuple[Any, str, ConfigData | None]],
    remote_projects: list[Project],
    config_manager: ConfigManager,
) -> None:
    """Output projects in JSON format"""
    workspace_root = config_manager.get_workspace_root()
    current_project_name = config_manager.get_current_project_name()

    output_data: dict[str, Any] = {
        "source": source,
        "current_project": current_project_name,
        "workspace_root": str(workspace_root) if workspace_root else None,
        "local_projects": [],
        "remote_projects": [],
    }

    # Process local projects
    if source in ["local", "both"]:
        for project_path, project_name, config_data in local_projects:
            if config_data:
                project_info = {
                    "name": project_name,
                    "directory": str(project_path.relative_to(workspace_root))
                    if workspace_root
                    else str(project_path),
                    "is_current": project_name == current_project_name,
                    "project_id": config_data.project_id,
                    "folder_id": config_data.folder_id,
                    "profile": config_data.profile,
                    "configured": True,
                }
            else:
                project_info = {
                    "name": project_name,
                    "directory": str(project_path.relative_to(workspace_root))
                    if workspace_root
                    else str(project_path),
                    "is_current": project_name == current_project_name,
                    "configured": False,
                    "error": "configuration error",
                }
            output_data["local_projects"].append(project_info)

    # Process remote projects
    if source in ["remote", "both"]:
        for remote_project in remote_projects:
            # Check if this remote project exists locally
            local_match = None
            if source == "both":
                for _, _, config_data in local_projects:
                    if config_data and config_data.project_id == remote_project.id:
                        local_match = config_data
                        break

            remote_info = {
                "name": remote_project.name,
                "project_id": remote_project.id,
                "folder_id": remote_project.folder_id,
                "description": remote_project.description or "",
                "has_local_copy": local_match is not None,
            }

            if local_match:
                remote_info["local_profile"] = local_match.profile

            output_data["remote_projects"].append(remote_info)

    click.echo(json.dumps(output_data))


async def _output_table(
    source: str,
    local_projects: list[tuple[Any, str, ConfigData | None]],
    remote_projects: list[Project],
    config_manager: ConfigManager,
) -> None:
    """Output projects in table format"""
    workspace_root = config_manager.get_workspace_root()
    current_project_name = config_manager.get_current_project_name()

    if source == "local":
        if not local_projects:
            click.echo("📋 No local projects found")
            click.echo("💡 Run 'workato init' to create your first project")
            return

        click.echo("📋 Local projects:")
        for project_path, project_name, config_data in sorted(
            local_projects, key=lambda x: x[1]
        ):
            current_indicator = (
                " (current)" if project_name == current_project_name else ""
            )

            if config_data:
                click.echo(f"  • {project_name}{current_indicator}")
                if config_data.project_id:
                    click.echo(f"    Project ID: {config_data.project_id}")
                if config_data.folder_id:
                    click.echo(f"    Folder ID: {config_data.folder_id}")
                if config_data.profile:
                    click.echo(f"    Profile: {config_data.profile}")
                if workspace_root:
                    click.echo(
                        f"    Directory: {project_path.relative_to(workspace_root)}"
                    )
            else:
                click.echo(
                    f"  • {project_name}{current_indicator} (configuration error)"
                )
            click.echo()

    elif source == "remote":
        if not remote_projects:
            click.echo("📋 No remote projects found")
            return

        click.echo("📋 Remote projects:")
        for remote_project in sorted(remote_projects, key=lambda x: x.name):
            click.echo(f"  • {remote_project.name}")
            click.echo(f"    Project ID: {remote_project.id}")
            click.echo(f"    Folder ID: {remote_project.folder_id}")
            if remote_project.description:
                click.echo(f"    Description: {remote_project.description}")
            click.echo()

    else:  # both
        # Show combined view with sync status
        if not local_projects and not remote_projects:
            click.echo("📋 No projects found locally or remotely")
            click.echo("💡 Run 'workato init' to create your first project")
            return

        click.echo("📋 All projects (local + remote):")

        # Create a unified view
        all_projects = {}

        # Add local projects
        for project_path, project_name, config_data in local_projects:
            project_id = config_data.project_id if config_data else None
            all_projects[project_id or f"local:{project_name}"] = {
                "name": project_name,
                "project_id": project_id,
                "folder_id": config_data.folder_id if config_data else None,
                "profile": config_data.profile if config_data else None,
                "local_path": project_path,
                "is_local": True,
                "is_remote": False,
                "is_current": project_name == current_project_name,
                "config_error": config_data is None,
            }

        # Add/update with remote projects
        for remote_project in remote_projects:
            key = remote_project.id
            if key in all_projects:
                # Update existing local project with remote info
                all_projects[key]["is_remote"] = True
                all_projects[key]["remote_description"] = remote_project.description
            else:
                # Add remote-only project
                all_projects[key] = {
                    "name": remote_project.name,
                    "project_id": remote_project.id,
                    "folder_id": remote_project.folder_id,
                    "remote_description": remote_project.description,
                    "is_local": False,
                    "is_remote": True,
                    "is_current": False,
                    "config_error": False,
                }

        # Display unified projects
        for project_data in sorted(all_projects.values(), key=lambda x: x["name"]):
            status_indicators = []
            if project_data["is_current"]:
                status_indicators.append("current")
            if project_data["is_local"] and project_data["is_remote"]:
                status_indicators.append("synced")
            elif project_data["is_local"]:
                status_indicators.append("local only")
            elif project_data["is_remote"]:
                status_indicators.append("remote only")
            if project_data.get("config_error"):
                status_indicators.append("config error")

            status_text = (
                f" ({', '.join(status_indicators)})" if status_indicators else ""
            )
            click.echo(f"  • {project_data['name']}{status_text}")

            if project_data["project_id"]:
                click.echo(f"    Project ID: {project_data['project_id']}")
            if project_data["folder_id"]:
                click.echo(f"    Folder ID: {project_data['folder_id']}")
            if project_data.get("profile"):
                click.echo(f"    Profile: {project_data['profile']}")
            if project_data.get("remote_description"):
                click.echo(f"    Description: {project_data['remote_description']}")
            if project_data.get("local_path") and workspace_root:
                local_path = project_data["local_path"]
                click.echo(f"    Directory: {local_path.relative_to(workspace_root)}")
            click.echo()
