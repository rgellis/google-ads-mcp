"""Tests for IdentityVerificationService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.account.identity_verification_service import (
    IdentityVerificationService,
    register_identity_verification_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> IdentityVerificationService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.account.identity_verification_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = IdentityVerificationService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_start_identity_verification(
    service: IdentityVerificationService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.start_identity_verification.return_value = None
    result = await service.start_identity_verification(
        ctx=mock_ctx,
        customer_id="1234567890",
        verification_program="ADVERTISER_IDENTITY_VERIFICATION",
    )
    assert result["status"] == "started"


@pytest.mark.asyncio
async def test_get_identity_verification(
    service: IdentityVerificationService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_response = Mock()
    mock_response.identity_verification = []
    mock_client.get_identity_verification.return_value = mock_response
    result = await service.get_identity_verification(
        ctx=mock_ctx, customer_id="1234567890"
    )
    assert isinstance(result, dict)


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_identity_verification_tools(mock_mcp)
    assert isinstance(service, IdentityVerificationService)
    assert mock_mcp.tool.call_count > 0
