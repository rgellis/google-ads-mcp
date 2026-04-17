"""Tests for SharedCriterionService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.shared.shared_criterion_service import (
    SharedCriterionService,
    register_shared_criterion_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> SharedCriterionService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.shared.shared_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = SharedCriterionService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_add_keywords_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~1"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_keywords_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        keywords=[{"text": "keyword1", "match_type": "BROAD"}],
    )
    assert isinstance(result, list)
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_remove_shared_criterion(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_shared_criteria.return_value = Mock()
    with patch(
        "src.services.shared.shared_criterion_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_shared_criterion(
            ctx=mock_ctx,
            customer_id="1234567890",
            criterion_resource_name="customers/1234567890/sharedCriteria/111~222",
        )
    assert result == {"results": []}


@pytest.mark.asyncio
async def test_add_placements_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~1"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_placements_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        placement_urls=["badsite.com"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "PLACEMENT"
    assert result[0]["url"] == "badsite.com"
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_list_shared_criteria(
    service: SharedCriterionService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    mock_google_ads_service = Mock()
    mock_criterion = Mock()
    mock_criterion.resource_name = "customers/1234567890/sharedCriteria/111~1"
    mock_criterion.criterion_id = 1
    mock_criterion.type_ = Mock()
    mock_criterion.type_.name = "KEYWORD"
    mock_criterion.keyword = Mock()
    mock_criterion.keyword.text = "bad keyword"
    mock_criterion.keyword.match_type = Mock()
    mock_criterion.keyword.match_type.name = "BROAD"
    mock_criterion.placement = None
    mock_row = Mock()
    mock_row.shared_criterion = mock_criterion
    mock_google_ads_service.search.return_value = [mock_row]

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.shared.shared_criterion_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_shared_criteria(
            ctx=mock_ctx,
            customer_id="1234567890",
            shared_set_id="111",
        )
    assert len(result) == 1
    assert result[0]["type"] == "KEYWORD"
    assert result[0]["keyword_text"] == "bad keyword"
    mock_google_ads_service.search.assert_called_once()


@pytest.mark.asyncio
async def test_add_youtube_videos_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~2"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_youtube_videos_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        video_ids=["dQw4w9WgXcQ"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "YOUTUBE_VIDEO"
    assert result[0]["video_id"] == "dQw4w9WgXcQ"
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_youtube_channels_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~3"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_youtube_channels_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        channel_ids=["UCxxxxxx"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "YOUTUBE_CHANNEL"
    assert result[0]["channel_id"] == "UCxxxxxx"
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_mobile_app_categories_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~4"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_mobile_app_categories_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        category_constants=["mobileAppCategoryConstants/60001"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "MOBILE_APP_CATEGORY"
    assert (
        result[0]["mobile_app_category_constant"] == "mobileAppCategoryConstants/60001"
    )
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_mobile_applications_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~5"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_mobile_applications_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        app_ids=["com.example.app"],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "MOBILE_APPLICATION"
    assert result[0]["app_id"] == "com.example.app"
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_brands_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~6"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_brands_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        brands=[{"entity_id": "brand123", "display_name": "Test Brand"}],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "BRAND"
    assert result[0]["entity_id"] == "brand123"
    assert result[0]["display_name"] == "Test Brand"
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_webpages_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~7"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_webpages_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        webpages=[{"criterion_name": "Excluded Pages"}],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "WEBPAGE"
    assert result[0]["criterion_name"] == "Excluded Pages"
    mock_client.mutate_shared_criteria.assert_called_once()


@pytest.mark.asyncio
async def test_add_vertical_ads_item_group_rules_to_shared_set(
    service: SharedCriterionService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_result = Mock()
    mock_result.resource_name = "customers/1234567890/sharedCriteria/111~8"
    mock_response = Mock()
    mock_response.results = [mock_result]
    mock_client.mutate_shared_criteria.return_value = mock_response
    result = await service.add_vertical_ads_item_group_rules_to_shared_set(
        ctx=mock_ctx,
        customer_id="1234567890",
        shared_set_id="111",
        rules=[{"item_code": "ITEM123", "country_criterion_id": 2840}],
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["type"] == "VERTICAL_ADS_ITEM_GROUP_RULE"
    assert result[0]["item_code"] == "ITEM123"
    assert result[0]["country_criterion_id"] == 2840
    mock_client.mutate_shared_criteria.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_shared_criterion_tools(mock_mcp)
    assert isinstance(service, SharedCriterionService)
    assert mock_mcp.tool.call_count == 11
