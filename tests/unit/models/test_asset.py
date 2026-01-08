import pytest
from workato_platform_cli.client.workato_api.models.asset import Asset

def test_asset_accepts_all_valid_types():
    """Test that Asset model accepts all valid asset types."""
    valid_types = [
        "recipe",
        "connection",
        "lookup_table",
        "workato_db_table",
        "account_property",
        "project_property",
        "workato_schema",
        "workato_template",
        "lcap_app",
        "lcap_page",
        "custom_adapter",
        "topic",
        "api_group",
        "api_endpoint",
        "agentic_genie",
        "agentic_skill",
        "data_pipeline",
        "decision_engine_model",
        "agentic_knowledge_base",
        "mcp_server",
    ]

    for asset_type in valid_types:
        asset_data = {
            "id": 1,
            "name": f"Test {asset_type}",
            "type": asset_type,
            "zip_name": "test.zip",
            "checked": True,
            "root_folder": False,
        }

        # Should not raise ValueError
        asset = Asset.from_dict(asset_data)
        assert asset.type == asset_type


def test_asset_rejects_invalid_type():
    """Test that Asset model rejects invalid types."""
    asset_data = {
        "id": 12345,
        "name": "Test Asset",
        "type": "invalid_type",
        "zip_name": "test.zip",
        "checked": True,
        "root_folder": False,
    }

    with pytest.raises(ValueError, match="must be one of enum values"):
        Asset.from_dict(asset_data)

