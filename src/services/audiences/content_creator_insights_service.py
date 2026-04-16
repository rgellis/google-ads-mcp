"""Content creator insights service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.content_creator_insights_service import (
    ContentCreatorInsightsServiceClient,
)
from google.ads.googleads.v23.services.types.content_creator_insights_service import (
    GenerateCreatorInsightsRequest,
    GenerateCreatorInsightsResponse,
    GenerateTrendingInsightsRequest,
    GenerateTrendingInsightsResponse,
)
from google.ads.googleads.v23.common.types.criteria import LocationInfo

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ContentCreatorInsightsService:
    def __init__(self) -> None:
        self._client: Optional[ContentCreatorInsightsServiceClient] = None

    @property
    def client(self) -> ContentCreatorInsightsServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "ContentCreatorInsightsService"
            )
        assert self._client is not None
        return self._client

    async def generate_creator_insights(
        self, ctx: Context, customer_id: str, country_locations: List[str]
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = GenerateCreatorInsightsRequest()
            request.customer_id = customer_id
            for loc in country_locations:
                location = LocationInfo()
                location.geo_target_constant = loc
                request.country_locations.append(location)
            response: GenerateCreatorInsightsResponse = (
                self.client.generate_creator_insights(request=request)
            )
            await ctx.log(level="info", message="Generated creator insights")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate creator insights: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_trending_insights(
        self, ctx: Context, customer_id: str, country_location: str
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = GenerateTrendingInsightsRequest()
            request.customer_id = customer_id
            location = LocationInfo()
            location.geo_target_constant = country_location
            request.country_location = location
            response: GenerateTrendingInsightsResponse = (
                self.client.generate_trending_insights(request=request)
            )
            await ctx.log(level="info", message="Generated trending insights")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate trending insights: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_content_creator_insights_tools(
    service: ContentCreatorInsightsService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def generate_creator_insights(
        ctx: Context, customer_id: str, country_locations: List[str]
    ) -> Dict[str, Any]:
        """Generate YouTube creator insights.

        Args:
            customer_id: The customer ID
            country_locations: List of geo target constant resource names
        """
        return await service.generate_creator_insights(
            ctx=ctx, customer_id=customer_id, country_locations=country_locations
        )

    async def generate_trending_insights(
        ctx: Context, customer_id: str, country_location: str
    ) -> Dict[str, Any]:
        """Generate YouTube trending content insights.

        Args:
            customer_id: The customer ID
            country_location: Geo target constant resource name
        """
        return await service.generate_trending_insights(
            ctx=ctx, customer_id=customer_id, country_location=country_location
        )

    tools.extend([generate_creator_insights, generate_trending_insights])
    return tools


def register_content_creator_insights_tools(
    mcp: FastMCP[Any],
) -> ContentCreatorInsightsService:
    service = ContentCreatorInsightsService()
    tools = create_content_creator_insights_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
