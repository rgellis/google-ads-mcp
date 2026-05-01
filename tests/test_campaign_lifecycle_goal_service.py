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
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.campaign.campaign_lifecycle_goal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CampaignLifecycleGoalService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_configure_create(
    service: CampaignLifecycleGoalService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.configure_campaign_lifecycle_goals.return_value = Mock()  # type: ignore

    with patch(
        "src.services.campaign.campaign_lifecycle_goal_service.serialize_proto_message",
        return_value={"result": {}},
    ):
        await service.configure_campaign_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="CREATE",
            campaign="customers/1234567890/campaigns/1",
            optimization_mode="TARGET_NEW_CUSTOMER",
            value=10.0,
            high_lifetime_value=50.0,
        )

    request = mock_client.configure_campaign_lifecycle_goals.call_args[1]["request"]  # type: ignore
    op = request.operation
    assert op.create.campaign == "customers/1234567890/campaigns/1"
    settings = op.create.customer_acquisition_goal_settings
    assert settings.value_settings.value == 10.0
    assert settings.value_settings.high_lifetime_value == 50.0


@pytest.mark.asyncio
async def test_configure_update(
    service: CampaignLifecycleGoalService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.configure_campaign_lifecycle_goals.return_value = Mock()  # type: ignore

    rn = "customers/1234567890/campaignLifecycleGoal/1"
    with patch(
        "src.services.campaign.campaign_lifecycle_goal_service.serialize_proto_message",
        return_value={"result": {}},
    ):
        await service.configure_campaign_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="UPDATE",
            resource_name=rn,
            value=12.0,
        )

    request = mock_client.configure_campaign_lifecycle_goals.call_args[1]["request"]  # type: ignore
    op = request.operation
    assert op.update.resource_name == rn
    paths = list(op.update_mask.paths)
    assert "customer_acquisition_goal_settings.value_settings" in paths


@pytest.mark.asyncio
async def test_create_requires_campaign(
    service: CampaignLifecycleGoalService, mock_ctx: Context
) -> None:
    with pytest.raises(ValueError, match="requires `campaign`"):
        await service.configure_campaign_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="CREATE",
        )


@pytest.mark.asyncio
async def test_update_requires_resource_name(
    service: CampaignLifecycleGoalService, mock_ctx: Context
) -> None:
    with pytest.raises(ValueError, match="requires `resource_name`"):
        await service.configure_campaign_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="UPDATE",
        )


def test_register_tools() -> None:
    mock_mcp = Mock()
    svc = register_campaign_lifecycle_goal_tools(mock_mcp)
    assert isinstance(svc, CampaignLifecycleGoalService)
    assert mock_mcp.tool.call_count == 1
