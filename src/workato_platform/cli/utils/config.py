"""Simplified configuration management for the CLI with clear workspace rules"""

import contextlib
import json
import os
import sys
import threading
from pathlib import Path
from typing import Optional
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
    """Validate URL security - only allow HTTP for localhost, require HTTPS for others."""
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


def _set_secure_permissions(path: Path) -> None:
    """Best-effort attempt to set secure file permissions."""
    with contextlib.suppress(OSError):
        path.chmod(0o600)


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
        self.global_config_dir.mkdir(exist_ok=True, mode=0o700)

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
        """Resolve API token and host with environment variable override support"""
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
        """Validate that credentials are available from environment or profile"""
        api_token, api_host = self.resolve_environment_variables(
            project_profile_override
        )
        missing_items = []

        if not api_token:
            missing_items.append("API token (WORKATO_API_TOKEN or profile credentials)")
        if not api_host:
            missing_items.append("API host (WORKATO_HOST or profile region)")

        return len(missing_items) == 0, missing_items

    def select_region_interactive(self, profile_name: str | None = None) -> RegionInfo | None:
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
                message="Select your Workato region",
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
                profile_data = self.get_profile(profile_name)
            else:
                profile_data = self.get_current_profile_data()

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


class ProjectInfo(BaseModel):
    """Data model for project information"""
    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    folder_id: Optional[int] = Field(None, description="Associated folder ID")


class ConfigData(BaseModel):
    """Data model for configuration file data"""
    project_id: Optional[int] = Field(None, description="Project ID")
    project_name: Optional[str] = Field(None, description="Project name")
    project_path: Optional[str] = Field(None, description="Relative path to project (workspace only)")
    folder_id: Optional[int] = Field(None, description="Folder ID")
    profile: Optional[str] = Field(None, description="Profile override")


class WorkspaceManager:
    """Manages workspace root detection and validation"""

    def __init__(self, start_path: Optional[Path] = None):
        self.start_path = start_path or Path.cwd()

    def find_nearest_workatoenv(self) -> Optional[Path]:
        """Find the nearest .workatoenv file by traversing up the directory tree"""
        current = self.start_path.resolve()

        while current != current.parent:
            workatoenv_file = current / ".workatoenv"
            if workatoenv_file.exists():
                return current
            current = current.parent

        return None

    def find_workspace_root(self) -> Path:
        """Find workspace root by traversing up for .workatoenv file with project_path"""
        current = self.start_path.resolve()

        while current != current.parent:
            workatoenv_file = current / ".workatoenv"
            if workatoenv_file.exists():
                try:
                    with open(workatoenv_file) as f:
                        data = json.load(f)
                        # Workspace root has project_path pointing to a project
                        if "project_path" in data and data["project_path"]:
                            return current
                        # If no project_path, this might be a project directory itself
                        elif "project_id" in data and not data.get("project_path"):
                            # This is a project directory, continue searching up
                            pass
                except (json.JSONDecodeError, OSError):
                    pass
            current = current.parent

        # If no workspace found, current directory becomes workspace root
        return self.start_path

    def is_in_project_directory(self) -> bool:
        """Check if current directory is a project directory"""
        workatoenv_file = self.start_path / ".workatoenv"
        if not workatoenv_file.exists():
            return False

        try:
            with open(workatoenv_file) as f:
                data = json.load(f)
                # Project directory has project_id but no project_path
                return "project_id" in data and not data.get("project_path")
        except (json.JSONDecodeError, OSError):
            return False

    def validate_not_in_project(self) -> None:
        """Validate that we're not running from within a project directory"""
        if self.is_in_project_directory():
            workspace_root = self.find_workspace_root()
            if workspace_root != self.start_path:
                click.echo(f"❌ Run init from workspace root: {workspace_root}")
            else:
                click.echo("❌ Cannot run init from within a project directory")
            sys.exit(1)

    def validate_project_path(self, project_path: Path, workspace_root: Path) -> None:
        """Validate project path follows our rules"""
        # Convert to absolute paths for comparison
        abs_project_path = project_path.resolve()
        abs_workspace_root = workspace_root.resolve()

        # Project cannot be in workspace root directly
        if abs_project_path == abs_workspace_root:
            raise ValueError("Projects cannot be created in workspace root directly. Use a subdirectory.")

        # Project must be within workspace
        try:
            abs_project_path.relative_to(abs_workspace_root)
        except ValueError:
            raise ValueError(f"Project path must be within workspace root: {abs_workspace_root}")

        # Check for nested projects by looking for .workatoenv in parent directories
        current = abs_project_path.parent
        while current != abs_workspace_root and current != current.parent:
            if (current / ".workatoenv").exists():
                try:
                    with open(current / ".workatoenv") as f:
                        data = json.load(f)
                        if "project_id" in data:
                            raise ValueError(f"Cannot create project within another project: {current}")
                except (json.JSONDecodeError, OSError):
                    pass
            current = current.parent


