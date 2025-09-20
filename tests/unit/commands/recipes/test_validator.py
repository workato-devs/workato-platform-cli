"""Targeted tests for the recipes validator helpers."""

from __future__ import annotations

import asyncio
import json
import tempfile
import time

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Tests cover a wide set of validator helpers; keep imports explicit for clarity.
from workato_platform.cli.commands.recipes.validator import (
    ErrorType,
    Keyword,
    RecipeLine,
    RecipeStructure,
    RecipeValidator,
    ValidationError,
    ValidationResult,
)


if TYPE_CHECKING:
    from workato_platform import Workato


@pytest.fixture
def validator() -> RecipeValidator:
    """Provide a validator with a mocked Workato client."""
    client = cast("Workato", Mock())
    instance = RecipeValidator(client)
    cast(Any, instance)._ensure_connectors_loaded = AsyncMock()
    instance.known_adapters = {"scheduler", "http", "workato"}
    return instance


@pytest.fixture
def make_line() -> Callable[..., RecipeLine]:
    """Factory for creating RecipeLine instances with sensible defaults."""

    def _factory(**overrides: Any) -> RecipeLine:
        data: dict[str, Any] = {
            "number": 0,
            "keyword": Keyword.TRIGGER,
            "uuid": "root-uuid",
        }
        data.update(overrides)
        return RecipeLine(**data)

    return _factory


def test_validation_error_retains_metadata() -> None:
    error = ValidationError(
        message="Issue detected",
        error_type=ErrorType.STRUCTURE_INVALID,
        line_number=3,
        field_path=["trigger"],
    )

    assert error.message == "Issue detected"
    assert error.error_type is ErrorType.STRUCTURE_INVALID
    assert error.line_number == 3
    assert error.field_path == ["trigger"]


def test_validation_result_collects_errors_and_warnings() -> None:
    errors = [
        ValidationError(message="E1", error_type=ErrorType.SYNTAX_INVALID),
    ]
    warnings = [
        ValidationError(message="W1", error_type=ErrorType.INPUT_INVALID_BY_ADAPTER),
    ]

    result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    assert not result.is_valid
    assert result.errors[0].message == "E1"
    assert result.warnings[0].message == "W1"


def test_is_expression_detects_formulas_jinja_and_data_pills(
    validator: RecipeValidator,
) -> None:
    assert validator._is_expression("=_dp('trigger.data')") is True
    assert validator._is_expression("value {{ foo }}") is True
    assert validator._is_expression("Before #{_dp('data.path')} after") is True
    assert validator._is_expression("plain text") is False
    assert validator._is_expression(None) is False


def test_extract_data_pills_supports_dp_and_legacy_notation(
    validator: RecipeValidator,
) -> None:
    text = "prefix #{_dp('data.trigger.step')} and #{_('data.legacy.step')} suffix"
    pills = validator._extract_data_pills(text)

    assert pills == ["data.trigger.step", "data.legacy.step"]


def test_extract_data_pills_gracefully_handles_non_string(
    validator: RecipeValidator,
) -> None:
    assert validator._extract_data_pills(None) == []


def test_recipe_structure_requires_trigger_start(
    make_line: Callable[..., RecipeLine],
) -> None:
    with pytest.raises(ValueError):
        RecipeStructure(root=make_line(keyword=Keyword.ACTION))


def test_recipe_structure_accepts_valid_nested_structure(
    make_line: Callable[..., RecipeLine],
) -> None:
    root = make_line(block=[make_line(number=1, keyword=Keyword.ACTION, uuid="step-1")])

    structure = RecipeStructure(root=root)

    assert structure.root.block is not None
    assert structure.root.block[0].uuid == "step-1"


def test_foreach_structure_requires_source(
    make_line: Callable[..., RecipeLine],
) -> None:
    line = make_line(number=1, keyword=Keyword.FOREACH, uuid="loop", source=None)

    errors = RecipeStructure._validate_foreach_structure(line, [])

    assert errors
    assert errors[0].error_type is ErrorType.LINE_ATTR_INVALID


def test_repeat_structure_requires_block(
    make_line: Callable[..., RecipeLine],
) -> None:
    line = make_line(number=2, keyword=Keyword.REPEAT, uuid="repeat")

    errors = RecipeStructure._validate_repeat_structure(line, [])

    assert errors
    assert errors[0].error_type is ErrorType.LINE_SYNTAX_INVALID


def test_try_structure_requires_block(
    make_line: Callable[..., RecipeLine],
) -> None:
    line = make_line(number=3, keyword=Keyword.TRY, uuid="try")

    errors = RecipeStructure._validate_try_structure(line, [])

    assert errors
    assert errors[0].error_type is ErrorType.LINE_SYNTAX_INVALID


def test_action_structure_disallows_blocks(
    make_line: Callable[..., RecipeLine],
) -> None:
    child = make_line(number=4, keyword=Keyword.ACTION, uuid="child-action")
    line = make_line(
        number=3,
        keyword=Keyword.ACTION,
        uuid="parent-action",
        block=[child],
    )

    errors = RecipeStructure._validate_action_structure(line, [])

    assert errors
    assert errors[0].error_type is ErrorType.LINE_SYNTAX_INVALID


