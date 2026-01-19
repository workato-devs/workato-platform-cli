"""Focused tests for the profiles command module."""

import json

from collections.abc import Callable
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import asyncclick as click
import pytest

from workato_platform_cli.cli.commands.profiles import (
    create,
    delete,
    list_profiles,
    show,
    status,
    use,
)
from workato_platform_cli.cli.utils.config import ConfigData, ProfileData


@pytest.fixture
def profile_data_factory() -> Callable[..., ProfileData]:
    """Create ProfileData instances for test scenarios."""

    def _factory(
        *,
        region: str = "us",
        region_url: str = "https://app.workato.com",
        workspace_id: int = 123,
    ) -> ProfileData:
        return ProfileData(
            region=region,
            region_url=region_url,
            workspace_id=workspace_id,
        )

    return _factory


@pytest.fixture
def make_config_manager() -> Callable[..., Mock]:
    """Factory for building config manager stubs with attached profile manager."""

    def _factory(**profile_methods: Mock) -> Mock:
        profile_manager = Mock()
        config_manager = Mock()
        config_manager.profile_manager = profile_manager
        # Provide deterministic config data unless overridden in tests
        config_manager.load_config.return_value = ConfigData()

        config_methods = {
            "load_config",
            "save_config",
            "get_workspace_root",
            "get_project_directory",
        }

        for name, value in profile_methods.items():
            if name in config_methods:
                setattr(config_manager, name, value)
            else:
                setattr(profile_manager, name, value)

        return config_manager

    return _factory