class ConfigManager:
    """Simplified configuration manager with clear workspace rules"""

    def __init__(self, config_dir: Optional[Path] = None, skip_validation: bool = False):
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
    async def initialize(cls, config_dir: Optional[Path] = None) -> "ConfigManager":
        """Initialize workspace with interactive setup"""
        click.echo("🚀 Welcome to Workato CLI")
        click.echo()

        # Create manager without validation for setup
        manager = cls(config_dir, skip_validation=True)

        # Validate we're not in a project directory
        manager.workspace_manager.validate_not_in_project()

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

    async def _setup_profile(self) -> str:
        """Setup or select profile"""
        click.echo("📋 Step 1: Configure profile")

        existing_profiles = self.profile_manager.list_profiles()
        profile_name: str | None = None

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
                profile_name = click.prompt("Enter new profile name", type=str).strip()
                if not profile_name:
                    click.echo("❌ Profile name cannot be empty")
                    sys.exit(1)
                await self._create_new_profile(profile_name)
            else:
                profile_name = answers["profile_choice"]
        else:
            profile_name = click.prompt(
                "Enter profile name", default="default", type=str
            ).strip()
            if not profile_name:
                click.echo("❌ Profile name cannot be empty")
                sys.exit(1)
            await self._create_new_profile(profile_name)

        # Set as current profile
        self.profile_manager.set_current_profile(profile_name)
        click.echo(f"✅ Profile: {profile_name}")

        return profile_name

    async def _create_new_profile(self, profile_name: str) -> None:
        """Create a new profile interactively"""
        # AVAILABLE_REGIONS and RegionInfo already imported at top

        # Region selection
        click.echo("📍 Select your Workato region")
        regions = list(AVAILABLE_REGIONS.values())
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
                message="Select your Workato region",
                choices=choices,
            ),
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            click.echo("❌ Setup cancelled")
            sys.exit(1)

        selected_index = choices.index(answers["region"])
        selected_region = regions[selected_index]

        # Handle custom URL
        if selected_region.region == "custom":
            custom_url = click.prompt(
                "Enter your custom Workato base URL",
                type=str,
                default="https://www.workato.com",
            )
            selected_region = RegionInfo(region="custom", name="Custom URL", url=custom_url)

        # Get API token
        click.echo("🔐 Enter your API token")
        token = click.prompt("Enter your Workato API token", hide_input=True)
        if not token.strip():
            click.echo("❌ No token provided")
            sys.exit(1)

        # Test authentication and get workspace info
        api_config = Configuration(access_token=token, host=selected_region.url)
        api_config.verify_ssl = False

        async with Workato(configuration=api_config) as workato_api_client:
            user_info = await workato_api_client.users_api.get_workspace_details()

        # Create and save profile
        profile_data = ProfileData(
            region=selected_region.region,
            region_url=selected_region.url,
            workspace_id=user_info.id,
        )

        self.profile_manager.set_profile(profile_name, profile_data, token)
        click.echo(f"✅ Authenticated as: {user_info.name}")

    async def _setup_project(self, profile_name: str, workspace_root: Path) -> None:
        """Setup project interactively"""
        click.echo("📁 Step 2: Setup project")

        # Check for existing project
        existing_config = self.load_config()
        if existing_config.project_id:
            click.echo(f"Found existing project: {existing_config.project_name}")
            if click.confirm("Use this project?", default=True):
                # Update profile and we're done
                existing_config.profile = profile_name
                self.save_config(existing_config)
                return

        # Determine project location from current directory
        current_dir = Path.cwd().resolve()
        if current_dir == workspace_root:
            # Running from workspace root - need to create subdirectory
            project_location_mode = "workspace_root"
        else:
            # Running from subdirectory - use current directory as project location
            project_location_mode = "current_dir"

        # Get API client for project operations
        config_data = ConfigData(profile=profile_name)
        api_token, api_host = self.profile_manager.resolve_environment_variables(profile_name)
        api_config = Configuration(access_token=api_token, host=api_host)
        api_config.verify_ssl = False

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
                project_name = click.prompt("Enter project name", type=str)
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

            # Always create project subdirectory named after the project
            project_name = selected_project.name

            if project_location_mode == "current_dir":
                # Create project subdirectory within current directory
                project_path = current_dir / project_name
            else:
                # Create project subdirectory in workspace root
                project_path = workspace_root / project_name

            # Validate project path
            try:
                self.workspace_manager.validate_project_path(project_path, workspace_root)
            except ValueError as e:
                click.echo(f"❌ {e}")
                sys.exit(1)

            # Check if project directory already exists and is non-empty
            if project_path.exists():
                try:
                    # Check if directory has any files
                    existing_files = list(project_path.iterdir())
                    if existing_files:
                        # Check if it's a Workato project with matching project ID
                        existing_workatoenv = project_path / ".workatoenv"
                        if existing_workatoenv.exists():
                            try:
                                with open(existing_workatoenv) as f:
                                    existing_data = json.load(f)
                                    existing_project_id = existing_data.get("project_id")

                                if existing_project_id == selected_project.id:
                                    # Same project ID - allow reconfiguration
                                    click.echo(f"🔄 Reconfiguring existing project: {selected_project.name}")
                                elif existing_project_id:
                                    # Different project ID - block it
                                    existing_name = existing_data.get("project_name", "Unknown")
                                    click.echo(f"❌ Directory contains different Workato project: {existing_name} (ID: {existing_project_id})")
                                    click.echo(f"   Cannot initialize {selected_project.name} (ID: {selected_project.id}) here")
                                    click.echo("💡 Choose a different directory or project name")
                                    sys.exit(1)
                                # If no project_id in existing config, treat as invalid and block below
                            except (json.JSONDecodeError, OSError):
                                # Invalid .workatoenv file - treat as non-Workato project
                                pass

                        # Not a Workato project or invalid config - block it
                        if not (existing_workatoenv.exists() and existing_project_id == selected_project.id):
                            click.echo(f"❌ Project directory is not empty: {project_path.relative_to(workspace_root)}")
                            click.echo(f"   Found {len(existing_files)} existing files")
                            click.echo("💡 Choose a different project name or clean the directory first")
                            sys.exit(1)
                except OSError:
                    pass  # If we can't read the directory, let mkdir handle it

            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            click.echo(f"✅ Project directory: {project_path.relative_to(workspace_root)}")

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
            return ConfigData()

        try:
            with open(config_file) as f:
                data = json.load(f)
                return ConfigData.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            return ConfigData()

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

    def get_project_directory(self) -> Optional[Path]:
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

    def _handle_invalid_project_selection(self, workspace_root: Path, current_config: ConfigData) -> Optional[Path]:
        """Handle case where current project selection is invalid"""
        click.echo(f"⚠️  Configured project directory does not exist: {current_config.project_path}")
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
            import inquirer
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
            workspace_config.project_path = str(selected_path.relative_to(workspace_root))
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
                    if "project_id" in data and data.get("project_id") and not data.get("project_path"):
                        project_dir = workatoenv_file.parent
                        project_name = data.get("project_name", project_dir.name)
                        projects.append((project_dir, project_name))
            except (json.JSONDecodeError, OSError):
                continue

        return sorted(projects, key=lambda x: x[1])  # Sort by project name

    def get_current_project_name(self) -> Optional[str]:
        """Get current project name"""
        config_data = self.load_config()
        return config_data.project_name

    def get_project_root(self) -> Optional[Path]:
        """Get project root (directory containing .workatoenv)"""
        # For compatibility - this is the same as config_dir when in project
        if self.workspace_manager.is_in_project_directory():
            return self.config_dir

        # If in workspace, return project directory
        return self.get_project_directory()

    def is_in_project_workspace(self) -> bool:
        """Check if in a project workspace"""
        return self.get_workspace_root() is not None

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
    def api_token(self) -> Optional[str]:
        """Get API token"""
        config_data = self.load_config()
        api_token, _ = self.profile_manager.resolve_environment_variables(config_data.profile)
        return api_token

    @api_token.setter
    def api_token(self, value: str) -> None:
        """Save API token to current profile"""
        config_data = self.load_config()
        current_profile_name = self.profile_manager.get_current_profile_name(config_data.profile)

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
        success = self.profile_manager._store_token_in_keyring(current_profile_name, value)
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
    def api_host(self) -> Optional[str]:
        """Get API host"""
        config_data = self.load_config()
        _, api_host = self.profile_manager.resolve_environment_variables(config_data.profile)
        return api_host

    # Region management methods

    def validate_region(self, region_code: str) -> bool:
        """Validate if region code is valid"""
        return region_code.lower() in AVAILABLE_REGIONS

    def set_region(self, region_code: str, custom_url: Optional[str] = None) -> tuple[bool, str]:
        """Set region by updating the current profile"""

        if region_code.lower() not in AVAILABLE_REGIONS:
            return False, f"Invalid region: {region_code}"

        region_info = AVAILABLE_REGIONS[region_code.lower()]

        # Get current profile
        config_data = self.load_config()
        current_profile_name = self.profile_manager.get_current_profile_name(config_data.profile)
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
            from urllib.parse import urlparse
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