"""Tests for CampaignCriterionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v23.enums.types.day_of_week import DayOfWeekEnum
from google.ads.googleads.v23.enums.types.device import DeviceEnum
from google.ads.googleads.v23.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.v23.enums.types.income_range_type import IncomeRangeTypeEnum
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.enums.types.minute_of_hour import MinuteOfHourEnum
from google.ads.googleads.v23.enums.types.proximity_radius_units import (
    ProximityRadiusUnitsEnum,
)
from google.ads.googleads.v23.services.services.campaign_criterion_service import (
    CampaignCriterionServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_criterion_service import (
    MutateCampaignCriteriaResponse,
)

from src.services.campaign.campaign_criterion_service import (
    CampaignCriterionService,
    register_campaign_criterion_tools,
)


@pytest.fixture
def campaign_criterion_service(mock_sdk_client: Any) -> CampaignCriterionService:
    """Create a CampaignCriterionService instance with mocked dependencies."""
    # Mock CampaignCriterionService client
    mock_campaign_criterion_client = Mock(spec=CampaignCriterionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_campaign_criterion_client  # type: ignore

    with patch(
        "src.services.campaign.campaign_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = CampaignCriterionService()
        # Force client initialization
        _ = service.client
        return service


@pytest.mark.asyncio
async def test_add_location_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding location criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    location_ids = ["1014044", "1007734"]  # California, Arizona
    negative = False
    bid_modifier = 1.2

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(location_ids):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 100}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 100}"
            }
            for i in range(len(location_ids))
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_location_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=location_ids,
            negative=negative,
            bid_modifier=bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(location_ids)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == negative
    assert abs(criterion.bid_modifier - bid_modifier) < 0.001
    assert (
        criterion.location.geo_target_constant
        == f"geoTargetConstants/{location_ids[0]}"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(location_ids)} location criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_location_criteria_negative(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding negative location criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    location_ids = ["1014045"]  # Florida
    negative = True

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~101"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~101"
            }
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_location_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=location_ids,
            negative=negative,
            bid_modifier=1.5,  # Should be ignored for negative criteria
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.negative == negative
    # Bid modifier should not be set for negative criteria
    assert not hasattr(criterion, "bid_modifier") or criterion.bid_modifier == 0


@pytest.mark.asyncio
async def test_add_language_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding language criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    language_ids = ["1000", "1003"]  # English, Spanish

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(language_ids):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 200}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 200}"
            }
            for i in range(len(language_ids))
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_language_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            language_ids=language_ids,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(language_ids)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert (
        criterion.language.language_constant == f"languageConstants/{language_ids[0]}"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(language_ids)} language criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_device_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding device criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    device_types = [DeviceEnum.Device.MOBILE, DeviceEnum.Device.DESKTOP]
    bid_modifiers = {"MOBILE": 1.3, "DESKTOP": 0.9}

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(device_types):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 300}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 300}"
            }
            for i in range(len(device_types))
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_device_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            device_types=device_types,
            bid_modifiers=bid_modifiers,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(device_types)

    # Check operations
    mobile_operation = request.operations[0]
    mobile_criterion = mobile_operation.create
    assert (
        mobile_criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    )
    assert mobile_criterion.negative == False
    assert mobile_criterion.device.type_ == DeviceEnum.Device.MOBILE
    assert abs(mobile_criterion.bid_modifier - 1.3) < 0.001

    desktop_operation = request.operations[1]
    desktop_criterion = desktop_operation.create
    assert desktop_criterion.device.type_ == DeviceEnum.Device.DESKTOP
    assert abs(desktop_criterion.bid_modifier - 0.9) < 0.001

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(device_types)} device criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_device_criteria_no_bid_modifiers(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding device criteria without bid modifiers."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    device_types = [DeviceEnum.Device.TABLET]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~301"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~301"
            }
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_device_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            device_types=device_types,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.device.type_ == DeviceEnum.Device.TABLET
    # No bid modifier should be set
    assert not hasattr(criterion, "bid_modifier") or criterion.bid_modifier == 0


@pytest.mark.asyncio
async def test_add_negative_keyword_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding negative keyword criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    keywords = [
        {"text": "free", "match_type": "BROAD"},
        {"text": "cheap", "match_type": "PHRASE"},
        {"text": "discount", "match_type": "EXACT"},
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, keyword in enumerate(keywords):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 400}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 400}"
            }
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_negative_keyword_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            keywords=keywords,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(keywords)

    # Check operations
    for i, keyword in enumerate(keywords):
        operation = request.operations[i]
        criterion = operation.create
        assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
        assert criterion.negative == True
        assert criterion.keyword.text == keyword["text"]
        assert criterion.keyword.match_type == getattr(
            KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
        )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(keywords)} negative keywords to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_remove_campaign_criterion(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a campaign criterion."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    criterion_resource_name = (
        f"customers/{customer_id}/campaignCriteria/{campaign_id}~500"
    )

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.remove_campaign_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == criterion_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed campaign criterion: {criterion_resource_name}",
    )


@pytest.mark.asyncio
async def test_update_campaign_criterion(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating a campaign criterion."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    criterion_id = "500"
    criterion_resource_name = (
        f"customers/{customer_id}/campaignCriteria/{campaign_id}~{criterion_id}"
    )

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.update_campaign_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            criterion_id=criterion_id,
            bid_modifier=1.5,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert "bid_modifier" in operation.update_mask.paths


@pytest.mark.asyncio
async def test_error_handling(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when API call fails."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"

    # Get the mocked campaign criterion service client and make it raise exception
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await campaign_criterion_service.add_location_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=["1014044"],
        )

    assert "Failed to add location criteria" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add location criteria: Test Google Ads Exception",
    )


def test_register_campaign_criterion_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_campaign_criterion_tools(mock_mcp)

    # Assert
    assert isinstance(service, CampaignCriterionService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 38  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "add_location_criteria",
        "add_language_criteria",
        "add_device_criteria",
        "add_negative_keyword_criteria",
        "add_ad_schedule_criteria",
        "add_audience_criteria",
        "add_age_range_criteria",
        "add_gender_criteria",
        "add_income_range_criteria",
        "add_proximity_criteria",
        "add_parental_status_criteria",
        "add_user_interest_criteria",
        "add_topic_criteria",
        "add_placement_criteria",
        "add_youtube_channel_criteria",
        "add_youtube_video_criteria",
        "add_content_label_criteria",
        "add_custom_audience_criteria",
        "add_custom_affinity_criteria",
        "add_combined_audience_criteria",
        "add_life_event_criteria",
        "add_keyword_theme_criteria",
        "add_ip_block_criteria",
        "add_carrier_criteria",
        "add_mobile_app_category_criteria",
        "add_mobile_application_criteria",
        "add_mobile_device_criteria",
        "add_operating_system_criteria",
        "add_location_group_criteria",
        "add_listing_scope_criteria",
        "add_webpage_criteria",
        "add_brand_list_criteria",
        "add_local_service_id_criteria",
        "add_webpage_list_criteria",
        "add_video_lineup_criteria",
        "add_extended_demographic_criteria",
        "update_campaign_criterion",
        "remove_campaign_criterion",
    ]

    assert set(tool_names) == set(expected_tools)


@pytest.mark.asyncio
async def test_add_ad_schedule_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding ad schedule criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    schedules = [
        {
            "day_of_week": "MONDAY",
            "start_hour": 9,
            "start_minute": "ZERO",
            "end_hour": 17,
            "end_minute": "ZERO",
        }
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~500"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~500"
            }
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_ad_schedule_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            schedules=schedules,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(schedules)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert criterion.ad_schedule.day_of_week == DayOfWeekEnum.DayOfWeek.MONDAY
    assert criterion.ad_schedule.start_hour == 9
    assert criterion.ad_schedule.start_minute == MinuteOfHourEnum.MinuteOfHour.ZERO
    assert criterion.ad_schedule.end_hour == 17
    assert criterion.ad_schedule.end_minute == MinuteOfHourEnum.MinuteOfHour.ZERO

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(schedules)} ad schedule criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_audience_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding audience criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    user_list_resource_names = ["customers/123/userLists/456"]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~600"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~600"
            }
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_audience_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            user_list_resource_names=user_list_resource_names,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(user_list_resource_names)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert criterion.user_list.user_list == user_list_resource_names[0]

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(user_list_resource_names)} audience criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_age_range_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding age range criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    age_ranges = [
        AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_25_34,
        AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_35_44,
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(age_ranges):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 700}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 700}"
            }
            for i in range(len(age_ranges))
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_age_range_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            age_ranges=age_ranges,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(age_ranges)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert criterion.age_range.type_ == AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_25_34

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(age_ranges)} age range criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_gender_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding gender criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    genders = [
        GenderTypeEnum.GenderType.MALE,
        GenderTypeEnum.GenderType.FEMALE,
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    for i, _ in enumerate(genders):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 800}"
        )
        mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~{i + 800}"
            }
            for i in range(len(genders))
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_gender_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            genders=genders,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(genders)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert criterion.gender.type_ == GenderTypeEnum.GenderType.MALE

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(genders)} gender criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_income_range_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding income range criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    income_ranges = [
        IncomeRangeTypeEnum.IncomeRangeType.INCOME_RANGE_50_60,
    ]

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/campaignCriteria/{campaign_id}~900"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~900"
            }
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_income_range_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            income_ranges=income_ranges,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(income_ranges)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert (
        criterion.income_range.type_
        == IncomeRangeTypeEnum.IncomeRangeType.INCOME_RANGE_50_60
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(income_ranges)} income range criteria to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_proximity_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding proximity criteria to a campaign."""
    # Arrange
    customer_id = "1234567890"
    campaign_id = "9876543210"
    latitude = 40.7128
    longitude = -74.006
    radius = 10.0
    radius_units = ProximityRadiusUnitsEnum.ProximityRadiusUnits.MILES

    # Create mock response
    mock_response = Mock(spec=MutateCampaignCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = (
        f"customers/{customer_id}/campaignCriteria/{campaign_id}~1000"
    )
    mock_response.results.append(result)  # type: ignore

    # Get the mocked campaign criterion service client
    mock_campaign_criterion_client = campaign_criterion_service.client  # type: ignore
    mock_campaign_criterion_client.mutate_campaign_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~1000"
            }
        ]
    }

    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await campaign_criterion_service.add_proximity_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            radius_units=radius_units,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_campaign_criterion_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
    call_args = mock_campaign_criterion_client.mutate_campaign_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    # Check operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.campaign == f"customers/{customer_id}/campaigns/{campaign_id}"
    assert criterion.negative == False
    assert criterion.proximity.geo_point.latitude_in_micro_degrees == int(
        latitude * 1_000_000
    )
    assert criterion.proximity.geo_point.longitude_in_micro_degrees == int(
        longitude * 1_000_000
    )
    assert criterion.proximity.radius == radius
    assert (
        criterion.proximity.radius_units
        == ProximityRadiusUnitsEnum.ProximityRadiusUnits.MILES
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added proximity criterion to campaign {campaign_id}",
    )


