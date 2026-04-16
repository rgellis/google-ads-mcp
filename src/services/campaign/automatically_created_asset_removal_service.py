"""Automatically created asset removal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.asset_field_type import AssetFieldTypeEnum
from google.ads.googleads.v23.services.services.automatically_created_asset_removal_service import (
    AutomaticallyCreatedAssetRemovalServiceClient,
)
from google.ads.googleads.v23.services.types.automatically_created_asset_removal_service import (
    RemoveCampaignAutomaticallyCreatedAssetOperation,
    RemoveCampaignAutomaticallyCreatedAssetRequest,
    RemoveCampaignAutomaticallyCreatedAssetResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AutomaticallyCreatedAssetRemovalService:
    """Service for removing automatically created assets from campaigns."""

    def __init__(self) -> None:
        self._client: Optional[AutomaticallyCreatedAssetRemovalServiceClient] = None

    @property
    def client(self) -> AutomaticallyCreatedAssetRemovalServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "AutomaticallyCreatedAssetRemovalService"
            )
        assert self._client is not None
        return self._client

    async def remove_campaign_automatically_created_assets(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Remove automatically created assets from campaigns.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of dicts with:
                - campaign: Campaign resource name
                - asset: Asset resource name
                - field_type: Asset field type (e.g. HEADLINE, DESCRIPTION)

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            removal_ops = []
            for op_data in operations:
                op = RemoveCampaignAutomaticallyCreatedAssetOperation()
                op.campaign = op_data["campaign"]
                op.asset = op_data["asset"]
                op.field_type = getattr(
                    AssetFieldTypeEnum.AssetFieldType, op_data["field_type"]
                )
                removal_ops.append(op)

            request = RemoveCampaignAutomaticallyCreatedAssetRequest()
            request.customer_id = customer_id
            request.operations = removal_ops

            response: RemoveCampaignAutomaticallyCreatedAssetResponse = (
                self.client.remove_campaign_automatically_created_asset(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed {len(removal_ops)} automatically created assets",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove automatically created assets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_automatically_created_asset_removal_tools(
    service: AutomaticallyCreatedAssetRemovalService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the automatically created asset removal service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def remove_campaign_automatically_created_assets(
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Remove automatically created assets from campaigns.

        Args:
            customer_id: The customer ID
            operations: List of dicts with campaign (resource name),
                asset (resource name), and field_type (HEADLINE, DESCRIPTION, etc.)

        Returns:
            Removal result
        """
        return await service.remove_campaign_automatically_created_assets(
            ctx=ctx, customer_id=customer_id, operations=operations
        )

    tools.append(remove_campaign_automatically_created_assets)
    return tools


def register_automatically_created_asset_removal_tools(
    mcp: FastMCP[Any],
) -> AutomaticallyCreatedAssetRemovalService:
    """Register automatically created asset removal tools with the MCP server."""
    service = AutomaticallyCreatedAssetRemovalService()
    tools = create_automatically_created_asset_removal_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
