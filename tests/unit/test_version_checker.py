"""Tests for version checking functionality."""

import json
import urllib.error

from unittest.mock import Mock, patch

from workato_platform.cli.utils.version_checker import VersionChecker


class TestVersionChecker:
    """Test the VersionChecker class."""

    def test_init(self, mock_config_manager, temp_config_dir):
        """Test VersionChecker initialization."""
        checker = VersionChecker(mock_config_manager)

        assert checker.config_manager == mock_config_manager
        assert checker.cache_dir.name == "workato-platform-cli"
        assert checker.cache_file.name == "last_update_check"

    def test_is_update_check_disabled_env_var(self, mock_config_manager, monkeypatch):
        """Test update checking can be disabled via environment variable."""
        monkeypatch.setenv("WORKATO_DISABLE_UPDATE_CHECK", "1")
        checker = VersionChecker(mock_config_manager)

        assert checker.is_update_check_disabled() is True

    def test_is_update_check_disabled_default(self, mock_config_manager, monkeypatch):
        """Test update checking is enabled by default."""
        # Ensure environment variable is not set
        monkeypatch.delenv("WORKATO_DISABLE_UPDATE_CHECK", raising=False)

        checker = VersionChecker(mock_config_manager)

        assert checker.is_update_check_disabled() is False

    @patch("workato_platform.cli.utils.version_checker.urllib.request.urlopen")
    def test_get_latest_version_success(self, mock_urlopen, mock_config_manager):
        """Test successful version retrieval from PyPI."""
        # Mock response
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value.decode.return_value = json.dumps(
            {"info": {"version": "1.2.3"}}
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        checker = VersionChecker(mock_config_manager)
        version = checker.get_latest_version()

        assert version == "1.2.3"

    @patch("workato_platform.cli.utils.version_checker.urllib.request.urlopen")
    def test_get_latest_version_http_error(self, mock_urlopen, mock_config_manager):
        """Test version retrieval handles HTTP errors."""
        mock_urlopen.side_effect = urllib.error.URLError("Network error")

        checker = VersionChecker(mock_config_manager)
        version = checker.get_latest_version()

        assert version is None

    @patch("workato_platform.cli.utils.version_checker.urllib.request.urlopen")
    def test_get_latest_version_non_https_url(self, mock_urlopen, mock_config_manager):
        """Test version retrieval only allows HTTPS URLs."""
        # This should be caught by the HTTPS validation
        checker = VersionChecker(mock_config_manager)

        # Patch the PYPI_API_URL to use HTTP (should be rejected)
        with patch(
            "workato_platform.cli.utils.version_checker.PYPI_API_URL",
            "http://pypi.org/test",
        ):
            version = checker.get_latest_version()
            assert version is None
            # URL should not be called due to HTTPS validation
            mock_urlopen.assert_not_called()

    def test_check_for_updates_newer_available(self, mock_config_manager):
        """Test check_for_updates detects newer version."""
        checker = VersionChecker(mock_config_manager)

        with patch.object(checker, "get_latest_version", return_value="2.0.0"):
            result = checker.check_for_updates("1.0.0")
            assert result == "2.0.0"

    def test_check_for_updates_current_latest(self, mock_config_manager):
        """Test check_for_updates when current version is latest."""
        checker = VersionChecker(mock_config_manager)

        with patch.object(checker, "get_latest_version", return_value="1.0.0"):
            result = checker.check_for_updates("1.0.0")
            assert result is None

    def test_check_for_updates_newer_current(self, mock_config_manager):
        """Test check_for_updates when current version is newer than published."""
        checker = VersionChecker(mock_config_manager)

        with patch.object(checker, "get_latest_version", return_value="1.0.0"):
            result = checker.check_for_updates("2.0.0.dev1")
            assert result is None

    def test_should_check_for_updates_disabled(self, mock_config_manager, monkeypatch):
        """Test should_check_for_updates respects disable flag."""
        monkeypatch.setenv("WORKATO_DISABLE_UPDATE_CHECK", "true")
        checker = VersionChecker(mock_config_manager)

        assert checker.should_check_for_updates() is False

    @patch("workato_platform.cli.utils.version_checker.HAS_DEPENDENCIES", True)
    def test_should_check_for_updates_no_cache_file(
        self, mock_config_manager, monkeypatch, tmp_path
    ):
        """Test should_check_for_updates when no cache file exists."""
        # Ensure environment variable is not set
        monkeypatch.delenv("WORKATO_DISABLE_UPDATE_CHECK", raising=False)

        checker = VersionChecker(mock_config_manager)

        # Mock the cache directory to use temp directory
        checker.cache_dir = tmp_path / "workato-platform-cli-cache"
        checker.cache_file = checker.cache_dir / "last_update_check"

        # Cache file shouldn't exist in temp directory
        assert not checker.cache_file.exists()
        assert checker.should_check_for_updates() is True
