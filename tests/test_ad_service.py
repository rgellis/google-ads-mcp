"""Tests for AdService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.enums.types.ad_group_ad_status import AdGroupAdStatusEnum
from google.ads.googleads.v23.services.services.ad_group_ad_service import (
    AdGroupAdServiceClient,
)
from google.ads.googleads.v23.services.services.ad_service import (
    AdServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_ad_service import (
    MutateAdGroupAdsResponse,
)
from google.ads.googleads.v23.services.types.ad_service import (
    MutateAdsResponse,
)

from src.services.ad_group.ad_service import (
    AdService,
    register_ad_tools,
)


@pytest.fixture
def ad_service(mock_sdk_client: Any) -> AdService:
    """Create an AdService instance with mocked dependencies."""
    mock_ad_group_ad_client = Mock(spec=AdGroupAdServiceClient)
    mock_ad_client = Mock(spec=AdServiceClient)

    def get_service_side_effect(service_name: str) -> Any:
        if service_name == "AdService":
            return mock_ad_client
        return mock_ad_group_ad_client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdService()
        # Force both client initializations
        _ = service.client
        _ = service.ad_client
        return service


@pytest.mark.asyncio
async def test_create_responsive_search_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a responsive search ad."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headlines = [
        "Best Running Shoes",
        "Premium Athletic Footwear",
        "Top Quality Sports Shoes",
        "Comfortable Running Gear",
    ]
    descriptions = [
        "Discover our premium collection of running shoes with superior comfort.",
        "Get the best performance with our top-rated athletic footwear.",
    ]
    final_urls = ["https://example.com/running-shoes"]
    path1 = "shoes"
    path2 = "running"
    status = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~123"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~123"}
        ]
    }

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_responsive_search_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_ad_client.mutate_ad_group_ads.assert_called_once()  # type: ignore
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    ad_group_ad = operation.create
    assert ad_group_ad.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert ad_group_ad.status == status

    # Check ad details
    ad = ad_group_ad.ad
    assert ad.final_urls[0] == final_urls[0]

    # Check responsive search ad
    responsive_ad = ad.responsive_search_ad
    assert len(responsive_ad.headlines) == len(headlines)
    assert len(responsive_ad.descriptions) == len(descriptions)
    assert responsive_ad.headlines[0].text == headlines[0]
    assert responsive_ad.descriptions[0].text == descriptions[0]
    assert responsive_ad.path1 == path1
    assert responsive_ad.path2 == path2

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created responsive search ad in ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_create_responsive_search_ad_minimal(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a responsive search ad with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headlines = ["Headline 1", "Headline 2", "Headline 3"]
    descriptions = ["Description 1", "Description 2"]
    final_urls = ["https://example.com"]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~124"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~124"}
        ]
    }

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_responsive_search_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    ad = operation.create.ad

    # Check that optional paths are not set
    responsive_ad = ad.responsive_search_ad
    assert not hasattr(responsive_ad, "path1") or responsive_ad.path1 == ""
    assert not hasattr(responsive_ad, "path2") or responsive_ad.path2 == ""


@pytest.mark.asyncio
async def test_create_expanded_text_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an expanded text ad."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headline1 = "Best Running Shoes"
    headline2 = "Premium Athletic Footwear"
    headline3 = "Top Quality Sports"
    description1 = "Discover our premium collection of running shoes with superior comfort and style."
    description2 = "Get the best performance with our top-rated athletic footwear designed for athletes."
    final_urls = ["https://example.com/running-shoes"]
    path1 = "shoes"
    path2 = "running"
    status = AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~125"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~125"}
        ]
    }

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_expanded_text_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1=headline1,
            headline2=headline2,
            headline3=headline3,
            description1=description1,
            description2=description2,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_ad_client.mutate_ad_group_ads.assert_called_once()  # type: ignore
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    ad_group_ad = operation.create
    assert ad_group_ad.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert ad_group_ad.status == status

    # Check ad details
    ad = ad_group_ad.ad
    assert ad.final_urls[0] == final_urls[0]

    # Check expanded text ad
    expanded_ad = ad.expanded_text_ad
    assert expanded_ad.headline_part1 == headline1
    assert expanded_ad.headline_part2 == headline2
    assert expanded_ad.headline_part3 == headline3
    assert expanded_ad.description == description1
    assert expanded_ad.description2 == description2
    assert expanded_ad.path1 == path1
    assert expanded_ad.path2 == path2

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Created expanded text ad in ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_create_expanded_text_ad_minimal(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an expanded text ad with minimal parameters."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    headline1 = "Headline 1"
    headline2 = "Headline 2"
    headline3 = None
    description1 = "Description 1"
    description2 = None
    final_urls = ["https://example.com"]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~126"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {"resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~126"}
        ]
    }

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.create_expanded_text_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1=headline1,
            headline2=headline2,
            headline3=headline3,
            description1=description1,
            description2=description2,
            final_urls=final_urls,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    expanded_ad = operation.create.ad.expanded_text_ad

    # Check that optional fields are handled correctly
    assert expanded_ad.headline_part1 == headline1
    assert expanded_ad.headline_part2 == headline2
    assert expanded_ad.description == description1
    # headline3 and description2 should not be set if None


@pytest.mark.asyncio
async def test_update_ad_status(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating ad status."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    ad_id = "456"
    new_status = AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group ad service client
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"
            }
        ]
    }

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_service.update_ad_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_id=ad_id,
            status=new_status,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_ad_client.mutate_ad_group_ads.assert_called_once()  # type: ignore
    call_args = mock_ad_group_ad_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    ad_group_ad = operation.update
    assert (
        ad_group_ad.resource_name
        == f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"
    )
    assert ad_group_ad.status == new_status
    assert "status" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated ad {ad_id} status to {new_status}",
    )


@pytest.mark.asyncio
async def test_error_handling_responsive_search_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating responsive search ad fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group ad service client and make it raise exception
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_service.create_responsive_search_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://example.com"],
        )

    assert "Failed to create responsive search ad" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create responsive search ad: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_expanded_text_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating expanded text ad fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group ad service client and make it raise exception
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_service.create_expanded_text_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1="H1",
            headline2="H2",
            headline3=None,
            description1="D1",
            description2=None,
            final_urls=["https://example.com"],
        )

    assert "Failed to create expanded text ad" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to create expanded text ad: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_status(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating ad status fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    ad_id = "456"

    # Get the mocked ad group ad service client and make it raise exception
    mock_ad_group_ad_client = ad_service.client  # type: ignore
    mock_ad_group_ad_client.mutate_ad_group_ads.side_effect = google_ads_exception  # type: ignore

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_service.update_ad_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_id=ad_id,
            status=AdGroupAdStatusEnum.AdGroupAdStatus.ENABLED,
        )

    assert "Failed to update ad status" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update ad status: Test Google Ads Exception",
    )


def test_register_ad_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 16  # 16 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "create_responsive_search_ad",
        "create_expanded_text_ad",
        "update_ad_status",
        "update_ad",
        "create_responsive_display_ad",
        "create_video_ad",
        "create_demand_gen_multi_asset_ad",
        "create_smart_campaign_ad",
        "create_app_ad",
        "create_shopping_product_ad",
        "create_hotel_ad",
        "create_video_responsive_ad",
        "create_local_ad",
        "create_travel_ad",
        "create_demand_gen_carousel_ad",
        "create_display_upload_ad",
    ]

    assert set(tool_names) == set(expected_tools)


@pytest.mark.asyncio
async def test_update_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating ad content via AdServiceClient.mutate_ads."""
    # Arrange
    customer_id = "1234567890"
    ad_resource_name = f"customers/{customer_id}/ads/456"

    mock_response = Mock(spec=MutateAdsResponse)
    mock_response.results = []
    result_mock = Mock()
    result_mock.resource_name = ad_resource_name
    mock_response.results.append(result_mock)  # type: ignore

    # Get the mocked ad service client
    mock_ad_client = ad_service.ad_client  # type: ignore
    mock_ad_client.mutate_ads.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": ad_resource_name}]}

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_service.update_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_resource_name=ad_resource_name,
            headlines=["New Headline 1", "New Headline 2", "New Headline 3"],
            descriptions=["New Description 1", "New Description 2"],
            final_urls=["https://example.com/new"],
        )

    # Assert
    assert result == expected_result

    # Verify the AdService.mutate_ads call
    mock_ad_client.mutate_ads.assert_called_once()  # type: ignore
    call_args = mock_ad_client.mutate_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.update.resource_name == ad_resource_name
    assert "final_urls" in operation.update_mask.paths
    assert "responsive_search_ad.headlines" in operation.update_mask.paths
    assert "responsive_search_ad.descriptions" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated ad content: {ad_resource_name}",
    )


