"""Version checking utilities for the Workato CLI."""

import contextlib
import json
import os
import ssl
import threading
import time
import urllib.request

from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import asyncclick as click

from workato_platform.cli.utils.config import ConfigManager


try:
    from workato_platform._version import __version__
except ImportError:
    # Fallback for development when not built with hatch
    __version__ = "0.0.0+unknown"


try:
    from packaging import version

    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False


PACKAGE_NAME = "workato-platform-cli"
PYPI_API_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
CHECK_INTERVAL = 86400  # 24 hours in seconds
REQUEST_TIMEOUT = 2  # seconds


class VersionChecker:
    """Handles version checking and update notifications."""

    def __init__(self, config_manager: ConfigManager) -> None:
        """Initialize version checker with config manager."""
        self.config_manager = config_manager
        self.cache_dir = Path.home() / ".cache" / "workato-platform-cli"
        self.cache_file = self.cache_dir / "last_update_check"
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

    def is_update_check_disabled(self) -> bool:
        """Check if update checking is disabled."""
        # Environment variable override
        return os.getenv("WORKATO_DISABLE_UPDATE_CHECK", "").lower() in (
            "1",
            "true",
            "yes",
        )

    def should_check_for_updates(self) -> bool:
        """Check if it's time to check for updates."""
        if self.is_update_check_disabled():
            return False

        if not HAS_DEPENDENCIES:
            return False

        if not self.cache_file.exists():
            return True

        try:
            last_check = self.cache_file.stat().st_mtime
            return time.time() - last_check > CHECK_INTERVAL
        except OSError:
            return True

    def get_latest_version(self) -> str | None:
        """Get the latest version from PyPI."""
        if not HAS_DEPENDENCIES:
            return None

        try:
            # Ensure only HTTPS scheme is allowed for security
            if not PYPI_API_URL.startswith("https://"):
                return None

            parsed_url = urlparse(PYPI_API_URL)
            if parsed_url.scheme != "https":
                return None

            # Create SSL context with TLS 1.2 minimum
            ssl_context = ssl.create_default_context()
            if hasattr(ssl, "TLSVersion"):  # Python 3.7+
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            else:  # Fallback for older Python versions
                ssl_context.options |= (
                    ssl.OP_NO_SSLv2
                    | ssl.OP_NO_SSLv3
                    | ssl.OP_NO_TLSv1
                    | ssl.OP_NO_TLSv1_1
                )

            request = urllib.request.Request(PYPI_API_URL)  # noqa: S310
            # Secure: URL scheme validated above, HTTPS only, proper SSL context
            with urllib.request.urlopen(  # noqa: S310
                request, timeout=REQUEST_TIMEOUT, context=ssl_context
            ) as response:
                status_code = response.getcode()
                if status_code != 200:
                    return None
                data = json.loads(response.read().decode())
                version_str: str = data["info"]["version"]
                return version_str
        except (OSError, KeyError, ValueError, json.JSONDecodeError):
            return None

    def update_cache_timestamp(self) -> None:
        """Update the last check timestamp."""
        with contextlib.suppress(OSError):
            self.cache_file.touch()

    def check_for_updates(self, current_version: str) -> str | None:
        """Check if a newer version is available."""
        if not HAS_DEPENDENCIES:
            return None

        latest = self.get_latest_version()
        if not latest:
            return None

        try:
            if version.parse(latest) > version.parse(current_version):
                return latest
        except Exception:
            click.echo("Failed to check for updates")

        return None

    def show_update_notification(self, latest_version: str) -> None:
        """Show update notification to user."""
        click.echo()
        click.echo(f"💡 A new version of {PACKAGE_NAME} is available: {latest_version}")
        click.echo(f"   Run 'pip install --upgrade {PACKAGE_NAME}' to update")
        click.echo(
            "   To disable these notifications: export WORKATO_DISABLE_UPDATE_CHECK=1"
        )

    def background_update_check(self, current_version: str) -> None:
        """Perform update check in background (non-blocking)."""
        if not self.should_check_for_updates():
            return

        try:
            latest_version = self.check_for_updates(current_version)
            if latest_version:
                self.show_update_notification(latest_version)

            # Always update timestamp after a check attempt
            self.update_cache_timestamp()

        except Exception:
            # Never let update checking break the CLI
            click.echo("Failed to check for updates")


def check_updates_async(func: Callable) -> Callable:
    """Decorator to add background update checking to CLI commands."""

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Import here to avoid circular imports
        from workato_platform.cli.containers import Container

        try:
            # Run main command first
            result = await func(*args, **kwargs)

            # Check updates in background (non-blocking)
            config_manager = Container.config_manager()
            version_checker = VersionChecker(config_manager)

            if version_checker.should_check_for_updates():
                thread = threading.Thread(
                    target=version_checker.background_update_check,
                    args=(__version__,),
                    daemon=True,
                )
                thread.start()
                thread.join(timeout=3)  # Don't wait too long

            return result

        except Exception:
            # If anything goes wrong with update checking, just run the main command
            return await func(*args, **kwargs)

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Import here to avoid circular imports
        from workato_platform.cli.containers import Container

        try:
            # Run main command first
            result = func(*args, **kwargs)

            # Check updates in background (non-blocking)
            config_manager = Container.config_manager()
            version_checker = VersionChecker(config_manager)

            if version_checker.should_check_for_updates():
                thread = threading.Thread(
                    target=version_checker.background_update_check,
                    args=(__version__,),
                    daemon=True,
                )
                thread.start()
                thread.join(timeout=3)  # Don't wait too long

            return result

        except Exception:
            # If anything goes wrong with update checking, just run the main command
            return func(*args, **kwargs)

    # Return appropriate wrapper based on whether function is async
    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
