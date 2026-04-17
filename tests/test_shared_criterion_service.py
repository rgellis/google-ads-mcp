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


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_shared_criterion_tools(mock_mcp)
    assert isinstance(service, SharedCriterionService)
    assert mock_mcp.tool.call_count > 0
