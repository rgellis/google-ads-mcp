"""Tests for TravelAssetSuggestionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.planning.travel_asset_suggestion_service import (
    TravelAssetSuggestionService,
    register_travel_asset_suggestion_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> TravelAssetSuggestionService:
    """Create a TravelAssetSuggestionService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.planning.travel_asset_suggestion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = TravelAssetSuggestionService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_suggest_travel_assets(
    service: TravelAssetSuggestionService,
    mock_ctx: Context,
) -> None:
    """Test suggesting travel assets for place IDs."""
    mock_client = service.client
    mock_client.suggest_travel_assets.return_value = Mock()  # type: ignore

    expected_result = {"hotel_asset_suggestions": []}

    with patch(
        "src.services.planning.travel_asset_suggestion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.suggest_travel_assets(
            ctx=mock_ctx,
            customer_id="1234567890",
            place_ids=["ChIJN1t_tDeuEmsRUsoyG83frY4", "ChIJP3Sa8ziYEmsRUKgyFmh9AQM"],
        )

    assert result == expected_result
    mock_client.suggest_travel_assets.assert_called_once()  # type: ignore
    call_args = mock_client.suggest_travel_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert list(request.place_ids) == [
        "ChIJN1t_tDeuEmsRUsoyG83frY4",
        "ChIJP3Sa8ziYEmsRUKgyFmh9AQM",
    ]


@pytest.mark.asyncio
async def test_suggest_travel_assets_with_language(
    service: TravelAssetSuggestionService,
    mock_ctx: Context,
) -> None:
    """Test suggesting travel assets with language option."""
    mock_client = service.client
    mock_client.suggest_travel_assets.return_value = Mock()  # type: ignore

    expected_result = {"hotel_asset_suggestions": []}

    with patch(
        "src.services.planning.travel_asset_suggestion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.suggest_travel_assets(
            ctx=mock_ctx,
            customer_id="1234567890",
            place_ids=["ChIJN1t_tDeuEmsRUsoyG83frY4"],
            language_option="en",
        )

    assert result == expected_result
    call_args = mock_client.suggest_travel_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.language_option == "en"


@pytest.mark.asyncio
async def test_suggest_travel_assets_error(
    service: TravelAssetSuggestionService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when suggesting travel assets fails."""
    mock_client = service.client
    mock_client.suggest_travel_assets.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.suggest_travel_assets(
            ctx=mock_ctx,
            customer_id="1234567890",
            place_ids=["ChIJN1t_tDeuEmsRUsoyG83frY4"],
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_travel_asset_suggestion_tools(mock_mcp)
    assert isinstance(svc, TravelAssetSuggestionService)
    assert mock_mcp.tool.call_count == 1  # type: ignore
