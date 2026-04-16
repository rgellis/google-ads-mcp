"""Tests for Google Ads Keyword Plan Campaign Service"""

import pytest
from typing import Any
from unittest.mock import Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)
from google.ads.googleads.v23.services.types.keyword_plan_campaign_service import (
    KeywordPlanCampaignOperation,
    MutateKeywordPlanCampaignsResponse,
    MutateKeywordPlanCampaignResult,
)

from src.services.planning.keyword_plan_campaign_service import (
    KeywordPlanCampaignService,
)


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock service client"""
    return Mock()


@pytest.fixture
def keyword_plan_campaign_service(
    mock_service_client: Any,
) -> KeywordPlanCampaignService:
    """Create KeywordPlanCampaignService instance with mock client"""
    service = KeywordPlanCampaignService()
    service._client = mock_service_client  # type: ignore
    return service


@pytest.mark.asyncio
async def test_mutate_keyword_plan_campaigns(
    keyword_plan_campaign_service: KeywordPlanCampaignService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test mutating keyword plan campaigns"""
    customer_id = "1234567890"
    operations = [KeywordPlanCampaignOperation()]

    mock_response = MutateKeywordPlanCampaignsResponse(
        results=[
            MutateKeywordPlanCampaignResult(
                resource_name="customers/1234567890/keywordPlanCampaigns/123"
            )
        ]
    )
    mock_service_client.mutate_keyword_plan_campaigns.return_value = mock_response  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/keywordPlanCampaigns/123"}]
    }

    with patch(
        "src.services.planning.keyword_plan_campaign_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await keyword_plan_campaign_service.mutate_keyword_plan_campaigns(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

    assert response == expected_result

    call_args = (
        mock_service_client.mutate_keyword_plan_campaigns.call_args  # type: ignore
    )
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.operations == operations
    assert request.partial_failure == True
    assert request.validate_only == False


def test_create_keyword_plan_campaign_operation(
    keyword_plan_campaign_service: KeywordPlanCampaignService,
) -> None:
    """Test creating keyword plan campaign operation for creation"""
    keyword_plan = "customers/1234567890/keywordPlans/123"
    name = "Test Keyword Plan Campaign"
    keyword_plan_network = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
    cpc_bid_micros = 1000000
    language_constants = ["languageConstants/1000"]
    geo_target_constants = ["geoTargetConstants/2840"]

    operation = keyword_plan_campaign_service.create_keyword_plan_campaign_operation(
        keyword_plan=keyword_plan,
        name=name,
        keyword_plan_network=keyword_plan_network,
        cpc_bid_micros=cpc_bid_micros,
        language_constants=language_constants,
        geo_target_constants=geo_target_constants,
    )

    assert isinstance(operation, KeywordPlanCampaignOperation)
    assert operation.create.keyword_plan == keyword_plan
    assert operation.create.name == name
    assert operation.create.keyword_plan_network == keyword_plan_network
    assert operation.create.cpc_bid_micros == cpc_bid_micros
    assert operation.create.language_constants == language_constants
    assert len(operation.create.geo_targets) == 1
    assert (
        operation.create.geo_targets[0].geo_target_constant == geo_target_constants[0]
    )


def test_create_keyword_plan_campaign_operation_minimal(
    keyword_plan_campaign_service: KeywordPlanCampaignService,
) -> None:
    """Test creating keyword plan campaign operation with minimal fields"""
    keyword_plan = "customers/1234567890/keywordPlans/123"
    name = "Test Keyword Plan Campaign"
    keyword_plan_network = (
        KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
    )
    cpc_bid_micros = 1000000

    operation = keyword_plan_campaign_service.create_keyword_plan_campaign_operation(
        keyword_plan=keyword_plan,
        name=name,
        keyword_plan_network=keyword_plan_network,
        cpc_bid_micros=cpc_bid_micros,
    )

    assert isinstance(operation, KeywordPlanCampaignOperation)
    assert operation.create.keyword_plan == keyword_plan
    assert operation.create.name == name
    assert operation.create.keyword_plan_network == keyword_plan_network
    assert operation.create.cpc_bid_micros == cpc_bid_micros
    assert operation.create.language_constants == []
    assert operation.create.geo_targets == []


def test_update_keyword_plan_campaign_operation(
    keyword_plan_campaign_service: KeywordPlanCampaignService,
) -> None:
    """Test creating keyword plan campaign operation for update"""
    resource_name = "customers/1234567890/keywordPlanCampaigns/123"
    name = "Updated Keyword Plan Campaign"
    keyword_plan_network = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH
    cpc_bid_micros = 2000000
    language_constants = ["languageConstants/1001"]
    geo_target_constants = ["geoTargetConstants/2841"]

    operation = keyword_plan_campaign_service.update_keyword_plan_campaign_operation(
        resource_name=resource_name,
        name=name,
        keyword_plan_network=keyword_plan_network,
        cpc_bid_micros=cpc_bid_micros,
        language_constants=language_constants,
        geo_target_constants=geo_target_constants,
    )

    assert isinstance(operation, KeywordPlanCampaignOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.name == name
    assert operation.update.keyword_plan_network == keyword_plan_network
    assert operation.update.cpc_bid_micros == cpc_bid_micros
    assert operation.update.language_constants == language_constants
    assert len(operation.update.geo_targets) == 1
    assert (
        operation.update.geo_targets[0].geo_target_constant == geo_target_constants[0]
    )
    assert set(operation.update_mask.paths) == {
        "name",
        "keyword_plan_network",
        "cpc_bid_micros",
        "language_constants",
        "geo_targets",
    }


def test_update_keyword_plan_campaign_operation_partial(
    keyword_plan_campaign_service: KeywordPlanCampaignService,
) -> None:
    """Test creating keyword plan campaign operation for partial update"""
    resource_name = "customers/1234567890/keywordPlanCampaigns/123"
    name = "Updated Keyword Plan Campaign"

    operation = keyword_plan_campaign_service.update_keyword_plan_campaign_operation(
        resource_name=resource_name, name=name
    )

    assert isinstance(operation, KeywordPlanCampaignOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.name == name
    assert operation.update_mask.paths == ["name"]


def test_remove_keyword_plan_campaign_operation(
    keyword_plan_campaign_service: KeywordPlanCampaignService,
) -> None:
    """Test creating keyword plan campaign operation for removal"""
    resource_name = "customers/1234567890/keywordPlanCampaigns/123"

    operation = keyword_plan_campaign_service.remove_keyword_plan_campaign_operation(
        resource_name
    )

    assert isinstance(operation, KeywordPlanCampaignOperation)
    assert operation.remove == resource_name
