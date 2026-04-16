"""Tests for AutomaticallyCreatedAssetRemovalService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.campaign.automatically_created_asset_removal_service import (
    AutomaticallyCreatedAssetRemovalService,
    register_automatically_created_asset_removal_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> AutomaticallyCreatedAssetRemovalService:
    """Create an AutomaticallyCreatedAssetRemovalService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.campaign.automatically_created_asset_removal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = AutomaticallyCreatedAssetRemovalService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_remove_campaign_automatically_created_assets(
    service: AutomaticallyCreatedAssetRemovalService, mock_ctx: Context
) -> None:
    """Test removing automatically created assets from a campaign."""
    mock_client = service.client
    mock_client.remove_campaign_automatically_created_asset.return_value = Mock()  # type: ignore

    expected_result = {"results": []}
    operations = [
        {
            "campaign": "customers/1234567890/campaigns/111",
            "asset": "customers/1234567890/assets/222",
            "field_type": "HEADLINE",
        }
    ]

    with patch(
        "src.services.campaign.automatically_created_asset_removal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_campaign_automatically_created_assets(
            ctx=mock_ctx,
            customer_id="1234567890",
            operations=operations,
        )

    assert result == expected_result
    mock_client.remove_campaign_automatically_created_asset.assert_called_once()  # type: ignore
    call_args = mock_client.remove_campaign_automatically_created_asset.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    assert request.operations[0].campaign == "customers/1234567890/campaigns/111"
    assert request.operations[0].asset == "customers/1234567890/assets/222"


@pytest.mark.asyncio
async def test_remove_campaign_automatically_created_assets_multiple(
    service: AutomaticallyCreatedAssetRemovalService, mock_ctx: Context
) -> None:
    """Test removing multiple automatically created assets."""
    mock_client = service.client
    mock_client.remove_campaign_automatically_created_asset.return_value = Mock()  # type: ignore

    expected_result = {"results": []}
    operations = [
        {
            "campaign": "customers/1234567890/campaigns/111",
            "asset": "customers/1234567890/assets/222",
            "field_type": "HEADLINE",
        },
        {
            "campaign": "customers/1234567890/campaigns/111",
            "asset": "customers/1234567890/assets/333",
            "field_type": "DESCRIPTION",
        },
    ]

    with patch(
        "src.services.campaign.automatically_created_asset_removal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_campaign_automatically_created_assets(
            ctx=mock_ctx,
            customer_id="1234567890",
            operations=operations,
        )

    assert result == expected_result
    call_args = mock_client.remove_campaign_automatically_created_asset.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2


@pytest.mark.asyncio
async def test_remove_campaign_automatically_created_assets_error(
    service: AutomaticallyCreatedAssetRemovalService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in remove_campaign_automatically_created_assets."""
    mock_client = service.client
    mock_client.remove_campaign_automatically_created_asset.side_effect = (
        google_ads_exception  # type: ignore
    )

    with pytest.raises(Exception) as exc_info:
        await service.remove_campaign_automatically_created_assets(
            ctx=mock_ctx,
            customer_id="1234567890",
            operations=[
                {
                    "campaign": "customers/1234567890/campaigns/111",
                    "asset": "customers/1234567890/assets/222",
                    "field_type": "HEADLINE",
                }
            ],
        )

    assert "Failed to remove automatically created assets" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_automatically_created_asset_removal_tools(mock_mcp)
    assert isinstance(svc, AutomaticallyCreatedAssetRemovalService)
    assert mock_mcp.tool.call_count == 1  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert tool_names == ["remove_campaign_automatically_created_assets"]
