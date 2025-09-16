import contextlib
import filecmp
import json
import shutil
import tempfile

from pathlib import Path

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform.cli.commands.projects.project_manager import ProjectManager
from workato_platform.cli.containers import Container
from workato_platform.cli.utils.config import ConfigData, ConfigManager
from workato_platform.cli.utils.exception_handler import handle_api_exceptions


def _ensure_workato_in_gitignore(project_dir: Path) -> None:
    """Ensure .workato/ is added to .gitignore in the project directory"""
    gitignore_file = project_dir / ".gitignore"
    workato_entry = ".workato/"

    # Read existing .gitignore if it exists
    existing_lines = []
    if gitignore_file.exists():
        with open(gitignore_file) as f:
            existing_lines = [line.rstrip("\n") for line in f.readlines()]

    # Check if .workato/ is already in .gitignore
    if workato_entry not in existing_lines:
        # Add .workato/ to .gitignore
        with open(gitignore_file, "a") as f:
            if existing_lines and existing_lines[-1] != "":
                f.write("\n")  # Add newline if file doesn't end with one
            f.write(f"{workato_entry}\n")


async def _pull_project(
    config_manager: ConfigManager,
    project_manager: ProjectManager,
) -> None:
    """Internal pull logic that can be called from other commands"""

    # Load API token
    api_token = config_manager.api_token
    if not api_token:
        click.echo("❌ No API token found. Please run 'workato init' first.")
        return

    # Load project metadata
    meta_data = config_manager.load_config()
    if not meta_data.folder_id:
        click.echo("❌ No project configured. Please run 'workato init' first.")
        return

    folder_id = meta_data.folder_id
    project_name = meta_data.project_name or "project"

    # Determine project structure
    current_project_name = config_manager.get_current_project_name()
    if current_project_name:
        # We're in a project directory, use the project root (not cwd)
        project_dir = config_manager.get_project_root()
        if not project_dir:
            click.echo("❌ Could not determine project root directory")
            return
    else:
        # Find the workspace root (where .workato config is)
        workspace_root = config_manager.get_project_root()
        if not workspace_root:
            workspace_root = Path.cwd()

        # Create projects/{project_name} structure relative to workspace root
        projects_root = workspace_root / "projects"
        projects_root.mkdir(exist_ok=True)
        project_dir = projects_root / project_name
        project_dir.mkdir(exist_ok=True)

        # Create project-specific .workato directory with only project metadata
        project_workato_dir = project_dir / ".workato"
        project_workato_dir.mkdir(exist_ok=True)

        # Save only project-specific metadata (no credentials/profiles)
        project_config_data = ConfigData(
            project_id=meta_data.project_id,
            project_name=meta_data.project_name,
            folder_id=meta_data.folder_id,
            profile=meta_data.profile,  # Keep profile reference for this project
        )
        project_config_manager = ConfigManager(project_workato_dir)
        project_config_manager.save_config(project_config_data)

        # Ensure .workato/ is in workspace root .gitignore
        _ensure_workato_in_gitignore(workspace_root)

    # Export the project to a temporary directory first
    click.echo(f"Pulling latest changes for project: {project_name}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_project_path = Path(temp_dir) / "remote_project"

        # Download remote project to temp directory
        result = await project_manager.export_project(
            folder_id,
            project_name,
            target_dir=str(temp_project_path),
        )

        if not result:
            click.echo("❌ Failed to pull project")
            return

        # If local project doesn't exist, just move the temp directory
        if not project_dir.exists():
            shutil.copytree(temp_project_path, project_dir)
            click.echo("✅ Successfully pulled project to ./project")
            return

        # Merge changes between remote and local
        changes = merge_directories(temp_project_path, project_dir)

        # Show summary of changes
        if changes["added"] or changes["modified"] or changes["removed"]:
            click.echo("Changes applied:")
            for change in changes["added"]:
                file_path, stats = (
                    change if isinstance(change, tuple) else (change, None)
                )
                if stats:
                    click.echo(f"  📄 {file_path} (+{stats['lines']} lines)")
                else:
                    click.echo(f"  📄 {file_path}")
            for change in changes["modified"]:
                file_path, stats = (
                    change if isinstance(change, tuple) else (change, None)
                )
                if stats:
                    added, removed = stats["added"], stats["removed"]
                    click.echo(f"  📝 {file_path} (+{added} -{removed})")
                else:
                    click.echo(f"  📝 {file_path}")
            for change in changes["removed"]:
                file_path, stats = (
                    change if isinstance(change, tuple) else (change, None)
                )
                if stats:
                    click.echo(f"  🗑️  {file_path} (-{stats['lines']} lines)")
                else:
                    click.echo(f"  🗑️  {file_path}")

            # Show total stats
            total_added = sum(
                s[1]["lines"] if isinstance(s, tuple) and s[1] else 0
                for s in changes["added"]
            )
            total_added += sum(
                s[1]["added"] if isinstance(s, tuple) and s[1] else 0
                for s in changes["modified"]
            )
            total_removed = sum(
                s[1]["lines"] if isinstance(s, tuple) and s[1] else 0
                for s in changes["removed"]
            )
            total_removed += sum(
                s[1]["removed"] if isinstance(s, tuple) and s[1] else 0
                for s in changes["modified"]
            )

            click.echo(
                f"✅ Successfully pulled project changes (+{total_added} "
                f"-{total_removed})"
            )
        else:
            click.echo("✅ Project is already up to date")


def count_lines(file_path: Path) -> int:
    """Count lines in a file, handling different file types"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return len(f.readlines())
    except (UnicodeDecodeError, OSError):
        # For binary files, just return file size as rough estimate
        try:
            return file_path.stat().st_size // 50  # Rough estimate: 50 bytes per "line"
        except OSError:
            return 0


def calculate_diff_stats(old_file: Path, new_file: Path) -> dict[str, int]:
    """Calculate diff statistics between two files"""
    try:
        # For JSON files, try to do more intelligent diffing
        if old_file.suffix.lower() == ".json" and new_file.suffix.lower() == ".json":
            return calculate_json_diff_stats(old_file, new_file)

        # For text files, do line-based diffing
        with open(old_file, encoding="utf-8") as f:
            old_lines = f.readlines()
        with open(new_file, encoding="utf-8") as f:
            new_lines = f.readlines()

        # Simple diff: count different lines
        old_set = set(old_lines)
        new_set = set(new_lines)

        added = len(new_set - old_set)
        removed = len(old_set - new_set)

        return {"added": added, "removed": removed}

    except (UnicodeDecodeError, OSError):
        # For binary files, just show file size change
        try:
            old_size = old_file.stat().st_size
            new_size = new_file.stat().st_size
            if new_size > old_size:
                return {"added": (new_size - old_size) // 50, "removed": 0}
            else:
                return {"added": 0, "removed": (old_size - new_size) // 50}
        except OSError:
            return {"added": 0, "removed": 0}


def calculate_json_diff_stats(old_file: Path, new_file: Path) -> dict[str, int]:
    """Calculate diff statistics for JSON files"""
    try:
        with open(old_file, encoding="utf-8") as f:
            old_data = json.load(f)
        with open(new_file, encoding="utf-8") as f:
            new_data = json.load(f)

        # Convert to JSON strings for comparison
        old_str = json.dumps(old_data, sort_keys=True, indent=2)
        new_str = json.dumps(new_data, sort_keys=True, indent=2)

        old_lines = old_str.split("\n")
        new_lines = new_str.split("\n")

        old_set = set(old_lines)
        new_set = set(new_lines)

        added = len(new_set - old_set)
        removed = len(old_set - new_set)

        return {"added": added, "removed": removed}

    except (json.JSONDecodeError, OSError):
        # Fall back to regular diff
        return calculate_diff_stats(old_file, new_file)


def merge_directories(
    remote_dir: Path, local_dir: Path
) -> dict[str, list[tuple[str, dict[str, int]]]]:
    """Merge remote directory into local directory, return summary of changes"""
    remote_path = Path(remote_dir)
    local_path = Path(local_dir)

    changes: dict[str, list[tuple[str, dict[str, int]]]] = {
        "added": [],
        "modified": [],
        "removed": [],
    }

    # Get all files in both directories
    remote_files: set[Path] = set()
    local_files = set()

    # Collect remote files
    if remote_path.exists():
        for file_path in remote_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(remote_path)
                remote_files.add(rel_path)

    # Collect local files
    for file_path in local_path.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(local_path)
            local_files.add(rel_path)

    # Handle additions and modifications
    for rel_path in remote_files:
        remote_file = remote_path / rel_path
        local_file = local_path / rel_path

        if not local_file.exists():
            # New file - copy it and count lines
            local_file.parent.mkdir(parents=True, exist_ok=True)
            lines = count_lines(remote_file)
            shutil.copy2(remote_file, local_file)
            changes["added"].append((str(rel_path), {"lines": lines}))
        else:
            # Check if file is different
            if not filecmp.cmp(remote_file, local_file, shallow=False):
                # File modified - calculate diff stats before updating
                diff_stats = calculate_diff_stats(local_file, remote_file)
                shutil.copy2(remote_file, local_file)
                changes["modified"].append((str(rel_path), diff_stats))

    # Handle deletions (files that exist locally but not remotely)
    # Exclude .workato directory from deletion
    for rel_path in local_files - remote_files:
        # Skip files in .workato directory
        if rel_path.parts[0] == ".workato":
            continue

        local_file = local_path / rel_path
        lines = count_lines(local_file)
        local_file.unlink()
        changes["removed"].append((str(rel_path), {"lines": lines}))

        # Remove empty directories
        with contextlib.suppress(OSError):
            local_file.parent.rmdir()

    return changes


@click.command()
@inject
@handle_api_exceptions
async def pull(
    config_manager: ConfigManager = Provide[Container.config_manager],
    project_manager: ProjectManager = Provide[Container.project_manager],
) -> None:
    """Pull latest changes from Workato remote"""
    await _pull_project(config_manager, project_manager)
