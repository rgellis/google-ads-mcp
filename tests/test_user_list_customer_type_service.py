"""Tests for UserListCustomerTypeService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.audiences.user_list_customer_type_service import (
    UserListCustomerTypeService,
    register_user_list_customer_type_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> UserListCustomerTypeService:
    """Create a UserListCustomerTypeService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.audiences.user_list_customer_type_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = UserListCustomerTypeService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_add_customer_type(
    service: UserListCustomerTypeService, mock_ctx: Context
) -> None:
    """Test adding a customer type to a user list."""
    mock_client = service.client
    mock_client.mutate_user_list_customer_types.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/userListCustomerTypes/1~PURCHASERS"}
        ]
    }

    with patch(
        "src.services.audiences.user_list_customer_type_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.add_customer_type(
            ctx=mock_ctx,
            customer_id="1234567890",
            user_list_resource_name="customers/1234567890/userLists/1",
            customer_type_category="PURCHASERS",
        )

    assert result == expected_result
    mock_client.mutate_user_list_customer_types.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_user_list_customer_types.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    assert request.operations[0].create.user_list == "customers/1234567890/userLists/1"


@pytest.mark.asyncio
async def test_remove_customer_type(
    service: UserListCustomerTypeService, mock_ctx: Context
) -> None:
    """Test removing a customer type from a user list."""
    mock_client = service.client
    mock_client.mutate_user_list_customer_types.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [
            {"resource_name": "customers/1234567890/userListCustomerTypes/1~PURCHASERS"}
        ]
    }
    resource_name = "customers/1234567890/userListCustomerTypes/1~PURCHASERS"

    with patch(
        "src.services.audiences.user_list_customer_type_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_customer_type(
            ctx=mock_ctx,
            customer_id="1234567890",
            user_list_customer_type_resource_name=resource_name,
        )

    assert result == expected_result
    mock_client.mutate_user_list_customer_types.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_user_list_customer_types.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].remove == resource_name


@pytest.mark.asyncio
async def test_add_customer_type_error(
    service: UserListCustomerTypeService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in add_customer_type."""
    mock_client = service.client
    mock_client.mutate_user_list_customer_types.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.add_customer_type(
            ctx=mock_ctx,
            customer_id="1234567890",
            user_list_resource_name="customers/1234567890/userLists/1",
            customer_type_category="PURCHASERS",
        )

    assert "Failed to add customer type" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_customer_type_error(
    service: UserListCustomerTypeService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in remove_customer_type."""
    mock_client = service.client
    mock_client.mutate_user_list_customer_types.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.remove_customer_type(
            ctx=mock_ctx,
            customer_id="1234567890",
            user_list_customer_type_resource_name="customers/1234567890/userListCustomerTypes/1~PURCHASERS",
        )

    assert "Failed to remove customer type" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_user_list_customer_type_tools(mock_mcp)
    assert isinstance(svc, UserListCustomerTypeService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert set(tool_names) == {
        "add_customer_type_to_user_list",
        "remove_customer_type_from_user_list",
    }
