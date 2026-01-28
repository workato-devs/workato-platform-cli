import time

from pathlib import Path

import pytest

from asyncclick.testing import CliRunner

from tests.live.helpers import (
    allow_live_action,
    delete_project,
    prepare_live_env,
    require_live_env,
    resolve_project_id,
    run_init,
    run_init_create_project,
)
from workato_platform_cli.cli import cli


@pytest.mark.live
@pytest.mark.asyncio
async def test_project_bootstrap_sync_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    prepare_live_env(monkeypatch, tmp_path)

    project_id = await resolve_project_id()

    with cli_runner.isolated_filesystem():
        await run_init(cli_runner, project_id)

        pull_result = await cli_runner.invoke(cli, ["pull"])
        assert pull_result.exit_code == 0, pull_result.output


@pytest.mark.live
@pytest.mark.asyncio
async def test_project_push_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    if not allow_live_action("WORKATO_LIVE_ALLOW_PUSH"):
        pytest.skip("Set WORKATO_LIVE_ALLOW_PUSH=1 to run live push")

    prepare_live_env(monkeypatch, tmp_path)

    project_id = await resolve_project_id()

    with cli_runner.isolated_filesystem():
        await run_init(cli_runner, project_id)

        push_result = await cli_runner.invoke(cli, ["push"])
        assert push_result.exit_code == 0, push_result.output


@pytest.mark.live
@pytest.mark.asyncio
async def test_projects_list_remote_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    prepare_live_env(monkeypatch, tmp_path)

    result = await cli_runner.invoke(
        cli, ["projects", "list", "--source", "remote", "--output-mode", "json"]
    )
    assert result.exit_code == 0, result.output


@pytest.mark.live
@pytest.mark.asyncio
async def test_project_create_and_cleanup_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    prepare_live_env(monkeypatch, tmp_path)

    project_prefix = "cli-live"
    project_name = f"{project_prefix}-{int(time.time())}"

    with cli_runner.isolated_filesystem():
        result = await run_init_create_project(cli_runner, project_name)
        project_info = result.get("project")
        project_id = None
        if isinstance(project_info, dict):
            project_id = project_info.get("id")
        if not project_id:
            pytest.skip("Project ID not returned from init; cannot clean up.")

        try:
            list_result = await cli_runner.invoke(cli, ["projects", "list"])
            assert list_result.exit_code == 0, list_result.output
        finally:
            await delete_project(int(project_id))
