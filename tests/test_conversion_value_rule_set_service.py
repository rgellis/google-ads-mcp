"""Tests for ConversionValueRuleSetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.conversions.conversion_value_rule_set_service import (
    ConversionValueRuleSetService,
    register_conversion_value_rule_set_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ConversionValueRuleSetService:
    """Create a ConversionValueRuleSetService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.conversions.conversion_value_rule_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ConversionValueRuleSetService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_conversion_value_rule_set(
    service: ConversionValueRuleSetService, mock_ctx: Context
) -> None:
    """Test creating a conversion value rule set."""
    mock_client = service.client
    mock_client.mutate_conversion_value_rule_sets.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/123/conversionValueRuleSets/1"}]
    }

    with patch(
        "src.services.conversions.conversion_value_rule_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.create_conversion_value_rule_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            dimensions=["GEO_LOCATION"],
            conversion_value_rules=["customers/1234567890/conversionValueRules/1"],
            attachment_type="CUSTOMER",
        )

    assert result == expected_result
    mock_client.mutate_conversion_value_rule_sets.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_conversion_value_rule_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1


@pytest.mark.asyncio
async def test_update_conversion_value_rule_set(
    service: ConversionValueRuleSetService, mock_ctx: Context
) -> None:
    """Test updating a conversion value rule set."""
    mock_client = service.client
    mock_client.mutate_conversion_value_rule_sets.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/123/conversionValueRuleSets/1"}]
    }
    resource_name = "customers/1234567890/conversionValueRuleSets/1"

    with patch(
        "src.services.conversions.conversion_value_rule_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.update_conversion_value_rule_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name=resource_name,
            conversion_value_rules=["customers/1234567890/conversionValueRules/2"],
        )

    assert result == expected_result
    mock_client.mutate_conversion_value_rule_sets.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_conversion_value_rule_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    operation = request.operations[0]
    assert operation.update.resource_name == resource_name
    assert "conversion_value_rules" in operation.update_mask.paths


@pytest.mark.asyncio
async def test_remove_conversion_value_rule_set(
    service: ConversionValueRuleSetService, mock_ctx: Context
) -> None:
    """Test removing a conversion value rule set."""
    mock_client = service.client
    mock_client.mutate_conversion_value_rule_sets.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/123/conversionValueRuleSets/1"}]
    }
    resource_name = "customers/1234567890/conversionValueRuleSets/1"

    with patch(
        "src.services.conversions.conversion_value_rule_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_conversion_value_rule_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name=resource_name,
        )

    assert result == expected_result
    mock_client.mutate_conversion_value_rule_sets.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_conversion_value_rule_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].remove == resource_name


@pytest.mark.asyncio
async def test_create_conversion_value_rule_set_error(
    service: ConversionValueRuleSetService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in create."""
    mock_client = service.client
    mock_client.mutate_conversion_value_rule_sets.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.create_conversion_value_rule_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            dimensions=["GEO_LOCATION"],
            conversion_value_rules=[],
            attachment_type="CUSTOMER",
        )

    assert "Failed to create conversion value rule set" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_conversion_value_rule_set_error(
    service: ConversionValueRuleSetService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in remove."""
    mock_client = service.client
    mock_client.mutate_conversion_value_rule_sets.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.remove_conversion_value_rule_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/conversionValueRuleSets/1",
        )

    assert "Failed to remove conversion value rule set" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_conversion_value_rule_set_tools(mock_mcp)
    assert isinstance(svc, ConversionValueRuleSetService)
    assert mock_mcp.tool.call_count == 3  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert set(tool_names) == {
        "create_conversion_value_rule_set",
        "update_conversion_value_rule_set",
        "remove_conversion_value_rule_set",
    }
