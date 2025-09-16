"""Basic import tests that work without heavy dependencies."""

import sys

from pathlib import Path

import pytest


# Add src to Python path for testing
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestBasicImports:
    """Test basic module imports and structure."""

    def test_workato_cli_package_exists(self):
        """Test that the main package exists."""
        try:
            import workato_platform.cli

            assert workato_platform.cli is not None
        except ImportError:
            pytest.fail("workato_platform.cli package could not be imported")

    def test_version_is_available(self):
        """Test that version is available."""
        try:
            import workato_platform

            version = getattr(workato_platform, "__version__", None)
            assert version is not None
            assert isinstance(version, str)
        except ImportError:
            pytest.skip("Version not available due to import issues")

    def test_utils_package_structure(self):
        """Test that utils package has expected structure."""
        try:
            from workato_platform.cli.utils import version_checker

            assert hasattr(version_checker, "VersionChecker")
        except ImportError:
            pytest.skip("Utils package not available due to dependencies")

    def test_version_checker_class_structure(self):
        """Test version checker class structure."""
        try:
            from workato_platform.cli.utils.version_checker import VersionChecker

            # Check that class has expected methods
            assert hasattr(VersionChecker, "check_for_updates")
            assert hasattr(VersionChecker, "get_latest_version")
            assert hasattr(VersionChecker, "should_check_for_updates")

        except ImportError:
            pytest.skip("VersionChecker not available due to dependencies")

    def test_commands_package_exists(self):
        """Test that commands package structure exists."""
        commands_path = src_path / "workato_platform" / "cli" / "commands"
        assert commands_path.exists()
        assert commands_path.is_dir()

        # Check for expected command modules
        expected_commands = [
            "connections.py",
            "guide.py",
            "profiles.py",
            "recipes",  # directory
        ]

        for cmd in expected_commands:
            cmd_path = commands_path / cmd
            assert cmd_path.exists(), f"Missing command: {cmd}"

    def test_basic_configuration_can_be_created(self):
        """Test basic configuration without heavy dependencies."""
        try:
            from workato_platform.cli.utils.config import ConfigManager

            # Should be able to import the class
            assert ConfigManager is not None

        except ImportError:
            pytest.skip("ConfigManager not available due to dependencies")

    def test_container_module_exists(self):
        """Test container module exists."""
        try:
            from workato_platform.cli import containers

            assert hasattr(containers, "Container")

        except ImportError:
            pytest.skip("Container module not available due to dependencies")


class TestProjectStructure:
    """Test project file structure."""

    def test_required_files_exist(self):
        """Test that required project files exist."""
        project_root = Path(__file__).parent.parent.parent

        required_files = [
            "pyproject.toml",
            "README.md",
            "src/workato_platform/cli/__init__.py",
            "src/workato_platform/cli/cli.py",
        ]

        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Missing required file: {file_path}"

    def test_test_structure_exists(self):
        """Test that test structure is properly organized."""
        tests_path = Path(__file__).parent.parent

        assert tests_path.exists()
        assert (tests_path / "unit").exists()
        assert (tests_path / "integration").exists()
        assert (tests_path / "conftest.py").exists()

    def test_source_code_structure(self):
        """Test source code directory structure."""
        src_path = (
            Path(__file__).parent.parent.parent / "src" / "workato_platform" / "cli"
        )

        expected_dirs = ["commands", "utils"]

        for dir_name in expected_dirs:
            dir_path = src_path / dir_name
            assert dir_path.exists(), f"Missing directory: {dir_name}"
            assert dir_path.is_dir()
