"""Tests for profiles create command --non-interactive mode."""

from collections.abc import Callable
from unittest.mock import AsyncMock, Mock, patch

import pytest

from workato_platform_cli.cli.commands.profiles import create
from workato_platform_cli.cli.utils.config import ProfileData


@pytest.fixture
def mock_workato_client() -> AsyncMock:
    """Create a mock Workato API client."""
    client = AsyncMock()
    # Mock the user object with just the id attribute
    mock_user = Mock()
    mock_user.id = 123
    client.users_api.get_workspace_details = AsyncMock(return_value=mock_user)
    # Mock the async context manager
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.fixture
def profile_data_factory() -> Callable[..., ProfileData]:
    """Create ProfileData instances for test scenarios."""

    def _factory(
        *,
        region: str = "us",
        region_url: str = "https://www.workato.com",
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
    """Factory for building config manager stubs."""

    def _factory(**profile_methods: Mock) -> Mock:
        profile_manager = Mock()
        config_manager = Mock()
        config_manager.profile_manager = profile_manager

        for name, value in profile_methods.items():
            setattr(profile_manager, name, value)

        return config_manager

    return _factory


@pytest.mark.asyncio
async def test_create_non_interactive_us_region_success(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    mock_workato_client: AsyncMock,
) -> None:
    """Test successful non-interactive profile creation for US region."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
        set_profile=Mock(),
        set_current_profile=Mock(),
    )

    with patch(
        "workato_platform_cli.cli.commands.profiles.Workato",
        return_value=mock_workato_client,
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

    # Verify profile was set with correct data
    config_manager.profile_manager.set_profile.assert_called_once()
    call_args = config_manager.profile_manager.set_profile.call_args
    assert call_args[0][0] == "test_profile"
    profile_data = call_args[0][1]
    assert profile_data.region == "us"
    assert profile_data.region_url == "https://www.workato.com"
    assert profile_data.workspace_id == 123

    # Verify token was passed
    assert call_args[0][2] == "test_token"


@pytest.mark.asyncio
async def test_create_non_interactive_custom_region_success(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    mock_workato_client: AsyncMock,
) -> None:
    """Test successful non-interactive profile creation for custom region."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
        set_profile=Mock(),
        set_current_profile=Mock(),
    )

    with patch(
        "workato_platform_cli.cli.commands.profiles.Workato",
        return_value=mock_workato_client,
    ):
        assert create.callback
        await create.callback(
            profile_name="custom_profile",
            region="custom",
            api_token="custom_token",
            api_url="https://custom.workato.com",
            non_interactive=True,
            config_manager=config_manager,
        )

    output = capsys.readouterr().out
    assert "✅ Profile 'custom_profile' created successfully" in output

    # Verify profile was set with custom URL
    call_args = config_manager.profile_manager.set_profile.call_args
    profile_data = call_args[0][1]
    assert profile_data.region == "custom"
    assert profile_data.region_url == "https://custom.workato.com"


