"""Campaign service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types import ManualCpc
from google.ads.googleads.v23.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v23.enums.types.eu_political_advertising_status import (
    EuPoliticalAdvertisingStatusEnum,
)
from google.ads.googleads.v23.enums.types.campaign_status import CampaignStatusEnum
from google.ads.googleads.v23.resources.types.campaign import Campaign
from google.ads.googleads.v23.services.services.campaign_service import (
    CampaignServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_service import (
    BrandCampaignAssets,
    CampaignOperation,
    EnableOperation,
    EnablePMaxBrandGuidelinesRequest,
    EnablePMaxBrandGuidelinesResponse,
    MutateCampaignsRequest,
    MutateCampaignsResponse,
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


class CampaignService:
    """Campaign service for managing Google Ads campaigns."""

    def __init__(self) -> None:
        """Initialize the campaign service."""
        self._client: Optional[CampaignServiceClient] = None

    @property
    def client(self) -> CampaignServiceClient:
        """Get the campaign service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignService")
        assert self._client is not None
        return self._client

    async def create_campaign(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        budget_resource_name: str,
        advertising_channel_type: AdvertisingChannelTypeEnum.AdvertisingChannelType = AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH,
        status: CampaignStatusEnum.CampaignStatus = CampaignStatusEnum.CampaignStatus.PAUSED,
        target_google_search: bool = True,
        target_search_network: bool = False,
        target_content_network: bool = False,
        target_partner_search_network: bool = False,
        bidding_strategy: Optional[str] = None,
        bidding_strategy_resource_name: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        eu_political_advertising: str = "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a new campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Campaign name
            budget_resource_name: Resource name of the campaign budget
            advertising_channel_type: Type of advertising channel (SEARCH, DISPLAY, etc.)
            status: Campaign status (ENABLED, PAUSED, REMOVED)
            target_google_search: Show ads on Google Search (default: True)
            target_search_network: Show ads on Google search partner sites (default: False)
            target_content_network: Show ads on Google Display Network (default: False)
            target_partner_search_network: Show ads on partner search network (default: False)
            bidding_strategy: Bidding strategy type - MANUAL_CPC, MAXIMIZE_CONVERSIONS,
                MAXIMIZE_CONVERSION_VALUE, TARGET_CPA, TARGET_ROAS, TARGET_SPEND,
                TARGET_IMPRESSION_SHARE. If not set, defaults to MANUAL_CPC.
            bidding_strategy_resource_name: Resource name of a portfolio bidding strategy
                (overrides bidding_strategy if set)
            target_cpa_micros: Target CPA in micros (for TARGET_CPA strategy)
            target_roas: Target ROAS (for TARGET_ROAS strategy, e.g. 1.5 for 150%)
            eu_political_advertising: EU political advertising status -
                DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING or CONTAINS_EU_POLITICAL_ADVERTISING
            start_date: Campaign start date (YYYY-MM-DD)
            end_date: Campaign end date (YYYY-MM-DD)

        Returns:
            Created campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create a new campaign
            campaign = Campaign()
            campaign.name = name
            campaign.campaign_budget = budget_resource_name

            # Set network settings
            campaign.network_settings.target_google_search = target_google_search
            campaign.network_settings.target_search_network = target_search_network
            campaign.network_settings.target_content_network = target_content_network
            campaign.network_settings.target_partner_search_network = (
                target_partner_search_network
            )

            # Set advertising channel type
            campaign.advertising_channel_type = advertising_channel_type

            # Set status
            campaign.status = status

            # Set bidding strategy
            if bidding_strategy_resource_name:
                campaign.bidding_strategy = bidding_strategy_resource_name
            elif bidding_strategy == "MAXIMIZE_CONVERSIONS":
                from google.ads.googleads.v23.common.types import MaximizeConversions

                mc = MaximizeConversions()
                if target_cpa_micros is not None:
                    mc.target_cpa_micros = target_cpa_micros
                campaign.maximize_conversions = mc
            elif bidding_strategy == "MAXIMIZE_CONVERSION_VALUE":
                from google.ads.googleads.v23.common.types import (
                    MaximizeConversionValue,
                )

                mcv = MaximizeConversionValue()
                if target_roas is not None:
                    mcv.target_roas = target_roas
                campaign.maximize_conversion_value = mcv
            elif bidding_strategy == "TARGET_CPA":
                from google.ads.googleads.v23.common.types import TargetCpa

                tc = TargetCpa()
                if target_cpa_micros is not None:
                    tc.target_cpa_micros = target_cpa_micros
                campaign.target_cpa = tc
            elif bidding_strategy == "TARGET_ROAS":
                from google.ads.googleads.v23.common.types import TargetRoas

                tr = TargetRoas()
                if target_roas is not None:
                    tr.target_roas = target_roas
                campaign.target_roas = tr
            elif bidding_strategy == "TARGET_SPEND":
                from google.ads.googleads.v23.common.types import TargetSpend

                campaign.target_spend = TargetSpend()
            elif bidding_strategy == "TARGET_IMPRESSION_SHARE":
                from google.ads.googleads.v23.common.types import TargetImpressionShare

                campaign.target_impression_share = TargetImpressionShare()
            else:
                # Default to ManualCpc
                manual_cpc: ManualCpc = ManualCpc()
                campaign.manual_cpc = manual_cpc

            # EU political advertising declaration
            campaign.contains_eu_political_advertising = getattr(
                EuPoliticalAdvertisingStatusEnum.EuPoliticalAdvertisingStatus,
                eu_political_advertising,
            )

            # Set dates if provided
            if start_date:
                campaign.start_date_time = start_date.replace("-", "")
            if end_date:
                campaign.end_date_time = end_date.replace("-", "")

            # Create the operation
            operation = CampaignOperation()
            operation.create = campaign

            # Create the request
            request = MutateCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCampaignsResponse = self.client.mutate_campaigns(
                request=request
            )

            await ctx.log(level="info", message=f"Created campaign '{name}'")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: Optional[str] = None,
        status: Optional[CampaignStatusEnum.CampaignStatus] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID to update
            name: New campaign name (optional)
            status: New campaign status (optional)
            start_date: New start date (optional)
            end_date: New end date (optional)

        Returns:
            Updated campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create campaign with resource name
            campaign = Campaign()
            campaign.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                campaign.name = name
                update_mask_fields.append("name")

            if status is not None:
                campaign.status = status
                update_mask_fields.append("status")

            if start_date is not None:
                campaign.start_date_time = start_date.replace("-", "")
                update_mask_fields.append("start_date_time")

            if end_date is not None:
                campaign.end_date_time = end_date.replace("-", "")
                update_mask_fields.append("end_date_time")

            # Create the operation
            operation = CampaignOperation()
            operation.update = campaign
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_campaigns(request=request)

            await ctx.log(
                level="info",
                message=f"Updated campaign {campaign_id} for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_campaign(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID to remove

        Returns:
            Removal result with resource name
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"

            operation = CampaignOperation()
            operation.remove = resource_name

            request = MutateCampaignsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignsResponse = self.client.mutate_campaigns(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Removed campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove campaign: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def enable_p_max_brand_guidelines(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Enable Performance Max brand guidelines for campaigns.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of dicts, each with:
                - campaign: Campaign resource name (required)
                - auto_populate_brand_assets: bool (required)
                - brand_assets: dict with business_name_asset, logo_asset (list),
                    landscape_logo_asset (optional list) - required if auto_populate is False
                - final_uri_domain: str (optional)
                - main_color: str (optional)
                - accent_color: str (optional)
                - font_family: str (optional)

        Returns:
            Enablement results per campaign
        """
        try:
            customer_id = format_customer_id(customer_id)

            enable_ops = []
            for op_data in operations:
                enable_op = EnableOperation()
                enable_op.campaign = op_data["campaign"]
                enable_op.auto_populate_brand_assets = op_data[
                    "auto_populate_brand_assets"
                ]

                if "brand_assets" in op_data:
                    ba = op_data["brand_assets"]
                    brand_assets = BrandCampaignAssets()
                    brand_assets.business_name_asset = ba["business_name_asset"]
                    brand_assets.logo_asset = ba["logo_asset"]
                    if "landscape_logo_asset" in ba:
                        brand_assets.landscape_logo_asset = ba["landscape_logo_asset"]
                    enable_op.brand_assets = brand_assets

                if "final_uri_domain" in op_data:
                    enable_op.final_uri_domain = op_data["final_uri_domain"]
                if "main_color" in op_data:
                    enable_op.main_color = op_data["main_color"]
                if "accent_color" in op_data:
                    enable_op.accent_color = op_data["accent_color"]
                if "font_family" in op_data:
                    enable_op.font_family = op_data["font_family"]

                enable_ops.append(enable_op)

            request = EnablePMaxBrandGuidelinesRequest()
            request.customer_id = customer_id
            request.operations = enable_ops
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: EnablePMaxBrandGuidelinesResponse = (
                self.client.enable_p_max_brand_guidelines(request=request)
            )

            await ctx.log(
                level="info",
                message="Enabled PMax brand guidelines",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to enable PMax brand guidelines: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_tools(
    service: CampaignService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_campaign(
        ctx: Context,
        customer_id: str,
        name: str,
        budget_resource_name: str,
        advertising_channel_type: str = "SEARCH",
        status: str = "PAUSED",
        target_google_search: bool = True,
        target_search_network: bool = False,
        target_content_network: bool = False,
        target_partner_search_network: bool = False,
        bidding_strategy: Optional[str] = None,
        bidding_strategy_resource_name: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        eu_political_advertising: str = "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign.

        Args:
            customer_id: The customer ID
            name: Campaign name
            budget_resource_name: Resource name of the campaign budget (e.g. customers/123/campaignBudgets/456)
            advertising_channel_type: Channel type - SEARCH, DISPLAY, SHOPPING, VIDEO,
                MULTI_CHANNEL, LOCAL, SMART, PERFORMANCE_MAX, DEMAND_GEN, TRAVEL
            status: Campaign status - ENABLED or PAUSED
            target_google_search: Show ads on Google Search results (default: true)
            target_search_network: Show ads on Google search partner sites (default: false)
            target_content_network: Show ads on Google Display Network (default: false)
            target_partner_search_network: Show ads on partner search network (default: false)
            bidding_strategy: Bidding strategy type - MANUAL_CPC (default), MAXIMIZE_CONVERSIONS,
                MAXIMIZE_CONVERSION_VALUE, TARGET_CPA, TARGET_ROAS, TARGET_SPEND,
                TARGET_IMPRESSION_SHARE
            bidding_strategy_resource_name: Resource name of a portfolio bidding strategy
                (overrides bidding_strategy if set)
            target_cpa_micros: Target CPA in micros for TARGET_CPA or MAXIMIZE_CONVERSIONS
                (e.g. 5000000 for $5.00)
            target_roas: Target ROAS for TARGET_ROAS or MAXIMIZE_CONVERSION_VALUE
                (e.g. 1.5 for 150% return)
            eu_political_advertising: EU political advertising status -
                DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING or CONTAINS_EU_POLITICAL_ADVERTISING
            start_date: Campaign start date (YYYY-MM-DD)
            end_date: Campaign end date (YYYY-MM-DD)

        Returns:
            Created campaign details
        """
        channel_type_enum = getattr(
            AdvertisingChannelTypeEnum.AdvertisingChannelType, advertising_channel_type
        )
        status_enum = getattr(CampaignStatusEnum.CampaignStatus, status)

        return await service.create_campaign(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            budget_resource_name=budget_resource_name,
            advertising_channel_type=channel_type_enum,
            status=status_enum,
            target_google_search=target_google_search,
            target_search_network=target_search_network,
            target_content_network=target_content_network,
            target_partner_search_network=target_partner_search_network,
            bidding_strategy=bidding_strategy,
            bidding_strategy_resource_name=bidding_strategy_resource_name,
            target_cpa_micros=target_cpa_micros,
            target_roas=target_roas,
            eu_political_advertising=eu_political_advertising,
            start_date=start_date,
            end_date=end_date,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID to update
            name: New campaign name (optional)
            status: New campaign status (ENABLED, PAUSED, REMOVED) (optional)
            start_date: New start date (YYYY-MM-DD) (optional)
            end_date: New end date (YYYY-MM-DD) (optional)

        Returns:
            Updated campaign details
        """
        # Convert string enum to proper enum type if provided
        status_enum = (
            getattr(CampaignStatusEnum.CampaignStatus, status) if status else None
        )

        return await service.update_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            name=name,
            status=status_enum,
            start_date=start_date,
            end_date=end_date,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def enable_p_max_brand_guidelines(
        ctx: Context,
        customer_id: str,
        operations: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enable Performance Max brand guidelines for campaigns.

        Max 10 operations per request.

        Args:
            customer_id: The customer ID
            operations: List of dicts, each with:
                - campaign: Campaign resource name (required)
                - auto_populate_brand_assets: bool (required)
                - brand_assets: dict with business_name_asset, logo_asset (list),
                    landscape_logo_asset (optional list) - required if auto_populate is False
                - final_uri_domain: str (optional)
                - main_color: str (optional)
                - accent_color: str (optional)
                - font_family: str (optional)

        Returns:
            Enablement results per campaign
        """
        return await service.enable_p_max_brand_guidelines(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_campaign(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove (delete) a campaign permanently.

        This is different from pausing — a removed campaign cannot be re-enabled.
        To temporarily stop a campaign, use update_campaign with status PAUSED instead.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID to remove

        Returns:
            Removal result with resource name
        """
        return await service.remove_campaign(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_campaign,
            update_campaign,
            remove_campaign,
            enable_p_max_brand_guidelines,
        ]
    )
    return tools


def register_campaign_tools(mcp: FastMCP[Any]) -> CampaignService:
    """Register campaign tools with the MCP server.

    Returns the CampaignService instance for testing purposes.
    """
    service = CampaignService()
    tools = create_campaign_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
