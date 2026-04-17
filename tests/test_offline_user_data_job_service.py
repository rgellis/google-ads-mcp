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


@pytest.mark.asyncio
async def test_add_user_data_operations(
    service: OfflineUserDataJobService, mock_ctx: Context
) -> None:
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

    result = await service.add_user_data_operations(
        ctx=mock_ctx,
        customer_id="1234567890",
        job_resource_name="customers/1234567890/offlineUserDataJobs/1",
        user_data_list=user_data_list,
    )

    assert result["job_resource_name"] == "customers/1234567890/offlineUserDataJobs/1"
    assert result["operations_added"] == 1
    assert result["partial_failure_error"] is None
    mock_client.add_offline_user_data_job_operations.assert_called_once()


@pytest.mark.asyncio
async def test_get_offline_user_data_job(
    service: OfflineUserDataJobService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    mock_google_ads_service = Mock()
    mock_row = Mock()
    mock_row.offline_user_data_job = Mock()
    mock_row.offline_user_data_job.resource_name = (
        "customers/1234567890/offlineUserDataJobs/1"
    )
    mock_google_ads_service.search.return_value = [mock_row]

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with (
        patch(
            "src.services.data_import.offline_user_data_job_service.get_sdk_client",
            return_value=mock_sdk_client,
        ),
        patch(
            "src.services.data_import.offline_user_data_job_service.serialize_proto_message",
            return_value={
                "resource_name": "customers/1234567890/offlineUserDataJobs/1"
            },
        ),
    ):
        result = await service.get_offline_user_data_job(
            ctx=mock_ctx,
            customer_id="1234567890",
            job_resource_name="customers/1234567890/offlineUserDataJobs/1",
        )
    assert result == {"resource_name": "customers/1234567890/offlineUserDataJobs/1"}
    mock_google_ads_service.search.assert_called_once()


@pytest.mark.asyncio
async def test_list_offline_user_data_jobs(
    service: OfflineUserDataJobService, mock_sdk_client: Any, mock_ctx: Context
) -> None:
    mock_google_ads_service = Mock()
    mock_job = Mock()
    mock_job.resource_name = "customers/1234567890/offlineUserDataJobs/1"
    mock_job.id = 1
    mock_job.type_ = Mock()
    mock_job.type_.name = "CUSTOMER_MATCH_USER_LIST"
    mock_job.status = Mock()
    mock_job.status.name = "SUCCESS"
    mock_job.failure_reason = None
    mock_job.operation_metadata = None
    mock_row = Mock()
    mock_row.offline_user_data_job = mock_job
    mock_google_ads_service.search.return_value = [mock_row]

    def get_service_side_effect(service_name: str):
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect

    with patch(
        "src.services.data_import.offline_user_data_job_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        result = await service.list_offline_user_data_jobs(
            ctx=mock_ctx,
            customer_id="1234567890",
        )
    assert len(result) == 1
    assert result[0]["resource_name"] == "customers/1234567890/offlineUserDataJobs/1"
    assert result[0]["status"] == "SUCCESS"
    mock_google_ads_service.search.assert_called_once()


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_offline_user_data_job_tools(mock_mcp)
    assert isinstance(service, OfflineUserDataJobService)
    assert mock_mcp.tool.call_count > 0
