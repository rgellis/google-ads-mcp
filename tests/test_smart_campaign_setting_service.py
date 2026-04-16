"""Tests for SmartCampaignSettingService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.campaign.smart_campaign_setting_service import (
    SmartCampaignSettingService,
    register_smart_campaign_setting_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> SmartCampaignSettingService:
    """Create a SmartCampaignSettingService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.campaign.smart_campaign_setting_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = SmartCampaignSettingService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_get_smart_campaign_status(
    service: SmartCampaignSettingService,
    mock_ctx: Context,
) -> None:
    """Test getting smart campaign status."""
    mock_client = service.client
    mock_client.get_smart_campaign_status.return_value = Mock()  # type: ignore

    expected_result = {"smart_campaign_status": 2}

    with patch(
        "src.services.campaign.smart_campaign_setting_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.get_smart_campaign_status(
            ctx=mock_ctx,
            resource_name="customers/1234567890/smartCampaignSettings/111",
        )

    assert result == expected_result
    mock_client.get_smart_campaign_status.assert_called_once()  # type: ignore
    call_args = mock_client.get_smart_campaign_status.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.resource_name == "customers/1234567890/smartCampaignSettings/111"


@pytest.mark.asyncio
async def test_get_smart_campaign_status_error(
    service: SmartCampaignSettingService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when getting smart campaign status fails."""
    mock_client = service.client
    mock_client.get_smart_campaign_status.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.get_smart_campaign_status(
            ctx=mock_ctx,
            resource_name="customers/1234567890/smartCampaignSettings/111",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_smart_campaign_setting(
    service: SmartCampaignSettingService,
    mock_ctx: Context,
) -> None:
    """Test updating smart campaign setting."""
    mock_client = service.client
    mock_client.mutate_smart_campaign_settings.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/smartCampaignSettings/111"}]
    }

    with patch(
        "src.services.campaign.smart_campaign_setting_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.update_smart_campaign_setting(
            ctx=mock_ctx,
            customer_id="1234567890",
            setting_resource_name="customers/1234567890/smartCampaignSettings/111",
            update_fields=["advertising_language_code"],
        )

    assert result == expected_result
    mock_client.mutate_smart_campaign_settings.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_smart_campaign_settings.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1


@pytest.mark.asyncio
async def test_update_smart_campaign_setting_error(
    service: SmartCampaignSettingService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating smart campaign setting fails."""
    mock_client = service.client
    mock_client.mutate_smart_campaign_settings.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.update_smart_campaign_setting(
            ctx=mock_ctx,
            customer_id="1234567890",
            setting_resource_name="customers/1234567890/smartCampaignSettings/111",
            update_fields=["advertising_language_code"],
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_smart_campaign_setting_tools(mock_mcp)
    assert isinstance(svc, SmartCampaignSettingService)
    assert mock_mcp.tool.call_count == 2  # type: ignore
