"""Unit tests for the recipes CLI commands."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from workato_platform.cli.commands.recipes import command


class DummySpinner:
    """Minimal spinner stub that mimics the runtime interface."""

    def __init__(self, _message: str) -> None:  # pragma: no cover - simple wiring
        self._stopped = False

    def start(self) -> None:  # pragma: no cover - side-effect free
        pass

    def stop(self) -> float:
        self._stopped = True
        return 0.42


@pytest.fixture(autouse=True)
def patch_spinner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure spinner interactions are deterministic in tests."""

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.Spinner",
        DummySpinner,
    )


@pytest.fixture
def capture_echo(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Capture text emitted via click.echo for assertions."""

    captured: list[str] = []

    def _capture(message: str = "") -> None:
        captured.append(message)

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.click.echo",
        _capture,
    )

    return captured


@pytest.mark.asyncio
async def test_list_recipes_requires_folder_id(monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]) -> None:
    """When no folder is configured the command guides the user."""

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=None)

    await command.list_recipes.callback(config_manager=config_manager)

    output = "\n".join(capture_echo)
    assert "No folder ID provided" in output
    assert "workato init" in output


@pytest.mark.asyncio
async def test_list_recipes_recursive_filters_running(monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]) -> None:
    """Recursive listing warns about ignored filters and respects the running flag."""

    running_recipe = SimpleNamespace(running=True, name="Active", id=1)
    stopped_recipe = SimpleNamespace(running=False, name="Stopped", id=2)

    mock_recursive = AsyncMock(return_value=[running_recipe, stopped_recipe])
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_recipes_recursive",
        mock_recursive,
    )

    seen: list[SimpleNamespace] = []

    def fake_display(recipe: SimpleNamespace) -> None:
        seen.append(recipe)

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.display_recipe_summary",
        fake_display,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=999)

    await command.list_recipes.callback(
        folder_id=123,
        recursive=True,
        running=True,
        config_manager=config_manager,
    )

    mock_recursive.assert_awaited_once_with(123)
    assert seen == [running_recipe]
    full_output = "\n".join(capture_echo)
    assert "Recursive" in full_output
    assert "Total: 1 recipe(s)" in full_output


@pytest.mark.asyncio
async def test_list_recipes_non_recursive_with_filters(monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]) -> None:
    """The non-recursive path fetches recipes and surfaces filter details."""

    recipe_stub = SimpleNamespace(running=True, name="Demo", id=99)

    mock_paginated = AsyncMock(return_value=[recipe_stub])
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_all_recipes_paginated",
        mock_paginated,
    )

    recorded: list[SimpleNamespace] = []

    def fake_display(recipe: SimpleNamespace) -> None:
        recorded.append(recipe)

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.display_recipe_summary",
        fake_display,
    )

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=None)

    await command.list_recipes.callback(
        folder_id=555,
        adapter_names_all="http",
        adapter_names_any="slack",
        running=True,
        stop_cause="trigger_errors_limit",
        exclude_code=True,
        config_manager=config_manager,
    )

    mock_paginated.assert_awaited_once()
    kwargs = mock_paginated.await_args.kwargs
    assert kwargs["folder_id"] == 555
    assert kwargs["adapter_names_all"] == "http"
    assert kwargs["exclude_code"] is True
    assert recorded == [recipe_stub]
    text = "\n".join(capture_echo)
    assert "Filters" in text
    assert "Recipes (1 found)" in text


@pytest.mark.asyncio
async def test_validate_missing_file(capture_echo: list[str]) -> None:
    """Validation rejects non-existent files early."""

    validator = Mock()

    await command.validate.callback(
        path="/tmp/unknown.json",
        recipe_validator=validator,
    )

    assert "File not found" in capture_echo[0]
    validator.validate_recipe.assert_not_called()


@pytest.mark.asyncio
async def test_validate_requires_json_extension(tmp_path: Path, capture_echo: list[str]) -> None:
    """Validation enforces JSON file extension before reading content."""

    text_file = tmp_path / "recipe.txt"
    text_file.write_text("{}")

    validator = Mock()

    await command.validate.callback(
        path=str(text_file),
        recipe_validator=validator,
    )

    assert any("must be a JSON" in line for line in capture_echo)
    validator.validate_recipe.assert_not_called()


@pytest.mark.asyncio
async def test_validate_json_errors(tmp_path: Path, capture_echo: list[str]) -> None:
    """Invalid JSON content surfaces a helpful error."""

    bad_file = tmp_path / "broken.json"
    bad_file.write_text("{invalid}")

    validator = Mock()

    await command.validate.callback(
        path=str(bad_file),
        recipe_validator=validator,
    )

    assert any("Invalid JSON" in line for line in capture_echo)
    validator.validate_recipe.assert_not_called()


@pytest.mark.asyncio
async def test_validate_success(tmp_path: Path, capture_echo: list[str]) -> None:
    """A successful validation reports elapsed time and file info."""

    ok_file = tmp_path / "valid.json"
    ok_file.write_text("{}")

    result = SimpleNamespace(is_valid=True, errors=[], warnings=[])

    validator = Mock()
    validator.validate_recipe = AsyncMock(return_value=result)

    await command.validate.callback(
        path=str(ok_file),
        recipe_validator=validator,
    )

    validator.validate_recipe.assert_awaited_once()
    joined = "\n".join(capture_echo)
    assert "Recipe validation passed" in joined
    assert "valid.json" in joined


@pytest.mark.asyncio
async def test_validate_failure_with_warnings(tmp_path: Path, capture_echo: list[str]) -> None:
    """Failed validation prints every reported error and warning."""

    data_file = tmp_path / "invalid.json"
    data_file.write_text("{}")

    error = SimpleNamespace(
        line_number=7,
        field_label="field",
        field_path=["step", "field"],
        message="Something broke",
        error_type=SimpleNamespace(value="issue"),
    )
    warning = SimpleNamespace(message="Be careful")
    result = SimpleNamespace(is_valid=False, errors=[error], warnings=[warning])

    validator = Mock()
    validator.validate_recipe = AsyncMock(return_value=result)

    await command.validate.callback(
        path=str(data_file),
        recipe_validator=validator,
    )

    validator.validate_recipe.assert_awaited_once()
    combined = "\n".join(capture_echo)
    assert "validation failed" in combined.lower()
    assert "Something broke" in combined
    assert "Be careful" in combined


@pytest.mark.asyncio
async def test_start_requires_single_option(capture_echo: list[str]) -> None:
    """The start command enforces exclusive option selection."""

    await command.start.callback(recipe_id=None, start_all=False, folder_id=None)
    assert any("Please specify one" in line for line in capture_echo)

    capture_echo.clear()

    await command.start.callback(recipe_id=1, start_all=True, folder_id=None)
    assert any("only one option" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_start_dispatches_correct_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each start variant invokes the matching helper."""

    single = AsyncMock()
    project = AsyncMock()
    folder = AsyncMock()

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.start_single_recipe",
        single,
    )
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.start_project_recipes",
        project,
    )
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.start_folder_recipes",
        folder,
    )

    await command.start.callback(recipe_id=10, start_all=False, folder_id=None)
    single.assert_awaited_once_with(10)

    await command.start.callback(recipe_id=None, start_all=True, folder_id=None)
    project.assert_awaited_once()

    await command.start.callback(recipe_id=None, start_all=False, folder_id=22)
    folder.assert_awaited_once_with(22)


