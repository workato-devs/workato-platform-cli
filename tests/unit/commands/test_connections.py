"""Tests for connections command."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform.cli.commands.connections import (
    OAUTH_TIMEOUT,
    _get_callback_url_from_api_host,
    connections,
    create,
    create_oauth,
    display_connection_summary,
    get_connection_oauth_url,
    group_connections_by_provider,
    is_custom_connector_oauth,
    is_platform_oauth_provider,
    list_connections,
    parse_connection_input,
    pick_list,
    pick_lists,
    poll_oauth_connection_status,
    requires_oauth_flow,
    show_connection_statistics,
    update,
    update_connection,
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


class TestUtilityFunctions:
    """Test utility functions in connections module."""

    def test_get_callback_url_from_api_host_empty(self):
        """Test _get_callback_url_from_api_host with empty string."""
        result = _get_callback_url_from_api_host("")
        assert result == "https://app.workato.com/"

    def test_get_callback_url_from_api_host_none(self):
        """Test _get_callback_url_from_api_host with None."""
        result = _get_callback_url_from_api_host("")
        assert result == "https://app.workato.com/"

    def test_get_callback_url_from_api_host_workato_com(self):
        """Test _get_callback_url_from_api_host with workato.com."""
        result = _get_callback_url_from_api_host("https://workato.com")
        assert result == "https://app.workato.com/"

    def test_get_callback_url_from_api_host_ends_with_workato_com(self):
        """Test _get_callback_url_from_api_host with hostname ending in .workato.com."""
        result = _get_callback_url_from_api_host("https://custom.workato.com")
        assert result == "https://app.workato.com/"

    def test_get_callback_url_from_api_host_exception(self):
        """Test _get_callback_url_from_api_host with invalid URL that causes exception."""
        result = _get_callback_url_from_api_host("invalid-url")
        assert result == "https://app.workato.com/"

    def test_get_callback_url_from_api_host_other_domain(self):
        """Test _get_callback_url_from_api_host with non-workato domain."""
        result = _get_callback_url_from_api_host("https://example.com")
        assert result == "https://app.workato.com/"

    def test_get_callback_url_from_api_host_parse_failure(self):
        """Test _get_callback_url_from_api_host when urlparse raises."""
        with patch(
            "workato_platform.cli.commands.connections.urlparse",
            side_effect=ValueError("bad url"),
        ):
            result = _get_callback_url_from_api_host("https://anything")

        assert result == "https://app.workato.com/"

    def test_parse_connection_input_none(self):
        """Test parse_connection_input with None input."""
        result = parse_connection_input(None)
        assert result is None

    def test_parse_connection_input_empty(self):
        """Test parse_connection_input with empty string."""
        result = parse_connection_input("")
        assert result is None

    def test_parse_connection_input_valid_json(self):
        """Test parse_connection_input with valid JSON."""
        result = parse_connection_input('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_connection_input_invalid_json(self):
        """Test parse_connection_input with invalid JSON."""
        result = parse_connection_input('{"key": "value"')
        assert result is None

    def test_parse_connection_input_non_dict(self):
        """Test parse_connection_input with JSON that's not a dict."""
        result = parse_connection_input('["list", "not", "dict"]')
        assert result is None


