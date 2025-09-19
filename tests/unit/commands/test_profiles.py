"""Focused tests for the profiles command module."""

from collections.abc import Callable
from unittest.mock import Mock

import pytest

from workato_platform.cli.commands.profiles import (
    delete,
    list_profiles,
    show,
    status,
    use,
)
from workato_platform.cli.utils.config import ConfigData, ProfileData


@pytest.fixture
def profile_data_factory():
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
        for name, value in profile_methods.items():
            setattr(profile_manager, name, value)

        config_manager = Mock()
        config_manager.profile_manager = profile_manager
        # Provide deterministic config data unless overridden in tests
        config_manager.load_config.return_value = ConfigData()
        return config_manager

    return _factory


@pytest.mark.asyncio
async def test_list_profiles_displays_profile_details(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory,
    make_config_manager,
) -> None:
    profiles_dict = {
        "default": profile_data_factory(workspace_id=111),
        "dev": profile_data_factory(region="eu", region_url="https://app.eu.workato.com", workspace_id=222),
    }

    config_manager = make_config_manager(
        list_profiles=Mock(return_value=profiles_dict),
        get_current_profile_name=Mock(return_value="default"),
    )

    await list_profiles.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Available profiles" in output
    assert "• default (current)" in output
    assert "Region: US Data Center (us)" in output
    assert "Workspace ID: 222" in output


@pytest.mark.asyncio
async def test_list_profiles_handles_empty_state(
    capsys: pytest.CaptureFixture[str],
    make_config_manager,
) -> None:
    config_manager = make_config_manager(
        list_profiles=Mock(return_value={}),
        get_current_profile_name=Mock(return_value=None),
    )

    await list_profiles.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "No profiles configured" in output
    assert "Run 'workato init'" in output


@pytest.mark.asyncio
async def test_use_sets_current_profile(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory,
    make_config_manager,
) -> None:
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        set_current_profile=Mock(),
    )

    await use.callback(profile_name="dev", config_manager=config_manager)

    config_manager.profile_manager.set_current_profile.assert_called_once_with("dev")
    assert "Set 'dev' as current profile" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_use_missing_profile_shows_hint(
    capsys: pytest.CaptureFixture[str],
    make_config_manager,
) -> None:
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    await use.callback(profile_name="ghost", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'ghost' not found" in output
    assert not config_manager.profile_manager.set_current_profile.called


@pytest.mark.asyncio
async def test_show_displays_profile_and_token_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory,
    make_config_manager,
) -> None:
    monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(return_value="default"),
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )

    await show.callback(profile_name="default", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile: default" in output
    assert "Token configured" in output
    assert "Source: ~/.workato/credentials" in output


@pytest.mark.asyncio
async def test_show_handles_missing_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager,
) -> None:
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    await show.callback(profile_name="missing", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'missing' not found" in output


@pytest.mark.asyncio
async def test_status_reports_project_override(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory,
    make_config_manager,
) -> None:
    profile = profile_data_factory(workspace_id=789)
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="override"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=("token", profile.region_url)),
    )
    config_manager.load_config.return_value = ConfigData(profile="override")

    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: Project override" in output
    assert "Workspace ID: 789" in output


@pytest.mark.asyncio
async def test_status_handles_missing_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager,
) -> None:
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value=None),
    )

    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "No active profile configured" in output


@pytest.mark.asyncio
async def test_delete_confirms_successful_removal(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory,
    make_config_manager,
) -> None:
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        delete_profile=Mock(return_value=True),
    )

    await delete.callback(profile_name="old", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'old' deleted successfully" in output


@pytest.mark.asyncio
async def test_delete_handles_missing_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager,
) -> None:
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    await delete.callback(profile_name="missing", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Profile 'missing' not found" in output


@pytest.mark.asyncio
async def test_show_displays_env_token_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory,
    make_config_manager,
) -> None:
    """Test show command displays WORKATO_API_TOKEN environment variable source."""
    monkeypatch.setenv("WORKATO_API_TOKEN", "env_token")

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(return_value="default"),
        resolve_environment_variables=Mock(return_value=("env_token", profile.region_url)),
    )

    await show.callback(profile_name="default", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_show_handles_missing_token(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory,
    make_config_manager,
) -> None:
    """Test show command handles missing API token."""
    monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        get_current_profile_name=Mock(return_value="default"),
        resolve_environment_variables=Mock(return_value=(None, profile.region_url)),
    )

    await show.callback(profile_name="default", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Token not found" in output
    assert "Token should be stored in ~/.workato/credentials" in output
    assert "Or set WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_status_displays_env_profile_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory,
    make_config_manager,
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

    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: Environment variable (WORKATO_PROFILE)" in output


@pytest.mark.asyncio
async def test_status_displays_env_token_source(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory,
    make_config_manager,
) -> None:
    """Test status command displays WORKATO_API_TOKEN environment variable source."""
    monkeypatch.setenv("WORKATO_API_TOKEN", "env_token")

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="default"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=("env_token", profile.region_url)),
    )

    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Source: WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_status_handles_missing_token(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_data_factory,
    make_config_manager,
) -> None:
    """Test status command handles missing API token."""
    monkeypatch.delenv("WORKATO_API_TOKEN", raising=False)

    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_current_profile_name=Mock(return_value="default"),
        get_current_profile_data=Mock(return_value=profile),
        resolve_environment_variables=Mock(return_value=(None, profile.region_url)),
    )

    await status.callback(config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Token not found" in output
    assert "Token should be stored in ~/.workato/credentials" in output
    assert "Or set WORKATO_API_TOKEN environment variable" in output


@pytest.mark.asyncio
async def test_delete_handles_failure(
    capsys: pytest.CaptureFixture[str],
    profile_data_factory,
    make_config_manager,
) -> None:
    """Test delete command handles deletion failure."""
    profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=profile),
        delete_profile=Mock(return_value=False),  # Simulate failure
    )

    await delete.callback(profile_name="old", config_manager=config_manager)

    output = capsys.readouterr().out
    assert "Failed to delete profile 'old'" in output


def test_profiles_group_exists() -> None:
    """Test that the profiles group command exists."""
    from workato_platform.cli.commands.profiles import profiles

    # Test that the profiles group function exists and is callable
    assert callable(profiles)

    # Test that it's a click group
    import asyncclick as click
    assert isinstance(profiles, click.Group)
