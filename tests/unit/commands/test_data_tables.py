"""Tests for the data-tables command."""

import json

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from workato_platform.cli.commands.data_tables import (
    create_data_table,
    create_table,
    list_data_tables,
    validate_schema,
)
from workato_platform.client.workato_api.models.data_table_column_request import (
    DataTableColumnRequest,
)


class TestListDataTablesCommand:
    """Test the list-data-tables command."""

    @pytest.fixture
    def mock_workato_client(self) -> AsyncMock:
        """Mock Workato API client."""
        client = AsyncMock()
        client.data_tables_api.list_data_tables = AsyncMock()
        return client

    @pytest.fixture
    def mock_data_tables_response(self) -> list[MagicMock]:
        """Mock data tables list response."""
        # Create mock tables with the required attributes
        table1 = MagicMock()
        table1.id = "table_123"
        table1.name = "Users Table"
        table1.folder_id = 456

        # Mock schema columns
        col1 = MagicMock()
        col1.name = "id"
        col1.type = "integer"
        col2 = MagicMock()
        col2.name = "name"
        col2.type = "string"
        col3 = MagicMock()
        col3.name = "email"
        col3.type = "string"

        table1.var_schema = [col1, col2, col3]
        table1.created_at = datetime(2024, 1, 1)
        table1.updated_at = datetime(2024, 1, 1)

        table2 = MagicMock()
        table2.id = "table_789"
        table2.name = "Products Table"
        table2.folder_id = 456

        # Mock schema columns for table 2
        col4 = MagicMock()
        col4.name = "product_id"
        col4.type = "integer"
        col5 = MagicMock()
        col5.name = "product_name"
        col5.type = "string"
        col6 = MagicMock()
        col6.name = "price"
        col6.type = "number"
        col7 = MagicMock()
        col7.name = "description"
        col7.type = "string"
        col8 = MagicMock()
        col8.name = "created_at"
        col8.type = "date_time"
        col9 = MagicMock()
        col9.name = "in_stock"
        col9.type = "boolean"

        table2.var_schema = [col4, col5, col6, col7, col8, col9]
        table2.created_at = datetime(2024, 1, 2)
        table2.updated_at = datetime(2024, 1, 2)

        return [table1, table2]

    @pytest.mark.asyncio
    async def test_list_data_tables_success(
        self,
        mock_workato_client: AsyncMock,
        mock_data_tables_response: list[MagicMock],
    ) -> None:
        """Test successful listing of data tables."""
        mock_response = MagicMock()
        mock_response.data = mock_data_tables_response
        mock_workato_client.data_tables_api.list_data_tables.return_value = (
            mock_response
        )

        with patch("workato_platform.cli.commands.data_tables.Spinner") as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 1.2
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.data_tables.display_table_summary"
            ) as mock_display:
                assert list_data_tables.callback
                await list_data_tables.callback(workato_api_client=mock_workato_client)

        mock_workato_client.data_tables_api.list_data_tables.assert_called_once()
        assert mock_display.call_count == 2  # Two tables in response

    @pytest.mark.asyncio
    async def test_list_data_tables_empty(self, mock_workato_client: AsyncMock) -> None:
        """Test listing when no data tables exist."""
        mock_response = MagicMock()
        mock_response.data = []
        mock_workato_client.data_tables_api.list_data_tables.return_value = (
            mock_response
        )

        with patch("workato_platform.cli.commands.data_tables.Spinner") as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 0.8
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.data_tables.click.echo"
            ) as mock_echo:
                assert list_data_tables.callback
                await list_data_tables.callback(workato_api_client=mock_workato_client)

        mock_echo.assert_any_call("  ℹ️  No data tables found")


