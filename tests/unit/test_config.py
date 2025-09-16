"""Tests for configuration management."""

from unittest.mock import patch

from workato_platform.cli.utils.config import (
    ConfigManager,
    CredentialsConfig,
    ProfileManager,
)


class TestConfigManager:
    """Test the ConfigManager class."""

    def test_init_with_profile(self, temp_config_dir):
        """Test ConfigManager initialization with config_dir."""
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        assert config_manager.config_dir == temp_config_dir

    def test_validate_region_valid(self, temp_config_dir):
        """Test region validation with valid region."""
        config_manager = ConfigManager(config_dir=temp_config_dir)

        # Should not raise exception
        assert config_manager.validate_region("us")
        assert config_manager.validate_region("eu")

    def test_validate_region_invalid(self, temp_config_dir):
        """Test region validation with invalid region."""
        config_manager = ConfigManager(config_dir=temp_config_dir)

        # Should return False for invalid region
        assert not config_manager.validate_region("invalid")

    def test_get_api_host_us(self, temp_config_dir):
        """Test API host for US region."""
        # Create a config manager instance
        config_manager = ConfigManager(config_dir=temp_config_dir, skip_validation=True)

        # Mock the profile manager's resolve_environment_variables method
        with patch.object(
            config_manager.profile_manager, "resolve_environment_variables"
        ) as mock_resolve:
            mock_resolve.return_value = ("token", "https://app.workato.com")

            assert config_manager.api_host == "https://app.workato.com"

    def test_get_api_host_eu(self, temp_config_dir):
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

    def test_init(self, temp_config_dir):
        """Test ProfileManager initialization."""
        profile_manager = ProfileManager()

        # ProfileManager uses global config dir, not temp_config_dir
        assert profile_manager.global_config_dir.name == ".workato"
        assert profile_manager.credentials_file.name == "credentials"

    def test_load_credentials_no_file(self, temp_config_dir):
        """Test loading credentials when file doesn't exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()
            credentials = profile_manager.load_credentials()

            assert isinstance(credentials, CredentialsConfig)
            assert credentials.profiles == {}

    def test_save_and_load_credentials(self, temp_config_dir):
        """Test saving and loading credentials."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Create test credentials
            profile_data = ProfileData(
                api_token="test-token",
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

    def test_set_profile(self, temp_config_dir):
        """Test setting a new profile."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            profile_data = ProfileData(
                api_token="test-token",
                region="eu",
                region_url="https://app.eu.workato.com",
                workspace_id=456,
            )

            profile_manager.set_profile("new-profile", profile_data)

            credentials = profile_manager.load_credentials()
            assert "new-profile" in credentials.profiles
            profile = credentials.profiles["new-profile"]
            assert profile.api_token == "test-token"
            assert profile.region == "eu"

    def test_delete_profile(self, temp_config_dir):
        """Test deleting a profile."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Create a profile first
            profile_data = ProfileData(
                api_token="token",
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

    def test_delete_nonexistent_profile(self, temp_config_dir):
        """Test deleting a profile that doesn't exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # delete_profile returns False for non-existent profiles
            result = profile_manager.delete_profile("nonexistent")
            assert result is False

    def test_list_profiles(self, temp_config_dir):
        """Test listing all profiles."""
        from workato_platform.cli.utils.config import ProfileData

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_config_dir
            profile_manager = ProfileManager()

            # Create multiple profiles
            profile_data1 = ProfileData(
                api_token="token1",
                region="us",
                region_url="https://app.workato.com",
                workspace_id=123,
            )
            profile_data2 = ProfileData(
                api_token="token2",
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
