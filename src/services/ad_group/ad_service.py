"""Ad service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.ad_asset import (
    AdDemandGenCarouselCardAsset,
    AdImageAsset,
    AdMediaBundleAsset,
    AdTextAsset,
    AdVideoAsset,
)
from google.ads.googleads.v23.common.types.ad_type_infos import (
    AppAdInfo,
    DemandGenCarouselAdInfo,
    DemandGenMultiAssetAdInfo,
    DemandGenVideoResponsiveAdInfo,
    DisplayUploadAdInfo,
    ExpandedTextAdInfo,
    HotelAdInfo,
    InFeedVideoAdInfo,
    LocalAdInfo,
    ResponsiveDisplayAdInfo,
    ResponsiveSearchAdInfo,
    ShoppingProductAdInfo,
    SmartCampaignAdInfo,
    TravelAdInfo,
    VideoBumperInStreamAdInfo,
    VideoAdInfo,
    VideoNonSkippableInStreamAdInfo,
    VideoResponsiveAdInfo,
    VideoTrueViewInStreamAdInfo,
)
from google.ads.googleads.v23.enums.types.display_upload_product_type import (
    DisplayUploadProductTypeEnum,
)
from google.ads.googleads.v23.enums.types.ad_group_ad_status import (
    AdGroupAdStatusEnum,
)
from google.ads.googleads.v23.resources.types.ad import Ad
from google.ads.googleads.v23.resources.types.ad_group_ad import AdGroupAd
from google.ads.googleads.v23.services.services.ad_group_ad_service import (
    AdGroupAdServiceClient,
)
from google.ads.googleads.v23.services.services.ad_service import (
    AdServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_ad_service import (
    AdGroupAdOperation,
    MutateAdGroupAdsRequest,
    MutateAdGroupAdsResponse,
)
from google.ads.googleads.v23.services.types.ad_service import (
    AdOperation,
    MutateAdsRequest,
    MutateAdsResponse,
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


class AdService:
    """Ad service for managing Google Ads ads.

    Uses AdGroupAdServiceClient for create/remove/status (ads must be
    associated with an ad group), and AdServiceClient for updating
    ad content (headlines, descriptions, URLs).
    """

    def __init__(self) -> None:
        """Initialize the ad service."""
        self._client: Optional[AdGroupAdServiceClient] = None
        self._ad_client: Optional[AdServiceClient] = None

    @property
    def client(self) -> AdGroupAdServiceClient:
        """Get the ad group ad service client (for create/remove/status)."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupAdService")
        assert self._client is not None
        return self._client

    @property
    def ad_client(self) -> AdServiceClient:
        """Get the ad service client (for updating ad content)."""
        if self._ad_client is None:
            sdk_client = get_sdk_client()
            self._ad_client = sdk_client.client.get_service("AdService")
        assert self._ad_client is not None
        return self._ad_client

    async def create_responsive_search_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a responsive search ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts (min 3, max 15)
            descriptions: List of description texts (min 2, max 4)
            final_urls: List of landing page URLs
            path1: First path component for display URL
            path2: Second path component for display URL
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create ad
            ad = Ad()
            ad.final_urls.extend(final_urls)

            # Create responsive search ad info
            responsive_search_ad = ResponsiveSearchAdInfo()

            # Set display URL paths on the ad info
            if path1:
                responsive_search_ad.path1 = path1
            if path2:
                responsive_search_ad.path2 = path2

            # Add headlines
            for headline_text in headlines:
                headline = AdTextAsset()
                headline.text = headline_text
                responsive_search_ad.headlines.append(headline)

            # Add descriptions
            for description_text in descriptions:
                description = AdTextAsset()
                description.text = description_text
                responsive_search_ad.descriptions.append(description)

            ad.responsive_search_ad = responsive_search_ad

            # Create ad group ad
            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            # Create operation
            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            # Create request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created responsive search ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create responsive search ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_expanded_text_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headline1: str,
        headline2: str,
        headline3: Optional[str],
        description1: str,
        description2: Optional[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create an expanded text ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headline1: First headline (required)
            headline2: Second headline (required)
            headline3: Third headline (optional)
            description1: First description (required)
            description2: Second description (optional)
            final_urls: List of landing page URLs
            path1: First path component for display URL
            path2: Second path component for display URL
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create ad
            ad = Ad()
            ad.final_urls.extend(final_urls)

            # Create expanded text ad info
            expanded_text_ad = ExpandedTextAdInfo()

            # Set display URL paths on the ad info
            if path1:
                expanded_text_ad.path1 = path1
            if path2:
                expanded_text_ad.path2 = path2
            expanded_text_ad.headline_part1 = headline1
            expanded_text_ad.headline_part2 = headline2
            if headline3:
                expanded_text_ad.headline_part3 = headline3

            expanded_text_ad.description = description1
            if description2:
                expanded_text_ad.description2 = description2

            ad.expanded_text_ad = expanded_text_ad

            # Create ad group ad
            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            # Create operation
            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            # Create request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created expanded text ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create expanded text ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_ad_status(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        ad_id: str,
        status: AdGroupAdStatusEnum.AdGroupAdStatus,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update the status of an ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            ad_id: The ad ID
            status: New ad status enum value

        Returns:
            Updated ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/adGroupAds/{ad_group_id}~{ad_id}"

            # Create ad group ad with resource name
            ad_group_ad = AdGroupAd()
            ad_group_ad.resource_name = resource_name
            ad_group_ad.status = status

            # Create the operation
            operation = AdGroupAdOperation()
            operation.update = ad_group_ad
            operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

            # Create the request
            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_ad_group_ads(request=request)

            await ctx.log(
                level="info",
                message=f"Updated ad {ad_id} status to {status}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update ad status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_resource_name: str,
        headlines: Optional[List[str]] = None,
        descriptions: Optional[List[str]] = None,
        final_urls: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update an existing ad's content via AdService.MutateAds.

        This updates the ad itself (headlines, descriptions, URLs) without
        changing its ad group association or status.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_resource_name: Resource name of the ad (e.g. customers/123/ads/456)
            headlines: New headline texts (for responsive search ads)
            descriptions: New description texts (for responsive search ads)
            final_urls: New landing page URLs
            path1: New first path component for display URL
            path2: New second path component for display URL

        Returns:
            Updated ad details
        """
        try:
            customer_id = format_customer_id(customer_id)

            ad = Ad()
            ad.resource_name = ad_resource_name

            update_mask_fields = []

            if final_urls is not None:
                ad.final_urls[:] = final_urls
                update_mask_fields.append("final_urls")

            if (
                headlines is not None
                or descriptions is not None
                or path1 is not None
                or path2 is not None
            ):
                rsa = ResponsiveSearchAdInfo()
                if headlines is not None:
                    for text in headlines:
                        asset = AdTextAsset()
                        asset.text = text
                        rsa.headlines.append(asset)
                    update_mask_fields.append("responsive_search_ad.headlines")
                if descriptions is not None:
                    for text in descriptions:
                        asset = AdTextAsset()
                        asset.text = text
                        rsa.descriptions.append(asset)
                    update_mask_fields.append("responsive_search_ad.descriptions")
                if path1 is not None:
                    rsa.path1 = path1
                    update_mask_fields.append("responsive_search_ad.path1")
                if path2 is not None:
                    rsa.path2 = path2
                    update_mask_fields.append("responsive_search_ad.path2")
                ad.responsive_search_ad = rsa

            operation = AdOperation()
            operation.update = ad
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            request = MutateAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdsResponse = self.ad_client.mutate_ads(request=request)

            await ctx.log(
                level="info",
                message=f"Updated ad content: {ad_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_responsive_display_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        marketing_images: List[str],
        headlines: List[str],
        long_headline: str,
        descriptions: List[str],
        business_name: str,
        final_urls: List[str],
        square_marketing_images: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a responsive display ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            marketing_images: List of image asset resource names
            headlines: List of headline texts (max 5)
            long_headline: Long headline text
            descriptions: List of description texts (max 5)
            business_name: Business name
            final_urls: List of landing page URLs
            square_marketing_images: Optional list of square image asset resource names
            logo_images: Optional list of logo image asset resource names
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            responsive_display_ad = ResponsiveDisplayAdInfo()

            for asset_rn in marketing_images:
                img = AdImageAsset()
                img.asset = asset_rn
                responsive_display_ad.marketing_images.append(img)

            if square_marketing_images:
                for asset_rn in square_marketing_images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    responsive_display_ad.square_marketing_images.append(img)

            if logo_images:
                for asset_rn in logo_images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    responsive_display_ad.logo_images.append(img)

            for text in headlines:
                headline = AdTextAsset()
                headline.text = text
                responsive_display_ad.headlines.append(headline)

            long_hl = AdTextAsset()
            long_hl.text = long_headline
            responsive_display_ad.long_headline = long_hl

            for text in descriptions:
                desc = AdTextAsset()
                desc.text = text
                responsive_display_ad.descriptions.append(desc)

            responsive_display_ad.business_name = business_name
            ad.responsive_display_ad = responsive_display_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created responsive display ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create responsive display ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_video_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        video_asset: str,
        final_urls: List[str],
        video_format: str = "in_stream",
        action_button_label: Optional[str] = None,
        action_headline: Optional[str] = None,
        companion_banner: Optional[str] = None,
        in_feed_headline: Optional[str] = None,
        in_feed_description1: Optional[str] = None,
        in_feed_description2: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a video ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            video_asset: Video asset resource name
            final_urls: List of landing page URLs
            video_format: Video ad format - 'in_stream', 'bumper', 'non_skippable', or 'in_feed'
            action_button_label: CTA button label (for in_stream/bumper/non_skippable)
            action_headline: CTA headline (for in_stream/bumper/non_skippable)
            companion_banner: Companion banner image asset resource name
            in_feed_headline: Headline for in-feed video ads
            in_feed_description1: First description for in-feed video ads
            in_feed_description2: Second description for in-feed video ads
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            video_ad = VideoAdInfo()

            video_asset_obj = AdVideoAsset()
            video_asset_obj.asset = video_asset
            video_ad.video = video_asset_obj

            if video_format == "in_stream":
                in_stream = VideoTrueViewInStreamAdInfo()
                if action_button_label:
                    in_stream.action_button_label = action_button_label
                if action_headline:
                    in_stream.action_headline = action_headline
                if companion_banner:
                    banner = AdImageAsset()
                    banner.asset = companion_banner
                    in_stream.companion_banner = banner
                video_ad.in_stream = in_stream
            elif video_format == "bumper":
                bumper = VideoBumperInStreamAdInfo()
                if action_button_label:
                    bumper.action_button_label = action_button_label
                if action_headline:
                    bumper.action_headline = action_headline
                if companion_banner:
                    banner = AdImageAsset()
                    banner.asset = companion_banner
                    bumper.companion_banner = banner
                video_ad.bumper = bumper
            elif video_format == "non_skippable":
                non_skip = VideoNonSkippableInStreamAdInfo()
                if action_button_label:
                    non_skip.action_button_label = action_button_label
                if action_headline:
                    non_skip.action_headline = action_headline
                if companion_banner:
                    banner = AdImageAsset()
                    banner.asset = companion_banner
                    non_skip.companion_banner = banner
                video_ad.non_skippable = non_skip
            elif video_format == "in_feed":
                in_feed = InFeedVideoAdInfo()
                if in_feed_headline:
                    in_feed.headline = in_feed_headline
                if in_feed_description1:
                    in_feed.description1 = in_feed_description1
                if in_feed_description2:
                    in_feed.description2 = in_feed_description2
                video_ad.in_feed = in_feed
            else:
                raise ValueError(
                    f"Unsupported video format: {video_format}. "
                    "Must be 'in_stream', 'bumper', 'non_skippable', or 'in_feed'."
                )

            ad.video_ad = video_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created {video_format} video ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create video ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_demand_gen_multi_asset_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        marketing_images: List[str],
        headlines: List[str],
        descriptions: List[str],
        business_name: str,
        final_urls: List[str],
        square_marketing_images: Optional[List[str]] = None,
        portrait_marketing_images: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        call_to_action_text: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen multi-asset ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            marketing_images: List of image asset resource names
            headlines: List of headline texts
            descriptions: List of description texts
            business_name: Business name
            final_urls: List of landing page URLs
            square_marketing_images: Optional square image asset resource names
            portrait_marketing_images: Optional portrait image asset resource names
            logo_images: Optional logo image asset resource names
            call_to_action_text: Optional call to action text
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            dg_ad = DemandGenMultiAssetAdInfo()

            for asset_rn in marketing_images:
                img = AdImageAsset()
                img.asset = asset_rn
                dg_ad.marketing_images.append(img)

            if square_marketing_images:
                for asset_rn in square_marketing_images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    dg_ad.square_marketing_images.append(img)

            if portrait_marketing_images:
                for asset_rn in portrait_marketing_images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    dg_ad.portrait_marketing_images.append(img)

            if logo_images:
                for asset_rn in logo_images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    dg_ad.logo_images.append(img)

            for text in headlines:
                hl = AdTextAsset()
                hl.text = text
                dg_ad.headlines.append(hl)

            for text in descriptions:
                desc = AdTextAsset()
                desc.text = text
                dg_ad.descriptions.append(desc)

            dg_ad.business_name = business_name
            if call_to_action_text:
                dg_ad.call_to_action_text = call_to_action_text

            ad.demand_gen_multi_asset_ad = dg_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created demand gen multi-asset ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create demand gen multi-asset ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_smart_campaign_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Smart Campaign ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            descriptions: List of description texts
            final_urls: List of landing page URLs
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            smart_ad = SmartCampaignAdInfo()

            for text in headlines:
                hl = AdTextAsset()
                hl.text = text
                smart_ad.headlines.append(hl)

            for text in descriptions:
                desc = AdTextAsset()
                desc.text = text
                smart_ad.descriptions.append(desc)

            ad.smart_campaign_ad = smart_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created smart campaign ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create smart campaign ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_app_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create an app ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            descriptions: List of description texts
            final_urls: List of landing page URLs
            images: Optional list of image asset resource names
            videos: Optional list of video asset resource names
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            app_ad = AppAdInfo()

            for text in headlines:
                hl = AdTextAsset()
                hl.text = text
                app_ad.headlines.append(hl)

            for text in descriptions:
                desc = AdTextAsset()
                desc.text = text
                app_ad.descriptions.append(desc)

            if images:
                for asset_rn in images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    app_ad.images.append(img)

            if videos:
                for asset_rn in videos:
                    vid = AdVideoAsset()
                    vid.asset = asset_rn
                    app_ad.youtube_videos.append(vid)

            ad.app_ad = app_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created app ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create app ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_shopping_product_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a shopping product ad.

        ShoppingProductAdInfo has no fields - product data comes from Merchant Center.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.shopping_product_ad = ShoppingProductAdInfo()

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created shopping product ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create shopping product ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_hotel_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a hotel ad.

        HotelAdInfo has no fields - hotel data comes from the Hotel Center feed.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.hotel_ad = HotelAdInfo()

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created hotel ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create hotel ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_video_responsive_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        long_headlines: List[str],
        descriptions: List[str],
        videos: List[str],
        final_urls: List[str],
        business_name: Optional[str] = None,
        call_to_actions: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        companion_banners: Optional[List[str]] = None,
        breadcrumb1: Optional[str] = None,
        breadcrumb2: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a video responsive ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            long_headlines: List of long headline texts
            descriptions: List of description texts
            videos: List of video asset resource names
            final_urls: List of landing page URLs
            business_name: Optional business name
            call_to_actions: Optional list of CTA texts
            logo_images: Optional list of logo image asset resource names
            companion_banners: Optional list of companion banner asset resource names
            breadcrumb1: First breadcrumb for display URL
            breadcrumb2: Second breadcrumb for display URL
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            vr_ad = VideoResponsiveAdInfo()

            for text in headlines:
                hl = AdTextAsset()
                hl.text = text
                vr_ad.headlines.append(hl)

            for text in long_headlines:
                lhl = AdTextAsset()
                lhl.text = text
                vr_ad.long_headlines.append(lhl)

            for text in descriptions:
                desc = AdTextAsset()
                desc.text = text
                vr_ad.descriptions.append(desc)

            for asset_rn in videos:
                vid = AdVideoAsset()
                vid.asset = asset_rn
                vr_ad.videos.append(vid)

            if call_to_actions:
                for text in call_to_actions:
                    cta = AdTextAsset()
                    cta.text = text
                    vr_ad.call_to_actions.append(cta)

            if business_name:
                bn = AdTextAsset()
                bn.text = business_name
                vr_ad.business_name = bn

            if logo_images:
                for asset_rn in logo_images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    vr_ad.logo_images.append(img)

            if companion_banners:
                for asset_rn in companion_banners:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    vr_ad.companion_banners.append(img)

            if breadcrumb1:
                vr_ad.breadcrumb1 = breadcrumb1
            if breadcrumb2:
                vr_ad.breadcrumb2 = breadcrumb2

            ad.video_responsive_ad = vr_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created video responsive ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create video responsive ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_local_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        marketing_images: List[str],
        final_urls: List[str],
        call_to_actions: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a local ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            descriptions: List of description texts
            marketing_images: List of image asset resource names
            final_urls: List of landing page URLs
            call_to_actions: Optional list of CTA texts
            logo_images: Optional list of logo image asset resource names
            videos: Optional list of video asset resource names
            path1: First path component for display URL
            path2: Second path component for display URL
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            local_ad = LocalAdInfo()

            for text in headlines:
                hl = AdTextAsset()
                hl.text = text
                local_ad.headlines.append(hl)

            for text in descriptions:
                desc = AdTextAsset()
                desc.text = text
                local_ad.descriptions.append(desc)

            for asset_rn in marketing_images:
                img = AdImageAsset()
                img.asset = asset_rn
                local_ad.marketing_images.append(img)

            if call_to_actions:
                for text in call_to_actions:
                    cta = AdTextAsset()
                    cta.text = text
                    local_ad.call_to_actions.append(cta)

            if logo_images:
                for asset_rn in logo_images:
                    img = AdImageAsset()
                    img.asset = asset_rn
                    local_ad.logo_images.append(img)

            if videos:
                for asset_rn in videos:
                    vid = AdVideoAsset()
                    vid.asset = asset_rn
                    local_ad.videos.append(vid)

            if path1:
                local_ad.path1 = path1
            if path2:
                local_ad.path2 = path2

            ad.local_ad = local_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created local ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create local ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_travel_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a travel ad.

        TravelAdInfo has no fields - travel data comes from the feed.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.travel_ad = TravelAdInfo()

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created travel ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create travel ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_demand_gen_carousel_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        business_name: str,
        headline: str,
        description: str,
        carousel_cards: List[str],
        final_urls: List[str],
        logo_image: Optional[str] = None,
        call_to_action_text: Optional[str] = None,
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen carousel ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            business_name: Business name
            headline: Ad headline text
            description: Ad description text
            carousel_cards: List of carousel card asset resource names
            final_urls: List of landing page URLs
            logo_image: Optional logo image asset resource name
            call_to_action_text: Optional call to action text
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            carousel_ad = DemandGenCarouselAdInfo()
            carousel_ad.business_name = business_name

            hl = AdTextAsset()
            hl.text = headline
            carousel_ad.headline = hl

            desc = AdTextAsset()
            desc.text = description
            carousel_ad.description = desc

            for asset_rn in carousel_cards:
                card = AdDemandGenCarouselCardAsset()
                card.asset = asset_rn
                carousel_ad.carousel_cards.append(card)

            if logo_image:
                logo = AdImageAsset()
                logo.asset = logo_image
                carousel_ad.logo_image = logo

            if call_to_action_text:
                carousel_ad.call_to_action_text = call_to_action_text

            ad.demand_gen_carousel_ad = carousel_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created demand gen carousel ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create demand gen carousel ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_display_upload_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        media_bundle: str,
        display_upload_product_type: str,
        final_urls: List[str],
        status: AdGroupAdStatusEnum.AdGroupAdStatus = AdGroupAdStatusEnum.AdGroupAdStatus.PAUSED,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a display upload ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            media_bundle: Media bundle asset resource name
            display_upload_product_type: Product type - e.g. 'HTML5_UPLOAD_AD',
                'DYNAMIC_HTML5_CUSTOM_AD', 'DYNAMIC_HTML5_EDUCATION_AD', etc.
            final_urls: List of landing page URLs
            status: Ad status enum value

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad = Ad()
            ad.final_urls.extend(final_urls)

            upload_ad = DisplayUploadAdInfo()

            bundle = AdMediaBundleAsset()
            bundle.asset = media_bundle
            upload_ad.media_bundle = bundle

            upload_ad.display_upload_product_type = getattr(
                DisplayUploadProductTypeEnum.DisplayUploadProductType,
                display_upload_product_type,
            )

            ad.display_upload_ad = upload_ad

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.ad = ad
            ad_group_ad.status = status

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = self.client.mutate_ad_group_ads(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created display upload ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create display upload ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_demand_gen_video_responsive_ad(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        long_headlines: List[str],
        descriptions: List[str],
        videos: List[str],
        business_name: str,
        logo_images: Optional[List[str]] = None,
        call_to_actions: Optional[List[str]] = None,
        breadcrumb1: Optional[str] = None,
        breadcrumb2: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen video responsive ad.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts (1-5)
            long_headlines: List of long headline texts (1-5)
            descriptions: List of description texts (1-5)
            videos: List of video asset resource names (1-5)
            business_name: Business name
            logo_images: Optional list of logo image asset resource names
            call_to_actions: Optional list of call to action texts
            breadcrumb1: Optional first breadcrumb
            breadcrumb2: Optional second breadcrumb
            status: Ad status - ENABLED or PAUSED

        Returns:
            Created ad details
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad_group_ad = AdGroupAd()
            ad_group_ad.ad_group = ad_group_resource
            ad_group_ad.status = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

            ad_info = DemandGenVideoResponsiveAdInfo()
            for h in headlines:
                ad_info.headlines.append(AdTextAsset(text=h))
            for lh in long_headlines:
                ad_info.long_headlines.append(AdTextAsset(text=lh))
            for d in descriptions:
                ad_info.descriptions.append(AdTextAsset(text=d))
            for v in videos:
                ad_info.videos.append(AdVideoAsset(asset=v))
            ad_info.business_name = business_name

            if logo_images:
                for img in logo_images:
                    ad_info.logo_images.append(AdImageAsset(asset=img))
            if call_to_actions:
                for cta in call_to_actions:
                    ad_info.call_to_actions.append(AdTextAsset(text=cta))
            if breadcrumb1:
                ad_info.breadcrumb1 = breadcrumb1
            if breadcrumb2:
                ad_info.breadcrumb2 = breadcrumb2

            ad_group_ad.ad.demand_gen_video_responsive_ad = ad_info

            operation = AdGroupAdOperation()
            operation.create = ad_group_ad

            request = MutateAdGroupAdsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupAdsResponse = (
                self.ad_group_ad_client.mutate_ad_group_ads(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created demand gen video responsive ad in ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create demand gen video responsive ad: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_tools(service: AdService) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_responsive_search_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a responsive search ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts (min 3, max 15, each max 30 chars)
            descriptions: List of description texts (min 2, max 4, each max 90 chars)
            final_urls: List of landing page URLs
            path1: First path component for display URL (max 15 chars)
            path2: Second path component for display URL (max 15 chars)
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        # Convert string enum to proper enum type
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

        return await service.create_responsive_search_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_expanded_text_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headline1: str,
        headline2: str,
        headline3: Optional[str],
        description1: str,
        description2: Optional[str],
        final_urls: List[str],
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an expanded text ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headline1: First headline (max 30 chars)
            headline2: Second headline (max 30 chars)
            headline3: Third headline (optional, max 30 chars)
            description1: First description (max 90 chars)
            description2: Second description (optional, max 90 chars)
            final_urls: List of landing page URLs
            path1: First path component for display URL (max 15 chars)
            path2: Second path component for display URL (max 15 chars)
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        # Convert string enum to proper enum type
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

        return await service.create_expanded_text_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headline1=headline1,
            headline2=headline2,
            headline3=headline3,
            description1=description1,
            description2=description2,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_ad_status(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        ad_id: str,
        status: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the status of an ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            ad_id: The ad ID
            status: New ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Updated ad details
        """
        # Convert string enum to proper enum type
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)

        return await service.update_ad_status(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            ad_id=ad_id,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_ad(
        ctx: Context,
        customer_id: str,
        ad_resource_name: str,
        headlines: Optional[List[str]] = None,
        descriptions: Optional[List[str]] = None,
        final_urls: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing ad's content (headlines, descriptions, URLs).

        Uses AdService.MutateAds to update the ad itself without changing
        its ad group association or status.

        Args:
            customer_id: The customer ID
            ad_resource_name: Resource name of the ad (e.g. customers/123/ads/456)
            headlines: New headline texts (for responsive search ads)
            descriptions: New description texts (for responsive search ads)
            final_urls: New landing page URLs
            path1: New first display URL path component
            path2: New second display URL path component

        Returns:
            Updated ad details
        """
        return await service.update_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_resource_name=ad_resource_name,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
            path1=path1,
            path2=path2,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_responsive_display_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        marketing_images: List[str],
        headlines: List[str],
        long_headline: str,
        descriptions: List[str],
        business_name: str,
        final_urls: List[str],
        square_marketing_images: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a responsive display ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            marketing_images: List of image asset resource names (landscape)
            headlines: List of headline texts (max 5, each max 30 chars)
            long_headline: Long headline text (max 90 chars)
            descriptions: List of description texts (max 5, each max 90 chars)
            business_name: Business name (max 25 chars)
            final_urls: List of landing page URLs
            square_marketing_images: Optional square image asset resource names
            logo_images: Optional logo image asset resource names
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_responsive_display_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            marketing_images=marketing_images,
            headlines=headlines,
            long_headline=long_headline,
            descriptions=descriptions,
            business_name=business_name,
            final_urls=final_urls,
            square_marketing_images=square_marketing_images,
            logo_images=logo_images,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_video_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        video_asset: str,
        final_urls: List[str],
        video_format: str = "in_stream",
        action_button_label: Optional[str] = None,
        action_headline: Optional[str] = None,
        companion_banner: Optional[str] = None,
        in_feed_headline: Optional[str] = None,
        in_feed_description1: Optional[str] = None,
        in_feed_description2: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a video ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            video_asset: Video asset resource name
            final_urls: List of landing page URLs
            video_format: Format - 'in_stream', 'bumper', 'non_skippable', or 'in_feed'
            action_button_label: CTA button label (for in_stream/bumper/non_skippable)
            action_headline: CTA headline (for in_stream/bumper/non_skippable)
            companion_banner: Companion banner image asset resource name
            in_feed_headline: Headline for in-feed video ads
            in_feed_description1: First description for in-feed video ads
            in_feed_description2: Second description for in-feed video ads
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_video_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            video_asset=video_asset,
            final_urls=final_urls,
            video_format=video_format,
            action_button_label=action_button_label,
            action_headline=action_headline,
            companion_banner=companion_banner,
            in_feed_headline=in_feed_headline,
            in_feed_description1=in_feed_description1,
            in_feed_description2=in_feed_description2,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_demand_gen_multi_asset_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        marketing_images: List[str],
        headlines: List[str],
        descriptions: List[str],
        business_name: str,
        final_urls: List[str],
        square_marketing_images: Optional[List[str]] = None,
        portrait_marketing_images: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        call_to_action_text: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen multi-asset ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            marketing_images: List of image asset resource names
            headlines: List of headline texts
            descriptions: List of description texts
            business_name: Business name
            final_urls: List of landing page URLs
            square_marketing_images: Optional square image asset resource names
            portrait_marketing_images: Optional portrait image asset resource names
            logo_images: Optional logo image asset resource names
            call_to_action_text: Optional call to action text
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_demand_gen_multi_asset_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            marketing_images=marketing_images,
            headlines=headlines,
            descriptions=descriptions,
            business_name=business_name,
            final_urls=final_urls,
            square_marketing_images=square_marketing_images,
            portrait_marketing_images=portrait_marketing_images,
            logo_images=logo_images,
            call_to_action_text=call_to_action_text,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_smart_campaign_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Smart Campaign ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            descriptions: List of description texts
            final_urls: List of landing page URLs
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_smart_campaign_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_app_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        final_urls: List[str],
        images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an app ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            descriptions: List of description texts
            final_urls: List of landing page URLs
            images: Optional list of image asset resource names
            videos: Optional list of video asset resource names
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_app_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            final_urls=final_urls,
            images=images,
            videos=videos,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_shopping_product_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a shopping product ad.

        Product data comes from Merchant Center - no ad-specific fields needed.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_shopping_product_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_hotel_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a hotel ad.

        Hotel data comes from the Hotel Center feed - no ad-specific fields needed.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_hotel_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_video_responsive_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        long_headlines: List[str],
        descriptions: List[str],
        videos: List[str],
        final_urls: List[str],
        business_name: Optional[str] = None,
        call_to_actions: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        companion_banners: Optional[List[str]] = None,
        breadcrumb1: Optional[str] = None,
        breadcrumb2: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a video responsive ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            long_headlines: List of long headline texts
            descriptions: List of description texts
            videos: List of video asset resource names
            final_urls: List of landing page URLs
            business_name: Optional business name
            call_to_actions: Optional list of CTA texts
            logo_images: Optional logo image asset resource names
            companion_banners: Optional companion banner asset resource names
            breadcrumb1: First breadcrumb for display URL
            breadcrumb2: Second breadcrumb for display URL
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_video_responsive_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            long_headlines=long_headlines,
            descriptions=descriptions,
            videos=videos,
            final_urls=final_urls,
            business_name=business_name,
            call_to_actions=call_to_actions,
            logo_images=logo_images,
            companion_banners=companion_banners,
            breadcrumb1=breadcrumb1,
            breadcrumb2=breadcrumb2,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_local_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        descriptions: List[str],
        marketing_images: List[str],
        final_urls: List[str],
        call_to_actions: Optional[List[str]] = None,
        logo_images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        path1: Optional[str] = None,
        path2: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a local ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts
            descriptions: List of description texts
            marketing_images: List of image asset resource names
            final_urls: List of landing page URLs
            call_to_actions: Optional list of CTA texts
            logo_images: Optional logo image asset resource names
            videos: Optional video asset resource names
            path1: First path for display URL
            path2: Second path for display URL
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_local_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            descriptions=descriptions,
            marketing_images=marketing_images,
            final_urls=final_urls,
            call_to_actions=call_to_actions,
            logo_images=logo_images,
            videos=videos,
            path1=path1,
            path2=path2,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_travel_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a travel ad.

        Travel data comes from the feed - no ad-specific fields needed.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_travel_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_demand_gen_carousel_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        business_name: str,
        headline: str,
        description: str,
        carousel_cards: List[str],
        final_urls: List[str],
        logo_image: Optional[str] = None,
        call_to_action_text: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen carousel ad.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            business_name: Business name
            headline: Ad headline text
            description: Ad description text
            carousel_cards: List of carousel card asset resource names
            final_urls: List of landing page URLs
            logo_image: Optional logo image asset resource name
            call_to_action_text: Optional call to action text
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_demand_gen_carousel_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            business_name=business_name,
            headline=headline,
            description=description,
            carousel_cards=carousel_cards,
            final_urls=final_urls,
            logo_image=logo_image,
            call_to_action_text=call_to_action_text,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_display_upload_ad(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        media_bundle: str,
        display_upload_product_type: str,
        final_urls: List[str],
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a display upload ad (HTML5/dynamic).

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            media_bundle: Media bundle asset resource name
            display_upload_product_type: Product type - e.g. 'HTML5_UPLOAD_AD',
                'DYNAMIC_HTML5_CUSTOM_AD', 'DYNAMIC_HTML5_EDUCATION_AD', etc.
            final_urls: List of landing page URLs
            status: Ad status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created ad details
        """
        status_enum = getattr(AdGroupAdStatusEnum.AdGroupAdStatus, status)
        return await service.create_display_upload_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            media_bundle=media_bundle,
            display_upload_product_type=display_upload_product_type,
            final_urls=final_urls,
            status=status_enum,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_demand_gen_video_responsive_ad_tool(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        headlines: List[str],
        long_headlines: List[str],
        descriptions: List[str],
        videos: List[str],
        business_name: str,
        logo_images: Optional[List[str]] = None,
        call_to_actions: Optional[List[str]] = None,
        breadcrumb1: Optional[str] = None,
        breadcrumb2: Optional[str] = None,
        status: str = "PAUSED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Demand Gen video responsive ad for video-first Demand Gen campaigns.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            headlines: List of headline texts (1-5)
            long_headlines: List of long headline texts (1-5)
            descriptions: List of description texts (1-5)
            videos: List of video asset resource names (1-5)
            business_name: Business name displayed in the ad
            logo_images: Optional logo image asset resource names
            call_to_actions: Optional call to action texts
            breadcrumb1: Optional first URL breadcrumb
            breadcrumb2: Optional second URL breadcrumb
            status: Ad status - ENABLED or PAUSED

        Returns:
            Created ad details
        """
        return await service.create_demand_gen_video_responsive_ad(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            headlines=headlines,
            long_headlines=long_headlines,
            descriptions=descriptions,
            videos=videos,
            business_name=business_name,
            logo_images=logo_images,
            call_to_actions=call_to_actions,
            breadcrumb1=breadcrumb1,
            breadcrumb2=breadcrumb2,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_responsive_search_ad,
            create_expanded_text_ad,
            update_ad_status,
            update_ad,
            create_responsive_display_ad,
            create_video_ad,
            create_demand_gen_multi_asset_ad,
            create_smart_campaign_ad,
            create_app_ad,
            create_shopping_product_ad,
            create_hotel_ad,
            create_video_responsive_ad,
            create_local_ad,
            create_travel_ad,
            create_demand_gen_carousel_ad,
            create_display_upload_ad,
            create_demand_gen_video_responsive_ad_tool,
        ]
    )
    return tools


def register_ad_tools(mcp: FastMCP[Any]) -> AdService:
    """Register ad tools with the MCP server.

    Returns the AdService instance for testing purposes.
    """
    service = AdService()
    tools = create_ad_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