class TestCreateDataTableCommand:
    """Test the create-data-table command."""

    @pytest.fixture
    def mock_workato_client(self) -> AsyncMock:
        """Mock Workato API client."""
        client = AsyncMock()
        client.data_tables_api.create_data_table = AsyncMock()
        return client

    @pytest.fixture
    def mock_config_manager(self) -> MagicMock:
        """Mock config manager."""
        config_manager = MagicMock()
        mock_config = MagicMock()
        mock_config.folder_id = 123
        config_manager.load_config.return_value = mock_config
        return config_manager

    @pytest.fixture
    def mock_project_manager(self) -> AsyncMock:
        """Mock project manager."""
        manager = AsyncMock()
        manager.handle_post_api_sync = AsyncMock()
        return manager

    @pytest.fixture
    def valid_schema_json(self) -> str:
        """Valid schema JSON for testing."""
        schema = [
            {
                "name": "id",
                "type": "integer",
                "optional": False,
                "hint": "Primary key",
            },
            {
                "name": "name",
                "type": "string",
                "optional": False,
                "hint": "User name",
            },
            {
                "name": "email",
                "type": "string",
                "optional": True,
                "hint": "User email",
            },
        ]
        return json.dumps(schema)

    @pytest.fixture
    def mock_create_table_response(self) -> MagicMock:
        """Mock create table API response."""
        response = MagicMock()

        # Mock table data
        table_data = MagicMock()
        table_data.id = "table_123"
        table_data.name = "Test Table"
        table_data.folder_id = 123

        # Mock schema columns
        col1 = MagicMock()
        col1.name = "id"
        col1.type = "integer"
        col2 = MagicMock()
        col2.name = "name"
        col2.type = "string"
        col3 = MagicMock()
        col3.name = "email"
        col3.type = "string"

        table_data.var_schema = [col1, col2, col3]

        response.data = table_data
        return response

    @pytest.mark.asyncio
    async def test_create_data_table_success(
        self,
        mock_config_manager: MagicMock,
        valid_schema_json: str,
    ) -> None:
        """Test successful data table creation."""
        with patch(
            "workato_platform.cli.commands.data_tables.create_table"
        ) as mock_create:
            assert create_data_table.callback
            await create_data_table.callback(
                name="Test Table",
                schema_json=valid_schema_json,
                folder_id=None,
                config_manager=mock_config_manager,
            )

        # Should load config to get folder_id
        mock_config_manager.load_config.assert_called_once()

        # Should call create_table with parsed schema
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert call_args[0][0] == "Test Table"  # name
        assert call_args[0][1] == 123  # folder_id
        assert len(call_args[0][2]) == 3  # schema with 3 columns

    @pytest.mark.asyncio
    async def test_create_data_table_with_explicit_folder_id(
        self,
        mock_config_manager: MagicMock,
        valid_schema_json: str,
    ) -> None:
        """Test data table creation with explicit folder ID."""
        with patch(
            "workato_platform.cli.commands.data_tables.create_table"
        ) as mock_create:
            assert create_data_table.callback
            await create_data_table.callback(
                name="Test Table",
                schema_json=valid_schema_json,
                folder_id=456,
                config_manager=mock_config_manager,
            )

        # Should not load config when folder_id is provided
        mock_config_manager.load_config.assert_not_called()

        # Should call create_table with explicit folder_id
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert call_args[0][1] == 456  # folder_id

    @pytest.mark.asyncio
    async def test_create_data_table_invalid_json(
        self,
        mock_config_manager: MagicMock,
    ) -> None:
        """Test data table creation with invalid JSON."""
        with patch("workato_platform.cli.commands.data_tables.click.echo") as mock_echo:
            assert create_data_table.callback
            await create_data_table.callback(
                name="Test Table",
                schema_json="invalid json",
                folder_id=None,
                config_manager=mock_config_manager,
            )

        mock_echo.assert_any_call(
            "❌ Invalid JSON in schema: Expecting value: line 1 column 1 (char 0)"
        )

    @pytest.mark.asyncio
    async def test_create_data_table_non_list_schema(
        self,
        mock_config_manager: MagicMock,
    ) -> None:
        """Test data table creation with non-list schema."""
        with patch("workato_platform.cli.commands.data_tables.click.echo") as mock_echo:
            assert create_data_table.callback
            await create_data_table.callback(
                name="Test Table",
                schema_json='{"name": "id", "type": "integer"}',
                folder_id=None,
                config_manager=mock_config_manager,
            )

        mock_echo.assert_any_call("❌ Schema must be an array of column definitions")

    @pytest.mark.asyncio
    async def test_create_data_table_no_folder_id(
        self,
    ) -> None:
        """Test data table creation without folder ID."""
        mock_config_manager = MagicMock()
        mock_config = MagicMock()
        mock_config.folder_id = None
        mock_config_manager.load_config.return_value = mock_config

        with patch("workato_platform.cli.commands.data_tables.click.echo") as mock_echo:
            assert create_data_table.callback
            await create_data_table.callback(
                name="Test Table",
                schema_json='[{"name": "id", "type": "integer", "optional": false}]',
                folder_id=None,
                config_manager=mock_config_manager,
            )

        mock_echo.assert_any_call("❌ No folder ID provided and no project configured.")

    @pytest.mark.asyncio
    async def test_create_table_function(
        self,
        mock_workato_client: AsyncMock,
        mock_project_manager: AsyncMock,
        mock_create_table_response: MagicMock,
    ) -> None:
        """Test the create_table helper function."""
        mock_workato_client.data_tables_api.create_data_table.return_value = (
            mock_create_table_response
        )

        schema = [
            DataTableColumnRequest.model_validate(
                {
                    "name": "id",
                    "type": "integer",
                    "optional": False,
                    "hint": "Primary key",
                }
            )
        ]

        with patch("workato_platform.cli.commands.data_tables.Spinner") as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 1.5
            mock_spinner.return_value = mock_spinner_instance

            await create_table(
                name="Test Table",
                folder_id=123,
                schema=schema,
                workato_api_client=mock_workato_client,
                project_manager=mock_project_manager,
            )

        # Verify API was called with correct parameters
        call_args = mock_workato_client.data_tables_api.create_data_table.call_args
        create_request = call_args.kwargs["data_table_create_request"]
        assert create_request.name == "Test Table"
        assert create_request.folder_id == 123
        # Schema should be converted to DataTableColumnRequest objects
        assert len(create_request.var_schema) == 1
        assert create_request.var_schema[0].name == "id"
        assert create_request.var_schema[0].type == "integer"
        assert not create_request.var_schema[0].optional

        # Verify post-creation sync was called
        mock_project_manager.handle_post_api_sync.assert_called_once()


