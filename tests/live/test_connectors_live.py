from pathlib import Path

import pytest

from asyncclick.testing import CliRunner

from tests.live.helpers import prepare_live_env, require_live_env
from workato_platform_cli.cli import cli


@pytest.mark.live
@pytest.mark.asyncio
async def test_connectors_discovery_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    prepare_live_env(monkeypatch, tmp_path)

    list_result = await cli_runner.invoke(cli, ["connectors", "list"])
    assert list_result.exit_code == 0, list_result.output

    params_result = await cli_runner.invoke(cli, ["connectors", "parameters"])
    assert params_result.exit_code == 0, params_result.output
