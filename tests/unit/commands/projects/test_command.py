"""Unit tests for the projects CLI command module."""

from __future__ import annotations

import json
import sys

from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

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
async def test_list_projects_no_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    config_manager = Mock()
    config_manager.get_workspace_root.return_value = tmp_path
    config_manager.get_current_project_name.return_value = None
    config_manager._find_all_projects.return_value = []  # No projects found

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_list_projects_with_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    workspace = tmp_path
    projects_dir = workspace / "projects"
    alpha_project = projects_dir / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text(
        '{"project_id": 5, "project_name": "Alpha", '
        '"folder_id": 9, "profile": "default"}',
    )

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager._find_all_projects.return_value = [(alpha_project, "alpha")]

    project_config = ConfigData(
        project_id=5, project_name="Alpha", folder_id=9, profile="default"
    )

    class StubConfigManager:
        def __init__(
            self, path: Path | None = None, skip_validation: bool = False
        ) -> None:
            self.path = path
            self.skip_validation = skip_validation

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
    project_dir.mkdir(parents=True)
    (project_dir / ".workatoenv").write_text(
        '{"project_id": 3, "project_name": "Beta", "folder_id": 7, "profile": "p1"}'
    )

    project_config = ConfigData(
        project_id=3, project_name="Beta", folder_id=7, profile="p1"
    )

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = [(project_dir, "beta")]
    config_manager.load_config.return_value = workspace_config
    config_manager.save_config = Mock()

    class StubConfigManager:
        def __init__(
            self, path: Path | None = None, skip_validation: bool = False
        ) -> None:
            self.path = path
            self.skip_validation = skip_validation

        def load_config(self) -> ConfigData:
            return project_config if self.path == project_dir else workspace_config

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
    assert saved.project_path == "projects/beta"
    assert "Switched to project" in "\n".join(capture_echo)


@pytest.mark.asyncio
async def test_use_project_not_found(tmp_path: Path, capture_echo: list[str]) -> None:
    config_manager = Mock()
    config_manager.get_workspace_root.return_value = tmp_path
    config_manager._find_all_projects.return_value = []  # No projects found

    await command.use.callback(project_name="missing", config_manager=config_manager)  # type: ignore[misc]

    assert any("not found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_interactive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    workspace = tmp_path
    beta_project = workspace / "projects" / "beta"
    beta_project.mkdir(parents=True)
    (beta_project / ".workatoenv").write_text(
        '{"project_id": 9, "project_name": "Beta", "folder_id": 11}'
    )

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager._find_all_projects.return_value = [
        (workspace / "alpha", "alpha"),
        (beta_project, "beta"),
    ]
    config_manager.load_config.return_value = ConfigData()
    config_manager.save_config = Mock()

    selected_config = ConfigData(
        project_id=9, project_name="Beta", folder_id=11, profile="default"
    )

    class StubConfigManager:
        def __init__(
            self, path: Path | None = None, skip_validation: bool = False
        ) -> None:
            self.path = path
            self.skip_validation = skip_validation

        def load_config(self) -> ConfigData:
            if self.path == beta_project:
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
    alpha_project = workspace / "projects" / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text('{"project_name": "alpha"}')

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager._find_all_projects.return_value = [(alpha_project, "alpha")]

    class StubConfigManager:
        def __init__(
            self, path: Path | None = None, skip_validation: bool = False
        ) -> None:
            self.path = path
            self.skip_validation = skip_validation

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
    assert callable(command.projects)

    # Test that it's a click group
    import asyncclick as click

    assert isinstance(command.projects, click.Group)
    assert command.projects.callback is not None
    assert command.projects.callback() is None


@pytest.mark.asyncio
async def test_list_projects_empty_directory(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list projects when projects directory exists but is empty."""
    workspace = tmp_path
    projects_dir = workspace / "projects"
    projects_dir.mkdir()  # Create empty projects directory

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None
    config_manager._find_all_projects.return_value = []  # Empty directory

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_list_projects_config_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list projects when project has configuration error."""
    workspace = tmp_path
    projects_dir = workspace / "projects"
    alpha_project = projects_dir / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text('{"project_name": "alpha"}')

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None
    config_manager._find_all_projects.return_value = [(alpha_project, "alpha")]

    # Mock ConfigManager to raise exception
    def failing_config_manager(*_: Any, **__: Any) -> Any:
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
async def test_list_projects_json_config_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """JSON mode should surface configuration errors."""

    workspace = tmp_path
    project_dir = workspace / "projects" / "alpha"
    project_dir.mkdir(parents=True)

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager._find_all_projects.return_value = [(project_dir, "alpha")]

    def failing_config_manager(*_: Any, **__: Any) -> Any:
        mock = Mock()
        mock.load_config.side_effect = Exception("broken")
        return mock

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        failing_config_manager,
    )

    await command.list_projects.callback(  # type: ignore[misc]
        output_mode="json", config_manager=config_manager
    )

    assert capture_echo, "Expected JSON output"
    data = json.loads("".join(capture_echo))
    assert data["projects"][0]["configured"] is False
    assert "configuration error" in data["projects"][0]["error"]


@pytest.mark.asyncio
async def test_list_projects_workspace_root_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list projects when workspace root is None, falls back to cwd."""
    monkeypatch.chdir(tmp_path)

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = Path.cwd()
    config_manager._find_all_projects.return_value = []  # Force fallback
    config_manager.get_current_project_name.return_value = None

    await command.list_projects.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_use_project_not_configured(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test use project when project exists but is not configured."""
    workspace = tmp_path
    project_dir = workspace / "projects" / "beta"
    project_dir.mkdir(parents=True)
    # No .workatoenv file created

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = [(project_dir, "beta")]

    # Mock ConfigManager to raise exception for unconfigured project
    def failing_config_manager(*_: Any, **__: Any) -> Any:
        mock = Mock()
        mock.load_config.side_effect = Exception("Configuration error")
        return mock

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        failing_config_manager,
    )

    await command.use.callback(  # type: ignore[misc]
        project_name="beta",
        config_manager=config_manager,
    )

    output = "\n".join(capture_echo)
    assert "configuration errors" in output


