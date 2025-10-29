import json
import re

from typing import Any

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform_cli import Workato
from workato_platform_cli.cli.commands.projects.project_manager import ProjectManager
from workato_platform_cli.cli.containers import Container
from workato_platform_cli.cli.utils import Spinner
from workato_platform_cli.cli.utils.config import ConfigManager
from workato_platform_cli.cli.utils.exception_handler import handle_api_exceptions
from workato_platform_cli.client.workato_api.models.data_table import DataTable
from workato_platform_cli.client.workato_api.models.data_table_column_request import (
    DataTableColumnRequest,
)
from workato_platform_cli.client.workato_api.models.data_table_create_request import (
    DataTableCreateRequest,
)


@click.group(name="data-tables")
def data_tables() -> None:
    """Manage data tables"""
    pass


@data_tables.command(name="list")
@inject
@handle_api_exceptions
async def list_data_tables(
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """List all data tables using the Workato API"""
    spinner = Spinner("Fetching data tables")
    spinner.start()

    try:
        response = await workato_api_client.data_tables_api.list_data_tables()
        tables = response.data
    finally:
        elapsed = spinner.stop()

    click.echo(f"📊 Data Tables ({len(tables)} found) - ({elapsed:.1f}s)")

    if not tables:
        click.echo("  ℹ️  No data tables found")
        click.echo(
            "  💡 Create one: workato data-tables create --name 'Table Name' "
            "--schema-json '[...]'"
        )
        return

    click.echo()

    # Display tables
    for table in tables:
        display_table_summary(table)
        click.echo()

    click.echo("💡 Commands:")
    click.echo(
        "  • Create table: workato data-tables create --name 'Table Name' "
        "--schema-json '[...]'"
    )


@data_tables.command(name="create")
@click.option("--name", required=True, help="Name of the data table")
@click.option(
    "--folder-id",
    type=int,
    help="Folder ID (uses current project folder if not specified)",
)
@click.option(
    "--schema-json", required=True, help="JSON string containing table schema"
)
@inject
@handle_api_exceptions
async def create_data_table(
    name: str,
    schema_json: str,
    folder_id: int | None = None,
    config_manager: ConfigManager = Provide[Container.config_manager],
) -> None:
    """Create a new data table with schema definition

    Schema can be provided via --schema-json (JSON string).

    Schema format example:
    [
        {
            "name": "id",
            "type": "integer",
            "optional": false,
            "hint": "Unique identifier"
        },
        {
            "name": "name",
            "type": "string",
            "optional": false,
            "default_value": "Unknown"
        },
        {
            "name": "created_at",
            "type": "date_time",
            "optional": true
        }
    ]
    """

    if not schema_json:
        click.echo("❌ Schema is required. Provide --schema-json")
        return

    # Get folder ID from parameter or meta file
    if not folder_id:
        meta_data = config_manager.load_config()

        if not meta_data.folder_id:
            click.echo("❌ No folder ID provided and no project configured.")
            click.echo("💡 Either specify --folder-id or run 'workato init' first.")
            return

        folder_id = meta_data.folder_id

    # Parse schema
    try:
        schema = json.loads(schema_json)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON in schema: {str(e)}")
        return

    if not isinstance(schema, list):
        click.echo("❌ Schema must be an array of column definitions")
        return

    # Validate schema
    validation_errors = validate_schema(schema)
    if validation_errors:
        click.echo("❌ Schema validation failed:")
        for error in validation_errors:
            click.echo(f"  • {error}")
        return

    # Create data table
    await create_table(name, folder_id, schema)


@inject
@handle_api_exceptions
async def create_table(
    name: str,
    folder_id: int,
    schema: list[DataTableColumnRequest],
    workato_api_client: Workato = Provide[Container.workato_api_client],
    project_manager: ProjectManager = Provide[Container.project_manager],
) -> None:
    """Create a data table using the Workato API"""
    spinner = Spinner(f"Creating data table '{name}'")
    spinner.start()

    try:
        response = await workato_api_client.data_tables_api.create_data_table(
            data_table_create_request=DataTableCreateRequest(
                name=name,
                folder_id=folder_id,
                var_schema=schema,
            )
        )
        table_data = response.data
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ Data table created successfully ({elapsed:.1f}s)")

    # Display table details
    click.echo(f"  📄 Name: {table_data.name}")
    click.echo(f"  🆔 ID: {table_data.id}")
    click.echo(f"  📁 Folder ID: {table_data.folder_id}")

    # Show schema summary
    column_count = len(table_data.var_schema)
    column_names = [col.name for col in table_data.var_schema[:5]]
    if column_count <= 5:
        click.echo(f"  📊 Columns: {', '.join(column_names)}")
    else:
        click.echo(f"  📊 Columns: {', '.join(column_names)} +{column_count - 5} more")

    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  • Add data to the table via recipes or API")
    click.echo("  • Configure table permissions if needed")
    click.echo("  • Use table in recipe actions and triggers")

    # Handle post-creation sync
    await project_manager.handle_post_api_sync()


def validate_schema(schema: list[dict[str, Any]]) -> list[str]:
    """Validate schema structure and field types"""
    errors: list[str] = []
    valid_types = [
        "boolean",
        "date",
        "date_time",
        "integer",
        "number",
        "string",
        "file",
        "relation",
    ]
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

    if not schema:
        errors.append("Schema cannot be empty")
        return errors

    for i, column in enumerate(schema):
        # Check required fields
        if "name" not in column:
            errors.append(f"Column {i + 1}: 'name' is required")
        elif not isinstance(column["name"], str) or not column["name"].strip():
            errors.append(f"Column {i + 1}: 'name' must be a non-empty string")

        if "type" not in column:
            errors.append(f"Column {i + 1}: 'type' is required")
        elif column["type"] not in valid_types:
            errors.append(f"Column {i + 1}: 'type' must be one of {valid_types}")

        if "optional" not in column:
            errors.append(f"Column {i + 1}: 'optional' is required")
        elif not isinstance(column["optional"], bool | int) or column[
            "optional"
        ] not in [True, False, 0, 1]:
            errors.append(f"Column {i + 1}: 'optional' must be true, false, 0, or 1")

        # Check optional fields
        if "field_id" in column:
            field_id = column["field_id"]
            if not isinstance(field_id, str) or not re.match(uuid_pattern, field_id):
                errors.append(f"Column {i + 1}: 'field_id' must be a valid UUID format")

        if "hint" in column and not isinstance(column["hint"], str):
            errors.append(f"Column {i + 1}: 'hint' must be a string")

        if "multivalue" in column and not isinstance(column["multivalue"], bool):
            errors.append(f"Column {i + 1}: 'multivalue' must be a boolean")

        # Validate relation fields
        if column.get("type") == "relation":
            if "relation" not in column:
                errors.append(
                    f"Column {i + 1}: 'relation' object required for relation type"
                )
            else:
                relation = column["relation"]
                if not isinstance(relation, dict):
                    errors.append(f"Column {i + 1}: 'relation' must be an object")
                else:
                    if "field_id" not in relation:
                        errors.append(
                            f"Column {i + 1}: 'relation.field_id' is required"
                        )
                    if "table_id" in relation and not isinstance(
                        relation["table_id"], str
                    ):
                        errors.append(
                            f"Column {i + 1}: 'relation.table_id' must be a string"
                        )

        # Validate default_value matches type
        if "default_value" in column and "type" in column:
            default_val = column["default_value"]
            col_type = column["type"]

            type_checks = {
                "boolean": lambda x: isinstance(x, bool),
                "integer": lambda x: isinstance(x, int),
                "number": lambda x: isinstance(x, int | float),
                "string": lambda x: isinstance(x, str),
                "date": lambda x: isinstance(x, str),  # Should be date string
                "date_time": lambda x: isinstance(x, str),  # Should be datetime string
            }

            if col_type in type_checks and not type_checks[col_type](default_val):
                errors.append(
                    f"Column {i + 1}: 'default_value' type doesn't match column "
                    f"type '{col_type}'"
                )

    return errors


def display_table_summary(table: DataTable) -> None:
    """Display a summary of a data table"""
    name = table.name
    table_id = table.id
    folder_id = table.folder_id

    click.echo(f"  📊 {name}")
    click.echo(f"    🆔 ID: {table_id}")
    click.echo(f"    📁 Folder ID: {folder_id}")

    schema = table.var_schema
    column_count = len(schema)

    # Show column summary
    if column_count <= 5:
        column_names = [col.name for col in schema]
        click.echo(f"    📊 Columns ({column_count}): {', '.join(column_names)}")
    else:
        column_names = [col.name for col in schema[:3]]
        click.echo(
            f"    📊 Columns ({column_count}): {', '.join(column_names)} "
            f"+{column_count - 3} more"
        )

    # Show column types summary
    type_counts: dict[str, int] = {}
    for col in schema:
        col_type = col.type
        type_counts[col_type] = type_counts.get(col_type, 0) + 1

    type_summary = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
    click.echo(f"    🔧 Types: {type_summary}")

    # Show metadata if available
    if table.created_at:
        click.echo(
            f"    🕐 Created: {table.created_at.strftime('%Y-%m-%d')}"
        )  # Just the date part

    if table.updated_at:
        click.echo(
            f"    🔄 Updated: {table.updated_at.strftime('%Y-%m-%d')}"
        )  # Just the date part
