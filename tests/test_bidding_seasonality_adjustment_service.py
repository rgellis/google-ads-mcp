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


@pytest.mark.asyncio
async def test_create_bidding_seasonality_adjustment(
    service: BiddingSeasonalityAdjustmentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a bidding seasonality adjustment."""
    mock_client = service.client
    mock_client.mutate_bidding_seasonality_adjustments.return_value = Mock()
    expected = {
        "results": [
            {"resource_name": "customers/1234567890/biddingSeasonalityAdjustments/1"}
        ]
    }
    with patch(
        "src.services.bidding.bidding_seasonality_adjustment_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await service.create_bidding_seasonality_adjustment(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Summer Sale",
            scope="CUSTOMER",
            start_date_time="2026-06-01 00:00:00",
            end_date_time="2026-06-15 23:59:59",
            conversion_rate_modifier=1.3,
        )
    assert result == expected
    mock_client.mutate_bidding_seasonality_adjustments.assert_called_once()


@pytest.mark.asyncio
async def test_list_bidding_seasonality_adjustments(
    service: BiddingSeasonalityAdjustmentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing bidding seasonality adjustments."""
    from google.ads.googleads.v23.services.services.google_ads_service import (
        GoogleAdsServiceClient,
    )

    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result
    row = Mock()
    row.bidding_seasonality_adjustment = Mock()
    row.bidding_seasonality_adjustment.resource_name = (
        "customers/1234567890/biddingSeasonalityAdjustments/1"
    )
    row.bidding_seasonality_adjustment.seasonality_adjustment_id = 1
    row.bidding_seasonality_adjustment.scope = Mock()
    row.bidding_seasonality_adjustment.scope.name = "CUSTOMER"
    row.bidding_seasonality_adjustment.status = Mock()
    row.bidding_seasonality_adjustment.status.name = "ENABLED"
    row.bidding_seasonality_adjustment.name = "Holiday Season"
    row.bidding_seasonality_adjustment.description = "Holiday adjustment"
    row.bidding_seasonality_adjustment.start_date_time = "2026-12-20 00:00:00"
    row.bidding_seasonality_adjustment.end_date_time = "2026-12-31 23:59:59"
    row.bidding_seasonality_adjustment.conversion_rate_modifier = 1.5
    row.bidding_seasonality_adjustment.campaigns = []
    row.bidding_seasonality_adjustment.advertising_channel_types = []
    row.bidding_seasonality_adjustment.devices = []

    mock_google_ads_service.search.return_value = [row]

    def get_service_side_effect(service_name: str):  # type: ignore
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.bidding.bidding_seasonality_adjustment_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_bidding_seasonality_adjustments(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert len(result) == 1
    assert result[0]["name"] == "Holiday Season"
    assert result[0]["scope"] == "CUSTOMER"
    assert result[0]["conversion_rate_modifier"] == 1.5
    mock_google_ads_service.search.assert_called_once()


@pytest.mark.asyncio
async def test_remove_bidding_seasonality_adjustment(
    service: BiddingSeasonalityAdjustmentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a bidding seasonality adjustment."""
    mock_client = service.client
    mock_client.mutate_bidding_seasonality_adjustments.return_value = Mock()
    expected = {"results": []}
    with patch(
        "src.services.bidding.bidding_seasonality_adjustment_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await service.remove_bidding_seasonality_adjustment(
            ctx=mock_ctx,
            customer_id="1234567890",
            adjustment_resource_name="customers/1234567890/biddingSeasonalityAdjustments/1",
        )
    assert result == expected
    mock_client.mutate_bidding_seasonality_adjustments.assert_called_once()


@pytest.mark.asyncio
async def test_update_bidding_seasonality_adjustment(
    service: BiddingSeasonalityAdjustmentService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a bidding seasonality adjustment."""
    mock_client = service.client
    mock_client.mutate_bidding_seasonality_adjustments.return_value = Mock()
    expected = {
        "results": [
            {"resource_name": "customers/1234567890/biddingSeasonalityAdjustments/1"}
        ]
    }
    with patch(
        "src.services.bidding.bidding_seasonality_adjustment_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await service.update_bidding_seasonality_adjustment(
            ctx=mock_ctx,
            customer_id="1234567890",
            adjustment_resource_name="customers/1234567890/biddingSeasonalityAdjustments/1",
            name="Updated Holiday Season",
            conversion_rate_modifier=2.0,
        )
    assert result == expected
    mock_client.mutate_bidding_seasonality_adjustments.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_bidding_seasonality_adjustment_tools(mock_mcp)
    assert isinstance(service, BiddingSeasonalityAdjustmentService)
    assert mock_mcp.tool.call_count > 0
