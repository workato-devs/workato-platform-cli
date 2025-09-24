"""Unit tests for the projects CLI command module."""

from __future__ import annotations

import sys

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from workato_platform.cli.commands.projects import command
from workato_platform.cli.utils.config import ConfigData


@pytest.fixture(autouse=True)
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.click.echo",
        _capture,
    )
    return captured


@pytest.mark.asyncio
async def test_delete_requires_config(capture_echo: list[str]) -> None:
    config_manager = Mock()
    config_manager.load_config.return_value = ConfigData()

    await command.delete.callback(  # type: ignore[misc]
        config_manager=config_manager,
        project_manager=Mock(),
        workato_api_client=Mock(),
    )

    assert any("No project configured" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_delete_aborts_on_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    config_manager = Mock()
    config_manager.load_config.side_effect = [
        ConfigData(project_id=1, folder_id=2, project_name="Demo"),
        ConfigData(project_id=1, folder_id=2, project_name="Demo"),
    ]
    config_manager.save_config = Mock()

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.get_all_recipes_paginated",
        AsyncMock(return_value=[]),
    )
    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.click.confirm",
        lambda *_, **__: False,
    )

    project_manager = Mock(delete_project=AsyncMock())

    await command.delete.callback(  # type: ignore[misc]
        config_manager=config_manager,
        project_manager=project_manager,
        workato_api_client=Mock(),
    )

    project_manager.delete_project.assert_not_awaited()
    config_manager.save_config.assert_not_called()


@pytest.mark.asyncio
async def test_delete_handles_running_recipes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_manager = Mock()
    config_manager.load_config.side_effect = [
        ConfigData(project_id=10, folder_id=20, project_name="Demo"),
        ConfigData(project_id=10, folder_id=20, project_name="Demo"),
    ]
    config_manager.save_config = Mock()

    recipes = [
        SimpleNamespace(id=1, name="R1", running=True),
        SimpleNamespace(id=2, name="R2", running=False),
    ]
    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.get_all_recipes_paginated",
        AsyncMock(return_value=recipes),
    )
    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.click.confirm",
        lambda *_, **__: True,
    )

    recipes_api = SimpleNamespace(stop_recipe=AsyncMock())
    workato_client = SimpleNamespace(recipes_api=recipes_api)
    project_manager = Mock(delete_project=AsyncMock())

    monkeypatch.chdir(tmp_path)
    (tmp_path / "project").mkdir()

    await command.delete.callback(  # type: ignore[misc]
        config_manager=config_manager,
        project_manager=project_manager,
        workato_api_client=workato_client,
    )

    recipes_api.stop_recipe.assert_awaited_once_with(1)
    project_manager.delete_project.assert_awaited_once_with(10)
    assert config_manager.save_config.called


