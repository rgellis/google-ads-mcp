"""Tests for Google Ads Conversion Goal Campaign Config Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.enums.types.goal_config_level import GoalConfigLevelEnum
from google.ads.googleads.v23.services.types.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigOperation,
    MutateConversionGoalCampaignConfigsResponse,
    MutateConversionGoalCampaignConfigResult,
)

from src.services.conversions.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigService,
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
