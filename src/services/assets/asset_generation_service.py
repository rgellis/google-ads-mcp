"""Asset generation service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.asset_generation_service import (
    AssetGenerationServiceClient,
)
from google.ads.googleads.v23.services.types.asset_generation_service import (
    AssetGenerationExistingContext,
    FinalUrlImageGenerationInput,
    FreeformImageGenerationInput,
    GenerateImagesRequest,
    GenerateImagesResponse,
    GenerateTextRequest,
    GenerateTextResponse,
    ProductRecontextGenerationImageInput,
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
        asset_field_types: List[str],
        final_url: Optional[str] = None,
        freeform_prompt: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        advertising_channel_type: str = "SEARCH",
        existing_asset_group: Optional[str] = None,
        existing_ad_group_ad: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text assets using AI.

        Provide either final_url or freeform_prompt as the generation source.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_field_types: Types to generate (HEADLINE, DESCRIPTION, etc.)
            final_url: Landing page URL for context (mutually exclusive with freeform_prompt)
            freeform_prompt: Free-text prompt for generation (mutually exclusive with final_url)
            keywords: Optional keywords for context
            advertising_channel_type: Channel type (SEARCH, PERFORMANCE_MAX)
            existing_asset_group: Resource name of existing asset group for context
            existing_ad_group_ad: Resource name of existing ad group ad for context
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
            request.asset_field_types = [
                getattr(AssetFieldTypeEnum.AssetFieldType, t) for t in asset_field_types
            ]
            request.advertising_channel_type = getattr(
                AdvertisingChannelTypeEnum.AdvertisingChannelType,
                advertising_channel_type,
            )
            if final_url:
                request.final_url = final_url
            if freeform_prompt:
                request.freeform_prompt = freeform_prompt
            if keywords:
                request.keywords = keywords
            if existing_asset_group or existing_ad_group_ad:
                context = AssetGenerationExistingContext()
                if existing_asset_group:
                    context.existing_asset_group = existing_asset_group
                if existing_ad_group_ad:
                    context.existing_ad_group_ad = existing_ad_group_ad
                request.existing_generation_context = context

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
        asset_field_types: List[str],
        final_url: Optional[str] = None,
        freeform_prompt: Optional[str] = None,
        product_recontext_prompt: Optional[str] = None,
        product_recontext_source_images: Optional[List[bytes]] = None,
        advertising_channel_type: str = "PERFORMANCE_MAX",
    ) -> Dict[str, Any]:
        """Generate image assets using AI.

        Provide exactly one generation source: final_url, freeform_prompt,
        or product_recontext_prompt.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_field_types: Types to generate (MARKETING_IMAGE, etc.)
            final_url: Landing page URL to generate images from
            freeform_prompt: Free-text prompt for image generation
            product_recontext_prompt: Prompt for product recontextualization
            product_recontext_source_images: Source product images as bytes (for recontext)
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

            if final_url:
                final_url_input = FinalUrlImageGenerationInput()
                final_url_input.final_url = final_url
                request.final_url_generation = final_url_input
            elif freeform_prompt:
                freeform_input = FreeformImageGenerationInput()
                freeform_input.freeform_prompt = freeform_prompt
                request.freeform_generation = freeform_input
            elif product_recontext_prompt:
                from google.ads.googleads.v23.services.types.asset_generation_service import (
                    SourceImage,
                )

                recontext_input = ProductRecontextGenerationImageInput()
                recontext_input.prompt = product_recontext_prompt
                if product_recontext_source_images:
                    for img_data in product_recontext_source_images:
                        src_img = SourceImage()
                        src_img.image_data = img_data
                        recontext_input.source_images.append(src_img)
                request.product_recontext_generation = recontext_input

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
        asset_field_types: List[str],
        final_url: Optional[str] = None,
        freeform_prompt: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        advertising_channel_type: str = "SEARCH",
        existing_asset_group: Optional[str] = None,
        existing_ad_group_ad: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text assets (headlines, descriptions) using AI.

        Provide either final_url or freeform_prompt as the generation source.

        Args:
            customer_id: The customer ID
            asset_field_types: HEADLINE, DESCRIPTION, etc.
            final_url: Landing page URL for context
            freeform_prompt: Free-text prompt for generation
            keywords: Optional keywords for context
            advertising_channel_type: SEARCH or PERFORMANCE_MAX
            existing_asset_group: Existing asset group resource name for context
            existing_ad_group_ad: Existing ad group ad resource name for context
        """
        return await service.generate_text(
            ctx=ctx,
            customer_id=customer_id,
            asset_field_types=asset_field_types,
            final_url=final_url,
            freeform_prompt=freeform_prompt,
            keywords=keywords,
            advertising_channel_type=advertising_channel_type,
            existing_asset_group=existing_asset_group,
            existing_ad_group_ad=existing_ad_group_ad,
        )

    async def generate_image_assets(
        ctx: Context,
        customer_id: str,
        asset_field_types: List[str],
        final_url: Optional[str] = None,
        freeform_prompt: Optional[str] = None,
        product_recontext_prompt: Optional[str] = None,
        product_recontext_source_images: Optional[List[bytes]] = None,
        advertising_channel_type: str = "PERFORMANCE_MAX",
    ) -> Dict[str, Any]:
        """Generate image assets using AI.

        Provide one of: final_url, freeform_prompt, or product_recontext_prompt.

        Args:
            customer_id: The customer ID
            asset_field_types: MARKETING_IMAGE, SQUARE_MARKETING_IMAGE, etc.
            final_url: Landing page URL for image generation
            freeform_prompt: Free-text prompt for image generation
            product_recontext_prompt: Prompt for product recontextualization
            product_recontext_source_images: Source product images as bytes
            advertising_channel_type: PERFORMANCE_MAX or SEARCH
        """
        return await service.generate_images(
            ctx=ctx,
            customer_id=customer_id,
            asset_field_types=asset_field_types,
            final_url=final_url,
            freeform_prompt=freeform_prompt,
            product_recontext_prompt=product_recontext_prompt,
            product_recontext_source_images=product_recontext_source_images,
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
