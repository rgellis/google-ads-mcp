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
