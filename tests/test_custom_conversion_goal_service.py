"""Tests for CustomConversionGoalService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.services.types.custom_conversion_goal_service import (
    CustomConversionGoalOperation,
    MutateCustomConversionGoalsResponse,
    MutateCustomConversionGoalResult,
)

from src.services.conversions.custom_conversion_goal_service import (
    CustomConversionGoalService,
    register_custom_conversion_goal_tools,
)


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock service client"""
    return Mock()


@pytest.fixture
def service(mock_service_client: Any) -> CustomConversionGoalService:
    """Create CustomConversionGoalService instance with mock client"""
    svc = CustomConversionGoalService()
    svc._client = mock_service_client  # type: ignore
    return svc


@pytest.mark.asyncio
async def test_mutate_custom_conversion_goals(
    service: CustomConversionGoalService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test mutating custom conversion goals"""
    mock_response = MutateCustomConversionGoalsResponse(
        results=[
            MutateCustomConversionGoalResult(
                resource_name="customers/1234567890/customConversionGoals/123"
            )
        ]
    )
    mock_service_client.mutate_custom_conversion_goals.return_value = mock_response  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/customConversionGoals/123"}]
    }

    with patch(
        "src.services.conversions.custom_conversion_goal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_custom_conversion_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operations=[CustomConversionGoalOperation()],
        )

    assert result == expected_result
    mock_service_client.mutate_custom_conversion_goals.assert_called_once()  # type: ignore


def test_register_tools() -> None:
    """Test that register function returns service and registers tools"""
    mock_mcp = Mock()
    service = register_custom_conversion_goal_tools(mock_mcp)
    assert isinstance(service, CustomConversionGoalService)
    assert mock_mcp.tool.call_count > 0
