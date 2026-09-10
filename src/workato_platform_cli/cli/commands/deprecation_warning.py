"""Manage the deprecation warning for the retired Python CLI."""

import asyncclick as click

from workato_platform_cli.cli.utils.version_checker import (
    DEPRECATION_DISABLE_FLAG,
    NEW_CLI_URL,
    DeprecationNotifier,
)


@click.group(name="deprecation-warning")
def deprecation_warning() -> None:
    """Manage the deprecation warning for this CLI.

    workato-platform-cli is deprecated and has been replaced by a new
    Go-based CLI. Use the subcommands below to control whether the
    deprecation warning is shown after each command.
    """
    pass


@deprecation_warning.command()
def disable() -> None:
    """Suppress the deprecation warning on future runs.

    Creates a flag file at ~/.cache/workato-platform-cli/deprecation_warning_disabled.
    You can also set WORKATO_DISABLE_DEPRECATION_WARNING=1 to suppress the warning
    without touching the filesystem (useful for CI/CD pipelines).
    """
    notifier = DeprecationNotifier()

    if notifier.is_disabled():
        click.echo("ℹ️  Deprecation warning is already disabled.")
        return

    notifier.disable()
    click.echo("✅ Deprecation warning disabled.")
    click.echo(
        f"   Flag file: ~/.cache/workato-platform-cli/{DEPRECATION_DISABLE_FLAG}"
    )
    click.echo()
    click.echo(
        "   You can re-enable it at any time with:  workato deprecation-warning enable"
    )


@deprecation_warning.command()
def enable() -> None:
    """Re-enable the deprecation warning after it has been disabled.

    Removes the flag file created by 'workato deprecation-warning disable'.
    Has no effect if the warning is suppressed via the
    WORKATO_DISABLE_DEPRECATION_WARNING environment variable.
    """
    notifier = DeprecationNotifier()

    if notifier.disable_flag_file.exists():
        notifier.enable()
        click.echo("✅ Deprecation warning re-enabled.")
    else:
        click.echo("ℹ️  Deprecation warning is not currently disabled by a flag file.")

    if notifier.is_disabled():
        click.echo()
        click.echo(
            "⚠️  Warning: WORKATO_DISABLE_DEPRECATION_WARNING is set in your"
            " environment."
        )
        click.echo(
            "   The warning will remain suppressed until that variable is unset."
        )


@deprecation_warning.command()
def status() -> None:
    """Show whether the deprecation warning is enabled or disabled."""
    notifier = DeprecationNotifier()

    click.echo("📋 Deprecation Warning Status")
    click.echo()

    flag_file_exists = notifier.disable_flag_file.exists()
    env_var_set = __import__("os").getenv(
        "WORKATO_DISABLE_DEPRECATION_WARNING", ""
    ).lower() in ("1", "true", "yes")

    if notifier.is_disabled():
        click.echo("   Status:  ⚠️  DISABLED — warning will not be shown")
    else:
        click.echo("   Status:  ✅ ENABLED — warning shown after each command")

    click.echo()
    click.echo("   Disable mechanisms:")
    flag_indicator = "✅ active" if flag_file_exists else "○  not set"
    click.echo(
        f"   • Flag file (~/.cache/workato-platform-cli/"
        f"{DEPRECATION_DISABLE_FLAG}):  {flag_indicator}"
    )
    env_indicator = "✅ active" if env_var_set else "○  not set"
    click.echo(
        f"   • Env var (WORKATO_DISABLE_DEPRECATION_WARNING):  {env_indicator}"
    )

    click.echo()
    click.echo(f"   New CLI:  {NEW_CLI_URL}")
