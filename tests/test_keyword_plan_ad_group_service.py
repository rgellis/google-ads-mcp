"""Tests for Google Ads Keyword Plan Ad Group Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.services.types.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupOperation,
    MutateKeywordPlanAdGroupsResponse,
    MutateKeywordPlanAdGroupResult,
)

from src.services.planning.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupService,
)


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock service client"""
    return Mock()


@pytest.fixture
def keyword_plan_ad_group_service(
    mock_service_client: Any,
) -> KeywordPlanAdGroupService:
    """Create KeywordPlanAdGroupService instance with mock client"""
    service = KeywordPlanAdGroupService()
    service._client = mock_service_client  # type: ignore
    return service


@pytest.mark.asyncio
async def test_mutate_keyword_plan_ad_groups(
    keyword_plan_ad_group_service: KeywordPlanAdGroupService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test mutating keyword plan ad groups"""
    customer_id = "1234567890"
    operations = [KeywordPlanAdGroupOperation()]

    mock_response = MutateKeywordPlanAdGroupsResponse(
        results=[
            MutateKeywordPlanAdGroupResult(
                resource_name="customers/1234567890/keywordPlanAdGroups/123"
            )
        ]
    )
    mock_service_client.mutate_keyword_plan_ad_groups.return_value = mock_response  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/keywordPlanAdGroups/123"}]
    }

    with patch(
        "src.services.planning.keyword_plan_ad_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await keyword_plan_ad_group_service.mutate_keyword_plan_ad_groups(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

    assert response == expected_result

    call_args = (
        mock_service_client.mutate_keyword_plan_ad_groups.call_args  # type: ignore
    )
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.operations == operations
    assert request.partial_failure == True
    assert request.validate_only == False


def test_create_keyword_plan_ad_group_operation(
    keyword_plan_ad_group_service: KeywordPlanAdGroupService,
) -> None:
    """Test creating keyword plan ad group operation for creation"""
    keyword_plan_campaign = "customers/1234567890/keywordPlanCampaigns/123"
    name = "Test Keyword Plan Ad Group"
    cpc_bid_micros = 1000000

    operation = keyword_plan_ad_group_service.create_keyword_plan_ad_group_operation(
        keyword_plan_campaign=keyword_plan_campaign,
        name=name,
        cpc_bid_micros=cpc_bid_micros,
    )

    assert isinstance(operation, KeywordPlanAdGroupOperation)
    assert operation.create.keyword_plan_campaign == keyword_plan_campaign
    assert operation.create.name == name
    assert operation.create.cpc_bid_micros == cpc_bid_micros


def test_create_keyword_plan_ad_group_operation_without_bid(
    keyword_plan_ad_group_service: KeywordPlanAdGroupService,
) -> None:
    """Test creating keyword plan ad group operation without CPC bid"""
    keyword_plan_campaign = "customers/1234567890/keywordPlanCampaigns/123"
    name = "Test Keyword Plan Ad Group"

    operation = keyword_plan_ad_group_service.create_keyword_plan_ad_group_operation(
        keyword_plan_campaign=keyword_plan_campaign, name=name
    )

    assert isinstance(operation, KeywordPlanAdGroupOperation)
    assert operation.create.keyword_plan_campaign == keyword_plan_campaign
    assert operation.create.name == name


def test_update_keyword_plan_ad_group_operation(
    keyword_plan_ad_group_service: KeywordPlanAdGroupService,
) -> None:
    """Test creating keyword plan ad group operation for update"""
    resource_name = "customers/1234567890/keywordPlanAdGroups/123"
    name = "Updated Keyword Plan Ad Group"
    cpc_bid_micros = 2000000

    operation = keyword_plan_ad_group_service.update_keyword_plan_ad_group_operation(
        resource_name=resource_name, name=name, cpc_bid_micros=cpc_bid_micros
    )

    assert isinstance(operation, KeywordPlanAdGroupOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.name == name
    assert operation.update.cpc_bid_micros == cpc_bid_micros
    assert set(operation.update_mask.paths) == {"name", "cpc_bid_micros"}


def test_update_keyword_plan_ad_group_operation_partial(
    keyword_plan_ad_group_service: KeywordPlanAdGroupService,
) -> None:
    """Test creating keyword plan ad group operation for partial update"""
    resource_name = "customers/1234567890/keywordPlanAdGroups/123"
    name = "Updated Keyword Plan Ad Group"

    operation = keyword_plan_ad_group_service.update_keyword_plan_ad_group_operation(
        resource_name=resource_name, name=name
    )

    assert isinstance(operation, KeywordPlanAdGroupOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.name == name
    assert operation.update_mask.paths == ["name"]


def test_remove_keyword_plan_ad_group_operation(
    keyword_plan_ad_group_service: KeywordPlanAdGroupService,
) -> None:
    """Test creating keyword plan ad group operation for removal"""
    resource_name = "customers/1234567890/keywordPlanAdGroups/123"

    operation = keyword_plan_ad_group_service.remove_keyword_plan_ad_group_operation(
        resource_name
    )

    assert isinstance(operation, KeywordPlanAdGroupOperation)
    assert operation.remove == resource_name
