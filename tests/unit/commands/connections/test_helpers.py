"""Helper-focused tests for the connections command module."""

from __future__ import annotations

import json

from datetime import datetime
from pathlib import Path

import pytest

import workato_platform.cli.commands.connections as connections_module

from workato_platform.cli.commands.connections import (
    _get_callback_url_from_api_host,
    display_connection_summary,
    group_connections_by_provider,
    parse_connection_input,
    show_connection_statistics,
)
from workato_platform.client.workato_api.models.connection import Connection


@pytest.fixture(autouse=True)
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _record(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform.cli.commands.connections.click.echo",
        _record,
    )
    return captured


def test_get_callback_url_from_api_host_known_domains() -> None:
    assert (
        _get_callback_url_from_api_host("https://www.workato.com")
        == "https://app.workato.com/"
    )
    assert (
        _get_callback_url_from_api_host("https://eu.workato.com")
        == "https://app.eu.workato.com/"
    )
    assert (
        _get_callback_url_from_api_host("https://sg.workato.com")
        == "https://app.sg.workato.com/"
    )
    assert _get_callback_url_from_api_host("invalid") == "https://app.workato.com/"
    assert _get_callback_url_from_api_host("") == "https://app.workato.com/"


def test_parse_connection_input_cases(capture_echo: list[str]) -> None:
    assert parse_connection_input(None) is None
    assert parse_connection_input("{}") == {}

    assert parse_connection_input("{invalid}") is None
    assert any("Invalid JSON" in line for line in capture_echo)

    capture_echo.clear()
    assert parse_connection_input("[]") is None
    assert any("must be a JSON object" in line for line in capture_echo)


def test_group_connections_by_provider() -> None:
    from datetime import datetime

    connections: list[Connection] = [
        Connection.model_validate(
            {
                "id": 1,
                "application": "salesforce",
                "name": "B",
                "description": None,
                "authorized_at": None,
                "authorization_status": "success",
                "authorization_error": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "external_id": None,
                "folder_id": 1,
                "connection_lost_at": None,
                "connection_lost_reason": None,
                "parent_id": None,
                "tags": None,
            }
        ),
        Connection.model_validate(
            {
                "id": 2,
                "application": "salesforce",
                "name": "A",
                "description": None,
                "authorized_at": None,
                "authorization_status": "success",
                "authorization_error": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "external_id": None,
                "folder_id": 1,
                "connection_lost_at": None,
                "connection_lost_reason": None,
                "parent_id": None,
                "tags": None,
            }
        ),
        Connection.model_validate(
            {
                "id": 3,
                "application": "jira",
                "name": "Alpha",
                "description": None,
                "authorized_at": None,
                "authorization_status": "failed",
                "authorization_error": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "external_id": None,
                "folder_id": 1,
                "connection_lost_at": None,
                "connection_lost_reason": None,
                "parent_id": None,
                "tags": None,
            }
        ),
        Connection.model_validate(
            {
                "id": 4,
                "application": "custom",
                "name": "X",
                "description": None,
                "authorized_at": None,
                "authorization_status": "success",
                "authorization_error": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "external_id": None,
                "folder_id": 1,
                "connection_lost_at": None,
                "connection_lost_reason": None,
                "parent_id": None,
                "tags": None,
            }
        ),
    ]

    grouped = group_connections_by_provider(connections)

    assert list(grouped.keys()) == ["Custom", "Jira", "Salesforce"]
    assert [c.name for c in grouped["Salesforce"]] == ["A", "B"]


def test_display_connection_summary_outputs_details(capture_echo: list[str]) -> None:
    connection = Connection.model_validate(
        {
            "name": "My Conn",
            "id": 42,
            "application": "salesforce",
            "description": None,
            "authorized_at": None,
            "authorization_status": "success",
            "authorization_error": None,
            "folder_id": 100,
            "parent_id": 5,
            "external_id": "ext-1",
            "tags": ["one", "two", "three", "four"],
            "created_at": datetime(2024, 1, 15),
            "updated_at": datetime(2024, 1, 15),
            "connection_lost_at": None,
            "connection_lost_reason": None,
        }
    )

    display_connection_summary(connection)

    output = "\n".join(capture_echo)
    assert "My Conn" in output
    assert "Authorized" in output
    assert "Folder ID: 100" in output
    assert "+1 more" in output
    assert "2024-01-15" in output


