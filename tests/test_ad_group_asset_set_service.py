"""Tests for AdGroupAssetSetService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.ad_group.ad_group_asset_set_service import (
    AdGroupAssetSetService,
    register_ad_group_asset_set_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> AdGroupAssetSetService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.ad_group.ad_group_asset_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = AdGroupAssetSetService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_ad_group_asset_set(
    service: AdGroupAssetSetService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_ad_group_asset_sets.return_value = Mock()
    with patch(
        "src.services.ad_group.ad_group_asset_set_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.create_ad_group_asset_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group_id="111",
            asset_set_resource_name="customers/1234567890/assetSets/222",
        )
    assert result == {"results": []}
    mock_client.mutate_ad_group_asset_sets.assert_called_once()


@pytest.mark.asyncio
async def test_remove_ad_group_asset_set(
    service: AdGroupAssetSetService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_ad_group_asset_sets.return_value = Mock()
    with patch(
        "src.services.ad_group.ad_group_asset_set_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_ad_group_asset_set(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group_asset_set_resource_name="customers/1234567890/adGroupAssetSets/111~222",
        )
    assert result == {"results": []}


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_ad_group_asset_set_tools(mock_mcp)
    assert isinstance(service, AdGroupAssetSetService)
    assert mock_mcp.tool.call_count > 0