@pytest.mark.asyncio
async def test_create_non_interactive_missing_region(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test non-interactive mode fails when --region is missing."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    assert create.callback
    await create.callback(
        profile_name="test_profile",
        region=None,  # Missing region
        api_token="test_token",
        api_url=None,
        non_interactive=True,
        config_manager=config_manager,
    )

    output = capsys.readouterr().out
    assert "❌ --region is required in non-interactive mode" in output

    # Verify profile was not created
    config_manager.profile_manager.set_profile.assert_not_called()


@pytest.mark.asyncio
async def test_create_non_interactive_missing_api_token(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test non-interactive mode fails when --api-token is missing."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    assert create.callback
    await create.callback(
        profile_name="test_profile",
        region="us",
        api_token=None,  # Missing token
        api_url=None,
        non_interactive=True,
        config_manager=config_manager,
    )

    output = capsys.readouterr().out
    assert "❌ --api-token is required in non-interactive mode" in output

    # Verify profile was not created
    config_manager.profile_manager.set_profile.assert_not_called()


@pytest.mark.asyncio
async def test_create_non_interactive_custom_region_missing_api_url(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test non-interactive mode fails when --api-url is missing for custom region."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    assert create.callback
    await create.callback(
        profile_name="test_profile",
        region="custom",
        api_token="test_token",
        api_url=None,  # Missing api_url for custom region
        non_interactive=True,
        config_manager=config_manager,
    )

    output = capsys.readouterr().out
    assert "❌ --api-url is required when region=custom" in output

    # Verify profile was not created
    config_manager.profile_manager.set_profile.assert_not_called()


@pytest.mark.asyncio
async def test_create_non_interactive_invalid_region(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test non-interactive mode fails with invalid region."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    assert create.callback
    await create.callback(
        profile_name="test_profile",
        region="invalid_region",
        api_token="test_token",
        api_url=None,
        non_interactive=True,
        config_manager=config_manager,
    )

    output = capsys.readouterr().out
    assert "❌ Invalid region: invalid_region" in output

    # Verify profile was not created
    config_manager.profile_manager.set_profile.assert_not_called()


@pytest.mark.asyncio
async def test_create_non_interactive_authentication_failure(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
) -> None:
    """Test non-interactive mode fails when authentication fails."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
    )

    # Mock Workato client that raises authentication error
    mock_client = AsyncMock()
    mock_client.users_api.get_workspace_details = AsyncMock(
        side_effect=Exception("401 Unauthorized")
    )
    # Mock the async context manager
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
            api_token="invalid_token",
            api_url=None,
            non_interactive=True,
            config_manager=config_manager,
        )

    output = capsys.readouterr().out
    assert "❌ Authentication failed:" in output
    assert "401 Unauthorized" in output

    # Verify profile was not created
    config_manager.profile_manager.set_profile.assert_not_called()


@pytest.mark.asyncio
async def test_create_non_interactive_profile_already_exists(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    profile_data_factory: Callable[..., ProfileData],
) -> None:
    """Test non-interactive mode handles existing profile gracefully."""
    existing_profile = profile_data_factory()
    config_manager = make_config_manager(
        get_profile=Mock(return_value=existing_profile),
    )

    assert create.callback
    await create.callback(
        profile_name="existing_profile",
        region="us",
        api_token="test_token",
        api_url=None,
        non_interactive=True,
        config_manager=config_manager,
    )

    output = capsys.readouterr().out
    assert "❌ Profile 'existing_profile' already exists" in output
    assert "Use 'workato profiles use' to switch to it" in output

    # Verify profile was not overwritten
    config_manager.profile_manager.set_profile.assert_not_called()


@pytest.mark.asyncio
async def test_create_non_interactive_eu_region(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    mock_workato_client: AsyncMock,
) -> None:
    """Test non-interactive profile creation for EU region."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
        set_profile=Mock(),
        set_current_profile=Mock(),
    )

    with patch(
        "workato_platform_cli.cli.commands.profiles.Workato",
        return_value=mock_workato_client,
    ):
        assert create.callback
        await create.callback(
            profile_name="eu_profile",
            region="eu",
            api_token="eu_token",
            api_url=None,
            non_interactive=True,
            config_manager=config_manager,
        )

    output = capsys.readouterr().out
    assert "✅ Profile 'eu_profile' created successfully" in output

    # Verify correct EU region URL was used
    call_args = config_manager.profile_manager.set_profile.call_args
    profile_data = call_args[0][1]
    assert profile_data.region == "eu"
    assert profile_data.region_url == "https://app.eu.workato.com"


@pytest.mark.asyncio
async def test_create_non_interactive_sets_current_profile(
    capsys: pytest.CaptureFixture[str],
    make_config_manager: Callable[..., Mock],
    mock_workato_client: AsyncMock,
) -> None:
    """Test non-interactive mode sets the new profile as current."""
    config_manager = make_config_manager(
        get_profile=Mock(return_value=None),
        set_profile=Mock(),
        set_current_profile=Mock(),
    )

    with patch(
        "workato_platform_cli.cli.commands.profiles.Workato",
        return_value=mock_workato_client,
    ):
        assert create.callback
        await create.callback(
            profile_name="new_profile",
            region="us",
            api_token="test_token",
            api_url=None,
            non_interactive=True,
            config_manager=config_manager,
        )

    # Verify profile was set as current
    config_manager.profile_manager.set_current_profile.assert_called_once_with(
        "new_profile"
    )

    output = capsys.readouterr().out
    assert "✅ Set 'new_profile' as the active profile" in output
