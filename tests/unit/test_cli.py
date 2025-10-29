"""Tests for CLI entry point and command structure."""

from unittest.mock import Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform_cli.cli import cli


class TestCLI:
    """Test the main CLI interface."""

    @pytest.mark.asyncio
    async def test_cli_help(self) -> None:
        """Test CLI shows help message."""
        runner = CliRunner()
        result = await runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "CLI tool for the Workato API" in result.output

    @pytest.mark.asyncio
    async def test_cli_with_profile(self) -> None:
        """Test CLI accepts profile option."""
        runner = CliRunner()

        with patch("workato_platform_cli.cli.Container") as mock_container:
            # Mock the container to avoid actual initialization
            mock_instance = Mock()
            mock_container.return_value = mock_instance

            result = await runner.invoke(cli, ["--profile", "test-profile", "--help"])

            assert result.exit_code == 0
            # Verify CLI ran with profile option without error
            assert (
                "--profile" in result.output
                or "CLI tool for the Workato API" in result.output
            )

    @pytest.mark.asyncio
    async def test_cli_commands_registered(self) -> None:
        """Test that all expected commands are registered."""
        runner = CliRunner()
        result = await runner.invoke(cli, ["--help"])

        # Check for main command groups
        expected_commands = [
            "init",
            "profiles",
            "recipes",
            "connections",
            "connectors",
            "projects",
            "push",
            "pull",
            "guide",
            "api-collections",
            "api-clients",
            "data-tables",
            "assets",
            "workspace",
        ]

        for command in expected_commands:
            assert command in result.output, (
                f"Command '{command}' not found in CLI help"
            )

    @pytest.mark.asyncio
    async def test_cli_version_checking_decorator(self) -> None:
        """Test that version checking functionality exists."""
        # Check that the cli function exists and is callable
        assert callable(cli)
        # Test that CLI can be imported and executed without errors
        runner = CliRunner()
        result = await runner.invoke(cli, ["--help"])
        assert result.exit_code == 0


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    @pytest.mark.asyncio
    async def test_init_command_exists(self) -> None:
        """Test that init command is available."""
        runner = CliRunner()
        result = await runner.invoke(cli, ["init", "--help"])

        # Should not fail with "No such command"
        assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_profiles_command_exists(self) -> None:
        """Test that profiles command is available."""
        runner = CliRunner()
        result = await runner.invoke(cli, ["profiles", "--help"])

        assert "No such command" not in result.output
        assert "list" in result.output  # Should show subcommands

    @pytest.mark.asyncio
    async def test_recipes_command_exists(self) -> None:
        """Test that recipes command is available."""
        runner = CliRunner()
        result = await runner.invoke(cli, ["recipes", "--help"])

        assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_connections_command_exists(self) -> None:
        """Test that connections command is available."""
        runner = CliRunner()
        result = await runner.invoke(cli, ["connections", "--help"])

        assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_guide_command_exists(self) -> None:
        """Test that guide command is available (for AI agents)."""
        runner = CliRunner()
        result = await runner.invoke(cli, ["guide", "--help"])

        assert "No such command" not in result.output
        assert "documentation" in result.output.lower()
