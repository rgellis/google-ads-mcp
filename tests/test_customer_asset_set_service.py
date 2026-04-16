"""Tests for CustomerAssetSetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.assets.customer_asset_set_service import (
    CustomerAssetSetService,
    register_customer_asset_set_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomerAssetSetService:
    """Create a CustomerAssetSetService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.assets.customer_asset_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomerAssetSetService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_link_asset_set_to_customer(
    service: CustomerAssetSetService, mock_ctx: Context
) -> None:
    """Test linking an asset set to a customer."""
    mock_client = service.client
    mock_client.mutate_customer_asset_sets.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/customerAssetSets/1"}]
    }

    with patch(
        "src.services.assets.customer_asset_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.link_asset_set_to_customer(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_set_resource_name="customers/1234567890/assetSets/1",
        )

    assert result == expected_result
    mock_client.mutate_customer_asset_sets.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_customer_asset_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    assert request.operations[0].create.asset_set == "customers/1234567890/assetSets/1"


@pytest.mark.asyncio
async def test_unlink_asset_set_from_customer(
    service: CustomerAssetSetService, mock_ctx: Context
) -> None:
    """Test unlinking an asset set from a customer."""
    mock_client = service.client
    mock_client.mutate_customer_asset_sets.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/customerAssetSets/1"}]
    }
    resource_name = "customers/1234567890/customerAssetSets/1"

    with patch(
        "src.services.assets.customer_asset_set_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.unlink_asset_set_from_customer(
            ctx=mock_ctx,
            customer_id="1234567890",
            customer_asset_set_resource_name=resource_name,
        )

    assert result == expected_result
    mock_client.mutate_customer_asset_sets.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_customer_asset_sets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].remove == resource_name


@pytest.mark.asyncio
async def test_link_error_handling(
    service: CustomerAssetSetService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in link_asset_set_to_customer."""
    mock_client = service.client
    mock_client.mutate_customer_asset_sets.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.link_asset_set_to_customer(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_set_resource_name="customers/1234567890/assetSets/1",
        )

    assert "Failed to link asset set to customer" in str(exc_info.value)


@pytest.mark.asyncio
async def test_unlink_error_handling(
    service: CustomerAssetSetService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in unlink_asset_set_from_customer."""
    mock_client = service.client
    mock_client.mutate_customer_asset_sets.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.unlink_asset_set_from_customer(
            ctx=mock_ctx,
            customer_id="1234567890",
            customer_asset_set_resource_name="customers/1234567890/customerAssetSets/1",
        )

    assert "Failed to unlink asset set from customer" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_customer_asset_set_tools(mock_mcp)
    assert isinstance(svc, CustomerAssetSetService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert set(tool_names) == {
        "link_asset_set_to_customer",
        "unlink_asset_set_from_customer",
    }
