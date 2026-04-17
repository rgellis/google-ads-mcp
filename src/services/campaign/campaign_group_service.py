"""Campaign group service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.campaign_group import CampaignGroup
from google.ads.googleads.v23.services.services.campaign_group_service import (
    CampaignGroupServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_group_service import (
    CampaignGroupOperation,
    MutateCampaignGroupsRequest,
    MutateCampaignGroupsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class CampaignGroupService:
    """Service for managing campaign groups."""

    def __init__(self) -> None:
        self._client: Optional[CampaignGroupServiceClient] = None

    @property
    def client(self) -> CampaignGroupServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignGroupService")
        assert self._client is not None
        return self._client

    async def create_campaign_group(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a campaign group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Campaign group name

        Returns:
            Created campaign group details
        """
        try:
            customer_id = format_customer_id(customer_id)

            campaign_group = CampaignGroup()
            campaign_group.name = name

            operation = CampaignGroupOperation()
            operation.create = campaign_group

            request = MutateCampaignGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignGroupsResponse = self.client.mutate_campaign_groups(
                request=request
            )

            await ctx.log(level="info", message=f"Created campaign group '{name}'")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create campaign group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_campaign_group(
        self,
        ctx: Context,
        customer_id: str,
        campaign_group_resource_name: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update a campaign group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_group_resource_name: Resource name of the campaign group
            name: New name (optional)

        Returns:
            Updated campaign group details
        """
        try:
            customer_id = format_customer_id(customer_id)

            campaign_group = CampaignGroup()
            campaign_group.resource_name = campaign_group_resource_name

            update_mask_fields = []
            if name is not None:
                campaign_group.name = name
                update_mask_fields.append("name")

            operation = CampaignGroupOperation()
            operation.update = campaign_group
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            request = MutateCampaignGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignGroupsResponse = self.client.mutate_campaign_groups(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Updated campaign group {campaign_group_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_campaign_group(
        self,
        ctx: Context,
        customer_id: str,
        campaign_group_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a campaign group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_group_resource_name: Resource name of the campaign group

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = CampaignGroupOperation()
            operation.remove = campaign_group_resource_name

            request = MutateCampaignGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignGroupsResponse = self.client.mutate_campaign_groups(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Removed campaign group: {campaign_group_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove campaign group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_campaign_groups(
        self,
        ctx: Context,
        customer_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List campaign groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            limit: Maximum number of results

        Returns:
            List of campaign groups
        """
        try:
            customer_id = format_customer_id(customer_id)

            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            query = f"""
                SELECT
                    campaign_group.resource_name,
                    campaign_group.id,
                    campaign_group.name,
                    campaign_group.status
                FROM campaign_group
                LIMIT {limit}
            """

            response = google_ads_service.search(customer_id=customer_id, query=query)

            results = []
            for row in response:
                results.append(serialize_proto_message(row.campaign_group))

            await ctx.log(level="info", message=f"Found {len(results)} campaign groups")

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list campaign groups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_group_tools(
    service: CampaignGroupService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign group service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def create_campaign_group(
        ctx: Context,
        customer_id: str,
        name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a campaign group for organizing campaigns.

        Args:
            customer_id: The customer ID
            name: Campaign group name

        Returns:
            Created campaign group details
        """
        return await service.create_campaign_group(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_campaign_group(
        ctx: Context,
        customer_id: str,
        campaign_group_resource_name: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a campaign group.

        Args:
            customer_id: The customer ID
            campaign_group_resource_name: Resource name of the campaign group
            name: New name

        Returns:
            Updated campaign group details
        """
        return await service.update_campaign_group(
            ctx=ctx,
            customer_id=customer_id,
            campaign_group_resource_name=campaign_group_resource_name,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_campaign_group(
        ctx: Context,
        customer_id: str,
        campaign_group_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a campaign group.

        Args:
            customer_id: The customer ID
            campaign_group_resource_name: Resource name of the campaign group

        Returns:
            Removal result
        """
        return await service.remove_campaign_group(
            ctx=ctx,
            customer_id=customer_id,
            campaign_group_resource_name=campaign_group_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def list_campaign_groups(
        ctx: Context, customer_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List campaign groups.

        Args:
            customer_id: The customer ID
            limit: Maximum number of results

        Returns:
            List of campaign groups
        """
        return await service.list_campaign_groups(
            ctx=ctx, customer_id=customer_id, limit=limit
        )

    tools.extend(
        [
            create_campaign_group,
            update_campaign_group,
            remove_campaign_group,
            list_campaign_groups,
        ]
    )
    return tools


def register_campaign_group_tools(mcp: FastMCP[Any]) -> CampaignGroupService:
    """Register campaign group tools with the MCP server."""
    service = CampaignGroupService()
    tools = create_campaign_group_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
