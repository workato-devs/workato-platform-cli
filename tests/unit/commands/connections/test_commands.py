"""Command-level tests for connections CLI module."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

import workato_platform_cli.cli.commands.connections as connections_module

from workato_platform_cli.cli.commands.connectors.connector_manager import (
    ConnectionParameter,
    ProviderData,
)
from workato_platform_cli.cli.utils.config import ConfigData


class DummySpinner:
    """Spinner stub to avoid timing in tests."""

    def __init__(self, _message: str) -> None:
        self.stopped = False

    def start(self) -> None:
        pass

    def stop(self) -> float:
        self.stopped = True
        return 0.1

    def update_message(self, _message: str) -> None:
        pass


@pytest.fixture(autouse=True)
def patch_spinner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(connections_module, "Spinner", DummySpinner)


@pytest.fixture(autouse=True)
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(connections_module.click, "echo", _capture)
    return captured


def make_stub(**attrs: Any) -> Mock:
    stub = Mock()
    stub.configure_mock(**attrs)
    return stub


@pytest.mark.asyncio
async def test_create_requires_folder(capture_echo: list[str]) -> None:
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(folder_id=None)

    callback = connections_module.create.callback
    assert callback is not None

    await callback(
        name="Conn",
        provider="jira",
        config_manager=config_manager,
        connector_manager=Mock(),
        workato_api_client=Mock(),
    )

    assert any("No folder ID" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_basic_success(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(folder_id=99)

    provider_data = ProviderData(name="Jira", provider="jira", oauth=False)
    connector_manager = Mock(get_provider_data=Mock(return_value=provider_data))

    api = make_stub(
        create_connection=AsyncMock(
            return_value=make_stub(id=5, name="Conn", provider="jira")
        )
    )
    workato_client = make_stub(connections_api=api)

    monkeypatch.setattr(
        connections_module, "requires_oauth_flow", AsyncMock(return_value=False)
    )

    callback = connections_module.create.callback
    assert callback is not None

    await callback(
        name="Conn",
        provider="jira",
        input_params='{"key":"value"}',
        config_manager=config_manager,
        connector_manager=connector_manager,
        workato_api_client=workato_client,
    )

    api.create_connection.assert_awaited_once()
    payload = api.create_connection.await_args.kwargs["connection_create_request"]
    assert payload.shell_connection is False
    assert payload.input == {"key": "value"}
    assert any("Connection created successfully" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_oauth_flow(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(folder_id=12)
    config_manager.api_host = "https://www.workato.com"

    provider_data = ProviderData(
        name="Jira",
        provider="jira",
        oauth=True,
        input=[
            ConnectionParameter(name="auth_type", label="Auth Type", type="string"),
            ConnectionParameter(name="host_url", label="Host URL", type="string"),
        ],
    )
    connector_manager = Mock(
        get_provider_data=Mock(return_value=provider_data),
        prompt_for_oauth_parameters=AsyncMock(
            return_value={"auth_type": "oauth", "host_url": "https://jira"}
        ),
    )

    api = make_stub(
        create_connection=AsyncMock(
            return_value=make_stub(id=7, name="Jira", provider="jira")
        )
    )
    workato_client = make_stub(connections_api=api)

    monkeypatch.setattr(
        connections_module, "requires_oauth_flow", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(connections_module, "get_connection_oauth_url", AsyncMock())
    monkeypatch.setattr(connections_module, "poll_oauth_connection_status", AsyncMock())

    callback = connections_module.create.callback
    assert callback is not None

    await callback(
        name="Conn",
        provider="jira",
        config_manager=config_manager,
        connector_manager=connector_manager,
        workato_api_client=workato_client,
    )

    api.create_connection.assert_awaited_once()
    payload = api.create_connection.await_args.kwargs["connection_create_request"]
    assert payload.shell_connection is True
    assert payload.input == {"auth_type": "oauth", "host_url": "https://jira"}
    assert any("OAuth provider detected" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_oauth_manual_fallback(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(folder_id=42)
    config_manager.api_host = "https://www.workato.com"

    provider_data = ProviderData(
        name="Jira",
        provider="jira",
        oauth=True,
        input=[ConnectionParameter(name="host_url", label="Host URL", type="string")],
    )
    connector_manager = Mock(
        get_provider_data=Mock(return_value=provider_data),
        prompt_for_oauth_parameters=AsyncMock(
            return_value={"host_url": "https://jira"}
        ),
    )

    api = make_stub(
        create_connection=AsyncMock(
            return_value=make_stub(id=10, name="Conn", provider="jira")
        )
    )
    workato_client = make_stub(connections_api=api)

    monkeypatch.setattr(
        connections_module, "requires_oauth_flow", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(
        connections_module,
        "get_connection_oauth_url",
        AsyncMock(side_effect=RuntimeError("boom")),
    )
    monkeypatch.setattr(connections_module, "poll_oauth_connection_status", AsyncMock())
    browser_mock = Mock()
    monkeypatch.setattr(connections_module.webbrowser, "open", browser_mock)

    callback = connections_module.create.callback
    assert callback is not None

    await callback(
        name="Conn",
        provider="jira",
        config_manager=config_manager,
        connector_manager=connector_manager,
        workato_api_client=workato_client,
    )

    browser_mock.assert_called_once()
    assert any("Manual authorization" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_oauth_missing_folder(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(folder_id=None)
    workato_client = make_stub(connections_api=make_stub())

    callback = connections_module.create_oauth.callback
    assert callback is not None

    await callback(
        parent_id=1,
        external_id="ext",
        name=None,
        folder_id=None,
        workato_api_client=workato_client,
        config_manager=config_manager,
    )

    assert any("No folder ID" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_oauth_command(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(folder_id=None)
    config_manager.api_host = "https://www.workato.com"

    api = make_stub(
        create_runtime_user_connection=AsyncMock(
            return_value=make_stub(data=make_stub(id=321, url="https://oauth"))
        )
    )
    workato_client = make_stub(connections_api=api)

    monkeypatch.setattr(connections_module, "poll_oauth_connection_status", AsyncMock())
    monkeypatch.setattr(connections_module.webbrowser, "open", Mock())

    callback = connections_module.create_oauth.callback
    assert callback is not None

    await callback(
        parent_id=9,
        external_id="user",
        name=None,
        folder_id=77,
        workato_api_client=workato_client,
        config_manager=config_manager,
    )

    api.create_runtime_user_connection.assert_awaited_once()
    assert any("Runtime user connection created" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_update_with_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    update_mock = AsyncMock()
    monkeypatch.setattr(connections_module, "update_connection", update_mock)

    callback = connections_module.update.callback
    assert callback is not None

    await callback(
        connection_id=1,
        input_params="[1,2,3]",
    )

    update_mock.assert_not_called()


@pytest.mark.asyncio
async def test_update_calls_update_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    update_mock = AsyncMock()
    monkeypatch.setattr(connections_module, "update_connection", update_mock)

    callback = connections_module.update.callback
    assert callback is not None

    await callback(
        connection_id=5,
        name="New",
        input_params='{"k":"v"}',
    )

    update_mock.assert_awaited_once()
    assert update_mock.await_args
    request = update_mock.await_args.args[1]
    assert request.name == "New"
    assert request.input == {"k": "v"}


@pytest.mark.asyncio
async def test_update_connection_outputs(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    connections_api = make_stub(
        update_connection=AsyncMock(
            return_value=make_stub(
                name="Conn",
                id=10,
                provider="jira",
                folder_id=3,
                authorization_status="success",
                parent_id=1,
                external_id="ext",
            )
        )
    )
    workato_client = make_stub(connections_api=connections_api)
    project_manager = make_stub(handle_post_api_sync=AsyncMock())

    assert connections_module.update_connection is not None
    assert hasattr(connections_module.update_connection, "__wrapped__")

    await connections_module.update_connection.__wrapped__(
        connection_id=10,
        connection_update_request=make_stub(
            name="Conn",
            folder_id=3,
            parent_id=1,
            external_id="ext",
            shell_connection=True,
            input={"k": "v"},
        ),
        workato_api_client=workato_client,
        project_manager=project_manager,
    )

    project_manager.handle_post_api_sync.assert_awaited_once()
    output = "\n".join(capture_echo)
    assert "Connection updated successfully" in output
    assert "Updated: name" in output


@pytest.mark.asyncio
async def test_get_connection_oauth_url(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    connections_api = make_stub(
        get_connection_oauth_url=AsyncMock(
            return_value=make_stub(data=make_stub(url="https://oauth"))
        )
    )
    workato_client = make_stub(connections_api=connections_api)

    open_mock = Mock()
    monkeypatch.setattr(connections_module.webbrowser, "open", open_mock)

    assert connections_module.get_connection_oauth_url is not None
    assert hasattr(connections_module.get_connection_oauth_url, "__wrapped__")

    await connections_module.get_connection_oauth_url.__wrapped__(
        connection_id=5,
        open_browser=True,
        workato_api_client=workato_client,
    )

    open_mock.assert_called_once_with("https://oauth")
    assert any("OAuth URL retrieved successfully" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_get_connection_oauth_url_no_browser(capture_echo: list[str]) -> None:
    connections_api = make_stub(
        get_connection_oauth_url=AsyncMock(
            return_value=make_stub(data=make_stub(url="https://oauth"))
        )
    )
    workato_client = make_stub(connections_api=connections_api)

    assert connections_module.get_connection_oauth_url is not None
    assert hasattr(connections_module.get_connection_oauth_url, "__wrapped__")

    await connections_module.get_connection_oauth_url.__wrapped__(
        connection_id=5,
        open_browser=False,
        workato_api_client=workato_client,
    )

    assert not any("Opening OAuth URL" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_list_connections_no_results(capture_echo: list[str]) -> None:
    workato_client = make_stub(
        connections_api=make_stub(list_connections=AsyncMock(return_value=[]))
    )

    assert connections_module.list_connections.callback

    await connections_module.list_connections.callback(
        workato_api_client=workato_client,
        folder_id=1,
        parent_id=None,
        external_id=None,
        include_runtime=False,
        tags=None,
        provider=None,
        unauthorized=False,
    )

    output = "\n".join(capture_echo)
    assert "No connections found" in output


@pytest.mark.asyncio
async def test_list_connections_filters(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    connection_items = [
        make_stub(
            name="ConnA",
            id=1,
            provider="jira",
            application="jira",
            authorization_status="success",
            folder_id=2,
            parent_id=None,
            external_id=None,
            tags=["one"],
            created_at=datetime(2024, 1, 1),
        ),
        make_stub(
            name="ConnB",
            id=2,
            provider="jira",
            application="jira",
            authorization_status="failed",
            folder_id=2,
            parent_id=None,
            external_id=None,
            tags=[],
            created_at=None,
        ),
        make_stub(
            name="ConnC",
            id=3,
            provider="salesforce",
            application="salesforce",
            authorization_status="success",
            folder_id=3,
            parent_id=None,
            external_id=None,
            tags=[],
            created_at=None,
        ),
    ]

    workato_client = make_stub(
        connections_api=make_stub(
            list_connections=AsyncMock(return_value=connection_items)
        )
    )

    assert connections_module.list_connections.callback

    await connections_module.list_connections.callback(
        provider="jira",
        unauthorized=True,
        folder_id=None,
        parent_id=None,
        include_runtime=False,
        tags=None,
        workato_api_client=workato_client,
    )

    output = "\n".join(capture_echo)
    assert "Connections (1 found" in output
    assert "Unauthorized" in output


@pytest.mark.asyncio
async def test_pick_list_command(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    workato_client = make_stub(
        connections_api=make_stub(
            get_connection_picklist=AsyncMock(return_value=make_stub(data=["A", "B"]))
        )
    )

    assert connections_module.pick_list.callback

    await connections_module.pick_list.callback(
        id=10,
        pick_list_name="objects",
        params='{"key":"value"}',
        workato_api_client=workato_client,
    )

    output = "\n".join(capture_echo)
    assert "Pick List Results" in output
    assert "A" in output


@pytest.mark.asyncio
async def test_pick_list_invalid_json(capture_echo: list[str]) -> None:
    workato_client = make_stub(connections_api=make_stub())

    assert connections_module.pick_list.callback

    await connections_module.pick_list.callback(
        id=5,
        pick_list_name="objects",
        params="not-json",
        workato_api_client=workato_client,
    )

    assert any("Invalid JSON" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_pick_list_no_results(capture_echo: list[str]) -> None:
    workato_client = make_stub(
        connections_api=make_stub(
            get_connection_picklist=AsyncMock(return_value=make_stub(data=[]))
        )
    )

    assert connections_module.pick_list.callback

    await connections_module.pick_list.callback(
        id=6,
        pick_list_name="objects",
        params=None,
        workato_api_client=workato_client,
    )

    assert any("No results found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_poll_oauth_connection_status_timeout(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    monkeypatch.setattr(connections_module, "OAUTH_TIMEOUT", 1)
    api = make_stub(
        list_connections=AsyncMock(
            return_value=[
                make_stub(
                    id=1,
                    name="Conn",
                    provider="jira",
                    authorization_status="pending",
                    folder_id=None,
                    parent_id=None,
                    external_id=None,
                    tags=[],
                    created_at=None,
                )
            ]
        )
    )
    workato_client = make_stub(connections_api=api)
    project_manager = make_stub(handle_post_api_sync=AsyncMock())
    config_manager = make_stub(api_host="https://app.workato.com")

    times = [0, 0.6, 1.2]

    def fake_time() -> float:
        return times.pop(0) if times else 2.0

    monkeypatch.setattr("time.time", fake_time)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    assert connections_module.poll_oauth_connection_status is not None
    assert hasattr(connections_module.poll_oauth_connection_status, "__wrapped__")

    await connections_module.poll_oauth_connection_status.__wrapped__(
        1,
        external_id="ext",
        workato_api_client=workato_client,
        project_manager=project_manager,
        config_manager=config_manager,
    )

    output = "\n".join(capture_echo)
    assert "Timeout reached" in output


@pytest.mark.asyncio
async def test_poll_oauth_connection_status_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    api = make_stub(
        list_connections=AsyncMock(
            return_value=[
                make_stub(
                    id=1,
                    name="Conn",
                    provider="jira",
                    authorization_status="pending",
                    folder_id=None,
                    parent_id=None,
                    external_id=None,
                    tags=[],
                    created_at=None,
                )
            ]
        )
    )
    workato_client = make_stub(connections_api=api)
    project_manager = make_stub(handle_post_api_sync=AsyncMock())
    config_manager = make_stub(api_host="https://app.workato.com")

    monkeypatch.setattr("time.time", lambda: 0)

    def raise_interrupt(*_args: Any, **_kwargs: Any) -> None:
        raise KeyboardInterrupt()

    monkeypatch.setattr("time.sleep", raise_interrupt)

    assert connections_module.poll_oauth_connection_status is not None
    assert hasattr(connections_module.poll_oauth_connection_status, "__wrapped__")

    await connections_module.poll_oauth_connection_status.__wrapped__(
        1,
        external_id="ext",
        workato_api_client=workato_client,
        project_manager=project_manager,
        config_manager=config_manager,
    )

    output = "\n".join(capture_echo)
    assert "Polling interrupted" in output


@pytest.mark.asyncio
async def test_requires_oauth_flow_none() -> None:
    result = await connections_module.requires_oauth_flow("")
    assert result is False


@pytest.mark.asyncio
async def test_requires_oauth_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        connections_module, "is_platform_oauth_provider", AsyncMock(return_value=False)
    )
    monkeypatch.setattr(
        connections_module, "is_custom_connector_oauth", AsyncMock(return_value=True)
    )

    result = await connections_module.requires_oauth_flow("jira")
    assert result is True


@pytest.mark.asyncio
async def test_is_platform_oauth_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    connector_manager = Mock(
        list_platform_connectors=AsyncMock(
            return_value=[make_stub(name="jira", oauth=True)]
        )
    )

    assert connections_module.is_platform_oauth_provider is not None
    assert hasattr(connections_module.is_platform_oauth_provider, "__wrapped__")

    result = await connections_module.is_platform_oauth_provider.__wrapped__(
        "jira",
        connector_manager=connector_manager,
    )

    assert result is True


@pytest.mark.asyncio
async def test_is_custom_connector_oauth_not_found() -> None:
    connectors_api = make_stub(
        list_custom_connectors=AsyncMock(
            return_value=make_stub(result=[make_stub(name="other", id=1)])
        ),
        get_custom_connector_code=AsyncMock(),
    )
    workato_client = make_stub(connectors_api=connectors_api)

    assert connections_module.is_custom_connector_oauth is not None
    assert hasattr(connections_module.is_custom_connector_oauth, "__wrapped__")

    result = await connections_module.is_custom_connector_oauth.__wrapped__(
        "jira",
        workato_api_client=workato_client,
    )

    assert result is False
    connectors_api.get_custom_connector_code.assert_not_called()


@pytest.mark.asyncio
async def test_is_custom_connector_oauth(monkeypatch: pytest.MonkeyPatch) -> None:
    connectors_api = make_stub(
        list_custom_connectors=AsyncMock(
            return_value=make_stub(result=[make_stub(name="jira", id=5)])
        ),
        get_custom_connector_code=AsyncMock(
            return_value=make_stub(data=make_stub(code="client_id"))
        ),
    )
    workato_client = make_stub(connectors_api=connectors_api)

    assert connections_module.is_custom_connector_oauth is not None
    assert hasattr(connections_module.is_custom_connector_oauth, "__wrapped__")

    result = await connections_module.is_custom_connector_oauth.__wrapped__(
        "jira",
        workato_api_client=workato_client,
    )

    assert result is True
    connectors_api.get_custom_connector_code.assert_awaited_once()


@pytest.mark.asyncio
async def test_poll_oauth_connection_status(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    responses = [
        [
            make_stub(
                id=1,
                name="Conn",
                provider="jira",
                authorization_status="pending",
                folder_id=None,
                parent_id=None,
                external_id=None,
                tags=[],
                created_at=None,
            )
        ],
        [
            make_stub(
                id=1,
                name="Conn",
                provider="jira",
                authorization_status="success",
                folder_id=None,
                parent_id=None,
                external_id=None,
                tags=[],
                created_at=None,
            )
        ],
    ]

    api = make_stub(list_connections=AsyncMock(side_effect=responses))

    workato_client = make_stub(connections_api=api)
    project_manager = make_stub(handle_post_api_sync=AsyncMock())
    config_manager = make_stub(api_host="https://app.workato.com")

    times = [0, 1, 2, 10]

    def fake_time() -> float:
        return times.pop(0) if times else 10

    monkeypatch.setattr("time.time", fake_time)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    assert connections_module.poll_oauth_connection_status is not None
    assert hasattr(connections_module.poll_oauth_connection_status, "__wrapped__")

    await connections_module.poll_oauth_connection_status.__wrapped__(
        1,
        external_id=None,
        workato_api_client=workato_client,
        project_manager=project_manager,
        config_manager=config_manager,
    )

    project_manager.handle_post_api_sync.assert_awaited_once()
    assert any(
        "OAuth authorization completed successfully" in line for line in capture_echo
    )
