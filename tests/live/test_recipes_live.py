import os

from pathlib import Path

import pytest

from asyncclick.testing import CliRunner

from tests.live.helpers import (
    allow_live_action,
    prepare_live_env,
    require_live_env,
    resolve_project_id,
    run_init,
)
from workato_platform_cli.cli import cli


@pytest.mark.live
@pytest.mark.asyncio
async def test_recipes_list_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    prepare_live_env(monkeypatch, tmp_path)

    project_id = await resolve_project_id()

    with cli_runner.isolated_filesystem():
        await run_init(cli_runner, project_id)

        list_result = await cli_runner.invoke(cli, ["recipes", "list"])
        assert list_result.exit_code == 0, list_result.output


@pytest.mark.live
@pytest.mark.asyncio
async def test_recipes_start_stop_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env(["WORKATO_TEST_RECIPE_ID"])
    if not allow_live_action("WORKATO_LIVE_ALLOW_RECIPE_CONTROL"):
        pytest.skip("Set WORKATO_LIVE_ALLOW_RECIPE_CONTROL=1 to run start/stop")

    prepare_live_env(monkeypatch, tmp_path)

    project_id = await resolve_project_id()
    recipe_id = os.environ["WORKATO_TEST_RECIPE_ID"]

    with cli_runner.isolated_filesystem():
        await run_init(cli_runner, project_id)

        start_result = await cli_runner.invoke(
            cli, ["recipes", "start", "--id", str(recipe_id)]
        )
        assert start_result.exit_code == 0, start_result.output

        stop_result = await cli_runner.invoke(
            cli, ["recipes", "stop", "--id", str(recipe_id)]
        )
        assert stop_result.exit_code == 0, stop_result.output


@pytest.mark.live
@pytest.mark.asyncio
async def test_recipe_validate_live(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_live_env()
    prepare_live_env(monkeypatch, tmp_path)

    fixtures_dir = Path(__file__).resolve().parents[1] / "fixtures"
    sample_recipe = fixtures_dir / "sample_recipe.json"

    with cli_runner.isolated_filesystem():
        recipe_path = Path("sample_recipe.json")
        recipe_contents = sample_recipe.read_text(encoding="utf-8")
        recipe_path.write_text(recipe_contents, encoding="utf-8")

        result = await cli_runner.invoke(
            cli, ["recipes", "validate", "--path", str(recipe_path)]
        )
        assert result.exit_code == 0, result.output
