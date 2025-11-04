"""Tests for the init command."""

import json

from io import StringIO
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import asyncclick as click
import pytest

from workato_platform_cli.cli.commands import init as init_module


@pytest.mark.asyncio
async def test_init_interactive_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test interactive mode (default behavior)."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager, "load_config", return_value=Mock(profile="default")
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=None,
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)

        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda _="": None)

        assert init_module.init.callback
        await init_module.init.callback()

        # Should call initialize with no parameters (interactive mode)
        mock_initialize.assert_awaited_once_with(
            profile_name=None,
            region=None,
            api_token=None,
            api_url=None,
            project_name=None,
            project_id=None,
            output_mode="table",
            non_interactive=False,
        )
        mock_pull.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_non_interactive_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful non-interactive mode with all required parameters."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=None,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)

        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda _="": None)

        # Test non-interactive mode with profile
        # (region and api_token can be None when profile provided)
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )

        # Should call initialize with provided parameters
        mock_initialize.assert_awaited_once_with(
            profile_name="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            output_mode="table",
            non_interactive=True,
        )
        mock_pull.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_non_interactive_custom_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test non-interactive mode with custom region and API URL."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=None,
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://custom.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)

        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda _="": None)

        # Test custom region with API URL
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region="custom",
            api_token="test-token",
            api_url="https://custom.workato.com",
            project_name=None,
            project_id=123,
            non_interactive=True,
        )

        mock_initialize.assert_awaited_once_with(
            profile_name="test-profile",
            region="custom",
            api_token="test-token",
            api_url="https://custom.workato.com",
            project_name=None,
            project_id=123,
            output_mode="table",
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_missing_profile_and_credentials() -> None:
    """Test non-interactive mode fails when neither profile
    nor (region+token) provided."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile=None,
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_missing_region_without_profile() -> None:
    """Test non-interactive mode fails when region missing and no profile provided."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile=None,
            region=None,
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_missing_token_without_profile() -> None:
    """Test non-interactive mode fails when API token missing
    and no profile provided."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile=None,
            region="us",
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_custom_region_missing_url() -> None:
    """Test non-interactive mode fails when custom region is used without API URL."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region="custom",
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_missing_project() -> None:
    """Test non-interactive mode fails when neither project name nor ID is provided."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region="us",
            api_token="test-token",
            api_url=None,
            project_name=None,
            project_id=None,
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_both_project_options() -> None:
    """Test non-interactive mode fails when both project name and ID are provided."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region="us",
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=123,
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_with_region_and_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test non-interactive mode succeeds with region and token (no profile)."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="default"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=None,
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)
        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())
        monkeypatch.setattr(init_module.click, "echo", lambda _="": None)

        # Test with region and token (no profile)
        assert init_module.init.callback
        await init_module.init.callback(
            profile=None,
            region="us",
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )

        # Should call initialize with region and token
        mock_initialize.assert_awaited_once_with(
            profile_name=None,
            region="us",
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
            output_mode="table",
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_json_mode_without_non_interactive() -> None:
    """Test that JSON output mode requires non-interactive flag."""
    output = StringIO()

    with patch.object(init_module.click, "echo", lambda msg: output.write(msg)):
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region="us",
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=False,
            output_mode="json",
        )

    result = json.loads(output.getvalue())
    assert result["status"] == "error"
    assert "non-interactive" in result["error"]
    assert result["error_code"] == "INVALID_OPTIONS"


@pytest.mark.asyncio
async def test_init_json_mode_with_validation_errors() -> None:
    """Test that validation errors in JSON mode return proper JSON."""
    output = StringIO()

    with patch.object(init_module.click, "echo", lambda msg: output.write(msg)):
        # Test missing profile and credentials
        assert init_module.init.callback
        await init_module.init.callback(
            profile=None,
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
            output_mode="json",
        )

    result = json.loads(output.getvalue())
    assert result["status"] == "error"
    assert "profile" in result["error"] or "region" in result["error"]
    assert result["error_code"] == "MISSING_REQUIRED_OPTIONS"


