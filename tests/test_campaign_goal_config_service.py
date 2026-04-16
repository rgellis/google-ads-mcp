"""Tests for CampaignGoalConfigService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.campaign.campaign_goal_config_service import (
    CampaignGoalConfigService,
    register_campaign_goal_config_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CampaignGoalConfigService:
    """Create a CampaignGoalConfigService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.campaign.campaign_goal_config_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CampaignGoalConfigService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_mutate_campaign_goal_configs_create(
    service: CampaignGoalConfigService, mock_ctx: Context
) -> None:
    """Test creating a campaign goal config."""
    mock_client = service.client
    mock_client.mutate_campaign_goal_configs.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaignGoalConfigs/111~1"}]
    }

    with patch(
        "src.services.campaign.campaign_goal_config_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_campaign_goal_configs(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_resource_name="customers/1234567890/campaigns/111",
            goal_resource_name="customers/1234567890/goals/1",
            operation_type="create",
        )

    assert result == expected_result
    mock_client.mutate_campaign_goal_configs.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_campaign_goal_configs.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    assert request.operations[0].create.campaign == "customers/1234567890/campaigns/111"
    assert request.operations[0].create.goal == "customers/1234567890/goals/1"


@pytest.mark.asyncio
async def test_mutate_campaign_goal_configs_update(
    service: CampaignGoalConfigService, mock_ctx: Context
) -> None:
    """Test updating a campaign goal config."""
    mock_client = service.client
    mock_client.mutate_campaign_goal_configs.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaignGoalConfigs/111~1"}]
    }
    config_rn = "customers/1234567890/campaignGoalConfigs/111~1"

    with patch(
        "src.services.campaign.campaign_goal_config_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_campaign_goal_configs(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_resource_name=config_rn,
            operation_type="update",
        )

    assert result == expected_result
    mock_client.mutate_campaign_goal_configs.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_campaign_goal_configs.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].update.resource_name == config_rn


@pytest.mark.asyncio
async def test_mutate_campaign_goal_configs_remove(
    service: CampaignGoalConfigService, mock_ctx: Context
) -> None:
    """Test removing a campaign goal config."""
    mock_client = service.client
    mock_client.mutate_campaign_goal_configs.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaignGoalConfigs/111~1"}]
    }
    config_rn = "customers/1234567890/campaignGoalConfigs/111~1"

    with patch(
        "src.services.campaign.campaign_goal_config_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_campaign_goal_configs(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_resource_name=config_rn,
            operation_type="remove",
        )

    assert result == expected_result
    call_args = mock_client.mutate_campaign_goal_configs.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].remove == config_rn


@pytest.mark.asyncio
async def test_mutate_campaign_goal_configs_error(
    service: CampaignGoalConfigService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in mutate_campaign_goal_configs."""
    mock_client = service.client
    mock_client.mutate_campaign_goal_configs.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.mutate_campaign_goal_configs(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_resource_name="customers/1234567890/campaigns/111",
            operation_type="create",
        )

    assert "Failed to mutate campaign goal config" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_campaign_goal_config_tools(mock_mcp)
    assert isinstance(svc, CampaignGoalConfigService)
    assert mock_mcp.tool.call_count == 1  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert tool_names == ["mutate_campaign_goal_config"]
