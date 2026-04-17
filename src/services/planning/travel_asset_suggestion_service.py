"""Travel asset suggestion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.travel_asset_suggestion_service import (
    TravelAssetSuggestionServiceClient,
)
from google.ads.googleads.v23.services.types.travel_asset_suggestion_service import (
    SuggestTravelAssetsRequest,
    SuggestTravelAssetsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class TravelAssetSuggestionService:
    def __init__(self) -> None:
        self._client: Optional[TravelAssetSuggestionServiceClient] = None

    @property
    def client(self) -> TravelAssetSuggestionServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("TravelAssetSuggestionService")
        assert self._client is not None
        return self._client

    async def suggest_travel_assets(
        self,
        ctx: Context,
        customer_id: str,
        place_ids: List[str],
        language_option: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = SuggestTravelAssetsRequest()
            request.customer_id = customer_id
            request.place_ids = place_ids
            if language_option:
                request.language_option = language_option
            response: SuggestTravelAssetsResponse = self.client.suggest_travel_assets(
                request=request
            )
            await ctx.log(
                level="info",
                message=f"Got travel asset suggestions for {len(place_ids)} places",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to suggest travel assets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_travel_asset_suggestion_tools(
    service: TravelAssetSuggestionService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def suggest_travel_assets(
        ctx: Context,
        customer_id: str,
        place_ids: List[str],
        language_option: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest text and image assets for travel campaigns based on Google Places.

        Generates headlines, descriptions, and images using business information from Google Maps.

        Args:
            customer_id: The customer ID
            place_ids: List of Google Place IDs (from Google Maps/Places API)
            language_option: Optional language code (e.g. "en") for generated content

        Returns:
            Suggested assets including headlines, descriptions, and image URLs for each place
        """
        return await service.suggest_travel_assets(
            ctx=ctx,
            customer_id=customer_id,
            place_ids=place_ids,
            language_option=language_option,
        )

    tools.append(suggest_travel_assets)
    return tools


def register_travel_asset_suggestion_tools(
    mcp: FastMCP[Any],
) -> TravelAssetSuggestionService:
    service = TravelAssetSuggestionService()
    tools = create_travel_asset_suggestion_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