@pytest.mark.asyncio
async def test_use_project_exception_handling(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test use project exception handling."""
    workspace = tmp_path
    project_dir = workspace / "projects" / "beta"
    project_dir.mkdir(parents=True)
    (project_dir / ".workatoenv").write_text(
        '{"project_id": 3, "project_name": "Beta", "folder_id": 7}'
    )

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = [(project_dir, "beta")]
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
    config_manager.get_workspace_root.return_value = Path.cwd()
    config_manager._find_all_projects.return_value = []  # Force fallback
    config_manager.get_current_project_name.return_value = None

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_no_projects_directory(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when no projects directory exists."""
    workspace = tmp_path
    # No projects directory created

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = []
    config_manager.get_current_project_name.return_value = None

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_config_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command with configuration error."""
    workspace = tmp_path
    alpha_project = workspace / "projects" / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text('{"project_name": "alpha"}')

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = [(alpha_project, "alpha")]
    config_manager.get_current_project_name.return_value = None

    # Mock ConfigManager to raise exception
    def failing_config_manager(*_: Any, **__: Any) -> Any:
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
async def test_switch_config_error_current_project(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Config errors on the current project should report already current."""

    workspace = tmp_path
    alpha_project = workspace / "projects" / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text('{"project_name": "alpha"}')

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = [(alpha_project, "alpha")]
    config_manager.get_current_project_name.return_value = "alpha"

    def failing_config_manager(*_: Any, **__: Any) -> Any:
        mock = Mock()
        mock.load_config.side_effect = Exception("Configuration error")
        return mock

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        failing_config_manager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: {"project": "alpha (configuration error) (current)"},
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    output = "\n".join(capture_echo)
    assert "already current" in output


@pytest.mark.asyncio
async def test_switch_no_configured_projects(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when no configured projects found."""
    workspace = tmp_path
    projects_dir = workspace / "projects"
    projects_dir.mkdir()
    # Create directory but no projects with .workatoenv

    project_dir = projects_dir / "unconfigured"
    project_dir.mkdir()
    # No .workatoenv file created

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = []  # No configured projects
    config_manager.get_current_project_name.return_value = None

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No projects found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_no_project_choices_after_iteration(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Guard clause should trigger when iteration yields nothing."""

    class TruthyEmpty:
        def __iter__(self) -> Iterator[tuple[Path, str]]:
            return iter(())

        def __bool__(self) -> bool:
            return True

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = tmp_path
    config_manager._find_all_projects.return_value = TruthyEmpty()
    config_manager.get_current_project_name.return_value = None

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("No configured projects" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_no_project_selected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command when user cancels selection."""
    workspace = tmp_path
    alpha_project = workspace / "projects" / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text('{"project_name": "alpha"}')

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = [(alpha_project, "alpha")]
    config_manager.get_current_project_name.return_value = None

    class StubConfigManager:
        def __init__(self, path: Any, skip_validation: bool = False) -> None:
            self.path = path
            self.skip_validation = skip_validation

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
    alpha_project = workspace / "projects" / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text('{"project_name": "alpha"}')

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager._find_all_projects.return_value = [(alpha_project, "alpha")]
    config_manager.get_current_project_name.return_value = None

    class StubConfigManager:
        def __init__(self, path: Any, skip_validation: bool = False) -> None:
            self.path = path
            self.skip_validation = skip_validation

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
    alpha_project = workspace / "projects" / "alpha"
    alpha_project.mkdir(parents=True)
    (alpha_project / ".workatoenv").write_text('{"project_name": "alpha"}')
    beta_project = workspace / "projects" / "beta"
    beta_project.mkdir(parents=True)
    (beta_project / ".workatoenv").write_text('{"project_name": "beta"}')

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager._find_all_projects.return_value = [
        (alpha_project, "alpha"),
        (beta_project, "beta"),
    ]

    class StubConfigManager:
        def __init__(self, path: Any, skip_validation: bool = False) -> None:
            self.path = path
            self.skip_validation = skip_validation

        def load_config(self) -> Any:
            if self.path == alpha_project:
                return ConfigData(project_name="alpha")
            return ConfigData(project_name="beta")

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
async def test_switch_missing_project_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """If the project list becomes stale, path lookup should fail gracefully."""

    workspace = tmp_path
    beta_project = workspace / "projects" / "beta"
    beta_project.mkdir(parents=True)

    class OneShot:
        def __init__(self, entry: tuple[Path, str]) -> None:
            self.entry = entry
            self.iterations = 0

        def __iter__(self) -> Iterator[tuple[Path, str]]:
            if self.iterations == 0:
                self.iterations += 1
                return iter([self.entry])
            return iter(())

        def __bool__(self) -> bool:
            return True

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = None
    config_manager._find_all_projects.return_value = OneShot((beta_project, "beta"))

    class StubConfigManager:
        def __init__(self, path: Any, skip_validation: bool = False) -> None:
            self.path = path

        def load_config(self) -> ConfigData:
            return ConfigData(project_name="Beta Display")

    monkeypatch.setattr(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        StubConfigManager,
    )

    stub_inquirer = SimpleNamespace(
        List=lambda *args, **kwargs: SimpleNamespace(),
        prompt=lambda *_: {"project": "beta (Beta Display)"},
    )
    monkeypatch.setitem(sys.modules, "inquirer", stub_inquirer)

    await command.switch.callback(config_manager=config_manager)  # type: ignore[misc]

    assert any("Failed to find path" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_switch_exception_handling(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test switch command exception handling."""
    workspace = tmp_path
    beta_project = workspace / "projects" / "beta"
    beta_project.mkdir(parents=True)
    (beta_project / ".workatoenv").write_text(
        '{"project_id": 9, "project_name": "Beta", "folder_id": 11}'
    )

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace
    config_manager.get_current_project_name.return_value = "alpha"
    config_manager._find_all_projects.return_value = [
        (workspace / "alpha", "alpha"),
        (beta_project, "beta"),
    ]
    config_manager.load_config.side_effect = Exception(
        "Config error"
    )  # Force exception

    selected_config = ConfigData(project_id=9, project_name="Beta", folder_id=11)

    class StubConfigManager:
        def __init__(self, path: Any, skip_validation: bool = False) -> None:
            self.path = path
            self.skip_validation = skip_validation

        def load_config(self) -> Any:
            if self.path == beta_project:
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


@pytest.mark.asyncio
async def test_list_projects_json_output_mode(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list_projects with JSON output mode."""
    workspace_root = tmp_path / "workspace"
    project_path = workspace_root / "test-project"

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace_root
    config_manager.get_current_project_name.return_value = "test-project"
    config_manager._find_all_projects.return_value = [(project_path, "test-project")]

    # Mock project config manager
    project_config = ConfigData(
        project_id=123, project_name="Test Project", folder_id=456, profile="dev"
    )
    mock_project_config_manager = Mock()
    mock_project_config_manager.load_config.return_value = project_config

    with patch(
        "workato_platform.cli.commands.projects.command.ConfigManager",
        return_value=mock_project_config_manager,
    ):
        assert command.list_projects.callback
        await command.list_projects.callback(
            output_mode="json", config_manager=config_manager
        )

    output = "\n".join(capture_echo)

    # Parse JSON output
    import json

    parsed = json.loads(output)

    assert parsed["current_project"] == "test-project"
    assert len(parsed["projects"]) == 1
    project = parsed["projects"][0]
    assert project["name"] == "test-project"
    assert project["is_current"] is True
    assert project["project_id"] == 123
    assert project["folder_id"] == 456
    assert project["profile"] == "dev"
    assert project["configured"] is True


@pytest.mark.asyncio
async def test_list_projects_json_output_mode_empty(
    tmp_path: Path, capture_echo: list[str]
) -> None:
    """Test list_projects JSON output with no projects."""
    workspace_root = tmp_path / "workspace"

    config_manager = Mock()
    config_manager.get_workspace_root.return_value = workspace_root
    config_manager.get_current_project_name.return_value = None
    config_manager._find_all_projects.return_value = []

    assert command.list_projects.callback
    await command.list_projects.callback(
        output_mode="json", config_manager=config_manager
    )

    output = "\n".join(capture_echo)

    # Parse JSON output
    import json

    parsed = json.loads(output)

    assert parsed["current_project"] is None
    assert parsed["projects"] == []
