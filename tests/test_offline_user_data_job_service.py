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
            user_list_resource_name="customers/1234567890/userLists/1",
        )
    assert result == {"resource_name": "test"}
    mock_client.create_offline_user_data_job.assert_called_once()


@pytest.mark.asyncio
async def test_run_offline_user_data_job(
    service: OfflineUserDataJobService, mock_ctx: Context
) -> None:
    mock_client = service.client
    mock_client.run_offline_user_data_job.return_value = Mock()
    with patch(
        "src.services.data_import.offline_user_data_job_service.serialize_proto_message",
        return_value={"status": "running"},
    ):
        result = await service.run_offline_user_data_job(
            ctx=mock_ctx,
            customer_id="1234567890",
            job_resource_name="customers/1234567890/offlineUserDataJobs/1",
        )
    assert result == {"status": "running"}


def test_register_tools() -> None:
    mock_mcp = Mock()
    service = register_offline_user_data_job_tools(mock_mcp)
    assert isinstance(service, OfflineUserDataJobService)
    assert mock_mcp.tool.call_count > 0
