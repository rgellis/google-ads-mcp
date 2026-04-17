"""Tests for AdGroupAdLabelService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.ad_group.ad_group_ad_label_service import (
    AdGroupAdLabelService,
    register_ad_group_ad_label_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> AdGroupAdLabelService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.ad_group.ad_group_ad_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = AdGroupAdLabelService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_ad_group_ad_label(
    service: AdGroupAdLabelService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_ad_group_ad_labels.return_value = Mock()
    with patch(
        "src.services.ad_group.ad_group_ad_label_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.create_ad_group_ad_label(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group_ad_resource_name="customers/1234567890/adGroupAds/123~456",
            label_resource_name="customers/1234567890/labels/789",
        )
    assert result == {"results": []}
    mock_client.mutate_ad_group_ad_labels.assert_called_once()


@pytest.mark.asyncio
async def test_remove_ad_group_ad_label(
    service: AdGroupAdLabelService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_ad_group_ad_labels.return_value = Mock()
    with patch(
        "src.services.ad_group.ad_group_ad_label_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_ad_group_ad_label(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group_ad_label_resource_name="customers/1234567890/adGroupAdLabels/123~456~789",
        )
    assert result == {"results": []}


@pytest.mark.asyncio
async def test_list_ad_group_ad_labels(
    service: AdGroupAdLabelService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    """Test listing ad group ad labels."""
    from google.ads.googleads.v23.services.services.google_ads_service import (
        GoogleAdsServiceClient,
    )

    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search result
    row = Mock()
    row.ad_group_ad_label = Mock()
    row.ad_group_ad_label.resource_name = (
        "customers/1234567890/adGroupAdLabels/123~456~789"
    )
    row.ad_group_ad_label.ad_group_ad = "customers/1234567890/adGroupAds/123~456"
    row.ad_group_ad_label.label = "customers/1234567890/labels/789"
    row.ad_group_ad = Mock()
    row.ad_group_ad.ad = Mock()
    row.ad_group_ad.ad.id = 456
    row.ad_group_ad.ad_group = "customers/1234567890/adGroups/123"
    row.label = Mock()
    row.label.id = 789
    row.label.name = "Test Label"
    row.label.description = "A test label"

    mock_google_ads_service.search.return_value = [row]

    def get_service_side_effect(service_name: str):  # type: ignore
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.ad_group.ad_group_ad_label_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_ad_group_ad_labels(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert len(result) == 1
    assert (
        result[0]["resource_name"] == "customers/1234567890/adGroupAdLabels/123~456~789"
    )
    assert result[0]["label_name"] == "Test Label"
    assert result[0]["ad_id"] == "456"
    mock_google_ads_service.search.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_ad_group_ad_label_tools(mock_mcp)
    assert isinstance(service, AdGroupAdLabelService)
    assert mock_mcp.tool.call_count > 0
