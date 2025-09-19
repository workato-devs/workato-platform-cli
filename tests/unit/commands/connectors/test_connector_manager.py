"""Tests for the connector manager helpers."""

from __future__ import annotations

import json

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from workato_platform.cli.commands.connectors import connector_manager
from workato_platform.cli.commands.connectors.connector_manager import (
    ConnectionParameter,
    ConnectorManager,
    ProviderData,
)


class DummySpinner:
    """Stub spinner for deterministic behaviour in tests."""

    def __init__(self, message: str) -> None:  # pragma: no cover - trivial
        self.message = message
        self.stopped = False

    def start(self) -> None:  # pragma: no cover - no behaviour needed
        pass

    def stop(self) -> float:
        self.stopped = True
        return 0.2

    def update_message(self, message: str) -> None:
        self.message = message


@pytest.fixture(autouse=True)
def patch_spinner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "workato_platform.cli.commands.connectors.connector_manager.Spinner",
        DummySpinner,
    )


@pytest.fixture(autouse=True)
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform.cli.commands.connectors.connector_manager.click.echo",
        _capture,
    )
    return captured


@pytest.fixture
def manager() -> ConnectorManager:
    client = SimpleNamespace(connectors_api=SimpleNamespace())
    return ConnectorManager(workato_api_client=client)


def test_load_connection_data_reads_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, manager: ConnectorManager) -> None:
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


def test_load_connection_data_invalid_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, manager: ConnectorManager) -> None:
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


def test_prompt_for_oauth_parameters_prompts(monkeypatch: pytest.MonkeyPatch, manager: ConnectorManager, capture_echo: list[str]) -> None:
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

    monkeypatch.setattr(
        "workato_platform.cli.commands.connectors.connector_manager.click.prompt",
        lambda *_args, **_kwargs: "https://example.atlassian.net",
    )

    result = manager.prompt_for_oauth_parameters("jira", existing_input={})

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
                pick_list=[["prod", "Production"], ["sandbox", "Sandbox"], ["dev", "Development"], ["qa", "QA"]],
            ),
        ],
    )

    connector_manager.ConnectorManager.show_provider_details(
        SimpleNamespace(), provider_key="sample", provider_data=provider
    )

    text = "\n".join(capture_echo)
    assert "Sample (sample)" in text
    assert "API Key" in text
    assert "Production" in text
    assert "... and 1 more" in text


@pytest.mark.asyncio
async def test_list_platform_connectors(monkeypatch: pytest.MonkeyPatch, manager: ConnectorManager, capture_echo: list[str]) -> None:
    responses = [
        SimpleNamespace(items=[SimpleNamespace(name="C1"), SimpleNamespace(name="C2")]),
        SimpleNamespace(items=[]),
    ]

    manager.workato_api_client.connectors_api = SimpleNamespace(
        list_platform_connectors=AsyncMock(side_effect=responses)
    )

    connectors = await manager.list_platform_connectors()

    assert len(connectors) == 2
    assert "Platform Connectors" in "\n".join(capture_echo)


@pytest.mark.asyncio
async def test_list_custom_connectors(monkeypatch: pytest.MonkeyPatch, manager: ConnectorManager, capture_echo: list[str]) -> None:
    manager.workato_api_client.connectors_api = SimpleNamespace(
        list_custom_connectors=AsyncMock(
            return_value=SimpleNamespace(
                result=[
                    SimpleNamespace(name="Alpha", version="1.0", description="Desc"),
                    SimpleNamespace(name="Beta", version="2.0", description=None),
                ]
            )
        )
    )

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
