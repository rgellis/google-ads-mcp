"""Tests for BiddingSeasonalityAdjustmentService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.bidding.bidding_seasonality_adjustment_service import (
    BiddingSeasonalityAdjustmentService,
    register_bidding_seasonality_adjustment_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> BiddingSeasonalityAdjustmentService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.bidding.bidding_seasonality_adjustment_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = BiddingSeasonalityAdjustmentService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_seasonality_adjustment(
    service: BiddingSeasonalityAdjustmentService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_bidding_seasonality_adjustments.return_value = Mock()
    with patch(
        "src.services.bidding.bidding_seasonality_adjustment_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.create_bidding_seasonality_adjustment(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Holiday Season",
            scope="CUSTOMER",
            start_date_time="2026-12-20 00:00:00",
            end_date_time="2026-12-31 23:59:59",
            conversion_rate_modifier=1.5,
        )
    assert result == {"results": []}
    mock_client.mutate_bidding_seasonality_adjustments.assert_called_once()


@pytest.mark.asyncio
async def test_remove_seasonality_adjustment(
    service: BiddingSeasonalityAdjustmentService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_bidding_seasonality_adjustments.return_value = Mock()
    with patch(
        "src.services.bidding.bidding_seasonality_adjustment_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_bidding_seasonality_adjustment(
            ctx=mock_ctx,
            customer_id="1234567890",
            adjustment_resource_name="customers/1234567890/biddingSeasonalityAdjustments/1",
        )
    assert result == {"results": []}


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_bidding_seasonality_adjustment_tools(mock_mcp)
    assert isinstance(service, BiddingSeasonalityAdjustmentService)
    assert mock_mcp.tool.call_count > 0