class TestSchemaValidation:
    """Test schema validation functionality."""

    def test_validate_schema_valid(self) -> None:
        """Test validation with valid schema."""
        schema = [
            {
                "name": "id",
                "type": "integer",
                "optional": False,
                "hint": "Primary key",
            },
            {
                "name": "name",
                "type": "string",
                "optional": False,
                "default_value": "Unknown",
            },
            {
                "name": "created_at",
                "type": "date_time",
                "optional": True,
            },
        ]

        errors = validate_schema(schema)
        assert errors == []

    def test_validate_schema_empty(self) -> None:
        """Test validation with empty schema."""
        errors = validate_schema([])
        assert "Schema cannot be empty" in errors

    def test_validate_schema_missing_required_fields(self) -> None:
        """Test validation with missing required fields."""
        schema = [
            {
                "name": "id",
                # missing type and optional
            }
        ]

        errors = validate_schema(schema)
        assert any("'type' is required" in error for error in errors)
        assert any("'optional' is required" in error for error in errors)

    def test_validate_schema_invalid_type(self) -> None:
        """Test validation with invalid column type."""
        schema = [
            {
                "name": "id",
                "type": "invalid_type",
                "optional": False,
            }
        ]

        errors = validate_schema(schema)
        assert any("'type' must be one of" in error for error in errors)

    def test_validate_schema_invalid_name(self) -> None:
        """Test validation with invalid column name."""
        schema = [
            {
                "name": "",  # empty name
                "type": "string",
                "optional": False,
            },
            {
                "name": 123,  # non-string name
                "type": "string",
                "optional": False,
            },
        ]

        errors = validate_schema(schema)
        assert any("'name' must be a non-empty string" in error for error in errors)

    def test_validate_schema_invalid_optional(self) -> None:
        """Test validation with invalid optional field."""
        schema = [
            {
                "name": "id",
                "type": "integer",
                "optional": "yes",  # should be boolean
            }
        ]

        errors = validate_schema(schema)
        assert any(
            "'optional' must be true, false, 0, or 1" in error for error in errors
        )

    def test_validate_schema_relation_type(self) -> None:
        """Test validation with relation type columns."""
        schema = [
            {
                "name": "user_id",
                "type": "relation",
                "optional": False,
                "relation": {
                    "field_id": "field_123",
                    "table_id": "table_456",
                },
            },
            {
                "name": "invalid_relation",
                "type": "relation",
                "optional": False,
                # missing relation object
            },
        ]

        errors = validate_schema(schema)
        assert any(
            "'relation' object required for relation type" in error for error in errors
        )

    def test_validate_schema_default_value_type_mismatch(self) -> None:
        """Test validation with default value type mismatch."""
        schema = [
            {
                "name": "age",
                "type": "integer",
                "optional": True,
                "default_value": "twenty",  # should be integer
            },
            {
                "name": "active",
                "type": "boolean",
                "optional": True,
                "default_value": "true",  # should be boolean
            },
        ]

        errors = validate_schema(schema)
        assert any(
            "'default_value' type doesn't match column type 'integer'" in error
            for error in errors
        )
        assert any(
            "'default_value' type doesn't match column type 'boolean'" in error
            for error in errors
        )

    def test_validate_schema_invalid_field_id(self) -> None:
        """Test validation with invalid field_id format."""
        schema = [
            {
                "name": "id",
                "type": "string",
                "optional": False,
                "field_id": "invalid-uuid-format",
            }
        ]

        errors = validate_schema(schema)
        assert any(
            "'field_id' must be a valid UUID format" in error for error in errors
        )

    def test_validate_schema_valid_field_id(self) -> None:
        """Test validation with valid field_id format."""
        schema = [
            {
                "name": "id",
                "type": "string",
                "optional": False,
                "field_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        ]

        errors = validate_schema(schema)
        assert errors == []  # Should be valid

    def test_validate_schema_multivalue_field(self) -> None:
        """Test validation with multivalue field."""
        schema = [
            {
                "name": "tags",
                "type": "string",
                "optional": True,
                "multivalue": True,
            },
            {
                "name": "invalid_multivalue",
                "type": "string",
                "optional": True,
                "multivalue": "yes",  # should be boolean
            },
        ]

        errors = validate_schema(schema)
        assert any("'multivalue' must be a boolean" in error for error in errors)
        # First column should be valid
        assert len([e for e in errors if "tags" in e]) == 0
