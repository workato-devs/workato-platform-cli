"""Tests for the connector manager helpers."""

from __future__ import annotations

import json

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from workato_platform_cli.cli.commands.connectors import connector_manager
from workato_platform_cli.cli.commands.connectors.connector_manager import (
    ConnectionParameter,
    ConnectorManager,
    ProviderData,
)


class DummySpinner:
    """Stub spinner for deterministic behaviour in tests."""

    def __init__(self, message: str) -> None:
        self.message = message
        self.stopped = False

    def start(self) -> None:
        pass

    def stop(self) -> float:
        self.stopped = True
        return 0.2

    def update_message(self, message: str) -> None:
        self.message = message


@pytest.fixture(autouse=True)
def patch_spinner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.connectors.connector_manager.Spinner",
        DummySpinner,
    )


@pytest.fixture(autouse=True)
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.connectors.connector_manager.click.echo",
        _capture,
    )
    return captured


@pytest.fixture
def manager() -> ConnectorManager:
    client = Mock()
    client.connectors_api = Mock()
    return ConnectorManager(workato_api_client=client)


def test_load_connection_data_reads_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, manager: ConnectorManager
) -> None:
    data_path = tmp_path / "connection-data.json"
    payload = {
        "jira": {
            "name": "Jira",
            "provider": "jira",
            "oauth": True,
            "input": [
                {
                    "name": "auth_type",
                    "label": "Auth Type",
                    "type": "string",
                    "hint": "",
                    "pick_list": None,
                }
            ],
        }
    }
    data_path.write_text(json.dumps(payload))

    monkeypatch.setattr(
        ConnectorManager,
        "data_file_path",
        property(lambda self: data_path),
    )

    data = manager.load_connection_data()

    assert "jira" in data
    assert data["jira"].name == "Jira"
    assert manager._data_cache is data


def test_load_connection_data_invalid_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, manager: ConnectorManager
) -> None:
    broken_path = tmp_path / "connection-data.json"
    broken_path.write_text("{invalid")

    monkeypatch.setattr(
        ConnectorManager,
        "data_file_path",
        property(lambda self: broken_path),
    )

    data = manager.load_connection_data()

    assert data == {}


def test_get_oauth_required_parameters_defaults(manager: ConnectorManager) -> None:
    param = ConnectionParameter(name="auth_type", label="Auth Type", type="string")
    manager._data_cache = {
        "jira": ProviderData(
            name="Jira",
            provider="jira",
            oauth=True,
            input=[param],
        )
    }

    params = manager.get_oauth_required_parameters("jira")

    assert params == [param]


@pytest.mark.asyncio
async def test_prompt_for_oauth_parameters_prompts(
    monkeypatch: pytest.MonkeyPatch, manager: ConnectorManager, capture_echo: list[str]
) -> None:
    manager._data_cache = {
        "jira": ProviderData(
            name="Jira",
            provider="jira",
            oauth=True,
            input=[
                ConnectionParameter(name="auth_type", label="Auth Type", type="string"),
                ConnectionParameter(
                    name="host_url",
                    label="Host URL",
                    type="string",
                    hint="Provide your Jira domain",
                ),
            ],
        )
    }

    async def mock_prompt(*_args: object, **_kwargs: object) -> str:
        return "https://example.atlassian.net"

    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.connectors.connector_manager.click.prompt",
        mock_prompt,
    )

    result = await manager.prompt_for_oauth_parameters("jira", existing_input={})

    assert result["auth_type"] == "oauth"
    assert result["host_url"] == "https://example.atlassian.net"
    assert any("requires additional parameters" in line for line in capture_echo)


def test_show_provider_details_outputs_info(capture_echo: list[str]) -> None:
    provider = ProviderData(
        name="Sample",
        provider="sample",
        oauth=False,
        input=[
            ConnectionParameter(
                name="api_key",
                label="API Key",
                type="string",
                hint="<b>Enter</b> the key",
            ),
            ConnectionParameter(
                name="mode",
                label="Mode",
                type="select",
                pick_list=[
                    ["prod", "Production"],
                    ["sandbox", "Sandbox"],
                    ["dev", "Development"],
                    ["qa", "QA"],
                ],
            ),
        ],
    )

    mock_manager = Mock()
    connector_manager.ConnectorManager.show_provider_details(
        mock_manager, provider_key="sample", provider_data=provider
    )

    text = "\n".join(capture_echo)
    assert "Sample (sample)" in text
    assert "API Key" in text
    assert "Production" in text
    assert "... and 1 more" in text


