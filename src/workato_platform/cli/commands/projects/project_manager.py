"""ProjectManager for handling Workato project operations"""

import os
import subprocess
import time
import zipfile

from pathlib import Path

import asyncclick as click
import inquirer

from workato_platform import Workato
from workato_platform.cli.utils.spinner import Spinner
from workato_platform.client.workato_api.models.asset import Asset
from workato_platform.client.workato_api.models.create_export_manifest_request import (
    CreateExportManifestRequest,
)
from workato_platform.client.workato_api.models.create_folder_request import (
    CreateFolderRequest,
)
from workato_platform.client.workato_api.models.export_manifest_request import (
    ExportManifestRequest,
)
from workato_platform.client.workato_api.models.project import Project


class ProjectManager:
    """Manages Workato project operations using the new API client"""

    def __init__(self, workato_api_client: Workato):
        self.client = workato_api_client

    def _format_project_display(self, project: Project) -> str:
        """Format a project object for display - returns formatted string"""
        return f"{project.name} (ID: {project.id})"

    def _get_project_by_display_name(
        self,
        projects: list[Project],
        display_name: str,
    ) -> Project | None:
        """Find a project by its display name - returns project object or None"""
        for project in projects:
            if self._format_project_display(project) == display_name:
                return project
        return None

    async def get_projects(self, page: int = 1, per_page: int = 100) -> list[Project]:
        """Get list of projects with pagination"""
        return await self.client.projects_api.list_projects(
            page=page, per_page=per_page
        )

    async def get_all_projects(self) -> list[Project]:
        """Get all projects by handling pagination"""
        all_projects = []
        page = 1
        per_page = 100

        while True:
            projects = await self.get_projects(page, per_page)

            if not projects:
                break

            all_projects.extend(projects)

            # If we got fewer than per_page results, we're on the last page
            if len(projects) < per_page:
                break

            page += 1

        return all_projects

    async def create_project(self, project_name: str) -> Project:
        """Create a new project folder"""
        folder_data = await self.client.folders_api.create_folder(
            create_folder_request=CreateFolderRequest(name=project_name)
        )

        for project in await self.get_all_projects():
            if project.folder_id == folder_data.id:
                return project

        return Project(
            id=folder_data.id,
            name=project_name,
            folder_id=folder_data.id,
            description="",
        )

    async def check_folder_assets(self, folder_id: int) -> list[Asset]:
        """Check if a folder has any assets"""
        assets_response = await self.client.export_api.list_assets_in_folder(
            folder_id=folder_id
        )
        assets = (
            assets_response.result.assets
            if assets_response.result and assets_response.result.assets
            else []
        )
        return assets

    async def export_project(
        self,
        folder_id: int,
        project_name: str,
        target_dir: str = "project",
    ) -> str | None:
        """Export project assets and return project directory path"""
        # Check if project has any assets before attempting export
        assets = await self.check_folder_assets(folder_id)

        if not assets:
            # Empty project - just create the directory structure
            click.echo("📂 Project is empty, creating directory structure...")
            project_dir = Path(target_dir)
            project_dir.mkdir(exist_ok=True)
            return str(project_dir)

        # Create export manifest with spinner
        spinner = Spinner("Creating export manifest")
        spinner.start()
        try:
            manifest_data = await self.client.export_api.create_export_manifest(
                create_export_manifest_request=CreateExportManifestRequest(
                    export_manifest=ExportManifestRequest(
                        name=project_name,
                        folder_id=folder_id,
                        auto_generate_assets=True,
                    )
                )
            )
            manifest_id = manifest_data.result.id
        finally:
            elapsed = spinner.stop()

        click.echo(f"✅ Export manifest created: {manifest_id} ({elapsed:.1f}s)")

        # Trigger the export package creation
        spinner = Spinner("Triggering export package")
        spinner.start()
        try:
            package_data = await self.client.packages_api.export_package(
                id=str(manifest_id)
            )
            package_id = package_data.id
        finally:
            elapsed = spinner.stop()

        click.echo(f"✅ Export package triggered: {package_id} ({elapsed:.1f}s)")

        # Poll for package completion and download
        extracted_project_dir = await self.download_and_extract_package(
            package_id,
            target_dir,
        )
        return str(extracted_project_dir)

    async def download_and_extract_package(
        self, package_id: int, target_dir: str = "project"
    ) -> Path | None:
        """Download and extract the package, return project directory path"""

        # Poll package status until completed with dynamic status
        spinner = Spinner("Preparing package")
        spinner.start()

        max_wait_time = 300  # 5 minutes timeout
        start_time = time.time()

        try:
            while time.time() - start_time < max_wait_time:
                package_response = await self.client.packages_api.get_package(
                    package_id=package_id
                )
                status = package_response.status

                if status == "completed":
                    break
                elif status == "failed":
                    spinner.stop()
                    click.echo("❌ Package export failed")

                    # Show error details if available
                    if package_response.error:
                        click.echo(f"  📄 Error: {package_response.error}")
                    if package_response.recipe_status:
                        click.echo("  📋 Detailed errors:")
                        for error in package_response.recipe_status:
                            click.echo(f"    • {error}")

                    return None
                else:
                    # Update spinner message with current status
                    spinner.update_message(f"Processing package ({status})")
                    time.sleep(2)  # Wait 2 seconds before polling again

            # Check if we timed out
            if time.time() - start_time >= max_wait_time:
                spinner.stop()
                click.echo(
                    f"⏰ Package still processing after {max_wait_time // 60} minutes"
                )
                click.echo("  💡 Check status manually or try again later")
                click.echo(f"  📊 Package ID: {package_id}")
                return None

        finally:
            elapsed = spinner.stop()

        click.echo(f"✅ Package ready for download ({elapsed:.1f}s)")

        # Download the package using the direct download API
        spinner = Spinner("Downloading package")
        spinner.start()
        try:
            download_response = await self.client.packages_api.download_package(
                package_id=package_id
            )
        finally:
            elapsed = spinner.stop()

        click.echo(f"✅ Package downloaded ({elapsed:.1f}s)")

        # Create project directory and extract
        spinner = Spinner("Extracting files")
        spinner.start()
        try:
            project_dir = Path(target_dir)
            project_dir.mkdir(exist_ok=True)

            # Save and extract zip file
            zip_path = f"{target_dir}.zip"
            with open(zip_path, "wb") as f:
                f.write(download_response)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(project_dir)

            os.remove(zip_path)
        finally:
            elapsed = spinner.stop()

        # Show clean message - don't expose internal temp paths to the user
        click.echo(f"✅ Project assets extracted ({elapsed:.1f}s)")
        return project_dir

    async def handle_post_api_sync(
        self,
    ) -> None:
        """Handle syncing project files after API resource operations"""
        # Auto-sync is always enabled - run pull automatically
        click.echo()
        click.echo("🔄 Auto-syncing project files...")
        try:
            result = subprocess.run(
                ["workato", "pull"],  # noqa: S607, S603
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                click.echo("✅ Project synced successfully")
            else:
                click.echo(f"⚠️  Sync completed with warnings: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            click.echo("⚠️  Sync timed out - please run 'workato pull' manually")

    async def delete_project(self, project_id: int) -> None:
        """Delete a project (folder and assets are automatically cleaned up)"""
        await self.client.projects_api.delete_project(project_id=project_id)

    def save_project_to_config(self, project: Project) -> None:
        """Save project info to config - returns True if successful"""
        from workato_platform.cli.utils.config import ConfigManager

        config_manager = ConfigManager()

        meta_data = config_manager.load_config()
        meta_data.project_id = project.id
        meta_data.project_name = project.name
        meta_data.folder_id = project.folder_id

        config_manager.save_config(meta_data)

    async def import_existing_project(self) -> Project | None:
        """Import an existing project - returns project info or None if failed"""
        projects = await self.client.projects_api.list_projects()

        if not projects:
            click.echo("No projects found in your workspace.")
            return None

        # Create project choices using utility function
        choices = [self._format_project_display(p) for p in projects]
        questions = [
            inquirer.List(
                "project",  # noboost
                message="Select a project:",  # noboost
                choices=choices,
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return None

        # Find selected project using utility function
        selected_project = self._get_project_by_display_name(
            projects, answers["project"]
        )

        if not selected_project:
            return None
            # Save project info using utility function

        self.save_project_to_config(selected_project)
        click.echo(f"✅ Selected project: {selected_project.name}")

        # Export project files
        if selected_project.folder_id:
            await self.export_project(
                folder_id=selected_project.folder_id,
                project_name=selected_project.name,
            )

        return selected_project
