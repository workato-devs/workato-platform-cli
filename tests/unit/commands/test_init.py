"""Tests for the init command."""

from unittest.mock import AsyncMock, Mock, patch

import asyncclick as click
import pytest

from workato_platform.cli.commands import init as init_module


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
            mock_config_manager, "load_config", return_value=Mock(profile="test-profile")
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

        # Test non-interactive mode with all parameters
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region="us",
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )

        # Should call initialize with provided parameters
        mock_initialize.assert_awaited_once_with(
            profile_name="test-profile",
            region="us",
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
        )
        mock_pull.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_non_interactive_custom_region(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test non-interactive mode with custom region and API URL."""
    mock_config_manager = Mock()
    mock_workato_client = Mock()
    workato_context = AsyncMock()

    with (
        patch.object(
            mock_config_manager, "load_config", return_value=Mock(profile="test-profile")
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
        )


@pytest.mark.asyncio
async def test_init_non_interactive_missing_profile() -> None:
    """Test non-interactive mode fails when profile is missing."""
    with pytest.raises(click.Abort):
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


@pytest.mark.asyncio
async def test_init_non_interactive_missing_region() -> None:
    """Test non-interactive mode fails when region is missing."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
            region=None,
            api_token="test-token",
            api_url=None,
            project_name="test-project",
            project_id=None,
            non_interactive=True,
        )


@pytest.mark.asyncio
async def test_init_non_interactive_missing_api_token() -> None:
    """Test non-interactive mode fails when API token is missing."""
    with pytest.raises(click.Abort):
        assert init_module.init.callback
        await init_module.init.callback(
            profile="test-profile",
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
