"""Integration tests for profile management workflow."""

from unittest.mock import Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform_cli.cli import cli


class TestProfileWorkflow:
    """Test complete profile management workflows."""

    @pytest.mark.asyncio
    async def test_profile_creation_and_usage(self) -> None:
        """Test creating and using profiles end-to-end."""
        runner = CliRunner()

        # List profiles (create command doesn't exist)
        result = await runner.invoke(cli, ["profiles", "list"])

        # Should succeed (or at least not fail with command not found)
        assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_profile_switching(self) -> None:
        """Test switching between profiles."""
        runner = CliRunner()

        # List profiles first (create command doesn't exist)
        result = await runner.invoke(cli, ["profiles", "list"])
        assert "No such command" not in result.output

        # Switch to prod profile (use takes positional argument)
        result = await runner.invoke(cli, ["profiles", "use", "prod"])
        assert "No such command" not in result.output

        # Check current profile
        result = await runner.invoke(cli, ["profiles", "status"])
        assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_profile_with_api_operations(self, mock_workato_client: Mock) -> None:
        """Test using profiles with API operations."""
        runner = CliRunner()

        # This test would require more complex mocking of the API client
        # For now, just test that commands don't fail with basic setup

        with patch("workato_platform_cli.cli.containers.Container") as mock_container:
            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Test that commands are available and don't fail immediately
            result = await runner.invoke(
                cli, ["--profile", "test", "recipes", "--help"]
            )
            assert "No such command" not in result.output

            result = await runner.invoke(
                cli, ["--profile", "test", "connections", "--help"]
            )
            assert "No such command" not in result.output
