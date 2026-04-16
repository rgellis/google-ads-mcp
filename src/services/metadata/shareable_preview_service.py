"""Shareable preview service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.shareable_preview_service import (
    ShareablePreviewServiceClient,
)
from google.ads.googleads.v23.services.types.shareable_preview_service import (
    GenerateShareablePreviewsRequest,
    GenerateShareablePreviewsResponse,
    ShareablePreview,
    AssetGroupIdentifier,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ShareablePreviewService:
    """Service for generating shareable ad preview URLs."""

    def __init__(self) -> None:
        self._client: Optional[ShareablePreviewServiceClient] = None

    @property
    def client(self) -> ShareablePreviewServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ShareablePreviewService")
        assert self._client is not None
        return self._client

    async def generate_shareable_previews(
        self,
        ctx: Context,
        customer_id: str,
        asset_group_ids: List[int],
    ) -> Dict[str, Any]:
        """Generate shareable preview URLs for asset groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_group_ids: List of asset group IDs to generate previews for

        Returns:
            Shareable preview URLs and expiration details
        """
        try:
            customer_id = format_customer_id(customer_id)

            previews = []
            for ag_id in asset_group_ids:
                preview = ShareablePreview()
                identifier = AssetGroupIdentifier()
                identifier.asset_group_id = ag_id
                preview.asset_group_identifier = identifier
                previews.append(preview)

            request = GenerateShareablePreviewsRequest()
            request.customer_id = customer_id
            request.shareable_previews = previews

            response: GenerateShareablePreviewsResponse = (
                self.client.generate_shareable_previews(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Generated {len(asset_group_ids)} shareable previews",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate shareable previews: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_shareable_preview_tools(
    service: ShareablePreviewService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the shareable preview service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def generate_shareable_previews(
        ctx: Context,
        customer_id: str,
        asset_group_ids: List[int],
    ) -> Dict[str, Any]:
        """Generate shareable ad preview URLs for asset groups.

        Args:
            customer_id: The customer ID
            asset_group_ids: List of asset group IDs

        Returns:
            Shareable preview URLs with expiration times
        """
        return await service.generate_shareable_previews(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_ids=asset_group_ids,
        )

    tools.append(generate_shareable_previews)
    return tools


def register_shareable_preview_tools(
    mcp: FastMCP[Any],
) -> ShareablePreviewService:
    """Register shareable preview tools with the MCP server."""
    service = ShareablePreviewService()
    tools = create_shareable_preview_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
