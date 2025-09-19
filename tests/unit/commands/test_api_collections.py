"""Unit tests for API collections commands module."""

import os
import tempfile

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from workato_platform.cli.commands.api_collections import (
    api_collections,
    create,
    display_collection_summary,
    display_endpoint_summary,
    enable_all_endpoints_in_collection,
    enable_api_endpoint,
    enable_endpoint,
    list_collections,
    list_endpoints,
)
from workato_platform.client.workato_api.models.api_collection import ApiCollection
from workato_platform.client.workato_api.models.api_endpoint import ApiEndpoint
from workato_platform.client.workato_api.models.open_api_spec import OpenApiSpec


class TestApiCollectionsGroup:
    """Test the main api-collections group command."""

    def test_api_collections_group_exists(self) -> None:
        """Test that the api-collections group exists and has correct name."""
        assert api_collections.name == "api-collections"
        assert api_collections.help and "Manage API collections" in api_collections.help


class TestCreateCommand:
    """Test the create command and its various scenarios."""

    @pytest.fixture
    def mock_workato_client(self) -> AsyncMock:
        """Mock Workato API client."""
        client = AsyncMock()
        client.api_platform_api.create_api_collection = AsyncMock()
        return client

    @pytest.fixture
    def mock_config_manager(self) -> MagicMock:
        """Mock ConfigManager."""
        config_manager = MagicMock()
        config_manager.load_config.return_value = MagicMock(
            project_id=123, project_name="Test Project"
        )
        return config_manager

    @pytest.fixture
    def mock_project_manager(self) -> AsyncMock:
        """Mock ProjectManager."""
        project_manager = AsyncMock()
        return project_manager

    @pytest.fixture
    def mock_collection_response(self) -> ApiCollection:
        """Mock API collection response."""
        collection = ApiCollection(
            id=123,
            name="Test Collection",
            project_id="123",
            url="https://api.example.com/collection",
            api_spec_url="https://api.example.com/spec",
            version="1.0",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )
        return collection

    @pytest.mark.asyncio
    async def test_create_success_with_file_json(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
        mock_collection_response: ApiCollection,
    ) -> None:
        """Test successful collection creation with JSON file."""
        mock_workato_client.api_platform_api.create_api_collection.return_value = (
            mock_collection_response
        )

        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write('{"openapi": "3.0.0", "info": {"title": "Test API"}}')
            temp_file_path = temp_file.name

        try:
            with patch(
                "workato_platform.cli.commands.api_collections.Spinner"
            ) as mock_spinner:
                mock_spinner_instance = MagicMock()
                mock_spinner_instance.stop.return_value = 1.5
                mock_spinner.return_value = mock_spinner_instance

                await create.callback(
                    name="Test Collection",
                    format="json",
                    content=temp_file_path,
                    proxy_connection_id=456,
                    config_manager=mock_config_manager,
                    project_manager=mock_project_manager,
                    workato_api_client=mock_workato_client,
                )

            # Verify API was called
            mock_workato_client.api_platform_api.create_api_collection.assert_called_once()
            call_args = (
                mock_workato_client.api_platform_api.create_api_collection.call_args
            )
            create_request = call_args.kwargs["api_collection_create_request"]

            assert create_request.name == "Test Collection"
            assert create_request.project_id == 123
            assert create_request.proxy_connection_id == 456
            assert isinstance(create_request.openapi_spec, OpenApiSpec)
            assert create_request.openapi_spec.format == "json"
            assert "openapi" in create_request.openapi_spec.content

        finally:
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_create_success_with_file_yaml(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
        mock_collection_response: ApiCollection,
    ) -> None:
        """Test successful collection creation with YAML file."""
        mock_workato_client.api_platform_api.create_api_collection.return_value = (
            mock_collection_response
        )

        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as temp_file:
            temp_file.write("openapi: 3.0.0\ninfo:\n  title: Test API")
            temp_file_path = temp_file.name

        try:
            with patch(
                "workato_platform.cli.commands.api_collections.Spinner"
            ) as mock_spinner:
                mock_spinner_instance = MagicMock()
                mock_spinner_instance.stop.return_value = 1.2
                mock_spinner.return_value = mock_spinner_instance

                await create.callback(
                    name="Test Collection",
                    format="yaml",
                    content=temp_file_path,
                    proxy_connection_id=None,
                    config_manager=mock_config_manager,
                    project_manager=mock_project_manager,
                    workato_api_client=mock_workato_client,
                )

            # Verify API was called
            call_args = (
                mock_workato_client.api_platform_api.create_api_collection.call_args
            )
            create_request = call_args.kwargs["api_collection_create_request"]
            assert create_request.openapi_spec.format == "yaml"
            assert "openapi" in create_request.openapi_spec.content

        finally:
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_create_success_with_url(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
        mock_collection_response: ApiCollection,
    ) -> None:
        """Test successful collection creation with URL."""
        mock_workato_client.api_platform_api.create_api_collection.return_value = (
            mock_collection_response
        )

        mock_response = AsyncMock()
        mock_response.text = AsyncMock(
            return_value='{"openapi": "3.0.0", "info": {"title": "Test API"}}'
        )

        with patch(
            "workato_platform.cli.commands.api_collections.aiohttp.ClientSession"
        ) as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            with patch(
                "workato_platform.cli.commands.api_collections.Spinner"
            ) as mock_spinner:
                mock_spinner_instance = MagicMock()
                mock_spinner_instance.stop.return_value = 2.0
                mock_spinner.return_value = mock_spinner_instance

                await create.callback(
                    name="Test Collection",
                    format="url",
                    content="https://api.example.com/spec.json",
                    proxy_connection_id=None,
                    config_manager=mock_config_manager,
                    project_manager=mock_project_manager,
                    workato_api_client=mock_workato_client,
                )

            # Verify API was called
            call_args = (
                mock_workato_client.api_platform_api.create_api_collection.call_args
            )
            create_request = call_args.kwargs["api_collection_create_request"]
            assert create_request.openapi_spec.format == "json"
            assert "openapi" in create_request.openapi_spec.content

    @pytest.mark.asyncio
    async def test_create_no_project_id(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
    ) -> None:
        """Test create when no project is configured."""
        mock_config_manager.load_config.return_value = MagicMock(project_id=None)

        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            await create.callback(
                name="Test Collection",
                format="json",
                content="test.json",
                proxy_connection_id=None,
                config_manager=mock_config_manager,
                project_manager=mock_project_manager,
                workato_api_client=mock_workato_client,
            )

        mock_echo.assert_called_with(
            "❌ No project configured. Please run 'workato init' first."
        )
        mock_workato_client.api_platform_api.create_api_collection.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_file_not_found(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
    ) -> None:
        """Test create when file doesn't exist."""
        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            await create.callback(
                name="Test Collection",
                format="json",
                content="nonexistent.json",
                proxy_connection_id=None,
                config_manager=mock_config_manager,
                project_manager=mock_project_manager,
                workato_api_client=mock_workato_client,
            )

        mock_echo.assert_called_with("❌ File not found: nonexistent.json")
        mock_workato_client.api_platform_api.create_api_collection.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_file_read_error(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
    ) -> None:
        """Test create when file read fails."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write('{"test": "data"}')
            temp_file_path = temp_file.name

        try:
            # Make file read-only to cause permission error
            os.chmod(temp_file_path, 0o000)

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await create.callback(
                    name="Test Collection",
                    format="json",
                    content=temp_file_path,
                    proxy_connection_id=None,
                    config_manager=mock_config_manager,
                    project_manager=mock_project_manager,
                    workato_api_client=mock_workato_client,
                )

            mock_echo.assert_called_with(
                f"❌ Failed to read file {temp_file_path}: [Errno 13] Permission denied: '{temp_file_path}'"
            )
            mock_workato_client.api_platform_api.create_api_collection.assert_not_called()

        finally:
            os.chmod(temp_file_path, 0o644)
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_create_uses_project_name_as_default(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
        mock_collection_response: ApiCollection,
    ) -> None:
        """Test create uses project name as default when name not provided."""
        mock_workato_client.api_platform_api.create_api_collection.return_value = (
            mock_collection_response
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write('{"openapi": "3.0.0"}')
            temp_file_path = temp_file.name

        try:
            with patch(
                "workato_platform.cli.commands.api_collections.Spinner"
            ) as mock_spinner:
                mock_spinner_instance = MagicMock()
                mock_spinner_instance.stop.return_value = 1.0
                mock_spinner.return_value = mock_spinner_instance

                await create.callback(
                    name=None,  # No name provided
                    format="json",
                    content=temp_file_path,
                    proxy_connection_id=None,
                    config_manager=mock_config_manager,
                    project_manager=mock_project_manager,
                    workato_api_client=mock_workato_client,
                )

            # Verify API was called with project name
            call_args = (
                mock_workato_client.api_platform_api.create_api_collection.call_args
            )
            create_request = call_args.kwargs["api_collection_create_request"]
            assert create_request.name == "Test Project"

        finally:
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_create_uses_default_name_when_project_name_none(
        self,
        mock_workato_client: AsyncMock,
        mock_config_manager: MagicMock,
        mock_project_manager: AsyncMock,
        mock_collection_response: ApiCollection,
    ) -> None:
        """Test create uses default name when project name is None."""
        mock_config_manager.load_config.return_value = MagicMock(
            project_id=123, project_name=None
        )
        mock_workato_client.api_platform_api.create_api_collection.return_value = (
            mock_collection_response
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write('{"openapi": "3.0.0"}')
            temp_file_path = temp_file.name

        try:
            with patch(
                "workato_platform.cli.commands.api_collections.Spinner"
            ) as mock_spinner:
                mock_spinner_instance = MagicMock()
                mock_spinner_instance.stop.return_value = 1.0
                mock_spinner.return_value = mock_spinner_instance

                await create.callback(
                    name=None,  # No name provided
                    format="json",
                    content=temp_file_path,
                    proxy_connection_id=None,
                    config_manager=mock_config_manager,
                    project_manager=mock_project_manager,
                    workato_api_client=mock_workato_client,
                )

            # Verify API was called with default name
            call_args = (
                mock_workato_client.api_platform_api.create_api_collection.call_args
            )
            create_request = call_args.kwargs["api_collection_create_request"]
            assert create_request.name == "API Collection"

        finally:
            os.unlink(temp_file_path)


class TestListCollectionsCommand:
    """Test the list-collections command."""

    @pytest.fixture
    def mock_workato_client(self) -> AsyncMock:
        """Mock Workato API client."""
        client = AsyncMock()
        client.api_platform_api.list_api_collections = AsyncMock()
        return client

    @pytest.fixture
    def mock_collections_response(self) -> list[ApiCollection]:
        """Mock API collections list response."""
        collections = [
            ApiCollection(
                id=123,
                name="Collection 1",
                project_id="123",
                url="https://api.example.com/collection1",
                api_spec_url="https://api.example.com/spec1",
                version="1.0",
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
            ApiCollection(
                id=456,
                name="Collection 2",
                project_id="123",
                url="https://api.example.com/collection2",
                api_spec_url="https://api.example.com/spec2",
                version="1.1",
                created_at=datetime(2024, 1, 2),
                updated_at=datetime(2024, 1, 2),
            ),
        ]
        return collections

    @pytest.mark.asyncio
    async def test_list_collections_success(
        self,
        mock_workato_client: AsyncMock,
        mock_collections_response: list[ApiCollection],
    ) -> None:
        """Test successful listing of API collections."""
        mock_workato_client.api_platform_api.list_api_collections.return_value = (
            mock_collections_response
        )

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 1.2
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.display_collection_summary"
            ) as mock_display:
                await list_collections.callback(
                    page=1, per_page=50, workato_api_client=mock_workato_client
                )

        mock_workato_client.api_platform_api.list_api_collections.assert_called_once_with(
            page=1, per_page=50
        )
        assert mock_display.call_count == 2  # Two collections in response

    @pytest.mark.asyncio
    async def test_list_collections_empty(self, mock_workato_client: AsyncMock) -> None:
        """Test listing when no collections exist."""
        mock_workato_client.api_platform_api.list_api_collections.return_value = []

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 0.8
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await list_collections.callback(
                    page=1, per_page=50, workato_api_client=mock_workato_client
                )

        mock_echo.assert_any_call("  ℹ️  No API collections found")

    @pytest.mark.asyncio
    async def test_list_collections_per_page_limit_exceeded(
        self, mock_workato_client: AsyncMock
    ) -> None:
        """Test listing with per_page limit exceeded."""
        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            await list_collections.callback(
                page=1,
                per_page=150,  # Exceeds limit of 100
                workato_api_client=mock_workato_client,
            )

        mock_echo.assert_called_with("❌ Maximum per-page limit is 100")
        mock_workato_client.api_platform_api.list_api_collections.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_collections_pagination_info(
        self, mock_workato_client: AsyncMock
    ) -> None:
        """Test pagination info display."""
        # Mock response with exactly per_page items to trigger pagination info
        mock_collections = [
            ApiCollection(
                id=i,
                name=f"Collection {i}",
                project_id="123",
                url=f"https://api.example.com/collection{i}",
                api_spec_url=f"https://api.example.com/spec{i}",
                version="1.0",
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            )
            for i in range(100)
        ]  # Exactly 100 items

        mock_workato_client.api_platform_api.list_api_collections.return_value = (
            mock_collections
        )

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 1.0
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.display_collection_summary"
            ):
                with patch(
                    "workato_platform.cli.commands.api_collections.click.echo"
                ) as mock_echo:
                    await list_collections.callback(
                        page=2, per_page=100, workato_api_client=mock_workato_client
                    )

        # Should show pagination info
        mock_echo.assert_any_call("💡 Pagination:")
        mock_echo.assert_any_call(
            "  • Next page: workato api-collections list --page 3"
        )
        mock_echo.assert_any_call(
            "  • Previous page: workato api-collections list --page 1"
        )


class TestListEndpointsCommand:
    """Test the list-endpoints command."""

    @pytest.fixture
    def mock_workato_client(self) -> AsyncMock:
        """Mock Workato API client."""
        client = AsyncMock()
        client.api_platform_api.list_api_endpoints = AsyncMock()
        return client

    @pytest.fixture
    def mock_endpoints_response(self) -> list[ApiEndpoint]:
        """Mock API endpoints list response."""
        endpoints = [
            ApiEndpoint(
                id=1,
                api_collection_id=123,
                flow_id=456,
                name="Get Users",
                method="GET",
                url="https://api.example.com/users",
                base_path="/api/v1",
                path="/users",
                active=True,
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
            ApiEndpoint(
                id=2,
                api_collection_id=123,
                flow_id=789,
                name="Create User",
                method="POST",
                url="https://api.example.com/users",
                base_path="/api/v1",
                path="/users",
                active=False,
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
        ]
        return endpoints

    @pytest.mark.asyncio
    async def test_list_endpoints_success(
        self, mock_workato_client: AsyncMock, mock_endpoints_response: list[ApiEndpoint]
    ) -> None:
        """Test successful listing of API endpoints."""
        mock_workato_client.api_platform_api.list_api_endpoints.return_value = (
            mock_endpoints_response
        )

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 1.5
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.display_endpoint_summary"
            ) as mock_display:
                await list_endpoints.callback(
                    api_collection_id=123, workato_api_client=mock_workato_client
                )

        # Should call API once since we have 2 endpoints < 100 (no pagination needed)
        assert mock_workato_client.api_platform_api.list_api_endpoints.call_count == 1
        assert mock_display.call_count == 2  # Two endpoints

    @pytest.mark.asyncio
    async def test_list_endpoints_empty(self, mock_workato_client: AsyncMock) -> None:
        """Test listing when no endpoints exist."""
        mock_workato_client.api_platform_api.list_api_endpoints.return_value = []

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 0.5
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await list_endpoints.callback(
                    api_collection_id=123, workato_api_client=mock_workato_client
                )

        mock_echo.assert_called_with("  ℹ️  No endpoints found for this collection")

    @pytest.mark.asyncio
    async def test_list_endpoints_pagination(
        self, mock_workato_client: AsyncMock
    ) -> None:
        """Test endpoint listing with pagination."""
        # Mock first page with 100 endpoints (triggers pagination)
        first_page = [
            ApiEndpoint(
                id=i,
                api_collection_id=123,
                flow_id=456,
                name=f"Endpoint {i}",
                method="GET",
                url=f"https://api.example.com/endpoint{i}",
                base_path="/api/v1",
                path=f"/endpoint{i}",
                active=True,
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            )
            for i in range(100)
        ]

        # Mock second page with 50 endpoints (stops pagination)
        second_page = [
            ApiEndpoint(
                id=i + 100,
                api_collection_id=123,
                flow_id=456,
                name=f"Endpoint {i + 100}",
                method="GET",
                url=f"https://api.example.com/endpoint{i + 100}",
                base_path="/api/v1",
                path=f"/endpoint{i + 100}",
                active=True,
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            )
            for i in range(50)
        ]

        mock_workato_client.api_platform_api.list_api_endpoints.side_effect = [
            first_page,
            second_page,
        ]

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 2.0
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.display_endpoint_summary"
            ):
                await list_endpoints.callback(
                    api_collection_id=123, workato_api_client=mock_workato_client
                )

        # Should call API twice (page 1 and 2)
        assert mock_workato_client.api_platform_api.list_api_endpoints.call_count == 2
        # First call should be page 1
        first_call = (
            mock_workato_client.api_platform_api.list_api_endpoints.call_args_list[0]
        )
        assert first_call.kwargs["page"] == 1
        # Second call should be page 2
        second_call = (
            mock_workato_client.api_platform_api.list_api_endpoints.call_args_list[1]
        )
        assert second_call.kwargs["page"] == 2


class TestEnableEndpointCommand:
    """Test the enable-endpoint command."""

    @pytest.fixture
    def mock_workato_client(self) -> AsyncMock:
        """Mock Workato API client."""
        client = AsyncMock()
        client.api_platform_api.enable_api_endpoint = AsyncMock()
        client.api_platform_api.list_api_endpoints = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_enable_endpoint_single_success(
        self, mock_workato_client: AsyncMock
    ) -> None:
        """Test enabling a single endpoint successfully."""
        with patch(
            "workato_platform.cli.commands.api_collections.enable_api_endpoint"
        ) as mock_enable:
            await enable_endpoint.callback(
                api_endpoint_id=123, api_collection_id=None, all=False
            )

        mock_enable.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_enable_endpoint_all_success(
        self, mock_workato_client: AsyncMock
    ) -> None:
        """Test enabling all endpoints in collection successfully."""
        with patch(
            "workato_platform.cli.commands.api_collections.enable_all_endpoints_in_collection"
        ) as mock_enable_all:
            await enable_endpoint.callback(api_endpoint_id=None, api_collection_id=456, all=True)

        mock_enable_all.assert_called_once_with(456)

    @pytest.mark.asyncio
    async def test_enable_endpoint_all_without_collection_id(self, mock_workato_client):
        """Test enabling all endpoints without collection ID fails."""
        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            await enable_endpoint.callback(
                api_endpoint_id=None, api_collection_id=None, all=True
            )

        mock_echo.assert_called_with("❌ --all flag requires --api-collection-id")

    @pytest.mark.asyncio
    async def test_enable_endpoint_all_with_endpoint_id(self, mock_workato_client):
        """Test enabling all endpoints with endpoint ID fails."""
        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            await enable_endpoint.callback(api_endpoint_id=123, api_collection_id=456, all=True)

        mock_echo.assert_called_with(
            "❌ Cannot specify both --api-endpoint-id and --all"
        )

    @pytest.mark.asyncio
    async def test_enable_endpoint_no_parameters(self, mock_workato_client):
        """Test enabling endpoint with no parameters fails."""
        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            await enable_endpoint.callback(
                api_endpoint_id=None, api_collection_id=None, all=False
            )

        mock_echo.assert_called_with(
            "❌ Must specify either --api-endpoint-id or --all with --api-collection-id"
        )


class TestEnableAllEndpointsInCollection:
    """Test the enable_all_endpoints_in_collection function."""

    @pytest.fixture
    def mock_workato_client(self):
        """Mock Workato API client."""
        client = AsyncMock()
        client.api_platform_api.list_api_endpoints = AsyncMock()
        client.api_platform_api.enable_api_endpoint = AsyncMock()
        return client

    @pytest.fixture
    def mock_endpoints_mixed_status(self):
        """Mock endpoints with mixed active status."""
        return [
            ApiEndpoint(
                id=1,
                api_collection_id=123,
                flow_id=456,
                name="Active Endpoint",
                method="GET",
                url="https://api.example.com/active",
                base_path="/api/v1",
                path="/active",
                active=True,  # Already active
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
            ApiEndpoint(
                id=2,
                api_collection_id=123,
                flow_id=789,
                name="Disabled Endpoint 1",
                method="POST",
                url="https://api.example.com/disabled1",
                base_path="/api/v1",
                path="/disabled1",
                active=False,  # Needs enabling
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
            ApiEndpoint(
                id=3,
                api_collection_id=123,
                flow_id=101,
                name="Disabled Endpoint 2",
                method="PUT",
                url="https://api.example.com/disabled2",
                base_path="/api/v1",
                path="/disabled2",
                active=False,  # Needs enabling
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
        ]

    @pytest.mark.asyncio
    async def test_enable_all_endpoints_success(
        self, mock_workato_client, mock_endpoints_mixed_status
    ):
        """Test successfully enabling all disabled endpoints."""
        mock_workato_client.api_platform_api.list_api_endpoints.return_value = (
            mock_endpoints_mixed_status
        )

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 1.0
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await enable_all_endpoints_in_collection(
                    api_collection_id=123, workato_api_client=mock_workato_client
                )

        # Should enable 2 disabled endpoints (not the active one)
        assert mock_workato_client.api_platform_api.enable_api_endpoint.call_count == 2
        mock_workato_client.api_platform_api.enable_api_endpoint.assert_any_call(
            api_endpoint_id=2
        )
        mock_workato_client.api_platform_api.enable_api_endpoint.assert_any_call(
            api_endpoint_id=3
        )

        # Should show success message
        mock_echo.assert_any_call("📊 Results:")
        mock_echo.assert_any_call("  ✅ Successfully enabled: 2")

    @pytest.mark.asyncio
    async def test_enable_all_endpoints_no_endpoints(self, mock_workato_client):
        """Test enabling all endpoints when no endpoints exist."""
        mock_workato_client.api_platform_api.list_api_endpoints.return_value = []

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 0.5
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await enable_all_endpoints_in_collection(
                    api_collection_id=123, workato_api_client=mock_workato_client
                )

        mock_echo.assert_called_with("❌ No endpoints found for collection 123")
        mock_workato_client.api_platform_api.enable_api_endpoint.assert_not_called()

    @pytest.mark.asyncio
    async def test_enable_all_endpoints_all_already_enabled(self, mock_workato_client):
        """Test enabling all endpoints when all are already enabled."""
        all_active_endpoints = [
            ApiEndpoint(
                id=1,
                api_collection_id=123,
                flow_id=456,
                name="Active Endpoint 1",
                method="GET",
                url="https://api.example.com/active1",
                base_path="/api/v1",
                path="/active1",
                active=True,
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
            ApiEndpoint(
                id=2,
                api_collection_id=123,
                flow_id=789,
                name="Active Endpoint 2",
                method="POST",
                url="https://api.example.com/active2",
                base_path="/api/v1",
                path="/active2",
                active=True,
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
        ]
        mock_workato_client.api_platform_api.list_api_endpoints.return_value = (
            all_active_endpoints
        )

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 0.8
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await enable_all_endpoints_in_collection(
                    api_collection_id=123, workato_api_client=mock_workato_client
                )

        mock_echo.assert_called_with(
            "✅ All endpoints in collection 123 are already enabled"
        )
        mock_workato_client.api_platform_api.enable_api_endpoint.assert_not_called()

    @pytest.mark.asyncio
    async def test_enable_all_endpoints_with_failures(
        self, mock_workato_client, mock_endpoints_mixed_status
    ):
        """Test enabling all endpoints with some failures."""
        mock_workato_client.api_platform_api.list_api_endpoints.return_value = (
            mock_endpoints_mixed_status
        )

        # Make one endpoint fail to enable
        async def mock_enable_side_effect(api_endpoint_id):
            if api_endpoint_id == 2:
                raise Exception("API Error: Endpoint not found")
            return None

        mock_workato_client.api_platform_api.enable_api_endpoint.side_effect = (
            mock_enable_side_effect
        )

        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 1.0
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await enable_all_endpoints_in_collection(
                    api_collection_id=123, workato_api_client=mock_workato_client
                )

        # Should show mixed results
        mock_echo.assert_any_call("📊 Results:")
        mock_echo.assert_any_call("  ✅ Successfully enabled: 1")
        mock_echo.assert_any_call("  ❌ Failed: 1")
        mock_echo.assert_any_call(
            "    • Disabled Endpoint 1: API Error: Endpoint not found"
        )


class TestEnableApiEndpoint:
    """Test the enable_api_endpoint function."""

    @pytest.fixture
    def mock_workato_client(self):
        """Mock Workato API client."""
        client = AsyncMock()
        client.api_platform_api.enable_api_endpoint = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_enable_api_endpoint_success(self, mock_workato_client):
        """Test successfully enabling a single API endpoint."""
        with patch(
            "workato_platform.cli.commands.api_collections.Spinner"
        ) as mock_spinner:
            mock_spinner_instance = MagicMock()
            mock_spinner_instance.stop.return_value = 0.8
            mock_spinner.return_value = mock_spinner_instance

            with patch(
                "workato_platform.cli.commands.api_collections.click.echo"
            ) as mock_echo:
                await enable_api_endpoint(
                    api_endpoint_id=123, workato_api_client=mock_workato_client
                )

        mock_workato_client.api_platform_api.enable_api_endpoint.assert_called_once_with(
            api_endpoint_id=123
        )
        mock_echo.assert_any_call("✅ API endpoint enabled successfully (0.8s)")


class TestDisplayFunctions:
    """Test display helper functions."""

    def test_display_endpoint_summary_active(self):
        """Test displaying active endpoint summary."""
        endpoint = ApiEndpoint(
            id=123,
            api_collection_id=456,
            flow_id=789,
            name="Test Endpoint",
            method="GET",
            url="https://api.example.com/test",
            base_path="/api/v1",
            path="/test",
            active=True,
            legacy=False,
            created_at=datetime(2024, 1, 15, 10, 30, 0),
            updated_at=datetime(2024, 1, 15, 10, 30, 0),
        )

        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            display_endpoint_summary(endpoint)

        mock_echo.assert_any_call("  ✅ Test Endpoint")
        mock_echo.assert_any_call("    🆔 ID: 123")
        mock_echo.assert_any_call("    🔗 Method: GET")
        mock_echo.assert_any_call("    📍 Path: https://api.example.com/test")
        mock_echo.assert_any_call("    📊 Status: Enabled")
        mock_echo.assert_any_call("    🔄 Recipe ID: 789")
        mock_echo.assert_any_call("    🕐 Created: 2024-01-15")
        mock_echo.assert_any_call("    📚 Collection ID: 456")
        # Note: Legacy status not shown when legacy=False

    def test_display_endpoint_summary_disabled_with_legacy(self):
        """Test displaying disabled endpoint summary with legacy flag."""
        endpoint = ApiEndpoint(
            id=456,
            api_collection_id=789,
            flow_id=101,
            name="Legacy Endpoint",
            method="POST",
            url="https://api.example.com/legacy",
            base_path="/api/v1",
            path="/legacy",
            active=False,
            legacy=True,
            created_at=datetime(2024, 2, 1, 14, 20, 0),
            updated_at=datetime(2024, 2, 1, 14, 20, 0),
        )

        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            display_endpoint_summary(endpoint)

        mock_echo.assert_any_call("  ❌ Legacy Endpoint")
        mock_echo.assert_any_call("    📊 Status: Disabled")
        mock_echo.assert_any_call("    📜 Legacy: Yes")

    def test_display_collection_summary(self):
        """Test displaying collection summary."""
        collection = ApiCollection(
            id=123,
            name="Test Collection",
            project_id="proj_456",
            url="https://api.example.com/very/long/url/that/should/be/truncated/for/display/purposes",
            api_spec_url="https://api.example.com/very/long/spec/url/that/should/be/truncated/for/display/purposes",
            version="1.2.3",
            created_at=datetime(2024, 1, 10, 9, 15, 30),
            updated_at=datetime(2024, 1, 20, 16, 45, 0),
        )

        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            display_collection_summary(collection)

        mock_echo.assert_any_call("  📚 Test Collection")
        mock_echo.assert_any_call("    🆔 ID: 123")
        mock_echo.assert_any_call("    📁 Project ID: proj_456")
        mock_echo.assert_any_call(
            "    🌐 API URL: https://api.example.com/very/long/url/that/should/be/trun..."
        )
        mock_echo.assert_any_call(
            "    📄 Spec URL: https://api.example.com/very/long/spec/url/that/should/be..."
        )
        mock_echo.assert_any_call("    🕐 Created: 2024-01-10")
        mock_echo.assert_any_call("    🔄 Updated: 2024-01-20")

    def test_display_collection_summary_no_updated_at(self):
        """Test displaying collection summary when updated_at equals created_at."""
        collection = ApiCollection(
            id=456,
            name="New Collection",
            project_id="proj_789",
            url="https://api.example.com/new",
            api_spec_url="https://api.example.com/new/spec",
            version="1.0.0",
            created_at=datetime(2024, 3, 1, 12, 0, 0),
            updated_at=datetime(2024, 3, 1, 12, 0, 0),  # Same as created_at
        )

        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            display_collection_summary(collection)

        # Should not show updated date when it equals created date
        mock_echo.assert_any_call("    🕐 Created: 2024-03-01")
        # Should not call with updated date
        updated_calls = [
            call for call in mock_echo.call_args_list if "Updated:" in str(call)
        ]
        assert len(updated_calls) == 0

    def test_display_collection_summary_short_urls(self):
        """Test displaying collection summary with short URLs."""
        collection = ApiCollection(
            id=789,
            name="Short Collection",
            project_id="proj_short",
            url="https://api.example.com/short",
            api_spec_url="https://api.example.com/short/spec",
            version="2.0.0",
            created_at=datetime(2024, 4, 1, 8, 30, 0),
            updated_at=datetime(2024, 4, 2, 10, 15, 0),
        )

        with patch(
            "workato_platform.cli.commands.api_collections.click.echo"
        ) as mock_echo:
            display_collection_summary(collection)

        # URLs should not be truncated
        mock_echo.assert_any_call("    🌐 API URL: https://api.example.com/short")
        mock_echo.assert_any_call("    📄 Spec URL: https://api.example.com/short/spec")


class TestCommandsWithCallbackApproach:
    """Test commands using .callback() approach to bypass AsyncClick+DI issues."""

    @pytest.mark.asyncio
    async def test_create_command_callback_success_json(self) -> None:
        """Test create command with JSON file using callback approach."""
        import tempfile
        import os

        mock_collection = ApiCollection(
            id=123,
            name="Test Collection",
            project_id="123",
            url="https://api.example.com/collection",
            api_spec_url="https://api.example.com/spec",
            version="1.0",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

        mock_workato_client = AsyncMock()
        mock_workato_client.api_platform_api.create_api_collection.return_value = mock_collection

        mock_config_manager = MagicMock()
        mock_config_manager.load_config.return_value = MagicMock(
            project_id=123, project_name="Test Project"
        )

        mock_project_manager = AsyncMock()

        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_file.write('{"openapi": "3.0.0", "info": {"title": "Test API"}}')
            temp_file_path = temp_file.name

        try:
            with patch("workato_platform.cli.commands.api_collections.click.echo") as mock_echo:
                await create.callback(
                    name="Test Collection",
                    format="json",
                    content=temp_file_path,
                    proxy_connection_id=456,
                    config_manager=mock_config_manager,
                    project_manager=mock_project_manager,
                    workato_api_client=mock_workato_client,
                )

            # Verify API was called
            mock_workato_client.api_platform_api.create_api_collection.assert_called_once()
            call_args = mock_workato_client.api_platform_api.create_api_collection.call_args.kwargs
            create_request = call_args["api_collection_create_request"]
            assert create_request.name == "Test Collection"
            assert create_request.project_id == 123
            assert create_request.proxy_connection_id == 456

            # Verify success output
            assert mock_echo.called

        finally:
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_create_command_callback_no_project_id(self) -> None:
        """Test create command when no project is configured."""
        mock_config_manager = MagicMock()
        mock_config_manager.load_config.return_value = MagicMock(project_id=None)

        mock_project_manager = AsyncMock()
        mock_workato_client = AsyncMock()

        with patch("workato_platform.cli.commands.api_collections.click.echo") as mock_echo:
            await create.callback(
                name="Test Collection",
                format="json",
                content="test.json",
                proxy_connection_id=None,
                config_manager=mock_config_manager,
                project_manager=mock_project_manager,
                workato_api_client=mock_workato_client,
            )

        mock_echo.assert_called_with("❌ No project configured. Please run 'workato init' first.")
        mock_workato_client.api_platform_api.create_api_collection.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_collections_callback_success(self) -> None:
        """Test list_collections command using callback approach."""
        mock_collections = [
            ApiCollection(
                id=123,
                name="Collection 1",
                project_id="123",
                url="https://api.example.com/collection1",
                api_spec_url="https://api.example.com/spec1",
                version="1.0",
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
            ApiCollection(
                id=456,
                name="Collection 2",
                project_id="123",
                url="https://api.example.com/collection2",
                api_spec_url="https://api.example.com/spec2",
                version="1.1",
                created_at=datetime(2024, 1, 2),
                updated_at=datetime(2024, 1, 2),
            ),
        ]

        mock_workato_client = AsyncMock()
        mock_workato_client.api_platform_api.list_api_collections.return_value = mock_collections

        with patch("workato_platform.cli.commands.api_collections.display_collection_summary") as mock_display:
            with patch("workato_platform.cli.commands.api_collections.click.echo") as mock_echo:
                await list_collections.callback(
                    page=1,
                    per_page=50,
                    workato_api_client=mock_workato_client,
                )

        # Verify API was called
        mock_workato_client.api_platform_api.list_api_collections.assert_called_once_with(page=1, per_page=50)

        # Verify display was called for each collection
        assert mock_display.call_count == 2

        # Verify output was generated
        assert mock_echo.called

    @pytest.mark.asyncio
    async def test_list_collections_callback_per_page_limit(self) -> None:
        """Test list_collections with per_page limit exceeded."""
        mock_workato_client = AsyncMock()

        with patch("workato_platform.cli.commands.api_collections.click.echo") as mock_echo:
            await list_collections.callback(
                page=1,
                per_page=150,  # Exceeds limit of 100
                workato_api_client=mock_workato_client,
            )

        mock_echo.assert_called_with("❌ Maximum per-page limit is 100")
        mock_workato_client.api_platform_api.list_api_collections.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_endpoints_callback_success(self) -> None:
        """Test list_endpoints command using callback approach."""
        mock_endpoints = [
            ApiEndpoint(
                id=1,
                api_collection_id=123,
                flow_id=456,
                name="Get Users",
                method="GET",
                url="https://api.example.com/users",
                base_path="/api/v1",
                path="/users",
                active=True,
                legacy=False,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1),
            ),
        ]

        mock_workato_client = AsyncMock()
        mock_workato_client.api_platform_api.list_api_endpoints.return_value = mock_endpoints

        with patch("workato_platform.cli.commands.api_collections.display_endpoint_summary") as mock_display:
            with patch("workato_platform.cli.commands.api_collections.click.echo") as mock_echo:
                await list_endpoints.callback(
                    api_collection_id=123,
                    workato_api_client=mock_workato_client,
                )

        # Verify API was called (should be called twice for pagination check)
        assert mock_workato_client.api_platform_api.list_api_endpoints.call_count >= 1

        # Verify display was called
        mock_display.assert_called()

        # Verify output was generated
        assert mock_echo.called

    @pytest.mark.asyncio
    async def test_create_command_callback_file_not_found(self) -> None:
        """Test create command when file doesn't exist."""
        mock_config_manager = MagicMock()
        mock_config_manager.load_config.return_value = MagicMock(
            project_id=123, project_name="Test Project"
        )

        mock_project_manager = AsyncMock()
        mock_workato_client = AsyncMock()

        with patch("workato_platform.cli.commands.api_collections.click.echo") as mock_echo:
            await create.callback(
                name="Test Collection",
                format="json",
                content="nonexistent.json",
                proxy_connection_id=None,
                config_manager=mock_config_manager,
                project_manager=mock_project_manager,
                workato_api_client=mock_workato_client,
            )

        mock_echo.assert_called_with("❌ File not found: nonexistent.json")
        mock_workato_client.api_platform_api.create_api_collection.assert_not_called()
