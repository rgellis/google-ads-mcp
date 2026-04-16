"""Tests for CustomConversionGoalService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.conversions.custom_conversion_goal_service import (
    CustomConversionGoalService,
    register_custom_conversion_goal_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomConversionGoalService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.conversions.custom_conversion_goal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomConversionGoalService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_mutate_custom_conversion_goals(
    service: CustomConversionGoalService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_custom_conversion_goals.return_value = Mock()
    with patch(
        "src.services.conversions.custom_conversion_goal_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.mutate_custom_conversion_goals(
            ctx=mock_ctx, customer_id="1234567890", operations=[Mock()]
        )
    assert result == {"results": []}
    mock_client.mutate_custom_conversion_goals.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_custom_conversion_goal_tools(mock_mcp)
    assert isinstance(service, CustomConversionGoalService)
    assert mock_mcp.tool.call_count > 0