@pytest.mark.asyncio
async def test_list_platform_connectors(
    manager: ConnectorManager, capture_echo: list[str]
) -> None:
    # Create mock connector objects
    connector1 = Mock()
    connector1.name = "C1"
    connector2 = Mock()
    connector2.name = "C2"

    # Create mock response objects
    response1 = Mock()
    response1.items = [connector1, connector2]
    response2 = Mock()
    response2.items = []

    responses = [response1, response2]

    with patch.object(
        manager.workato_api_client.connectors_api,
        "list_platform_connectors",
        AsyncMock(side_effect=responses),
    ):
        connectors = await manager.list_platform_connectors()

    assert len(connectors) == 2
    assert "Platform Connectors" in "\n".join(capture_echo)


@pytest.mark.asyncio
async def test_list_custom_connectors(
    manager: ConnectorManager, capture_echo: list[str]
) -> None:
    # Create mock custom connector objects
    connector1 = Mock()
    connector1.name = "Alpha"
    connector1.version = "1.0"
    connector1.description = "Desc"

    connector2 = Mock()
    connector2.name = "Beta"
    connector2.version = "2.0"
    connector2.description = None

    # Create mock response
    response = Mock()
    response.result = [connector1, connector2]

    with patch.object(
        manager.workato_api_client.connectors_api,
        "list_custom_connectors",
        AsyncMock(return_value=response),
    ):
        await manager.list_custom_connectors()

    output = "\n".join(capture_echo)
    assert "Custom Connectors" in output
    assert "Alpha" in output


def test_get_oauth_providers_filters(manager: ConnectorManager) -> None:
    manager._data_cache = {
        "alpha": ProviderData(name="Alpha", provider="alpha", oauth=True),
        "beta": ProviderData(name="Beta", provider="beta", oauth=False),
    }

    oauth_providers = manager.get_oauth_providers()

    assert list(oauth_providers.keys()) == ["alpha"]


def test_connection_parameter_model() -> None:
    """Test ConnectionParameter model creation and defaults."""
    # Test with all fields
    param = ConnectionParameter(
        name="test_param",
        label="Test Parameter",
        type="string",
        hint="Test hint",
        pick_list=[["value1", "Label1"], ["value2", "Label2"]],
    )
    assert param.name == "test_param"
    assert param.label == "Test Parameter"
    assert param.type == "string"
    assert param.hint == "Test hint"
    assert param.pick_list == [["value1", "Label1"], ["value2", "Label2"]]

    # Test with minimal fields (hint defaults to empty string)
    minimal_param = ConnectionParameter(name="minimal", label="Minimal", type="string")
    assert minimal_param.hint == ""
    assert minimal_param.pick_list is None


def test_provider_data_parameter_count() -> None:
    """Test ProviderData parameter_count property."""
    param1 = ConnectionParameter(name="param1", label="Param 1", type="string")
    param2 = ConnectionParameter(name="param2", label="Param 2", type="string")

    provider = ProviderData(
        name="Test Provider", provider="test", input=[param1, param2]
    )
    assert provider.parameter_count == 2

    empty_provider = ProviderData(name="Empty", provider="empty")
    assert empty_provider.parameter_count == 0


def test_provider_data_get_oauth_parameters_jira() -> None:
    """Test get_oauth_parameters for Jira provider."""
    auth_param = ConnectionParameter(name="auth_type", label="Auth Type", type="string")
    host_param = ConnectionParameter(name="host_url", label="Host URL", type="string")
    other_param = ConnectionParameter(name="other", label="Other", type="string")

    jira_provider = ProviderData(
        name="Jira",
        provider="jira",
        oauth=True,
        input=[auth_param, host_param, other_param],
    )

    oauth_params = jira_provider.get_oauth_parameters()
    assert len(oauth_params) == 2
    assert auth_param in oauth_params
    assert host_param in oauth_params
    assert other_param not in oauth_params


def test_provider_data_get_oauth_parameters_other_provider() -> None:
    """Test get_oauth_parameters for non-Jira provider returns empty."""
    param = ConnectionParameter(name="param", label="Param", type="string")
    provider = ProviderData(
        name="Other Provider", provider="other", oauth=True, input=[param]
    )

    oauth_params = provider.get_oauth_parameters()
    assert oauth_params == []


