"""Tests for AssetGroupListingGroupFilterService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.assets.asset_group_listing_group_filter_service import (
    AssetGroupListingGroupFilterService,
    register_asset_group_listing_group_filter_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> AssetGroupListingGroupFilterService:
    """Create an AssetGroupListingGroupFilterService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.assets.asset_group_listing_group_filter_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = AssetGroupListingGroupFilterService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_listing_group_filter(
    service: AssetGroupListingGroupFilterService, mock_ctx: Context
) -> None:
    """Test creating a listing group filter."""
    mock_client = service.client
    mock_client.mutate_asset_group_listing_group_filters.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/assetGroupListingGroupFilters/1~2"}
        ]
    }
    asset_group_rn = "customers/1234567890/assetGroups/1"

    with patch(
        "src.services.assets.asset_group_listing_group_filter_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.create_listing_group_filter(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_group_resource_name=asset_group_rn,
            filter_type="UNIT_INCLUDED",
        )

    assert result == expected_result
    mock_client.mutate_asset_group_listing_group_filters.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_asset_group_listing_group_filters.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    assert request.operations[0].create.asset_group == asset_group_rn


@pytest.mark.asyncio
async def test_create_listing_group_filter_with_parent(
    service: AssetGroupListingGroupFilterService, mock_ctx: Context
) -> None:
    """Test creating a listing group filter with a parent."""
    mock_client = service.client
    mock_client.mutate_asset_group_listing_group_filters.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [
            {"resource_name": "customers/123/assetGroupListingGroupFilters/1~3"}
        ]
    }
    asset_group_rn = "customers/1234567890/assetGroups/1"
    parent_rn = "customers/1234567890/assetGroupListingGroupFilters/1~2"

    with patch(
        "src.services.assets.asset_group_listing_group_filter_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.create_listing_group_filter(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_group_resource_name=asset_group_rn,
            filter_type="SUBDIVISION",
            parent_listing_group_filter=parent_rn,
        )

    assert result == expected_result
    call_args = mock_client.mutate_asset_group_listing_group_filters.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].create.parent_listing_group_filter == parent_rn


@pytest.mark.asyncio
async def test_remove_listing_group_filter(
    service: AssetGroupListingGroupFilterService, mock_ctx: Context
) -> None:
    """Test removing a listing group filter."""
    mock_client = service.client
    mock_client.mutate_asset_group_listing_group_filters.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [
            {"resource_name": "customers/123/assetGroupListingGroupFilters/1~2"}
        ]
    }
    resource_name = "customers/1234567890/assetGroupListingGroupFilters/1~2"

    with patch(
        "src.services.assets.asset_group_listing_group_filter_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_listing_group_filter(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name=resource_name,
        )

    assert result == expected_result
    mock_client.mutate_asset_group_listing_group_filters.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_asset_group_listing_group_filters.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].remove == resource_name


@pytest.mark.asyncio
async def test_create_listing_group_filter_error(
    service: AssetGroupListingGroupFilterService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in create_listing_group_filter."""
    mock_client = service.client
    mock_client.mutate_asset_group_listing_group_filters.side_effect = (
        google_ads_exception  # type: ignore
    )

    with pytest.raises(Exception) as exc_info:
        await service.create_listing_group_filter(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_group_resource_name="customers/1234567890/assetGroups/1",
            filter_type="UNIT_INCLUDED",
        )

    assert "Failed to create listing group filter" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_listing_group_filter_error(
    service: AssetGroupListingGroupFilterService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in remove_listing_group_filter."""
    mock_client = service.client
    mock_client.mutate_asset_group_listing_group_filters.side_effect = (
        google_ads_exception  # type: ignore
    )

    with pytest.raises(Exception) as exc_info:
        await service.remove_listing_group_filter(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/assetGroupListingGroupFilters/1~2",
        )

    assert "Failed to remove listing group filter" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_asset_group_listing_group_filter_tools(mock_mcp)
    assert isinstance(svc, AssetGroupListingGroupFilterService)
    assert mock_mcp.tool.call_count == 3  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert set(tool_names) == {
        "create_listing_group_filter",
        "remove_listing_group_filter",
        "update_listing_group_filter",
    }
