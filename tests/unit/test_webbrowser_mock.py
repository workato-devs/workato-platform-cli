"""Test to verify webbrowser mocking works correctly."""

import webbrowser


def test_webbrowser_is_mocked():
    """Test that webbrowser.open is properly mocked and doesn't actually open browser."""
    # This should not actually open a browser
    result = webbrowser.open("https://example.com")

    # The mocked version should return None
    assert result is None


def test_connections_webbrowser_is_mocked():
    """Test that connections module webbrowser is also mocked."""
    from workato_platform.cli.commands.connections import (
        webbrowser as connections_webbrowser,
    )

    # Call webbrowser.open from connections module - should return None
    result = connections_webbrowser.open("https://oauth.example.com")

    # Should return None (mocked) instead of opening browser
    assert result is None
