"""Tests for DataLinkService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.data_import.data_link_service import (
    DataLinkService,
    register_data_link_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> DataLinkService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.data_import.data_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = DataLinkService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_data_link(service: DataLinkService, mock_ctx: Context) -> None:
    mock_client = service.client
    mock_client.create_data_link.return_value = Mock()
    with patch(
        "src.services.data_import.data_link_service.serialize_proto_message",
        return_value={"resource_name": "test"},
    ):
        result = await service.create_data_link(
            ctx=mock_ctx, customer_id="1234567890", youtube_video_channel_id="UC123"
        )
    assert result == {"resource_name": "test"}
    mock_client.create_data_link.assert_called_once()


@pytest.mark.asyncio
async def test_remove_data_link(service: DataLinkService, mock_ctx: Context) -> None:
    mock_client = service.client
    mock_client.remove_data_link.return_value = Mock()
    with patch(
        "src.services.data_import.data_link_service.serialize_proto_message",
        return_value={"resource_name": "test"},
    ):
        result = await service.remove_data_link(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/dataLinks/1",
        )
    assert result == {"resource_name": "test"}


@pytest.mark.asyncio
async def test_update_data_link(service: DataLinkService, mock_ctx: Context) -> None:
    mock_client = service.client
    mock_client.update_data_link.return_value = Mock()
    from google.ads.googleads.v23.enums.types.data_link_status import DataLinkStatusEnum

    with patch(
        "src.services.data_import.data_link_service.serialize_proto_message",
        return_value={"resource_name": "test"},
    ):
        result = await service.update_data_link(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/dataLinks/1",
            data_link_status=DataLinkStatusEnum.DataLinkStatus.ENABLED,
        )
    assert result == {"resource_name": "test"}


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_data_link_tools(mock_mcp)
    assert isinstance(service, DataLinkService)
    assert mock_mcp.tool.call_count == 4
