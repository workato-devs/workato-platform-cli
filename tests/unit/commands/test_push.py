"""Unit tests for the push command module."""

from __future__ import annotations

import zipfile

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from workato_platform import Workato
from workato_platform.cli.commands import push


class DummySpinner:
    """Simple spinner stub used to avoid timing dependencies in tests."""

    def __init__(self, _message: str) -> None:
        self.message = _message
        self._stopped = False

    def start(self) -> None:  # pragma: no cover - no behaviour to test
        pass

    def stop(self) -> float:
        self._stopped = True
        return 0.4

    def update_message(self, message: str) -> None:
        self.message = message


@pytest.fixture(autouse=True)
def patch_spinner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure spinner usage is deterministic across tests."""

    monkeypatch.setattr(
        "workato_platform.cli.commands.push.Spinner",
        DummySpinner,
    )


@pytest.fixture
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Capture click output for assertions."""

    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform.cli.commands.push.click.echo",
        _capture,
    )

    return captured


@pytest.mark.asyncio
async def test_push_requires_api_token(capture_echo: list[str]) -> None:
    config_manager = Mock()
    config_manager.api_token = None

    assert push.push.callback
    await push.push.callback(config_manager=config_manager)

    assert any("No API token" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_push_requires_project_configuration(capture_echo: list[str]) -> None:
    config_manager = Mock()
    config_manager.api_token = "token"
    config_manager.load_config.return_value = SimpleNamespace(
        folder_id=None,
        project_name="demo",
    )

    assert push.push.callback
    await push.push.callback(config_manager=config_manager)

    assert any("No project configured" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_push_requires_project_root_when_inside_project(
    capture_echo: list[str],
) -> None:
    config_manager = Mock()
    config_manager.api_token = "token"
    config_manager.load_config.return_value = SimpleNamespace(
        folder_id=123,
        project_name="demo",
    )
    config_manager.get_current_project_name.return_value = "demo"
    config_manager.get_project_root.return_value = None

    assert push.push.callback
    await push.push.callback(config_manager=config_manager)

    assert any("Could not determine project root" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_push_requires_project_directory_when_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    config_manager = Mock()
    config_manager.api_token = "token"
    config_manager.load_config.return_value = SimpleNamespace(
        folder_id=123,
        project_name="demo",
    )
    config_manager.get_current_project_name.return_value = None

    monkeypatch.chdir(tmp_path)

    assert push.push.callback
    await push.push.callback(config_manager=config_manager)

    assert any("No project directory found" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_push_creates_zip_and_invokes_upload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    config_manager = Mock()
    config_manager.api_token = "token"
    config_manager.load_config.return_value = SimpleNamespace(
        folder_id=777,
        project_name="demo",
    )
    config_manager.get_current_project_name.return_value = None

    project_dir = tmp_path / "projects" / "demo"
    (project_dir / "nested").mkdir(parents=True)
    (project_dir / "nested" / "file.txt").write_text("content")
    (project_dir / "workato").mkdir()  # Should be excluded
    (project_dir / "workato" / "skip.txt").write_text("skip")

    monkeypatch.chdir(tmp_path)

    upload_calls: list[dict[str, object]] = []

    async def fake_upload(**kwargs: object) -> None:
        upload_calls.append(kwargs)
        zip_path = Path(str(kwargs["zip_path"]))
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path) as archive:
            assert "nested/file.txt" in archive.namelist()
            assert "workato/skip.txt" not in archive.namelist()

    upload_mock = AsyncMock(side_effect=fake_upload)
    monkeypatch.setattr(
        "workato_platform.cli.commands.push.upload_package",
        upload_mock,
    )

    assert push.push.callback
    await push.push.callback(config_manager=config_manager)

    assert upload_mock.await_count == 1
    call_kwargs = upload_calls[0]
    assert call_kwargs["folder_id"] == 777
    assert call_kwargs["restart_recipes"] is True
    assert call_kwargs["include_tags"] is True
    assert not (tmp_path / "demo.zip").exists()
    assert any("Package created" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_upload_package_handles_completed_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    zip_file = tmp_path / "demo.zip"
    zip_file.write_bytes(b"zip-data")

    import_response = SimpleNamespace(id=321, status="completed")
    packages_api = SimpleNamespace(
        import_package=AsyncMock(return_value=import_response),
    )
    client = MagicMock(spec=Workato)
    client.packages_api = packages_api

    poll_mock = AsyncMock()
    monkeypatch.setattr(
        "workato_platform.cli.commands.push.poll_import_status",
        poll_mock,
    )

    await push.upload_package(
        folder_id=123,
        zip_path=str(zip_file),
        restart_recipes=False,
        include_tags=True,
        workato_api_client=client,
    )

    packages_api.import_package.assert_awaited_once()
    poll_mock.assert_not_called()
    assert any("Import completed successfully" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_upload_package_triggers_poll_when_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    zip_file = tmp_path / "demo.zip"
    zip_file.write_bytes(b"zip-data")

    import_response = SimpleNamespace(id=321, status="processing")
    packages_api = SimpleNamespace(
        import_package=AsyncMock(return_value=import_response),
    )
    client = MagicMock(spec=Workato)
    client.packages_api = packages_api

    poll_mock = AsyncMock()
    monkeypatch.setattr(
        "workato_platform.cli.commands.push.poll_import_status",
        poll_mock,
    )

    await push.upload_package(
        folder_id=123,
        zip_path=str(zip_file),
        restart_recipes=True,
        include_tags=False,
        workato_api_client=client,
    )

    poll_mock.assert_awaited_once_with(321)


@pytest.mark.asyncio
async def test_poll_import_status_reports_success(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    responses = [
        SimpleNamespace(status="processing", recipe_status=[]),
        SimpleNamespace(
            status="completed",
            recipe_status=[
                SimpleNamespace(import_result="restarted"),
                SimpleNamespace(import_result="stop_failed"),
            ],
        ),
    ]

    async def fake_get_package(_import_id: int) -> SimpleNamespace:
        return responses.pop(0)

    packages_api = SimpleNamespace(get_package=AsyncMock(side_effect=fake_get_package))
    client = MagicMock(spec=Workato)
    client.packages_api = packages_api

    fake_time_mock = Mock()
    fake_time_mock.current = -50.0

    def fake_time() -> float:
        fake_time_mock.current += 50
        return float(fake_time_mock.current)

    monkeypatch.setattr("time.time", fake_time)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    await push.poll_import_status(999, workato_api_client=client)

    packages_api.get_package.assert_awaited()
    assert any("Import completed successfully" in line for line in capture_echo)
    assert any("Updated and restarted" in line for line in capture_echo)
    assert any("Failed to stop" in line for line in capture_echo)
    assert any("Summary" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_poll_import_status_reports_failure(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    responses = [
        SimpleNamespace(
            status="failed",
            error="Something went wrong",
            recipe_status=[("Recipe A", "Error details")],
        ),
    ]

    async def fake_get_package(_import_id: int) -> SimpleNamespace:
        return responses.pop(0)

    packages_api = SimpleNamespace(get_package=AsyncMock(side_effect=fake_get_package))
    client = MagicMock(spec=Workato)
    client.packages_api = packages_api

    fake_time_mock = Mock()
    fake_time_mock.current = -100.0

    def fake_time() -> float:
        fake_time_mock.current += 100
        return float(fake_time_mock.current)

    monkeypatch.setattr("time.time", fake_time)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    await push.poll_import_status(111, workato_api_client=client)

    assert any("Import failed" in line for line in capture_echo)
    assert any("Error: Something went wrong" in line for line in capture_echo)
    assert any("Recipe A" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_poll_import_status_timeout(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    packages_api = SimpleNamespace(
        get_package=AsyncMock(return_value=SimpleNamespace(status="processing"))
    )
    client = MagicMock(spec=Workato)
    client.packages_api = packages_api

    fake_time_mock = Mock()
    fake_time_mock.current = -120.0

    def fake_time() -> float:
        fake_time_mock.current += 120
        return float(fake_time_mock.current)

    monkeypatch.setattr("time.time", fake_time)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    await push.poll_import_status(555, workato_api_client=client)

    assert any("Import still in progress" in line for line in capture_echo)
    assert any("555" in line for line in capture_echo)