def test_show_connection_statistics(capture_echo: list[str]) -> None:
    from datetime import datetime

    connections = [
        Connection.model_validate(
            {
                "id": 1,
                "name": "Test 1",
                "application": "salesforce",
                "description": None,
                "authorized_at": None,
                "authorization_status": "success",
                "authorization_error": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "external_id": None,
                "folder_id": 1,
                "connection_lost_at": None,
                "connection_lost_reason": None,
                "parent_id": None,
                "provider": "salesforce",
                "tags": None,
            }
        ),
        Connection.model_validate(
            {
                "id": 2,
                "name": "Test 2",
                "application": "jira",
                "description": None,
                "authorized_at": None,
                "authorization_status": "failed",
                "authorization_error": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "external_id": None,
                "folder_id": 1,
                "connection_lost_at": None,
                "connection_lost_reason": None,
                "parent_id": None,
                "provider": "jira",
                "tags": None,
            }
        ),
        Connection.model_validate(
            {
                "id": 3,
                "name": "Test 3",
                "application": "custom",
                "description": None,
                "authorized_at": None,
                "authorization_status": "success",
                "authorization_error": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "external_id": None,
                "folder_id": 1,
                "connection_lost_at": None,
                "connection_lost_reason": None,
                "parent_id": None,
                "provider": None,
                "tags": None,
            }
        ),
    ]

    show_connection_statistics(connections)

    output = "\n".join(capture_echo)
    assert "Authorized: 2" in output
    assert "Unauthorized: 1" in output
    assert "Providers" in output


@pytest.mark.parametrize(
    "adapter,expected",
    [(None, "Available Adapters"), ("alpha", "Pick Lists for 'alpha'")],
)
def test_pick_lists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capture_echo: list[str],
    adapter: str | None,
    expected: str,
) -> None:
    module_root = tmp_path / "cli" / "commands"
    data_dir = module_root.parent / "data"
    data_dir.mkdir(parents=True)

    picklist_file = data_dir / "picklist-data.json"
    picklist_content = {
        "alpha": [
            {"name": "ListA", "parameters": ["param1", "param2"]},
            {"name": "ListB", "parameters": []},
        ]
    }
    picklist_file.write_text(json.dumps(picklist_content))

    original_file = connections_module.__file__
    monkeypatch.setattr(
        connections_module, "__file__", str(module_root / "connections.py")
    )

    assert connections_module.pick_lists.callback

    try:
        connections_module.pick_lists.callback(adapter=adapter)
    finally:
        monkeypatch.setattr(connections_module, "__file__", original_file)

    assert any(expected.split()[0] in line for line in capture_echo)


def test_pick_lists_missing_file(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str], tmp_path: Path
) -> None:
    module_root = tmp_path / "cli" / "commands"
    module_root.mkdir(parents=True)
    original_file = connections_module.__file__
    monkeypatch.setattr(
        connections_module, "__file__", str(module_root / "connections.py")
    )

    assert connections_module.pick_lists.callback

    try:
        connections_module.pick_lists.callback()
    finally:
        monkeypatch.setattr(connections_module, "__file__", original_file)

    assert any("Picklist data not found" in line for line in capture_echo)


def test_pick_lists_invalid_json(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str], tmp_path: Path
) -> None:
    module_root = tmp_path / "cli" / "commands"
    data_dir = module_root.parent / "data"
    data_dir.mkdir(parents=True)
    invalid_file = data_dir / "picklist-data.json"
    invalid_file.write_text("not-json")

    original_file = connections_module.__file__
    monkeypatch.setattr(
        connections_module, "__file__", str(module_root / "connections.py")
    )

    assert connections_module.pick_lists.callback

    try:
        connections_module.pick_lists.callback()
    finally:
        monkeypatch.setattr(connections_module, "__file__", original_file)

    assert any("Failed to load picklist data" in line for line in capture_echo)
