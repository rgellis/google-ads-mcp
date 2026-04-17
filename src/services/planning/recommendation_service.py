"""Recommendation service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.recommendation_service import (
    RecommendationServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v23.enums.types.recommendation_type import (
    RecommendationTypeEnum,
)
from google.ads.googleads.v23.services.types.recommendation_service import (
    ApplyRecommendationOperation,
    ApplyRecommendationRequest,
    ApplyRecommendationResponse,
    DismissRecommendationRequest,
    DismissRecommendationResponse,
    GenerateRecommendationsRequest,
    GenerateRecommendationsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class RecommendationService:
    """Recommendation service for Google Ads optimization suggestions."""

    def __init__(self) -> None:
        """Initialize the recommendation service."""
        self._client: Optional[RecommendationServiceClient] = None

    @property
    def client(self) -> RecommendationServiceClient:
        """Get the recommendation service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("RecommendationService")
        assert self._client is not None
        return self._client

    async def get_recommendations(
        self,
        ctx: Context,
        customer_id: str,
        types: Optional[List[str]] = None,
        campaign_ids: Optional[List[str]] = None,
        dismissed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get recommendations for the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            types: Optional list of recommendation types to filter
            campaign_ids: Optional list of campaign IDs to filter
            dismissed: Whether to include dismissed recommendations
            limit: Maximum number of results

        Returns:
            List of recommendations
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
                    recommendation.type,
                    recommendation.impact,
                    recommendation.campaign,
                    recommendation.ad_group,
                    recommendation.resource_name,
                    recommendation.dismissed,
                    recommendation.campaign_budget_recommendation,
                    recommendation.keyword_recommendation,
                    recommendation.text_ad_recommendation,
                    recommendation.target_cpa_opt_in_recommendation,
                    recommendation.responsive_search_ad_recommendation,
                    recommendation.sitelink_asset_recommendation
                FROM recommendation
            """

            # Add filters
            conditions = []
            if not dismissed:
                conditions.append("recommendation.dismissed = FALSE")

            if types:
                type_conditions = [f"recommendation.type = '{t}'" for t in types]
                conditions.append(f"({' OR '.join(type_conditions)})")

            if campaign_ids:
                campaign_conditions = [
                    f"recommendation.campaign = 'customers/{customer_id}/campaigns/{cid}'"
                    for cid in campaign_ids
                ]
                conditions.append(f"({' OR '.join(campaign_conditions)})")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += f" ORDER BY recommendation.impact.base_metrics.clicks DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            recommendations = []
            for row in response:
                rec = row.recommendation
                rec_dict = {
                    "resource_name": rec.resource_name,
                    "type": rec.type.name if rec.type else "UNKNOWN",
                    "dismissed": rec.dismissed,
                }

                # Add impact if available
                if rec.impact:
                    impact = rec.impact
                    rec_dict["impact"] = {"base_metrics": {}, "potential_metrics": {}}

                    if impact.base_metrics:
                        base = impact.base_metrics
                        rec_dict["impact"]["base_metrics"] = {
                            "impressions": base.impressions,
                            "clicks": base.clicks,
                            "cost_micros": base.cost_micros,
                            "conversions": base.conversions,
                            "conversions_value": base.conversions_value,
                        }

                    if impact.potential_metrics:
                        potential = impact.potential_metrics
                        rec_dict["impact"]["potential_metrics"] = {
                            "impressions": potential.impressions,
                            "clicks": potential.clicks,
                            "cost_micros": potential.cost_micros,
                            "conversions": potential.conversions,
                            "conversions_value": potential.conversions_value,
                        }

                # Add campaign and ad group info
                if rec.campaign:
                    rec_dict["campaign"] = rec.campaign
                if rec.ad_group:
                    rec_dict["ad_group"] = rec.ad_group

                # Add type-specific details
                if rec.campaign_budget_recommendation:
                    budget_rec = rec.campaign_budget_recommendation
                    rec_dict["campaign_budget_recommendation"] = {
                        "current_budget_amount_micros": budget_rec.current_budget_amount_micros,
                        "recommended_budget_amount_micros": budget_rec.recommended_budget_amount_micros,
                        "budget_options": [
                            {
                                "budget_amount_micros": opt.budget_amount_micros,
                                "impact": {
                                    "impressions": opt.impact.impressions,
                                    "clicks": opt.impact.clicks,
                                    "cost_micros": opt.impact.cost_micros,
                                    "conversions": opt.impact.conversions,
                                },
                            }
                            for opt in budget_rec.budget_options
                        ],
                    }

                if rec.keyword_recommendation:
                    kw_rec = rec.keyword_recommendation
                    rec_dict["keyword_recommendation"] = {
                        "keyword_text": kw_rec.keyword.text,
                        "match_type": kw_rec.keyword.match_type.name,
                        "recommended_cpc_bid_micros": kw_rec.recommended_cpc_bid_micros,
                    }

                if rec.text_ad_recommendation:
                    ad_rec = rec.text_ad_recommendation
                    rec_dict["text_ad_recommendation"] = {
                        "ad": {
                            "headlines": [h.text for h in ad_rec.ad.headlines],
                            "descriptions": [d.text for d in ad_rec.ad.descriptions],
                            "final_urls": list(ad_rec.ad.final_urls),
                        }
                    }

                recommendations.append(rec_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(recommendations)} recommendations",
            )

            return recommendations

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get recommendations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def apply_recommendation(
        self,
        ctx: Context,
        customer_id: str,
        recommendation_resource_name: str,
        partial_failure: bool = False,
    ) -> Dict[str, Any]:
        """Apply a recommendation.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            recommendation_resource_name: The recommendation resource name to apply

        Returns:
            Applied recommendation details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = ApplyRecommendationOperation()
            operation.resource_name = recommendation_resource_name

            # Create request
            request = ApplyRecommendationRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            if partial_failure:
                request.partial_failure = partial_failure

            # Make the API call
            response: ApplyRecommendationResponse = self.client.apply_recommendation(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Applied recommendation: {recommendation_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply recommendation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def dismiss_recommendation(
        self,
        ctx: Context,
        customer_id: str,
        recommendation_resource_names: List[str],
        partial_failure: bool = False,
    ) -> Dict[str, Any]:
        """Dismiss one or more recommendations.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            recommendation_resource_names: List of recommendation resource names to dismiss

        Returns:
            Dismissal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for resource_name in recommendation_resource_names:
                operation = (
                    DismissRecommendationRequest.DismissRecommendationOperation()
                )
                operation.resource_name = resource_name
                operations.append(operation)

            # Create request
            request = DismissRecommendationRequest()
            request.customer_id = customer_id
            request.operations = operations
            if partial_failure:
                request.partial_failure = partial_failure

            # Make the API call
            response: DismissRecommendationResponse = (
                self.client.dismiss_recommendation(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Dismissed {len(recommendation_resource_names)} recommendations",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to dismiss recommendations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_recommendations(
        self,
        ctx: Context,
        customer_id: str,
        recommendation_types: List[str],
        advertising_channel_type: str,
        campaign_sitelink_count: Optional[int] = None,
        conversion_tracking_status: Optional[str] = None,
        bidding_info: Optional[Dict[str, Any]] = None,
        ad_group_info: Optional[List[Dict[str, Any]]] = None,
        seed_info: Optional[Dict[str, Any]] = None,
        budget_info: Optional[Dict[str, Any]] = None,
        campaign_image_asset_count: Optional[int] = None,
        campaign_call_asset_count: Optional[int] = None,
        country_codes: Optional[List[str]] = None,
        language_codes: Optional[List[str]] = None,
        positive_locations_ids: Optional[List[int]] = None,
        negative_locations_ids: Optional[List[int]] = None,
        target_partner_search_network: Optional[bool] = None,
        target_content_network: Optional[bool] = None,
        merchant_center_account_id: Optional[int] = None,
        is_new_customer: Optional[bool] = None,
        asset_group_info: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Generate recommendations for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            recommendation_types: List of types to generate (e.g. CAMPAIGN_BUDGET, KEYWORD,
                MAXIMIZE_CLICKS_OPT_IN, SET_TARGET_CPA, SITELINK_ASSET, etc.)
            advertising_channel_type: Channel type (SEARCH, PERFORMANCE_MAX)
            campaign_sitelink_count: Number of sitelinks (needed for SITELINK_ASSET)
            conversion_tracking_status: Conversion tracking status (for bidding opt-in types)
            bidding_info: Dict with bidding_strategy_type and optional target_cpa_micros/target_roas
            ad_group_info: List of ad group dicts with ad_group_type and keywords
            seed_info: Dict with url_seed and/or keyword_seeds
            budget_info: Dict with current_budget (micros)
            asset_group_info: List of PMax asset group dicts with final_url, headline, description

        Returns:
            Generated recommendations
        """
        try:
            customer_id = format_customer_id(customer_id)

            rec_type_enums = [
                getattr(RecommendationTypeEnum.RecommendationType, t)
                for t in recommendation_types
            ]
            channel_enum = getattr(
                AdvertisingChannelTypeEnum.AdvertisingChannelType,
                advertising_channel_type,
            )

            request = GenerateRecommendationsRequest()
            request.customer_id = customer_id
            request.recommendation_types = rec_type_enums
            request.advertising_channel_type = channel_enum

            if campaign_sitelink_count is not None:
                request.campaign_sitelink_count = campaign_sitelink_count

            if conversion_tracking_status is not None:
                from google.ads.googleads.v23.enums.types.conversion_tracking_status_enum import (
                    ConversionTrackingStatusEnum,
                )

                request.conversion_tracking_status = getattr(
                    ConversionTrackingStatusEnum.ConversionTrackingStatus,
                    conversion_tracking_status,
                )

            if bidding_info is not None:
                from google.ads.googleads.v23.enums.types.bidding_strategy_type import (
                    BiddingStrategyTypeEnum,
                )

                bi = request.bidding_info
                bi.bidding_strategy_type = getattr(
                    BiddingStrategyTypeEnum.BiddingStrategyType,
                    bidding_info["bidding_strategy_type"],
                )
                if "target_cpa_micros" in bidding_info:
                    bi.target_cpa_micros = bidding_info["target_cpa_micros"]
                if "target_roas" in bidding_info:
                    bi.target_roas = bidding_info["target_roas"]

            if seed_info is not None:
                si = request.seed_info
                if "url_seed" in seed_info:
                    si.url_seed = seed_info["url_seed"]
                if "keyword_seeds" in seed_info:
                    si.keyword_seeds = seed_info["keyword_seeds"]

            if budget_info is not None:
                request.budget_info.current_budget = budget_info["current_budget"]

            if campaign_image_asset_count is not None:
                request.campaign_image_asset_count = campaign_image_asset_count
            if campaign_call_asset_count is not None:
                request.campaign_call_asset_count = campaign_call_asset_count
            if country_codes is not None:
                request.country_codes = country_codes
            if language_codes is not None:
                request.language_codes = language_codes
            if positive_locations_ids is not None:
                request.positive_locations_ids = positive_locations_ids
            if negative_locations_ids is not None:
                request.negative_locations_ids = negative_locations_ids
            if target_partner_search_network is not None:
                request.target_partner_search_network = target_partner_search_network
            if target_content_network is not None:
                request.target_content_network = target_content_network
            if merchant_center_account_id is not None:
                request.merchant_center_account_id = merchant_center_account_id
            if is_new_customer is not None:
                request.is_new_customer = is_new_customer
            if asset_group_info is not None:
                for ag in asset_group_info:
                    agi = GenerateRecommendationsRequest.AssetGroupInfo()
                    if "final_url" in ag:
                        agi.final_url = ag["final_url"]
                    if "headline" in ag:
                        agi.headline = ag["headline"]
                    if "description" in ag:
                        agi.description = ag["description"]
                    request.asset_group_info.append(agi)

            response: GenerateRecommendationsResponse = (
                self.client.generate_recommendations(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate recommendations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_recommendation_tools(
    service: RecommendationService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the recommendation service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def get_recommendations(
        ctx: Context,
        customer_id: str,
        types: Optional[List[str]] = None,
        campaign_ids: Optional[List[str]] = None,
        dismissed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations for the account.

        Args:
            customer_id: The customer ID
            types: Optional list of recommendation types to filter:
                - CAMPAIGN_BUDGET
                - KEYWORD
                - TEXT_AD
                - TARGET_CPA_OPT_IN
                - RESPONSIVE_SEARCH_AD
                - SITELINK_EXTENSION
                - CALL_EXTENSION
                - KEYWORD_MATCH_TYPE
                - etc.
            campaign_ids: Optional list of campaign IDs to filter recommendations
            dismissed: Whether to include dismissed recommendations
            limit: Maximum number of results

        Returns:
            List of recommendations with type, impact, and specific details
        """
        return await service.get_recommendations(
            ctx=ctx,
            customer_id=customer_id,
            types=types,
            campaign_ids=campaign_ids,
            dismissed=dismissed,
            limit=limit,
        )

    async def apply_recommendation(
        ctx: Context,
        customer_id: str,
        recommendation_resource_name: str,
        partial_failure: bool = False,
    ) -> Dict[str, Any]:
        """Apply a specific recommendation.

        Args:
            customer_id: The customer ID
            recommendation_resource_name: The full resource name of the recommendation to apply
            partial_failure: Whether to enable partial failure

        Returns:
            Applied recommendation details
        """
        return await service.apply_recommendation(
            ctx=ctx,
            customer_id=customer_id,
            recommendation_resource_name=recommendation_resource_name,
            partial_failure=partial_failure,
        )

    async def dismiss_recommendation(
        ctx: Context,
        customer_id: str,
        recommendation_resource_names: List[str],
        partial_failure: bool = False,
    ) -> Dict[str, Any]:
        """Dismiss one or more recommendations.

        Args:
            customer_id: The customer ID
            recommendation_resource_names: List of recommendation resource names to dismiss
            partial_failure: Whether to enable partial failure

        Returns:
            Dismissal result with count and status
        """
        return await service.dismiss_recommendation(
            ctx=ctx,
            customer_id=customer_id,
            recommendation_resource_names=recommendation_resource_names,
            partial_failure=partial_failure,
        )

    async def generate_recommendations(
        ctx: Context,
        customer_id: str,
        recommendation_types: List[str],
        advertising_channel_type: str,
        campaign_sitelink_count: Optional[int] = None,
        conversion_tracking_status: Optional[str] = None,
        bidding_info: Optional[Dict[str, Any]] = None,
        seed_info: Optional[Dict[str, Any]] = None,
        budget_info: Optional[Dict[str, Any]] = None,
        campaign_image_asset_count: Optional[int] = None,
        campaign_call_asset_count: Optional[int] = None,
        country_codes: Optional[List[str]] = None,
        language_codes: Optional[List[str]] = None,
        positive_locations_ids: Optional[List[int]] = None,
        negative_locations_ids: Optional[List[int]] = None,
        target_partner_search_network: Optional[bool] = None,
        target_content_network: Optional[bool] = None,
        merchant_center_account_id: Optional[int] = None,
        is_new_customer: Optional[bool] = None,
        asset_group_info: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Generate optimization recommendations for a customer.

        Args:
            customer_id: The customer ID
            recommendation_types: List of types to generate
            advertising_channel_type: Channel type - SEARCH or PERFORMANCE_MAX
            campaign_sitelink_count: Number of sitelinks (for SITELINK_ASSET type)
            conversion_tracking_status: Conversion tracking status (for bidding opt-in)
            bidding_info: Dict with bidding_strategy_type and optional target_cpa_micros/target_roas
            seed_info: Dict with url_seed and/or keyword_seeds for keyword generation
            budget_info: Dict with current_budget (micros) for budget recommendations
            campaign_image_asset_count: Number of image assets in the campaign
            campaign_call_asset_count: Number of call assets in the campaign
            country_codes: List of country codes for targeting
            language_codes: List of language codes for targeting
            positive_locations_ids: List of positive location IDs for targeting
            negative_locations_ids: List of negative location IDs for targeting
            target_partner_search_network: Whether to target partner search network
            target_content_network: Whether to target content network
            merchant_center_account_id: Merchant Center account ID
            is_new_customer: Whether this is a new customer
            asset_group_info: List of PMax asset groups, each with final_url, headline, description

        Returns:
            Generated recommendations
        """
        return await service.generate_recommendations(
            ctx=ctx,
            customer_id=customer_id,
            recommendation_types=recommendation_types,
            advertising_channel_type=advertising_channel_type,
            campaign_sitelink_count=campaign_sitelink_count,
            conversion_tracking_status=conversion_tracking_status,
            bidding_info=bidding_info,
            seed_info=seed_info,
            budget_info=budget_info,
            campaign_image_asset_count=campaign_image_asset_count,
            campaign_call_asset_count=campaign_call_asset_count,
            country_codes=country_codes,
            language_codes=language_codes,
            positive_locations_ids=positive_locations_ids,
            negative_locations_ids=negative_locations_ids,
            target_partner_search_network=target_partner_search_network,
            target_content_network=target_content_network,
            merchant_center_account_id=merchant_center_account_id,
            is_new_customer=is_new_customer,
            asset_group_info=asset_group_info,
        )

    tools.extend(
        [
            get_recommendations,
            apply_recommendation,
            dismiss_recommendation,
            generate_recommendations,
        ]
    )
    return tools


def register_recommendation_tools(mcp: FastMCP[Any]) -> RecommendationService:
    """Register recommendation tools with the MCP server.

    Returns the RecommendationService instance for testing purposes.
    """
    service = RecommendationService()
    tools = create_recommendation_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
