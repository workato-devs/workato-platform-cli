"""Configuration management for the CLI using class-based approach"""

import contextlib
import json
import os
import sys
import threading

from pathlib import Path
from urllib.parse import urlparse

import asyncclick as click
import inquirer
import keyring

from keyring.backend import KeyringBackend
from keyring.compat import properties
from keyring.errors import KeyringError, NoKeyringError
from pydantic import BaseModel, Field, field_validator

from workato_platform import Workato
from workato_platform.cli.commands.projects.project_manager import ProjectManager
from workato_platform.client.workato_api.configuration import Configuration


def _validate_url_security(url: str) -> tuple[bool, str]:
    """Validate URL security - only allow HTTP for localhost, require HTTPS for others.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"

    parsed = urlparse(url)

    # Allow HTTP only for localhost/127.0.0.1
    if parsed.scheme == "http":
        hostname = parsed.hostname
        if hostname not in ("localhost", "127.0.0.1", "::1"):
            return (
                False,
                "HTTP URLs are only allowed for localhost. Use HTTPS for other hosts.",
            )

    return True, ""


class RegionInfo(BaseModel):
    """Data model for region information"""

    region: str = Field(..., description="Region code")
    name: str = Field(..., description="Human-readable region name")
    url: str | None = Field(None, description="Base URL for the region")


# Available Workato regions
AVAILABLE_REGIONS = {
    "us": RegionInfo(region="us", name="US Data Center", url="https://www.workato.com"),
    "eu": RegionInfo(
        region="eu", name="EU Data Center", url="https://app.eu.workato.com"
    ),
    "jp": RegionInfo(
        region="jp", name="JP Data Center", url="https://app.jp.workato.com"
    ),
    "sg": RegionInfo(
        region="sg", name="SG Data Center", url="https://app.sg.workato.com"
    ),
    "au": RegionInfo(
        region="au", name="AU Data Center", url="https://app.au.workato.com"
    ),
    "il": RegionInfo(
        region="il", name="IL Data Center", url="https://app.il.workato.com"
    ),
    "trial": RegionInfo(
        region="trial", name="Developer Sandbox", url="https://app.trial.workato.com"
    ),
    "custom": RegionInfo(region="custom", name="Custom URL", url=None),
}


def _set_secure_permissions(path: Path) -> None:
    """Best-effort attempt to set secure file permissions."""
    with contextlib.suppress(OSError):
        path.chmod(0o600)
        # On some platforms (e.g., Windows) chmod may fail; ignore silently.


class _WorkatoFileKeyring(KeyringBackend):
    """Fallback keyring that stores secrets in a local JSON file."""

    @properties.classproperty
    def priority(self) -> float:
        return 0.1

    def __init__(self, storage_path: Path) -> None:
        super().__init__()
        self._storage_path = storage_path
        self._lock = threading.Lock()
        self._ensure_storage_initialized()

    def _ensure_storage_initialized(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._storage_path.write_text("{}", encoding="utf-8")
            _set_secure_permissions(self._storage_path)

    def _load_data(self) -> dict[str, dict[str, str]]:
        try:
            raw = self._storage_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        except OSError:
            return {}

        if not raw.strip():
            return {}

        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError:
            return {}

        if isinstance(loaded, dict):
            # Ensure nested dictionaries
            normalized: dict[str, dict[str, str]] = {}
            for service, usernames in loaded.items():
                if isinstance(usernames, dict):
                    normalized[service] = {
                        str(username): str(password)
                        for username, password in usernames.items()
                    }
            return normalized
        return {}

    def _save_data(self, data: dict[str, dict[str, str]]) -> None:
        serialized = json.dumps(data, indent=2)
        self._storage_path.write_text(serialized, encoding="utf-8")
        _set_secure_permissions(self._storage_path)

    def get_password(self, service: str, username: str) -> str | None:
        with self._lock:
            data = self._load_data()
            return data.get(service, {}).get(username)

    def set_password(self, service: str, username: str, password: str) -> None:
        with self._lock:
            data = self._load_data()
            data.setdefault(service, {})[username] = password
            self._save_data(data)

    def delete_password(self, service: str, username: str) -> None:
        with self._lock:
            data = self._load_data()
            usernames = data.get(service)
            if usernames and username in usernames:
                del usernames[username]
                if not usernames:
                    del data[service]
                self._save_data(data)


class ProjectInfo(BaseModel):
    """Data model for project information"""

    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    folder_id: int | None = Field(None, description="Associated folder ID")


class ProfileData(BaseModel):
    """Data model for a single profile"""

    region: str = Field(
        ..., description="Region code (us, eu, jp, sg, au, il, trial, custom)"
    )
    region_url: str = Field(..., description="Base URL for the region")
    workspace_id: int = Field(..., description="Workspace ID")

    @field_validator("region")
    def validate_region(cls, v: str) -> str:  # noqa: N805
        """Validate region code"""
        valid_regions = {"us", "eu", "jp", "sg", "au", "il", "trial", "custom"}
        if v not in valid_regions:
            raise ValueError(f"Invalid region code: {v}")
        return v

    @property
    def region_name(self) -> str:
        """Get human-readable region name from region code"""
        region_info = AVAILABLE_REGIONS.get(self.region)
        return region_info.name if region_info else f"Unknown ({self.region})"


class ProfilesConfig(BaseModel):
    """Data model for profiles file (~/.workato/profiles)"""

    current_profile: str | None = Field(None, description="Currently active profile")
    profiles: dict[str, ProfileData] = Field(
        default_factory=dict, description="Profile definitions"
    )


class ConfigData(BaseModel):
    """Data model for project-specific configuration file data"""

    project_id: int | None = Field(None, description="Current project ID")
    project_name: str | None = Field(None, description="Current project name")
    folder_id: int | None = Field(None, description="Current folder ID")
    profile: str | None = Field(None, description="Profile override for this project")


class ProfileManager:
    """Manages profiles file configuration"""

    def __init__(self) -> None:
        """Initialize profile manager"""
        self.global_config_dir = Path.home() / ".workato"
        self.profiles_file = self.global_config_dir / "profiles"
        self.keyring_service = "workato-platform-cli"
        self._fallback_token_file = self.global_config_dir / "token_store.json"
        self._using_fallback_keyring = False
        self._ensure_keyring_backend()

    def _ensure_keyring_backend(self, force_fallback: bool = False) -> None:
        """Ensure a usable keyring backend is available for storing tokens."""
        if os.environ.get("WORKATO_DISABLE_KEYRING", "").lower() == "true":
            self._using_fallback_keyring = False
            return

        if force_fallback:
            fallback_keyring = _WorkatoFileKeyring(self._fallback_token_file)
            keyring.set_keyring(fallback_keyring)
            self._using_fallback_keyring = True
            return

        try:
            backend = keyring.get_keyring()
        except Exception:
            backend = None

        backend_priority = getattr(backend, "priority", 0) if backend else 0
        backend_module = getattr(backend, "__class__", type("", (), {})).__module__

        if (
            backend_priority
            and backend_priority > 0
            and not str(backend_module).startswith("keyring.backends.fail")
        ):
            # Perform a quick health check to ensure the backend is usable.
            test_service = f"{self.keyring_service}-self-test"
            test_username = "__workato__"
            with contextlib.suppress(NoKeyringError, KeyringError, Exception):
                backend = backend or keyring.get_keyring()
                backend.set_password(test_service, test_username, "0")
                backend.delete_password(test_service, test_username)
                self._using_fallback_keyring = False
                return

        fallback_keyring = _WorkatoFileKeyring(self._fallback_token_file)
        keyring.set_keyring(fallback_keyring)
        self._using_fallback_keyring = True

    def _is_keyring_enabled(self) -> bool:
        """Check if keyring usage is enabled"""
        return os.environ.get("WORKATO_DISABLE_KEYRING", "").lower() != "true"

    def _get_token_from_keyring(self, profile_name: str) -> str | None:
        """Get API token from keyring for the given profile"""
        if not self._is_keyring_enabled():
            return None

        try:
            pw: str | None = keyring.get_password(self.keyring_service, profile_name)
            return pw
        except NoKeyringError:
            if not self._using_fallback_keyring:
                self._ensure_keyring_backend(force_fallback=True)
            if self._using_fallback_keyring:
                with contextlib.suppress(NoKeyringError, KeyringError, Exception):
                    token: str | None = keyring.get_password(
                        self.keyring_service, profile_name
                    )
                    return token
            return None
        except KeyringError:
            if not self._using_fallback_keyring:
                self._ensure_keyring_backend(force_fallback=True)
            if self._using_fallback_keyring:
                with contextlib.suppress(NoKeyringError, KeyringError, Exception):
                    fallback_token: str | None = keyring.get_password(
                        self.keyring_service, profile_name
                    )
                    return fallback_token
            return None
        except Exception:
            return None

    def _store_token_in_keyring(self, profile_name: str, token: str) -> bool:
        """Store API token in keyring for the given profile"""
        if not self._is_keyring_enabled():
            return False

        try:
            keyring.set_password(self.keyring_service, profile_name, token)
            return True
        except NoKeyringError:
            if not self._using_fallback_keyring:
                self._ensure_keyring_backend(force_fallback=True)
            if self._using_fallback_keyring:
                with contextlib.suppress(NoKeyringError, KeyringError, Exception):
                    keyring.set_password(self.keyring_service, profile_name, token)
                    return True
            return False
        except KeyringError:
            if not self._using_fallback_keyring:
                self._ensure_keyring_backend(force_fallback=True)
            if self._using_fallback_keyring:
                with contextlib.suppress(NoKeyringError, KeyringError, Exception):
                    keyring.set_password(self.keyring_service, profile_name, token)
                    return True
            return False
        except Exception:
            return False

    def _delete_token_from_keyring(self, profile_name: str) -> bool:
        """Delete API token from keyring for the given profile"""
        if not self._is_keyring_enabled():
            return False

        try:
            keyring.delete_password(self.keyring_service, profile_name)
            return True
        except NoKeyringError:
            if not self._using_fallback_keyring:
                self._ensure_keyring_backend(force_fallback=True)
            if self._using_fallback_keyring:
                with contextlib.suppress(NoKeyringError, KeyringError, Exception):
                    keyring.delete_password(self.keyring_service, profile_name)
                    return True
            return False
        except KeyringError:
            if not self._using_fallback_keyring:
                self._ensure_keyring_backend(force_fallback=True)
            if self._using_fallback_keyring:
                with contextlib.suppress(NoKeyringError, KeyringError, Exception):
                    keyring.delete_password(self.keyring_service, profile_name)
                    return True
            return False
        except Exception:
            return False

    def _ensure_global_config_dir(self) -> None:
        """Ensure global config directory exists with proper permissions"""
        self.global_config_dir.mkdir(exist_ok=True, mode=0o700)  # Only user can access

    def load_profiles(self) -> ProfilesConfig:
        """Load profiles configuration from file"""
        if not self.profiles_file.exists():
            return ProfilesConfig(current_profile=None, profiles={})

        try:
            with open(self.profiles_file) as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Invalid profiles file")
                config: ProfilesConfig = ProfilesConfig.model_validate(data)
                return config
        except (json.JSONDecodeError, ValueError):
            return ProfilesConfig(current_profile=None, profiles={})

    def save_profiles(self, profiles_config: ProfilesConfig) -> None:
        """Save profiles configuration to file with secure permissions"""
        self._ensure_global_config_dir()

        # Write to temp file first, then rename for atomic operation
        temp_file = self.profiles_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(profiles_config.model_dump(exclude_none=True), f, indent=2)

        # Set secure permissions (only user can read/write)
        temp_file.chmod(0o600)

        # Atomic rename
        temp_file.rename(self.profiles_file)

    def get_profile(self, profile_name: str) -> ProfileData | None:
        """Get profile data by name"""
        profiles_config = self.load_profiles()
        return profiles_config.profiles.get(profile_name)

    def set_profile(
        self, profile_name: str, profile_data: ProfileData, token: str | None = None
    ) -> None:
        """Set or update a profile"""
        profiles_config = self.load_profiles()
        profiles_config.profiles[profile_name] = profile_data
        self.save_profiles(profiles_config)

        # Store token in keyring if provided
        if not token or self._store_token_in_keyring(profile_name, token):
            return

        if self._is_keyring_enabled():
            raise ValueError(
                "Failed to store token in keyring. "
                "Please check your system keyring setup."
            )
        else:
            raise ValueError(
                "Keyring is disabled. "
                "Please set WORKATO_API_TOKEN environment variable instead."
            )

    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile by name"""
        profiles_config = self.load_profiles()
        if profile_name not in profiles_config.profiles:
            return False

        del profiles_config.profiles[profile_name]

        # If this was the current profile, clear it
        if profiles_config.current_profile == profile_name:
            profiles_config.current_profile = None

        # Delete token from keyring
        self._delete_token_from_keyring(profile_name)

        self.save_profiles(profiles_config)
        return True

    def get_current_profile_name(
        self, project_profile_override: str | None = None
    ) -> str | None:
        """Get current profile name, considering project override"""
        # Priority order:
        # 1. Project-specific profile override
        # 2. Environment variable WORKATO_PROFILE
        # 3. Global current profile setting

        if project_profile_override:
            return project_profile_override

        env_profile = os.environ.get("WORKATO_PROFILE")
        if env_profile:
            return env_profile

        profiles_config = self.load_profiles()
        return profiles_config.current_profile

    def set_current_profile(self, profile_name: str | None) -> None:
        """Set the current profile in global config"""
        profiles_config = self.load_profiles()
        profiles_config.current_profile = profile_name
        self.save_profiles(profiles_config)

    def get_current_profile_data(
        self, project_profile_override: str | None = None
    ) -> ProfileData | None:
        """Get current profile data"""
        profile_name = self.get_current_profile_name(project_profile_override)
        if not profile_name:
            return None
        return self.get_profile(profile_name)

    def list_profiles(self) -> dict[str, ProfileData]:
        """Get all available profiles"""
        profiles_config = self.load_profiles()
        return profiles_config.profiles.copy()

    def resolve_environment_variables(
        self, project_profile_override: str | None = None
    ) -> tuple[str | None, str | None]:
        """Resolve API token and host with environment variable override support

        Priority order:
        1. Environment variables: WORKATO_API_TOKEN, WORKATO_HOST (highest)
        2. Profile from keyring + credentials file

        Returns:
            Tuple of (api_token, api_host) or (None, None) if no valid source
        """
        # Check for environment variable overrides first (highest priority)
        env_token = os.environ.get("WORKATO_API_TOKEN")
        env_host = os.environ.get("WORKATO_HOST")

        if env_token and env_host:
            return env_token, env_host

        # Fall back to profile-based configuration
        profile_name = self.get_current_profile_name(project_profile_override)
        if not profile_name:
            return None, None

        profile_data = self.get_profile(profile_name)
        if not profile_data:
            return None, None

        # Get token from keyring or env var, use profile data for host
        api_token = env_token or self._get_token_from_keyring(profile_name)
        api_host = env_host or profile_data.region_url

        return api_token, api_host

    def validate_credentials(
        self, project_profile_override: str | None = None
    ) -> tuple[bool, list[str]]:
        """Validate that credentials are available from environment or profile

        Returns:
            Tuple of (is_valid, missing_items)
        """
        api_token, api_host = self.resolve_environment_variables(
            project_profile_override
        )
        missing_items = []

        if not api_token:
            missing_items.append("API token (WORKATO_API_TOKEN or profile credentials)")
        if not api_host:
            missing_items.append("API host (WORKATO_HOST or profile region)")

        return len(missing_items) == 0, missing_items


