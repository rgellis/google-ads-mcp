"""Tests for GoalService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.account.goal_service import (
    GoalService,
    register_goal_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> GoalService:
    """Create a GoalService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.account.goal_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = GoalService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_mutate_goals_create(service: GoalService, mock_ctx: Context) -> None:
    """Test creating a retention goal with value settings."""
    mock_client = service.client
    mock_client.mutate_goals.return_value = Mock()  # type: ignore

    expected_result = {"results": [{"resource_name": "customers/1234567890/goals/1"}]}

    with patch(
        "src.services.account.goal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="create",
            retention_additional_value=10.0,
            retention_additional_high_lifetime_value=25.0,
        )

    assert result == expected_result
    mock_client.mutate_goals.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_goals.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    create = request.operations[0].create
    assert create.retention_goal_settings.value_settings.additional_value == 10.0
    assert (
        create.retention_goal_settings.value_settings.additional_high_lifetime_value
        == 25.0
    )


@pytest.mark.asyncio
async def test_mutate_goals_update(service: GoalService, mock_ctx: Context) -> None:
    """Test updating a retention goal's value settings."""
    mock_client = service.client
    mock_client.mutate_goals.return_value = Mock()  # type: ignore

    expected_result = {"results": [{"resource_name": "customers/1234567890/goals/1"}]}
    goal_rn = "customers/1234567890/goals/1"

    with patch(
        "src.services.account.goal_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.mutate_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            goal_resource_name=goal_rn,
            operation_type="update",
            retention_additional_value=15.0,
        )

    assert result == expected_result
    mock_client.mutate_goals.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_goals.call_args  # type: ignore
    request = call_args[1]["request"]
    op = request.operations[0]
    assert op.update.resource_name == goal_rn
    assert op.update.retention_goal_settings.value_settings.additional_value == 15.0
    assert list(op.update_mask.paths) == [
        "retention_goal_settings.value_settings.additional_value"
    ]


@pytest.mark.asyncio
async def test_mutate_goals_create_requires_value(
    service: GoalService, mock_ctx: Context
) -> None:
    """Create without retention_* params raises (proto has only that field settable)."""
    with pytest.raises(Exception, match="requires at least one of retention"):
        await service.mutate_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="create",
        )


@pytest.mark.asyncio
async def test_mutate_goals_error(
    service: GoalService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in mutate_goals."""
    mock_client = service.client
    mock_client.mutate_goals.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.mutate_goals(
            ctx=mock_ctx,
            customer_id="1234567890",
            operation_type="create",
            retention_additional_value=5.0,
        )

    assert "Failed to mutate goal" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_goal_tools(mock_mcp)
    assert isinstance(svc, GoalService)
    assert mock_mcp.tool.call_count == 1  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert tool_names == ["mutate_goal"]
