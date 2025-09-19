"""Tests for the assets command."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from workato_platform.cli.commands.assets import assets
from workato_platform.cli.utils.config import ConfigData


class DummySpinner:
    def __init__(self, _message: str) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> float:
        return 0.25


@pytest.mark.asyncio
async def test_assets_lists_grouped_results(monkeypatch):
    monkeypatch.setattr(
        "workato_platform.cli.commands.assets.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(folder_id=55)

    asset1 = SimpleNamespace(type="data_table", name="Table A", id=1)
    asset2 = SimpleNamespace(type="data_table", name="Table B", id=2)
    asset3 = SimpleNamespace(type="custom_connector", name="Connector", id=3)

    response = SimpleNamespace(result=SimpleNamespace(assets=[asset1, asset2, asset3]))
    workato_client = Mock()
    workato_client.export_api.list_assets_in_folder = AsyncMock(return_value=response)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.assets.click.echo",
        lambda msg="": captured.append(msg),
    )

    await assets.callback(
        folder_id=None,
        config_manager=config_manager,
        workato_api_client=workato_client,
    )

    output = "\n".join(captured)
    assert "Table A" in output and "Connector" in output
    workato_client.export_api.list_assets_in_folder.assert_awaited_once_with(
        folder_id=55,
    )


@pytest.mark.asyncio
async def test_assets_missing_folder(monkeypatch):
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData()

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.assets.click.echo",
        lambda msg="": captured.append(msg),
    )

    await assets.callback(
        folder_id=None,
        config_manager=config_manager,
        workato_api_client=Mock(),
    )

    assert "No folder ID provided" in "".join(captured)
