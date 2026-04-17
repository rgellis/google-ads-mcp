"""Benchmarks service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.benchmarks_service import (
    BenchmarksServiceClient,
)
from google.ads.googleads.v23.services.types.benchmarks_service import (
    ListBenchmarksLocationsRequest,
    ListBenchmarksLocationsResponse,
    ListBenchmarksProductsRequest,
    ListBenchmarksProductsResponse,
    ListBenchmarksSourcesRequest,
    ListBenchmarksSourcesResponse,
    ListBenchmarksAvailableDatesRequest,
    ListBenchmarksAvailableDatesResponse,
    GenerateBenchmarksMetricsRequest,
    GenerateBenchmarksMetricsResponse,
    BenchmarksSource,
)
from google.ads.googleads.v23.common.types.criteria import LocationInfo
from google.ads.googleads.v23.common.types.dates import DateRange

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class BenchmarksService:
    def __init__(self) -> None:
        self._client: Optional[BenchmarksServiceClient] = None

    @property
    def client(self) -> BenchmarksServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BenchmarksService")
        assert self._client is not None
        return self._client

    async def list_benchmarks_locations(self, ctx: Context) -> Dict[str, Any]:
        try:
            request = ListBenchmarksLocationsRequest()
            response: ListBenchmarksLocationsResponse = (
                self.client.list_benchmarks_locations(request=request)
            )
            return serialize_proto_message(response)
        except Exception as e:
            error_msg = f"Failed to list benchmarks locations: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_benchmarks_products(self, ctx: Context) -> Dict[str, Any]:
        try:
            request = ListBenchmarksProductsRequest()
            response: ListBenchmarksProductsResponse = (
                self.client.list_benchmarks_products(request=request)
            )
            return serialize_proto_message(response)
        except Exception as e:
            error_msg = f"Failed to list benchmarks products: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_benchmarks_sources(
        self, ctx: Context, benchmarks_source_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List available benchmark sources (industry verticals).

        Args:
            ctx: FastMCP context
            benchmarks_source_types: Optional filter by source type
        """
        try:
            request = ListBenchmarksSourcesRequest()
            if benchmarks_source_types:
                from google.ads.googleads.v23.enums.types.benchmarks_source_type import (
                    BenchmarksSourceTypeEnum,
                )

                request.benchmarks_sources = [
                    getattr(BenchmarksSourceTypeEnum.BenchmarksSourceType, t)
                    for t in benchmarks_source_types
                ]
            response: ListBenchmarksSourcesResponse = (
                self.client.list_benchmarks_sources(request=request)
            )
            return serialize_proto_message(response)
        except Exception as e:
            error_msg = f"Failed to list benchmarks sources: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_benchmarks_available_dates(self, ctx: Context) -> Dict[str, Any]:
        try:
            request = ListBenchmarksAvailableDatesRequest()
            response: ListBenchmarksAvailableDatesResponse = (
                self.client.list_benchmarks_available_dates(request=request)
            )
            return serialize_proto_message(response)
        except Exception as e:
            error_msg = f"Failed to list benchmarks available dates: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_benchmarks_metrics(
        self,
        ctx: Context,
        customer_id: str,
        industry_vertical_id: int,
        location_resource_name: str,
        start_date: str,
        end_date: str,
        currency_code: Optional[str] = None,
        product_codes: Optional[List[str]] = None,
        date_breakdown: Optional[str] = None,
        customer_benchmarks_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate competitive benchmark metrics.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            industry_vertical_id: Industry vertical ID from list_benchmarks_sources
            location_resource_name: Geo target constant resource name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            currency_code: Optional currency code (e.g. USD)
            product_codes: Optional list of product codes to filter benchmarks
            date_breakdown: Optional time granularity (WEEK, MONTH, QUARTER)
            customer_benchmarks_group: Optional user-defined grouping label
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = GenerateBenchmarksMetricsRequest()
            request.customer_id = customer_id
            source = BenchmarksSource()
            source.industry_vertical_id = industry_vertical_id
            request.benchmarks_source = source
            location = LocationInfo()
            location.geo_target_constant = location_resource_name
            request.location = location
            date_range = DateRange()
            date_range.start_date = start_date
            date_range.end_date = end_date
            request.date_range = date_range
            if currency_code:
                request.currency_code = currency_code
            if product_codes:
                from google.ads.googleads.v23.services.types.benchmarks_service import (
                    ProductFilter,
                )

                product_filter = ProductFilter()
                product_filter.product_list.product_codes = product_codes
                request.product_filter = product_filter
            if date_breakdown:
                from google.ads.googleads.v23.services.types.benchmarks_service import (
                    BreakdownDefinition,
                )
                from google.ads.googleads.v23.enums.types.benchmarks_time_granularity import (
                    BenchmarksTimeGranularityEnum,
                )

                breakdown = BreakdownDefinition()
                breakdown.date_breakdown = getattr(
                    BenchmarksTimeGranularityEnum.BenchmarksTimeGranularity,
                    date_breakdown,
                )
                request.breakdown_definition = breakdown
            if customer_benchmarks_group:
                request.customer_benchmarks_group = customer_benchmarks_group
            response: GenerateBenchmarksMetricsResponse = (
                self.client.generate_benchmarks_metrics(request=request)
            )
            await ctx.log(level="info", message="Generated benchmarks metrics")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate benchmarks metrics: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_benchmarks_tools(
    service: BenchmarksService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def list_benchmarks_locations(ctx: Context) -> Dict[str, Any]:
        """List available geographic locations for competitive benchmarking.

        Returns:
            List of locations (countries/regions) with geo target constant resource names
        """
        return await service.list_benchmarks_locations(ctx=ctx)

    async def list_benchmarks_products(ctx: Context) -> Dict[str, Any]:
        """List available Google Ads products for competitive benchmarking (e.g. Search, Shopping, Display).

        Returns:
            List of products with codes that can be passed to generate_benchmarks_metrics
        """
        return await service.list_benchmarks_products(ctx=ctx)

    async def list_benchmarks_sources(
        ctx: Context, benchmarks_source_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List available benchmark sources (industry verticals).

        Args:
            benchmarks_source_types: Optional filter by source type
        """
        return await service.list_benchmarks_sources(
            ctx=ctx, benchmarks_source_types=benchmarks_source_types
        )

    async def list_benchmarks_available_dates(ctx: Context) -> Dict[str, Any]:
        """List available date ranges for benchmarks."""
        return await service.list_benchmarks_available_dates(ctx=ctx)

    async def generate_benchmarks_metrics(
        ctx: Context,
        customer_id: str,
        industry_vertical_id: int,
        location_resource_name: str,
        start_date: str,
        end_date: str,
        currency_code: Optional[str] = None,
        product_codes: Optional[List[str]] = None,
        date_breakdown: Optional[str] = None,
        customer_benchmarks_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate competitive benchmark metrics to compare your performance against your industry.

        Args:
            customer_id: The customer ID
            industry_vertical_id: Industry vertical ID (get from list_benchmarks_sources)
            location_resource_name: Geo target constant resource name (get from list_benchmarks_locations)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            currency_code: Optional currency code (e.g. "USD")
            product_codes: Optional product codes to filter (get from list_benchmarks_products)
            date_breakdown: Optional time granularity - WEEK, MONTH, or QUARTER
            customer_benchmarks_group: Optional user-defined grouping label

        Returns:
            Benchmark metrics including CPCs, CTRs, and conversion rates for your industry
        """
        return await service.generate_benchmarks_metrics(
            ctx=ctx,
            customer_id=customer_id,
            industry_vertical_id=industry_vertical_id,
            location_resource_name=location_resource_name,
            start_date=start_date,
            end_date=end_date,
            currency_code=currency_code,
            product_codes=product_codes,
            date_breakdown=date_breakdown,
            customer_benchmarks_group=customer_benchmarks_group,
        )

    tools.extend(
        [
            list_benchmarks_locations,
            list_benchmarks_products,
            list_benchmarks_sources,
            list_benchmarks_available_dates,
            generate_benchmarks_metrics,
        ]
    )
    return tools


def register_benchmarks_tools(mcp: FastMCP[Any]) -> BenchmarksService:
    service = BenchmarksService()
    tools = create_benchmarks_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