def test_block_structure_requires_trigger_start(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    line = make_line(keyword=Keyword.ACTION)

    errors = validator._validate_block_structure(line)

    assert errors
    assert "Block 0 must be a trigger" in errors[0].message


def test_validate_references_with_context_detects_unknown_step(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    validator.known_adapters = {"scheduler", "http"}
    action_with_alias = make_line(
        number=1,
        keyword=Keyword.ACTION,
        uuid="http-step",
        provider="http",
        as_="http_step",
        input={"url": "https://example.com"},
    )
    action_with_bad_reference = make_line(
        number=2,
        keyword=Keyword.ACTION,
        uuid="second-step",
        provider="http",
        input={"message": "#{_dp('data.http.unknown.status')}"},
    )
    root = make_line(
        provider="scheduler",
        block=[action_with_alias, action_with_bad_reference],
    )

    errors = validator._validate_references_with_context(root, {})

    assert errors
    assert any("unknown step" in error.message for error in errors)


def test_validate_input_modes_flags_mixed_modes(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    line = make_line(
        number=2,
        keyword=Keyword.ACTION,
        uuid="action-1",
        input={
            "url": "=_dp('trigger.data.url') #{_dp('trigger.data.path')}",
        },
    )

    errors = validator._validate_input_modes(line)

    assert errors
    assert errors[0].error_type is ErrorType.INPUT_MODE_INCONSISTENT


def test_validate_input_modes_accepts_formula_only(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    line = make_line(
        number=2,
        keyword=Keyword.ACTION,
        uuid="action-2",
        input={"url": "=_dp('trigger.data.url')"},
    )

    assert validator._validate_input_modes(line) == []


def test_validate_formula_syntax_rejects_non_dp_formulas(
    validator: RecipeValidator,
) -> None:
    errors = validator._validate_formula_syntax("=sum('value')", "total", 5)

    assert errors
    assert errors[0].error_type is ErrorType.FORMULA_SYNTAX_INVALID


def test_data_pill_cross_reference_unknown_step(
    validator: RecipeValidator,
) -> None:
    error = validator._validate_data_pill_cross_reference(
        "data.http.unknown.field",
        line_number=3,
        step_context={},
        field_path=["input"],
    )

    assert isinstance(error, ValidationError)
    assert "unknown step" in error.message


def test_data_pill_cross_reference_provider_mismatch(
    validator: RecipeValidator,
) -> None:
    context = {
        "alias": {
            "provider": "http",
            "keyword": "action",
            "number": 1,
            "name": "HTTP step",
        }
    }

    error = validator._validate_data_pill_cross_reference(
        "data.s3.alias.field",
        line_number=4,
        step_context=context,
        field_path=["input"],
    )

    assert isinstance(error, ValidationError)
    assert "provider mismatch" in error.message


def test_data_pill_cross_reference_valid_reference(
    validator: RecipeValidator,
) -> None:
    context = {
        "alias": {
            "provider": "http",
            "keyword": "action",
            "number": 1,
            "name": "HTTP step",
        }
    }

    assert (
        validator._validate_data_pill_cross_reference(
            "data.http.alias.response",
            line_number=4,
            step_context=context,
            field_path=["input"],
        )
        is None
    )


@pytest.mark.asyncio
async def test_validate_recipe_requires_code(validator: RecipeValidator) -> None:
    result = await validator.validate_recipe({})

    assert not result.is_valid
    assert any("code" in error.message for error in result.errors)


@pytest.mark.asyncio
async def test_validate_recipe_flags_unknown_provider(
    validator: RecipeValidator,
) -> None:
    validator.known_adapters = {"scheduler"}
    recipe_data = {
        "code": {
            "number": 0,
            "keyword": "trigger",
            "uuid": "root",
            "provider": "scheduler",
            "name": "Schedule",
            "block": [
                {
                    "number": 1,
                    "keyword": "action",
                    "uuid": "action-unknown",
                    "provider": "mystery",
                    "name": "Do stuff",
                }
            ],
        },
        "config": [
            {"provider": "scheduler"},
            {"provider": "mystery"},
        ],
    }

    result = await validator.validate_recipe(recipe_data)

    assert not result.is_valid
    assert any("Unknown provider" in error.message for error in result.errors)


@pytest.mark.asyncio
async def test_validate_recipe_detects_duplicate_as_entries(
    validator: RecipeValidator,
) -> None:
    validator.known_adapters = {"scheduler", "http"}
    recipe_data = {
        "code": {
            "number": 0,
            "keyword": "trigger",
            "uuid": "root",
            "provider": "scheduler",
            "name": "Schedule",
            "block": [
                {
                    "number": 1,
                    "keyword": "action",
                    "uuid": "action-1",
                    "provider": "http",
                    "name": "Call HTTP",
                    "as": "dup_step",
                    "input": {"url": "https://example.com"},
                },
                {
                    "number": 2,
                    "keyword": "action",
                    "uuid": "action-2",
                    "provider": "http",
                    "name": "Call HTTP again",
                    "as": "dup_step",
                    "input": {"url": "https://example.com"},
                },
            ],
        },
        "config": [
            {"provider": "scheduler"},
            {"provider": "http"},
        ],
    }

    result = await validator.validate_recipe(recipe_data)

    assert not result.is_valid
    assert any("Duplicate 'as' value" in error.message for error in result.errors)


@pytest.mark.asyncio
async def test_validate_recipe_missing_config_provider(
    validator: RecipeValidator,
) -> None:
    validator.known_adapters = {"scheduler", "http"}
    recipe_data = {
        "code": {
            "number": 0,
            "keyword": "trigger",
            "uuid": "root",
            "provider": "scheduler",
            "name": "Schedule",
            "block": [
                {
                    "number": 1,
                    "keyword": "action",
                    "uuid": "action-1",
                    "provider": "http",
                    "name": "Call HTTP",
                    "input": {"url": "https://example.com"},
                }
            ],
        },
        "config": [
            {"provider": "scheduler"},
        ],
    }

    result = await validator.validate_recipe(recipe_data)

    assert not result.is_valid
    assert any(
        "missing from config section" in error.message for error in result.errors
    )


@pytest.mark.asyncio
async def test_validate_recipe_detects_invalid_formula(
    validator: RecipeValidator,
) -> None:
    validator.known_adapters = {"scheduler", "http"}
    recipe_data = {
        "code": {
            "number": 0,
            "keyword": "trigger",
            "uuid": "root",
            "provider": "scheduler",
            "name": "Schedule",
            "block": [
                {
                    "number": 1,
                    "keyword": "action",
                    "uuid": "action-1",
                    "provider": "http",
                    "name": "Call HTTP",
                    "input": {"message": "Result =_dp(1, 2)"},
                }
            ],
        },
        "config": [
            {"provider": "scheduler"},
            {"provider": "http"},
        ],
    }

    result = await validator.validate_recipe(recipe_data)

    assert not result.is_valid
    assert any(
        error.error_type is ErrorType.FORMULA_SYNTAX_INVALID for error in result.errors
    )


def test_validate_data_pill_structures_invalid_json(
    validator: RecipeValidator,
) -> None:
    errors = validator._validate_data_pill_structures(
        {"mapping": "#{_dp('not valid json')}"},
        line_number=5,
    )

    assert errors
    assert "Invalid JSON" in errors[0].message


def test_validate_data_pill_structures_missing_required_fields(
    validator: RecipeValidator,
) -> None:
    payload = '#{_dp(\'{"pill_type":"refs","line":"alias"}\')}'
    errors = validator._validate_data_pill_structures(
        {"mapping": payload},
        line_number=6,
    )

    assert errors
    assert "missing required field 'provider'" in errors[0].message


def test_validate_data_pill_structures_path_must_be_array(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    producer = make_line(
        number=1,
        keyword=Keyword.ACTION,
        uuid="producer",
        provider="http",
        as_="alias",
    )
    root = make_line(provider="scheduler", block=[producer])
    validator.current_recipe_root = root

    payload = (
        '#{_dp(\'{"pill_type":"refs","provider":"http",'
        '"line":"alias","path":"not array"}\')}'
    )
    errors = validator._validate_data_pill_structures(
        {"mapping": payload},
        line_number=7,
    )

    assert errors
    assert any(err.field_path and err.field_path[-1] == "path" for err in errors)


def test_validate_data_pill_structures_unknown_step(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    validator.current_recipe_root = make_line(provider="scheduler")
    payload = (
        '#{_dp(\'{"pill_type":"refs","provider":"http","line":"missing","path":[]}\')}'
    )
    errors = validator._validate_data_pill_structures(
        {"mapping": payload},
        line_number=8,
    )

    assert errors
    assert "non-existent step" in errors[0].message


def test_validate_array_consistency_flags_inconsistent_paths(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    loop_step = make_line(
        number=1,
        keyword=Keyword.ACTION,
        uuid="loop",
        provider="http",
        as_="loop",
    )
    root = make_line(provider="scheduler", block=[loop_step])
    validator.current_recipe_root = root

    line = make_line(
        number=2,
        keyword=Keyword.ACTION,
        uuid="mapper",
        provider="http",
        input={
            "____source": (
                '#{_dp(\'{"provider":"http","line":"loop","path":["data","items"]}\')}'
            ),
            "value": (
                '#{_dp(\'{"provider":"http","line":"loop","path":["data","items","value"]}\')}'
            ),
        },
    )

    errors = validator._validate_array_consistency(line.input or {}, line.number)

    assert errors
    assert "Array element path inconsistent" in errors[0].message


def test_validate_array_mappings_enhanced_requires_current_item(
    validator: RecipeValidator,
) -> None:
    line = RecipeLine(
        number=3,
        keyword=Keyword.ACTION,
        uuid="mapper",
        provider="http",
        input={
            "____source": (
                '#{_dp(\'{"provider":"http","line":"loop","path":["data","items"]}\')}'
            ),
            "value": (
                '#{_dp(\'{"provider":"http","line":"loop","path":["data","items","value"]}\')}'
            ),
        },
    )

    errors = validator._validate_array_mappings_enhanced(line)

    assert errors
    assert errors[0].error_type is ErrorType.ARRAY_MAPPING_INVALID


def test_recipe_line_field_validators_raise_on_long_values() -> None:
    with pytest.raises(ValueError):
        RecipeLine.model_validate(
            {
                "number": 1,
                "keyword": "action",
                "uuid": "valid-uuid",
                "provider": "http",
                "as": "a" * 49,
            }
        )

    with pytest.raises(ValueError):
        RecipeLine.model_validate(
            {
                "number": 1,
                "keyword": "action",
                "uuid": "u" * 37,
                "provider": "http",
            }
        )

    with pytest.raises(ValueError):
        RecipeLine.model_validate(
            {
                "number": 1,
                "keyword": "action",
                "uuid": "valid",
                "provider": "http",
                "job_report_schema": [{}] * 11,
            }
        )


def test_recipe_structure_requires_trigger_start_validation(
    make_line: Callable[..., RecipeLine],
) -> None:
    with pytest.raises(ValueError):
        RecipeStructure(root=make_line(keyword=Keyword.ACTION))


def test_validate_line_structure_branch_coverage(
    make_line: Callable[..., RecipeLine],
) -> None:
    errors_if = RecipeStructure._validate_line_structure(
        make_line(number=1, keyword=Keyword.IF, block=[]),
        [],
    )
    assert errors_if

    errors_foreach = RecipeStructure._validate_line_structure(
        make_line(number=2, keyword=Keyword.FOREACH, source=None),
        [],
    )
    assert errors_foreach

    errors_repeat = RecipeStructure._validate_line_structure(
        make_line(number=3, keyword=Keyword.REPEAT, block=None),
        [],
    )
    assert errors_repeat

    errors_try = RecipeStructure._validate_line_structure(
        make_line(number=4, keyword=Keyword.TRY, block=None),
        [],
    )
    assert errors_try

    errors_action = RecipeStructure._validate_line_structure(
        make_line(
            number=5, keyword=Keyword.ACTION, block=[make_line(number=6, uuid="child")]
        ),
        [],
    )
    assert errors_action


def test_validate_if_structure_unexpected_keyword(
    make_line: Callable[..., RecipeLine],
) -> None:
    else_line = make_line(number=2, keyword=Keyword.ELSE)
    invalid = make_line(number=3, keyword=Keyword.APPLICATION)
    line = make_line(
        number=1,
        keyword=Keyword.IF,
        block=[make_line(number=1, keyword=Keyword.ACTION), else_line, invalid],
    )

    errors = RecipeStructure._validate_if_structure(line, [])
    assert any("Unexpected line type" in err.message for err in errors)


def test_validate_try_structure_unexpected_keyword(
    make_line: Callable[..., RecipeLine],
) -> None:
    catch_line = make_line(number=2, keyword=Keyword.CATCH)
    invalid = make_line(number=3, keyword=Keyword.APPLICATION)
    line = make_line(
        number=1,
        keyword=Keyword.TRY,
        block=[make_line(number=1, keyword=Keyword.ACTION), catch_line, invalid],
    )

    errors = RecipeStructure._validate_try_structure(line, [])
    assert any("Unexpected line type" in err.message for err in errors)


def test_validate_providers_unknown_and_metadata_errors(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    validator.known_adapters = {"http"}
    line_unknown = make_line(number=1, keyword=Keyword.ACTION, provider="mystery")
    errors_unknown = validator._validate_providers(line_unknown)
    assert any("Unknown provider" in err.message for err in errors_unknown)

    validator.connector_metadata = {
        "http": {"triggers": {"valid": {}}, "actions": {"valid": {}}, "categories": []}
    }
    trigger_line = make_line(
        number=2,
        keyword=Keyword.TRIGGER,
        provider="http",
        name="missing",
    )
    action_line = make_line(
        number=3,
        keyword=Keyword.ACTION,
        provider="http",
        name="missing",
    )

    trigger_errors = validator._validate_providers(trigger_line)
    action_errors = validator._validate_providers(action_line)

    assert any("Unknown trigger" in err.message for err in trigger_errors)
    assert any("Unknown action" in err.message for err in action_errors)


def test_validate_providers_skips_non_action_keywords(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    validator.known_adapters = {"http"}
    foreach_line = make_line(number=4, keyword=Keyword.FOREACH, provider="http")

    assert validator._validate_providers(foreach_line) == []


def test_validate_references_with_repeat_context(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    step_context = {
        "http_step": {
            "provider": "http",
            "keyword": "action",
            "number": 1,
            "name": "HTTP",
        }
    }
    repeat_child = make_line(
        number=3,
        keyword=Keyword.ACTION,
        provider="http",
        input={"url": "#{_dp('data.http.http_step.result')}"},
    )
    repeat_line = make_line(
        number=2,
        keyword=Keyword.REPEAT,
        provider="control",
        as_="loop",
        block=[repeat_child],
    )

    errors = validator._validate_references_with_context(repeat_line, step_context)
    assert isinstance(errors, list)


def test_validate_references_if_branch(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    step_context = {
        "http_step": {
            "provider": "http",
            "keyword": "action",
            "number": 1,
            "name": "HTTP",
        }
    }
    if_line = make_line(
        number=4,
        keyword=Keyword.IF,
        provider="control",
        input={"condition": "#{_dp('data.http.http_step.status')}"},
    )

    errors = validator._validate_references_with_context(if_line, step_context)
    assert isinstance(errors, list)


def test_validate_config_coverage_missing_provider(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    root = make_line(
        number=0,
        keyword=Keyword.TRIGGER,
        provider="scheduler",
        block=[make_line(number=1, keyword=Keyword.ACTION, provider="http")],
    )

    errors = validator._validate_config_coverage(
        root,
        config=[{"provider": "scheduler"}],
    )

    assert any("Provider 'http'" in err.message for err in errors)


@pytest.mark.asyncio
async def test_validate_recipe_handles_parsing_error(
    validator: RecipeValidator,
) -> None:
    invalid_recipe = {"code": {"provider": "missing-number"}}

    result = await validator.validate_recipe(invalid_recipe)

    assert not result.is_valid
    assert any("Recipe parsing failed" in err.message for err in result.errors)


def test_validate_recipe_handles_parsing_error_sync(validator: RecipeValidator) -> None:
    invalid_recipe = {"code": {"provider": "missing-number"}}

    result = asyncio.run(validator.validate_recipe(invalid_recipe))

    assert not result.is_valid
    assert any("Recipe parsing failed" in err.message for err in result.errors)


# Test cache functionality
@pytest.mark.asyncio
async def test_load_cached_connectors_cache_miss(validator: RecipeValidator) -> None:
    """Test loading connectors when cache file doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        validator._cache_file = Path(tmpdir) / "nonexistent.json"
        result = validator._load_cached_connectors()
        assert result is False


@pytest.mark.asyncio
async def test_load_cached_connectors_expired_cache(validator: RecipeValidator) -> None:
    """Test loading connectors when cache is expired"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = Path(tmpdir) / "cache.json"
        cache_data = {
            "known_adapters": ["http"],
            "connector_metadata": {},
            "last_update": 0,
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)

        # Set modification time to past
        old_time = time.time() - (validator._cache_ttl_hours * 3600 + 1)
        import os

        os.utime(cache_file, times=(old_time, old_time))

        validator._cache_file = cache_file
        result = validator._load_cached_connectors()
        assert result is False


@pytest.mark.asyncio
async def test_load_cached_connectors_valid_cache(validator: RecipeValidator) -> None:
    """Test loading connectors from valid cache"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = Path(tmpdir) / "cache.json"
        cache_data = {
            "known_adapters": ["http", "scheduler"],
            "connector_metadata": {"http": {"type": "platform"}},
            "last_update": time.time(),
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)

        validator._cache_file = cache_file
        result = validator._load_cached_connectors()

        assert result is True
        assert validator.known_adapters == {"http", "scheduler"}
        assert validator.connector_metadata == {"http": {"type": "platform"}}


@pytest.mark.asyncio
async def test_load_cached_connectors_invalid_json(validator: RecipeValidator) -> None:
    """Test loading connectors with invalid JSON in cache"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = Path(tmpdir) / "cache.json"
        with open(cache_file, "w") as f:
            f.write("invalid json content")

        validator._cache_file = cache_file
        result = validator._load_cached_connectors()
        assert result is False


@pytest.mark.asyncio
async def test_save_connectors_to_cache_success(validator: RecipeValidator) -> None:
    """Test saving connectors to cache successfully"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = Path(tmpdir) / "cache.json"
        validator._cache_file = cache_file
        validator.known_adapters = {"http", "scheduler"}
        validator.connector_metadata = {"http": {"type": "platform"}}

        validator._save_connectors_to_cache()

        assert cache_file.exists()
        with open(cache_file) as f:
            saved_data = json.load(f)
        assert set(saved_data["known_adapters"]) == {"http", "scheduler"}
        assert saved_data["connector_metadata"] == {"http": {"type": "platform"}}


@pytest.mark.asyncio
async def test_save_connectors_to_cache_permission_error(
    validator: RecipeValidator,
) -> None:
    """Test saving connectors when permission denied"""
    validator._cache_file = Path("/nonexistent/readonly/cache.json")
    validator.known_adapters = {"http"}
    validator.connector_metadata = {}

    # Should not raise exception, just return silently
    validator._save_connectors_to_cache()


@pytest.mark.asyncio
async def test_ensure_connectors_loaded_first_time() -> None:
    """Test ensuring connectors are loaded for the first time"""
    validator = RecipeValidator(Mock())
    validator._connectors_loaded = False

    with patch.object(
        validator,
        "_load_builtin_connectors",
        new=AsyncMock(),
    ) as mock_load:
        await validator._ensure_connectors_loaded()
        mock_load.assert_called_once()
        assert validator._connectors_loaded is True


@pytest.mark.asyncio
async def test_ensure_connectors_loaded_already_loaded(
    validator: RecipeValidator,
) -> None:
    """Test ensuring connectors when already loaded"""
    validator._connectors_loaded = True

    with patch.object(
        validator, "_load_builtin_connectors", new=AsyncMock()
    ) as mock_load:
        await validator._ensure_connectors_loaded()
        mock_load.assert_not_called()


@pytest.mark.asyncio
async def test_load_builtin_connectors_from_api(validator: RecipeValidator) -> None:
    """Test loading connectors from API when cache fails"""
    # Mock API responses
    mock_platform_response = MagicMock()
    platform_connector = Mock(
        deprecated=False,
        categories=["Data"],
        triggers={"webhook": {}},
        actions={"get": {}},
    )
    platform_connector.name = "HTTP"
    mock_platform_response.items = [platform_connector]

    mock_custom_response = MagicMock()
    custom_connector = Mock(id=1)
    custom_connector.name = "Custom"
    mock_custom_response.result = [custom_connector]

    mock_code_response = MagicMock()
    mock_code_response.data.code = "connector code"

    workato_client = cast(Any, validator.workato_api_client)
    workato_client.connectors_api = Mock()
    connectors_api = cast(Any, workato_client.connectors_api)
    connectors_api.list_platform_connectors = AsyncMock(
        return_value=mock_platform_response,
    )
    connectors_api.list_custom_connectors = AsyncMock(return_value=mock_custom_response)
    connectors_api.get_custom_connector_code = AsyncMock(
        return_value=mock_code_response
    )

    # Mock cache loading to fail
    with (
        patch.object(validator, "_load_cached_connectors", return_value=False),
        patch.object(validator, "_save_connectors_to_cache"),
    ):
        await validator._load_builtin_connectors()

    assert "http" in validator.known_adapters
    assert "custom" in validator.known_adapters
    assert "http" in validator.connector_metadata
    assert "custom" in validator.connector_metadata


@pytest.mark.asyncio
async def test_load_builtin_connectors_uses_cache_shortcut(
    validator: RecipeValidator,
) -> None:
    with patch.object(validator, "_load_cached_connectors", return_value=True):
        # Use a spec to control what attributes exist
        cast(Any, validator.workato_api_client).connectors_api = Mock(spec=[])
        await validator._load_builtin_connectors()

    # Should short-circuit without hitting the API
    assert not hasattr(
        validator.workato_api_client.connectors_api,
        "list_platform_connectors",
    )


# Test validation methods missing coverage
def test_is_valid_data_pill_edge_cases(validator: RecipeValidator) -> None:
    """Test data pill validation edge cases"""
    assert validator._is_valid_data_pill("data.http.step") is False  # Too few parts
    assert (
        validator._is_valid_data_pill("not_data.http.step.field") is False
    )  # Wrong prefix
    # Empty provider is actually valid because it just checks that parts exist
    assert (
        validator._is_valid_data_pill("data..step.field") is True
    )  # Empty provider (still valid)


def test_is_expression_edge_cases(validator: RecipeValidator) -> None:
    """Test expression detection edge cases"""
    assert validator._is_expression("") is False
    assert validator._is_expression("   ") is False
    assert validator._is_expression("text with #{} but no _") is False


def test_is_valid_expression_edge_cases(validator: RecipeValidator) -> None:
    """Test expression validation edge cases"""
    assert validator._is_valid_expression("") is False
    assert validator._is_valid_expression("   ") is False
    assert validator._is_valid_expression("valid expression") is True


def test_validate_input_expressions_recursive(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test input expression validation with nested structures"""
    line = make_line(
        number=1,
        keyword=Keyword.ACTION,
        input={
            "nested": {
                "array": ["=", {"key": "=  "}]  # Empty expressions after =
            }
        },
    )

    # Override the validator's _is_valid_expression to make these invalid
    with patch.object(validator, "_is_valid_expression", return_value=False):
        assert line.input is not None
        errors = validator._validate_input_expressions(line.input, line.number)

    assert len(errors) == 2
    assert all(err.error_type == ErrorType.INPUT_EXPR_INVALID for err in errors)


def test_collect_providers_recursive(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test provider collection from nested recipe structure"""
    child = make_line(number=2, keyword=Keyword.ACTION, provider="http")
    parent = make_line(
        number=1, keyword=Keyword.IF, provider="scheduler", block=[child]
    )

    providers: set[str] = set()
    validator._collect_providers(parent, providers)

    assert providers == {"scheduler", "http"}


def test_step_is_referenced_without_as(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test step reference detection when step has no 'as' value"""
    line = make_line(number=1, keyword=Keyword.ACTION, provider="http")
    validator.current_recipe_root = make_line()

    result = validator._step_is_referenced(line)
    assert result is False


def test_step_is_referenced_no_recipe_root(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test step reference detection when no recipe root is set"""
    line = make_line(number=1, keyword=Keyword.ACTION, provider="http", as_="step")
    validator.current_recipe_root = None

    result = validator._step_is_referenced(line)
    assert result is False


def test_step_exists_with_recipe_context(
    validator: RecipeValidator,
    make_line: Callable[..., RecipeLine],
) -> None:
    target = make_line(
        number=2,
        keyword=Keyword.ACTION,
        provider="http",
        **{"as": "http_step"},
    )
    root = make_line(block=[target])
    validator.current_recipe_root = root

    assert validator._step_exists("http", "http_step") is True
    assert validator._step_exists("http", "missing") is False


def test_find_references_to_step_no_provider_or_as(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test finding references when target step has no provider or as"""
    root = make_line()
    target_line_no_as = make_line(number=1, provider="http")
    target_line_no_provider = make_line(number=1, as_="step")

    result1 = validator._find_references_to_step(root, target_line_no_as)
    result2 = validator._find_references_to_step(root, target_line_no_provider)

    assert result1 is False
    assert result2 is False


def test_search_for_reference_pattern_in_blocks(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test searching for reference patterns in nested blocks"""
    child = make_line(
        number=2, keyword=Keyword.ACTION, input={"url": "data.http.step.result"}
    )
    parent = make_line(number=1, keyword=Keyword.IF, block=[child])

    result = validator._search_for_reference_pattern(parent, "data.http.step")
    assert result is True


def test_step_exists_no_recipe_context(validator: RecipeValidator) -> None:
    """Test step existence check without recipe context"""
    validator.current_recipe_root = None

    result = validator._step_exists("http", "step")
    assert result is True  # Should skip validation


def test_find_step_by_as_recursive_search(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test finding step by provider and as value in nested structure"""
    target = make_line(
        number=3, keyword=Keyword.ACTION, provider="http", **{"as": "target"}
    )
    child = make_line(number=2, keyword=Keyword.IF, block=[target])
    root = make_line(number=1, keyword=Keyword.TRIGGER, block=[child])

    result = validator._find_step_by_as(root, "http", "target")
    assert result == target

    # Test not found case
    result_not_found = validator._find_step_by_as(root, "missing", "target")
    assert result_not_found is None


def test_extract_path_from_dp_simple_syntax(validator: RecipeValidator) -> None:
    """Test extracting path from simple data pill syntax"""
    simple_dp = "#{_dp('data.http.step.field')}"
    result = validator._extract_path_from_dp(simple_dp)
    assert result == []


def test_extract_path_from_dp_invalid_json(validator: RecipeValidator) -> None:
    """Test extracting path from data pill with invalid JSON"""
    invalid_dp = "#{_dp('invalid json')}"
    result = validator._extract_path_from_dp(invalid_dp)
    assert result == []


def test_is_valid_element_path_edge_cases(validator: RecipeValidator) -> None:
    """Test element path validation edge cases"""
    # Empty paths
    assert validator._is_valid_element_path([], []) is True
    assert validator._is_valid_element_path(["source"], []) is True

    # Too short element path
    source_path = ["data", "items"]
    short_element = ["data"]
    assert validator._is_valid_element_path(source_path, short_element) is False

    # Mismatched prefix
    element_wrong_prefix = [
        "wrong",
        "items",
        {"path_element_type": "current_item"},
        "field",
    ]
    assert validator._is_valid_element_path(source_path, element_wrong_prefix) is False

    # Missing current_item marker
    element_no_marker = ["data", "items", "field"]
    assert validator._is_valid_element_path(source_path, element_no_marker) is False


def test_validate_formula_syntax_unmatched_parentheses(
    validator: RecipeValidator,
) -> None:
    """Test formula validation with unmatched parentheses"""
    errors = validator._validate_formula_syntax("=_dp('data.field'", "field", 1)
    assert len(errors) == 1
    assert "unmatched parentheses" in errors[0].message
    assert errors[0].error_type == ErrorType.FORMULA_SYNTAX_INVALID


def test_validate_formula_syntax_unknown_method(validator: RecipeValidator) -> None:
    """Test formula validation with unknown methods"""
    formula = "=_dp('data.field').unknown_method()"
    errors = validator._validate_formula_syntax(formula, "field", 1)
    assert len(errors) == 1
    assert "unknown_method" in errors[0].message
    assert errors[0].error_type == ErrorType.FORMULA_SYNTAX_INVALID


def test_validate_array_mappings_enhanced_nested_structures(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test enhanced array mapping validation with nested structures"""
    line = make_line(
        number=1,
        keyword=Keyword.ACTION,
        input={
            "nested": {
                "____source": "#{_dp('data.http.step')}",
                "items": [
                    {
                        "____source": "#{_dp('data.http.step2')}",
                        # Missing current_item mappings
                    }
                ],
            }
        },
    )

    errors = validator._validate_array_mappings_enhanced(line)
    assert len(errors) == 2  # Both nested objects should error
    assert all(err.error_type == ErrorType.ARRAY_MAPPING_INVALID for err in errors)


def test_validate_data_pill_structures_simple_syntax_validation(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test data pill structure validation with simple syntax"""
    # Set up recipe context
    target = make_line(
        number=1, keyword=Keyword.ACTION, provider="http", **{"as": "step"}
    )
    validator.current_recipe_root = make_line(block=[target])

    # Test too few parts
    errors_short = validator._validate_data_pill_structures(
        {"field": "#{_dp('data.http')}"},  # Missing as and field parts
        line_number=2,
    )
    assert len(errors_short) == 1
    assert "at least 4 parts" in errors_short[0].message

    # Test valid reference - should pass now that step exists with correct as value
    errors_valid = validator._validate_data_pill_structures(
        {"field": "#{_dp('data.http.step.result')}"}, line_number=2
    )
    assert len(errors_valid) == 0


def test_validate_data_pill_structures_complex_json_missing_fields(
    validator: RecipeValidator,
) -> None:
    """Test data pill structure validation with missing required fields in JSON"""
    incomplete_json = json.dumps(
        {
            "pill_type": "refs",
            "provider": "http",
            # Missing line and path
        }
    )

    errors = validator._validate_data_pill_structures(
        {"field": f"#{{_dp('{incomplete_json}')}}"}, line_number=1
    )

    assert len(errors) >= 2  # Should error for missing 'line' and 'path'
    missing_fields = [err for err in errors if "missing required field" in err.message]
    assert len(missing_fields) >= 2


def test_validate_data_pill_structures_path_not_array(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test data pill validation when path is not an array"""
    target = make_line(number=1, keyword=Keyword.ACTION, provider="http", as_="step")
    validator.current_recipe_root = make_line(block=[target])

    invalid_json = json.dumps(
        {
            "pill_type": "refs",
            "provider": "http",
            "line": "step",
            "path": "not_an_array",
        }
    )

    errors = validator._validate_data_pill_structures(
        {"field": f"#{{_dp('{invalid_json}')}}"}, line_number=1
    )

    assert len(errors) >= 1
    path_errors = [err for err in errors if "'path' must be an array" in err.message]
    assert len(path_errors) == 1


def test_validate_array_consistency_flags_missing_field_mappings_with_others(
    validator: RecipeValidator,
) -> None:
    payload_json = json.dumps({"provider": "http", "line": "loop", "path": ["data"]})
    payload = f"#{{_dp('{payload_json}')}}"
    input_data = {
        "mapper": {
            "____source": payload,
            "static_field": "no mapping here",
        }
    }

    errors = validator._validate_array_consistency(input_data, line_number=11)

    assert any("Consider mapping individual fields" in err.message for err in errors)


def test_validate_array_consistency_flags_missing_field_mappings_without_others(
    validator: RecipeValidator,
) -> None:
    payload_json = json.dumps({"provider": "http", "line": "loop", "path": ["data"]})
    payload = f"#{{_dp('{payload_json}')}}"
    input_data = {"mapper": {"____source": payload}}

    errors = validator._validate_array_consistency(input_data, line_number=12)

    assert any(
        "Array mapping with ____source found but no individual field mappings"
        in err.message
        for err in errors
    )


# Test control flow and edge cases
def test_validate_unique_as_values_nested_collection(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test unique as value validation with deeply nested structures"""
    # Use 'as' instead of 'as_' in the make_line calls since it uses Field(alias="as")
    inner = make_line(
        number=3, keyword=Keyword.ACTION, provider="http", **{"as": "dup"}
    )
    middle = make_line(number=2, keyword=Keyword.IF, block=[inner])
    outer = make_line(
        number=1,
        keyword=Keyword.FOREACH,
        provider="http",
        **{"as": "dup"},
        block=[middle],
    )

    errors = validator._validate_unique_as_values(outer)
    assert len(errors) == 1
    assert "Duplicate 'as' value 'dup'" in errors[0].message


def test_recipe_structure_validation_recursive_errors(
    make_line: Callable[..., RecipeLine],
) -> None:
    """Test recursive structure validation propagates errors"""
    # Create a structure with multiple validation errors
    bad_child = make_line(
        number=2, keyword=Keyword.FOREACH, source=None
    )  # Missing source
    bad_parent = make_line(number=1, keyword=Keyword.IF, block=None)  # Missing block
    root = make_line(number=0, keyword=Keyword.TRIGGER, block=[bad_parent, bad_child])

    with pytest.raises(ValueError) as exc_info:
        RecipeStructure(root=root)

    assert "structure validation failed" in str(exc_info.value)


# Additional tests for pagination and API loading edge cases
@pytest.mark.asyncio
async def test_load_builtin_connectors_pagination(validator: RecipeValidator) -> None:
    """Test connector loading with multiple pages"""
    # Mock first page with exactly 100 items (triggers pagination)
    first_page_connectors = []
    for i in range(100):
        conn = MagicMock()
        conn.name = f"Connector{i}"
        conn.deprecated = False
        conn.categories = ["Data"]
        conn.triggers = {}
        conn.actions = {}
        first_page_connectors.append(conn)

    # Mock second page with fewer items (ends pagination)
    last_conn = MagicMock()
    last_conn.name = "LastConnector"
    last_conn.deprecated = False
    last_conn.categories = ["Data"]
    last_conn.triggers = {}
    last_conn.actions = {}
    second_page_connectors = [last_conn]

    mock_first_response = MagicMock()
    mock_first_response.items = first_page_connectors

    mock_second_response = MagicMock()
    mock_second_response.items = second_page_connectors

    mock_custom_response = MagicMock()
    mock_custom_response.result = []

    # Set up paginated responses
    mock_list_platform = AsyncMock(
        side_effect=[mock_first_response, mock_second_response]
    )
    cast(Any, validator.workato_api_client).connectors_api = Mock(
        list_platform_connectors=mock_list_platform,
        list_custom_connectors=AsyncMock(return_value=mock_custom_response),
    )

    with (
        patch.object(validator, "_load_cached_connectors", return_value=False),
        patch.object(validator, "_save_connectors_to_cache"),
    ):
        await validator._load_builtin_connectors()

    # Should have called API twice for pagination
    assert mock_list_platform.call_count == 2
    # Should have loaded all 101 connectors
    assert len(validator.known_adapters) == 101 + 3


@pytest.mark.asyncio
async def test_load_builtin_connectors_empty_pages(validator: RecipeValidator) -> None:
    """Test connector loading when API returns empty pages"""
    mock_empty_response = MagicMock()
    mock_empty_response.items = []

    mock_custom_response = MagicMock()
    mock_custom_response.result = []

    cast(Any, validator.workato_api_client).connectors_api = Mock(
        list_platform_connectors=AsyncMock(return_value=mock_empty_response),
        list_custom_connectors=AsyncMock(return_value=mock_custom_response),
    )

    with (
        patch.object(validator, "_load_cached_connectors", return_value=False),
        patch.object(validator, "_save_connectors_to_cache"),
    ):
        await validator._load_builtin_connectors()

    # Should still complete successfully with empty results
    assert validator.known_adapters == {"scheduler", "http", "workato"}


def test_validate_data_pill_references_legacy_method(
    validator: RecipeValidator,
) -> None:
    """Test the legacy data pill validation method"""
    input_data = {"field": "#{_dp('data.http.unknown.field')}"}

    errors = validator._validate_data_pill_references(input_data, 1)

    # Should use empty context and return results
    assert isinstance(errors, list)


def test_step_uses_data_pills_detection(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test detection of data pill usage in step inputs"""
    # Step with data pills
    line_with_pills = make_line(
        number=1, input={"url": "#{_dp('data.trigger.step.url')}", "method": "GET"}
    )
    assert validator._step_uses_data_pills(line_with_pills) is True

    # Step without data pills
    line_without_pills = make_line(
        number=2, input={"url": "https://static.example.com", "method": "POST"}
    )
    assert validator._step_uses_data_pills(line_without_pills) is False

    # Step with no input
    line_no_input = make_line(number=3)
    assert validator._step_uses_data_pills(line_no_input) is False


def test_is_control_block_detection(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test control block detection"""
    # Control blocks
    if_line = make_line(number=1, keyword=Keyword.IF)
    elsif_line = make_line(number=2, keyword=Keyword.ELSIF)
    repeat_line = make_line(number=3, keyword=Keyword.REPEAT)

    assert validator._is_control_block(if_line) is True
    assert validator._is_control_block(elsif_line) is True
    assert validator._is_control_block(repeat_line) is True

    # Non-control blocks
    action_line = make_line(number=4, keyword=Keyword.ACTION)
    trigger_line = make_line(number=0, keyword=Keyword.TRIGGER)

    assert validator._is_control_block(action_line) is False
    assert validator._is_control_block(trigger_line) is False


def test_validate_generic_schema_usage_referenced_step(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test generic schema validation for referenced steps"""
    # Create a step that will be referenced
    referenced_step = make_line(
        number=1, keyword=Keyword.ACTION, provider="http", **{"as": "api_call"}
    )

    # Create step that references the first one
    referencing_step = make_line(
        number=2,
        keyword=Keyword.ACTION,
        input={"data": "#{_dp('data.http.api_call.result')}"},
    )

    root = make_line(block=[referenced_step, referencing_step])
    validator.current_recipe_root = root

    errors = validator._validate_generic_schema_usage(referenced_step)

    # Should error because referenced step lacks extended_output_schema
    assert len(errors) == 1
    assert errors[0].error_type == ErrorType.EXTENDED_SCHEMA_INVALID
    assert "extended_output_schema" in errors[0].message


def test_validate_config_coverage_builtin_connectors(
    validator: RecipeValidator, make_line: Callable[..., RecipeLine]
) -> None:
    """Test config coverage with builtin connectors exclusion"""
    validator.connector_metadata = {
        "workato_app": {"categories": ["App"]},  # Excluded by name
        "scheduler": {
            "categories": ["Workato"]
        },  # NOT in builtin_connectors (has "Workato")
        "custom_http": {"categories": ["Data"]},  # In builtin_connectors (no "Workato")
    }

    root = make_line(
        provider="scheduler",
        block=[make_line(number=1, keyword=Keyword.ACTION, provider="custom_http")],
    )

    config = [{"provider": "custom_http"}]  # Missing scheduler config

    errors = validator._validate_config_coverage(root, config)

    # Should error for missing scheduler config (has "Workato" in categories)
    assert len(errors) == 1
    assert "scheduler" in errors[0].message
    assert "missing from config section" in errors[0].message
