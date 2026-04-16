"""Google Ads Brand Suggestion Service

This module provides functionality for getting brand suggestions in Google Ads.
Brand suggestions help advertisers find relevant brands for their campaigns.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.brand_suggestion_service import (
    BrandSuggestionServiceClient,
)
from google.ads.googleads.v23.services.types.brand_suggestion_service import (
    SuggestBrandsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class BrandSuggestionService:
    """Service for getting Google Ads brand suggestions."""

    def __init__(self) -> None:
        """Initialize the brand suggestion service."""
        self._client: Optional[BrandSuggestionServiceClient] = None

    @property
    def client(self) -> BrandSuggestionServiceClient:
        """Get the brand suggestion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BrandSuggestionService")
        assert self._client is not None
        return self._client

    async def suggest_brands(
        self,
        ctx: Context,
        customer_id: str,
        brand_prefix: str,
        selected_brands: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get brand suggestions based on a brand prefix.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            brand_prefix: The prefix of a brand name to search for
            selected_brands: Optional list of brand IDs to exclude from results

        Returns:
            Serialized response containing brand suggestions
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = SuggestBrandsRequest(
                customer_id=customer_id,
                brand_prefix=brand_prefix,
                selected_brands=selected_brands or [],
            )
            response = self.client.suggest_brands(request=request)
            await ctx.log(
                level="info",
                message=f"Found {len(response.brands)} brand suggestions",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to suggest brands: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_brand_suggestion_tools(
    service: BrandSuggestionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create brand suggestion tools for MCP."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def suggest_brands(
        ctx: Context,
        customer_id: str,
        brand_prefix: str,
        selected_brands: list[str] = [],
    ) -> Dict[str, Any]:
        """Get brand suggestions based on a brand prefix.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            brand_prefix: The prefix of a brand name to search for
            selected_brands: Optional list of brand IDs to exclude from results

        Returns:
            Serialized response containing brand suggestions
        """
        return await service.suggest_brands(
            ctx=ctx,
            customer_id=customer_id,
            brand_prefix=brand_prefix,
            selected_brands=selected_brands,
        )

    tools.append(suggest_brands)

    return tools


def register_brand_suggestion_tools(mcp: FastMCP[Any]) -> BrandSuggestionService:
    """Register brand suggestion tools with the MCP server."""
    service = BrandSuggestionService()
    tools = create_brand_suggestion_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