@pytest.mark.asyncio
async def test_init_non_empty_directory_non_interactive_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test non-empty directory error in non-interactive JSON mode."""
    mock_config_manager = Mock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file.txt").write_text("content")

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        output = StringIO()
        monkeypatch.setattr(init_module.click, "echo", lambda msg: output.write(msg))

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
            output_mode="json",
        )

        result = json.loads(output.getvalue())
        assert result["status"] == "error"
        assert "not empty" in result["error"]
        assert result["error_code"] == "DIRECTORY_NOT_EMPTY"


@pytest.mark.asyncio
async def test_init_non_empty_directory_non_interactive_table(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test non-empty directory error in non-interactive table mode."""
    mock_config_manager = Mock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file.txt").write_text("content")

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        monkeypatch.setattr(init_module.click, "echo", lambda *args, **kwargs: None)

        assert init_module.init.callback
        with pytest.raises(click.Abort):
            await init_module.init.callback(
                profile="test-profile",
                region=None,
                api_token=None,
                api_url=None,
                project_name="test-project",
                project_id=None,
                non_interactive=True,
                output_mode="table",
            )


@pytest.mark.asyncio
async def test_init_non_empty_directory_interactive_cancelled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test user cancelling init when directory is non-empty."""
    mock_config_manager = Mock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file.txt").write_text("content")

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        monkeypatch.setattr(init_module.click, "echo", lambda *args, **kwargs: None)
        monkeypatch.setattr(init_module.click, "confirm", lambda *args, **kwargs: False)

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=False,
            output_mode="table",
        )

        # Should not call pull when user cancels
        mock_pull.assert_not_awaited()


@pytest.mark.asyncio
async def test_init_non_empty_directory_interactive_confirmed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test user confirming init when directory is non-empty."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file.txt").write_text("content")

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)
        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda msg="": None)
        monkeypatch.setattr(init_module.click, "confirm", lambda *args, **kwargs: True)

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=False,
            output_mode="table",
        )

        # Should call pull when user confirms
        mock_pull.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_json_output_mode_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test successful init with JSON output mode."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(
                profile="test-profile",
                project_name="test-project",
                project_id=123,
                folder_id=456,
            ),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=None,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "get_profile",
            return_value=Mock(
                region="us",
                region_name="US",
                region_url="https://api.workato.com",
                workspace_id=789,
            ),
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "get_current_profile_name",
            return_value="test-profile",
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)
        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        output = StringIO()
        monkeypatch.setattr(
            init_module.click, "echo", lambda msg: output.write(str(msg))
        )

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
            output_mode="json",
        )

        result = json.loads(output.getvalue())
        assert result["status"] == "success"
        assert result["profile"]["name"] == "test-profile"
        assert result["profile"]["region"] == "us"
        assert result["project"]["name"] == "test-project"
        assert result["project"]["id"] == 123


@pytest.mark.asyncio
async def test_init_cli_managed_files_ignored_interactive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that CLI-managed files are ignored in emptiness check (interactive mode)."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    # Create only CLI-managed files
    (project_dir / ".workatoenv").write_text('{"project_id": 123}')
    (project_dir / ".gitignore").write_text(".workatoenv\n")
    (project_dir / ".workato-ignore").write_text("*.py\n")

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)
        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        echo_calls = []
        monkeypatch.setattr(
            init_module.click, "echo", lambda msg="": echo_calls.append(msg)
        )

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=False,
            output_mode="table",
        )

        # Should proceed without prompting user (no warning about non-empty directory)
        mock_pull.assert_awaited_once()
        # Check that no "not empty" warning was shown
        assert not any("not empty" in str(call) for call in echo_calls)


@pytest.mark.asyncio
async def test_init_cli_managed_files_ignored_non_interactive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that CLI-managed files are ignored in emptiness check (non-interactive)."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    # Create only CLI-managed files
    (project_dir / ".workatoenv").write_text('{"project_id": 123}')
    (project_dir / ".gitignore").write_text(".workatoenv\n")

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)
        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda msg="": None)

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
            output_mode="table",
        )

        # Should proceed without error
        mock_pull.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_user_files_with_cli_files_triggers_warning(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that user files trigger warning even with CLI-managed files present."""
    mock_config_manager = Mock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    # Create both CLI-managed files AND user files
    (project_dir / ".workatoenv").write_text('{"project_id": 123}')
    (project_dir / ".gitignore").write_text(".workatoenv\n")
    (project_dir / "user_file.txt").write_text("user content")

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        monkeypatch.setattr(init_module.click, "echo", lambda msg="": None)

        assert init_module.init.callback
        with pytest.raises(click.Abort):
            await init_module.init.callback(
                profile="test-profile",
                region=None,
                api_token=None,
                api_url=None,
                project_name="test-project",
                project_id=None,
                non_interactive=True,
                output_mode="table",
            )


