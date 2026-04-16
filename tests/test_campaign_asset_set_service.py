"""Tests for Campaign Asset Set Service."""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock

from google.ads.googleads.v23.services.services.campaign_asset_set_service import (
    CampaignAssetSetServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_asset_set_service import (
    CampaignAssetSetOperation,
    MutateCampaignAssetSetsRequest,
    MutateCampaignAssetSetsResponse,
    MutateCampaignAssetSetResult,
)
from google.ads.googleads.v23.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)

from src.services.campaign.campaign_asset_set_service import (
    CampaignAssetSetService,
    create_campaign_asset_set_tools,
    register_campaign_asset_set_tools,
)


class TestCampaignAssetSetService:
    """Test cases for CampaignAssetSetService."""

    @pytest.fixture
    def mock_client(self) -> Any:
        """Create a mock CampaignAssetSetServiceClient."""
        return Mock(spec=CampaignAssetSetServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any) -> CampaignAssetSetService:
        """Create a CampaignAssetSetService instance with mock client."""
        service = CampaignAssetSetService()
        service._client = mock_client  # type: ignore
        return service

    @pytest.fixture
    def mock_ctx(self) -> AsyncMock:
        """Create a mock FastMCP context."""
        ctx = AsyncMock()
        ctx.log = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_mutate_campaign_asset_sets_success(
        self, service: CampaignAssetSetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test successful campaign asset sets mutation."""
        customer_id = "1234567890"
        operation = CampaignAssetSetOperation()
        operation.remove = "customers/1234567890/campaignAssetSets/123~456"
        operations = [operation]
        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                )
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        response = await service.mutate_campaign_asset_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
        )

        assert isinstance(response, dict)
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore
        mock_ctx.log.assert_called()

        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateCampaignAssetSetsRequest)
        assert request.customer_id == customer_id

    @pytest.mark.asyncio
    async def test_mutate_campaign_asset_sets_with_options(
        self, service: CampaignAssetSetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test campaign asset sets mutation with all options."""
        customer_id = "1234567890"
        operation = CampaignAssetSetOperation()
        operation.remove = "customers/1234567890/campaignAssetSets/123~456"
        operations = [operation]
        expected_response = MutateCampaignAssetSetsResponse()
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        response = await service.mutate_campaign_asset_sets(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        assert isinstance(response, dict)
        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    @pytest.mark.asyncio
    async def test_mutate_campaign_asset_sets_failure(
        self, service: CampaignAssetSetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test campaign asset sets mutation failure."""
        customer_id = "1234567890"
        operations = [CampaignAssetSetOperation()]
        mock_client.mutate_campaign_asset_sets.side_effect = Exception("API Error")  # type: ignore

        with pytest.raises(Exception, match="Failed to mutate campaign asset sets"):
            await service.mutate_campaign_asset_sets(
                ctx=mock_ctx,
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_campaign_asset_set_operation(
        self, service: CampaignAssetSetService
    ) -> None:
        """Test creating campaign asset set operation."""
        campaign = "customers/1234567890/campaigns/123"
        asset_set = "customers/1234567890/assetSets/456"

        operation = service.create_campaign_asset_set_operation(
            campaign=campaign,
            asset_set=asset_set,
        )

        assert isinstance(operation, CampaignAssetSetOperation)
        assert operation.create.campaign == campaign
        assert operation.create.asset_set == asset_set

    def test_create_remove_operation(self, service: CampaignAssetSetService) -> None:
        """Test creating remove operation."""
        resource_name = "customers/1234567890/campaignAssetSets/123~456"

        operation = service.create_remove_operation(resource_name=resource_name)

        assert isinstance(operation, CampaignAssetSetOperation)
        assert operation.remove == resource_name
        assert not operation.create

    @pytest.mark.asyncio
    async def test_link_asset_set_to_campaign(
        self, service: CampaignAssetSetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test linking an asset set to a campaign."""
        customer_id = "1234567890"
        campaign = "customers/1234567890/campaigns/123"
        asset_set = "customers/1234567890/assetSets/456"

        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                )
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        response = await service.link_asset_set_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign=campaign,
            asset_set=asset_set,
        )

        assert isinstance(response, dict)
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_unlink_asset_set_from_campaign(
        self, service: CampaignAssetSetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test unlinking an asset set from a campaign."""
        customer_id = "1234567890"
        resource_name = "customers/1234567890/campaignAssetSets/123~456"

        expected_response = MutateCampaignAssetSetsResponse(
            results=[MutateCampaignAssetSetResult(resource_name=resource_name)]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        response = await service.unlink_asset_set_from_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            resource_name=resource_name,
        )

        assert isinstance(response, dict)
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_link_multiple_asset_sets_to_campaign(
        self, service: CampaignAssetSetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test linking multiple asset sets to a campaign."""
        customer_id = "1234567890"
        campaign = "customers/1234567890/campaigns/123"
        asset_sets = [
            "customers/1234567890/assetSets/456",
            "customers/1234567890/assetSets/789",
        ]

        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~456"
                ),
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~789"
                ),
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        response = await service.link_multiple_asset_sets_to_campaign(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaign=campaign,
            asset_sets=asset_sets,
        )

        assert isinstance(response, dict)
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2

    @pytest.mark.asyncio
    async def test_link_asset_set_to_multiple_campaigns(
        self, service: CampaignAssetSetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test linking an asset set to multiple campaigns."""
        customer_id = "1234567890"
        campaigns = [
            "customers/1234567890/campaigns/123",
            "customers/1234567890/campaigns/456",
        ]
        asset_set = "customers/1234567890/assetSets/789"

        expected_response = MutateCampaignAssetSetsResponse(
            results=[
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/123~789"
                ),
                MutateCampaignAssetSetResult(
                    resource_name="customers/1234567890/campaignAssetSets/456~789"
                ),
            ]
        )
        mock_client.mutate_campaign_asset_sets.return_value = expected_response  # type: ignore

        response = await service.link_asset_set_to_multiple_campaigns(
            ctx=mock_ctx,
            customer_id=customer_id,
            campaigns=campaigns,
            asset_set=asset_set,
        )

        assert isinstance(response, dict)
        mock_client.mutate_campaign_asset_sets.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_campaign_asset_sets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2

    def test_register_tools(self) -> None:
        """Test registering tools."""
        mock_mcp = Mock()
        service = register_campaign_asset_set_tools(mock_mcp)
        assert isinstance(service, CampaignAssetSetService)
        assert mock_mcp.tool.call_count > 0
