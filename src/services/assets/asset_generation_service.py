"""Asset generation service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.asset_generation_service import (
    AssetGenerationServiceClient,
)
from google.ads.googleads.v23.services.types.asset_generation_service import (
    GenerateImagesRequest,
    GenerateImagesResponse,
    GenerateTextRequest,
    GenerateTextResponse,
    FinalUrlImageGenerationInput,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AssetGenerationService:
    """Service for AI-generated text and image assets."""

    def __init__(self) -> None:
        self._client: Optional[AssetGenerationServiceClient] = None

    @property
    def client(self) -> AssetGenerationServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetGenerationService")
        assert self._client is not None
        return self._client

    async def generate_text(
        self,
        ctx: Context,
        customer_id: str,
        final_url: str,
        asset_field_types: List[str],
        keywords: Optional[List[str]] = None,
        advertising_channel_type: str = "SEARCH",
    ) -> Dict[str, Any]:
        """Generate text assets using AI.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            final_url: Landing page URL for context
            asset_field_types: Types to generate (HEADLINE, DESCRIPTION, etc.)
            keywords: Optional keywords for context
            advertising_channel_type: Channel type (SEARCH, PERFORMANCE_MAX)
        """
        try:
            customer_id = format_customer_id(customer_id)
            from google.ads.googleads.v23.enums.types.asset_field_type import (
                AssetFieldTypeEnum,
            )
            from google.ads.googleads.v23.enums.types.advertising_channel_type import (
                AdvertisingChannelTypeEnum,
            )

            request = GenerateTextRequest()
            request.customer_id = customer_id
            request.final_url = final_url
            request.asset_field_types = [
                getattr(AssetFieldTypeEnum.AssetFieldType, t) for t in asset_field_types
            ]
            request.advertising_channel_type = getattr(
                AdvertisingChannelTypeEnum.AdvertisingChannelType,
                advertising_channel_type,
            )
            if keywords:
                request.keywords = keywords

            response: GenerateTextResponse = self.client.generate_text(request=request)
            await ctx.log(
                level="info", message=f"Generated text assets for {final_url}"
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate text: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_images(
        self,
        ctx: Context,
        customer_id: str,
        final_url: str,
        asset_field_types: List[str],
        advertising_channel_type: str = "PERFORMANCE_MAX",
    ) -> Dict[str, Any]:
        """Generate image assets using AI from a final URL.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            final_url: Landing page URL to generate images from
            asset_field_types: Types to generate (MARKETING_IMAGE, etc.)
            advertising_channel_type: Channel type
        """
        try:
            customer_id = format_customer_id(customer_id)
            from google.ads.googleads.v23.enums.types.asset_field_type import (
                AssetFieldTypeEnum,
            )
            from google.ads.googleads.v23.enums.types.advertising_channel_type import (
                AdvertisingChannelTypeEnum,
            )

            request = GenerateImagesRequest()
            request.customer_id = customer_id
            request.asset_field_types = [
                getattr(AssetFieldTypeEnum.AssetFieldType, t) for t in asset_field_types
            ]
            request.advertising_channel_type = getattr(
                AdvertisingChannelTypeEnum.AdvertisingChannelType,
                advertising_channel_type,
            )
            final_url_input = FinalUrlImageGenerationInput()
            final_url_input.final_url = final_url
            request.final_url_generation = final_url_input

            response: GenerateImagesResponse = self.client.generate_images(
                request=request
            )
            await ctx.log(
                level="info", message=f"Generated image assets for {final_url}"
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate images: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_asset_generation_tools(
    service: AssetGenerationService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def generate_text_assets(
        ctx: Context,
        customer_id: str,
        final_url: str,
        asset_field_types: List[str],
        keywords: Optional[List[str]] = None,
        advertising_channel_type: str = "SEARCH",
    ) -> Dict[str, Any]:
        """Generate text assets (headlines, descriptions) using AI.

        Args:
            customer_id: The customer ID
            final_url: Landing page URL for context
            asset_field_types: HEADLINE, DESCRIPTION, etc.
            keywords: Optional keywords for context
            advertising_channel_type: SEARCH or PERFORMANCE_MAX
        """
        return await service.generate_text(
            ctx=ctx,
            customer_id=customer_id,
            final_url=final_url,
            asset_field_types=asset_field_types,
            keywords=keywords,
            advertising_channel_type=advertising_channel_type,
        )

    async def generate_image_assets(
        ctx: Context,
        customer_id: str,
        final_url: str,
        asset_field_types: List[str],
        advertising_channel_type: str = "PERFORMANCE_MAX",
    ) -> Dict[str, Any]:
        """Generate image assets using AI from a landing page.

        Args:
            customer_id: The customer ID
            final_url: Landing page URL
            asset_field_types: MARKETING_IMAGE, SQUARE_MARKETING_IMAGE, etc.
            advertising_channel_type: PERFORMANCE_MAX or SEARCH
        """
        return await service.generate_images(
            ctx=ctx,
            customer_id=customer_id,
            final_url=final_url,
            asset_field_types=asset_field_types,
            advertising_channel_type=advertising_channel_type,
        )

    tools.extend([generate_text_assets, generate_image_assets])
    return tools


def register_asset_generation_tools(mcp: FastMCP[Any]) -> AssetGenerationService:
    service = AssetGenerationService()
    tools = create_asset_generation_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
