"""Tests for CustomizerAttributeService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.shared.customizer_attribute_service import (
    CustomizerAttributeService,
    register_customizer_attribute_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomizerAttributeService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.shared.customizer_attribute_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomizerAttributeService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_customizer_attribute(
    service: CustomizerAttributeService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customizer_attributes.return_value = Mock()
    with patch(
        "src.services.shared.customizer_attribute_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.create_customizer_attribute(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="test_attr",
            attribute_type="TEXT",
        )
    assert result == {"results": []}
    mock_client.mutate_customizer_attributes.assert_called_once()


@pytest.mark.asyncio
async def test_remove_customizer_attribute(
    service: CustomizerAttributeService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customizer_attributes.return_value = Mock()
    with patch(
        "src.services.shared.customizer_attribute_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_customizer_attribute(
            ctx=mock_ctx,
            customer_id="1234567890",
            attribute_resource_name="customers/1234567890/customizerAttributes/1",
        )
    assert result == {"results": []}


@pytest.mark.asyncio
async def test_list_customizer_attributes(
    service: CustomizerAttributeService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    mock_google_ads_service = Mock()
    mock_attr = Mock()
    mock_attr.resource_name = "customers/1234567890/customizerAttributes/1"
    mock_attr.id = 1
    mock_attr.name = "test_attr"
    mock_attr.type_ = Mock()
    mock_attr.type_.name = "TEXT"
    mock_attr.status = Mock()
    mock_attr.status.name = "ENABLED"
    mock_row = Mock()
    mock_row.customizer_attribute = mock_attr
    mock_google_ads_service.search.return_value = [mock_row]

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.shared.customizer_attribute_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_customizer_attributes(
            ctx=mock_ctx,
            customer_id="1234567890",
        )
    assert len(result) == 1
    assert result[0]["name"] == "test_attr"
    mock_google_ads_service.search.assert_called_once()


@pytest.mark.asyncio
async def test_update_customizer_attribute(
    service: CustomizerAttributeService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customizer_attributes.return_value = Mock()
    with (
        patch(
            "src.services.shared.customizer_attribute_service.CustomizerAttributeOperation",
            return_value=Mock(),
        ),
        patch(
            "src.services.shared.customizer_attribute_service.MutateCustomizerAttributesRequest",
            return_value=Mock(),
        ),
        patch(
            "src.services.shared.customizer_attribute_service.serialize_proto_message",
            return_value={"results": []},
        ),
    ):
        result = await service.update_customizer_attribute(
            ctx=mock_ctx,
            customer_id="1234567890",
            attribute_resource_name="customers/1234567890/customizerAttributes/1",
            status="REMOVED",
        )
    assert result == {"results": []}
    mock_client.mutate_customizer_attributes.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_customizer_attribute_tools(mock_mcp)
    assert isinstance(service, CustomizerAttributeService)
    assert mock_mcp.tool.call_count > 0
