"""Tests for Google Ads Keyword Plan Campaign Keyword Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.services.types.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordOperation,
    MutateKeywordPlanCampaignKeywordsResponse,
    MutateKeywordPlanCampaignKeywordResult,
)

from src.services.planning.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordService,
)


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock service client"""
    return Mock()


@pytest.fixture
def keyword_plan_campaign_keyword_service(
    mock_service_client: Any,
) -> KeywordPlanCampaignKeywordService:
    """Create KeywordPlanCampaignKeywordService instance with mock client"""
    service = KeywordPlanCampaignKeywordService()
    service._client = mock_service_client  # type: ignore
    return service


@pytest.mark.asyncio
async def test_mutate_keyword_plan_campaign_keywords(
    keyword_plan_campaign_keyword_service: KeywordPlanCampaignKeywordService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test mutating keyword plan campaign keywords"""
    customer_id = "1234567890"
    operations = [KeywordPlanCampaignKeywordOperation()]

    mock_response = MutateKeywordPlanCampaignKeywordsResponse(
        results=[
            MutateKeywordPlanCampaignKeywordResult(
                resource_name="customers/1234567890/keywordPlanCampaignKeywords/123"
            )
        ]
    )
    mock_service_client.mutate_keyword_plan_campaign_keywords.return_value = (
        mock_response  # type: ignore
    )

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/keywordPlanCampaignKeywords/123"}
        ]
    }

    with patch(
        "src.services.planning.keyword_plan_campaign_keyword_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await keyword_plan_campaign_keyword_service.mutate_keyword_plan_campaign_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

    assert response == expected_result

    call_args = mock_service_client.mutate_keyword_plan_campaign_keywords.call_args  # type: ignore
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.operations == operations
    assert request.partial_failure == True
    assert request.validate_only == False


def test_create_keyword_plan_campaign_keyword_operation(
    keyword_plan_campaign_keyword_service: KeywordPlanCampaignKeywordService,
) -> None:
    """Test creating keyword plan campaign keyword operation for creation"""
    keyword_plan_campaign = "customers/1234567890/keywordPlanCampaigns/123"
    text = "cheap shoes"
    match_type = KeywordMatchTypeEnum.KeywordMatchType.BROAD

    operation = keyword_plan_campaign_keyword_service.create_keyword_plan_campaign_keyword_operation(
        keyword_plan_campaign=keyword_plan_campaign,
        text=text,
        match_type=match_type,
    )

    assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
    assert operation.create.keyword_plan_campaign == keyword_plan_campaign
    assert operation.create.text == text
    assert operation.create.match_type == match_type
    assert operation.create.negative == True  # Always true for campaign keywords


def test_update_keyword_plan_campaign_keyword_operation(
    keyword_plan_campaign_keyword_service: KeywordPlanCampaignKeywordService,
) -> None:
    """Test creating keyword plan campaign keyword operation for update"""
    resource_name = "customers/1234567890/keywordPlanCampaignKeywords/123"
    text = "updated cheap shoes"
    match_type = KeywordMatchTypeEnum.KeywordMatchType.EXACT

    operation = keyword_plan_campaign_keyword_service.update_keyword_plan_campaign_keyword_operation(
        resource_name=resource_name, text=text, match_type=match_type
    )

    assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.text == text
    assert operation.update.match_type == match_type
    assert set(operation.update_mask.paths) == {"text", "match_type"}


def test_update_keyword_plan_campaign_keyword_operation_partial(
    keyword_plan_campaign_keyword_service: KeywordPlanCampaignKeywordService,
) -> None:
    """Test creating keyword plan campaign keyword operation for partial update"""
    resource_name = "customers/1234567890/keywordPlanCampaignKeywords/123"
    text = "updated cheap shoes"

    operation = keyword_plan_campaign_keyword_service.update_keyword_plan_campaign_keyword_operation(
        resource_name=resource_name, text=text
    )

    assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.text == text
    assert operation.update_mask.paths == ["text"]


def test_remove_keyword_plan_campaign_keyword_operation(
    keyword_plan_campaign_keyword_service: KeywordPlanCampaignKeywordService,
) -> None:
    """Test creating keyword plan campaign keyword operation for removal"""
    resource_name = "customers/1234567890/keywordPlanCampaignKeywords/123"

    operation = keyword_plan_campaign_keyword_service.remove_keyword_plan_campaign_keyword_operation(
        resource_name
    )

    assert isinstance(operation, KeywordPlanCampaignKeywordOperation)
    assert operation.remove == resource_name
