from pathlib import Path

import aiohttp
import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform import Workato
from workato_platform.cli.commands.projects.project_manager import ProjectManager
from workato_platform.cli.containers import Container
from workato_platform.cli.utils import Spinner
from workato_platform.cli.utils.config import ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions
from workato_platform.client.workato_api.models.api_collection import ApiCollection
from workato_platform.client.workato_api.models.api_collection_create_request import (
    ApiCollectionCreateRequest,
)
from workato_platform.client.workato_api.models.api_endpoint import ApiEndpoint
from workato_platform.client.workato_api.models.open_api_spec import OpenApiSpec


@click.group()
def api_collections() -> None:
    """Manage API collections (generates recipes and endpoints from OpenAPI specs)"""
    pass


@api_collections.command()
@click.option("--name", help="Name for the API collection (defaults to project name)")
@click.option(
    "--format",
    type=click.Choice(["json", "yaml", "url"]),
    required=True,
    help="Format of the OpenAPI spec",
)
@click.option(
    "--content",
    required=True,
    help="Path to the spec file (for json/yaml) or URL (for url format)",
)
@click.option(
    "--proxy-connection-id",
    type=int,
    help="ID of the proxy connection to use",
)
@inject
@handle_api_exceptions
async def create(
    name: str,
    format: str,
    content: str,
    proxy_connection_id: int | None = None,
    config_manager: ConfigManager = Provide[Container.config_manager],
    project_manager: ProjectManager = Provide[Container.project_manager],
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Create a new API collection from OpenAPI spec (creates recipes and endpoints)"""

    # Load project metadata
    meta_data = config_manager.load_config()
    project_id = meta_data.project_id
    if not project_id:
        click.echo("❌ No project configured. Please run 'workato init' first.")
        return

    # Use project name as default if name not provided
    if not name:
        name = meta_data.project_name or "API Collection"

    # Prepare OpenAPI spec content
    openapi_spec = {"format": format}

    if format in ["json", "yaml"]:
        # Read content from file
        content_path = Path(content)
        if not content_path.exists():
            click.echo(f"❌ File not found: {content}")
            return

        try:
            with open(content_path) as f:
                openapi_spec["content"] = f.read()
        except (FileNotFoundError, PermissionError, OSError) as e:
            click.echo(f"❌ Failed to read file {content}: {str(e)}")
            return
    else:  # url format, download the file
        async with aiohttp.ClientSession() as session:
            response = await session.get(content)
            openapi_spec["content"] = await response.text()
            openapi_spec["format"] = "json"

    # Create API collection
    spinner = Spinner(f"Creating API collection '{name}'")
    spinner.start()

    try:
        collection_response = (
            await workato_api_client.api_platform_api.create_api_collection(
                api_collection_create_request=ApiCollectionCreateRequest(
                    name=name,
                    project_id=project_id,
                    proxy_connection_id=proxy_connection_id,
                    openapi_spec=OpenApiSpec.model_validate(openapi_spec),
                ),
            )
        )
        collection_id = collection_response.id
    finally:
        elapsed = spinner.stop()

    click.echo(
        f"✅ API collection '{name}' ({collection_id}) created successfully "
        f"({elapsed:.1f}s)"
    )
    click.echo()

    # Display detailed collection information from create response
    # Handle different possible response structures (result, data, or direct)
    display_collection_summary(collection_response)

    click.echo()
    click.echo("🎉 Generated from OpenAPI spec:")
    click.echo("  • API endpoints for each path/method combination")
    click.echo("  • Workato recipes implementing the business logic")
    click.echo("  • Request/response schemas and validation")
    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  • Review generated recipes in your project")
    click.echo(
        "  • Enable endpoints: workato api-collections enable-endpoint "
        "--api-endpoint-id <ID>"
    )
    click.echo("  • Test API endpoints with your API client")

    # Handle post-creation sync
    await project_manager.handle_post_api_sync()


@api_collections.command(name="list")
@click.option("--page", default=1, type=int, help="Page number (default: 1)")
@click.option(
    "--per-page",
    default=100,
    type=int,
    help="Items per page (default: 100, max: 100)",
)
@inject
@handle_api_exceptions
async def list_collections(
    page: int,
    per_page: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """List API collections"""

    # Validate per_page limit
    if per_page > 100:
        click.echo("❌ Maximum per-page limit is 100")
        return

    spinner = Spinner(f"Fetching API collections (page {page})")
    spinner.start()

    try:
        collections = await workato_api_client.api_platform_api.list_api_collections(
            page=page,
            per_page=per_page,
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"📚 API Collections ({elapsed:.1f}s)")
    click.echo(f"  📄 Page {page} ({len(collections)} collections)")

    if not collections:
        click.echo("  ℹ️  No API collections found")
        if page > 1:
            click.echo("  💡 Try a lower page number")
        return

    click.echo()

    # Display collections
    for collection in collections:
        display_collection_summary(collection=collection)
        click.echo()

    # Show pagination info if more than per_page results might exist
    if len(collections) == per_page:
        click.echo("💡 Pagination:")
        click.echo(f"  • Next page: workato api-collections list --page {page + 1}")

    if page > 1:
        click.echo(f"  • Previous page: workato api-collections list --page {page - 1}")

    click.echo()
    click.echo("💡 Commands:")
    click.echo(
        "  • List endpoints: workato api-collections list-endpoints "
        "--api-collection-id <ID>"
    )
    click.echo(
        "  • Enable endpoint: workato api-collections enable-endpoint "
        "--api-endpoint-id <ID>"
    )


@api_collections.command(name="list-endpoints")
@click.option(
    "--api-collection-id", required=True, type=int, help="ID of the API collection"
)
@inject
@handle_api_exceptions
async def list_endpoints(
    api_collection_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """List endpoints for an API collection"""
    spinner = Spinner(f"Fetching endpoints for collection {api_collection_id}")
    spinner.start()

    try:
        endpoints: list[ApiEndpoint] = []
        page = 1
        while True:
            page_endpoints = (
                await workato_api_client.api_platform_api.list_api_endpoints(
                    api_collection_id=api_collection_id,
                    page=page,
                    per_page=100,
                )
            )
            endpoints.extend(page_endpoints)
            if len(page_endpoints) < 100:
                break
            page += 1

    finally:
        elapsed = spinner.stop()

    if not endpoints:
        click.echo("  ℹ️  No endpoints found for this collection")
        return

    # Parse the response - API returns a list directly
    total_count = len(endpoints)

    click.echo(
        f"🔗 {total_count} API Endpoints for API Collection {api_collection_id} "
        f"({elapsed:.1f}s)"
    )
    click.echo(
        f"  🌐 Base URL: {endpoints[0].url.removesuffix(f'/{endpoints[0].path}')}"
    )

    click.echo()

    # Display endpoints
    for endpoint in endpoints:
        display_endpoint_summary(endpoint=endpoint)
        click.echo()

    click.echo()
    click.echo("💡 Commands:")
    click.echo(
        "  • Enable endpoint: workato api-collections enable-endpoint "
        "--api-endpoint-id <ID>"
    )
    click.echo(
        "  • Enable all endpoints: workato api-collections enable-endpoint "
        "--api-collection-id <ID> --all"
    )


@api_collections.command(name="enable-endpoint")
@click.option("--api-endpoint-id", type=int, help="ID of the API endpoint to enable")
@click.option(
    "--api-collection-id", type=int, help="ID of the API collection (use with --all)"
)
@click.option(
    "--all",
    is_flag=True,
    help="Enable all endpoints in the collection (requires --api-collection-id)",
)
@handle_api_exceptions
async def enable_endpoint(
    api_endpoint_id: int,
    api_collection_id: int,
    all: bool,
) -> None:
    """Enable an API endpoint or all endpoints in a collection"""

    # Validate parameter combinations
    if all and not api_collection_id:
        click.echo("❌ --all flag requires --api-collection-id")
        return

    if all and api_endpoint_id:
        click.echo("❌ Cannot specify both --api-endpoint-id and --all")
        return

    if not all and not api_endpoint_id:
        click.echo(
            "❌ Must specify either --api-endpoint-id or --all with --api-collection-id"
        )
        return

    if all:
        # Enable all endpoints in the collection
        await enable_all_endpoints_in_collection(api_collection_id)
    else:
        # Enable single endpoint
        await enable_api_endpoint(api_endpoint_id)


@inject
async def enable_all_endpoints_in_collection(
    api_collection_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Enable all endpoints in an API collection"""
    spinner = Spinner(f"Fetching endpoints for collection {api_collection_id}")
    spinner.start()

    # First, get all endpoints in the collection
    try:
        endpoints: list[ApiEndpoint] = []
        page = 1
        while True:
            page_endpoints = (
                await workato_api_client.api_platform_api.list_api_endpoints(
                    api_collection_id=api_collection_id,
                    page=page,
                    per_page=100,
                )
            )
            endpoints.extend(page_endpoints)
            if len(page_endpoints) < 100:
                break
            page += 1

    finally:
        elapsed = spinner.stop()

    if not endpoints:
        click.echo(f"❌ No endpoints found for collection {api_collection_id}")
        return

    # Filter for disabled endpoints
    disabled_endpoints = [ep for ep in endpoints if not ep.active]

    if not disabled_endpoints:
        click.echo(
            f"✅ All endpoints in collection {api_collection_id} are already enabled"
        )
        return

    click.echo(
        f"📋 Found {len(disabled_endpoints)} disabled endpoints in "
        f"collection {api_collection_id}"
    )
    click.echo("💡 Enabling all disabled endpoints:")
    for ep in disabled_endpoints:
        method = ep.method.upper()
        click.echo(f"  • {ep.name} ({method} {ep.url})")
    click.echo()

    # Enable each disabled endpoint
    success_count = 0
    failed_endpoints = []

    for endpoint in disabled_endpoints:
        endpoint_id = endpoint.id
        endpoint_name = endpoint.name

        try:
            spinner = Spinner(f"Enabling {endpoint_name}")
            spinner.start()

            try:
                await workato_api_client.api_platform_api.enable_api_endpoint(
                    api_endpoint_id=endpoint_id
                )
                success_count += 1
            finally:
                elapsed = spinner.stop()

            click.echo(f"  ✅ {endpoint_name} enabled ({elapsed:.1f}s)")

        except Exception as e:
            # Keep broad exception handling here since we want to continue with other
            # endpoints even if one fails, and the outer function has
            # @handle_api_exceptions for overall errors
            failed_endpoints.append((endpoint_name, str(e)))
            click.echo(f"  ❌ Failed to enable {endpoint_name}: {str(e)}")

    # Summary
    click.echo()
    click.echo("📊 Results:")
    click.echo(f"  ✅ Successfully enabled: {success_count}")
    if failed_endpoints:
        click.echo(f"  ❌ Failed: {len(failed_endpoints)}")
        for name, error in failed_endpoints:
            click.echo(f"    • {name}: {error}")

    if success_count > 0:
        click.echo()
        click.echo("💡 Next steps:")
        click.echo("  • Test the enabled endpoints with API calls")
        click.echo("  • Monitor endpoint usage and performance")


@inject
async def enable_api_endpoint(
    api_endpoint_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Enable an API endpoint using the Workato API"""
    spinner = Spinner(f"Enabling API endpoint {api_endpoint_id}")
    spinner.start()

    try:
        await workato_api_client.api_platform_api.enable_api_endpoint(
            api_endpoint_id=api_endpoint_id
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ API endpoint enabled successfully ({elapsed:.1f}s)")
    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  • Test the endpoint with API calls")
    click.echo("  • Monitor endpoint usage and performance")
    click.echo("  • Configure rate limiting if needed")


def display_endpoint_summary(endpoint: ApiEndpoint) -> None:
    """Display a summary of an API endpoint"""
    name = endpoint.name
    endpoint_id = endpoint.id

    # Try different field names for enabled/active status
    enabled = endpoint.active

    status_icon = "✅" if enabled else "❌"
    status_text = "Enabled" if enabled else "Disabled"

    click.echo(f"  {status_icon} {name}")
    click.echo(f"    🆔 ID: {endpoint_id}")
    click.echo(f"    🔗 Method: {endpoint.method}")
    click.echo(f"    📍 Path: {endpoint.url}")
    click.echo(f"    📊 Status: {status_text}")

    # Show flow ID if available (recipe connection)
    if endpoint.flow_id:
        click.echo(f"    🔄 Recipe ID: {endpoint.flow_id}")

    # Show additional metadata if available
    click.echo(f"    🕐 Created: {endpoint.created_at.strftime('%Y-%m-%d')}")

    # Show legacy status if available
    if endpoint.legacy:
        click.echo(f"    📜 Legacy: {'Yes' if endpoint.legacy else 'No'}")

    # Show collection info if available
    click.echo(f"    📚 Collection ID: {endpoint.api_collection_id}")


def display_collection_summary(collection: ApiCollection) -> None:
    """Display a summary of an API collection"""
    name = collection.name or "Unknown"
    collection_id = collection.id or "Unknown"

    click.echo(f"  📚 {name}")
    click.echo(f"    🆔 ID: {collection_id}")
    click.echo(f"    📁 Project ID: {collection.project_id}")

    url = collection.url
    if len(url) > 60:
        url = url[:57] + "..."
    click.echo(f"    🌐 API URL: {url}")
    spec_url = collection.api_spec_url
    if len(spec_url) > 60:
        spec_url = spec_url[:57] + "..."
    click.echo(f"    📄 Spec URL: {spec_url}")

    click.echo(f"    🕐 Created: {collection.created_at.strftime('%Y-%m-%d')}")

    if collection.updated_at and collection.updated_at != collection.created_at:
        click.echo(f"    🔄 Updated: {collection.updated_at.strftime('%Y-%m-%d')}")
