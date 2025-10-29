"""Tests for the workspace command."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from workato_platform_cli.cli.commands.workspace import workspace
from workato_platform_cli.cli.utils.config import ConfigData, ProfileData


@pytest.mark.asyncio
async def test_workspace_command_outputs(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_config_manager = Mock()
    profile_data = ProfileData(
        region="us",
        region_url="https://app.workato.com",
        workspace_id=123,
    )
    config_data = ConfigData(
        project_id=42,
        project_name="Demo Project",
        folder_id=888,
        profile="default",
    )
    # load_config is called twice in the command

    user_info = Mock(
        name="Test User",
        email="user@example.com",
        id=321,
        plan_id="enterprise",
        recipes_count=10,
        active_recipes_count=5,
        last_seen="2024-01-01",
    )

    mock_client = Mock()

    captured: list[str] = []

    def fake_echo(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.workspace.click.echo",
        fake_echo,
    )

    with (
        patch.object(
            mock_config_manager, "load_config", side_effect=[config_data, config_data]
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "get_current_profile_data",
            return_value=profile_data,
        ),
        patch.object(
            mock_config_manager.profile_manager,
            "get_current_profile_name",
            return_value="default",
        ),
        patch.object(
            mock_client.users_api,
            "get_workspace_details",
            AsyncMock(return_value=user_info),
        ),
    ):
        assert workspace.callback
        await workspace.callback(
            config_manager=mock_config_manager,
            workato_api_client=mock_client,
        )

        joined_output = "\n".join(captured)
        assert "Test User" in joined_output
        assert "Demo Project" in joined_output
        assert "Region" in joined_output
