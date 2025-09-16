"""Manage Workato projects"""

import shutil

from pathlib import Path

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform import Workato
from workato_platform.cli.commands.projects.project_manager import ProjectManager
from workato_platform.cli.commands.recipes.command import (
    get_all_recipes_paginated,
)
from workato_platform.cli.containers import Container
from workato_platform.cli.utils.config import ConfigData, ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions


@click.group()
def project() -> None:
    """Manage Workato projects"""
    pass


@project.command()
@inject
@handle_api_exceptions
async def delete(
    config_manager: ConfigManager = Provide[Container.config_manager],
    project_manager: ProjectManager = Provide[Container.project_manager],
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Delete the current project and all its recipes"""

    meta_data = config_manager.load_config()
    project_id = meta_data.project_id
    folder_id = meta_data.folder_id
    project_name = meta_data.project_name

    if not project_id or not folder_id:
        click.echo("❌ No project configured")
        click.echo("💡 Set up a project: workato init")
        return

    click.echo(f"🗑️  Deleting project: {project_name}")
    click.echo(f"  📊 Project ID: {project_id}")
    click.echo(f"  📁 Folder ID: {folder_id}")
    click.echo()

    # Get all recipes in the project
    recipes = []
    click.echo("🔍 Fetching project recipes...")
    recipes = await get_all_recipes_paginated(folder_id)

    if not recipes:
        click.echo("📋 No recipes found in this project")
    else:
        click.echo(f"📋 Found {len(recipes)} recipe(s) in this project:")
        for recipe in recipes:
            status = "🟢 Running" if recipe.running else "⏹️  Stopped"
            click.echo(f"  • {recipe.name} (ID: {recipe.id}) - {status}")
        click.echo()

    # Show final confirmation BEFORE stopping any recipes
    click.echo("⚠️  WARNING: This action cannot be undone!")
    click.echo("The following will be deleted:")
    click.echo(f"  • Project: {project_name}")
    click.echo(f"  • All {len(recipes)} recipe(s)")
    click.echo("  • Project folder and all assets")
    click.echo("  • Local project directory (./project/)")
    click.echo("  • Project configuration from config.json")
    click.echo()

    if not click.confirm(
        "Are you sure you want to delete this project?", default=False
    ):
        click.echo("❌ Deletion cancelled")
        return

    # Now check if any recipes are running and stop them
    running_recipes = [r for r in recipes if r.running]
    if running_recipes:
        click.echo("⚠️  Found running recipes. These must be stopped before deletion.")
        click.echo("🔄 Stopping running recipes...")

        for recipe in running_recipes:
            click.echo(f"  ⏹️  Stopping {recipe.name}...")
            await workato_api_client.recipes_api.stop_recipe(recipe.id)
            click.echo("    ✅ Stopped successfully")

        click.echo()

    # Delete the project
    click.echo("🗑️  Deleting project...")
    await project_manager.delete_project(project_id)

    # Clean up local files
    click.echo("🧹 Cleaning up local files...")

    # Remove project directory
    project_dir = Path("project")
    if project_dir.exists():
        shutil.rmtree(project_dir)
        click.echo("  ✅ Removed ./project/ directory")

    # Clean up config.json
    meta_data = config_manager.load_config()
    meta_data.project_id = None
    meta_data.project_name = None
    meta_data.folder_id = None
    config_manager.save_config(meta_data)
    click.echo("  ✅ Removed project configuration")

    click.echo()
    click.echo("✅ Project deleted successfully")
    click.echo("💡 Run 'workato init' to set up a new project")


@project.command(name="list")
@inject
async def list_projects(
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """List all available local projects"""
    # Find workspace root
    workspace_root = config_manager.get_project_root()
    if not workspace_root:
        workspace_root = Path.cwd()

    projects_dir = workspace_root / "projects"

    if not projects_dir.exists():
        click.echo("📋 No projects directory found")
        click.echo("💡 Run 'workato init' to create your first project")
        return

    # Get current project for highlighting
    current_project_name = config_manager.get_current_project_name()

    # Find all project directories
    project_dirs = [
        d for d in projects_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
    ]

    if not project_dirs:
        click.echo("📋 No projects found")
        click.echo("💡 Run 'workato init' to create your first project")
        return

    click.echo("📋 Available projects:")
    for project_dir in sorted(project_dirs):
        project_name = project_dir.name
        current_indicator = " (current)" if project_name == current_project_name else ""

        # Check if project has configuration
        project_config_file = project_dir / ".workato" / "config.json"
        if project_config_file.exists():
            try:
                project_config = ConfigManager(project_dir / ".workato")
                config_data = project_config.load_config()
                click.echo(f"  • {project_name}{current_indicator}")
                if config_data.project_name:
                    click.echo(f"    Name: {config_data.project_name}")
                if config_data.folder_id:
                    click.echo(f"    Folder ID: {config_data.folder_id}")
                if config_data.profile:
                    click.echo(f"    Profile: {config_data.profile}")
            except Exception:
                click.echo(
                    f"  • {project_name}{current_indicator} (configuration error)"
                )
        else:
            click.echo(f"  • {project_name}{current_indicator} (not configured)")
        click.echo()


@project.command()
@click.argument("project_name")
@inject
async def use(
    project_name: str,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Switch to a specific project by name"""
    # Find workspace root
    workspace_root = config_manager.get_project_root()
    if not workspace_root:
        workspace_root = Path.cwd()

    project_dir = workspace_root / "projects" / project_name

    if not project_dir.exists():
        click.echo(f"❌ Project '{project_name}' not found")
        click.echo("💡 Use 'workato projects list' to see available projects")
        return

    # Check if project has configuration
    project_config_file = project_dir / ".workato" / "config.json"
    if not project_config_file.exists():
        click.echo(f"❌ Project '{project_name}' is not configured")
        click.echo("💡 Navigate to the project directory and run 'workato init'")
        return

    # Update workspace-level config to point to this project
    try:
        workspace_config = config_manager.load_config()
        project_config_manager = ConfigManager(project_dir / ".workato")
        project_config = project_config_manager.load_config()

        # Copy project-specific data to workspace config
        workspace_config.project_id = project_config.project_id
        workspace_config.project_name = project_config.project_name
        workspace_config.folder_id = project_config.folder_id

        config_manager.save_config(workspace_config)

        click.echo(f"✅ Switched to project '{project_name}'")

        # Show project details
        if project_config.project_name:
            click.echo(f"   Name: {project_config.project_name}")
        if project_config.folder_id:
            click.echo(f"   Folder ID: {project_config.folder_id}")
        if project_config.profile:
            click.echo(f"   Profile: {project_config.profile}")

    except Exception as e:
        click.echo(f"❌ Failed to switch to project '{project_name}': {e}")


@project.command()
@inject
async def switch(
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Interactively switch to a different project"""
    import inquirer

    # Find workspace root
    workspace_root = config_manager.get_project_root()
    if not workspace_root:
        workspace_root = Path.cwd()

    projects_dir = workspace_root / "projects"

    if not projects_dir.exists():
        click.echo("❌ No projects directory found")
        click.echo("💡 Run 'workato init' to create your first project")
        return

    # Get current project for context
    current_project_name = config_manager.get_current_project_name()

    # Find all project directories with configuration
    project_choices: list[tuple[str, str, ConfigData | None]] = []
    project_dirs = [
        d for d in projects_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
    ]

    for project_dir in sorted(project_dirs):
        project_name = project_dir.name
        project_config_file = project_dir / ".workato" / "config.json"

        if project_config_file.exists():
            try:
                project_config = ConfigManager(project_dir / ".workato")
                config_data = project_config.load_config()

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

    # Switch to the selected project
    try:
        workspace_config = config_manager.load_config()

        # Copy project-specific data to workspace config
        workspace_config.project_id = selected_config.project_id
        workspace_config.project_name = selected_config.project_name
        workspace_config.folder_id = selected_config.folder_id

        config_manager.save_config(workspace_config)

        click.echo(f"✅ Switched to project '{selected_project_name}'")

        # Show project details
        if selected_config.project_name:
            click.echo(f"   Name: {selected_config.project_name}")
        if selected_config.folder_id:
            click.echo(f"   Folder ID: {selected_config.folder_id}")
        if selected_config.profile:
            click.echo(f"   Profile: {selected_config.profile}")

    except Exception as e:
        click.echo(f"❌ Failed to switch to project '{selected_project_name}': {e}")