def test_provider_data_get_parameter_by_name() -> None:
    """Test get_parameter_by_name method."""
    param1 = ConnectionParameter(name="param1", label="Param 1", type="string")
    param2 = ConnectionParameter(name="param2", label="Param 2", type="string")

    provider = ProviderData(
        name="Test Provider", provider="test", input=[param1, param2]
    )

    # Test existing parameter
    result = provider.get_parameter_by_name("param1")
    assert result == param1

    # Test non-existent parameter
    result = provider.get_parameter_by_name("nonexistent")
    assert result is None


def test_connector_manager_data_file_path() -> None:
    """Test data_file_path property."""
    client = Mock()
    manager = ConnectorManager(workato_api_client=client)

    path = manager.data_file_path
    assert "connection-data.json" in str(path)
    assert "resources/data" in str(path)


def test_load_connection_data_missing_file(tmp_path: Path) -> None:
    """Test load_connection_data when file doesn't exist."""
    client = Mock()
    manager = ConnectorManager(workato_api_client=client)

    # Point to non-existent file
    missing_path = tmp_path / "missing.json"
    with patch.object(
        ConnectorManager, "data_file_path", property(lambda self: missing_path)
    ):
        data = manager.load_connection_data()

    assert data == {}
    assert manager._data_cache == {}


