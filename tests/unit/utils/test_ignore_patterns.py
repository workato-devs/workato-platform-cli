"""Tests for ignore_patterns utility functions."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from workato_platform.cli.utils.ignore_patterns import load_ignore_patterns, should_skip_file


class TestLoadIgnorePatterns:
    """Test load_ignore_patterns function."""

    def test_load_ignore_patterns_no_file(self, tmp_path: Path) -> None:
        """Test load_ignore_patterns when .workato-ignore doesn't exist."""
        result = load_ignore_patterns(tmp_path)
        assert result == {".workatoenv"}

    def test_load_ignore_patterns_with_file(self, tmp_path: Path) -> None:
        """Test load_ignore_patterns with existing .workato-ignore file."""
        ignore_file = tmp_path / ".workato-ignore"
        ignore_file.write_text("""# Comment line
*.py
node_modules/
# Another comment
.venv

""")

        result = load_ignore_patterns(tmp_path)
        expected = {".workatoenv", "*.py", "node_modules/", ".venv"}
        assert result == expected

    def test_load_ignore_patterns_empty_file(self, tmp_path: Path) -> None:
        """Test load_ignore_patterns with empty .workato-ignore file."""
        ignore_file = tmp_path / ".workato-ignore"
        ignore_file.write_text("")

        result = load_ignore_patterns(tmp_path)
        assert result == {".workatoenv"}

    def test_load_ignore_patterns_only_comments(self, tmp_path: Path) -> None:
        """Test load_ignore_patterns with file containing only comments."""
        ignore_file = tmp_path / ".workato-ignore"
        ignore_file.write_text("""# Comment 1
# Comment 2
# Another comment
""")

        result = load_ignore_patterns(tmp_path)
        assert result == {".workatoenv"}

    def test_load_ignore_patterns_whitespace_handling(self, tmp_path: Path) -> None:
        """Test load_ignore_patterns handles whitespace correctly."""
        ignore_file = tmp_path / ".workato-ignore"
        ignore_file.write_text("""  *.py
node_modules/
  # Comment with spaces
   .venv
""")

        result = load_ignore_patterns(tmp_path)
        expected = {".workatoenv", "*.py", "node_modules/", ".venv"}
        assert result == expected

    def test_load_ignore_patterns_handles_os_error(self, tmp_path: Path) -> None:
        """Test load_ignore_patterns handles OS errors gracefully."""
        ignore_file = tmp_path / ".workato-ignore"
        ignore_file.write_text("*.py")

        # Mock open to raise OSError
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            result = load_ignore_patterns(tmp_path)
            assert result == {".workatoenv"}

    def test_load_ignore_patterns_handles_unicode_error(self, tmp_path: Path) -> None:
        """Test load_ignore_patterns handles Unicode decode errors gracefully."""
        ignore_file = tmp_path / ".workato-ignore"
        ignore_file.write_text("*.py")

        # Mock open to raise UnicodeDecodeError
        with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")):
            result = load_ignore_patterns(tmp_path)
            assert result == {".workatoenv"}


class TestShouldSkipFile:
    """Test should_skip_file function."""

    def test_should_skip_file_exact_match(self) -> None:
        """Test should_skip_file with exact filename match."""
        file_path = Path("README.md")
        patterns = {"README.md", "*.py"}

        assert should_skip_file(file_path, patterns) is True

    def test_should_skip_file_glob_pattern(self) -> None:
        """Test should_skip_file with glob pattern match."""
        file_path = Path("src/main.py")
        patterns = {"*.py", "node_modules/"}

        assert should_skip_file(file_path, patterns) is True

    def test_should_skip_file_filename_pattern(self) -> None:
        """Test should_skip_file with filename glob pattern."""
        file_path = Path("deep/nested/test.py")
        patterns = {"*.py"}

        assert should_skip_file(file_path, patterns) is True

    def test_should_skip_file_directory_prefix(self) -> None:
        """Test should_skip_file with directory prefix match."""
        file_path = Path("node_modules/package/index.js")
        patterns = {"node_modules"}

        assert should_skip_file(file_path, patterns) is True

    def test_should_skip_file_windows_path_separator(self) -> None:
        """Test should_skip_file with Windows path separator."""
        file_path = Path("src\\main.py")
        patterns = {"src"}

        # Should match both forward and backslash separators
        assert should_skip_file(file_path, patterns) is True

    def test_should_skip_file_no_match(self) -> None:
        """Test should_skip_file when no patterns match."""
        file_path = Path("src/main.py")
        patterns = {"*.js", "node_modules/", "README.md"}

        assert should_skip_file(file_path, patterns) is False

    def test_should_skip_file_empty_patterns(self) -> None:
        """Test should_skip_file with empty pattern set."""
        file_path = Path("any/file.txt")
        patterns = set()

        assert should_skip_file(file_path, patterns) is False

    def test_should_skip_file_complex_glob_patterns(self) -> None:
        """Test should_skip_file with complex glob patterns."""
        patterns = {"**/*.pyc", "test_*.py", ".pytest_cache/*"}

        # Test various file paths
        assert should_skip_file(Path("deep/nested/file.pyc"), patterns) is True
        assert should_skip_file(Path("test_example.py"), patterns) is True
        assert should_skip_file(Path(".pytest_cache/file"), patterns) is True
        assert should_skip_file(Path("normal.py"), patterns) is False

    def test_should_skip_file_case_sensitive(self) -> None:
        """Test should_skip_file is case sensitive."""
        file_path = Path("README.MD")  # Different case
        patterns = {"README.md"}

        assert should_skip_file(file_path, patterns) is False

    def test_should_skip_file_multiple_pattern_types(self) -> None:
        """Test should_skip_file with multiple pattern matching approaches."""
        file_path = Path("src/test.py")
        patterns = {"*.py", "src/", "test.*"}

        # Should match on multiple criteria
        assert should_skip_file(file_path, patterns) is True

    def test_should_skip_file_nested_directory_patterns(self) -> None:
        """Test should_skip_file with directory patterns."""
        patterns = {".git", "__pycache__", ".git/*"}

        # Test direct matches
        assert should_skip_file(Path(".git/config"), patterns) is True
        assert should_skip_file(Path("__pycache__/file.pyc"), patterns) is True

        # Test glob patterns for nested paths
        assert should_skip_file(Path(".git/info/refs"), patterns) is True

        # Test non-matches
        assert should_skip_file(Path("src/normal.py"), patterns) is False
        assert should_skip_file(Path("deep/.git/info"), patterns) is False  # Doesn't match simple ".git" pattern