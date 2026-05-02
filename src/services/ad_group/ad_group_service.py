"""Ad group service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.ad_group_status import AdGroupStatusEnum
from google.ads.googleads.v23.enums.types.ad_group_type import AdGroupTypeEnum
from google.ads.googleads.v23.resources.types.ad_group import AdGroup
from google.ads.googleads.v23.services.services.ad_group_service import (
    AdGroupServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_service import (
    AdGroupOperation,
    MutateAdGroupsRequest,
    MutateAdGroupsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import (
    extend_repeated_submessages,
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_optional_submessage,
    set_request_options,
)

logger = get_logger(__name__)


class AdGroupService:
    """Ad group service for managing Google Ads ad groups."""

    def __init__(self) -> None:
        """Initialize the ad group service."""
        self._client: Optional[AdGroupServiceClient] = None

    @property
    def client(self) -> AdGroupServiceClient:
        """Get the ad group service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupService")
        assert self._client is not None
        return self._client

    async def create_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: str,
        type: AdGroupTypeEnum.AdGroupType,
        status: Optional[AdGroupStatusEnum.AdGroupStatus] = None,
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
        cpv_bid_micros: Optional[int] = None,
        target_cpa_micros: Optional[int] = None,
        target_cpc_micros: Optional[int] = None,
        target_cpm_micros: Optional[int] = None,
        target_cpv_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        percent_cpc_bid_micros: Optional[int] = None,
        fixed_cpm_micros: Optional[int] = None,
        ad_rotation_mode: Optional[str] = None,
        tracking_url_template: Optional[str] = None,
        final_url_suffix: Optional[str] = None,
        optimized_targeting_enabled: Optional[bool] = None,
        exclude_demographic_expansion: Optional[bool] = None,
        display_custom_bid_dimension: Optional[str] = None,
        audience_setting: Optional[Dict[str, Any]] = None,
        targeting_setting: Optional[Dict[str, Any]] = None,
        vertical_ads_format_setting: Optional[Dict[str, Any]] = None,
        ai_max_ad_group_setting: Optional[Dict[str, Any]] = None,
        demand_gen_ad_group_settings: Optional[Dict[str, Any]] = None,
        video_ad_group_settings: Optional[Dict[str, Any]] = None,
        url_custom_parameters: Optional[List[Dict[str, Any]]] = None,
        excluded_parent_asset_field_types: Optional[List[str]] = None,
        excluded_parent_asset_set_types: Optional[List[str]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a new ad group.

        ``type`` is required and must match the parent campaign's
        advertising_channel_type. Defaulting to SEARCH_STANDARD breaks
        creation under non-Search campaigns and silently misclassifies
        ad groups that should have been Display, Shopping, Video, or
        PMax types.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            name: Ad group name
            type: Required. Ad group type. Must match the parent campaign's
                channel type — e.g. SEARCH_STANDARD for SEARCH campaigns,
                DISPLAY_STANDARD for DISPLAY, SHOPPING_PRODUCT_ADS for
                SHOPPING, VIDEO_BUMPER / VIDEO_TRUE_VIEW_IN_STREAM /
                VIDEO_NON_SKIPPABLE_IN_STREAM for VIDEO, etc.
            status: Ad group status enum value
            cpc_bid_micros: Cost per click bid in micros (1 million micros = 1 unit)
            cpm_bid_micros: Cost per thousand impressions bid in micros
            cpv_bid_micros: Cost-per-view bid in micros (video).
            target_cpa_micros: Target CPA in micros for the ad group.
            target_cpc_micros: Average amount in micros the advertiser is
                willing to pay per click.
            target_cpm_micros: Average amount in micros the advertiser is
                willing to pay per 1000 impressions.
            target_cpv_micros: Average amount in micros the advertiser is
                willing to pay per view.
            target_roas: Target ROAS (e.g. 4.0 for 400%).
            percent_cpc_bid_micros: Percent CPC bid in micros (a fraction
                of the advertised price; only valid for hotel ad groups).
            fixed_cpm_micros: Fixed CPM in micros (only valid for ad
                groups using FIXED_CPM bidding).
            ad_rotation_mode: Ad rotation mode (OPTIMIZE or
                ROTATE_FOREVER).
            tracking_url_template: URL template for constructing a
                tracking URL.
            final_url_suffix: URL template for appending params to the
                final URL.
            optimized_targeting_enabled: Whether optimized targeting is
                enabled for the ad group.
            exclude_demographic_expansion: When True, demographics are
                excluded from the targeting types expanded by optimized
                targeting.
            display_custom_bid_dimension: Targeting dimension on which
                to place absolute bids — TargetingDimension enum value
                (e.g. AGE_RANGE, GENDER, AUDIENCE).
            audience_setting: Immutable. Dict that builds an
                ``AdGroup.AudienceSetting`` submessage.
            targeting_setting: Dict that builds a ``TargetingSetting``
                submessage controlling targeting-type-level filters.
            vertical_ads_format_setting: Dict that builds an
                ``AdGroup.VerticalAdsFormatSetting`` (vertical ads
                feature toggle for search ad groups).
            ai_max_ad_group_setting: Dict that builds an
                ``AdGroup.AiMaxAdGroupSetting`` (AI Max feature for
                standard search ad groups).
            demand_gen_ad_group_settings: Dict that builds a
                ``DemandGenAdGroupSettings`` submessage.
            video_ad_group_settings: Dict that builds a
                ``VideoAdGroupSettings`` submessage.
            url_custom_parameters: List of dicts each building a
                ``CustomParameter`` (key + value) for {_param}
                substitution in tracking_url_template / final URLs.
            excluded_parent_asset_field_types: List of
                ``AssetFieldType`` enum names that should NOT inherit
                from the parent campaign's asset set.
            excluded_parent_asset_set_types: List of ``AssetSetType``
                enum names that should NOT inherit from the parent
                campaign.

        Returns:
            Created ad group details
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create a new ad group
            ad_group = AdGroup()
            ad_group.name = name
            ad_group.campaign = campaign_resource_name

            # AdGroup.status is mutable and optional per the v23 RPC ref
            # (no Required/Output-only annotation; only `name` is required).
            # Gate the write so omitting status leaves the field unset on
            # the wire and the API applies its server-side default.
            if status is not None:
                ad_group.status = status

            # Set type
            ad_group.type_ = type

            # Set bidding if provided
            if cpc_bid_micros is not None:
                ad_group.cpc_bid_micros = cpc_bid_micros
            if cpm_bid_micros is not None:
                ad_group.cpm_bid_micros = cpm_bid_micros
            if cpv_bid_micros is not None:
                ad_group.cpv_bid_micros = cpv_bid_micros
            if target_cpa_micros is not None:
                ad_group.target_cpa_micros = target_cpa_micros
            if target_cpc_micros is not None:
                ad_group.target_cpc_micros = target_cpc_micros
            if target_cpm_micros is not None:
                ad_group.target_cpm_micros = target_cpm_micros
            if target_cpv_micros is not None:
                ad_group.target_cpv_micros = target_cpv_micros
            if target_roas is not None:
                ad_group.target_roas = target_roas
            if percent_cpc_bid_micros is not None:
                ad_group.percent_cpc_bid_micros = percent_cpc_bid_micros
            if fixed_cpm_micros is not None:
                ad_group.fixed_cpm_micros = fixed_cpm_micros

            if ad_rotation_mode is not None:
                from google.ads.googleads.v23.enums.types.ad_group_ad_rotation_mode import (
                    AdGroupAdRotationModeEnum,
                )

                ad_group.ad_rotation_mode = getattr(
                    AdGroupAdRotationModeEnum.AdGroupAdRotationMode,
                    ad_rotation_mode,
                )

            if tracking_url_template is not None:
                ad_group.tracking_url_template = tracking_url_template
            if final_url_suffix is not None:
                ad_group.final_url_suffix = final_url_suffix
            if optimized_targeting_enabled is not None:
                ad_group.optimized_targeting_enabled = optimized_targeting_enabled
            if exclude_demographic_expansion is not None:
                ad_group.exclude_demographic_expansion = exclude_demographic_expansion

            if display_custom_bid_dimension is not None:
                from google.ads.googleads.v23.enums.types.targeting_dimension import (
                    TargetingDimensionEnum,
                )

                ad_group.display_custom_bid_dimension = getattr(
                    TargetingDimensionEnum.TargetingDimension,
                    display_custom_bid_dimension,
                )

            if audience_setting is not None:
                set_optional_submessage(
                    ad_group,
                    "audience_setting",
                    audience_setting,
                    AdGroup.AudienceSetting,
                )
            if targeting_setting is not None:
                from google.ads.googleads.v23.common.types.targeting_setting import (
                    TargetingSetting,
                )

                set_optional_submessage(
                    ad_group,
                    "targeting_setting",
                    targeting_setting,
                    TargetingSetting,
                )
            if vertical_ads_format_setting is not None:
                set_optional_submessage(
                    ad_group,
                    "vertical_ads_format_setting",
                    vertical_ads_format_setting,
                    AdGroup.VerticalAdsFormatSetting,
                )
            if ai_max_ad_group_setting is not None:
                set_optional_submessage(
                    ad_group,
                    "ai_max_ad_group_setting",
                    ai_max_ad_group_setting,
                    AdGroup.AiMaxAdGroupSetting,
                )
            if demand_gen_ad_group_settings is not None:
                set_optional_submessage(
                    ad_group,
                    "demand_gen_ad_group_settings",
                    demand_gen_ad_group_settings,
                    AdGroup.DemandGenAdGroupSettings,
                )
            if video_ad_group_settings is not None:
                set_optional_submessage(
                    ad_group,
                    "video_ad_group_settings",
                    video_ad_group_settings,
                    AdGroup.VideoAdGroupSettings,
                )

            if url_custom_parameters is not None:
                from google.ads.googleads.v23.common.types import CustomParameter

                extend_repeated_submessages(
                    ad_group,
                    "url_custom_parameters",
                    url_custom_parameters,
                    CustomParameter,
                )
            if excluded_parent_asset_field_types is not None:
                from google.ads.googleads.v23.enums.types.asset_field_type import (
                    AssetFieldTypeEnum,
                )

                for name_ in excluded_parent_asset_field_types:
                    ad_group.excluded_parent_asset_field_types.append(
                        getattr(AssetFieldTypeEnum.AssetFieldType, name_)
                    )
            if excluded_parent_asset_set_types is not None:
                from google.ads.googleads.v23.enums.types.asset_set_type import (
                    AssetSetTypeEnum,
                )

                for name_ in excluded_parent_asset_set_types:
                    ad_group.excluded_parent_asset_set_types.append(
                        getattr(AssetSetTypeEnum.AssetSetType, name_)
                    )

            # Create the operation
            operation = AdGroupOperation()
            operation.create = ad_group

            # Create the request
            request = MutateAdGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAdGroupsResponse = self.client.mutate_ad_groups(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created ad group in campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        name: Optional[str] = None,
        status: Optional[AdGroupStatusEnum.AdGroupStatus] = None,
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update an existing ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID to update
            name: New ad group name (optional)
            status: New ad group status enum value (optional)
            cpc_bid_micros: New CPC bid in micros (optional)
            cpm_bid_micros: New CPM bid in micros (optional)

        Returns:
            Updated ad group details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create ad group with resource name
            ad_group = AdGroup()
            ad_group.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                ad_group.name = name
                update_mask_fields.append("name")

            if status is not None:
                ad_group.status = status
                update_mask_fields.append("status")

            if cpc_bid_micros is not None:
                ad_group.cpc_bid_micros = cpc_bid_micros
                update_mask_fields.append("cpc_bid_micros")

            if cpm_bid_micros is not None:
                ad_group.cpm_bid_micros = cpm_bid_micros
                update_mask_fields.append("cpm_bid_micros")

            # Create the operation
            operation = AdGroupOperation()
            operation.update = ad_group
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateAdGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_ad_groups(request=request)

            await ctx.log(
                level="info",
                message=f"Updated ad group {ad_group_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_ad_group(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove an ad group. This action is permanent and cannot be undone.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID to remove

        Returns:
            Removed ad group details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create the operation
            operation = AdGroupOperation()
            operation.remove = resource_name

            # Create the request
            request = MutateAdGroupsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAdGroupsResponse = self.client.mutate_ad_groups(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Removed ad group {ad_group_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove ad group: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_tools(
    service: AdGroupService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_ad_group(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: str,
        type: str,
        status: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
        cpv_bid_micros: Optional[int] = None,
        target_cpa_micros: Optional[int] = None,
        target_cpc_micros: Optional[int] = None,
        target_cpm_micros: Optional[int] = None,
        target_cpv_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        percent_cpc_bid_micros: Optional[int] = None,
        fixed_cpm_micros: Optional[int] = None,
        ad_rotation_mode: Optional[str] = None,
        tracking_url_template: Optional[str] = None,
        final_url_suffix: Optional[str] = None,
        optimized_targeting_enabled: Optional[bool] = None,
        exclude_demographic_expansion: Optional[bool] = None,
        display_custom_bid_dimension: Optional[str] = None,
        audience_setting: Optional[Dict[str, Any]] = None,
        targeting_setting: Optional[Dict[str, Any]] = None,
        vertical_ads_format_setting: Optional[Dict[str, Any]] = None,
        ai_max_ad_group_setting: Optional[Dict[str, Any]] = None,
        demand_gen_ad_group_settings: Optional[Dict[str, Any]] = None,
        video_ad_group_settings: Optional[Dict[str, Any]] = None,
        url_custom_parameters: Optional[List[Dict[str, Any]]] = None,
        excluded_parent_asset_field_types: Optional[List[str]] = None,
        excluded_parent_asset_set_types: Optional[List[str]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new ad group.

        ``type`` is required because it must match the parent campaign's
        channel type. The previous SEARCH_STANDARD default broke creation
        under non-Search campaigns and silently misclassified ad groups
        on Display, Shopping, Video, and PMax campaigns.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            name: Ad group name
            type: Required. Ad group type matching the parent campaign's
                channel: SEARCH_STANDARD for SEARCH campaigns,
                DISPLAY_STANDARD for DISPLAY, SHOPPING_PRODUCT_ADS for
                SHOPPING, VIDEO_BUMPER / VIDEO_TRUE_VIEW_IN_STREAM /
                VIDEO_NON_SKIPPABLE_IN_STREAM for VIDEO, etc.
            status: Optional. ENABLED, PAUSED, or REMOVED. Omit to let
                the API apply its default (ENABLED).
            cpc_bid_micros: Cost per click bid in micros (1 million micros = 1 unit)
            cpm_bid_micros: Cost per thousand impressions bid in micros
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').
            percent_cpc_bid_micros: Percent CPC bid in micros — fraction of advertised price (hotel only).
            final_url_suffix: URL template for appending params to the final URL.
            cpv_bid_micros: Cost-per-view bid in micros (video).
            target_cpm_micros: Target CPM in micros (cost per 1000 impressions).
            ad_rotation_mode: Ad rotation mode (OPTIMIZE or ROTATE_FOREVER).
            tracking_url_template: URL template for constructing a tracking URL.
            exclude_demographic_expansion: When True, demographics are excluded from optimized-targeting expansion.
            target_roas: Target ROAS (e.g. 4.0 for 400%).
            target_cpv_micros: Target CPV in micros (cost per view).
            fixed_cpm_micros: Fixed CPM in micros (for FIXED_CPM bidding).
            target_cpc_micros: Target CPC in micros.
            target_cpa_micros: Target CPA in micros (1_000_000 = $1).
            optimized_targeting_enabled: Whether optimized targeting is enabled.
            ai_max_ad_group_setting: Dict that builds an AiMaxAdGroupSetting submessage (AI Max for standard search ad groups).
            display_custom_bid_dimension: TargetingDimension enum value (e.g. AGE_RANGE, GENDER) for absolute bids.
            demand_gen_ad_group_settings: Dict that builds a DemandGenAdGroupSettings submessage.
            video_ad_group_settings: Dict that builds a VideoAdGroupSettings submessage.
            targeting_setting: Dict that builds a TargetingSetting submessage controlling targeting-type filters.
            audience_setting: Dict that builds the resource's AudienceSetting submessage (Immutable on Campaign/AdGroup).
            vertical_ads_format_setting: Dict that builds a VerticalAdsFormatSetting submessage (search-ads vertical formats).
            url_custom_parameters: List of dicts each building a CustomParameter (key + value) for {_param} substitution.
            excluded_parent_asset_field_types: List of AssetFieldType enum names that should NOT inherit from the parent campaign's asset set.
            excluded_parent_asset_set_types: List of AssetSetType enum names that should NOT inherit from the parent campaign.
        """
        # Convert string enums to proper enum types. status is Optional;
        # only convert when caller supplied a value.
        status_enum = (
            getattr(AdGroupStatusEnum.AdGroupStatus, status)
            if status is not None
            else None
        )
        type_enum = getattr(AdGroupTypeEnum.AdGroupType, type)

        return await service.create_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            type=type_enum,
            status=status_enum,
            cpc_bid_micros=cpc_bid_micros,
            cpm_bid_micros=cpm_bid_micros,
            cpv_bid_micros=cpv_bid_micros,
            target_cpa_micros=target_cpa_micros,
            target_cpc_micros=target_cpc_micros,
            target_cpm_micros=target_cpm_micros,
            target_cpv_micros=target_cpv_micros,
            target_roas=target_roas,
            percent_cpc_bid_micros=percent_cpc_bid_micros,
            fixed_cpm_micros=fixed_cpm_micros,
            ad_rotation_mode=ad_rotation_mode,
            tracking_url_template=tracking_url_template,
            final_url_suffix=final_url_suffix,
            optimized_targeting_enabled=optimized_targeting_enabled,
            exclude_demographic_expansion=exclude_demographic_expansion,
            display_custom_bid_dimension=display_custom_bid_dimension,
            audience_setting=audience_setting,
            targeting_setting=targeting_setting,
            vertical_ads_format_setting=vertical_ads_format_setting,
            ai_max_ad_group_setting=ai_max_ad_group_setting,
            demand_gen_ad_group_settings=demand_gen_ad_group_settings,
            video_ad_group_settings=video_ad_group_settings,
            url_custom_parameters=url_custom_parameters,
            excluded_parent_asset_field_types=excluded_parent_asset_field_types,
            excluded_parent_asset_set_types=excluded_parent_asset_set_types,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
        cpm_bid_micros: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID to update
            name: New ad group name (optional)
            status: New ad group status (ENABLED, PAUSED, REMOVED) (optional)
            cpc_bid_micros: New CPC bid in micros (optional)
            cpm_bid_micros: New CPM bid in micros (optional)
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        # Convert string enum to proper enum type if provided
        status_enum = (
            getattr(AdGroupStatusEnum.AdGroupStatus, status) if status else None
        )

        return await service.update_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            name=name,
            status=status_enum,
            cpc_bid_micros=cpc_bid_micros,
            cpm_bid_micros=cpm_bid_micros,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_ad_group(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Permanently remove an ad group. This action cannot be undone.

        The ad group and all its associated ads, keywords, and criteria
        will be permanently removed.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID to remove

        Returns:
            Removed ad group details
        """
        return await service.remove_ad_group(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([create_ad_group, update_ad_group, remove_ad_group])
    return tools


def register_ad_group_tools(mcp: FastMCP[Any]) -> AdGroupService:
    """Register ad group tools with the MCP server.

    Returns the AdGroupService instance for testing purposes.
    """
    service = AdGroupService()
    tools = create_ad_group_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
