import os
import zipfile

from pathlib import Path

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform import Workato
from workato_platform.cli.containers import Container
from workato_platform.cli.utils.config import ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions
from workato_platform.cli.utils.spinner import Spinner


STATUS_INFO = {
    "no_update_or_updated_without_restart": {
        "name": "No restart needed",
        "icon": "✅",
        "success": True,
        "description": "Updated successfully or no changes needed",
    },
    "restarted": {
        "name": "Updated and restarted",
        "icon": "✅",
        "success": True,
        "description": "Successfully updated and restarted",
    },
    "not_found": {
        "name": "Recipe not found",
        "icon": "❌",
        "success": False,
        "description": "Failed - recipe could not be found",
    },
    "stop_failed": {
        "name": "Failed to stop recipe",
        "icon": "❌",
        "success": False,
        "description": "Failed - could not stop running recipe",
    },
    "stopped": {
        "name": "Updated but stopped",
        "icon": "⚠️",
        "success": False,
        "description": "Updated but failed to restart due to errors",
    },
    "restart_failed": {
        "name": "Failed to restart recipe",
        "icon": "⚠️",
        "success": False,
        "description": "Updated but failed to restart",
    },
}


@click.command()
@click.option(
    "--restart-recipes", is_flag=True, default=True, help="Restart recipes after import"
)
@click.option(
    "--include-tags", is_flag=True, default=True, help="Include tags in import"
)
@inject
@handle_api_exceptions
async def push(
    restart_recipes: bool = True,
    include_tags: bool = True,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Push local project changes to Workato"""

    # Load API token
    api_token = config_manager.api_token
    if not api_token:
        click.echo("❌ No API token found. Please run 'workato init' first.")
        return

    # Load project metadata
    meta_data = config_manager.load_config()
    if not meta_data.folder_id:
        click.echo("❌ No project configured. Please run 'workato init' first.")
        return

    folder_id = meta_data.folder_id
    project_name = meta_data.project_name

    # Determine project directory based on current location
    current_project_name = config_manager.get_current_project_name()
    if current_project_name:
        # We're in a project directory, use the project root (not cwd)
        project_dir = config_manager.get_project_root()
        if not project_dir:
            click.echo("❌ Could not determine project root directory")
            return
    else:
        # Look for projects/{name} structure
        projects_root = Path("projects")
        if projects_root.exists() and project_name:
            project_dir = projects_root / project_name
            if not project_dir.exists():
                click.echo(
                    "❌ No project directory found. Please run 'workato pull' first."
                )
                return
        else:
            click.echo(
                "❌ No project directory found. Please run 'workato pull' first."
            )
            return

    # Create zip file from project directory, excluding .workato/
    zip_path = f"{project_name}.zip"

    try:
        spinner = Spinner("Creating package from project directory")
        spinner.start()
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_dir):
                    # Exclude .workato directories from traversal
                    dirs[:] = [d for d in dirs if d != ".workato"]

                    for file in files:
                        file_path = Path(root) / file
                        # Get relative path from project directory
                        arcname = file_path.relative_to(project_dir)
                        zipf.write(file_path, arcname)
        finally:
            elapsed = spinner.stop()

        click.echo(f"✅ Package created: {zip_path} ({elapsed:.1f}s)")

        # Upload the package
        await upload_package(
            folder_id=folder_id,
            zip_path=zip_path,
            restart_recipes=restart_recipes,
            include_tags=include_tags,
        )
    finally:
        # Clean up zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)


@inject
async def upload_package(
    folder_id: int,
    zip_path: str,
    restart_recipes: bool | None = None,
    include_tags: bool | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Upload the package to Workato"""
    spinner = Spinner("Uploading package to Workato")
    spinner.start()

    try:
        # Read and upload the zip file
        with open(zip_path, "rb") as f:
            response = await workato_api_client.packages_api.import_package(
                id=folder_id,
                body=f.read(),
                restart_recipes=restart_recipes,
                include_tags=include_tags,
            )

        import_data = response
        import_id = import_data.id
        status = import_data.status
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ Package uploaded successfully ({elapsed:.1f}s)")
    click.echo(f"  📊 Import ID: {import_id}")
    click.echo(f"  📈 Status: {status}")

    if status == "completed":
        click.echo("🎉 Import completed successfully")
    else:
        # Poll for completion
        await poll_import_status(import_id)


@inject
async def poll_import_status(
    import_id: int, workato_api_client: Workato = Provide[Container.workato_api_client]
) -> None:
    """Poll import status until completion or timeout"""
    import time

    max_wait_time = 300  # 5 minutes timeout
    poll_interval = 3  # Check every 3 seconds
    start_time = time.time()

    # Start spinner for polling
    spinner = Spinner("Processing import")
    spinner.start()

    # Give the import process a moment to initialize before first poll
    time.sleep(2)

    while time.time() - start_time < max_wait_time:
        package_response = await workato_api_client.packages_api.get_package(import_id)

        current_status = package_response.status

        if current_status == "completed":
            spinner.stop()
            click.echo("🎉 Import completed successfully")

            # Show recipe status information if available
            if package_response.recipe_status:
                recipe_statuses = package_response.recipe_status
                click.echo("📋 Recipe Import Results:")

                # Count different result types
                result_counts: dict[str, int] = {}
                for recipe in recipe_statuses:
                    if not recipe.import_result:
                        continue
                    result = recipe.import_result
                    result_counts[result] = result_counts.get(result, 0) + 1

                # Display counts with friendly names and success/failure indicators

                # Separate successful and failed imports
                successful_results = []
                failed_results = []

                for result, count in result_counts.items():
                    info = STATUS_INFO.get(
                        result,
                        {
                            "name": result.replace("_", " ").title()
                            if result
                            else "Unknown",
                            "icon": "❓",
                            "success": False,
                            "description": "Unknown status",
                        },
                    )

                    result_line = f"  {info['icon']} {count} recipe(s): {info['name']}"

                    if info["success"]:
                        successful_results.append(result_line)
                    else:
                        failed_results.append(result_line)

                # Display successful imports first
                for line in successful_results:
                    click.echo(line)

                # Display failed imports
                for line in failed_results:
                    click.echo(line)

                # Show overall import summary
                total_recipes = sum(result_counts.values())
                successful_count = sum(
                    count
                    for result, count in result_counts.items()
                    if STATUS_INFO.get(result, {}).get("success", False)
                )
                failed_count = total_recipes - successful_count

                if failed_count > 0:
                    click.echo(
                        f"  📊 Summary: {successful_count}/{total_recipes} "
                        "recipes imported successfully"
                    )

            return

        elif current_status == "failed":
            spinner.stop()
            click.echo("❌ Import failed")

            # Show error details from the correct field
            if package_response.error:
                click.echo(f"  📄 Error: {package_response.error}")
            if package_response.recipe_status:
                click.echo("  📋 Recipe Status:")
                for (
                    recipe_name,
                    status_info,
                ) in package_response.recipe_status:
                    click.echo(f"    📄 {recipe_name}: {status_info}")

            return

        elif current_status in ["in_progress", "processing"]:
            # Update spinner message with status (spinner handles elapsed time)
            spinner.update_message(f"Processing import ({current_status})")

        else:
            # Update spinner with unknown status (spinner handles elapsed time)
            spinner.update_message(f"Processing import ({current_status})")

        # Sleep before next poll (for non-404 cases)
        time.sleep(poll_interval)

    # Timeout reached
    spinner.stop()
    click.echo(f"⏰ Import still in progress after {max_wait_time // 60} minutes")
    click.echo(
        f"  💡 Check status manually: workato packages import-status "
        f"--import-id {import_id}"
    )
    click.echo(f"  📊 Import ID: {import_id}")
