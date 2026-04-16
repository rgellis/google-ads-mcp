"""Tests for CustomerSkAdNetworkService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.account.customer_sk_ad_network_service import (
    CustomerSkAdNetworkService,
    register_customer_sk_ad_network_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomerSkAdNetworkService:
    """Create a CustomerSkAdNetworkService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.account.customer_sk_ad_network_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomerSkAdNetworkService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_mutate_schema(
    service: CustomerSkAdNetworkService,
    mock_ctx: Context,
) -> None:
    """Test mutating the SKAdNetwork conversion value schema."""
    mock_client = service.client
    mock_client.mutate_customer_sk_ad_network_conversion_value_schema.return_value = (
        Mock()
    )  # type: ignore

    expected_result = {
        "result": {
            "resource_name": "customers/1234567890/customerSkAdNetworkConversionValueSchemas/~"
        }
    }

    with patch(
        "src.services.account.customer_sk_ad_network_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_schema(
            ctx=mock_ctx,
            customer_id="1234567890",
            schema={"app_id": "com.example.app", "measurement_window_hours": 24},
        )

    assert result == expected_result
    mock_client.mutate_customer_sk_ad_network_conversion_value_schema.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_mutate_schema_minimal(
    service: CustomerSkAdNetworkService,
    mock_ctx: Context,
) -> None:
    """Test mutating schema with minimal data."""
    mock_client = service.client
    mock_client.mutate_customer_sk_ad_network_conversion_value_schema.return_value = (
        Mock()
    )  # type: ignore

    expected_result = {"result": {}}

    with patch(
        "src.services.account.customer_sk_ad_network_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_schema(
            ctx=mock_ctx,
            customer_id="1234567890",
            schema={},
        )

    assert result == expected_result
    mock_client.mutate_customer_sk_ad_network_conversion_value_schema.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_mutate_schema_error(
    service: CustomerSkAdNetworkService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when mutating schema fails."""
    mock_client = service.client
    mock_client.mutate_customer_sk_ad_network_conversion_value_schema.side_effect = (
        google_ads_exception  # type: ignore
    )

    with pytest.raises(Exception) as exc_info:
        await service.mutate_schema(
            ctx=mock_ctx,
            customer_id="1234567890",
            schema={"app_id": "com.example.app"},
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_customer_sk_ad_network_tools(mock_mcp)
    assert isinstance(svc, CustomerSkAdNetworkService)
    assert mock_mcp.tool.call_count > 0  # type: ignore
