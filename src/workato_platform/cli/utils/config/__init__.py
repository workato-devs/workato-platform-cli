"""Configuration management for the CLI - public API exports."""

# Import all public APIs to maintain backward compatibility
from .manager import ConfigManager
from .models import (
    AVAILABLE_REGIONS,
    ConfigData,
    ProfileData,
    ProfilesConfig,
    ProjectInfo,
    RegionInfo,
)
from .profiles import ProfileManager, _validate_url_security
from .workspace import WorkspaceManager


# Export all public APIs
__all__ = [
    # Main manager class
    "ConfigManager",

    # Data models
    "ConfigData",
    "ProjectInfo",
    "RegionInfo",
    "ProfileData",
    "ProfilesConfig",

    # Component managers
    "ProfileManager",
    "WorkspaceManager",

    # Constants and utilities
    "AVAILABLE_REGIONS",
    "_validate_url_security",
]
