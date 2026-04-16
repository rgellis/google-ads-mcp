"""Tests for ContentCreatorInsightsService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.audiences.content_creator_insights_service import (
    ContentCreatorInsightsService,
    register_content_creator_insights_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ContentCreatorInsightsService:
    """Create a ContentCreatorInsightsService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.audiences.content_creator_insights_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ContentCreatorInsightsService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_generate_creator_insights(
    service: ContentCreatorInsightsService,
    mock_ctx: Context,
) -> None:
    """Test generating creator insights."""
    mock_client = service.client
    mock_client.generate_creator_insights.return_value = Mock()  # type: ignore

    expected_result = {"creator_insights": []}

    with patch(
        "src.services.audiences.content_creator_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_creator_insights(
            ctx=mock_ctx,
            customer_id="1234567890",
            country_locations=["geoTargetConstants/2840"],
        )

    assert result == expected_result
    mock_client.generate_creator_insights.assert_called_once()  # type: ignore
    call_args = mock_client.generate_creator_insights.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"


@pytest.mark.asyncio
async def test_generate_creator_insights_multiple_locations(
    service: ContentCreatorInsightsService,
    mock_ctx: Context,
) -> None:
    """Test generating creator insights with multiple locations."""
    mock_client = service.client
    mock_client.generate_creator_insights.return_value = Mock()  # type: ignore

    expected_result = {"creator_insights": []}

    with patch(
        "src.services.audiences.content_creator_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_creator_insights(
            ctx=mock_ctx,
            customer_id="1234567890",
            country_locations=["geoTargetConstants/2840", "geoTargetConstants/2826"],
        )

    assert result == expected_result
    mock_client.generate_creator_insights.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_generate_creator_insights_error(
    service: ContentCreatorInsightsService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when generating creator insights fails."""
    mock_client = service.client
    mock_client.generate_creator_insights.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.generate_creator_insights(
            ctx=mock_ctx,
            customer_id="1234567890",
            country_locations=["geoTargetConstants/2840"],
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_trending_insights(
    service: ContentCreatorInsightsService,
    mock_ctx: Context,
) -> None:
    """Test generating trending insights."""
    mock_client = service.client
    mock_client.generate_trending_insights.return_value = Mock()  # type: ignore

    expected_result = {"trending_insights": []}

    with patch(
        "src.services.audiences.content_creator_insights_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_trending_insights(
            ctx=mock_ctx,
            customer_id="1234567890",
            country_location="geoTargetConstants/2840",
        )

    assert result == expected_result
    mock_client.generate_trending_insights.assert_called_once()  # type: ignore
    call_args = mock_client.generate_trending_insights.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"


@pytest.mark.asyncio
async def test_generate_trending_insights_error(
    service: ContentCreatorInsightsService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when generating trending insights fails."""
    mock_client = service.client
    mock_client.generate_trending_insights.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.generate_trending_insights(
            ctx=mock_ctx,
            customer_id="1234567890",
            country_location="geoTargetConstants/2840",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_content_creator_insights_tools(mock_mcp)
    assert isinstance(svc, ContentCreatorInsightsService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