@pytest.mark.asyncio
async def test_stop_requires_single_option(capture_echo: list[str]) -> None:
    """The stop command mirrors the exclusivity checks."""

    await command.stop.callback(recipe_id=None, stop_all=False, folder_id=None)
    assert any("Please specify one" in line for line in capture_echo)

    capture_echo.clear()

    await command.stop.callback(recipe_id=1, stop_all=True, folder_id=None)
    assert any("only one option" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_stop_dispatches_correct_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each stop variant invokes the matching helper."""

    single = AsyncMock()
    project = AsyncMock()
    folder = AsyncMock()

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.stop_single_recipe",
        single,
    )
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.stop_project_recipes",
        project,
    )
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.stop_folder_recipes",
        folder,
    )

    await command.stop.callback(recipe_id=10, stop_all=False, folder_id=None)
    single.assert_awaited_once_with(10)

    await command.stop.callback(recipe_id=None, stop_all=True, folder_id=None)
    project.assert_awaited_once()

    await command.stop.callback(recipe_id=None, stop_all=False, folder_id=22)
    folder.assert_awaited_once_with(22)


@pytest.mark.asyncio
async def test_start_single_recipe_success(capture_echo: list[str]) -> None:
    """Successful start prints a confirmation message."""

    response = SimpleNamespace(success=True)
    client = SimpleNamespace(
        recipes_api=SimpleNamespace(start_recipe=AsyncMock(return_value=response))
    )

    await command.start_single_recipe(42, workato_api_client=client)

    assert client.recipes_api.start_recipe.await_args.args == (42,)
    assert any("started successfully" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_start_single_recipe_failure_shows_detailed_errors(
    capture_echo: list[str],
) -> None:
    """Failure path surfaces detailed error output."""

    response = SimpleNamespace(
        success=False,
        code_errors=[[1, [["Label", 12, "Message", "field.path"]]]],
        config_errors=[[2, [["ConfigField", None, "Missing"]]], "Other issue"],
    )
    client = SimpleNamespace(
        recipes_api=SimpleNamespace(start_recipe=AsyncMock(return_value=response))
    )

    await command.start_single_recipe(55, workato_api_client=client)

    output = "\n".join(capture_echo)
    assert "failed to start" in output
    assert "Step 1" in output
    assert "ConfigField" in output
    assert "Other issue" in output


@pytest.mark.asyncio
async def test_start_project_recipes_requires_configuration(
    capture_echo: list[str],
) -> None:
    """Missing folder configuration blocks bulk start."""

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=None)

    await command.start_project_recipes(config_manager=config_manager)

    assert any("No project configured" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_start_project_recipes_delegates_to_folder(monkeypatch: pytest.MonkeyPatch) -> None:
    """When configured the project helper delegates to folder start."""

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=777)

    start_folder = AsyncMock()
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.start_folder_recipes",
        start_folder,
    )

    await command.start_project_recipes(config_manager=config_manager)

    start_folder.assert_awaited_once_with(777)


@pytest.mark.asyncio
async def test_start_folder_recipes_handles_success_and_failure(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    """Folder start reports results per recipe and summarises failures."""

    assets = [
        SimpleNamespace(id=1, name="Recipe One"),
        SimpleNamespace(id=2, name="Recipe Two"),
    ]
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_folder_recipe_assets",
        AsyncMock(return_value=assets),
    )

    responses = [
        SimpleNamespace(success=True,
                        code_errors=[],
                        config_errors=[]),
        SimpleNamespace(
            success=False,
            code_errors=[[3, [["Label", 99, "Err", "path"]]]],
            config_errors=[],
        ),
    ]

    async def _start_recipe(recipe_id: int) -> SimpleNamespace:
        return responses[recipe_id - 1]

    client = SimpleNamespace(
        recipes_api=SimpleNamespace(start_recipe=AsyncMock(side_effect=_start_recipe))
    )

    await command.start_folder_recipes(123, workato_api_client=client)

    called_ids = [call.args[0] for call in client.recipes_api.start_recipe.await_args_list]
    assert called_ids == [1, 2]
    output = "\n".join(capture_echo)
    assert "Recipe One" in output and "started" in output
    assert "Recipe Two" in output and "Failed" in output
    assert "Failed recipes" in output


@pytest.mark.asyncio
async def test_start_folder_recipes_handles_empty_folder(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    """No assets produces an informational message."""

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_folder_recipe_assets",
        AsyncMock(return_value=[]),
    )

    client = SimpleNamespace(recipes_api=SimpleNamespace(start_recipe=AsyncMock()))

    await command.start_folder_recipes(789, workato_api_client=client)

    assert any("No recipes found" in line for line in capture_echo)
    client.recipes_api.start_recipe.assert_not_called()


@pytest.mark.asyncio
async def test_stop_single_recipe_outputs_confirmation(capture_echo: list[str]) -> None:
    """Stopping a recipe forwards to the API and reports success."""

    client = SimpleNamespace(
        recipes_api=SimpleNamespace(stop_recipe=AsyncMock())
    )

    await command.stop_single_recipe(88, workato_api_client=client)

    client.recipes_api.stop_recipe.assert_awaited_once_with(88)
    assert any("stopped successfully" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_stop_project_recipes_requires_configuration(
    capture_echo: list[str],
) -> None:
    """Missing project configuration prevents stopping all recipes."""

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=None)

    await command.stop_project_recipes(config_manager=config_manager)

    assert any("No project configured" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_stop_project_recipes_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    """Project-level stop delegates to folder helper."""

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=123)

    stop_folder = AsyncMock()
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.stop_folder_recipes",
        stop_folder,
    )

    await command.stop_project_recipes(config_manager=config_manager)

    stop_folder.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_stop_folder_recipes_iterates_assets(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    """Stop helper iterates through retrieved assets."""

    assets = [
        SimpleNamespace(id=1, name="Recipe One"),
        SimpleNamespace(id=2, name="Recipe Two"),
    ]
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_folder_recipe_assets",
        AsyncMock(return_value=assets),
    )

    client = SimpleNamespace(
        recipes_api=SimpleNamespace(stop_recipe=AsyncMock())
    )

    await command.stop_folder_recipes(44, workato_api_client=client)

    called_ids = [call.args[0] for call in client.recipes_api.stop_recipe.await_args_list]
    assert called_ids == [1, 2]
    assert "Results" in "\n".join(capture_echo)


@pytest.mark.asyncio
async def test_stop_folder_recipes_no_assets(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    """No assets triggers informational output."""

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_folder_recipe_assets",
        AsyncMock(return_value=[]),
    )

    client = SimpleNamespace(
        recipes_api=SimpleNamespace(stop_recipe=AsyncMock())
    )

    await command.stop_folder_recipes(44, workato_api_client=client)

    assert any("No recipes found" in line for line in capture_echo)
    client.recipes_api.stop_recipe.assert_not_called()


@pytest.mark.asyncio
async def test_get_folder_recipe_assets_filters_non_recipes(capture_echo: list[str]) -> None:
    """Asset helper filters responses down to recipe entries."""

    assets = [
        SimpleNamespace(type="recipe", id=1, name="R"),
        SimpleNamespace(type="folder", id=2, name="F"),
    ]
    response = SimpleNamespace(result=SimpleNamespace(assets=assets))

    client = SimpleNamespace(
        export_api=SimpleNamespace(
            list_assets_in_folder=AsyncMock(return_value=response)
        )
    )

    recipes = await command.get_folder_recipe_assets(5, workato_api_client=client)

    client.export_api.list_assets_in_folder.assert_awaited_once_with(folder_id=5)
    assert recipes == [assets[0]]
    assert any("Found 1 recipe" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_get_all_recipes_paginated_handles_multiple_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pagination helper keeps fetching until fewer than 100 results are returned."""

    first_page = SimpleNamespace(items=[SimpleNamespace(id=i) for i in range(100)])
    second_page = SimpleNamespace(items=[SimpleNamespace(id=101)])

    list_recipes_mock = AsyncMock(side_effect=[first_page, second_page])

    client = SimpleNamespace(
        recipes_api=SimpleNamespace(list_recipes=list_recipes_mock)
    )

    recipes = await command.get_all_recipes_paginated(
        folder_id=9,
        adapter_names_all="http",
        adapter_names_any="slack",
        running=True,
        since_id=10,
        stopped_after="2023-01-01T00:00:00",
        stop_cause="trial_expired",
        updated_after="2023-02-01T00:00:00",
        include_tags="foo,bar",
        exclude_code=False,
        workato_api_client=client,
    )

    assert len(recipes) == 101
    assert list_recipes_mock.await_count == 2

    kwargs = list_recipes_mock.await_args.kwargs
    assert isinstance(kwargs["stopped_after"], datetime)
    assert kwargs["includes"] == ["foo", "bar"]
    assert kwargs["exclude_code"] is None


@pytest.mark.asyncio
async def test_get_recipes_recursive_traverses_subfolders(
    monkeypatch: pytest.MonkeyPatch,
    capture_echo: list[str],
) -> None:
    """Recursive helper visits child folders exactly once."""

    async def _get_all_recipes_paginated(**kwargs):
        return [SimpleNamespace(id=kwargs["folder_id"])]

    mock_get_all = AsyncMock(side_effect=_get_all_recipes_paginated)
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_all_recipes_paginated",
        mock_get_all,
    )

    list_calls = {
        1: [SimpleNamespace(id=2)],
        2: [],
    }

    async def _list_folders(parent_id: int, page: int, per_page: int) -> list[SimpleNamespace]:
        return list_calls[parent_id]

    client = SimpleNamespace(
        folders_api=SimpleNamespace(list_folders=AsyncMock(side_effect=_list_folders))
    )

    raw_recursive = command.get_recipes_recursive.__wrapped__
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_recipes_recursive",
        raw_recursive,
    )

    recipes = await command.get_recipes_recursive(1, workato_api_client=client)

    assert {recipe.id for recipe in recipes} == {1, 2}
    assert mock_get_all.await_count == 2
    history = [call.kwargs["folder_id"] for call in mock_get_all.await_args_list]
    assert history == [1, 2]
    assert "Found 1 subfolder" in "\n".join(capture_echo)


