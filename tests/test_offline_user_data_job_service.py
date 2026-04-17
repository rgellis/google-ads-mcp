"""Tests for OfflineUserDataJobService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from fastmcp import Context
from src.services.data_import.offline_user_data_job_service import (
    OfflineUserDataJobService,
    register_offline_user_data_job_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> OfflineUserDataJobService:
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.data_import.offline_user_data_job_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = OfflineUserDataJobService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_customer_match_job(
    service: OfflineUserDataJobService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.create_offline_user_data_job.return_value = Mock()
    with patch(
        "src.services.data_import.offline_user_data_job_service.serialize_proto_message",
        return_value={"resource_name": "test"},
    ):
        result = await service.create_customer_match_job(
            ctx=mock_ctx,
            customer_id="1234567890",
            job_name="customers/1234567890/userLists/1",
        )
    assert result == {"resource_name": "test"}
    mock_client.create_offline_user_data_job.assert_called_once()


@pytest.mark.asyncio
async def test_run_offline_user_data_job(
    service: OfflineUserDataJobService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.run_offline_user_data_job.return_value = Mock()
    result = await service.run_offline_user_data_job(
        ctx=mock_ctx,
        customer_id="1234567890",
        job_resource_name="customers/1234567890/offlineUserDataJobs/1",
    )
    assert result["status"] == "RUNNING"
    assert result["job_resource_name"] == "customers/1234567890/offlineUserDataJobs/1"


@pytest.mark.asyncio
async def test_create_customer_match_job_validate_only(
    service: OfflineUserDataJobService, mock_ctx: Context
) -> None:
    """Test validate_only and enable_match_rate_range_preview reach the request."""
    mock_client = service.client
    mock_client.create_offline_user_data_job.return_value = Mock()
    with patch(
        "src.services.data_import.offline_user_data_job_service.serialize_proto_message",
        return_value={"resource_name": "test"},
    ):
        await service.create_customer_match_job(
            ctx=mock_ctx,
            customer_id="1234567890",
            validate_only=True,
            enable_match_rate_range_preview=True,
        )
    call_args = mock_client.create_offline_user_data_job.call_args
    request = call_args[1]["request"]
    assert request.validate_only is True
    assert request.enable_match_rate_range_preview is True


@pytest.mark.asyncio
async def test_run_offline_user_data_job_validate_only(
    service: OfflineUserDataJobService, mock_ctx: Context
) -> None:
    """Test validate_only reaches the RunOfflineUserDataJob request."""
    mock_client = service.client
    mock_client.run_offline_user_data_job.return_value = Mock()
    await service.run_offline_user_data_job(
        ctx=mock_ctx,
        customer_id="1234567890",
        job_resource_name="customers/1234567890/offlineUserDataJobs/1",
        validate_only=True,
    )
    call_args = mock_client.run_offline_user_data_job.call_args
    request = call_args[1]["request"]
    assert request.validate_only is True


@pytest.mark.asyncio
async def test_remove_user_data_operations(
    service: OfflineUserDataJobService, mock_ctx: Context
) -> None:
    """Test removing user data operations from a job."""
    mock_client = service.client
    mock_response = Mock()
    mock_response.partial_failure_error = None
    mock_client.add_offline_user_data_job_operations.return_value = mock_response

    user_data_list = [
        {
            "user_identifiers": [
                {"hashed_email": "abc123hash"},
            ]
        }
    ]

    result = await service.remove_user_data_operations(
        ctx=mock_ctx,
        customer_id="1234567890",
        job_resource_name="customers/1234567890/offlineUserDataJobs/1",
        user_data_list=user_data_list,
    )

    assert result["job_resource_name"] == "customers/1234567890/offlineUserDataJobs/1"
    assert result["operations_removed"] == 1
    assert result["partial_failure_error"] is None
    mock_client.add_offline_user_data_job_operations.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_offline_user_data_job_tools(mock_mcp)
    assert isinstance(service, OfflineUserDataJobService)
    assert mock_mcp.tool.call_count > 0
