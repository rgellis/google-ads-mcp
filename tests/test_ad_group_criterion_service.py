"""Tests for AdGroupCriterionService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.enums.types.ad_group_criterion_status import (
    AdGroupCriterionStatusEnum,
)
from google.ads.googleads.v23.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v23.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.v23.enums.types.income_range_type import IncomeRangeTypeEnum
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.enums.types.parental_status_type import (
    ParentalStatusTypeEnum,
)
from google.ads.googleads.v23.enums.types.webpage_condition_operand import (
    WebpageConditionOperandEnum,
)
from google.ads.googleads.v23.services.services.ad_group_criterion_service import (
    AdGroupCriterionServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_criterion_service import (
    MutateAdGroupCriteriaResponse,
)

from src.services.ad_group.ad_group_criterion_service import (
    AdGroupCriterionService,
    register_ad_group_criterion_tools,
)


@pytest.fixture
def ad_group_criterion_service(mock_sdk_client: Any) -> AdGroupCriterionService:
    """Create an AdGroupCriterionService instance with mocked dependencies."""
    # Mock AdGroupCriterionService client
    mock_ad_group_criterion_client = Mock(spec=AdGroupCriterionServiceClient)
    mock_sdk_client.client.get_service.return_value = mock_ad_group_criterion_client  # type: ignore

    with patch(
        "src.services.ad_group.ad_group_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        service = AdGroupCriterionService()
        # Force client initialization
        _ = service.client
        return service


def _make_mock_response(
    customer_id: str, ad_group_id: str, count: int, start_id: int = 100
) -> Mock:
    """Helper to create a mock MutateAdGroupCriteriaResponse."""
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    for i in range(count):
        result = Mock()
        result.resource_name = (
            f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + start_id}"
        )
        mock_response.results.append(result)  # type: ignore
    return mock_response


@pytest.mark.asyncio
async def test_add_keywords(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding keyword criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    keywords = [
        {"text": "running shoes", "match_type": "EXACT", "cpc_bid_micros": 1000000},
        {"text": "athletic footwear", "match_type": "PHRASE", "cpc_bid_micros": 800000},
        {"text": "sports shoes", "match_type": "BROAD"},
    ]
    negative = False

    # Create mock response
    mock_response = _make_mock_response(customer_id, ad_group_id, len(keywords))

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 100}"
            }
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            negative=negative,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(keywords)

    # Check first operation (with bid)
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert criterion.status == AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
    assert criterion.negative == negative
    assert criterion.cpc_bid_micros == 1000000
    assert criterion.keyword.text == "running shoes"
    assert criterion.keyword.match_type == KeywordMatchTypeEnum.KeywordMatchType.EXACT

    # Check third operation (without bid)
    operation = request.operations[2]
    criterion = operation.create
    assert criterion.keyword.text == "sports shoes"
    assert criterion.keyword.match_type == KeywordMatchTypeEnum.KeywordMatchType.BROAD
    assert not hasattr(criterion, "cpc_bid_micros") or criterion.cpc_bid_micros == 0

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(keywords)} keywords to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_add_negative_keywords(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding negative keyword criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    keywords = [
        {"text": "free", "match_type": "BROAD"},
        {"text": "cheap", "match_type": "PHRASE"},
    ]
    negative = True

    # Create mock response
    mock_response = _make_mock_response(customer_id, ad_group_id, len(keywords), 200)

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 200}"
            }
            for i in range(len(keywords))
        ]
    }

    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            negative=negative,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.negative == negative
    # Negative keywords should not have bid
    assert not hasattr(criterion, "cpc_bid_micros") or criterion.cpc_bid_micros == 0


@pytest.mark.asyncio
async def test_add_audience_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding audience (user list) criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    user_list_ids = ["123456", "789012"]
    bid_modifier = 1.2

    # Create mock response
    mock_response = _make_mock_response(
        customer_id, ad_group_id, len(user_list_ids), 300
    )

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_criterion_service.add_audience_criteria(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        user_list_ids=user_list_ids,
        bid_modifier=bid_modifier,
    )

    # Assert
    assert len(result) == len(user_list_ids)

    # Check first result
    first_result = result[0]
    assert (
        first_result["resource_name"]
        == f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~300"
    )
    assert first_result["criterion_id"] == f"{ad_group_id}~300"
    assert first_result["type"] == "AUDIENCE"
    assert first_result["user_list_id"] == user_list_ids[0]
    assert first_result["bid_modifier"] == bid_modifier

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(user_list_ids)

    # Check first operation
    operation = request.operations[0]
    criterion = operation.create
    assert criterion.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert criterion.status == AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
    assert abs(criterion.bid_modifier - bid_modifier) < 0.001
    assert (
        criterion.user_list.user_list
        == f"customers/{customer_id}/userLists/{user_list_ids[0]}"
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(user_list_ids)} audience criteria to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_add_audience_criteria_no_bid_modifier(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding audience criteria without bid modifier."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    user_list_ids = ["123456"]

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~301"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_criterion_service.add_audience_criteria(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        user_list_ids=user_list_ids,
    )

    # Assert
    assert len(result) == 1
    assert result[0]["bid_modifier"] is None

    # Verify the API call
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.create
    # No bid modifier should be set
    assert not hasattr(criterion, "bid_modifier") or criterion.bid_modifier == 0


@pytest.mark.asyncio
async def test_add_demographic_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding demographic criteria to an ad group."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    demographics = [
        {"type": "AGE_RANGE", "value": "AGE_RANGE_25_34", "bid_modifier": 1.1},
        {"type": "GENDER", "value": "MALE", "bid_modifier": 0.9},
        {"type": "PARENTAL_STATUS", "value": "PARENT"},
        {"type": "INCOME_RANGE", "value": "INCOME_RANGE_50_60"},
    ]

    # Create mock response
    mock_response = _make_mock_response(
        customer_id, ad_group_id, len(demographics), 400
    )

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {
        "results": [
            {
                "resource_name": f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 400}",
                "type": demo["type"],
                "value": demo["value"],
                "bid_modifier": demo.get("bid_modifier"),
            }
            for i, demo in enumerate(demographics)
        ]
    }

    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.add_demographic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            demographics=demographics,
        )

    # Assert
    assert len(result["results"]) == len(demographics)

    # Check results
    for i, demo in enumerate(demographics):
        criterion_result = result["results"][i]
        assert (
            criterion_result["resource_name"]
            == f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~{i + 400}"
        )
        assert criterion_result["type"] == demo["type"]
        assert criterion_result["value"] == demo["value"]
        assert criterion_result["bid_modifier"] == demo.get("bid_modifier")

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == len(demographics)

    # Check operations
    age_operation = request.operations[0]
    age_criterion = age_operation.create
    assert age_criterion.ad_group == f"customers/{customer_id}/adGroups/{ad_group_id}"
    assert (
        age_criterion.status
        == AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
    )
    assert abs(age_criterion.bid_modifier - 1.1) < 0.001
    assert (
        age_criterion.age_range.type_ == AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_25_34
    )

    gender_operation = request.operations[1]
    gender_criterion = gender_operation.create
    assert abs(gender_criterion.bid_modifier - 0.9) < 0.001
    assert gender_criterion.gender.type_ == GenderTypeEnum.GenderType.MALE

    parental_operation = request.operations[2]
    parental_criterion = parental_operation.create
    assert (
        not hasattr(parental_criterion, "bid_modifier")
        or parental_criterion.bid_modifier == 0
    )
    assert (
        parental_criterion.parental_status.type_
        == ParentalStatusTypeEnum.ParentalStatusType.PARENT
    )

    income_operation = request.operations[3]
    income_criterion = income_operation.create
    assert (
        income_criterion.income_range.type_
        == IncomeRangeTypeEnum.IncomeRangeType.INCOME_RANGE_50_60
    )

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Added {len(demographics)} demographic criteria to ad group {ad_group_id}",
    )


@pytest.mark.asyncio
async def test_add_demographic_criteria_unknown_type(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding demographic criteria with unknown type (should be skipped)."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    demographics = [
        {"type": "UNKNOWN_TYPE", "value": "UNKNOWN_VALUE"},
        {"type": "AGE_RANGE", "value": "AGE_RANGE_25_34"},
    ]

    # Create mock response - only one result since unknown type is skipped
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = f"customers/{customer_id}/adGroupCriteria/{ad_group_id}~401"
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Act
    result = await ad_group_criterion_service.add_demographic_criteria(
        ctx=mock_ctx,
        customer_id=customer_id,
        ad_group_id=ad_group_id,
        demographics=demographics,
    )

    # Assert - result is a serialized response dict
    assert isinstance(result, dict)

    # Verify the API call - only 1 operation since unknown type was skipped
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 1
    assert (
        request.operations[0].create.age_range.type_
        == AgeRangeTypeEnum.AgeRangeType.AGE_RANGE_25_34
    )


@pytest.mark.asyncio
async def test_add_placement_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding placement criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    urls = ["example.com", "youtube.com"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(urls), 500)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_placement_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            urls=urls,
            negative=True,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert request.operations[0].create.placement.url == "example.com"
    assert request.operations[0].create.negative is True
    assert request.operations[1].create.placement.url == "youtube.com"


@pytest.mark.asyncio
async def test_add_mobile_app_category_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding mobile app category criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    categories = ["mobileAppCategoryConstants/123", "mobileAppCategoryConstants/456"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(categories), 600)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_mobile_app_category_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            mobile_app_category_constants=categories,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert (
        request.operations[0].create.mobile_app_category.mobile_app_category_constant
        == "mobileAppCategoryConstants/123"
    )


@pytest.mark.asyncio
async def test_add_mobile_application_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding mobile application criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    app_ids = ["1-123456789"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(app_ids), 700)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_mobile_application_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            app_ids=app_ids,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].create.mobile_application.app_id == "1-123456789"


@pytest.mark.asyncio
async def test_add_youtube_video_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding YouTube video criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    video_ids = ["dQw4w9WgXcQ", "abc123"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(video_ids), 800)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_youtube_video_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            video_ids=video_ids,
            negative=True,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert request.operations[0].create.youtube_video.video_id == "dQw4w9WgXcQ"
    assert request.operations[0].create.negative is True


@pytest.mark.asyncio
async def test_add_youtube_channel_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding YouTube channel criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    channel_ids = ["UCxyz123"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(channel_ids), 900)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_youtube_channel_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            channel_ids=channel_ids,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].create.youtube_channel.channel_id == "UCxyz123"


@pytest.mark.asyncio
async def test_add_topic_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding topic criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    topics = ["topicConstants/123", "topicConstants/456"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(topics), 1000)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_topic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            topic_constant_resource_names=topics,
            bid_modifier=1.5,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert request.operations[0].create.topic.topic_constant == "topicConstants/123"
    assert abs(request.operations[0].create.bid_modifier - 1.5) < 0.001


@pytest.mark.asyncio
async def test_add_user_interest_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding user interest criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    interests = ["customers/1234567890/userInterests/123"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(interests), 1100)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_user_interest_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            user_interest_resource_names=interests,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.operations[0].create.user_interest.user_interest_category
        == "customers/1234567890/userInterests/123"
    )


@pytest.mark.asyncio
async def test_add_webpage_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding webpage criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    conditions = [
        {"operand": "URL", "argument": "example.com/shoes"},
        {"operand": "PAGE_TITLE", "argument": "running", "operator": "CONTAINS"},
    ]

    mock_response = _make_mock_response(customer_id, ad_group_id, 1, 1200)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_webpage_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_name="Shoes pages",
            conditions=conditions,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    criterion = request.operations[0].create
    assert criterion.webpage.criterion_name == "Shoes pages"
    assert len(criterion.webpage.conditions) == 2
    assert (
        criterion.webpage.conditions[0].operand
        == WebpageConditionOperandEnum.WebpageConditionOperand.URL
    )
    assert criterion.webpage.conditions[0].argument == "example.com/shoes"


@pytest.mark.asyncio
async def test_add_custom_affinity_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding custom affinity criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    affinities = ["customers/1234567890/customAffinities/123"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(affinities), 1300)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_custom_affinity_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            custom_affinity_resource_names=affinities,
            bid_modifier=1.3,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.operations[0].create.custom_affinity.custom_affinity
        == "customers/1234567890/customAffinities/123"
    )
    assert abs(request.operations[0].create.bid_modifier - 1.3) < 0.001


@pytest.mark.asyncio
async def test_add_custom_audience_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding custom audience criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    audiences = ["customers/1234567890/customAudiences/789"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(audiences), 1400)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_custom_audience_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            custom_audience_resource_names=audiences,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.operations[0].create.custom_audience.custom_audience
        == "customers/1234567890/customAudiences/789"
    )


@pytest.mark.asyncio
async def test_add_combined_audience_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding combined audience criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    audiences = ["customers/1234567890/combinedAudiences/111"]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(audiences), 1500)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_combined_audience_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            combined_audience_resource_names=audiences,
            bid_modifier=0.8,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.operations[0].create.combined_audience.combined_audience
        == "customers/1234567890/combinedAudiences/111"
    )
    assert abs(request.operations[0].create.bid_modifier - 0.8) < 0.001


@pytest.mark.asyncio
async def test_add_location_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding location criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    location_ids = ["2840", "2826"]

    mock_response = _make_mock_response(
        customer_id, ad_group_id, len(location_ids), 1600
    )
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_location_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            location_ids=location_ids,
            bid_modifier=1.2,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert (
        request.operations[0].create.location.geo_target_constant
        == "geoTargetConstants/2840"
    )
    assert abs(request.operations[0].create.bid_modifier - 1.2) < 0.001


@pytest.mark.asyncio
async def test_add_language_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding language criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    language_ids = ["1000", "1003"]

    mock_response = _make_mock_response(
        customer_id, ad_group_id, len(language_ids), 1700
    )
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_language_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            language_ids=language_ids,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert (
        request.operations[0].create.language.language_constant
        == "languageConstants/1000"
    )


@pytest.mark.asyncio
async def test_add_life_event_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding life event criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    life_event_ids = [123, 456]

    mock_response = _make_mock_response(
        customer_id, ad_group_id, len(life_event_ids), 1800
    )
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_life_event_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            life_event_ids=life_event_ids,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert request.operations[0].create.life_event.life_event_id == 123


@pytest.mark.asyncio
async def test_add_video_lineup_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding video lineup criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    lineup_ids = [100, 200]

    mock_response = _make_mock_response(customer_id, ad_group_id, len(lineup_ids), 1900)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_video_lineup_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            video_lineup_ids=lineup_ids,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 2
    assert request.operations[0].create.video_lineup.video_lineup_id == 100


@pytest.mark.asyncio
async def test_add_extended_demographic_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding extended demographic criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    demographic_ids = [1, 2, 3]

    mock_response = _make_mock_response(
        customer_id, ad_group_id, len(demographic_ids), 2000
    )
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_extended_demographic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            extended_demographic_ids=demographic_ids,
            bid_modifier=1.1,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.operations) == 3
    assert (
        request.operations[0].create.extended_demographic.extended_demographic_id == 1
    )
    assert abs(request.operations[0].create.bid_modifier - 1.1) < 0.001


@pytest.mark.asyncio
async def test_add_brand_list_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding brand list criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    shared_set = "customers/1234567890/sharedSets/456"

    mock_response = _make_mock_response(customer_id, ad_group_id, 1, 2100)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_brand_list_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            shared_set_resource_name=shared_set,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].create.brand_list.shared_set == shared_set


@pytest.mark.asyncio
async def test_update_criterion_bid(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating criterion bid."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"
    cpc_bid_micros = 1500000
    bid_modifier = 1.3

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.update_criterion_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=cpc_bid_micros,
            bid_modifier=bid_modifier,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    criterion = operation.update
    assert criterion.resource_name == criterion_resource_name
    assert criterion.cpc_bid_micros == cpc_bid_micros
    assert abs(criterion.bid_modifier - bid_modifier) < 0.001
    assert "cpc_bid_micros" in operation.update_mask.paths
    assert "bid_modifier" in operation.update_mask.paths

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Updated criterion bid: {criterion_resource_name}",
    )


@pytest.mark.asyncio
async def test_update_criterion_bid_partial(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test updating criterion bid with only one field."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"
    cpc_bid_micros = 2000000

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.update_criterion_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=cpc_bid_micros,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    criterion = operation.update
    assert criterion.cpc_bid_micros == cpc_bid_micros
    assert not hasattr(criterion, "bid_modifier") or criterion.bid_modifier == 0
    assert "cpc_bid_micros" in operation.update_mask.paths
    assert "bid_modifier" not in operation.update_mask.paths


@pytest.mark.asyncio
async def test_remove_ad_group_criterion(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing an ad group criterion."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"

    # Create mock response
    mock_response = Mock(spec=MutateAdGroupCriteriaResponse)
    mock_response.results = []
    result = Mock()
    result.resource_name = criterion_resource_name
    mock_response.results.append(result)  # type: ignore

    # Get the mocked ad group criterion service client
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    # Mock serialize_proto_message
    expected_result = {"results": [{"resource_name": criterion_resource_name}]}

    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        # Act
        result = await ad_group_criterion_service.remove_ad_group_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    # Assert
    assert result == expected_result

    # Verify the API call
    mock_ad_group_criterion_client.mutate_ad_group_criteria.assert_called_once()  # type: ignore
    call_args = mock_ad_group_criterion_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == customer_id
    assert len(request.operations) == 1

    operation = request.operations[0]
    assert operation.remove == criterion_resource_name

    # Verify logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="info",
        message=f"Removed ad group criterion: {criterion_resource_name}",
    )


@pytest.mark.asyncio
async def test_error_handling_keywords(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding keywords fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=[{"text": "test", "match_type": "BROAD"}],
        )

    assert "Failed to add keywords" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add keywords: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_audience_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding audience criteria fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_audience_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            user_list_ids=["123"],
        )

    assert "Failed to add audience criteria" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add audience criteria: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_demographic_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding demographic criteria fails."""
    # Arrange
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_demographic_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            demographics=[{"type": "AGE_RANGE", "value": "AGE_RANGE_25_34"}],
        )

    assert "Failed to add demographic criteria" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to add demographic criteria: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_update_criterion_bid(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating criterion bid fails."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.update_criterion_bid(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=1000000,
        )

    assert "Failed to update criterion bid" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to update criterion bid: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_remove_criterion(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when removing criterion fails."""
    # Arrange
    customer_id = "1234567890"
    criterion_resource_name = f"customers/{customer_id}/adGroupCriteria/123~456"

    # Get the mocked ad group criterion service client and make it raise exception
    mock_ad_group_criterion_client = ad_group_criterion_service.client  # type: ignore
    mock_ad_group_criterion_client.mutate_ad_group_criteria.side_effect = (  # type: ignore
        google_ads_exception  # type: ignore
    )

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.remove_ad_group_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
        )

    assert "Failed to remove ad group criterion" in str(exc_info.value)
    assert "Test Google Ads Exception" in str(exc_info.value)

    # Verify error logging
    mock_ctx.log.assert_called_once_with(  # type: ignore
        level="error",
        message="Failed to remove ad group criterion: Test Google Ads Exception",
    )


@pytest.mark.asyncio
async def test_error_handling_placement_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding placement criteria fails."""
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_placement_criteria(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group_id="9876543210",
            urls=["example.com"],
        )

    assert "Failed to add placement criteria" in str(exc_info.value)


@pytest.mark.asyncio
async def test_error_handling_topic_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when adding topic criteria fails."""
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await ad_group_criterion_service.add_topic_criteria(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group_id="9876543210",
            topic_constant_resource_names=["topicConstants/123"],
        )

    assert "Failed to add topic criteria" in str(exc_info.value)


@pytest.mark.asyncio
async def test_add_placement_criteria_with_bid_modifier(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding placement criteria with bid modifier (non-negative)."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    urls = ["example.com"]

    mock_response = _make_mock_response(customer_id, ad_group_id, 1, 2200)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_placement_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            urls=urls,
            negative=False,
            bid_modifier=1.5,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    assert abs(request.operations[0].create.bid_modifier - 1.5) < 0.001
    assert request.operations[0].create.negative is False


@pytest.mark.asyncio
async def test_add_negative_placement_no_bid_modifier(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test that negative placements don't get bid modifiers even if specified."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    urls = ["badsite.com"]

    mock_response = _make_mock_response(customer_id, ad_group_id, 1, 2300)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        await ad_group_criterion_service.add_placement_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            urls=urls,
            negative=True,
            bid_modifier=1.5,
        )

    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    criterion = request.operations[0].create
    assert criterion.negative is True
    # bid_modifier should not be set for negative criteria
    assert not hasattr(criterion, "bid_modifier") or criterion.bid_modifier == 0


def test_register_ad_group_criterion_tools() -> None:
    """Test tool registration."""
    # Arrange
    mock_mcp = Mock()

    # Act
    service = register_ad_group_criterion_tools(mock_mcp)

    # Assert
    assert isinstance(service, AdGroupCriterionService)

    # Verify that tools were registered
    assert mock_mcp.tool.call_count == 25  # 25 tools registered  # type: ignore

    # Verify tool functions were passed
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [tool.__name__ for tool in registered_tools]

    expected_tools = [
        "add_keywords",
        "add_audience_criteria",
        "add_demographic_criteria",
        "add_placement_criteria",
        "add_mobile_app_category_criteria",
        "add_mobile_application_criteria",
        "add_youtube_video_criteria",
        "add_youtube_channel_criteria",
        "add_topic_criteria",
        "add_user_interest_criteria",
        "add_webpage_criteria",
        "add_custom_affinity_criteria",
        "add_custom_audience_criteria",
        "add_combined_audience_criteria",
        "add_location_criteria",
        "add_language_criteria",
        "add_life_event_criteria",
        "add_video_lineup_criteria",
        "add_extended_demographic_criteria",
        "add_brand_list_criteria",
        "add_listing_group_criteria",
        "add_app_payment_model_criteria",
        "add_vertical_ads_item_group_rule_list_criteria",
        "update_criterion_bid",
        "remove_ad_group_criterion",
    ]

    assert set(tool_names) == set(expected_tools)


@pytest.mark.asyncio
async def test_add_listing_group_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding listing group criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = _make_mock_response(customer_id, ad_group_id, 1, 2400)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_listing_group_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            listing_group_type="UNIT",
            parent_ad_group_criterion="customers/1234567890/adGroupCriteria/9876543210~99",
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    criterion = request.operations[0].create
    assert criterion.negative is False
    assert (
        criterion.listing_group.parent_ad_group_criterion
        == "customers/1234567890/adGroupCriteria/9876543210~99"
    )


@pytest.mark.asyncio
async def test_add_app_payment_model_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding app payment model criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"

    mock_response = _make_mock_response(customer_id, ad_group_id, 1, 2500)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_app_payment_model_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            app_payment_model_type="PAID",
            bid_modifier=1.2,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    criterion = request.operations[0].create
    assert abs(criterion.bid_modifier - 1.2) < 0.001


@pytest.mark.asyncio
async def test_add_vertical_ads_item_group_rule_list_criteria(
    ad_group_criterion_service: AdGroupCriterionService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test adding vertical ads item group rule list criteria to an ad group."""
    customer_id = "1234567890"
    ad_group_id = "9876543210"
    shared_set = "customers/1234567890/sharedSets/789"

    mock_response = _make_mock_response(customer_id, ad_group_id, 1, 2600)
    mock_client = ad_group_criterion_service.client  # type: ignore
    mock_client.mutate_ad_group_criteria.return_value = mock_response  # type: ignore

    expected_result = {"results": [{"resource_name": "test"}]}
    with patch(
        "src.services.ad_group.ad_group_criterion_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await ad_group_criterion_service.add_vertical_ads_item_group_rule_list_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            shared_set_resource_name=shared_set,
        )

    assert result == expected_result
    call_args = mock_client.mutate_ad_group_criteria.call_args  # type: ignore
    request = call_args[1]["request"]
    criterion = request.operations[0].create
    assert criterion.vertical_ads_item_group_rule_list.shared_set == shared_set
    assert criterion.negative is False
