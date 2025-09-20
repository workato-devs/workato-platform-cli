"""Tests for Workato API client wrapper."""

from unittest.mock import Mock, patch

import pytest


# Import will be handled with try/except to avoid dependency issues


class TestWorkatoClient:
    """Test the Workato API client wrapper."""

    def test_workato_class_can_be_imported(self) -> None:
        """Test that Workato class can be imported."""
        try:
            from workato_platform import Workato

            assert Workato is not None
        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_workato_initialization_mocked(self) -> None:
        """Test Workato can be initialized with mocked dependencies."""
        try:
            from workato_platform import Workato

            with (
                patch("workato_platform.Configuration") as mock_config,
                patch("workato_platform.ApiClient") as mock_api_client,
            ):
                mock_configuration = Mock()
                mock_config.return_value = mock_configuration

                client = Workato(mock_configuration)

                assert client._api_client is not None
                mock_api_client.assert_called_once_with(mock_configuration)

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_workato_api_endpoints_structure(self) -> None:
        """Test that Workato class structure can be analyzed."""
        try:
            from workato_platform import Workato

            # Check expected API endpoint attributes
            expected_apis = [
                "projects_api",
                "properties_api",
                "users_api",
                "recipes_api",
                "connections_api",
                "connectors_api",
                "data_tables_api",
                "export_api",
                "folders_api",
                "packages_api",
            ]

            # Create mock configuration with proper SSL attributes
            with (
                patch("workato_platform.Configuration") as mock_config,
            ):
                mock_configuration = Mock()
                mock_configuration.connection_pool_maxsize = 10
                mock_configuration.ssl_ca_cert = None
                mock_configuration.ca_cert_data = None
                mock_configuration.cert_file = None
                mock_config.return_value = mock_configuration

                client = Workato(mock_configuration)

                # Check that expected API endpoints exist as attributes
                for api_name in expected_apis:
                    assert hasattr(client, api_name), f"Missing {api_name} attribute"

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")
