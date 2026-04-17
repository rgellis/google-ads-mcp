"""Tests for CustomerUserAccessInvitationService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.account.customer_user_access_invitation_service import (
    CustomerUserAccessInvitationService,
    register_customer_user_access_invitation_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomerUserAccessInvitationService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.account.customer_user_access_invitation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomerUserAccessInvitationService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_invitation(
    service: CustomerUserAccessInvitationService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customer_user_access_invitation.return_value = Mock()
    with patch(
        "src.services.account.customer_user_access_invitation_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.create_customer_user_access_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            email_address="test@example.com",
            access_role="ADMIN",
        )
    assert result == {"results": []}
    mock_client.mutate_customer_user_access_invitation.assert_called_once()


@pytest.mark.asyncio
async def test_create_customer_user_access_invitation(
    service: CustomerUserAccessInvitationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test creating a customer user access invitation."""
    mock_client = service.client
    mock_client.mutate_customer_user_access_invitation.return_value = Mock()
    expected = {
        "result": {
            "resource_name": "customers/1234567890/customerUserAccessInvitations/1"
        }
    }
    with patch(
        "src.services.account.customer_user_access_invitation_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await service.create_customer_user_access_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            email_address="newuser@example.com",
            access_role="STANDARD",
        )
    assert result == expected
    mock_client.mutate_customer_user_access_invitation.assert_called_once()


@pytest.mark.asyncio
async def test_list_customer_user_access_invitations(
    service: CustomerUserAccessInvitationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing customer user access invitations."""
    # Mock GoogleAdsService for search
    from google.ads.googleads.v23.services.services.google_ads_service import (
        GoogleAdsServiceClient,
    )

    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    # Create mock search results
    row = Mock()
    row.customer_user_access_invitation = Mock()
    row.customer_user_access_invitation.resource_name = (
        "customers/1234567890/customerUserAccessInvitations/1"
    )
    row.customer_user_access_invitation.invitation_id = 1
    row.customer_user_access_invitation.access_role = Mock()
    row.customer_user_access_invitation.access_role.name = "ADMIN"
    row.customer_user_access_invitation.email_address = "test@example.com"
    row.customer_user_access_invitation.creation_date_time = "2026-01-01"
    row.customer_user_access_invitation.invitation_status = Mock()
    row.customer_user_access_invitation.invitation_status.name = "PENDING"

    mock_google_ads_service.search.return_value = [row]

    def get_service_side_effect(service_name: str):  # type: ignore
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.account.customer_user_access_invitation_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_customer_user_access_invitations(
            ctx=mock_ctx,
            customer_id="1234567890",
        )

    assert len(result) == 1
    assert result[0]["email_address"] == "test@example.com"
    assert result[0]["invitation_status"] == "PENDING"
    mock_google_ads_service.search.assert_called_once()


@pytest.mark.asyncio
async def test_remove_customer_user_access_invitation(
    service: CustomerUserAccessInvitationService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test removing a customer user access invitation."""
    mock_client = service.client
    mock_client.mutate_customer_user_access_invitation.return_value = Mock()
    expected = {
        "result": {
            "resource_name": "customers/1234567890/customerUserAccessInvitations/1"
        }
    }
    with patch(
        "src.services.account.customer_user_access_invitation_service.serialize_proto_message",
        return_value=expected,
    ):
        result = await service.remove_customer_user_access_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            invitation_resource_name="customers/1234567890/customerUserAccessInvitations/1",
        )
    assert result == expected
    mock_client.mutate_customer_user_access_invitation.assert_called_once()


@pytest.mark.asyncio
async def test_remove_invitation(
    service: CustomerUserAccessInvitationService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.mutate_customer_user_access_invitation.return_value = Mock()
    with patch(
        "src.services.account.customer_user_access_invitation_service.serialize_proto_message",
        return_value={"results": []},
    ):
        result = await service.remove_customer_user_access_invitation(
            ctx=mock_ctx,
            customer_id="1234567890",
            invitation_resource_name="customers/1234567890/customerUserAccessInvitations/1",
        )
    assert result == {"results": []}


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_customer_user_access_invitation_tools(mock_mcp)
    assert isinstance(service, CustomerUserAccessInvitationService)
    assert mock_mcp.tool.call_count > 0
