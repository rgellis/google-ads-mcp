"""Tests for Google Ads Brand Suggestion Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.enums.types.brand_state import BrandStateEnum
from google.ads.googleads.v23.services.types.brand_suggestion_service import (
    BrandSuggestion,
    SuggestBrandsResponse,
)

from src.services.planning.brand_suggestion_service import BrandSuggestionService


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock BrandSuggestionServiceClient"""
    return Mock()


@pytest.fixture
def brand_suggestion_service(mock_service_client: Any) -> BrandSuggestionService:
    """Create BrandSuggestionService instance with mock client"""
    service = BrandSuggestionService()
    service._client = mock_service_client  # type: ignore
    return service


@pytest.mark.asyncio
async def test_suggest_brands(
    brand_suggestion_service: BrandSuggestionService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting brands"""
    customer_id = "1234567890"
    brand_prefix = "nike"
    selected_brands = ["brand123"]

    mock_response = SuggestBrandsResponse(
        brands=[
            BrandSuggestion(
                id="brand456",
                name="Nike",
                urls=["https://www.nike.com"],
                state=BrandStateEnum.BrandState.APPROVED,
            ),
            BrandSuggestion(
                id="brand789",
                name="Nike Air",
                urls=["https://www.nike.com/air"],
                state=BrandStateEnum.BrandState.APPROVED,
            ),
        ]
    )
    mock_service_client.suggest_brands.return_value = mock_response  # type: ignore

    expected_result = {
        "brands": [
            {"id": "brand456", "name": "Nike"},
            {"id": "brand789", "name": "Nike Air"},
        ]
    }

    with patch(
        "src.services.planning.brand_suggestion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await brand_suggestion_service.suggest_brands(
            ctx=mock_ctx,
            customer_id=customer_id,
            brand_prefix=brand_prefix,
            selected_brands=selected_brands,
        )

    assert response == expected_result
    mock_service_client.suggest_brands.assert_called_once()  # type: ignore

    call_args = mock_service_client.suggest_brands.call_args  # type: ignore
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.brand_prefix == brand_prefix
    assert request.selected_brands == selected_brands


@pytest.mark.asyncio
async def test_suggest_brands_without_selected_brands(
    brand_suggestion_service: BrandSuggestionService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test suggesting brands without selected brands"""
    customer_id = "1234567890"
    brand_prefix = "adidas"

    mock_response = SuggestBrandsResponse(
        brands=[
            BrandSuggestion(
                id="brand101",
                name="Adidas",
                urls=["https://www.adidas.com"],
                state=BrandStateEnum.BrandState.APPROVED,
            )
        ]
    )
    mock_service_client.suggest_brands.return_value = mock_response  # type: ignore

    expected_result = {"brands": [{"id": "brand101", "name": "Adidas"}]}

    with patch(
        "src.services.planning.brand_suggestion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await brand_suggestion_service.suggest_brands(
            ctx=mock_ctx, customer_id=customer_id, brand_prefix=brand_prefix
        )

    assert response == expected_result

    call_args = mock_service_client.suggest_brands.call_args  # type: ignore
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.brand_prefix == brand_prefix
    assert request.selected_brands == []
