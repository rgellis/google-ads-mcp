"""Tests for RecommendationSubscriptionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.planning.recommendation_subscription_service import (
    RecommendationSubscriptionService,
    register_recommendation_subscription_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> RecommendationSubscriptionService:
    """Create a RecommendationSubscriptionService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.planning.recommendation_subscription_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = RecommendationSubscriptionService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_subscription(
    service: RecommendationSubscriptionService, mock_ctx: Context
) -> None:
    """Test creating a recommendation subscription."""
    mock_client = service.client
    mock_client.mutate_recommendation_subscription.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/recommendationSubscriptions/1"}
        ]
    }

    with patch(
        "src.services.planning.recommendation_subscription_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.create_subscription(
            ctx=mock_ctx,
            customer_id="1234567890",
            recommendation_type="CAMPAIGN_BUDGET",
        )

    assert result == expected_result
    mock_client.mutate_recommendation_subscription.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_recommendation_subscription.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1


@pytest.mark.asyncio
async def test_update_subscription(
    service: RecommendationSubscriptionService, mock_ctx: Context
) -> None:
    """Test updating a recommendation subscription."""
    mock_client = service.client
    mock_client.mutate_recommendation_subscription.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/recommendationSubscriptions/1"}
        ]
    }
    resource_name = "customers/1234567890/recommendationSubscriptions/1"

    with patch(
        "src.services.planning.recommendation_subscription_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.update_subscription(
            ctx=mock_ctx,
            customer_id="1234567890",
            subscription_resource_name=resource_name,
            recommendation_type="KEYWORD",
        )

    assert result == expected_result
    mock_client.mutate_recommendation_subscription.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_recommendation_subscription.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert operation.update.resource_name == resource_name
    assert "type" in operation.update_mask.paths


@pytest.mark.asyncio
async def test_create_subscription_error(
    service: RecommendationSubscriptionService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in create_subscription."""
    mock_client = service.client
    mock_client.mutate_recommendation_subscription.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.create_subscription(
            ctx=mock_ctx,
            customer_id="1234567890",
            recommendation_type="CAMPAIGN_BUDGET",
        )

    assert "Failed to create recommendation subscription" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_subscription_error(
    service: RecommendationSubscriptionService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in update_subscription."""
    mock_client = service.client
    mock_client.mutate_recommendation_subscription.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.update_subscription(
            ctx=mock_ctx,
            customer_id="1234567890",
            subscription_resource_name="customers/1234567890/recommendationSubscriptions/1",
        )

    assert "Failed to update recommendation subscription" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_recommendation_subscription_tools(mock_mcp)
    assert isinstance(svc, RecommendationSubscriptionService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert set(tool_names) == {
        "create_recommendation_subscription",
        "update_recommendation_subscription",
    }
