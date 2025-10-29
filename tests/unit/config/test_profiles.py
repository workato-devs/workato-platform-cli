"""Tests for ProfileManager and related functionality."""

import json

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from keyring.errors import KeyringError, NoKeyringError

from workato_platform_cli.cli.utils.config.models import (
    ProfileData,
    ProfilesConfig,
)
from workato_platform_cli.cli.utils.config.profiles import (
    ProfileManager,
    _set_secure_permissions,
    _validate_url_security,
    _WorkatoFileKeyring,
)


class TestValidateUrlSecurity:
    """Test URL security validation."""

    def test_validate_url_security_https_valid(self) -> None:
        """Test HTTPS URLs are valid."""
        is_valid, error = _validate_url_security("https://www.workato.com")
        assert is_valid is True
        assert error == ""

    def test_validate_url_security_http_localhost_valid(self) -> None:
        """Test HTTP localhost URLs are valid."""
        # Test standard localhost addresses
        is_valid, error = _validate_url_security("http://localhost:3000")
        assert is_valid is True
        assert error == ""

        is_valid, error = _validate_url_security("http://127.0.0.1:3000")
        assert is_valid is True
        assert error == ""

    def test_validate_url_security_http_ipv6_localhost(self) -> None:
        """Test HTTP IPv6 localhost URLs."""
        # IPv6 localhost needs brackets in URL
        is_valid, error = _validate_url_security("http://[::1]:3000")
        assert is_valid is True
        assert error == ""

    def test_validate_url_security_http_external_invalid(self) -> None:
        """Test HTTP external URLs are invalid."""
        is_valid, error = _validate_url_security("http://example.com")
        assert is_valid is False
        assert "HTTPS" in error

    def test_validate_url_security_invalid_scheme(self) -> None:
        """Test invalid URL schemes."""
        is_valid, error = _validate_url_security("ftp://example.com")
        assert is_valid is False
        assert "http://" in error or "https://" in error

    def test_validate_url_security_no_scheme(self) -> None:
        """Test URLs without scheme."""
        is_valid, error = _validate_url_security("example.com")
        assert is_valid is False
        assert "http://" in error or "https://" in error


