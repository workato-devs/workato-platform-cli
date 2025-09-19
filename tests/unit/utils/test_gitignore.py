"""Tests for gitignore utilities."""

import tempfile
from pathlib import Path

from workato_platform.cli.utils.gitignore import (
    ensure_gitignore_entry,
    ensure_stubs_in_gitignore,
)


class TestGitignoreUtilities:
    """Test gitignore utility functions."""

    def test_ensure_gitignore_entry_new_file(self):
        """Test adding entry to non-existent .gitignore file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)
            entry = "projects/*/workato/"

            ensure_gitignore_entry(workspace_root, entry)

            gitignore_file = workspace_root / ".gitignore"
            assert gitignore_file.exists()

            content = gitignore_file.read_text()
            assert entry in content
            assert content.endswith("\n")

    def test_ensure_gitignore_entry_existing_file_without_entry(self):
        """Test adding entry to existing .gitignore file that doesn't have the entry."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)
            gitignore_file = workspace_root / ".gitignore"
            entry = "projects/*/workato/"

            # Create existing .gitignore with some content
            existing_content = "*.pyc\n__pycache__/\n"
            gitignore_file.write_text(existing_content)

            ensure_gitignore_entry(workspace_root, entry)

            content = gitignore_file.read_text()
            assert entry in content
            assert "*.pyc" in content
            assert "__pycache__/" in content
            assert content.endswith(f"{entry}\n")

    def test_ensure_gitignore_entry_existing_file_with_entry(self):
        """Test adding entry to existing .gitignore file that already has the entry."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)
            gitignore_file = workspace_root / ".gitignore"
            entry = "projects/*/workato/"

            # Create existing .gitignore with the entry already present
            existing_content = f"*.pyc\n{entry}\n__pycache__/\n"
            gitignore_file.write_text(existing_content)

            ensure_gitignore_entry(workspace_root, entry)

            content = gitignore_file.read_text()
            # Should not duplicate the entry
            assert content.count(entry) == 1
            assert content == existing_content

    def test_ensure_gitignore_entry_no_trailing_newline(self):
        """Test adding entry to existing .gitignore file without trailing newline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)
            gitignore_file = workspace_root / ".gitignore"
            entry = "projects/*/workato/"

            # Create existing .gitignore without trailing newline
            existing_content = "*.pyc"
            gitignore_file.write_text(existing_content)

            ensure_gitignore_entry(workspace_root, entry)

            content = gitignore_file.read_text()
            # Should add newline before the entry
            assert content == f"*.pyc\n{entry}\n"

    def test_ensure_gitignore_entry_empty_file(self):
        """Test adding entry to empty .gitignore file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)
            gitignore_file = workspace_root / ".gitignore"
            entry = "projects/*/workato/"

            # Create empty .gitignore
            gitignore_file.touch()

            ensure_gitignore_entry(workspace_root, entry)

            content = gitignore_file.read_text()
            assert content == f"{entry}\n"

    def test_ensure_stubs_in_gitignore(self):
        """Test the convenience function for adding stubs to gitignore."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)

            ensure_stubs_in_gitignore(workspace_root)

            gitignore_file = workspace_root / ".gitignore"
            assert gitignore_file.exists()

            content = gitignore_file.read_text()
            assert "projects/*/workato/" in content

    def test_ensure_stubs_in_gitignore_existing_file(self):
        """Test adding stubs to existing .gitignore file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)
            gitignore_file = workspace_root / ".gitignore"

            # Create existing .gitignore with some content
            existing_content = "*.log\n.env\n"
            gitignore_file.write_text(existing_content)

            ensure_stubs_in_gitignore(workspace_root)

            content = gitignore_file.read_text()
            assert "projects/*/workato/" in content
            assert "*.log" in content
            assert ".env" in content

    def test_multiple_entries(self):
        """Test adding multiple different entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)

            # Add multiple entries
            entries = [
                "*.pyc",
                "__pycache__/",
                "projects/*/workato/",
                ".env",
                "dist/",
            ]

            for entry in entries:
                ensure_gitignore_entry(workspace_root, entry)

            gitignore_file = workspace_root / ".gitignore"
            content = gitignore_file.read_text()

            for entry in entries:
                assert entry in content
                # Each entry should appear only once
                assert content.count(entry) == 1

    def test_edge_cases(self):
        """Test edge cases like special characters and long paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)

            # Test with special characters
            special_entry = "*.tmp~"
            ensure_gitignore_entry(workspace_root, special_entry)

            # Test with long path
            long_entry = "a" * 200 + "/"
            ensure_gitignore_entry(workspace_root, long_entry)

            gitignore_file = workspace_root / ".gitignore"
            content = gitignore_file.read_text()

            assert special_entry in content
            assert long_entry in content
