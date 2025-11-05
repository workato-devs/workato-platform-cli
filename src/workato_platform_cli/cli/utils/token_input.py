"""Smart token input utility with paste detection.

This module provides a user-friendly API token input method that:
- Shows asterisks for typed characters (secure visual feedback)
- Detects long paste operations and shows confirmation dialog instead
- Avoids terminal buffer issues with very long tokens (750+ chars)
"""

import asyncclick as click

from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys


class TokenInputCancelledError(Exception):
    """Raised when user cancels token input."""

    pass


def get_token_with_smart_paste(
    prompt_text: str = "API Token",
    paste_threshold: int = 50,
    max_retries: int = 3,
) -> str:
    """Get API token with smart paste detection.

    For normal typing: Shows asterisks for each character
    For pasting long text (>paste_threshold chars): Shows checkmark and asks for
    confirmation

    Args:
        prompt_text: The prompt text to display
        paste_threshold: Character count threshold to trigger paste detection
        max_retries: Maximum number of retry attempts if user rejects pasted token

    Returns:
        str: The validated API token

    Raises:
        TokenInputCancelledError: If user cancels after max retries

    Example:
        >>> token = get_token_with_smart_paste()
        🔐 Enter your API Token
        API Token: ****  # User types
        >>> # or
        ✅ Detected API token (750 characters)
        Is this correct? [Y/n]: y
    """
    for attempt in range(max_retries):
        try:
            token = _prompt_for_token(prompt_text, paste_threshold)
            if token and token.strip():
                return token.strip()

            click.echo("❌ Token cannot be empty")

        except TokenInputCancelledError:
            if attempt < max_retries - 1:
                click.echo("❌ Token rejected. Please try again.")
            else:
                raise

    raise TokenInputCancelledError("Maximum retry attempts reached")


def _prompt_for_token(prompt_text: str, paste_threshold: int) -> str:
    """Internal method to prompt for token with paste detection.

    Args:
        prompt_text: The prompt text to display
        paste_threshold: Character count threshold to trigger paste detection

    Returns:
        str: The token (typed or pasted)

    Raises:
        TokenInputCancelledError: If user rejects the pasted token
    """
    bindings = KeyBindings()
    pasted_token: str | None = None
    typed_token: str = ""  # Store typed characters before paste

    @bindings.add(Keys.BracketedPaste)
    def handle_paste(event):  # type: ignore[no-untyped-def]
        """Handle paste events for long tokens.

        Bracketed paste mode allows terminals to signal when text is pasted
        vs typed. We use this to provide better UX for long API tokens.
        """
        nonlocal pasted_token, typed_token
        pasted_text: str = event.data

        if len(pasted_text) > paste_threshold:
            # Long paste detected - capture typed content and exit prompt
            typed_token = event.app.current_buffer.text
            pasted_token = pasted_text
            event.app.exit()
        else:
            # Short paste - treat like normal typing with asterisks
            event.app.current_buffer.insert_text(pasted_text)

    # Prompt user for input
    click.echo(f"🔐 Enter your {prompt_text}")

    token = pt_prompt(
        f"{prompt_text}: ",
        is_password=True,  # Shows asterisks for typing
        key_bindings=bindings,
        enable_open_in_editor=False,
    )

    # If long paste was detected, ask for confirmation inline
    if pasted_token:
        # Move cursor up one line to the prompt line
        # \033[A moves up one line
        # \r moves to start of line
        click.echo("\033[A\r", nl=False)

        # Re-print the full prompt line with asterisks and paste confirmation
        typed_asterisks = "*" * len(typed_token)
        gray_text = click.style(
            f"(📋 {len(pasted_token)} chars pasted)", fg="bright_black"
        )
        # Add space before gray text only if there are typed characters
        separator = " " if typed_asterisks else ""
        confirmation_prompt = (
            f"{prompt_text}: {typed_asterisks}{separator}{gray_text} - confirm? [Y/n]: "
        )
        click.echo(confirmation_prompt, nl=False)

        # Get confirmation (default to yes)
        response = input().strip().lower()
        if response in ("y", "yes", ""):
            # Combine typed chars (if any) with pasted token
            return typed_token + pasted_token

        raise TokenInputCancelledError("User rejected pasted token")

    return token