@pytest.mark.asyncio
async def test_list_profiles_displays_profile_details(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    profiles_dict = {
        "default": profile_data_factory(workspace_id=111),
        "dev": profile_data_factory(
            region="eu", region_url="https://app.eu.workato.com", workspace_id=222
        ),
    }

    config_manager = make_config_manager(
        list_profiles=Mock(return_value=profiles_dict),
        get_current_profile_name=Mock(return_value="default"),
    )

    assert list_profiles.callback
    await list_profiles.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Available profiles" in output
    assert "• default (current)" in output
    assert "Region: US Data Center (us)" in output
    assert "Workspace ID: 222" in output


@pytest.mark.asyncio
async def test_list_profiles_handles_empty_state(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    config_manager = make_config_manager(
        list_profiles=Mock(return_value={}),
        get_current_profile_name=Mock(return_value=None),
    )

    assert list_profiles.callback
    await list_profiles.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "No profiles configured" in output
    assert "Run 'workato init'" in output


@pytest.mark.asyncio
async def test_use_sets_current_profile(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        set_current_profile=Mock(),
        get_workspace_root=Mock(return_value=Path("/workspace")),
        load_config=Mock(return_value=Mock(project_id=None)),  # No project context
    )

    assert use.callback
    await use.callback(profile_name="dev", config_manager=config_manager)

    config_manager.profile_manager.set_current_profile.assert_called_once_with("dev")
    assert "Set 'dev' as global default profile" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_use_missing_profile_shows_hint(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    assert use.callback
    await use.callback(profile_name="ghost", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'ghost' not found" in output
    assert not config_manager.profile_manager.set_current_profile.called


@pytest.mark.asyncio
async def test_show_displays_profile_and_token_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(return_value="default"),
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )

    assert show.callback
    await show.callback(profile_name="default", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile: default" in output
    assert "Token configured" in output
    assert "Source: ~/.workato/profiles" in output


@pytest.mark.asyncio
async def test_show_handles_missing_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    assert show.callback
    await show.callback(profile_name="missing", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'missing' not found" in output


@pytest.mark.asyncio
async def test_status_reports_project_override(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    profile = profile_data_factory(workspace_id=789)
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="override"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )
    config_manager.load_config.return_value = ConfigData(profile="override")

    assert status.callback
    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: Project override" in output
    assert "Workspace ID: 789" in output


@pytest.mark.asyncio
async def test_status_handles_missing_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value=None),
    )

    assert status.callback
    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "No active profile configured" in output


@pytest.mark.asyncio
async def test_delete_confirms_successful_removal(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        delete_profile=Mock(return_value=True),
    )

    assert delete.callback
    await delete.callback(profile_name="old", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'old' deleted successfully" in output


@pytest.mark.asyncio
async def test_delete_handles_missing_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    assert delete.callback
    await delete.callback(profile_name="missing", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'missing' not found" in output


@pytest.mark.asyncio
async def test_show_displays_env_token_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test show command displays WORKATO_API_TOKEN environment variable source."""
    monkeypatch.setenv("WORKATO_API_TOKEN", "env_token")

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(return_value="default"),
        resolve_environment_variables=Mock(
            return_value=("env_token", profile.region_url)
        ),
    )

    assert show.callback
    await show.callback(profile_name="default", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_show_handles_missing_token(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test show command handles missing API token."""
    monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(return_value="default"),
        resolve_environment_variables=Mock(return_value=(None, profile.region_url)),
    )

    assert show.callback
    await show.callback(profile_name="default", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Token not found" in output
    assert "Token should be stored in keyring" in output
    assert "Or set WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_status_displays_env_profile_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status command displays WORKATO_PROFILE environment variable source."""
    monkeypatch.setenv("WORKATO_PROFILE", "env_profile")

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="env_profile"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )
    # No project profile override
    config_manager.load_config.return_value = ConfigData(profile=None)

    assert status.callback
    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: Environment variable (WORKATO_PROFILE)" in output


@pytest.mark.asyncio
async def test_status_displays_env_token_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status command displays WORKATO_API_TOKEN environment variable source."""
    monkeypatch.setenv("WORKATO_API_TOKEN", "env_token")

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="default"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(
            return_value=("env_token", profile.region_url)
        ),
    )

    assert status.callback
    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_status_handles_missing_token(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status command handles missing API token."""
    monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="default"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=(None, profile.region_url)),
    )

    assert status.callback
    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Token not found" in output
    assert "Token should be stored in keyring" in output
    assert "Or set WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_delete_handles_failure(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test delete command handles deletion failure."""
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        delete_profile=Mock(return_value=False),  # Simulate failure
    )

    assert delete.callback
    await delete.callback(profile_name="old", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Failed to delete profile 'old'" in output


def test_profiles_group_exists() -> None:
    """Test that the profiles group command exists."""
    from workato_platform_cli.cli.commands.profiles import profiles

    # Test that the profiles group function exists and is callable
    assert callable(profiles)

    # Test that it's a click group
    import asyncclick as click

    assert isinstance(profiles, click.Group)


@pytest.mark.asyncio
async def test_use_sets_workspace_profile(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test use command sets workspace profile when in workspace context."""
    profile = profile_data_factory()
    project_config = ConfigData(project_id=123, project_name="test")

    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_workspace_root=Mock(return_value=Path("/workspace")),
        load_config=Mock(return_value=project_config),
        save_config=Mock(),
        get_project_directory=Mock(return_value=Path("/workspace/project")),
    )

    assert use.callback
    await use.callback(profile_name="dev", config_manager=config_manager)

    # Should save config with updated profile
    config_manager.save_config.assert_called()
    saved_config = config_manager.save_config.call_args[0][0]
    assert saved_config.profile == "dev"

    output = capsys.readouterr().out
    assert "Set 'dev' as profile for current workspace" in output


@pytest.mark.asyncio
async def test_use_updates_both_workspace_and_project_configs(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test use command updates both workspace and project configs when different."""
    profile = profile_data_factory()
    project_config = ConfigData(project_id=123, project_name="test")

    # Mock project config manager
    project_config_manager = Mock()
    project_config_manager.load_config.return_value = Mock(project_id=123)
    project_config_manager.save_config = Mock()

    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_workspace_root=Mock(return_value=Path("/workspace")),
        load_config=Mock(return_value=project_config),
        save_config=Mock(),
        get_project_directory=Mock(return_value=Path("/workspace/project")),
    )

    # Mock ConfigManager constructor for project config
    with patch(
        "workato_platform_cli.cli.commands.profiles.ConfigManager",
        return_value=project_config_manager,
    ):
        assert use.callback
        await use.callback(profile_name="dev", config_manager=config_manager)

    # Should update both configs
    config_manager.save_config.assert_called()
    project_config_manager.save_config.assert_called()

    output = capsys.readouterr().out
    assert "Project config also updated" in output


@pytest.mark.asyncio
async def test_status_displays_global_setting_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status command displays global setting source."""
    monkeypatch.delenv("WORKATO_PROFILE", raising=False)

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="global"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )
    # No project profile override and no env var
    config_manager.load_config.return_value = ConfigData(profile=None)

    assert status.callback
    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: Global setting (~/.workato/profiles)" in output


@pytest.mark.asyncio
async def test_show_handles_different_profile_name_resolution(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test show command when showing different profile than current."""
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(
            return_value="current"
        ),  # Different from shown profile
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )

    assert show.callback
    await show.callback(profile_name="other", config_manager=config_manager)

    # Should call resolve_environment_variables with the shown profile name
    config_manager.profile_manager.resolve_environment_variables.assert_called_with(
        "other"
    )


@pytest.mark.asyncio
async def test_use_handles_exception_gracefully(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test use command handles exceptions gracefully and falls back to global."""
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        set_current_profile=Mock(),
        get_workspace_root=Mock(side_effect=RuntimeError("Workspace error")),
    )

    assert use.callback
    await use.callback(profile_name="dev", config_manager=config_manager)

    # Should fall back to global profile setting
    config_manager.profile_manager.set_current_profile.assert_called_once_with("dev")
    assert "Set 'dev' as global default profile" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_use_workspace_context_same_directory(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test use command when workspace and project are the same directory."""
    profile = profile_data_factory()
    project_config = ConfigData(project_id=123, project_name="test")

    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_workspace_root=Mock(return_value=Path("/workspace")),
        load_config=Mock(return_value=project_config),
        save_config=Mock(),
        get_project_directory=Mock(
            return_value=Path("/workspace")
        ),  # Same as workspace
    )

    assert use.callback
    await use.callback(profile_name="dev", config_manager=config_manager)

    # Should update workspace config but not create separate project config
    config_manager.save_config.assert_called()
    output = capsys.readouterr().out
    assert "Set 'dev' as profile for current workspace" in output
    # Should NOT show "Project config also updated" since directories are the same


@pytest.mark.asyncio
async def test_status_shows_current_profile_indicator(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status command shows current profile indicator."""
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="dev"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )
    config_manager.load_config.return_value = ConfigData(profile=None)

    assert status.callback
    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Current Profile: dev" in output


@pytest.mark.asyncio
async def test_show_handles_current_profile_check(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test show command checks if profile is current."""
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(return_value="dev"),  # Same as shown profile
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )

    assert show.callback
    await show.callback(profile_name="dev", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "This is the current active profile" in output


@pytest.mark.asyncio
async def test_list_profiles_json_output_mode(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test list_profiles with JSON output mode."""
    profiles_dict = {
        "dev": profile_data_factory(
            region="us", region_url="https://www.workato.com", workspace_id=123
        ),
        "prod": profile_data_factory(
            region="eu", region_url="https://app.eu.workato.com", workspace_id=456
        ),
    }

    config_manager = make_config_manager(
        list_profiles=Mock(return_value=profiles_dict),
        get_current_profile_name=Mock(return_value="dev"),
    )

    assert list_profiles.callback
    await list_profiles.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out

    # Parse JSON output
    parsed = json.loads(output)

    assert parsed["current_profile"] == "dev"
    assert "dev" in parsed["profiles"]
    assert "prod" in parsed["profiles"]
    assert parsed["profiles"]["dev"]["is_current"] is True
    assert parsed["profiles"]["prod"]["is_current"] is False
    assert parsed["profiles"]["dev"]["region"] == "us"
    assert parsed["profiles"]["prod"]["region"] == "eu"


@pytest.mark.asyncio
async def test_list_profiles_json_output_mode_empty(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test list_profiles JSON output with no profiles."""
    config_manager = make_config_manager(
        list_profiles=Mock(return_value={}),
        get_current_profile_name=Mock(return_value=None),
    )

    assert list_profiles.callback
    await list_profiles.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out

    # Parse JSON output
    parsed = json.loads(output)

    assert parsed["current_profile"] is None
    assert parsed["profiles"] == {}


@pytest.mark.asyncio
async def test_status_json_no_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status JSON output when no profile is configured."""
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value=None),
    )

    assert status.callback
    await status.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert parsed["profile"] is None
    assert parsed["error"] == "No active profile configured"


@pytest.mark.asyncio
async def test_status_json_with_project_override(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    tmp_path: Path,
) -> None:
    """Test status JSON output with project override."""
    config_manager = make_config_manager(
        load_config=Mock(
            return_value=Mock(
                profile="dev-profile",
                project_id=123,
                project_name="Test Project",
                folder_id=456,
            )
        ),
        get_current_profile_name=Mock(return_value="dev-profile"),
        get_current_profile_data=Mock(
            return_value=Mock(
                region="us",
                region_name="US Data Center",
                region_url="https://www.workato.com",
                workspace_id=789,
            )
        ),
        resolve_environment_variables=Mock(
            return_value=("test-token", "https://www.workato.com")
        ),
        get_workspace_root=Mock(return_value=tmp_path),
        get_project_directory=Mock(return_value=tmp_path / "project"),
    )

    assert status.callback
    await status.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert parsed["profile"]["name"] == "dev-profile"
    assert parsed["profile"]["source"]["type"] == "project_override"
    assert parsed["profile"]["source"]["location"] == ".workatoenv"
    assert parsed["profile"]["configuration"]["region"]["code"] == "us"
    assert parsed["profile"]["configuration"]["workspace_id"] == 789
    assert parsed["authentication"]["configured"] is True
    assert parsed["authentication"]["source"]["type"] == "keyring"
    assert parsed["project"]["configured"] is True
    assert "Test Project" in str(parsed["project"]["metadata"]["name"])


@pytest.mark.asyncio
async def test_status_json_with_env_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test status JSON output with environment variable profile."""
    monkeypatch.setenv("WORKATO_PROFILE", "env-profile")

    config_manager = make_config_manager(
        load_config=Mock(return_value=Mock(profile=None)),
        get_current_profile_name=Mock(return_value="env-profile"),
        get_current_profile_data=Mock(
            return_value=Mock(
                region="us",
                region_name="US Data Center",
                region_url="https://www.workato.com",
                workspace_id=789,
            )
        ),
        resolve_environment_variables=Mock(
            return_value=("test-token", "https://www.workato.com")
        ),
        get_workspace_root=Mock(return_value=None),
        get_project_directory=Mock(return_value=None),
    )

    assert status.callback
    await status.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert parsed["profile"]["name"] == "env-profile"
    assert parsed["profile"]["source"]["type"] == "environment_variable"
    assert parsed["profile"]["source"]["location"] == "WORKATO_PROFILE"
    assert parsed["project"]["configured"] is False


@pytest.mark.asyncio
async def test_status_json_with_env_token(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test status JSON output with environment variable token."""
    monkeypatch.setenv("WORKATO_API_TOKEN", "env-token")

    config_manager = make_config_manager(
        load_config=Mock(return_value=Mock(profile=None)),
        get_current_profile_name=Mock(return_value="default-profile"),
        get_current_profile_data=Mock(
            return_value=Mock(
                region="us",
                region_name="US Data Center",
                region_url="https://www.workato.com",
                workspace_id=789,
            )
        ),
        resolve_environment_variables=Mock(
            return_value=("env-token", "https://www.workato.com")
        ),
        get_workspace_root=Mock(return_value=None),
        get_project_directory=Mock(return_value=None),
    )

    assert status.callback
    await status.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert parsed["authentication"]["configured"] is True
    assert parsed["authentication"]["source"]["type"] == "environment_variable"
    assert parsed["authentication"]["source"]["location"] == "WORKATO_API_TOKEN"


@pytest.mark.asyncio
async def test_status_json_no_token(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status JSON output with no authentication token."""
    config_manager = make_config_manager(
        load_config=Mock(return_value=Mock(profile=None)),
        get_current_profile_name=Mock(return_value="default-profile"),
        get_current_profile_data=Mock(
            return_value=Mock(
                region="us",
                region_name="US Data Center",
                region_url="https://www.workato.com",
                workspace_id=789,
            )
        ),
        resolve_environment_variables=Mock(
            return_value=(None, "https://www.workato.com")
        ),
        get_workspace_root=Mock(return_value=None),
        get_project_directory=Mock(return_value=None),
    )

    assert status.callback
    await status.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert parsed["authentication"]["configured"] is False


@pytest.mark.asyncio
async def test_status_json_project_path_none(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    tmp_path: Path,
) -> None:
    """Test status JSON output when project path doesn't exist."""
    config_manager = make_config_manager(
        load_config=Mock(
            return_value=Mock(
                profile=None,
                project_id=123,
                project_name="Test Project",
                folder_id=456,
            )
        ),
        get_current_profile_name=Mock(return_value="default-profile"),
        get_current_profile_data=Mock(
            return_value=Mock(
                region="us",
                region_name="US Data Center",
                region_url="https://www.workato.com",
                workspace_id=789,
            )
        ),
        resolve_environment_variables=Mock(
            return_value=("test-token", "https://www.workato.com")
        ),
        get_workspace_root=Mock(return_value=tmp_path),
        get_project_directory=Mock(return_value=None),
    )

    assert status.callback
    await status.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert parsed["project"]["configured"] is False


@pytest.mark.asyncio
async def test_status_json_exception_handling(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test status JSON output handles exceptions gracefully."""
    config_manager = make_config_manager(
        load_config=Mock(return_value=Mock(profile=None)),
        get_current_profile_name=Mock(return_value="default-profile"),
        get_current_profile_data=Mock(
            return_value=Mock(
                region="us",
                region_name="US Data Center",
                region_url="https://www.workato.com",
                workspace_id=789,
            )
        ),
        resolve_environment_variables=Mock(
            return_value=("test-token", "https://www.workato.com")
        ),
        get_workspace_root=Mock(side_effect=Exception("Test exception")),
    )

    assert status.callback
    await status.callback(output_mode="json", config_manager=config_manager)

    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert parsed["project"]["configured"] is False


@pytest.mark.asyncio
async def test_create_profile_success(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    profile_data_factory: Callable[..., ProfileData],
) -> None:
    """Test successful profile creation."""
    # Mock profile data returned from create_profile_interactive
    profile_data = profile_data_factory(
        region="us",
        region_url="https://www.workato.com",
        workspace_id=123,
    )

    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),  # Profile doesn't exist yet
        set_profile=Mock(),
        set_current_profile=Mock(),
    )

    # Mock the create_profile_interactive method
    config_manager.profile_manager.create_profile_interactive = AsyncMock(
        return_value=(profile_data, "test_token")
    )

    assert create.callback
    await create.callback(profile_name="new_profile", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "✅ Profile 'new_profile' created successfully" in output
    assert "✅ Set 'new_profile' as the active profile" in output

    # Verify profile was set and made current
    config_manager.profile_manager.set_profile.assert_called_once()
    config_manager.profile_manager.set_current_profile.assert_called_once_with(
        "new_profile"
    )


@pytest.mark.asyncio
async def test_create_profile_already_exists(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test creating a profile that already exists."""
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),  # Profile already exists
    )

    assert create.callback
    await create.callback(profile_name="existing", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "❌ Profile 'existing' already exists" in output
    assert "Use 'workato profiles use' to switch to it" in output


@pytest.mark.asyncio
async def test_create_profile_cancelled_region_selection(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test profile creation when region selection is cancelled."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    # Mock create_profile_interactive to raise ClickException (cancelled)
    config_manager.profile_manager.create_profile_interactive = AsyncMock(
        side_effect=click.ClickException("Setup cancelled")
    )

    assert create.callback
    await create.callback(profile_name="new_profile", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "❌ Profile creation cancelled" in output


@pytest.mark.asyncio
async def test_create_profile_empty_token(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test profile creation with empty token."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    # Mock create_profile_interactive to raise ClickException (empty token)
    config_manager.profile_manager.create_profile_interactive = AsyncMock(
        side_effect=click.ClickException("API token cannot be empty")
    )

    assert create.callback
    await create.callback(profile_name="new_profile", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "❌ Profile creation cancelled" in output


@pytest.mark.asyncio
async def test_create_profile_authentication_failure(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test profile creation when authentication fails."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    # Mock create_profile_interactive to raise ClickException (auth failed)
    config_manager.profile_manager.create_profile_interactive = AsyncMock(
        side_effect=click.ClickException("Authentication failed: Invalid credentials")
    )

    assert create.callback
    await create.callback(profile_name="new_profile", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "❌ Profile creation cancelled" in output


@pytest.mark.asyncio
async def test_create_profile_keyring_failure(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    profile_data_factory: Callable[..., ProfileData],
) -> None:
    """Test profile creation when keyring storage fails."""
    # Mock profile data returned from create_profile_interactive
    profile_data = profile_data_factory(
        region="us",
        region_url="https://www.workato.com",
        workspace_id=123,
    )

    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
        set_profile=Mock(side_effect=ValueError("Failed to store token in keyring")),
    )

    # Mock create_profile_interactive to succeed, but set_profile will fail
    config_manager.profile_manager.create_profile_interactive = AsyncMock(
        return_value=(profile_data, "test_token")
    )

    assert create.callback
    await create.callback(profile_name="new_profile", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "❌ Failed to save profile:" in output
    assert "Failed to store token in keyring" in output
