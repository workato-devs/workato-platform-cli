"""Tests for 429 retry configuration in Workato API client."""

from unittest.mock import Mock, patch

import pytest


class TestRetry429Configuration:
    """Test that 429 (Too Many Requests) errors are properly configured for retry."""

    def test_retries_enabled_by_default(self) -> None:
        """Test that retries are enabled by default when not explicitly set."""
        try:
            from workato_platform import Workato

            with patch("workato_platform.ApiClient") as mock_api_client:
                mock_configuration = Mock()
                mock_configuration.retries = None  # Not explicitly set

                mock_client_instance = Mock()
                mock_rest_client = Mock()
                mock_rest_client.pool_manager = Mock()
                mock_rest_client.retry_client = None
                mock_rest_client.ssl_context = Mock()

                mock_api_client.return_value = mock_client_instance
                mock_client_instance.rest_client = mock_rest_client

                Workato(mock_configuration)

                # Should be set to default value of 3
                assert mock_configuration.retries == 3
                assert mock_rest_client.retries == 3

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_custom_retry_count_preserved(self) -> None:
        """Test that explicitly set retry count is preserved."""
        try:
            from workato_platform import Workato

            with patch("workato_platform.ApiClient") as mock_api_client:
                mock_configuration = Mock()
                mock_configuration.retries = 5  # Custom value

                mock_client_instance = Mock()
                mock_rest_client = Mock()
                mock_rest_client.pool_manager = Mock()
                mock_rest_client.retry_client = None
                mock_rest_client.ssl_context = Mock()

                mock_api_client.return_value = mock_client_instance
                mock_client_instance.rest_client = mock_rest_client

                Workato(mock_configuration)

                # Should keep custom value
                assert mock_configuration.retries == 5
                assert mock_rest_client.retries == 5

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_retry_client_created_with_429_support(self) -> None:
        """Test that retry client is created with 429 status code support."""
        try:
            from workato_platform import Workato

            with (
                patch("workato_platform.ApiClient") as mock_api_client,
                patch("aiohttp_retry.RetryClient"),
                patch("aiohttp_retry.ExponentialRetry") as mock_exponential_retry,
            ):
                mock_configuration = Mock()
                mock_configuration.retries = None

                mock_client_instance = Mock()
                mock_rest_client = Mock()
                mock_rest_client.pool_manager = Mock()
                mock_rest_client.retry_client = None
                mock_rest_client.ssl_context = Mock()

                mock_api_client.return_value = mock_client_instance
                mock_client_instance.rest_client = mock_rest_client

                Workato(mock_configuration)

                # Verify ExponentialRetry was called with correct parameters
                mock_exponential_retry.assert_called_once()
                call_kwargs = mock_exponential_retry.call_args[1]

                assert call_kwargs["attempts"] == 3
                assert call_kwargs["factor"] == 2.0
                assert call_kwargs["start_timeout"] == 1.0
                assert call_kwargs["max_timeout"] == 120.0
                assert call_kwargs["statuses"] == {429}
                assert call_kwargs["retry_all_server_errors"] is True

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_exponential_backoff_timing(self) -> None:
        """Test that exponential backoff uses correct timing for rate limiting."""
        try:
            from workato_platform import Workato

            with (
                patch("workato_platform.ApiClient") as mock_api_client,
                patch("aiohttp_retry.ExponentialRetry") as mock_exponential_retry,
            ):
                mock_configuration = Mock()
                mock_configuration.retries = 3

                mock_client_instance = Mock()
                mock_rest_client = Mock()
                mock_rest_client.pool_manager = Mock()
                mock_rest_client.retry_client = None
                mock_rest_client.ssl_context = Mock()

                mock_api_client.return_value = mock_client_instance
                mock_client_instance.rest_client = mock_rest_client

                Workato(mock_configuration)

                # Verify timing parameters
                call_kwargs = mock_exponential_retry.call_args[1]
                assert call_kwargs["start_timeout"] == 1.0  # 1 second (not 0.1s)
                assert call_kwargs["max_timeout"] == 120.0  # 2 minutes
                assert call_kwargs["factor"] == 2.0  # 2x backoff

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_configure_retry_helper_function(self) -> None:
        """Test the _configure_retry_with_429_support helper function directly."""
        try:
            from workato_platform import _configure_retry_with_429_support

            with (
                patch("aiohttp_retry.RetryClient") as mock_retry_client,
                patch("aiohttp_retry.ExponentialRetry"),
            ):
                mock_rest_client = Mock()
                mock_rest_client.pool_manager = Mock()
                mock_rest_client.retry_client = None

                mock_configuration = Mock()
                mock_configuration.retries = None

                _configure_retry_with_429_support(mock_rest_client, mock_configuration)

                # Verify retries were set to default
                assert mock_configuration.retries == 3
                assert mock_rest_client.retries == 3

                # Verify retry client was created
                mock_retry_client.assert_called_once()

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_retry_client_recreated_if_exists(self) -> None:
        """Test that existing retry_client is recreated with new config."""
        try:
            from workato_platform import _configure_retry_with_429_support

            with (
                patch("aiohttp_retry.RetryClient") as mock_retry_client,
            ):
                mock_rest_client = Mock()
                mock_rest_client.pool_manager = Mock()
                mock_rest_client.retry_client = Mock()  # Pre-existing retry client

                mock_configuration = Mock()
                mock_configuration.retries = 5

                _configure_retry_with_429_support(mock_rest_client, mock_configuration)

                # Old retry_client should be set to None
                # New retry_client should be created
                mock_retry_client.assert_called_once()

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")

    def test_server_errors_still_retried(self) -> None:
        """Test that 5xx server errors are still retried alongside 429."""
        try:
            from workato_platform import Workato

            with (
                patch("workato_platform.ApiClient") as mock_api_client,
                patch("aiohttp_retry.ExponentialRetry") as mock_exponential_retry,
            ):
                mock_configuration = Mock()
                mock_configuration.retries = 3

                mock_client_instance = Mock()
                mock_rest_client = Mock()
                mock_rest_client.pool_manager = Mock()
                mock_rest_client.retry_client = None
                mock_rest_client.ssl_context = Mock()

                mock_api_client.return_value = mock_client_instance
                mock_client_instance.rest_client = mock_rest_client

                Workato(mock_configuration)

                # Verify retry_all_server_errors is True
                call_kwargs = mock_exponential_retry.call_args[1]
                assert call_kwargs["retry_all_server_errors"] is True

        except ImportError:
            pytest.skip("Workato class not available due to missing dependencies")