@pytest.mark.asyncio
async def test_get_recipes_recursive_skips_visited(monkeypatch: pytest.MonkeyPatch) -> None:
    """Visited folders are ignored to avoid infinite recursion."""

    mock_get_all = AsyncMock()
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_all_recipes_paginated",
        mock_get_all,
    )

    client = SimpleNamespace(
        folders_api=SimpleNamespace(list_folders=AsyncMock())
    )

    raw_recursive = command.get_recipes_recursive.__wrapped__
    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_recipes_recursive",
        raw_recursive,
    )

    recipes = await command.get_recipes_recursive(
        5, visited_folders={5}, workato_api_client=client
    )

    assert recipes == []
    mock_get_all.assert_not_called()


def test_display_recipe_summary_outputs_all_sections(
    capture_echo: list[str],
) -> None:
    """Summary printer shows optional metadata when available."""

    config_item = SimpleNamespace(keyword="application", name="App", account_id=321)
    recipe = SimpleNamespace(
        name="Complex Recipe",
        id=555,
        running=False,
        trigger_application="http",
        action_applications=["slack"],
        config=[config_item],
        folder_id=999,
        job_succeeded_count=5,
        job_failed_count=1,
        last_run_at=datetime(2024, 1, 1),
        stopped_at=datetime(2024, 1, 2),
        stop_cause="trigger_errors_limit",
        created_at=datetime(2023, 12, 31),
        author_name="Author",
        tags=["tag1", "tag2"],
        description="This is a long description " * 5,
    )

    command.display_recipe_summary(recipe)

    output = "\n".join(capture_echo)
    assert "Complex Recipe" in output
    assert "Action Apps" in output
    assert "Config Apps" in output
    assert "Stopped" in output
    assert "Stop Cause" in output
    assert "Tags" in output
    assert "Description" in output and "..." in output


