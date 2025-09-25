"""Workspace and project directory management."""

import json
import sys
from pathlib import Path
from typing import Optional

import asyncclick as click


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