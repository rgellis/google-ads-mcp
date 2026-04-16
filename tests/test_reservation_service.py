"""Tests for ReservationService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.campaign.reservation_service import (
    ReservationService,
    register_reservation_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ReservationService:
    """Create a ReservationService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.campaign.reservation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ReservationService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_quote_campaigns(
    service: ReservationService,
    mock_ctx: Context,
) -> None:
    """Test getting a quote for reservation campaigns."""
    mock_client = service.client
    mock_client.quote_campaigns.return_value = Mock()  # type: ignore

    expected_result = {"quote": {"total_budget_micros": 1000000000}}

    with patch(
        "src.services.campaign.reservation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.quote_campaigns(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert result == expected_result
    mock_client.quote_campaigns.assert_called_once()  # type: ignore
    call_args = mock_client.quote_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"


@pytest.mark.asyncio
async def test_quote_campaigns_error(
    service: ReservationService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when quoting campaigns fails."""
    mock_client = service.client
    mock_client.quote_campaigns.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.quote_campaigns(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_book_campaigns(
    service: ReservationService,
    mock_ctx: Context,
) -> None:
    """Test booking reservation campaigns."""
    mock_client = service.client
    mock_client.book_campaigns.return_value = Mock()  # type: ignore

    expected_result = {
        "booked_campaigns": [{"campaign": "customers/1234567890/campaigns/111"}]
    }

    with patch(
        "src.services.campaign.reservation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.book_campaigns(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert result == expected_result
    mock_client.book_campaigns.assert_called_once()  # type: ignore
    call_args = mock_client.book_campaigns.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"


@pytest.mark.asyncio
async def test_book_campaigns_error(
    service: ReservationService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when booking campaigns fails."""
    mock_client = service.client
    mock_client.book_campaigns.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.book_campaigns(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_reservation_tools(mock_mcp)
    assert isinstance(svc, ReservationService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
