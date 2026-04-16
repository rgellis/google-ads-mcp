"""Audience insights service implementation using Google Ads SDK."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import Context, FastMCP
from google.ads.googleads.v23.services.services.audience_insights_service import (
    AudienceInsightsServiceClient,
)
from google.ads.googleads.v23.services.types.audience_insights_service import (
    GenerateAudienceCompositionInsightsRequest,
    GenerateAudienceCompositionInsightsResponse,
    GenerateAudienceDefinitionRequest,
    GenerateAudienceDefinitionResponse,
    GenerateAudienceOverlapInsightsRequest,
    GenerateAudienceOverlapInsightsResponse,
    GenerateInsightsFinderReportRequest,
    GenerateInsightsFinderReportResponse,
    GenerateSuggestedTargetingInsightsRequest,
    GenerateSuggestedTargetingInsightsResponse,
    GenerateTargetingSuggestionMetricsRequest,
    GenerateTargetingSuggestionMetricsResponse,
    InsightsAudienceDescription,
    ListAudienceInsightsAttributesRequest,
    ListAudienceInsightsAttributesResponse,
    ListInsightsEligibleDatesRequest,
    ListInsightsEligibleDatesResponse,
    InsightsAudience,
    InsightsAudienceAttributeGroup,
    InsightsAudienceDefinition,
)
from google.ads.googleads.v23.common.types.audience_insights_attribute import (
    AudienceInsightsAttribute,
)
from google.ads.googleads.v23.common.types.criteria import (
    AgeRangeInfo,
    GenderInfo,
    LocationInfo,
    UserInterestInfo,
)
from google.ads.googleads.v23.enums.types.audience_insights_dimension import (
    AudienceInsightsDimensionEnum,
)
from google.ads.googleads.v23.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v23.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.errors import GoogleAdsException

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AudienceInsightsService:
    """Audience insights service for analyzing audience data and getting recommendations."""

    def __init__(self) -> None:
        """Initialize the audience insights service."""
        self._client: Optional[AudienceInsightsServiceClient] = None

    @property
    def client(self) -> AudienceInsightsServiceClient:
        """Get the audience insights service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AudienceInsightsService")
        assert self._client is not None
        return self._client

    async def generate_insights_finder_report(
        self,
        ctx: Context,
        customer_id: str,
        baseline_audience_countries: List[str],
        specific_audience_countries: List[str],
        dimensions: List[str],
        baseline_audience_ages: Optional[List[str]] = None,
        baseline_audience_genders: Optional[List[str]] = None,
        specific_audience_ages: Optional[List[str]] = None,
        specific_audience_genders: Optional[List[str]] = None,
        specific_audience_user_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate insights finder report comparing two audiences.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            baseline_audience_countries: List of country location IDs for baseline audience
            specific_audience_countries: List of country location IDs for specific audience
            dimensions: List of dimensions to analyze (AGE_RANGE, GENDER, LOCATION, USER_INTEREST, etc.)
            baseline_audience_ages: Optional age ranges for baseline (AGE_RANGE_18_24, etc.)
            baseline_audience_genders: Optional genders for baseline (MALE, FEMALE, UNDETERMINED)
            specific_audience_ages: Optional age ranges for specific audience
            specific_audience_genders: Optional genders for specific audience
            specific_audience_user_interests: Optional user interest IDs for specific audience
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Insights report with audience comparisons
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create baseline audience
            baseline_audience = InsightsAudience()

            # Add countries
            for country_id in baseline_audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                baseline_audience.country_locations.append(location)

            # Add age ranges if provided
            if baseline_audience_ages:
                for age_range in baseline_audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    baseline_audience.age_ranges.append(age_info)

            # Add gender if provided
            if baseline_audience_genders and len(baseline_audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, baseline_audience_genders[0]
                )
                baseline_audience.gender = gender_info

            # Create specific audience
            specific_audience = InsightsAudience()

            # Add countries
            for country_id in specific_audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                specific_audience.country_locations.append(location)

            # Add age ranges if provided
            if specific_audience_ages:
                for age_range in specific_audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    specific_audience.age_ranges.append(age_info)

            # Add gender if provided
            if specific_audience_genders and len(specific_audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, specific_audience_genders[0]
                )
                specific_audience.gender = gender_info

            # Add user interests if provided (via topic_audience_combinations)
            if specific_audience_user_interests:
                attr_group = InsightsAudienceAttributeGroup()
                for interest_id in specific_audience_user_interests:
                    from google.ads.googleads.v23.common.types.audience_insights_attribute import (
                        AudienceInsightsAttribute as AudienceInsightsAttr,
                    )

                    attr = AudienceInsightsAttr()
                    interest_info = UserInterestInfo()
                    interest_info.user_interest_category = (
                        f"customers/{customer_id}/userInterests/{interest_id}"
                    )
                    attr.user_interest = interest_info
                    attr_group.attributes.append(attr)
                specific_audience.topic_audience_combinations.append(attr_group)

            # Create request
            request = GenerateInsightsFinderReportRequest()
            request.customer_id = customer_id
            request.baseline_audience = baseline_audience
            request.specific_audience = specific_audience
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

            # Make the API call
            response: GenerateInsightsFinderReportResponse = (
                self.client.generate_insights_finder_report(request=request)
            )

            await ctx.log(
                level="info",
                message="Generated insights finder report",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate insights finder report: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_audience_composition_insights(
        self,
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        dimensions: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
        audience_attribute_groups: Optional[List[Dict[str, Any]]] = None,
        customer_insights_group: Optional[str] = None,
        data_month: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate audience composition insights for a specific audience.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audience_countries: List of country location IDs
            dimensions: List of dimensions to analyze
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs
            audience_attribute_groups: Optional custom attribute groups
            customer_insights_group: Optional user-defined grouping label
            data_month: Optional specific month in YYYY-MM format

        Returns:
            Audience composition insights
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create audience
            audience = InsightsAudience()

            # Add countries
            for country_id in audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                audience.country_locations.append(location)

            # Add demographics and interests
            if audience_ages:
                for age_range in audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    audience.age_ranges.append(age_info)

            if audience_genders and len(audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, audience_genders[0]
                )
                audience.gender = gender_info

            # Add attribute groups if provided
            if audience_attribute_groups:
                for _ in (
                    audience_attribute_groups
                ):  # group_data will be used when fully implemented
                    attr_group = InsightsAudienceAttributeGroup()
                    # Process attributes based on group_data structure
                    # This is a simplified implementation
                    audience.topic_audience_combinations.append(attr_group)

            # Create request
            request = GenerateAudienceCompositionInsightsRequest()
            request.customer_id = customer_id
            request.audience = audience

            # Add dimensions
            for dimension in dimensions:
                request.dimensions.append(
                    getattr(
                        AudienceInsightsDimensionEnum.AudienceInsightsDimension,
                        dimension,
                    )
                )
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group
            if data_month:
                request.data_month = data_month

            # Make the API call
            response: GenerateAudienceCompositionInsightsResponse = (
                self.client.generate_audience_composition_insights(request=request)
            )

            await ctx.log(
                level="info",
                message="Generated audience composition insights",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate audience composition insights: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_suggested_targeting_insights(
        self,
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate suggested targeting insights for reaching similar audiences.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audience_countries: List of country location IDs
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Suggested targeting insights
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create audience
            audience = InsightsAudience()

            # Add countries
            for country_id in audience_countries:
                location = LocationInfo()
                location.geo_target_constant = f"geoTargetConstants/{country_id}"
                audience.country_locations.append(location)

            # Add demographics and interests
            if audience_ages:
                for age_range in audience_ages:
                    age_info = AgeRangeInfo()
                    age_info.type_ = getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
                    audience.age_ranges.append(age_info)

            if audience_genders and len(audience_genders) > 0:
                gender_info = GenderInfo()
                gender_info.type_ = getattr(
                    GenderTypeEnum.GenderType, audience_genders[0]
                )
                audience.gender = gender_info

            # Create audience definition
            audience_definition = InsightsAudienceDefinition()
            audience_definition.audience = audience

            # Create request
            request = GenerateSuggestedTargetingInsightsRequest()
            request.customer_id = customer_id
            request.audience_definition = audience_definition
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

            # Make the API call
            response: GenerateSuggestedTargetingInsightsResponse = (
                self.client.generate_suggested_targeting_insights(request=request)
            )

            await ctx.log(
                level="info",
                message="Generated suggested targeting insights",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate suggested targeting insights: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_audience_definition(
        self,
        ctx: Context,
        customer_id: str,
        audience_description: str,
        country_locations: List[str],
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an audience definition from a free-text description.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audience_description: Free-text description of the audience (max 2000 chars)
            country_locations: List of country geo target constant resource names
            customer_insights_group: Optional user-defined grouping label

        Returns:
            High and medium relevance attributes for the described audience
        """
        try:
            customer_id = format_customer_id(customer_id)

            description = InsightsAudienceDescription()
            description.audience_description = audience_description
            for country in country_locations:
                location = LocationInfo()
                location.geo_target_constant = country
                description.country_locations.append(location)

            request = GenerateAudienceDefinitionRequest()
            request.customer_id = customer_id
            request.audience_description = description
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

            response: GenerateAudienceDefinitionResponse = (
                self.client.generate_audience_definition(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate audience definition: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_audience_overlap_insights(
        self,
        ctx: Context,
        customer_id: str,
        country_location: str,
        primary_attribute_type: str,
        primary_attribute_value: str,
        dimensions: List[str],
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate audience overlap insights for a primary attribute.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            country_location: Country geo target constant resource name
            primary_attribute_type: Type of primary attribute - 'user_interest' or 'age_range' or 'gender'
            primary_attribute_value: Value - user interest resource name, age range, or gender
            dimensions: Dimensions to analyze overlap - AFFINITY_USER_INTEREST,
                IN_MARKET_USER_INTEREST, AGE_RANGE, GENDER
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Overlap insights with potential YouTube reach intersections
        """
        try:
            customer_id = format_customer_id(customer_id)

            country = LocationInfo()
            country.geo_target_constant = country_location

            primary_attr = AudienceInsightsAttribute()
            if primary_attribute_type == "user_interest":
                interest = UserInterestInfo()
                interest.user_interest_category = primary_attribute_value
                primary_attr.user_interest = interest
            elif primary_attribute_type == "age_range":
                age = AgeRangeInfo()
                age.type_ = getattr(
                    AgeRangeTypeEnum.AgeRangeType, primary_attribute_value
                )
                primary_attr.age_range = age
            elif primary_attribute_type == "gender":
                gender = GenderInfo()
                gender.type_ = getattr(
                    GenderTypeEnum.GenderType, primary_attribute_value
                )
                primary_attr.gender = gender

            dim_enums = [
                getattr(AudienceInsightsDimensionEnum.AudienceInsightsDimension, d)
                for d in dimensions
            ]

            request = GenerateAudienceOverlapInsightsRequest()
            request.customer_id = customer_id
            request.country_location = country
            request.primary_attribute = primary_attr
            request.dimensions = dim_enums
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

            response: GenerateAudienceOverlapInsightsResponse = (
                self.client.generate_audience_overlap_insights(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate audience overlap insights: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def generate_targeting_suggestion_metrics(
        self,
        ctx: Context,
        customer_id: str,
        audiences: List[Dict[str, Any]],
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate targeting suggestion metrics for audiences.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            audiences: List of audience dicts, each with:
                - country_locations: List of geo target constant resource names
                - age_ranges: Optional list of age range strings
                - gender: Optional gender string
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Targeting suggestion metrics per audience
        """
        try:
            customer_id = format_customer_id(customer_id)

            insights_audiences = []
            for aud_data in audiences:
                audience = InsightsAudience()
                for country in aud_data.get("country_locations", []):
                    location = LocationInfo()
                    location.geo_target_constant = country
                    audience.country_locations.append(location)
                if "age_ranges" in aud_data:
                    for age_range in aud_data["age_ranges"]:
                        age_info = AgeRangeInfo()
                        age_info.type_ = getattr(
                            AgeRangeTypeEnum.AgeRangeType, age_range
                        )
                        audience.age_ranges.append(age_info)
                if "gender" in aud_data:
                    gender_info = GenderInfo()
                    gender_info.type_ = getattr(
                        GenderTypeEnum.GenderType, aud_data["gender"]
                    )
                    audience.gender = gender_info
                insights_audiences.append(audience)

            request = GenerateTargetingSuggestionMetricsRequest()
            request.customer_id = customer_id
            request.audiences = insights_audiences
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

            response: GenerateTargetingSuggestionMetricsResponse = (
                self.client.generate_targeting_suggestion_metrics(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate targeting suggestion metrics: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_audience_insights_attributes(
        self,
        ctx: Context,
        customer_id: str,
        dimensions: List[str],
        query_text: str,
        customer_insights_group: Optional[str] = None,
        location_country_filters: Optional[List[str]] = None,
        youtube_reach_location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List audience insights attributes by searching.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            dimensions: Dimensions to search - CATEGORY, KNOWLEDGE_GRAPH, AFFINITY_USER_INTEREST,
                IN_MARKET_USER_INTEREST, AGE_RANGE, GENDER, etc.
            query_text: Free text search query
            customer_insights_group: Optional user-defined grouping label
            location_country_filters: Optional list of geo target constant resource names for location filtering
            youtube_reach_location: Optional geo target constant resource name for YouTube reach

        Returns:
            Matching audience insights attributes
        """
        try:
            customer_id = format_customer_id(customer_id)

            dim_enums = [
                getattr(AudienceInsightsDimensionEnum.AudienceInsightsDimension, d)
                for d in dimensions
            ]

            request = ListAudienceInsightsAttributesRequest()
            request.customer_id = customer_id
            request.dimensions = dim_enums
            request.query_text = query_text
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group
            if location_country_filters:
                for resource_name in location_country_filters:
                    location = LocationInfo()
                    location.geo_target_constant = resource_name
                    request.location_country_filters.append(location)
            if youtube_reach_location:
                location = LocationInfo()
                location.geo_target_constant = youtube_reach_location
                request.youtube_reach_location = location

            response: ListAudienceInsightsAttributesResponse = (
                self.client.list_audience_insights_attributes(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list audience insights attributes: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_insights_eligible_dates(
        self,
        ctx: Context,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List eligible date ranges for audience insights reports.

        Args:
            ctx: FastMCP context
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Available data months and last 30 days date range
        """
        try:
            request = ListInsightsEligibleDatesRequest()
            if customer_insights_group:
                request.customer_insights_group = customer_insights_group

            response: ListInsightsEligibleDatesResponse = (
                self.client.list_insights_eligible_dates(request=request)
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list insights eligible dates: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_audience_insights_tools(
    service: AudienceInsightsService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the audience insights service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def generate_insights_finder_report(
        ctx: Context,
        customer_id: str,
        baseline_audience_countries: List[str],
        specific_audience_countries: List[str],
        dimensions: List[str],
        baseline_audience_ages: Optional[List[str]] = None,
        baseline_audience_genders: Optional[List[str]] = None,
        specific_audience_ages: Optional[List[str]] = None,
        specific_audience_genders: Optional[List[str]] = None,
        specific_audience_user_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate insights finder report comparing baseline and specific audiences.

        Args:
            customer_id: The customer ID
            baseline_audience_countries: Country location IDs for baseline audience (e.g., ["2840"] for US)
            specific_audience_countries: Country location IDs for specific audience
            dimensions: Dimensions to analyze (AGE_RANGE, GENDER, LOCATION, USER_INTEREST, TOPIC, etc.)
            baseline_audience_ages: Age ranges (AGE_RANGE_18_24, AGE_RANGE_25_34, etc.)
            baseline_audience_genders: Genders (MALE, FEMALE, UNDETERMINED)
            specific_audience_ages: Age ranges for specific audience
            specific_audience_genders: Genders for specific audience
            specific_audience_user_interests: User interest IDs for specific audience
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Insights report with saved_report_url for downloading results
        """
        return await service.generate_insights_finder_report(
            ctx=ctx,
            customer_id=customer_id,
            baseline_audience_countries=baseline_audience_countries,
            specific_audience_countries=specific_audience_countries,
            dimensions=dimensions,
            baseline_audience_ages=baseline_audience_ages,
            baseline_audience_genders=baseline_audience_genders,
            specific_audience_ages=specific_audience_ages,
            specific_audience_genders=specific_audience_genders,
            specific_audience_user_interests=specific_audience_user_interests,
            customer_insights_group=customer_insights_group,
        )

    async def generate_audience_composition_insights(
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        dimensions: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
        audience_attribute_groups: Optional[List[Dict[str, Any]]] = None,
        customer_insights_group: Optional[str] = None,
        data_month: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate detailed composition insights for a specific audience.

        Args:
            customer_id: The customer ID
            audience_countries: Country location IDs (e.g., ["2840"] for US)
            dimensions: Dimensions to analyze (AGE_RANGE, GENDER, LOCATION, USER_INTEREST, etc.)
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs
            audience_attribute_groups: Optional custom attribute groups
            customer_insights_group: Optional user-defined grouping label
            data_month: Optional specific month in YYYY-MM format

        Returns:
            Detailed audience composition with affinity scores and demographic breakdowns
        """
        return await service.generate_audience_composition_insights(
            ctx=ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
            dimensions=dimensions,
            audience_ages=audience_ages,
            audience_genders=audience_genders,
            audience_user_interests=audience_user_interests,
            audience_attribute_groups=audience_attribute_groups,
            customer_insights_group=customer_insights_group,
            data_month=data_month,
        )

    async def generate_suggested_targeting_insights(
        ctx: Context,
        customer_id: str,
        audience_countries: List[str],
        audience_ages: Optional[List[str]] = None,
        audience_genders: Optional[List[str]] = None,
        audience_user_interests: Optional[List[str]] = None,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate targeting suggestions for reaching similar audiences.

        Args:
            customer_id: The customer ID
            audience_countries: Country location IDs (e.g., ["2840"] for US)
            audience_ages: Optional age ranges
            audience_genders: Optional genders
            audience_user_interests: Optional user interest IDs
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Suggested user interests and targeting options for similar audiences
        """
        return await service.generate_suggested_targeting_insights(
            ctx=ctx,
            customer_id=customer_id,
            audience_countries=audience_countries,
            audience_ages=audience_ages,
            audience_genders=audience_genders,
            audience_user_interests=audience_user_interests,
            customer_insights_group=customer_insights_group,
        )

    async def generate_audience_definition(
        ctx: Context,
        customer_id: str,
        audience_description: str,
        country_locations: List[str],
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an audience definition from a free-text description using AI.

        Args:
            customer_id: The customer ID
            audience_description: Free-text description of the audience (max 2000 chars)
            country_locations: List of country geo target constant resource names
                (e.g., ["geoTargetConstants/2840"] for US)
            customer_insights_group: Optional user-defined grouping label

        Returns:
            High and medium relevance attributes for the described audience
        """
        return await service.generate_audience_definition(
            ctx=ctx,
            customer_id=customer_id,
            audience_description=audience_description,
            country_locations=country_locations,
            customer_insights_group=customer_insights_group,
        )

    async def generate_audience_overlap_insights(
        ctx: Context,
        customer_id: str,
        country_location: str,
        primary_attribute_type: str,
        primary_attribute_value: str,
        dimensions: List[str],
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate audience overlap insights for a primary attribute.

        Args:
            customer_id: The customer ID
            country_location: Country geo target constant (e.g., "geoTargetConstants/2840")
            primary_attribute_type: Type - 'user_interest', 'age_range', or 'gender'
            primary_attribute_value: Resource name for user_interest, or enum name for age/gender
            dimensions: Dimensions to overlap - AFFINITY_USER_INTEREST,
                IN_MARKET_USER_INTEREST, AGE_RANGE, GENDER
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Overlap insights with potential YouTube reach intersections
        """
        return await service.generate_audience_overlap_insights(
            ctx=ctx,
            customer_id=customer_id,
            country_location=country_location,
            primary_attribute_type=primary_attribute_type,
            primary_attribute_value=primary_attribute_value,
            dimensions=dimensions,
            customer_insights_group=customer_insights_group,
        )

    async def generate_targeting_suggestion_metrics(
        ctx: Context,
        customer_id: str,
        audiences: List[Dict[str, Any]],
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate targeting suggestion metrics for audiences.

        Args:
            customer_id: The customer ID
            audiences: List of audience dicts, each with:
                - country_locations: List of geo target constant resource names
                - age_ranges: Optional list of age range strings
                - gender: Optional gender string (MALE, FEMALE)
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Targeting suggestion metrics per audience (one per input, in order)
        """
        return await service.generate_targeting_suggestion_metrics(
            ctx=ctx,
            customer_id=customer_id,
            audiences=audiences,
            customer_insights_group=customer_insights_group,
        )

    async def list_audience_insights_attributes(
        ctx: Context,
        customer_id: str,
        dimensions: List[str],
        query_text: str,
        customer_insights_group: Optional[str] = None,
        location_country_filters: Optional[List[str]] = None,
        youtube_reach_location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for audience insights attributes by text query.

        Args:
            customer_id: The customer ID
            dimensions: Dimensions to search - CATEGORY, KNOWLEDGE_GRAPH,
                AFFINITY_USER_INTEREST, IN_MARKET_USER_INTEREST, AGE_RANGE, GENDER,
                DEVICE, GEO_TARGET_COUNTRY, SUB_COUNTRY_LOCATION, YOUTUBE_LINEUP,
                LIFE_EVENT_USER_INTEREST, PARENTAL_STATUS, INCOME_RANGE
            query_text: Free text search query
            customer_insights_group: Optional user-defined grouping label
            location_country_filters: Optional list of geo target constant resource names for location filtering
            youtube_reach_location: Optional geo target constant resource name for YouTube reach

        Returns:
            Matching audience insights attributes with metadata
        """
        return await service.list_audience_insights_attributes(
            ctx=ctx,
            customer_id=customer_id,
            dimensions=dimensions,
            query_text=query_text,
            customer_insights_group=customer_insights_group,
            location_country_filters=location_country_filters,
            youtube_reach_location=youtube_reach_location,
        )

    async def list_insights_eligible_dates(
        ctx: Context,
        customer_insights_group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List eligible date ranges for audience insights reports.

        Args:
            customer_insights_group: Optional user-defined grouping label

        Returns:
            Available data months (YYYY-MM format) and last 30 days date range
        """
        return await service.list_insights_eligible_dates(
            ctx=ctx,
            customer_insights_group=customer_insights_group,
        )

    tools.extend(
        [
            generate_insights_finder_report,
            generate_audience_composition_insights,
            generate_suggested_targeting_insights,
            generate_audience_definition,
            generate_audience_overlap_insights,
            generate_targeting_suggestion_metrics,
            list_audience_insights_attributes,
            list_insights_eligible_dates,
        ]
    )
    return tools


def register_audience_insights_tools(
    mcp: FastMCP[Any],
) -> AudienceInsightsService:
    """Register audience insights tools with the MCP server.

    Returns the AudienceInsightsService instance for testing purposes.
    """
    service = AudienceInsightsService()
    tools = create_audience_insights_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
