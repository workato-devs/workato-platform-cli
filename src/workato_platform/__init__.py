"""Wrapper for the generated Workato API client for easier access to endpoints."""

import ssl

from typing import Any

import aiohttp_retry


try:
    from workato_platform._version import __version__
except ImportError:
    __version__ = "unknown"

from workato_platform.client.workato_api.api.api_platform_api import APIPlatformApi
from workato_platform.client.workato_api.api.connections_api import ConnectionsApi
from workato_platform.client.workato_api.api.connectors_api import ConnectorsApi
from workato_platform.client.workato_api.api.data_tables_api import DataTablesApi
from workato_platform.client.workato_api.api.export_api import ExportApi
from workato_platform.client.workato_api.api.folders_api import FoldersApi
from workato_platform.client.workato_api.api.packages_api import PackagesApi
from workato_platform.client.workato_api.api.projects_api import ProjectsApi
from workato_platform.client.workato_api.api.properties_api import PropertiesApi
from workato_platform.client.workato_api.api.recipes_api import RecipesApi
from workato_platform.client.workato_api.api.users_api import UsersApi
from workato_platform.client.workato_api.api_client import ApiClient
from workato_platform.client.workato_api.configuration import Configuration


def _configure_retry_with_429_support(
    rest_client: Any, configuration: Configuration
) -> None:
    """
    Configure REST client to retry on 429 (Too Many Requests) errors.

    This patches the auto-generated REST client to add 429 to the list of
    retryable status codes with appropriate exponential backoff for rate limiting.

    Args:
        rest_client: The RESTClientObject instance to configure
        configuration: The Configuration object containing retry settings
    """
    # Enable retries by default if not explicitly set
    if configuration.retries is None:
        configuration.retries = 3

    # Update the retries setting on the REST client
    rest_client.retries = configuration.retries

    # Force recreation of retry_client with 429 support
    if rest_client.retry_client is not None:
        rest_client.retry_client = None

    # The retry_client will be lazily created on first request with our patched settings
    # We need to pre-create it here to ensure 429 support
    if rest_client.retries is not None:
        rest_client.retry_client = aiohttp_retry.RetryClient(
            client_session=rest_client.pool_manager,
            retry_options=aiohttp_retry.ExponentialRetry(
                attempts=rest_client.retries,
                factor=2.0,
                start_timeout=1.0,  # Increased from default 0.1s for rate limiting
                max_timeout=120.0,  # 2 minutes max
                statuses={429},  # Add 429 Too Many Requests
                retry_all_server_errors=True,  # Keep 5xx errors
            ),
        )


class Workato:
    """Wrapper class that provides easy access to all Workato API endpoints."""

    def __init__(self, configuration: Configuration):
        self._configuration = configuration
        self._api_client = ApiClient(configuration)

        # Set User-Agent header with CLI version
        user_agent = f"workato-platform-cli/{__version__}"
        self._api_client.user_agent = user_agent

        # Enforce TLS 1.2 minimum on the REST client's SSL context
        rest_client = self._api_client.rest_client
        if hasattr(ssl, "TLSVersion"):  # Python 3.7+
            rest_client.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        else:  # Fallback for older Python versions
            rest_client.ssl_context.options |= (
                ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            )

        # Configure retry logic with 429 (Too Many Requests) support
        _configure_retry_with_429_support(rest_client, configuration)

        # Initialize all API endpoints
        self.projects_api = ProjectsApi(self._api_client)
        self.properties_api = PropertiesApi(self._api_client)
        self.users_api = UsersApi(self._api_client)
        self.recipes_api = RecipesApi(self._api_client)
        self.connections_api = ConnectionsApi(self._api_client)
        self.folders_api = FoldersApi(self._api_client)
        self.packages_api = PackagesApi(self._api_client)
        self.export_api = ExportApi(self._api_client)
        self.data_tables_api = DataTablesApi(self._api_client)
        self.connectors_api = ConnectorsApi(self._api_client)
        self.api_platform_api = APIPlatformApi(self._api_client)

    @property
    def configuration(self) -> Configuration:
        """Access to the underlying API client configuration."""
        return self._configuration

    async def __aenter__(self) -> "Workato":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the underlying API client session."""
        await self._api_client.close()

    @property
    def api_client(self) -> ApiClient:
        """Access to the underlying API client."""
        return self._api_client
