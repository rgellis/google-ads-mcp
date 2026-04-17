"""Tests for AssetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.enums.types.asset_type import AssetTypeEnum
from google.ads.googleads.v23.enums.types.mime_type import MimeTypeEnum
from google.ads.googleads.v23.services.services.asset_service import (
    AssetServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.asset_service import (
    MutateAssetsResponse,
)

from src.services.assets.asset_service import (
    AssetService,
    register_asset_tools,
)


@pytest.fixture
def asset_service(mock_sdk_client: Any) -> AssetService:
    """Create an AssetService instance with mocked dependencies."""
    # Mock AssetService client
    mock_asset_service_client = Mock(spec=AssetServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_asset_service_client  # type: ignore

    with patch(
        "src.services.assets.asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AssetService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_create_text_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a text asset."""
    # Arrange
    customer_id = "1234567890"
    text = "This is a test headline"
    name = "Test Text Asset"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/123"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.create_text_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            text=text,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == AssetTypeEnum.AssetType.TEXT
    assert operation.create.text_asset.text == text


@pytest.mark.asyncio
async def test_create_text_asset_without_name(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a text asset without explicit name."""
    # Arrange
    customer_id = "1234567890"
    text = "This is a very long test headline that should be truncated in the name"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/124"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/124"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.create_text_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            text=text,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]

    operation = request.operations[0]
    # Should use first 50 chars of text as name
    assert operation.create.name == f"Text: {text[:50]}"


@pytest.mark.asyncio
async def test_create_image_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an image asset."""
    # Arrange
    customer_id = "1234567890"
    image_data = b"fake_image_data"
    name = "Test Image Asset"
    mime_type = "image/jpeg"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/125"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/125"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.create_image_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            image_data=image_data,
            name=name,
            mime_type=mime_type,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == AssetTypeEnum.AssetType.IMAGE
    assert operation.create.image_asset.data == image_data
    assert operation.create.image_asset.mime_type == MimeTypeEnum.MimeType.IMAGE_JPEG


@pytest.mark.asyncio
async def test_create_youtube_video_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a YouTube video asset."""
    # Arrange
    customer_id = "1234567890"
    youtube_video_id = "dQw4w9WgXcQ"
    name = "Test Video Asset"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/126"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/126"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.create_youtube_video_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            youtube_video_id=youtube_video_id,
            name=name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.create.name == name
    assert operation.create.type_ == AssetTypeEnum.AssetType.YOUTUBE_VIDEO
    assert operation.create.youtube_video_asset.youtube_video_id == youtube_video_id


@pytest.mark.asyncio
async def test_search_assets(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test searching for assets."""
    # Arrange
    customer_id = "1234567890"
    asset_types = ["TEXT", "IMAGE"]
    limit = 10

    # Mock GoogleAdsService for search
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    mock_results = []
    for i in range(3):
        row = Mock()
        row.asset = Mock()
        row.asset.id = f"100{i}"
        row.asset.name = f"Asset {i}"
        row.asset.resource_name = f"customers/{customer_id}/assets/100{i}"

        if i == 0:
            # Use actual enum value
            row.asset.type_ = AssetTypeEnum.AssetType.TEXT
            row.asset.text_asset = Mock()
            row.asset.text_asset.text = "Text content"
        elif i == 1:
            row.asset.type_ = AssetTypeEnum.AssetType.IMAGE
            row.asset.image_asset = Mock()
            row.asset.image_asset.file_size = 12345
        else:
            row.asset.type_ = AssetTypeEnum.AssetType.YOUTUBE_VIDEO
            row.asset.youtube_video_asset = Mock()
            row.asset.youtube_video_asset.youtube_video_id = "abc123"

        mock_results.append(row)

    mock_google_ads_service.search.return_value = mock_results  # type: ignore

    # Update the mock to return GoogleAdsService when requested
    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return asset_service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    # Act
    with patch(
        "src.services.assets.asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await asset_service.search_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_types=asset_types,
            limit=limit,
        )

    # Assert
    assert len(result) == 3
    assert result[0]["asset_id"] == "1000"
    assert result[0]["type"] == "TEXT"
    assert result[0]["text"] == "Text content"
    assert result[1]["asset_id"] == "1001"
    assert result[1]["type"] == "IMAGE"
    assert result[1]["file_size"] == "12345"
    assert result[2]["asset_id"] == "1002"
    assert result[2]["type"] == "YOUTUBE_VIDEO"
    assert result[2]["youtube_video_id"] == "abc123"

    # Verify the search call
    mock_google_ads_service.search.assert_called_once()  # type: ignore
    call_args = mock_google_ads_service.search.call_args  # type: ignore
    assert call_args[1]["customer_id"] == customer_id
    query = call_args[1]["query"]
    assert "asset.type = 'TEXT'" in query
    assert "asset.type = 'IMAGE'" in query
    assert f"LIMIT {limit}" in query

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message="Found 3 assets",
    )


