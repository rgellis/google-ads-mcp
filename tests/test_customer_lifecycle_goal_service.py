"""Tests for CustomerLifecycleGoalService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.account.customer_lifecycle_goal_service import (
    CustomerLifecycleGoalService,
    register_customer_lifecycle_goal_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CustomerLifecycleGoalService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.account.customer_lifecycle_goal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CustomerLifecycleGoalService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_configure_create(
    service: CustomerLifecycleGoalService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.configure_customer_lifecycle_goals.return_value = Mock()  # type: ignore

    with patch(
        "src.services.account.customer_lifecycle_goal_service.serialize_proto_message",
        return_value={"result": {}},
    ):
        await service.configure_customer_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="CREATE",
            value=15.0,
            high_lifetime_value=75.0,
        )

    request = mock_client.configure_customer_lifecycle_goals.call_args[1]["request"]  # type: ignore
    op = request.operation
    settings = op.create.customer_acquisition_goal_value_settings
    assert settings.value == 15.0
    assert settings.high_lifetime_value == 75.0


@pytest.mark.asyncio
async def test_configure_update(
    service: CustomerLifecycleGoalService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.configure_customer_lifecycle_goals.return_value = Mock()  # type: ignore

    with patch(
        "src.services.account.customer_lifecycle_goal_service.serialize_proto_message",
        return_value={"result": {}},
    ):
        await service.configure_customer_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="UPDATE",
            value=20.0,
        )

    request = mock_client.configure_customer_lifecycle_goals.call_args[1]["request"]  # type: ignore
    op = request.operation
    assert op.update.resource_name == "customers/1234567890/customerLifecycleGoal"
    paths = list(op.update_mask.paths)
    assert "customer_acquisition_goal_value_settings" in paths


@pytest.mark.asyncio
async def test_invalid_operation_type(
    service: CustomerLifecycleGoalService, mock_ctx: Context
) -> None:
    with pytest.raises(ValueError, match="must be CREATE or UPDATE"):
        await service.configure_customer_lifecycle_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="DELETE",
        )


def test_register_tools() -> None:
    mock_mcp = Mock()
    svc = register_customer_lifecycle_goal_tools(mock_mcp)
    assert isinstance(svc, CustomerLifecycleGoalService)
    assert mock_mcp.tool.call_count == 1