@pytest.mark.asyncio
async def test_list_projects_no_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    config_manager = Mock()
    config_manager.get_project_root.return_value = None
    config_manager.get_current_project_name.return_value = None

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        lambda *_, **__: Mock(load_config=lambda: ConfigData()),
    )

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects directory" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_list_projects_with_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    workspace = tmp_path
    projects_dir = workspace / "projects"
    alpha_workato = projects_dir / "alpha" / "workato"
    alpha_workato.mkdir(parents=True)
    (alpha_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"

    project_config = ConfigData(
        project_id=5, project_name="Alpha", folder_id=9, profile="default"
    )

    class StubConfigManager:
        def __init__(self, path: Path | None = None) -> None:
            self.path = path

        def load_config(self) -> ConfigData:
            return project_config

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    output = "\n".join(capture_echo)
    assert "alpha" in output
    assert "Folder ID" in output


@pytest.mark.asyncio
async def test_use_project_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    workspace = tmp_path
    workspace_config = ConfigData()

    project_dir = workspace / "projects" / "beta"
    project_workato = project_dir / "workato"
    project_workato.mkdir(parents=True)
    (project_workato / "config.json").write_text("{}")

    project_config = ConfigData(
        project_id=3, project_name="Beta", folder_id=7, profile="p1"
    )

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.load_config.return_value = workspace_config
    config_manager.save_config = Mock()

    class StubConfigManager:
        def __init__(self, path: Path | None = None) -> None:
            self.path = path

        def load_config(self) -> ConfigData:
            return project_config if self.path == project_workato else workspace_config

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    await command.use.callback(  # type: ignore[misc]
        project_name="beta",
        config_manager=config_manager,
    )

    saved = config_manager.save_config.call_args.args[0]
    assert saved.project_id == 3
    assert "Switched to project" in "\n".join(capture_echo)


@pytest.mark.asyncio
async def test_use_project_not_found(tmp_path: Path, capture_echo: list[str]) -> None:
    config_manager = Mock()
    config_manager.get_project_root.return_value = tmp_path

    await command.use.callback(project_name="missing", config_manager=config_manager)  # type: ignore[misc]

    assert any("not found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_interactive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    workspace = tmp_path
    beta_workato = workspace / "projects" / "beta" / "workato"
    beta_workato.mkdir(parents=True)
    (beta_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager.load_config.return_value = ConfigData()
    config_manager.save_config = Mock()

    selected_config = ConfigData(project_id=9, project_name="Beta", folder_id=11)

    class StubConfigManager:
        def __init__(self, path: Path | None = None) -> None:
            self.path = path

        def load_config(self) -> ConfigData:
            if self.path == beta_workato:
                return selected_config
            return ConfigData(project_name="alpha")

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: {"project": "beta (Beta)"},
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    config_manager.save_config.assert_called_once()
    assert "Switched to project 'beta'" in "\n".join(capture_echo)


@pytest.mark.asyncio
async def test_switch_keeps_current_when_only_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    workspace = tmp_path
    alpha_workato = workspace / "projects" / "alpha" / "workato"
    alpha_workato.mkdir(parents=True)
    (alpha_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"

    class StubConfigManager:
        def __init__(self, path: Path | None = None) -> None:
            self.path = path

        def load_config(self) -> ConfigData:
            return ConfigData(project_name="alpha")

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: None,
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("already current" in line for line in capture_echo)


def test_project_group_exists() -> None:
    """Test that the project group command exists."""
    assert callable(command.project)

    # Test that it's a click group
    import asyncclick as click

    assert isinstance(command.project, click.Group)


@pytest.mark.asyncio
async def test_list_projects_empty_directory(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list projects when projects directory exists but is empty."""
    workspace = tmp_path
    projects_dir = workspace / "projects"
    projects_dir.mkdir()  # Create empty projects directory

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_list_projects_config_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list projects when project has configuration error."""
    workspace = tmp_path
    projects_dir = workspace / "projects"
    alpha_workato = projects_dir / "alpha" / "workato"
    alpha_workato.mkdir(parents=True)
    (alpha_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None

    # Mock ConfigManager to raise exception
    def failing_config_manager(*args: Any, **kwargs: Any) -> Any:
        mock = Mock()
        mock.load_config.side_effect = Exception("Configuration error")
        return mock

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        failing_config_manager,
    )

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    output = "\n".join(capture_echo)
    assert "configuration error" in output


@pytest.mark.asyncio
async def test_list_projects_workspace_root_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list projects when workspace root is None, falls back to cwd."""
    monkeypatch.chdir(tmp_path)

    config_manager = Mock()
    config_manager.get_project_root.return_value = None  # Force fallback
    config_manager.get_current_project_name.return_value = None

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects directory" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_use_project_not_configured(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test use project when project exists but is not configured."""
    workspace = tmp_path
    project_dir = workspace / "projects" / "beta"
    project_dir.mkdir(parents=True)
    # No workato/config.json file created

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace

    await command.use.callback(  # type: ignore[misc]
        project_name="beta",
        config_manager=config_manager,
    )

    output = "\n".join(capture_echo)
    assert "is not configured" in output


@pytest.mark.asyncio
async def test_use_project_exception_handling(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test use project exception handling."""
    workspace = tmp_path
    project_dir = workspace / "projects" / "beta"
    project_workato = project_dir / "workato"
    project_workato.mkdir(parents=True)
    (project_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.load_config.side_effect = Exception(
        "Config error"
    )  # Force exception

    await command.use.callback(  # type: ignore[misc]
        project_name="beta",
        config_manager=config_manager,
    )

    output = "\n".join(capture_echo)
    assert "Failed to switch to project" in output


@pytest.mark.asyncio
async def test_switch_workspace_root_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when workspace root is None, falls back to cwd."""
    monkeypatch.chdir(tmp_path)

    config_manager = Mock()
    config_manager.get_project_root.return_value = None  # Force fallback
    config_manager.get_current_project_name.return_value = None

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects directory" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_no_projects_directory(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when no projects directory exists."""
    workspace = tmp_path
    # No projects directory created

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects directory" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_config_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command with configuration error."""
    workspace = tmp_path
    alpha_workato = workspace / "projects" / "alpha" / "workato"
    alpha_workato.mkdir(parents=True)
    (alpha_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None

    # Mock ConfigManager to raise exception
    def failing_config_manager(*args: Any, **kwargs: Any) -> Any:
        mock = Mock()
        mock.load_config.side_effect = Exception("Configuration error")
        return mock

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        failing_config_manager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: {"project": "alpha (configuration error)"},
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    output = "\n".join(capture_echo)
    assert "configuration errors" in output


@pytest.mark.asyncio
async def test_switch_no_configured_projects(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when no configured projects found."""
    workspace = tmp_path
    projects_dir = workspace / "projects"
    projects_dir.mkdir()
    # Create directory but no projects with config.json

    project_dir = projects_dir / "unconfigured"
    project_dir.mkdir()
    # No workato/config.json file created

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No configured projects" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_no_project_selected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when user cancels selection."""
    workspace = tmp_path
    alpha_workato = workspace / "projects" / "alpha" / "workato"
    alpha_workato.mkdir(parents=True)
    (alpha_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None

    class StubConfigManager:
        def __init__(self, path: Any) -> None:
            self.path = path

        def load_config(self) -> Any:
            return ConfigData(project_name="alpha")

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: None,  # User cancelled
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No project selected" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_failed_to_identify_project(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when selected project can't be identified."""
    workspace = tmp_path
    alpha_workato = workspace / "projects" / "alpha" / "workato"
    alpha_workato.mkdir(parents=True)
    (alpha_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None

    class StubConfigManager:
        def __init__(self, path: Any) -> None:
            self.path = path

        def load_config(self) -> Any:
            return ConfigData(project_name="alpha")

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: {"project": "nonexistent"},  # Select non-matching project
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("Failed to identify selected project" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_already_current(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when selected project is already current."""
    workspace = tmp_path
    alpha_workato = workspace / "projects" / "alpha" / "workato"
    alpha_workato.mkdir(parents=True)
    (alpha_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"  # Already current

    class StubConfigManager:
        def __init__(self, path: Any) -> None:
            self.path = path

        def load_config(self) -> Any:
            return ConfigData(project_name="alpha")

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: {"project": "alpha (current)"},
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("already current" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_exception_handling(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command exception handling."""
    workspace = tmp_path
    beta_workato = workspace / "projects" / "beta" / "workato"
    beta_workato.mkdir(parents=True)
    (beta_workato / "config.json").write_text("{}")

    config_manager = Mock()
    config_manager.get_project_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager.load_config.side_effect = Exception(
        "Config error"
    )  # Force exception

    selected_config = ConfigData(project_id=9, project_name="Beta", folder_id=11)

    class StubConfigManager:
        def __init__(self, path: Any) -> None:
            self.path = path

        def load_config(self) -> Any:
            if self.path == beta_workato:
                return selected_config
            return ConfigData(project_name="alpha")

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: {"project": "beta (Beta)"},
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    output = "\n".join(capture_echo)
    assert "Failed to switch to project" in output
