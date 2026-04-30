"""Tests for Google Ads Conversion Goal Campaign Config Service"""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.enums.types.goal_config_level import GoalConfigLevelEnum
from google.ads.googleads.v23.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v23.services.types.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigOperation,
    MutateConversionGoalCampaignConfigsResponse,
    MutateConversionGoalCampaignConfigResult,
)

from src.services.conversions.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigService,
    create_conversion_goal_campaign_config_tools,
)


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock service client"""
    return Mock()


@pytest.fixture
def conversion_goal_campaign_config_service(
    mock_service_client: Any,
) -> ConversionGoalCampaignConfigService:
    """Create ConversionGoalCampaignConfigService instance with mock client"""
    service = ConversionGoalCampaignConfigService()
    service._client = mock_service_client  # type: ignore
    return service


@pytest.mark.asyncio
async def test_mutate_conversion_goal_campaign_configs(
    conversion_goal_campaign_config_service: ConversionGoalCampaignConfigService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test mutating conversion goal campaign configs"""
    customer_id = "1234567890"
    operations = [ConversionGoalCampaignConfigOperation()]

    mock_response = MutateConversionGoalCampaignConfigsResponse(
        results=[
            MutateConversionGoalCampaignConfigResult(
                resource_name="customers/1234567890/conversionGoalCampaignConfigs/123"
            )
        ]
    )
    mock_service_client.mutate_conversion_goal_campaign_configs.return_value = (
        mock_response  # type: ignore
    )

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/conversionGoalCampaignConfigs/123"}
        ]
    }

    with patch(
        "src.services.conversions.conversion_goal_campaign_config_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await conversion_goal_campaign_config_service.mutate_conversion_goal_campaign_configs(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            validate_only=False,
        )

    assert response == expected_result

    call_args = mock_service_client.mutate_conversion_goal_campaign_configs.call_args  # type: ignore
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.operations == operations
    assert request.validate_only == False


def test_update_conversion_goal_campaign_config_operation(
    conversion_goal_campaign_config_service: ConversionGoalCampaignConfigService,
) -> None:
    """Test creating conversion goal campaign config operation for update"""
    resource_name = "customers/1234567890/conversionGoalCampaignConfigs/123"
    goal_config_level = GoalConfigLevelEnum.GoalConfigLevel.CAMPAIGN
    custom_conversion_goal = "customers/1234567890/customConversionGoals/456"

    operation = conversion_goal_campaign_config_service.update_conversion_goal_campaign_config_operation(
        resource_name=resource_name,
        goal_config_level=goal_config_level,
        custom_conversion_goal=custom_conversion_goal,
    )

    assert isinstance(operation, ConversionGoalCampaignConfigOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.goal_config_level == goal_config_level
    assert operation.update.custom_conversion_goal == custom_conversion_goal
    assert set(operation.update_mask.paths) == {
        "goal_config_level",
        "custom_conversion_goal",
    }


def test_update_conversion_goal_campaign_config_operation_partial(
    conversion_goal_campaign_config_service: ConversionGoalCampaignConfigService,
) -> None:
    """Test creating conversion goal campaign config operation for partial update"""
    resource_name = "customers/1234567890/conversionGoalCampaignConfigs/123"
    goal_config_level = GoalConfigLevelEnum.GoalConfigLevel.CUSTOMER

    operation = conversion_goal_campaign_config_service.update_conversion_goal_campaign_config_operation(
        resource_name=resource_name, goal_config_level=goal_config_level
    )

    assert isinstance(operation, ConversionGoalCampaignConfigOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.goal_config_level == goal_config_level
    assert operation.update_mask.paths == ["goal_config_level"]


@pytest.mark.asyncio
async def test_mutate_tool_routes_response_content_type(
    conversion_goal_campaign_config_service: ConversionGoalCampaignConfigService,
    mock_ctx: Context,
) -> None:
    """Phase 10 coverage gap: tool wrapper now exposes response_content_type
    (the request proto supports it; the wrapper had been hiding it)."""
    tools = create_conversion_goal_campaign_config_tools(
        conversion_goal_campaign_config_service
    )
    mutate_tool = tools[0]  # mutate_conversion_goal_campaign_configs

    with patch.object(
        conversion_goal_campaign_config_service,
        "mutate_conversion_goal_campaign_configs",
        new=AsyncMock(return_value={"results": []}),
    ) as mock_call:
        await mutate_tool(
            ctx=mock_ctx,
            customer_id="1234567890",
            operations=[
                {
                    "operation_type": "update",
                    "resource_name": "customers/1234567890/conversionGoalCampaignConfigs/123",
                    "goal_config_level": "CAMPAIGN",
                }
            ],
            response_content_type="MUTABLE_RESOURCE",
        )

        kwargs = mock_call.call_args.kwargs
        assert (
            kwargs["response_content_type"]
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )


@pytest.mark.asyncio
async def test_update_tool_routes_response_content_type(
    conversion_goal_campaign_config_service: ConversionGoalCampaignConfigService,
    mock_ctx: Context,
) -> None:
    """Same coverage gap on the single-resource update tool wrapper."""
    tools = create_conversion_goal_campaign_config_tools(
        conversion_goal_campaign_config_service
    )
    update_tool = tools[1]  # update_conversion_goal_campaign_config

    with patch.object(
        conversion_goal_campaign_config_service,
        "mutate_conversion_goal_campaign_configs",
        new=AsyncMock(return_value={"results": []}),
    ) as mock_call:
        await update_tool(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/conversionGoalCampaignConfigs/123",
            goal_config_level="CAMPAIGN",
            response_content_type="MUTABLE_RESOURCE",
        )

        kwargs = mock_call.call_args.kwargs
        assert (
            kwargs["response_content_type"]
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )
