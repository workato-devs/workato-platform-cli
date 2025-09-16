"""Tests for recipe validator."""

from unittest.mock import Mock, patch

from workato_platform.cli.commands.recipes.validator import (
    ErrorType,
    RecipeLine,
    RecipeValidator,
    ValidationError,
    ValidationResult,
)


class TestRecipeValidator:
    """Test the RecipeValidator class."""

    @patch("asyncio.run")
    def test_recipe_validator_initialization(self, mock_asyncio_run):
        """Test RecipeValidator can be initialized."""
        mock_asyncio_run.return_value = None  # Mock asyncio.run

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        assert validator.workato_api_client == mock_client
        mock_asyncio_run.assert_called_once()

    def test_validation_error_creation(self):
        """Test ValidationError can be created."""
        error = ValidationError(
            message="Test error",
            error_type=ErrorType.STRUCTURE_INVALID,
            line_number=5,
            field_path=["trigger", "input"],
        )

        assert error.message == "Test error"
        assert error.error_type == ErrorType.STRUCTURE_INVALID
        assert error.line_number == 5
        assert error.field_path == ["trigger", "input"]

    def test_error_type_enum_values(self):
        """Test that ErrorType enum has expected values."""
        # Should have various error types defined
        assert hasattr(ErrorType, "STRUCTURE_INVALID")
        assert hasattr(ErrorType, "INPUT_INVALID_BY_ADAPTER")
        assert hasattr(ErrorType, "FORMULA_SYNTAX_INVALID")

    @patch("asyncio.run")
    def test_recipe_validation_with_valid_recipe(self, mock_asyncio_run):
        """Test validation with a valid recipe structure."""
        mock_asyncio_run.return_value = None  # Mock asyncio.run

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        recipe_data = {
            "name": "Test Recipe",
            "trigger": {"provider": "scheduler", "name": "scheduled_job"},
            "actions": [{"provider": "http", "name": "get_request"}],
        }

        # Should not raise exception
        result = validator.validate_recipe(recipe_data)
        assert isinstance(result, ValidationResult)

    def test_recipe_line_creation(self):
        """Test RecipeLine can be created."""
        line = RecipeLine(
            provider="http",
            name="get_request",
            input={"url": "https://api.example.com"},
            number=1,
            keyword="action",
            uuid="test-uuid",
        )

        assert line.provider == "http"
        assert line.name == "get_request"
        assert line.input == {"url": "https://api.example.com"}
        assert line.number == 1

    @patch("asyncio.run")
    def test_recipe_validator_decorators(self, mock_asyncio_run):
        """Test that validator methods have proper decorators."""
        mock_asyncio_run.return_value = None

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        # These methods should exist and be callable
        assert hasattr(validator, "validate_recipe")
        assert callable(validator.validate_recipe)

        assert hasattr(validator, "_validate_input_modes")
        assert callable(validator._validate_input_modes)

        assert hasattr(validator, "_extract_data_pills")
        assert callable(validator._extract_data_pills)

    @patch("asyncio.run")
    def test_recipe_validation_with_invalid_provider(self, mock_asyncio_run):
        """Test validation with invalid provider."""
        mock_asyncio_run.return_value = None

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        recipe_data = {
            "name": "Invalid Recipe",
            "trigger": {"provider": "nonexistent_provider", "name": "some_trigger"},
        }

        result = validator.validate_recipe(recipe_data)
        assert isinstance(result, ValidationResult)

    @patch("asyncio.run")
    def test_expression_validation(self, mock_asyncio_run):
        """Test expression validation."""
        mock_asyncio_run.return_value = None

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        # Test if expressions can be identified
        test_expression = "=_dp('trigger.data.name')"
        is_expr = validator._is_expression(test_expression)
        assert isinstance(is_expr, bool)

    @patch("asyncio.run")
    def test_input_mode_validation(self, mock_asyncio_run):
        """Test input mode validation."""
        mock_asyncio_run.return_value = None

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        # Create a recipe line with mixed input modes
        line = RecipeLine(
            provider="http",
            name="get_request",
            input={
                "url": "=_dp('trigger.data.url') + #{_dp('trigger.data.path')}",
                "method": "GET",
            },
            number=1,
            keyword="action",
            uuid="test-uuid",
        )

        errors = validator._validate_input_modes(line)
        assert isinstance(errors, list)

    @patch("asyncio.run")
    def test_data_pill_extraction(self, mock_asyncio_run):
        """Test data pill extraction."""
        mock_asyncio_run.return_value = None

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        # Test data pill extraction from text
        text_with_pills = "#{_dp('trigger.data.name')} and #{_dp('action.data.id')}"
        pills = validator._extract_data_pills(text_with_pills)
        assert isinstance(pills, list)

    @patch("asyncio.run")
    def test_validator_instance_methods(self, mock_asyncio_run):
        """Test that validator has expected methods."""
        mock_asyncio_run.return_value = None

        mock_client = Mock()
        validator = RecipeValidator(mock_client)

        # Test that required methods exist
        assert hasattr(validator, "validate_recipe")
        assert hasattr(validator, "_validate_input_modes")
        assert hasattr(validator, "_extract_data_pills")
        assert hasattr(validator, "_is_expression")

    def test_recipe_line_pydantic_validators(self):
        """Test RecipeLine pydantic validators work."""
        # Test valid RecipeLine creation
        line = RecipeLine(
            provider="http",
            name="get_request",
            number=1,
            keyword="action",
            uuid="valid-uuid-1234567890123456789012",  # 30 chars
            as_="short_name",  # Valid length
        )

        assert line.provider == "http"
        assert line.name == "get_request"
        assert len(line.uuid) <= 36

    def test_validation_result_structure(self):
        """Test ValidationResult structure."""
        # Test creating validation result
        errors = [
            ValidationError(
                message="Test error", error_type=ErrorType.STRUCTURE_INVALID
            )
        ]

        result = ValidationResult(is_valid=False, errors=errors)

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"
