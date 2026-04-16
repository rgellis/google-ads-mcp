"""Tests for ProductLinkInvitationService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.product_integration.product_link_invitation_service import (
    ProductLinkInvitationService,
    register_product_link_invitation_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> ProductLinkInvitationService:
    """Create a ProductLinkInvitationService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.product_integration.product_link_invitation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = ProductLinkInvitationService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_invitation(
    service: ProductLinkInvitationService,
    mock_ctx: Context,
) -> None:
    """Test creating a product link invitation."""
    mock_client = service.client
    mock_client.create_product_link_invitation.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/productLinkInvitations/111"
    }

    with patch(
        "src.services.product_integration.product_link_invitation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.create_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            link_type="MERCHANT_CENTER",
            linked_account="12345",
        )

    assert result == expected_result
    mock_client.create_product_link_invitation.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_create_invitation_merchant_center(
    service: ProductLinkInvitationService,
    mock_ctx: Context,
) -> None:
    """Test creating a Merchant Center product link invitation."""
    mock_client = service.client
    mock_client.create_product_link_invitation.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/productLinkInvitations/222"
    }

    with patch(
        "src.services.product_integration.product_link_invitation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.create_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            link_type="MERCHANT_CENTER",
            linked_account="12345678",
        )

    assert result == expected_result
    mock_client.create_product_link_invitation.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_create_invitation_error(
    service: ProductLinkInvitationService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating invitation fails."""
    mock_client = service.client
    mock_client.create_product_link_invitation.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.create_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            link_type="MERCHANT_CENTER",
            linked_account="12345",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_invitation(
    service: ProductLinkInvitationService,
    mock_ctx: Context,
) -> None:
    """Test updating a product link invitation."""
    mock_client = service.client
    mock_client.update_product_link_invitation.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/productLinkInvitations/111"
    }

    with patch(
        "src.services.product_integration.product_link_invitation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.update_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/productLinkInvitations/111",
            status="ACCEPTED",
        )

    assert result == expected_result
    mock_client.update_product_link_invitation.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_update_invitation_error(
    service: ProductLinkInvitationService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating invitation fails."""
    mock_client = service.client
    mock_client.update_product_link_invitation.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.update_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/productLinkInvitations/111",
            status="ACCEPTED",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_invitation(
    service: ProductLinkInvitationService,
    mock_ctx: Context,
) -> None:
    """Test removing a product link invitation."""
    mock_client = service.client
    mock_client.remove_product_link_invitation.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/productLinkInvitations/111"
    }

    with patch(
        "src.services.product_integration.product_link_invitation_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/productLinkInvitations/111",
        )

    assert result == expected_result
    mock_client.remove_product_link_invitation.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_remove_invitation_error(
    service: ProductLinkInvitationService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when removing invitation fails."""
    mock_client = service.client
    mock_client.remove_product_link_invitation.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.remove_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/productLinkInvitations/111",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_product_link_invitation_tools(mock_mcp)
    assert isinstance(svc, ProductLinkInvitationService)
    assert mock_mcp.tool.call_count == 3  # type: ignore
