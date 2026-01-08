import pytest

from workato_platform_cli.client.workato_api.models.asset_reference import (
    AssetReference,
)


def test_asset_reference_accepts_all_valid_types() -> None:
    """Test that AssetReference model accepts all valid asset types."""
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
        asset_ref_data = {
            "id": 1,
            "type": asset_type,
            "absolute_path": f"/test/{asset_type}",
        }

        # Should not raise ValueError
        asset_ref = AssetReference.from_dict(asset_ref_data)
        assert asset_ref is not None
        assert asset_ref.type == asset_type


def test_asset_reference_rejects_invalid_type() -> None:
    """Test that AssetReference model rejects invalid types."""
    asset_ref_data = {
        "id": 12345,
        "type": "invalid_type",
        "absolute_path": "/test/invalid",
    }

    with pytest.raises(ValueError, match="must be one of enum values"):
        AssetReference.from_dict(asset_ref_data)
