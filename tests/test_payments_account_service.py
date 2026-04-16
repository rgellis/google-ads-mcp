"""Tests for PaymentsAccountService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.account.payments_account_service import (
    PaymentsAccountService,
    register_payments_account_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> PaymentsAccountService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.account.payments_account_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = PaymentsAccountService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_list_payments_accounts(
    service: PaymentsAccountService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_response = Mock()
    mock_response.payments_accounts = []
    mock_client.list_payments_accounts.return_value = mock_response
    result = await service.list_payments_accounts(
        ctx=mock_ctx, customer_id="1234567890"
    )
    assert isinstance(result, list)


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_payments_account_tools(mock_mcp)
    assert isinstance(service, PaymentsAccountService)
    assert mock_mcp.tool.call_count > 0
