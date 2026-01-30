import os

from pathlib import Path

import pytest

from asyncclick.testing import CliRunner

from tests.live.helpers import (
    prepare_live_env,
    require_live_env,
    resolve_project_id,
    run_init,
)
from workato_platform_cli.cli import cli


@pytest.mark.live
@pytest.mark.asyncio
async def test_profiles_workflow_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    prepare_live_env(monkeypatch, tmp_path)

    project_id = await resolve_project_id()

    with cli_runner.isolated_filesystem():
        await run_init(cli_runner, project_id)

        list_result = await cli_runner.invoke(cli, ["profiles", "list"])
        assert list_result.exit_code == 0, list_result.output

        status_result = await cli_runner.invoke(cli, ["profiles", "status"])
        assert status_result.exit_code == 0, status_result.output

        profile_name = os.getenv("WORKATO_TEST_PROFILE", "live-test")
        use_result = await cli_runner.invoke(cli, ["profiles", "use", profile_name])
        assert use_result.exit_code == 0, use_result.output
