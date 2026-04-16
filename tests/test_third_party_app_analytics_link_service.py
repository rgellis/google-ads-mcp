"""Tests for ThirdPartyAppAnalyticsLinkService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.product_integration.third_party_app_analytics_link_service import (
    ThirdPartyAppAnalyticsLinkService,
    register_third_party_app_analytics_link_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ThirdPartyAppAnalyticsLinkService:
    """Create a ThirdPartyAppAnalyticsLinkService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.product_integration.third_party_app_analytics_link_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ThirdPartyAppAnalyticsLinkService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_regenerate_shareable_link_id(
    service: ThirdPartyAppAnalyticsLinkService, mock_ctx: Context
) -> None:
    """Test regenerating the shareable link ID."""
    mock_client = service.client
    mock_client.regenerate_shareable_link_id.return_value = Mock()  # type: ignore

    expected_result = {"shareable_link_id": "new_link_id_abc123"}
    resource_name = "customers/1234567890/thirdPartyAppAnalyticsLinks/1"

    with patch(
        "src.services.product_integration.third_party_app_analytics_link_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.regenerate_shareable_link_id(
            ctx=mock_ctx,
            resource_name=resource_name,
        )

    assert result == expected_result
    mock_client.regenerate_shareable_link_id.assert_called_once()  # type: ignore
    call_args = mock_client.regenerate_shareable_link_id.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.resource_name == resource_name


@pytest.mark.asyncio
async def test_regenerate_shareable_link_id_error(
    service: ThirdPartyAppAnalyticsLinkService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in regenerate_shareable_link_id."""
    mock_client = service.client
    mock_client.regenerate_shareable_link_id.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.regenerate_shareable_link_id(
            ctx=mock_ctx,
            resource_name="customers/1234567890/thirdPartyAppAnalyticsLinks/1",
        )

    assert "Failed to regenerate shareable link ID" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_third_party_app_analytics_link_tools(mock_mcp)
    assert isinstance(svc, ThirdPartyAppAnalyticsLinkService)
    assert mock_mcp.tool.call_count == 1  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert tool_names == ["regenerate_shareable_link_id"]
