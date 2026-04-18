"""Ad group criterion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.criteria import (
    AgeRangeInfo,
    AppPaymentModelInfo,
    BrandListInfo,
    CombinedAudienceInfo,
    CustomAffinityInfo,
    CustomAudienceInfo,
    ExtendedDemographicInfo,
    GenderInfo,
    IncomeRangeInfo,
    KeywordInfo,
    LanguageInfo,
    LifeEventInfo,
    ListingGroupInfo,
    LocationInfo,
    MobileAppCategoryInfo,
    MobileApplicationInfo,
    ParentalStatusInfo,
    PlacementInfo,
    TopicInfo,
    UserInterestInfo,
    UserListInfo,
    VerticalAdsItemGroupRuleListInfo,
    VideoLineupInfo,
    WebpageConditionInfo,
    WebpageInfo,
    YouTubeChannelInfo,
    YouTubeVideoInfo,
)
from google.ads.googleads.v23.enums.types.ad_group_criterion_status import (
    AdGroupCriterionStatusEnum,
)
from google.ads.googleads.v23.enums.types.age_range_type import AgeRangeTypeEnum
from google.ads.googleads.v23.enums.types.app_payment_model_type import (
    AppPaymentModelTypeEnum,
)
from google.ads.googleads.v23.enums.types.gender_type import GenderTypeEnum
from google.ads.googleads.v23.enums.types.income_range_type import IncomeRangeTypeEnum
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.enums.types.listing_group_type import (
    ListingGroupTypeEnum,
)
from google.ads.googleads.v23.enums.types.parental_status_type import (
    ParentalStatusTypeEnum,
)
from google.ads.googleads.v23.enums.types.webpage_condition_operand import (
    WebpageConditionOperandEnum,
)
from google.ads.googleads.v23.enums.types.webpage_condition_operator import (
    WebpageConditionOperatorEnum,
)
from google.ads.googleads.v23.resources.types.ad_group_criterion import AdGroupCriterion
from google.ads.googleads.v23.services.services.ad_group_criterion_service import (
    AdGroupCriterionServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_criterion_service import (
    AdGroupCriterionOperation,
    MutateAdGroupCriteriaRequest,
    MutateAdGroupCriteriaResponse,
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


class AdGroupCriterionService:
    """Ad group criterion service for managing ad group-level targeting."""

    def __init__(self) -> None:
        """Initialize the ad group criterion service."""
        self._client: Optional[AdGroupCriterionServiceClient] = None

    @property
    def client(self) -> AdGroupCriterionServiceClient:
        """Get the ad group criterion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupCriterionService")
        assert self._client is not None
        return self._client

    async def add_keywords(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add keyword criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            keywords: List of keyword dicts with 'text', 'match_type', and optional 'cpc_bid_micros'
            negative: Whether these are negative keywords

        Returns:
            List of created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create operations
            operations = []
            for keyword in keywords:
                # Create ad group criterion
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.status = (
                    AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
                )
                ad_group_criterion.negative = negative

                # Set bid if provided and not negative
                if not negative and "cpc_bid_micros" in keyword:
                    ad_group_criterion.cpc_bid_micros = keyword["cpc_bid_micros"]

                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
                )
                ad_group_criterion.keyword = keyword_info

                # Create operation
                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(response.results)} keywords to ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add keywords: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_audience_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        user_list_ids: List[str],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add audience (user list) targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            user_list_ids: List of user list IDs
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            List of created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create operations
            operations = []
            for user_list_id in user_list_ids:
                # Create ad group criterion
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.status = (
                    AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
                )

                if bid_modifier is not None:
                    ad_group_criterion.bid_modifier = bid_modifier

                # Create user list info
                user_list_info = UserListInfo()
                user_list_info.user_list = (
                    f"customers/{customer_id}/userLists/{user_list_id}"
                )
                ad_group_criterion.user_list = user_list_info

                # Create operation
                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                criterion_resource = result.resource_name
                criterion_id = (
                    criterion_resource.split("/")[-1] if criterion_resource else ""
                )
                results.append(
                    {
                        "resource_name": criterion_resource,
                        "criterion_id": criterion_id,
                        "type": "AUDIENCE",
                        "user_list_id": user_list_ids[i],
                        "bid_modifier": bid_modifier,
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} audience criteria to ad group {ad_group_id}",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add audience criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_demographic_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        demographics: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add demographic targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            demographics: List of demographic dicts with 'type' and 'value'

        Returns:
            List of created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            # Create operations
            operations = []
            for demo in demographics:
                # Create ad group criterion
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.status = (
                    AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
                )

                # Set bid modifier if provided
                if "bid_modifier" in demo:
                    ad_group_criterion.bid_modifier = demo["bid_modifier"]

                # Set demographic based on type
                demo_type = demo["type"].upper()
                if demo_type == "AGE_RANGE":
                    age_range_info = AgeRangeInfo()
                    age_range_info.type_ = getattr(
                        AgeRangeTypeEnum.AgeRangeType, demo["value"]
                    )
                    ad_group_criterion.age_range = age_range_info
                elif demo_type == "GENDER":
                    gender_info = GenderInfo()
                    gender_info.type_ = getattr(
                        GenderTypeEnum.GenderType, demo["value"]
                    )
                    ad_group_criterion.gender = gender_info
                elif demo_type == "PARENTAL_STATUS":
                    parental_status_info = ParentalStatusInfo()
                    parental_status_info.type_ = getattr(
                        ParentalStatusTypeEnum.ParentalStatusType, demo["value"]
                    )
                    ad_group_criterion.parental_status = parental_status_info
                elif demo_type == "INCOME_RANGE":
                    income_range_info = IncomeRangeInfo()
                    income_range_info.type_ = getattr(
                        IncomeRangeTypeEnum.IncomeRangeType, demo["value"]
                    )
                    ad_group_criterion.income_range = income_range_info
                else:
                    continue  # Skip unknown types

                # Create operation
                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(demographics)} demographic criteria to ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add demographic criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_placement_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        urls: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add placement (website/app) targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            urls: List of placement URLs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for url in urls:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                placement_info = PlacementInfo()
                placement_info.url = url
                ad_group_criterion.placement = placement_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} placement criteria to ad group {ad_group_id}",
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

    async def add_mobile_app_category_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        mobile_app_category_constants: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add mobile app category targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            mobile_app_category_constants: List of mobile app category constant
                resource names (e.g., "mobileAppCategoryConstants/123")
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for resource_name in mobile_app_category_constants:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                mobile_app_category_info = MobileAppCategoryInfo()
                mobile_app_category_info.mobile_app_category_constant = resource_name
                ad_group_criterion.mobile_app_category = mobile_app_category_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} mobile app category criteria to ad group {ad_group_id}",
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
        ad_group_id: str,
        app_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add specific mobile application targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            app_ids: List of mobile application IDs (e.g., "1-123456789" for
                Android or "1-com.example.app" format)
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for app_id in app_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                mobile_application_info = MobileApplicationInfo()
                mobile_application_info.app_id = app_id
                ad_group_criterion.mobile_application = mobile_application_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} mobile application criteria to ad group {ad_group_id}",
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

    async def add_youtube_video_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        video_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add YouTube video targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            video_ids: List of YouTube video IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for video_id in video_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                youtube_video_info = YouTubeVideoInfo()
                youtube_video_info.video_id = video_id
                ad_group_criterion.youtube_video = youtube_video_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} YouTube video criteria to ad group {ad_group_id}",
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

    async def add_youtube_channel_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        channel_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add YouTube channel targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            channel_ids: List of YouTube channel IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for channel_id in channel_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                youtube_channel_info = YouTubeChannelInfo()
                youtube_channel_info.channel_id = channel_id
                ad_group_criterion.youtube_channel = youtube_channel_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} YouTube channel criteria to ad group {ad_group_id}",
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

    async def add_topic_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        topic_constant_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add topic targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            topic_constant_resource_names: List of topic constant resource names
                (e.g., ["topicConstants/123"])
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for resource_name in topic_constant_resource_names:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                topic_info = TopicInfo()
                topic_info.topic_constant = resource_name
                ad_group_criterion.topic = topic_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} topic criteria to ad group {ad_group_id}",
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

    async def add_user_interest_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        user_interest_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add user interest (in-market/affinity) targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            user_interest_resource_names: List of user interest resource names
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for resource_name in user_interest_resource_names:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                user_interest_info = UserInterestInfo()
                user_interest_info.user_interest_category = resource_name
                ad_group_criterion.user_interest = user_interest_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} user interest criteria to ad group {ad_group_id}",
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

    async def add_webpage_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        criterion_name: str,
        conditions: List[Dict[str, str]],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add webpage targeting criteria to an ad group (for DSA campaigns).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            criterion_name: A name for this webpage criterion
            conditions: List of condition dicts, each with keys:
                - operand: The operand type. Valid values: URL, CATEGORY,
                    PAGE_TITLE, PAGE_CONTENT, CUSTOM_LABEL
                - argument: The argument string to match
                - operator: Optional operator. Valid values: EQUALS, CONTAINS
                    (defaults to CONTAINS if not specified)
            negative: Whether this is a negative criterion
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.ad_group = ad_group_resource
            ad_group_criterion.negative = negative

            if bid_modifier is not None and not negative:
                ad_group_criterion.bid_modifier = bid_modifier

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

            ad_group_criterion.webpage = webpage_info

            operation = AdGroupCriterionOperation()
            operation.create = ad_group_criterion

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added webpage criterion to ad group {ad_group_id}",
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

    async def add_custom_affinity_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        custom_affinity_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add custom affinity audience targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            custom_affinity_resource_names: List of custom affinity resource names
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for resource_name in custom_affinity_resource_names:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                custom_affinity_info = CustomAffinityInfo()
                custom_affinity_info.custom_affinity = resource_name
                ad_group_criterion.custom_affinity = custom_affinity_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} custom affinity criteria to ad group {ad_group_id}",
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

    async def add_custom_audience_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        custom_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add custom audience targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            custom_audience_resource_names: List of custom audience resource names
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for resource_name in custom_audience_resource_names:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                custom_audience_info = CustomAudienceInfo()
                custom_audience_info.custom_audience = resource_name
                ad_group_criterion.custom_audience = custom_audience_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} custom audience criteria to ad group {ad_group_id}",
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

    async def add_combined_audience_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        combined_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add combined audience targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            combined_audience_resource_names: List of combined audience resource names
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for resource_name in combined_audience_resource_names:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                combined_audience_info = CombinedAudienceInfo()
                combined_audience_info.combined_audience = resource_name
                ad_group_criterion.combined_audience = combined_audience_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} combined audience criteria to ad group {ad_group_id}",
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

    async def add_location_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        location_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add location targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            location_ids: List of geo target constant IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for location_id in location_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                location_info = LocationInfo()
                location_info.geo_target_constant = f"geoTargetConstants/{location_id}"
                ad_group_criterion.location = location_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} location criteria to ad group {ad_group_id}",
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
        ad_group_id: str,
        language_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add language targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            language_ids: List of language constant IDs (e.g., "1000" for English)

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for language_id in language_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource

                language_info = LanguageInfo()
                language_info.language_constant = f"languageConstants/{language_id}"
                ad_group_criterion.language = language_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} language criteria to ad group {ad_group_id}",
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

    async def add_life_event_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        life_event_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add life event targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            life_event_ids: List of life event taxonomy IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for life_event_id in life_event_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                life_event_info = LifeEventInfo()
                life_event_info.life_event_id = life_event_id
                ad_group_criterion.life_event = life_event_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} life event criteria to ad group {ad_group_id}",
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

    async def add_video_lineup_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        video_lineup_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add YouTube video lineup targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            video_lineup_ids: List of video lineup IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for lineup_id in video_lineup_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                video_lineup_info = VideoLineupInfo()
                video_lineup_info.video_lineup_id = lineup_id
                ad_group_criterion.video_lineup = video_lineup_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} video lineup criteria to ad group {ad_group_id}",
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
        ad_group_id: str,
        extended_demographic_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add extended demographic targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            extended_demographic_ids: List of extended demographic IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            operations = []
            for demographic_id in extended_demographic_ids:
                ad_group_criterion = AdGroupCriterion()
                ad_group_criterion.ad_group = ad_group_resource
                ad_group_criterion.negative = negative

                if bid_modifier is not None and not negative:
                    ad_group_criterion.bid_modifier = bid_modifier

                extended_demographic_info = ExtendedDemographicInfo()
                extended_demographic_info.extended_demographic_id = demographic_id
                ad_group_criterion.extended_demographic = extended_demographic_info

                operation = AdGroupCriterionOperation()
                operation.create = ad_group_criterion
                operations.append(operation)

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {len(operations)} extended demographic criteria to ad group {ad_group_id}",
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

    async def add_brand_list_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add brand list targeting criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            shared_set_resource_name: Resource name of the shared set containing
                the brand list (e.g., "customers/123/sharedSets/456")

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.ad_group = ad_group_resource

            brand_list_info = BrandListInfo()
            brand_list_info.shared_set = shared_set_resource_name
            ad_group_criterion.brand_list = brand_list_info

            operation = AdGroupCriterionOperation()
            operation.create = ad_group_criterion

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added brand list criterion to ad group {ad_group_id}",
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

    async def add_listing_group_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        listing_group_type: str,
        case_value: Optional[Dict[str, Any]] = None,
        parent_ad_group_criterion: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add listing group criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            listing_group_type: Type of listing group: SUBDIVISION or UNIT
            case_value: Optional case value dict for the listing group
            parent_ad_group_criterion: Optional parent ad group criterion resource name

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.ad_group = ad_group_resource
            listing_group_info = ListingGroupInfo()
            listing_group_info.type_ = getattr(
                ListingGroupTypeEnum.ListingGroupType, listing_group_type
            )
            if parent_ad_group_criterion is not None:
                listing_group_info.parent_ad_group_criterion = parent_ad_group_criterion
            ad_group_criterion.listing_group = listing_group_info

            operation = AdGroupCriterionOperation()
            operation.create = ad_group_criterion

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added listing group criterion to ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add listing group criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_app_payment_model_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        app_payment_model_type: str = "PAID",
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add app payment model criteria to an ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            app_payment_model_type: The app payment model type (PAID)
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.ad_group = ad_group_resource

            if bid_modifier is not None:
                ad_group_criterion.bid_modifier = bid_modifier

            app_payment_info = AppPaymentModelInfo()
            app_payment_info.type_ = getattr(
                AppPaymentModelTypeEnum.AppPaymentModelType,
                app_payment_model_type,
            )
            ad_group_criterion.app_payment_model = app_payment_info

            operation = AdGroupCriterionOperation()
            operation.create = ad_group_criterion

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added app payment model criterion to ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add app payment model criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_vertical_ads_item_group_rule_list_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        shared_set_resource_name: str,
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add vertical ads item group rules from a shared set for product-level targeting.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ad_group_id: The ad group ID
            shared_set_resource_name: Resource name of the shared set containing
                the vertical ads item group rules
            negative: Whether this is a negative criterion

        Returns:
            Mutation response with created ad group criteria
        """
        try:
            customer_id = format_customer_id(customer_id)
            ad_group_resource = f"customers/{customer_id}/adGroups/{ad_group_id}"

            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.ad_group = ad_group_resource
            ad_group_criterion.negative = negative

            rule_list_info = VerticalAdsItemGroupRuleListInfo()
            rule_list_info.shared_set = shared_set_resource_name
            ad_group_criterion.vertical_ads_item_group_rule_list = rule_list_info

            operation = AdGroupCriterionOperation()
            operation.create = ad_group_criterion

            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAdGroupCriteriaResponse = (
                self.client.mutate_ad_group_criteria(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added vertical ads item group rule list criterion to ad group {ad_group_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = (
                f"Failed to add vertical ads item group rule list criteria: {str(e)}"
            )
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_criterion_bid(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        cpc_bid_micros: Optional[int] = None,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update the bid for an ad group criterion.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            criterion_resource_name: The criterion resource name
            cpc_bid_micros: New CPC bid in micros
            bid_modifier: New bid modifier

        Returns:
            Updated criterion details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create ad group criterion
            ad_group_criterion = AdGroupCriterion()
            ad_group_criterion.resource_name = criterion_resource_name

            # Create update mask
            update_mask_fields = []

            if cpc_bid_micros is not None:
                ad_group_criterion.cpc_bid_micros = cpc_bid_micros
                update_mask_fields.append("cpc_bid_micros")

            if bid_modifier is not None:
                ad_group_criterion.bid_modifier = bid_modifier
                update_mask_fields.append("bid_modifier")

            # Create operation
            operation = AdGroupCriterionOperation()
            operation.update = ad_group_criterion
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_ad_group_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Updated criterion bid: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update criterion bid: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_ad_group_criterion(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove an ad group criterion.

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
            operation = AdGroupCriterionOperation()
            operation.remove = criterion_resource_name

            # Create request
            request = MutateAdGroupCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_ad_group_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Removed ad group criterion: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove ad group criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_ad_group_criterion_tools(
    service: AdGroupCriterionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group criterion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def add_keywords(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add keyword criteria to an ad group.

        Ad group-level only. For campaign-level negative keywords, use campaign criterion tools.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            keywords: List of keyword dicts with:
                - text: Keyword text
                - match_type: BROAD, PHRASE, EXACT
                - cpc_bid_micros: Optional CPC bid in micros
            negative: Whether these are negative keywords

        Returns:
            Response with created ad group criteria details
        """
        return await service.add_keywords(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            keywords=keywords,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_audience_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        user_list_ids: List[str],
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add audience (user list) targeting criteria to an ad group.

        Ad group-level. Supports both targeting and observation (bid-only) modes.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            user_list_ids: List of user list IDs for remarketing
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            List of created ad group criteria with resource names and IDs
        """
        return await service.add_audience_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            user_list_ids=user_list_ids,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_demographic_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        demographics: List[Dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add demographic targeting criteria to an ad group.

        Ad group-level. For Search campaigns, use ad group-level demographics for bid adjustments (campaign-level demographics are exclusion-only).

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            demographics: List of demographic dicts with:
                - type: AGE_RANGE, GENDER, PARENTAL_STATUS, or INCOME_RANGE
                - value: Specific value for the type (e.g., AGE_RANGE_18_24, MALE, PARENT)
                - bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            List of created ad group criteria with resource names and IDs
        """
        return await service.add_demographic_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            demographics=demographics,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_placement_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        urls: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add placement (website/app URL) targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            urls: List of placement URLs (e.g., "example.com", "youtube.com")
            negative: Whether these are negative placements (exclusions)
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group placement criteria
        """
        return await service.add_placement_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            urls=urls,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_mobile_app_category_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        mobile_app_category_constants: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add mobile app category targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            mobile_app_category_constants: List of mobile app category constant
                resource names (e.g., "mobileAppCategoryConstants/123")
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group mobile app category criteria
        """
        return await service.add_mobile_app_category_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            mobile_app_category_constants=mobile_app_category_constants,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_mobile_application_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        app_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add specific mobile application targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            app_ids: List of mobile application IDs (e.g., "1-123456789" for
                Android or "1-com.example.app" format)
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group mobile application criteria
        """
        return await service.add_mobile_application_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            app_ids=app_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_youtube_video_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        video_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add YouTube video targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            video_ids: List of YouTube video IDs
            negative: Whether these are negative criteria (exclusions)
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group YouTube video criteria
        """
        return await service.add_youtube_video_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            video_ids=video_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_youtube_channel_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        channel_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add YouTube channel targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            channel_ids: List of YouTube channel IDs
            negative: Whether these are negative criteria (exclusions)
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group YouTube channel criteria
        """
        return await service.add_youtube_channel_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            channel_ids=channel_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_topic_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        topic_constant_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add topic targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            topic_constant_resource_names: List of topic constant resource names
                (e.g., "topicConstants/123")
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group topic criteria
        """
        return await service.add_topic_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            topic_constant_resource_names=topic_constant_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_user_interest_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        user_interest_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add user interest (in-market/affinity audience) targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            user_interest_resource_names: List of user interest resource names
                (e.g., "customers/123/userInterests/456")
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group user interest criteria
        """
        return await service.add_user_interest_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            user_interest_resource_names=user_interest_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_webpage_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        criterion_name: str,
        conditions: List[Dict[str, str]],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add webpage targeting criteria to an ad group (for DSA campaigns).

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            criterion_name: A name for this webpage criterion
            conditions: List of condition dicts, each with keys:
                - operand: URL, CATEGORY, PAGE_TITLE, PAGE_CONTENT, CUSTOM_LABEL
                - argument: The argument string to match
                - operator: Optional. EQUALS or CONTAINS (defaults to CONTAINS)
            negative: Whether this is a negative criterion
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group webpage criteria
        """
        return await service.add_webpage_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            criterion_name=criterion_name,
            conditions=conditions,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_custom_affinity_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        custom_affinity_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add custom affinity audience targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            custom_affinity_resource_names: List of custom affinity resource names
                (e.g., "customers/123/customAffinities/456")
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group custom affinity criteria
        """
        return await service.add_custom_affinity_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            custom_affinity_resource_names=custom_affinity_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_custom_audience_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        custom_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add custom audience targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            custom_audience_resource_names: List of custom audience resource names
                (e.g., "customers/123/customAudiences/456")
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group custom audience criteria
        """
        return await service.add_custom_audience_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            custom_audience_resource_names=custom_audience_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_combined_audience_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        combined_audience_resource_names: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add combined audience targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            combined_audience_resource_names: List of combined audience resource names
                (e.g., "customers/123/combinedAudiences/456")
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group combined audience criteria
        """
        return await service.add_combined_audience_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            combined_audience_resource_names=combined_audience_resource_names,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_location_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        location_ids: List[str],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add location targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            location_ids: List of geo target constant IDs (e.g., "2840" for US)
            negative: Whether these are negative criteria (exclusions)
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group location criteria
        """
        return await service.add_location_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
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
        ad_group_id: str,
        language_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add language targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            language_ids: List of language constant IDs (e.g., "1000" for English)

        Returns:
            Response with created ad group language criteria
        """
        return await service.add_language_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            language_ids=language_ids,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_life_event_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        life_event_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add life event targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            life_event_ids: List of life event taxonomy IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group life event criteria
        """
        return await service.add_life_event_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            life_event_ids=life_event_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_video_lineup_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        video_lineup_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add YouTube video lineup targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            video_lineup_ids: List of video lineup IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group video lineup criteria
        """
        return await service.add_video_lineup_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            video_lineup_ids=video_lineup_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_extended_demographic_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        extended_demographic_ids: List[int],
        negative: bool = False,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add extended demographic targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            extended_demographic_ids: List of extended demographic IDs
            negative: Whether these are negative criteria
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group extended demographic criteria
        """
        return await service.add_extended_demographic_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            extended_demographic_ids=extended_demographic_ids,
            negative=negative,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_brand_list_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add brand list targeting criteria to an ad group.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            shared_set_resource_name: Resource name of the shared set containing
                the brand list (e.g., "customers/123/sharedSets/456")

        Returns:
            Response with created ad group brand list criteria
        """
        return await service.add_brand_list_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            shared_set_resource_name=shared_set_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_listing_group_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        listing_group_type: str,
        case_value: Optional[Dict[str, Any]] = None,
        parent_ad_group_criterion: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add listing group criteria to an ad group for Shopping campaigns.

        Ad group-level only. For Shopping campaigns product group targeting.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            listing_group_type: Type of listing group: SUBDIVISION or UNIT
            case_value: Optional case value dict for the listing group
            parent_ad_group_criterion: Optional parent ad group criterion resource name

        Returns:
            Response with created ad group listing group criteria
        """
        return await service.add_listing_group_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            listing_group_type=listing_group_type,
            case_value=case_value,
            parent_ad_group_criterion=parent_ad_group_criterion,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_app_payment_model_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        app_payment_model_type: str = "PAID",
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add app payment model criteria to an ad group.

        Ad group-level only.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            app_payment_model_type: The app payment model type (PAID)
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%.

        Returns:
            Response with created ad group app payment model criteria
        """
        return await service.add_app_payment_model_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            app_payment_model_type=app_payment_model_type,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_vertical_ads_item_group_rule_list_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_id: str,
        shared_set_resource_name: str,
        negative: bool = False,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add vertical ads item group rules from a shared set for product-level targeting.

        Args:
            customer_id: The customer ID
            ad_group_id: The ad group ID
            shared_set_resource_name: Resource name of the shared set containing
                the vertical ads item group rules
            negative: Whether this is a negative criterion

        Returns:
            Response with created ad group vertical ads item group rule list criteria
        """
        return await service.add_vertical_ads_item_group_rule_list_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_id=ad_group_id,
            shared_set_resource_name=shared_set_resource_name,
            negative=negative,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_criterion_bid(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        cpc_bid_micros: Optional[int] = None,
        bid_modifier: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the bid for an ad group criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion
            cpc_bid_micros: New CPC bid in micros (for keywords)
            bid_modifier: Multiplier on base bid. 1.0 = no change, 1.5 = +50%, 0.5 = -50%. (for audiences, demographics)

        Returns:
            Updated criterion details with updated fields
        """
        return await service.update_criterion_bid(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            cpc_bid_micros=cpc_bid_micros,
            bid_modifier=bid_modifier,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_ad_group_criterion(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove an ad group criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_ad_group_criterion(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            add_keywords,
            add_audience_criteria,
            add_demographic_criteria,
            add_placement_criteria,
            add_mobile_app_category_criteria,
            add_mobile_application_criteria,
            add_youtube_video_criteria,
            add_youtube_channel_criteria,
            add_topic_criteria,
            add_user_interest_criteria,
            add_webpage_criteria,
            add_custom_affinity_criteria,
            add_custom_audience_criteria,
            add_combined_audience_criteria,
            add_location_criteria,
            add_language_criteria,
            add_life_event_criteria,
            add_video_lineup_criteria,
            add_extended_demographic_criteria,
            add_brand_list_criteria,
            add_listing_group_criteria,
            add_app_payment_model_criteria,
            add_vertical_ads_item_group_rule_list_criteria,
            update_criterion_bid,
            remove_ad_group_criterion,
        ]
    )
    return tools


def register_ad_group_criterion_tools(mcp: FastMCP[Any]) -> AdGroupCriterionService:
    """Register ad group criterion tools with the MCP server.

    Returns the AdGroupCriterionService instance for testing purposes.
    """
    service = AdGroupCriterionService()
    tools = create_ad_group_criterion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
