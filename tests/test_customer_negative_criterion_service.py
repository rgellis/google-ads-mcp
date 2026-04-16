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


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_customer_negative_criterion_tools(mock_mcp)
    assert isinstance(service, CustomerNegativeCriterionService)
    assert mock_mcp.tool.call_count > 0
