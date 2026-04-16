"""Tests for ConversionAdjustmentUploadService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.conversions.conversion_adjustment_upload_service import (
    ConversionAdjustmentUploadService,
    register_conversion_adjustment_upload_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ConversionAdjustmentUploadService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.conversions.conversion_adjustment_upload_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ConversionAdjustmentUploadService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_upload_conversion_adjustments(
    service: ConversionAdjustmentUploadService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.upload_conversion_adjustments.return_value = Mock()
    with patch(
        "src.services.conversions.conversion_adjustment_upload_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.upload_conversion_adjustments(
            ctx=mock_ctx,
            customer_id="1234567890",
            adjustments=[Mock()],
            partial_failure=True,
        )
    assert result == {"results": []}
    mock_client.upload_conversion_adjustments.assert_called_once()


@pytest.mark.asyncio
async def test_create_restatement_adjustment(
    service: ConversionAdjustmentUploadService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.upload_conversion_adjustments.return_value = Mock()
    with patch(
        "src.services.conversions.conversion_adjustment_upload_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.create_restatement_adjustment(
            ctx=mock_ctx,
            customer_id="1234567890",
            conversion_action_resource_name="customers/1234567890/conversionActions/1",
            order_id="order123",
            adjustment_date_time="2026-01-01 00:00:00",
            restated_value=50.0,
        )
    assert result == {"results": []}


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_conversion_adjustment_upload_tools(mock_mcp)
    assert isinstance(service, ConversionAdjustmentUploadService)
    assert mock_mcp.tool.call_count > 0
