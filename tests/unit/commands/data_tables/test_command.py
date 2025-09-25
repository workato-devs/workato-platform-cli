"""Tests for data tables CLI commands."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock, Mock, patch

import pytest

from workato_platform.cli.commands.data_tables import (
    create_data_table,
    create_table,
    display_table_summary,
    list_data_tables,
    validate_schema,
)
from workato_platform.client.workato_api.models.data_table_column_request import (
    DataTableColumnRequest,
)


if TYPE_CHECKING:
    from workato_platform import Workato
    from workato_platform.client.workato_api.models.data_table import DataTable


def _get_callback(cmd: Any) -> Callable[..., Any]:
    callback = cmd.callback
    assert callback is not None
    return cast(Callable[..., Any], callback)


def _workato_stub(**kwargs: Any) -> Workato:
    return cast("Workato", Mock(**kwargs))


class DummySpinner:
    def __init__(self, _message: str) -> None:
        self.message = _message
        self.stopped = False

    def start(self) -> None:
        pass

    def stop(self) -> float:
        self.stopped = True
        return 0.1

    def update_message(self, message: str) -> None:
        self.message = message


@pytest.fixture(autouse=True)
def patch_spinner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "workato_platform.cli.commands.data_tables.Spinner",
        DummySpinner,
    )


@pytest.fixture(autouse=True)
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform.cli.commands.data_tables.click.echo",
        _capture,
    )
    return captured


@pytest.mark.asyncio
async def test_list_data_tables_empty(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    workato_client = _workato_stub(
        data_tables_api=Mock(list_data_tables=AsyncMock(return_value=Mock(data=[])))
    )

    list_cb = _get_callback(list_data_tables)
    await list_cb(workato_api_client=workato_client)

    output = "\n".join(capture_echo)
    assert "No data tables found" in output


@pytest.mark.asyncio
async def test_list_data_tables_with_entries(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    col1 = Mock()
    col1.name = "col"
    col1.type = "string"

    col2 = Mock()
    col2.name = "amt"
    col2.type = "number"

    table = Mock(
        name="Sales",
        id=5,
        folder_id=99,
        var_schema=[col1, col2],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
    )
    workato_client = _workato_stub(
        data_tables_api=Mock(
            list_data_tables=AsyncMock(return_value=Mock(data=[table]))
        )
    )

    list_cb = _get_callback(list_data_tables)
    await list_cb(workato_api_client=workato_client)

    output = "\n".join(capture_echo)
    assert "Sales" in output
    assert "Columns (2)" in output


@pytest.mark.asyncio
async def test_create_data_table_missing_schema(capture_echo: list[str]) -> None:
    create_cb = _get_callback(create_data_table)
    await create_cb(name="Table", schema_json=None, config_manager=Mock())
    assert any("Schema is required" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_data_table_no_folder(capture_echo: list[str]) -> None:
    config_manager = Mock()

    with patch.object(config_manager, "load_config", return_value=Mock(folder_id=None)):
        create_cb = _get_callback(create_data_table)
        await create_cb(name="Table", schema_json="[]", config_manager=config_manager)

        assert any("No folder ID" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_data_table_invalid_json(capture_echo: list[str]) -> None:
    config_manager = Mock()

    with patch.object(config_manager, "load_config", return_value=Mock(folder_id=1)):
        create_cb = _get_callback(create_data_table)
        await create_cb(
            name="Table", schema_json="{invalid}", config_manager=config_manager
        )

        assert any("Invalid JSON" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_data_table_invalid_schema_type(capture_echo: list[str]) -> None:
    config_manager = Mock()

    with patch.object(config_manager, "load_config", return_value=Mock(folder_id=1)):
        create_cb = _get_callback(create_data_table)
        await create_cb(name="Table", schema_json="{}", config_manager=config_manager)

        assert any("Schema must be an array" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_data_table_validation_errors(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    config_manager = Mock()

    with patch.object(config_manager, "load_config", return_value=Mock(folder_id=1)):
        monkeypatch.setattr(
            "workato_platform.cli.commands.data_tables.validate_schema",
            lambda schema: ["Error"],
        )

        create_cb = _get_callback(create_data_table)
        await create_cb(name="Table", schema_json="[]", config_manager=config_manager)

        assert any("Schema validation failed" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_create_data_table_success(monkeypatch: pytest.MonkeyPatch) -> None:
    config_manager = Mock()

    with patch.object(config_manager, "load_config", return_value=Mock(folder_id=1)):
        monkeypatch.setattr(
            "workato_platform.cli.commands.data_tables.validate_schema",
            lambda schema: [],
        )
        create_table_mock = AsyncMock()
        monkeypatch.setattr(
            "workato_platform.cli.commands.data_tables.create_table",
            create_table_mock,
        )

        create_cb = _get_callback(create_data_table)
        await create_cb(name="Table", schema_json="[]", config_manager=config_manager)

        create_table_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_table_calls_api(capture_echo: list[str]) -> None:
    connections = _workato_stub(
        data_tables_api=Mock(
            create_data_table=AsyncMock(
                return_value=Mock(
                    data=Mock(
                        name="Table",
                        id=3,
                        folder_id=4,
                        var_schema=[
                            type("MockCol", (), {"name": "a"})(),
                            type("MockCol", (), {"name": "b"})(),
                            type("MockCol", (), {"name": "c"})(),
                            type("MockCol", (), {"name": "d"})(),
                            type("MockCol", (), {"name": "e"})(),
                            type("MockCol", (), {"name": "f"})(),
                        ],
                    )
                )
            )
        )
    )
    project_manager = Mock(handle_post_api_sync=AsyncMock())

    schema = [DataTableColumnRequest(name="col", type="string", optional=False)]
    create_table_fn = cast(Any, create_table).__wrapped__
    await create_table_fn(
        name="Table",
        folder_id=4,
        schema=schema,
        workato_api_client=connections,
        project_manager=project_manager,
    )

    project_manager.handle_post_api_sync.assert_awaited_once()
    output = "\n".join(capture_echo)
    assert "Data table created" in output


def test_validate_schema_errors() -> None:
    errors = validate_schema(
        [
            {"type": "unknown", "optional": "yes"},
            {
                "name": "id",
                "type": "relation",
                "optional": True,
                "relation": {"table_id": 123},
            },
            {
                "name": "flag",
                "type": "boolean",
                "optional": False,
                "default_value": "yes",
            },
        ]
    )

    assert any("name" in err for err in errors)
    assert any("type" in err for err in errors)
    assert any("optional" in err for err in errors)
    assert any("relation" in err for err in errors)
    assert any("default_value" in err for err in errors)


def test_validate_schema_success() -> None:
    schema = [
        {
            "name": "id",
            "type": "integer",
            "optional": False,
            "default_value": 1,
        }
    ]

    assert validate_schema(schema) == []


def test_display_table_summary(capture_echo: list[str]) -> None:
    table = Mock(
        name="Table",
        id=1,
        folder_id=2,
        var_schema=[
            type("MockCol", (), {"name": "a", "type": "string"})(),
            type("MockCol", (), {"name": "b", "type": "string"})(),
            type("MockCol", (), {"name": "c", "type": "number"})(),
            type("MockCol", (), {"name": "d", "type": "string"})(),
        ],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
    )

    display_table_summary(cast("DataTable", table))

    output = "\n".join(capture_echo)
    assert "Table" in output
    assert "Columns (4)" in output
    assert "Types" in output
