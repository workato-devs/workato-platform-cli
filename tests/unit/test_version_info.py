"""Tests for Workato client wrapper and version module."""

from __future__ import annotations

import ssl

from types import SimpleNamespace

import pytest

import workato_platform


@pytest.mark.asyncio
async def test_workato_wrapper_sets_user_agent_and_tls(monkeypatch) -> None:
    configuration = SimpleNamespace()
    rest_context = SimpleNamespace(ssl_context=SimpleNamespace(minimum_version=None, options=0))

    created_clients: list[SimpleNamespace] = []

    class DummyApiClient:
        def __init__(self, config) -> None:
            self.configuration = config
            self.user_agent = None
            self.rest_client = rest_context
            created_clients.append(self)

        async def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(workato_platform, "ApiClient", DummyApiClient)

    # Patch all API classes to simple namespaces
    for api_name in [
        "ProjectsApi",
        "PropertiesApi",
        "UsersApi",
        "RecipesApi",
        "ConnectionsApi",
        "FoldersApi",
        "PackagesApi",
        "ExportApi",
        "DataTablesApi",
        "ConnectorsApi",
        "APIPlatformApi",
    ]:
        monkeypatch.setattr(workato_platform, api_name, lambda client, name=api_name: SimpleNamespace(api=name, client=client))

    wrapper = workato_platform.Workato(configuration)

    assert created_clients
    api_client = created_clients[0]
    assert api_client.user_agent.startswith("workato-platform-cli/")
    if hasattr(ssl, "TLSVersion"):
        assert rest_context.ssl_context.minimum_version == ssl.TLSVersion.TLSv1_2

    await wrapper.close()
    assert getattr(api_client, "closed", False) is True


@pytest.mark.asyncio
async def test_workato_async_context_manager(monkeypatch) -> None:
    class DummyApiClient:
        def __init__(self, config) -> None:
            self.rest_client = SimpleNamespace(ssl_context=SimpleNamespace(minimum_version=None, options=0))

        async def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(workato_platform, "ApiClient", DummyApiClient)
    for api_name in [
        "ProjectsApi",
        "PropertiesApi",
        "UsersApi",
        "RecipesApi",
        "ConnectionsApi",
        "FoldersApi",
        "PackagesApi",
        "ExportApi",
        "DataTablesApi",
        "ConnectorsApi",
        "APIPlatformApi",
    ]:
        monkeypatch.setattr(workato_platform, api_name, lambda client: SimpleNamespace(client=client))

    async with workato_platform.Workato(SimpleNamespace()) as wrapper:
        assert isinstance(wrapper, workato_platform.Workato)


def test_version_metadata_exposed() -> None:
    assert workato_platform.__version__
    from workato_platform import _version

    assert _version.__version__ == _version.version
    assert isinstance(_version.version_tuple, tuple)


def test_version_type_checking_imports() -> None:
    """Test TYPE_CHECKING branch in _version.py to improve coverage."""
    # Import the module and temporarily enable TYPE_CHECKING
    import workato_platform._version as version_module

    # Save original value
    original_type_checking = version_module.TYPE_CHECKING

    try:
        # Enable TYPE_CHECKING to trigger the import branch
        version_module.TYPE_CHECKING = True

        # Re-import the module to trigger the TYPE_CHECKING branch
        import importlib
        importlib.reload(version_module)

        # Check that the type definitions exist when TYPE_CHECKING is True

        # The module should have the type annotations
        assert hasattr(version_module, 'VERSION_TUPLE')
        assert hasattr(version_module, 'COMMIT_ID')

    finally:
        # Restore original state
        version_module.TYPE_CHECKING = original_type_checking
        importlib.reload(version_module)


def test_version_all_exports() -> None:
    """Test that all exported names in __all__ are accessible."""
    from workato_platform import _version

    for name in _version.__all__:
        assert hasattr(_version, name), f"Exported name '{name}' not found in module"

    # Test specific attributes
    assert _version.version == _version.__version__
    assert _version.version_tuple == _version.__version_tuple__
    assert _version.commit_id == _version.__commit_id__
