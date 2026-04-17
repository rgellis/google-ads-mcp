"""Campaign criterion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.criteria import (
    AddressInfo,
    AdScheduleInfo,
    AgeRangeInfo,
    BrandListInfo,
    CarrierInfo,
    CombinedAudienceInfo,
    ContentLabelInfo,
    CustomAffinityInfo,
    CustomAudienceInfo,
    DeviceInfo,
    ExtendedDemographicInfo,
    GenderInfo,
    GeoPointInfo,
    IncomeRangeInfo,
    IpBlockInfo,
    KeywordInfo,
    KeywordThemeInfo,
    LanguageInfo,
    LifeEventInfo,
    ListingDimensionInfo,
    ListingScopeInfo,
    LocalServiceIdInfo,
    LocationGroupInfo,
    LocationInfo,
    MobileAppCategoryInfo,
    MobileApplicationInfo,
    MobileDeviceInfo,
    OperatingSystemVersionInfo,
    ParentalStatusInfo,
    PlacementInfo,
    ProximityInfo,
    TopicInfo,
    UserInterestInfo,
    UserListInfo,
    VideoLineupInfo,
    WebpageConditionInfo,
    WebpageInfo,
    YouTubeChannelInfo,
    YouTubeVideoInfo,
)
from google.ads.googleads.v23.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v23.enums.types.content_label_type import ContentLabelTypeEnum
from google.ads.googleads.v23.enums.types.day_of_week import DayOfWeekEnum
from google.ads.googleads.v23.enums.types.device import DeviceEnum
from google.ads.googleads.v23.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.v23.enums.types.income_range_type import IncomeRangeTypeEnum
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.enums.types.location_group_radius_units import (
    LocationGroupRadiusUnitsEnum,
)
from google.ads.googleads.v23.enums.types.minute_of_hour import MinuteOfHourEnum
from google.ads.googleads.v23.enums.types.parental_status_type import (
    ParentalStatusTypeEnum,
)
from google.ads.googleads.v23.enums.types.proximity_radius_units import (
    ProximityRadiusUnitsEnum,
)
from google.ads.googleads.v23.enums.types.webpage_condition_operand import (
    WebpageConditionOperandEnum,
)
from google.ads.googleads.v23.enums.types.webpage_condition_operator import (
    WebpageConditionOperatorEnum,
)
from google.ads.googleads.v23.resources.types.campaign_criterion import (
    CampaignCriterion,
)
from google.ads.googleads.v23.services.services.campaign_criterion_service import (
    CampaignCriterionServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_criterion_service import (
    CampaignCriterionOperation,
    MutateCampaignCriteriaRequest,
    MutateCampaignCriteriaResponse,
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


class CampaignCriterionService:
    """Campaign criterion service for managing campaign-level targeting."""

    def __init__(self) -> None:
        """Initialize the campaign criterion service."""
        self._client: Optional[CampaignCriterionServiceClient] = None

    @property
    def client(self) -> CampaignCriterionServiceClient:
        """Get the campaign criterion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignCriterionService")
        assert self._client is not None
        return self._client

    async def add_location_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        location_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add location targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            location_ids: List of geo target constant IDs
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for location_id in location_ids:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                # Create location info
                location_info = LocationInfo()
                location_info.geo_target_constant = f"geoTargetConstants/{location_id}"
                campaign_criterion.location = location_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} location criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add location criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_language_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        language_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add language targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            language_ids: List of language constant IDs

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for language_id in language_ids:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = (
                    False  # Language targeting can't be negative
                )

                # Create language info
                language_info = LanguageInfo()
                language_info.language_constant = f"languageConstants/{language_id}"
                campaign_criterion.language = language_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} language criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add language criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_device_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        device_types: List[DeviceEnum.Device],
        bid_modifiers: Optional[Dict[str, float]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add device targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            device_types: List of device type enum values
            bid_modifiers: Optional dict of device type to bid modifier

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for device_type in device_types:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = (
                    False  # Device targeting can't be negative
                )

                # Set bid modifier if provided
                device_type_str = device_type.name
                if bid_modifiers and device_type_str in bid_modifiers:
                    campaign_criterion.bid_modifier = bid_modifiers[device_type_str]

                # Create device info
                device_info = DeviceInfo()
                device_info.type_ = device_type
                campaign_criterion.device = device_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} device criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add device criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_negative_keyword_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        keywords: List[Dict[str, str]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add negative keyword criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            keywords: List of dicts with 'text' and 'match_type' keys

        Returns:
            List of created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            # Create operations
            operations = []
            for keyword in keywords:
                # Create campaign criterion
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = True  # Negative keywords

                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
                )
                campaign_criterion.keyword = keyword_info

                # Create operation
                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} negative keywords to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add negative keyword criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_ad_schedule_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        schedules: List[Dict[str, Any]],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add ad schedule (day/time) targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            schedules: List of schedule dicts with keys:
                day_of_week, start_hour, start_minute, end_hour, end_minute
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for schedule in schedules:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = False

                if bid_modifier is not None:
                    campaign_criterion.bid_modifier = bid_modifier

                ad_schedule_info = AdScheduleInfo()
                ad_schedule_info.day_of_week = getattr(
                    DayOfWeekEnum.DayOfWeek, schedule["day_of_week"]
                )
                ad_schedule_info.start_hour = schedule["start_hour"]
                ad_schedule_info.start_minute = getattr(
                    MinuteOfHourEnum.MinuteOfHour, schedule["start_minute"]
                )
                ad_schedule_info.end_hour = schedule["end_hour"]
                ad_schedule_info.end_minute = getattr(
                    MinuteOfHourEnum.MinuteOfHour, schedule["end_minute"]
                )
                campaign_criterion.ad_schedule = ad_schedule_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} ad schedule criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add ad schedule criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_audience_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        user_list_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add audience (user list) targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            user_list_resource_names: List of user list resource names
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for user_list_resource_name in user_list_resource_names:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                user_list_info = UserListInfo()
                user_list_info.user_list = user_list_resource_name
                campaign_criterion.user_list = user_list_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} audience criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add audience criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_age_range_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        age_ranges: List[AgeRangeTypeEnum.AgeRangeType],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add age range demographic targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            age_ranges: List of age range enum values
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for age_range in age_ranges:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = False

                if bid_modifier is not None:
                    campaign_criterion.bid_modifier = bid_modifier

                age_range_info = AgeRangeInfo()
                age_range_info.type_ = age_range
                campaign_criterion.age_range = age_range_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} age range criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add age range criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_gender_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        genders: List[GenderTypeEnum.GenderType],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add gender demographic targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            genders: List of gender enum values
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for gender in genders:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = False

                if bid_modifier is not None:
                    campaign_criterion.bid_modifier = bid_modifier

                gender_info = GenderInfo()
                gender_info.type_ = gender
                campaign_criterion.gender = gender_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} gender criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add gender criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_income_range_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        income_ranges: List[IncomeRangeTypeEnum.IncomeRangeType],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add income range demographic targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            income_ranges: List of income range enum values
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for income_range in income_ranges:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = False

                if bid_modifier is not None:
                    campaign_criterion.bid_modifier = bid_modifier

                income_range_info = IncomeRangeInfo()
                income_range_info.type_ = income_range
                campaign_criterion.income_range = income_range_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} income range criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add income range criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_proximity_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        latitude: float,
        longitude: float,
        radius: float,
        radius_units: ProximityRadiusUnitsEnum.ProximityRadiusUnits,
        address: Optional[str] = None,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add proximity (radius) targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius: Radius distance
            radius_units: Radius units enum value (MILES or KILOMETERS)
            address: Optional address string for display
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign_criterion = CampaignCriterion()
            campaign_criterion.campaign = campaign_resource
            campaign_criterion.negative = False

            if bid_modifier is not None:
                campaign_criterion.bid_modifier = bid_modifier

            geo_point_info = GeoPointInfo()
            geo_point_info.latitude_in_micro_degrees = int(latitude * 1_000_000)
            geo_point_info.longitude_in_micro_degrees = int(longitude * 1_000_000)

            proximity_info = ProximityInfo()
            proximity_info.geo_point = geo_point_info
            proximity_info.radius = radius
            proximity_info.radius_units = radius_units

            if address is not None:
                address_info = AddressInfo()
                address_info.street_address = address
                proximity_info.address = address_info

            campaign_criterion.proximity = proximity_info

            operation = CampaignCriterionOperation()
            operation.create = campaign_criterion

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added proximity criterion to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add proximity criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_parental_status_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        parental_statuses: List[ParentalStatusTypeEnum.ParentalStatusType],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add parental status demographic targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            parental_statuses: List of parental status enum values
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for parental_status in parental_statuses:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = False

                if bid_modifier is not None:
                    campaign_criterion.bid_modifier = bid_modifier

                parental_status_info = ParentalStatusInfo()
                parental_status_info.type_ = parental_status
                campaign_criterion.parental_status = parental_status_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} parental status criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add parental status criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_user_interest_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        user_interest_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add user interest (in-market/affinity) targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            user_interest_resource_names: List of user interest resource names
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in user_interest_resource_names:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                user_interest_info = UserInterestInfo()
                user_interest_info.user_interest_category = resource_name
                campaign_criterion.user_interest = user_interest_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} user interest criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add user interest criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_topic_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        topic_constant_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add topic targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            topic_constant_resource_names: List of topic constant resource names
                (e.g., ["topicConstants/123"])
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in topic_constant_resource_names:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                topic_info = TopicInfo()
                topic_info.topic_constant = resource_name
                campaign_criterion.topic = topic_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} topic criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add topic criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_placement_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        urls: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add placement (website/app) targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            urls: List of placement URLs
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for url in urls:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                placement_info = PlacementInfo()
                placement_info.url = url
                campaign_criterion.placement = placement_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} placement criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add placement criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_youtube_channel_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        channel_ids: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add YouTube channel targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            channel_ids: List of YouTube channel IDs
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for channel_id in channel_ids:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                youtube_channel_info = YouTubeChannelInfo()
                youtube_channel_info.channel_id = channel_id
                campaign_criterion.youtube_channel = youtube_channel_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} YouTube channel criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add YouTube channel criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_youtube_video_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        video_ids: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add YouTube video targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            video_ids: List of YouTube video IDs
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for video_id in video_ids:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                youtube_video_info = YouTubeVideoInfo()
                youtube_video_info.video_id = video_id
                campaign_criterion.youtube_video = youtube_video_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} YouTube video criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add YouTube video criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_content_label_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        content_label_types: List[ContentLabelTypeEnum.ContentLabelType],
        negative: bool = True,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add content label exclusion criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            content_label_types: List of content label type enum values
            negative: Whether these are negative criteria (default True)

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for content_label_type in content_label_types:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                content_label_info = ContentLabelInfo()
                content_label_info.type_ = content_label_type
                campaign_criterion.content_label = content_label_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} content label criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add content label criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_custom_audience_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        custom_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add custom audience targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            custom_audience_resource_names: List of custom audience resource names
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in custom_audience_resource_names:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                custom_audience_info = CustomAudienceInfo()
                custom_audience_info.custom_audience = resource_name
                campaign_criterion.custom_audience = custom_audience_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} custom audience criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add custom audience criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_custom_affinity_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        custom_affinity_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add custom affinity audience targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            custom_affinity_resource_names: List of custom affinity resource names
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in custom_affinity_resource_names:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                custom_affinity_info = CustomAffinityInfo()
                custom_affinity_info.custom_affinity = resource_name
                campaign_criterion.custom_affinity = custom_affinity_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} custom affinity criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add custom affinity criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_combined_audience_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        combined_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add combined audience targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            combined_audience_resource_names: List of combined audience resource names
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in combined_audience_resource_names:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                combined_audience_info = CombinedAudienceInfo()
                combined_audience_info.combined_audience = resource_name
                campaign_criterion.combined_audience = combined_audience_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} combined audience criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add combined audience criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_life_event_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        life_event_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add life event targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            life_event_resource_names: List of life event resource names
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in life_event_resource_names:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                life_event_info = LifeEventInfo()
                life_event_info.life_event_id = resource_name
                campaign_criterion.life_event = life_event_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} life event criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add life event criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_keyword_theme_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        keyword_theme_constants: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add keyword theme criteria to a smart campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            keyword_theme_constants: List of keyword theme constant resource names

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for constant in keyword_theme_constants:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = False

                keyword_theme_info = KeywordThemeInfo()
                keyword_theme_info.keyword_theme_constant = constant
                campaign_criterion.keyword_theme = keyword_theme_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} keyword theme criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add keyword theme criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_ip_block_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        ip_addresses: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add IP address exclusion criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            ip_addresses: List of IP addresses to exclude

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for ip_addr in ip_addresses:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = True  # IP blocks are always exclusions

                ip_block_info = IpBlockInfo()
                ip_block_info.ip_address = ip_addr
                campaign_criterion.ip_block = ip_block_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} IP block criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add IP block criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_carrier_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        carrier_constants: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add mobile carrier targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            carrier_constants: List of carrier constant resource names
                (e.g., "carrierConstants/123")
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in carrier_constants:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                carrier_info = CarrierInfo()
                carrier_info.carrier_constant = resource_name
                campaign_criterion.carrier = carrier_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} carrier criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add carrier criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_mobile_app_category_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        mobile_app_category_constants: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add mobile app category targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            mobile_app_category_constants: List of mobile app category constant
                resource names (e.g., "mobileAppCategoryConstants/123")
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in mobile_app_category_constants:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                mobile_app_category_info = MobileAppCategoryInfo()
                mobile_app_category_info.mobile_app_category_constant = resource_name
                campaign_criterion.mobile_app_category = mobile_app_category_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} mobile app category criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add mobile app category criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_mobile_application_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        app_ids: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add specific mobile application targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            app_ids: List of mobile application IDs (e.g., "1-123456789" for
                Android or "1-com.example.app" format)
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for app_id in app_ids:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                mobile_application_info = MobileApplicationInfo()
                mobile_application_info.app_id = app_id
                campaign_criterion.mobile_application = mobile_application_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} mobile application criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add mobile application criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_mobile_device_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        mobile_device_constants: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add mobile device model targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            mobile_device_constants: List of mobile device constant resource names
                (e.g., "mobileDeviceConstants/123")
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in mobile_device_constants:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                mobile_device_info = MobileDeviceInfo()
                mobile_device_info.mobile_device_constant = resource_name
                campaign_criterion.mobile_device = mobile_device_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} mobile device criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add mobile device criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_operating_system_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        os_version_constants: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add operating system version targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            os_version_constants: List of operating system version constant
                resource names (e.g., "operatingSystemVersionConstants/123")
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for resource_name in os_version_constants:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                os_version_info = OperatingSystemVersionInfo()
                os_version_info.operating_system_version_constant = resource_name
                campaign_criterion.operating_system_version = os_version_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} OS version criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add operating system criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_location_group_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        geo_target_constants: Optional[List[str]] = None,
        radius: Optional[int] = None,
        radius_units: Optional[str] = None,
        feed_item_sets: Optional[List[str]] = None,
        location_group_asset_sets: Optional[List[str]] = None,
        enable_customer_level_location_asset_set: Optional[bool] = None,
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add location group targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            geo_target_constants: List of geo target constant resource names
            radius: Radius distance for the location group
            radius_units: Radius units. Valid values: METERS, MILES, MILLI_MILES
            feed_item_sets: List of feed item set resource names
            location_group_asset_sets: List of location group asset set resource names
            enable_customer_level_location_asset_set: Whether to enable customer
                level location asset set
            negative: Whether this is a negative criterion

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign_criterion = CampaignCriterion()
            campaign_criterion.campaign = campaign_resource
            campaign_criterion.negative = negative

            location_group_info = LocationGroupInfo()

            if geo_target_constants is not None:
                location_group_info.geo_target_constants = geo_target_constants

            if radius is not None:
                location_group_info.radius = radius

            if radius_units is not None:
                location_group_info.radius_units = getattr(
                    LocationGroupRadiusUnitsEnum.LocationGroupRadiusUnits,
                    radius_units,
                )

            if feed_item_sets is not None:
                location_group_info.feed_item_sets = feed_item_sets

            if location_group_asset_sets is not None:
                location_group_info.location_group_asset_sets = (
                    location_group_asset_sets
                )

            if enable_customer_level_location_asset_set is not None:
                location_group_info.enable_customer_level_location_asset_set = (
                    enable_customer_level_location_asset_set
                )

            campaign_criterion.location_group = location_group_info

            operation = CampaignCriterionOperation()
            operation.create = campaign_criterion

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added location group criterion to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add location group criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_listing_scope_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        dimensions: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add listing scope criteria to a campaign (Shopping/PMax product filters).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            dimensions: List of dimension dicts. Each dict should have a 'type'
                key indicating the dimension type (e.g., 'product_brand',
                'product_channel', 'product_item_id', 'product_type',
                'product_condition', 'product_custom_attribute', 'product_category')
                and a 'value' dict with the fields for that dimension type.
                Example: [
                    {"type": "product_brand", "value": {"value": "Nike"}},
                    {"type": "product_item_id", "value": {"value": "SKU123"}}
                ]

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign_criterion = CampaignCriterion()
            campaign_criterion.campaign = campaign_resource

            listing_scope_info = ListingScopeInfo()

            for dim_dict in dimensions:
                dim_type = dim_dict["type"]
                dim_value = dim_dict.get("value", {})
                listing_dimension = ListingDimensionInfo()
                # Set the appropriate oneof field on the dimension
                dim_obj = getattr(listing_dimension, dim_type)
                for field_name, field_value in dim_value.items():
                    setattr(dim_obj, field_name, field_value)
                setattr(listing_dimension, dim_type, dim_obj)
                listing_scope_info.dimensions.append(listing_dimension)

            campaign_criterion.listing_scope = listing_scope_info

            operation = CampaignCriterionOperation()
            operation.create = campaign_criterion

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added listing scope criterion to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add listing scope criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_webpage_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        criterion_name: str,
        conditions: List[Dict[str, str]],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add webpage targeting criteria to a campaign (for DSA campaigns).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            criterion_name: A name for this webpage criterion
            conditions: List of condition dicts, each with keys:
                - operand: The operand type. Valid values: URL, CATEGORY,
                    PAGE_TITLE, PAGE_CONTENT, CUSTOM_LABEL
                - argument: The argument string to match
                - operator: Optional operator. Valid values: EQUALS, CONTAINS
                    (defaults to CONTAINS if not specified)
            negative: Whether this is a negative criterion

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign_criterion = CampaignCriterion()
            campaign_criterion.campaign = campaign_resource
            campaign_criterion.negative = negative

            webpage_info = WebpageInfo()
            webpage_info.criterion_name = criterion_name

            for cond_dict in conditions:
                condition = WebpageConditionInfo()
                condition.operand = getattr(
                    WebpageConditionOperandEnum.WebpageConditionOperand,
                    cond_dict["operand"],
                )
                condition.argument = cond_dict["argument"]
                if "operator" in cond_dict:
                    condition.operator = getattr(
                        WebpageConditionOperatorEnum.WebpageConditionOperator,
                        cond_dict["operator"],
                    )
                webpage_info.conditions.append(condition)

            campaign_criterion.webpage = webpage_info

            operation = CampaignCriterionOperation()
            operation.create = campaign_criterion

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added webpage criterion to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add webpage criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_brand_list_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add brand list targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_resource_name: Resource name of the shared set containing
                the brand list (e.g., "customers/123/sharedSets/456")

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign_criterion = CampaignCriterion()
            campaign_criterion.campaign = campaign_resource

            brand_list_info = BrandListInfo()
            brand_list_info.shared_set = shared_set_resource_name
            campaign_criterion.brand_list = brand_list_info

            operation = CampaignCriterionOperation()
            operation.create = campaign_criterion

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added brand list criterion to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add brand list criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_local_service_id_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        service_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add local service ID targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            service_id: The local service ID string

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign_criterion = CampaignCriterion()
            campaign_criterion.campaign = campaign_resource

            local_service_id_info = LocalServiceIdInfo()
            local_service_id_info.service_id = service_id
            campaign_criterion.local_service_id = local_service_id_info

            operation = CampaignCriterionOperation()
            operation.create = campaign_criterion

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added local service ID criterion to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add local service ID criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_webpage_list_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        criterion_name: str,
        conditions: List[Dict[str, str]],
        negative: bool = True,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add webpage list targeting criteria to a campaign.

        This is similar to webpage criteria but intended for predefined URL
        sets, typically used as negative criteria to exclude specific pages.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            criterion_name: A name for this webpage list criterion
            conditions: List of condition dicts, each with keys:
                - operand: The operand type. Valid values: URL, CATEGORY,
                    PAGE_TITLE, PAGE_CONTENT, CUSTOM_LABEL
                - argument: The argument string to match
                - operator: Optional operator. Valid values: EQUALS, CONTAINS
            negative: Whether this is a negative criterion (default True)

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            campaign_criterion = CampaignCriterion()
            campaign_criterion.campaign = campaign_resource
            campaign_criterion.negative = negative

            webpage_info = WebpageInfo()
            webpage_info.criterion_name = criterion_name

            for cond_dict in conditions:
                condition = WebpageConditionInfo()
                condition.operand = getattr(
                    WebpageConditionOperandEnum.WebpageConditionOperand,
                    cond_dict["operand"],
                )
                condition.argument = cond_dict["argument"]
                if "operator" in cond_dict:
                    condition.operator = getattr(
                        WebpageConditionOperatorEnum.WebpageConditionOperator,
                        cond_dict["operator"],
                    )
                webpage_info.conditions.append(condition)

            campaign_criterion.webpage = webpage_info

            operation = CampaignCriterionOperation()
            operation.create = campaign_criterion

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added webpage list criterion to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add webpage list criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_video_lineup_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        video_lineup_ids: List[int],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add YouTube video lineup targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            video_lineup_ids: List of video lineup IDs
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for lineup_id in video_lineup_ids:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                video_lineup_info = VideoLineupInfo()
                video_lineup_info.video_lineup_id = lineup_id
                campaign_criterion.video_lineup = video_lineup_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} video lineup criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add video lineup criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_extended_demographic_criteria(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        extended_demographic_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add extended demographic targeting criteria to a campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            extended_demographic_ids: List of extended demographic IDs
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            campaign_resource = f"customers/{customer_id}/campaigns/{campaign_id}"

            operations = []
            for demographic_id in extended_demographic_ids:
                campaign_criterion = CampaignCriterion()
                campaign_criterion.campaign = campaign_resource
                campaign_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    campaign_criterion.bid_modifier = bid_modifier

                extended_demographic_info = ExtendedDemographicInfo()
                extended_demographic_info.extended_demographic_id = demographic_id
                campaign_criterion.extended_demographic = extended_demographic_info

                operation = CampaignCriterionOperation()
                operation.create = campaign_criterion
                operations.append(operation)

            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} extended demographic criteria to campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add extended demographic criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_campaign_criterion(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        criterion_id: str,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update a campaign criterion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: The campaign ID
            criterion_id: The criterion ID to update
            bid_modifier: New bid modifier (e.g., 1.2 for +20%, 0.8 for -20%)

        Returns:
            Updated campaign criterion details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/campaignCriteria/{campaign_id}~{criterion_id}"
            )

            campaign_criterion = CampaignCriterion()
            campaign_criterion.resource_name = resource_name

            update_mask_fields: List[str] = []

            if bid_modifier is not None:
                campaign_criterion.bid_modifier = bid_modifier
                update_mask_fields.append("bid_modifier")

            if not update_mask_fields:
                raise ValueError("At least one field must be provided for update")

            # Create operation
            operation = CampaignCriterionOperation()
            operation.update = campaign_criterion
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Updated campaign criterion {criterion_id} on campaign {campaign_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update campaign criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_campaign_criterion(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a campaign criterion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            criterion_resource_name: The resource name of the criterion to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = CampaignCriterionOperation()
            operation.remove = criterion_resource_name

            # Create request
            request = MutateCampaignCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCampaignCriteriaResponse = (
                self.client.mutate_campaign_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed campaign criterion: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove campaign criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_criterion_tools(
    service: CampaignCriterionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign criterion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def add_location_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        location_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add location targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            location_ids: List of geo target constant IDs (e.g., ["1014044"] for California)
            negative: Whether these are negative criteria (exclude locations)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%, 0.8 for -20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_location_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            location_ids=location_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_language_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        language_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add language targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            language_ids: List of language constant IDs (e.g., ["1000"] for English)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_language_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            language_ids=language_ids,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_device_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        device_types: List[str],
        bid_modifiers: Optional[Dict[str, float]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add device targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            device_types: List of device types - MOBILE, DESKTOP, TABLET
            bid_modifiers: Optional dict of device type to bid modifier
                Example: {"MOBILE": 1.2, "DESKTOP": 0.9}

        Returns:
            Mutation response with created campaign criteria
        """
        # Convert string enums to proper enum types
        device_type_enums = [
            getattr(DeviceEnum.Device, device_type) for device_type in device_types
        ]

        return await service.add_device_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            device_types=device_type_enums,
            bid_modifiers=bid_modifiers,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_negative_keyword_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        keywords: List[Dict[str, str]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add negative keyword criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            keywords: List of keyword dicts with 'text' and 'match_type' keys
                Example: [
                    {"text": "free", "match_type": "BROAD"},
                    {"text": "[cheap]", "match_type": "EXACT"}
                ]

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_negative_keyword_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            keywords=keywords,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_ad_schedule_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        schedules: List[Dict[str, Any]],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add ad schedule (day/time) targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            schedules: List of schedule dicts, each with keys:
                - day_of_week: Day of week. Valid values: MONDAY, TUESDAY, WEDNESDAY,
                    THURSDAY, FRIDAY, SATURDAY, SUNDAY
                - start_hour: Start hour (0-23)
                - start_minute: Start minute. Valid values: ZERO, FIFTEEN, THIRTY, FORTY_FIVE
                - end_hour: End hour (0-24)
                - end_minute: End minute. Valid values: ZERO, FIFTEEN, THIRTY, FORTY_FIVE
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_ad_schedule_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            schedules=schedules,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_audience_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        user_list_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add audience (user list / RLSA) targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            user_list_resource_names: List of user list resource names
                (e.g., ["customers/123/userLists/456"])
            negative: Whether these are negative criteria (exclude audiences)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_audience_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            user_list_resource_names=user_list_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_age_range_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        age_ranges: List[str],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add age range demographic targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            age_ranges: List of age range values. Valid values:
                AGE_RANGE_18_24, AGE_RANGE_25_34, AGE_RANGE_35_44,
                AGE_RANGE_45_54, AGE_RANGE_55_64, AGE_RANGE_65_UP,
                AGE_RANGE_UNDETERMINED
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        age_range_enums = [
            getattr(AgeRangeTypeEnum.AgeRangeType, age_range)
            for age_range in age_ranges
        ]

        return await service.add_age_range_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            age_ranges=age_range_enums,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_gender_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        genders: List[str],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add gender demographic targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            genders: List of gender values. Valid values: MALE, FEMALE, UNDETERMINED
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        gender_enums = [
            getattr(GenderTypeEnum.GenderType, gender) for gender in genders
        ]

        return await service.add_gender_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            genders=gender_enums,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_income_range_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        income_ranges: List[str],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add income range demographic targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            income_ranges: List of income range values. Valid values:
                INCOME_RANGE_0_50, INCOME_RANGE_50_60, INCOME_RANGE_60_70,
                INCOME_RANGE_70_80, INCOME_RANGE_80_90, INCOME_RANGE_90_100,
                INCOME_RANGE_UNDETERMINED
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        income_range_enums = [
            getattr(IncomeRangeTypeEnum.IncomeRangeType, income_range)
            for income_range in income_ranges
        ]

        return await service.add_income_range_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            income_ranges=income_range_enums,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_proximity_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        latitude: float,
        longitude: float,
        radius: float,
        radius_units: str = "MILES",
        address: Optional[str] = None,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add proximity (radius) targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius: Radius distance
            radius_units: Radius units. Valid values: MILES, KILOMETERS
            address: Optional address string for display purposes
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        radius_units_enum = getattr(
            ProximityRadiusUnitsEnum.ProximityRadiusUnits, radius_units
        )

        return await service.add_proximity_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            radius_units=radius_units_enum,
            address=address,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_parental_status_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        parental_statuses: List[str],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add parental status demographic targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            parental_statuses: List of parental status values. Valid values:
                PARENT, NOT_A_PARENT, UNDETERMINED
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        parental_status_enums = [
            getattr(ParentalStatusTypeEnum.ParentalStatusType, ps)
            for ps in parental_statuses
        ]

        return await service.add_parental_status_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            parental_statuses=parental_status_enums,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_user_interest_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        user_interest_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add user interest (in-market/affinity audience) targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            user_interest_resource_names: List of user interest resource names
                (e.g., ["customers/123/userInterests/456"])
            negative: Whether these are negative criteria (exclude interests)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_user_interest_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            user_interest_resource_names=user_interest_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_topic_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        topic_constant_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add topic targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            topic_constant_resource_names: List of topic constant resource names
                (e.g., ["topicConstants/123"])
            negative: Whether these are negative criteria (exclude topics)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_topic_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            topic_constant_resource_names=topic_constant_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_placement_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        urls: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add placement (website/app) targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            urls: List of placement URLs (e.g., ["example.com", "youtube.com"])
            negative: Whether these are negative criteria (exclude placements)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_placement_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            urls=urls,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_youtube_channel_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        channel_ids: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add YouTube channel targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            channel_ids: List of YouTube channel IDs (e.g., ["UCxxxxxx"])
            negative: Whether these are negative criteria (exclude channels)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_youtube_channel_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            channel_ids=channel_ids,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_youtube_video_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        video_ids: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add YouTube video targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            video_ids: List of YouTube video IDs (e.g., ["dQw4w9WgXcQ"])
            negative: Whether these are negative criteria (exclude videos)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_youtube_video_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            video_ids=video_ids,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_content_label_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        content_label_types: List[str],
        negative: bool = True,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add content label exclusion criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            content_label_types: List of content label types. Valid values:
                SEXUALLY_SUGGESTIVE, BELOW_THE_FOLD, PARKED_DOMAIN, JUVENILE,
                PROFANITY, TRAGEDY, VIDEO, VIDEO_RATING_DV_G, VIDEO_RATING_DV_PG,
                VIDEO_RATING_DV_T, VIDEO_RATING_DV_MA, VIDEO_NOT_YET_RATED,
                EMBEDDED_VIDEO, LIVE_STREAMING_VIDEO, SOCIAL_ISSUES
            negative: Whether these are negative criteria (default True for exclusions)

        Returns:
            Mutation response with created campaign criteria
        """
        content_label_enums = [
            getattr(ContentLabelTypeEnum.ContentLabelType, cl)
            for cl in content_label_types
        ]

        return await service.add_content_label_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            content_label_types=content_label_enums,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_custom_audience_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        custom_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add custom audience targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            custom_audience_resource_names: List of custom audience resource names
                (e.g., ["customers/123/customAudiences/456"])
            negative: Whether these are negative criteria (exclude audiences)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_custom_audience_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            custom_audience_resource_names=custom_audience_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_custom_affinity_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        custom_affinity_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add custom affinity audience targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            custom_affinity_resource_names: List of custom affinity resource names
                (e.g., ["customers/123/customAffinities/456"])
            negative: Whether these are negative criteria (exclude affinities)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_custom_affinity_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            custom_affinity_resource_names=custom_affinity_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_combined_audience_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        combined_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add combined audience targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            combined_audience_resource_names: List of combined audience resource names
                (e.g., ["customers/123/combinedAudiences/456"])
            negative: Whether these are negative criteria (exclude audiences)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_combined_audience_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            combined_audience_resource_names=combined_audience_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_life_event_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        life_event_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add life event targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            life_event_resource_names: List of life event resource names
                (e.g., ["customers/123/lifeEvents/456"])
            negative: Whether these are negative criteria (exclude life events)
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_life_event_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            life_event_resource_names=life_event_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_keyword_theme_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        keyword_theme_constants: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add keyword theme criteria to a smart campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            keyword_theme_constants: List of keyword theme constant resource names
                (e.g., ["keywordThemeConstants/123~456"])

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_keyword_theme_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            keyword_theme_constants=keyword_theme_constants,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_ip_block_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        ip_addresses: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add IP address exclusion criteria to a campaign.

        IP blocks are always negative (exclusion) criteria.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            ip_addresses: List of IP addresses to exclude (e.g., ["192.168.1.0/24"])

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_ip_block_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            ip_addresses=ip_addresses,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_carrier_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        carrier_constants: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add mobile carrier targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            carrier_constants: List of carrier constant resource names
                (e.g., "carrierConstants/123")
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_carrier_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            carrier_constants=carrier_constants,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_mobile_app_category_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        mobile_app_category_constants: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add mobile app category targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            mobile_app_category_constants: List of mobile app category constant
                resource names (e.g., "mobileAppCategoryConstants/123")
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_mobile_app_category_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            mobile_app_category_constants=mobile_app_category_constants,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_mobile_application_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        app_ids: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add specific mobile application targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            app_ids: List of mobile application IDs
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_mobile_application_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            app_ids=app_ids,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_mobile_device_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        mobile_device_constants: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add mobile device model targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            mobile_device_constants: List of mobile device constant resource names
                (e.g., "mobileDeviceConstants/123")
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_mobile_device_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            mobile_device_constants=mobile_device_constants,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_operating_system_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        os_version_constants: List[str],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add operating system version targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            os_version_constants: List of OS version constant resource names
                (e.g., "operatingSystemVersionConstants/123")
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_operating_system_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            os_version_constants=os_version_constants,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_location_group_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        geo_target_constants: Optional[List[str]] = None,
        radius: Optional[int] = None,
        radius_units: Optional[str] = None,
        feed_item_sets: Optional[List[str]] = None,
        location_group_asset_sets: Optional[List[str]] = None,
        enable_customer_level_location_asset_set: Optional[bool] = None,
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add location group targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            geo_target_constants: List of geo target constant resource names
            radius: Radius distance for the location group
            radius_units: Radius units. Valid values: METERS, MILES, MILLI_MILES
            feed_item_sets: List of feed item set resource names
            location_group_asset_sets: List of location group asset set resource names
            enable_customer_level_location_asset_set: Whether to enable customer
                level location asset set
            negative: Whether this is a negative criterion

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_location_group_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            geo_target_constants=geo_target_constants,
            radius=radius,
            radius_units=radius_units,
            feed_item_sets=feed_item_sets,
            location_group_asset_sets=location_group_asset_sets,
            enable_customer_level_location_asset_set=enable_customer_level_location_asset_set,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_listing_scope_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        dimensions: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add listing scope criteria to a campaign (Shopping/PMax product filters).

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            dimensions: List of dimension dicts. Each dict should have a 'type'
                key (e.g., 'product_brand', 'product_item_id', 'product_type')
                and a 'value' dict with the fields for that dimension type.
                Example: [
                    {"type": "product_brand", "value": {"value": "Nike"}},
                    {"type": "product_item_id", "value": {"value": "SKU123"}}
                ]

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_listing_scope_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            dimensions=dimensions,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_webpage_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        criterion_name: str,
        conditions: List[Dict[str, str]],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add webpage targeting criteria to a campaign (for DSA campaigns).

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            criterion_name: A name for this webpage criterion
            conditions: List of condition dicts, each with keys:
                - operand: Valid values: URL, CATEGORY, PAGE_TITLE, PAGE_CONTENT, CUSTOM_LABEL
                - argument: The argument string to match
                - operator: Optional. Valid values: EQUALS, CONTAINS
            negative: Whether this is a negative criterion

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_webpage_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            criterion_name=criterion_name,
            conditions=conditions,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_brand_list_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add brand list targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            shared_set_resource_name: Resource name of the shared set containing
                the brand list (e.g., "customers/123/sharedSets/456")

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_brand_list_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            shared_set_resource_name=shared_set_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_local_service_id_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        service_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add local service ID targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            service_id: The local service ID string

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_local_service_id_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            service_id=service_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_webpage_list_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        criterion_name: str,
        conditions: List[Dict[str, str]],
        negative: bool = True,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add webpage list targeting criteria to a campaign.

        Similar to webpage criteria but intended for predefined URL sets,
        typically used as negative criteria to exclude specific pages.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            criterion_name: A name for this webpage list criterion
            conditions: List of condition dicts, each with keys:
                - operand: Valid values: URL, CATEGORY, PAGE_TITLE, PAGE_CONTENT, CUSTOM_LABEL
                - argument: The argument string to match
                - operator: Optional. Valid values: EQUALS, CONTAINS
            negative: Whether this is a negative criterion (default True)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_webpage_list_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            criterion_name=criterion_name,
            conditions=conditions,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_video_lineup_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        video_lineup_ids: List[int],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add YouTube video lineup targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            video_lineup_ids: List of video lineup IDs
            negative: Whether these are negative criteria

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_video_lineup_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            video_lineup_ids=video_lineup_ids,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_extended_demographic_criteria(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        extended_demographic_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add extended demographic targeting criteria to a campaign.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            extended_demographic_ids: List of extended demographic IDs
            negative: Whether these are negative criteria
            bid_modifier: Optional bid modifier (e.g., 1.2 for +20%)

        Returns:
            Mutation response with created campaign criteria
        """
        return await service.add_extended_demographic_criteria(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            extended_demographic_ids=extended_demographic_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_campaign_criterion(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a campaign criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_campaign_criterion(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_campaign_criterion(
        ctx: Context,
        customer_id: str,
        campaign_id: str,
        criterion_id: str,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a campaign criterion using partial update with field mask.

        Updatable fields:
            - bid_modifier (float): Bid modifier for the criterion. Use values like
                1.2 for +20%, 0.8 for -20%, 0.0 to remove the modifier.
                Not applicable to negative criteria.

        Args:
            customer_id: The customer ID
            campaign_id: The campaign ID
            criterion_id: The criterion ID to update
            bid_modifier: New bid modifier value

        Returns:
            Updated campaign criterion details including resource_name
        """
        return await service.update_campaign_criterion(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            criterion_id=criterion_id,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            add_location_criteria,
            add_language_criteria,
            add_device_criteria,
            add_negative_keyword_criteria,
            add_ad_schedule_criteria,
            add_audience_criteria,
            add_age_range_criteria,
            add_gender_criteria,
            add_income_range_criteria,
            add_proximity_criteria,
            add_parental_status_criteria,
            add_user_interest_criteria,
            add_topic_criteria,
            add_placement_criteria,
            add_youtube_channel_criteria,
            add_youtube_video_criteria,
            add_content_label_criteria,
            add_custom_audience_criteria,
            add_custom_affinity_criteria,
            add_combined_audience_criteria,
            add_life_event_criteria,
            add_keyword_theme_criteria,
            add_ip_block_criteria,
            add_carrier_criteria,
            add_mobile_app_category_criteria,
            add_mobile_application_criteria,
            add_mobile_device_criteria,
            add_operating_system_criteria,
            add_location_group_criteria,
            add_listing_scope_criteria,
            add_webpage_criteria,
            add_brand_list_criteria,
            add_local_service_id_criteria,
            add_webpage_list_criteria,
            add_video_lineup_criteria,
            add_extended_demographic_criteria,
            update_campaign_criterion,
            remove_campaign_criterion,
        ]
    )
    return tools


def register_campaign_criterion_tools(mcp: FastMCP[Any]) -> CampaignCriterionService:
    """Register campaign criterion tools with the MCP server.

    Returns the CampaignCriterionService instance for testing purposes.
    """
    service = CampaignCriterionService()
    tools = create_campaign_criterion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
