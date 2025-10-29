"""Tests for WorkspaceManager."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from workato_platform_cli.cli.utils.config.workspace import WorkspaceManager


class TestWorkspaceManager:
    """Test WorkspaceManager functionality."""

    def test_find_nearest_workatoenv(self, tmp_path: Path) -> None:
        """Test finding nearest .workatoenv file."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "projects" / "test"
        project_dir.mkdir(parents=True)

        # Create .workatoenv in workspace root
        (workspace_root / ".workatoenv").write_text('{"project_path": "projects/test"}')

        manager = WorkspaceManager(project_dir)
        result = manager.find_nearest_workatoenv()
        assert result == workspace_root

    def test_find_nearest_workatoenv_none_when_missing(self, tmp_path: Path) -> None:
        """Test returns None when no .workatoenv found."""
        manager = WorkspaceManager(tmp_path)
        result = manager.find_nearest_workatoenv()
        assert result is None

    def test_find_workspace_root(self, tmp_path: Path) -> None:
        """Test finding workspace root with project_path."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "projects" / "test"
        project_dir.mkdir(parents=True)

        # Create workspace config
        (workspace_root / ".workatoenv").write_text(
            '{"project_path": "projects/test", "project_id": 123}',
        )

        manager = WorkspaceManager(project_dir)
        result = manager.find_workspace_root()
        assert result == workspace_root

    def test_find_workspace_root_fallback(self, tmp_path: Path) -> None:
        """Test workspace root falls back to start_path when not found."""
        manager = WorkspaceManager(tmp_path)
        result = manager.find_workspace_root()
        assert result == tmp_path

    def test_is_in_project_directory(self, tmp_path: Path) -> None:
        """Test detection of project directory."""
        # Create project config (no project_path)
        (tmp_path / ".workatoenv").write_text('{"project_id": 123}')

        manager = WorkspaceManager(tmp_path)
        assert manager.is_in_project_directory() is True

    def test_is_in_project_directory_false_for_workspace(self, tmp_path: Path) -> None:
        """Test workspace directory is not detected as project directory."""
        # Create workspace config (has project_path)
        (tmp_path / ".workatoenv").write_text(
            '{"project_path": "projects/test", "project_id": 123}'
        )

        manager = WorkspaceManager(tmp_path)
        assert manager.is_in_project_directory() is False

    def test_validate_project_path_success(self, tmp_path: Path) -> None:
        """Test valid project path validation."""
        workspace_root = tmp_path / "workspace"
        project_path = workspace_root / "project1"
        workspace_root.mkdir()

        manager = WorkspaceManager()
        # Should not raise exception
        manager.validate_project_path(project_path, workspace_root)

    def test_validate_project_path_blocks_workspace_root(self, tmp_path: Path) -> None:
        """Test project cannot be created in workspace root."""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()

        manager = WorkspaceManager()
        with pytest.raises(ValueError, match="cannot be created in workspace root"):
            manager.validate_project_path(workspace_root, workspace_root)

    def test_validate_project_path_blocks_outside_workspace(
        self, tmp_path: Path
    ) -> None:
        """Test project must be within workspace."""
        workspace_root = tmp_path / "workspace"
        outside_path = tmp_path / "outside"
        workspace_root.mkdir()

        manager = WorkspaceManager()
        with pytest.raises(ValueError, match="must be within workspace root"):
            manager.validate_project_path(outside_path, workspace_root)

    def test_validate_project_path_blocks_nested_projects(self, tmp_path: Path) -> None:
        """Test project cannot be created within another project."""
        workspace_root = tmp_path / "workspace"
        parent_project = workspace_root / "parent"
        nested_project = parent_project / "nested"

        workspace_root.mkdir()
        parent_project.mkdir(parents=True)

        # Create parent project config
        (parent_project / ".workatoenv").write_text('{"project_id": 123}')

        manager = WorkspaceManager()
        with pytest.raises(
            ValueError, match="Cannot create project within another project"
        ):
            manager.validate_project_path(nested_project, workspace_root)

    def test_validate_not_in_project_success(self, tmp_path: Path) -> None:
        """Test validate_not_in_project passes when not in project."""
        # No .workatoenv file
        manager = WorkspaceManager(tmp_path)
        # Should not raise exception
        manager.validate_not_in_project()

    def test_validate_not_in_project_exits_when_in_project(
        self, tmp_path: Path
    ) -> None:
        """Test validate_not_in_project exits when in project directory."""
        # Create project config
        (tmp_path / ".workatoenv").write_text('{"project_id": 123}')

        manager = WorkspaceManager(tmp_path)

        with pytest.raises(SystemExit):
            manager.validate_not_in_project()

    def test_validate_not_in_project_shows_workspace_root(self, tmp_path: Path) -> None:
        """Test validate_not_in_project shows workspace root when available."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "project"
        project_dir.mkdir(parents=True)

        # Create workspace and project configs
        (workspace_root / ".workatoenv").write_text(
            '{"project_path": "project", "project_id": 123}'
        )
        (project_dir / ".workatoenv").write_text('{"project_id": 123}')

        manager = WorkspaceManager(project_dir)

        with pytest.raises(SystemExit):
            manager.validate_not_in_project()

    def test_find_workspace_root_with_invalid_json(self, tmp_path: Path) -> None:
        """Test find_workspace_root handles invalid JSON gracefully."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "project"
        project_dir.mkdir(parents=True)

        # Create invalid JSON file
        (workspace_root / ".workatoenv").write_text("invalid json")

        manager = WorkspaceManager(project_dir)
        result = manager.find_workspace_root()
        # Should fall back to start_path
        assert result == project_dir

    def test_find_workspace_root_with_os_error(self, tmp_path: Path) -> None:
        """Test find_workspace_root handles OS errors gracefully."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "project"
        project_dir.mkdir(parents=True)

        # Create .workatoenv file
        workatoenv_file = workspace_root / ".workatoenv"
        workatoenv_file.write_text('{"project_path": "project"}')

        # Mock open to raise OSError
        def mock_open(*args: Any, **kwargs: Any) -> None:
            raise OSError("Permission denied")

        manager = WorkspaceManager(project_dir)

        with patch("builtins.open", side_effect=mock_open):
            result = manager.find_workspace_root()
            # Should fall back to start_path
            assert result == project_dir

    def test_is_in_project_directory_handles_json_error(self, tmp_path: Path) -> None:
        """Test is_in_project_directory handles JSON decode errors."""
        # Create invalid JSON
        (tmp_path / ".workatoenv").write_text("invalid json")

        manager = WorkspaceManager(tmp_path)
        assert manager.is_in_project_directory() is False

    def test_is_in_project_directory_handles_os_error(self, tmp_path: Path) -> None:
        """Test is_in_project_directory handles OS errors."""
        # Create .workatoenv file
        (tmp_path / ".workatoenv").write_text('{"project_id": 123}')

        manager = WorkspaceManager(tmp_path)

        # Mock open to raise OSError
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            assert manager.is_in_project_directory() is False

    def test_validate_project_path_handles_json_error_in_nested_check(
        self, tmp_path: Path
    ) -> None:
        """Test validate_project_path handles JSON errors in nested project check."""
        workspace_root = tmp_path / "workspace"
        parent_project = workspace_root / "parent"
        nested_project = parent_project / "nested"

        workspace_root.mkdir()
        parent_project.mkdir(parents=True)

        # Create invalid JSON in parent
        (parent_project / ".workatoenv").write_text("invalid json")

        manager = WorkspaceManager()
        # Should not raise exception (treats as non-project)
        manager.validate_project_path(nested_project, workspace_root)

    def test_validate_project_path_handles_os_error_in_nested_check(
        self, tmp_path: Path
    ) -> None:
        """Test validate_project_path handles OS errors in nested project check."""
        workspace_root = tmp_path / "workspace"
        parent_project = workspace_root / "parent"
        nested_project = parent_project / "nested"

        workspace_root.mkdir()
        parent_project.mkdir(parents=True)

        # Create .workatoenv file
        (parent_project / ".workatoenv").write_text('{"project_id": 123}')

        manager = WorkspaceManager()

        # Mock open to raise OSError during nested check
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            # Should not raise exception (treats as non-project)
            manager.validate_project_path(nested_project, workspace_root)
