"""Data models for configuration management."""


from pydantic import BaseModel, Field, field_validator


class ProjectInfo(BaseModel):
    """Data model for project information"""
    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    folder_id: int | None = Field(None, description="Associated folder ID")


class ConfigData(BaseModel):
    """Data model for configuration file data"""
    project_id: int | None = Field(None, description="Project ID")
    project_name: str | None = Field(None, description="Project name")
    project_path: str | None = Field(None, description="Relative path to project (workspace only)")
    folder_id: int | None = Field(None, description="Folder ID")
    profile: str | None = Field(None, description="Profile override")


class RegionInfo(BaseModel):
    """Data model for region information"""
    region: str = Field(..., description="Region code")
    name: str = Field(..., description="Human-readable region name")
    url: str | None = Field(None, description="Base URL for the region")


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
