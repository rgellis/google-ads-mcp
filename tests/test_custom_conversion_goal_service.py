"""Tests for CustomConversionGoalService."""

from typing import Any
from unittest.mock import Mock
import pytest
from src.services.conversions.custom_conversion_goal_service import (
    CustomConversionGoalService,
    register_custom_conversion_goal_tools,
)
from google.ads.googleads.v23.services.types.custom_conversion_goal_service import (
    CustomConversionGoalOperation,
)


@pytest.fixture
def service() -> CustomConversionGoalService:
    mock_client = Mock()
    svc = CustomConversionGoalService()
    svc._client = mock_client  # type: ignore
    return svc


def test_mutate_custom_conversion_goals(service: CustomConversionGoalService) -> None:
    mock_client = service.client
    mock_response = Mock()
    mock_client.mutate_custom_conversion_goals.return_value = mock_response
    result = service.mutate_custom_conversion_goals(
        customer_id="1234567890",
        operations=[CustomConversionGoalOperation()],
    )
    assert result == mock_response
    mock_client.mutate_custom_conversion_goals.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    register_custom_conversion_goal_tools(mock_mcp)
    assert mock_mcp.tool.call_count > 0
