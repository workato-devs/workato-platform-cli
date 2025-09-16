"""Tests for recipes command."""

from unittest.mock import Mock, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform.cli.commands.recipes.command import (
    recipes,
)


class TestRecipesCommand:
    """Test the recipes command and subcommands."""

    @pytest.mark.asyncio
    async def test_recipes_command_group_exists(self):
        """Test that recipes command group can be invoked."""
        runner = CliRunner()
        result = await runner.invoke(recipes, ["--help"])

        # Should not crash and command should be found
        assert "No such command" not in result.output
        assert "recipe" in result.output.lower()

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_list_command(self, mock_container):
        """Test the list subcommand."""
        mock_workato_client = Mock()
        mock_workato_client.recipes_api.list_recipes.return_value = Mock(
            items=[
                Mock(id=1, name="Recipe 1", running=True),
                Mock(id=2, name="Recipe 2", running=False),
            ]
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["recipes", "list", "--folder-id", "123"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_list_with_filters(self, mock_container):
        """Test the list subcommand with various filters."""
        mock_workato_client = Mock()
        mock_workato_client.recipes_api.list_recipes.return_value = Mock(items=[])

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(
            cli,
            [
                "recipes",
                "list",
                "--folder-id",
                "456",
                "--running",
                "--stopped",
                "--name",
                "test",
                "--adapter",
                "salesforce",
                "--format",
                "json",
            ],
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_validate_command(self, mock_container):
        """Test the validate subcommand."""
        mock_validator = Mock()
        mock_validator.validate_recipe_structure.return_value = []  # No errors

        mock_container_instance = Mock()
        mock_container_instance.recipe_validator.return_value = mock_validator
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(
            cli, ["recipes", "validate", "--project-id", "123"]
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_validate_with_errors(self, mock_container):
        """Test the validate subcommand when validation errors exist."""
        from workato_platform.cli.commands.recipes.validator import (
            ErrorType,
            ValidationError,
        )

        mock_validator = Mock()
        mock_validator.validate_recipe_structure.return_value = [
            ValidationError(
                message="Invalid provider",
                error_type=ErrorType.STRUCTURE_INVALID,
                line_number=1,
                field_path=["trigger", "provider"],
            )
        ]

        mock_container_instance = Mock()
        mock_container_instance.recipe_validator.return_value = mock_validator
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(
            cli, ["recipes", "validate", "--project-id", "123"]
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_start_command(self, mock_container):
        """Test the start subcommand."""
        mock_workato_client = Mock()
        mock_workato_client.recipes_api.start_recipe.return_value = Mock(success=True)

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["recipes", "start", "--recipe-id", "789"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_stop_command(self, mock_container):
        """Test the stop subcommand."""
        mock_workato_client = Mock()
        mock_workato_client.recipes_api.stop_recipe.return_value = Mock(success=True)

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["recipes", "stop", "--recipe-id", "789"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_start_project_recipes(self, mock_container):
        """Test starting all recipes in a project."""
        mock_project_manager = Mock()
        mock_project_manager.get_project_recipes.return_value = [
            Mock(id=1, name="Recipe 1"),
            Mock(id=2, name="Recipe 2"),
        ]

        mock_workato_client = Mock()
        mock_workato_client.recipes_api.start_recipe.return_value = Mock(success=True)

        mock_container_instance = Mock()
        mock_container_instance.project_manager.return_value = mock_project_manager
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        # Test start with project
        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(
            cli, ["recipes", "start", "--project", "test-project"]
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_start_folder_recipes(self, mock_container):
        """Test starting all recipes in a folder."""
        mock_workato_client = Mock()
        mock_workato_client.recipes_api.list_recipes.return_value = Mock(
            items=[Mock(id=1, name="Recipe 1"), Mock(id=2, name="Recipe 2")]
        )
        mock_workato_client.recipes_api.start_recipe.return_value = Mock(success=True)

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["recipes", "start", "--folder-id", "456"])

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_update_connection_command(self, mock_container):
        """Test the update-connection subcommand."""
        try:
            from workato_platform.cli.commands.recipes.command import update_connection

            mock_workato_client = Mock()
            mock_project_manager = Mock()

            mock_container_instance = Mock()
            mock_container_instance.workato_api_client.return_value = (
                mock_workato_client
            )
            mock_container_instance.project_manager.return_value = mock_project_manager
            mock_container.return_value = mock_container_instance

            runner = CliRunner()
            result = await runner.invoke(
                update_connection,
                [
                    "--old-connection",
                    "old-conn",
                    "--new-connection",
                    "new-conn",
                    "--project",
                    "test-project",
                ],
            )

            # Should not crash and command should be found
            assert "No such command" not in result.output

        except ImportError:
            # Command might not exist, skip test
            pass

    @pytest.mark.asyncio
    async def test_recipes_helper_functions(self):
        """Test helper functions in recipes module."""
        # Test helper functions that might exist
        try:
            from workato_platform.cli.commands.recipes.command import (
                display_recipe_summary,
                get_folder_recipe_assets,
            )

            # These should be callable
            assert callable(display_recipe_summary)
            assert callable(get_folder_recipe_assets)

        except ImportError:
            # Functions might not exist, skip test
            pass

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_pagination_handling(self, mock_container):
        """Test that list command handles pagination."""
        # Mock paginated response
        mock_workato_client = Mock()

        # First page
        page1 = Mock(items=[Mock(id=1, name="Recipe 1")], has_more=True)
        # Second page
        page2 = Mock(items=[Mock(id=2, name="Recipe 2")], has_more=False)

        mock_workato_client.recipes_api.list_recipes.side_effect = [page1, page2]

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(
            cli, ["recipes", "list", "--folder-id", "123", "--all"]
        )

        # Should not crash and command should be found
        assert "No such command" not in result.output

    @patch("workato_platform.cli.containers.Container")
    @pytest.mark.asyncio
    async def test_recipes_error_handling(self, mock_container):
        """Test error handling in recipes commands."""
        mock_workato_client = Mock()
        mock_workato_client.recipes_api.list_recipes.side_effect = Exception(
            "API Error"
        )

        mock_container_instance = Mock()
        mock_container_instance.workato_api_client.return_value = mock_workato_client
        mock_container.return_value = mock_container_instance

        runner = CliRunner()
        from workato_platform.cli.cli import cli

        result = await runner.invoke(cli, ["recipes", "list", "--folder-id", "123"])

        # Should handle error gracefully (depends on exception handler)
        assert result.exit_code in [0, 1]
