"""Tests for the init command."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from workato_platform.cli.commands import init as init_module


@pytest.mark.asyncio
async def test_init_runs_pull(monkeypatch):
    mock_config_manager = Mock()
    mock_config_manager.load_config.return_value = SimpleNamespace(
        profile="default",
    )
    mock_config_manager.profile_manager.resolve_environment_variables.return_value = (
        "token",
        "https://api.workato.com",
    )

    monkeypatch.setattr(
        init_module.ConfigManager,
        "initialize",
        AsyncMock(return_value=mock_config_manager),
    )

    mock_pull = AsyncMock()
    monkeypatch.setattr(init_module, "_pull_project", mock_pull)

    mock_workato_client = Mock()
    workato_context = AsyncMock()
    workato_context.__aenter__.return_value = mock_workato_client
    workato_context.__aexit__.return_value = False
    monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)
    monkeypatch.setattr(init_module, "Configuration", lambda **_: SimpleNamespace())

    monkeypatch.setattr(init_module.click, "echo", lambda _="": None)

    await init_module.init.callback()

    init_module.ConfigManager.initialize.assert_awaited_once()
    mock_pull.assert_awaited_once()
