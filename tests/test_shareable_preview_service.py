"""Tests for ShareablePreviewService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.metadata.shareable_preview_service import (
    ShareablePreviewService,
    register_shareable_preview_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ShareablePreviewService:
    """Create a ShareablePreviewService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.metadata.shareable_preview_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ShareablePreviewService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_generate_shareable_previews(
    service: ShareablePreviewService, mock_ctx: Context
) -> None:
    """Test generating shareable previews for asset groups."""
    mock_client = service.client
    mock_client.generate_shareable_previews.return_value = Mock()  # type: ignore

    expected_result = {
        "responses": [
            {
                "shareable_preview_url": "https://preview.example.com/abc123",
                "expiration_date_time": "2026-05-01 12:00:00",
            }
        ]
    }

    with patch(
        "src.services.metadata.shareable_preview_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_shareable_previews(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_group_ids=[111, 222],
        )

    assert result == expected_result
    mock_client.generate_shareable_previews.assert_called_once()  # type: ignore
    call_args = mock_client.generate_shareable_previews.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.shareable_previews) == 2
    assert request.shareable_previews[0].asset_group_identifier.asset_group_id == 111
    assert request.shareable_previews[1].asset_group_identifier.asset_group_id == 222


@pytest.mark.asyncio
async def test_generate_shareable_previews_single(
    service: ShareablePreviewService, mock_ctx: Context
) -> None:
    """Test generating a preview for a single asset group."""
    mock_client = service.client
    mock_client.generate_shareable_previews.return_value = Mock()  # type: ignore

    expected_result = {
        "responses": [{"shareable_preview_url": "https://preview.example.com/xyz"}]
    }

    with patch(
        "src.services.metadata.shareable_preview_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_shareable_previews(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_group_ids=[333],
        )

    assert result == expected_result
    call_args = mock_client.generate_shareable_previews.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.shareable_previews) == 1


@pytest.mark.asyncio
async def test_generate_shareable_previews_error(
    service: ShareablePreviewService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in generate_shareable_previews."""
    mock_client = service.client
    mock_client.generate_shareable_previews.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.generate_shareable_previews(
            ctx=mock_ctx,
            customer_id="1234567890",
            asset_group_ids=[111],
        )

    assert "Failed to generate shareable previews" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_shareable_preview_tools(mock_mcp)
    assert isinstance(svc, ShareablePreviewService)
    assert mock_mcp.tool.call_count == 1  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert tool_names == ["generate_shareable_previews"]
