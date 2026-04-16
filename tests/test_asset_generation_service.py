"""Tests for AssetGenerationService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.assets.asset_generation_service import (
    AssetGenerationService,
    register_asset_generation_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> AssetGenerationService:
    """Create an AssetGenerationService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.assets.asset_generation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = AssetGenerationService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_generate_text(
    service: AssetGenerationService,
    mock_ctx: Context,
) -> None:
    """Test generating text assets."""
    mock_client = service.client
    mock_client.generate_text.return_value = Mock()  # type: ignore

    expected_result = {"assets": [{"text_asset": {"text": "Great Deals Online"}}]}

    with patch(
        "src.services.assets.asset_generation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_text(
            ctx=mock_ctx,
            customer_id="1234567890",
            final_url="https://example.com",
            asset_field_types=["HEADLINE", "DESCRIPTION"],
        )

    assert result == expected_result
    mock_client.generate_text.assert_called_once()  # type: ignore
    call_args = mock_client.generate_text.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert request.final_url == "https://example.com"


@pytest.mark.asyncio
async def test_generate_text_with_keywords(
    service: AssetGenerationService,
    mock_ctx: Context,
) -> None:
    """Test generating text assets with keywords."""
    mock_client = service.client
    mock_client.generate_text.return_value = Mock()  # type: ignore

    expected_result = {"assets": [{"text_asset": {"text": "Buy Shoes Online"}}]}

    with patch(
        "src.services.assets.asset_generation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_text(
            ctx=mock_ctx,
            customer_id="1234567890",
            final_url="https://example.com/shoes",
            asset_field_types=["HEADLINE"],
            keywords=["running shoes", "athletic footwear"],
            advertising_channel_type="SEARCH",
        )

    assert result == expected_result
    mock_client.generate_text.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_generate_text_error(
    service: AssetGenerationService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when generating text fails."""
    mock_client = service.client
    mock_client.generate_text.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.generate_text(
            ctx=mock_ctx,
            customer_id="1234567890",
            final_url="https://example.com",
            asset_field_types=["HEADLINE"],
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_images(
    service: AssetGenerationService,
    mock_ctx: Context,
) -> None:
    """Test generating image assets."""
    mock_client = service.client
    mock_client.generate_images.return_value = Mock()  # type: ignore

    expected_result = {"assets": [{"image_asset": {"data": "base64encodeddata"}}]}

    with patch(
        "src.services.assets.asset_generation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_images(
            ctx=mock_ctx,
            customer_id="1234567890",
            final_url="https://example.com",
            asset_field_types=["MARKETING_IMAGE"],
        )

    assert result == expected_result
    mock_client.generate_images.assert_called_once()  # type: ignore
    call_args = mock_client.generate_images.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"


@pytest.mark.asyncio
async def test_generate_images_error(
    service: AssetGenerationService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when generating images fails."""
    mock_client = service.client
    mock_client.generate_images.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.generate_images(
            ctx=mock_ctx,
            customer_id="1234567890",
            final_url="https://example.com",
            asset_field_types=["MARKETING_IMAGE"],
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_asset_generation_tools(mock_mcp)
    assert isinstance(svc, AssetGenerationService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
