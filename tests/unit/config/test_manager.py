"""Tests for ConfigManager."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from workato_platform.cli.utils.config.manager import ConfigManager
from workato_platform.cli.utils.config.models import ConfigData, ProjectInfo


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_init_with_explicit_config_dir(self, tmp_path: Path) -> None:
        """Test ConfigManager respects explicit config_dir."""
        config_dir = tmp_path / "explicit"
        config_dir.mkdir()

        config_manager = ConfigManager(config_dir=config_dir, skip_validation=True)
        assert config_manager.config_dir == config_dir

    def test_init_without_config_dir_finds_nearest(self, tmp_path: Path, monkeypatch) -> None:
        """Test ConfigManager finds nearest .workatoenv when no config_dir provided."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".workatoenv").write_text('{"project_id": 123}')

        monkeypatch.chdir(project_dir)
        config_manager = ConfigManager(skip_validation=True)
        assert config_manager.config_dir == project_dir

    def test_load_config_success(self, tmp_path: Path) -> None:
        """Test loading valid config file."""
        config_file = tmp_path / ".workatoenv"
        config_data = {
            "project_id": 123,
            "project_name": "test",
            "folder_id": 456,
            "profile": "dev"
        }
        config_file.write_text(json.dumps(config_data))

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        loaded_config = config_manager.load_config()

        assert loaded_config.project_id == 123
        assert loaded_config.project_name == "test"
        assert loaded_config.folder_id == 456
        assert loaded_config.profile == "dev"

    def test_load_config_missing_file(self, tmp_path: Path) -> None:
        """Test loading config when file doesn't exist."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        loaded_config = config_manager.load_config()

        assert loaded_config.project_id is None
        assert loaded_config.project_name is None

    def test_load_config_invalid_json(self, tmp_path: Path) -> None:
        """Test loading config with invalid JSON."""
        config_file = tmp_path / ".workatoenv"
        config_file.write_text("invalid json")

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        loaded_config = config_manager.load_config()

        # Should return empty config
        assert loaded_config.project_id is None

    def test_save_config(self, tmp_path: Path) -> None:
        """Test saving config to file."""
        config_data = ConfigData(
            project_id=123,
            project_name="test",
            folder_id=456
        )

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        config_manager.save_config(config_data)

        config_file = tmp_path / ".workatoenv"
        assert config_file.exists()

        with open(config_file) as f:
            saved_data = json.load(f)

        assert saved_data["project_id"] == 123
        assert saved_data["project_name"] == "test"
        assert saved_data["folder_id"] == 456
        assert "project_path" not in saved_data  # None values excluded

    def test_save_project_info(self, tmp_path: Path) -> None:
        """Test saving project info updates config."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        project_info = ProjectInfo(id=123, name="test", folder_id=456)
        config_manager.save_project_info(project_info)

        loaded_config = config_manager.load_config()
        assert loaded_config.project_id == 123
        assert loaded_config.project_name == "test"
        assert loaded_config.folder_id == 456

    def test_get_workspace_root(self, tmp_path: Path) -> None:
        """Test get_workspace_root returns workspace root."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "project"
        project_dir.mkdir(parents=True)

        # Create workspace config
        (workspace_root / ".workatoenv").write_text('{"project_path": "project", "project_id": 123}')

        config_manager = ConfigManager(config_dir=project_dir, skip_validation=True)
        result = config_manager.get_workspace_root()
        assert result == workspace_root

    def test_get_project_directory_from_workspace_config(self, tmp_path: Path) -> None:
        """Test get_project_directory with workspace config."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "project"
        project_dir.mkdir(parents=True)

        # Create workspace config with project_path
        (workspace_root / ".workatoenv").write_text('{"project_path": "project", "project_id": 123}')

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        result = config_manager.get_project_directory()
        assert result == project_dir.resolve()

    def test_get_project_directory_from_project_config(self, tmp_path: Path) -> None:
        """Test get_project_directory when in project directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Create project config (no project_path)
        (project_dir / ".workatoenv").write_text('{"project_id": 123}')

        with patch.object(ConfigManager, '_update_workspace_selection'):
            config_manager = ConfigManager(config_dir=project_dir, skip_validation=True)
            result = config_manager.get_project_directory()
            assert result == project_dir

    def test_get_project_directory_none_when_no_project(self, tmp_path: Path) -> None:
        """Test get_project_directory returns None when no project configured."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        result = config_manager.get_project_directory()
        assert result is None

    def test_get_current_project_name(self, tmp_path: Path) -> None:
        """Test get_current_project_name returns project name."""
        config_data = ConfigData(project_name="test-project")

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        config_manager.save_config(config_data)

        result = config_manager.get_current_project_name()
        assert result == "test-project"

    def test_get_project_root_compatibility(self, tmp_path: Path) -> None:
        """Test get_project_root for backward compatibility."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".workatoenv").write_text('{"project_id": 123}')

        config_manager = ConfigManager(config_dir=project_dir, skip_validation=True)
        result = config_manager.get_project_root()
        assert result == project_dir

    def test_is_in_project_workspace(self, tmp_path: Path) -> None:
        """Test is_in_project_workspace detection."""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / ".workatoenv").write_text('{"project_path": "project", "project_id": 123}')

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        assert config_manager.is_in_project_workspace() is True

    def test_validate_environment_config(self, tmp_path: Path) -> None:
        """Test environment config validation."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock the profile manager after creation
        config_manager.profile_manager.validate_credentials = Mock(return_value=(True, []))

        is_valid, missing = config_manager.validate_environment_config()

        assert is_valid is True
        assert missing == []

    def test_api_token_property(self, tmp_path: Path) -> None:
        """Test api_token property."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock the profile manager after creation
        config_manager.profile_manager.resolve_environment_variables = Mock(return_value=("test-token", "https://test.com"))

        assert config_manager.api_token == "test-token"

    def test_api_host_property(self, tmp_path: Path) -> None:
        """Test api_host property."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock the profile manager after creation
        config_manager.profile_manager.resolve_environment_variables = Mock(return_value=("test-token", "https://test.com"))

        assert config_manager.api_host == "https://test.com"

    def test_validate_region_valid(self, tmp_path: Path) -> None:
        """Test validate_region with valid region."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        assert config_manager.validate_region("us") is True
        assert config_manager.validate_region("eu") is True
        assert config_manager.validate_region("custom") is True

    def test_validate_region_invalid(self, tmp_path: Path) -> None:
        """Test validate_region with invalid region."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        assert config_manager.validate_region("invalid") is False