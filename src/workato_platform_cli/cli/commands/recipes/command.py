import json

from datetime import datetime
from pathlib import Path

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform import Workato
from workato_platform.cli.commands.recipes.validator import RecipeValidator
from workato_platform.cli.containers import Container
from workato_platform.cli.utils import Spinner
from workato_platform.cli.utils.config import ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions
from workato_platform.client.workato_api.models.asset import Asset
from workato_platform.client.workato_api.models.recipe import Recipe
from workato_platform.client.workato_api.models.recipe_connection_update_request import (  # noqa: E501
    RecipeConnectionUpdateRequest,
)
from workato_platform.client.workato_api.models.recipe_start_response import (
    RecipeStartResponse,
)


@click.group()
def recipes() -> None:
    """Manage recipes"""
    pass


@recipes.command(name="list")
@click.option(
    "--adapter-names-all", help="Comma-separated adapter names (recipes must use ALL)"
)
@click.option(
    "--adapter-names-any", help="Comma-separated adapter names (recipes must use ANY)"
)
@click.option("--folder-id", type=int, help="Return recipes in specified folder")
@click.option(
    "--order", type=click.Choice(["activity", "default"]), help="Ordering method"
)
@click.option("--running", is_flag=True, help="Return only running recipes")
@click.option(
    "--since-id", type=int, help="Return recipes with IDs lower than this value"
)
@click.option(
    "--stopped-after", help="Exclude recipes stopped after this date (ISO 8601 format)"
)
@click.option(
    "--stop-cause",
    type=click.Choice(
        [
            "trigger_errors_limit",
            "action_quota_limit",
            "trial_expired",
            "txn_quota_limit",
        ]
    ),
    help="Filter by stop reason",
)
@click.option(
    "--updated-after", help="Include recipes updated after this date (ISO 8601 format)"
)
@click.option("--include-tags", help="Filter by recipe tags (comma-separated)")
@click.option(
    "--exclude-code", is_flag=True, help="Exclude recipe code from response (faster)"
)
@click.option(
    "--recursive", is_flag=True, help="Recursively list recipes in subfolders"
)
@inject
@handle_api_exceptions
async def list_recipes(
    adapter_names_all: str | None = None,
    adapter_names_any: str | None = None,
    folder_id: int | None = None,
    order: str | None = None,
    running: bool | None = None,
    since_id: int | None = None,
    stopped_after: str | None = None,
    stop_cause: str | None = None,
    updated_after: str | None = None,
    include_tags: str | None = None,
    exclude_code: bool | None = None,
    recursive: bool | None = None,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """List recipes with optional filtering"""

    folder_id = folder_id or config_manager.load_config().folder_id

    if not folder_id:
        click.echo("❌ No folder ID provided and no project configured.")
        click.echo("💡 Use --folder-id <ID> or run 'workato init' first.")
        return

    # Handle recursive mode
    if recursive:
        # Recursive mode - ignore some filters
        if any(
            [
                adapter_names_all,
                adapter_names_any,
                order,
                since_id,
                stopped_after,
                stop_cause,
                updated_after,
                include_tags,
            ]
        ):
            click.echo("⚠️  Recursive mode ignores most filters except --running")

        click.echo(f"🔍 Recursively searching for recipes in folder {folder_id}...")
        click.echo()

        # Get all recipes recursively
        recipes = await get_recipes_recursive(folder_id)

        # Apply running filter if specified
        if running:
            recipes = [recipe for recipe in recipes if recipe.running]

        click.echo()
        click.echo(f"📊 Total: {len(recipes)} recipe(s) found across all folders")

        if not recipes:
            click.echo("  ℹ️  No recipes found")
            return

        click.echo()

        # Display all recipes
        for recipe in recipes:
            display_recipe_summary(recipe=recipe)
            click.echo()

        click.echo("💡 Commands:")
        click.echo("  • Start recipe: workato recipes start --id <ID>")
        click.echo("  • View running only: workato recipes list --running --recursive")
        return

    # Non-recursive mode - get ALL recipes with pagination
    # Build filter description for user feedback
    filter_parts = []
    if folder_id:
        filter_parts.append(f"folder {folder_id}")
    if running:
        filter_parts.append("running recipes only")
    if adapter_names_all:
        filter_parts.append(f"using ALL adapters: {adapter_names_all}")
    if adapter_names_any:
        filter_parts.append(f"using ANY adapters: {adapter_names_any}")
    if stop_cause:
        filter_parts.append(f"stopped due to: {stop_cause}")

    filter_desc = f" ({', '.join(filter_parts)})" if filter_parts else ""

    spinner = Spinner(f"Fetching all recipes{filter_desc}")
    spinner.start()

    try:
        recipes = await get_all_recipes_paginated(
            folder_id=folder_id,
            adapter_names_all=adapter_names_all,
            adapter_names_any=adapter_names_any,
            order=order,
            running=running,
            since_id=since_id,
            stopped_after=stopped_after,
            stop_cause=stop_cause,
            updated_after=updated_after,
            include_tags=include_tags,
            exclude_code=exclude_code,
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"📋 Recipes ({len(recipes)} found) - ({elapsed:.1f}s)")
    if filter_parts:
        click.echo(f"  🔍 Filters: {', '.join(filter_parts)}")

    if not recipes:
        click.echo("  ℹ️  No recipes found")
        return

    click.echo()

    # Display recipes
    for recipe in recipes:
        display_recipe_summary(recipe=recipe)
        click.echo()

    click.echo("💡 Commands:")
    click.echo("  • Start recipe: workato recipes start --id <ID>")
    click.echo("  • View running only: workato recipes list --running")
    click.echo("  • Recursive search: workato recipes list --recursive")
    click.echo("  • Filter by folder: workato recipes list --folder-id <ID>")


@recipes.command()
@click.option("--path", required=True, help="Path to the recipe JSON file")
@inject
@handle_api_exceptions
async def validate(
    path: str,
    recipe_validator: RecipeValidator = Provide[Container.recipe_validator],
) -> None:
    """Validate a recipe file"""

    recipe_path = Path(path)

    # Check if file exists
    if not recipe_path.exists():
        click.echo(f"❌ File not found: {path}")
        return

    # Check if it's a JSON file
    if recipe_path.suffix.lower() != ".json":
        click.echo(f"❌ File must be a JSON file: {path}")
        return

    try:
        # Read and parse the recipe file
        with open(recipe_path) as f:
            recipe_data = json.load(f)

        # Validate the recipe
        spinner = Spinner(f"Validating recipe: {recipe_path.name}")
        spinner.start()

        try:
            result = await recipe_validator.validate_recipe(recipe_data)
        finally:
            elapsed = spinner.stop()

        # Display results
        if result.is_valid:
            click.echo(f"✅ Recipe validation passed ({elapsed:.1f}s)")
            click.echo(f"  📄 File: {recipe_path.name}")
        else:
            click.echo(f"❌ Recipe validation failed ({elapsed:.1f}s)")
            click.echo(f"  📄 File: {recipe_path.name}")
            click.echo(f"  ❗ {len(result.errors)} error(s) found")

            for i, error in enumerate(result.errors, 1):
                click.echo(f"\n  Error {i}:")
                if error.line_number:
                    click.echo(f"    Line: {error.line_number}")
                if error.field_label:
                    click.echo(f"    Field: {error.field_label}")
                if error.field_path:
                    click.echo(f"    Path: {' -> '.join(error.field_path)}")
                click.echo(f"    Message: {error.message}")
                if error.error_type:
                    click.echo(f"    Type: {error.error_type.value}")

        # Display warnings if any
        if result.warnings:
            click.echo(f"\n⚠️  {len(result.warnings)} warning(s):")
            for warning in result.warnings:
                click.echo(f"  • {warning.message}")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON file: {str(e)}")
    except (FileNotFoundError, PermissionError) as e:
        click.echo(f"❌ File access error: {str(e)}")
    except ValueError as e:
        click.echo(f"❌ Validation failed: {str(e)}")


@recipes.command()
@click.option("--id", "recipe_id", help="Recipe ID to start")
@click.option(
    "--all", "start_all", is_flag=True, help="Start all recipes in current project"
)
@click.option("--folder-id", help="Start all recipes in specified folder")
@handle_api_exceptions
async def start(
    recipe_id: int,
    start_all: bool,
    folder_id: int,
) -> None:
    """Start recipes (individual, all in project, or all in folder)"""

    # Validate that exactly one option is provided
    options_count = sum([bool(recipe_id), start_all, bool(folder_id)])
    if options_count == 0:
        click.echo("❌ Please specify one of: --id, --all, or --folder-id")
        click.echo("💡 Examples:")
        click.echo("  workato recipes start --id 12345")
        click.echo("  workato recipes start --all")
        click.echo("  workato recipes start --folder-id 67890")
        return
    elif options_count > 1:
        click.echo("❌ Please specify only one option: --id, --all, or --folder-id")
        return

    if recipe_id:
        # Start single recipe
        await start_single_recipe(recipe_id)
    elif start_all:
        # Start all recipes in current project
        await start_project_recipes()
    elif folder_id:
        # Start all recipes in specified folder
        await start_folder_recipes(folder_id)


@recipes.command()
@click.option("--id", "recipe_id", help="Recipe ID to stop")
@click.option(
    "--all", "stop_all", is_flag=True, help="Stop all recipes in current project"
)
@click.option("--folder-id", help="Stop all recipes in specified folder")
async def stop(
    recipe_id: int,
    stop_all: bool,
    folder_id: int,
) -> None:
    """Stop recipes (individual, all in project, or all in folder)"""

    # Validate that exactly one option is provided
    options_count = sum([bool(recipe_id), stop_all, bool(folder_id)])
    if options_count == 0:
        click.echo("❌ Please specify one of: --id, --all, or --folder-id")
        click.echo("💡 Examples:")
        click.echo("  workato recipes stop --id 12345")
        click.echo("  workato recipes stop --all")
        click.echo("  workato recipes stop --folder-id 67890")
        return
    elif options_count > 1:
        click.echo("❌ Please specify only one option: --id, --all, or --folder-id")
        return

    if recipe_id:
        # Stop single recipe
        await stop_single_recipe(recipe_id)
    elif stop_all:
        # Stop all recipes in current project
        await stop_project_recipes()
    elif folder_id:
        # Stop all recipes in specified folder
        await stop_folder_recipes(folder_id)


def _display_recipe_errors(
    recipe_start_response: RecipeStartResponse,
    indent: str = "  ",
) -> None:
    """Display detailed recipe error information in a readable format"""
    # Handle code_errors (validation errors in recipe steps)
    code_errors = recipe_start_response.code_errors
    if code_errors:
        click.echo(f"{indent}📋 Recipe Validation Errors:")

        for step_error in code_errors:
            if len(step_error) >= 2:
                step_number = step_error[0]
                error_details = step_error[1]

                click.echo(f"{indent}  🔸 Step {step_number}:")

                for error in error_details:
                    field_label = error[0]
                    account_id = error[1]  # Connection ID (account_id)
                    error_message = error[2]
                    field_path = error[3]

                    click.echo(f"{indent}    • {field_label}: {error_message}")
                    if account_id is not None:
                        click.echo(f"{indent}      Connection ID: {account_id}")
                    if field_path:
                        click.echo(f"{indent}      Field: {field_path}")

    # Handle config_errors (configuration-level errors)
    config_errors = recipe_start_response.config_errors
    if config_errors:
        click.echo(f"{indent}⚙️ Configuration Errors:")

        for config_error in config_errors:
            if isinstance(config_error, list) and len(config_error) >= 2:
                step_number = config_error[0]
                error_details = config_error[1]

                click.echo(f"{indent}  🔸 Step {step_number}:")

                for error in error_details:
                    if len(error) >= 3:
                        field_name = error[0]
                        account_id = error[1]  # Connection ID (account_id)
                        error_message = error[2]

                        click.echo(f"{indent}    • {field_name}: {error_message}")
                        if account_id is not None:
                            click.echo(f"{indent}      Connection ID: {account_id}")
            else:
                click.echo(f"{indent}  • {config_error}")


@inject
async def start_single_recipe(
    recipe_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Start a single recipe by ID"""
    spinner = Spinner(f"Starting recipe {recipe_id}")
    spinner.start()

    try:
        recipe_start_response = await workato_api_client.recipes_api.start_recipe(
            recipe_id
        )
    finally:
        elapsed = spinner.stop()

    # Check if the API response indicates success
    if recipe_start_response.success:
        click.echo(f"✅ Recipe {recipe_id} started successfully ({elapsed:.1f}s)")
    else:
        # API returned success: false - extract error message
        click.echo(f"❌ Recipe {recipe_id} failed to start ({elapsed:.1f}s)")

        # Handle detailed error information
        _display_recipe_errors(recipe_start_response=recipe_start_response)
        return


@inject
async def start_project_recipes(
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Start all recipes in the current project"""
    # Get project folder ID from meta file
    meta_data = config_manager.load_config()
    folder_id = meta_data.folder_id

    if not folder_id:
        click.echo("❌ No project configured. Please run 'workato init' first.")
        return

    click.echo(f"🚀 Starting all recipes in current project (folder {folder_id})")
    await start_folder_recipes(folder_id)


@inject
async def start_folder_recipes(
    folder_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Start all recipes in a specific folder"""
    # First, get all recipes in the folder using the assets API
    recipe_assets = await get_folder_recipe_assets(folder_id)

    if not recipe_assets:
        click.echo(f"ℹ️  No recipes found in folder {folder_id}")
        return

    click.echo(f"📋 Found {len(recipe_assets)} recipe(s) to start")
    click.echo()

    # Track results
    started_count = 0
    failed_count = 0
    failed_recipes: list[Asset] = []

    # Start each recipe
    for recipe in recipe_assets:
        recipe_id = recipe.id
        recipe_name = recipe.name

        response = await workato_api_client.recipes_api.start_recipe(recipe_id)

        if response.success:
            click.echo(f"  ✅ {recipe_name} (ID: {recipe_id})")
            started_count += 1
        else:
            # success is false or missing - show detailed error
            click.echo(f"  ❌ {recipe_name} (ID: {recipe_id})")
            _display_recipe_errors(response, indent="    ")
            failed_count += 1
            failed_recipes.append(recipe)

    # Summary
    click.echo()
    click.echo(f"📊 Results: {started_count} started, {failed_count} failed")

    if failed_recipes:
        click.echo()
        click.echo("❌ Failed recipes (you can retry individually):")
        for recipe in failed_recipes:
            click.echo(f"  • {recipe.name} (ID: {recipe.id})")
            click.echo(f"    Retry: workato recipes start --id {recipe.id}")


@inject
async def stop_single_recipe(
    recipe_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Stop a single recipe by ID"""
    spinner = Spinner(f"Stopping recipe {recipe_id}")
    spinner.start()

    try:
        await workato_api_client.recipes_api.stop_recipe(recipe_id)
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ Recipe {recipe_id} stopped successfully ({elapsed:.1f}s)")


@inject
async def stop_project_recipes(
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Stop all recipes in the current project"""
    # Get project folder ID from meta file
    meta_data = config_manager.load_config()
    folder_id = meta_data.folder_id

    if not folder_id:
        click.echo("❌ No project configured. Please run 'workato init' first.")
        return

    click.echo(f"🚀 Stopping all recipes in current project (folder {folder_id})")
    await stop_folder_recipes(folder_id)


@inject
async def stop_folder_recipes(
    folder_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Stop all recipes in a specific folder"""
    # First, get all recipes in the folder using the assets API
    recipes = await get_folder_recipe_assets(folder_id)

    if not recipes:
        click.echo(f"ℹ️  No recipes found in folder {folder_id}")
        return

    click.echo(f"📋 Found {len(recipes)} recipe(s) to stop")
    click.echo()

    # Track results
    stopped_count = 0

    # Stop each recipe
    for recipe in recipes:
        recipe_id = recipe.id
        recipe_name = recipe.name

        await workato_api_client.recipes_api.stop_recipe(recipe_id)

        click.echo(f"  ✅ {recipe_name} (ID: {recipe_id})")
        stopped_count += 1

    # Summary
    click.echo()
    click.echo(f"📊 Results: {stopped_count} stopped")


@inject
async def get_folder_recipe_assets(
    folder_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> list[Asset]:
    """Get all recipes in a folder using the assets API"""
    spinner = Spinner(f"Fetching recipes in folder {folder_id}")
    spinner.start()

    try:
        # Use existing utility function
        assets_response = await workato_api_client.export_api.list_assets_in_folder(
            folder_id=folder_id,
        )
    finally:
        elapsed = spinner.stop()

    # Filter for recipe assets
    recipes = [
        asset for asset in assets_response.result.assets if asset.type == "recipe"
    ]

    click.echo(
        f"🔍 Found {len(recipes)} recipe(s) in folder {folder_id} ({elapsed:.1f}s)"
    )

    return recipes


@inject
async def get_all_recipes_paginated(
    folder_id: int,
    adapter_names_all: str | None = None,
    adapter_names_any: str | None = None,
    order: str | None = None,
    running: bool | None = None,
    since_id: int | None = None,
    stopped_after: str | None = None,
    stop_cause: str | None = None,
    updated_after: str | None = None,
    include_tags: str | None = None,
    exclude_code: bool | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> list[Recipe]:
    """Get all recipes in a folder with automatic pagination"""
    all_recipes = []
    page = 1
    while True:
        response = await workato_api_client.recipes_api.list_recipes(
            adapter_names_all=adapter_names_all,
            adapter_names_any=adapter_names_any,
            folder_id=folder_id,
            order=order,
            page=page,
            per_page=100,
            running=running,
            since_id=since_id,
            stopped_after=datetime.fromisoformat(stopped_after)
            if stopped_after
            else None,
            stop_cause=stop_cause,
            updated_after=datetime.fromisoformat(updated_after)
            if updated_after
            else None,
            includes=[tag.strip() for tag in include_tags.split(",")]
            if include_tags
            else None,
            exclude_code=exclude_code if exclude_code else None,
        )

        all_recipes.extend(response.items)

        # If we got less than 100 results, we're on the last page
        if len(response.items) < 100:
            break

        page += 1

    return all_recipes


@inject
async def get_recipes_recursive(
    folder_id: int,
    visited_folders: set | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> list[Recipe]:
    """Recursively get all recipes in a folder and its subfolders"""
    if visited_folders is None:
        visited_folders = set()

    # Prevent infinite loops in case of circular folder references
    if folder_id in visited_folders:
        return []

    visited_folders.add(folder_id)

    all_recipes = []

    # Get ALL recipes in current folder with pagination
    spinner = Spinner(f"Fetching recipes in folder {folder_id}")
    spinner.start()

    try:
        folder_recipes = await get_all_recipes_paginated(
            folder_id=folder_id,
            exclude_code=True,
        )
        all_recipes.extend(folder_recipes)

    finally:
        elapsed = spinner.stop()

    click.echo(
        f"📂 Found {len(folder_recipes)} recipe(s) in folder {folder_id} "
        f"({elapsed:.1f}s)"
    )

    # Get ALL subfolders and recursively process them with pagination
    spinner = Spinner(f"Fetching subfolders in folder {folder_id}")
    spinner.start()

    try:
        folders = []
        page = 1
        while True:
            folder_response = await workato_api_client.folders_api.list_folders(
                parent_id=folder_id,
                page=page,
                per_page=100,
            )

            folders.extend(folder_response)

            # If we got less than 100 results, we're on the last page
            if len(folder_response) < 100:
                break

            page += 1

    finally:
        elapsed = spinner.stop()

    folder_count = len(folders)
    click.echo(
        f"📁 Found {folder_count} subfolder(s) in folder {folder_id} ({elapsed:.1f}s)"
    )

    # Recursively get recipes from each subfolder
    for folder in folders:
        subfolder_recipes = await get_recipes_recursive(
            folder.id, visited_folders, workato_api_client
        )
        all_recipes.extend(subfolder_recipes)

    return all_recipes


def display_recipe_summary(recipe: Recipe) -> None:
    """Display a summary of a recipe"""
    name = recipe.name
    recipe_id = recipe.id
    running = recipe.running

    status_icon = "▶️" if running else "⏸️"
    status_text = "Running" if running else "Stopped"

    click.echo(f"  {status_icon} {name}")
    click.echo(f"    🆔 ID: {recipe_id}")
    click.echo(f"    📊 Status: {status_text}")
    click.echo(f"    📱 Trigger App: {recipe.trigger_application}")

    # Show action applications if available
    if recipe.action_applications:
        apps_display = ", ".join(recipe.action_applications)
        click.echo(f"    🔧 Action Apps: {apps_display}")

    # Show config information (applications/connections configured)
    if recipe.config:
        config_apps = []
        for config_item in recipe.config:
            if config_item.keyword == "application":
                name = config_item.name or ""

                # Show account_id if present and not null
                account_info = ""
                if config_item.account_id:
                    account_info = f" (Account: {config_item.account_id})"

                config_apps.append(f"{name}{account_info}")

        if config_apps:
            config_display = ", ".join(config_apps)
            click.echo(f"    ⚙️  Config Apps: {config_display}")

    click.echo(f"    📁 Folder ID: {recipe.folder_id}")

    # Show job statistics if available
    succeeded = recipe.job_succeeded_count
    failed = recipe.job_failed_count
    if succeeded > 0 or failed > 0:
        click.echo(f"    📊 Jobs: {succeeded} succeeded, {failed} failed")

    # Show last run information if available
    if recipe.last_run_at:
        click.echo(f"    🕐 Last Run: {recipe.last_run_at.isoformat()}")

    # Show stopped time if recipe is stopped
    if not running and recipe.stopped_at:
        click.echo(f"    ⏹️  Stopped: {recipe.stopped_at.isoformat()}")

    # Show stop cause if recipe is stopped and has a cause
    if not running and recipe.stop_cause:
        stop_cause = recipe.stop_cause.replace("_", " ").title()
        click.echo(f"    ⚠️  Stop Cause: {stop_cause}")

    # Show creation date if available
    if recipe.created_at:
        click.echo(f"    📅 Created: {recipe.created_at.isoformat()}")

    # Show author information if available
    if recipe.author_name:
        click.echo(f"    👤 Author: {recipe.author_name}")

    if recipe.tags:
        tags_display = ", ".join(recipe.tags)
        click.echo(f"    🏷️  Tags: {tags_display}")

    # Show description if available (truncated)
    if recipe.description:
        description = recipe.description
        if len(description) > 80:
            description = description[:77] + "..."
        click.echo(f"    📝 Description: {description}")


@recipes.command()
@click.argument("recipe_id", type=int)
@click.option(
    "--adapter-name",
    required=True,
    help="The internal name of the connector (e.g., box, salesforce)",
)
@click.option(
    "--connection-id", required=True, type=int, help="The ID of the connection to use"
)
@inject
@handle_api_exceptions
async def update_connection(
    recipe_id: int,
    adapter_name: str,
    connection_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Update a connection for a specific connector in a recipe"""

    spinner = Spinner("Updating recipe connection...")
    spinner.start()

    try:
        await workato_api_client.recipes_api.update_recipe_connection(
            recipe_id=recipe_id,
            recipe_connection_update_request=RecipeConnectionUpdateRequest(
                adapter_name=adapter_name,
                connection_id=connection_id,
            ),
        )

    finally:
        elapsed = spinner.stop()

    click.echo(
        f"✅ Successfully updated connection for recipe {recipe_id} ({elapsed:.1f}s)"
    )
    click.echo(f"   🔗 Connector: {adapter_name}")
    click.echo(f"   🆔 Connection ID: {connection_id}")