def test_load_connection_data_caching(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test load_connection_data uses cache on subsequent calls."""
    client = Mock()
    manager = ConnectorManager(workato_api_client=client)

    # Set up cache
    cached_data = {"test": ProviderData(name="Test", provider="test")}
    manager._data_cache = cached_data

    # Should return cached data without reading file
    result = manager.load_connection_data()
    assert result is cached_data


def test_get_provider_data_found(manager: ConnectorManager) -> None:
    """Test get_provider_data for existing provider."""
    provider = ProviderData(name="Test", provider="test")
    manager._data_cache = {"test": provider}

    result = manager.get_provider_data("test")
    assert result == provider


def test_get_provider_data_not_found(manager: ConnectorManager) -> None:
    """Test get_provider_data for non-existent provider."""
    manager._data_cache = {}

    result = manager.get_provider_data("nonexistent")
    assert result is None


def test_get_oauth_required_parameters_no_provider(manager: ConnectorManager) -> None:
    """Test get_oauth_required_parameters for non-existent provider."""
    manager._data_cache = {}

    result = manager.get_oauth_required_parameters("nonexistent")
    assert result == []


@pytest.mark.asyncio
async def test_prompt_for_oauth_parameters_no_oauth_params(
    manager: ConnectorManager,
) -> None:
    """Test prompt_for_oauth_parameters when no OAuth params needed."""
    manager._data_cache = {"simple": ProviderData(name="Simple", provider="simple")}

    result = await manager.prompt_for_oauth_parameters("simple", {"existing": "value"})
    assert result == {"existing": "value"}


@pytest.mark.asyncio
async def test_prompt_for_oauth_parameters_all_provided(
    manager: ConnectorManager,
) -> None:
    """Test prompt_for_oauth_parameters when all params already provided."""
    auth_param = ConnectionParameter(name="auth_type", label="Auth Type", type="string")
    provider = ProviderData(
        name="Jira", provider="jira", oauth=True, input=[auth_param]
    )
    manager._data_cache = {"jira": provider}

    existing_input = {"auth_type": "oauth"}
    result = await manager.prompt_for_oauth_parameters("jira", existing_input)
    assert result == existing_input


def test_show_provider_details_no_parameters(capture_echo: list[str]) -> None:
    """Test show_provider_details with provider that has no parameters."""
    provider = ProviderData(
        name="Simple Provider",
        provider="simple",
        oauth=False,
        personalization=False,
        secure_tunnel=False,
        input=[],
    )

    mock_manager = Mock()
    ConnectorManager.show_provider_details(mock_manager, "simple", provider)

    output = "\n".join(capture_echo)
    assert "Simple Provider (simple)" in output
    assert "No configuration parameters required" in output
    assert "OAuth: No" in output
    assert "Personalization: Not supported" in output


def test_show_provider_details_with_secure_tunnel(capture_echo: list[str]) -> None:
    """Test show_provider_details with secure tunnel support."""
    provider = ProviderData(
        name="Secure Provider",
        provider="secure",
        oauth=True,
        personalization=True,
        secure_tunnel=True,
        input=[],
    )

    mock_manager = Mock()
    ConnectorManager.show_provider_details(mock_manager, "secure", provider)

    output = "\n".join(capture_echo)
    assert "OAuth: Yes" in output
    assert "Personalization: Supported" in output
    assert "Secure Tunnel: Supported" in output


def test_show_provider_details_long_hint_truncation(capture_echo: list[str]) -> None:
    """Test show_provider_details truncates long hints."""
    long_hint = (
        "This is a very long hint that should be truncated because "
        "it exceeds the 100 character limit and goes on and on"
    )
    param = ConnectionParameter(
        name="test_param", label="Test Parameter", type="string", hint=long_hint
    )

    provider = ProviderData(name="Test Provider", provider="test", input=[param])

    mock_manager = Mock()
    ConnectorManager.show_provider_details(mock_manager, "test", provider)

    output = "\n".join(capture_echo)
    assert "..." in output  # Should show truncation


def test_show_provider_details_pick_list_truncation(capture_echo: list[str]) -> None:
    """Test show_provider_details truncates long pick lists."""
    pick_list = [
        ["opt1", "Option 1"],
        ["opt2", "Option 2"],
        ["opt3", "Option 3"],
        ["opt4", "Option 4"],
        ["opt5", "Option 5"],
    ]
    param = ConnectionParameter(
        name="test_param", label="Test Parameter", type="select", pick_list=pick_list
    )

    provider = ProviderData(name="Test Provider", provider="test", input=[param])

    mock_manager = Mock()
    ConnectorManager.show_provider_details(mock_manager, "test", provider)

    output = "\n".join(capture_echo)
    assert "... and 2 more" in output  # Should show truncation for 5 options


@pytest.mark.asyncio
async def test_list_custom_connectors_empty(
    manager: ConnectorManager, capture_echo: list[str]
) -> None:
    """Test list_custom_connectors with no connectors."""
    response = Mock()
    response.result = []

    with patch.object(
        manager.workato_api_client.connectors_api,
        "list_custom_connectors",
        AsyncMock(return_value=response),
    ):
        await manager.list_custom_connectors()

    output = "\n".join(capture_echo)
    assert "No custom connectors found" in output


@pytest.mark.asyncio
async def test_list_custom_connectors_long_description(
    manager: ConnectorManager, capture_echo: list[str]
) -> None:
    """Test list_custom_connectors truncates long descriptions."""
    connector = Mock()
    connector.name = "Long Desc Connector"
    connector.version = "1.0"
    connector.description = "A" * 150  # Very long description

    response = Mock()
    response.result = [connector]

    with patch.object(
        manager.workato_api_client.connectors_api,
        "list_custom_connectors",
        AsyncMock(return_value=response),
    ):
        await manager.list_custom_connectors()

    output = "\n".join(capture_echo)
    assert "..." in output  # Should show truncation


@pytest.mark.asyncio
async def test_list_custom_connectors_no_version_attribute(
    manager: ConnectorManager, capture_echo: list[str]
) -> None:
    """Test list_custom_connectors handles missing version attribute."""
    connector = Mock()
    connector.name = "No Version Connector"
    # Don't set version attribute
    del connector.version
    connector.description = "Test description"

    response = Mock()
    response.result = [connector]

    with patch.object(
        manager.workato_api_client.connectors_api,
        "list_custom_connectors",
        AsyncMock(return_value=response),
    ):
        await manager.list_custom_connectors()

    output = "\n".join(capture_echo)
    assert "No Version Connector (vUnknown)" in output


def test_load_connection_data_value_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, manager: ConnectorManager
) -> None:
    """Test load_connection_data handles ValueError from invalid data structure."""
    data_path = tmp_path / "connection-data.json"
    # Valid JSON but missing required fields to trigger ValueError
    payload = {
        "invalid": {
            # Missing required 'name' and 'provider' fields
            "oauth": True
        }
    }
    data_path.write_text(json.dumps(payload))

    monkeypatch.setattr(
        ConnectorManager,
        "data_file_path",
        property(lambda self: data_path),
    )

    data = manager.load_connection_data()
    assert data == {}  # Should return empty dict on ValueError
