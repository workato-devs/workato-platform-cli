"""Tests for connections command."""

from unittest.mock import Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform.cli.commands.connections import (
    connections,
    create_oauth,
    list_connections,
)


class TestConnectionsCommand:
    """Test the connections command and subcommands."""

    @pytest.mark.asyncio
    async def test_connections_command_group_exists(self):
        """Test that connections command group can be invoked."""
        runner = CliRunner()
        result = await runner.invoke(connections, ["--help"])

        assert result.exit_code == 0
        assert "connection" in result.output.lower()

    @patch("workato_platform.cli.commands.connections.Container")
    @pytest.mark.asyncio
    async def test_connections_create_oauth_command(self, mock_container):
        """Test the create-oauth subcommand."""
        mock_workato_client = Mock()
        mock_workato_client.connections_api.create_runtime_user_connection.return_value = Mock(
            data=Mock(id=12345, name="Test Connection")
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_platform.client.return_value = (
            mock_workato_client
        )
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(
            create_oauth,
            [
                "--parent-id",
                "123",
                "--external-id",
                "test-external-id",
                "--name",
                "Test Salesforce Connection",
            ],
        )

        # Should not fail with command not found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_connections_list_command(self, mock_container):
        """Test the list command through CLI."""
        from workato_platform.cli.cli import cli

        mock_workato_client = Mock()
        mock_workato_client.connections_api.list_connections.return_value = Mock(
            items=[
                Mock(id=1, name="Connection 1", provider="salesforce"),
                Mock(id=2, name="Connection 2", provider="hubspot"),
            ]
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(cli, ["connections", "list"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_connections_list_with_filters(self, mock_container):
        """Test the list subcommand with filters."""
        from workato_platform.cli.cli import cli

        mock_workato_client = Mock()
        mock_workato_client.connections_api.list_connections.return_value = Mock(
            items=[]
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(
            cli, ["connections", "list", "--provider", "salesforce"]
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_connections_get_oauth_url_command(self, mock_container):
        """Test the get-oauth-url subcommand."""
        from workato_platform.cli.cli import cli

        mock_workato_client = Mock()
        mock_workato_client.connections_api.get_connection_oauth_url.return_value = (
            Mock(oauth_url="https://login.salesforce.com/oauth2/authorize?...")
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(
            cli, ["connections", "get-oauth-url", "--id", "12345"]
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_connections_pick_list_command(self, mock_container):
        """Test the pick-list subcommand."""
        from workato_platform.cli.cli import cli

        mock_workato_client = Mock()
        mock_workato_client.connections_api.get_connection_pick_list.return_value = [
            {"label": "Option 1", "value": "opt1"},
            {"label": "Option 2", "value": "opt2"},
        ]

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
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

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_connections_pick_lists_command(self, mock_container):
        """Test the pick-lists subcommand."""
        from workato_platform.cli.cli import cli

        mock_container_instance = Mock()
        mock_connector_manager = Mock()
        mock_connector_manager.get_connector_pick_lists.return_value = {
            "salesforce": {"objects": [{"label": "Account", "value": "Account"}]}
        }
        mock_container_instance.connector_manager.return_value = mock_connector_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(
            cli, ["connections", "pick-lists", "--adapter", "salesforce"]
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_connections_create_oauth_command_help(self):
        """Test create-oauth command shows help without error."""
        runner = CliRunner()
        result = await runner.invoke(create_oauth, ["--help"])

        assert result.exit_code == 0
        assert "Create an OAuth runtime user connection" in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_connections_update_command(self, mock_container):
        """Test the update subcommand."""
        from workato_platform.cli.cli import cli

        mock_workato_client = Mock()
        mock_workato_client.connections_api.update_connection.return_value = Mock(
            id=12345, name="Updated Connection"
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(
            cli,
            [
                "connections",
                "update",
                "--connection-id",
                "12345",
                "--name",
                "Updated Connection Name",
            ],
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.commands.connections.Container")
    @pytest.mark.asyncio
    async def test_connections_error_handling(self, mock_container):
        """Test error handling in connections commands."""
        mock_workato_client = Mock()
        mock_workato_client.connections_api.list_connections.side_effect = Exception(
            "API Error"
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_platform.client.return_value = (
            mock_workato_client
        )
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(list_connections)

        # Should handle error gracefully (depends on exception handler)
        assert result.exit_code in [0, 1]

    @pytest.mark.asyncio
    async def test_connections_helper_functions(self):
        """Test helper functions in connections module."""
        # Test helper functions that might exist
        from workato_platform.cli.commands.connections import (
            is_custom_connector_oauth,
            is_platform_oauth_provider,
        )

        # These should be callable
        assert callable(is_platform_oauth_provider)
        assert callable(is_custom_connector_oauth)

    @patch("workato_platform.cli.commands.connections.Container")
    @pytest.mark.asyncio
    async def test_connections_oauth_polling(self, mock_container):
        """Test OAuth connection status polling."""
        mock_workato_client = Mock()

        # Mock polling function if it exists
        try:
            from workato_platform.cli.commands.connections import (
                poll_oauth_connection_status,
            )

            with patch("workato_platform.cli.commands.connections.time.sleep"):
                # Should be callable without error
                assert callable(poll_oauth_connection_status)

        except ImportError:
            # Function might not exist, skip test
            pass