@pytest.mark.asyncio
async def test_update_connection_invokes_api(capture_echo: list[str]) -> None:
    """Connection update forwards parameters to Workato client."""

    client = SimpleNamespace(
        recipes_api=SimpleNamespace(
            update_recipe_connection=AsyncMock()
        )
    )

    await command.update_connection.callback(
        recipe_id=10,
        adapter_name="box",
        connection_id=222,
        workato_api_client=client,
    )

    args = client.recipes_api.update_recipe_connection.await_args.kwargs
    update_body = args["recipe_connection_update_request"]
    assert update_body.adapter_name == "box"
    assert update_body.connection_id == 222
    assert any("Successfully updated" in line for line in capture_echo)


def test_display_recipe_errors_with_string_config(capture_echo: list[str]) -> None:
    """Error display can handle string entries in config errors."""

    response = SimpleNamespace(
        code_errors=[],
        config_errors=["Generic problem"],
    )

    command._display_recipe_errors(response)

    assert any("Generic problem" in line for line in capture_echo)


@pytest.mark.asyncio
async def test_list_recipes_no_results(monkeypatch: pytest.MonkeyPatch, capture_echo: list[str]) -> None:
    """Listing with filters reports when nothing matches."""

    config_manager = Mock()
    config_manager.load_config.return_value = SimpleNamespace(folder_id=50)

    monkeypatch.setattr(
        "workato_platform.cli.commands.recipes.command.get_all_recipes_paginated",
        AsyncMock(return_value=[]),
    )

    await command.list_recipes.callback(
        running=True,
        config_manager=config_manager,
    )

    assert any("No recipes found" in line for line in capture_echo)
