"""Focused tests for the profiles command module."""

import json

from collections.abc import Callable
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import asyncclick as click
import pytest

from workato_platform_cli.cli.commands import profiles as profiles_module
from workato_platform_cli.cli.commands.profiles import (
    create,
    delete,
    list_profiles,
    rename,
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


def _make_workatoenv_updater(tmp_path: Path) -> Callable[[str, str], list[Path]]:
    """Create a mock _update_workatoenv_files function for testing.

    Returns a function that searches tmp_path instead of home directory.
    """

    def mock_update(old_name: str, new_name: str) -> list[Path]:
        updated_files = []
        for workatoenv_file in tmp_path.rglob(".workatoenv"):
            try:
                with open(workatoenv_file, "r+") as f:
                    data = json.load(f)
                    if data.get("profile") == old_name:
                        data["profile"] = new_name
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=2)
                        f.write("\n")
                        updated_files.append(workatoenv_file)
            except (OSError, json.JSONDecodeError):
                continue
        return updated_files

    return mock_update


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


@pytest.mark.asyncio
async def test_create_profile_non_interactive(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test successful non-interactive profile creation."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),  # Profile doesn't exist yet
        set_profile=Mock(),
        set_current_profile=Mock(),
    )

    # Mock Workato API client
    mock_client = AsyncMock()
    mock_user = Mock()
    mock_user.id = 123
    mock_client.users_api.get_workspace_details = AsyncMock(return_value=mock_user)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "workato_platform_cli.cli.commands.profiles.Workato",
        return_value=mock_client,
    ):
        assert create.callback
        await create.callback(
            profile_name="test_profile",
            region="us",
            api_token="test_token",
            api_url=None,
            non_interactive=True,
            config_manager=config_manager,
        )

    output = capsys.readouterr().out
    assert "✅ Profile 'test_profile' created successfully" in output
    assert "✅ Set 'test_profile' as the active profile" in output

    # Verify profile was set and made current
    config_manager.profile_manager.set_profile.assert_called_once()
    config_manager.profile_manager.set_current_profile.assert_called_once_with(
        "test_profile"
    )


@pytest.mark.asyncio
async def test_rename_profile_success(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test successful profile rename."""
    old_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(
            side_effect=lambda name: old_profile if name == "old" else None
        ),
        _get_token_from_keyring=Mock(return_value="test_token"),
        set_profile=Mock(),
        get_current_profile_name=Mock(return_value="other"),  # Not renaming current
        delete_profile=Mock(),
    )

    assert rename.callback
    with patch("asyncclick.confirm", return_value=True):
        await rename.callback(
            old_name="old", new_name="new", config_manager=config_manager
        )

    output = capsys.readouterr().out
    assert "✅ Profile renamed successfully" in output

    # Verify profile was created with new name and old profile deleted
    config_manager.profile_manager.set_profile.assert_called_once_with(
        "new", old_profile, "test_token"
    )
    config_manager.profile_manager.delete_profile.assert_called_once_with("old")


@pytest.mark.asyncio
async def test_rename_current_profile(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test renaming the current profile updates current profile setting."""
    old_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(
            side_effect=lambda name: old_profile if name == "old" else None
        ),
        _get_token_from_keyring=Mock(return_value="test_token"),
        set_profile=Mock(),
        get_current_profile_name=Mock(return_value="old"),  # Renaming current profile
        set_current_profile=Mock(),
        delete_profile=Mock(),
    )

    assert rename.callback
    with patch("asyncclick.confirm", return_value=True):
        await rename.callback(
            old_name="old", new_name="new", config_manager=config_manager
        )

    output = capsys.readouterr().out
    assert "✅ Profile renamed successfully" in output
    assert "✅ Set 'new' as the active profile" in output

    # Verify current profile was updated
    config_manager.profile_manager.set_current_profile.assert_called_once_with("new")


@pytest.mark.asyncio
async def test_rename_profile_not_found(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test renaming a profile that doesn't exist."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),  # Profile doesn't exist
    )

    assert rename.callback
    await rename.callback(
        old_name="missing", new_name="new", config_manager=config_manager
    )

    output = capsys.readouterr().out
    assert "❌ Profile 'missing' not found" in output
    assert "Use 'workato profiles list'" in output


@pytest.mark.asyncio
async def test_rename_profile_new_name_exists(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test renaming to a profile name that already exists."""
    old_profile = profile_data_factory()
    new_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(
            side_effect=lambda name: old_profile if name == "old" else new_profile
        ),
    )

    assert rename.callback
    await rename.callback(
        old_name="old", new_name="existing", config_manager=config_manager
    )

    output = capsys.readouterr().out
    assert "❌ Profile 'existing' already exists" in output
    assert "Choose a different name" in output


@pytest.mark.asyncio
async def test_rename_profile_cancelled(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test cancelling profile rename."""
    old_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(
            side_effect=lambda name: old_profile if name == "old" else None
        ),
        set_profile=Mock(),
        delete_profile=Mock(),
    )

    assert rename.callback
    with patch("asyncclick.confirm", return_value=False):  # User cancels
        await rename.callback(
            old_name="old", new_name="new", config_manager=config_manager
        )

    output = capsys.readouterr().out
    assert "❌ Rename cancelled" in output

    # Verify profile was not modified
    config_manager.profile_manager.set_profile.assert_not_called()
    config_manager.profile_manager.delete_profile.assert_not_called()


