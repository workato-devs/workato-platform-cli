"""Utilities for managing .gitignore files."""

from pathlib import Path


def ensure_gitignore_entry(workspace_root: Path, entry: str) -> None:
    """Ensure an entry is added to .gitignore in the workspace root.

    Args:
        workspace_root: Path to the workspace root directory
        entry: Gitignore entry to add (e.g., "projects/*/workato/")
    """
    gitignore_file = workspace_root / ".gitignore"

    # Read existing .gitignore if it exists
    existing_lines = []
    if gitignore_file.exists():
        with open(gitignore_file) as f:
            existing_lines = [line.rstrip("\n") for line in f.readlines()]

    # Check if entry is already in .gitignore
    if entry not in existing_lines:
        # Add entry to .gitignore
        with open(gitignore_file, "a") as f:
            if existing_lines and existing_lines[-1] != "":
                f.write("\n")  # Add newline if file doesn't end with one
            f.write(f"{entry}\n")


def ensure_stubs_in_gitignore(workspace_root: Path) -> None:
    """Ensure workato/ generated packages are added to .gitignore in workspace root."""
    ensure_gitignore_entry(workspace_root, "projects/*/workato/")