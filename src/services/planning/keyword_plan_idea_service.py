"""Keyword plan idea service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v23.services.services.keyword_plan_idea_service import (
    KeywordPlanIdeaServiceClient,
)
from google.ads.googleads.v23.services.types.keyword_plan_idea_service import (
    GenerateAdGroupThemesRequest,
    GenerateAdGroupThemesResponse,
    GenerateKeywordForecastMetricsRequest,
    GenerateKeywordForecastMetricsResponse,
    GenerateKeywordHistoricalMetricsRequest,
    GenerateKeywordHistoricalMetricsResponse,
    GenerateKeywordIdeasRequest,
    GenerateKeywordIdeaResult,
    CampaignToForecast,
    ForecastAdGroup,
    BiddableKeyword,
    KeywordAndUrlSeed,
    KeywordSeed,
    SiteSeed,
    UrlSeed,
)
from google.ads.googleads.v23.common.types.criteria import KeywordInfo
from google.ads.googleads.v23.enums.types.keyword_plan_network import (
    KeywordPlanNetworkEnum,
)
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import get_logger

logger = get_logger(__name__)


class KeywordPlanIdeaService:
    """Keyword plan idea service for keyword research and discovery."""

    def __init__(self) -> None:
        """Initialize the keyword plan idea service."""
        self._client: Optional[KeywordPlanIdeaServiceClient] = None

    @property
    def client(self) -> KeywordPlanIdeaServiceClient:
        """Get the keyword plan idea service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("KeywordPlanIdeaService")
        assert self._client is not None
        return self._client

    async def generate_keyword_ideas_from_keywords(
        self,
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: KeywordPlanNetworkEnum.KeywordPlanNetwork = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS,
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from seed keywords.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keywords: List of seed keywords
            language: Language constant resource name (e.g., "languageConstants/1000" for English)
            geo_target_constants: List of geo target constant resource names
            keyword_plan_network: Network type (UNSPECIFIED, GOOGLE_SEARCH, GOOGLE_SEARCH_AND_PARTNERS)
            include_adult_keywords: Whether to include adult keywords
            page_size: Number of results per page

        Returns:
            List of keyword ideas with metrics
        """
        try:
            # Create request
            request = GenerateKeywordIdeasRequest()
            request.customer_id = customer_id
            request.language = language
            request.geo_target_constants.extend(geo_target_constants)
            request.include_adult_keywords = include_adult_keywords
            request.page_size = page_size
            # Set keyword plan network using enum
            request.keyword_plan_network = keyword_plan_network

            # Create keyword seed
            keyword_seed = KeywordSeed()
            keyword_seed.keywords.extend(keywords)
            request.keyword_seed = keyword_seed

            # Generate ideas
            response = self.client.generate_keyword_ideas(request=request)

            # Process results
            keyword_ideas = []
            for idea in response:
                keyword_ideas.append(self._format_keyword_idea(idea))

            await ctx.log(
                level="info",
                message=f"Generated {len(keyword_ideas)} keyword ideas from {len(keywords)} seed keywords",
            )

            return keyword_ideas

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate keyword ideas: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_keyword_ideas_from_url(
        self,
        ctx: Context,
        customer_id: str,
        page_url: str,
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: KeywordPlanNetworkEnum.KeywordPlanNetwork = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS,
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from a URL.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            page_url: The URL to analyze
            language: Language constant resource name
            geo_target_constants: List of geo target constant resource names
            keyword_plan_network: Network type
            include_adult_keywords: Whether to include adult keywords
            page_size: Number of results per page

        Returns:
            List of keyword ideas with metrics
        """
        try:
            # Create request
            request = GenerateKeywordIdeasRequest()
            request.customer_id = customer_id
            request.language = language
            request.geo_target_constants.extend(geo_target_constants)
            request.include_adult_keywords = include_adult_keywords
            request.page_size = page_size
            # Set keyword plan network using enum
            request.keyword_plan_network = keyword_plan_network

            # Create URL seed
            url_seed = UrlSeed()
            url_seed.url = page_url
            request.url_seed = url_seed

            # Generate ideas
            response = self.client.generate_keyword_ideas(request=request)

            # Process results
            keyword_ideas = []
            for idea in response:
                keyword_ideas.append(self._format_keyword_idea(idea))

            await ctx.log(
                level="info",
                message=f"Generated {len(keyword_ideas)} keyword ideas from URL: {page_url}",
            )

            return keyword_ideas

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate keyword ideas from URL: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_keyword_ideas_from_site(
        self,
        ctx: Context,
        customer_id: str,
        site_url: str,
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: KeywordPlanNetworkEnum.KeywordPlanNetwork = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS,
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from an entire website.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            site_url: The website URL to analyze (domain only)
            language: Language constant resource name
            geo_target_constants: List of geo target constant resource names
            keyword_plan_network: Network type
            include_adult_keywords: Whether to include adult keywords
            page_size: Number of results per page

        Returns:
            List of keyword ideas with metrics
        """
        try:
            # Create request
            request = GenerateKeywordIdeasRequest()
            request.customer_id = customer_id
            request.language = language
            request.geo_target_constants.extend(geo_target_constants)
            request.include_adult_keywords = include_adult_keywords
            request.page_size = page_size
            # Set keyword plan network using enum
            request.keyword_plan_network = keyword_plan_network

            # Create site seed
            site_seed = SiteSeed()
            site_seed.site = site_url
            request.site_seed = site_seed

            # Generate ideas
            response = self.client.generate_keyword_ideas(request=request)

            # Process results
            keyword_ideas = []
            for idea in response:
                keyword_ideas.append(self._format_keyword_idea(idea))

            await ctx.log(
                level="info",
                message=f"Generated {len(keyword_ideas)} keyword ideas from site: {site_url}",
            )

            return keyword_ideas

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate keyword ideas from site: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_keyword_ideas_from_keywords_and_url(
        self,
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        page_url: str,
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: KeywordPlanNetworkEnum.KeywordPlanNetwork = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS,
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from both keywords and a URL.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keywords: List of seed keywords
            page_url: The URL to analyze
            language: Language constant resource name
            geo_target_constants: List of geo target constant resource names
            keyword_plan_network: Network type
            include_adult_keywords: Whether to include adult keywords
            page_size: Number of results per page

        Returns:
            List of keyword ideas with metrics
        """
        try:
            # Create request
            request = GenerateKeywordIdeasRequest()
            request.customer_id = customer_id
            request.language = language
            request.geo_target_constants.extend(geo_target_constants)
            request.include_adult_keywords = include_adult_keywords
            request.page_size = page_size
            # Set keyword plan network using enum
            request.keyword_plan_network = keyword_plan_network

            # Create keyword and URL seed
            keyword_and_url_seed = KeywordAndUrlSeed()
            keyword_and_url_seed.keywords.extend(keywords)
            keyword_and_url_seed.url = page_url
            request.keyword_and_url_seed = keyword_and_url_seed

            # Generate ideas
            response = self.client.generate_keyword_ideas(request=request)

            # Process results
            keyword_ideas = []
            for idea in response:
                keyword_ideas.append(self._format_keyword_idea(idea))

            await ctx.log(
                level="info",
                message=f"Generated {len(keyword_ideas)} keyword ideas from keywords and URL",
            )

            return keyword_ideas

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate keyword ideas: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_keyword_historical_metrics(
        self,
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        language: Optional[str] = None,
        geo_target_constants: Optional[List[str]] = None,
        keyword_plan_network: KeywordPlanNetworkEnum.KeywordPlanNetwork = KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS,
        include_adult_keywords: bool = False,
    ) -> Dict[str, Any]:
        """Generate historical metrics for a list of keywords.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keywords: List of keywords (up to 10,000; duplicates de-duped)
            language: Language constant resource name (optional)
            geo_target_constants: Geo target constant resource names (max 10, optional)
            keyword_plan_network: Network type
            include_adult_keywords: Whether to include adult keywords

        Returns:
            Historical metrics per keyword
        """
        try:
            from src.utils import format_customer_id, serialize_proto_message

            customer_id = format_customer_id(customer_id)

            request = GenerateKeywordHistoricalMetricsRequest()
            request.customer_id = customer_id
            request.keywords = keywords
            request.keyword_plan_network = keyword_plan_network
            request.include_adult_keywords = include_adult_keywords

            if language:
                request.language = language
            if geo_target_constants:
                request.geo_target_constants = geo_target_constants

            response: GenerateKeywordHistoricalMetricsResponse = (
                self.client.generate_keyword_historical_metrics(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate keyword historical metrics: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_ad_group_themes(
        self,
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        ad_groups: List[str],
    ) -> Dict[str, Any]:
        """Generate ad group themes by grouping keywords into existing ad groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keywords: List of keywords to group
            ad_groups: List of ad group resource names

        Returns:
            Keyword suggestions mapped to ad groups, plus unusable ad groups
        """
        try:
            from src.utils import format_customer_id, serialize_proto_message

            customer_id = format_customer_id(customer_id)

            request = GenerateAdGroupThemesRequest()
            request.customer_id = customer_id
            request.keywords = keywords
            request.ad_groups = ad_groups

            response: GenerateAdGroupThemesResponse = (
                self.client.generate_ad_group_themes(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate ad group themes: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_keyword_forecast_metrics(
        self,
        ctx: Context,
        customer_id: str,
        keyword_plan_network: str,
        biddable_keywords: List[Dict[str, Any]],
        bidding_strategy: Dict[str, Any],
        currency_code: Optional[str] = None,
        forecast_start_date: Optional[str] = None,
        forecast_end_date: Optional[str] = None,
        negative_keywords: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Generate forecast metrics for keywords.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keyword_plan_network: Network type (GOOGLE_SEARCH, GOOGLE_SEARCH_AND_PARTNERS)
            biddable_keywords: List of dicts with 'text', 'match_type', and optional 'max_cpc_bid_micros'
            bidding_strategy: Dict with 'type' (manual_cpc/maximize_clicks/maximize_conversions) and
                type-specific fields (daily_budget_micros, max_cpc_bid_micros, daily_target_spend_micros)
            currency_code: ISO 4217 currency code (optional)
            forecast_start_date: Start date YYYY-MM-DD (optional, defaults to next Sunday)
            forecast_end_date: End date YYYY-MM-DD (optional, defaults to next Saturday)
            negative_keywords: List of dicts with 'text' and 'match_type' (optional)

        Returns:
            Forecast metrics including impressions, clicks, cost, conversions
        """
        try:
            from google.ads.googleads.v23.enums.types.keyword_match_type import (
                KeywordMatchTypeEnum,
            )
            from src.utils import format_customer_id, serialize_proto_message

            customer_id = format_customer_id(customer_id)

            campaign = CampaignToForecast()
            campaign.keyword_plan_network = getattr(
                KeywordPlanNetworkEnum.KeywordPlanNetwork, keyword_plan_network
            )

            # Build bidding strategy
            strategy_type = bidding_strategy["type"]
            if strategy_type == "manual_cpc":
                campaign.manual_cpc_bidding_strategy.max_cpc_bid_micros = (
                    bidding_strategy["max_cpc_bid_micros"]
                )
                if "daily_budget_micros" in bidding_strategy:
                    campaign.manual_cpc_bidding_strategy.daily_budget_micros = (
                        bidding_strategy["daily_budget_micros"]
                    )
            elif strategy_type == "maximize_clicks":
                campaign.maximize_clicks_bidding_strategy.daily_target_spend_micros = (
                    bidding_strategy["daily_target_spend_micros"]
                )
                if "max_cpc_bid_ceiling_micros" in bidding_strategy:
                    campaign.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = bidding_strategy[
                        "max_cpc_bid_ceiling_micros"
                    ]
            elif strategy_type == "maximize_conversions":
                campaign.maximize_conversions_bidding_strategy.daily_target_spend_micros = bidding_strategy[
                    "daily_target_spend_micros"
                ]

            # Build ad group with biddable keywords
            ad_group = ForecastAdGroup()
            for kw_data in biddable_keywords:
                bk = BiddableKeyword()
                kw_info = KeywordInfo()
                kw_info.text = kw_data["text"]
                kw_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, kw_data["match_type"]
                )
                bk.keyword = kw_info
                if "max_cpc_bid_micros" in kw_data:
                    bk.max_cpc_bid_micros = kw_data["max_cpc_bid_micros"]
                ad_group.biddable_keywords.append(bk)

            if negative_keywords:
                for nk_data in negative_keywords:
                    nk = KeywordInfo()
                    nk.text = nk_data["text"]
                    nk.match_type = getattr(
                        KeywordMatchTypeEnum.KeywordMatchType, nk_data["match_type"]
                    )
                    ad_group.negative_keywords.append(nk)

            campaign.ad_groups.append(ad_group)

            request = GenerateKeywordForecastMetricsRequest()
            request.customer_id = customer_id
            request.campaign = campaign

            if currency_code:
                request.currency_code = currency_code
            if forecast_start_date and forecast_end_date:
                from google.ads.googleads.v23.common.types.dates import DateRange

                request.forecast_period = DateRange(
                    start_date=forecast_start_date,
                    end_date=forecast_end_date,
                )

            response: GenerateKeywordForecastMetricsResponse = (
                self.client.generate_keyword_forecast_metrics(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate keyword forecast metrics: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def _format_keyword_idea(self, idea: GenerateKeywordIdeaResult) -> Dict[str, Any]:
        """Format a keyword idea result into a dictionary."""
        result = {
            "text": idea.text,
            "keyword_idea_metrics": self._format_metrics(idea.keyword_idea_metrics)
            if idea.keyword_idea_metrics
            else None,
        }

        # Add keyword annotations if available
        if idea.keyword_annotations:
            result["keyword_annotations"] = {
                "concepts": [
                    {
                        "name": concept.name,
                        "concept_group": {
                            "name": concept.concept_group.name,
                            "type": concept.concept_group.type_.name
                            if concept.concept_group.type_
                            else None,
                        }
                        if concept.concept_group
                        else None,
                    }
                    for concept in idea.keyword_annotations.concepts
                ]
            }

        return result

    def _format_metrics(self, metrics: Any) -> Dict[str, Any]:
        """Format keyword metrics into a dictionary."""
        if not metrics:
            return {}

        return {
            "avg_monthly_searches": metrics.avg_monthly_searches,
            "monthly_search_volumes": [
                {
                    "year": volume.year,
                    "month": volume.month.name if volume.month else None,
                    "monthly_searches": volume.monthly_searches,
                }
                for volume in metrics.monthly_search_volumes
            ],
            "competition": metrics.competition.name if metrics.competition else None,
            "competition_index": metrics.competition_index,
            "low_top_of_page_bid_micros": metrics.low_top_of_page_bid_micros,
            "high_top_of_page_bid_micros": metrics.high_top_of_page_bid_micros,
        }


def create_keyword_plan_idea_tools(
    service: KeywordPlanIdeaService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the keyword plan idea service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def generate_keyword_ideas_from_keywords(
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: str = "GOOGLE_SEARCH_AND_PARTNERS",
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from seed keywords.

        Args:
            customer_id: The customer ID
            keywords: List of seed keywords to expand upon
            language: Language constant resource name (e.g., "languageConstants/1000" for English)
            geo_target_constants: List of geo target constant resource names (e.g., ["geoTargetConstants/2840"] for US)
            keyword_plan_network: Network type - UNSPECIFIED, GOOGLE_SEARCH, or GOOGLE_SEARCH_AND_PARTNERS
            include_adult_keywords: Whether to include adult keywords in results
            page_size: Number of results per page (max 10000)

        Returns:
            List of keyword ideas with:
            - text: The keyword text
            - keyword_idea_metrics: Metrics including avg_monthly_searches, competition, bid estimates
            - keyword_annotations: Conceptual categories for the keyword
        """
        # Convert string enum to proper enum type
        keyword_plan_network_enum = getattr(
            KeywordPlanNetworkEnum.KeywordPlanNetwork, keyword_plan_network
        )

        return await service.generate_keyword_ideas_from_keywords(
            ctx=ctx,
            customer_id=customer_id,
            keywords=keywords,
            language=language,
            geo_target_constants=geo_target_constants,
            keyword_plan_network=keyword_plan_network_enum,
            include_adult_keywords=include_adult_keywords,
            page_size=page_size,
        )

    async def generate_keyword_ideas_from_url(
        ctx: Context,
        customer_id: str,
        page_url: str,
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: str = "GOOGLE_SEARCH_AND_PARTNERS",
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from a specific URL/page.

        Args:
            customer_id: The customer ID
            page_url: The full URL of a specific page to analyze
            language: Language constant resource name (e.g., "languageConstants/1000" for English)
            geo_target_constants: List of geo target constant resource names
            keyword_plan_network: Network type - UNSPECIFIED, GOOGLE_SEARCH, or GOOGLE_SEARCH_AND_PARTNERS
            include_adult_keywords: Whether to include adult keywords in results
            page_size: Number of results per page (max 10000)

        Returns:
            List of keyword ideas with metrics and annotations
        """
        # Convert string enum to proper enum type
        keyword_plan_network_enum = getattr(
            KeywordPlanNetworkEnum.KeywordPlanNetwork, keyword_plan_network
        )

        return await service.generate_keyword_ideas_from_url(
            ctx=ctx,
            customer_id=customer_id,
            page_url=page_url,
            language=language,
            geo_target_constants=geo_target_constants,
            keyword_plan_network=keyword_plan_network_enum,
            include_adult_keywords=include_adult_keywords,
            page_size=page_size,
        )

    async def generate_keyword_ideas_from_site(
        ctx: Context,
        customer_id: str,
        site_url: str,
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: str = "GOOGLE_SEARCH_AND_PARTNERS",
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from an entire website.

        Args:
            customer_id: The customer ID
            site_url: The website domain to analyze (e.g., "example.com")
            language: Language constant resource name (e.g., "languageConstants/1000" for English)
            geo_target_constants: List of geo target constant resource names
            keyword_plan_network: Network type - UNSPECIFIED, GOOGLE_SEARCH, or GOOGLE_SEARCH_AND_PARTNERS
            include_adult_keywords: Whether to include adult keywords in results
            page_size: Number of results per page (max 10000)

        Returns:
            List of keyword ideas with metrics and annotations
        """
        # Convert string enum to proper enum type
        keyword_plan_network_enum = getattr(
            KeywordPlanNetworkEnum.KeywordPlanNetwork, keyword_plan_network
        )

        return await service.generate_keyword_ideas_from_site(
            ctx=ctx,
            customer_id=customer_id,
            site_url=site_url,
            language=language,
            geo_target_constants=geo_target_constants,
            keyword_plan_network=keyword_plan_network_enum,
            include_adult_keywords=include_adult_keywords,
            page_size=page_size,
        )

    async def generate_keyword_ideas_from_keywords_and_url(
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        page_url: str,
        language: str,
        geo_target_constants: List[str],
        keyword_plan_network: str = "GOOGLE_SEARCH_AND_PARTNERS",
        include_adult_keywords: bool = False,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate keyword ideas from both keywords and a URL.

        Args:
            customer_id: The customer ID
            keywords: List of seed keywords
            page_url: The URL to analyze in combination with keywords
            language: Language constant resource name (e.g., "languageConstants/1000" for English)
            geo_target_constants: List of geo target constant resource names
            keyword_plan_network: Network type - UNSPECIFIED, GOOGLE_SEARCH, or GOOGLE_SEARCH_AND_PARTNERS
            include_adult_keywords: Whether to include adult keywords in results
            page_size: Number of results per page (max 10000)

        Returns:
            List of keyword ideas with metrics and annotations
        """
        # Convert string enum to proper enum type
        keyword_plan_network_enum = getattr(
            KeywordPlanNetworkEnum.KeywordPlanNetwork, keyword_plan_network
        )

        return await service.generate_keyword_ideas_from_keywords_and_url(
            ctx=ctx,
            customer_id=customer_id,
            keywords=keywords,
            page_url=page_url,
            language=language,
            geo_target_constants=geo_target_constants,
            keyword_plan_network=keyword_plan_network_enum,
            include_adult_keywords=include_adult_keywords,
            page_size=page_size,
        )

    async def generate_keyword_historical_metrics(
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        language: Optional[str] = None,
        geo_target_constants: Optional[List[str]] = None,
        keyword_plan_network: str = "GOOGLE_SEARCH_AND_PARTNERS",
        include_adult_keywords: bool = False,
    ) -> Dict[str, Any]:
        """Generate historical metrics for a list of keywords.

        Args:
            customer_id: The customer ID
            keywords: List of keywords to get metrics for (up to 10,000)
            language: Language constant resource name (optional)
            geo_target_constants: Geo target constant resource names (max 10, optional)
            keyword_plan_network: Network type - GOOGLE_SEARCH or GOOGLE_SEARCH_AND_PARTNERS
            include_adult_keywords: Whether to include adult keywords

        Returns:
            Historical metrics per keyword including search volume, competition, bids
        """
        kw_network_enum = getattr(
            KeywordPlanNetworkEnum.KeywordPlanNetwork, keyword_plan_network
        )
        return await service.generate_keyword_historical_metrics(
            ctx=ctx,
            customer_id=customer_id,
            keywords=keywords,
            language=language,
            geo_target_constants=geo_target_constants,
            keyword_plan_network=kw_network_enum,
            include_adult_keywords=include_adult_keywords,
        )

    async def generate_ad_group_themes(
        ctx: Context,
        customer_id: str,
        keywords: List[str],
        ad_groups: List[str],
    ) -> Dict[str, Any]:
        """Generate ad group themes by grouping keywords into existing ad groups.

        Args:
            customer_id: The customer ID
            keywords: List of keywords to group
            ad_groups: List of ad group resource names (e.g. customers/{id}/adGroups/{id})

        Returns:
            Keyword suggestions mapped to ad groups, plus unusable ad groups
        """
        return await service.generate_ad_group_themes(
            ctx=ctx,
            customer_id=customer_id,
            keywords=keywords,
            ad_groups=ad_groups,
        )

    async def generate_keyword_forecast_metrics(
        ctx: Context,
        customer_id: str,
        keyword_plan_network: str,
        biddable_keywords: List[Dict[str, Any]],
        bidding_strategy: Dict[str, Any],
        currency_code: Optional[str] = None,
        forecast_start_date: Optional[str] = None,
        forecast_end_date: Optional[str] = None,
        negative_keywords: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Generate forecast metrics (impressions, clicks, cost) for keywords.

        Args:
            customer_id: The customer ID
            keyword_plan_network: GOOGLE_SEARCH or GOOGLE_SEARCH_AND_PARTNERS
            biddable_keywords: List of dicts with 'text', 'match_type' (EXACT/BROAD/PHRASE),
                and optional 'max_cpc_bid_micros'
            bidding_strategy: Dict with 'type' (manual_cpc/maximize_clicks/maximize_conversions)
                and type-specific fields:
                - manual_cpc: max_cpc_bid_micros (required), daily_budget_micros (optional)
                - maximize_clicks: daily_target_spend_micros (required), max_cpc_bid_ceiling_micros (optional)
                - maximize_conversions: daily_target_spend_micros (required)
            currency_code: ISO 4217 currency code (optional)
            forecast_start_date: Start date YYYY-MM-DD (optional)
            forecast_end_date: End date YYYY-MM-DD (optional)
            negative_keywords: List of dicts with 'text' and 'match_type' (optional)

        Returns:
            Forecast metrics including impressions, clicks, cost, conversions, CTR, CPC
        """
        return await service.generate_keyword_forecast_metrics(
            ctx=ctx,
            customer_id=customer_id,
            keyword_plan_network=keyword_plan_network,
            biddable_keywords=biddable_keywords,
            bidding_strategy=bidding_strategy,
            currency_code=currency_code,
            forecast_start_date=forecast_start_date,
            forecast_end_date=forecast_end_date,
            negative_keywords=negative_keywords,
        )

    tools.extend(
        [
            generate_keyword_ideas_from_keywords,
            generate_keyword_ideas_from_url,
            generate_keyword_ideas_from_site,
            generate_keyword_ideas_from_keywords_and_url,
            generate_keyword_historical_metrics,
            generate_ad_group_themes,
            generate_keyword_forecast_metrics,
        ]
    )
    return tools


def register_keyword_plan_idea_tools(mcp: FastMCP[Any]) -> KeywordPlanIdeaService:
    """Register keyword plan idea tools with the MCP server.

    Returns the KeywordPlanIdeaService instance for testing purposes.
    """
    service = KeywordPlanIdeaService()
    tools = create_keyword_plan_idea_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
