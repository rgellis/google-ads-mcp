"""Search service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.google_ads_service import (
    GoogleAdsRow,
    SearchGoogleAdsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    gaql_int,
    get_logger,
    serialize_proto_message,
)

logger = get_logger(__name__)


class SearchService:
    """Search service for querying Google Ads data."""

    def __init__(self) -> None:
        """Initialize the search service."""
        self._client: Optional[GoogleAdsServiceClient] = None

    @property
    def client(self) -> GoogleAdsServiceClient:
        """Get the Google Ads service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("GoogleAdsService")
        assert self._client is not None
        return self._client

    async def search_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Search for campaigns in a customer account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            include_removed: Whether to include removed campaigns
            limit: Maximum number of results to return

        Returns:
            List of campaign details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Build query
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.campaign_budget,
                    campaign_budget.amount_micros,
                    campaign.start_date,
                    campaign.end_date
                FROM campaign
            """

            if not include_removed:
                query += " WHERE campaign.status != 'REMOVED'"

            query += f" ORDER BY campaign.id LIMIT {gaql_int(limit, 'limit')}"

            # Create request
            request = SearchGoogleAdsRequest()
            request.customer_id = customer_id
            request.query = query

            # Execute search
            response = self.client.search(request=request)

            # Process results
            results: List[Dict[str, Any]] = []
            row: GoogleAdsRow
            for row in response:
                results.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(results)} campaigns for customer {customer_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to search campaigns: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def search_ad_groups(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Search for ad groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            include_removed: Whether to include removed ad groups
            limit: Maximum number of results to return

        Returns:
            List of ad group details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Build query
            query = """
                SELECT
                    ad_group.id,
                    ad_group.name,
                    ad_group.status,
                    ad_group.campaign,
                    ad_group.type,
                    ad_group.cpc_bid_micros,
                    ad_group.cpm_bid_micros,
                    campaign.id,
                    campaign.name
                FROM ad_group
            """

            conditions: List[str] = []
            if not include_removed:
                conditions.append("ad_group.status != 'REMOVED'")

            if campaign_id:
                conditions.append(
                    f"campaign.id = {gaql_int(campaign_id, 'campaign_id')}"
                )

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += f" ORDER BY ad_group.id LIMIT {gaql_int(limit, 'limit')}"

            # Create request
            request = SearchGoogleAdsRequest()
            request.customer_id = customer_id
            request.query = query

            # Execute search
            response = self.client.search(request=request)

            # Process results
            results: List[Dict[str, Any]] = []
            row: GoogleAdsRow
            for row in response:
                results.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(results)} ad groups",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to search ad groups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def search_keywords(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        include_negative: bool = False,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Search for keywords.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            include_negative: Whether to include negative keywords
            limit: Maximum number of results to return

        Returns:
            List of keyword details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Build query
            query = """
                SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group_criterion.negative,
                    ad_group_criterion.cpc_bid_micros,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = 'KEYWORD'
            """

            if not include_negative:
                query += " AND ad_group_criterion.negative = false"

            if ad_group_id:
                query += f" AND ad_group.id = {gaql_int(ad_group_id, 'ad_group_id')}"

            query += f" ORDER BY ad_group_criterion.criterion_id LIMIT {gaql_int(limit, 'limit')}"

            # Create request
            request = SearchGoogleAdsRequest()
            request.customer_id = customer_id
            request.query = query

            # Execute search
            response = self.client.search(request=request)

            # Process results
            results: List[Dict[str, Any]] = []
            row: GoogleAdsRow
            for row in response:
                results.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(results)} keywords",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to search keywords: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_search_tools(service: SearchService) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the search service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def search_campaigns(
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Search for campaigns in a customer account.

        For filters beyond the structured params here (name substring,
        date ranges, metric thresholds, custom field selection, etc.),
        use ``search_google_ads`` with a free-form GAQL query.

        Args:
            customer_id: The customer ID
            include_removed: Whether to include removed campaigns
            limit: Maximum number of results to return

        Returns:
            List of campaign details with id, name, status, budget, etc.
        """
        return await service.search_campaigns(
            ctx=ctx,
            customer_id=customer_id,
            include_removed=include_removed,
            limit=limit,
        )

    async def search_ad_groups(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Search for ad groups.

        For filters beyond the structured params here (name substring,
        date ranges, metric thresholds, custom field selection, etc.),
        use ``search_google_ads`` with a free-form GAQL query.

        Args:
            customer_id: The customer ID
            campaign_id: Optional campaign ID to filter by
            include_removed: Whether to include removed ad groups
            limit: Maximum number of results to return

        Returns:
            List of ad group details with id, name, status, bids, etc.
        """
        return await service.search_ad_groups(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            include_removed=include_removed,
            limit=limit,
        )

    async def search_keywords(
        ctx: Context,
        customer_id: str,
        ad_group_id: Optional[str] = None,
        include_negative: bool = False,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Search for keywords.

        For filters beyond the structured params here (substring-on-name,
        date ranges, metric thresholds, custom SELECT/ORDER BY,
        multi-condition AND/OR), use ``search_google_ads`` with a
        free-form GAQL query.

        Args:
            customer_id: The customer ID
            ad_group_id: Optional ad group ID to filter by
            include_negative: Whether to include negative keywords
            limit: Maximum number of results to return

        Returns:
            List of keyword details with text, match type, bid, etc.
        """
        return await service.search_keywords(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            include_negative=include_negative,
            limit=limit,
        )

    tools.extend([search_campaigns, search_ad_groups, search_keywords])
    return tools


def register_search_tools(mcp: FastMCP[Any]) -> SearchService:
    """Register search tools with the MCP server.

    Returns the SearchService instance for testing purposes.
    """
    service = SearchService()
    tools = create_search_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
