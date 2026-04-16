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


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_customizer_attribute_tools(mock_mcp)
    assert isinstance(service, CustomizerAttributeService)
    assert mock_mcp.tool.call_count > 0
