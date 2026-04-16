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


@pytest.mark.asyncio
async def test_generate_text_with_freeform_prompt(
    service: AssetGenerationService,
    mock_ctx: Context,
) -> None:
    """Test generating text assets from a freeform prompt."""
    mock_client = service.client
    mock_client.generate_text.return_value = Mock()  # type: ignore

    expected_result = {"assets": [{"text_asset": {"text": "AI Generated"}}]}

    with patch(
        "src.services.assets.asset_generation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_text(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_field_types=["HEADLINE"],
            freeform_prompt="Write headlines for a shoe store",
        )

    assert result == expected_result
    call_args = mock_client.generate_text.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.freeform_prompt == "Write headlines for a shoe store"
    assert request.final_url == ""  # not set


@pytest.mark.asyncio
async def test_generate_text_with_existing_context(
    service: AssetGenerationService,
    mock_ctx: Context,
) -> None:
    """Test generating text with existing asset group context."""
    mock_client = service.client
    mock_client.generate_text.return_value = Mock()  # type: ignore

    with patch(
        "src.services.assets.asset_generation_service.serialize_proto_message",
        return_value={"assets": []},
    ):
        result = await service.generate_text(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_field_types=["DESCRIPTION"],
            final_url="https://example.com",
            existing_asset_group="customers/1234567890/assetGroups/111",
        )

    call_args = mock_client.generate_text.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.existing_generation_context.existing_asset_group
        == "customers/1234567890/assetGroups/111"
    )


@pytest.mark.asyncio
async def test_generate_images_with_freeform_prompt(
    service: AssetGenerationService,
    mock_ctx: Context,
) -> None:
    """Test generating images from a freeform prompt."""
    mock_client = service.client
    mock_client.generate_images.return_value = Mock()  # type: ignore

    with patch(
        "src.services.assets.asset_generation_service.serialize_proto_message",
        return_value={"assets": []},
    ):
        result = await service.generate_images(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_field_types=["MARKETING_IMAGE"],
            freeform_prompt="A running shoe on a mountain trail",
        )

    call_args = mock_client.generate_images.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.freeform_generation.freeform_prompt
        == "A running shoe on a mountain trail"
    )


@pytest.mark.asyncio
async def test_generate_images_with_product_recontext(
    service: AssetGenerationService,
    mock_ctx: Context,
) -> None:
    """Test generating images with product recontextualization."""
    mock_client = service.client
    mock_client.generate_images.return_value = Mock()  # type: ignore

    with patch(
        "src.services.assets.asset_generation_service.serialize_proto_message",
        return_value={"assets": []},
    ):
        result = await service.generate_images(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_field_types=["MARKETING_IMAGE"],
            product_recontext_prompt="Product on a beach",
            product_recontext_source_images=[b"fake_image_bytes"],
        )

    call_args = mock_client.generate_images.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.product_recontext_generation.prompt == "Product on a beach"
    assert len(request.product_recontext_generation.source_images) == 1


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_asset_generation_tools(mock_mcp)
    assert isinstance(svc, AssetGenerationService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
