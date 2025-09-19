import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform import Workato
from workato_platform.cli.containers import Container
from workato_platform.cli.utils import Spinner
from workato_platform.cli.utils.config import ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions
from workato_platform.client.workato_api.models.upsert_project_properties_request import (  # noqa: E501
    UpsertProjectPropertiesRequest,
)


@click.group()
def properties() -> None:
    """Manage project properties"""
    pass


@properties.command(name="list")
@click.option("--prefix", required=True, help="Property name prefix to filter by")
@click.option(
    "--project-id",
    type=int,
    help="Project ID to get properties for. Defaults to current project.",
)
@inject
@handle_api_exceptions
async def list_properties(
    prefix: str,
    project_id: int | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """List project properties with a given prefix"""

    # Use provided project_id or get from config
    if not project_id:
        config = config_manager.load_config()
        project_id = config.project_id

    if not project_id:
        click.echo("❌ No project ID provided and no project configured.")
        click.echo("💡 Use --project-id <ID> or run 'workato init' first.")
        return

    spinner = Spinner(
        f"Fetching properties with prefix '{prefix}' for project {project_id}"
    )
    spinner.start()

    try:
        properties = await workato_api_client.properties_api.list_project_properties(
            prefix=prefix,
            project_id=project_id,
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"📋 Properties ({len(properties)} found) - ({elapsed:.1f}s)")
    click.echo(f"  🔍 Prefix: {prefix}")
    click.echo(f"  📁 Project ID: {project_id}")

    if not properties:
        click.echo("  ℹ️  No properties found")
        return

    click.echo()

    # Display properties as a table
    max_key_length = max(len(key) for key in properties) if properties else 0
    for key, value in properties.items():
        click.echo(f"  {key:<{max_key_length}} = {value}")

    click.echo()
    click.echo("💡 Commands:")
    click.echo("  • Update properties: workato properties upsert --project-id <ID>")


@properties.command(name="upsert")
@click.option("--project-id", type=int, help="Project ID to upsert properties for")
@click.option(
    "--property",
    "property_pairs",
    multiple=True,
    help="Property in key=value format (can be used multiple times)",
)
@inject
@handle_api_exceptions
async def upsert_properties(
    project_id: int | None = None,
    property_pairs: tuple[str, ...] = (),
    workato_api_client: Workato = Provide[Container.workato_api_client],
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Upsert (create or update) project properties"""

    # Use provided project_id or get from config
    if not project_id:
        config = config_manager.load_config()
        project_id = config.project_id

    if not project_id:
        click.echo("❌ No project ID provided and no project configured.")
        click.echo("💡 Use --project-id <ID> or run 'workato init' first.")
        return

    properties = {}

    # Parse properties from command line
    if property_pairs:
        for pair in property_pairs:
            if "=" not in pair:
                click.echo(f"❌ Invalid property format: {pair}")
                click.echo("💡 Use format: key=value")
                return
            key, value = pair.split("=", 1)
            properties[key] = value

    if not properties:
        click.echo("❌ No properties provided")
        click.echo("💡 Examples:")
        click.echo(
            "  workato properties upsert --property admin_email=user@example.com"
        )
        return

    # Validate property limits
    for key, value in properties.items():
        if len(key) > 100:
            click.echo(f"❌ Property name too long (max 100 chars): {key}")
            return
        if len(value) > 1024:
            click.echo(f"❌ Property value too long (max 1,024 chars): {key}")
            return

    spinner = Spinner(
        f"Upserting {len(properties)} properties for project {project_id}"
    )
    spinner.start()

    try:
        request = UpsertProjectPropertiesRequest(properties=properties)

        response = await workato_api_client.properties_api.upsert_project_properties(
            project_id=project_id,
            upsert_project_properties_request=request,
        )
    finally:
        elapsed = spinner.stop()

    if response.success:
        click.echo(f"✅ Properties upserted successfully ({elapsed:.1f}s)")
        click.echo(f"  📁 Project ID: {project_id}")
        click.echo(f"  📝 Properties updated: {len(properties)}")

        click.echo()
        click.echo("Updated properties:")
        max_key_length = max(len(key) for key in properties)
        for key, value in properties.items():
            click.echo(f"  {key:<{max_key_length}} = {value}")

    else:
        click.echo(f"❌ Failed to upsert properties ({elapsed:.1f}s)")

    click.echo()
    click.echo("💡 Commands:")
    click.echo("  • List properties: workato properties list --prefix <prefix>")
