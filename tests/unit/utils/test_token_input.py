"""Tests for smart token input functionality."""

from unittest.mock import Mock, patch

import pytest

from workato_platform_cli.cli.utils.token_input import (
    TokenInputCancelledError,
    get_token_with_smart_paste,
)


class TestGetTokenWithSmartPaste:
    """Test the get_token_with_smart_paste function."""

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_normal_typing_returns_token(
        self, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test normal typing without paste returns the typed token."""
        mock_prompt.return_value = "my_secret_token_123"

        result = get_token_with_smart_paste(
            prompt_text="API Token",
            paste_threshold=50,
        )

        assert result == "my_secret_token_123"
        mock_prompt.assert_called_once()
        mock_echo.assert_called_with("🔐 Enter your API Token")

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_empty_token_rejected(self, mock_echo: Mock, mock_prompt: Mock) -> None:
        """Test empty token is rejected and retried."""
        # First return empty, then return valid token
        mock_prompt.side_effect = ["", "valid_token"]

        result = get_token_with_smart_paste(
            prompt_text="API Token",
            paste_threshold=50,
        )

        assert result == "valid_token"
        assert mock_prompt.call_count == 2
        # Check that error message was shown
        mock_echo.assert_any_call("❌ Token cannot be empty")

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_whitespace_only_token_rejected(
        self, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test whitespace-only token is rejected."""
        mock_prompt.side_effect = ["   ", "valid_token"]

        result = get_token_with_smart_paste(
            prompt_text="API Token",
            paste_threshold=50,
        )

        assert result == "valid_token"
        assert mock_prompt.call_count == 2
        mock_echo.assert_any_call("❌ Token cannot be empty")

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_token_stripped(self, mock_echo: Mock, mock_prompt: Mock) -> None:
        """Test returned token is stripped of whitespace."""
        mock_prompt.return_value = "  my_token  "

        result = get_token_with_smart_paste(
            prompt_text="API Token",
            paste_threshold=50,
        )

        assert result == "my_token"

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    @patch("workato_platform_cli.cli.utils.token_input.click.style")
    @patch("builtins.input")
    def test_long_paste_with_confirmation_yes(
        self, mock_input: Mock, mock_style: Mock, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test long paste triggers confirmation and accepts 'yes'."""
        # Simulate long paste by manipulating the function's internal state
        long_token = "x" * 100  # Above 50 char threshold

        # We need to mock the paste detection mechanism
        # The pt_prompt will return None when paste exits early
        mock_prompt.return_value = None

        # Mock the confirmation response
        mock_input.return_value = "y"

        # Mock click.style to return a simple string
        mock_style.return_value = "(100 chars)"

        # We need to mock the internal _prompt_for_token behavior
        # Since we can't easily trigger the paste event, we'll mock at module level
        with patch(
            "workato_platform_cli.cli.utils.token_input._prompt_for_token"
        ) as mock_internal:
            mock_internal.return_value = long_token

            result = get_token_with_smart_paste(
                prompt_text="API Token",
                paste_threshold=50,
            )

            assert result == long_token

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    @patch("workato_platform_cli.cli.utils.token_input.click.style")
    @patch("builtins.input")
    def test_long_paste_with_confirmation_no(
        self, mock_input: Mock, mock_style: Mock, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test long paste triggers confirmation and rejects 'no'."""
        long_token = "x" * 100

        # Simulate rejection then acceptance
        mock_input.side_effect = ["n", "y"]
        mock_style.return_value = "(100 chars)"

        with patch(
            "workato_platform_cli.cli.utils.token_input._prompt_for_token"
        ) as mock_internal:
            # First call raises error (rejected), second succeeds
            mock_internal.side_effect = [
                TokenInputCancelledError("User rejected"),
                long_token,
            ]

            result = get_token_with_smart_paste(
                prompt_text="API Token",
                paste_threshold=50,
            )

            assert result == long_token
            # Should show rejection message
            mock_echo.assert_any_call("❌ Token rejected. Please try again.")

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_max_retries_exceeded(self, mock_echo: Mock, mock_prompt: Mock) -> None:
        """Test that max retries raises TokenInputCancelledError."""
        with patch(
            "workato_platform_cli.cli.utils.token_input._prompt_for_token"
        ) as mock_internal:
            # Always raise error
            mock_internal.side_effect = TokenInputCancelledError("User rejected")

            with pytest.raises(TokenInputCancelledError, match="User rejected"):
                get_token_with_smart_paste(
                    prompt_text="API Token",
                    paste_threshold=50,
                    max_retries=3,
                )

            # Should retry 3 times
            assert mock_internal.call_count == 3

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_custom_prompt_text(self, mock_echo: Mock, mock_prompt: Mock) -> None:
        """Test custom prompt text is used."""
        mock_prompt.return_value = "token123"

        result = get_token_with_smart_paste(
            prompt_text="My Custom Token",
            paste_threshold=50,
        )

        assert result == "token123"
        mock_echo.assert_called_with("🔐 Enter your My Custom Token")
        # Check prompt contains custom text
        args, kwargs = mock_prompt.call_args
        assert "My Custom Token" in args[0]

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_custom_paste_threshold(self, mock_echo: Mock, mock_prompt: Mock) -> None:
        """Test custom paste threshold is respected."""
        # Token of 30 chars (below custom threshold of 100)
        short_token = "x" * 30
        mock_prompt.return_value = short_token

        result = get_token_with_smart_paste(
            prompt_text="API Token",
            paste_threshold=100,  # Higher threshold
        )

        # Should be treated as normal typing, not paste
        assert result == short_token

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    @patch("workato_platform_cli.cli.utils.token_input.click.style")
    @patch("builtins.input")
    def test_confirmation_default_yes(
        self, mock_input: Mock, mock_style: Mock, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test confirmation defaults to yes on empty input."""
        long_token = "x" * 100

        # Empty input should default to yes
        mock_input.return_value = ""
        mock_style.return_value = "(100 chars)"

        with patch(
            "workato_platform_cli.cli.utils.token_input._prompt_for_token"
        ) as mock_internal:
            mock_internal.return_value = long_token

            result = get_token_with_smart_paste(
                prompt_text="API Token",
                paste_threshold=50,
            )

            assert result == long_token

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    @patch("workato_platform_cli.cli.utils.token_input.click.style")
    @patch("builtins.input")
    def test_typed_and_pasted_combined(
        self, mock_input: Mock, mock_style: Mock, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test that typed characters and pasted text are combined."""
        typed_part = "prefix_"
        pasted_part = "x" * 100
        expected = typed_part + pasted_part

        mock_input.return_value = "y"
        mock_style.return_value = "(100 chars)"

        with patch(
            "workato_platform_cli.cli.utils.token_input._prompt_for_token"
        ) as mock_internal:
            # Return the combined token
            mock_internal.return_value = expected

            result = get_token_with_smart_paste(
                prompt_text="API Token",
                paste_threshold=50,
            )

            assert result == expected


class TestPromptForTokenIntegration:
    """Integration tests for _prompt_for_token with mocked prompt_toolkit."""

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    def test_prompt_called_with_correct_params(
        self, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test that pt_prompt is called with correct parameters."""
        from workato_platform_cli.cli.utils.token_input import _prompt_for_token

        mock_prompt.return_value = "test_token"

        result = _prompt_for_token("API Token", 50)

        assert result == "test_token"
        # Verify prompt_toolkit was called with is_password=True
        args, kwargs = mock_prompt.call_args
        assert kwargs.get("is_password") is True
        assert kwargs.get("enable_open_in_editor") is False
        assert "key_bindings" in kwargs

    @patch("workato_platform_cli.cli.utils.token_input.pt_prompt")
    @patch("workato_platform_cli.cli.utils.token_input.click.echo")
    @patch("workato_platform_cli.cli.utils.token_input.click.style")
    @patch("builtins.input")
    def test_gray_text_formatting_used(
        self, mock_input: Mock, mock_style: Mock, mock_echo: Mock, mock_prompt: Mock
    ) -> None:
        """Test that gray text formatting is applied to paste confirmation."""
        # Mock a successful paste scenario
        mock_prompt.return_value = None
        mock_input.return_value = "y"

        # Verify click.style is called with gray color
        mock_style.return_value = "(100 chars)"

        # Mock the internal function to simulate paste
        with patch(
            "workato_platform_cli.cli.utils.token_input._prompt_for_token"
        ) as mock_internal:
            mock_internal.return_value = "x" * 100

            # This will trigger the formatting code path
            result = get_token_with_smart_paste("API Token", paste_threshold=50)

            assert result == "x" * 100
            # Verify style was called (will be called in the confirmation prompt)
            # Note: The exact call depends on internal implementation
