"""Tests for AssetSetAssetService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.assets.asset_set_asset_service import (
    AssetSetAssetService,
    register_asset_set_asset_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> AssetSetAssetService:
    """Create an AssetSetAssetService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.assets.asset_set_asset_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = AssetSetAssetService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_add_asset_to_set(
    service: AssetSetAssetService, mock_ctx: Context
) -> None:
    """Test adding an asset to an asset set."""
    mock_client = service.client
    mock_client.mutate_asset_set_assets.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/123/assetSetAssets/456~789"}]
    }

    with patch(
        "src.services.assets.asset_set_asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.add_asset_to_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_resource_name="customers/1234567890/assets/456",
            asset_set_resource_name="customers/1234567890/assetSets/789",
        )

    assert result == expected_result
    mock_client.mutate_asset_set_assets.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_asset_set_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    operation = request.operations[0]
    assert operation.create.asset == "customers/1234567890/assets/456"
    assert operation.create.asset_set == "customers/1234567890/assetSets/789"


@pytest.mark.asyncio
async def test_remove_asset_from_set(
    service: AssetSetAssetService, mock_ctx: Context
) -> None:
    """Test removing an asset from an asset set."""
    mock_client = service.client
    mock_client.mutate_asset_set_assets.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/123/assetSetAssets/456~789"}]
    }
    resource_name = "customers/1234567890/assetSetAssets/456~789"

    with patch(
        "src.services.assets.asset_set_asset_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_asset_from_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_set_asset_resource_name=resource_name,
        )

    assert result == expected_result
    mock_client.mutate_asset_set_assets.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_asset_set_assets.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    operation = request.operations[0]
    assert operation.remove == resource_name


@pytest.mark.asyncio
async def test_add_asset_to_set_error_handling(
    service: AssetSetAssetService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in add_asset_to_set."""
    mock_client = service.client
    mock_client.mutate_asset_set_assets.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.add_asset_to_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_resource_name="customers/1234567890/assets/456",
            asset_set_resource_name="customers/1234567890/assetSets/789",
        )

    assert "Failed to add asset to set" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_asset_from_set_error_handling(
    service: AssetSetAssetService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in remove_asset_from_set."""
    mock_client = service.client
    mock_client.mutate_asset_set_assets.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.remove_asset_from_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_set_asset_resource_name="customers/1234567890/assetSetAssets/456~789",
        )

    assert "Failed to remove asset from set" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_asset_set_asset_tools(mock_mcp)
    assert isinstance(svc, AssetSetAssetService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert set(tool_names) == {"add_asset_to_set", "remove_asset_from_set"}
