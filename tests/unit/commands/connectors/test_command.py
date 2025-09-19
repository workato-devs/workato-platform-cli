"""Unit tests for connectors CLI commands."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from workato_platform.cli.commands.connectors import command
from workato_platform.cli.commands.connectors.connector_manager import ProviderData


@pytest.fixture(autouse=True)
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _record(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform.cli.commands.connectors.command.click.echo",
        _record,
    )
    return captured


@pytest.mark.asyncio
async def test_list_connectors_defaults(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    manager = Mock()
    manager.list_platform_connectors = AsyncMock(
        return_value=[SimpleNamespace(name="salesforce", title="Salesforce")]
    )
    manager.list_custom_connectors = AsyncMock()

    assert command.list_connectors.callback

    await command.list_connectors.callback(
        platform=False, custom=False, connector_manager=manager
    )

    manager.list_platform_connectors.assert_awaited_once()
    manager.list_custom_connectors.assert_awaited_once()
    assert any("Salesforce" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_list_connectors_platform_only(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    manager = Mock()
    manager.list_platform_connectors = AsyncMock(return_value=[])
    manager.list_custom_connectors = AsyncMock()

    assert command.list_connectors.callback

    await command.list_connectors.callback(
        platform=True, custom=False, connector_manager=manager
    )

    manager.list_custom_connectors.assert_not_awaited()
    assert any("No platform connectors" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_parameters_no_data(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    manager = Mock(load_connection_data=Mock(return_value={}))

    assert command.parameters.callback

    await command.parameters.callback(
        provider=None,
        oauth_only=False,
        search=None,
        connector_manager=manager,
    )

    assert any("data not found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_parameters_specific_provider(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    provider_data = ProviderData(name="Salesforce", provider="salesforce", oauth=True)
    manager = Mock(
        load_connection_data=Mock(return_value={"salesforce": provider_data}),
        show_provider_details=Mock(),
    )

    assert command.parameters.callback

    await command.parameters.callback(
        provider="salesforce",
        oauth_only=False,
        search=None,
        connector_manager=manager,
    )

    manager.show_provider_details.assert_called_once_with("salesforce", provider_data)


@pytest.mark.asyncio
async def test_parameters_provider_not_found(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    manager = Mock(
        load_connection_data=Mock(
            return_value={
                "jira": ProviderData(name="Jira", provider="jira", oauth=True)
            }
        )
    )

    assert command.parameters.callback

    await command.parameters.callback(
        provider="unknown",
        oauth_only=False,
        search=None,
        connector_manager=manager,
    )

    assert any("not found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_parameters_filtered_list(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    manager = Mock()
    manager.load_connection_data.return_value = {
        "jira": ProviderData(
            name="Jira", provider="jira", oauth=True, secure_tunnel=True
        ),
        "mysql": ProviderData(name="MySQL", provider="mysql", oauth=False),
    }

    assert command.parameters.callback

    await command.parameters.callback(
        provider=None,
        oauth_only=True,
        search="ji",
        connector_manager=manager,
    )

    output = "\n".join(capture_echo)
    assert "Jira" in output
    assert "MySQL" not in output
    assert "secure tunnel" in output


@pytest.mark.asyncio
async def test_parameters_filtered_none(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    manager = Mock()
    manager.load_connection_data.return_value = {
        "jira": ProviderData(name="Jira", provider="jira", oauth=True),
    }

    assert command.parameters.callback

    await command.parameters.callback(
        provider=None,
        oauth_only=False,
        search="sales",
        connector_manager=manager,
    )

    assert any("No providers" in line for line in capture_echo)
