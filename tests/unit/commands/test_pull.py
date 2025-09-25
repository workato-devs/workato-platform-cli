"""Tests for the pull command."""

import shutil
import tempfile

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from workato_platform.cli.commands.projects.project_manager import ProjectManager
from workato_platform.cli.commands.pull import (
    _pull_project,
    calculate_diff_stats,
    calculate_json_diff_stats,
    count_lines,
    merge_directories,
    pull,
)
from workato_platform.cli.utils.config import ConfigData, ConfigManager


class TestPullCommand:
    """Test the pull command functionality."""

    # Note: gitignore tests removed - functionality moved to ConfigManager._create_workspace_files()

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

    def test_calculate_diff_stats_binary_file_shrinks(self) -> None:
        """Binary shrink should report removals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.bin"
            new_file = Path(tmpdir) / "new.bin"

            old_file.write_bytes(b"\xff" * 200)
            new_file.write_bytes(b"\xff" * 50)

            stats = calculate_diff_stats(old_file, new_file)
            assert stats["added"] == 0
            assert stats["removed"] > 0

    def test_calculate_diff_stats_delegates_to_json(self) -> None:
        """JSON inputs should use calculate_json_diff_stats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.json"
            new_file = Path(tmpdir) / "new.json"

            old_file.write_text('{"key": 1}', encoding="utf-8")
            new_file.write_text('{"key": 2}', encoding="utf-8")

            stats = calculate_diff_stats(old_file, new_file)
            assert "added" in stats and "removed" in stats

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

            old_file.write_text("invalid json {")
            new_file.write_text('{"key": "value"}')

            # Should fall back to regular diff
            stats = calculate_json_diff_stats(old_file, new_file)
            assert "added" in stats
            assert "removed" in stats

    def test_merge_directories(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test merge_directories reports changes and preserves workato files."""
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

        # .workatoenv contents must be preserved
        sensitive = local_dir / ".workatoenv"
        sensitive.write_text("keep", encoding="utf-8")

        # Create ignore patterns for test
        ignore_patterns = {".workatoenv"}

        # Avoid interactive confirmation during test
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.confirm",
            lambda *args, **kwargs: True,
        )

        changes = merge_directories(remote_dir, local_dir, ignore_patterns)

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

        # .workatoenv file should still exist and be untouched
        assert sensitive.exists()
        assert sensitive.read_text(encoding="utf-8") == "keep"

    def test_merge_directories_cancellation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """User cancellation should skip deletions and emit notice."""

        remote_dir = tmp_path / "remote"
        local_dir = tmp_path / "local"
        remote_dir.mkdir()
        local_dir.mkdir()

        (remote_dir / "keep.txt").write_text("data", encoding="utf-8")
        (local_dir / "keep.txt").write_text("stale", encoding="utf-8")
        (local_dir / "remove.txt").write_text("remove", encoding="utf-8")

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.confirm",
            lambda *args, **kwargs: False,
        )

        ignore_patterns = set()
        changes = merge_directories(remote_dir, local_dir, ignore_patterns)

        # No deletions should have been recorded or performed
        assert (local_dir / "remove.txt").exists()
        assert not changes["removed"]
        assert any("Pull cancelled" in msg for msg in captured)

    def test_merge_directories_many_deletions(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """More than ten deletions should show truncated list message."""

        remote_dir = tmp_path / "remote"
        local_dir = tmp_path / "local"
        remote_dir.mkdir()
        local_dir.mkdir()

        (remote_dir / "keep.txt").write_text("content", encoding="utf-8")
        (local_dir / "keep.txt").write_text("old", encoding="utf-8")

        for idx in range(12):
            (local_dir / f"extra_{idx}.txt").write_text("remove", encoding="utf-8")

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.confirm",
            lambda *args, **kwargs: True,
        )

        ignore_patterns = set()
        merge_directories(remote_dir, local_dir, ignore_patterns)

        assert any("... and 2 more" in msg for msg in captured)

    @pytest.mark.asyncio
    @patch("workato_platform.cli.commands.pull.click.echo")
    async def test_pull_project_no_api_token(self, mock_echo: MagicMock) -> None:
        """Test _pull_project with no API token."""
        mock_config_manager = MagicMock()
        mock_config_manager.api_token = None
        mock_project_manager = MagicMock()

        await _pull_project(mock_config_manager, mock_project_manager)

        mock_echo.assert_called_with(
            "❌ No API token found. Please run 'workato init' first."
        )

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

        mock_echo.assert_called_with(
            "❌ No project configured. Please run 'workato init' first."
        )

    @pytest.mark.asyncio
    async def test_pull_command_calls_pull_project(self) -> None:
        """Test pull command calls _pull_project."""
        mock_config_manager = MagicMock()
        mock_project_manager = MagicMock()

        with patch("workato_platform.cli.commands.pull._pull_project") as mock_pull:
            assert pull.callback
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

        config_manager = ConfigManager(skip_validation=True)

        with (
            patch.object(
                type(config_manager),
                "api_token",
                new_callable=PropertyMock,
                return_value="token",
            ),
            patch.object(
                config_manager, "load_config", return_value=ConfigData(folder_id=1)
            ),
            patch.object(
                config_manager, "get_current_project_name", return_value="demo"
            ),
            patch.object(config_manager, "get_project_directory", return_value=None),
        ):
            project_manager = AsyncMock()
            captured: list[str] = []
            monkeypatch.setattr(
                "workato_platform.cli.commands.pull.click.echo",
                lambda msg="": captured.append(msg),
            )

            await _pull_project(config_manager, project_manager)

            assert any("Could not determine project directory" in msg for msg in captured)
            project_manager.export_project.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_pull_project_merges_existing_project(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Existing project should merge remote changes and report summary."""

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "existing.txt").write_text("local\n", encoding="utf-8")

        config_manager = ConfigManager(skip_validation=True)

        async def fake_export(
            _folder_id: int, _project_name: str, target_dir: str
        ) -> bool:
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "existing.txt").write_text("remote\n", encoding="utf-8")
            (target / "new.txt").write_text("new\n", encoding="utf-8")
            return True

        project_manager = MagicMock(spec=ProjectManager)
        project_manager.export_project = AsyncMock(side_effect=fake_export)

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

        with (
            patch.object(
                type(config_manager),
                "api_token",
                new_callable=PropertyMock,
                return_value="token",
            ),
            patch.object(
                config_manager,
                "load_config",
                return_value=ConfigData(
                    project_id=1, project_name="Demo", folder_id=11
                ),
            ),
            patch.object(
                config_manager, "get_current_project_name", return_value="demo"
            ),
            patch.object(config_manager, "get_project_directory", return_value=project_dir),
        ):
            await _pull_project(config_manager, project_manager)

        assert any("Successfully pulled project changes" in msg for msg in captured)
        project_manager.export_project.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_pull_project_reports_simple_changes(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Ensure reporting handles change entries without diff stats."""

        project_dir = tmp_path / "project"
        project_dir.mkdir()

        config_manager = ConfigManager(skip_validation=True)

        async def fake_export(
            _folder_id: int, _project_name: str, target_dir: str
        ) -> bool:
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            return True

        project_manager = MagicMock(spec=ProjectManager)
        project_manager.export_project = AsyncMock(side_effect=fake_export)

        simple_changes = {
            "added": ["new.txt"],
            "modified": ["update.txt"],
            "removed": ["old.txt"],
        }

        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.merge_directories",
            lambda *args, **kwargs: simple_changes,
        )

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        with (
            patch.object(
                type(config_manager),
                "api_token",
                new_callable=PropertyMock,
                return_value="token",
            ),
            patch.object(
                config_manager,
                "load_config",
                return_value=ConfigData(project_id=1, project_name="Demo", folder_id=11),
            ),
            patch.object(config_manager, "get_project_directory", return_value=project_dir),
        ):
            await _pull_project(config_manager, project_manager)

        assert any("📄 new.txt" in msg for msg in captured)
        assert any("📝 update.txt" in msg for msg in captured)
        assert any("🗑️  old.txt" in msg for msg in captured)

    @pytest.mark.asyncio
    async def test_pull_project_creates_new_project_directory(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """When project directory is missing it should be created and populated."""

        project_dir = tmp_path / "missing_project"

        config_manager = ConfigManager(skip_validation=True)

        async def fake_export(
            _folder_id: int, _project_name: str, target_dir: str
        ) -> bool:
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "remote.txt").write_text("content", encoding="utf-8")
            return True

        project_manager = MagicMock(spec=ProjectManager)
        project_manager.export_project = AsyncMock(side_effect=fake_export)

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        with (
            patch.object(
                type(config_manager),
                "api_token",
                new_callable=PropertyMock,
                return_value="token",
            ),
            patch.object(
                config_manager,
                "load_config",
                return_value=ConfigData(project_id=1, project_name="Demo", folder_id=9),
            ),
            patch.object(
                config_manager, "get_current_project_name", return_value="demo"
            ),
            patch.object(config_manager, "get_project_directory", return_value=project_dir),
        ):
            await _pull_project(config_manager, project_manager)

        assert (project_dir / "remote.txt").exists()
        project_manager.export_project.assert_awaited_once()
        assert any(
            "Pulled latest changes" in msg or "Successfully pulled" in msg
            for msg in captured
        )

    @pytest.mark.asyncio
    async def test_pull_project_copies_when_local_missing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """If local project disappears before merge, copytree should run."""

        project_dir = tmp_path / "fresh_project"

        config_manager = ConfigManager(skip_validation=True)

        async def fake_export(
            _folder_id: int, _project_name: str, target_dir: str
        ) -> bool:
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "remote.txt").write_text("content", encoding="utf-8")

            if project_dir.exists():
                shutil.rmtree(project_dir)
            return True

        project_manager = MagicMock(spec=ProjectManager)
        project_manager.export_project = AsyncMock(side_effect=fake_export)

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        with (
            patch.object(
                type(config_manager),
                "api_token",
                new_callable=PropertyMock,
                return_value="token",
            ),
            patch.object(
                config_manager,
                "load_config",
                return_value=ConfigData(project_id=1, project_name="Demo", folder_id=9),
            ),
            patch.object(config_manager, "get_project_directory", return_value=project_dir),
        ):
            await _pull_project(config_manager, project_manager)

        assert (project_dir / "remote.txt").exists()
        assert any("Successfully pulled project to ./project" in msg for msg in captured)

    @pytest.mark.asyncio
    async def test_pull_project_failed_export(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Failed export should surface an error message and stop."""

        project_dir = tmp_path / "demo"

        config_manager = ConfigManager(skip_validation=True)

        project_manager = MagicMock(spec=ProjectManager)
        project_manager.export_project = AsyncMock(return_value=False)

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        with (
            patch.object(
                type(config_manager),
                "api_token",
                new_callable=PropertyMock,
                return_value="token",
            ),
            patch.object(
                config_manager,
                "load_config",
                return_value=ConfigData(project_id=1, project_name="Demo", folder_id=9),
            ),
            patch.object(config_manager, "get_project_directory", return_value=project_dir),
        ):
            await _pull_project(config_manager, project_manager)

        project_manager.export_project.assert_awaited_once()
        assert any("Failed to pull project" in msg for msg in captured)

    @pytest.mark.asyncio
    async def test_pull_project_up_to_date(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """When merge returns no changes, report project is up to date."""

        project_dir = tmp_path / "demo"
        project_dir.mkdir()

        config_manager = ConfigManager(skip_validation=True)

        async def fake_export(
            _folder_id: int, _project_name: str, target_dir: str
        ) -> bool:
            target = Path(target_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "existing.txt").write_text("remote\n", encoding="utf-8")
            return True

        project_manager = MagicMock(spec=ProjectManager)
        project_manager.export_project = AsyncMock(side_effect=fake_export)

        empty_changes = {"added": [], "modified": [], "removed": []}
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.merge_directories",
            lambda *args, **kwargs: empty_changes,
        )

        captured: list[str] = []
        monkeypatch.setattr(
            "workato_platform.cli.commands.pull.click.echo",
            lambda msg="": captured.append(msg),
        )

        with (
            patch.object(
                type(config_manager),
                "api_token",
                new_callable=PropertyMock,
                return_value="token",
            ),
            patch.object(
                config_manager,
                "load_config",
                return_value=ConfigData(project_id=1, project_name="Demo", folder_id=11),
            ),
            patch.object(config_manager, "get_project_directory", return_value=project_dir),
            patch.object(
                config_manager, "get_workspace_root", return_value=tmp_path
            ),
        ):
            await _pull_project(config_manager, project_manager)

        assert any("Project is already up to date" in msg for msg in captured)

    # Note: Legacy workspace structure test removed - behavior changed in simplified config
