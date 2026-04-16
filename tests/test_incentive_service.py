"""Tests for IncentiveService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.account.incentive_service import (
    IncentiveService,
    register_incentive_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> IncentiveService:
    """Create an IncentiveService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.account.incentive_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = IncentiveService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_fetch_incentive(
    service: IncentiveService,
    mock_ctx: Context,
) -> None:
    """Test fetching incentive offers."""
    mock_client = service.client
    mock_client.fetch_incentive.return_value = Mock()  # type: ignore

    expected_result = {
        "incentives": [{"incentive_id": 12345, "title": "Spend $500, Get $150"}]
    }

    with patch(
        "src.services.account.incentive_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.fetch_incentive(
            ctx=mock_ctx,
            language_code="en",
            country_code="US",
            email="advertiser@example.com",
        )

    assert result == expected_result
    mock_client.fetch_incentive.assert_called_once()  # type: ignore
    call_args = mock_client.fetch_incentive.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.language_code == "en"
    assert request.country_code == "US"
    assert request.email == "advertiser@example.com"


@pytest.mark.asyncio
async def test_fetch_incentive_error(
    service: IncentiveService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when fetching incentive fails."""
    mock_client = service.client
    mock_client.fetch_incentive.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.fetch_incentive(
            ctx=mock_ctx,
            language_code="en",
            country_code="US",
            email="advertiser@example.com",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_apply_incentive(
    service: IncentiveService,
    mock_ctx: Context,
) -> None:
    """Test applying an incentive to a customer account."""
    mock_client = service.client
    mock_client.apply_incentive.return_value = Mock()  # type: ignore

    expected_result = {"applied_incentive": {"incentive_id": 12345}}

    with patch(
        "src.services.account.incentive_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.apply_incentive(
            ctx=mock_ctx,
            customer_id="1234567890",
            selected_incentive_id=12345,
            country_code="US",
        )

    assert result == expected_result
    mock_client.apply_incentive.assert_called_once()  # type: ignore
    call_args = mock_client.apply_incentive.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert request.selected_incentive_id == 12345
    assert request.country_code == "US"


@pytest.mark.asyncio
async def test_apply_incentive_error(
    service: IncentiveService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when applying incentive fails."""
    mock_client = service.client
    mock_client.apply_incentive.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.apply_incentive(
            ctx=mock_ctx,
            customer_id="1234567890",
            selected_incentive_id=12345,
            country_code="US",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_fetch_incentive_with_type(
    service: IncentiveService,
    mock_ctx: Context,
) -> None:
    """Test incentive_type parameter reaches the request."""
    mock_client = service.client
    mock_client.fetch_incentive.return_value = Mock()  # type: ignore

    with patch(
        "src.services.account.incentive_service.serialize_proto_message",
        return_value={"incentives": []},
    ):
        await service.fetch_incentive(
            ctx=mock_ctx,
            language_code="en",
            country_code="US",
            email="test@example.com",
            incentive_type="ACQUISITION",
        )

    call_args = mock_client.fetch_incentive.call_args  # type: ignore
    request = call_args[1]["request"]
    # The type_ should be set to ACQUISITION enum value
    assert request.type_ != 0  # Not UNSPECIFIED


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_incentive_tools(mock_mcp)
    assert isinstance(svc, IncentiveService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
