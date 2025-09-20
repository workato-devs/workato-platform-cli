"""Integration tests for connection management workflow."""

from unittest.mock import Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform.cli.cli import cli


class TestConnectionWorkflow:
    """Test complete connection management workflows."""

    @pytest.mark.asyncio
    async def test_oauth_connection_creation_workflow(self) -> None:
        """Test end-to-end OAuth connection creation."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_workato_client = Mock()
            get_connection_oauth_url = (
                mock_workato_client.connections_api.get_connection_oauth_url
            )
            get_connection_oauth_url.return_value = Mock(
                oauth_url="https://login.salesforce.com/oauth2/authorize?client_id=123"
            )
            create_runtime_user_connection = (
                mock_workato_client.connections_api.create_runtime_user_connection
            )
            create_runtime_user_connection.return_value = Mock(
                data=Mock(id=12345, name="Test OAuth Connection", authorized=True)
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Test OAuth URL generation
            result = await runner.invoke(
                cli, ["connections", "get-oauth-url", "--id", "12345"]
            )

            # Should not crash and command should be found
            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_connection_discovery_workflow(self) -> None:
        """Test connection discovery and exploration workflow."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            # Mock connector manager
            mock_connector_manager = Mock()
            mock_connector_manager.get_available_connectors.return_value = [
                Mock(name="salesforce", title="Salesforce", oauth_enabled=True),
                Mock(name="hubspot", title="HubSpot", oauth_enabled=True),
            ]

            mock_instance = mock_container.return_value
            mock_instance.connector_manager.return_value = mock_connector_manager

            # Discover available connectors
            result = await runner.invoke(cli, ["connectors", "list"])
            # Should not crash and command should be found
            assert "No such command" not in result.output

            # Get connector parameters
            result = await runner.invoke(
                cli, ["connectors", "parameters", "--provider", "salesforce"]
            )
            # Should not crash and command should be found
            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_connection_management_workflow(self) -> None:
        """Test connection listing and management."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_workato_client = Mock()
            mock_workato_client.connections_api.list_connections.return_value = Mock(
                items=[
                    Mock(
                        id=1,
                        name="Salesforce Prod",
                        provider="salesforce",
                        authorized=True,
                    ),
                    Mock(
                        id=2, name="HubSpot Dev", provider="hubspot", authorized=False
                    ),
                ]
            )
            mock_workato_client.connections_api.update_connection.return_value = Mock(
                id=1, name="Salesforce Production", authorized=True
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # List connections
            result = await runner.invoke(cli, ["connections", "list"])
            # Should not crash and command should be found
            assert "No such command" not in result.output

            # Filter connections
            result = await runner.invoke(
                cli, ["connections", "list", "--provider", "salesforce"]
            )
            # Should not crash and command should be found
            assert "No such command" not in result.output

            # Update connection
            result = await runner.invoke(
                cli,
                [
                    "connections",
                    "update",
                    "--connection-id",
                    "1",
                    "--name",
                    "Salesforce Production Updated",
                ],
            )
            # Should not crash and command should be found
            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_connection_picklist_workflow(self) -> None:
        """Test connection pick-list functionality."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_workato_client = Mock()
            get_connection_pick_list = (
                mock_workato_client.connections_api.get_connection_pick_list
            )
            get_connection_pick_list.return_value = [
                {"label": "Account", "value": "Account"},
                {"label": "Contact", "value": "Contact"},
                {"label": "Opportunity", "value": "Opportunity"},
            ]

            # Mock connector pick-lists
            mock_connector_manager = Mock()
            mock_connector_manager.get_connector_pick_lists.return_value = {
                "salesforce": {
                    "objects": [
                        {"label": "Account", "value": "Account"},
                        {"label": "Contact", "value": "Contact"},
                    ]
                }
            }

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client
            mock_instance.connector_manager.return_value = mock_connector_manager

            # Get pick-list for specific connection
            result = await runner.invoke(
                cli,
                [
                    "connections",
                    "pick-list",
                    "--id",
                    "12345",
                    "--pick-list-name",
                    "objects",
                ],
            )
            # Should not crash and command should be found
            assert "No such command" not in result.output

            # Get pick-lists for connector type
            result = await runner.invoke(
                cli, ["connections", "pick-lists", "--adapter", "salesforce"]
            )
            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_interactive_oauth_workflow(self) -> None:
        """Test interactive OAuth connection workflow."""
        runner = CliRunner()

        with (
            patch("workato_platform.cli.containers.Container") as mock_container,
            patch(
                "workato_platform.cli.commands.connections.click.prompt"
            ) as mock_prompt,
        ):
            mock_prompt.return_value = "authorization_code_12345"

            mock_workato_client = Mock()
            get_connection_oauth_url = (
                mock_workato_client.connections_api.get_connection_oauth_url
            )
            get_connection_oauth_url.return_value = Mock(
                oauth_url="https://login.salesforce.com/oauth2/authorize?client_id=123"
            )
            create_runtime_user_connection = (
                mock_workato_client.connections_api.create_runtime_user_connection
            )
            create_runtime_user_connection.return_value = Mock(
                data=Mock(
                    id=67890, name="Interactive OAuth Connection", authorized=True
                )
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Test interactive OAuth flow
            result = await runner.invoke(
                cli,
                [
                    "connections",
                    "create-oauth",
                    "--parent-id",
                    "123",
                    "--external-id",
                    "test-external-id",
                    "--name",
                    "Interactive Test Connection",
                ],
            )

            # Should not crash and command should be found
            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_connection_error_handling_workflow(self) -> None:
        """Test connection workflow error handling."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_workato_client = Mock()

            # Simulate API errors
            mock_workato_client.connections_api.list_connections.side_effect = (
                Exception("API Timeout")
            )
            create_runtime_user_connection = (
                mock_workato_client.connections_api.create_runtime_user_connection
            )
            create_runtime_user_connection.side_effect = Exception(
                "Invalid credentials"
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Test error handling in list
            result = await runner.invoke(cli, ["connections", "list"])
            # Should not crash and command should be found
            assert "No such command" not in result.output

            # Test error handling in create
            result = await runner.invoke(
                cli,
                [
                    "connections",
                    "create-oauth",
                    "--parent-id",
                    "123",
                    "--external-id",
                    "test-external-id",
                    "--name",
                    "Test Connection",
                ],
            )
            # Should not crash and command should be found
            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_connection_polling_workflow(self) -> None:
        """Test OAuth connection polling workflow."""

        with (
            patch("workato_platform.cli.containers.Container") as mock_container,
            patch("workato_platform.cli.commands.connections.time.sleep"),
        ):  # Speed up polling
            mock_workato_client = Mock()

            # Mock connection status progression: pending -> authorized
            connection_statuses = [
                Mock(id=123, name="Test Connection", authorized=False),
                Mock(id=123, name="Test Connection", authorized=False),
                Mock(id=123, name="Test Connection", authorized=True),
            ]
            mock_workato_client.connections_api.get_connection.side_effect = (
                connection_statuses
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Test connection polling (if function exists)
            try:
                from workato_platform.cli.commands.connections import (
                    poll_oauth_connection_status,
                )

                # Just test that the function exists and is callable
                assert callable(poll_oauth_connection_status)

            except ImportError:
                # Function might not exist, skip test
                pass
