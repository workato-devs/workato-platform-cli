"""CLI tool for the Workato API"""

import asyncclick as click

from workato_platform.cli.commands import (
    api_clients,
    api_collections,
    assets,
    connections,
    data_tables,
    guide,
    init,
    profiles,
    properties,
    pull,
    push,
    workspace,
)
from workato_platform.cli.commands.connectors import command as connectors
from workato_platform.cli.commands.projects import command as projects
from workato_platform.cli.commands.recipes import command as recipes
from workato_platform.cli.containers import Container
from workato_platform.cli.utils.version_checker import check_updates_async


@click.group()
@click.option(
    "--profile",
    help="Profile to use for authentication and region settings",
    envvar="WORKATO_PROFILE",
)
@click.version_option(package_name="workato-platform-cli")
@click.pass_context
@check_updates_async
def cli(
    ctx: click.Context,
    profile: str | None = None,
) -> None:
    """CLI tool for the Workato API"""
    # Store profile in context for commands to access
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile

    container = Container()
    container.config.cli_profile.from_value(profile)
    container.wire(
        modules=[
            init,
            projects,
            profiles,
            properties,
            guide,
            push,
            pull,
            api_collections,
            api_clients,
            data_tables,
            connections,
            connectors,
            assets,
            workspace,
            recipes,
        ]
    )


# Core setup and configuration commands
cli.add_command(init.init)
cli.add_command(projects.project)
cli.add_command(profiles.profiles)
cli.add_command(properties.properties)

# Development commands
cli.add_command(guide.guide)
cli.add_command(push.push)
cli.add_command(pull.pull)

# API and resource management commands
cli.add_command(api_collections.api_collections)
cli.add_command(api_clients.api_clients)
cli.add_command(data_tables.data_tables)
cli.add_command(connections.connections)
cli.add_command(connectors.connectors)
cli.add_command(recipes.recipes)

# Information commands
cli.add_command(assets.assets)
cli.add_command(workspace.workspace)
