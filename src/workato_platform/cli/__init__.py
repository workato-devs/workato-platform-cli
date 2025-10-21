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
    workspace,
)
from workato_platform.cli.commands.connectors import command as connectors
from workato_platform.cli.commands.projects import command as projects
from workato_platform.cli.commands.push import command as push
from workato_platform.cli.commands.recipes import command as recipes
from workato_platform.cli.containers import Container
from workato_platform.cli.utils.version_checker import check_updates_async


class AliasedGroup(click.Group):
    """A Click Group that supports command aliases without showing them in help"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases = {}

    def add_command_with_alias(self, cmd, name=None, alias=None):
        """Add a command with an optional hidden alias"""
        # Add the main command
        self.add_command(cmd, name=name)

        # Store alias mapping
        if alias:
            main_name = name or cmd.name
            if alias == main_name:
                raise ValueError(
                    f"Alias '{alias}' cannot be the same as "
                    f"the main command name '{main_name}'."
                )
            self.aliases[alias] = main_name

    def get_command(self, ctx, cmd_name):
        # Check if it's an alias first
        if cmd_name in self.aliases:
            cmd_name = self.aliases[cmd_name]
        return super().get_command(ctx, cmd_name)


@click.group(cls=AliasedGroup)
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
cli.add_command_with_alias(projects.projects, alias="project")
cli.add_command(profiles.profiles)
cli.add_command_with_alias(properties.properties, alias="property")

# Development commands
cli.add_command(guide.guide)
cli.add_command(push.push)
cli.add_command(pull.pull)

# API and resource management commands
cli.add_command_with_alias(api_collections.api_collections, alias="api-collection")
cli.add_command_with_alias(api_clients.api_clients, alias="api-client")
cli.add_command_with_alias(data_tables.data_tables, alias="data-table")
cli.add_command_with_alias(connections.connections, alias="connection")
cli.add_command_with_alias(connectors.connectors, alias="connector")
cli.add_command_with_alias(recipes.recipes, alias="recipe")

# Information commands
cli.add_command_with_alias(assets.assets, alias="asset")
cli.add_command(workspace.workspace)