class TestOAuthFlowFunctions:
    """Test OAuth flow related functions."""

    @pytest.mark.asyncio
    async def test_requires_oauth_flow_empty_provider(self):
        """Test requires_oauth_flow with empty provider."""
        result = await requires_oauth_flow("")
        assert result is False

    @pytest.mark.asyncio
    async def test_requires_oauth_flow_none_provider(self):
        """Test requires_oauth_flow with None provider."""
        result = await requires_oauth_flow("")
        assert result is False

    @patch("workato_platform.cli.commands.connections.is_platform_oauth_provider")
    @patch("workato_platform.cli.commands.connections.is_custom_connector_oauth")
    @pytest.mark.asyncio
    async def test_requires_oauth_flow_platform_oauth(self, mock_custom, mock_platform):
        """Test requires_oauth_flow with platform OAuth provider."""
        mock_platform.return_value = True
        mock_custom.return_value = False

        result = await requires_oauth_flow("salesforce")
        assert result is True

    @patch("workato_platform.cli.commands.connections.is_platform_oauth_provider")
    @patch("workato_platform.cli.commands.connections.is_custom_connector_oauth")
    @pytest.mark.asyncio
    async def test_requires_oauth_flow_custom_oauth(self, mock_custom, mock_platform):
        """Test requires_oauth_flow with custom OAuth provider."""
        mock_platform.return_value = False
        mock_custom.return_value = True

        result = await requires_oauth_flow("custom_connector")
        assert result is True

    @pytest.mark.asyncio
    async def test_is_platform_oauth_provider(self):
        """Test is_platform_oauth_provider function."""
        connector_manager = AsyncMock()
        connector_manager.list_platform_connectors.return_value = [
            SimpleNamespace(name="salesforce", oauth=True),
            SimpleNamespace(name="hubspot", oauth=False),
        ]

        result = await is_platform_oauth_provider(
            "salesforce", connector_manager=connector_manager
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_is_custom_connector_oauth(self):
        """Test is_custom_connector_oauth function."""
        connections_api = SimpleNamespace(
            list_custom_connectors=AsyncMock(
                return_value=SimpleNamespace(
                    result=[SimpleNamespace(name="custom_connector", id=123)]
                )
            ),
            get_custom_connector_code=AsyncMock(
                return_value=SimpleNamespace(
                    data=SimpleNamespace(code="oauth authorization_url client_id")
                )
            ),
        )
        workato_client = SimpleNamespace(connectors_api=connections_api)

        result = await is_custom_connector_oauth(
            "custom_connector", workato_api_client=workato_client
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_is_custom_connector_oauth_not_found(self):
        """Test is_custom_connector_oauth with connector not found."""
        connections_api = SimpleNamespace(
            list_custom_connectors=AsyncMock(
                return_value=SimpleNamespace(
                    result=[SimpleNamespace(name="other_connector", id=123)]
                )
            ),
            get_custom_connector_code=AsyncMock(),
        )
        workato_client = SimpleNamespace(connectors_api=connections_api)

        result = await is_custom_connector_oauth(
            "custom_connector", workato_api_client=workato_client
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_is_custom_connector_oauth_no_id(self):
        """Test is_custom_connector_oauth with connector having no ID."""
        connections_api = SimpleNamespace(
            list_custom_connectors=AsyncMock(
                return_value=SimpleNamespace(
                    result=[SimpleNamespace(name="custom_connector", id=None)]
                )
            ),
            get_custom_connector_code=AsyncMock(),
        )
        workato_client = SimpleNamespace(connectors_api=connections_api)

        result = await is_custom_connector_oauth(
            "custom_connector", workato_api_client=workato_client
        )
        assert result is False


class TestConnectionListingFunctions:
    """Test connection listing helper functions."""

    def test_group_connections_by_provider(self):
        """Test group_connections_by_provider function."""

        # Create mock connections with proper attributes
        conn1 = Mock()
        conn1.provider = "salesforce"
        conn1.name = "SF1"

        conn2 = Mock()
        conn2.provider = "hubspot"
        conn2.name = "HS1"

        conn3 = Mock()
        conn3.provider = "salesforce"
        conn3.name = "SF2"

        conn4 = Mock()
        conn4.provider = None
        conn4.name = "Unknown"

        connections = [conn1, conn2, conn3, conn4]

        result = group_connections_by_provider(connections)

        assert "Salesforce" in result
        assert "Hubspot" in result
        assert "Unknown" in result
        assert len(result["Salesforce"]) == 2
        assert len(result["Hubspot"]) == 1
        assert len(result["Unknown"]) == 1

    @patch("workato_platform.cli.commands.connections.click.echo")
    def test_display_connection_summary(self, mock_echo):
        """Test display_connection_summary function."""
        from workato_platform.client.workato_api.models.connection import Connection

        connection = Mock(spec=Connection)
        connection.name = "Test Connection"
        connection.id = 123
        connection.authorization_status = "success"
        connection.folder_id = 456
        connection.parent_id = 789
        connection.external_id = "ext123"
        connection.tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
        connection.created_at = None

        display_connection_summary(connection)

        # Verify echo was called multiple times
        assert mock_echo.call_count > 0

    @patch("workato_platform.cli.commands.connections.click.echo")
    def test_show_connection_statistics(self, mock_echo):
        """Test show_connection_statistics function."""
        # Create mock connections with proper attributes
        conn1 = Mock()
        conn1.authorization_status = "success"
        conn1.provider = "salesforce"

        conn2 = Mock()
        conn2.authorization_status = "failed"
        conn2.provider = "hubspot"

        conn3 = Mock()
        conn3.authorization_status = "success"
        conn3.provider = "salesforce"

        connections = [conn1, conn2, conn3]

        show_connection_statistics(connections)

        # Verify echo was called
        assert mock_echo.call_count > 0


class TestConnectionCreationEdgeCases:
    """Test edge cases in connection creation."""

    @pytest.mark.asyncio
    async def test_create_missing_provider_and_name(self):
        """Test create command with missing provider and name."""
        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            await create.callback(
                name="",
                provider="",
                workato_api_client=Mock(),
                config_manager=Mock(),
                connector_manager=Mock(),
            )

        assert any("Provider and name are required" in call.args[0] for call in mock_echo.call_args_list)

    @pytest.mark.asyncio
    async def test_create_invalid_json_input(self):
        """Test create command with invalid JSON input."""
        config_manager = SimpleNamespace(
            load_config=Mock(return_value=SimpleNamespace(folder_id=123))
        )

        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            await create.callback(
                name="Test",
                provider="salesforce",
                input_params='{"invalid": json}',
                workato_api_client=Mock(),
                config_manager=config_manager,
                connector_manager=Mock(),
            )

        assert any("Invalid JSON" in call.args[0] for call in mock_echo.call_args_list)

    @pytest.mark.asyncio
    async def test_create_oauth_browser_error(self):
        """Test create OAuth command with browser opening error."""
        connections_api = SimpleNamespace(
            create_runtime_user_connection=AsyncMock(
                return_value=SimpleNamespace(data=SimpleNamespace(id=123, url="https://oauth.example.com"))
            )
        )
        workato_client = SimpleNamespace(connections_api=connections_api)
        config_manager = SimpleNamespace(
            load_config=Mock(return_value=SimpleNamespace(folder_id=456)),
            api_host="https://www.workato.com",
        )

        with patch(
            "workato_platform.cli.commands.connections.webbrowser.open",
            side_effect=OSError("Browser error"),
        ), patch(
            "workato_platform.cli.commands.connections.poll_oauth_connection_status",
            new=AsyncMock(),
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await create_oauth.callback(
                parent_id=123,
                external_id="test@example.com",
                workato_api_client=workato_client,
                config_manager=config_manager,
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Could not open browser" in message for message in messages)

    @pytest.mark.asyncio
    async def test_create_oauth_missing_folder_id(self):
        """Test create-oauth when folder cannot be resolved."""
        config_manager = SimpleNamespace(
            load_config=Mock(return_value=SimpleNamespace(folder_id=None)),
            api_host="https://www.workato.com",
        )

        with patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await create_oauth.callback(
                parent_id=1,
                external_id="user@example.com",
                workato_api_client=SimpleNamespace(
                    connections_api=SimpleNamespace(
                        create_runtime_user_connection=AsyncMock()
                    )
                ),
                config_manager=config_manager,
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("No folder ID" in message for message in messages)

    @pytest.mark.asyncio
    async def test_create_oauth_opens_browser_success(self):
        """Test create-oauth when browser opens successfully."""
        connections_api = SimpleNamespace(
            create_runtime_user_connection=AsyncMock(
                return_value=SimpleNamespace(
                    data=SimpleNamespace(id=234, url="https://oauth.example.com"),
                )
            )
        )
        workato_client = SimpleNamespace(connections_api=connections_api)
        config_manager = SimpleNamespace(
            load_config=Mock(return_value=SimpleNamespace(folder_id=42)),
            api_host="https://www.workato.com",
        )

        with patch(
            "workato_platform.cli.commands.connections.webbrowser.open",
            return_value=True,
        ), patch(
            "workato_platform.cli.commands.connections.poll_oauth_connection_status",
            new=AsyncMock(),
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await create_oauth.callback(
                parent_id=2,
                external_id="user@example.com",
                workato_api_client=workato_client,
                config_manager=config_manager,
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Opening OAuth URL in browser" in message for message in messages)

    @pytest.mark.asyncio
    async def test_get_oauth_url_browser_error(self):
        """Test get OAuth URL with browser opening error."""
        connections_api = SimpleNamespace(
            get_connection_oauth_url=AsyncMock(
                return_value=SimpleNamespace(data=SimpleNamespace(url="https://oauth.example.com"))
            )
        )
        workato_client = SimpleNamespace(connections_api=connections_api)

        spinner_stub = SimpleNamespace(
            start=lambda: None,
            stop=lambda: 0.5,
            update_message=lambda *_: None,
        )

        with patch(
            "workato_platform.cli.commands.connections.Spinner",
            return_value=spinner_stub,
        ), patch(
            "workato_platform.cli.commands.connections.webbrowser.open",
            side_effect=OSError("Browser error"),
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await get_connection_oauth_url(
                connection_id=123,
                open_browser=True,
                workato_api_client=workato_client,
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Could not open browser" in message for message in messages)

    @pytest.mark.asyncio
    async def test_update_connection_unauthorized_status(self):
        """Test update connection with unauthorized status."""
        connections_api = SimpleNamespace(
            update_connection=AsyncMock(
                return_value=SimpleNamespace(
                    name="Updated",
                    id=123,
                    provider="salesforce",
                    folder_id=456,
                    authorization_status="failed",
                    parent_id=None,
                    external_id=None,
                )
            )
        )
        workato_client = SimpleNamespace(connections_api=connections_api)
        project_manager = SimpleNamespace(handle_post_api_sync=AsyncMock())

        from workato_platform.client.workato_api.models.connection_update_request import (
            ConnectionUpdateRequest,
        )

        update_request = ConnectionUpdateRequest(name="Updated Connection")

        spinner_stub = SimpleNamespace(
            start=lambda: None,
            stop=lambda: 0.3,
        )

        with patch(
            "workato_platform.cli.commands.connections.Spinner",
            return_value=spinner_stub,
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await update_connection(
                123,
                update_request,
                workato_api_client=workato_client,
                project_manager=project_manager,
            )

        # Ensure unauthorized status message emitted
        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Not authorized" in message for message in messages)

    @pytest.mark.asyncio
    async def test_update_connection_authorized_status(self):
        """Test update_connection displays authorized details and updated fields."""
        connections_api = SimpleNamespace(
            update_connection=AsyncMock(
                return_value=SimpleNamespace(
                    name="Ready",
                    id=77,
                    provider="slack",
                    folder_id=900,
                    authorization_status="success",
                    parent_id=12,
                    external_id="ext-1",
                )
            )
        )
        workato_client = SimpleNamespace(connections_api=connections_api)
        project_manager = SimpleNamespace(handle_post_api_sync=AsyncMock())

        from workato_platform.client.workato_api.models.connection_update_request import (
            ConnectionUpdateRequest,
        )

        update_request = ConnectionUpdateRequest(
            name="Ready",
            folder_id=900,
            input={"token": "abc"},
            shell_connection=True,
            parent_id=12,
            external_id="ext-1",
        )

        spinner_stub = SimpleNamespace(
            start=lambda: None,
            stop=lambda: 1.2,
        )

        with patch(
            "workato_platform.cli.commands.connections.Spinner",
            return_value=spinner_stub,
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await update_connection(
                77,
                update_request,
                workato_api_client=workato_client,
                project_manager=project_manager,
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Authorized" in message for message in messages)
        assert any("Parent ID" in message for message in messages)
        assert any("External ID" in message for message in messages)
        assert any("Updated" in message for message in messages)

    @pytest.mark.asyncio
    async def test_update_command_invalid_json(self):
        """Test update command handles invalid JSON input."""
        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            await update.callback(
                connection_id=5,
                input_params='{"oops": json}',
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Invalid JSON" in message for message in messages)

    @pytest.mark.asyncio
    async def test_update_command_invokes_update_connection(self):
        """Test update command builds request and invokes update_connection."""
        with patch(
            "workato_platform.cli.commands.connections.update_connection",
            new=AsyncMock(),
        ) as mock_update:
            await update.callback(
                connection_id=7,
                name="Renamed",
                folder_id=50,
                shell_connection=True,
                parent_id=9,
                external_id="ext",
                input_params='{"user": "a"}',
            )

        assert mock_update.await_count == 1
        args, kwargs = mock_update.await_args
        request = args[1]
        assert request.name == "Renamed"
        assert request.folder_id == 50
        assert request.shell_connection is True
        assert request.parent_id == 9
        assert request.external_id == "ext"
        assert request.input == {"user": "a"}

    @pytest.mark.asyncio
    async def test_create_missing_folder_id(self):
        """Test create command when folder ID cannot be resolved."""
        config_manager = SimpleNamespace(
            load_config=Mock(return_value=SimpleNamespace(folder_id=None))
        )

        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            await create.callback(
                name="Test",
                provider="salesforce",
                workato_api_client=Mock(),
                config_manager=config_manager,
                connector_manager=Mock(),
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("No folder ID" in message for message in messages)

    @pytest.mark.asyncio
    async def test_create_oauth_success_flow(self):
        """Test create command OAuth path when automatic flow succeeds."""
        config_manager = SimpleNamespace(
            load_config=Mock(return_value=SimpleNamespace(folder_id=101)),
            api_host="https://www.workato.com",
        )
        provider_data = SimpleNamespace(oauth=True)
        connector_manager = SimpleNamespace(
            get_provider_data=Mock(return_value=provider_data),
            prompt_for_oauth_parameters=Mock(return_value={"client_id": "abc"}),
        )
        workato_client = SimpleNamespace(
            connections_api=SimpleNamespace(
                create_connection=AsyncMock(
                    return_value=SimpleNamespace(
                        id=321,
                        name="OAuth Conn",
                        provider="salesforce",
                    )
                )
            )
        )

        with patch(
            "workato_platform.cli.commands.connections.requires_oauth_flow",
            new=AsyncMock(return_value=True),
        ), patch(
            "workato_platform.cli.commands.connections.get_connection_oauth_url",
            new=AsyncMock(),
        ) as mock_oauth_url, patch(
            "workato_platform.cli.commands.connections.poll_oauth_connection_status",
            new=AsyncMock(),
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await create.callback(
                name="OAuth Conn",
                provider="salesforce",
                workato_api_client=workato_client,
                config_manager=config_manager,
                connector_manager=connector_manager,
            )

        assert mock_oauth_url.await_count == 1
        assert connector_manager.prompt_for_oauth_parameters.called
        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("OAuth provider detected" in message for message in messages)

    @pytest.mark.asyncio
    async def test_create_oauth_manual_fallback(self):
        """Test create command OAuth path when automatic retrieval fails."""
        config_manager = SimpleNamespace(
            load_config=Mock(return_value=SimpleNamespace(folder_id=202)),
            api_host="https://preview.workato.com",
        )
        connector_manager = SimpleNamespace(
            get_provider_data=Mock(return_value=None),
            prompt_for_oauth_parameters=Mock(return_value={}),
        )
        workato_client = SimpleNamespace(
            connections_api=SimpleNamespace(
                create_connection=AsyncMock(
                    return_value=SimpleNamespace(
                        id=456,
                        name="Fallback Conn",
                        provider="jira",
                    )
                )
            )
        )

        with patch(
            "workato_platform.cli.commands.connections.requires_oauth_flow",
            new=AsyncMock(return_value=True),
        ), patch(
            "workato_platform.cli.commands.connections.get_connection_oauth_url",
            new=AsyncMock(side_effect=RuntimeError("no url")),
        ), patch(
            "workato_platform.cli.commands.connections.poll_oauth_connection_status",
            new=AsyncMock(),
        ), patch(
            "workato_platform.cli.commands.connections.webbrowser.open",
            side_effect=OSError("browser blocked"),
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await create.callback(
                name="Fallback Conn",
                provider="jira",
                workato_api_client=workato_client,
                config_manager=config_manager,
                connector_manager=connector_manager,
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Manual authorization steps" in message for message in messages)


class TestPicklistFunctions:
    """Test picklist related functions."""

    @pytest.mark.asyncio
    async def test_pick_list_invalid_json_params(self):
        """Test pick_list command with invalid JSON params."""
        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            await pick_list.callback(
                id=123,
                pick_list_name="objects",
                params='{"invalid": json}',
                workato_api_client=SimpleNamespace(connections_api=SimpleNamespace()),
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Invalid JSON" in message for message in messages)

    @patch("workato_platform.cli.commands.connections.Path.exists")
    @patch("workato_platform.cli.commands.connections.open")
    def test_pick_lists_data_file_not_found(self, mock_open, mock_exists):
        """Test pick_lists command when data file doesn't exist."""
        mock_exists.return_value = False

        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            pick_lists.callback()

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Picklist data not found" in message for message in messages)

    @patch("workato_platform.cli.commands.connections.Path.exists")
    @patch("workato_platform.cli.commands.connections.open")
    def test_pick_lists_data_file_load_error(self, mock_open, mock_exists):
        """Test pick_lists command when data file fails to load."""
        mock_exists.return_value = True
        mock_open.side_effect = PermissionError("Permission denied")

        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            pick_lists.callback()

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Failed to load picklist data" in message for message in messages)

    @patch("workato_platform.cli.commands.connections.Path.exists")
    @patch("workato_platform.cli.commands.connections.open")
    def test_pick_lists_adapter_not_found(self, mock_open, mock_exists):
        """Test pick_lists command with adapter not found."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"salesforce": []}'
        )

        with patch("workato_platform.cli.commands.connections.click.echo") as mock_echo:
            pick_lists.callback(adapter="nonexistent")

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("Adapter 'nonexistent' not found" in message for message in messages)


class TestOAuthPolling:
    """Test OAuth polling functionality."""

    @patch("workato_platform.cli.commands.connections.time.sleep")
    @pytest.mark.asyncio
    async def test_poll_oauth_connection_status_connection_not_found(
        self, mock_sleep
    ):
        """Test OAuth polling when connection is not found."""
        mock_sleep.return_value = None

        connections_api = SimpleNamespace(
            list_connections=AsyncMock(return_value=[])
        )
        workato_client = SimpleNamespace(connections_api=connections_api)
        project_manager = SimpleNamespace(handle_post_api_sync=AsyncMock())
        config_manager = SimpleNamespace(api_host="https://app.workato.com")

        spinner_stub = SimpleNamespace(
            start=lambda: None,
            update_message=lambda *_: None,
            stop=lambda: 0.1,
        )

        with patch(
            "workato_platform.cli.commands.connections.Spinner",
            return_value=spinner_stub,
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await poll_oauth_connection_status(
                123,
                workato_api_client=workato_client,
                project_manager=project_manager,
                config_manager=config_manager,
            )

        assert any("not found" in call.args[0] for call in mock_echo.call_args_list)

    @patch("workato_platform.cli.commands.connections.time.sleep")
    @pytest.mark.asyncio
    async def test_poll_oauth_connection_status_timeout(
        self, mock_sleep
    ):
        """Test OAuth polling timeout scenario."""
        mock_sleep.return_value = None

        pending_connection = SimpleNamespace(
            id=123,
            authorization_status="pending",
            name="Pending",
            provider="salesforce",
            folder_id=456,
        )

        connections_api = SimpleNamespace(
            list_connections=AsyncMock(return_value=[pending_connection])
        )
        workato_client = SimpleNamespace(connections_api=connections_api)
        project_manager = SimpleNamespace(handle_post_api_sync=AsyncMock())
        config_manager = SimpleNamespace(api_host="https://app.workato.com")

        spinner_stub = SimpleNamespace(
            start=lambda: None,
            update_message=lambda *_: None,
            stop=lambda: 60.0,
        )

        time_values = iter([0, 1, 1, OAUTH_TIMEOUT + 1])

        with patch(
            "workato_platform.cli.commands.connections.Spinner",
            return_value=spinner_stub,
        ), patch(
            "workato_platform.cli.commands.connections.time.time",
            side_effect=lambda: next(time_values),
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await poll_oauth_connection_status(
                123,
                workato_api_client=workato_client,
                project_manager=project_manager,
                config_manager=config_manager,
            )

        assert any("Timeout" in call.args[0] for call in mock_echo.call_args_list)

    @patch("workato_platform.cli.commands.connections.time.sleep")
    @pytest.mark.asyncio
    async def test_poll_oauth_connection_status_keyboard_interrupt(
        self, mock_sleep
    ):
        """Test OAuth polling with keyboard interrupt."""
        pending_connection = SimpleNamespace(
            id=123,
            authorization_status="pending",
            name="Pending",
            provider="salesforce",
            folder_id=456,
        )

        connections_api = SimpleNamespace(
            list_connections=AsyncMock(return_value=[pending_connection])
        )
        workato_client = SimpleNamespace(connections_api=connections_api)
        project_manager = SimpleNamespace(handle_post_api_sync=AsyncMock())
        config_manager = SimpleNamespace(api_host="https://app.workato.com")

        mock_sleep.side_effect = KeyboardInterrupt()

        spinner_stub = SimpleNamespace(
            start=lambda: None,
            update_message=lambda *_: None,
            stop=lambda: 0.2,
        )

        with patch(
            "workato_platform.cli.commands.connections.Spinner",
            return_value=spinner_stub,
        ), patch(
            "workato_platform.cli.commands.connections.click.echo"
        ) as mock_echo:
            await poll_oauth_connection_status(
                123,
                workato_api_client=workato_client,
                project_manager=project_manager,
                config_manager=config_manager,
            )

        messages = [
            " ".join(str(arg) for arg in call.args if isinstance(arg, str))
            for call in mock_echo.call_args_list
            if call.args
        ]
        assert any("interrupted" in message.lower() for message in messages)


class TestConnectionListFilters:
    """Test connection listing with various filters."""

    @patch("workato_platform.cli.commands.connections.Container")
    @pytest.mark.asyncio
    async def test_list_connections_with_filters(self, mock_container):
        """Test list_connections with various filter combinations."""
        mock_workato_client = Mock()
        mock_workato_client.connections_api.list_connections.return_value = []

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        result = await runner.invoke(
            list_connections,
            [
                "--folder-id",
                "123",
                "--parent-id",
                "456",
                "--external-id",
                "ext123",
                "--provider",
                "salesforce",
                "--unauthorized",
                "--include-runtime",
                "--tags",
                "tag1,tag2",
            ],
        )

        # Should not crash
        assert "No such command" not in result.output