@pytest.mark.asyncio
async def test_rename_profile_set_profile_failure(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test handling of set_profile failure during rename."""
    old_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(
            side_effect=lambda name: old_profile if name == "old" else None
        ),
        _get_token_from_keyring=Mock(return_value="test_token"),
        set_profile=Mock(side_effect=ValueError("Keyring error")),
    )

    assert rename.callback
    with patch("asyncclick.confirm", return_value=True):
        await rename.callback(
            old_name="old", new_name="new", config_manager=config_manager
        )

    output = capsys.readouterr().out
    assert "❌ Failed to create new profile:" in output
    assert "Keyring error" in output


@pytest.mark.asyncio
async def test_rename_profile_updates_workatoenv_files(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
    tmp_path: Path,
) -> None:
    """Test that rename updates .workatoenv files that reference the old profile."""
    old_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(
            side_effect=lambda name: old_profile if name == "old" else None
        ),
        _get_token_from_keyring=Mock(return_value="test_token"),
        set_profile=Mock(),
        get_current_profile_name=Mock(return_value="other"),
        delete_profile=Mock(),
    )

    # Create test .workatoenv files
    project1 = tmp_path / "project1"
    project1.mkdir()
    workatoenv1 = project1 / ".workatoenv"
    workatoenv1.write_text(
        json.dumps(
            {
                "project_id": 123,
                "project_name": "Project 1",
                "folder_id": 456,
                "profile": "old",
            }
        )
    )

    project2 = tmp_path / "project2"
    project2.mkdir()
    workatoenv2 = project2 / ".workatoenv"
    workatoenv2.write_text(
        json.dumps(
            {
                "project_id": 789,
                "project_name": "Project 2",
                "folder_id": 101,
                "profile": "other",  # Different profile - should not be updated
            }
        )
    )

    # Mock _update_workatoenv_files to only search in tmp_path
    mock_update = _make_workatoenv_updater(tmp_path)

    with patch.object(
        profiles_module, "_update_workatoenv_files", side_effect=mock_update
    ):
        assert rename.callback
        with patch("asyncclick.confirm", return_value=True):
            await rename.callback(
                old_name="old", new_name="new", config_manager=config_manager
            )

    # Verify workatoenv1 was updated
    with open(workatoenv1) as f:
        data1 = json.load(f)
    assert data1["profile"] == "new"

    # Verify workatoenv2 was NOT updated
    with open(workatoenv2) as f:
        data2 = json.load(f)
    assert data2["profile"] == "other"

    output = capsys.readouterr().out
    assert "✅ Updated 1 project configuration(s)" in output


@pytest.mark.asyncio
async def test_rename_profile_skips_malformed_workatoenv_files(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory: Callable[..., ProfileData],
    make_config_manager: Callable[..., Mock],
    tmp_path: Path,
) -> None:
    """Test that rename skips malformed .workatoenv files."""
    old_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(
            side_effect=lambda name: old_profile if name == "old" else None
        ),
        _get_token_from_keyring=Mock(return_value="test_token"),
        set_profile=Mock(),
        get_current_profile_name=Mock(return_value="other"),
        delete_profile=Mock(),
    )

    # Create malformed .workatoenv file
    project1 = tmp_path / "project1"
    project1.mkdir()
    workatoenv1 = project1 / ".workatoenv"
    workatoenv1.write_text("invalid json {")

    # Create valid .workatoenv file
    project2 = tmp_path / "project2"
    project2.mkdir()
    workatoenv2 = project2 / ".workatoenv"
    workatoenv2.write_text(
        json.dumps(
            {
                "project_id": 789,
                "project_name": "Project 2",
                "folder_id": 101,
                "profile": "old",
            }
        )
    )

    mock_update = _make_workatoenv_updater(tmp_path)

    with patch.object(
        profiles_module, "_update_workatoenv_files", side_effect=mock_update
    ):
        assert rename.callback
        with patch("asyncclick.confirm", return_value=True):
            await rename.callback(
                old_name="old", new_name="new", config_manager=config_manager
            )

    # Verify valid file was updated
    with open(workatoenv2) as f:
        data2 = json.load(f)
    assert data2["profile"] == "new"

    # Verify malformed file was skipped (still invalid)
    assert workatoenv1.read_text() == "invalid json {"

    output = capsys.readouterr().out
    assert "✅ Updated 1 project configuration(s)" in output
