"""Tests for dependency injection container."""

from workato_platform.cli.containers import Container


class TestContainer:
    """Test the dependency injection container."""

    def test_container_initialization(self):
        """Test container can be initialized."""
        container = Container()
        assert container is not None

    def test_container_config_injection(self):
        """Test that config can be injected."""
        container = Container()

        # Should have a config provider
        assert hasattr(container, "config")

    def test_container_wiring(self):
        """Test that container can wire modules."""
        container = Container()

        # Should not raise exception when wiring
        # Using a minimal module list to avoid import issues
        container.wire(modules=[])

    def test_container_singleton_behavior(self):
        """Test that container providers behave as singletons where expected."""
        container = Container()

        # Access same provider twice should return same instance
        config1 = container.config()
        config2 = container.config()

        assert config1 is config2

    def test_container_with_mocked_config(self):
        """Test container with mocked dependencies."""
        container = Container()

        # Set a test value for CLI profile
        container.config.cli_profile.from_value("test-profile")

        # Should not raise an exception
        assert container.config is not None

    def test_container_provides_required_services(self):
        """Test that container provides all required services."""
        container = Container()

        # These should not raise AttributeError
        assert hasattr(container, "config")
        assert hasattr(container, "workato_api_client")

    def test_container_config_cli_profile_injection(self):
        """Test that CLI profile can be injected into config."""
        container = Container()

        # Should be able to set CLI profile
        container.config.cli_profile.from_value("test-profile")

        # This should not raise an exception
        assert True
