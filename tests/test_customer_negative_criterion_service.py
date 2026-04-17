"""Tests for CustomerNegativeCriterionService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.targeting.customer_negative_criterion_service import (
    CustomerNegativeCriterionService,
    register_customer_negative_criterion_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomerNegativeCriterionService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.targeting.customer_negative_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomerNegativeCriterionService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_add_placement_exclusions(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/1"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_placement_exclusions(
        ctx=mock_ctx,
        customer_id="1234567890",
        placement_urls=["badsite.com"],
    )
    assert isinstance(result, list)
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_remove_negative_criterion(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customer_negative_criteria.return_value = Mock()
    with patch(
        "src.services.targeting.customer_negative_criterion_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_negative_criterion(
            ctx=mock_ctx,
            customer_id="1234567890",
            criterion_resource_name="customers/1234567890/customerNegativeCriteria/1",
        )
    assert result == {"results": []}


@pytest.mark.asyncio
async def test_add_content_label_exclusions(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/1"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_content_label_exclusions(
        ctx=mock_ctx,
        customer_id="1234567890",
        content_labels=["PROFANITY"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "CONTENT_LABEL"
    assert result[0]["content_label"] == "PROFANITY"
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_negative_keywords(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/1"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    with (
        patch(
            "src.services.targeting.customer_negative_criterion_service.CustomerNegativeCriterion",
            return_value=Mock(),
        ),
        patch(
            "src.services.targeting.customer_negative_criterion_service.CustomerNegativeCriterionOperation",
            return_value=Mock(),
        ),
        patch(
            "src.services.targeting.customer_negative_criterion_service.MutateCustomerNegativeCriteriaRequest",
            return_value=Mock(),
        ),
    ):
        result = await service.add_negative_keywords(
            ctx=mock_ctx,
            customer_id="1234567890",
            keywords=[{"text": "bad keyword", "match_type": "BROAD"}],
        )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "KEYWORD"
    assert result[0]["keyword_text"] == "bad keyword"
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_list_negative_criteria(
    service: CustomerNegativeCriterionService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    mock_google_ads_service = Mock()
    mock_criterion = Mock()
    mock_criterion.resource_name = "customers/1234567890/customerNegativeCriteria/1"
    mock_criterion.id = 1
    mock_criterion.type_ = Mock()
    mock_criterion.type_.name = "KEYWORD"
    mock_criterion.keyword = Mock()
    mock_criterion.keyword.text = "bad keyword"
    mock_criterion.keyword.match_type = Mock()
    mock_criterion.keyword.match_type.name = "BROAD"
    mock_criterion.placement = None
    mock_criterion.content_label = None
    mock_row = Mock()
    mock_row.customer_negative_criterion = mock_criterion
    mock_google_ads_service.search.return_value = [mock_row]

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.targeting.customer_negative_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_negative_criteria(
            ctx=mock_ctx,
            customer_id="1234567890",
        )
    assert len(result) == 1
    assert result[0]["type"] == "KEYWORD"
    assert result[0]["keyword_text"] == "bad keyword"
    mock_google_ads_service.search.assert_called_once()


@pytest.mark.asyncio
async def test_add_mobile_application_exclusions(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/2"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_mobile_application_exclusions(
        ctx=mock_ctx,
        customer_id="1234567890",
        app_ids=["com.example.app"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "MOBILE_APPLICATION"
    assert result[0]["app_id"] == "com.example.app"
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_mobile_app_category_exclusions(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/3"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_mobile_app_category_exclusions(
        ctx=mock_ctx,
        customer_id="1234567890",
        category_constants=["mobileAppCategoryConstants/60001"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "MOBILE_APP_CATEGORY"
    assert (
        result[0]["mobile_app_category_constant"] == "mobileAppCategoryConstants/60001"
    )
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_youtube_video_exclusions(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/4"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_youtube_video_exclusions(
        ctx=mock_ctx,
        customer_id="1234567890",
        video_ids=["dQw4w9WgXcQ"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "YOUTUBE_VIDEO"
    assert result[0]["video_id"] == "dQw4w9WgXcQ"
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_youtube_channel_exclusions(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/5"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_youtube_channel_exclusions(
        ctx=mock_ctx,
        customer_id="1234567890",
        channel_ids=["UCxxxxxx"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "YOUTUBE_CHANNEL"
    assert result[0]["channel_id"] == "UCxxxxxx"
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_ip_block_exclusions(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/6"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_ip_block_exclusions(
        ctx=mock_ctx,
        customer_id="1234567890",
        ip_addresses=["192.168.1.0/24"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "IP_BLOCK"
    assert result[0]["ip_address"] == "192.168.1.0/24"
    mock_client.mutate_customer_negative_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_negative_keyword_list_exclusion(
    service: CustomerNegativeCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/customerNegativeCriteria/7"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_customer_negative_criteria.return_value = mock_response
    result = await service.add_negative_keyword_list_exclusion(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_resource_name="customers/1234567890/sharedSets/111",
    )
    assert isinstance(result, dict)
    assert result["type"] == "NEGATIVE_KEYWORD_LIST"
    assert result["shared_set"] == "customers/1234567890/sharedSets/111"
    mock_client.mutate_customer_negative_criteria.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_customer_negative_criterion_tools(mock_mcp)
    assert isinstance(service, CustomerNegativeCriterionService)
    assert mock_mcp.tool.call_count == 11
