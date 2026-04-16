"""Reach plan service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.reach_plan_service import (
    ReachPlanServiceClient,
)
from google.ads.googleads.v23.services.types.reach_plan_service import (
    EffectiveFrequencyLimit,
    ForecastMetricOptions,
    FrequencyCap,
    GenerateConversionRatesRequest,
    GenerateConversionRatesResponse,
    GenerateReachForecastRequest,
    GenerateReachForecastResponse,
    ListPlannableLocationsRequest,
    ListPlannableLocationsResponse,
    ListPlannableProductsRequest,
    ListPlannableProductsResponse,
    ListPlannableUserInterestsRequest,
    ListPlannableUserInterestsResponse,
    ListPlannableUserListsRequest,
    ListPlannableUserListsResponse,
    CampaignDuration,
    PlannedProduct,
    Targeting,
)
from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ReachPlanService:
    """Reach plan service for reach planning and forecasting."""

    def __init__(self) -> None:
        """Initialize the reach plan service."""
        self._client: Optional[ReachPlanServiceClient] = None

    @property
    def client(self) -> ReachPlanServiceClient:
        """Get the reach plan service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ReachPlanService")
        assert self._client is not None
        return self._client

    async def list_plannable_locations(
        self,
        ctx: Context,
    ) -> Dict[str, Any]:
        """List all plannable locations for reach planning.

        Args:
            ctx: FastMCP context

        Returns:
            List of plannable locations with details
        """
        try:
            request = ListPlannableLocationsRequest()
            response: ListPlannableLocationsResponse = (
                self.client.list_plannable_locations(request=request)
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list plannable locations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_plannable_products(
        self,
        ctx: Context,
        plannable_location_id: str,
    ) -> Dict[str, Any]:
        """List all plannable products for a given location.

        Args:
            ctx: FastMCP context
            plannable_location_id: The plannable location ID

        Returns:
            Plannable products for the location
        """
        try:
            request = ListPlannableProductsRequest()
            request.plannable_location_id = plannable_location_id

            response: ListPlannableProductsResponse = (
                self.client.list_plannable_products(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list plannable products: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_reach_forecast(
        self,
        ctx: Context,
        customer_id: str,
        plannable_location_id: str,
        currency_code: str,
        campaign_duration_days: int,
        planned_products: List[Dict[str, Any]],
        cookie_frequency_cap: Optional[int] = None,
        min_effective_frequency: Optional[int] = None,
        location_ids: Optional[List[str]] = None,
        customer_reach_group: Optional[str] = None,
        cookie_frequency_cap_setting: Optional[Dict[str, Any]] = None,
        effective_frequency_limit: Optional[int] = None,
        forecast_metric_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a reach forecast.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            plannable_location_id: Location ID for the forecast
            currency_code: Currency code (e.g. "USD")
            campaign_duration_days: Duration in days (1-90)
            planned_products: List of dicts with plannable_product_code and budget_micros
            cookie_frequency_cap: Max impressions per cookie (optional)
            min_effective_frequency: Min effective frequency (optional)
            location_ids: List of geo target constant resource names for targeting (optional)

        Returns:
            Reach forecast with on-target reach, total reach, and curve data
        """
        try:
            customer_id = format_customer_id(customer_id)

            request = GenerateReachForecastRequest()
            request.customer_id = customer_id
            request.currency_code = currency_code

            duration = CampaignDuration()
            duration.duration_in_days = campaign_duration_days
            request.campaign_duration = duration

            if cookie_frequency_cap is not None:
                request.cookie_frequency_cap = cookie_frequency_cap
            if min_effective_frequency is not None:
                request.min_effective_frequency = min_effective_frequency

            if location_ids:
                targeting = Targeting()
                targeting.plannable_location_id = plannable_location_id
                for loc_id in location_ids:
                    targeting.plannable_location_ids.append(loc_id)
                request.targeting = targeting
            else:
                targeting = Targeting()
                targeting.plannable_location_id = plannable_location_id
                request.targeting = targeting

            for pp_data in planned_products:
                pp = PlannedProduct()
                pp.plannable_product_code = pp_data["plannable_product_code"]
                pp.budget_micros = pp_data["budget_micros"]
                request.planned_products.append(pp)

            if customer_reach_group:
                request.customer_reach_group = customer_reach_group
            if cookie_frequency_cap_setting:
                fc = FrequencyCap()
                if "impressions" in cookie_frequency_cap_setting:
                    fc.impressions = cookie_frequency_cap_setting["impressions"]
                if "time_unit" in cookie_frequency_cap_setting:
                    from google.ads.googleads.v23.enums.types.frequency_cap_time_unit import (
                        FrequencyCapTimeUnitEnum,
                    )

                    fc.time_unit = getattr(
                        FrequencyCapTimeUnitEnum.FrequencyCapTimeUnit,
                        cookie_frequency_cap_setting["time_unit"],
                    )
                request.cookie_frequency_cap_setting = fc
            if effective_frequency_limit is not None:
                efl = EffectiveFrequencyLimit()
                efl.effective_frequency_breakdown_limit = effective_frequency_limit
                request.effective_frequency_limit = efl
            if forecast_metric_options:
                fmo = ForecastMetricOptions()
                if "include_coview" in forecast_metric_options:
                    fmo.include_coview = forecast_metric_options["include_coview"]
                request.forecast_metric_options = fmo

            response: GenerateReachForecastResponse = (
                self.client.generate_reach_forecast(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate reach forecast: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_conversion_rates(
        self,
        ctx: Context,
        customer_id: str,
        customer_reach_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate conversion rate suggestions for reach planning.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            Conversion rate suggestions per plannable product
        """
        try:
            customer_id = format_customer_id(customer_id)

            request = GenerateConversionRatesRequest()
            request.customer_id = customer_id
            if customer_reach_group:
                request.customer_reach_group = customer_reach_group

            response: GenerateConversionRatesResponse = (
                self.client.generate_conversion_rates(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate conversion rates: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_plannable_user_interests(
        self,
        ctx: Context,
        customer_id: str,
        taxonomy_types: Optional[List[str]] = None,
        name_query: Optional[str] = None,
        path_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List plannable user interests for reach targeting.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            taxonomy_types: Optional filter - AFFINITY, IN_MARKET
            name_query: Optional text filter on interest name (max 200 chars)

        Returns:
            List of plannable user interests
        """
        try:
            customer_id = format_customer_id(customer_id)

            request = ListPlannableUserInterestsRequest()
            request.customer_id = customer_id

            if taxonomy_types:
                from google.ads.googleads.v23.enums.types.user_interest_taxonomy_type import (
                    UserInterestTaxonomyTypeEnum,
                )

                request.user_interest_taxonomy_types = [
                    getattr(UserInterestTaxonomyTypeEnum.UserInterestTaxonomyType, t)
                    for t in taxonomy_types
                ]

            if name_query:
                request.name_query = name_query
            if path_query:
                request.path_query = path_query

            response: ListPlannableUserInterestsResponse = (
                self.client.list_plannable_user_interests(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list plannable user interests: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_plannable_user_lists(
        self,
        ctx: Context,
        customer_id: str,
        customer_reach_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List plannable user lists for reach targeting.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of plannable user lists
        """
        try:
            customer_id = format_customer_id(customer_id)

            request = ListPlannableUserListsRequest()
            request.customer_id = customer_id
            if customer_reach_group:
                request.customer_reach_group = customer_reach_group

            response: ListPlannableUserListsResponse = (
                self.client.list_plannable_user_lists(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list plannable user lists: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_reach_plan_tools(
    service: ReachPlanService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the reach plan service."""
    tools = []

    async def list_plannable_locations(
        ctx: Context,
    ) -> Dict[str, Any]:
        """List all available plannable locations for reach planning.

        Returns:
            Plannable locations with ID, name, country code, and location type
        """
        return await service.list_plannable_locations(ctx=ctx)

    async def list_plannable_products(
        ctx: Context,
        plannable_location_id: str,
    ) -> Dict[str, Any]:
        """List all plannable products available for a specific location.

        Args:
            plannable_location_id: The plannable location ID to get products for

        Returns:
            Plannable products with codes, names, and targeting options
        """
        return await service.list_plannable_products(
            ctx=ctx,
            plannable_location_id=plannable_location_id,
        )

    async def generate_reach_forecast(
        ctx: Context,
        customer_id: str,
        plannable_location_id: str,
        currency_code: str,
        campaign_duration_days: int,
        planned_products: List[Dict[str, Any]],
        cookie_frequency_cap: Optional[int] = None,
        min_effective_frequency: Optional[int] = None,
        location_ids: Optional[List[str]] = None,
        customer_reach_group: Optional[str] = None,
        cookie_frequency_cap_setting: Optional[Dict[str, Any]] = None,
        effective_frequency_limit: Optional[int] = None,
        forecast_metric_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a reach forecast for planned campaigns.

        Args:
            customer_id: The customer ID
            plannable_location_id: Location ID for the forecast
            currency_code: Currency code (e.g. "USD")
            campaign_duration_days: Duration in days (1-90)
            planned_products: List of dicts with plannable_product_code and budget_micros
            cookie_frequency_cap: Max impressions per cookie (optional)
            min_effective_frequency: Min effective frequency (optional)
            location_ids: Geo target constant resource names for targeting (optional)
            customer_reach_group: Customer reach group (optional)
            cookie_frequency_cap_setting: Dict with impressions and time_unit (optional)
            effective_frequency_limit: Effective frequency breakdown limit (optional)
            forecast_metric_options: Dict with include_coview (optional)

        Returns:
            Reach forecast with on-target reach, total reach, and curve data
        """
        return await service.generate_reach_forecast(
            ctx=ctx,
            customer_id=customer_id,
            plannable_location_id=plannable_location_id,
            currency_code=currency_code,
            campaign_duration_days=campaign_duration_days,
            planned_products=planned_products,
            cookie_frequency_cap=cookie_frequency_cap,
            min_effective_frequency=min_effective_frequency,
            location_ids=location_ids,
            customer_reach_group=customer_reach_group,
            cookie_frequency_cap_setting=cookie_frequency_cap_setting,
            effective_frequency_limit=effective_frequency_limit,
            forecast_metric_options=forecast_metric_options,
        )

    async def generate_conversion_rates(
        ctx: Context,
        customer_id: str,
        customer_reach_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate conversion rate suggestions for reach planning.

        Args:
            customer_id: The customer ID
            customer_reach_group: Customer reach group (optional)

        Returns:
            Conversion rate suggestions per plannable product
        """
        return await service.generate_conversion_rates(
            ctx=ctx,
            customer_id=customer_id,
            customer_reach_group=customer_reach_group,
        )

    async def list_plannable_user_interests(
        ctx: Context,
        customer_id: str,
        taxonomy_types: Optional[List[str]] = None,
        name_query: Optional[str] = None,
        path_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List plannable user interests for reach targeting.

        Args:
            customer_id: The customer ID
            taxonomy_types: Optional filter - AFFINITY, IN_MARKET
            name_query: Optional text filter on interest name (max 200 chars)
            path_query: Optional path query filter

        Returns:
            List of plannable user interests
        """
        return await service.list_plannable_user_interests(
            ctx=ctx,
            customer_id=customer_id,
            taxonomy_types=taxonomy_types,
            name_query=name_query,
            path_query=path_query,
        )

    async def list_plannable_user_lists(
        ctx: Context,
        customer_id: str,
        customer_reach_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List plannable user lists for reach targeting.

        Lists user lists eligible for reach planning (size 10k-700k, 30+ day membership, 10+ days old).

        Args:
            customer_id: The customer ID
            customer_reach_group: Customer reach group (optional)

        Returns:
            List of plannable user lists with display name, type, and status
        """
        return await service.list_plannable_user_lists(
            ctx=ctx,
            customer_id=customer_id,
            customer_reach_group=customer_reach_group,
        )

    tools.extend(
        [
            list_plannable_locations,
            list_plannable_products,
            generate_reach_forecast,
            generate_conversion_rates,
            list_plannable_user_interests,
            list_plannable_user_lists,
        ]
    )
    return tools


def register_reach_plan_tools(mcp: FastMCP[Any]) -> ReachPlanService:
    """Register reach plan tools with the MCP server.

    Returns the ReachPlanService instance for testing purposes.
    """
    service = ReachPlanService()
    tools = create_reach_plan_tools(service)

    for tool in tools:
        mcp.tool(tool)

    return service
