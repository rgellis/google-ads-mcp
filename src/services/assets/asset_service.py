"""Asset service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.asset_types import (
    AppDeepLinkAsset,
    BookOnGoogleAsset,
    BusinessMessageAsset,
    BusinessMessageCallToActionInfo,
    CallAsset,
    CalloutAsset,
    CallToActionAsset,
    DemandGenCarouselCardAsset,
    DynamicCustomAsset,
    DynamicEducationAsset,
    DynamicFlightsAsset,
    DynamicHotelsAndRentalsAsset,
    DynamicJobsAsset,
    DynamicLocalAsset,
    DynamicRealEstateAsset,
    DynamicTravelAsset,
    HotelCalloutAsset,
    HotelPropertyAsset,
    ImageAsset,
    LeadFormAsset,
    LeadFormField,
    LocationAsset,
    MediaBundleAsset,
    MobileAppAsset,
    PageFeedAsset,
    PriceAsset,
    PriceOffering,
    PromotionAsset,
    SitelinkAsset,
    StructuredSnippetAsset,
    TextAsset,
    YoutubeVideoAsset,
)
from google.ads.googleads.v23.common.types.feed_common import Money
from google.ads.googleads.v23.enums.types.asset_type import AssetTypeEnum
from google.ads.googleads.v23.enums.types.business_message_call_to_action_type import (
    BusinessMessageCallToActionTypeEnum,
)
from google.ads.googleads.v23.enums.types.business_message_provider import (
    BusinessMessageProviderEnum,
)
from google.ads.googleads.v23.enums.types.call_to_action_type import (
    CallToActionTypeEnum,
)
from google.ads.googleads.v23.enums.types.lead_form_field_user_input_type import (
    LeadFormFieldUserInputTypeEnum,
)
from google.ads.googleads.v23.enums.types.mobile_app_vendor import MobileAppVendorEnum
from google.ads.googleads.v23.enums.types.price_extension_price_qualifier import (
    PriceExtensionPriceQualifierEnum,
)
from google.ads.googleads.v23.enums.types.price_extension_price_unit import (
    PriceExtensionPriceUnitEnum,
)
from google.ads.googleads.v23.enums.types.price_extension_type import (
    PriceExtensionTypeEnum,
)
from google.ads.googleads.v23.resources.types.asset import Asset
from google.ads.googleads.v23.services.services.asset_service import (
    AssetServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.asset_service import (
    AssetOperation,
    MutateAssetsRequest,
    MutateAssetsResponse,
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


class AssetService:
    """Asset service for managing Google Ads assets (images, videos, text)."""

    def __init__(self) -> None:
        """Initialize the asset service."""
        self._client: Optional[AssetServiceClient] = None

    @property
    def client(self) -> AssetServiceClient:
        """Get the asset service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetService")
        assert self._client is not None
        return self._client

    async def create_text_asset(
        self,
        ctx: Context,
        customer_id: str,
        text: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a text asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            text: The text content
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create asset
            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.TEXT

            # Set name if provided
            if name:
                asset.name = name
            else:
                asset.name = f"Text: {text[:50]}"  # Use first 50 chars as name

            # Create text asset
            text_asset = TextAsset()
            text_asset.text = text
            asset.text_asset = text_asset

            # Create operation
            operation = AssetOperation()
            operation.create = asset

            # Create request
            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAssetsResponse = self.client.mutate_assets(request=request)

            await ctx.log(level="info", message=f"Created text asset '{name}'")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create text asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_image_asset(
        self,
        ctx: Context,
        customer_id: str,
        image_data: bytes,
        name: str,
        mime_type: str = "image/jpeg",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create an image asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            image_data: The image data as bytes
            name: Name for the asset
            mime_type: MIME type (image/jpeg, image/png, etc.)

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create asset
            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.IMAGE
            asset.name = name

            # Create image asset
            image_asset = ImageAsset()
            image_asset.data = image_data
            image_asset.mime_type = self.get_mime_type_enum(mime_type)
            asset.image_asset = image_asset

            # Create operation
            operation = AssetOperation()
            operation.create = asset

            # Create request
            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAssetsResponse = self.client.mutate_assets(request=request)

            await ctx.log(level="info", message=f"Created image asset '{name}'")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create image asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_youtube_video_asset(
        self,
        ctx: Context,
        customer_id: str,
        youtube_video_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a YouTube video asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            youtube_video_id: The YouTube video ID
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create asset
            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.YOUTUBE_VIDEO

            # Set name
            if name:
                asset.name = name
            else:
                asset.name = f"YouTube: {youtube_video_id}"

            # Create YouTube video asset
            youtube_video = YoutubeVideoAsset()
            youtube_video.youtube_video_id = youtube_video_id
            asset.youtube_video_asset = youtube_video

            # Create operation
            operation = AssetOperation()
            operation.create = asset

            # Create request
            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAssetsResponse = self.client.mutate_assets(request=request)

            await ctx.log(
                level="info", message=f"Created YouTube video asset '{asset.name}'"
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create YouTube video asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def search_assets(
        self,
        ctx: Context,
        customer_id: str,
        asset_types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for assets in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_types: Optional list of asset types to filter by
            limit: Maximum number of results

        Returns:
            List of asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    asset.id,
                    asset.name,
                    asset.type,
                    asset.resource_name,
                    asset.text_asset.text,
                    asset.image_asset.file_size,
                    asset.youtube_video_asset.youtube_video_id
                FROM asset
            """

            if asset_types:
                type_conditions = [f"asset.type = '{t}'" for t in asset_types]
                query += " WHERE " + " OR ".join(type_conditions)

            query += f" ORDER BY asset.id DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            assets = []
            for row in response:
                asset = row.asset
                asset_dict = {
                    "asset_id": str(asset.id),
                    "name": asset.name,
                    "type": asset.type_.name,
                    "resource_name": asset.resource_name,
                }

                # Add type-specific fields
                if asset.type_ == AssetTypeEnum.AssetType.TEXT:
                    asset_dict["text"] = asset.text_asset.text
                elif asset.type_ == AssetTypeEnum.AssetType.IMAGE:
                    asset_dict["file_size"] = str(asset.image_asset.file_size)
                elif asset.type_ == AssetTypeEnum.AssetType.YOUTUBE_VIDEO:
                    asset_dict["youtube_video_id"] = (
                        asset.youtube_video_asset.youtube_video_id
                    )

                assets.append(asset_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(assets)} assets",
            )

            return assets

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to search assets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_asset(
        self,
        ctx: Context,
        customer_id: str,
        asset_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update an existing asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_id: The asset ID to update
            name: New name for the asset

        Returns:
            Updated asset details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/assets/{asset_id}"

            # Create asset with fields to update
            asset = Asset()
            asset.resource_name = resource_name

            update_mask_fields: List[str] = []

            if name is not None:
                asset.name = name
                update_mask_fields.append("name")

            if not update_mask_fields:
                raise ValueError("At least one field must be provided for update")

            # Create operation
            operation = AssetOperation()
            operation.update = asset
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAssetsResponse = self.client.mutate_assets(request=request)

            await ctx.log(level="info", message=f"Updated asset {asset_id}")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_sitelink_asset(
        self,
        ctx: Context,
        customer_id: str,
        link_text: str,
        final_url: str,
        description1: Optional[str] = None,
        description2: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a sitelink asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            link_text: The text for the sitelink
            final_url: The final URL for the sitelink
            description1: Optional first description line
            description2: Optional second description line
            start_date: Optional start date (yyyy-MM-dd)
            end_date: Optional end date (yyyy-MM-dd)
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.SITELINK
            asset.name = name if name else f"Sitelink: {link_text[:50]}"
            asset.final_urls.append(final_url)

            sitelink_asset = SitelinkAsset()
            sitelink_asset.link_text = link_text
            if description1:
                sitelink_asset.description1 = description1
            if description2:
                sitelink_asset.description2 = description2
            if start_date:
                sitelink_asset.start_date = start_date
            if end_date:
                sitelink_asset.end_date = end_date
            asset.sitelink_asset = sitelink_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message=f"Created sitelink asset '{link_text}'")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create sitelink asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_callout_asset(
        self,
        ctx: Context,
        customer_id: str,
        callout_text: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a callout asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            callout_text: The callout text
            start_date: Optional start date (yyyy-MM-dd)
            end_date: Optional end date (yyyy-MM-dd)
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.CALLOUT
            asset.name = name if name else f"Callout: {callout_text[:50]}"

            callout_asset = CalloutAsset()
            callout_asset.callout_text = callout_text
            if start_date:
                callout_asset.start_date = start_date
            if end_date:
                callout_asset.end_date = end_date
            asset.callout_asset = callout_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info", message=f"Created callout asset '{callout_text}'"
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create callout asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_structured_snippet_asset(
        self,
        ctx: Context,
        customer_id: str,
        header: str,
        values: List[str],
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a structured snippet asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            header: The header for the snippet (e.g., "Brands", "Types")
            values: List of values for the snippet
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.STRUCTURED_SNIPPET
            asset.name = name if name else f"Snippet: {header}"

            snippet_asset = StructuredSnippetAsset()
            snippet_asset.header = header
            for value in values:
                snippet_asset.values.append(value)
            asset.structured_snippet_asset = snippet_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created structured snippet asset '{header}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create structured snippet asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_call_asset(
        self,
        ctx: Context,
        customer_id: str,
        country_code: str,
        phone_number: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a call asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            country_code: The country code (e.g., "US")
            phone_number: The phone number
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.CALL
            asset.name = name if name else f"Call: {country_code} {phone_number}"

            call_asset = CallAsset()
            call_asset.country_code = country_code
            call_asset.phone_number = phone_number
            asset.call_asset = call_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message=f"Created call asset '{phone_number}'")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create call asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_price_asset(
        self,
        ctx: Context,
        customer_id: str,
        type_: str,
        language_code: str,
        price_offerings: List[Dict[str, Any]],
        price_qualifier: str = "NONE",
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a price asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            type_: Price extension type (e.g., "BRANDS", "EVENTS", "SERVICES")
            language_code: Language code (e.g., "en")
            price_offerings: List of price offerings, each with keys:
                header (str), description (str), final_url (str),
                price (dict with currency_code and amount_micros),
                unit (str, e.g., "PER_HOUR", "PER_MONTH")
            price_qualifier: Price qualifier (e.g., "NONE", "FROM", "UP_TO")
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.PRICE
            asset.name = name if name else f"Price: {type_}"

            price_asset = PriceAsset()
            price_asset.type_ = PriceExtensionTypeEnum.PriceExtensionType[type_]
            price_asset.price_qualifier = (
                PriceExtensionPriceQualifierEnum.PriceExtensionPriceQualifier[
                    price_qualifier
                ]
            )
            price_asset.language_code = language_code

            for offering_data in price_offerings:
                offering = PriceOffering()
                offering.header = offering_data["header"]
                offering.description = offering_data["description"]
                offering.final_url = offering_data["final_url"]
                if "unit" in offering_data:
                    offering.unit = PriceExtensionPriceUnitEnum.PriceExtensionPriceUnit[
                        offering_data["unit"]
                    ]
                if "price" in offering_data:
                    price_info = offering_data["price"]
                    money = Money()
                    money.currency_code = price_info["currency_code"]
                    money.amount_micros = price_info["amount_micros"]
                    offering.price = money
                price_asset.price_offerings.append(offering)

            asset.price_asset = price_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message=f"Created price asset '{type_}'")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create price asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_promotion_asset(
        self,
        ctx: Context,
        customer_id: str,
        promotion_target: str,
        language_code: str,
        percent_off: Optional[int] = None,
        money_amount_off_micros: Optional[int] = None,
        money_amount_off_currency: Optional[str] = None,
        promotion_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a promotion asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            promotion_target: The promotion target text
            language_code: Language code (e.g., "en")
            percent_off: Optional percentage off (e.g., 20 for 20%)
            money_amount_off_micros: Optional money amount off in micros
            money_amount_off_currency: Optional currency code for money amount off
            promotion_code: Optional promotion code
            start_date: Optional start date (yyyy-MM-dd)
            end_date: Optional end date (yyyy-MM-dd)
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.PROMOTION
            asset.name = name if name else f"Promotion: {promotion_target[:50]}"

            promotion_asset = PromotionAsset()
            promotion_asset.promotion_target = promotion_target
            promotion_asset.language_code = language_code
            if percent_off is not None:
                promotion_asset.percent_off = percent_off
            if money_amount_off_micros is not None and money_amount_off_currency:
                money = Money()
                money.currency_code = money_amount_off_currency
                money.amount_micros = money_amount_off_micros
                promotion_asset.money_amount_off = money
            if promotion_code:
                promotion_asset.promotion_code = promotion_code
            if start_date:
                promotion_asset.start_date = start_date
            if end_date:
                promotion_asset.end_date = end_date
            asset.promotion_asset = promotion_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created promotion asset '{promotion_target}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create promotion asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_lead_form_asset(
        self,
        ctx: Context,
        customer_id: str,
        business_name: str,
        headline: str,
        description: str,
        privacy_policy_url: str,
        call_to_action_type: str,
        fields: List[Dict[str, str]],
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a lead form asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            business_name: The business name
            headline: The headline text
            description: The description text
            privacy_policy_url: URL to the privacy policy
            call_to_action_type: Call to action type (e.g., "SIGN_UP", "LEARN_MORE")
            fields: List of form fields, each with key "input_type"
                (e.g., "FULL_NAME", "EMAIL", "PHONE_NUMBER")
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.LEAD_FORM
            asset.name = name if name else f"Lead Form: {business_name[:50]}"

            lead_form_asset = LeadFormAsset()
            lead_form_asset.business_name = business_name
            lead_form_asset.headline = headline
            lead_form_asset.description = description
            lead_form_asset.privacy_policy_url = privacy_policy_url
            lead_form_asset.call_to_action_type = CallToActionTypeEnum.CallToActionType[
                call_to_action_type
            ]

            for field_data in fields:
                lead_form_field = LeadFormField()
                lead_form_field.input_type = (
                    LeadFormFieldUserInputTypeEnum.LeadFormFieldUserInputType[
                        field_data["input_type"]
                    ]
                )
                lead_form_asset.fields.append(lead_form_field)

            asset.lead_form_asset = lead_form_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created lead form asset '{business_name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create lead form asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_page_feed_asset(
        self,
        ctx: Context,
        customer_id: str,
        page_url: str,
        labels: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a page feed asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            page_url: The page URL
            labels: Optional list of labels
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.PAGE_FEED
            asset.name = name if name else f"Page Feed: {page_url[:50]}"

            page_feed_asset = PageFeedAsset()
            page_feed_asset.page_url = page_url
            if labels:
                for label in labels:
                    page_feed_asset.labels.append(label)
            asset.page_feed_asset = page_feed_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message=f"Created page feed asset '{page_url}'")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create page feed asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_mobile_app_asset(
        self,
        ctx: Context,
        customer_id: str,
        app_id: str,
        app_store: str,
        link_text: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a mobile app asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            app_id: The app ID
            app_store: The app store (APPLE_ITUNES or GOOGLE_PLAY)
            link_text: The link text
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.MOBILE_APP
            asset.name = name if name else f"Mobile App: {link_text[:50]}"

            mobile_app_asset = MobileAppAsset()
            mobile_app_asset.app_id = app_id
            mobile_app_asset.app_store = MobileAppVendorEnum.MobileAppVendor[app_store]
            mobile_app_asset.link_text = link_text
            asset.mobile_app_asset = mobile_app_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info", message=f"Created mobile app asset '{link_text}'"
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create mobile app asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_hotel_callout_asset(
        self,
        ctx: Context,
        customer_id: str,
        text: str,
        language_code: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a hotel callout asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            text: The callout text
            language_code: Language code (e.g., "en")
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.HOTEL_CALLOUT
            asset.name = name if name else f"Hotel Callout: {text[:50]}"

            hotel_callout_asset = HotelCalloutAsset()
            hotel_callout_asset.text = text
            hotel_callout_asset.language_code = language_code
            asset.hotel_callout_asset = hotel_callout_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message=f"Created hotel callout asset '{text}'")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create hotel callout asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_call_to_action_asset(
        self,
        ctx: Context,
        customer_id: str,
        call_to_action: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a call-to-action asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            call_to_action: Call to action type (e.g., LEARN_MORE, SIGN_UP, SHOP_NOW, BOOK_NOW, GET_QUOTE, APPLY_NOW, CONTACT_US, SUBSCRIBE, DOWNLOAD, ORDER_NOW, VISIT_SITE)
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.CALL_TO_ACTION
            asset.name = name if name else f"CTA: {call_to_action}"

            cta_asset = CallToActionAsset()
            cta_asset.call_to_action = CallToActionTypeEnum.CallToActionType[
                call_to_action
            ]
            asset.call_to_action_asset = cta_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created call-to-action asset '{call_to_action}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create call-to-action asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_location_asset(
        self,
        ctx: Context,
        customer_id: str,
        place_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a location asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            place_id: The Google Place ID
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.LOCATION
            asset.name = name if name else f"Location: {place_id}"

            location_asset = LocationAsset()
            location_asset.place_id = place_id
            asset.location_asset = location_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message=f"Created location asset '{place_id}'")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create location asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_hotel_property_asset(
        self,
        ctx: Context,
        customer_id: str,
        place_id: str,
        hotel_name: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a hotel property asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            place_id: The Google Place ID for the hotel
            hotel_name: Optional hotel name
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.HOTEL_PROPERTY
            asset.name = name if name else f"Hotel: {hotel_name or place_id}"

            hotel_property_asset = HotelPropertyAsset()
            hotel_property_asset.place_id = place_id
            if hotel_name:
                hotel_property_asset.hotel_name = hotel_name
            asset.hotel_property_asset = hotel_property_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created hotel property asset '{hotel_name or place_id}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create hotel property asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_app_deep_link_asset(
        self,
        ctx: Context,
        customer_id: str,
        app_deep_link_uri: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create an app deep link asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            app_deep_link_uri: The deep link URI for the app
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.APP_DEEP_LINK
            asset.name = name if name else f"App Deep Link: {app_deep_link_uri[:50]}"

            app_deep_link_asset = AppDeepLinkAsset()
            app_deep_link_asset.app_deep_link_uri = app_deep_link_uri
            asset.app_deep_link_asset = app_deep_link_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created app deep link asset '{app_deep_link_uri}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create app deep link asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_book_on_google_asset(
        self,
        ctx: Context,
        customer_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Book on Google asset (no additional fields required).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.BOOK_ON_GOOGLE
            asset.name = name if name else "Book on Google"

            book_on_google_asset = BookOnGoogleAsset()
            asset.book_on_google_asset = book_on_google_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message="Created Book on Google asset")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Book on Google asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_media_bundle_asset(
        self,
        ctx: Context,
        customer_id: str,
        data: bytes,
        name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a media bundle asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            data: The media bundle data as bytes (ZIP file)
            name: Name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.MEDIA_BUNDLE
            asset.name = name

            media_bundle_asset = MediaBundleAsset()
            media_bundle_asset.data = data
            asset.media_bundle_asset = media_bundle_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(level="info", message=f"Created media bundle asset '{name}'")
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create media bundle asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_demand_gen_carousel_card_asset(
        self,
        ctx: Context,
        customer_id: str,
        marketing_image_asset: str,
        headline: str,
        call_to_action_text: str,
        square_marketing_image_asset: Optional[str] = None,
        portrait_marketing_image_asset: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen carousel card asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            marketing_image_asset: Resource name of the marketing image asset
            headline: The headline text
            call_to_action_text: The call-to-action text
            square_marketing_image_asset: Optional resource name of the square marketing image asset
            portrait_marketing_image_asset: Optional resource name of the portrait marketing image asset
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DEMAND_GEN_CAROUSEL_CARD
            asset.name = name if name else f"Carousel: {headline[:50]}"

            carousel_asset = DemandGenCarouselCardAsset()
            carousel_asset.marketing_image_asset = marketing_image_asset
            carousel_asset.headline = headline
            carousel_asset.call_to_action_text = call_to_action_text
            if square_marketing_image_asset:
                carousel_asset.square_marketing_image_asset = (
                    square_marketing_image_asset
                )
            if portrait_marketing_image_asset:
                carousel_asset.portrait_marketing_image_asset = (
                    portrait_marketing_image_asset
                )
            asset.demand_gen_carousel_card_asset = carousel_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created Demand Gen carousel card asset '{headline}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Demand Gen carousel card asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_business_message_asset(
        self,
        ctx: Context,
        customer_id: str,
        message_provider: str,
        starter_message: str,
        call_to_action_selection: str,
        call_to_action_description: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a business message asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            message_provider: The message provider (WHATSAPP, FACEBOOK_MESSENGER, ZALO)
            starter_message: The starter message text
            call_to_action_selection: Call to action type (APPLY_NOW, BOOK_NOW, CONTACT_US, GET_INFO, GET_OFFER, GET_QUOTE, GET_STARTED, LEARN_MORE)
            call_to_action_description: Optional call-to-action description text
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.BUSINESS_MESSAGE
            asset.name = name if name else f"Business Message: {message_provider}"

            biz_msg_asset = BusinessMessageAsset()
            biz_msg_asset.message_provider = (
                BusinessMessageProviderEnum.BusinessMessageProvider[message_provider]
            )
            biz_msg_asset.starter_message = starter_message

            cta_info = BusinessMessageCallToActionInfo()
            cta_info.call_to_action_selection = (
                BusinessMessageCallToActionTypeEnum.BusinessMessageCallToActionType[
                    call_to_action_selection
                ]
            )
            if call_to_action_description:
                cta_info.call_to_action_description = call_to_action_description
            biz_msg_asset.call_to_action = cta_info

            asset.business_message_asset = biz_msg_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created business message asset '{message_provider}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create business message asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_education_asset(
        self,
        ctx: Context,
        customer_id: str,
        program_id: str,
        program_name: str,
        school_name: str,
        location_id: Optional[str] = None,
        subject: Optional[str] = None,
        program_description: Optional[str] = None,
        address: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        android_app_link: Optional[str] = None,
        similar_program_ids: Optional[List[str]] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        thumbnail_image_url: Optional[str] = None,
        image_url: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic education asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            program_id: The program ID
            program_name: The program name
            school_name: The school name
            location_id: Optional location ID
            subject: Optional subject
            program_description: Optional program description
            address: Optional address
            contextual_keywords: Optional list of contextual keywords
            android_app_link: Optional Android app deep link
            similar_program_ids: Optional list of similar program IDs
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            thumbnail_image_url: Optional thumbnail image URL
            image_url: Optional image URL
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_EDUCATION
            asset.name = name if name else f"Dynamic Education: {program_name[:50]}"

            dynamic_asset = DynamicEducationAsset()
            dynamic_asset.program_id = program_id
            dynamic_asset.program_name = program_name
            dynamic_asset.school_name = school_name
            if location_id:
                dynamic_asset.location_id = location_id
            if subject:
                dynamic_asset.subject = subject
            if program_description:
                dynamic_asset.program_description = program_description
            if address:
                dynamic_asset.address = address
            if contextual_keywords:
                for kw in contextual_keywords:
                    dynamic_asset.contextual_keywords.append(kw)
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if similar_program_ids:
                for pid in similar_program_ids:
                    dynamic_asset.similar_program_ids.append(pid)
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            if thumbnail_image_url:
                dynamic_asset.thumbnail_image_url = thumbnail_image_url
            if image_url:
                dynamic_asset.image_url = image_url
            asset.dynamic_education_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic education asset '{program_name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic education asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_real_estate_asset(
        self,
        ctx: Context,
        customer_id: str,
        listing_id: str,
        listing_name: str,
        city_name: Optional[str] = None,
        description: Optional[str] = None,
        address: Optional[str] = None,
        price: Optional[str] = None,
        image_url: Optional[str] = None,
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        formatted_price: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        similar_listing_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic real estate asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            listing_id: The listing ID
            listing_name: The listing name
            city_name: Optional city name
            description: Optional description
            address: Optional address
            price: Optional price
            image_url: Optional image URL
            property_type: Optional property type
            listing_type: Optional listing type
            contextual_keywords: Optional list of contextual keywords
            formatted_price: Optional formatted price string
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            similar_listing_ids: Optional list of similar listing IDs
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_REAL_ESTATE
            asset.name = name if name else f"Dynamic Real Estate: {listing_name[:50]}"

            dynamic_asset = DynamicRealEstateAsset()
            dynamic_asset.listing_id = listing_id
            dynamic_asset.listing_name = listing_name
            if city_name:
                dynamic_asset.city_name = city_name
            if description:
                dynamic_asset.description = description
            if address:
                dynamic_asset.address = address
            if price:
                dynamic_asset.price = price
            if image_url:
                dynamic_asset.image_url = image_url
            if property_type:
                dynamic_asset.property_type = property_type
            if listing_type:
                dynamic_asset.listing_type = listing_type
            if contextual_keywords:
                for kw in contextual_keywords:
                    dynamic_asset.contextual_keywords.append(kw)
            if formatted_price:
                dynamic_asset.formatted_price = formatted_price
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            if similar_listing_ids:
                for lid in similar_listing_ids:
                    dynamic_asset.similar_listing_ids.append(lid)
            asset.dynamic_real_estate_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic real estate asset '{listing_name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic real estate asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_custom_asset(
        self,
        ctx: Context,
        customer_id: str,
        id: str,
        item_title: str,
        id2: Optional[str] = None,
        item_subtitle: Optional[str] = None,
        item_description: Optional[str] = None,
        item_address: Optional[str] = None,
        item_category: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        image_url: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        similar_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic custom asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            id: The item ID
            item_title: The item title
            id2: Optional secondary ID
            item_subtitle: Optional item subtitle
            item_description: Optional item description
            item_address: Optional item address
            item_category: Optional item category
            price: Optional price
            sale_price: Optional sale price
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            image_url: Optional image URL
            contextual_keywords: Optional list of contextual keywords
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            similar_ids: Optional list of similar IDs
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_CUSTOM
            asset.name = name if name else f"Dynamic Custom: {item_title[:50]}"

            dynamic_asset = DynamicCustomAsset()
            dynamic_asset.id = id
            dynamic_asset.item_title = item_title
            if id2:
                dynamic_asset.id2 = id2
            if item_subtitle:
                dynamic_asset.item_subtitle = item_subtitle
            if item_description:
                dynamic_asset.item_description = item_description
            if item_address:
                dynamic_asset.item_address = item_address
            if item_category:
                dynamic_asset.item_category = item_category
            if price:
                dynamic_asset.price = price
            if sale_price:
                dynamic_asset.sale_price = sale_price
            if formatted_price:
                dynamic_asset.formatted_price = formatted_price
            if formatted_sale_price:
                dynamic_asset.formatted_sale_price = formatted_sale_price
            if image_url:
                dynamic_asset.image_url = image_url
            if contextual_keywords:
                for kw in contextual_keywords:
                    dynamic_asset.contextual_keywords.append(kw)
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            if similar_ids:
                for sid in similar_ids:
                    dynamic_asset.similar_ids.append(sid)
            asset.dynamic_custom_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic custom asset '{item_title}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic custom asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_hotels_and_rentals_asset(
        self,
        ctx: Context,
        customer_id: str,
        property_id: str,
        property_name: str,
        image_url: Optional[str] = None,
        destination_name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        star_rating: Optional[int] = None,
        category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        address: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        similar_property_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic hotels and rentals asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            property_id: The property ID
            property_name: The property name
            image_url: Optional image URL
            destination_name: Optional destination name
            description: Optional description
            price: Optional price
            sale_price: Optional sale price
            star_rating: Optional star rating (1-5)
            category: Optional category
            contextual_keywords: Optional list of contextual keywords
            address: Optional address
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            similar_property_ids: Optional list of similar property IDs
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_HOTELS_AND_RENTALS
            asset.name = name if name else f"Dynamic Hotels: {property_name[:50]}"

            dynamic_asset = DynamicHotelsAndRentalsAsset()
            dynamic_asset.property_id = property_id
            dynamic_asset.property_name = property_name
            if image_url:
                dynamic_asset.image_url = image_url
            if destination_name:
                dynamic_asset.destination_name = destination_name
            if description:
                dynamic_asset.description = description
            if price:
                dynamic_asset.price = price
            if sale_price:
                dynamic_asset.sale_price = sale_price
            if star_rating is not None:
                dynamic_asset.star_rating = star_rating
            if category:
                dynamic_asset.category = category
            if contextual_keywords:
                for kw in contextual_keywords:
                    dynamic_asset.contextual_keywords.append(kw)
            if address:
                dynamic_asset.address = address
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            if formatted_price:
                dynamic_asset.formatted_price = formatted_price
            if formatted_sale_price:
                dynamic_asset.formatted_sale_price = formatted_sale_price
            if similar_property_ids:
                for pid in similar_property_ids:
                    dynamic_asset.similar_property_ids.append(pid)
            asset.dynamic_hotels_and_rentals_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic hotels and rentals asset '{property_name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic hotels and rentals asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_flights_asset(
        self,
        ctx: Context,
        customer_id: str,
        destination_id: str,
        destination_name: str,
        origin_id: Optional[str] = None,
        origin_name: Optional[str] = None,
        flight_description: Optional[str] = None,
        image_url: Optional[str] = None,
        flight_price: Optional[str] = None,
        flight_sale_price: Optional[str] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        similar_destination_ids: Optional[List[str]] = None,
        custom_mapping: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic flights asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            destination_id: The destination ID
            destination_name: The destination name
            origin_id: Optional origin ID
            origin_name: Optional origin name
            flight_description: Optional flight description
            image_url: Optional image URL
            flight_price: Optional flight price
            flight_sale_price: Optional flight sale price
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            similar_destination_ids: Optional list of similar destination IDs
            custom_mapping: Optional custom mapping string
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_FLIGHTS
            asset.name = name if name else f"Dynamic Flights: {destination_name[:50]}"

            dynamic_asset = DynamicFlightsAsset()
            dynamic_asset.destination_id = destination_id
            dynamic_asset.destination_name = destination_name
            if origin_id:
                dynamic_asset.origin_id = origin_id
            if origin_name:
                dynamic_asset.origin_name = origin_name
            if flight_description:
                dynamic_asset.flight_description = flight_description
            if image_url:
                dynamic_asset.image_url = image_url
            if flight_price:
                dynamic_asset.flight_price = flight_price
            if flight_sale_price:
                dynamic_asset.flight_sale_price = flight_sale_price
            if formatted_price:
                dynamic_asset.formatted_price = formatted_price
            if formatted_sale_price:
                dynamic_asset.formatted_sale_price = formatted_sale_price
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            if similar_destination_ids:
                for did in similar_destination_ids:
                    dynamic_asset.similar_destination_ids.append(did)
            if custom_mapping:
                dynamic_asset.custom_mapping = custom_mapping
            asset.dynamic_flights_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic flights asset '{destination_name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic flights asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_travel_asset(
        self,
        ctx: Context,
        customer_id: str,
        destination_id: str,
        title: str,
        destination_name: str,
        origin_id: Optional[str] = None,
        destination_address: Optional[str] = None,
        origin_name: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        similar_destination_ids: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic travel asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            destination_id: The destination ID
            title: The title
            destination_name: The destination name
            origin_id: Optional origin ID
            destination_address: Optional destination address
            origin_name: Optional origin name
            price: Optional price
            sale_price: Optional sale price
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            category: Optional category
            contextual_keywords: Optional list of contextual keywords
            similar_destination_ids: Optional list of similar destination IDs
            image_url: Optional image URL
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_TRAVEL
            asset.name = name if name else f"Dynamic Travel: {title[:50]}"

            dynamic_asset = DynamicTravelAsset()
            dynamic_asset.destination_id = destination_id
            dynamic_asset.title = title
            dynamic_asset.destination_name = destination_name
            if origin_id:
                dynamic_asset.origin_id = origin_id
            if destination_address:
                dynamic_asset.destination_address = destination_address
            if origin_name:
                dynamic_asset.origin_name = origin_name
            if price:
                dynamic_asset.price = price
            if sale_price:
                dynamic_asset.sale_price = sale_price
            if formatted_price:
                dynamic_asset.formatted_price = formatted_price
            if formatted_sale_price:
                dynamic_asset.formatted_sale_price = formatted_sale_price
            if category:
                dynamic_asset.category = category
            if contextual_keywords:
                for kw in contextual_keywords:
                    dynamic_asset.contextual_keywords.append(kw)
            if similar_destination_ids:
                for did in similar_destination_ids:
                    dynamic_asset.similar_destination_ids.append(did)
            if image_url:
                dynamic_asset.image_url = image_url
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            asset.dynamic_travel_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic travel asset '{title}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic travel asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_local_asset(
        self,
        ctx: Context,
        customer_id: str,
        deal_id: str,
        deal_name: str,
        subtitle: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        image_url: Optional[str] = None,
        address: Optional[str] = None,
        category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        android_app_link: Optional[str] = None,
        similar_deal_ids: Optional[List[str]] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic local asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            deal_id: The deal ID
            deal_name: The deal name
            subtitle: Optional subtitle
            description: Optional description
            price: Optional price
            sale_price: Optional sale price
            image_url: Optional image URL
            address: Optional address
            category: Optional category
            contextual_keywords: Optional list of contextual keywords
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            android_app_link: Optional Android app deep link
            similar_deal_ids: Optional list of similar deal IDs
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_LOCAL
            asset.name = name if name else f"Dynamic Local: {deal_name[:50]}"

            dynamic_asset = DynamicLocalAsset()
            dynamic_asset.deal_id = deal_id
            dynamic_asset.deal_name = deal_name
            if subtitle:
                dynamic_asset.subtitle = subtitle
            if description:
                dynamic_asset.description = description
            if price:
                dynamic_asset.price = price
            if sale_price:
                dynamic_asset.sale_price = sale_price
            if image_url:
                dynamic_asset.image_url = image_url
            if address:
                dynamic_asset.address = address
            if category:
                dynamic_asset.category = category
            if contextual_keywords:
                for kw in contextual_keywords:
                    dynamic_asset.contextual_keywords.append(kw)
            if formatted_price:
                dynamic_asset.formatted_price = formatted_price
            if formatted_sale_price:
                dynamic_asset.formatted_sale_price = formatted_sale_price
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if similar_deal_ids:
                for did in similar_deal_ids:
                    dynamic_asset.similar_deal_ids.append(did)
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            asset.dynamic_local_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic local asset '{deal_name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic local asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_dynamic_jobs_asset(
        self,
        ctx: Context,
        customer_id: str,
        job_id: str,
        job_title: str,
        location_id: Optional[str] = None,
        job_subtitle: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        job_category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        address: Optional[str] = None,
        salary: Optional[str] = None,
        android_app_link: Optional[str] = None,
        similar_job_ids: Optional[List[str]] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a dynamic jobs asset.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            job_id: The job ID
            job_title: The job title
            location_id: Optional location ID
            job_subtitle: Optional job subtitle
            description: Optional description
            image_url: Optional image URL
            job_category: Optional job category
            contextual_keywords: Optional list of contextual keywords
            address: Optional address
            salary: Optional salary
            android_app_link: Optional Android app deep link
            similar_job_ids: Optional list of similar job IDs
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            name: Optional name for the asset

        Returns:
            Created asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset = Asset()
            asset.type_ = AssetTypeEnum.AssetType.DYNAMIC_JOBS
            asset.name = name if name else f"Dynamic Jobs: {job_title[:50]}"

            dynamic_asset = DynamicJobsAsset()
            dynamic_asset.job_id = job_id
            dynamic_asset.job_title = job_title
            if location_id:
                dynamic_asset.location_id = location_id
            if job_subtitle:
                dynamic_asset.job_subtitle = job_subtitle
            if description:
                dynamic_asset.description = description
            if image_url:
                dynamic_asset.image_url = image_url
            if job_category:
                dynamic_asset.job_category = job_category
            if contextual_keywords:
                for kw in contextual_keywords:
                    dynamic_asset.contextual_keywords.append(kw)
            if address:
                dynamic_asset.address = address
            if salary:
                dynamic_asset.salary = salary
            if android_app_link:
                dynamic_asset.android_app_link = android_app_link
            if similar_job_ids:
                for jid in similar_job_ids:
                    dynamic_asset.similar_job_ids.append(jid)
            if ios_app_link:
                dynamic_asset.ios_app_link = ios_app_link
            if ios_app_store_id is not None:
                dynamic_asset.ios_app_store_id = ios_app_store_id
            asset.dynamic_jobs_asset = dynamic_asset

            operation = AssetOperation()
            operation.create = asset

            request = MutateAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetsResponse = self.client.mutate_assets(request=request)
            await ctx.log(
                level="info",
                message=f"Created dynamic jobs asset '{job_title}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create dynamic jobs asset: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def get_mime_type_enum(self, mime_type: str):
        """Convert MIME type string to enum value."""
        from google.ads.googleads.v23.enums.types.mime_type import MimeTypeEnum

        mime_type_map = {
            "image/jpeg": MimeTypeEnum.MimeType.IMAGE_JPEG,
            "image/png": MimeTypeEnum.MimeType.IMAGE_PNG,
            "image/gif": MimeTypeEnum.MimeType.IMAGE_GIF,
        }

        return mime_type_map.get(
            mime_type.lower(),
            MimeTypeEnum.MimeType.IMAGE_JPEG,  # Default
        )


def create_asset_tools(service: AssetService) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the asset service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_text_asset(
        ctx: Context,
        customer_id: str,
        text: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a text asset.

        Args:
            customer_id: The customer ID
            text: The text content
            name: Optional name for the asset

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_text_asset(
            ctx=ctx,
            customer_id=customer_id,
            text=text,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_image_asset(
        ctx: Context,
        customer_id: str,
        image_data: bytes,
        name: str,
        mime_type: str = "image/jpeg",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an image asset.

        Args:
            customer_id: The customer ID
            image_data: The image data as bytes
            name: Name for the asset
            mime_type: MIME type (image/jpeg, image/png, image/gif)

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_image_asset(
            ctx=ctx,
            customer_id=customer_id,
            image_data=image_data,
            name=name,
            mime_type=mime_type,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_youtube_video_asset(
        ctx: Context,
        customer_id: str,
        youtube_video_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a YouTube video asset.

        Args:
            customer_id: The customer ID
            youtube_video_id: The YouTube video ID (e.g., "dQw4w9WgXcQ")
            name: Optional name for the asset

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_youtube_video_asset(
            ctx=ctx,
            customer_id=customer_id,
            youtube_video_id=youtube_video_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def search_assets(
        ctx: Context,
        customer_id: str,
        asset_types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for assets in the account.

        Args:
            customer_id: The customer ID
            asset_types: Optional list of asset types to filter by (TEXT, IMAGE, YOUTUBE_VIDEO)
            limit: Maximum number of results

        Returns:
            List of asset details
        """
        return await service.search_assets(
            ctx=ctx,
            customer_id=customer_id,
            asset_types=asset_types,
            limit=limit,
        )

    async def update_asset(
        ctx: Context,
        customer_id: str,
        asset_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing asset using partial update with field mask.

        Updatable fields:
            - name (str): The name of the asset

        Args:
            customer_id: The customer ID
            asset_id: The asset ID to update
            name: New name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Updated asset details including resource_name
        """
        return await service.update_asset(
            ctx=ctx,
            customer_id=customer_id,
            asset_id=asset_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_sitelink_asset(
        ctx: Context,
        customer_id: str,
        link_text: str,
        final_url: str,
        description1: Optional[str] = None,
        description2: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a sitelink asset.

        Args:
            customer_id: The customer ID
            link_text: The text for the sitelink
            final_url: The final URL for the sitelink
            description1: Optional first description line
            description2: Optional second description line
            start_date: Optional start date (yyyy-MM-dd)
            end_date: Optional end date (yyyy-MM-dd)
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_sitelink_asset(
            ctx=ctx,
            customer_id=customer_id,
            link_text=link_text,
            final_url=final_url,
            description1=description1,
            description2=description2,
            start_date=start_date,
            end_date=end_date,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_callout_asset(
        ctx: Context,
        customer_id: str,
        callout_text: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a callout asset.

        Args:
            customer_id: The customer ID
            callout_text: The callout text
            start_date: Optional start date (yyyy-MM-dd)
            end_date: Optional end date (yyyy-MM-dd)
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_callout_asset(
            ctx=ctx,
            customer_id=customer_id,
            callout_text=callout_text,
            start_date=start_date,
            end_date=end_date,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_structured_snippet_asset(
        ctx: Context,
        customer_id: str,
        header: str,
        values: List[str],
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a structured snippet asset.

        Args:
            customer_id: The customer ID
            header: The header for the snippet (e.g., "Brands", "Types")
            values: List of values for the snippet
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_structured_snippet_asset(
            ctx=ctx,
            customer_id=customer_id,
            header=header,
            values=values,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_call_asset(
        ctx: Context,
        customer_id: str,
        country_code: str,
        phone_number: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a call asset.

        Args:
            customer_id: The customer ID
            country_code: The country code (e.g., "US")
            phone_number: The phone number
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_call_asset(
            ctx=ctx,
            customer_id=customer_id,
            country_code=country_code,
            phone_number=phone_number,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_price_asset(
        ctx: Context,
        customer_id: str,
        type_: str,
        language_code: str,
        price_offerings: List[Dict[str, Any]],
        price_qualifier: str = "NONE",
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a price asset.

        Args:
            customer_id: The customer ID
            type_: Price extension type (e.g., "BRANDS", "EVENTS", "SERVICES")
            language_code: Language code (e.g., "en")
            price_offerings: List of price offerings, each a dict with keys:
                header (str), description (str), final_url (str),
                price (dict with currency_code and amount_micros),
                unit (str, e.g., "PER_HOUR", "PER_MONTH")
            price_qualifier: Price qualifier ("NONE", "FROM", "UP_TO")
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_price_asset(
            ctx=ctx,
            customer_id=customer_id,
            type_=type_,
            language_code=language_code,
            price_offerings=price_offerings,
            price_qualifier=price_qualifier,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_promotion_asset(
        ctx: Context,
        customer_id: str,
        promotion_target: str,
        language_code: str,
        percent_off: Optional[int] = None,
        money_amount_off_micros: Optional[int] = None,
        money_amount_off_currency: Optional[str] = None,
        promotion_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a promotion asset.

        Args:
            customer_id: The customer ID
            promotion_target: The promotion target text
            language_code: Language code (e.g., "en")
            percent_off: Optional percentage off (e.g., 20 for 20%)
            money_amount_off_micros: Optional money amount off in micros
            money_amount_off_currency: Optional currency code for money amount off
            promotion_code: Optional promotion code
            start_date: Optional start date (yyyy-MM-dd)
            end_date: Optional end date (yyyy-MM-dd)
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_promotion_asset(
            ctx=ctx,
            customer_id=customer_id,
            promotion_target=promotion_target,
            language_code=language_code,
            percent_off=percent_off,
            money_amount_off_micros=money_amount_off_micros,
            money_amount_off_currency=money_amount_off_currency,
            promotion_code=promotion_code,
            start_date=start_date,
            end_date=end_date,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_lead_form_asset(
        ctx: Context,
        customer_id: str,
        business_name: str,
        headline: str,
        description: str,
        privacy_policy_url: str,
        call_to_action_type: str,
        fields: List[Dict[str, str]],
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a lead form asset.

        Args:
            customer_id: The customer ID
            business_name: The business name
            headline: The headline text
            description: The description text
            privacy_policy_url: URL to the privacy policy
            call_to_action_type: Call to action type (e.g., "SIGN_UP", "LEARN_MORE")
            fields: List of form fields, each a dict with key "input_type"
                (e.g., "FULL_NAME", "EMAIL", "PHONE_NUMBER")
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_lead_form_asset(
            ctx=ctx,
            customer_id=customer_id,
            business_name=business_name,
            headline=headline,
            description=description,
            privacy_policy_url=privacy_policy_url,
            call_to_action_type=call_to_action_type,
            fields=fields,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_page_feed_asset(
        ctx: Context,
        customer_id: str,
        page_url: str,
        labels: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a page feed asset.

        Args:
            customer_id: The customer ID
            page_url: The page URL
            labels: Optional list of labels
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_page_feed_asset(
            ctx=ctx,
            customer_id=customer_id,
            page_url=page_url,
            labels=labels,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_mobile_app_asset(
        ctx: Context,
        customer_id: str,
        app_id: str,
        app_store: str,
        link_text: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a mobile app asset.

        Args:
            customer_id: The customer ID
            app_id: The app ID
            app_store: The app store (APPLE_ITUNES or GOOGLE_PLAY)
            link_text: The link text
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_mobile_app_asset(
            ctx=ctx,
            customer_id=customer_id,
            app_id=app_id,
            app_store=app_store,
            link_text=link_text,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_hotel_callout_asset(
        ctx: Context,
        customer_id: str,
        text: str,
        language_code: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a hotel callout asset.

        Args:
            customer_id: The customer ID
            text: The callout text
            language_code: Language code (e.g., "en")
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_hotel_callout_asset(
            ctx=ctx,
            customer_id=customer_id,
            text=text,
            language_code=language_code,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_call_to_action_asset(
        ctx: Context,
        customer_id: str,
        call_to_action: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a call-to-action asset.

        Args:
            customer_id: The customer ID
            call_to_action: Call to action type (LEARN_MORE, SIGN_UP, SHOP_NOW, BOOK_NOW, GET_QUOTE, APPLY_NOW, CONTACT_US, SUBSCRIBE, DOWNLOAD, ORDER_NOW, VISIT_SITE)
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_call_to_action_asset(
            ctx=ctx,
            customer_id=customer_id,
            call_to_action=call_to_action,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_location_asset(
        ctx: Context,
        customer_id: str,
        place_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a location asset.

        Args:
            customer_id: The customer ID
            place_id: The Google Place ID
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_location_asset(
            ctx=ctx,
            customer_id=customer_id,
            place_id=place_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_hotel_property_asset(
        ctx: Context,
        customer_id: str,
        place_id: str,
        hotel_name: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a hotel property asset.

        Args:
            customer_id: The customer ID
            place_id: The Google Place ID for the hotel
            hotel_name: Optional hotel name
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_hotel_property_asset(
            ctx=ctx,
            customer_id=customer_id,
            place_id=place_id,
            hotel_name=hotel_name,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_app_deep_link_asset(
        ctx: Context,
        customer_id: str,
        app_deep_link_uri: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an app deep link asset.

        Args:
            customer_id: The customer ID
            app_deep_link_uri: The deep link URI for the app
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_app_deep_link_asset(
            ctx=ctx,
            customer_id=customer_id,
            app_deep_link_uri=app_deep_link_uri,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_book_on_google_asset(
        ctx: Context,
        customer_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Book on Google asset. This asset type has no additional fields.

        Args:
            customer_id: The customer ID
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_book_on_google_asset(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_media_bundle_asset(
        ctx: Context,
        customer_id: str,
        data: bytes,
        name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a media bundle asset.

        Args:
            customer_id: The customer ID
            data: The media bundle data as bytes (ZIP file)
            name: Name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_media_bundle_asset(
            ctx=ctx,
            customer_id=customer_id,
            data=data,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_demand_gen_carousel_card_asset(
        ctx: Context,
        customer_id: str,
        marketing_image_asset: str,
        headline: str,
        call_to_action_text: str,
        square_marketing_image_asset: Optional[str] = None,
        portrait_marketing_image_asset: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen carousel card asset.

        Args:
            customer_id: The customer ID
            marketing_image_asset: Resource name of the marketing image asset
            headline: The headline text
            call_to_action_text: The call-to-action text
            square_marketing_image_asset: Optional resource name of the square marketing image asset
            portrait_marketing_image_asset: Optional resource name of the portrait marketing image asset
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_demand_gen_carousel_card_asset(
            ctx=ctx,
            customer_id=customer_id,
            marketing_image_asset=marketing_image_asset,
            headline=headline,
            call_to_action_text=call_to_action_text,
            square_marketing_image_asset=square_marketing_image_asset,
            portrait_marketing_image_asset=portrait_marketing_image_asset,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_business_message_asset(
        ctx: Context,
        customer_id: str,
        message_provider: str,
        starter_message: str,
        call_to_action_selection: str,
        call_to_action_description: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a business message asset.

        Args:
            customer_id: The customer ID
            message_provider: The message provider (WHATSAPP, FACEBOOK_MESSENGER, ZALO)
            starter_message: The starter message text
            call_to_action_selection: Call to action type (APPLY_NOW, BOOK_NOW, CONTACT_US, GET_INFO, GET_OFFER, GET_QUOTE, GET_STARTED, LEARN_MORE)
            call_to_action_description: Optional call-to-action description text
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_business_message_asset(
            ctx=ctx,
            customer_id=customer_id,
            message_provider=message_provider,
            starter_message=starter_message,
            call_to_action_selection=call_to_action_selection,
            call_to_action_description=call_to_action_description,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_education_asset(
        ctx: Context,
        customer_id: str,
        program_id: str,
        program_name: str,
        school_name: str,
        location_id: Optional[str] = None,
        subject: Optional[str] = None,
        program_description: Optional[str] = None,
        address: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        android_app_link: Optional[str] = None,
        similar_program_ids: Optional[List[str]] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        thumbnail_image_url: Optional[str] = None,
        image_url: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic education asset for education-related remarketing.

        Args:
            customer_id: The customer ID
            program_id: The program ID
            program_name: The program name
            school_name: The school name
            location_id: Optional location ID
            subject: Optional subject
            program_description: Optional program description
            address: Optional address
            contextual_keywords: Optional list of contextual keywords
            android_app_link: Optional Android app deep link
            similar_program_ids: Optional list of similar program IDs
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            thumbnail_image_url: Optional thumbnail image URL
            image_url: Optional image URL
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_education_asset(
            ctx=ctx,
            customer_id=customer_id,
            program_id=program_id,
            program_name=program_name,
            school_name=school_name,
            location_id=location_id,
            subject=subject,
            program_description=program_description,
            address=address,
            contextual_keywords=contextual_keywords,
            android_app_link=android_app_link,
            similar_program_ids=similar_program_ids,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            thumbnail_image_url=thumbnail_image_url,
            image_url=image_url,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_real_estate_asset(
        ctx: Context,
        customer_id: str,
        listing_id: str,
        listing_name: str,
        city_name: Optional[str] = None,
        description: Optional[str] = None,
        address: Optional[str] = None,
        price: Optional[str] = None,
        image_url: Optional[str] = None,
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        formatted_price: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        similar_listing_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic real estate asset for real estate remarketing.

        Args:
            customer_id: The customer ID
            listing_id: The listing ID
            listing_name: The listing name
            city_name: Optional city name
            description: Optional description
            address: Optional address
            price: Optional price
            image_url: Optional image URL
            property_type: Optional property type
            listing_type: Optional listing type
            contextual_keywords: Optional list of contextual keywords
            formatted_price: Optional formatted price string
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            similar_listing_ids: Optional list of similar listing IDs
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_real_estate_asset(
            ctx=ctx,
            customer_id=customer_id,
            listing_id=listing_id,
            listing_name=listing_name,
            city_name=city_name,
            description=description,
            address=address,
            price=price,
            image_url=image_url,
            property_type=property_type,
            listing_type=listing_type,
            contextual_keywords=contextual_keywords,
            formatted_price=formatted_price,
            android_app_link=android_app_link,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            similar_listing_ids=similar_listing_ids,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_custom_asset(
        ctx: Context,
        customer_id: str,
        id: str,
        item_title: str,
        id2: Optional[str] = None,
        item_subtitle: Optional[str] = None,
        item_description: Optional[str] = None,
        item_address: Optional[str] = None,
        item_category: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        image_url: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        similar_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic custom asset for custom remarketing.

        Args:
            customer_id: The customer ID
            id: The item ID
            item_title: The item title
            id2: Optional secondary ID
            item_subtitle: Optional item subtitle
            item_description: Optional item description
            item_address: Optional item address
            item_category: Optional item category
            price: Optional price
            sale_price: Optional sale price
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            image_url: Optional image URL
            contextual_keywords: Optional list of contextual keywords
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            similar_ids: Optional list of similar IDs
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_custom_asset(
            ctx=ctx,
            customer_id=customer_id,
            id=id,
            item_title=item_title,
            id2=id2,
            item_subtitle=item_subtitle,
            item_description=item_description,
            item_address=item_address,
            item_category=item_category,
            price=price,
            sale_price=sale_price,
            formatted_price=formatted_price,
            formatted_sale_price=formatted_sale_price,
            image_url=image_url,
            contextual_keywords=contextual_keywords,
            android_app_link=android_app_link,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            similar_ids=similar_ids,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_hotels_and_rentals_asset(
        ctx: Context,
        customer_id: str,
        property_id: str,
        property_name: str,
        image_url: Optional[str] = None,
        destination_name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        star_rating: Optional[int] = None,
        category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        address: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        similar_property_ids: Optional[List[str]] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic hotels and rentals asset for hotel remarketing.

        Args:
            customer_id: The customer ID
            property_id: The property ID
            property_name: The property name
            image_url: Optional image URL
            destination_name: Optional destination name
            description: Optional description
            price: Optional price
            sale_price: Optional sale price
            star_rating: Optional star rating (1-5)
            category: Optional category
            contextual_keywords: Optional list of contextual keywords
            address: Optional address
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            similar_property_ids: Optional list of similar property IDs
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_hotels_and_rentals_asset(
            ctx=ctx,
            customer_id=customer_id,
            property_id=property_id,
            property_name=property_name,
            image_url=image_url,
            destination_name=destination_name,
            description=description,
            price=price,
            sale_price=sale_price,
            star_rating=star_rating,
            category=category,
            contextual_keywords=contextual_keywords,
            address=address,
            android_app_link=android_app_link,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            formatted_price=formatted_price,
            formatted_sale_price=formatted_sale_price,
            similar_property_ids=similar_property_ids,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_flights_asset(
        ctx: Context,
        customer_id: str,
        destination_id: str,
        destination_name: str,
        origin_id: Optional[str] = None,
        origin_name: Optional[str] = None,
        flight_description: Optional[str] = None,
        image_url: Optional[str] = None,
        flight_price: Optional[str] = None,
        flight_sale_price: Optional[str] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        similar_destination_ids: Optional[List[str]] = None,
        custom_mapping: Optional[str] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic flights asset for flight remarketing.

        Args:
            customer_id: The customer ID
            destination_id: The destination ID
            destination_name: The destination name
            origin_id: Optional origin ID
            origin_name: Optional origin name
            flight_description: Optional flight description
            image_url: Optional image URL
            flight_price: Optional flight price
            flight_sale_price: Optional flight sale price
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            similar_destination_ids: Optional list of similar destination IDs
            custom_mapping: Optional custom mapping string
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_flights_asset(
            ctx=ctx,
            customer_id=customer_id,
            destination_id=destination_id,
            destination_name=destination_name,
            origin_id=origin_id,
            origin_name=origin_name,
            flight_description=flight_description,
            image_url=image_url,
            flight_price=flight_price,
            flight_sale_price=flight_sale_price,
            formatted_price=formatted_price,
            formatted_sale_price=formatted_sale_price,
            android_app_link=android_app_link,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            similar_destination_ids=similar_destination_ids,
            custom_mapping=custom_mapping,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_travel_asset(
        ctx: Context,
        customer_id: str,
        destination_id: str,
        title: str,
        destination_name: str,
        origin_id: Optional[str] = None,
        destination_address: Optional[str] = None,
        origin_name: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        similar_destination_ids: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        android_app_link: Optional[str] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic travel asset for travel remarketing.

        Args:
            customer_id: The customer ID
            destination_id: The destination ID
            title: The title
            destination_name: The destination name
            origin_id: Optional origin ID
            destination_address: Optional destination address
            origin_name: Optional origin name
            price: Optional price
            sale_price: Optional sale price
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            category: Optional category
            contextual_keywords: Optional list of contextual keywords
            similar_destination_ids: Optional list of similar destination IDs
            image_url: Optional image URL
            android_app_link: Optional Android app deep link
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_travel_asset(
            ctx=ctx,
            customer_id=customer_id,
            destination_id=destination_id,
            title=title,
            destination_name=destination_name,
            origin_id=origin_id,
            destination_address=destination_address,
            origin_name=origin_name,
            price=price,
            sale_price=sale_price,
            formatted_price=formatted_price,
            formatted_sale_price=formatted_sale_price,
            category=category,
            contextual_keywords=contextual_keywords,
            similar_destination_ids=similar_destination_ids,
            image_url=image_url,
            android_app_link=android_app_link,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_local_asset(
        ctx: Context,
        customer_id: str,
        deal_id: str,
        deal_name: str,
        subtitle: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[str] = None,
        sale_price: Optional[str] = None,
        image_url: Optional[str] = None,
        address: Optional[str] = None,
        category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        formatted_price: Optional[str] = None,
        formatted_sale_price: Optional[str] = None,
        android_app_link: Optional[str] = None,
        similar_deal_ids: Optional[List[str]] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic local asset for local deal remarketing.

        Args:
            customer_id: The customer ID
            deal_id: The deal ID
            deal_name: The deal name
            subtitle: Optional subtitle
            description: Optional description
            price: Optional price
            sale_price: Optional sale price
            image_url: Optional image URL
            address: Optional address
            category: Optional category
            contextual_keywords: Optional list of contextual keywords
            formatted_price: Optional formatted price string
            formatted_sale_price: Optional formatted sale price string
            android_app_link: Optional Android app deep link
            similar_deal_ids: Optional list of similar deal IDs
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_local_asset(
            ctx=ctx,
            customer_id=customer_id,
            deal_id=deal_id,
            deal_name=deal_name,
            subtitle=subtitle,
            description=description,
            price=price,
            sale_price=sale_price,
            image_url=image_url,
            address=address,
            category=category,
            contextual_keywords=contextual_keywords,
            formatted_price=formatted_price,
            formatted_sale_price=formatted_sale_price,
            android_app_link=android_app_link,
            similar_deal_ids=similar_deal_ids,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_dynamic_jobs_asset(
        ctx: Context,
        customer_id: str,
        job_id: str,
        job_title: str,
        location_id: Optional[str] = None,
        job_subtitle: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        job_category: Optional[str] = None,
        contextual_keywords: Optional[List[str]] = None,
        address: Optional[str] = None,
        salary: Optional[str] = None,
        android_app_link: Optional[str] = None,
        similar_job_ids: Optional[List[str]] = None,
        ios_app_link: Optional[str] = None,
        ios_app_store_id: Optional[int] = None,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a dynamic jobs asset for job remarketing.

        Args:
            customer_id: The customer ID
            job_id: The job ID
            job_title: The job title
            location_id: Optional location ID
            job_subtitle: Optional job subtitle
            description: Optional description
            image_url: Optional image URL
            job_category: Optional job category
            contextual_keywords: Optional list of contextual keywords
            address: Optional address
            salary: Optional salary
            android_app_link: Optional Android app deep link
            similar_job_ids: Optional list of similar job IDs
            ios_app_link: Optional iOS app deep link
            ios_app_store_id: Optional iOS App Store ID
            name: Optional name for the asset
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate without executing
            response_content_type: Response content type

        Returns:
            Created asset details including resource_name and asset_id
        """
        return await service.create_dynamic_jobs_asset(
            ctx=ctx,
            customer_id=customer_id,
            job_id=job_id,
            job_title=job_title,
            location_id=location_id,
            job_subtitle=job_subtitle,
            description=description,
            image_url=image_url,
            job_category=job_category,
            contextual_keywords=contextual_keywords,
            address=address,
            salary=salary,
            android_app_link=android_app_link,
            similar_job_ids=similar_job_ids,
            ios_app_link=ios_app_link,
            ios_app_store_id=ios_app_store_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_text_asset,
            create_image_asset,
            create_youtube_video_asset,
            search_assets,
            update_asset,
            create_sitelink_asset,
            create_callout_asset,
            create_structured_snippet_asset,
            create_call_asset,
            create_price_asset,
            create_promotion_asset,
            create_lead_form_asset,
            create_page_feed_asset,
            create_mobile_app_asset,
            create_hotel_callout_asset,
            create_call_to_action_asset,
            create_location_asset,
            create_hotel_property_asset,
            create_app_deep_link_asset,
            create_book_on_google_asset,
            create_media_bundle_asset,
            create_demand_gen_carousel_card_asset,
            create_business_message_asset,
            create_dynamic_education_asset,
            create_dynamic_real_estate_asset,
            create_dynamic_custom_asset,
            create_dynamic_hotels_and_rentals_asset,
            create_dynamic_flights_asset,
            create_dynamic_travel_asset,
            create_dynamic_local_asset,
            create_dynamic_jobs_asset,
        ]
    )
    return tools


def register_asset_tools(mcp: FastMCP[Any]) -> AssetService:
    """Register asset tools with the MCP server.

    Returns the AssetService instance for testing purposes.
    """
    service = AssetService()
    tools = create_asset_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
