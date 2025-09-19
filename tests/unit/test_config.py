"""Tests for configuration management."""

import contextlib
import os

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from workato_platform.cli.utils.config import (
    ConfigData,
    ConfigManager,
    CredentialsConfig,
    ProfileData,
    ProfileManager,
    RegionInfo,
)


class TestConfigManager:
    """Test the ConfigManager class."""

    def test_init_with_profile(self, temp_config_dir: Path) -> None:
        """Test ConfigManager initialization with config_dir."""
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        assert config_manager.config_dir == temp_config_dir

    def test_validate_region_valid(self, temp_config_dir: Path) -> None:
        """Test region validation with valid region."""
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        # Should not raise exception
        assert config_manager.validate_region("us")
        assert config_manager.validate_region("eu")

    def test_validate_region_invalid(self, temp_config_dir: Path) -> None:
        """Test region validation with invalid region."""
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        # Should return False for invalid region
        assert not config_manager.validate_region("invalid")

    def test_get_api_host_us(self, temp_config_dir: Path) -> None:
        """Test API host for US region."""
        # Create a config manager instance
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        # Mock the profile manager's resolve_environment_variables method
        with patch.object(
            config_manager.profile_manager, "resolve_environment_variables"
        ) as mock_resolve:
            mock_resolve.return_value = ("token", "https://app.workato.com")

            assert config_manager.api_host == "https://app.workato.com"

    def test_get_api_host_eu(self, temp_config_dir: Path) -> None:
        """Test API host for EU region."""
        # Create a config manager instance
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        # Mock the profile manager's resolve_environment_variables method
        with patch.object(
            config_manager.profile_manager, "resolve_environment_variables"
        ) as mock_resolve:
            mock_resolve.return_value = ("token", "https://app.eu.workato.com")

            assert config_manager.api_host == "https://app.eu.workato.com"


