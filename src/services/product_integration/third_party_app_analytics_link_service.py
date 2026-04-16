"""Third-party app analytics link service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.third_party_app_analytics_link_service import (
    ThirdPartyAppAnalyticsLinkServiceClient,
)
from google.ads.googleads.v23.services.types.third_party_app_analytics_link_service import (
    RegenerateShareableLinkIdRequest,
    RegenerateShareableLinkIdResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import get_logger, serialize_proto_message

logger = get_logger(__name__)


class ThirdPartyAppAnalyticsLinkService:
    """Service for managing third-party app analytics links."""

    def __init__(self) -> None:
        self._client: Optional[ThirdPartyAppAnalyticsLinkServiceClient] = None

    @property
    def client(self) -> ThirdPartyAppAnalyticsLinkServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "ThirdPartyAppAnalyticsLinkService"
            )
        assert self._client is not None
        return self._client

    async def regenerate_shareable_link_id(
        self,
        ctx: Context,
        resource_name: str,
    ) -> Dict[str, Any]:
        """Regenerate the shareable link ID for a third-party app analytics link.

        Args:
            ctx: FastMCP context
            resource_name: Resource name of the third-party app analytics link

        Returns:
            Regeneration result
        """
        try:
            request = RegenerateShareableLinkIdRequest()
            request.resource_name = resource_name

            response: RegenerateShareableLinkIdResponse = (
                self.client.regenerate_shareable_link_id(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Regenerated shareable link ID for {resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to regenerate shareable link ID: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_third_party_app_analytics_link_tools(
    service: ThirdPartyAppAnalyticsLinkService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the third-party app analytics link service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def regenerate_shareable_link_id(
        ctx: Context,
        resource_name: str,
    ) -> Dict[str, Any]:
        """Regenerate the shareable link ID for a third-party app analytics link.

        Args:
            resource_name: Resource name of the analytics link

        Returns:
            Regeneration result
        """
        return await service.regenerate_shareable_link_id(
            ctx=ctx, resource_name=resource_name
        )

    tools.append(regenerate_shareable_link_id)
    return tools


def register_third_party_app_analytics_link_tools(
    mcp: FastMCP[Any],
) -> ThirdPartyAppAnalyticsLinkService:
    """Register third-party app analytics link tools with the MCP server."""
    service = ThirdPartyAppAnalyticsLinkService()
    tools = create_third_party_app_analytics_link_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
