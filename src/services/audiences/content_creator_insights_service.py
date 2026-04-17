"""Content creator insights service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.audience_insights_attribute import (
    AudienceInsightsAttribute,
)
from google.ads.googleads.v23.common.types.criteria import LocationInfo
from google.ads.googleads.v23.services.services.content_creator_insights_service import (
    ContentCreatorInsightsServiceClient,
)
from google.ads.googleads.v23.services.types.content_creator_insights_service import (
    GenerateCreatorInsightsRequest,
    GenerateCreatorInsightsResponse,
    GenerateTrendingInsightsRequest,
    GenerateTrendingInsightsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


def _make_attr_youtube_channel(channel_id: str) -> AudienceInsightsAttribute:
    """Wrap a YouTube channel ID into an AudienceInsightsAttribute."""
    from google.ads.googleads.v23.common.types.criteria import YouTubeChannelInfo

    attr = AudienceInsightsAttribute()
    channel_info = YouTubeChannelInfo()
    channel_info.channel_id = channel_id
    attr.youtube_channel = channel_info
    return attr


def _make_attr_knowledge_graph(entity_id: str) -> AudienceInsightsAttribute:
    """Wrap a knowledge graph machine ID into an AudienceInsightsAttribute."""
    from google.ads.googleads.v23.common.types.audience_insights_attribute import (
        AudienceInsightsEntity,
    )

    attr = AudienceInsightsAttribute()
    entity = AudienceInsightsEntity()
    entity.knowledge_graph_machine_id = entity_id
    attr.entity = entity
    return attr


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
        self,
        ctx: Context,
        customer_id: str,
        country_locations: List[str],
        sub_country_locations: Optional[List[str]] = None,
        search_channel_ids: Optional[List[str]] = None,
        search_brand_names: Optional[List[str]] = None,
        search_audience_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate YouTube creator insights.

        Provide exactly one search mode: search_channel_ids, search_brand_names,
        or search_audience_interests. These are mutually exclusive.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            country_locations: Geo target constant resource names (e.g. geoTargetConstants/2840)
            sub_country_locations: Sub-country geo target constants for finer targeting
            search_channel_ids: YouTube channel IDs to search for specific creators
            search_brand_names: Knowledge graph entity IDs to search by brand (e.g. /m/0d8h3k)
            search_audience_interests: Knowledge graph entity IDs for audience interest targeting
            customer_insights_group: User-defined grouping label
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = GenerateCreatorInsightsRequest()
            request.customer_id = customer_id

            for loc in country_locations:
                location = LocationInfo()
                location.geo_target_constant = loc
                request.country_locations.append(location)

            if sub_country_locations:
                for loc in sub_country_locations:
                    location = LocationInfo()
                    location.geo_target_constant = loc
                    request.sub_country_locations.append(location)

            if search_channel_ids:
                from google.ads.googleads.v23.common.types.criteria import (
                    YouTubeChannelInfo,
                )

                for channel_id in search_channel_ids:
                    yci = YouTubeChannelInfo()
                    yci.channel_id = channel_id
                    request.search_channels.youtube_channels.append(yci)

            if search_brand_names:
                for brand in search_brand_names:
                    request.search_brand.brand_entities.append(
                        _make_attr_knowledge_graph(brand)
                    )

            if search_audience_interests:
                for interest in search_audience_interests:
                    request.search_attributes.audience_attributes.append(
                        _make_attr_knowledge_graph(interest)
                    )

            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

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
        self,
        ctx: Context,
        customer_id: str,
        country_location: str,
        search_topic_names: Optional[List[str]] = None,
        search_audience_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate YouTube trending content insights.

        Provide one search mode: search_topic_names or search_audience_interests.
        These are mutually exclusive.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            country_location: Geo target constant resource name
            search_topic_names: Knowledge graph entity IDs to filter by topic (e.g. /m/027x7n)
            search_audience_interests: Knowledge graph entity IDs for audience targeting
            customer_insights_group: User-defined grouping label
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = GenerateTrendingInsightsRequest()
            request.customer_id = customer_id

            location = LocationInfo()
            location.geo_target_constant = country_location
            request.country_location = location

            if search_topic_names:
                from google.ads.googleads.v23.common.types.audience_insights_attribute import (
                    AudienceInsightsEntity,
                )

                for topic in search_topic_names:
                    entity = AudienceInsightsEntity()
                    entity.knowledge_graph_machine_id = topic
                    request.search_topics.entities.append(entity)

            if search_audience_interests:
                for interest in search_audience_interests:
                    request.search_audience.audience_attributes.append(
                        _make_attr_knowledge_graph(interest)
                    )

            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

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
        ctx: Context,
        customer_id: str,
        country_locations: List[str],
        sub_country_locations: Optional[List[str]] = None,
        search_channel_ids: Optional[List[str]] = None,
        search_brand_names: Optional[List[str]] = None,
        search_audience_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate YouTube creator insights to find relevant content creators for advertising.

        Search by channel, brand, or audience interest. These three search modes are
        mutually exclusive — provide only ONE of: search_channel_ids, search_brand_names,
        or search_audience_interests.

        Args:
            customer_id: The customer ID
            country_locations: Country geo target constants (e.g. geoTargetConstants/2840 for US)
            sub_country_locations: Sub-country geo targets for finer geographic targeting
            search_channel_ids: YouTube channel resource names to analyze specific creators (mode 1)
            search_brand_names: Brand names (knowledge graph entities) to find related creators (mode 2)
            search_audience_interests: Audience interest topics to find creators whose audience matches (mode 3)
            customer_insights_group: Grouping label for organizing requests

        Returns:
            Creator insights including audience demographics, channel metrics, and content topics
        """
        return await service.generate_creator_insights(
            ctx=ctx,
            customer_id=customer_id,
            country_locations=country_locations,
            sub_country_locations=sub_country_locations,
            search_channel_ids=search_channel_ids,
            search_brand_names=search_brand_names,
            search_audience_interests=search_audience_interests,
            customer_insights_group=customer_insights_group,
        )

    async def generate_trending_insights(
        ctx: Context,
        customer_id: str,
        country_location: str,
        search_topic_names: Optional[List[str]] = None,
        search_audience_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate YouTube trending content insights to discover what's popular.

        Search by topic or audience interest. These two search modes are mutually exclusive —
        provide only ONE of: search_topic_names or search_audience_interests.

        Args:
            customer_id: The customer ID
            country_location: Country geo target constant (e.g. geoTargetConstants/2840 for US)
            search_topic_names: Topic names (knowledge graph entities) to filter trends (mode 1)
            search_audience_interests: Audience interests to filter which trends matter (mode 2)
            customer_insights_group: Grouping label for organizing requests

        Returns:
            Trending content insights including topics, creators, and engagement metrics
        """
        return await service.generate_trending_insights(
            ctx=ctx,
            customer_id=customer_id,
            country_location=country_location,
            search_topic_names=search_topic_names,
            search_audience_interests=search_audience_interests,
            customer_insights_group=customer_insights_group,
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
