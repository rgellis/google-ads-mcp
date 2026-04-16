"""Tests for CustomerCustomizerService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.account.customer_customizer_service import (
    CustomerCustomizerService,
    register_customer_customizer_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomerCustomizerService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.account.customer_customizer_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomerCustomizerService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_mutate_customer_customizers(
    service: CustomerCustomizerService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customer_customizers.return_value = Mock()
    with patch(
        "src.services.account.customer_customizer_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.mutate_customer_customizers(
            ctx=mock_ctx, customer_id="1234567890", operations=[Mock()]
        )
    assert result == {"results": []}
    mock_client.mutate_customer_customizers.assert_called_once()


@pytest.mark.asyncio
async def test_create_customer_customizer(
    service: CustomerCustomizerService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customer_customizers.return_value = Mock()
    with patch(
        "src.services.account.customer_customizer_service.serialize_proto_message",
        return_value={"results": [{"resource_name": "test"}]},
    ):
        result = await service.create_customer_customizer(
            ctx=mock_ctx,
            customer_id="1234567890",
            customizer_attribute_resource_name="customers/1234567890/customizerAttributes/1",
            value="test_value",
        )
    assert "results" in result


@pytest.mark.asyncio
async def test_remove_customer_customizer(
    service: CustomerCustomizerService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customer_customizers.return_value = Mock()
    with patch(
        "src.services.account.customer_customizer_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_customer_customizer(
            ctx=mock_ctx,
            customer_id="1234567890",
            customer_customizer_resource_name="customers/1234567890/customerCustomizers/1",
        )
    assert result == {"results": []}


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_customer_customizer_tools(mock_mcp)
    assert isinstance(service, CustomerCustomizerService)
    assert mock_mcp.tool.call_count > 0
