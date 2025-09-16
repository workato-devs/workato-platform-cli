import asyncio
import json
import time

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from workato_platform import Workato
from workato_platform.client.workato_api.models.platform_connector import (
    PlatformConnector,
)


class Keyword(str, Enum):
    """Recipe keywords that define the structure"""

    TRIGGER = "trigger"
    ACTION = "action"
    IF = "if"
    ELSIF = "elsif"
    ELSE = "else"
    FOREACH = "foreach"
    REPEAT = "repeat"
    WHILE_CONDITION = "while_condition"
    TRY = "try"
    CATCH = "catch"
    STOP = "stop"
    APPLICATION = "application"


class ErrorType(str, Enum):
    """Validation error types"""

    SYNTAX_INVALID = "syntax_invalid"
    LINE_SYNTAX_INVALID = "line_syntax_invalid"
    LINE_ATTR_INVALID = "line_attr_invalid"
    INPUT_FIELD_INVALID = "input_field_invalid"
    INPUT_EXPR_INVALID = "input_expr_invalid"
    INPUT_UNKNOWN_DATA_PILL = "input_unknown_data_pill"
    INPUT_FIELD_BLANK = "input_field_blank"
    INPUT_VALUE_INVALID = "input_value_invalid"
    INPUT_INVALID_BY_ADAPTER = "input_invalid_by_adapter"
    DEPENDS_ON_INVALID = "depends_on_invalid"
    EXTERNAL_INPUT_INVALID = "external_input_invalid"
    DYNAMIC_FIELD_MAPPING_INVALID = "dynamic_field_mapping_invalid"
    EXTENDED_SCHEMA_INVALID = "extended_schema_invalid"
    STRUCTURE_INVALID = "structure_invalid"
    INPUT_MODE_INCONSISTENT = "input_mode_inconsistent"
    ARRAY_MAPPING_INVALID = "array_mapping_invalid"
    FORMULA_SYNTAX_INVALID = "formula_syntax_invalid"
    BLOCK_NUMBERING_INVALID = "block_numbering_invalid"


@dataclass
class ValidationError:
    """Individual validation error"""

    field_label: str | None = None
    value: Any = None
    message: str = ""
    field_path: list[str] | None = None
    error_type: ErrorType | None = None
    line_number: int | None = None


@dataclass
class ValidationResult:
    """Complete validation result"""

    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError] = field(default_factory=list)


