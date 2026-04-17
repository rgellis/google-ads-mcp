"""Tests for ConversionValueRuleService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.conversions.conversion_value_rule_service import (
    ConversionValueRuleService,
    register_conversion_value_rule_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ConversionValueRuleService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.conversions.conversion_value_rule_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ConversionValueRuleService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_conversion_value_rule(
    service: ConversionValueRuleService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_conversion_value_rules.return_value = Mock()
    with patch(
        "src.services.conversions.conversion_value_rule_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.create_conversion_value_rule(
            ctx=mock_ctx,
            customer_id="1234567890",
            action_operation="ADD",
            action_value=10.0,
        )
    assert result == {"results": []}
    mock_client.mutate_conversion_value_rules.assert_called_once()


@pytest.mark.asyncio
async def test_update_conversion_value_rule(
    service: ConversionValueRuleService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_conversion_value_rules.return_value = Mock()
    with patch(
        "src.services.conversions.conversion_value_rule_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.update_conversion_value_rule(
            ctx=mock_ctx,
            customer_id="1234567890",
            rule_resource_name="customers/1234567890/conversionValueRules/1",
            action_value=20.0,
        )
    assert result == {"results": []}


@pytest.mark.asyncio
async def test_remove_conversion_value_rule(
    service: ConversionValueRuleService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_conversion_value_rules.return_value = Mock()
    with patch(
        "src.services.conversions.conversion_value_rule_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_conversion_value_rule(
            ctx=mock_ctx,
            customer_id="1234567890",
            rule_resource_name="customers/1234567890/conversionValueRules/1",
        )
    assert result == {"results": []}


@pytest.mark.asyncio
async def test_list_conversion_value_rules(
    service: ConversionValueRuleService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    mock_google_ads_service = Mock()
    mock_row = Mock()
    mock_row.conversion_value_rule = Mock()
    mock_google_ads_service.search.return_value = [mock_row]

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with (
        patch(
            "src.services.conversions.conversion_value_rule_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.services.conversions.conversion_value_rule_service.serialize_proto_message",
            return_value={"id": "1", "status": "ENABLED"},
        ),
    ):
        result = await service.list_conversion_value_rules(
            ctx=mock_ctx,
            customer_id="1234567890",
        )
    assert len(result) == 1
    mock_google_ads_service.search.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_conversion_value_rule_tools(mock_mcp)
    assert isinstance(service, ConversionValueRuleService)
    assert mock_mcp.tool.call_count == 4
