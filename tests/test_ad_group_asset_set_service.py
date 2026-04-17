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
            ad_group_resource_name="customers/1234567890/adGroups/111",
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


@pytest.mark.asyncio
async def test_list_ad_group_asset_sets(
    service: AdGroupAssetSetService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    """Test listing ad group asset sets."""
    from google.ads.googleads.v23.services.services.google_ads_service import (
        GoogleAdsServiceClient,
    )

    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result
    row = Mock()
    row.ad_group_asset_set = Mock()
    row.ad_group_asset_set.resource_name = (
        "customers/1234567890/adGroupAssetSets/111~222"
    )
    row.ad_group_asset_set.ad_group = "customers/1234567890/adGroups/111"
    row.ad_group_asset_set.asset_set = "customers/1234567890/assetSets/222"
    row.ad_group_asset_set.status = Mock()
    row.ad_group_asset_set.status.name = "ENABLED"
    row.ad_group = Mock()
    row.ad_group.id = 111
    row.ad_group.name = "Test Ad Group"
    row.asset_set = Mock()
    row.asset_set.id = 222
    row.asset_set.name = "Test Asset Set"
    row.asset_set.type_ = Mock()
    row.asset_set.type_.name = "PAGE_FEED"

    mock_google_ads_service.search.return_value = [row]

    def get_service_side_effect(service_name: str):  # type: ignore
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.ad_group.ad_group_asset_set_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_ad_group_asset_sets(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert len(result) == 1
    assert result[0]["resource_name"] == "customers/1234567890/adGroupAssetSets/111~222"
    assert result[0]["ad_group_name"] == "Test Ad Group"
    assert result[0]["asset_set_name"] == "Test Asset Set"
    assert result[0]["status"] == "ENABLED"
    mock_google_ads_service.search.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_ad_group_asset_set_tools(mock_mcp)
    assert isinstance(service, AdGroupAssetSetService)
    assert mock_mcp.tool.call_count > 0
