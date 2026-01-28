import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform_cli import Workato
from workato_platform_cli.cli.containers import Container
from workato_platform_cli.cli.utils import Spinner
from workato_platform_cli.cli.utils.config import ConfigManager
from workato_platform_cli.cli.utils.exception_handler import (
    handle_api_exceptions,
    handle_cli_exceptions,
)
from workato_platform_cli.client.workato_api.models.asset import Asset


@click.command()
@click.option(
    "--folder-id",
    type=int,
    help="Folder ID (uses current project folder if not specified)",
)
@handle_cli_exceptions
@inject
@handle_api_exceptions
async def assets(
    folder_id: int | None = None,
    config_manager: ConfigManager = Provide[Container.config_manager],
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """List project assets (data tables, custom connectors, properties, etc.)"""

    # Get folder ID from parameter or meta file
    if not folder_id:
        meta_data = config_manager.load_config()
        folder_id = meta_data.folder_id

        if not folder_id:
            click.echo("❌ No folder ID provided and no project configured.")
            click.echo("💡 Either specify --folder-id or run 'workato init' first.")
            return
    spinner = Spinner(f"Fetching assets for folder {folder_id}")
    spinner.start()

    try:
        response = await workato_api_client.export_api.list_assets_in_folder(
            folder_id=folder_id,
        )
    finally:
        elapsed = spinner.stop()

    assets = response.result.assets

    click.echo(f"📁 Project Assets ({len(assets)} total) - ({elapsed:.1f}s)")
    click.echo(f"  📋 Folder ID: {folder_id}")

    if not assets:
        click.echo("  ℹ️  No assets found in this project")
        return

    # Group assets by type
    asset_groups: dict[str, list[Asset]] = {}
    for asset in assets:
        asset_type = asset.type
        if asset_type not in asset_groups:
            asset_groups[asset_type] = []
        asset_groups[asset_type].append(asset)

    # Display assets by type
    for asset_type, type_assets in asset_groups.items():
        click.echo(
            f"\n  📦 {asset_type.replace('_', ' ').title()} ({len(type_assets)} items)"
        )

        for asset in type_assets:
            name = asset.name
            asset_id = asset.id

            # Basic info
            click.echo(f"    • {name}")

            if asset_id:
                click.echo(f"      🆔 ID: {asset_id}")

            click.echo()
