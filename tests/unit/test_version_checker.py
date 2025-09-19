"""Tests for version checking functionality."""

import json
import os
import time
import urllib.error

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import pytest

from workato_platform.cli.utils.config import ConfigManager
from workato_platform.cli.utils.version_checker import (
    CHECK_INTERVAL,
    VersionChecker,
    check_updates_async,
)


class TestVersionChecker:
    """Test the VersionChecker class."""

    def test_init(self, mock_config_manager: ConfigManager) -> None:
        """Test VersionChecker initialization."""
        checker = VersionChecker(mock_config_manager)

        assert checker.config_manager == mock_config_manager
        assert checker.cache_dir.name == "workato-platform-cli"
        assert checker.cache_file.name == "last_update_check"

    def test_is_update_check_disabled_env_var(
        self, mock_config_manager: ConfigManager, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test update checking can be disabled via environment variable."""
        monkeypatch.setenv("WORKATO_DISABLE_UPDATE_CHECK", "1")
        checker = VersionChecker(mock_config_manager)

        assert checker.is_update_check_disabled() is True

    def test_is_update_check_disabled_default(
        self, mock_config_manager: ConfigManager, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test update checking is enabled by default."""
        # Ensure environment variable is not set
        monkeypatch.delenv("WORKATO_DISABLE_UPDATE_CHECK", raising=False)

        checker = VersionChecker(mock_config_manager)

        assert checker.is_update_check_disabled() is False

    @patch("workato_platform.cli.utils.version_checker.urllib.request.urlopen")
    def test_get_latest_version_success(
        self, mock_urlopen: MagicMock, mock_config_manager: ConfigManager
    ) -> None:
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
    def test_get_latest_version_http_error(
        self, mock_urlopen: MagicMock, mock_config_manager: ConfigManager
    ) -> None:
        """Test version retrieval handles HTTP errors."""
        mock_urlopen.side_effect = urllib.error.URLError("Network error")

        checker = VersionChecker(mock_config_manager)
        version = checker.get_latest_version()

        assert version is None

    @patch("workato_platform.cli.utils.version_checker.urllib.request.urlopen")
    def test_get_latest_version_non_https_url(
        self, mock_urlopen: MagicMock, mock_config_manager: ConfigManager
    ) -> None:
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

    @patch("workato_platform.cli.utils.version_checker.urllib.request.urlopen")
    def test_get_latest_version_non_200_status(
        self,
        mock_urlopen: MagicMock,
        mock_config_manager: ConfigManager,
    ) -> None:
        response = Mock()
        response.getcode.return_value = 500
        mock_urlopen.return_value.__enter__.return_value = response

        checker = VersionChecker(mock_config_manager)

        assert checker.get_latest_version() is None

    def test_check_for_updates_newer_available(
        self, mock_config_manager: ConfigManager
    ) -> None:
        """Test check_for_updates detects newer version."""
        checker = VersionChecker(mock_config_manager)

        with patch.object(checker, "get_latest_version", return_value="2.0.0"):
            result = checker.check_for_updates("1.0.0")
            assert result == "2.0.0"

    def test_check_for_updates_current_latest(
        self, mock_config_manager: ConfigManager
    ) -> None:
        """Test check_for_updates when current version is latest."""
        checker = VersionChecker(mock_config_manager)

        with patch.object(checker, "get_latest_version", return_value="1.0.0"):
            result = checker.check_for_updates("1.0.0")
            assert result is None

    def test_check_for_updates_newer_current(
        self, mock_config_manager: ConfigManager
    ) -> None:
        """Test check_for_updates when current version is newer than published."""
        checker = VersionChecker(mock_config_manager)

        with patch.object(checker, "get_latest_version", return_value="1.0.0"):
            result = checker.check_for_updates("2.0.0.dev1")
            assert result is None

    def test_should_check_for_updates_disabled(
        self, mock_config_manager: ConfigManager, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test should_check_for_updates respects disable flag."""
        monkeypatch.setenv("WORKATO_DISABLE_UPDATE_CHECK", "true")
        checker = VersionChecker(mock_config_manager)

        assert checker.should_check_for_updates() is False

    @patch("workato_platform.cli.utils.version_checker.HAS_DEPENDENCIES", True)
    def test_should_check_for_updates_no_cache_file(
        self,
        mock_config_manager: ConfigManager,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
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

    def test_should_check_for_updates_respects_cache_timestamp(
        self,
        mock_config_manager: ConfigManager,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.delenv("WORKATO_DISABLE_UPDATE_CHECK", raising=False)
        checker = VersionChecker(mock_config_manager)
        checker.cache_dir = tmp_path
        checker.cache_file = tmp_path / "last_update_check"
        checker.cache_dir.mkdir(exist_ok=True)
        checker.cache_file.write_text("cached")

        recent = time.time() - (CHECK_INTERVAL / 2)
        os.utime(checker.cache_file, (recent, recent))

        assert checker.should_check_for_updates() is False

    def test_should_check_for_updates_handles_stat_error(
        self,
        mock_config_manager: ConfigManager,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.delenv("WORKATO_DISABLE_UPDATE_CHECK", raising=False)
        checker = VersionChecker(mock_config_manager)
        checker.cache_dir = tmp_path
        checker.cache_file = tmp_path / "last_update_check"
        checker.cache_dir.mkdir(exist_ok=True)
        checker.cache_file.write_text("cached")

        def raising_stat(_self: Path) -> None:
            raise OSError

        monkeypatch.setattr(Path, "exists", lambda self: True, raising=False)
        monkeypatch.setattr(Path, "stat", raising_stat, raising=False)

        assert checker.should_check_for_updates() is True

    def test_update_cache_timestamp_creates_file(
        self,
        mock_config_manager: ConfigManager,
        tmp_path: Path,
    ) -> None:
        checker = VersionChecker(mock_config_manager)
        checker.cache_dir = tmp_path
        checker.cache_file = tmp_path / "last_update_check"

        checker.update_cache_timestamp()

        assert checker.cache_file.exists()

    def test_background_update_check_notifies_when_new_version(
        self,
        mock_config_manager: ConfigManager,
        tmp_path: Path,
    ) -> None:
        checker = VersionChecker(mock_config_manager)
        checker.cache_dir = tmp_path
        checker.cache_file = tmp_path / "last_update_check"

        should_check_mock = Mock(return_value=True)
        check_for_updates_mock = Mock(return_value="2.0.0")
        show_notification_mock = Mock()
        update_cache_mock = Mock()

        with (
            patch.object(checker, "should_check_for_updates", should_check_mock),
            patch.object(checker, "check_for_updates", check_for_updates_mock),
            patch.object(checker, "show_update_notification", show_notification_mock),
            patch.object(checker, "update_cache_timestamp", update_cache_mock),
        ):
            checker.background_update_check("1.0.0")

        show_notification_mock.assert_called_once_with("2.0.0")
        update_cache_mock.assert_called_once()

    def test_background_update_check_handles_exceptions(
        self,
        mock_config_manager: ConfigManager,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        checker = VersionChecker(mock_config_manager)
        checker.cache_dir = tmp_path
        checker.cache_file = tmp_path / "last_update_check"

        should_check_mock = Mock(return_value=True)
        check_for_updates_mock = Mock(side_effect=RuntimeError("boom"))
        update_cache_mock = Mock()

        with (
            patch.object(checker, "should_check_for_updates", should_check_mock),
            patch.object(checker, "check_for_updates", check_for_updates_mock),
            patch.object(checker, "update_cache_timestamp", update_cache_mock),
        ):
            checker.background_update_check("1.0.0")

        output = capsys.readouterr().out
        assert "Failed to check for updates" in output

    def test_background_update_check_skips_when_not_needed(
        self,
        mock_config_manager: ConfigManager,
        tmp_path: Path,
    ) -> None:
        checker = VersionChecker(mock_config_manager)
        checker.cache_dir = tmp_path
        checker.cache_file = tmp_path / "last_update_check"

        should_check_mock = Mock(return_value=False)
        check_for_updates_mock = Mock()

        with (
            patch.object(checker, "should_check_for_updates", should_check_mock),
            patch.object(checker, "check_for_updates", check_for_updates_mock),
        ):
            checker.background_update_check("1.0.0")

        check_for_updates_mock.assert_not_called()

    @patch("workato_platform.cli.utils.version_checker.click.echo")
    def test_check_for_updates_handles_parse_error(
        self,
        mock_echo: MagicMock,
        mock_config_manager: ConfigManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        checker = VersionChecker(mock_config_manager)

        def raising_parse(_value: str) -> None:
            raise ValueError("bad version")

        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.version.parse",
            raising_parse,
        )

        get_latest_version_mock = Mock(return_value="2.0.0")
        with patch.object(checker, "get_latest_version", get_latest_version_mock):
            assert checker.check_for_updates("1.0.0") is None
        mock_echo.assert_called_with("Failed to check for updates")

    def test_should_check_for_updates_no_dependencies(
        self,
        mock_config_manager: ConfigManager,
    ) -> None:
        checker = VersionChecker(mock_config_manager)
        with patch(
            "workato_platform.cli.utils.version_checker.HAS_DEPENDENCIES", False
        ):
            assert checker.should_check_for_updates() is False
            assert checker.get_latest_version() is None
            assert checker.check_for_updates("1.0.0") is None

    @patch("workato_platform.cli.utils.version_checker.urllib.request.urlopen")
    def test_get_latest_version_without_tls_version(
        self,
        mock_urlopen: MagicMock,
        mock_config_manager: ConfigManager,
    ) -> None:
        fake_ctx = Mock()
        fake_ctx.options = 0
        fake_ssl = SimpleNamespace(
            create_default_context=Mock(return_value=fake_ctx),
            OP_NO_SSLv2=1,
            OP_NO_SSLv3=2,
            OP_NO_TLSv1=4,
            OP_NO_TLSv1_1=8,
        )

        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value.decode.return_value = json.dumps(
            {"info": {"version": "9.9.9"}}
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with patch("workato_platform.cli.utils.version_checker.ssl", fake_ssl):
            checker = VersionChecker(mock_config_manager)
            assert checker.get_latest_version() == "9.9.9"
            fake_ssl.create_default_context.assert_called_once()

    @patch("workato_platform.cli.utils.version_checker.click.echo")
    def test_show_update_notification_outputs(
        self, mock_echo: MagicMock, mock_config_manager: ConfigManager
    ) -> None:
        checker = VersionChecker(mock_config_manager)
        checker.show_update_notification("2.0.0")

        assert mock_echo.call_count >= 3

    def test_background_update_check_updates_timestamp_when_no_update(
        self,
        mock_config_manager: ConfigManager,
        tmp_path: Path,
    ) -> None:
        checker = VersionChecker(mock_config_manager)
        checker.cache_dir = tmp_path
        checker.cache_file = tmp_path / "last_update_check"

        should_check_mock = Mock(return_value=True)
        check_for_updates_mock = Mock(return_value=None)
        update_cache_mock = Mock()

        with (
            patch.object(checker, "should_check_for_updates", should_check_mock),
            patch.object(checker, "check_for_updates", check_for_updates_mock),
            patch.object(checker, "update_cache_timestamp", update_cache_mock),
        ):
            checker.background_update_check("1.0.0")

        update_cache_mock.assert_called_once()

    def test_check_updates_async_sync_wrapper(
        self,
        mock_config_manager: ConfigManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        checker_instance = Mock()
        checker_instance.should_check_for_updates.return_value = True
        thread_instance = Mock()

        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.VersionChecker",
            Mock(return_value=checker_instance),
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.threading.Thread",
            Mock(return_value=thread_instance),
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.Container",
            SimpleNamespace(config_manager=Mock(return_value=mock_config_manager)),
            raising=False,
        )

        @check_updates_async
        def sample() -> str:
            return "done"

        assert sample() == "done"
        thread_instance.start.assert_called_once()
        thread_instance.join.assert_called_once_with(timeout=3)

    @pytest.mark.asyncio
    async def test_check_updates_async_async_wrapper(
        self,
        mock_config_manager: ConfigManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        checker_instance = Mock()
        checker_instance.should_check_for_updates.return_value = False

        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.VersionChecker",
            Mock(return_value=checker_instance),
        )
        thread_mock = Mock()
        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.threading.Thread",
            thread_mock,
        )
        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.Container",
            SimpleNamespace(config_manager=Mock(return_value=mock_config_manager)),
            raising=False,
        )

        @check_updates_async
        async def async_sample() -> str:
            return "async-done"

        result = await async_sample()
        assert result == "async-done"
        thread_mock.assert_not_called()

    def test_check_updates_async_sync_wrapper_handles_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.Container",
            SimpleNamespace(config_manager=Mock(side_effect=RuntimeError("boom"))),
            raising=False,
        )

        @check_updates_async
        def sample() -> str:
            raise RuntimeError("command failed")

        with pytest.raises(RuntimeError):
            sample()

    @pytest.mark.asyncio
    async def test_check_updates_async_async_wrapper_handles_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "workato_platform.cli.utils.version_checker.Container",
            SimpleNamespace(config_manager=Mock(side_effect=RuntimeError("boom"))),
            raising=False,
        )

        @check_updates_async
        async def async_sample() -> None:
            raise RuntimeError("cmd failed")

        with pytest.raises(RuntimeError):
            await async_sample()
