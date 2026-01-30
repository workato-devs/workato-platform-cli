import os

from pathlib import Path

import pytest

from asyncclick.testing import CliRunner

from tests.live.helpers import prepare_live_env, require_live_env
from workato_platform_cli.cli import cli


@pytest.mark.live
@pytest.mark.asyncio
async def test_connections_oauth_flow_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env(["WORKATO_TEST_CONNECTION_ID"])
    prepare_live_env(monkeypatch, tmp_path)

    connection_id = os.environ["WORKATO_TEST_CONNECTION_ID"]

    list_result = await cli_runner.invoke(cli, ["connections", "list"])
    assert list_result.exit_code == 0, list_result.output

    oauth_result = await cli_runner.invoke(
        cli, ["connections", "get-oauth-url", "--id", str(connection_id)]
    )
    assert oauth_result.exit_code == 0, oauth_result.output


@pytest.mark.live
@pytest.mark.asyncio
async def test_connection_picklist_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env(["WORKATO_TEST_CONNECTION_ID", "WORKATO_TEST_PICKLIST_NAME"])
    prepare_live_env(monkeypatch, tmp_path)

    connection_id = os.environ["WORKATO_TEST_CONNECTION_ID"]
    picklist_name = os.environ["WORKATO_TEST_PICKLIST_NAME"]

    result = await cli_runner.invoke(
        cli,
        [
            "connections",
            "pick-list",
            "--id",
            str(connection_id),
            "--pick-list-name",
            picklist_name,
        ],
    )
    assert result.exit_code == 0, result.output
