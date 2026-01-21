"""Profile management for multiple Workato environments."""

import asyncio
import contextlib
import json
import os
import threading

from pathlib import Path
from urllib.parse import urlparse

import asyncclick as click
import certifi
import inquirer
import keyring

from keyring.backend import KeyringBackend
from keyring.compat import properties
from keyring.errors import KeyringError, NoKeyringError

from workato_platform_cli import Workato
from workato_platform_cli.cli.utils.token_input import get_token_with_smart_paste
from workato_platform_cli.client.workato_api.configuration import Configuration

from .models import AVAILABLE_REGIONS, ProfileData, ProfilesConfig, RegionInfo


def _validate_url_security(url: str) -> tuple[bool, str]:
    """Validate URL security - only allow HTTP for localhost,
    require HTTPS for others."""
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

    async def select_region_interactive(
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

            custom_url = await click.prompt(
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

    async def create_profile_interactive(
        self, profile_name: str
    ) -> tuple[ProfileData, str]:
        """Create a new profile with interactive prompts for region and token.

        Performs region selection, token input, credential validation, and returns
        the validated profile data and token.

        Args:
            profile_name: Name of the profile being created

        Returns:
            tuple[ProfileData, str]: The validated profile data and API token

        Raises:
            click.ClickException: If setup is cancelled, token is empty,
                or validation fails
        """
        # Step 1: Select region
        click.echo("📍 Select your Workato region")
        selected_region = await self.select_region_interactive(profile_name)

        if not selected_region:
            raise click.ClickException("Setup cancelled")

        # Step 2: Get API token
        token = await asyncio.to_thread(
            get_token_with_smart_paste,
            prompt_text="API token",
        )
        if not token.strip():
            raise click.ClickException("API token cannot be empty")

        # Step 3: Test authentication and get workspace info
        click.echo("🔄 Validating credentials...")
        api_config = Configuration(
            access_token=token, host=selected_region.url, ssl_ca_cert=certifi.where()
        )

        try:
            async with Workato(configuration=api_config) as workato_api_client:
                user_info = await workato_api_client.users_api.get_workspace_details()
        except Exception as e:
            raise click.ClickException(f"Authentication failed: {e}") from e

        # Step 4: Create profile data
        if not selected_region.url:
            raise click.ClickException("Region URL is required")

        profile_data = ProfileData(
            region=selected_region.region,
            region_url=selected_region.url,
            workspace_id=user_info.id,
        )

        click.echo(f"✅ Authenticated as: {user_info.name}")

        return profile_data, token