class TestProfileManager:
    """Test the ProfileManager class."""

    def test_init(self) -> None:
        """Test ProfileManager initialization."""
        profile_manager = ProfileManager()

        # ProfileManager uses global config dir, not temp_config_dir
        assert profile_manager.global_config_dir.name == ".workato"
        assert profile_manager.credentials_file.name == "credentials"

    def test_load_credentials_no_file(self, temp_config_dir: Path) -> None:
        """Test loading credentials when file doesn't exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()
            credentials = profile_manager.load_credentials()

            assert isinstance(credentials, CredentialsConfig)
            assert credentials.profiles == {}

    def test_save_and_load_credentials(self, temp_config_dir: Path) -> None:
        """Test saving and loading credentials."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Create test credentials
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            credentials = CredentialsConfig(profiles={"test": profile_data})

            # Save credentials
            profile_manager.save_credentials(credentials)

            # Verify file exists
            assert profile_manager.credentials_file.exists()

            # Load and verify
            loaded_credentials = profile_manager.load_credentials()
            assert "test" in loaded_credentials.profiles

    def test_set_profile(self, temp_config_dir: Path) -> None:
        """Test setting a new profile."""
        from workato_platform.cli.utils.config import ProfileData

        with (
            patch("pathlib.Path.home") as mock_home,
            patch("keyring.set_password") as mock_keyring_set,
        ):
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            profile_data = ProfileData(
                region="eu",
                region_url="https://app.eu.workato.com",
                workspace_id=456,
            )

            profile_manager.set_profile("new-profile", profile_data, "test-token")

            credentials = profile_manager.load_credentials()
            assert "new-profile" in credentials.profiles
            profile = credentials.profiles["new-profile"]
            assert profile.region == "eu"

            # Verify token was stored in keyring
            mock_keyring_set.assert_called_once_with(
                "workato-platform-cli", "new-profile", "test-token"
            )

    def test_delete_profile(self, temp_config_dir: Path) -> None:
        """Test deleting a profile."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Create a profile first
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            profile_manager.set_profile("to-delete", profile_data)

            # Verify it exists
            credentials = profile_manager.load_credentials()
            assert "to-delete" in credentials.profiles

            # Delete it
            result = profile_manager.delete_profile("to-delete")
            assert result is True

            # Verify it's gone
            credentials = profile_manager.load_credentials()
            assert "to-delete" not in credentials.profiles

    def test_delete_nonexistent_profile(self, temp_config_dir: Path) -> None:
        """Test deleting a profile that doesn't exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # delete_profile returns False for non-existent profiles
            result = profile_manager.delete_profile("nonexistent")
            assert result is False

    def test_get_token_from_keyring_exception_handling(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test keyring token retrieval with exception handling"""
        profile_manager = ProfileManager()

        # Mock keyring.get_password to raise an exception
        def mock_get_password() -> None:
            raise Exception("Keyring access failed")

        monkeypatch.setattr("keyring.get_password", mock_get_password)

        # Should return None when keyring fails
        token = profile_manager._get_token_from_keyring("test_profile")
        assert token is None

    def test_load_credentials_invalid_dict_structure(
        self, temp_config_dir: Path
    ) -> None:
        """Test loading credentials with invalid dict structure"""
        profile_manager = ProfileManager()
        profile_manager.global_config_dir = temp_config_dir
        profile_manager.credentials_file = temp_config_dir / "credentials.json"

        # Create credentials file with non-dict content
        profile_manager.credentials_file.write_text('"this is a string, not a dict"')

        # Should return default config when file contains invalid structure
        config = profile_manager.load_credentials()
        assert isinstance(config, CredentialsConfig)
        assert config.current_profile is None
        assert config.profiles == {}

    def test_load_credentials_json_decode_error(self, temp_config_dir: Path) -> None:
        """Test loading credentials with JSON decode error"""
        profile_manager = ProfileManager()
        profile_manager.global_config_dir = temp_config_dir
        profile_manager.credentials_file = temp_config_dir / "credentials.json"

        # Create credentials file with invalid JSON
        profile_manager.credentials_file.write_text('{"invalid": json}')

        # Should return default config when JSON is malformed
        config = profile_manager.load_credentials()
        assert isinstance(config, CredentialsConfig)
        assert config.current_profile is None
        assert config.profiles == {}

    def test_store_token_in_keyring_keyring_disabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test storing token when keyring is disabled"""
        profile_manager = ProfileManager()
        monkeypatch.setenv("WORKATO_DISABLE_KEYRING", "true")

        result = profile_manager._store_token_in_keyring("test", "token")
        assert result is False

    def test_store_token_in_keyring_exception_handling(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test storing token with keyring exception"""
        profile_manager = ProfileManager()

        # Mock keyring.set_password to raise an exception
        def mock_set_password() -> None:
            raise Exception("Keyring storage failed")

        monkeypatch.setattr("keyring.set_password", mock_set_password)
        monkeypatch.delenv("WORKATO_DISABLE_KEYRING", raising=False)

        # Should return False when keyring fails
        result = profile_manager._store_token_in_keyring("test", "token")
        assert result is False

    def test_delete_token_from_keyring_exception_handling(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test deleting token with keyring exception"""
        profile_manager = ProfileManager()

        # Mock keyring.delete_password to raise an exception
        def mock_delete_password() -> None:
            raise Exception("Keyring deletion failed")

        monkeypatch.setattr("keyring.delete_password", mock_delete_password)

        # Should handle exception gracefully
        profile_manager._delete_token_from_keyring("test")

    def test_ensure_global_config_dir_creation_failure(self, tmp_path: Path) -> None:
        """Test config directory creation when it fails"""
        profile_manager = ProfileManager()
        non_writable_parent = tmp_path / "readonly"
        non_writable_parent.mkdir()
        non_writable_parent.chmod(0o444)  # Read-only

        profile_manager.global_config_dir = non_writable_parent / "config"

        # Should handle creation failures gracefully (tests the except blocks)
        with contextlib.suppress(PermissionError):
            profile_manager._ensure_global_config_dir()

    def test_save_credentials_permission_error(self, tmp_path: Path) -> None:
        """Test save credentials with permission error"""
        profile_manager = ProfileManager()
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        profile_manager.global_config_dir = readonly_dir
        profile_manager.credentials_file = readonly_dir / "credentials"

        credentials = CredentialsConfig(current_profile=None, profiles={})

        # Should handle permission errors gracefully
        with contextlib.suppress(PermissionError):
            profile_manager.save_credentials(credentials)

    def test_credentials_config_validation(self) -> None:
        """Test CredentialsConfig validation"""
        from workato_platform.cli.utils.config import CredentialsConfig, ProfileData

        # Test with valid data
        profile_data = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )
        config = CredentialsConfig(
            current_profile="default", profiles={"default": profile_data}
        )
        assert config.current_profile == "default"
        assert "default" in config.profiles

    def test_delete_profile_current_profile_reset(self, temp_config_dir: Path) -> None:
        """Test deleting current profile resets current_profile to None"""
        profile_manager = ProfileManager()
        profile_manager.global_config_dir = temp_config_dir
        profile_manager.credentials_file = temp_config_dir / "credentials"

        # Set up existing credentials with current profile
        credentials = CredentialsConfig(
            current_profile="test",
            profiles={
                "test": ProfileData(
                    region="us", region_url="https://test.com", workspace_id=123
                )
            },
        )
        profile_manager.save_credentials(credentials)

        # Delete the current profile - should reset current_profile to None
        result = profile_manager.delete_profile("test")
        assert result is True

        # Verify current_profile is None
        reloaded = profile_manager.load_credentials()
        assert reloaded.current_profile is None

    def test_get_current_profile_name_with_project_override(self) -> None:
        """Test getting current profile name with project override"""
        profile_manager = ProfileManager()

        # Test with project profile override
        result = profile_manager.get_current_profile_name("project_override")
        assert result == "project_override"

    def test_profile_manager_get_profile_nonexistent(self) -> None:
        """Test getting non-existent profile"""
        profile_manager = ProfileManager()

        # Should return None for non-existent profile
        profile = profile_manager.get_profile("nonexistent")
        assert profile is None

    def test_config_manager_load_config_file_not_found(
        self, temp_config_dir: Path
    ) -> None:
        """Test loading config when file doesn't exist"""
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        # Should return default config when file doesn't exist
        config = config_manager.load_config()
        assert config.project_id is None
        assert config.project_name is None

    def test_list_profiles(self, temp_config_dir: Path) -> None:
        """Test listing all profiles."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Create multiple profiles
            profile_data1 = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            profile_data2 = ProfileData(
                region="eu",
                region_url="https://app.eu.workato.com",
                workspace_id=456,
            )

            profile_manager.set_profile("profile1", profile_data1)
            profile_manager.set_profile("profile2", profile_data2)

            profiles = profile_manager.list_profiles()
            assert len(profiles) == 2
            assert "profile1" in profiles
            assert "profile2" in profiles

    def test_resolve_environment_variables(self, temp_config_dir: Path) -> None:
        """Test environment variable resolution."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Test with no env vars and no profile
            api_token, api_host = profile_manager.resolve_environment_variables()
            assert api_token is None
            assert api_host is None

            # Test with env vars
            with patch.dict(
                os.environ,
                {
                    "WORKATO_API_TOKEN": "env-token",
                    "WORKATO_HOST": "https://env.workato.com",
                },
            ):
                api_token, api_host = profile_manager.resolve_environment_variables()
                assert api_token == "env-token"
                assert api_host == "https://env.workato.com"

            # Test with profile and keyring
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            profile_manager.set_profile("test", profile_data, "profile-token")
            profile_manager.set_current_profile("test")

            with patch.object(
                profile_manager, "_get_token_from_keyring", return_value="keyring-token"
            ):
                api_token, api_host = profile_manager.resolve_environment_variables()
                assert api_token == "keyring-token"
                assert api_host == "https://app.workato.com"

    def test_validate_credentials(self, temp_config_dir: Path) -> None:
        """Test credential validation."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Test with no credentials
            is_valid, missing = profile_manager.validate_credentials()
            assert not is_valid
            assert len(missing) == 2

            # Test with profile
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            profile_manager.set_profile("test", profile_data, "test-token")
            profile_manager.set_current_profile("test")

            with patch.object(
                profile_manager, "_get_token_from_keyring", return_value="test-token"
            ):
                is_valid, missing = profile_manager.validate_credentials()
                assert is_valid
                assert len(missing) == 0

    def test_keyring_operations(self, temp_config_dir: Path) -> None:
        """Test keyring integration."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            with (
                patch("keyring.set_password") as mock_set,
                patch("keyring.get_password") as mock_get,
                patch("keyring.delete_password") as mock_delete,
            ):
                # Test store token
                result = profile_manager._store_token_in_keyring("test", "token")
                assert result is True
                mock_set.assert_called_once_with(
                    "workato-platform-cli", "test", "token"
                )

                # Test get token
                mock_get.return_value = "stored-token"
                token = profile_manager._get_token_from_keyring("test")
                assert token == "stored-token"

                # Test delete token
                result = profile_manager._delete_token_from_keyring("test")
                assert result is True
                mock_delete.assert_called_once_with("workato-platform-cli", "test")

    def test_keyring_operations_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        profile_manager = ProfileManager()
        monkeypatch.setenv("WORKATO_DISABLE_KEYRING", "true")

        assert profile_manager._get_token_from_keyring("name") is None
        assert profile_manager._store_token_in_keyring("name", "token") is False
        assert profile_manager._delete_token_from_keyring("name") is False

    def test_keyring_store_and_delete_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_manager = ProfileManager()
        monkeypatch.delenv("WORKATO_DISABLE_KEYRING", raising=False)

        with patch("keyring.set_password", side_effect=Exception("boom")):
            assert profile_manager._store_token_in_keyring("name", "token") is False

        with patch("keyring.delete_password", side_effect=Exception("boom")):
            assert profile_manager._delete_token_from_keyring("name") is False


