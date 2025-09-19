"""Tests for the pull command."""

import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from workato_platform.cli.commands.pull import (
    _ensure_workato_in_gitignore,
    _pull_project,
    calculate_diff_stats,
    calculate_json_diff_stats,
    count_lines,
    merge_directories,
    pull,
)
from workato_platform.cli.utils.config import ConfigData


class TestPullCommand:
    """Test the pull command functionality."""

    def test_ensure_gitignore_creates_file(self) -> None:
        """Test _ensure_workato_in_gitignore creates .gitignore when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gitignore_file = project_root / ".gitignore"

            # File doesn't exist
            assert not gitignore_file.exists()

            _ensure_workato_in_gitignore(project_root)

            # File should now exist with .workato/ entry
            assert gitignore_file.exists()
            content = gitignore_file.read_text()
            assert ".workato/" in content

    def test_ensure_gitignore_adds_entry_to_existing_file(self) -> None:
        """Test _ensure_workato_in_gitignore adds entry to existing .gitignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gitignore_file = project_root / ".gitignore"

            # Create existing .gitignore without .workato/
            gitignore_file.write_text("node_modules/\n*.log\n")

            _ensure_workato_in_gitignore(project_root)

            content = gitignore_file.read_text()
            assert ".workato/" in content
            assert "node_modules/" in content  # Original content preserved

    def test_ensure_gitignore_adds_newline_to_non_empty_file(self) -> None:
        """Test _ensure_workato_in_gitignore adds newline when file doesn't end with one."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gitignore_file = project_root / ".gitignore"

            # Create existing .gitignore without newline at end
            gitignore_file.write_text("node_modules/")

            _ensure_workato_in_gitignore(project_root)

            content = gitignore_file.read_text()
            lines = content.split('\n')
            # Should have newline added before .workato/ entry
            assert lines[-2] == ".workato/"
            assert lines[-1] == ""  # Final newline

    def test_ensure_gitignore_skips_if_entry_exists(self) -> None:
        """Test _ensure_workato_in_gitignore skips adding entry if it already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gitignore_file = project_root / ".gitignore"

            # Create .gitignore with .workato/ already present
            original_content = "node_modules/\n.workato/\n*.log\n"
            gitignore_file.write_text(original_content)

            _ensure_workato_in_gitignore(project_root)

            # Content should be unchanged
            assert gitignore_file.read_text() == original_content

    def test_ensure_gitignore_handles_empty_file(self) -> None:
        """Test _ensure_workato_in_gitignore handles completely empty .gitignore file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            gitignore_file = project_root / ".gitignore"

            # Create empty .gitignore
            gitignore_file.write_text("")

            _ensure_workato_in_gitignore(project_root)

            content = gitignore_file.read_text()
            assert content == ".workato/\n"

    def test_count_lines_with_text_file(self) -> None:
        """Test count_lines with a regular text file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("line1\nline2\nline3\n")

            assert count_lines(test_file) == 3

    def test_count_lines_with_binary_file(self) -> None:
        """Test count_lines with a binary file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.bin"
            # Use bytes that trigger UnicodeDecodeError so the binary branch executes
            test_file.write_bytes(b"\xff\xfe\xfd\xfc")

            assert count_lines(test_file) == 0

    def test_count_lines_with_nonexistent_file(self) -> None:
        """Test count_lines with a nonexistent file."""
        nonexistent = Path("/nonexistent/file.txt")
        assert count_lines(nonexistent) == 0

    def test_calculate_diff_stats_text_files(self) -> None:
        """Test calculate_diff_stats with text files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.txt"
            new_file = Path(tmpdir) / "new.txt"

            old_file.write_text("line1\nline2\ncommon\n")
            new_file.write_text("line1\nline3\ncommon\nnew_line\n")

            stats = calculate_diff_stats(old_file, new_file)
            assert "added" in stats
            assert "removed" in stats
            assert stats["added"] > 0 or stats["removed"] > 0

    def test_calculate_diff_stats_binary_files(self) -> None:
        """Test calculate_diff_stats handles binary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.bin"
            new_file = Path(tmpdir) / "new.bin"

            old_file.write_bytes(b"\xff" * 100)
            new_file.write_bytes(b"\xff" * 200)

            stats = calculate_diff_stats(old_file, new_file)
            assert stats["added"] > 0
            assert stats["removed"] == 0

    def test_calculate_json_diff_stats(self) -> None:
        """Test calculate_json_diff_stats with JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.json"
            new_file = Path(tmpdir) / "new.json"

            old_file.write_text('{"key1": "value1", "common": "same"}')
            new_file.write_text('{"key2": "value2", "common": "same"}')

            stats = calculate_json_diff_stats(old_file, new_file)
            assert "added" in stats
            assert "removed" in stats

    def test_calculate_json_diff_stats_invalid_json(self) -> None:
        """Test calculate_json_diff_stats falls back for invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.txt"  # Use .txt to avoid recursion
            new_file = Path(tmpdir) / "new.txt"

            old_file.write_text('invalid json {')
            new_file.write_text('{"key": "value"}')

            # Should fall back to regular diff
            stats = calculate_json_diff_stats(old_file, new_file)
            assert "added" in stats
            assert "removed" in stats

    def test_merge_directories(self, tmp_path: Path) -> None:
        """Test merge_directories reports detailed changes and preserves workato files."""
        remote_dir = tmp_path / "remote"
        local_dir = tmp_path / "local"
        remote_dir.mkdir()
        local_dir.mkdir()

        # Remote has new file and modified file
        (remote_dir / "new.txt").write_text("new\n", encoding="utf-8")
        (remote_dir / "update.txt").write_text("remote\n", encoding="utf-8")

        # Local has old version and an extra file to be removed
        (local_dir / "update.txt").write_text("local\n", encoding="utf-8")
        (local_dir / "remove.txt").write_text("remove\n", encoding="utf-8")

        # .workato contents must be preserved
        workato_dir = local_dir / "workato"
        workato_dir.mkdir()
        sensitive = workato_dir / "config.json"
        sensitive.write_text("keep", encoding="utf-8")

        changes = merge_directories(remote_dir, local_dir)

        added_files = {name for name, _ in changes["added"]}
        modified_files = {name for name, _ in changes["modified"]}
        removed_files = {name for name, _ in changes["removed"]}

        assert "new.txt" in added_files
        assert "update.txt" in modified_files
        assert "remove.txt" in removed_files

        # Actual files on disk reflect merge
        assert (local_dir / "new.txt").exists()
        assert (local_dir / "update.txt").read_text(encoding="utf-8") == "remote\n"
        assert not (local_dir / "remove.txt").exists()

        # Workato file should still exist and be untouched
        assert sensitive.exists()

    @pytest.mark.asyncio
    @patch("workato_platform.cli.commands.pull.click.echo")
    async def test_pull_project_no_api_token(self, mock_echo: MagicMock) -> None:
        """Test _pull_project with no API token."""
        mock_config_manager = MagicMock()
        mock_config_manager.api_token = None
        mock_project_manager = MagicMock()

        await _pull_project(mock_config_manager, mock_project_manager)

        mock_echo.assert_called_with("❌ No API token found. Please run 'workato init' first.")

    @pytest.mark.asyncio
    @patch("workato_platform.cli.commands.pull.click.echo")
    async def test_pull_project_no_folder_id(self, mock_echo: MagicMock) -> None:
        """Test _pull_project with no folder ID."""
        mock_config_manager = MagicMock()
        mock_config_manager.api_token = "test-token"
        mock_config_data = MagicMock()
        mock_config_data.folder_id = None
        mock_config_manager.load_config.return_value = mock_config_data
        mock_project_manager = MagicMock()

        await _pull_project(mock_config_manager, mock_project_manager)

        mock_echo.assert_called_with("❌ No project configured. Please run 'workato init' first.")

    @pytest.mark.asyncio
    async def test_pull_command_calls_pull_project(self) -> None:
        """Test pull command calls _pull_project."""
        mock_config_manager = MagicMock()
        mock_project_manager = MagicMock()

        with patch("workato_platform.cli.commands.pull._pull_project") as mock_pull:
            await pull.callback(
                config_manager=mock_config_manager,
                project_manager=mock_project_manager,
            )

            mock_pull.assert_called_once_with(mock_config_manager, mock_project_manager)

    @pytest.mark.asyncio
    async def test_pull_project_missing_project_root(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test _pull_project when current project root cannot be determined."""

        class DummyConfig:
            @property
            def api_token(self) -> str | None:
                return "token"

            def load_config(self) -> ConfigData:
                return ConfigData(folder_id=1)

            def get_current_project_name(self) -> str:
                return "demo"

            def get_project_root(self) -> Path | None:
                return None

        project_manager = SimpleNamespace(export_project=AsyncMock())
        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        await _pull_project(DummyConfig(), project_manager)

        assert any("project root" in msg for msg in captured)
        project_manager.export_project.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_pull_project_merges_existing_project(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Existing project should merge remote changes and report summary."""

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "existing.txt").write_text("local\n", encoding="utf-8")

        class DummyConfig:
            @property
            def api_token(self) -> str | None:
                return "token"

            def load_config(self) -> ConfigData:
                return ConfigData(project_id=1, project_name="Demo", folder_id=11)

            def get_current_project_name(self) -> str:
                return "demo"

            def get_project_root(self) -> Path | None:
                return project_dir

        async def fake_export(folder_id, project_name, target_dir):
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "existing.txt").write_text("remote\n", encoding="utf-8")
            (target / "new.txt").write_text("new\n", encoding="utf-8")
            return True

        project_manager = SimpleNamespace(
            export_project=AsyncMock(side_effect=fake_export)
        )

        fake_changes = {
            "added": [("new.txt", {"lines": 1})],
            "modified": [("existing.txt", {"added": 1, "removed": 1})],
            "removed": [("old.txt", {"lines": 1})],
        }

        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.merge_directories",
            lambda *args, **kwargs: fake_changes,
        )

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        await _pull_project(DummyConfig(), project_manager)

        assert any("Successfully pulled project changes" in msg for msg in captured)
        project_manager.export_project.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_pull_project_creates_new_project_directory(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """When project directory is missing it should be created and populated."""

        project_dir = tmp_path / "missing_project"

        class DummyConfig:
            @property
            def api_token(self) -> str | None:
                return "token"

            def load_config(self) -> ConfigData:
                return ConfigData(project_id=1, project_name="Demo", folder_id=9)

            def get_current_project_name(self) -> str:
                return "demo"

            def get_project_root(self) -> Path | None:
                return project_dir

        async def fake_export(folder_id, project_name, target_dir):
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "remote.txt").write_text("content", encoding="utf-8")
            return True

        project_manager = SimpleNamespace(
            export_project=AsyncMock(side_effect=fake_export)
        )

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        await _pull_project(DummyConfig(), project_manager)

        assert (project_dir / "remote.txt").exists()
        project_manager.export_project.assert_awaited_once()
        assert any("Pulled latest changes" in msg or "Successfully pulled" in msg for msg in captured)

    @pytest.mark.asyncio
    async def test_pull_project_workspace_structure(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Pulling from workspace root should create project structure and save metadata."""

        workspace_root = tmp_path

        class DummyConfig:
            @property
            def api_token(self) -> str | None:
                return "token"

            def load_config(self) -> ConfigData:
                return ConfigData(project_id=1, project_name="Demo", folder_id=9)

            def get_current_project_name(self) -> str | None:
                return None

            def get_project_root(self) -> Path | None:
                return None

        async def fake_export(folder_id, project_name, target_dir):
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "remote.txt").write_text("content", encoding="utf-8")
            return True

        project_manager = SimpleNamespace(
            export_project=AsyncMock(side_effect=fake_export)
        )

        class StubConfig:
            def __init__(self, config_dir: Path):
                self.config_dir = Path(config_dir)
                self.saved: ConfigData | None = None

            def save_config(self, data: ConfigData) -> None:
                self.saved = data

        monkeypatch.chdir(workspace_root)
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.ConfigManager",
            StubConfig,
        )

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        await _pull_project(DummyConfig(), project_manager)

        project_config_dir = workspace_root / "projects" / "Demo" / "workato"
        assert project_config_dir.exists()
        assert (workspace_root / ".gitignore").read_text().count(".workato/") >= 1
        project_manager.export_project.assert_awaited_once()
