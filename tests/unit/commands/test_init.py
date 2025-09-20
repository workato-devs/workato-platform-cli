"""Tests for the init command."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from workato_platform.cli.commands import init as init_module


@pytest.mark.asyncio
async def test_init_runs_pull(monkeypatch: pytest.MonkeyPatch) -> None:
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

        mock_initialize.assert_awaited_once()
        mock_pull.assert_awaited_once()
