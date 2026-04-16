"""Tests for CampaignLifecycleGoalService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.campaign.campaign_lifecycle_goal_service import (
    CampaignLifecycleGoalService,
    register_campaign_lifecycle_goal_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CampaignLifecycleGoalService:
    """Create a CampaignLifecycleGoalService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.campaign.campaign_lifecycle_goal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CampaignLifecycleGoalService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_configure_campaign_lifecycle_goals_create(
    service: CampaignLifecycleGoalService,
    mock_ctx: Context,
) -> None:
    """Test configuring campaign lifecycle goals with create operation."""
    mock_client = service.client
    mock_client.configure_campaign_lifecycle_goals.return_value = Mock()  # type: ignore

    expected_result = {
        "result": {"resource_name": "customers/123/campaignLifecycleGoals/456"}
    }

    with patch(
        "src.services.campaign.campaign_lifecycle_goal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.configure_campaign_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_resource_name="customers/1234567890/campaigns/111",
            operation_type="create",
        )

    assert result == expected_result
    mock_client.configure_campaign_lifecycle_goals.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_configure_campaign_lifecycle_goals_update(
    service: CampaignLifecycleGoalService,
    mock_ctx: Context,
) -> None:
    """Test configuring campaign lifecycle goals with update operation."""
    mock_client = service.client
    mock_client.configure_campaign_lifecycle_goals.return_value = Mock()  # type: ignore

    expected_result = {
        "result": {"resource_name": "customers/123/campaignLifecycleGoals/456"}
    }

    with patch(
        "src.services.campaign.campaign_lifecycle_goal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.configure_campaign_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_resource_name="customers/1234567890/campaigns/111",
            operation_type="update",
        )

    assert result == expected_result
    mock_client.configure_campaign_lifecycle_goals.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_configure_campaign_lifecycle_goals_error(
    service: CampaignLifecycleGoalService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when configuring campaign lifecycle goals fails."""
    mock_client = service.client
    mock_client.configure_campaign_lifecycle_goals.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.configure_campaign_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_resource_name="customers/1234567890/campaigns/111",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_campaign_lifecycle_goal_tools(mock_mcp)
    assert isinstance(svc, CampaignLifecycleGoalService)
    assert mock_mcp.tool.call_count > 0  # type: ignore