@pytest.mark.asyncio
async def test_init_only_workatoenv_file_ignored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test that directory with only .workatoenv file is not considered non-empty."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    # Create only .workatoenv (most common case after ConfigManager.initialize)
    (project_dir / ".workatoenv").write_text('{"project_id": 123}')

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=project_dir,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)
        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda msg="": None)

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
            output_mode="table",
        )

        # Should proceed without error
        mock_pull.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_non_interactive_profile_missing_credentials_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test non-interactive mode with missing credentials in JSON output mode."""
    # Mock ConfigManager.initialize to raise ClickException
    # (simulating missing credentials)
    mock_initialize = AsyncMock(
        side_effect=click.ClickException(
            "Profile 'test-profile' exists but credentials not found in keychain. "
            "Please run 'workato init' interactively or set WORKATO_API_TOKEN "
            "environment variable."
        )
    )
    monkeypatch.setattr(
        init_module.ConfigManager,
        "initialize",
        mock_initialize,
    )

    output = StringIO()
    monkeypatch.setattr(init_module.click, "echo", lambda msg: output.write(msg))

    # Mock get_current_context to return output_mode
    mock_ctx = Mock()
    mock_ctx.params = {"output_mode": "json"}
    monkeypatch.setattr(
        init_module.click,
        "get_current_context",
        lambda silent=True: mock_ctx,
    )

    assert init_module.init.callback
    with pytest.raises(SystemExit) as exc_info:
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name=None,
            project_id=123,
            non_interactive=True,
            output_mode="json",
        )

    assert exc_info.value.code == 1
    result = json.loads(output.getvalue())
    assert result["status"] == "error"
    assert "credentials not found" in result["error"]
    assert "test-profile" in result["error"]
    assert result["error_code"] == "CLI_ERROR"


@pytest.mark.asyncio
async def test_init_non_interactive_profile_missing_credentials_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test non-interactive mode with missing credentials in table output mode."""
    # Mock ConfigManager.initialize to raise ClickException
    # (simulating missing credentials)
    mock_initialize = AsyncMock(
        side_effect=click.ClickException(
            "Profile 'test-profile' exists but credentials not found in keychain. "
            "Please run 'workato init' interactively or set WORKATO_API_TOKEN "
            "environment variable."
        )
    )
    monkeypatch.setattr(
        init_module.ConfigManager,
        "initialize",
        mock_initialize,
    )

    output = StringIO()
    monkeypatch.setattr(init_module.click, "echo", lambda msg: output.write(msg))

    # Mock get_current_context to return output_mode
    mock_ctx = Mock()
    mock_ctx.params = {"output_mode": "table"}
    monkeypatch.setattr(
        init_module.click,
        "get_current_context",
        lambda silent=True: mock_ctx,
    )

    assert init_module.init.callback
    with pytest.raises(SystemExit) as exc_info:
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name=None,
            project_id=123,
            non_interactive=True,
            output_mode="table",
        )

    assert exc_info.value.code == 1
    # Verify error message was shown
    output_text = output.getvalue()
    assert "credentials not found" in output_text
    assert "test-profile" in output_text


@pytest.mark.asyncio
async def test_init_non_interactive_profile_with_valid_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test non-interactive mode with valid credentials proceeds normally."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="test-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=None,
        ),
        patch.object(
            mock_config_manager,
            "validate_environment_config",
            return_value=(True, []),
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)

        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda *args, **kwargs: None)

        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token=None,
            api_url=None,
            project_name=None,
            project_id=123,
            non_interactive=True,
            output_mode="table",
        )

        # Should proceed without error
        mock_pull.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_non_interactive_new_profile_with_region_and_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test non-interactive mode creating new profile with region and token.

    This test verifies that credential validation is skipped when creating
    a new profile with both region and token provided.
    """
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager,
            "load_config",
            return_value=Mock(profile="new-profile"),
        ),
        patch.object(
            mock_config_manager,
            "get_project_directory",
            return_value=None,
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("new-token", "https://api.workato.com"),
        ),
        patch.object(workato_context, "__aenter__", return_value=mock_workato_client),
        patch.object(workato_context, "__aexit__", return_value=False),
    ):
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)

        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
        monkeypatch.setattr(init_module, "Configuration", lambda **_: Mock())

        monkeypatch.setattr(init_module.click, "echo", lambda *args, **kwargs: None)

        # Should not call validate_environment_config when creating new profile
        # (region and api_token are both provided)
        assert init_module.init.callback
        await init_module.init.callback(
            profile="new-profile",
            region="us",
            api_token="new-token",
            api_url=None,
            project_name=None,
            project_id=123,
            non_interactive=True,
            output_mode="table",
        )

        # Should proceed without error and not check credentials
        mock_pull.assert_awaited_once()
