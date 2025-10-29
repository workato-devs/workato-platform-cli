"""Tests for dependency injection container."""

from unittest.mock import Mock

from workato_platform_cli.cli.containers import (
    Container,
    create_profile_aware_workato_config,
    create_workato_config,
)


class TestContainer:
    """Test the dependency injection container."""

    def test_container_initialization(self) -> None:
        """Test container can be initialized."""
        container = Container()
        assert container is not None

    def test_container_config_injection(self) -> None:
        """Test that config can be injected."""
        container = Container()

        # Should have a config provider
        assert hasattr(container, "config")

    def test_container_wiring(self) -> None:
        """Test that container can wire modules."""
        container = Container()

        # Should not raise exception when wiring
        # Using a minimal module list to avoid import issues
        container.wire(modules=[])

    def test_container_singleton_behavior(self) -> None:
        """Test that container providers behave as singletons where expected."""
        container = Container()

        # Access same provider twice should return same instance
        config1 = container.config()
        config2 = container.config()

        assert config1 is config2

    def test_container_with_mocked_config(self) -> None:
        """Test container with mocked dependencies."""
        container = Container()

        # Set a test value for CLI profile
        container.config.cli_profile.from_value("test-profile")

        # Should not raise an exception
        assert container.config is not None

    def test_container_provides_required_services(self) -> None:
        """Test that container provides all required services."""
        container = Container()

        # These should not raise AttributeError
        assert hasattr(container, "config")
        assert hasattr(container, "workato_api_client")

    def test_container_config_cli_profile_injection(self) -> None:
        """Test that CLI profile can be injected into config."""
        container = Container()

        # Should be able to set CLI profile
        container.config.cli_profile.from_value("test-profile")

        # This should not raise an exception
        assert True


def test_create_workato_config() -> None:
    """Test create_workato_config function."""
    config = create_workato_config("test_token", "https://test.workato.com")

    assert config.access_token == "test_token"
    assert config.host == "https://test.workato.com"
    assert config.ssl_ca_cert is not None  # Should be set to certifi path


def test_create_profile_aware_workato_config_success() -> None:
    """Test create_profile_aware_workato_config with valid credentials."""
    # Mock the config manager
    mock_config_manager = Mock()
    mock_config_data = Mock()
    mock_config_data.profile = None
    mock_config_manager.load_config.return_value = mock_config_data

    # Mock profile manager resolution
    mock_config_manager.profile_manager.resolve_environment_variables.return_value = (
        "test_token",
        "https://test.workato.com",
    )

    config = create_profile_aware_workato_config(mock_config_manager)

    assert config.access_token == "test_token"
    assert config.host == "https://test.workato.com"


def test_create_profile_aware_workato_config_with_cli_profile() -> None:
    """Test create_profile_aware_workato_config with CLI profile override."""
    # Mock the config manager
    mock_config_manager = Mock()
    mock_config_data = Mock()
    mock_config_data.profile = "project_profile"
    mock_config_manager.load_config.return_value = mock_config_data

    # Mock profile manager resolution - should be called with CLI profile
    mock_config_manager.profile_manager.resolve_environment_variables.return_value = (
        "test_token",
        "https://test.workato.com",
    )

    # Call the function with CLI profile override
    config = create_profile_aware_workato_config(mock_config_manager, "cli_profile")

    # Verify CLI profile was used over project profile
    mock_config_manager.profile_manager.resolve_environment_variables.assert_called_with(
        "cli_profile"
    )

    # Verify configuration was created correctly
    assert config.access_token == "test_token"
    assert config.host == "https://test.workato.com"


def test_create_profile_aware_workato_config_no_credentials() -> None:
    """Test create_profile_aware_workato_config raises error when no credentials."""
    # Mock the config manager
    mock_config_manager = Mock()
    mock_config_data = Mock()
    mock_config_data.profile = None
    mock_config_manager.load_config.return_value = mock_config_data

    # Mock profile manager resolution to return None (no credentials)
    mock_config_manager.profile_manager.resolve_environment_variables.return_value = (
        None,
        None,
    )

    import pytest

    with pytest.raises(ValueError, match="Could not resolve API credentials"):
        create_profile_aware_workato_config(mock_config_manager)
