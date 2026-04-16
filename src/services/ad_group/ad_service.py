"""Ad service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.ad_asset import AdTextAsset
from google.ads.googleads.v23.common.types.ad_type_infos import (
    ExpandedTextAdInfo,
    ResponsiveSearchAdInfo,
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

    tools.extend(
        [
            create_responsive_search_ad,
            create_expanded_text_ad,
            update_ad_status,
            update_ad,
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
