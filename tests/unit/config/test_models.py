"""Tests for configuration data models."""

import pytest

from pydantic import ValidationError

from workato_platform.cli.utils.config.models import (
    AVAILABLE_REGIONS,
    ConfigData,
    ProfileData,
    ProfilesConfig,
    ProjectInfo,
    RegionInfo,
)


class TestConfigData:
    """Test ConfigData model."""

    def test_config_data_creation(self) -> None:
        """Test ConfigData can be created with various fields."""
        config = ConfigData(
            project_id=123,
            project_name="test",
            project_path="projects/test",
            folder_id=456,
            profile="dev",
        )
        assert config.project_id == 123
        assert config.project_name == "test"
        assert config.project_path == "projects/test"
        assert config.folder_id == 456
        assert config.profile == "dev"

    def test_config_data_optional_fields(self) -> None:
        """Test ConfigData works with minimal fields."""
        config = ConfigData()
        assert config.project_id is None
        assert config.project_name is None
        assert config.project_path is None
        assert config.folder_id is None
        assert config.profile is None

    def test_config_data_model_dump_excludes_none(self) -> None:
        """Test ConfigData excludes None values when dumped."""
        config = ConfigData(project_id=123, project_name="test")
        dumped = config.model_dump(exclude_none=True)
        assert dumped == {"project_id": 123, "project_name": "test"}
        assert "project_path" not in dumped


class TestRegionInfo:
    """Test RegionInfo model."""

    def test_region_info_creation(self) -> None:
        """Test RegionInfo model creation."""
        region = RegionInfo(region="us", name="US", url="https://www.workato.com")
        assert region.region == "us"
        assert region.name == "US"
        assert region.url == "https://www.workato.com"

    def test_available_regions_defined(self) -> None:
        """Test AVAILABLE_REGIONS constant is properly defined."""
        assert "us" in AVAILABLE_REGIONS
        assert "eu" in AVAILABLE_REGIONS
        assert "custom" in AVAILABLE_REGIONS

        us_region = AVAILABLE_REGIONS["us"]
        assert us_region.region == "us"
        assert us_region.url == "https://www.workato.com"


class TestProfileData:
    """Test ProfileData model."""

    def test_profile_data_creation(self) -> None:
        """Test ProfileData model creation."""
        profile = ProfileData(
            region="us", region_url="https://www.workato.com", workspace_id=123
        )
        assert profile.region == "us"
        assert profile.region_url == "https://www.workato.com"
        assert profile.workspace_id == 123

    def test_profile_data_region_validation(self) -> None:
        """Test ProfileData validates region codes."""
        with pytest.raises(ValidationError):
            ProfileData(
                region="invalid", region_url="https://example.com", workspace_id=123
            )

    def test_profile_data_region_name_property(self) -> None:
        """Test region_name property."""
        profile = ProfileData(
            region="us",
            region_url="https://www.workato.com",
            workspace_id=123,
        )
        assert profile.region_name == "US Data Center"

        profile_custom = ProfileData(
            region="custom",
            region_url="https://custom.com",
            workspace_id=123,
        )
        assert profile_custom.region_name == "Custom URL"


class TestProfilesConfig:
    """Test ProfilesConfig model."""

    def test_profiles_config_creation(self) -> None:
        """Test ProfilesConfig creation."""
        config = ProfilesConfig()
        assert config.current_profile is None
        assert config.profiles == {}

    def test_profiles_config_with_data(self) -> None:
        """Test ProfilesConfig with profile data."""
        profile = ProfileData(
            region="us",
            region_url="https://www.workato.com",
            workspace_id=123,
        )
        config = ProfilesConfig(
            current_profile="default", profiles={"default": profile}
        )
        assert config.current_profile == "default"
        assert "default" in config.profiles
        assert config.profiles["default"] == profile


class TestProjectInfo:
    """Test ProjectInfo model."""

    def test_project_info_creation(self) -> None:
        """Test ProjectInfo model creation."""
        project = ProjectInfo(id=123, name="test", folder_id=456)
        assert project.id == 123
        assert project.name == "test"
        assert project.folder_id == 456

    def test_project_info_optional_folder_id(self) -> None:
        """Test ProjectInfo with optional folder_id."""
        project = ProjectInfo(id=123, name="test")
        assert project.id == 123
        assert project.name == "test"
        assert project.folder_id is None
