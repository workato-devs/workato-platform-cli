"""Pytest configuration and shared fixtures."""

import tempfile

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from asyncclick.testing import CliRunner



@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide an async click testing runner."""
    return CliRunner()


@pytest.fixture
def mock_config_manager():
    """Mock ConfigManager for testing."""
    config_manager = Mock()
    config_manager.get_api_token.return_value = "test-api-token"
    config_manager.get_api_host.return_value = "https://app.workato.com"
    config_manager.get_current_profile.return_value = "default"
    return config_manager


@pytest.fixture
def mock_workato_client():
    """Mock Workato API client."""
    client = Mock()

    # Mock API responses
    client.recipes_api = Mock()
    client.connections_api = Mock()
    client.connectors_api = Mock()
    client.projects_api = Mock()

    return client


@pytest.fixture(autouse=True)
def isolate_tests(monkeypatch, temp_config_dir):
    """Isolate tests by using temporary directories and env vars."""
    # Prevent tests from accessing real config files
    monkeypatch.setenv("WORKATO_CONFIG_DIR", str(temp_config_dir))
    monkeypatch.setenv("WORKATO_DISABLE_UPDATE_CHECK", "1")

    # Ensure we don't make real API calls
    monkeypatch.setenv("WORKATO_TEST_MODE", "1")


@pytest.fixture(autouse=True)
def mock_webbrowser():
    """Automatically mock webbrowser.open for all tests to prevent browser launching."""
    with (
        patch("webbrowser.open", return_value=None) as mock_open_global,
        patch(
            "workato_platform.cli.commands.connections.webbrowser.open",
            return_value=None,
        ) as mock_open_connections,
    ):
        yield {"global": mock_open_global, "connections": mock_open_connections}


@pytest.fixture
def sample_recipe():
    """Sample recipe JSON for testing."""
    return {
        "name": "Test Recipe",
        "description": "A test recipe",
        "trigger": {
            "provider": "scheduler",
            "name": "scheduled_job",
            "input": {"interval": "5", "start_date": "2024-01-01T00:00:00Z"},
        },
        "actions": [
            {
                "provider": "http",
                "name": "get_request",
                "input": {"url": "https://api.example.com/data"},
            }
        ],
    }


@pytest.fixture
def sample_connection():
    """Sample connection data for testing."""
    return {
        "id": 12345,
        "name": "Test Connection",
        "provider": "salesforce",
        "authorized": True,
        "created_at": "2024-01-01T00:00:00Z",
    }
