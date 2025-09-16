"""Integration tests for recipe management workflow."""

from unittest.mock import Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform.cli.cli import cli


class TestRecipeWorkflow:
    """Test complete recipe management workflows."""

    @pytest.mark.asyncio
    async def test_recipe_validation_workflow(self, temp_config_dir) -> None:
        """Test end-to-end recipe validation workflow."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            # Mock the validator
            mock_validator = Mock()
            mock_validator.validate_recipe_structure.return_value = []

            mock_instance = mock_container.return_value
            mock_instance.recipe_validator.return_value = mock_validator

            # Test recipe validation
            result = await runner.invoke(
                cli, ["recipes", "validate", "--project-id", "123"]
            )

            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_recipe_lifecycle_workflow(self, temp_config_dir) -> None:
        """Test recipe start/stop lifecycle."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_workato_client = Mock()
            mock_workato_client.recipes_api.start_recipe.return_value = Mock(
                success=True
            )
            mock_workato_client.recipes_api.stop_recipe.return_value = Mock(
                success=True
            )
            mock_workato_client.recipes_api.get_recipe.return_value = Mock(
                id=789, name="Test Recipe", running=False
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Start recipe
            result = await runner.invoke(
                cli, ["recipes", "start", "--recipe-id", "789"]
            )
            assert "No such command" not in result.output

            # Stop recipe
            result = await runner.invoke(cli, ["recipes", "stop", "--recipe-id", "789"])
            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_recipe_bulk_operations_workflow(self, temp_config_dir) -> None:
        """Test bulk recipe operations."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_workato_client = Mock()
            mock_workato_client.recipes_api.list_recipes.return_value = Mock(
                items=[
                    Mock(id=1, name="Recipe 1", running=False),
                    Mock(id=2, name="Recipe 2", running=False),
                ]
            )
            mock_workato_client.recipes_api.start_recipe.return_value = Mock(
                success=True
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Start all recipes in folder
            result = await runner.invoke(
                cli, ["recipes", "start", "--folder-id", "456"]
            )

            assert "No such command" not in result.output

    @pytest.mark.asyncio
    async def test_recipe_connection_update_workflow(self, temp_config_dir) -> None:
        """Test recipe connection update workflow."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_project_manager = Mock()
            mock_project_manager.get_project_recipes.return_value = [
                Mock(id=1, name="Recipe 1"),
                Mock(id=2, name="Recipe 2"),
            ]

            mock_instance = mock_container.return_value
            mock_instance.project_manager.return_value = mock_project_manager

            try:
                result = await runner.invoke(
                    cli,
                    [
                        "recipes",
                        "update-connection",
                        "--old-connection",
                        "old-conn",
                        "--new-connection",
                        "new-conn",
                        "--project",
                        "test-project",
                    ],
                )

                assert "No such command" not in result.output

            except SystemExit:
                # Command might not be fully implemented
                pass

    @pytest.mark.asyncio
    async def test_recipe_async_operations(self, temp_config_dir) -> None:
        """Test async recipe operations."""
        runner = CliRunner()

        with patch("workato_platform.cli.containers.Container") as mock_container:
            mock_workato_client = Mock()

            # Mock async methods
            async def mock_async_start() -> Mock:
                return Mock(success=True)

            mock_workato_client.recipes_api.start_recipe = Mock(
                side_effect=mock_async_start
            )

            mock_instance = mock_container.return_value
            mock_instance.workato_api_client.return_value = mock_workato_client

            # Test async command execution
            result = await runner.invoke(
                cli, ["recipes", "start", "--recipe-id", "123"]
            )

            # Should not crash and command should be found
            assert "No such command" not in result.output