class TestSetSecurePermissions:
    """Test secure file permissions."""

    def test_set_secure_permissions_success(self, tmp_path: Path) -> None:
        """Test _set_secure_permissions sets permissions correctly."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        _set_secure_permissions(test_file)

        # Check that file still exists (permissions set successfully)
        assert test_file.exists()

    def test_set_secure_permissions_handles_os_error(self, tmp_path: Path) -> None:
        """Test _set_secure_permissions handles OS errors gracefully."""
        test_file = tmp_path / "nonexistent.txt"

        # Should not raise exception
        _set_secure_permissions(test_file)


class TestWorkatoFileKeyring:
    """Test _WorkatoFileKeyring fallback keyring."""

    def test_priority(self) -> None:
        """Test _WorkatoFileKeyring has low priority."""
        assert _WorkatoFileKeyring.priority == 0.1

    def test_init_creates_storage(self, tmp_path: Path) -> None:
        """Test initialization creates storage file."""
        storage_path = tmp_path / "keyring.json"
        _WorkatoFileKeyring(storage_path)

        assert storage_path.exists()
        assert json.loads(storage_path.read_text()) == {}

    def test_set_and_get_password(self, tmp_path: Path) -> None:
        """Test storing and retrieving passwords."""
        storage_path = tmp_path / "keyring.json"
        keyring = _WorkatoFileKeyring(storage_path)

        keyring.set_password("test-service", "user", "password123")

        result = keyring.get_password("test-service", "user")
        assert result == "password123"

    def test_get_password_nonexistent(self, tmp_path: Path) -> None:
        """Test getting non-existent password returns None."""
        storage_path = tmp_path / "keyring.json"
        keyring = _WorkatoFileKeyring(storage_path)

        result = keyring.get_password("nonexistent", "user")
        assert result is None

    def test_delete_password(self, tmp_path: Path) -> None:
        """Test deleting passwords."""
        storage_path = tmp_path / "keyring.json"
        keyring = _WorkatoFileKeyring(storage_path)

        # Set then delete
        keyring.set_password("test-service", "user", "password123")
        keyring.delete_password("test-service", "user")

        result = keyring.get_password("test-service", "user")
        assert result is None

    def test_delete_nonexistent_password(self, tmp_path: Path) -> None:
        """Test deleting non-existent password doesn't error."""
        storage_path = tmp_path / "keyring.json"
        keyring = _WorkatoFileKeyring(storage_path)

        # Should not raise exception
        keyring.delete_password("nonexistent", "user")

    def test_load_data_file_not_found(self, tmp_path: Path) -> None:
        """Test _load_data handles missing file."""
        storage_path = tmp_path / "nonexistent.json"
        keyring = _WorkatoFileKeyring.__new__(_WorkatoFileKeyring)
        keyring._storage_path = storage_path
        keyring._lock = keyring.__class__._lock = type(
            "Lock", (), {"__enter__": lambda s: None, "__exit__": lambda s, *a: None}
        )()

        result = keyring._load_data()
        assert result == {}

    def test_load_data_os_error(self, tmp_path: Path) -> None:
        """Test _load_data handles OS errors."""
        storage_path = tmp_path / "keyring.json"
        storage_path.write_text("{}")

        keyring = _WorkatoFileKeyring.__new__(_WorkatoFileKeyring)
        keyring._storage_path = storage_path
        keyring._lock = type(
            "Lock", (), {"__enter__": lambda s: None, "__exit__": lambda s, *a: None}
        )()

        # Mock read_text to raise OSError
        with patch.object(Path, "read_text", side_effect=OSError("Permission denied")):
            result = keyring._load_data()
            assert result == {}

    def test_load_data_empty_file(self, tmp_path: Path) -> None:
        """Test _load_data handles empty file."""
        storage_path = tmp_path / "keyring.json"
        storage_path.write_text("")

        keyring = _WorkatoFileKeyring.__new__(_WorkatoFileKeyring)
        keyring._storage_path = storage_path
        keyring._lock = type(
            "Lock", (), {"__enter__": lambda s: None, "__exit__": lambda s, *a: None}
        )()

        result = keyring._load_data()
        assert result == {}

    def test_load_data_invalid_json(self, tmp_path: Path) -> None:
        """Test _load_data handles invalid JSON."""
        storage_path = tmp_path / "keyring.json"
        storage_path.write_text("invalid json")

        keyring = _WorkatoFileKeyring.__new__(_WorkatoFileKeyring)
        keyring._storage_path = storage_path
        keyring._lock = type(
            "Lock", (), {"__enter__": lambda s: None, "__exit__": lambda s, *a: None}
        )()

        result = keyring._load_data()
        assert result == {}


