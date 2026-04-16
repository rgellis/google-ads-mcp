"""Campaign Asset Set Service for Google Ads API v23.

This service manages asset set associations with campaigns, allowing asset sets
to be linked to campaigns for use in advertising.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.campaign_asset_set_service import (
    CampaignAssetSetServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_asset_set_service import (
    CampaignAssetSetOperation,
    MutateCampaignAssetSetsRequest,
)
from google.ads.googleads.v23.resources.types.campaign_asset_set import CampaignAssetSet

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CampaignAssetSetService:
    """Service for managing campaign asset sets in Google Ads.

    Campaign asset sets link asset sets to campaigns, enabling the use of
    asset sets in campaign advertising.
    """

    def __init__(self) -> None:
        """Initialize the campaign asset set service."""
        self._client: Optional[CampaignAssetSetServiceClient] = None

    @property
    def client(self) -> CampaignAssetSetServiceClient:
        """Get the campaign asset set service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignAssetSetService")
        assert self._client is not None
        return self._client

    async def mutate_campaign_asset_sets(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[CampaignAssetSetOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create or remove campaign asset sets.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            Serialized response dictionary.
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateCampaignAssetSetsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
            )
            if response_content_type is not None:
                request.response_content_type = response_content_type
            response = self.client.mutate_campaign_asset_sets(request=request)
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(operations)} campaign asset set(s) for customer {customer_id}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate campaign asset sets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def create_campaign_asset_set_operation(
        self,
        campaign: str,
        asset_set: str,
    ) -> CampaignAssetSetOperation:
        """Create a campaign asset set operation for creation.

        Args:
            campaign: The campaign resource name.
            asset_set: The asset set resource name.

        Returns:
            CampaignAssetSetOperation: The operation to create the campaign asset set.
        """
        campaign_asset_set = CampaignAssetSet(
            campaign=campaign,
            asset_set=asset_set,
        )

        return CampaignAssetSetOperation(create=campaign_asset_set)

    def create_remove_operation(self, resource_name: str) -> CampaignAssetSetOperation:
        """Create a campaign asset set operation for removal.

        Args:
            resource_name: The resource name of the campaign asset set to remove.
                Format: customers/{customer_id}/campaignAssetSets/{campaign_id}~{asset_set_id}

        Returns:
            CampaignAssetSetOperation: The operation to remove the campaign asset set.
        """
        return CampaignAssetSetOperation(remove=resource_name)

    async def link_asset_set_to_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign: str,
        asset_set: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Link an asset set to a campaign.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            campaign: The campaign resource name.
            asset_set: The asset set resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operation = self.create_campaign_asset_set_operation(
            campaign=campaign,
            asset_set=asset_set,
        )

        return await self.mutate_campaign_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    async def unlink_asset_set_from_campaign(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Unlink an asset set from a campaign.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            resource_name: The resource name of the campaign asset set to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return await self.mutate_campaign_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    async def link_multiple_asset_sets_to_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign: str,
        asset_sets: List[str],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Link multiple asset sets to a campaign.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            campaign: The campaign resource name.
            asset_sets: List of asset set resource names.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operations = []
        for asset_set in asset_sets:
            operation = self.create_campaign_asset_set_operation(
                campaign=campaign,
                asset_set=asset_set,
            )
            operations.append(operation)

        return await self.mutate_campaign_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )

    async def link_asset_set_to_multiple_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        campaigns: List[str],
        asset_set: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Link an asset set to multiple campaigns.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            campaigns: List of campaign resource names.
            asset_set: The asset set resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operations = []
        for campaign in campaigns:
            operation = self.create_campaign_asset_set_operation(
                campaign=campaign,
                asset_set=asset_set,
            )
            operations.append(operation)

        return await self.mutate_campaign_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )


def create_campaign_asset_set_tools(
    service: CampaignAssetSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign asset set service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_campaign_asset_sets(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or remove campaign asset set associations.

        Args:
            customer_id: The customer ID
            operations: List of campaign asset set operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Response with results and any partial failure errors
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_campaign_asset_set_operation(
                    campaign=op_data["campaign"],
                    asset_set=op_data["asset_set"],
                )
            elif op_type == "remove":
                operation = service.create_remove_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        rct = None
        if response_content_type is not None:
            from google.ads.googleads.v23.enums.types.response_content_type import (
                ResponseContentTypeEnum,
            )

            rct = getattr(
                ResponseContentTypeEnum.ResponseContentType, response_content_type
            )

        return await service.mutate_campaign_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=rct,
        )

    async def link_asset_set_to_campaign(
        ctx: Context,
        customer_id: str,
        campaign: str,
        asset_set: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Link an asset set to a campaign.

        Args:
            customer_id: The customer ID
            campaign: The campaign resource name
            asset_set: The asset set resource name
            validate_only: Only validate the request

        Returns:
            Created campaign asset set details
        """
        return await service.link_asset_set_to_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign=campaign,
            asset_set=asset_set,
            validate_only=validate_only,
        )

    async def unlink_asset_set_from_campaign(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Unlink an asset set from a campaign.

        Args:
            customer_id: The customer ID
            resource_name: The campaign asset set resource name to remove
            validate_only: Only validate the request

        Returns:
            Removal result details
        """
        return await service.unlink_asset_set_from_campaign(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            validate_only=validate_only,
        )

    async def link_multiple_asset_sets_to_campaign(
        ctx: Context,
        customer_id: str,
        campaign: str,
        asset_sets: list[str],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Link multiple asset sets to a campaign.

        Args:
            customer_id: The customer ID
            campaign: The campaign resource name
            asset_sets: List of asset set resource names
            validate_only: Only validate the request

        Returns:
            Results with linked asset sets
        """
        return await service.link_multiple_asset_sets_to_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign=campaign,
            asset_sets=asset_sets,
            validate_only=validate_only,
        )

    async def link_asset_set_to_multiple_campaigns(
        ctx: Context,
        customer_id: str,
        campaigns: list[str],
        asset_set: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Link an asset set to multiple campaigns.

        Args:
            customer_id: The customer ID
            campaigns: List of campaign resource names
            asset_set: The asset set resource name
            validate_only: Only validate the request

        Returns:
            Results with linked campaigns
        """
        return await service.link_asset_set_to_multiple_campaigns(
            ctx=ctx,
            customer_id=customer_id,
            campaigns=campaigns,
            asset_set=asset_set,
            validate_only=validate_only,
        )

    tools.extend(
        [
            mutate_campaign_asset_sets,
            link_asset_set_to_campaign,
            unlink_asset_set_from_campaign,
            link_multiple_asset_sets_to_campaign,
            link_asset_set_to_multiple_campaigns,
        ]
    )
    return tools


def register_campaign_asset_set_tools(mcp: FastMCP[Any]) -> CampaignAssetSetService:
    """Register campaign asset set tools with the MCP server."""
    service = CampaignAssetSetService()
    tools = create_campaign_asset_set_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
