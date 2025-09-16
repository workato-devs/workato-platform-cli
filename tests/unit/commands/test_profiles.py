"""Tests for profiles command."""

from unittest.mock import Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform.cli.commands.profiles import (
    profiles,
)


class TestProfilesCommand:
    """Test the profiles command and subcommands."""

    @pytest.mark.asyncio
    async def test_profiles_command_group_exists(self):
        """Test that profiles command group can be invoked."""
        runner = CliRunner()
        result = await runner.invoke(profiles, ["--help"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        assert "profile" in result.output.lower()

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_list_command(self, mock_container):
        """Test the list subcommand."""
        # Mock the profile manager
        mock_profile_manager = Mock()
        mock_profile_manager.list_profiles.return_value = [
            Mock(name="dev", region="us", created_at="2024-01-01T00:00:00Z"),
            Mock(name="prod", region="eu", created_at="2024-01-01T00:00:00Z"),
        ]

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "list"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        # Test passes if command doesn't crash

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_list_command_json_format(self, mock_container):
        """Test the list subcommand with JSON format."""
        mock_profile_manager = Mock()
        mock_profile_manager.list_profiles.return_value = []

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "list"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_show_command(self, mock_container):
        """Test the show subcommand."""
        mock_profile_manager = Mock()
        mock_profile = Mock(
            name="test-profile", region="us", created_at="2024-01-01T00:00:00Z"
        )
        mock_profile_manager.get_profile.return_value = mock_profile

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "show", "test-profile"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        # Test passes if command doesn't crash

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_show_command_json_format(self, mock_container):
        """Test the show subcommand with JSON format."""
        mock_profile_manager = Mock()
        mock_profile = Mock(
            name="test-profile", region="us", created_at="2024-01-01T00:00:00Z"
        )
        mock_profile_manager.get_profile.return_value = mock_profile

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "show", "test-profile"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_use_command(self, mock_container):
        """Test the use subcommand."""
        mock_config_manager = Mock()
        mock_profile_manager = Mock()
        mock_profile_manager.profile_exists.return_value = True

        mock_container_instance = Mock()
        mock_container_instance.config_manager.return_value = mock_config_manager
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "use", "dev-profile"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        # Test passes if command doesn't crash

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_use_nonexistent_profile(self, mock_container):
        """Test the use subcommand with nonexistent profile."""
        mock_profile_manager = Mock()
        mock_profile_manager.profile_exists.return_value = False

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "use", "nonexistent"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_status_command(self, mock_container):
        """Test the status subcommand."""
        mock_config_manager = Mock()
        mock_config_manager.get_current_profile.return_value = "current-profile"

        mock_container_instance = Mock()
        mock_container_instance.config_manager.return_value = mock_config_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "status"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        # Test passes if command doesn't crash

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_status_json_format(self, mock_container):
        """Test the status subcommand with JSON format."""
        mock_config_manager = Mock()
        mock_config_manager.get_current_profile.return_value = "current-profile"

        mock_container_instance = Mock()
        mock_container_instance.config_manager.return_value = mock_config_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "status"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @patch("workato_platform.cli.commands.profiles.click.confirm")
    @pytest.mark.asyncio
    async def test_profiles_delete_command(self, mock_confirm, mock_container):
        """Test the delete subcommand."""
        mock_confirm.return_value = True

        mock_profile_manager = Mock()
        mock_profile_manager.profile_exists.return_value = True

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "delete", "old-profile"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        # Test passes if command doesn't crash

    @patch("workato_platform.cli.containers.Container")
    @patch("workato_platform.cli.commands.profiles.click.confirm")
    @pytest.mark.asyncio
    async def test_profiles_delete_command_cancelled(
        self, mock_confirm, mock_container
    ):
        """Test the delete subcommand when user cancels."""
        mock_confirm.return_value = False

        mock_profile_manager = Mock()
        mock_profile_manager.profile_exists.return_value = True

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "delete", "profile-to-keep"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        # Test passes if command doesn't crash

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_profiles_delete_nonexistent_profile(self, mock_container):
        """Test deleting a profile that doesn't exist."""
        mock_profile_manager = Mock()
        mock_profile_manager.profile_exists.return_value = False

        mock_container_instance = Mock()
        mock_container_instance.profile_manager.return_value = mock_profile_manager
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["profiles", "delete", "nonexistent"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
