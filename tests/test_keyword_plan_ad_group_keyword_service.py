"""Tests for Google Ads Keyword Plan Ad Group Keyword Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.services.types.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordOperation,
    MutateKeywordPlanAdGroupKeywordsResponse,
    MutateKeywordPlanAdGroupKeywordResult,
)

from src.services.planning.keyword_plan_ad_group_keyword_service import (
    KeywordPlanAdGroupKeywordService,
)


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock service client"""
    return Mock()


@pytest.fixture
def keyword_plan_ad_group_keyword_service(
    mock_service_client: Any,
) -> KeywordPlanAdGroupKeywordService:
    """Create KeywordPlanAdGroupKeywordService instance with mock client"""
    service = KeywordPlanAdGroupKeywordService()
    service._client = mock_service_client  # type: ignore
    return service


@pytest.mark.asyncio
async def test_mutate_keyword_plan_ad_group_keywords(
    keyword_plan_ad_group_keyword_service: KeywordPlanAdGroupKeywordService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test mutating keyword plan ad group keywords"""
    customer_id = "1234567890"
    operations = [KeywordPlanAdGroupKeywordOperation()]

    mock_response = MutateKeywordPlanAdGroupKeywordsResponse(
        results=[
            MutateKeywordPlanAdGroupKeywordResult(
                resource_name="customers/1234567890/keywordPlanAdGroupKeywords/123"
            )
        ]
    )
    mock_service_client.mutate_keyword_plan_ad_group_keywords.return_value = (
        mock_response  # type: ignore
    )

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/keywordPlanAdGroupKeywords/123"}
        ]
    }

    with patch(
        "src.services.planning.keyword_plan_ad_group_keyword_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await keyword_plan_ad_group_keyword_service.mutate_keyword_plan_ad_group_keywords(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

    assert response == expected_result

    call_args = mock_service_client.mutate_keyword_plan_ad_group_keywords.call_args  # type: ignore
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.operations == operations
    assert request.partial_failure == True
    assert request.validate_only == False


def test_create_keyword_plan_ad_group_keyword_operation(
    keyword_plan_ad_group_keyword_service: KeywordPlanAdGroupKeywordService,
) -> None:
    """Test creating keyword plan ad group keyword operation for creation"""
    keyword_plan_ad_group = "customers/1234567890/keywordPlanAdGroups/123"
    text = "running shoes"
    match_type = KeywordMatchTypeEnum.KeywordMatchType.EXACT
    cpc_bid_micros = 1000000
    negative = False

    operation = keyword_plan_ad_group_keyword_service.create_keyword_plan_ad_group_keyword_operation(
        keyword_plan_ad_group=keyword_plan_ad_group,
        text=text,
        match_type=match_type,
        cpc_bid_micros=cpc_bid_micros,
        negative=negative,
    )

    assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
    assert operation.create.keyword_plan_ad_group == keyword_plan_ad_group
    assert operation.create.text == text
    assert operation.create.match_type == match_type
    assert operation.create.cpc_bid_micros == cpc_bid_micros
    assert operation.create.negative == negative


def test_create_keyword_plan_ad_group_keyword_operation_negative(
    keyword_plan_ad_group_keyword_service: KeywordPlanAdGroupKeywordService,
) -> None:
    """Test creating negative keyword plan ad group keyword operation"""
    keyword_plan_ad_group = "customers/1234567890/keywordPlanAdGroups/123"
    text = "cheap shoes"
    match_type = KeywordMatchTypeEnum.KeywordMatchType.BROAD
    negative = True

    operation = keyword_plan_ad_group_keyword_service.create_keyword_plan_ad_group_keyword_operation(
        keyword_plan_ad_group=keyword_plan_ad_group,
        text=text,
        match_type=match_type,
        negative=negative,
    )

    assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
    assert operation.create.keyword_plan_ad_group == keyword_plan_ad_group
    assert operation.create.text == text
    assert operation.create.match_type == match_type
    assert operation.create.negative == negative


def test_update_keyword_plan_ad_group_keyword_operation(
    keyword_plan_ad_group_keyword_service: KeywordPlanAdGroupKeywordService,
) -> None:
    """Test creating keyword plan ad group keyword operation for update"""
    resource_name = "customers/1234567890/keywordPlanAdGroupKeywords/123"
    text = "updated running shoes"
    match_type = KeywordMatchTypeEnum.KeywordMatchType.PHRASE
    cpc_bid_micros = 2000000

    operation = keyword_plan_ad_group_keyword_service.update_keyword_plan_ad_group_keyword_operation(
        resource_name=resource_name,
        text=text,
        match_type=match_type,
        cpc_bid_micros=cpc_bid_micros,
    )

    assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.text == text
    assert operation.update.match_type == match_type
    assert operation.update.cpc_bid_micros == cpc_bid_micros
    assert set(operation.update_mask.paths) == {
        "text",
        "match_type",
        "cpc_bid_micros",
    }


def test_update_keyword_plan_ad_group_keyword_operation_partial(
    keyword_plan_ad_group_keyword_service: KeywordPlanAdGroupKeywordService,
) -> None:
    """Test creating keyword plan ad group keyword operation for partial update"""
    resource_name = "customers/1234567890/keywordPlanAdGroupKeywords/123"
    text = "updated running shoes"

    operation = keyword_plan_ad_group_keyword_service.update_keyword_plan_ad_group_keyword_operation(
        resource_name=resource_name, text=text
    )

    assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.text == text
    assert operation.update_mask.paths == ["text"]


def test_remove_keyword_plan_ad_group_keyword_operation(
    keyword_plan_ad_group_keyword_service: KeywordPlanAdGroupKeywordService,
) -> None:
    """Test creating keyword plan ad group keyword operation for removal"""
    resource_name = "customers/1234567890/keywordPlanAdGroupKeywords/123"

    operation = keyword_plan_ad_group_keyword_service.remove_keyword_plan_ad_group_keyword_operation(
        resource_name
    )

    assert isinstance(operation, KeywordPlanAdGroupKeywordOperation)
    assert operation.remove == resource_name