class RecipeLine(BaseModel):
    """Base recipe line structure"""

    number: int
    keyword: Keyword
    uuid: str
    as_: str | None = Field(None, alias="as")
    input: dict[str, Any] | None = None
    block: list["RecipeLine"] | None = None
    comment: str | None = None
    custom_title: str | None = None
    description: str | None = None
    hidden_config_fields: list[str] | None = None
    name: str | None = None
    provider: str | None = None
    title: str | None = None
    visible_config_fields: list[str] | None = None
    wizard_finished: bool | None = Field(None, alias="wizardFinished")
    mask_data: bool | None = Field(None, alias="mask_data")
    skip: bool | None = None
    toggle_cfg: dict[str, Any] | None = Field(None, alias="toggleCfg")
    dynamic_pick_list_selection: dict[str, Any] | None = Field(
        None, alias="dynamicPickListSelection"
    )
    extended_input_schema: list[dict[str, Any]] | None = None
    extended_output_schema: list[dict[str, Any]] | None = None
    requirements: dict[str, Any] | None = None
    external_input_definition: dict[str, Any] | None = None
    filter: dict[str, Any] | None = None
    batch_size: int | None = Field(None, alias="batch_size")
    clear_scope: bool | None = Field(None, alias="clear_scope")
    repeat_mode: str | None = Field(None, alias="repeat_mode")
    source: str | None = None
    format_version: str | None = Field(None, alias="format_version")
    job_report_config: dict[str, Any] | None = None
    job_report_schema: list[dict[str, Any]] | None = None
    param: dict[str, Any] | None = None
    parameters_schema: list[dict[str, Any]] | None = None
    unfinished: bool | None = None

    class Config:
        extra = "allow"  # Allow extra fields for flexibility

    @field_validator("as_")
    @classmethod
    def validate_as_length(cls, v: str) -> str:
        if v and len(v) > 48:
            raise ValueError("'as' field must be 48 characters or less")
        return v

    @field_validator("uuid")
    @classmethod
    def validate_uuid_length(cls, v: str) -> str:
        if v and len(v) > 36:
            raise ValueError("UUID must be 36 characters or less")
        return v

    @field_validator("job_report_schema", "job_report_config")
    @classmethod
    def validate_job_report_size(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if v and len(v) > 10:
            raise ValueError("Job report schema/config must be 10 items or less")
        return v


class RecipeAccountId(BaseModel):
    zip_name: str
    name: str
    folder: str


class RecipeConfig(BaseModel):
    keyword: Keyword
    provider: str
    skip_validation: bool | None = None
    account_id: RecipeAccountId | None = None


class Recipe(BaseModel):
    name: str
    description: str | None = None
    version: int | None = None
    private: bool
    concurrency: int
    code: RecipeLine
    config: list[RecipeConfig]


class RecipeStructure(BaseModel):
    """Complete recipe structure"""

    root: RecipeLine

    @model_validator(mode="after")
    def validate_recipe_structure(self) -> "RecipeStructure":
        """Validate the overall recipe structure"""
        if not self.root:
            return self

        errors: list[ValidationError] = []

        # Must start with trigger
        if self.root.keyword != Keyword.TRIGGER:
            errors.append(
                ValidationError(
                    message="Recipe must start with a trigger",
                    error_type=ErrorType.SYNTAX_INVALID,
                    line_number=self.root.number,
                )
            )

        # Validate structure recursively
        structure_errors = self._validate_structure_recursive(self.root, [])
        errors.extend(structure_errors)

        if errors:
            raise ValueError(
                f"Recipe structure validation failed: {len(errors)} errors found"
            )

        return self

    @classmethod
    def _validate_structure_recursive(
        cls, line: RecipeLine, path: list[int]
    ) -> list[ValidationError]:
        """Recursively validate recipe structure"""
        errors = []
        current_path = path + [line.number]

        # Validate line-specific rules
        line_errors = cls._validate_line_structure(line, current_path)
        errors.extend(line_errors)

        # Validate children
        if line.block:
            for child in line.block:
                child_errors = cls._validate_structure_recursive(child, current_path)
                errors.extend(child_errors)

        return errors

    @classmethod
    def _validate_line_structure(
        cls, line: RecipeLine, path: list[int]
    ) -> list[ValidationError]:
        """Validate specific line structure rules"""
        errors = []

        # Validate keyword-specific rules
        if line.keyword == Keyword.IF:
            errors.extend(cls._validate_if_structure(line, path))
        elif line.keyword == Keyword.FOREACH:
            errors.extend(cls._validate_foreach_structure(line, path))
        elif line.keyword == Keyword.REPEAT:
            errors.extend(cls._validate_repeat_structure(line, path))
        elif line.keyword == Keyword.TRY:
            errors.extend(cls._validate_try_structure(line, path))
        elif line.keyword == Keyword.ACTION:
            errors.extend(cls._validate_action_structure(line, path))

        return errors

    @classmethod
    def _validate_if_structure(
        cls, line: RecipeLine, path: list[int]
    ) -> list[ValidationError]:
        """Validate IF block structure"""
        errors = []

        if not line.block:
            errors.append(
                ValidationError(
                    message="IF statement must have a block",
                    error_type=ErrorType.LINE_SYNTAX_INVALID,
                    line_number=line.number,
                )
            )
            return errors

        # Validate IF block structure: [top_level_lines*, elsif_lines*, else_line?]
        block = line.block
        i = 0

        # top_level_lines*
        while i < len(block) and block[i].keyword in [
            Keyword.ACTION,
            Keyword.IF,
            Keyword.FOREACH,
            Keyword.REPEAT,
            Keyword.TRY,
            Keyword.STOP,
        ]:
            i += 1

        # elsif_lines*
        while i < len(block) and block[i].keyword == Keyword.ELSIF:
            i += 1

        # else_line?
        if i < len(block) and block[i].keyword == Keyword.ELSE:
            i += 1

        if i < len(block):
            errors.append(
                ValidationError(
                    message=f"Unexpected line type '{block[i].keyword}' in IF block",
                    error_type=ErrorType.LINE_SYNTAX_INVALID,
                    line_number=block[i].number,
                )
            )

        return errors

    @classmethod
    def _validate_foreach_structure(
        cls, line: RecipeLine, path: list[int]
    ) -> list[ValidationError]:
        """Validate FOREACH structure"""
        errors = []

        if not line.source:
            errors.append(
                ValidationError(
                    message="FOREACH must have a source",
                    error_type=ErrorType.LINE_ATTR_INVALID,
                    line_number=line.number,
                )
            )

        return errors

    @classmethod
    def _validate_repeat_structure(
        cls, line: RecipeLine, path: list[int]
    ) -> list[ValidationError]:
        """Validate REPEAT structure"""
        errors = []

        if not line.block:
            errors.append(
                ValidationError(
                    message="REPEAT must have a block",
                    error_type=ErrorType.LINE_SYNTAX_INVALID,
                    line_number=line.number,
                )
            )

        return errors

    @classmethod
    def _validate_try_structure(
        cls, line: RecipeLine, path: list[int]
    ) -> list[ValidationError]:
        """Validate TRY block structure"""
        errors = []

        if not line.block:
            errors.append(
                ValidationError(
                    message="TRY statement must have a block",
                    error_type=ErrorType.LINE_SYNTAX_INVALID,
                    line_number=line.number,
                )
            )
            return errors

        # Validate TRY block structure: [top_level_lines*, catch_line?]
        block = line.block
        i = 0

        # top_level_lines*
        while i < len(block) and block[i].keyword in [
            Keyword.ACTION,
            Keyword.IF,
            Keyword.FOREACH,
            Keyword.REPEAT,
            Keyword.TRY,
            Keyword.STOP,
        ]:
            i += 1

        # catch_line?
        if i < len(block) and block[i].keyword == Keyword.CATCH:
            i += 1

        if i < len(block):
            errors.append(
                ValidationError(
                    message=f"Unexpected line type '{block[i].keyword}' in TRY block",
                    error_type=ErrorType.LINE_SYNTAX_INVALID,
                    line_number=block[i].number,
                )
            )

        return errors

    @classmethod
    def _validate_action_structure(
        cls, line: RecipeLine, path: list[int]
    ) -> list[ValidationError]:
        """Validate ACTION structure"""
        errors = []

        if line.block:
            errors.append(
                ValidationError(
                    message="ACTION should not have a block",
                    error_type=ErrorType.LINE_SYNTAX_INVALID,
                    line_number=line.number,
                )
            )

        return errors


class RecipeValidator:
    """Main recipe validator class"""

    def __init__(
        self,
        workato_api_client: Workato,
    ):
        self.workato_api_client = workato_api_client
        self.known_adapters: set[str] = set()
        self.known_data_pills: set[str] = set()
        self.connection_configs: dict[str, Any] = {}
        self.platform_connectors: dict[str, Any] = {}
        self.custom_connectors: dict[str, Any] = {}
        self.connector_metadata: dict[str, dict[str, Any]] = {}
        self.current_recipe_root: RecipeLine | None = None

        # Cache settings
        self._cache_file = (
            Path.home() / ".workato_platform" / "cli" / "connector_cache.json"
        )
        self._cache_ttl_hours = 24  # Cache for 24 hours
        self._last_cache_update = None

        # Initialize with some well-known platform connectors
        asyncio.run(self._load_builtin_connectors())

    def _load_cached_connectors(self) -> bool:
        """Load connector metadata from cache if available and not expired"""
        try:
            if not self._cache_file.exists():
                return False

            # Check cache age
            cache_age = time.time() - self._cache_file.stat().st_mtime
            if cache_age > (self._cache_ttl_hours * 3600):
                return False  # Cache expired

            # Load from cache
            with open(self._cache_file) as f:
                cache_data = json.load(f)

            self.known_adapters = set(cache_data.get("known_adapters", []))
            self.connector_metadata = cache_data.get("connector_metadata", {})
            self._last_cache_update = cache_data.get("last_update", 0)

            return True

        except json.JSONDecodeError:
            return False

    def _save_connectors_to_cache(self) -> None:
        """Save connector metadata to cache file"""
        try:
            # Ensure cache directory exists
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)

            cache_data = {
                "known_adapters": list(self.known_adapters),
                "connector_metadata": self.connector_metadata,
                "last_update": time.time(),
                "cache_version": "1.0",
            }

            with open(self._cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

        except (OSError, PermissionError):
            return

    def validate_recipe(self, recipe_data: dict[str, Any]) -> ValidationResult:
        """Main validation entry point"""
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []

        try:
            # Extract the recipe code structure
            if "code" not in recipe_data:
                errors.append(
                    ValidationError(
                        message="Recipe must have a 'code' field",
                        error_type=ErrorType.SYNTAX_INVALID,
                    )
                )
                return ValidationResult(
                    is_valid=False, errors=errors, warnings=warnings
                )

            # Parse and validate basic structure
            recipe = RecipeStructure(root=RecipeLine(**recipe_data["code"]))

            # Set the current recipe root for cross-reference validation
            self.current_recipe_root = recipe.root

            # Validate unique 'as' values across all recipe steps
            as_errors = self._validate_unique_as_values(recipe.root)
            errors.extend(as_errors)

            # Validate block structure and numbering rules
            structure_errors = self._validate_block_structure(recipe.root)
            errors.extend(structure_errors)

            # Validate providers and trigger/action names
            provider_errors = self._validate_providers(recipe.root)
            errors.extend(provider_errors)

            # Validate references and dependencies with step context
            step_context: dict[str, Any] = {}  # Track available data sources
            ref_errors = self._validate_references_with_context(
                recipe.root, step_context
            )
            errors.extend(ref_errors)

            # Validate input/output schemas
            schema_errors = self._validate_schemas(recipe.root)
            errors.extend(schema_errors)

            # Validate expressions
            expr_errors = self._validate_expressions(recipe.root)
            errors.extend(expr_errors)

            # Validate array mappings and data pill structures
            array_errors = self._validate_array_mappings(recipe.root)
            errors.extend(array_errors)

            # Validate input modes and formulas
            input_mode_errors = self._validate_input_modes(recipe.root)
            errors.extend(input_mode_errors)

            # Validate config section coverage
            config_errors = self._validate_config_coverage(
                recipe.root, recipe_data.get("config", [])
            )
            errors.extend(config_errors)

        except Exception as e:
            errors.append(
                ValidationError(
                    message=f"Recipe parsing failed: {str(e)}",
                    error_type=ErrorType.SYNTAX_INVALID,
                )
            )

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings or []
        )

    async def _load_builtin_connectors(self) -> None:
        """Load connector metadata from cache or Workato API"""
        # Try to load from cache first
        if self._load_cached_connectors():
            return  # Successfully loaded from cache

        # Fetch platform connectors with pagination
        all_connectors: list[PlatformConnector] = []
        page: int = 1
        per_page = 100

        while True:
            response = (
                await self.workato_api_client.connectors_api.list_platform_connectors(
                    page=page,
                    per_page=per_page,
                )
            )

            connectors = response.items

            if not connectors:
                break

            all_connectors.extend(connectors)

            # If we got fewer than per_page results, we're on the last page
            if len(connectors) < per_page:
                break

            page += 1

        for platform_connector in all_connectors:
            provider_name = platform_connector.name.lower()
            self.known_adapters.add(provider_name)

            self.connector_metadata[provider_name] = {
                "type": "platform",
                "name": platform_connector.name,
                "deprecated": platform_connector.deprecated,
                "categories": platform_connector.categories,
                "triggers": platform_connector.triggers,
                "actions": platform_connector.actions,
            }

        # Fetch custom connectors
        customer_connectores_response = (
            await self.workato_api_client.connectors_api.list_custom_connectors()
        )

        for custom_connector in customer_connectores_response.result:
            provider_name = custom_connector.name.lower()
            code_response = (
                await self.workato_api_client.connectors_api.get_custom_connector_code(
                    custom_connector.id
                )
            )
            self.known_adapters.add(provider_name)
            self.connector_metadata[provider_name] = {
                "type": "custom",
                "name": custom_connector.name,
                "code": code_response.data.code,
                "triggers": [],  # Not Implemented
                "actions": [],  # Not Implemented
            }

        # Save to cache for next time
        self._save_connectors_to_cache()

    def _validate_providers(self, line: RecipeLine) -> list[ValidationError]:
        """Validate provider names and trigger/action names"""
        errors = []

        # Validate provider if present
        if line.provider:
            provider_name = line.provider.lower()

            # Check if provider is known
            if self.known_adapters and provider_name not in self.known_adapters:
                errors.append(
                    ValidationError(
                        message=(
                            f"Unknown provider '{line.provider}'. Provider not found in"
                            " available connectors."
                        ),
                        error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                        field_label="provider",
                        line_number=line.number,
                    )
                )

            # Validate trigger/action name if we have metadata
            if line.keyword not in [Keyword.TRIGGER, Keyword.ACTION]:
                return errors

            if provider_name in self.connector_metadata:
                connector_meta = self.connector_metadata[provider_name]

                if line.keyword == Keyword.TRIGGER:
                    available_triggers = connector_meta.get("triggers", {})
                    if available_triggers and line.name not in available_triggers:
                        trigger_names = ", ".join(list(available_triggers.keys()))
                        errors.append(
                            ValidationError(
                                message=(
                                    f"Unknown trigger '{line.name}' for provider "
                                    f"'{line.provider}'. Available "
                                    f"triggers: {trigger_names}"
                                ),
                                error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                field_label="name",
                                line_number=line.number,
                            )
                        )

                elif line.keyword == Keyword.ACTION:
                    available_actions = connector_meta.get("actions", {})
                    if available_actions and line.name not in available_actions:
                        action_names = ", ".join(list(available_actions.keys()))
                        errors.append(
                            ValidationError(
                                message=(
                                    f"Unknown action '{line.name}' for provider "
                                    f"'{line.provider}'. Available "
                                    f"actions: {action_names}"
                                ),
                                error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                field_label="name",
                                line_number=line.number,
                            )
                        )

        # Recursively validate children
        if line.block:
            for child in line.block:
                child_errors = self._validate_providers(child)
                errors.extend(child_errors)

        return errors

    def _validate_unique_as_values(self, line: RecipeLine) -> list[ValidationError]:
        """Validate that all 'as' values are unique across the recipe"""
        errors = []
        # as_value -> {"line_number": int, "provider": str, "keyword": str}
        as_tracker: dict[str, dict[str, Any]] = {}

        def collect_as_values(
            current_line: RecipeLine,
            path: list[int] | None = None,
        ) -> None:
            """Recursively collect all 'as' values and their locations"""
            if path is None:
                path = []

            current_path = path + [current_line.number]

            # Check if this line has an 'as' value
            if current_line.as_:
                as_value = current_line.as_

                if as_value in as_tracker:
                    # Found duplicate!
                    existing_info = as_tracker[as_value]
                    current_keyword = (
                        current_line.keyword.value
                        if hasattr(current_line.keyword, "value")
                        else str(current_line.keyword)
                    )

                    errors.append(
                        ValidationError(
                            message=(
                                f"Duplicate 'as' value '{as_value}' found. First used "
                                f"in {existing_info['keyword']} step "
                                f"{existing_info['line_number']} "
                                f"({existing_info['provider']}), also used in "
                                f"{current_keyword} step {current_line.number} "
                                f"({current_line.provider})"
                            ),
                            error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                            field_path=["as"],
                            line_number=current_line.number,
                        )
                    )
                else:
                    # Record this 'as' value
                    current_keyword = (
                        current_line.keyword.value
                        if hasattr(current_line.keyword, "value")
                        else str(current_line.keyword)
                    )

                    as_tracker[as_value] = {
                        "line_number": current_line.number,
                        "provider": current_line.provider or "unknown",
                        "keyword": current_keyword,
                        "path": current_path,
                    }

            # Recursively check children
            if current_line.block:
                for child in current_line.block:
                    collect_as_values(child, current_path)

        # Collect all 'as' values starting from root
        collect_as_values(line)

        return errors

    def _validate_references_with_context(
        self, line: RecipeLine, step_context: dict[str, Any]
    ) -> list[ValidationError]:
        """Validate references between steps with context tracking"""
        errors: list[ValidationError] = []

        # Add current step to context if it has an 'as' name
        # Note: Duplicate 'as' values are now caught early by _validate_unique_as_values
        if line.as_ and line.provider:
            step_context[line.as_] = {
                "provider": line.provider,
                "keyword": line.keyword.value
                if hasattr(line.keyword, "value")
                else str(line.keyword),
                "number": line.number,
                "name": line.name,
            }

        # Validate data pill references in input
        if line.input:
            pill_errors = self._validate_data_pill_references_with_context(
                line.input, line.number, step_context
            )
            errors.extend(pill_errors)

        # Validate data pill references in conditional input
        # (for if/elsif/while_condition)
        if (
            hasattr(line, "input")
            and line.input
            and line.keyword in [Keyword.IF, Keyword.ELSIF]
        ):
            pill_errors = self._validate_data_pill_references_with_context(
                line.input, line.number, step_context
            )
            errors.extend(pill_errors)

        # Validate children with updated context
        if line.block:
            # For repeat blocks, add special repeat context
            if line.keyword == Keyword.REPEAT and line.as_:
                repeat_context = step_context.copy()
                repeat_context[line.as_] = {
                    "provider": "repeat",
                    "keyword": "repeat",
                    "number": line.number,
                    "name": "repeat_processor",
                }
                for child in line.block:
                    child_errors = self._validate_references_with_context(
                        child, repeat_context
                    )
                    errors.extend(child_errors)
            else:
                for child in line.block:
                    child_errors = self._validate_references_with_context(
                        child, step_context
                    )
                    errors.extend(child_errors)

        return errors

    def _validate_data_pill_references_with_context(
        self, input_data: dict[str, Any], line_number: int, step_context: dict[str, Any]
    ) -> list[ValidationError]:
        """Validate data pill references in input fields with step context"""
        errors: list[ValidationError] = []

        def check_value(value: Any, field_path: list[str]) -> None:
            if isinstance(value, str):
                # Look for data pill patterns like #{_('data.provider.as.field')}
                pill_matches = self._extract_data_pills(value)
                for pill in pill_matches:
                    if not self._is_valid_data_pill(pill):
                        errors.append(
                            ValidationError(
                                message=(
                                    f"Invalid data pill format: '{pill}'. Expected "
                                    f"format: data.provider.as.field"
                                ),
                                error_type=ErrorType.INPUT_UNKNOWN_DATA_PILL,
                                field_path=field_path,
                                line_number=line_number,
                            )
                        )
                    else:
                        # Validate cross-reference
                        validation_error = self._validate_data_pill_cross_reference(
                            pill, line_number, step_context, field_path
                        )
                        if validation_error:
                            errors.append(validation_error)
            elif isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, field_path + [key])
            elif type(value).__name__ == "list":
                for i, val in enumerate(value):
                    check_value(val, field_path + [str(i)])

        check_value(input_data, [])
        return errors

    def _validate_data_pill_cross_reference(
        self,
        pill: str,
        line_number: int,
        step_context: dict[str, Any],
        field_path: list[str],
    ) -> ValidationError | None:
        """Validate that data pill references point to valid previous steps"""
        # Parse data pill: data.provider.as.field_path
        parts = pill.split(".")
        if len(parts) < 4:
            return None

        provider = parts[1]
        as_name = parts[2]

        # Check if the referenced step exists
        if as_name not in step_context:
            available_steps = list(step_context.keys())
            suggestion = (
                f" Available steps: {', '.join(available_steps[:5])}"
                if available_steps
                else ""
            )
            return ValidationError(
                message=f"Data pill references unknown step '{as_name}'.{suggestion}",
                error_type=ErrorType.INPUT_UNKNOWN_DATA_PILL,
                field_path=field_path,
                line_number=line_number,
            )

        # Validate provider matches
        step_info = step_context[as_name]
        if step_info["provider"] != provider:
            return ValidationError(
                message=(
                    f"Data pill provider mismatch: step '{as_name}' uses "
                    f"provider '{step_info['provider']}', not '{provider}'"
                ),
                error_type=ErrorType.INPUT_UNKNOWN_DATA_PILL,
                field_path=field_path,
                line_number=line_number,
            )

        return None

    def _validate_data_pill_references(
        self, input_data: dict[str, Any], line_number: int
    ) -> list[ValidationError]:
        """Legacy method - kept for compatibility"""
        return self._validate_data_pill_references_with_context(
            input_data, line_number, {}
        )

    def _extract_data_pills(self, text: str) -> list[str]:
        """Extract data pill references from text"""
        import re

        # Match Workato data pill format: #{_('data.provider.as.field')}
        pattern = r"#\{_\('([^']+)'\)\}"
        return re.findall(pattern, text)

    def _is_valid_data_pill(self, pill: str) -> bool:
        """Check if data pill reference is valid"""
        # Validate data pill format: data.provider.as.field_path
        if not pill.startswith("data."):
            return False

        parts = pill.split(".")
        if len(parts) < 4:  # Need at least: data.provider.as.field
            return False

        # Extract components
        prefix = parts[0]  # should be 'data'
        provider = parts[1]
        as_name = parts[2]
        # field_path is parts[3:]

        return prefix == "data" and provider is not None and as_name is not None

    def _validate_schemas(self, line: RecipeLine) -> list[ValidationError]:
        """Validate input/output schemas"""
        errors: list[ValidationError] = []

        # Validate children
        if line.block:
            for child in line.block:
                child_errors = self._validate_schemas(child)
                errors.extend(child_errors)

        return errors

    def _validate_expressions(self, line: RecipeLine) -> list[ValidationError]:
        """Validate expressions in recipe"""
        errors: list[ValidationError] = []

        # Validate expressions in input fields
        if line.input:
            expr_errors = self._validate_input_expressions(line.input, line.number)
            errors.extend(expr_errors)

        # Validate children
        if line.block:
            for child in line.block:
                child_errors = self._validate_expressions(child)
                errors.extend(child_errors)

        return errors

    def _validate_input_expressions(
        self, input_data: dict[str, Any], line_number: int
    ) -> list[ValidationError]:
        """Validate expressions in input fields"""
        errors = []

        def check_expression(value: Any, field_path: list[str]) -> None:
            if (
                isinstance(value, str)
                and self._is_expression(value)
                and not self._is_valid_expression(value)
            ):
                errors.append(
                    ValidationError(
                        message=f"Invalid expression syntax: {value}",
                        error_type=ErrorType.INPUT_EXPR_INVALID,
                        field_path=field_path,
                        line_number=line_number,
                    )
                )
            elif isinstance(value, dict):
                for key, val in value.items():
                    check_expression(val, field_path + [key])
            elif type(value).__name__ == "list":
                for i, val in enumerate(value):
                    check_expression(val, field_path + [str(i)])

        check_expression(input_data, [])
        return errors

    def _is_expression(self, text: str) -> bool:
        """Check if text is an expression"""
        # Basic expression detection
        return text.startswith("=") or "{{" in text

    def _is_valid_expression(self, expression: str) -> bool:
        """Validate expression syntax"""
        # Basic expression validation - could be enhanced
        # For now, just check if it's not empty
        return bool(expression and expression.strip())

    def _validate_config_coverage(
        self, line: RecipeLine, config: list[dict[str, Any]]
    ) -> list[ValidationError]:
        """Validate that all providers used in recipe have config entries"""
        errors = []

        # Collect all providers used in the recipe
        used_providers: set[str] = set()
        self._collect_providers(line, used_providers)

        # Collect providers declared in config
        config_providers: set[str] = set()
        for config_entry in config:
            if isinstance(config_entry, dict) and config_entry.get("provider"):
                config_providers.add(config_entry["provider"])

        builtin_connectors = {
            key
            for key, meta in self.connector_metadata.items()
            if key != "workato_app" and "Workato" not in meta["categories"]
        }

        # Check for missing config entries (excluding built-in connectors)
        missing_providers = used_providers - config_providers - builtin_connectors
        for provider in missing_providers:
            errors.append(
                ValidationError(
                    message=(
                        f"Provider '{provider}' is used in recipe but missing from "
                        f"config section"
                    ),
                    error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                    field_path=["config"],
                )
            )

        return errors

    def _collect_providers(self, line: RecipeLine, providers: set[str]) -> None:
        """Recursively collect all providers used in the recipe"""
        if line.provider:
            providers.add(line.provider)

        if line.block:
            for child in line.block:
                self._collect_providers(child, providers)

    def _validate_generic_schema_usage(self, line: RecipeLine) -> list[ValidationError]:
        """Generic schema validation based on actual usage patterns for any provider"""
        errors = []

        # Check if this step is referenced by others - needs extended_output_schema
        if self._step_is_referenced(line) and (
            not hasattr(line, "extended_output_schema")
            or not line.extended_output_schema
        ):
            errors.append(
                ValidationError(
                    message=(
                        f"Step {line.number} ({line.provider}) requires "
                        f"'extended_output_schema' because it's referenced by "
                        f"other steps"
                    ),
                    error_type=ErrorType.EXTENDED_SCHEMA_INVALID,
                    line_number=line.number,
                    field_path=["extended_output_schema"],
                )
            )

        return errors

    def _is_control_block(self, line: RecipeLine) -> bool:
        """Check if a step is a control block that doesn't need input schemas"""
        # Control blocks are if, while, repeat, etc. - they use data pills for
        # conditions but don't process input data that needs schemas
        return line.keyword in [
            Keyword.IF,
            Keyword.ELSIF,
            Keyword.WHILE_CONDITION,
            Keyword.REPEAT,
        ]

    def _step_uses_data_pills(self, line: RecipeLine) -> bool:
        """Check if a step uses data pill references in its input"""
        if not line.input:
            return False

        # Convert input to string to search for data pill patterns
        input_str = str(line.input)

        # Look for data pill patterns: #{_('...')} or #{...}
        import re

        data_pill_patterns = [
            r"#\{\s*_\([^)]+\)\s*\}",  # #{_('data.provider.as.field')}
            r"#\{[^}]+\}",  # #{simple_reference}
        ]

        return any(re.search(pattern, input_str) for pattern in data_pill_patterns)

    def _step_is_referenced(self, target_line: RecipeLine) -> bool:
        """Check if this step is referenced by other steps via data pills"""
        if not target_line.as_:
            return False  # Can't be referenced without an 'as' value

        if not self.current_recipe_root:
            return False

        # We need to check the entire recipe tree for references to this step
        # This requires access to the root of the recipe
        return self._find_references_to_step(self.current_recipe_root, target_line)

    def _find_references_to_step(
        self, search_root: RecipeLine, target_line: RecipeLine
    ) -> bool:
        """Recursively search for data pill references to a specific step"""
        if not target_line.as_ or not target_line.provider:
            return False

        # Pattern to look for: data.{provider}.{as_value}
        reference_pattern = f"data.{target_line.provider}.{target_line.as_}"

        return self._search_for_reference_pattern(search_root, reference_pattern)

    def _search_for_reference_pattern(self, line: RecipeLine, pattern: str) -> bool:
        """Recursively search for a data pill reference pattern"""
        # Check current line's input for the pattern
        if line.input:
            input_str = str(line.input)
            if pattern in input_str:
                return True

        # Check children
        if line.block:
            for child in line.block:
                if self._search_for_reference_pattern(child, pattern):
                    return True

        return False

    def _validate_array_mappings(self, line: RecipeLine) -> list[ValidationError]:
        """Validate array mapping structures and data pill patterns"""
        errors = []

        if line.input:
            errors.extend(self._validate_data_pill_structures(line.input, line.number))
            errors.extend(self._validate_array_consistency(line.input, line.number))

        # Check children
        if line.block:
            for child in line.block:
                child_errors = self._validate_array_mappings(child)
                errors.extend(child_errors)

        return errors

    def _validate_data_pill_structures(
        self, input_data: dict[str, Any], line_number: int
    ) -> list[ValidationError]:
        """Validate data pill JSON structures in _dp() patterns"""
        errors: list[ValidationError] = []
        import json
        import re

        def check_value(value: Any, field_path: list[str] | None = None) -> None:
            if field_path is None:
                field_path = []
            if isinstance(value, str):
                # Find all _dp() patterns
                dp_patterns = re.findall(r"#\{_dp\(\'([^\']+)\'\)\}", value)
                for dp_json in dp_patterns:
                    # Check if this is simple syntax (data.provider.as.field)
                    if dp_json.startswith("data."):
                        # Simple syntax - validate the data path structure
                        path_parts = dp_json.split(".")
                        if len(path_parts) < 4:  # data.provider.as.field (minimum)
                            errors.append(
                                ValidationError(
                                    message=(
                                        f"Simple data pill syntax must have at least 4 "
                                        "parts: data.provider.as.field in step "
                                        f"{line_number}"
                                    ),
                                    error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                    line_number=line_number,
                                    field_path=field_path + ["_dp"],
                                )
                            )
                        else:
                            # Validate provider/as reference exists
                            provider = path_parts[1]
                            as_value = path_parts[2]
                            if not self._step_exists(provider, as_value):
                                errors.append(
                                    ValidationError(
                                        message=(
                                            f"Simple data pill references non-existent "
                                            "step: provider='{provider}', "
                                            f"as='{as_value}' in step {line_number}"
                                        ),
                                        error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                        line_number=line_number,
                                        field_path=field_path + ["_dp"],
                                    )
                                )
                    else:
                        # Complex JSON syntax - parse and validate
                        try:
                            # Parse the JSON structure
                            dp_data = json.loads(dp_json)

                            # Validate required fields
                            required_fields = ["pill_type", "provider", "line", "path"]
                            for required_field in required_fields:
                                if required_field not in dp_data:
                                    errors.append(
                                        ValidationError(
                                            message=(
                                                f"Data pill missing required field "
                                                f"'{required_field}' in step "
                                                f"{line_number}"
                                            ),
                                            error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                            line_number=line_number,
                                            field_path=field_path + ["_dp"],
                                        )
                                    )

                            # Validate provider/line references exist
                            if (
                                "provider" in dp_data
                                and "line" in dp_data
                                and not self._step_exists(
                                    dp_data["provider"], dp_data["line"]
                                )
                            ):
                                errors.append(
                                    ValidationError(
                                        message=(
                                            f"Data pill references non-existent step: "
                                            f"provider='{dp_data['provider']}', "
                                            f"line='{dp_data['line']}' in step "
                                            f"{line_number}"
                                        ),
                                        error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                        line_number=line_number,
                                        field_path=field_path + ["_dp"],
                                    )
                                )

                            # Validate path is an array
                            if "path" in dp_data and not isinstance(
                                dp_data["path"], list
                            ):
                                errors.append(
                                    ValidationError(
                                        message=(
                                            f"Data pill 'path' must be an array in "
                                            f"step {line_number}"
                                        ),
                                        error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                        line_number=line_number,
                                        field_path=field_path + ["_dp", "path"],
                                    )
                                )

                        except json.JSONDecodeError:
                            errors.append(
                                ValidationError(
                                    message=(
                                        f"Invalid JSON in data pill _dp() pattern "
                                        f"in step {line_number}"
                                    ),
                                    error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                    line_number=line_number,
                                    field_path=field_path + ["_dp"],
                                )
                            )

            elif isinstance(value, dict):
                for key, subvalue in value.items():
                    check_value(subvalue, field_path + [key])

            elif isinstance(value, list):
                for i, subvalue in enumerate(value):
                    check_value(subvalue, field_path + [str(i)])

        check_value(input_data)
        return errors

    def _validate_array_consistency(
        self, input_data: dict[str, Any], line_number: int
    ) -> list[ValidationError]:
        """Validate array structure consistency (____source + element mappings)"""
        errors = []

        def check_array_structure(
            obj: Any, field_path: list[str] | None = None
        ) -> None:
            if field_path is None:
                field_path = []
            if isinstance(obj, dict):
                # Check if this looks like an array mapping structure
                if "____source" in obj:
                    source_path = self._extract_path_from_dp(obj["____source"])

                    # Check if there are any individual field mappings
                    has_element_mappings = False

                    # Check other fields for consistent element mappings
                    for key, value in obj.items():
                        if (
                            key != "____source"
                            and isinstance(value, str)
                            and "_dp(" in value
                        ):
                            has_element_mappings = True
                            element_path = self._extract_path_from_dp(value)

                            # Validate element path consistency
                            if (
                                source_path
                                and element_path
                                and not self._is_valid_element_path(
                                    source_path, element_path
                                )
                            ):
                                errors.append(
                                    ValidationError(
                                        message=(
                                            f"Array element path inconsistent with "
                                            f"source path in step {line_number}. "
                                            f"Source: {source_path}, Element: "
                                            f"{element_path}"
                                        ),
                                        error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                        line_number=line_number,
                                        field_path=field_path + [key],
                                    )
                                )

                    # Warn if ____source exists but no individual field mappings found
                    if not has_element_mappings:
                        # Check if there are any non-____source fields that could be
                        # element mappings
                        other_fields = [k for k in obj if k != "____source"]
                        if other_fields:
                            errors.append(
                                ValidationError(
                                    message=(
                                        f"Array mapping with ____source found but no "
                                        f"individual field mappings using _dp() with "
                                        f"current_item in step {line_number}. Consider "
                                        f"mapping individual fields: "
                                        f"{', '.join(other_fields[:3])}"
                                    ),
                                    error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                    line_number=line_number,
                                    field_path=field_path + ["____source"],
                                )
                            )
                        else:
                            errors.append(
                                ValidationError(
                                    message=(
                                        f"Array mapping with ____source found but "
                                        "no individual field mappings in step "
                                        f"{line_number}. Array elements cannot be "
                                        "accessed without field mappings."
                                    ),
                                    error_type=ErrorType.INPUT_INVALID_BY_ADAPTER,
                                    line_number=line_number,
                                    field_path=field_path + ["____source"],
                                )
                            )

                # Recursively check nested objects
                for key, value in obj.items():
                    check_array_structure(value, field_path + [key])

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_array_structure(item, field_path + [str(i)])

        check_array_structure(input_data)
        return errors

    def _step_exists(self, provider: str, as_value: str) -> bool:
        """Check if a step with given provider and as_value exists in the recipe"""
        if not hasattr(self, "current_recipe_root") or not self.current_recipe_root:
            return True  # Skip validation if we don't have recipe context

        return (
            self._find_step_by_as(self.current_recipe_root, provider, as_value)
            is not None
        )

    def _find_step_by_as(
        self, line: RecipeLine, provider: str, as_value: str
    ) -> RecipeLine | None:
        """Find a step by provider and as_value"""
        if line.provider == provider and line.as_ == as_value:
            return line

        if line.block:
            for child in line.block:
                result = self._find_step_by_as(child, provider, as_value)
                if result:
                    return result

        return None

    def _extract_path_from_dp(self, dp_string: str) -> list[Any]:
        """Extract path array from _dp() string"""
        import json
        import re

        match = re.search(r"#\{_dp\(\'([^\']+)\'\)\}", dp_string)
        if match:
            try:
                dp_data = json.loads(match.group(1))
                return dp_data.get("path", []) or []
            except json.JSONDecodeError:
                pass
        return []

    def _is_valid_element_path(self, source_path: list, element_path: list) -> bool:
        """Check if element path is a valid extension of source path"""
        if not source_path or not element_path:
            return True  # Skip validation if we can't parse paths

        # Element path should start with source path, then have current_item,
        # then additional fields
        if len(element_path) < len(source_path) + 2:
            return False

        # Check source path prefix matches
        if element_path[: len(source_path)] != source_path:
            return False

        # Check for current_item marker
        current_item_index = len(source_path)
        return (
            current_item_index < len(element_path)
            and isinstance(element_path[current_item_index], dict)
            and element_path[current_item_index].get("path_element_type")
            == "current_item"
        )

    def _validate_block_structure(self, line: RecipeLine) -> list[ValidationError]:
        """Validate block numbering and keyword rules"""
        errors = []

        # Block 0 must be trigger
        if line.number == 0 and line.keyword != Keyword.TRIGGER:
            errors.append(
                ValidationError(
                    message="Block 0 must be a trigger",
                    error_type=ErrorType.STRUCTURE_INVALID,
                    line_number=line.number,
                    field_label="keyword",
                )
            )

        # Note: Removed the rule that blocks 1+ must be actions
        # This was incorrect - recipes can have various block structures
        # including conditional blocks, repeat blocks, etc.

        # Recursively validate children
        if line.block:
            for child in line.block:
                child_errors = self._validate_block_structure(child)
                errors.extend(child_errors)

        return errors

    def _validate_input_modes(self, line: RecipeLine) -> list[ValidationError]:
        """Validate input mode consistency and formulas"""
        errors = []

        if line.input:
            for input_field, value in line.input.items():
                if isinstance(value, str):
                    # Check for mixed modes
                    has_formula = "=_dp(" in value
                    has_text = "#{_dp(" in value

                    if has_formula and has_text:
                        errors.append(
                            ValidationError(
                                message=(
                                    f"Mixed input modes detected in field "
                                    f"'{input_field}'. Consider using one mode "
                                    "per field for clarity."
                                ),
                                error_type=ErrorType.INPUT_MODE_INCONSISTENT,
                                line_number=line.number,
                                field_path=[input_field],
                            )
                        )

                    # Validate formula syntax if in formula mode
                    if has_formula:
                        formula_errors = self._validate_formula_syntax(
                            value, input_field, line.number
                        )
                        errors.extend(formula_errors)

        # Recursively validate children
        if line.block:
            for child in line.block:
                child_errors = self._validate_input_modes(child)
                errors.extend(child_errors)

        return errors

    def _validate_formula_syntax(
        self, value: str, field: str, line_number: int
    ) -> list[ValidationError]:
        """Validate formula syntax and allowed methods"""
        errors = []

        # Check if formula starts with =_dp(
        if not value.strip().startswith("=_dp("):
            errors.append(
                ValidationError(
                    message=f"Formula in field '{field}' must start with '=_dp('",
                    error_type=ErrorType.FORMULA_SYNTAX_INVALID,
                    line_number=line_number,
                    field_path=[field],
                )
            )

        # Check for common formula syntax issues
        if "=_dp(" in value:
            # Extract the data pill part
            start = value.find("=_dp(")
            end = value.find(")", start)
            if end == -1:
                errors.append(
                    ValidationError(
                        message=f"Formula in field '{field}' has unmatched parentheses",
                        error_type=ErrorType.FORMULA_SYNTAX_INVALID,
                        line_number=line_number,
                        field_path=[field],
                    )
                )
            else:
                # Check for common Ruby method calls
                formula_part = value[end + 1 :]
                if formula_part:
                    # Validate common Ruby methods
                    allowed_methods = [
                        "split",
                        "first",
                        "last",
                        "length",
                        "size",
                        "count",
                        "upcase",
                        "downcase",
                        "capitalize",
                        "strip",
                        "chomp",
                        "gsub",
                        "sub",
                        "replace",
                        "to_i",
                        "to_f",
                        "to_s",
                        "present?",
                        "blank?",
                        "nil?",
                        "empty?",
                        "map",
                        "select",
                        "filter",
                        "reject",
                        "find",
                        "detect",
                        "any?",
                        "all?",
                        "none?",
                        "one?",
                        "sum",
                        "min",
                        "max",
                        "average",
                        "mean",
                    ]

                    # Extract method calls (simple pattern matching)
                    import re

                    method_calls = re.findall(r"\.(\w+)\s*\(?", formula_part)
                    for method in method_calls:
                        if method not in allowed_methods:
                            errors.append(
                                ValidationError(
                                    message=(
                                        f"Method '{method}' in field '{field}' "
                                        "may not be supported. Common methods: "
                                        f"{', '.join(allowed_methods[:10])}..."
                                    ),
                                    error_type=ErrorType.FORMULA_SYNTAX_INVALID,
                                    line_number=line_number,
                                    field_path=[field],
                                )
                            )

        return errors

    def _validate_array_mappings_enhanced(
        self, line: RecipeLine
    ) -> list[ValidationError]:
        """Enhanced array mapping validation"""
        errors = []

        def check_array_mapping(obj: Any, field_path: list[str] | None = None) -> None:
            if field_path is None:
                field_path = []
            if isinstance(obj, dict):
                if "____source" in obj:
                    # Check if there are current_item mappings in the same object
                    has_current_item = False
                    for key, value in obj.items():
                        if (
                            key != "____source"
                            and isinstance(value, str)
                            and "current_item" in value
                        ):
                            has_current_item = True
                            break

                    if not has_current_item:
                        errors.append(
                            ValidationError(
                                message=(
                                    f"Field '{'.'.join(field_path)}' uses ____source "
                                    "but no current_item mappings found. Array "
                                    "elements cannot be accessed without mappings."
                                ),
                                error_type=ErrorType.ARRAY_MAPPING_INVALID,
                                line_number=line.number,
                                field_path=field_path,
                            )
                        )

                # Recursively check nested objects
                for key, value in obj.items():
                    check_array_mapping(value, field_path + [key])
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_array_mapping(item, field_path + [str(i)])

        if line.input:
            check_array_mapping(line.input)

        # Recursively validate children
        if line.block:
            for child in line.block:
                child_errors = self._validate_array_mappings_enhanced(child)
                errors.extend(child_errors)

        return errors
