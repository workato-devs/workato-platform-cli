"""Unit tests for the ProjectManager command helper."""

from __future__ import annotations

import subprocess
import zipfile

from pathlib import Path
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from workato_platform_cli.cli.commands.projects.project_manager import ProjectManager
from workato_platform_cli.client.workato_api.models.project import Project


class DummySpinner:
    """Minimal spinner stub to avoid timing noise."""

    def __init__(self, message: str) -> None:
        self.message = message
        self.stopped = False

    def start(self) -> None:
        pass

    def stop(self) -> float:
        self.stopped = True
        return 0.3

    def update_message(self, message: str) -> None:
        self.message = message


@pytest.fixture(autouse=True)
def patch_spinner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch spinner globally for deterministic tests."""

    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.projects.project_manager.Spinner",
        DummySpinner,
    )


@pytest.fixture
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.projects.project_manager.click.echo",
        _capture,
    )
    return captured


@pytest.fixture
def project_manager() -> ProjectManager:
    client = Mock()  # Use regular Mock instead of spec=Workato
    return ProjectManager(workato_api_client=client)


def make_project(idx: int, folder_id: int | None = None) -> Project:
    return Project(
        id=idx,
        name=f"Project {idx}",
        folder_id=folder_id or 1,  # Default to 1 if None since folder_id is required
        description="",
    )


@pytest.mark.asyncio
async def test_get_projects_delegates_to_client(
    project_manager: ProjectManager,
) -> None:
    with patch.object(
        project_manager.client.projects_api,
        "list_projects",
        AsyncMock(return_value=[make_project(1)]),
    ) as mock_list_projects:
        result = await project_manager.get_projects(page=2, per_page=55)

        mock_list_projects.assert_awaited_once_with(page=2, per_page=55)
        assert result == [make_project(1)]


@pytest.mark.asyncio
async def test_get_all_projects_aggregates_pages(
    project_manager: ProjectManager,
) -> None:
    first_page = [make_project(idx) for idx in range(1, 101)]
    second_page = [make_project(200)]
    pages = [first_page, second_page]
    with patch.object(
        project_manager, "get_projects", AsyncMock(side_effect=pages)
    ) as mock_get_projects:
        result = await project_manager.get_all_projects()

        assert [p.id for p in result] == list(range(1, 101)) + [200]
        mock_get_projects.assert_has_awaits([call(1, 100), call(2, 100)])


@pytest.mark.asyncio
async def test_create_project_returns_existing_match(
    project_manager: ProjectManager,
) -> None:
    folder = Mock(id=99)
    existing = make_project(55, folder_id=99)

    with (
        patch.object(
            project_manager.client.folders_api,
            "create_folder",
            AsyncMock(return_value=folder),
        ),
        patch.object(
            project_manager, "get_all_projects", AsyncMock(return_value=[existing])
        ) as mock_get_all_projects,
    ):
        result = await project_manager.create_project("Test")

        assert result is existing
        mock_get_all_projects.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_project_returns_synthetic_when_missing(
    project_manager: ProjectManager,
) -> None:
    folder = Mock(id=77)

    with (
        patch.object(
            project_manager.client.folders_api,
            "create_folder",
            AsyncMock(return_value=folder),
        ),
        patch.object(project_manager, "get_all_projects", AsyncMock(return_value=[])),
    ):
        result = await project_manager.create_project("My Project")

        assert result.id == 77
        assert result.name == "My Project"
        assert result.folder_id == 77


@pytest.mark.asyncio
async def test_check_folder_assets_handles_missing(
    project_manager: ProjectManager,
) -> None:
    empty_response = Mock(result=None)

    with patch.object(
        project_manager.client.export_api,
        "list_assets_in_folder",
        AsyncMock(return_value=empty_response),
    ):
        assets = await project_manager.check_folder_assets(3)

        assert assets == []


@pytest.mark.asyncio
async def test_export_project_short_circuits_for_empty_folder(
    project_manager: ProjectManager,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    with (
        patch.object(
            project_manager, "check_folder_assets", AsyncMock(return_value=[])
        ),
        patch.object(
            project_manager.client.export_api, "create_export_manifest", AsyncMock()
        ) as mock_create_export_manifest,
    ):
        result = await project_manager.export_project(1, "Empty", target_dir="out")

        assert Path(result or "").exists()
        assert any("Project is empty" in line for line in capture_echo)
        mock_create_export_manifest.assert_not_called()


@pytest.mark.asyncio
async def test_export_project_happy_path(
    project_manager: ProjectManager, tmp_path: Path
) -> None:
    manifest = Mock(result=Mock(id=88))
    project_dir = tmp_path / "extracted"

    with (
        patch.object(
            project_manager, "check_folder_assets", AsyncMock(return_value=[Mock()])
        ),
        patch.object(
            project_manager.client.export_api,
            "create_export_manifest",
            AsyncMock(return_value=manifest),
        ) as mock_create_manifest,
        patch.object(
            project_manager.client.packages_api,
            "export_package",
            AsyncMock(return_value=Mock(id=44)),
        ) as mock_export_package,
        patch.object(
            project_manager,
            "download_and_extract_package",
            AsyncMock(return_value=project_dir),
        ) as mock_download_extract,
    ):
        result = await project_manager.export_project(
            folder_id=9,
            project_name="Demo",
            target_dir=str(project_dir),
        )

        mock_create_manifest.assert_awaited_once()
        mock_export_package.assert_awaited_once_with(id="88")
        mock_download_extract.assert_awaited_once_with(44, str(project_dir))
        assert result == str(project_dir)


@pytest.mark.asyncio
async def test_download_and_extract_package_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = Mock()
    client.packages_api = Mock()
    client.packages_api.get_package = AsyncMock(
        side_effect=[
            Mock(status="processing"),
            Mock(status="completed"),
        ]
    )
    client.packages_api.download_package = AsyncMock(
        return_value=b"PK\x03\x04" + b"test" * 10
    )

    manager = ProjectManager(client)

    fake_time = Mock(side_effect=[0, 10, 20, 30])
    monkeypatch.setattr("time.time", fake_time)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    target_dir = tmp_path / "project"
    monkeypatch.chdir(tmp_path)

    with zipfile.ZipFile(tmp_path / "dummy.zip", "w") as zf:
        zip_info = zipfile.ZipInfo("file.txt")
        zip_info.date_time = (2024, 1, 1, 0, 0, 0)
        zf.writestr(zip_info, "data")
    data = (tmp_path / "dummy.zip").read_bytes()

    with patch.object(
        manager.client.packages_api, "download_package", AsyncMock(return_value=data)
    ) as mock_download_package:
        result = await manager.download_and_extract_package(
            12, target_dir=str(target_dir)
        )

        client.packages_api.get_package.assert_awaited()
        mock_download_package.assert_awaited_once_with(package_id=12)
        assert result == target_dir
        assert (target_dir / "file.txt").exists()


@pytest.mark.asyncio
async def test_download_and_extract_package_handles_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    client = Mock()
    client.packages_api = Mock()
    client.packages_api.get_package = AsyncMock(
        return_value=Mock(
            status="failed",
            error="boom",
            recipe_status=["detail1"],
        )
    )
    client.packages_api.download_package = AsyncMock()

    manager = ProjectManager(client)

    monkeypatch.setattr("time.time", Mock(side_effect=[0, 1, 2]))
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    result = await manager.download_and_extract_package(7, target_dir=str(tmp_path))

    assert result is None
    assert any("Package export failed" in line for line in capture_echo)
    client.packages_api.download_package.assert_not_called()


@pytest.mark.asyncio
async def test_download_and_extract_package_times_out(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    client = Mock()
    client.packages_api = Mock()
    client.packages_api.get_package = AsyncMock(return_value=Mock(status="processing"))
    client.packages_api.download_package = AsyncMock()

    manager = ProjectManager(client)

    fake_time = Mock(side_effect=[0, 100, 200, 400, 600])
    monkeypatch.setattr("time.time", fake_time)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    result = await manager.download_and_extract_package(3, target_dir=str(tmp_path))

    assert result is None
    assert any("Package still processing" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_handle_post_api_sync_success(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    client = Mock()
    manager = ProjectManager(client)
    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.projects.project_manager.subprocess.run",
        Mock(return_value=Mock(returncode=0, stderr="")),
    )

    await manager.handle_post_api_sync()

    assert any("Project synced successfully" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_handle_post_api_sync_timeout(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    client = Mock()
    manager = ProjectManager(client)
    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.projects.project_manager.subprocess.run",
        Mock(side_effect=subprocess.TimeoutExpired(cmd="workato", timeout=30)),
    )

    await manager.handle_post_api_sync()

    assert any("Sync timed out" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_delete_project_delegates(project_manager: ProjectManager) -> None:
    with patch.object(
        project_manager.client.projects_api, "delete_project", AsyncMock()
    ) as mock_delete_project:
        await project_manager.delete_project(99)

        mock_delete_project.assert_awaited_once_with(project_id=99)


def test_save_project_to_config(monkeypatch: pytest.MonkeyPatch) -> None:
    # Use a real ProjectManager with mocked client
    client = Mock()
    manager = ProjectManager(client)

    config_manager = Mock()
    config_manager.load_config.return_value = Mock()

    monkeypatch.setattr(
        "workato_platform_cli.cli.utils.config.ConfigManager",
        Mock(return_value=config_manager),
    )

    project = make_project(1, folder_id=5)
    manager.save_project_to_config(project)

    assert config_manager.save_config.called
    saved_meta = config_manager.save_config.call_args.args[0]
    assert saved_meta.project_id == 1
    assert saved_meta.folder_id == 5


@pytest.mark.asyncio
async def test_import_existing_project_workflow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    projects = [make_project(1, folder_id=10), make_project(2, folder_id=None)]
    client = Mock()
    client.projects_api = Mock()
    client.projects_api.list_projects = AsyncMock(return_value=projects)

    manager = ProjectManager(client)

    monkeypatch.setattr(
        "workato_platform_cli.cli.commands.projects.project_manager.inquirer.prompt",
        lambda *_: {"project": manager._format_project_display(projects[0])},
    )

    with (
        patch.object(manager, "save_project_to_config", Mock()) as mock_save_config,
        patch.object(manager, "export_project", AsyncMock()) as mock_export_project,
    ):
        selected = await manager.import_existing_project()

        assert selected is not None
        assert selected.id == 1
        mock_save_config.assert_called_once_with(projects[0])
        mock_export_project.assert_awaited_once_with(
            folder_id=10,
            project_name=projects[0].name,
        )


@pytest.mark.asyncio
async def test_import_existing_project_no_projects(
    monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]
) -> None:
    client = Mock()
    client.projects_api = Mock()
    client.projects_api.list_projects = AsyncMock(return_value=[])

    manager = ProjectManager(client)

    result = await manager.import_existing_project()

    assert result is None
    assert any("No projects found" in line for line in capture_echo)
