"""Tests for the deprecation warning command and DeprecationNotifier class."""

import os

from pathlib import Path
from unittest.mock import patch

import pytest
from asyncclick.testing import CliRunner

from workato_platform_cli.cli.commands.deprecation_warning import deprecation_warning
from workato_platform_cli.cli.utils.version_checker import (
    DEPRECATION_DISABLE_FLAG,
    NEW_CLI_URL,
    DeprecationNotifier,
)


# ---------------------------------------------------------------------------
# DeprecationNotifier unit tests
# ---------------------------------------------------------------------------


class TestDeprecationNotifier:
    """Tests for the DeprecationNotifier class."""

    def test_is_disabled_false_by_default(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Warning is enabled when no env var is set and no flag file exists."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        assert notifier.is_disabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "YES"])
    def test_is_disabled_via_env_var(
        self,
        value: str,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """All truthy env var values disable the warning."""
        monkeypatch.setenv("WORKATO_DISABLE_DEPRECATION_WARNING", value)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        assert notifier.is_disabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", "random"])
    def test_is_not_disabled_for_falsy_env_values(
        self,
        value: str,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Non-truthy env var values leave the warning enabled."""
        monkeypatch.setenv("WORKATO_DISABLE_DEPRECATION_WARNING", value)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        assert notifier.is_disabled() is False

    def test_is_disabled_via_flag_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Flag file presence disables the warning."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        flag = tmp_path / DEPRECATION_DISABLE_FLAG
        flag.touch()
        notifier.disable_flag_file = flag

        assert notifier.is_disabled() is True

    def test_disable_creates_flag_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """disable() creates the flag file."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        assert not notifier.disable_flag_file.exists()
        notifier.disable()
        assert notifier.disable_flag_file.exists()

    def test_enable_removes_flag_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """enable() removes the flag file."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        flag = tmp_path / DEPRECATION_DISABLE_FLAG
        flag.touch()
        notifier.disable_flag_file = flag

        assert flag.exists()
        notifier.enable()
        assert not flag.exists()

    def test_enable_is_idempotent_when_no_flag_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """enable() does not raise when no flag file exists."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        # Should not raise
        notifier.enable()

    def test_disable_is_idempotent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Calling disable() twice does not raise."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        notifier.disable()
        notifier.disable()  # second call should be fine
        assert notifier.disable_flag_file.exists()

    def test_show_prints_to_stderr(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """show() writes the deprecation message to stderr."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.show()

        captured = capsys.readouterr()
        assert "DEPRECATION NOTICE" in captured.err
        assert NEW_CLI_URL in captured.err
        assert "workato deprecation-warning disable" in captured.err
        assert "WORKATO_DISABLE_DEPRECATION_WARNING" in captured.err

    def test_show_does_not_write_to_stdout(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """show() must not pollute stdout (important for users piping CLI output)."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.show()

        captured = capsys.readouterr()
        # The only stdout line is the blank separator echo(file=None)
        assert "DEPRECATION" not in captured.out

    def test_run_shows_warning_when_enabled(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run() calls show() when the warning is not disabled."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        with patch.object(notifier, "show") as mock_show:
            notifier.run()
            mock_show.assert_called_once()

    def test_run_is_suppressed_by_env_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run() does not call show() when the env var is set."""
        monkeypatch.setenv("WORKATO_DISABLE_DEPRECATION_WARNING", "1")
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        with patch.object(notifier, "show") as mock_show:
            notifier.run()
            mock_show.assert_not_called()

    def test_run_is_suppressed_by_flag_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run() does not call show() when the flag file exists."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        flag = tmp_path / DEPRECATION_DISABLE_FLAG
        flag.touch()
        notifier.disable_flag_file = flag

        with patch.object(notifier, "show") as mock_show:
            notifier.run()
            mock_show.assert_not_called()

    def test_run_silences_exceptions(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """run() never raises — exceptions from show() are swallowed."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG

        with patch.object(notifier, "show", side_effect=RuntimeError("boom")):
            # Must not raise
            notifier.run()

    def test_ensure_cache_dir_created(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """DeprecationNotifier creates its cache directory on init."""
        # Path.home() is already monkeypatched to tmp_path via isolate_tests fixture
        notifier = DeprecationNotifier()
        assert notifier.cache_dir.exists()

    def test_disable_handles_os_error_gracefully(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """disable() swallows OSError when the flag file cannot be created."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        # Point flag file at a path inside a non-existent, read-only structure
        notifier.disable_flag_file = Path("/nonexistent/readonly/flag")

        # Should not raise
        notifier.disable()

    def test_enable_handles_os_error_gracefully(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """enable() swallows OSError when the flag file cannot be removed."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        notifier = DeprecationNotifier()
        flag = tmp_path / DEPRECATION_DISABLE_FLAG
        flag.touch()
        notifier.disable_flag_file = flag

        with patch.object(Path, "unlink", side_effect=OSError("permission denied")):
            # Should not raise
            notifier.enable()


# ---------------------------------------------------------------------------
# CLI command tests: workato deprecation-warning disable/enable/status
# ---------------------------------------------------------------------------


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def notifier_with_tmp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> DeprecationNotifier:
    """A DeprecationNotifier whose flag file lives in tmp_path."""
    monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
    notifier = DeprecationNotifier()
    notifier.disable_flag_file = tmp_path / DEPRECATION_DISABLE_FLAG
    return notifier


class TestDeprecationWarningDisableCommand:
    """Tests for `workato deprecation-warning disable`."""

    @pytest.mark.asyncio
    async def test_disable_creates_flag_and_confirms(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """disable command creates the flag file and prints confirmation."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        flag = tmp_path / DEPRECATION_DISABLE_FLAG

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.is_disabled.return_value = False
            instance.disable_flag_file = flag

            result = await CliRunner().invoke(deprecation_warning, ["disable"])

        assert result.exit_code == 0
        assert "disabled" in result.output.lower()
        instance.disable.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_is_idempotent_message(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """disable command tells the user when it's already disabled."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.is_disabled.return_value = True

            result = await CliRunner().invoke(deprecation_warning, ["disable"])

        assert result.exit_code == 0
        assert "already disabled" in result.output.lower()
        instance.disable.assert_not_called()


class TestDeprecationWarningEnableCommand:
    """Tests for `workato deprecation-warning enable`."""

    @pytest.mark.asyncio
    async def test_enable_removes_flag_and_confirms(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """enable command removes the flag file and prints confirmation."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        flag = tmp_path / DEPRECATION_DISABLE_FLAG
        flag.touch()

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.disable_flag_file = flag
            instance.is_disabled.return_value = False

            result = await CliRunner().invoke(deprecation_warning, ["enable"])

        assert result.exit_code == 0
        assert "re-enabled" in result.output.lower()
        instance.enable.assert_called_once()

    @pytest.mark.asyncio
    async def test_enable_when_already_enabled_gives_info(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """enable command informs user when the flag file was not set."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        flag = tmp_path / DEPRECATION_DISABLE_FLAG  # Does not exist

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.disable_flag_file = flag
            instance.is_disabled.return_value = False

            result = await CliRunner().invoke(deprecation_warning, ["enable"])

        assert result.exit_code == 0
        assert "not currently disabled" in result.output.lower()

    @pytest.mark.asyncio
    async def test_enable_warns_when_env_var_still_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """enable command warns the user if the env var is still suppressing the warning."""
        monkeypatch.setenv("WORKATO_DISABLE_DEPRECATION_WARNING", "1")
        flag = tmp_path / DEPRECATION_DISABLE_FLAG
        flag.touch()

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.disable_flag_file = flag
            instance.is_disabled.return_value = True  # still disabled via env var

            result = await CliRunner().invoke(deprecation_warning, ["enable"])

        assert result.exit_code == 0
        assert "WORKATO_DISABLE_DEPRECATION_WARNING" in result.output


class TestDeprecationWarningStatusCommand:
    """Tests for `workato deprecation-warning status`."""

    @pytest.mark.asyncio
    async def test_status_shows_enabled(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """status command reports ENABLED when no disable mechanism is active."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        flag = tmp_path / DEPRECATION_DISABLE_FLAG  # Does not exist

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.is_disabled.return_value = False
            instance.disable_flag_file = flag

            result = await CliRunner().invoke(deprecation_warning, ["status"])

        assert result.exit_code == 0
        assert "ENABLED" in result.output

    @pytest.mark.asyncio
    async def test_status_shows_disabled_when_flag_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """status command reports DISABLED when flag file exists."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        flag = tmp_path / DEPRECATION_DISABLE_FLAG
        flag.touch()

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.is_disabled.return_value = True
            instance.disable_flag_file = flag

            result = await CliRunner().invoke(deprecation_warning, ["status"])

        assert result.exit_code == 0
        assert "DISABLED" in result.output

    @pytest.mark.asyncio
    async def test_status_shows_env_var_active(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """status command shows env var as active when it is set."""
        monkeypatch.setenv("WORKATO_DISABLE_DEPRECATION_WARNING", "1")
        flag = tmp_path / DEPRECATION_DISABLE_FLAG

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.is_disabled.return_value = True
            instance.disable_flag_file = flag

            result = await CliRunner().invoke(deprecation_warning, ["status"])

        assert result.exit_code == 0
        assert "WORKATO_DISABLE_DEPRECATION_WARNING" in result.output

    @pytest.mark.asyncio
    async def test_status_shows_new_cli_url(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """status command always displays the new CLI URL."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        flag = tmp_path / DEPRECATION_DISABLE_FLAG

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.is_disabled.return_value = False
            instance.disable_flag_file = flag

            result = await CliRunner().invoke(deprecation_warning, ["status"])

        assert result.exit_code == 0
        assert NEW_CLI_URL in result.output

    @pytest.mark.asyncio
    async def test_status_shows_both_mechanisms(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """status command lists both the flag file and env var disable mechanisms."""
        monkeypatch.delenv("WORKATO_DISABLE_DEPRECATION_WARNING", raising=False)
        flag = tmp_path / DEPRECATION_DISABLE_FLAG

        with patch(
            "workato_platform_cli.cli.commands.deprecation_warning.DeprecationNotifier"
        ) as MockNotifier:
            instance = MockNotifier.return_value
            instance.is_disabled.return_value = False
            instance.disable_flag_file = flag

            result = await CliRunner().invoke(deprecation_warning, ["status"])

        assert result.exit_code == 0
        assert DEPRECATION_DISABLE_FLAG in result.output
        assert "WORKATO_DISABLE_DEPRECATION_WARNING" in result.output


class TestDeprecationWarningCommandHelp:
    """Tests that the command group and subcommands are wired correctly."""

    @pytest.mark.asyncio
    async def test_group_help_lists_subcommands(self) -> None:
        """The deprecation-warning group exposes disable, enable, status."""
        result = await CliRunner().invoke(deprecation_warning, ["--help"])

        assert result.exit_code == 0
        assert "disable" in result.output
        assert "enable" in result.output
        assert "status" in result.output

    @pytest.mark.asyncio
    async def test_disable_help(self) -> None:
        result = await CliRunner().invoke(deprecation_warning, ["disable", "--help"])
        assert result.exit_code == 0
        assert "WORKATO_DISABLE_DEPRECATION_WARNING" in result.output

    @pytest.mark.asyncio
    async def test_enable_help(self) -> None:
        result = await CliRunner().invoke(deprecation_warning, ["enable", "--help"])
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_status_help(self) -> None:
        result = await CliRunner().invoke(deprecation_warning, ["status", "--help"])
        assert result.exit_code == 0
