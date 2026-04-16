"""Tests for LocalServicesLeadService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.data_import.local_services_lead_service import (
    LocalServicesLeadService,
    register_local_services_lead_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> LocalServicesLeadService:
    """Create a LocalServicesLeadService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.data_import.local_services_lead_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = LocalServicesLeadService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_append_lead_conversation(
    service: LocalServicesLeadService,
    mock_ctx: Context,
) -> None:
    """Test appending conversations to a local services lead."""
    mock_client = service.client
    mock_client.append_lead_conversation.return_value = Mock()  # type: ignore

    expected_result = {
        "responses": [
            {
                "local_services_lead_conversation": "customers/123/localServicesLeadConversations/456"
            }
        ]
    }

    conversations = [
        {
            "local_services_lead": "customers/1234567890/localServicesLeads/111",
            "text": "Hello, I'd like to schedule a service.",
        }
    ]

    with patch(
        "src.services.data_import.local_services_lead_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.append_lead_conversation(
            ctx=mock_ctx,
            customer_id="1234567890",
            conversations=conversations,
        )

    assert result == expected_result
    mock_client.append_lead_conversation.assert_called_once()  # type: ignore
    call_args = mock_client.append_lead_conversation.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.conversations) == 1


@pytest.mark.asyncio
async def test_append_lead_conversation_error(
    service: LocalServicesLeadService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when appending conversation fails."""
    mock_client = service.client
    mock_client.append_lead_conversation.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.append_lead_conversation(
            ctx=mock_ctx,
            customer_id="1234567890",
            conversations=[
                {
                    "local_services_lead": "customers/1234567890/localServicesLeads/111",
                    "text": "Hello",
                }
            ],
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_provide_lead_feedback(
    service: LocalServicesLeadService,
    mock_ctx: Context,
) -> None:
    """Test providing feedback for a local services lead."""
    mock_client = service.client
    mock_client.provide_lead_feedback.return_value = Mock()  # type: ignore

    expected_result = {"resource_name": "customers/1234567890/localServicesLeads/111"}

    with patch(
        "src.services.data_import.local_services_lead_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.provide_lead_feedback(
            ctx=mock_ctx,
            resource_name="customers/1234567890/localServicesLeads/111",
            survey_answer="SATISFIED",
        )

    assert result == expected_result
    mock_client.provide_lead_feedback.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_provide_lead_feedback_error(
    service: LocalServicesLeadService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when providing feedback fails."""
    mock_client = service.client
    mock_client.provide_lead_feedback.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.provide_lead_feedback(
            ctx=mock_ctx,
            resource_name="customers/1234567890/localServicesLeads/111",
            survey_answer="SATISFIED",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_local_services_lead_tools(mock_mcp)
    assert isinstance(svc, LocalServicesLeadService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