class ConfigManager:
    """Configuration manager for Workato CLI"""

    def __init__(self, config_dir: Path | None = None, skip_validation: bool = False):
        """Initialize config manager"""
        self.config_dir = config_dir or self._get_default_config_dir()
        self.profile_manager = ProfileManager()

        # Only validate if not explicitly skipped
        if not skip_validation:
            self._validate_env_vars_or_exit()

    @classmethod
    async def initialize(cls, config_dir: Path | None = None) -> "ConfigManager":
        """Complete workspace initialization flow"""
        click.echo("🚀 Welcome to Workato CLI")
        click.echo()

        # Use skip_validation=True for setup
        manager = cls(config_dir, skip_validation=True)
        await manager._run_setup_flow()

        # Return the setup manager instance - it should work fine for credential access
        return manager

    async def _run_setup_flow(self) -> None:
        """Run the complete setup flow"""
        # Step 1: Configure profile name
        click.echo("📋 Step 1: Create or select a profile")
        existing_profiles = self.profile_manager.list_profiles()

        profile_name = None
        is_existing_profile = False

        if existing_profiles:
            # Show profile selection menu
            choices = list(existing_profiles.keys()) + ["Create new profile"]  # noboost
            questions = [
                inquirer.List(
                    "profile_choice",
                    message="Select a profile",  # noboost
                    choices=choices,
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers:
                click.echo("❌ No profile selected")
                sys.exit(1)

            if answers["profile_choice"] == "Create new profile":
                profile_name = click.prompt("Enter new profile name", type=str).strip()
                if not profile_name:
                    click.echo("❌ Profile name cannot be empty")
                    sys.exit(1)
                is_existing_profile = False
            else:
                profile_name = answers["profile_choice"]
                is_existing_profile = True
        else:
            # No existing profiles, create first one
            profile_name = click.prompt(
                "Enter profile name", default="default", type=str
            ).strip()

            if not profile_name:
                click.echo("❌ Profile name cannot be empty")
                sys.exit(1)
            is_existing_profile = False

        # Get existing profile data for defaults
        existing_profile_data = None
        if is_existing_profile:
            existing_profile_data = self.profile_manager.get_profile(profile_name)

        # Step 2: Configure region
        click.echo("📍 Step 2: Select your Workato region")
        if existing_profile_data:
            click.echo(
                f"Current region: {existing_profile_data.region_name} "
                f"({existing_profile_data.region_url})"
            )

        region = self.select_region_interactive(profile_name)
        if not region or not region.url:
            click.echo("❌ Setup cancelled")
            sys.exit(1)

        click.echo(f"✅ Region: {region.name}")

        # Step 3: Authenticate user
        click.echo("🔐 Step 3: Authenticate with your API token")

        # Check if token already exists for this profile
        current_token = None
        if is_existing_profile and existing_profile_data:
            # Check for environment variable override first
            env_token = os.environ.get("WORKATO_API_TOKEN")
            if env_token:
                current_token = env_token
                click.echo("Current token: Found in WORKATO_API_TOKEN")
            else:
                # Try to get token from keyring
                keyring_token = self.profile_manager._get_token_from_keyring(
                    profile_name
                )
                if keyring_token:
                    current_token = keyring_token
                    masked_token = current_token[:8] + "..." + current_token[-4:]
                    click.echo(f"Current token: {masked_token} (from keyring)")

            if current_token:
                if click.confirm("Use existing token?", default=True):
                    token = current_token
                else:
                    token = click.prompt(
                        "Enter your Workato API token", hide_input=True
                    )
            else:
                click.echo("No token found for this profile")
                token = click.prompt("Enter your Workato API token", hide_input=True)
        else:
            # New profile
            token = click.prompt("Enter your Workato API token", hide_input=True)

        if not token.strip():
            click.echo("❌ No token provided")
            sys.exit(1)

        # Create configuration for API client
        api_config = Configuration(
            access_token=token,
            host=region.url,
        )
        api_config.verify_ssl = False

        # Test authentication
        async with Workato(configuration=api_config) as workato_api_client:
            user_info = await workato_api_client.users_api.get_workspace_details()

        # Create profile data (without token)
        profile_data = ProfileData(
            region=region.region,
            region_url=region.url,
            workspace_id=user_info.id,
        )

        # Save profile to profiles file and store token in keyring
        self.profile_manager.set_profile(profile_name, profile_data, token)

        # Set as current profile
        self.profile_manager.set_current_profile(profile_name)

        action = "updated" if is_existing_profile else "created"
        click.echo(
            f"✅ Profile '{profile_name}' {action} and saved to ~/.workato/profiles"
        )
        click.echo("✅ Credentials available immediately for all CLI commands")
        click.echo("💡 Override with WORKATO_API_TOKEN environment variable if needed")

        click.echo(f"✅ Authenticated as: {user_info.name}")

        # Step 4: Setup project
        click.echo("📁 Step 4: Setup your project")
        # Check for existing project first
        meta_data = self.load_config()
        if meta_data.project_id:
            click.echo(f"Found existing project: {meta_data.project_name or 'Unknown'}")
            if click.confirm("Use this project?", default=True):
                # Update project to use the current profile
                current_profile_name = self.profile_manager.get_current_profile_name()
                if current_profile_name:
                    meta_data.profile = current_profile_name

                # Validate that the project exists in the current workspace
                async with Workato(configuration=api_config) as workato_api_client:
                    project_manager = ProjectManager(
                        workato_api_client=workato_api_client
                    )

                    # Check if the folder exists by trying to list its assets
                    try:
                        if meta_data.folder_id is None:
                            raise Exception("No folder ID configured")
                        await project_manager.check_folder_assets(meta_data.folder_id)
                        # Project exists, save the updated config
                        self.save_config(meta_data)
                        click.echo(f"   Updated profile: {current_profile_name}")
                        click.echo("✅ Using existing project")
                        click.echo("🎉 Setup complete!")
                        click.echo()
                        click.echo("💡 Next steps:")
                        click.echo("  • workato workspace")
                        click.echo("  • workato --help")
                        return
                    except Exception:
                        # Project doesn't exist in current workspace
                        project_name = meta_data.project_name
                        msg = f"❌ Project '{project_name}' not found in workspace"
                        click.echo(msg)
                        click.echo("   This can happen when switching profiles")
                        click.echo("   Please select a new project:")
                        # Continue to project selection below

        # Create a new client instance for project operations
        async with Workato(configuration=api_config) as workato_api_client:
            project_manager = ProjectManager(workato_api_client=workato_api_client)

            # Select new project
            projects = await project_manager.get_all_projects()

            # Always include "Create new project" option
            choices = ["Create new project"]
            project_choices = []

            if projects:
                project_choices = [(f"{p.name} (ID: {p.id})", p) for p in projects]
                choices.extend([choice[0] for choice in project_choices])

            questions = [
                inquirer.List(
                    "project",
                    message="Select a project",  # noboost
                    choices=choices,
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                click.echo("❌ No project selected")
                sys.exit(1)

            selected_project = None

            # Handle "Create new project" option
            if answers["project"] == "Create new project":
                project_name = click.prompt("Enter project name", type=str)
                if not project_name or not project_name.strip():
                    click.echo("❌ Project name cannot be empty")
                    sys.exit(1)

                click.echo(f"🔨 Creating project: {project_name}")
                selected_project = await project_manager.create_project(project_name)
                click.echo(f"✅ Created project: {selected_project.name}")
            else:
                # Find selected existing project
                for choice_text, project in project_choices:
                    if choice_text == answers["project"]:
                        selected_project = project
                        break

            if selected_project:
                # Save project info and tie it to current profile for safety
                meta_data.project_id = selected_project.id
                meta_data.project_name = selected_project.name
                meta_data.folder_id = selected_project.folder_id

                # Capture current effective profile to tie project to workspace
                current_profile_name = self.profile_manager.get_current_profile_name()
                if current_profile_name:
                    meta_data.profile = current_profile_name
                    click.echo(f"   Profile: {current_profile_name}")

                self.save_config(meta_data)
                click.echo(f"✅ Project: {selected_project.name}")

        click.echo("🎉 Setup complete!")
        click.echo()
        click.echo("💡 Next steps:")
        click.echo("  • workato workspace")
        click.echo("  • workato --help")

    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory using hierarchical search"""
        # First, try to find nearest .workatoenv file up the hierarchy
        config_file_path = self._find_nearest_workatoenv_file()

        # If no .workatoenv found up the hierarchy, use current directory
        if config_file_path is None:
            return Path.cwd()
        else:
            return config_file_path.parent

    def _find_nearest_workatoenv_file(self) -> Path | None:
        """Find the nearest .workatoenv file by traversing up the directory tree"""
        current = Path.cwd().resolve()

        # Only traverse up within reasonable project boundaries
        # Stop at home directory to avoid going to global config
        home_dir = Path.home().resolve()

        while current != current.parent and current != home_dir:
            workatoenv_file = current / ".workatoenv"
            if workatoenv_file.exists() and workatoenv_file.is_file():
                return workatoenv_file
            current = current.parent

        return None

    def get_project_root(self) -> Path | None:
        """Get the root directory of the current project (containing .workatoenv)"""
        workatoenv_file = self._find_nearest_workatoenv_file()
        return workatoenv_file.parent if workatoenv_file else None

    def get_current_project_name(self) -> str | None:
        """Get the current project name from directory structure"""
        project_root = self.get_project_root()
        if not project_root:
            return None

        # Check if we're in a projects/{name} structure
        if (
            project_root.parent.name == "projects"
            and project_root.parent.parent.exists()
        ):
            return project_root.name

        return None

    def is_in_project_workspace(self) -> bool:
        """Check if current directory is within a project workspace"""
        return self._find_nearest_workatoenv_file() is not None

    # Configuration File Management

    def load_config(self) -> ConfigData:
        """Load project metadata from .workatoenv"""
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
        """Save project metadata (without sensitive data) to .workatoenv"""
        config_file = self.config_dir / ".workatoenv"

        with open(config_file, "w") as f:
            json.dump(config_data.model_dump(exclude_none=True), f, indent=2)

    def save_project_info(self, project_info: ProjectInfo) -> None:
        """Save project information to configuration - returns success boolean"""
        config_data = self.load_config()
        updated_config = ConfigData(
            **config_data.model_dump(),
            project_id=project_info.id,
            project_name=project_info.name,
            folder_id=project_info.folder_id,
        )
        self.save_config(updated_config)

    # API Token Management

    def validate_environment_config(self) -> tuple[bool, list[str]]:
        """Validate that required credentials are available

        Returns:
            Tuple of (is_valid, missing_items) where missing_items contains
            descriptions of missing required credentials
        """
        # Get current profile from project config
        config_data = self.load_config()
        project_profile_override = config_data.profile

        # Validate credentials using profile manager
        return self.profile_manager.validate_credentials(project_profile_override)

    def _validate_env_vars_or_exit(self) -> None:
        """Validate credentials and exit if missing"""
        is_valid, missing_items = self.validate_environment_config()
        if not is_valid:
            import sys

            click.echo("❌ Missing required credentials:")
            for item in missing_items:
                click.echo(f"   • {item}")
            click.echo()
            click.echo(
                "💡 Run 'workato init' to set up authentication and configuration"
            )
            sys.exit(1)

    @property
    def api_token(self) -> str | None:
        """Get API token from current profile environment variable"""
        config_data = self.load_config()
        project_profile_override = config_data.profile
        api_token, _ = self.profile_manager.resolve_environment_variables(
            project_profile_override
        )
        return api_token

    @api_token.setter
    def api_token(self, value: str) -> None:
        """Save API token as environment variable with shell persistence"""
        self._set_api_token(value)

    def _set_api_token(self, api_token: str) -> None:
        """Internal method to save API token to the current profile"""
        # Get current profile from project config
        config_data = self.load_config()
        project_profile_override = config_data.profile

        # Get current profile name or use "default"
        current_profile_name = self.profile_manager.get_current_profile_name(
            project_profile_override
        )
        if not current_profile_name:
            current_profile_name = "default"

        # Check if profile exists
        profiles = self.profile_manager.load_profiles()
        if current_profile_name not in profiles.profiles:
            # If profile doesn't exist, we need more info to create it
            raise ValueError(
                f"Profile '{current_profile_name}' does not exist. "
                "Please run 'workato init' to create a profile first."
            )

        # Store the token in keyring
        success = self.profile_manager._store_token_in_keyring(
            current_profile_name, api_token
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

    # API Host Management

    @property
    def api_host(self) -> str | None:
        """Get API host from current profile"""
        config_data = self.load_config()
        project_profile_override = config_data.profile
        _, api_host = self.profile_manager.resolve_environment_variables(
            project_profile_override
        )
        return api_host

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

        # Get current profile name
        config_data = self.load_config()
        project_profile_override = config_data.profile
        current_profile_name = self.profile_manager.get_current_profile_name(
            project_profile_override
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

            # Validate URL format and security
            is_valid, error_msg = _validate_url_security(custom_url)
            if not is_valid:
                return False, error_msg

            # Parse URL and keep only scheme + netloc (strip any path components)
            parsed = urlparse(custom_url)
            region_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            region_url = region_info.url or ""

        # Update the profile with new region info
        profiles.profiles[current_profile_name].region = region_code.lower()
        profiles.profiles[current_profile_name].region_url = region_url

        # Save updated profiles
        self.profile_manager.save_profiles(profiles)

        return True, f"{region_info.name} ({region_info.url})"

    def select_region_interactive(
        self, profile_name: str | None = None
    ) -> RegionInfo | None:
        """Interactive region selection"""
        regions = list(AVAILABLE_REGIONS.values())

        click.echo()

        # Create choices for inquirer
        choices = []
        for region in regions:
            if region.region == "custom":
                choice_text = "Custom URL"
            else:
                choice_text = f"{region.name} ({region.url})"

            choices.append(choice_text)

        questions = [
            inquirer.List(
                "region",
                message="Select your Workato region",  # noboost
                choices=choices,
            ),
        ]

        answers = inquirer.prompt(questions)
        if not answers:  # User cancelled
            return None

        # Find the selected region by index
        selected_choice = answers["region"]
        selected_index = choices.index(selected_choice)
        selected_region = regions[selected_index]

        # Handle custom URL
        if selected_region.region == "custom":
            click.echo()

            # Get selected profile's custom URL as default
            profile_data = None
            if profile_name:
                profile_data = self.profile_manager.get_profile(profile_name)
            else:
                profile_data = self.profile_manager.get_current_profile_data()

            current_url = "https://www.workato.com"  # fallback default
            if profile_data and profile_data.region == "custom":
                current_url = profile_data.region_url

            custom_url = click.prompt(
                "Enter your custom Workato base URL",
                type=str,
                default=current_url,
            )

            # Validate URL security
            is_valid, error_msg = _validate_url_security(custom_url)
            if not is_valid:
                click.echo(f"❌ {error_msg}")
                return None

            # Parse URL and keep only scheme + netloc (strip any path components)
            parsed = urlparse(custom_url)
            custom_url = f"{parsed.scheme}://{parsed.netloc}"

            return RegionInfo(region="custom", name="Custom URL", url=custom_url)

        return selected_region
