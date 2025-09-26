"""Manage Workato projects"""

import json
from typing import Any
from pathlib import Path

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform.cli.containers import Container
from workato_platform.cli.utils.config import ConfigData, ConfigManager


@click.group()
def projects() -> None:
    """Manage Workato projects"""
    pass


@projects.command(name="list")
@click.option(
    "--output-mode",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table (default) or json"
)
@inject
async def list_projects(
    output_mode: str = "table",
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """List all available local projects"""
    # Find workspace root to search for projects
    workspace_root = config_manager.get_workspace_root()

    # Use the new config system to find all projects in workspace
    all_projects = config_manager._find_all_projects(workspace_root)

    # Get current project for highlighting
    current_project_name = config_manager.get_current_project_name()

    if output_mode == "json":
        # JSON output mode - return structured data
        output_data: dict[str, Any] = {
            "current_project": current_project_name,
            "workspace_root": str(workspace_root),
            "projects": []
        }

        for project_path, project_name in all_projects:
            try:
                # Load project config
                project_config_manager = ConfigManager(project_path, skip_validation=True)
                config_data = project_config_manager.load_config()

                project_info = {
                    "name": project_name,
                    "directory": str(project_path.relative_to(workspace_root)),
                    "is_current": project_name == current_project_name,
                    "project_id": config_data.project_id,
                    "folder_id": config_data.folder_id,
                    "profile": config_data.profile,
                    "configured": True
                }
            except Exception as e:
                project_info = {
                    "name": project_name,
                    "directory": str(project_path.relative_to(workspace_root)),
                    "is_current": project_name == current_project_name,
                    "configured": False,
                    "error": f"configuration error: {e}"
                }

            output_data["projects"].append(project_info)

        click.echo(json.dumps(output_data, indent=2))
        return

    # Table output mode (default)
    if not all_projects:
        click.echo("📋 No projects found")
        click.echo("💡 Run 'workato init' to create your first project")
        return

    click.echo("📋 Available projects:")
    for project_path, project_name in sorted(all_projects, key=lambda x: x[1]):
        current_indicator = " (current)" if project_name == current_project_name else ""

        try:
            # Load project config
            project_config_manager = ConfigManager(project_path, skip_validation=True)
            config_data = project_config_manager.load_config()

            click.echo(f"  • {project_name}{current_indicator}")
            if config_data.project_id:
                click.echo(f"    Project ID: {config_data.project_id}")
            if config_data.folder_id:
                click.echo(f"    Folder ID: {config_data.folder_id}")
            if config_data.profile:
                click.echo(f"    Profile: {config_data.profile}")
            click.echo(f"    Directory: {project_path.relative_to(workspace_root)}")
        except Exception:
            click.echo(f"  • {project_name}{current_indicator} (configuration error)")

        click.echo()


@projects.command()
@click.argument("project_name")
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
            if (
                config_data.project_name
                and config_data.project_name != project_name
            ):
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