@pytest.mark.asyncio
async def test_add_parental_status_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding parental status criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_parental_status_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            parental_statuses=["PARENT"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_user_interest_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding user interest criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_user_interest_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            user_interest_resource_names=["customers/123/userInterests/456"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_topic_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding topic criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_topic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            topic_constant_resource_names=["topicConstants/123"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_placement_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding placement criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_placement_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            urls=["example.com"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_youtube_channel_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding YouTube channel criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_youtube_channel_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            channel_ids=["UC123"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_youtube_video_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding YouTube video criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_youtube_video_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            video_ids=["dQw4w9WgXcQ"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_content_label_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding content label criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_content_label_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            content_label_types=["PROFANITY"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_custom_audience_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding custom audience criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_custom_audience_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            custom_audience_resource_names=["customers/123/customAudiences/456"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_custom_affinity_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding custom affinity criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_custom_affinity_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            custom_affinity_resource_names=["customers/123/customAffinities/456"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_combined_audience_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding combined audience criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_combined_audience_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            combined_audience_resource_names=["customers/123/combinedAudiences/456"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_life_event_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding life event criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_life_event_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            life_event_resource_names=["456"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_keyword_theme_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding keyword theme criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_keyword_theme_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            keyword_theme_constants=["keywordThemeConstants/123"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_ip_block_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding IP block criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_ip_block_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            ip_addresses=["192.168.1.0/24"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_carrier_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding carrier criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_carrier_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            carrier_constants=["carrierConstants/123"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_mobile_app_category_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding mobile app category criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_mobile_app_category_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            mobile_app_category_constants=["mobileAppCategoryConstants/123"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_mobile_application_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding mobile application criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_mobile_application_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            app_ids=["com.example.app"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_mobile_device_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding mobile device criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_mobile_device_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            mobile_device_constants=["mobileDeviceConstants/123"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_operating_system_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding operating system criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_operating_system_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            os_version_constants=["operatingSystemVersionConstants/123"],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_location_group_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding location group criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_location_group_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            geo_target_constants=["geoTargetConstants/1014044"],
            radius=50000,
            radius_units="MILES",
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_listing_scope_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding listing scope criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_listing_scope_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            dimensions=[{"type": "product_brand", "value": {"value": "Google"}}],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_webpage_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding webpage criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_webpage_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            criterion_name="test",
            conditions=[{"operand": "URL", "argument": "example.com"}],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_brand_list_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding brand list criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_brand_list_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_resource_name="customers/123/sharedSets/456",
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_local_service_id_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding local service ID criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_local_service_id_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            service_id="123",
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_webpage_list_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding webpage list criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_webpage_list_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            criterion_name="test",
            conditions=[{"operand": "URL", "argument": "example.com"}],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_video_lineup_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding video lineup criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_video_lineup_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            video_lineup_ids=[123],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_add_extended_demographic_criteria(
    campaign_criterion_service: CampaignCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding extended demographic criteria."""
    customer_id = "1234567890"
    campaign_id = "12345"

    mock_client = campaign_criterion_service.client
    mock_client.mutate_campaign_criteria.return_value = Mock()  # type: ignore

    expected = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/campaignCriteria/{campaign_id}~100"
            }
        ]
    }
    with patch(
        "src.services.campaign.campaign_criterion_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await campaign_criterion_service.add_extended_demographic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            extended_demographic_ids=[123],
        )
    assert result == expected
    mock_client.mutate_campaign_criteria.assert_called_once()  # type: ignore
