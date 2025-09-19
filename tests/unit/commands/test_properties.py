"""Tests for the properties command group."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from workato_platform.cli.commands.properties import list_properties, properties, upsert_properties
from workato_platform.cli.utils.config import ConfigData


class DummySpinner:
    """Minimal spinner stub for testing."""

    def __init__(self, _message: str) -> None:
        self._stopped = False

    def start(self) -> None:
        pass

    def stop(self) -> float:
        self._stopped = True
        return 0.5


@pytest.mark.asyncio
async def test_list_properties_success(monkeypatch):
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(
        project_id=101,
        project_name="Demo",
    )

    props = {"admin_email": "user@example.com"}
    client = Mock()
    client.properties_api.list_project_properties = AsyncMock(return_value=props)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    await list_properties.callback(
        prefix="admin",
        project_id=None,
        workato_api_client=client,
        config_manager=config_manager,
    )

    output = "\n".join(captured)
    assert "admin_email" in output
    assert "101" in output
    client.properties_api.list_project_properties.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_properties_missing_project(monkeypatch):
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData()

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    result = await list_properties.callback(
        prefix="admin",
        project_id=None,
        workato_api_client=Mock(),
        config_manager=config_manager,
    )

    assert "No project ID provided" in "\n".join(captured)
    assert result is None


@pytest.mark.asyncio
async def test_upsert_properties_invalid_format(monkeypatch):
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(project_id=5)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    await upsert_properties.callback(
        project_id=None,
        property_pairs=("invalid",),
        workato_api_client=Mock(),
        config_manager=config_manager,
    )

    assert "Invalid property format" in "\n".join(captured)


@pytest.mark.asyncio
async def test_upsert_properties_success(monkeypatch):
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(project_id=77)

    response = SimpleNamespace(success=True)

    client = Mock()
    client.properties_api.upsert_project_properties = AsyncMock(return_value=response)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    await upsert_properties.callback(
        project_id=None,
        property_pairs=("admin_email=user@example.com",),
        workato_api_client=client,
        config_manager=config_manager,
    )

    text = "\n".join(captured)
    assert "Properties upserted successfully" in text
    assert "admin_email" in text
    client.properties_api.upsert_project_properties.assert_awaited_once()


@pytest.mark.asyncio
async def test_upsert_properties_failure(monkeypatch):
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(project_id=77)

    response = SimpleNamespace(success=False)

    client = Mock()
    client.properties_api.upsert_project_properties = AsyncMock(return_value=response)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    await upsert_properties.callback(
        project_id=None,
        property_pairs=("admin_email=user@example.com",),
        workato_api_client=client,
        config_manager=config_manager,
    )

    assert any("Failed to upsert properties" in line for line in captured)


@pytest.mark.asyncio
async def test_list_properties_empty_result(monkeypatch):
    """Test list properties when no properties are found."""
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(project_id=101)

    # Empty properties dict
    props = {}
    client = Mock()
    client.properties_api.list_project_properties = AsyncMock(return_value=props)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    await list_properties.callback(
        prefix="admin",
        project_id=None,
        workato_api_client=client,
        config_manager=config_manager,
    )

    output = "\n".join(captured)
    assert "No properties found" in output


@pytest.mark.asyncio
async def test_upsert_properties_missing_project(monkeypatch):
    """Test upsert properties when no project ID is provided."""
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData()  # No project_id

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    await upsert_properties.callback(
        project_id=None,
        property_pairs=("key=value",),
        workato_api_client=Mock(),
        config_manager=config_manager,
    )

    output = "\n".join(captured)
    assert "No project ID provided" in output


@pytest.mark.asyncio
async def test_upsert_properties_no_properties(monkeypatch):
    """Test upsert properties when no properties are provided."""
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(project_id=123)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    await upsert_properties.callback(
        project_id=None,
        property_pairs=(),  # Empty tuple - no properties
        workato_api_client=Mock(),
        config_manager=config_manager,
    )

    output = "\n".join(captured)
    assert "No properties provided" in output


@pytest.mark.asyncio
async def test_upsert_properties_name_too_long(monkeypatch):
    """Test upsert properties with property name that's too long."""
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(project_id=123)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    # Create a property name longer than 100 characters
    long_name = "x" * 101

    await upsert_properties.callback(
        project_id=None,
        property_pairs=(f"{long_name}=value",),
        workato_api_client=Mock(),
        config_manager=config_manager,
    )

    output = "\n".join(captured)
    assert "Property name too long" in output


@pytest.mark.asyncio
async def test_upsert_properties_value_too_long(monkeypatch):
    """Test upsert properties with property value that's too long."""
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.Spinner",
        DummySpinner,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData(project_id=123)

    captured: list[str] = []
    monkeypatch.setattr(
        "workato_platform.cli.commands.properties.click.echo",
        lambda msg="": captured.append(msg),
    )

    # Create a property value longer than 1024 characters
    long_value = "x" * 1025

    await upsert_properties.callback(
        project_id=None,
        property_pairs=(f"key={long_value}",),
        workato_api_client=Mock(),
        config_manager=config_manager,
    )

    output = "\n".join(captured)
    assert "Property value too long" in output


def test_properties_group_exists():
    """Test that the properties group command exists."""
    assert callable(properties)

    # Test that it's a click group
    import asyncclick as click
    assert isinstance(properties, click.Group)