@pytest.mark.asyncio
async def test_update_ad_partial(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating only specific ad fields."""
    customer_id = "1234567890"
    ad_resource_name = f"customers/{customer_id}/ads/456"

    mock_ad_client = ad_service.ad_client  # type: ignore
    mock_response = Mock(spec=MutateAdsResponse)
    mock_response.results = []
    mock_ad_client.mutate_ads.return_value = mock_response  # type: ignore

    expected_result = {"results": []}

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_service.update_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_resource_name=ad_resource_name,
            final_urls=["https://example.com/updated"],
        )

    assert result == expected_result

    call_args = mock_ad_client.mutate_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert "final_urls" in operation.update_mask.paths
    assert "responsive_search_ad.headlines" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_create_responsive_display_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a responsive display ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    marketing_images = ["customers/123/assets/1001"]
    headlines = ["Great Products", "Best Deals"]
    long_headline = "Discover the best deals on premium products today"
    descriptions = ["Shop now and save big."]
    business_name = "Test Business"
    final_urls = ["https://example.com/display"]

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result_mock = Mock()
    result_mock.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~200"
    mock_response.results.append(result_mock)

    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": result_mock.resource_name}]}

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_service.create_responsive_display_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            marketing_images=marketing_images,
            headlines=headlines,
            long_headline=long_headline,
            descriptions=descriptions,
            business_name=business_name,
            final_urls=final_urls,
            square_marketing_images=["customers/123/assets/1002"],
            logo_images=["customers/123/assets/1003"],
        )

    assert result == expected_result
    mock_client.mutate_ad_group_ads.assert_called_once()  # type: ignore

    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    ad = operation.create.ad
    rda = ad.responsive_display_ad
    assert len(rda.marketing_images) == 1
    assert rda.marketing_images[0].asset == "customers/123/assets/1001"
    assert len(rda.headlines) == 2
    assert rda.long_headline.text == long_headline
    assert rda.business_name == business_name
    assert len(rda.square_marketing_images) == 1
    assert len(rda.logo_images) == 1


@pytest.mark.asyncio
async def test_create_video_ad_in_stream(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an in-stream video ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    video_asset = "customers/123/assets/2001"
    final_urls = ["https://example.com/video"]

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result_mock = Mock()
    result_mock.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~201"
    mock_response.results.append(result_mock)

    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": result_mock.resource_name}]}

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_service.create_video_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            video_asset=video_asset,
            final_urls=final_urls,
            video_format="in_stream",
            action_button_label="Learn More",
            action_headline="Check this out",
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    assert ad.video_ad.video.asset == video_asset
    assert ad.video_ad.in_stream.action_button_label == "Learn More"
    assert ad.video_ad.in_stream.action_headline == "Check this out"


@pytest.mark.asyncio
async def test_create_video_ad_bumper(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a bumper video ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_video_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            video_asset="customers/123/assets/2002",
            final_urls=["https://example.com"],
            video_format="bumper",
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    # bumper oneof should be set
    assert ad.video_ad.bumper is not None


@pytest.mark.asyncio
async def test_create_video_ad_invalid_format(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a video ad with an invalid format raises error."""
    with pytest.raises(Exception, match="Unsupported video format"):
        await ad_service.create_video_ad(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group_id="9876543210",
            video_asset="customers/123/assets/2003",
            final_urls=["https://example.com"],
            video_format="invalid_format",
        )


@pytest.mark.asyncio
async def test_create_demand_gen_multi_asset_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a demand gen multi-asset ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    result_mock = Mock()
    result_mock.resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~202"
    mock_response.results.append(result_mock)

    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": result_mock.resource_name}]}

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_service.create_demand_gen_multi_asset_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            marketing_images=["customers/123/assets/3001"],
            headlines=["DG Headline 1"],
            descriptions=["DG Description 1"],
            business_name="DG Business",
            final_urls=["https://example.com/dg"],
            call_to_action_text="Sign Up",
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    dg = ad.demand_gen_multi_asset_ad
    assert len(dg.marketing_images) == 1
    assert dg.business_name == "DG Business"
    assert dg.call_to_action_text == "Sign Up"


@pytest.mark.asyncio
async def test_create_smart_campaign_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a smart campaign ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_smart_campaign_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=["Smart H1", "Smart H2"],
            descriptions=["Smart D1"],
            final_urls=["https://example.com/smart"],
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    assert len(ad.smart_campaign_ad.headlines) == 2
    assert ad.smart_campaign_ad.headlines[0].text == "Smart H1"


@pytest.mark.asyncio
async def test_create_app_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating an app ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_app_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=["App H1"],
            descriptions=["App D1"],
            final_urls=["https://example.com/app"],
            images=["customers/123/assets/4001"],
            videos=["customers/123/assets/4002"],
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    assert len(ad.app_ad.headlines) == 1
    assert len(ad.app_ad.images) == 1
    assert len(ad.app_ad.youtube_videos) == 1
    assert ad.app_ad.images[0].asset == "customers/123/assets/4001"


@pytest.mark.asyncio
async def test_create_shopping_product_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a shopping product ad (empty info)."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_shopping_product_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    assert ad.shopping_product_ad is not None


@pytest.mark.asyncio
async def test_create_hotel_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a hotel ad (empty info)."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_hotel_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    assert ad.hotel_ad is not None


@pytest.mark.asyncio
async def test_create_video_responsive_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a video responsive ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_video_responsive_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=["VR H1"],
            long_headlines=["VR Long Headline"],
            descriptions=["VR D1"],
            videos=["customers/123/assets/5001"],
            final_urls=["https://example.com/vr"],
            business_name="VR Business",
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    vr = ad.video_responsive_ad
    assert len(vr.headlines) == 1
    assert len(vr.long_headlines) == 1
    assert len(vr.videos) == 1
    assert vr.business_name.text == "VR Business"


@pytest.mark.asyncio
async def test_create_local_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a local ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_local_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=["Local H1"],
            descriptions=["Local D1"],
            marketing_images=["customers/123/assets/6001"],
            final_urls=["https://example.com/local"],
            path1="local",
            path2="deals",
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    local = ad.local_ad
    assert len(local.headlines) == 1
    assert len(local.marketing_images) == 1
    assert local.path1 == "local"
    assert local.path2 == "deals"


@pytest.mark.asyncio
async def test_create_travel_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a travel ad (empty info)."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_travel_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    assert ad.travel_ad is not None


@pytest.mark.asyncio
async def test_create_demand_gen_carousel_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a demand gen carousel ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_demand_gen_carousel_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            business_name="Carousel Biz",
            headline="Carousel Headline",
            description="Carousel Description",
            carousel_cards=["customers/123/assets/7001", "customers/123/assets/7002"],
            final_urls=["https://example.com/carousel"],
            logo_image="customers/123/assets/7003",
            call_to_action_text="Shop Now",
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    carousel = ad.demand_gen_carousel_ad
    assert carousel.business_name == "Carousel Biz"
    assert carousel.headline.text == "Carousel Headline"
    assert len(carousel.carousel_cards) == 2
    assert carousel.logo_image.asset == "customers/123/assets/7003"
    assert carousel.call_to_action_text == "Shop Now"


@pytest.mark.asyncio
async def test_create_display_upload_ad(
    ad_service: AdService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a display upload ad."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = Mock(spec=MutateAdGroupAdsResponse)
    mock_response.results = []
    mock_client = ad_service.client
    mock_client.mutate_ad_group_ads.return_value = mock_response  # type: ignore

    with patch(
        "src.services.ad_group.ad_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await ad_service.create_display_upload_ad(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            media_bundle="customers/123/assets/8001",
            display_upload_product_type="HTML5_UPLOAD_AD",
            final_urls=["https://example.com/display-upload"],
        )

    assert result == {"results": []}
    call_args = mock_client.mutate_ad_group_ads.call_args  # type: ignore
    request = call_args[1]["request"]
    ad = request.operations[0].create.ad
    upload = ad.display_upload_ad
    assert upload.media_bundle.asset == "customers/123/assets/8001"
