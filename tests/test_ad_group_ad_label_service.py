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


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_ad_group_ad_label_tools(mock_mcp)
    assert isinstance(service, AdGroupAdLabelService)
    assert mock_mcp.tool.call_count > 0
