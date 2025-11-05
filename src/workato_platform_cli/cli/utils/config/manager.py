"""Main configuration manager with simplified workspace rules."""

import json
import os
import sys

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import asyncclick as click
import certifi
import inquirer

from workato_platform_cli import Workato
from workato_platform_cli.cli.commands.projects.project_manager import ProjectManager
from workato_platform_cli.client.workato_api.configuration import Configuration
from workato_platform_cli.client.workato_api.models.project import Project

from .models import AVAILABLE_REGIONS, ConfigData, ProfileData, ProjectInfo, RegionInfo
from .profiles import ProfileManager, _validate_url_security
from .workspace import WorkspaceManager


class ConfigManager:
    """Simplified configuration manager with clear workspace rules"""

    def __init__(self, config_dir: Path | None = None, skip_validation: bool = False):
        start_path = config_dir or Path.cwd()
        self.workspace_manager = WorkspaceManager(start_path)

        # If explicit config_dir provided, use it directly
        if config_dir:
            self.config_dir = config_dir
        else:
            # Find nearest .workatoenv file and use that directory as config directory
            nearest_config = self.workspace_manager.find_nearest_workatoenv()
            self.config_dir = nearest_config or start_path

        self.profile_manager = ProfileManager()

        # Validate credentials unless skipped
        if not skip_validation:
            self._validate_credentials_or_exit()

    @classmethod
    async def initialize(
        cls,
        config_dir: Path | None = None,
        profile_name: str | None = None,
        region: str | None = None,
        api_token: str | None = None,
        api_url: str | None = None,
        project_name: str | None = None,
        project_id: int | None = None,
        output_mode: str = "table",
        non_interactive: bool = False,
    ) -> "ConfigManager":
        """Initialize workspace with interactive or non-interactive setup"""
        if output_mode == "table":
            if non_interactive:
                click.echo("🚀 Welcome to Workato CLI (Non-interactive mode)")
            else:
                click.echo("🚀 Welcome to Workato CLI")
            click.echo()

        # Create manager without validation for setup
        manager = cls(config_dir, skip_validation=True)

        # Validate we're not in a project directory
        manager.workspace_manager.validate_not_in_project()

        if non_interactive and (profile_name or (region and api_token)):
            # Non-interactive setup
            await manager._setup_non_interactive(
                profile_name=profile_name,
                region=region,
                api_token=api_token,
                api_url=api_url,
                project_name=project_name,
                project_id=project_id,
            )
        else:
            # Run setup flow
            await manager._run_setup_flow()

        return manager

    async def _run_setup_flow(self) -> None:
        """Run the complete setup flow"""
        workspace_root = self.workspace_manager.find_workspace_root()
        self.config_dir = workspace_root

        click.echo(f"📁 Workspace root: {workspace_root}")
        click.echo()

        # Step 1: Profile setup
        profile_name = await self._setup_profile()

        # Step 2: Project setup
        await self._setup_project(profile_name, workspace_root)

        # Step 3: Create workspace files
        self._create_workspace_files(workspace_root)

        click.echo("🎉 Configuration complete!")

    async def _setup_non_interactive(
        self,
        profile_name: str | None = None,
        region: str | None = None,
        api_token: str | None = None,
        api_url: str | None = None,
        project_name: str | None = None,
        project_id: int | None = None,
    ) -> None:
        """Perform all setup actions non-interactively"""

        workspace_root = self.workspace_manager.find_workspace_root()
        self.config_dir = workspace_root

        current_profile_name = self.profile_manager.get_current_profile_name(
            profile_name
        )
        if not current_profile_name:
            raise click.ClickException("Profile name is required")

        profile = self.profile_manager.get_profile(current_profile_name)
        if profile and profile.region:
            region = profile.region
        env_token, env_url = self.profile_manager.resolve_environment_variables(
            project_profile_override=current_profile_name
        )

        # Use provided values or fall back to env vars
        if not api_token:
            api_token = env_token
        if not api_url:
            api_url = env_url

        # Detect region from api_url if region not provided
        if not region and api_url:
            region_info = self._match_host_to_region(api_url)
            region = region_info.region

        # Validate credentials are available before attempting authentication
        if not api_token:
            raise click.ClickException(
                f"Profile '{current_profile_name}' exists but credentials not found "
                "in keychain. Please run 'workato init' interactively or set "
                "WORKATO_API_TOKEN environment variable."
            )

        # Map region to URL
        if region == "custom":
            if not api_url:
                raise click.ClickException("--api-url is required when region=custom")
            region_info = RegionInfo(region="custom", name="Custom URL", url=api_url)
        elif region:
            if region not in AVAILABLE_REGIONS:
                raise click.ClickException(f"Invalid region: {region}")
            region_info = AVAILABLE_REGIONS[region]
        else:
            raise click.ClickException("Region could not be determined")

        # Test authentication and get workspace info
        api_config = Configuration(
            access_token=api_token, host=region_info.url, ssl_ca_cert=certifi.where()
        )

        async with Workato(configuration=api_config) as workato_api_client:
            user_info = await workato_api_client.users_api.get_workspace_details()

        # Create and save profile
        if not region_info.url:
            raise click.ClickException("Region URL is required")
        profile_data = ProfileData(
            region=region_info.region,
            region_url=region_info.url,
            workspace_id=user_info.id,
        )

        self.profile_manager.set_profile(current_profile_name, profile_data, api_token)
        self.profile_manager.set_current_profile(current_profile_name)

        # Get API client for project operations
        api_config = Configuration(
            access_token=api_token, host=region_info.url, ssl_ca_cert=certifi.where()
        )

        async with Workato(configuration=api_config) as workato_api_client:
            project_manager = ProjectManager(workato_api_client=workato_api_client)

            selected_project = None

            if project_name:
                selected_project = await project_manager.create_project(project_name)
            elif project_id:
                # Use existing project
                projects = await project_manager.get_all_projects()
                selected_project = next(
                    (p for p in projects if p.id == project_id),
                    None,
                )
                if not selected_project:
                    raise click.ClickException(
                        f"Project with ID {project_id} not found"
                    )

            if not selected_project:
                raise click.ClickException("No project selected")

            # Check if this specific project already exists locally in the workspace
            local_projects = self._find_all_projects(workspace_root)
            existing_local_path = None

            for project_path_candidate, _ in local_projects:
                try:
                    project_config_manager = ConfigManager(
                        project_path_candidate, skip_validation=True
                    )
                    config_data = project_config_manager.load_config()
                    if config_data.project_id == selected_project.id:
                        existing_local_path = project_path_candidate
                        break
                except (json.JSONDecodeError, OSError):
                    continue

            # In non-interactive mode, fail if project already exists
            if existing_local_path:
                relative_path = existing_local_path.relative_to(workspace_root)
                raise click.ClickException(
                    f"Project '{selected_project.name}' (ID: {selected_project.id}) "
                    f"already exists locally at: {relative_path}. "
                    f"Cannot reinitialize in non-interactive mode."
                )

            # Project doesn't exist locally - create new directory
            current_dir = Path.cwd().resolve()
            project_path = current_dir / selected_project.name

            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)

            # Save workspace config (with project_path)
            relative_project_path = str(project_path.relative_to(workspace_root))
            workspace_config = ConfigData(
                project_id=selected_project.id,
                project_name=selected_project.name,
                project_path=relative_project_path,
                folder_id=selected_project.folder_id,
                profile=profile_name,
            )

            self.save_config(workspace_config)

            # Save project config (without project_path)
            project_config_manager = ConfigManager(project_path, skip_validation=True)
            project_config = ConfigData(
                project_id=selected_project.id,
                project_name=selected_project.name,
                project_path=None,  # No project_path in project directory
                folder_id=selected_project.folder_id,
                profile=profile_name,
            )

            project_config_manager.save_config(project_config)

        # Step 3: Create workspace files
        self._create_workspace_files(workspace_root)

    async def _setup_profile(self) -> str:
        """Setup or select profile"""
        click.echo("📋 Step 1: Configure profile")

        # Check for environment variables FIRST
        env_token = os.environ.get("WORKATO_API_TOKEN")
        env_host = os.environ.get("WORKATO_HOST")

        profile_name: str | None = None

        if env_token or env_host:
            # Show what was detected and what's missing
            if env_token:
                click.echo("✓ Found WORKATO_API_TOKEN in environment")
            else:
                click.echo("✗ WORKATO_API_TOKEN not found - will prompt for token")

            if env_host:
                region_info = self._match_host_to_region(env_host)
                click.echo(f"✓ Found WORKATO_HOST in environment ({region_info.name})")
            else:
                click.echo("✗ WORKATO_HOST not found - will prompt for region")

            # Ask user if they want to use env vars
            if env_token and env_host:
                prompt_msg = "Use environment variables for authentication?"
            elif env_token:
                prompt_msg = "Use WORKATO_API_TOKEN from environment?"
            else:  # only env_host
                prompt_msg = "Use WORKATO_HOST from environment?"

            use_env_vars = click.confirm(
                prompt_msg,
                default=True,
            )

            if use_env_vars:
                # Just select/create profile NAME (credentials from env vars)
                click.echo()
                profile_name = await self._select_profile_name_for_env_vars()

                # Create profile with env var credentials
                await self._create_profile_with_env_vars(
                    profile_name, env_token, env_host
                )

                # Set as current profile
                self.profile_manager.set_current_profile(profile_name)
                click.echo(f"✅ Profile: {profile_name}")

                return profile_name

        # Normal flow - no env vars or user declined
        existing_profiles = self.profile_manager.list_profiles()

        if existing_profiles:
            choices = list(existing_profiles.keys()) + ["Create new profile"]
            questions = [
                inquirer.List(
                    "profile_choice",
                    message="Select a profile",
                    choices=choices,
                )
            ]

            answers: dict[str, str] = inquirer.prompt(questions)
            if not answers:
                click.echo("❌ No profile selected")
                sys.exit(1)

            if answers["profile_choice"] == "Create new profile":
                profile_name = (
                    await click.prompt("Enter new profile name", type=str)
                ).strip()
                if not profile_name:
                    click.echo("❌ Profile name cannot be empty")
                    sys.exit(1)
                await self._create_new_profile(profile_name)
            else:
                profile_name = answers["profile_choice"]

                # Check if credentials exist in keychain for existing profile
                existing_profile = self.profile_manager.get_profile(profile_name)
                token = self.profile_manager._get_token_from_keyring(profile_name)

                if existing_profile and not token:
                    # Credentials missing from keychain - prompt for re-entry
                    click.echo("⚠️  Credentials not found for this profile")

                    # Get region info from existing profile
                    region_info = RegionInfo(
                        region=existing_profile.region,
                        url=existing_profile.region_url,
                        name=existing_profile.region,
                    )

                    # Prompt and validate credentials
                    (
                        profile_data,
                        validated_token,
                    ) = await self._prompt_and_validate_credentials(
                        profile_name, region_info
                    )

                    # Update profile with validated credentials
                    self.profile_manager.set_profile(
                        profile_name, profile_data, validated_token
                    )
        else:
            profile_name = (
                await click.prompt("Enter profile name", default="default", type=str)
            ).strip()
            if not profile_name:
                click.echo("❌ Profile name cannot be empty")
                sys.exit(1)
            await self._create_new_profile(profile_name)

        # Set as current profile
        self.profile_manager.set_current_profile(profile_name)
        click.echo(f"✅ Profile: {profile_name}")

        return profile_name

    def _match_host_to_region(self, host: str) -> RegionInfo:
        """Match host URL to known region or return custom"""
        for region_info in AVAILABLE_REGIONS.values():
            if region_info.url and region_info.url in host:
                return region_info
        # Return custom region with provided host
        return RegionInfo(region="custom", name="Custom URL", url=host)

    async def _select_profile_name_for_env_vars(self) -> str:
        """Let user choose profile name when using env var credentials"""
        existing_profiles = self.profile_manager.list_profiles()

        if existing_profiles:
            choices = list(existing_profiles.keys()) + ["Create new profile"]
            questions = [
                inquirer.List(
                    "profile_choice",
                    message="Select a profile name to use",
                    choices=choices,
                )
            ]

            answers: dict[str, str] = inquirer.prompt(questions)
            if not answers:
                click.echo("❌ No profile selected")
                sys.exit(1)

            selected_choice: str = answers["profile_choice"]
            if selected_choice == "Create new profile":
                new_profile_input: str = await click.prompt(
                    "Enter new profile name", type=str
                )
                profile_name = new_profile_input.strip()
                if not profile_name:
                    click.echo("❌ Profile name cannot be empty")
                    sys.exit(1)
                return profile_name
            else:
                # Warn user about overwriting existing profile
                click.echo(
                    f"\n⚠️  This will overwrite the existing profile "
                    f"'{selected_choice}' with the environment variables."
                )
                if not click.confirm("Continue?", default=True):
                    click.echo("❌ Cancelled")
                    sys.exit(1)
                return selected_choice
        else:
            default_profile_input: str = await click.prompt(
                "Enter profile name", default="default", type=str
            )
            profile_name = default_profile_input.strip()
            if not profile_name:
                click.echo("❌ Profile name cannot be empty")
                sys.exit(1)
            return profile_name

    async def _create_profile_with_env_vars(
        self,
        profile_name: str,
        env_token: str | None,
        env_host: str | None,
    ) -> None:
        """Create profile using environment variable credentials"""
        # Detect region from env_host
        selected_region: RegionInfo
        if env_host:
            selected_region = self._match_host_to_region(env_host)
        else:
            # No env_host, need to ask for region
            click.echo()
            click.echo("📍 Select your Workato region")
            region_result = await self.profile_manager.select_region_interactive()

            if not region_result:
                click.echo("❌ Setup cancelled")
                sys.exit(1)

            selected_region = region_result

        # Get token from env or prompt
        if env_token:
            token = env_token
        else:
            click.echo()
            token = await click.prompt("Enter your Workato API token", hide_input=True)
            if not token.strip():
                click.echo("❌ No token provided")
                sys.exit(1)

        # Test authentication and get workspace info
        click.echo("🔄 Testing authentication with environment variables...")
        api_config = Configuration(
            access_token=token, host=selected_region.url, ssl_ca_cert=certifi.where()
        )

        async with Workato(configuration=api_config) as workato_api_client:
            user_info = await workato_api_client.users_api.get_workspace_details()

        # Create and save profile
        if not selected_region.url:
            raise click.ClickException("Region URL is required")
        profile_data = ProfileData(
            region=selected_region.region,
            region_url=selected_region.url,
            workspace_id=user_info.id,
        )

        self.profile_manager.set_profile(profile_name, profile_data, token)
        click.echo(f"✅ Authenticated as: {user_info.name}")
        click.echo("✓ Using environment variables for authentication")

    async def _prompt_and_validate_credentials(
        self, profile_name: str, region_info: RegionInfo
    ) -> tuple[ProfileData, str]:
        """Prompt for API credentials and validate them with an API call.
        Args:
            profile_name: Name of the profile being configured
            region_info: Region information containing the API URL
        Returns:
            tuple[ProfileData, str]: Validated profile data and API token
        Raises:
            click.ClickException: If token is empty or validation fails
        """
        # Prompt for API token
        click.echo("🔐 Enter your API token")
        token = await click.prompt("Enter your Workato API token", hide_input=True)

        # Validate token is not empty
        if not token.strip():
            raise click.ClickException("API token cannot be empty")

        # Create API configuration with the token and region URL
        api_config = Configuration(
            access_token=token, host=region_info.url, ssl_ca_cert=certifi.where()
        )

        # Make API call to test authentication and get workspace info
        try:
            async with Workato(configuration=api_config) as workato_api_client:
                user_info = await workato_api_client.users_api.get_workspace_details()
        except Exception as e:
            raise click.ClickException(
                f"Authentication failed: {e}\n"
                "Please verify your API token is correct and try again."
            ) from e

        # Create and return ProfileData object with workspace info
        if not region_info.url:
            raise click.ClickException("Region URL is required")

        profile_data = ProfileData(
            region=region_info.region,
            region_url=region_info.url,
            workspace_id=user_info.id,
        )

        click.echo(f"✅ Authenticated as: {user_info.name}")

        return profile_data, token

    async def _create_new_profile(self, profile_name: str) -> None:
        """Create a new profile interactively"""
        # Select region
        click.echo("📍 Select your Workato region")
        region_result = await self.profile_manager.select_region_interactive()

        if not region_result:
            click.echo("❌ Setup cancelled")
            sys.exit(1)

        selected_region = region_result

        # Prompt for credentials and validate with API
        profile_data, token = await self._prompt_and_validate_credentials(
            profile_name, selected_region
        )

        # Save profile and token
        self.profile_manager.set_profile(profile_name, profile_data, token)

    async def _setup_project(self, profile_name: str, workspace_root: Path) -> None:
        """Setup project interactively"""
        click.echo("📁 Step 2: Setup project")

        # Get API client for project operations
        api_token, api_host = self.profile_manager.resolve_environment_variables(
            profile_name
        )
        api_config = Configuration(
            access_token=api_token, host=api_host, ssl_ca_cert=certifi.where()
        )

        async with Workato(configuration=api_config) as workato_api_client:
            project_manager = ProjectManager(workato_api_client=workato_api_client)

            # Get available projects
            projects = await project_manager.get_all_projects()
            choices = ["Create new project"]

            if projects:
                project_choices = [(f"{p.name} (ID: {p.id})", p) for p in projects]
                choices.extend([choice[0] for choice in project_choices])

            questions = [
                inquirer.List(
                    "project",
                    message="Select a project",
                    choices=choices,
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers:
                click.echo("❌ No project selected")
                sys.exit(1)

            selected_project = None

            if answers["project"] == "Create new project":
                project_name = await click.prompt("Enter project name", type=str)
                if not project_name or not project_name.strip():
                    click.echo("❌ Project name cannot be empty")
                    sys.exit(1)

                click.echo(f"🔨 Creating project: {project_name}")
                selected_project = await project_manager.create_project(project_name)
                click.echo(f"✅ Created project: {selected_project.name}")
            else:
                # Find selected existing project
                for choice_text, project in [(choices[0], None)] + project_choices:
                    if choice_text == answers["project"] and project:
                        selected_project = project
                        break

            if not selected_project:
                click.echo("❌ No project selected")
                sys.exit(1)

            # Check if this specific project already exists locally in the workspace
            local_projects = self._find_all_projects(workspace_root)
            existing_local_path = None

            for project_path_candidate, _ in local_projects:
                try:
                    project_config_manager = ConfigManager(
                        project_path_candidate, skip_validation=True
                    )
                    config_data = project_config_manager.load_config()
                    if config_data.project_id == selected_project.id:
                        existing_local_path = project_path_candidate
                        break
                except (json.JSONDecodeError, OSError):
                    continue

            # If project exists locally, prompt for reinitialization
            if existing_local_path:
                relative_path = existing_local_path.relative_to(workspace_root)
                click.echo(
                    f"Project '{selected_project.name}' (ID: {selected_project.id}) "
                    f"already exists locally at: {relative_path}"
                )
                if not click.confirm(
                    "Reinitialize this project? "
                    "This may overwrite or delete local files.",
                    default=False,
                ):
                    click.echo("❌ Initialization cancelled")
                    sys.exit(1)
                # Use existing path instead of creating new one
                project_path = existing_local_path
            else:
                # Project doesn't exist locally - create new directory
                current_dir = Path.cwd().resolve()
                project_path = current_dir / selected_project.name

            # Validate project path
            try:
                self.workspace_manager.validate_project_path(
                    project_path, workspace_root
                )
            except ValueError as e:
                click.echo(f"❌ {e}")
                sys.exit(1)

            # Check if project directory already exists and is non-empty
            if not project_path.exists():
                pass  # Directory doesn't exist, we can proceed
            else:
                try:
                    existing_files = list(project_path.iterdir())
                    if not existing_files:
                        pass  # Directory is empty, we can proceed
                    else:
                        # Directory has files - check if it's the same Workato project
                        existing_project_id = self._get_existing_project_id(
                            project_path
                        )

                        if existing_project_id == selected_project.id:
                            # Same project ID - allow reconfiguration
                            click.echo(
                                f"🔄 Reconfiguring existing project: "
                                f"{selected_project.name}"
                            )
                        elif existing_project_id:
                            # Different project ID - block it
                            self._handle_different_project_error(
                                project_path, existing_project_id, selected_project
                            )
                        else:
                            # Not a Workato project - block it
                            self._handle_non_empty_directory_error(
                                project_path, workspace_root, existing_files
                            )
                except OSError:
                    pass  # If we can't read the directory, let mkdir handle it

            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            click.echo(
                f"✅ Project directory: {project_path.relative_to(workspace_root)}"
            )

            # Save workspace config (with project_path)
            relative_project_path = str(project_path.relative_to(workspace_root))
            workspace_config = ConfigData(
                project_id=selected_project.id,
                project_name=selected_project.name,
                project_path=relative_project_path,
                folder_id=selected_project.folder_id,
                profile=profile_name,
            )

            self.save_config(workspace_config)

            # Save project config (without project_path)
            project_config_manager = ConfigManager(project_path, skip_validation=True)
            project_config = ConfigData(
                project_id=selected_project.id,
                project_name=selected_project.name,
                project_path=None,  # No project_path in project directory
                folder_id=selected_project.folder_id,
                profile=profile_name,
            )

            project_config_manager.save_config(project_config)

            click.echo(f"✅ Project: {selected_project.name}")

    def _create_workspace_files(self, workspace_root: Path) -> None:
        """Create workspace .gitignore and .workato-ignore files"""
        # Create .gitignore entry for .workatoenv
        gitignore_file = workspace_root / ".gitignore"
        workatoenv_entry = ".workatoenv"

        existing_lines = []
        if gitignore_file.exists():
            with open(gitignore_file) as f:
                existing_lines = [line.rstrip("\n") for line in f.readlines()]

        if workatoenv_entry not in existing_lines:
            with open(gitignore_file, "a") as f:
                if existing_lines and existing_lines[-1] != "":
                    f.write("\n")
                f.write(f"{workatoenv_entry}\n")

        # Create .workato-ignore file
        workato_ignore_file = workspace_root / ".workato-ignore"
        if not workato_ignore_file.exists():
            workato_ignore_content = """# Workato CLI ignore patterns
# Files matching these patterns will be preserved during 'workato pull'
# and excluded from 'workato push' operations

# Configuration files
.workatoenv

# Git files
.git
.gitignore
.gitattributes
.gitmodules

# Python files and virtual environments
*.py
*.pyc
*.pyo
*.pyd
__pycache__/
*.egg-info/
.venv/
venv/
.env

# Node.js files
node_modules/
package.json
package-lock.json
yarn.lock
.npmrc

# Development tools
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
.tox/

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Build artifacts
dist/
build/
*.egg

# Documentation and project files
*.md
LICENSE
.editorconfig
pyproject.toml
setup.py
setup.cfg
Makefile
Dockerfile
docker-compose.yml

# OS files
.DS_Store
Thumbs.db

# Add your own patterns below
"""
            with open(workato_ignore_file, "w") as f:
                f.write(workato_ignore_content)

    # Configuration file management

    def load_config(self) -> ConfigData:
        """Load configuration from .workatoenv file"""
        config_file = self.config_dir / ".workatoenv"

        if not config_file.exists():
            return ConfigData.model_construct()

        try:
            with open(config_file) as f:
                data = json.load(f)
                return ConfigData.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            return ConfigData.model_construct()

    def save_config(self, config_data: ConfigData) -> None:
        """Save configuration to .workatoenv file"""
        config_file = self.config_dir / ".workatoenv"

        with open(config_file, "w") as f:
            json.dump(config_data.model_dump(exclude_none=True), f, indent=2)

    def save_project_info(self, project_info: ProjectInfo) -> None:
        """Save project information to configuration"""
        config_data = self.load_config()
        config_data.project_id = project_info.id
        config_data.project_name = project_info.name
        config_data.folder_id = project_info.folder_id
        self.save_config(config_data)

    # Project and workspace detection methods

    def get_workspace_root(self) -> Path:
        """Get workspace root directory"""
        return self.workspace_manager.find_workspace_root()

    def get_project_directory(self) -> Path | None:
        """Get project directory from closest .workatoenv config"""
        # Load config from closest .workatoenv file (already found in __init__)
        config_data = self.load_config()

        if not config_data.project_id:
            return None

        if not config_data.project_path:
            # No project_path means this .workatoenv IS in the project directory
            # Update workspace root to select this project as current
            self._update_workspace_selection()
            return self.config_dir

        # Has project_path, so this is a workspace config - resolve relative path
        workspace_root = self.config_dir
        project_dir = workspace_root / config_data.project_path

        if project_dir.exists():
            return project_dir.resolve()
        else:
            # Current selection is invalid - let user choose from available projects
            return self._handle_invalid_project_selection(workspace_root, config_data)

    def _update_workspace_selection(self) -> None:
        """Update workspace root config to select current project"""
        workspace_root = self.workspace_manager.find_workspace_root()
        if not workspace_root or workspace_root == self.config_dir:
            return  # Already at workspace root or no workspace found

        # Load current project config
        project_config = self.load_config()
        if not project_config.project_id:
            return

        # Calculate relative path from workspace root to current project
        try:
            relative_path = self.config_dir.relative_to(workspace_root)
        except ValueError:
            return  # Current dir not within workspace

        # Update workspace config
        workspace_manager = ConfigManager(workspace_root, skip_validation=True)
        workspace_config = workspace_manager.load_config()
        workspace_config.project_id = project_config.project_id
        workspace_config.project_name = project_config.project_name
        workspace_config.project_path = str(relative_path)
        workspace_config.folder_id = project_config.folder_id
        workspace_config.profile = project_config.profile
        workspace_manager.save_config(workspace_config)

        click.echo(f"✅ Selected '{project_config.project_name}' as current project")

    def _handle_invalid_project_selection(
        self, workspace_root: Path, current_config: ConfigData
    ) -> Path | None:
        """Handle case where current project selection is invalid"""
        click.echo(
            f"⚠️  Configured project directory does not exist: "
            f"{current_config.project_path}"
        )
        click.echo(f"   Project: {current_config.project_name}")
        click.echo()

        # Find all available projects in workspace hierarchy
        available_projects = self._find_all_projects(workspace_root)

        if not available_projects:
            click.echo("❌ No projects found in workspace")
            click.echo("💡 Run 'workato init' to create a new project")
            return None

        # Prepare choices for inquirer
        choices = []
        for project_path, project_name in available_projects:
            rel_path = project_path.relative_to(workspace_root)
            choice_text = f"{project_name} ({rel_path})"
            choices.append(choice_text)

        # Let user select
        try:
            questions = [
                inquirer.List(
                    "project",
                    message="Select a project to use",
                    choices=choices,
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers:
                return None

            # Find selected project
            selected_index = choices.index(answers["project"])
            selected_path, selected_name = available_projects[selected_index]

            # Load selected project config to get full details
            selected_manager = ConfigManager(selected_path, skip_validation=True)
            selected_config = selected_manager.load_config()

            # Update workspace config
            workspace_manager = ConfigManager(workspace_root, skip_validation=True)
            workspace_config = workspace_manager.load_config()
            workspace_config.project_id = selected_config.project_id
            workspace_config.project_name = selected_config.project_name
            workspace_config.project_path = str(
                selected_path.relative_to(workspace_root)
            )
            workspace_config.folder_id = selected_config.folder_id
            workspace_config.profile = selected_config.profile
            workspace_manager.save_config(workspace_config)

            click.echo(f"✅ Selected '{selected_name}' as current project")
            return selected_path

        except (ImportError, KeyboardInterrupt):
            click.echo("❌ Project selection cancelled")
            return None

    def _find_all_projects(self, workspace_root: Path) -> list[tuple[Path, str]]:
        """Find all project directories in workspace hierarchy"""
        projects = []

        # Recursively search for .workatoenv files without project_path
        for workatoenv_file in workspace_root.rglob(".workatoenv"):
            try:
                with open(workatoenv_file) as f:
                    data = json.load(f)
                    # Project config has project_id but no project_path
                    if (
                        "project_id" in data
                        and data.get("project_id")
                        and not data.get("project_path")
                    ):
                        project_dir = workatoenv_file.parent
                        project_name = data.get("project_name", project_dir.name)
                        projects.append((project_dir, project_name))
            except (json.JSONDecodeError, OSError):
                continue

        return sorted(projects, key=lambda x: x[1])  # Sort by project name

    def get_current_project_name(self) -> str | None:
        """Get current project name"""
        config_data = self.load_config()
        return config_data.project_name

    def get_project_root(self) -> Path | None:
        """Get project root (directory containing .workatoenv)"""
        # For compatibility - this is the same as config_dir when in project
        if self.workspace_manager.is_in_project_directory():
            return self.config_dir

        # If in workspace, return project directory
        return self.get_project_directory()

    def is_in_project_workspace(self) -> bool:
        """Check if in a project workspace"""
        return self.get_workspace_root() is not None

    def _get_existing_project_id(self, project_path: Path) -> int | None:
        """Get project ID from existing .workatoenv file, if valid."""
        workatoenv_path = project_path / ".workatoenv"
        if not workatoenv_path.exists():
            return None

        try:
            with open(workatoenv_path) as f:
                data: dict[str, Any] = json.load(f)
                return data.get("project_id")
        except (json.JSONDecodeError, OSError):
            return None

    def _handle_different_project_error(
        self,
        project_path: Path,
        existing_project_id: int,
        selected_project: Project,
    ) -> None:
        """Handle error when directory contains different Workato project."""
        workatoenv_path = project_path / ".workatoenv"
        try:
            with open(workatoenv_path) as f:
                existing_data = json.load(f)
                existing_name = existing_data.get("project_name", "Unknown")
        except (json.JSONDecodeError, OSError):
            existing_name = "Unknown"

        click.echo(
            f"❌ Directory contains different Workato project: "
            f"{existing_name} (ID: {existing_project_id})"
        )
        click.echo(
            f"   Cannot initialize {selected_project.name} "
            f"(ID: {selected_project.id}) here"
        )
        click.echo("💡 Choose a different directory or project name")
        sys.exit(1)

    def _handle_non_empty_directory_error(
        self, project_path: Path, workspace_root: Path, existing_files: list
    ) -> None:
        """Handle error when directory is non-empty but not a Workato project."""
        click.echo(
            f"❌ Project directory is not empty: "
            f"{project_path.relative_to(workspace_root)}"
        )
        click.echo(f"   Found {len(existing_files)} existing files")
        click.echo("💡 Choose a different project name or clean the directory first")
        sys.exit(1)

    # Credential management

    def _validate_credentials_or_exit(self) -> None:
        """Validate credentials and exit if missing"""
        is_valid, missing_items = self.validate_environment_config()
        if not is_valid:
            click.echo("❌ Missing required credentials:")
            for item in missing_items:
                click.echo(f"   • {item}")
            click.echo()
            click.echo("💡 Run 'workato init' to set up authentication")
            sys.exit(1)

    def validate_environment_config(self) -> tuple[bool, list[str]]:
        """Validate environment configuration"""
        config_data = self.load_config()
        return self.profile_manager.validate_credentials(config_data.profile)

    @property
    def api_token(self) -> str | None:
        """Get API token"""
        config_data = self.load_config()
        api_token, _ = self.profile_manager.resolve_environment_variables(
            config_data.profile
        )
        return api_token

    @api_token.setter
    def api_token(self, value: str) -> None:
        """Save API token to current profile"""
        config_data = self.load_config()
        current_profile_name = self.profile_manager.get_current_profile_name(
            config_data.profile
        )

        if not current_profile_name:
            current_profile_name = "default"

        # Check if profile exists
        profiles = self.profile_manager.load_profiles()
        if current_profile_name not in profiles.profiles:
            raise ValueError(
                f"Profile '{current_profile_name}' does not exist. "
                "Please run 'workato init' to create a profile first."
            )

        # Store token in keyring
        success = self.profile_manager._store_token_in_keyring(
            current_profile_name, value
        )
        if not success:
            if self.profile_manager._is_keyring_enabled():
                raise ValueError(
                    "Failed to store token in keyring. "
                    "Please check your system keyring setup."
                )
            else:
                raise ValueError(
                    "Keyring is disabled. "
                    "Please set WORKATO_API_TOKEN environment variable instead."
                )

        click.echo(f"✅ API token saved to profile '{current_profile_name}'")

    @property
    def api_host(self) -> str | None:
        """Get API host"""
        config_data = self.load_config()
        _, api_host = self.profile_manager.resolve_environment_variables(
            config_data.profile
        )
        return api_host

    # Region management methods

    def validate_region(self, region_code: str) -> bool:
        """Validate if region code is valid"""
        return region_code.lower() in AVAILABLE_REGIONS

    def set_region(
        self, region_code: str, custom_url: str | None = None
    ) -> tuple[bool, str]:
        """Set region by updating the current profile"""

        if region_code.lower() not in AVAILABLE_REGIONS:
            return False, f"Invalid region: {region_code}"

        region_info = AVAILABLE_REGIONS[region_code.lower()]

        # Get current profile
        config_data = self.load_config()
        current_profile_name = self.profile_manager.get_current_profile_name(
            config_data.profile
        )
        if not current_profile_name:
            current_profile_name = "default"

        # Load profiles
        profiles = self.profile_manager.load_profiles()
        if current_profile_name not in profiles.profiles:
            return False, f"Profile '{current_profile_name}' does not exist"

        # Handle custom region
        if region_code.lower() == "custom":
            if not custom_url:
                return False, "Custom region requires a URL to be provided"

            # Validate URL security
            is_valid, error_msg = _validate_url_security(custom_url)
            if not is_valid:
                return False, error_msg

            # Parse URL and keep only scheme + netloc
            parsed = urlparse(custom_url)
            region_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            region_url = region_info.url or ""

        # Update profile
        profiles.profiles[current_profile_name].region = region_code.lower()
        profiles.profiles[current_profile_name].region_url = region_url

        # Save updated profiles
        self.profile_manager.save_profiles(profiles)

        return True, f"{region_info.name} ({region_url})"
