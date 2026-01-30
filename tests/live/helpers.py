import json
import os

from pathlib import Path
from typing import cast

import certifi
import pytest

from asyncclick.testing import CliRunner

from workato_platform_cli import Workato
from workato_platform_cli.cli import cli
from workato_platform_cli.cli.commands.projects.project_manager import ProjectManager
from workato_platform_cli.client.workato_api.configuration import Configuration


REQUIRED_BASE = ["WORKATO_HOST", "WORKATO_API_TOKEN"]
_PROJECT_ID_CACHE: str | None = None


def ensure_sandbox() -> None:
    host = os.getenv("WORKATO_HOST", "").lower()
    if os.getenv("WORKATO_LIVE_SANDBOX", "").lower() in {"1", "true", "yes"}:
        return
    if any(token in host for token in ("trial", "preview", "sandbox")):
        return
    pytest.skip(
        "Set WORKATO_LIVE_SANDBOX=1 to confirm tests are running against a sandbox."
    )


def require_live_env(extra: list[str] | None = None) -> None:
    ensure_sandbox()
    required = REQUIRED_BASE + (extra or [])
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        pytest.skip(f"Missing env vars for live tests: {', '.join(missing)}")


def allow_live_action(flag: str) -> bool:
    return os.getenv(flag, "").lower() in {"1", "true", "yes"}


def force_keyring_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    import workato_platform_cli.cli.utils.config.profiles as profiles

    def _raise_no_keyring() -> None:
        raise Exception("No keyring backend")

    monkeypatch.setattr(profiles.keyring, "get_keyring", _raise_no_keyring)


def prepare_live_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WORKATO_DISABLE_UPDATE_CHECK", "1")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    force_keyring_fallback(monkeypatch)


def _build_api_client() -> Workato:
    api_host = os.environ["WORKATO_HOST"]
    api_token = os.environ["WORKATO_API_TOKEN"]
    api_config = Configuration(
        access_token=api_token,
        host=api_host,
        ssl_ca_cert=certifi.where(),
    )
    return Workato(configuration=api_config)


async def resolve_project_id() -> str:
    global _PROJECT_ID_CACHE
    if _PROJECT_ID_CACHE:
        return _PROJECT_ID_CACHE

    project_id = os.getenv("WORKATO_TEST_PROJECT_ID")
    if project_id:
        _PROJECT_ID_CACHE = project_id
        return project_id

    project_name = os.getenv("WORKATO_TEST_PROJECT_NAME")

    async with _build_api_client() as workato_api_client:
        project_manager = ProjectManager(workato_api_client=workato_api_client)
        projects = await project_manager.get_all_projects()

    if not projects:
        pytest.skip("No projects found in workspace.")

    if project_name:
        for project in projects:
            if project.name == project_name:
                _PROJECT_ID_CACHE = str(project.id)
                return str(project.id)
        pytest.skip(f"No project found with name '{project_name}'.")

    _PROJECT_ID_CACHE = str(projects[0].id)
    return _PROJECT_ID_CACHE


async def delete_project(project_id: int) -> None:
    async with _build_api_client() as workato_api_client:
        await workato_api_client.projects_api.delete_project(project_id=project_id)


async def run_init(cli_runner: CliRunner, project_id: str) -> dict[str, object]:
    api_host = os.environ["WORKATO_HOST"]
    profile_name = os.getenv("WORKATO_TEST_PROFILE", "live-test")
    result = await cli_runner.invoke(
        cli,
        [
            "init",
            "--non-interactive",
            "--profile",
            profile_name,
            "--project-id",
            str(project_id),
            "--output-mode",
            "json",
            "--region",
            "custom",
            "--api-url",
            api_host,
        ],
    )

    assert result.exit_code == 0, result.output

    lines = [line for line in result.output.splitlines() if line.strip()]
    data = cast(dict[str, object], json.loads(lines[-1]))
    assert data.get("status") == "success"
    return data


async def run_init_create_project(
    cli_runner: CliRunner,
    project_name: str,
) -> dict[str, object]:
    api_host = os.environ["WORKATO_HOST"]
    profile_name = os.getenv("WORKATO_TEST_PROFILE", "live-test")
    result = await cli_runner.invoke(
        cli,
        [
            "init",
            "--non-interactive",
            "--profile",
            profile_name,
            "--project-name",
            project_name,
            "--output-mode",
            "json",
            "--region",
            "custom",
            "--api-url",
            api_host,
        ],
    )

    if result.exit_code != 0:
        if "UNAUTHORIZED" in result.output or "Authentication failed" in result.output:
            pytest.skip(
                "Project creation/pull not authorized for this token. "
                "Check sandbox permissions or token scope."
            )
        assert result.exit_code == 0, result.output

    lines = [line for line in result.output.splitlines() if line.strip()]
    data = cast(dict[str, object], json.loads(lines[-1]))
    assert data.get("status") == "success"
    return data
