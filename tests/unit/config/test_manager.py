"""Tests for ConfigManager."""

import json

from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import asyncclick as click
import pytest

from workato_platform_cli import Workato
from workato_platform_cli.cli.utils.config.manager import (
    ConfigManager,
    ProfileManager,
    WorkspaceManager,
)
from workato_platform_cli.cli.utils.config.models import (
    ConfigData,
    ProfileData,
    ProjectInfo,
)
from workato_platform_cli.client.workato_api.configuration import Configuration
from workato_platform_cli.client.workato_api.models.user import User


@pytest.fixture
def mock_profile_manager() -> Mock:
    """Create a properly mocked ProfileManager for tests."""
    mock_pm = Mock(spec=ProfileManager)

    # Default profile data
    profiles_mock = Mock()
    profiles_mock.profiles = {
        "default": ProfileData(
            region="us",
            region_url="https://www.workato.com",
            workspace_id=1,
        ),
        "dev": ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=1
        ),
        "existing": ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=1
        ),
    }

    # Configure common methods
    mock_pm.list_profiles.return_value = profiles_mock.profiles
    mock_pm.load_profiles.return_value = profiles_mock
    mock_pm.get_current_profile_name.return_value = "default"
    mock_pm.resolve_environment_variables.return_value = (
        "token",
        "https://www.workato.com",
    )
    mock_pm.validate_credentials.return_value = (True, [])
    mock_pm._store_token_in_keyring.return_value = True
    mock_pm._is_keyring_enabled.return_value = True
    mock_pm.save_profiles = Mock()
    mock_pm.set_profile = Mock()
    mock_pm.set_current_profile = Mock()

    # Ensure get_profile returns actual ProfileData objects with valid regions
    mock_pm.get_profile.return_value = ProfileData(
        region="us",
        region_url="https://www.workato.com",
        workspace_id=1,
    )

    return mock_pm


class StubUsersAPI:
    async def get_workspace_details(self) -> User:
        return User(
            id=101,
            name="Stub User",
            created_at=datetime.now(),
            plan_id="plan_id",
            current_billing_period_start=datetime.now(),
            current_billing_period_end=datetime.now(),
            recipes_count=100,
            company_name="Stub Company",
            location="Stub Location",
            last_seen=datetime.now(),
            email="stub@example.com",
            active_recipes_count=100,
            root_folder_id=101,
        )


class StubWorkato:
    """Async Workato client stub."""

    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.users_api = StubUsersAPI()

    async def __aenter__(self) -> "StubWorkato":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


class StubProject:
    def __init__(self, project_id: int, name: str, folder_id: int) -> None:
        self.id = project_id
        self.name = name
        self.folder_id = folder_id


