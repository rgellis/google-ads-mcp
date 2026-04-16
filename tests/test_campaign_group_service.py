"""Tests for CampaignGroupService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)

from src.services.campaign.campaign_group_service import (
    CampaignGroupService,
    register_campaign_group_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> CampaignGroupService:
    """Create a CampaignGroupService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.campaign.campaign_group_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = CampaignGroupService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_campaign_group(
    service: CampaignGroupService, mock_ctx: Context
) -> None:
    """Test creating a campaign group."""
    mock_client = service.client
    mock_client.mutate_campaign_groups.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaignGroups/1"}]
    }

    with patch(
        "src.services.campaign.campaign_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.create_campaign_group(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Test Campaign Group",
        )

    assert result == expected_result
    mock_client.mutate_campaign_groups.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_campaign_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert len(request.operations) == 1
    assert request.operations[0].create.name == "Test Campaign Group"


@pytest.mark.asyncio
async def test_update_campaign_group(
    service: CampaignGroupService, mock_ctx: Context
) -> None:
    """Test updating a campaign group."""
    mock_client = service.client
    mock_client.mutate_campaign_groups.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaignGroups/1"}]
    }
    resource_name = "customers/1234567890/campaignGroups/1"

    with patch(
        "src.services.campaign.campaign_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.update_campaign_group(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_group_resource_name=resource_name,
            name="Updated Group Name",
        )

    assert result == expected_result
    mock_client.mutate_campaign_groups.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_campaign_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    operation = request.operations[0]
    assert operation.update.resource_name == resource_name
    assert operation.update.name == "Updated Group Name"
    assert "name" in operation.update_mask.paths


@pytest.mark.asyncio
async def test_remove_campaign_group(
    service: CampaignGroupService, mock_ctx: Context
) -> None:
    """Test removing a campaign group."""
    mock_client = service.client
    mock_client.mutate_campaign_groups.return_value = Mock()  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/campaignGroups/1"}]
    }
    resource_name = "customers/1234567890/campaignGroups/1"

    with patch(
        "src.services.campaign.campaign_group_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_campaign_group(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_group_resource_name=resource_name,
        )

    assert result == expected_result
    mock_client.mutate_campaign_groups.assert_called_once()  # type: ignore
    call_args = mock_client.mutate_campaign_groups.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.operations[0].remove == resource_name


@pytest.mark.asyncio
async def test_list_campaign_groups(
    service: CampaignGroupService,
    mock_sdk_client: Any,
    mock_ctx: Context,
) -> None:
    """Test listing campaign groups."""
    mock_google_ads_service = Mock(spec=GoogleAdsServiceClient)

    row = Mock()
    row.campaign_group = Mock()

    mock_google_ads_service.search.return_value = [row]  # type: ignore

    def get_service_side_effect(service_name: str) -> Any:
        if service_name == "GoogleAdsService":
            return mock_google_ads_service
        return service.client

    mock_sdk_client.client.get_service.side_effect = get_service_side_effect  # type: ignore

    serialized = {
        "resource_name": "customers/1234567890/campaignGroups/1",
        "name": "Group 1",
    }

    with patch(
        "src.services.campaign.campaign_group_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        with patch(
            "src.services.campaign.campaign_group_service.serialize_proto_message",
            return_value=serialized,
        ):
            result = await service.list_campaign_groups(
                ctx=mock_ctx,
                customer_id="1234567890",
            )

    assert len(result) == 1
    assert result[0] == serialized


@pytest.mark.asyncio
async def test_create_campaign_group_error(
    service: CampaignGroupService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in create_campaign_group."""
    mock_client = service.client
    mock_client.mutate_campaign_groups.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.create_campaign_group(
            ctx=mock_ctx,
            customer_id="1234567890",
            name="Test Group",
        )

    assert "Failed to create campaign group" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_campaign_group_error(
    service: CampaignGroupService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in update_campaign_group."""
    mock_client = service.client
    mock_client.mutate_campaign_groups.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.update_campaign_group(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_group_resource_name="customers/1234567890/campaignGroups/1",
        )

    assert "Failed to update campaign group" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_campaign_group_error(
    service: CampaignGroupService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in remove_campaign_group."""
    mock_client = service.client
    mock_client.mutate_campaign_groups.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.remove_campaign_group(
            ctx=mock_ctx,
            customer_id="1234567890",
            campaign_group_resource_name="customers/1234567890/campaignGroups/1",
        )

    assert "Failed to remove campaign group" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_campaign_group_tools(mock_mcp)
    assert isinstance(svc, CampaignGroupService)
    assert mock_mcp.tool.call_count == 4  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert set(tool_names) == {
        "create_campaign_group",
        "update_campaign_group",
        "remove_campaign_group",
        "list_campaign_groups",
    }