class TestProfileManager:
    """Test ProfileManager functionality."""

    def test_init(self, tmp_path: Path) -> None:
        """Test ProfileManager initialization."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            assert manager.global_config_dir == tmp_path / ".workato"
            assert manager.profiles_file == tmp_path / ".workato" / "profiles"
            assert manager.keyring_service == "workato-platform-cli"

    def test_load_profiles_no_file(self, tmp_path: Path) -> None:
        """Test load_profiles when file doesn't exist."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            config = manager.load_profiles()

            assert config.current_profile is None
            assert config.profiles == {}

    def test_load_profiles_success(self, tmp_path: Path) -> None:
        """Test loading profiles successfully."""
        profiles_dir = tmp_path / ".workato"
        profiles_dir.mkdir()
        profiles_file = profiles_dir / "profiles"

        profile_data = {
            "current_profile": "dev",
            "profiles": {
                "dev": {
                    "region": "us",
                    "region_url": "https://www.workato.com",
                    "workspace_id": 123,
                }
            },
        }
        profiles_file.write_text(json.dumps(profile_data))

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            config = manager.load_profiles()

            assert config.current_profile == "dev"
            assert "dev" in config.profiles
            assert config.profiles["dev"].region == "us"

    def test_load_profiles_invalid_json(self, tmp_path: Path) -> None:
        """Test load_profiles handles invalid JSON."""
        profiles_dir = tmp_path / ".workato"
        profiles_dir.mkdir()
        profiles_file = profiles_dir / "profiles"
        profiles_file.write_text("invalid json")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            config = manager.load_profiles()

            # Should return empty config
            assert config.current_profile is None
            assert config.profiles == {}

    def test_load_profiles_invalid_data_structure(self, tmp_path: Path) -> None:
        """Test load_profiles handles invalid data structure."""
        profiles_dir = tmp_path / ".workato"
        profiles_dir.mkdir()
        profiles_file = profiles_dir / "profiles"
        profiles_file.write_text('"not a dict"')  # Valid JSON but wrong structure

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            config = manager.load_profiles()

            # Should return empty config
            assert config.current_profile is None
            assert config.profiles == {}

    def test_save_profiles(self, tmp_path: Path) -> None:
        """Test saving profiles configuration."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            profile = ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=123
            )
            config = ProfilesConfig(current_profile="dev", profiles={"dev": profile})

            manager.save_profiles(config)

            # Verify file was created
            profiles_file = tmp_path / ".workato" / "profiles"
            assert profiles_file.exists()

            # Verify content
            with open(profiles_file) as f:
                saved_data = json.load(f)

            assert saved_data["current_profile"] == "dev"
            assert "dev" in saved_data["profiles"]

    def test_get_profile_success(self, tmp_path: Path) -> None:
        """Test getting profile data."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )
        config = ProfilesConfig(profiles={"dev": profile})

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "load_profiles", return_value=config):
                result = manager.get_profile("dev")
                assert result == profile

    def test_get_profile_not_found(self, tmp_path: Path) -> None:
        """Test getting non-existent profile."""
        config = ProfilesConfig(profiles={})

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "load_profiles", return_value=config):
                result = manager.get_profile("nonexistent")
                assert result is None

    def test_set_profile_without_token(self, tmp_path: Path) -> None:
        """Test setting profile without token."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "save_profiles") as mock_save:
                manager.set_profile("dev", profile)
                mock_save.assert_called_once()

    def test_set_profile_with_token_success(self, tmp_path: Path) -> None:
        """Test setting profile with token stored successfully."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "save_profiles") as mock_save,
                patch.object(manager, "_store_token_in_keyring", return_value=True),
            ):
                manager.set_profile("dev", profile, "token123")
                mock_save.assert_called_once()

    def test_set_profile_with_token_keyring_failure(self, tmp_path: Path) -> None:
        """Test setting profile when keyring fails but keyring is enabled."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "save_profiles"),
                patch.object(manager, "_store_token_in_keyring", return_value=False),
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                pytest.raises(ValueError, match="Failed to store token in keyring"),
            ):
                manager.set_profile("dev", profile, "token123")

    def test_set_profile_with_token_keyring_disabled(self, tmp_path: Path) -> None:
        """Test setting profile when keyring is disabled."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "save_profiles"),
                patch.object(manager, "_store_token_in_keyring", return_value=False),
                patch.object(manager, "_is_keyring_enabled", return_value=False),
                pytest.raises(ValueError, match="Keyring is disabled"),
            ):
                manager.set_profile("dev", profile, "token123")

    def test_delete_profile_success(self, tmp_path: Path) -> None:
        """Test deleting existing profile."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )
        config = ProfilesConfig(
            current_profile="dev", profiles={"dev": profile, "prod": profile}
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "load_profiles", return_value=config),
                patch.object(manager, "save_profiles") as mock_save,
                patch.object(
                    manager, "_delete_token_from_keyring"
                ) as mock_delete_token,
            ):
                result = manager.delete_profile("dev")

                assert result is True
                mock_delete_token.assert_called_once_with("dev")
                # Should have saved config with dev removed and current_profile cleared
                saved_config = mock_save.call_args[0][0]
                assert "dev" not in saved_config.profiles
                assert saved_config.current_profile is None

    def test_delete_profile_not_found(self, tmp_path: Path) -> None:
        """Test deleting non-existent profile."""
        config = ProfilesConfig(profiles={})

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "load_profiles", return_value=config):
                result = manager.delete_profile("nonexistent")
                assert result is False

    def test_get_current_profile_name_project_override(self, tmp_path: Path) -> None:
        """Test get_current_profile_name with project override."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            result = manager.get_current_profile_name("project-profile")
            assert result == "project-profile"

    def test_get_current_profile_name_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_current_profile_name with environment variable."""
        monkeypatch.setenv("WORKATO_PROFILE", "env-profile")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            result = manager.get_current_profile_name()
            assert result == "env-profile"

    def test_get_current_profile_name_global_setting(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_current_profile_name with global setting."""
        monkeypatch.delenv("WORKATO_PROFILE", raising=False)
        config = ProfilesConfig(current_profile="global-profile")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "load_profiles", return_value=config):
                result = manager.get_current_profile_name()
                assert result == "global-profile"

    def test_set_current_profile(self, tmp_path: Path) -> None:
        """Test setting current profile."""
        config = ProfilesConfig(profiles={})

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "load_profiles", return_value=config),
                patch.object(manager, "save_profiles") as mock_save,
            ):
                manager.set_current_profile("new-profile")

                # Should save config with updated current_profile
                saved_config = mock_save.call_args[0][0]
                assert saved_config.current_profile == "new-profile"

    def test_get_current_profile_data(self, tmp_path: Path) -> None:
        """Test getting current profile data."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "get_current_profile_name", return_value="dev"),
                patch.object(manager, "get_profile", return_value=profile),
            ):
                result = manager.get_current_profile_data()
                assert result == profile

    def test_get_current_profile_data_no_profile(self, tmp_path: Path) -> None:
        """Test getting current profile data when no profile set."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "get_current_profile_name", return_value=None):
                result = manager.get_current_profile_data()
                assert result is None

    def test_list_profiles(self, tmp_path: Path) -> None:
        """Test listing all profiles."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )
        config = ProfilesConfig(profiles={"dev": profile, "prod": profile})

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "load_profiles", return_value=config):
                result = manager.list_profiles()
                assert "dev" in result
                assert "prod" in result
                assert len(result) == 2

    def test_resolve_environment_variables_env_override(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test resolve_environment_variables with env var override."""
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token")
        monkeypatch.setenv("WORKATO_HOST", "env-host")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            token, host = manager.resolve_environment_variables()
            assert token == "env-token"
            assert host == "env-host"

    def test_resolve_environment_variables_partial_env_override(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test resolve_environment_variables with partial env override."""
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token")
        monkeypatch.delenv("WORKATO_HOST", raising=False)

        profile = ProfileData(
            region="us", region_url="https://profile-host", workspace_id=123
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "get_current_profile_name", return_value="dev"),
                patch.object(manager, "get_profile", return_value=profile),
                patch.object(
                    manager, "_get_token_from_keyring", return_value="keyring-token"
                ),
            ):
                token, host = manager.resolve_environment_variables()
                assert token == "env-token"  # From env
                assert host == "https://profile-host"  # From profile

    def test_resolve_environment_variables_profile_fallback(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test resolve_environment_variables falls back to profile."""
        monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)
        monkeypatch.delenv("WORKATO_HOST", raising=False)

        profile = ProfileData(
            region="us", region_url="https://profile-host", workspace_id=123
        )

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "get_current_profile_name", return_value="dev"),
                patch.object(manager, "get_profile", return_value=profile),
                patch.object(
                    manager, "_get_token_from_keyring", return_value="keyring-token"
                ),
            ):
                token, host = manager.resolve_environment_variables()
                assert token == "keyring-token"
                assert host == "https://profile-host"

    def test_resolve_environment_variables_no_profile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test resolve_environment_variables when no profile configured."""
        monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)
        monkeypatch.delenv("WORKATO_HOST", raising=False)

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "get_current_profile_name", return_value=None):
                token, host = manager.resolve_environment_variables()
                assert token is None
                assert host is None

    def test_validate_credentials_success(self, tmp_path: Path) -> None:
        """Test validate_credentials with valid credentials."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(
                manager, "resolve_environment_variables", return_value=("token", "host")
            ):
                is_valid, missing = manager.validate_credentials()
                assert is_valid is True
                assert missing == []

    def test_validate_credentials_missing_token(self, tmp_path: Path) -> None:
        """Test validate_credentials with missing token."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(
                manager, "resolve_environment_variables", return_value=(None, "host")
            ):
                is_valid, missing = manager.validate_credentials()
                assert is_valid is False
                assert any("token" in item.lower() for item in missing)

    def test_validate_credentials_missing_host(self, tmp_path: Path) -> None:
        """Test validate_credentials with missing host."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(
                manager, "resolve_environment_variables", return_value=("token", None)
            ):
                is_valid, missing = manager.validate_credentials()
                assert is_valid is False
                assert any("host" in item.lower() for item in missing)

    def test_is_keyring_enabled_default(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test keyring is enabled by default."""
        monkeypatch.delenv("WORKATO_DISABLE_KEYRING", raising=False)

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            assert manager._is_keyring_enabled() is True

    def test_is_keyring_disabled_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test keyring can be disabled via environment variable."""
        monkeypatch.setenv("WORKATO_DISABLE_KEYRING", "true")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            assert manager._is_keyring_enabled() is False

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_password")
    def test_get_token_from_keyring_success(
        self, mock_get_password: Mock, tmp_path: Path
    ) -> None:
        """Test successful token retrieval from keyring."""
        mock_get_password.return_value = "test-token"

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=True):
                result = manager._get_token_from_keyring("dev")
                assert result == "test-token"

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_password")
    def test_get_token_from_keyring_disabled(
        self, mock_get_password: Mock, tmp_path: Path
    ) -> None:
        """Test token retrieval when keyring is disabled."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=False):
                result = manager._get_token_from_keyring("dev")
                assert result is None
                mock_get_password.assert_not_called()

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_password")
    def test_get_token_from_keyring_no_keyring_error(
        self, mock_get_password: Mock, tmp_path: Path
    ) -> None:
        """Test token retrieval handles NoKeyringError."""
        mock_get_password.side_effect = NoKeyringError("No keyring")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch.object(manager, "_ensure_keyring_backend") as mock_ensure,
            ):
                manager._get_token_from_keyring("dev")
                mock_ensure.assert_called_with(force_fallback=True)

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_password")
    def test_get_token_from_keyring_keyring_error(
        self, mock_get_password: Mock, tmp_path: Path
    ) -> None:
        """Test token retrieval handles KeyringError."""
        mock_get_password.side_effect = KeyringError("Keyring error")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch.object(manager, "_ensure_keyring_backend") as mock_ensure,
            ):
                manager._get_token_from_keyring("dev")
                mock_ensure.assert_called_with(force_fallback=True)

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_password")
    def test_get_token_from_keyring_general_exception(
        self, mock_get_password: Mock, tmp_path: Path
    ) -> None:
        """Test token retrieval handles general exceptions."""
        mock_get_password.side_effect = RuntimeError("Unexpected error")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=True):
                result = manager._get_token_from_keyring("dev")
                assert result is None

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.set_password")
    def test_store_token_in_keyring_success(
        self, mock_set_password: Mock, tmp_path: Path
    ) -> None:
        """Test successful token storage in keyring."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=True):
                result = manager._store_token_in_keyring("dev", "token123")
                assert result is True
                mock_set_password.assert_called_once_with(
                    manager.keyring_service, "dev", "token123"
                )

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.set_password")
    def test_store_token_in_keyring_disabled(
        self, mock_set_password: Mock, tmp_path: Path
    ) -> None:
        """Test token storage when keyring is disabled."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=False):
                result = manager._store_token_in_keyring("dev", "token123")
                assert result is False
                mock_set_password.assert_not_called()

    def test_ensure_keyring_backend_disabled_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test _ensure_keyring_backend when disabled via environment."""
        monkeypatch.setenv("WORKATO_DISABLE_KEYRING", "true")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            # Constructor calls _ensure_keyring_backend
            assert manager._using_fallback_keyring is False

    def test_ensure_keyring_backend_force_fallback(self, tmp_path: Path) -> None:
        """Test _ensure_keyring_backend with force_fallback."""
        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch(
                "workato_platform_cli.cli.utils.config.profiles.keyring.set_keyring"
            ) as mock_set_keyring,
        ):
            manager = ProfileManager()
            manager._ensure_keyring_backend(force_fallback=True)

            assert manager._using_fallback_keyring is True
            mock_set_keyring.assert_called()

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_keyring")
    def test_ensure_keyring_backend_no_backend(
        self, mock_get_keyring: Mock, tmp_path: Path
    ) -> None:
        """Test _ensure_keyring_backend when no backend available."""
        mock_get_keyring.side_effect = Exception("No backend")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            # Should fall back to file keyring
            assert manager._using_fallback_keyring is True

    @patch("inquirer.prompt")
    @pytest.mark.asyncio
    async def test_select_region_interactive_standard_region(
        self, mock_prompt: Mock, tmp_path: Path
    ) -> None:
        """Test interactive region selection for standard region."""
        mock_prompt.return_value = {
            "region": "US Data Center (https://www.workato.com)"
        }

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            result = await manager.select_region_interactive()

            assert result is not None
            assert result.region == "us"
            assert result.name == "US Data Center"

    @patch("inquirer.prompt")
    @pytest.mark.asyncio
    async def test_select_region_interactive_custom_region(
        self, mock_prompt: Mock, tmp_path: Path
    ) -> None:
        """Test interactive region selection for custom region."""
        mock_prompt.return_value = {"region": "Custom URL"}

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("asyncclick.prompt", return_value="https://custom.workato.com"),
        ):
            manager = ProfileManager()
            result = await manager.select_region_interactive()

            assert result is not None
            assert result.region == "custom"
            assert result.url == "https://custom.workato.com"

    @patch("inquirer.prompt")
    @pytest.mark.asyncio
    async def test_select_region_interactive_user_cancel(
        self, mock_prompt: Mock, tmp_path: Path
    ) -> None:
        """Test interactive region selection when user cancels."""
        mock_prompt.return_value = None  # User cancelled

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            result = await manager.select_region_interactive()

            assert result is None

    @patch("inquirer.prompt")
    @pytest.mark.asyncio
    async def test_select_region_interactive_custom_invalid_url(
        self, mock_prompt: Mock, tmp_path: Path
    ) -> None:
        """Test interactive region selection with invalid custom URL."""
        mock_prompt.return_value = {"region": "Custom URL"}

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch(
                "asyncclick.prompt", return_value="http://insecure.com"
            ),  # Invalid HTTP URL
            patch("asyncclick.echo") as mock_echo,
        ):
            manager = ProfileManager()
            result = await manager.select_region_interactive()

            assert result is None
            # Should have shown error message
            mock_echo.assert_called()

    @patch("inquirer.prompt")
    @pytest.mark.asyncio
    async def test_select_region_interactive_custom_with_existing_profile(
        self, mock_prompt: Mock, tmp_path: Path
    ) -> None:
        """Test interactive region selection for custom region with existing profile."""
        mock_prompt.return_value = {"region": "Custom URL"}

        existing_profile = ProfileData(
            region="custom", region_url="https://existing.workato.com", workspace_id=123
        )

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("asyncclick.prompt", return_value="https://new.workato.com"),
            patch.object(ProfileManager, "get_profile", return_value=existing_profile),
        ):
            manager = ProfileManager()
            result = await manager.select_region_interactive("existing-profile")

            assert result is not None
            assert result.region == "custom"
            assert result.url == "https://new.workato.com"

    def test_ensure_global_config_dir(self, tmp_path: Path) -> None:
        """Test _ensure_global_config_dir creates directory with correct permissions."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            config_dir = tmp_path / ".workato"

            # Remove directory if it exists
            if config_dir.exists():
                config_dir.rmdir()

            manager._ensure_global_config_dir()
            assert config_dir.exists()

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.delete_password")
    def test_delete_token_from_keyring_success(
        self, mock_delete_password: Mock, tmp_path: Path
    ) -> None:
        """Test successful token deletion from keyring."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=True):
                result = manager._delete_token_from_keyring("dev")
                assert result is True
                mock_delete_password.assert_called_once()

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.delete_password")
    def test_delete_token_from_keyring_disabled(
        self, mock_delete_password: Mock, tmp_path: Path
    ) -> None:
        """Test token deletion when keyring is disabled."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=False):
                result = manager._delete_token_from_keyring("dev")
                assert result is False
                mock_delete_password.assert_not_called()

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.delete_password")
    def test_delete_token_from_keyring_no_keyring_error(
        self, mock_delete_password: Mock, tmp_path: Path
    ) -> None:
        """Test token deletion handles NoKeyringError."""
        mock_delete_password.side_effect = NoKeyringError("No keyring")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch.object(manager, "_ensure_keyring_backend") as mock_ensure,
            ):
                manager._delete_token_from_keyring("dev")
                mock_ensure.assert_called_with(force_fallback=True)

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.delete_password")
    def test_delete_token_from_keyring_keyring_error(
        self, mock_delete_password: Mock, tmp_path: Path
    ) -> None:
        """Test token deletion handles KeyringError."""
        mock_delete_password.side_effect = KeyringError("Keyring error")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch.object(manager, "_ensure_keyring_backend") as mock_ensure,
            ):
                manager._delete_token_from_keyring("dev")
                mock_ensure.assert_called_with(force_fallback=True)

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.delete_password")
    def test_delete_token_from_keyring_general_exception(
        self, mock_delete_password: Mock, tmp_path: Path
    ) -> None:
        """Test token deletion handles general exceptions."""
        mock_delete_password.side_effect = RuntimeError("Unexpected error")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=True):
                result = manager._delete_token_from_keyring("dev")
                assert result is False

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.set_password")
    def test_store_token_in_keyring_no_keyring_error(
        self, mock_set_password: Mock, tmp_path: Path
    ) -> None:
        """Test token storage handles NoKeyringError."""
        mock_set_password.side_effect = NoKeyringError("No keyring")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch.object(manager, "_ensure_keyring_backend") as mock_ensure,
            ):
                manager._store_token_in_keyring("dev", "token123")
                mock_ensure.assert_called_with(force_fallback=True)

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.set_password")
    def test_store_token_in_keyring_keyring_error(
        self, mock_set_password: Mock, tmp_path: Path
    ) -> None:
        """Test token storage handles KeyringError."""
        mock_set_password.side_effect = KeyringError("Keyring error")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch.object(manager, "_ensure_keyring_backend") as mock_ensure,
            ):
                manager._store_token_in_keyring("dev", "token123")
                mock_ensure.assert_called_with(force_fallback=True)

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.set_password")
    def test_store_token_in_keyring_general_exception(
        self, mock_set_password: Mock, tmp_path: Path
    ) -> None:
        """Test token storage handles general exceptions."""
        mock_set_password.side_effect = RuntimeError("Unexpected error")

        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()

            with patch.object(manager, "_is_keyring_enabled", return_value=True):
                result = manager._store_token_in_keyring("dev", "token123")
                assert result is False

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_keyring")
    def test_ensure_keyring_backend_successful_backend(
        self, mock_get_keyring: Mock, tmp_path: Path
    ) -> None:
        """Test _ensure_keyring_backend with successful backend."""
        # Create a mock backend with proper priority
        mock_backend = Mock()
        mock_backend.priority = 1.0  # Good priority
        mock_backend.__class__.__module__ = "keyring.backends.macOS"

        # Mock the health check to succeed
        mock_get_keyring.return_value = mock_backend

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch.object(mock_backend, "set_password"),
            patch.object(mock_backend, "delete_password"),
        ):
            manager = ProfileManager()
            # Should not fall back since backend is good
            assert manager._using_fallback_keyring is False

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_keyring")
    def test_ensure_keyring_backend_failed_backend(
        self, mock_get_keyring: Mock, tmp_path: Path
    ) -> None:
        """Test _ensure_keyring_backend with failed backend."""
        # Create a mock backend that fails health check
        mock_backend = Mock()
        mock_backend.priority = 1.0
        mock_backend.__class__.__module__ = "keyring.backends.macOS"
        mock_backend.set_password.side_effect = KeyringError("Health check failed")

        mock_get_keyring.return_value = mock_backend

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch(
                "workato_platform_cli.cli.utils.config.profiles.keyring.set_keyring"
            ) as mock_set_keyring,
        ):
            manager = ProfileManager()
            # Should fall back due to failed health check
            assert manager._using_fallback_keyring is True
            mock_set_keyring.assert_called()

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_keyring")
    def test_ensure_keyring_backend_fail_module(
        self, mock_get_keyring: Mock, tmp_path: Path
    ) -> None:
        """Test _ensure_keyring_backend with fail backend module."""
        # Create a mock backend from fail module
        mock_backend = Mock()
        mock_backend.priority = 1.0
        mock_backend.__class__.__module__ = "keyring.backends.fail"

        mock_get_keyring.return_value = mock_backend

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch(
                "workato_platform_cli.cli.utils.config.profiles.keyring.set_keyring"
            ) as mock_set_keyring,
        ):
            manager = ProfileManager()
            # Should fall back due to fail module
            assert manager._using_fallback_keyring is True
            mock_set_keyring.assert_called()

    @patch("workato_platform_cli.cli.utils.config.profiles.keyring.get_keyring")
    def test_ensure_keyring_backend_zero_priority(
        self, mock_get_keyring: Mock, tmp_path: Path
    ) -> None:
        """Test _ensure_keyring_backend with zero priority backend."""
        # Create a mock backend with zero priority
        mock_backend = Mock()
        mock_backend.priority = 0  # Zero priority
        mock_backend.__class__.__module__ = "keyring.backends.macOS"

        mock_get_keyring.return_value = mock_backend

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch(
                "workato_platform_cli.cli.utils.config.profiles.keyring.set_keyring"
            ) as mock_set_keyring,
        ):
            manager = ProfileManager()
            # Should fall back due to zero priority
            assert manager._using_fallback_keyring is True
            mock_set_keyring.assert_called()

    def test_get_token_from_keyring_fallback_after_error(self, tmp_path: Path) -> None:
        """Test token retrieval uses fallback keyring when already set."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            manager._using_fallback_keyring = True  # Already using fallback

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch(
                    "workato_platform_cli.cli.utils.config.profiles.keyring.get_password",
                    return_value="fallback-token",
                ),
            ):
                result = manager._get_token_from_keyring("dev")
                assert result == "fallback-token"

    def test_store_token_fallback_keyring_success(self, tmp_path: Path) -> None:
        """Test token storage with fallback keyring after error."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            manager._using_fallback_keyring = False

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch(
                    "workato_platform_cli.cli.utils.config.profiles.keyring.set_password"
                ) as mock_set_password,
                patch.object(manager, "_ensure_keyring_backend"),
            ):
                # First fails, then succeeds with fallback
                mock_set_password.side_effect = [NoKeyringError("No keyring"), None]
                manager._using_fallback_keyring = True  # Set to fallback after error

                result = manager._store_token_in_keyring("dev", "token123")
                assert result is True

    def test_delete_token_fallback_keyring_success(self, tmp_path: Path) -> None:
        """Test token deletion with fallback keyring after error."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            manager._using_fallback_keyring = False

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch(
                    "workato_platform_cli.cli.utils.config.profiles.keyring.delete_password"
                ) as mock_delete_password,
                patch.object(manager, "_ensure_keyring_backend"),
            ):
                # First fails, then succeeds with fallback
                mock_delete_password.side_effect = [NoKeyringError("No keyring"), None]
                manager._using_fallback_keyring = True  # Set to fallback after error

                result = manager._delete_token_from_keyring("dev")
                assert result is True

    def test_get_token_fallback_keyring_after_keyring_error(
        self, tmp_path: Path
    ) -> None:
        """Test token retrieval with fallback after KeyringError."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            manager = ProfileManager()
            manager._using_fallback_keyring = False

            with (
                patch.object(manager, "_is_keyring_enabled", return_value=True),
                patch(
                    "workato_platform_cli.cli.utils.config.profiles.keyring.get_password"
                ) as mock_get_password,
                patch.object(manager, "_ensure_keyring_backend"),
            ):
                # First fails with KeyringError, then succeeds with fallback
                mock_get_password.side_effect = [
                    KeyringError("Keyring error"),
                    "fallback-token",
                ]
                manager._using_fallback_keyring = True  # Set to fallback after error

                result = manager._get_token_from_keyring("dev")
                assert result == "fallback-token"