@pytest.mark.asyncio
async def test_error_handling(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"

    # Get the mocked asset service client and make it raise exception
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await asset_service.create_text_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            text="Test text",
        )

    assert "Failed to create text asset" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create text asset: Test Google Ads Exception",
    )


def test_mime_type_conversion() -> None:
    """Test MIME type conversion."""
    service = AssetService()

    # Test supported MIME types
    assert service.get_mime_type_enum("image/jpeg") == MimeTypeEnum.MimeType.IMAGE_JPEG
    assert service.get_mime_type_enum("image/png") == MimeTypeEnum.MimeType.IMAGE_PNG
    assert service.get_mime_type_enum("image/gif") == MimeTypeEnum.MimeType.IMAGE_GIF

    # Test case insensitive
    assert service.get_mime_type_enum("IMAGE/JPEG") == MimeTypeEnum.MimeType.IMAGE_JPEG

    # Test default fallback
    assert service.get_mime_type_enum("image/webp") == MimeTypeEnum.MimeType.IMAGE_JPEG


@pytest.mark.asyncio
async def test_update_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating an asset."""
    # Arrange
    customer_id = "1234567890"
    asset_id = "456"

    # Create mock response
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[
        0
    ].resource_name = f"customers/{customer_id}/assets/{asset_id}"

    # Get the mocked asset service client
    mock_asset_service_client = asset_service.client  # type: ignore
    mock_asset_service_client.mutate_assets.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [{"resource_name": f"customers/{customer_id}/assets/{asset_id}"}]
    }

    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await asset_service.update_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset_id=asset_id,
            name="New Name",
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_asset_service_client.mutate_assets.assert_called_once()  # type: ignore
    call_args = mock_asset_service_client.mutate_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert "name" in operation.update_mask.paths


@pytest.mark.asyncio
async def test_create_sitelink_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a sitelink asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_sitelink_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            link_text="Visit Us",
            final_url="https://example.com",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_callout_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a callout asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_callout_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            callout_text="Free Shipping",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_structured_snippet_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a structured snippet asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_structured_snippet_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            header="Brands",
            values=["Brand A", "Brand B"],
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_call_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a call asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_call_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            country_code="US",
            phone_number="555-0100",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_price_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a price asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_price_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            type_="SERVICES",
            language_code="en",
            price_qualifier="FROM",
            price_offerings=[
                {
                    "header": "Basic",
                    "description": "Basic plan",
                    "final_url": "https://example.com/basic",
                    "price": {"currency_code": "USD", "amount_micros": 9990000},
                    "unit": "PER_MONTH",
                }
            ],
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_promotion_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a promotion asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_promotion_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            promotion_target="Summer Sale",
            language_code="en",
            percent_off=20,
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_lead_form_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a lead form asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_lead_form_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            business_name="Test Business",
            headline="Get a Quote",
            description="Fill out the form",
            privacy_policy_url="https://example.com/privacy",
            call_to_action_type="SIGN_UP",
            fields=[{"input_type": "FULL_NAME"}, {"input_type": "EMAIL"}],
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_page_feed_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a page feed asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_page_feed_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            page_url="https://example.com/page",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_mobile_app_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a mobile app asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_mobile_app_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            app_id="com.example.app",
            app_store="GOOGLE_APP_STORE",
            link_text="Download Now",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_hotel_callout_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a hotel callout asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_hotel_callout_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            text="Free WiFi",
            language_code="en",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_call_to_action_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a call-to-action asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_call_to_action_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            call_to_action="LEARN_MORE",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_location_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a location asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_location_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_hotel_property_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a hotel property asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_hotel_property_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
            hotel_name="Grand Hotel",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_app_deep_link_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an app deep link asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_app_deep_link_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            app_deep_link_uri="myapp://products/123",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_book_on_google_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Book on Google asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_book_on_google_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_media_bundle_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a media bundle asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_media_bundle_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            data=b"fake_zip_data",
            name="Test Bundle",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_demand_gen_carousel_card_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a Demand Gen carousel card asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_demand_gen_carousel_card_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            marketing_image_asset="customers/1234567890/assets/111",
            headline="Shop Now",
            call_to_action_text="Buy",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_business_message_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a business message asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_business_message_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            message_provider="WHATSAPP",
            starter_message="Hello!",
            call_to_action_selection="CONTACT_US",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_education_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic education asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_education_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            program_id="CS101",
            program_name="Computer Science",
            school_name="MIT",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_real_estate_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic real estate asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_real_estate_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            listing_id="RE001",
            listing_name="Beautiful Condo",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_custom_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic custom asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_custom_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            id="ITEM001",
            item_title="Custom Widget",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_hotels_and_rentals_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic hotels and rentals asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_hotels_and_rentals_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            property_id="HOTEL001",
            property_name="Beach Resort",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_flights_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic flights asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_flights_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            destination_id="LAX",
            destination_name="Los Angeles",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_travel_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic travel asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_travel_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            destination_id="PARIS01",
            title="Paris Getaway",
            destination_name="Paris",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_local_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic local asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_local_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            deal_id="DEAL001",
            deal_name="50% Off Pizza",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_dynamic_jobs_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a dynamic jobs asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}
    with patch(
        "src.services.assets.asset_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await asset_service.create_dynamic_jobs_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            job_id="JOB001",
            job_title="Software Engineer",
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


@pytest.mark.asyncio
async def test_create_youtube_video_list_asset(
    asset_service: AssetService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a YouTube video list asset."""
    customer_id = "1234567890"
    mock_response = Mock(spec=MutateAssetsResponse)
    mock_response.results = [Mock()]
    mock_response.results[0].resource_name = f"customers/{customer_id}/assets/123"
    mock_asset_service_client = asset_service.client
    mock_asset_service_client.mutate_assets.return_value = mock_response
    expected = {"results": [{"resource_name": f"customers/{customer_id}/assets/123"}]}

    mock_video_list = Mock()
    mock_video_list.youtube_videos = []

    with (
        patch(
            "src.services.assets.asset_service.serialize_proto_message",
            return_value=expected,
        ),
        patch(
            "src.services.assets.asset_service.YouTubeVideoListAsset",
            return_value=mock_video_list,
        ),
        patch("src.services.assets.asset_service.Asset", return_value=Mock()),
        patch("src.services.assets.asset_service.AssetOperation", return_value=Mock()),
        patch(
            "src.services.assets.asset_service.MutateAssetsRequest", return_value=Mock()
        ),
    ):
        result = await asset_service.create_youtube_video_list_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            youtube_videos=[
                "customers/1234567890/assets/v1",
                "customers/1234567890/assets/v2",
            ],
        )
    assert result == expected
    mock_asset_service_client.mutate_assets.assert_called_once()


def test_register_asset_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_asset_tools(mock_mcp)

    # Assert
    assert isinstance(service, AssetService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 32  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_text_asset",
        "create_image_asset",
        "create_youtube_video_asset",
        "search_assets",
        "update_asset",
        "create_sitelink_asset",
        "create_callout_asset",
        "create_structured_snippet_asset",
        "create_call_asset",
        "create_price_asset",
        "create_promotion_asset",
        "create_lead_form_asset",
        "create_page_feed_asset",
        "create_mobile_app_asset",
        "create_hotel_callout_asset",
        "create_call_to_action_asset",
        "create_location_asset",
        "create_hotel_property_asset",
        "create_app_deep_link_asset",
        "create_book_on_google_asset",
        "create_media_bundle_asset",
        "create_demand_gen_carousel_card_asset",
        "create_business_message_asset",
        "create_dynamic_education_asset",
        "create_dynamic_real_estate_asset",
        "create_dynamic_custom_asset",
        "create_dynamic_hotels_and_rentals_asset",
        "create_dynamic_flights_asset",
        "create_dynamic_travel_asset",
        "create_dynamic_local_asset",
        "create_dynamic_jobs_asset",
        "create_youtube_video_list_asset",
    ]

    assert set(tool_names) == set(expected_tools)
