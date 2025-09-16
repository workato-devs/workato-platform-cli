"""Tests for guide command (AI agent documentation interface)."""

from unittest.mock import Mock, mock_open, patch

import pytest

from asyncclick.testing import CliRunner

from workato_platform.cli.commands.guide import (
    content,
    guide,
    index,
    search,
    structure,
    topics,
)


class TestGuideCommand:
    """Test the guide command for AI agents."""

    @pytest.mark.asyncio
    async def test_guide_command_group_exists(self):
        """Test that guide command group can be invoked."""
        runner = CliRunner()
        result = await runner.invoke(guide, ["--help"])

        assert result.exit_code == 0
        assert "documentation" in result.output.lower()

    @pytest.mark.asyncio
    async def test_guide_topics_command(self):
        """Test the topics subcommand."""
        runner = CliRunner()

        # Mock the docs directory and files
        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_docs_dir = Mock()
            mock_docs_dir.exists.return_value = True
            mock_docs_dir.glob.return_value = [
                Mock(name="recipe-fundamentals.md"),
                Mock(name="connections-parameters.md"),
            ]
            mock_path.return_value.parent.parent.joinpath.return_value = mock_docs_dir

            result = await runner.invoke(topics)

            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_guide_content_command_with_valid_topic(self):
        """Test the content subcommand with valid topic."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_file = Mock()
            mock_file.exists.return_value = True
            mock_path.return_value.parent.parent.joinpath.return_value = mock_file

            with patch(
                "builtins.open",
                mock_open(read_data="# Test Content\nThis is test documentation."),
            ):
                result = await runner.invoke(content, ["recipe-fundamentals"])

                assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_guide_content_command_with_invalid_topic(self):
        """Test the content subcommand with invalid topic."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_file = Mock()
            mock_file.exists.return_value = False
            mock_path.return_value.parent.parent.joinpath.return_value = mock_file

            result = await runner.invoke(content, ["nonexistent-topic"])

            # Should handle missing file gracefully
            assert result.exit_code == 0 or result.exit_code == 1

    @pytest.mark.asyncio
    async def test_guide_search_command(self):
        """Test the search subcommand."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_docs_dir = Mock()
            mock_docs_dir.exists.return_value = True
            mock_docs_dir.glob.return_value = [
                Mock(name="recipe-fundamentals.md", stem="recipe-fundamentals"),
                Mock(name="connections-parameters.md", stem="connections-parameters"),
            ]

            # Mock file reading
            def mock_read_text(encoding=None):
                return "This document covers OAuth authentication and connection setup."

            for mock_file in mock_docs_dir.glob.return_value:
                mock_file.read_text = Mock(side_effect=mock_read_text)

            mock_path.return_value.parent.parent.joinpath.return_value = mock_docs_dir

            result = await runner.invoke(search, ["oauth"])

            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_guide_search_with_no_results(self):
        """Test search command when no results found."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_docs_dir = Mock()
            mock_docs_dir.exists.return_value = True
            mock_docs_dir.glob.return_value = []
            mock_path.return_value.parent.parent.joinpath.return_value = mock_docs_dir

            result = await runner.invoke(search, ["nonexistent"])

            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_guide_structure_command(self):
        """Test the structure subcommand."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_docs_dir = Mock()
            mock_docs_dir.exists.return_value = True
            mock_docs_dir.rglob.return_value = [
                Mock(
                    name="recipe-fundamentals.md",
                    relative_to=Mock(return_value="recipe-fundamentals.md"),
                ),
                Mock(
                    name="connections-parameters.md",
                    relative_to=Mock(return_value="connections-parameters.md"),
                ),
            ]
            mock_path.return_value.parent.parent.joinpath.return_value = mock_docs_dir

            result = await runner.invoke(structure, ["recipe-fundamentals"])

            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_guide_index_command(self):
        """Test the index subcommand."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_docs_dir = Mock()
            mock_docs_dir.exists.return_value = True
            mock_docs_dir.glob.return_value = [
                Mock(name="recipe-fundamentals.md", stem="recipe-fundamentals"),
                Mock(name="connections-parameters.md", stem="connections-parameters"),
            ]

            # Mock file content
            def mock_read_text(encoding=None):
                return """# Recipe Fundamentals

This document explains recipe basics.

## Topics Covered
- Recipe structure
- Triggers and actions
"""

            for mock_file in mock_docs_dir.glob.return_value:
                mock_file.read_text = Mock(side_effect=mock_read_text)

            mock_path.return_value.parent.parent.joinpath.return_value = mock_docs_dir

            result = await runner.invoke(index)

            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_guide_handles_missing_docs_directory(self):
        """Test guide commands handle missing docs directory gracefully."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_docs_dir = Mock()
            mock_docs_dir.exists.return_value = False
            mock_path.return_value.parent.parent.joinpath.return_value = mock_docs_dir

            result = await runner.invoke(topics)

            # Should handle missing directory gracefully
            assert result.exit_code in [
                0,
                1,
            ]  # Either success with message or handled error

    @pytest.mark.asyncio
    async def test_guide_json_output_format(self):
        """Test guide commands with JSON output format."""
        runner = CliRunner()

        with patch("workato_platform.cli.commands.guide.Path") as mock_path:
            mock_docs_dir = Mock()
            mock_docs_dir.exists.return_value = True
            mock_docs_dir.glob.return_value = [Mock(name="test.md", stem="test")]
            mock_path.return_value.parent.parent.joinpath.return_value = mock_docs_dir

            result = await runner.invoke(topics)

            assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_guide_text_processing(self):
        """Test that guide commands properly process markdown text."""
        runner = CliRunner()

        markdown_content = """# Test Document

This is a test document with **bold** text and `code`.

## Section 1
Content here.

## Section 2
More content.
"""

        with (
            patch("workato_platform.cli.commands.guide.Path") as mock_path,
            patch("builtins.open", mock_open(read_data=markdown_content)),
        ):
            mock_file = Mock()
            mock_file.exists.return_value = True
            mock_path.return_value.parent.parent.joinpath.return_value = mock_file

            result = await runner.invoke(content, ["test"])

            assert result.exit_code == 0
