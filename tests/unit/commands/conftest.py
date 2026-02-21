"""Shared test fixtures for command tests."""

from collections.abc import Callable
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def mock_init_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., dict[str, Mock | AsyncMock]]:
    """Setup common init command dependencies and mocks.

    Returns a factory that creates and patches all common init test dependencies.

    Usage:
        mocks = mock_init_dependencies(profile="test-profile", token="test-token")
        # mocks contains: initialize_mock, pull_mock
    """

    def _factory(
        profile: str = "default",
        token: str = "test-token",  # noqa: S107
    ) -> dict[str, Mock | AsyncMock]:
        from workato_platform_cli.cli.commands import init as init_module

        # Create mocks
        mock_config_manager = Mock()
        mock_workato_client = Mock()
        workato_context = AsyncMock()

        # Setup config manager defaults
        mock_config_manager.load_config.return_value = Mock(profile=profile)
        mock_config_manager.get_project_directory.return_value = None
        resolve_env = mock_config_manager.profile_manager.resolve_environment_variables
        resolve_env.return_value = (token, "https://api.workato.com")

        # Setup Workato context
        workato_context.__aenter__.return_value = mock_workato_client
        workato_context.__aexit__.return_value = False

        # Create and patch initialize mock
        mock_initialize = AsyncMock(return_value=mock_config_manager)
        monkeypatch.setattr(
            init_module.ConfigManager,
            "initialize",
            mock_initialize,
        )

        # Create and patch pull mock
        mock_pull = AsyncMock()
        monkeypatch.setattr(init_module, "_pull_project", mock_pull)

        # Patch Workato (Configuration doesn't need mocking)
        monkeypatch.setattr(init_module, "Workato", lambda **_: workato_context)

        # Silence click.echo
        monkeypatch.setattr(init_module.click, "echo", lambda _="": None)

        return {
            "initialize_mock": mock_initialize,
            "pull_mock": mock_pull,
        }

    return _factory