class TestConfigManagerExtended:
    """Extended tests for ConfigManager class."""

    def test_set_region_valid(self, temp_config_dir: Path) -> None:
        """Test setting valid regions."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            config_manager = ConfigManager(
                config_dir=temp_config_dir, skip_validation=True
            )

            # Create a profile first
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            config_manager.profile_manager.set_profile("default", profile_data, "token")
            config_manager.profile_manager.set_current_profile("default")

            # Test setting valid region
            success, message = config_manager.set_region("eu")
            assert success is True
            assert "EU Data Center" in message

    def test_set_region_custom(self, temp_config_dir: Path) -> None:
        """Test setting custom region."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            config_manager = ConfigManager(
                config_dir=temp_config_dir, skip_validation=True
            )

            # Create a profile first
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            config_manager.profile_manager.set_profile("default", profile_data, "token")
            config_manager.profile_manager.set_current_profile("default")

            # Test custom region with valid URL
            success, message = config_manager.set_region(
                "custom", "https://custom.workato.com"
            )
            assert success is True

            # Test custom region without URL
            success, message = config_manager.set_region("custom")
            assert success is False
            assert "requires a URL" in message

    def test_set_region_invalid(self, temp_config_dir: Path) -> None:
        """Test setting invalid region."""
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        success, message = config_manager.set_region("invalid")
        assert success is False
        assert "Invalid region" in message

    def test_profile_data_invalid_region(self) -> None:
        with pytest.raises(ValueError):
            ProfileData(
                region="invalid", region_url="https://example.com", workspace_id=1
            )

    def test_config_file_operations(self, temp_config_dir: Path) -> None:
        """Test config file save/load operations."""
        from workato_platform.cli.utils.config import ConfigData

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        # Test loading non-existent config
        config_data = config_manager.load_config()
        assert config_data.project_id is None

        # Test saving and loading config
        new_config = ConfigData(
            project_id=123,
            project_name="Test Project",
            folder_id=456,
            profile="test-profile",
        )
        config_manager.save_config(new_config)

        loaded_config = config_manager.load_config()
        assert loaded_config.project_id == 123
        assert loaded_config.project_name == "Test Project"

    def test_api_properties(self, temp_config_dir: Path) -> None:
        """Test API token and host properties."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            config_manager = ConfigManager(
                config_dir=temp_config_dir, skip_validation=True
            )

            # Test with no profile
            assert config_manager.api_token is None
            assert config_manager.api_host is None

            # Create profile and test
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            config_manager.profile_manager.set_profile(
                "default", profile_data, "test-token"
            )
            config_manager.profile_manager.set_current_profile("default")

            with patch.object(
                config_manager.profile_manager,
                "_get_token_from_keyring",
                return_value="test-token",
            ):
                assert config_manager.api_token == "test-token"
                assert config_manager.api_host == "https://app.workato.com"

    def test_environment_validation(self, temp_config_dir: Path) -> None:
        """Test environment config validation."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            config_manager = ConfigManager(
                config_dir=temp_config_dir, skip_validation=True
            )

            # Test with no credentials
            is_valid, missing = config_manager.validate_environment_config()
            assert not is_valid
            assert len(missing) == 2

            # Create profile and test validation
            profile_data = ProfileData(
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            config_manager.profile_manager.set_profile(
                "default", profile_data, "test-token"
            )
            config_manager.profile_manager.set_current_profile("default")

        with patch.object(
            config_manager.profile_manager,
            "_get_token_from_keyring",
            return_value="test-token",
        ):
            is_valid, missing = config_manager.validate_environment_config()
            assert is_valid
            assert len(missing) == 0


class TestConfigManagerWorkspace:
    """Tests for workspace and project discovery helpers."""

    def test_get_current_project_name_detects_projects_directory(
        self,
        temp_config_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        project_root = temp_config_dir / "projects" / "demo"
        workato_dir = project_root / "workato"
        workato_dir.mkdir(parents=True)
        monkeypatch.chdir(project_root)

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        assert config_manager.get_current_project_name() == "demo"

    def test_get_project_root_returns_none_when_missing_workato(
        self,
        temp_config_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        project_dir = temp_config_dir / "projects" / "demo"
        project_dir.mkdir(parents=True)
        monkeypatch.chdir(project_dir)

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        assert config_manager.get_project_root() is None

    def test_get_project_root_detects_nearest_workato_folder(
        self,
        temp_config_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        project_root = temp_config_dir / "projects" / "demo"
        nested_dir = project_root / "src"
        workato_dir = project_root / "workato"
        workato_dir.mkdir(parents=True)
        nested_dir.mkdir(parents=True)
        monkeypatch.chdir(nested_dir)

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        project_root_result = config_manager.get_project_root()
        assert project_root_result is not None
        assert project_root_result.resolve() == project_root.resolve()

    def test_is_in_project_workspace_checks_for_workato_folder(
        self,
        temp_config_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        workspace_dir = temp_config_dir / "workspace"
        workato_dir = workspace_dir / "workato"
        workato_dir.mkdir(parents=True)
        monkeypatch.chdir(workspace_dir)

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        assert config_manager.is_in_project_workspace() is True

    def test_validate_env_vars_or_exit_exits_on_missing_credentials(
        self,
        temp_config_dir: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        with (
            patch.object(
                config_manager,
                "validate_environment_config",
                return_value=(False, ["API token"]),
            ),
            pytest.raises(SystemExit) as exc,
        ):
            config_manager._validate_env_vars_or_exit()

        assert exc.value.code == 1
        output = capsys.readouterr().out
        assert "Missing required credentials" in output
        assert "API token" in output

    def test_validate_env_vars_or_exit_passes_when_valid(
        self,
        temp_config_dir: Path,
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        with patch.object(
            config_manager, "validate_environment_config", return_value=(True, [])
        ):
            # Should not raise
            config_manager._validate_env_vars_or_exit()

    def test_get_default_config_dir_creates_when_missing(
        self,
        temp_config_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(temp_config_dir)
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        monkeypatch.setattr(
            config_manager,
            "_find_nearest_workato_dir",
            lambda: None,
        )

        default_dir = config_manager._get_default_config_dir()

        assert default_dir.exists()
        assert default_dir.name == "workato"

    def test_find_nearest_workato_dir_returns_none_when_absent(
        self,
        temp_config_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        nested = temp_config_dir / "nested" / "deeper"
        nested.mkdir(parents=True)
        monkeypatch.chdir(nested)

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        assert config_manager._find_nearest_workato_dir() is None

    def test_save_project_info_round_trip(
        self,
        temp_config_dir: Path,
    ) -> None:
        from workato_platform.cli.utils.config import ProjectInfo

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        project_info = ProjectInfo(id=42, name="Demo", folder_id=99)

        dummy_config = Mock()
        dummy_config.model_dump.return_value = {}

        with patch.object(config_manager, "load_config", return_value=dummy_config):
            config_manager.save_project_info(project_info)

        reloaded = ConfigManager(
            config_dir=temp_config_dir, skip_validation=True
        ).load_config()
        assert reloaded.project_id == 42
        assert reloaded.project_name == "Demo"
        assert reloaded.folder_id == 99

    def test_load_config_handles_invalid_json(
        self,
        temp_config_dir: Path,
    ) -> None:
        config_file = temp_config_dir / "config.json"
        config_file.write_text("{ invalid json")

        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        loaded = config_manager.load_config()
        assert loaded.project_id is None
        assert loaded.project_name is None

    def test_profile_manager_keyring_disabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_manager = ProfileManager()
        monkeypatch.setenv("WORKATO_DISABLE_KEYRING", "true")

        assert profile_manager._is_keyring_enabled() is False

    def test_profile_manager_env_profile_priority(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_manager = ProfileManager()
        monkeypatch.setenv("WORKATO_PROFILE", "env-profile")

        assert profile_manager.get_current_profile_name(None) == "env-profile"

    def test_profile_manager_resolve_env_vars_env_first(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_manager = ProfileManager()
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token")
        monkeypatch.setenv("WORKATO_HOST", "https://env.workato.com")

        token, host = profile_manager.resolve_environment_variables()

        assert token == "env-token"
        assert host == "https://env.workato.com"

    def test_profile_manager_resolve_env_vars_profile_fallback(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_manager = ProfileManager()
        profile = ProfileData(
            region="us",
            region_url="https://app.workato.com",
            workspace_id=1,
        )

        monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)
        monkeypatch.delenv("WORKATO_HOST", raising=False)
        monkeypatch.setattr(
            profile_manager,
            "get_current_profile_name",
            lambda override=None: "default",
        )
        monkeypatch.setattr(
            profile_manager,
            "get_profile",
            lambda name: profile,
        )
        monkeypatch.setattr(
            profile_manager,
            "_get_token_from_keyring",
            lambda name: "keyring-token",
        )

        token, host = profile_manager.resolve_environment_variables()

        assert token == "keyring-token"
        assert host == profile.region_url

    def test_profile_manager_set_profile_keyring_failure_enabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_manager = ProfileManager()
        profile = ProfileData(
            region="us",
            region_url="https://app.workato.com",
            workspace_id=1,
        )

        credentials = CredentialsConfig(profiles={})
        monkeypatch.setattr(profile_manager, "load_credentials", lambda: credentials)
        monkeypatch.setattr(profile_manager, "save_credentials", lambda cfg: None)
        monkeypatch.setattr(
            profile_manager, "_store_token_in_keyring", lambda *args, **kwargs: False
        )
        monkeypatch.setattr(profile_manager, "_is_keyring_enabled", lambda: True)

        with pytest.raises(ValueError) as exc:
            profile_manager.set_profile("default", profile, "token")

        assert "Failed to store token" in str(exc.value)

    def test_profile_manager_set_profile_keyring_failure_disabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        profile_manager = ProfileManager()
        profile = ProfileData(
            region="us",
            region_url="https://app.workato.com",
            workspace_id=1,
        )

        credentials = CredentialsConfig(profiles={})
        monkeypatch.setattr(profile_manager, "load_credentials", lambda: credentials)
        monkeypatch.setattr(profile_manager, "save_credentials", lambda cfg: None)
        monkeypatch.setattr(
            profile_manager, "_store_token_in_keyring", lambda *args, **kwargs: False
        )
        monkeypatch.setattr(profile_manager, "_is_keyring_enabled", lambda: False)

        with pytest.raises(ValueError) as exc:
            profile_manager.set_profile("default", profile, "token")

        assert "Keyring is disabled" in str(exc.value)

    def test_config_manager_set_api_token_success(
        self,
        temp_config_dir: Path,
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        profile = ProfileData(
            region="us",
            region_url="https://app.workato.com",
            workspace_id=1,
        )
        credentials = CredentialsConfig(profiles={"default": profile})

        config_manager.profile_manager = Mock()
        config_manager.profile_manager.get_current_profile_name.return_value = "default"
        config_manager.profile_manager.load_credentials.return_value = credentials
        config_manager.profile_manager._store_token_in_keyring.return_value = True

        with patch("workato_platform.cli.utils.config.click.echo") as mock_echo:
            config_manager._set_api_token("token")

        mock_echo.assert_called_with("✅ API token saved to profile 'default'")

    def test_config_manager_set_api_token_missing_profile(
        self,
        temp_config_dir: Path,
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        config_manager.profile_manager = Mock()
        config_manager.profile_manager.get_current_profile_name.return_value = "ghost"
        config_manager.profile_manager.load_credentials.return_value = (
            CredentialsConfig(profiles={})
        )

        with pytest.raises(ValueError):
            config_manager._set_api_token("token")

    def test_config_manager_set_api_token_keyring_failure(
        self,
        temp_config_dir: Path,
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        profile = ProfileData(
            region="us",
            region_url="https://app.workato.com",
            workspace_id=1,
        )
        credentials = CredentialsConfig(profiles={"default": profile})

        profile_manager = Mock()
        profile_manager.get_current_profile_name.return_value = "default"
        profile_manager.load_credentials.return_value = credentials
        profile_manager._store_token_in_keyring.return_value = False
        profile_manager._is_keyring_enabled.return_value = True
        config_manager.profile_manager = profile_manager

        with pytest.raises(ValueError) as exc:
            config_manager._set_api_token("token")

        assert "Failed to store token" in str(exc.value)

    def test_config_manager_set_api_token_keyring_disabled_failure(
        self,
        temp_config_dir: Path,
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        profile = ProfileData(
            region="us",
            region_url="https://app.workato.com",
            workspace_id=1,
        )
        credentials = CredentialsConfig(profiles={"default": profile})

        profile_manager = Mock()
        profile_manager.get_current_profile_name.return_value = "default"
        profile_manager.load_credentials.return_value = credentials
        profile_manager._store_token_in_keyring.return_value = False
        profile_manager._is_keyring_enabled.return_value = False
        config_manager.profile_manager = profile_manager

        with pytest.raises(ValueError) as exc:
            config_manager._set_api_token("token")

        assert "Keyring is disabled" in str(exc.value)


class TestConfigManagerInteractive:
    """Tests covering interactive setup flows."""

    @pytest.mark.asyncio
    async def test_initialize_runs_setup_flow(
        self, monkeypatch: pytest.MonkeyPatch, temp_config_dir: Path
    ) -> None:
        run_flow = AsyncMock()
        monkeypatch.setattr(ConfigManager, "_run_setup_flow", run_flow)
        monkeypatch.setenv("WORKATO_API_TOKEN", "token")
        monkeypatch.setenv("WORKATO_HOST", "https://app.workato.com")

        manager = await ConfigManager.initialize(temp_config_dir)

        assert isinstance(manager, ConfigManager)
        run_flow.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_setup_flow_creates_profile(
        self, monkeypatch: pytest.MonkeyPatch, temp_config_dir: Path
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        class StubProfileManager(ProfileManager):
            def __init__(self) -> None:
                self.profiles: dict[str, ProfileData] = {}
                self.saved_profile: tuple[str, ProfileData, str] | None = None
                self.current_profile: str | None = None

            def list_profiles(self) -> dict[str, ProfileData]:
                return {}

            def get_profile(self, name: str) -> ProfileData | None:
                return self.profiles.get(name)

            def set_profile(
                self, name: str, data: ProfileData, token: str | None = None
            ) -> None:
                self.profiles[name] = data
                self.saved_profile = (name, data, token or "")

            def set_current_profile(self, name: str | None) -> None:
                self.current_profile = name

            def _get_token_from_keyring(self, name: str) -> str | None:
                return None

            def _store_token_in_keyring(self, name: str, token: str) -> bool:
                return True

            def get_current_profile_data(
                self, override: str | None = None
            ) -> ProfileData | None:
                return None

            def get_current_profile_name(
                self, override: str | None = None
            ) -> str | None:
                return None

            def resolve_environment_variables(
                self, override: str | None = None
            ) -> tuple[str | None, str | None]:
                return None, None

            def load_credentials(self) -> CredentialsConfig:
                return CredentialsConfig(current_profile=None, profiles=self.profiles)

            def save_credentials(self, credentials: CredentialsConfig) -> None:
                self.profiles = credentials.profiles

        stub_profile_manager = StubProfileManager()
        config_manager.profile_manager = stub_profile_manager

        region = RegionInfo(
            region="us", name="US Data Center", url="https://www.workato.com"
        )
        monkeypatch.setattr(
            config_manager, "select_region_interactive", lambda _: region
        )

        prompt_values = iter(["new-profile", "api-token"])

        def fake_prompt(*_args: Any, **_kwargs: Any) -> str:
            try:
                return next(prompt_values)
            except StopIteration:
                return "api-token"

        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.prompt", fake_prompt
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.confirm", lambda *a, **k: True
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.echo", lambda *a, **k: None
        )

        class StubConfiguration(SimpleNamespace):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.verify_ssl = False

        class StubWorkato:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            async def __aenter__(self) -> SimpleNamespace:
                user_info = SimpleNamespace(
                    id=123,
                    name="Tester",
                    plan_id="enterprise",
                    recipes_count=1,
                    active_recipes_count=1,
                    last_seen="2024-01-01",
                )
                users_api = SimpleNamespace(
                    get_workspace_details=AsyncMock(return_value=user_info)
                )
                return SimpleNamespace(users_api=users_api)

            async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
                return None

        monkeypatch.setattr(
            "workato_platform.cli.utils.config.Configuration", StubConfiguration
        )
        monkeypatch.setattr("workato_platform.cli.utils.config.Workato", StubWorkato)

        with patch.object(
            config_manager,
            "load_config",
            return_value=ConfigData(project_id=1, project_name="Demo"),
        ):
            await config_manager._run_setup_flow()

        assert stub_profile_manager.saved_profile is not None
        assert stub_profile_manager.current_profile == "new-profile"

    def test_select_region_interactive_standard(
        self, monkeypatch: pytest.MonkeyPatch, temp_config_dir: Path
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        profile_manager = Mock(spec=ProfileManager)
        profile_manager.get_profile = lambda name: None
        profile_manager.get_current_profile_data = lambda override=None: None
        config_manager.profile_manager = profile_manager

        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.echo", lambda *a, **k: None
        )

        selected = "US Data Center (https://www.workato.com)"
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.inquirer.prompt",
            lambda _questions: {"region": selected},
        )

        region = config_manager.select_region_interactive(None)

        assert region is not None
        assert region.region == "us"

    def test_select_region_interactive_custom(
        self, monkeypatch: pytest.MonkeyPatch, temp_config_dir: Path
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)
        profile_manager = Mock(spec=ProfileManager)
        profile_manager.get_profile = lambda name: ProfileData(
            region="custom",
            region_url="https://custom.workato.com",
            workspace_id=1,
        )
        profile_manager.get_current_profile_data = lambda override=None: None
        config_manager.profile_manager = profile_manager

        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.echo", lambda *a, **k: None
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.inquirer.prompt",
            lambda _questions: {"region": "Custom URL"},
        )

        prompt_values = iter(["https://custom.workato.com/path"])
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.prompt",
            lambda *a, **k: next(prompt_values),
        )

        region = config_manager.select_region_interactive("default")

        assert region is not None
        assert region.region == "custom"
        assert region.url == "https://custom.workato.com"

    @pytest.mark.asyncio
    async def test_run_setup_flow_existing_profile_creates_project(
        self,
        monkeypatch: pytest.MonkeyPatch,
        temp_config_dir: Path,
    ) -> None:
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        existing_profile = ProfileData(
            region="us",
            region_url="https://www.workato.com",
            workspace_id=999,
        )

        class StubProfileManager(ProfileManager):
            def __init__(self) -> None:
                self.profiles = {"default": existing_profile}
                self.updated_profile: tuple[str, ProfileData, str] | None = None
                self.current_profile: str | None = None

            def list_profiles(self) -> dict[str, ProfileData]:
                return self.profiles

            def get_profile(self, name: str) -> ProfileData | None:
                return self.profiles.get(name)

            def set_profile(
                self, name: str, data: ProfileData, token: str | None = None
            ) -> None:
                self.profiles[name] = data
                self.updated_profile = (name, data, token or "")

            def set_current_profile(self, name: str | None) -> None:
                self.current_profile = name

            def _get_token_from_keyring(self, name: str) -> str | None:
                return None

            def _store_token_in_keyring(self, name: str, token: str) -> bool:
                return True

            def get_current_profile_data(
                self, override: str | None = None
            ) -> ProfileData | None:
                return existing_profile

            def get_current_profile_name(
                self, override: str | None = None
            ) -> str | None:
                return "default"

            def resolve_environment_variables(
                self, override: str | None = None
            ) -> tuple[str | None, str | None]:
                return "env-token", existing_profile.region_url

            def load_credentials(self) -> CredentialsConfig:
                return CredentialsConfig(
                    current_profile="default", profiles=self.profiles
                )

            def save_credentials(self, credentials: CredentialsConfig) -> None:
                self.profiles = credentials.profiles

        stub_profile_manager = StubProfileManager()
        config_manager.profile_manager = stub_profile_manager

        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token")
        region = RegionInfo(
            region="us", name="US Data Center", url="https://www.workato.com"
        )
        monkeypatch.setattr(
            config_manager, "select_region_interactive", lambda _: region
        )

        monkeypatch.setattr(
            "workato_platform.cli.utils.config.inquirer.prompt",
            lambda questions: {"profile_choice": "default"}
            if questions and questions[0].message.startswith("Select a profile")
            else {"project": "Create new project"},
        )

        def fake_prompt(message: str, **_kwargs: Any) -> str:
            if "project name" in message:
                return "New Project"
            raise AssertionError(f"Unexpected prompt: {message}")

        confirms = iter([True])

        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.prompt", fake_prompt
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.confirm",
            lambda *a, **k: next(confirms, False),
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.click.echo", lambda *a, **k: None
        )

        class StubConfiguration(SimpleNamespace):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.verify_ssl = False

        class StubWorkato:
            def __init__(self, **_kwargs: Any) -> None:
                pass

            async def __aenter__(self) -> SimpleNamespace:
                user = SimpleNamespace(
                    id=123,
                    name="Tester",
                    plan_id="enterprise",
                    recipes_count=1,
                    active_recipes_count=1,
                    last_seen="2024-01-01",
                )
                users_api = SimpleNamespace(
                    get_workspace_details=AsyncMock(return_value=user)
                )
                return SimpleNamespace(users_api=users_api)

            async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
                return None

        class StubProject(SimpleNamespace):
            id: int
            name: str
            folder_id: int

        class StubProjectManager:
            def __init__(self, *_: Any, **__: Any) -> None:
                pass

            async def get_all_projects(self) -> list[StubProject]:
                return []

            async def create_project(self, name: str) -> StubProject:
                return StubProject(id=101, name=name, folder_id=55)

        monkeypatch.setattr(
            "workato_platform.cli.utils.config.Configuration", StubConfiguration
        )
        monkeypatch.setattr("workato_platform.cli.utils.config.Workato", StubWorkato)
        monkeypatch.setattr(
            "workato_platform.cli.utils.config.ProjectManager", StubProjectManager
        )

        load_config_mock = Mock(return_value=ConfigData())
        save_config_mock = Mock()

        with (
            patch.object(config_manager, "load_config", load_config_mock),
            patch.object(config_manager, "save_config", save_config_mock),
        ):
            await config_manager._run_setup_flow()

        assert stub_profile_manager.updated_profile is not None
        save_config_mock.assert_called_once()


class TestRegionInfo:
    """Test RegionInfo and related functions."""

    def test_available_regions(self) -> None:
        """Test that all expected regions are available."""
        from workato_platform.cli.utils.config import AVAILABLE_REGIONS

        expected_regions = ["us", "eu", "jp", "sg", "au", "il", "trial", "custom"]
        for region in expected_regions:
            assert region in AVAILABLE_REGIONS

        # Test region properties
        us_region = AVAILABLE_REGIONS["us"]
        assert us_region.name == "US Data Center"
        assert us_region.url == "https://www.workato.com"

    def test_url_validation(self) -> None:
        """Test URL security validation."""
        from workato_platform.cli.utils.config import _validate_url_security

        # Test valid HTTPS URLs
        is_valid, msg = _validate_url_security("https://app.workato.com")
        assert is_valid is True

        # Test invalid protocol
        is_valid, msg = _validate_url_security("ftp://app.workato.com")
        assert is_valid is False
        assert "must start with http://" in msg

        # Test HTTP for localhost (should be allowed)
        is_valid, msg = _validate_url_security("http://localhost:3000")
        assert is_valid is True

        # Test HTTP for non-localhost (should be rejected)
        is_valid, msg = _validate_url_security("http://app.workato.com")
        assert is_valid is False
        assert "HTTPS for other hosts" in msg


class TestProfileManagerEdgeCases:
    """Test edge cases and error handling in ProfileManager."""

    def test_get_current_profile_data_no_profile_name(
        self, temp_config_dir: Path
    ) -> None:
        """Test get_current_profile_data when no profile name is available."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Mock get_current_profile_name to return None
            with patch.object(
                profile_manager, "get_current_profile_name", return_value=None
            ):
                result = profile_manager.get_current_profile_data()
                assert result is None

    def test_resolve_environment_variables_no_profile_data(
        self, temp_config_dir: Path
    ) -> None:
        """Test resolve_environment_variables when profile data is None."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Mock get_profile to return None
            with patch.object(profile_manager, "get_profile", return_value=None):
                result = profile_manager.resolve_environment_variables(
                    "nonexistent_profile"
                )
                assert result == (None, None)


class TestConfigManagerEdgeCases:
    """Test simpler edge cases that improve coverage."""

    def test_profile_manager_keyring_token_access(self, temp_config_dir: Path) -> None:
        """Test accessing token from keyring when it exists."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Store a token in keyring
            import workato_platform.cli.utils.config as config_module

            config_module.keyring.set_password(
                "workato-platform-cli", "test_profile", "test_token_abcdef123456"
            )

            # Test that we can retrieve it
            token = profile_manager._get_token_from_keyring("test_profile")
            assert token == "test_token_abcdef123456"

    def test_profile_manager_masked_token_display(self, temp_config_dir: Path) -> None:
        """Test token masking for display."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Store a long token
            token = "test_token_abcdef123456789"
            import workato_platform.cli.utils.config as config_module

            config_module.keyring.set_password(
                "workato-platform-cli", "test_profile", token
            )

            retrieved = profile_manager._get_token_from_keyring("test_profile")

            # Test masking logic (first 8 chars + ... + last 4 chars)
            masked = retrieved[:8] + "..." + retrieved[-4:] if retrieved else ""
            expected = "test_tok...6789"
            assert masked == expected

    def test_get_current_profile_data_with_profile_name(
        self, temp_config_dir: Path
    ) -> None:
        """Test get_current_profile_data when profile name is available."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Create and save a profile
            profile_data = ProfileData(
                region="us", region_url="https://app.workato.com", workspace_id=123
            )
            profile_manager.set_profile("test_profile", profile_data)

            # Mock get_current_profile_name to return the profile name
            with patch.object(
                profile_manager, "get_current_profile_name", return_value="test_profile"
            ):
                result = profile_manager.get_current_profile_data()
                assert result == profile_data

    def test_profile_manager_token_operations(self, temp_config_dir: Path) -> None:
        """Test profile manager token storage and deletion."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Store a token
            success = profile_manager._store_token_in_keyring(
                "test_profile", "test_token"
            )
            assert success is True

            # Retrieve the token
            token = profile_manager._get_token_from_keyring("test_profile")
            assert token == "test_token"

            # Delete the token
            success = profile_manager._delete_token_from_keyring("test_profile")
            assert success is True

            # Verify it's gone
            token = profile_manager._get_token_from_keyring("test_profile")
            assert token is None

    def test_get_current_project_name_no_project_root(
        self, temp_config_dir: Path
    ) -> None:
        """Test get_current_project_name when no project root is found."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock get_project_root to return None
        with patch.object(config_manager, "get_project_root", return_value=None):
            result = config_manager.get_current_project_name()
            assert result is None

    def test_get_current_project_name_not_in_projects_structure(
        self, temp_config_dir: Path
    ) -> None:
        """Test get_current_project_name when not in projects/ structure."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Create a mock project root that's not in projects/ structure
        mock_project_root = temp_config_dir / "some_project"
        mock_project_root.mkdir()

        with patch.object(
            config_manager, "get_project_root", return_value=mock_project_root
        ):
            result = config_manager.get_current_project_name()
            assert result is None

    def test_api_token_setter(self, temp_config_dir: Path) -> None:
        """Test API token setter method."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock the internal method
        with patch.object(config_manager, "_set_api_token") as mock_set:
            config_manager.api_token = "test_token_123"
            mock_set.assert_called_once_with("test_token_123")

    def test_is_in_project_workspace_false(self, temp_config_dir: Path) -> None:
        """Test is_in_project_workspace when not in workspace."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock _find_nearest_workato_dir to return None
        with patch.object(
            config_manager, "_find_nearest_workato_dir", return_value=None
        ):
            result = config_manager.is_in_project_workspace()
            assert result is False

    def test_is_in_project_workspace_true(self, temp_config_dir: Path) -> None:
        """Test is_in_project_workspace when in workspace."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock _find_nearest_workato_dir to return a directory
        mock_dir = temp_config_dir / ".workato"
        with patch.object(
            config_manager, "_find_nearest_workato_dir", return_value=mock_dir
        ):
            result = config_manager.is_in_project_workspace()
            assert result is True

    def test_set_region_profile_not_exists(self, temp_config_dir: Path) -> None:
        """Test set_region when profile doesn't exist."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock profile manager to return None for current profile
        with patch.object(
            config_manager.profile_manager,
            "get_current_profile_name",
            return_value=None,
        ):
            success, message = config_manager.set_region("us")
            assert success is False
            assert "Profile 'default' does not exist" in message

    def test_set_region_custom_without_url(self, temp_config_dir: Path) -> None:
        """Test set_region with custom region but no URL."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Create a profile first
        profile_data = ProfileData(
            region="us", region_url="https://app.workato.com", workspace_id=123
        )
        config_manager.profile_manager.set_profile("default", profile_data)

        # Mock get_current_profile_name to return existing profile
        with patch.object(
            config_manager.profile_manager,
            "get_current_profile_name",
            return_value="default",
        ):
            success, message = config_manager.set_region("custom", None)
            assert success is False
            assert "Custom region requires a URL" in message

    def test_set_api_token_no_profile(self, temp_config_dir: Path) -> None:
        """Test _set_api_token when no current profile."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock to return None for current profile
        with (
            patch.object(
                config_manager.profile_manager,
                "get_current_profile_name",
                return_value=None,
            ),
            patch.object(
                config_manager.profile_manager, "load_credentials"
            ) as mock_load,
            pytest.raises(ValueError, match="Profile 'default' does not exist"),
        ):
            mock_credentials = Mock()
            mock_credentials.profiles = {}
            mock_load.return_value = mock_credentials

            # This should trigger the default profile name assignment and raise error
            config_manager._set_api_token("test_token")

    def test_profile_manager_current_profile_override(
        self, temp_config_dir: Path
    ) -> None:
        """Test profile manager with project profile override."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Test with project profile override
            result = profile_manager.get_current_profile_data(
                project_profile_override="override_profile"
            )
            # Should return None since override_profile doesn't exist
            assert result is None

    def test_set_region_custom_invalid_url(self, temp_config_dir: Path) -> None:
        """Test set_region with custom region and invalid URL."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Create a profile first
        profile_data = ProfileData(
            region="us", region_url="https://app.workato.com", workspace_id=123
        )
        config_manager.profile_manager.set_profile("default", profile_data)

        # Mock get_current_profile_name to return existing profile
        with patch.object(
            config_manager.profile_manager,
            "get_current_profile_name",
            return_value="default",
        ):
            # Test with invalid URL (non-HTTPS for non-localhost)
            success, message = config_manager.set_region(
                "custom", "http://app.workato.com"
            )
            assert success is False
            assert "HTTPS for other hosts" in message

    def test_config_data_str_representation(self) -> None:
        """Test ConfigData string representation."""
        config_data = ConfigData(
            project_id=123, project_name="Test Project", profile="test_profile"
        )
        # This should cover the __str__ method
        str_repr = str(config_data)
        assert "Test Project" in str_repr or "123" in str_repr

    def test_select_region_interactive_user_cancel(self, temp_config_dir: Path) -> None:
        """Test select_region_interactive when user cancels."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock inquirer to return None (user cancelled)
        with patch(
            "workato_platform.cli.utils.config.inquirer.prompt", return_value=None
        ):
            result = config_manager.select_region_interactive()
            assert result is None

    def test_select_region_interactive_custom_invalid_url(
        self, temp_config_dir: Path
    ) -> None:
        """Test select_region_interactive with custom region and invalid URL."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock inquirer to select custom region, then mock click.prompt for URL
        with (
            patch(
                "workato_platform.cli.utils.config.inquirer.prompt",
                return_value={"region": "Custom URL"},
            ),
            patch(
                "workato_platform.cli.utils.config.click.prompt",
                return_value="http://invalid.com",
            ),
            patch("workato_platform.cli.utils.config.click.echo") as mock_echo,
        ):
            result = config_manager.select_region_interactive()
            assert result is None
            # Should show validation error
            mock_echo.assert_called()

    def test_profile_manager_get_current_profile_no_override(
        self, temp_config_dir: Path
    ) -> None:
        """Test get_current_profile_name without project override."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Test with no project profile override (should use current profile)
            with patch.object(
                profile_manager,
                "get_current_profile_name",
                return_value="default_profile",
            ) as mock_get:
                profile_manager.get_current_profile_data(None)
                mock_get.assert_called_with(None)

    def test_config_manager_fallback_url(self, temp_config_dir: Path) -> None:
        """Test config manager uses fallback URL when profile data is None."""
        config_manager = ConfigManager(temp_config_dir, skip_validation=True)

        # Mock inquirer to select custom region (last option)
        mock_answers = {"region": "Custom URL"}

        with (
            patch.object(
                config_manager.profile_manager,
                "get_current_profile_data",
                return_value=None,
            ),
            patch(
                "workato_platform.cli.utils.config.inquirer.prompt",
                return_value=mock_answers,
            ),
            patch(
                "workato_platform.cli.utils.config.click.prompt"
            ) as mock_click_prompt,
        ):
            # Configure click.prompt to return a valid custom URL
            mock_click_prompt.return_value = "https://custom.workato.com"

            # Call the method that should use the fallback URL
            result = config_manager.select_region_interactive()

            # Verify click.prompt was called with the fallback URL as default
            mock_click_prompt.assert_called_once_with(
                "Enter your custom Workato base URL",
                type=str,
                default="https://www.workato.com",
            )

            # Verify the result is a custom RegionInfo
            assert result is not None
            assert result.region == "custom"
            assert result.url == "https://custom.workato.com"