class StubProjectManager:
    """Minimal project manager stub."""

    available_projects: list[StubProject] = []
    created_projects: list[StubProject] = []

    def __init__(self, workato_api_client: Workato) -> None:
        self.workato_api_client = workato_api_client

    async def get_all_projects(self) -> list[StubProject]:
        return list(self.available_projects)

    async def create_project(self, project_name: str) -> StubProject:
        project = StubProject(999, project_name, 111)
        self.created_projects.append(project)
        return project


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_init_triggers_validation(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """__init__ should run credential validation when not skipped."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )

        calls: list[bool] = []

        def fake_validate(self: ConfigManager) -> None:  # noqa: D401
            calls.append(True)

        monkeypatch.setattr(
            ConfigManager, "_validate_credentials_or_exit", fake_validate
        )

        ConfigManager(config_dir=tmp_path)

        assert calls == [True]

    @pytest.mark.asyncio
    async def test_initialize_runs_setup_flow(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """initialize() should invoke validation guard and setup flow."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".WorkspaceManager.validate_not_in_project",
            lambda self: None,
        )

        run_mock = AsyncMock()
        monkeypatch.setattr(ConfigManager, "_run_setup_flow", run_mock)

        manager = await ConfigManager.initialize(tmp_path)

        assert isinstance(manager, ConfigManager)
        run_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_initialize_non_interactive_branch(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Non-interactive initialize should announce mode and call helper."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".WorkspaceManager.validate_not_in_project",
            lambda self: None,
        )

        setup_mock = AsyncMock()
        run_mock = AsyncMock()
        monkeypatch.setattr(ConfigManager, "_setup_non_interactive", setup_mock)
        monkeypatch.setattr(ConfigManager, "_run_setup_flow", run_mock)

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        manager = await ConfigManager.initialize(
            tmp_path,
            profile_name="dev",
            region="us",
            api_token="token",
            non_interactive=True,
        )

        assert isinstance(manager, ConfigManager)
        setup_mock.assert_awaited_once()
        run_mock.assert_not_awaited()
        assert any("Non-interactive mode" in line for line in outputs)

    @pytest.mark.asyncio
    async def test_run_setup_flow_invokes_steps(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_run_setup_flow should adjust config dir and call helpers."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()

        manager.workspace_manager = WorkspaceManager(start_path=workspace_root)

        profile_mock = AsyncMock(return_value="dev")
        project_mock = AsyncMock()
        create_mock = Mock()

        with (
            patch.object(manager, "_setup_profile", profile_mock),
            patch.object(manager, "_setup_project", project_mock),
            patch.object(manager, "_create_workspace_files", create_mock),
        ):
            await manager._run_setup_flow()

            assert manager.config_dir == workspace_root
            profile_mock.assert_awaited_once()
            project_mock.assert_awaited_once_with("dev", workspace_root)
            create_mock.assert_called_once_with(workspace_root)

    @pytest.mark.asyncio
    async def test_setup_non_interactive_creates_configs(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Non-interactive setup should create workspace and project configs."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path)
        monkeypatch.chdir(tmp_path)

        await manager._setup_non_interactive(
            profile_name="dev",
            region="us",
            api_token="token-123",
            project_name="DemoProject",
        )

        workspace_env = json.loads(
            (tmp_path / ".workatoenv").read_text(encoding="utf-8")
        )
        project_dir = tmp_path / "DemoProject"
        project_env = json.loads(
            (project_dir / ".workatoenv").read_text(encoding="utf-8")
        )

        assert workspace_env["project_name"] == "DemoProject"
        assert workspace_env["project_path"] == "DemoProject"
        assert project_env["project_name"] == "DemoProject"
        assert "project_path" not in project_env
        assert StubProjectManager.created_projects[-1].name == "DemoProject"

    @pytest.mark.asyncio
    async def test_setup_non_interactive_uses_project_id(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Providing project_id should reuse existing remote project."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        existing = StubProject(777, "Existing", 55)
        StubProjectManager.available_projects = [existing]
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path)
        monkeypatch.chdir(tmp_path)

        await manager._setup_non_interactive(
            profile_name="dev",
            region="us",
            api_token="token-xyz",
            project_id=777,
        )

        workspace_env = json.loads(
            (tmp_path / ".workatoenv").read_text(encoding="utf-8")
        )
        assert workspace_env["project_name"] == "Existing"
        assert StubProjectManager.created_projects == []

    @pytest.mark.asyncio
    async def test_setup_non_interactive_custom_region_subdirectory(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Custom region should accept URL and honor running from subdirectory."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path)

        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        await manager._setup_non_interactive(
            profile_name="dev",
            region="custom",
            api_token="token",
            api_url="https://custom.workato.test",
            project_name="CustomProj",
        )

        workspace_env = json.loads(
            (tmp_path / ".workatoenv").read_text(encoding="utf-8")
        )
        assert workspace_env["project_path"] == "subdir/CustomProj"
        assert StubProjectManager.created_projects[-1].name == "CustomProj"

    @pytest.mark.asyncio
    async def test_setup_non_interactive_project_id_not_found(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Unknown project_id should raise a descriptive ClickException."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path)

        with pytest.raises(click.ClickException) as excinfo:
            await manager._setup_non_interactive(
                profile_name="dev",
                region="us",
                api_token="token",
                project_id=999,
            )

        assert "Project with ID 999 not found" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_setup_non_interactive_requires_project_selection(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Missing project name and ID should raise ClickException."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path)

        with pytest.raises(click.ClickException) as excinfo:
            await manager._setup_non_interactive(
                profile_name="dev",
                region="us",
                api_token="token",
            )

        assert "No project selected" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_setup_non_interactive_with_env_vars(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Non-interactive mode should use environment variables automatically."""
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token-ni")
        monkeypatch.setenv("WORKATO_HOST", "https://www.workato.com")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        # Mock resolve_environment_variables to return None
        # so it uses the api_token/api_url params
        mock_profile_manager.resolve_environment_variables.return_value = (None, None)
        mock_profile_manager.get_current_profile_name.return_value = "env-profile"
        mock_profile_manager.get_profile.return_value = None  # No existing profile

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path)
        monkeypatch.chdir(tmp_path)

        # Should use env vars without requiring --region or --api-token flags
        await manager._setup_non_interactive(
            profile_name="env-profile",
            api_token="env-token-ni",
            api_url="https://www.workato.com",
            project_name="EnvProject",
        )

        # Verify profile was created
        mock_profile_manager.set_profile.assert_called_once()
        call_args = mock_profile_manager.set_profile.call_args
        profile_name, profile_data, token = call_args[0]

        assert profile_name == "env-profile"
        assert token == "env-token-ni"
        assert profile_data.region == "us"

    @pytest.mark.asyncio
    async def test_setup_non_interactive_detects_eu_from_env(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Non-interactive mode should detect EU region from WORKATO_HOST."""
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token-eu")
        monkeypatch.setenv("WORKATO_HOST", "https://app.eu.workato.com")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        mock_profile_manager.resolve_environment_variables.return_value = (None, None)
        mock_profile_manager.get_current_profile_name.return_value = "eu-profile"
        mock_profile_manager.get_profile.return_value = None  # No existing profile

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path)
        monkeypatch.chdir(tmp_path)

        await manager._setup_non_interactive(
            profile_name="eu-profile",
            api_token="env-token-eu",
            api_url="https://app.eu.workato.com",
            project_name="EuProject",
        )

        # Verify EU region was detected
        mock_profile_manager.set_profile.assert_called_once()
        call_args = mock_profile_manager.set_profile.call_args
        profile_name, profile_data, token = call_args[0]

        assert profile_name == "eu-profile"
        assert profile_data.region == "eu"
        assert profile_data.region_url == "https://app.eu.workato.com"

    @pytest.mark.asyncio
    async def test_setup_profile_with_both_env_vars_user_accepts_new_profile(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When both env vars detected and user accepts, profile should use env vars."""
        # Setup environment variables
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token-123")
        monkeypatch.setenv("WORKATO_HOST", "https://www.workato.com")

        # Setup stubs and mocks
        monkeypatch.setattr(ConfigManager.__module__ + ".Workato", StubWorkato)

        # Mock that no profiles exist yet
        mock_profile_manager.list_profiles.return_value = {}

        # Mock user confirms using env vars
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda message, **k: True,
        )

        # Mock profile name prompt (message is "Enter profile name")
        prompt_responses = {"Enter profile name": "test-env-profile"}

        async def fake_prompt(message: str, **kwargs: Any) -> str:
            return prompt_responses.get(message, "default")

        monkeypatch.setattr(ConfigManager.__module__ + ".click.prompt", fake_prompt)

        # Capture outputs
        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        # Execute method under test
        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        profile_name = await manager._setup_profile()

        # Assertions
        assert profile_name == "test-env-profile"

        # Verify env vars were detected and shown to user
        assert any(
            "✓ Found WORKATO_API_TOKEN in environment" in output for output in outputs
        )
        assert any(
            "✓ Found WORKATO_HOST in environment" in output for output in outputs
        )

        # Verify profile was created with env var credentials
        mock_profile_manager.set_profile.assert_called_once()
        call_args = mock_profile_manager.set_profile.call_args
        created_profile_name, profile_data, token = call_args[0]

        assert created_profile_name == "test-env-profile"
        assert token == "env-token-123"
        assert profile_data.region == "us"
        assert profile_data.region_url == "https://www.workato.com"

        # Verify profile was set as current
        mock_profile_manager.set_current_profile.assert_called_once_with(
            "test-env-profile"
        )

    @pytest.mark.asyncio
    async def test_setup_profile_with_env_vars_user_declines(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When env vars detected but user declines, should follow normal flow."""
        # Setup environment variables
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token-decline")
        monkeypatch.setenv("WORKATO_HOST", "https://www.workato.com")

        # Setup stubs and mocks
        monkeypatch.setattr(ConfigManager.__module__ + ".Workato", StubWorkato)

        # Mock that profiles exist
        mock_profile_manager.list_profiles.return_value = {
            "default": ProfileData(
                region="us",
                region_url="https://www.workato.com",
                workspace_id=1,
            )
        }

        # Mock user DECLINES using env vars
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda message, **k: False,
        )

        # Mock inquirer.prompt for profile selection (normal flow)
        def fake_inquirer_prompt(questions: list[Any]) -> dict[str, str]:
            # User selects existing profile in normal flow
            return {"profile_choice": "default"}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_inquirer_prompt,
        )

        # Capture outputs
        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        # Execute method under test
        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        profile_name = await manager._setup_profile()

        # Assertions
        assert profile_name == "default"

        # Verify env vars were detected
        assert any(
            "✓ Found WORKATO_API_TOKEN in environment" in output for output in outputs
        )

        # Verify profile was NOT created with env vars (normal flow was followed)
        # The set_profile should not have been called for env vars
        # Instead, set_current_profile should be called for existing profile
        mock_profile_manager.set_current_profile.assert_called_once_with("default")

    @pytest.mark.asyncio
    async def test_setup_profile_with_only_token_prompts_for_region(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When only WORKATO_API_TOKEN set, should prompt for region selection."""
        # Setup only token env var (no host)
        monkeypatch.setenv("WORKATO_API_TOKEN", "token-only")

        # Setup stubs and mocks
        monkeypatch.setattr(ConfigManager.__module__ + ".Workato", StubWorkato)

        # Mock that no profiles exist yet
        mock_profile_manager.list_profiles.return_value = {}

        # Mock user confirms using env vars
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda message, **k: True,
        )

        # Mock profile name prompt (message is "Enter profile name")
        prompt_responses = {"Enter profile name": "token-only-profile"}

        async def fake_prompt(message: str, **kwargs: Any) -> str:
            return prompt_responses.get(message, "default")

        monkeypatch.setattr(ConfigManager.__module__ + ".click.prompt", fake_prompt)

        # Mock region selection (since no host provided)
        from workato_platform_cli.cli.utils.config.models import RegionInfo

        region_selected = False

        async def mock_select_region() -> RegionInfo:
            nonlocal region_selected
            region_selected = True
            return RegionInfo(
                region="us",
                name="United States",
                url="https://www.workato.com",
            )

        mock_profile_manager.select_region_interactive = mock_select_region

        # Capture outputs
        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        # Execute method under test
        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        profile_name = await manager._setup_profile()

        # Assertions
        assert profile_name == "token-only-profile"

        # Verify only token was detected (not host)
        assert any(
            "✓ Found WORKATO_API_TOKEN in environment" in output for output in outputs
        )
        assert not any(
            "✓ Found WORKATO_HOST in environment" in output for output in outputs
        )

        # Verify missing host message was shown
        assert any(
            "✗ WORKATO_HOST not found - will prompt for region" in output
            for output in outputs
        )

        # Verify region was prompted
        assert region_selected

        # Verify profile was created
        mock_profile_manager.set_profile.assert_called_once()
        call_args = mock_profile_manager.set_profile.call_args
        created_profile_name, profile_data, token = call_args[0]

        assert created_profile_name == "token-only-profile"
        assert token == "token-only"
        assert profile_data.region == "us"

    @pytest.mark.asyncio
    async def test_setup_profile_with_only_host_prompts_for_token(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When only WORKATO_HOST set, should prompt for token input."""
        # Setup only host env var (no token)
        monkeypatch.setenv("WORKATO_HOST", "https://app.eu.workato.com")

        # Setup stubs and mocks
        monkeypatch.setattr(ConfigManager.__module__ + ".Workato", StubWorkato)

        # Mock that no profiles exist yet
        mock_profile_manager.list_profiles.return_value = {}

        # Mock user confirms using env vars
        confirm_calls = []

        def fake_confirm(message: str, **kwargs: Any) -> bool:
            confirm_calls.append(message)
            return True

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            fake_confirm,
        )

        # Mock prompts for both profile name and token
        token_prompted = False
        prompt_responses = {
            "Enter profile name": "host-only-profile",
            "Enter your Workato API token": "prompted-token-456",
        }

        async def fake_prompt(message: str, **kwargs: Any) -> str:
            nonlocal token_prompted
            if "API token" in message:
                token_prompted = True
            return prompt_responses.get(message, "default")

        monkeypatch.setattr(ConfigManager.__module__ + ".click.prompt", fake_prompt)

        # Capture outputs
        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        # Execute method under test
        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        profile_name = await manager._setup_profile()

        # Assertions
        assert profile_name == "host-only-profile"

        # Verify only host was detected (not token)
        assert any(
            "✓ Found WORKATO_HOST in environment (EU Data Center)" in output
            for output in outputs
        )
        assert not any(
            "✓ Found WORKATO_API_TOKEN in environment" in output for output in outputs
        )

        # Verify missing token message was shown
        assert any(
            "✗ WORKATO_API_TOKEN not found - will prompt for token" in output
            for output in outputs
        )

        # Verify token was prompted
        assert token_prompted

        # Verify profile was created with prompted token and env host
        mock_profile_manager.set_profile.assert_called_once()
        call_args = mock_profile_manager.set_profile.call_args
        created_profile_name, profile_data, token = call_args[0]

        assert created_profile_name == "host-only-profile"
        assert token == "prompted-token-456"
        assert profile_data.region == "eu"
        assert profile_data.region_url == "https://app.eu.workato.com"

    @pytest.mark.asyncio
    async def test_select_profile_name_overwrites_existing_with_confirmation(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When existing profile selected and user confirms, should overwrite."""
        # Setup environment variables
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token-overwrite")
        monkeypatch.setenv("WORKATO_HOST", "https://www.workato.com")

        # Setup stubs and mocks
        monkeypatch.setattr(ConfigManager.__module__ + ".Workato", StubWorkato)

        # Mock that profiles exist
        mock_profile_manager.list_profiles.return_value = {
            "dev": ProfileData(
                region="us",
                region_url="https://www.workato.com",
                workspace_id=1,
            ),
            "prod": ProfileData(
                region="us",
                region_url="https://www.workato.com",
                workspace_id=2,
            ),
        }

        # Track confirm calls to verify both prompts
        confirm_calls: list[str] = []

        def fake_confirm(message: str, **kwargs: Any) -> bool:
            confirm_calls.append(message)
            return True  # User accepts both times

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            fake_confirm,
        )

        # Mock inquirer to select existing profile
        def fake_inquirer_prompt(questions: list[Any]) -> dict[str, str]:
            message = questions[0].message
            if "Select a profile name" in message:
                # Select existing profile "dev"
                return {"profile_choice": "dev"}
            return {}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_inquirer_prompt,
        )

        # Capture outputs
        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        # Execute method under test
        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        profile_name = await manager._setup_profile()

        # Assertions
        assert profile_name == "dev"

        # Verify both confirm prompts were called
        assert len(confirm_calls) == 2
        assert "Use environment variables for authentication?" in confirm_calls[0]
        assert "Continue?" in confirm_calls[1]

        # Verify overwrite warning was shown
        assert any(
            "⚠️" in output and "overwrite" in output.lower() for output in outputs
        )

        # Verify profile was created/overwritten
        mock_profile_manager.set_profile.assert_called_once()
        call_args = mock_profile_manager.set_profile.call_args
        created_profile_name, profile_data, token = call_args[0]

        assert created_profile_name == "dev"
        assert token == "env-token-overwrite"

    @pytest.mark.asyncio
    async def test_select_profile_name_cancels_on_overwrite_decline(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When existing profile selected but user declines overwrite, should exit."""
        # Setup environment variables
        monkeypatch.setenv("WORKATO_API_TOKEN", "env-token-cancel")
        monkeypatch.setenv("WORKATO_HOST", "https://www.workato.com")

        # Setup stubs and mocks
        monkeypatch.setattr(ConfigManager.__module__ + ".Workato", StubWorkato)

        # Mock that profiles exist
        mock_profile_manager.list_profiles.return_value = {
            "dev": ProfileData(
                region="us",
                region_url="https://www.workato.com",
                workspace_id=1,
            ),
            "prod": ProfileData(
                region="us",
                region_url="https://www.workato.com",
                workspace_id=2,
            ),
        }

        # Track confirm calls - accept env vars, but decline overwrite
        confirm_calls: list[str] = []

        def fake_confirm(message: str, **kwargs: Any) -> bool:
            confirm_calls.append(message)
            if "Use environment variables" in message:
                return True  # Accept using env vars
            elif "Continue?" in message:
                return False  # Decline overwrite
            return True

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            fake_confirm,
        )

        # Mock inquirer to select existing profile
        def fake_inquirer_prompt(questions: list[Any]) -> dict[str, str]:
            message = questions[0].message
            if "Select a profile name" in message:
                # Select existing profile "dev"
                return {"profile_choice": "dev"}
            return {}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_inquirer_prompt,
        )

        # Capture outputs
        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        # Execute method under test - should raise SystemExit
        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        with pytest.raises(SystemExit):
            await manager._setup_profile()

        # Verify both confirm prompts were called
        assert len(confirm_calls) == 2
        assert "Use environment variables for authentication?" in confirm_calls[0]
        assert "Continue?" in confirm_calls[1]

        # Verify overwrite warning was shown
        assert any(
            "⚠️" in output and "overwrite" in output.lower() for output in outputs
        )

        # Verify profile was NOT created (user cancelled)
        mock_profile_manager.set_profile.assert_not_called()

    def test_init_with_explicit_config_dir(self, tmp_path: Path) -> None:
        """Test ConfigManager respects explicit config_dir."""
        config_dir = tmp_path / "explicit"
        config_dir.mkdir()

        config_manager = ConfigManager(config_dir=config_dir, skip_validation=True)
        assert config_manager.config_dir == config_dir

    def test_init_without_config_dir_finds_nearest(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Test ConfigManager finds nearest .workatoenv when no config_dir provided."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".workatoenv").write_text('{"project_id": 123}')

        monkeypatch.chdir(project_dir)
        config_manager = ConfigManager(skip_validation=True)
        assert config_manager.config_dir == project_dir

    def test_load_config_success(self, tmp_path: Path) -> None:
        """Test loading valid config file."""
        config_file = tmp_path / ".workatoenv"
        config_data = {
            "project_id": 123,
            "project_name": "test",
            "folder_id": 456,
            "profile": "dev",
        }
        config_file.write_text(json.dumps(config_data))

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        loaded_config = config_manager.load_config()

        assert loaded_config.project_id == 123
        assert loaded_config.project_name == "test"
        assert loaded_config.folder_id == 456
        assert loaded_config.profile == "dev"

    def test_load_config_missing_file(self, tmp_path: Path) -> None:
        """Test loading config when file doesn't exist."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        loaded_config = config_manager.load_config()

        assert loaded_config.project_id is None
        assert loaded_config.project_name is None

    def test_load_config_invalid_json(self, tmp_path: Path) -> None:
        """Test loading config with invalid JSON."""
        config_file = tmp_path / ".workatoenv"
        config_file.write_text("invalid json")

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        loaded_config = config_manager.load_config()

        # Should return empty config
        assert loaded_config.project_id is None

    def test_save_config(self, tmp_path: Path) -> None:
        """Test saving config to file."""
        config_data = ConfigData(project_id=123, project_name="test", folder_id=456)

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        config_manager.save_config(config_data)

        config_file = tmp_path / ".workatoenv"
        assert config_file.exists()

        with open(config_file) as f:
            saved_data = json.load(f)

        assert saved_data["project_id"] == 123
        assert saved_data["project_name"] == "test"
        assert saved_data["folder_id"] == 456
        assert "project_path" not in saved_data  # None values excluded

    def test_save_project_info(self, tmp_path: Path) -> None:
        """Test saving project info updates config."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        project_info = ProjectInfo(id=123, name="test", folder_id=456)
        config_manager.save_project_info(project_info)

        loaded_config = config_manager.load_config()
        assert loaded_config.project_id == 123
        assert loaded_config.project_name == "test"
        assert loaded_config.folder_id == 456

    def test_get_workspace_root(self, tmp_path: Path) -> None:
        """Test get_workspace_root returns workspace root."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "project"
        project_dir.mkdir(parents=True)

        # Create workspace config
        (workspace_root / ".workatoenv").write_text(
            '{"project_path": "project", "project_id": 123}'
        )

        config_manager = ConfigManager(config_dir=project_dir, skip_validation=True)
        result = config_manager.get_workspace_root()
        assert result == workspace_root

    def test_get_project_directory_from_workspace_config(self, tmp_path: Path) -> None:
        """Test get_project_directory with workspace config."""
        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "project"
        project_dir.mkdir(parents=True)

        # Create workspace config with project_path
        (workspace_root / ".workatoenv").write_text(
            '{"project_path": "project", "project_id": 123}'
        )

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        result = config_manager.get_project_directory()
        assert result == project_dir.resolve()

    def test_get_project_directory_from_project_config(self, tmp_path: Path) -> None:
        """Test get_project_directory when in project directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Create project config (no project_path)
        (project_dir / ".workatoenv").write_text('{"project_id": 123}')

        with patch.object(ConfigManager, "_update_workspace_selection"):
            config_manager = ConfigManager(config_dir=project_dir, skip_validation=True)
            result = config_manager.get_project_directory()
            assert result == project_dir

    def test_get_project_directory_none_when_no_project(self, tmp_path: Path) -> None:
        """Test get_project_directory returns None when no project configured."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        result = config_manager.get_project_directory()
        assert result is None

    def test_get_current_project_name(self, tmp_path: Path) -> None:
        """Test get_current_project_name returns project name."""
        config_data = ConfigData(project_name="test-project")

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        config_manager.save_config(config_data)

        result = config_manager.get_current_project_name()
        assert result == "test-project"

    def test_get_project_root_compatibility(self, tmp_path: Path) -> None:
        """Test get_project_root for backward compatibility."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".workatoenv").write_text('{"project_id": 123}')

        config_manager = ConfigManager(config_dir=project_dir, skip_validation=True)
        result = config_manager.get_project_root()
        assert result == project_dir

    def test_is_in_project_workspace(self, tmp_path: Path) -> None:
        """Test is_in_project_workspace detection."""
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / ".workatoenv").write_text(
            '{"project_path": "project", "project_id": 123}'
        )

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        assert config_manager.is_in_project_workspace() is True

    def test_validate_environment_config(self, tmp_path: Path) -> None:
        """Test environment config validation."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock the profile manager after creation
        with patch.object(
            config_manager.profile_manager,
            "validate_credentials",
            return_value=(True, []),
        ):
            is_valid, missing = config_manager.validate_environment_config()

            assert is_valid is True
            assert missing == []

    def test_api_token_property(self, tmp_path: Path) -> None:
        """Test api_token property."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock the profile manager after creation
        with patch.object(
            config_manager.profile_manager,
            "resolve_environment_variables",
            return_value=("test-token", "https://test.com"),
        ):
            assert config_manager.api_token == "test-token"

    def test_api_token_setter_success(
        self, tmp_path: Path, mock_profile_manager: Mock
    ) -> None:
        """Token setter should store token via profile manager."""

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Customize the mock for this test
        mock_profile_manager.get_current_profile_name.return_value = "dev"

        config_manager.profile_manager = mock_profile_manager
        config_manager.save_config(ConfigData(profile="dev"))

        config_manager.api_token = "new-token"

        # Verify the token was stored
        mock_profile_manager._store_token_in_keyring.assert_called_with(
            "dev", "new-token"
        )

    def test_api_token_setter_keyring_failure(
        self, tmp_path: Path, mock_profile_manager: Mock
    ) -> None:
        """Failure to store token should raise informative error."""

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Customize the mock for keyring failure
        mock_profile_manager.get_current_profile_name.return_value = "dev"
        mock_profile_manager._store_token_in_keyring.return_value = False
        mock_profile_manager._is_keyring_enabled.return_value = True

        config_manager.profile_manager = mock_profile_manager
        config_manager.save_config(ConfigData(profile="dev"))

        with pytest.raises(ValueError) as excinfo:
            config_manager.api_token = "new-token"
        assert "Failed to store token" in str(excinfo.value)

        # Test keyring disabled case
        mock_profile_manager._is_keyring_enabled.return_value = False
        with pytest.raises(ValueError) as excinfo2:
            config_manager.api_token = "new-token"
        assert "Keyring is disabled" in str(excinfo2.value)

    def test_validate_region_and_set_region(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Region helpers should validate and persist settings."""

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock the profile manager methods properly
        profiles_mock = Mock()
        profiles_mock.profiles = {
            "dev": ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            )
        }
        mock_profile_manager.load_profiles.return_value = profiles_mock
        mock_profile_manager.get_current_profile_name.return_value = "dev"
        mock_profile_manager.save_profiles = Mock()

        config_manager.profile_manager = mock_profile_manager
        config_manager.save_config(ConfigData(profile="dev"))

        from urllib.parse import urlparse

        monkeypatch.setattr(
            ConfigManager.__module__ + ".urlparse",
            urlparse,
            raising=False,
        )

        assert config_manager.validate_region("us") is True
        success, _ = config_manager.set_region("us")
        assert success is True

        success_custom, message = config_manager.set_region(
            "custom", custom_url="https://custom.workato.test"
        )
        assert success_custom is True
        assert "custom" in message

        success_invalid, message_invalid = config_manager.set_region("xx")
        assert success_invalid is False
        assert "Invalid region" in message_invalid

        success_missing_url, message_missing = config_manager.set_region("custom")
        assert success_missing_url is False
        assert "requires a URL" in message_missing

    def test_set_region_url_validation(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Custom region should reject insecure URLs."""

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock the profile manager methods properly
        profiles_mock = Mock()
        profiles_mock.profiles = {
            "dev": ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            )
        }
        mock_profile_manager.load_profiles.return_value = profiles_mock
        mock_profile_manager.get_current_profile_name.return_value = "dev"

        config_manager.profile_manager = mock_profile_manager
        config_manager.save_config(ConfigData(profile="dev"))

        from urllib.parse import urlparse

        monkeypatch.setattr(
            ConfigManager.__module__ + ".urlparse",
            urlparse,
            raising=False,
        )

        success, message = config_manager.set_region("custom", custom_url="ftp://bad")
        assert success is False
        assert "URL must" in message

    def test_api_host_property(
        self, tmp_path: Path, mock_profile_manager: Mock
    ) -> None:
        """api_host should read host from profile manager."""

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        mock_profile_manager.resolve_environment_variables.return_value = (
            "token",
            "https://example.com",
        )

        config_manager.profile_manager = mock_profile_manager
        config_manager.save_config(ConfigData(profile="dev"))

        assert config_manager.api_host == "https://example.com"

    def test_create_workspace_files(self, tmp_path: Path) -> None:
        """Workspace helper should create ignore files."""

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/", encoding="utf-8")

        config_manager._create_workspace_files(tmp_path)

        gitignore_content = gitignore.read_text(encoding="utf-8")
        workato_ignore = (tmp_path / ".workato-ignore").read_text(encoding="utf-8")

        assert gitignore_content.endswith("\n")
        assert ".workatoenv" in gitignore_content
        assert "# Workato CLI ignore patterns" in workato_ignore

    def test_update_workspace_selection(self, tmp_path: Path) -> None:
        """Selecting a project should update workspace .workatoenv."""

        workspace_root = tmp_path / "workspace"
        project_dir = workspace_root / "projects" / "Demo"
        project_dir.mkdir(parents=True)

        workspace_root.mkdir(exist_ok=True)
        (workspace_root / ".workatoenv").write_text(
            json.dumps({"project_path": "projects/demo"}),
            encoding="utf-8",
        )

        project_config = {
            "project_id": 123,
            "project_name": "Demo",
            "folder_id": 55,
            "profile": "dev",
        }
        (project_dir / ".workatoenv").write_text(
            json.dumps(project_config), encoding="utf-8"
        )

        config_manager = ConfigManager(config_dir=project_dir, skip_validation=True)
        config_manager._update_workspace_selection()

        updated = json.loads(
            (workspace_root / ".workatoenv").read_text(encoding="utf-8")
        )
        assert updated["project_name"] == "Demo"
        assert updated["project_id"] == 123

    def test_update_workspace_selection_no_workspace(self, tmp_path: Path) -> None:
        """No workspace root should result in no changes."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.workspace_manager = WorkspaceManager(start_path=None)
        manager._update_workspace_selection()

    def test_update_workspace_selection_no_project_id(self, tmp_path: Path) -> None:
        """Missing project metadata should abort update."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.workspace_manager = WorkspaceManager(start_path=tmp_path.parent)
        with patch.object(manager, "load_config", return_value=ConfigData()):
            manager._update_workspace_selection()

    def test_update_workspace_selection_outside_workspace(self, tmp_path: Path) -> None:
        """Projects outside workspace should be ignored."""

        manager = ConfigManager(
            config_dir=tmp_path / "outside" / "project", skip_validation=True
        )
        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        manager.workspace_manager = WorkspaceManager(start_path=workspace_root)
        with patch.object(
            manager,
            "load_config",
            return_value=ConfigData(
                project_id=1,
                project_name="Demo",
                folder_id=2,
                profile="dev",
            ),
        ):
            manager._update_workspace_selection()

    def test_handle_invalid_project_selection_returns_none(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When no projects exist, handler returns None."""

        workspace_root = tmp_path

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        result = config_manager._handle_invalid_project_selection(
            workspace_root, ConfigData(project_path="missing", project_name="Missing")
        )
        assert result is None
        assert any("No projects found" in msg for msg in outputs)

    def test_handle_invalid_project_selection_choose_project(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """User selection should update workspace config with chosen project."""

        workspace_root = tmp_path
        available = workspace_root / "proj"
        available.mkdir()
        (available / ".workatoenv").write_text(
            json.dumps(
                {
                    "project_id": 200,
                    "project_name": "Chosen",
                    "folder_id": 9,
                }
            ),
            encoding="utf-8",
        )

        (workspace_root / ".workatoenv").write_text("{}", encoding="utf-8")

        def fake_prompt(questions: list[Any]) -> dict[str, str]:
            assert questions[0].message == "Select a project to use"
            return {"project": "Chosen (proj)"}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_prompt,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        selected = config_manager._handle_invalid_project_selection(
            workspace_root,
            ConfigData(project_path="missing", project_name="Missing"),
        )

        assert selected == available
        workspace_data = json.loads(
            (workspace_root / ".workatoenv").read_text(encoding="utf-8")
        )
        assert workspace_data["project_name"] == "Chosen"
        assert any("Selected 'Chosen'" in msg for msg in outputs)

    def test_handle_invalid_project_selection_no_answers(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If user cancels selection, None should be returned."""

        workspace_root = tmp_path
        available = workspace_root / "proj"
        available.mkdir()
        (available / ".workatoenv").write_text(
            json.dumps({"project_id": 1, "project_name": "Proj"}),
            encoding="utf-8",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: None,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        result = manager._handle_invalid_project_selection(
            workspace_root,
            ConfigData(project_path="missing", project_name="Missing"),
        )
        assert result is None

    def test_handle_invalid_project_selection_keyboard_interrupt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """KeyboardInterrupt should be handled gracefully."""

        workspace_root = tmp_path
        available = workspace_root / "proj"
        available.mkdir()
        (available / ".workatoenv").write_text(
            json.dumps({"project_id": 1, "project_name": "Proj"}),
            encoding="utf-8",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: (_ for _ in ()).throw(KeyboardInterrupt()),
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        result = manager._handle_invalid_project_selection(
            workspace_root,
            ConfigData(project_path="missing", project_name="Missing"),
        )
        assert result is None

    def test_find_all_projects(self, tmp_path: Path) -> None:
        """find_all_projects should discover projects with configs."""

        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        (workspace_root / "a").mkdir()
        (workspace_root / "b").mkdir()
        (workspace_root / "a" / ".workatoenv").write_text(
            json.dumps({"project_id": 1, "project_name": "Alpha"}),
            encoding="utf-8",
        )
        (workspace_root / "b" / ".workatoenv").write_text(
            json.dumps({"project_id": 2, "project_name": "Beta"}),
            encoding="utf-8",
        )
        (workspace_root / "c").mkdir()
        (workspace_root / "c" / ".workatoenv").write_text("invalid", encoding="utf-8")

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        projects = config_manager._find_all_projects(workspace_root)

        assert projects == [
            (workspace_root / "a", "Alpha"),
            (workspace_root / "b", "Beta"),
        ]

    def test_get_project_directory_handles_missing_selection(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When project path invalid, selection helper should run."""

        workspace_root = tmp_path
        (workspace_root / ".workatoenv").write_text(
            json.dumps(
                {
                    "project_id": 1,
                    "project_name": "Missing",
                    "project_path": "missing",
                }
            ),
            encoding="utf-8",
        )

        available = workspace_root / "valid"
        available.mkdir()
        (available / ".workatoenv").write_text(
            json.dumps({"project_id": 1, "project_name": "Valid", "folder_id": 3}),
            encoding="utf-8",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )

        def fake_prompt(questions: list[Any]) -> dict[str, str]:
            if questions[0].message == "Select a project to use":
                return {"project": "Valid (valid)"}
            raise AssertionError(questions[0].message)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_prompt,
        )

        config_manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        project_dir = config_manager.get_project_directory()
        assert project_dir == available.resolve()

    def test_get_project_root_delegates_to_directory(self, tmp_path: Path) -> None:
        """When not in a project directory, get_project_root should reuse lookup."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        with (
            patch.object(
                manager.workspace_manager, "is_in_project_directory", return_value=False
            ),
            patch.object(
                manager, "get_project_directory", return_value=tmp_path / "project"
            ),
        ):
            assert manager.get_project_root() == tmp_path / "project"

    def test_validate_credentials_or_exit_failure(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing credentials should trigger sys.exit."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        with patch.object(manager, "profile_manager", spec=ProfileManager) as mock_pm:
            mock_pm.validate_credentials = Mock(return_value=(False, ["token"]))
            with pytest.raises(SystemExit):
                manager._validate_credentials_or_exit()

    def test_api_token_setter_missing_profile(
        self, tmp_path: Path, mock_profile_manager: Mock
    ) -> None:
        """Setting a token when the profile is missing should raise."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock to return empty profiles (missing profile)
        profiles_mock = Mock()
        profiles_mock.profiles = {}  # Empty profiles dict
        mock_profile_manager.load_profiles.return_value = profiles_mock
        mock_profile_manager.get_current_profile_name.return_value = "dev"

        manager.profile_manager = mock_profile_manager
        manager.save_config(ConfigData(profile="dev"))

        with pytest.raises(ValueError):
            manager.api_token = "token"

    def test_api_token_setter_uses_default_profile(
        self, tmp_path: Path, mock_profile_manager: Mock
    ) -> None:
        """Default profile should be assumed when none stored."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock for default profile case
        profiles_mock = Mock()
        profiles_mock.profiles = {
            "default": ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            )
        }
        mock_profile_manager.load_profiles.return_value = profiles_mock
        mock_profile_manager.get_current_profile_name.return_value = "default"
        mock_profile_manager._store_token_in_keyring.return_value = True
        mock_profile_manager.tokens = {"default": "old"}

        manager.profile_manager = mock_profile_manager
        manager.save_config(ConfigData(profile=None))

        manager.api_token = "new-token"
        mock_profile_manager._store_token_in_keyring.assert_called_with(
            "default", "new-token"
        )

    def test_set_region_missing_profile(
        self, tmp_path: Path, mock_profile_manager: Mock
    ) -> None:
        """set_region should report failure when no matching profile exists."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock to return empty profiles (missing profile)
        profiles_mock = Mock()
        profiles_mock.profiles = {}  # Empty profiles dict
        mock_profile_manager.load_profiles.return_value = profiles_mock
        mock_profile_manager.get_current_profile_name.return_value = "dev"

        manager.profile_manager = mock_profile_manager
        manager.save_config(ConfigData(profile="dev"))

        success, message = manager.set_region("us")
        assert success is False
        assert "does not exist" in message

    def test_set_region_uses_default_profile(
        self, tmp_path: Path, mock_profile_manager: Mock
    ) -> None:
        """Fallback to default profile should be supported."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        # Mock for default profile case
        profiles_mock = Mock()
        profiles_mock.profiles = {
            "default": ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            )
        }
        mock_profile_manager.load_profiles.return_value = profiles_mock
        mock_profile_manager.get_current_profile_name.return_value = "default"
        mock_profile_manager.save_profiles = Mock()

        manager.profile_manager = mock_profile_manager
        manager.save_config(ConfigData(profile=None))

        success, message = manager.set_region("us")
        assert success is True
        assert "US Data Center" in message

    @pytest.mark.asyncio
    async def test_setup_profile_and_project_new_flow(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Cover happy path for profile setup and project creation."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        prompt_answers = {
            "Enter profile name": ["dev"],
            "Enter your Workato API token": ["token-123"],
            "Enter project name": ["DemoProject"],
        }

        async def fake_prompt(message: str, **_: object) -> str:
            values = prompt_answers.get(message)
            assert values, f"Unexpected prompt: {message}"
            return values.pop(0)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda *a, **k: True,
        )

        def fake_inquirer_prompt(questions: list[Any]) -> dict[str, str]:
            message = questions[0].message
            if message == "Select your Workato region":
                return {"region": questions[0].choices[0]}
            if message == "Select a project":
                return {"project": "Create new project"}
            if message == "Select a profile":
                return {"profile_choice": "dev"}
            raise AssertionError(f"Unexpected prompt message: {message}")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_inquirer_prompt,
        )

        monkeypatch.chdir(tmp_path)
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        profile_name = await config_manager._setup_profile()
        await config_manager._setup_project(profile_name, tmp_path)
        config_manager._create_workspace_files(tmp_path)

        project_env = tmp_path / "DemoProject" / ".workatoenv"
        assert profile_name == "dev"
        assert project_env.exists()
        assert ".workatoenv" in (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert (tmp_path / ".workato-ignore").exists()

    @pytest.mark.asyncio
    async def test_setup_profile_requires_selection(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Missing selection should abort setup."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        mock_profile_manager.set_profile(
            "existing",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )
        manager.profile_manager = mock_profile_manager

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: None,
        )

        with pytest.raises(SystemExit):
            await manager._setup_profile()

    @pytest.mark.asyncio
    async def test_setup_profile_rejects_blank_new_profile(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Entering an empty profile name should exit."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        mock_profile_manager.set_profile(
            "existing",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )
        manager.profile_manager = mock_profile_manager

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: {"profile_choice": "Create new profile"},
        )

        async def mock_prompt(message: str, **_: Any) -> str:
            return " " if "profile name" in message else "value"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            mock_prompt,
        )

        with pytest.raises(SystemExit):
            await manager._setup_profile()

    @pytest.mark.asyncio
    async def test_setup_profile_requires_nonempty_first_prompt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Initial profile prompt must not be empty."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: None,
        )

        async def mock_prompt2(message: str, **_: Any) -> str:
            return " " if "Enter profile name" in message else "value"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            mock_prompt2,
        )

        with pytest.raises(SystemExit):
            await manager._setup_profile()

    @pytest.mark.asyncio
    async def test_setup_profile_with_existing_choice(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Existing profiles branch should select the chosen profile."""

        mock_profile_manager.set_profile(
            "existing",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "existing-token",
        )
        mock_profile_manager.set_current_profile("existing")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        def fake_inquirer_prompt(questions: list[Any]) -> dict[str, str]:
            assert questions[0].message == "Select a profile"
            return {"profile_choice": "existing"}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_inquirer_prompt,
        )

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        profile_name = await config_manager._setup_profile()
        assert profile_name == "existing"
        assert any("Profile:" in line for line in outputs)

    @pytest.mark.asyncio
    async def test_setup_profile_existing_with_valid_credentials(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Existing profile with valid credentials should not prompt for re-entry."""

        mock_profile_manager.set_profile(
            "existing",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "existing-token",
        )
        mock_profile_manager.set_current_profile("existing")

        # Mock _get_token_from_keyring to return valid token
        mock_profile_manager._get_token_from_keyring.return_value = "existing-token"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        def fake_inquirer_prompt(questions: list[Any]) -> dict[str, str]:
            assert questions[0].message == "Select a profile"
            return {"profile_choice": "existing"}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_inquirer_prompt,
        )

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        profile_name = await config_manager._setup_profile()
        assert profile_name == "existing"
        assert any("Profile:" in line for line in outputs)
        # Should not show credential warning
        assert not any("Credentials not found" in line for line in outputs)

    @pytest.mark.asyncio
    async def test_setup_profile_existing_with_missing_credentials(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Existing profile with missing credentials should prompt for re-entry."""

        existing_profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=1
        )
        mock_profile_manager.set_profile("existing", existing_profile, None)
        mock_profile_manager.set_current_profile("existing")

        # Mock _get_token_from_keyring to return None (missing credentials)
        mock_profile_manager._get_token_from_keyring.return_value = None

        # Mock get_profile to return the existing profile
        mock_profile_manager.get_profile.return_value = existing_profile

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        prompt_answers = {
            "Enter your Workato API token": ["new-token"],
        }

        async def fake_prompt(
            text: str, type: Any = None, hide_input: bool = False
        ) -> Any:
            return prompt_answers.get(text, [""])[0]

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )

        def fake_inquirer_prompt(questions: list[Any]) -> dict[str, str]:
            assert questions[0].message == "Select a profile"
            return {"profile_choice": "existing"}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_inquirer_prompt,
        )

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        profile_name = await config_manager._setup_profile()
        assert profile_name == "existing"

        # Should show credential warning
        assert any("Credentials not found" in line for line in outputs)
        assert any("Enter your API token" in line for line in outputs)

        # Should call set_profile with new credentials
        mock_profile_manager.set_profile.assert_called()

    @pytest.mark.asyncio
    async def test_create_new_profile_custom_region(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Cover custom region handling and token storage."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )

        # Mock select_region_interactive to return a custom region
        from workato_platform_cli.cli.utils.config.models import RegionInfo

        async def mock_select_region() -> RegionInfo:
            return RegionInfo(
                region="custom",
                name="Custom URL",
                url="https://custom.workato.test",
            )

        mock_profile_manager.select_region_interactive = mock_select_region

        prompt_answers = {
            "Enter your Workato API token": ["custom-token"],
        }

        async def fake_prompt(message: str, **_: Any) -> str:
            values = prompt_answers.get(message)
            assert values, f"Unexpected prompt: {message}"
            return values.pop(0)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        await config_manager._create_new_profile("custom")

        # Verify the profile was created with correct parameters
        mock_profile_manager.set_profile.assert_called_once()
        call_args = mock_profile_manager.set_profile.call_args
        profile_name, profile_data, token = call_args[0]

        assert profile_name == "custom"
        assert profile_data.region == "custom"
        assert profile_data.region_url == "https://custom.workato.test"
        assert token == "custom-token"

    @pytest.mark.asyncio
    async def test_create_new_profile_cancelled(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """User cancellation at region prompt should exit."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        # Mock select_region_interactive to return None (cancelled)
        async def mock_select_region_cancelled() -> None:
            return None

        mock_profile_manager.select_region_interactive = mock_select_region_cancelled

        with pytest.raises(SystemExit):
            await manager._create_new_profile("dev")

    @pytest.mark.asyncio
    async def test_create_new_profile_requires_token(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Blank token should abort profile creation."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: {"region": "US Data Center (https://www.workato.com)"},
        )

        async def fake_prompt(message: str, **_: Any) -> str:
            if "API token" in message:
                return "   "
            return "unused"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )

        with pytest.raises(click.ClickException, match="API token cannot be empty"):
            await manager._create_new_profile("dev")

    @pytest.mark.asyncio
    async def test_prompt_and_validate_credentials_success(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Test successful credential prompt and validation."""
        from workato_platform_cli.cli.utils.config.models import RegionInfo

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )

        async def fake_prompt(message: str, **_: Any) -> str:
            if "API token" in message:
                return "valid-token-123"
            return "unused"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        region_info = RegionInfo(
            region="us", name="US Data Center", url="https://www.workato.com"
        )
        profile_data, token = await manager._prompt_and_validate_credentials(
            "test-profile", region_info
        )

        assert profile_data.region == "us"
        assert profile_data.region_url == "https://www.workato.com"
        assert profile_data.workspace_id == 101
        assert token == "valid-token-123"
        assert any("Authenticated as" in msg for msg in outputs)

    @pytest.mark.asyncio
    async def test_prompt_and_validate_credentials_empty_token(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Test that empty token raises ClickException."""
        from workato_platform_cli.cli.utils.config.models import RegionInfo

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        async def fake_prompt(message: str, **_: Any) -> str:
            if "API token" in message:
                return "   "  # Empty/whitespace token
            return "unused"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        region_info = RegionInfo(
            region="us", name="US Data Center", url="https://www.workato.com"
        )

        with pytest.raises(click.ClickException) as excinfo:
            await manager._prompt_and_validate_credentials("test-profile", region_info)

        assert "token cannot be empty" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_prompt_and_validate_credentials_api_failure(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Test that API validation failure raises appropriate exception."""
        from workato_platform_cli.cli.utils.config.models import RegionInfo

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        # Create a Workato stub that raises an exception
        class FailingWorkato:
            def __init__(self, configuration: Configuration) -> None:
                self.configuration = configuration
                self.users_api = FailingUsersAPI()

            async def __aenter__(self) -> "FailingWorkato":
                return self

            async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
                return None

        class FailingUsersAPI:
            async def get_workspace_details(self) -> User:
                raise Exception("Authentication failed: Invalid token")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            FailingWorkato,
        )

        async def fake_prompt(message: str, **_: Any) -> str:
            if "API token" in message:
                return "invalid-token"
            return "unused"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        region_info = RegionInfo(
            region="us", name="US Data Center", url="https://www.workato.com"
        )

        with pytest.raises(click.ClickException) as excinfo:
            await manager._prompt_and_validate_credentials("test-profile", region_info)

        assert "Authentication failed" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_prompt_and_validate_credentials_keyring_disabled(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Test credential validation returns correct data."""
        from workato_platform_cli.cli.utils.config.models import RegionInfo

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )

        async def fake_prompt(message: str, **_: Any) -> str:
            if "API token" in message:
                return "valid-token-123"
            return "unused"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_prompt,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        region_info = RegionInfo(
            region="us", name="US Data Center", url="https://www.workato.com"
        )
        profile_data, token = await manager._prompt_and_validate_credentials(
            "test-profile", region_info
        )

        assert profile_data.region == "us"
        assert token == "valid-token-123"
        assert any("Authenticated as" in msg for msg in outputs)

    @pytest.mark.asyncio
    async def test_setup_profile_existing_create_new_success(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Choosing 'Create new profile' should call helper and return name."""

        manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        mock_profile_manager.set_profile(
            "existing",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )
        manager.profile_manager = mock_profile_manager

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: {"profile_choice": "Create new profile"},
        )

        async def mock_prompt3(message: str, **_: Any) -> str:
            return "newprofile" if "profile name" in message else "value"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            mock_prompt3,
        )

        create_mock = AsyncMock(return_value=None)
        with patch.object(manager, "_create_new_profile", create_mock):
            profile_name = await manager._setup_profile()
            assert profile_name == "newprofile"
            create_mock.assert_awaited_once_with("newprofile")

    @pytest.mark.asyncio
    async def test_setup_project_selects_existing_remote(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Selecting an existing remote project should configure directories."""

        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        monkeypatch.chdir(workspace_root)

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )
        mock_profile_manager.set_current_profile("dev")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "ExistingProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        def select_project(questions: list[Any]) -> dict[str, str]:
            assert questions[0].message == "Select a project"
            return {"project": "ExistingProj (ID: 42)"}

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            select_project,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        manager.profile_manager = mock_profile_manager

        await manager._setup_project("dev", workspace_root)

        project_dir = workspace_root / "ExistingProj"
        assert project_dir.exists()
        workspace_config = json.loads(
            (workspace_root / ".workatoenv").read_text(encoding="utf-8")
        )
        assert workspace_config["project_name"] == "ExistingProj"

    @pytest.mark.asyncio
    async def test_setup_project_in_subdirectory(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """When running from subdirectory, project should be created there."""

        workspace_root = tmp_path / "workspace"
        nested_dir = workspace_root / "nested"
        nested_dir.mkdir(parents=True)
        monkeypatch.chdir(nested_dir)

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )
        mock_profile_manager.set_current_profile("dev")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        answers = {
            "Select your Workato region": {
                "region": "US Data Center (https://www.workato.com)"
            },
            "Select a project": {"project": "Create new project"},
        }

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: answers[qs[0].message],
        )

        async def mock_prompt4(message: str, **_: Any) -> str:
            return "NestedProj" if message == "Enter project name" else "token"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            mock_prompt4,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        await manager._setup_project("dev", workspace_root)

        assert (nested_dir / "NestedProj").exists()

    @pytest.mark.asyncio
    async def test_setup_project_reconfigures_existing_directory(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Existing matching project should reconfigure without errors."""

        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        monkeypatch.chdir(workspace_root)
        project_dir = workspace_root / "ExistingProj"
        project_dir.mkdir()
        (project_dir / ".workatoenv").write_text(
            json.dumps({"project_id": 42, "project_name": "ExistingProj"}),
            encoding="utf-8",
        )

        mock_profile_manager.list_profiles.return_value = {}
        mock_profile_manager.resolve_environment_variables.return_value = (
            "token",
            "https://www.workato.com",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "ExistingProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: {"project": "ExistingProj (ID: 42)"},
        )

        # User confirms reinitialization when project exists
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda *args, **kwargs: True,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        await manager._setup_project("dev", workspace_root)

        assert any("Reconfiguring existing project" in msg for msg in outputs)

    @pytest.mark.asyncio
    async def test_setup_project_handles_invalid_workatoenv(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Invalid JSON in existing project config should use to blocking logic."""

        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        project = StubProject(42, "ExistingProj", 5)
        StubProjectManager.available_projects = [project]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)

        project_dir = workspace_root / project.name
        project_dir.mkdir()
        workatoenv = project_dir / ".workatoenv"
        workatoenv.write_text("malformed", encoding="utf-8")
        (project_dir / "data.txt").write_text("keep", encoding="utf-8")

        def fake_prompt(questions: list[Any]) -> dict[str, str]:
            assert questions[0].message == "Select a project"
            return {"project": "ExistingProj (ID: 42)"}

        def fake_json_load(_handle: Any) -> None:
            workatoenv.unlink(missing_ok=True)
            raise json.JSONDecodeError("bad", "doc", 0)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_prompt,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".json.load",
            fake_json_load,
        )

        with (
            patch.object(manager, "load_config", return_value=ConfigData()),
            patch.object(manager.workspace_manager, "validate_project_path"),
            patch.object(
                manager.workspace_manager,
                "find_workspace_root",
                return_value=workspace_root,
            ),
        ):
            manager.profile_manager = mock_profile_manager
            with pytest.raises(SystemExit):
                await manager._setup_project("dev", workspace_root)

    @pytest.mark.asyncio
    async def test_setup_project_rejects_conflicting_directory(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Different project ID in directory should raise error."""

        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        monkeypatch.chdir(workspace_root)
        project_dir = workspace_root / "ExistingProj"
        project_dir.mkdir()
        (project_dir / ".workatoenv").write_text(
            json.dumps({"project_id": 99, "project_name": "Other"}),
            encoding="utf-8",
        )

        mock_profile_manager.list_profiles.return_value = {}
        mock_profile_manager.resolve_environment_variables.return_value = (
            "token",
            "https://www.workato.com",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "ExistingProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: {"project": "ExistingProj (ID: 42)"},
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        with pytest.raises(SystemExit):
            await manager._setup_project("dev", workspace_root)

    @pytest.mark.asyncio
    async def test_setup_project_handles_iterdir_oserror(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """OS errors while listing directory contents should be ignored."""

        workspace_root = tmp_path / "workspace"
        workspace_root.mkdir()
        monkeypatch.chdir(workspace_root)

        stub_profile = Mock(spec=ProfileManager)
        stub_profile.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )
        stub_profile.set_current_profile("dev")

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: stub_profile,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        project = StubProject(77, "IterdirProj", 6)
        StubProjectManager.available_projects = [project]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)

        with (
            patch.object(manager, "load_config", return_value=ConfigData()),
            patch.object(manager.workspace_manager, "validate_project_path"),
            patch.object(
                manager.workspace_manager,
                "find_workspace_root",
                return_value=workspace_root,
            ),
        ):
            manager.profile_manager = mock_profile_manager

        project_dir = workspace_root / project.name
        project_dir.mkdir()

        def fake_prompt(questions: list[Any]) -> dict[str, str]:
            return {"project": "IterdirProj (ID: 77)"}

        original_iterdir = Path.iterdir

        def fake_iterdir(self: Path) -> Any:
            if self == project_dir:
                raise OSError("permission denied")
            return original_iterdir(self)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_prompt,
        )
        monkeypatch.setattr(Path, "iterdir", fake_iterdir)

        await manager._setup_project("dev", workspace_root)

        workspace_env = json.loads(
            (workspace_root / ".workatoenv").read_text(encoding="utf-8")
        )
        assert workspace_env["project_name"] == "IterdirProj"

    @pytest.mark.asyncio
    async def test_setup_project_requires_valid_selection(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """If selection is unknown, setup should exit."""

        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "ExistingProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda _questions: {"project": "Unknown"},
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)

        with pytest.raises(SystemExit):
            await manager._setup_project("dev", workspace_root)

    @pytest.mark.asyncio
    async def test_setup_project_path_validation_failure(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Validation errors should abort project setup."""

        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        answers = {
            "Select your Workato region": {
                "region": "US Data Center (https://www.workato.com)"
            },
            "Select a project": {"project": "Create new project"},
        }

        def fake_prompt(questions: list[Any]) -> dict[str, str]:
            return answers[questions[0].message]

        async def fake_click_prompt(message: str, **_: object) -> str:
            if message == "Enter project name":
                return "NewProj"
            if "API token" in message:
                return "token"
            return "value"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            fake_prompt,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            fake_click_prompt,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)

        with (
            patch.object(
                manager.workspace_manager,
                "validate_project_path",
                side_effect=ValueError("bad path"),
            ),
            pytest.raises(SystemExit),
        ):
            await manager._setup_project("dev", workspace_root)

    @pytest.mark.asyncio
    async def test_setup_project_blocks_non_empty_directory(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Non-empty directories without matching config should be rejected."""

        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        project_dir = workspace_root / "NewProj"
        project_dir.mkdir()
        (project_dir / "random.txt").write_text("data", encoding="utf-8")

        answers = {
            "Select your Workato region": {
                "region": "US Data Center (https://www.workato.com)"
            },
            "Select a project": {"project": "Create new project"},
        }

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: answers[qs[0].message],
        )

        async def mock_prompt5(message: str, **_: Any) -> str:
            return "NewProj" if message == "Enter project name" else "token"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            mock_prompt5,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)

        with pytest.raises(SystemExit):
            await manager._setup_project("dev", workspace_root)

    @pytest.mark.asyncio
    async def test_setup_project_requires_project_name(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Empty project name should trigger exit."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        async def mock_prompt6(message: str, **_: Any) -> str:
            return "   " if message == "Enter project name" else "token"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            mock_prompt6,
        )

        def prompt_create_new(questions: list[Any]) -> dict[str, str]:
            message = questions[0].message
            if message == "Select your Workato region":
                return {"region": questions[0].choices[0]}
            if message == "Select a project":
                return {"project": "Create new project"}
            raise AssertionError(message)

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            prompt_create_new,
        )

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        with pytest.raises(SystemExit):
            await config_manager._setup_project("dev", tmp_path)

    @pytest.mark.asyncio
    async def test_setup_project_no_selection_exits(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """No selection should exit early."""

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        def failing_prompt(questions: list[Any]) -> dict[str, str] | None:
            message = questions[0].message
            if message == "Select your Workato region":
                return {"region": questions[0].choices[0]}
            return None

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            failing_prompt,
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            lambda *a, **k: "token",
        )

        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        with pytest.raises(SystemExit):
            await config_manager._setup_project("dev", tmp_path)

    def test_validate_region_valid(self, tmp_path: Path) -> None:
        """Test validate_region with valid region."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        assert config_manager.validate_region("us") is True
        assert config_manager.validate_region("eu") is True
        assert config_manager.validate_region("custom") is True

    def test_validate_region_invalid(self, tmp_path: Path) -> None:
        """Test validate_region with invalid region."""
        config_manager = ConfigManager(config_dir=tmp_path, skip_validation=True)
        assert config_manager.validate_region("invalid") is False

    @pytest.mark.asyncio
    async def test_setup_project_no_premature_prompt_with_old_workatoenv(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Old .workatoenv should NOT prompt before user selects project."""
        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        # Create old .workatoenv with different project
        # (use ID 888 to ensure it's different from StubProjectManager's ID 999)
        old_config = {
            "project_id": 888,
            "project_name": "OldProject",
            "folder_id": 1,
        }
        (workspace_root / ".workatoenv").write_text(
            json.dumps(old_config), encoding="utf-8"
        )

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = []
        StubProjectManager.created_projects = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        answers = {
            "Select a project": {"project": "Create new project"},
        }

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: answers[qs[0].message],
        )

        async def mock_prompt(message: str, **_: Any) -> str:
            return "NewProject"

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.prompt",
            mock_prompt,
        )

        # Should not call confirm, but if it does, return True
        # (which means detection found old project incorrectly)
        confirm_called = []

        def mock_confirm(*args: Any, **kwargs: Any) -> bool:
            confirm_called.append(True)
            return True

        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            mock_confirm,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        await manager._setup_project("dev", workspace_root)

        # Confirm should NOT have been called (no premature prompt)
        assert len(confirm_called) == 0

        # Should NOT see "Found existing project" or "Use this project"
        assert not any("Found existing project" in msg for msg in outputs)
        assert not any("Use this project" in msg for msg in outputs)

        # Should create new project directory
        new_project_dir = workspace_root / "NewProject"
        assert new_project_dir.exists()

    @pytest.mark.asyncio
    async def test_setup_project_detects_existing_after_selection(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """After user selects project, detect if it exists locally."""
        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        # Create existing project in subdirectory
        existing_project_dir = workspace_root / "projects" / "ExistingProj"
        existing_project_dir.mkdir(parents=True)
        existing_config = {
            "project_id": 42,
            "project_name": "ExistingProj",
            "folder_id": 5,
        }
        (existing_project_dir / ".workatoenv").write_text(
            json.dumps(existing_config), encoding="utf-8"
        )

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "ExistingProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: {"project": "ExistingProj (ID: 42)"},
        )

        # User confirms reinitialization
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda *args, **kwargs: True,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        await manager._setup_project("dev", workspace_root)

        # Should see project exists message AFTER selection
        assert any(
            "already exists locally at" in msg and "projects/ExistingProj" in msg
            for msg in outputs
        )

    @pytest.mark.asyncio
    async def test_setup_project_user_declines_reinitialization(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """User declining reinitialization should cancel setup."""
        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        # Create existing project
        existing_project_dir = workspace_root / "ExistingProj"
        existing_project_dir.mkdir()
        existing_config = {
            "project_id": 42,
            "project_name": "ExistingProj",
            "folder_id": 5,
        }
        (existing_project_dir / ".workatoenv").write_text(
            json.dumps(existing_config), encoding="utf-8"
        )

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "ExistingProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: {"project": "ExistingProj (ID: 42)"},
        )

        # User declines reinitialization
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda *args, **kwargs: False,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)

        with pytest.raises(SystemExit):
            await manager._setup_project("dev", workspace_root)

        # Should see cancellation message
        assert any("Initialization cancelled" in msg for msg in outputs)

    @pytest.mark.asyncio
    async def test_setup_non_interactive_fails_when_project_exists(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Non-interactive mode should fail if project already exists locally."""
        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        # Create existing project
        existing_project_dir = workspace_root / "ExistingProj"
        existing_project_dir.mkdir()
        existing_config = {
            "project_id": 42,
            "project_name": "ExistingProj",
            "folder_id": 5,
        }
        (existing_project_dir / ".workatoenv").write_text(
            json.dumps(existing_config), encoding="utf-8"
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "ExistingProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        manager.profile_manager = mock_profile_manager
        manager.workspace_manager = WorkspaceManager(start_path=workspace_root)

        with pytest.raises(click.ClickException) as excinfo:
            await manager._setup_non_interactive(
                profile_name="dev",
                region="us",
                api_token="token",
                project_id=42,
            )

        # Should see error about project existing
        assert "already exists locally" in str(excinfo.value)
        assert "ExistingProj" in str(excinfo.value)
        assert "non-interactive" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_setup_project_skips_corrupted_configs(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Corrupted .workatoenv files should be skipped during detection."""
        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        # Create directory with corrupted .workatoenv
        corrupted_dir = workspace_root / "corrupted"
        corrupted_dir.mkdir()
        (corrupted_dir / ".workatoenv").write_text("invalid json{", encoding="utf-8")

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        StubProjectManager.available_projects = [StubProject(42, "TestProj", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: {"project": "TestProj (ID: 42)"},
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)

        # Should not raise error, just skip corrupted config
        await manager._setup_project("dev", workspace_root)

        # Should create new project successfully
        test_project_dir = workspace_root / "TestProj"
        assert test_project_dir.exists()

    @pytest.mark.asyncio
    async def test_setup_project_matches_by_project_id(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_profile_manager: Mock,
    ) -> None:
        """Project detection should match by project_id, not by name."""
        workspace_root = tmp_path
        monkeypatch.chdir(workspace_root)

        # Create existing project with different name but same ID
        existing_project_dir = workspace_root / "OldName"
        existing_project_dir.mkdir()
        existing_config = {
            "project_id": 42,
            "project_name": "OldName",
            "folder_id": 5,
        }
        (existing_project_dir / ".workatoenv").write_text(
            json.dumps(existing_config), encoding="utf-8"
        )

        mock_profile_manager.set_profile(
            "dev",
            ProfileData(
                region="us", region_url="https://www.workato.com", workspace_id=1
            ),
            "token",
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProfileManager",
            lambda: mock_profile_manager,
        )
        monkeypatch.setattr(
            ConfigManager.__module__ + ".Workato",
            StubWorkato,
        )
        # Project renamed on remote to "NewName"
        StubProjectManager.available_projects = [StubProject(42, "NewName", 5)]
        monkeypatch.setattr(
            ConfigManager.__module__ + ".ProjectManager",
            StubProjectManager,
        )

        monkeypatch.setattr(
            ConfigManager.__module__ + ".inquirer.prompt",
            lambda qs: {"project": "NewName (ID: 42)"},
        )

        # User confirms reinitialization
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.confirm",
            lambda *args, **kwargs: True,
        )

        outputs: list[str] = []
        monkeypatch.setattr(
            ConfigManager.__module__ + ".click.echo",
            lambda msg="": outputs.append(str(msg)),
        )

        manager = ConfigManager(config_dir=workspace_root, skip_validation=True)
        await manager._setup_project("dev", workspace_root)

        # Should detect existing project by ID even though name changed
        assert any("already exists locally" in msg for msg in outputs)
        assert any("OldName" in msg for msg in outputs)
