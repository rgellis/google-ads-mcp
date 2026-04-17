"""Customer negative criterion service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.criteria import (
    ContentLabelInfo,
    IpBlockInfo,
    KeywordInfo,
    MobileAppCategoryInfo,
    MobileApplicationInfo,
    NegativeKeywordListInfo,
    PlacementInfo,
    PlacementListInfo,
    YouTubeChannelInfo,
    YouTubeVideoInfo,
)
from google.ads.googleads.v23.enums.types.content_label_type import ContentLabelTypeEnum
from google.ads.googleads.v23.enums.types.criterion_type import CriterionTypeEnum
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.resources.types.customer_negative_criterion import (
    CustomerNegativeCriterion,
)
from google.ads.googleads.v23.services.services.customer_negative_criterion_service import (
    CustomerNegativeCriterionServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.customer_negative_criterion_service import (
    CustomerNegativeCriterionOperation,
    MutateCustomerNegativeCriteriaRequest,
    MutateCustomerNegativeCriteriaResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class CustomerNegativeCriterionService:
    """Customer negative criterion service for account-level exclusions."""

    def __init__(self) -> None:
        """Initialize the customer negative criterion service."""
        self._client: Optional[CustomerNegativeCriterionServiceClient] = None

    @property
    def client(self) -> CustomerNegativeCriterionServiceClient:
        """Get the customer negative criterion service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "CustomerNegativeCriterionService"
            )
        assert self._client is not None
        return self._client

    async def add_negative_keywords(
        self,
        ctx: Context,
        customer_id: str,
        keywords: List[Dict[str, str]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add negative keywords at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keywords: List of dicts with 'text' and 'match_type' keys

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for keyword in keywords:
                # Create customer negative criterion
                customer_negative_criterion = CustomerNegativeCriterion()

                # Create keyword info
                keyword_info = KeywordInfo()
                keyword_info.text = keyword["text"]
                keyword_info.match_type = getattr(
                    KeywordMatchTypeEnum.KeywordMatchType, keyword["match_type"]
                )
                customer_negative_criterion.keyword = keyword_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.KEYWORD
                )

                # Create operation
                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

            # Process results
            results = []
            for i, result in enumerate(response.results):
                criterion_resource = result.resource_name
                criterion_id = (
                    criterion_resource.split("/")[-1] if criterion_resource else ""
                )
                keyword = keywords[i]
                results.append(
                    {
                        "resource_name": criterion_resource,
                        "criterion_id": criterion_id,
                        "type": "KEYWORD",
                        "keyword_text": keyword["text"],
                        "match_type": keyword["match_type"],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} negative keywords at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add negative keywords: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_placement_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        placement_urls: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add placement (website) exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            placement_urls: List of website URLs to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for url in placement_urls:
                # Create customer negative criterion
                customer_negative_criterion = CustomerNegativeCriterion()

                # Create placement info
                placement_info = PlacementInfo()
                placement_info.url = url
                customer_negative_criterion.placement = placement_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.PLACEMENT
                )

                # Create operation
                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
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
                        "type": "PLACEMENT",
                        "url": placement_urls[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} placement exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add placement exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_content_label_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        content_labels: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add content label exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            content_labels: List of content label types to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operations
            operations = []
            for label in content_labels:
                # Create customer negative criterion
                customer_negative_criterion = CustomerNegativeCriterion()

                # Create content label info
                content_label_info = ContentLabelInfo()
                content_label_info.type_ = getattr(
                    ContentLabelTypeEnum.ContentLabelType, label
                )
                customer_negative_criterion.content_label = content_label_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.CONTENT_LABEL
                )

                # Create operation
                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
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
                        "type": "CONTENT_LABEL",
                        "content_label": content_labels[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} content label exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add content label exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_mobile_application_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        app_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add mobile application exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            app_ids: List of mobile app IDs to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            operations = []
            for app_id in app_ids:
                customer_negative_criterion = CustomerNegativeCriterion()
                mobile_app_info = MobileApplicationInfo()
                mobile_app_info.app_id = app_id
                customer_negative_criterion.mobile_application = mobile_app_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.MOBILE_APPLICATION
                )

                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

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
                        "type": "MOBILE_APPLICATION",
                        "app_id": app_ids[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} mobile application exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add mobile application exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_mobile_app_category_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        category_constants: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add mobile app category exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            category_constants: List of mobile app category constant resource names

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            operations = []
            for constant in category_constants:
                customer_negative_criterion = CustomerNegativeCriterion()
                category_info = MobileAppCategoryInfo()
                category_info.mobile_app_category_constant = constant
                customer_negative_criterion.mobile_app_category = category_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.MOBILE_APP_CATEGORY
                )

                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

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
                        "type": "MOBILE_APP_CATEGORY",
                        "mobile_app_category_constant": category_constants[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} mobile app category exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add mobile app category exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_youtube_video_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        video_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add YouTube video exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            video_ids: List of YouTube video IDs to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            operations = []
            for video_id in video_ids:
                customer_negative_criterion = CustomerNegativeCriterion()
                video_info = YouTubeVideoInfo()
                video_info.video_id = video_id
                customer_negative_criterion.youtube_video = video_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.YOUTUBE_VIDEO
                )

                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

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
                        "type": "YOUTUBE_VIDEO",
                        "video_id": video_ids[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} YouTube video exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add YouTube video exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_youtube_channel_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        channel_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add YouTube channel exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            channel_ids: List of YouTube channel IDs to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            operations = []
            for channel_id in channel_ids:
                customer_negative_criterion = CustomerNegativeCriterion()
                channel_info = YouTubeChannelInfo()
                channel_info.channel_id = channel_id
                customer_negative_criterion.youtube_channel = channel_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.YOUTUBE_CHANNEL
                )

                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

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
                        "type": "YOUTUBE_CHANNEL",
                        "channel_id": channel_ids[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} YouTube channel exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add YouTube channel exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_ip_block_exclusions(
        self,
        ctx: Context,
        customer_id: str,
        ip_addresses: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> List[Dict[str, Any]]:
        """Add IP block exclusions at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            ip_addresses: List of IP addresses or CIDR ranges to exclude

        Returns:
            List of created customer negative criteria
        """
        try:
            customer_id = format_customer_id(customer_id)

            operations = []
            for ip_address in ip_addresses:
                customer_negative_criterion = CustomerNegativeCriterion()
                ip_block_info = IpBlockInfo()
                ip_block_info.ip_address = ip_address
                customer_negative_criterion.ip_block = ip_block_info
                customer_negative_criterion.type_ = (
                    CriterionTypeEnum.CriterionType.IP_BLOCK
                )

                operation = CustomerNegativeCriterionOperation()
                operation.create = customer_negative_criterion
                operations.append(operation)

            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = operations
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

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
                        "type": "IP_BLOCK",
                        "ip_address": ip_addresses[i],
                    }
                )

            await ctx.log(
                level="info",
                message=f"Added {len(results)} IP block exclusions at account level",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add IP block exclusions: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_negative_keyword_list_exclusion(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add a negative keyword list exclusion at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_resource_name: Resource name of the shared set (negative keyword list)

        Returns:
            Created customer negative criterion
        """
        try:
            customer_id = format_customer_id(customer_id)

            customer_negative_criterion = CustomerNegativeCriterion()
            nkl_info = NegativeKeywordListInfo()
            nkl_info.shared_set = shared_set_resource_name
            customer_negative_criterion.negative_keyword_list = nkl_info
            customer_negative_criterion.type_ = (
                CriterionTypeEnum.CriterionType.NEGATIVE_KEYWORD_LIST
            )

            operation = CustomerNegativeCriterionOperation()
            operation.create = customer_negative_criterion

            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

            result = response.results[0]
            criterion_resource = result.resource_name
            criterion_id = (
                criterion_resource.split("/")[-1] if criterion_resource else ""
            )

            await ctx.log(
                level="info",
                message="Added negative keyword list exclusion at account level",
            )

            return {
                "resource_name": criterion_resource,
                "criterion_id": criterion_id,
                "type": "NEGATIVE_KEYWORD_LIST",
                "shared_set": shared_set_resource_name,
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add negative keyword list exclusion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def add_placement_list_exclusion(
        self,
        ctx: Context,
        customer_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Exclude placements from a shared placement list at the account level.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            shared_set_resource_name: Resource name of the shared set (placement list)

        Returns:
            Created customer negative criterion
        """
        try:
            customer_id = format_customer_id(customer_id)

            customer_negative_criterion = CustomerNegativeCriterion()
            placement_list_info = PlacementListInfo()
            placement_list_info.shared_set = shared_set_resource_name
            customer_negative_criterion.placement_list = placement_list_info
            customer_negative_criterion.type_ = (
                CriterionTypeEnum.CriterionType.PLACEMENT_LIST
            )

            operation = CustomerNegativeCriterionOperation()
            operation.create = customer_negative_criterion

            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerNegativeCriteriaResponse = (
                self.client.mutate_customer_negative_criteria(request=request)
            )

            result = response.results[0]
            criterion_resource = result.resource_name
            criterion_id = (
                criterion_resource.split("/")[-1] if criterion_resource else ""
            )

            await ctx.log(
                level="info",
                message="Added placement list exclusion at account level",
            )

            return {
                "resource_name": criterion_resource,
                "criterion_id": criterion_id,
                "type": "PLACEMENT_LIST",
                "shared_set": shared_set_resource_name,
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add placement list exclusion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_negative_criteria(
        self,
        ctx: Context,
        customer_id: str,
        criterion_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all customer negative criteria.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            criterion_type: Optional filter by type (KEYWORD, PLACEMENT, CONTENT_LABEL,
                MOBILE_APPLICATION, MOBILE_APP_CATEGORY, YOUTUBE_VIDEO, YOUTUBE_CHANNEL,
                IP_BLOCK, NEGATIVE_KEYWORD_LIST)

        Returns:
            List of customer negative criteria
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
                    customer_negative_criterion.resource_name,
                    customer_negative_criterion.id,
                    customer_negative_criterion.type,
                    customer_negative_criterion.keyword.text,
                    customer_negative_criterion.keyword.match_type,
                    customer_negative_criterion.placement.url,
                    customer_negative_criterion.content_label.type
                FROM customer_negative_criterion
            """

            if criterion_type:
                query += f" WHERE customer_negative_criterion.type = '{criterion_type}'"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            criteria = []
            for row in response:
                criterion = row.customer_negative_criterion
                criterion_dict = {
                    "resource_name": criterion.resource_name,
                    "criterion_id": str(criterion.id),
                    "type": criterion.type_.name if criterion.type_ else "UNKNOWN",
                }

                # Add type-specific fields
                if criterion.keyword:
                    criterion_dict["keyword_text"] = criterion.keyword.text
                    criterion_dict["match_type"] = criterion.keyword.match_type.name
                elif criterion.placement:
                    criterion_dict["url"] = criterion.placement.url
                elif criterion.content_label:
                    criterion_dict["content_label"] = criterion.content_label.type_.name

                criteria.append(criterion_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(criteria)} customer negative criteria",
            )

            return criteria

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list negative criteria: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_negative_criterion(
        self,
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a customer negative criterion.

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
            operation = CustomerNegativeCriterionOperation()
            operation.remove = criterion_resource_name

            # Create request
            request = MutateCustomerNegativeCriteriaRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_customer_negative_criteria(request=request)

            await ctx.log(
                level="info",
                message=f"Removed customer negative criterion: {criterion_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove negative criterion: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_negative_criterion_tools(
    service: CustomerNegativeCriterionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer negative criterion service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def add_negative_keywords(
        ctx: Context,
        customer_id: str,
        keywords: List[Dict[str, str]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add negative keywords at the account level.

        Args:
            customer_id: The customer ID
            keywords: List of keyword dicts with:
                - text: Keyword text
                - match_type: BROAD, PHRASE, or EXACT

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_negative_keywords(
            ctx=ctx,
            customer_id=customer_id,
            keywords=keywords,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_placement_exclusions(
        ctx: Context,
        customer_id: str,
        placement_urls: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add placement (website) exclusions at the account level.

        Args:
            customer_id: The customer ID
            placement_urls: List of website URLs to exclude (e.g., ["example.com", "site.com"])

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_placement_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            placement_urls=placement_urls,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_content_label_exclusions(
        ctx: Context,
        customer_id: str,
        content_labels: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add content label exclusions at the account level.

        Args:
            customer_id: The customer ID
            content_labels: List of content label types to exclude:
                - JUVENILE
                - PROFANITY
                - TRAGEDY
                - VIDEO
                - VIDEO_RATING_DV_G
                - VIDEO_RATING_DV_PG
                - VIDEO_RATING_DV_T
                - VIDEO_RATING_DV_MA
                - VIDEO_NOT_YET_RATED
                - EMBEDDED_VIDEO
                - LIVE_STREAMING_VIDEO
                - SOCIAL_ISSUES

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_content_label_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            content_labels=content_labels,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def list_negative_criteria(
        ctx: Context,
        customer_id: str,
        criterion_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all customer negative criteria.

        Args:
            customer_id: The customer ID
            criterion_type: Optional filter by type - KEYWORD, PLACEMENT, or CONTENT_LABEL

        Returns:
            List of customer negative criteria with details
        """
        return await service.list_negative_criteria(
            ctx=ctx,
            customer_id=customer_id,
            criterion_type=criterion_type,
        )

    async def remove_negative_criterion(
        ctx: Context,
        customer_id: str,
        criterion_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a customer negative criterion.

        Args:
            customer_id: The customer ID
            criterion_resource_name: The full resource name of the criterion to remove

        Returns:
            Removal result with status
        """
        return await service.remove_negative_criterion(
            ctx=ctx,
            customer_id=customer_id,
            criterion_resource_name=criterion_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_mobile_application_exclusions(
        ctx: Context,
        customer_id: str,
        app_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add mobile application exclusions at the account level.

        Args:
            customer_id: The customer ID
            app_ids: List of mobile app IDs to exclude (e.g., ["com.example.app"])

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_mobile_application_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            app_ids=app_ids,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_mobile_app_category_exclusions(
        ctx: Context,
        customer_id: str,
        category_constants: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add mobile app category exclusions at the account level.

        Args:
            customer_id: The customer ID
            category_constants: List of mobile app category constant resource names
                (e.g., ["mobileAppCategoryConstants/60001"])

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_mobile_app_category_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            category_constants=category_constants,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_youtube_video_exclusions(
        ctx: Context,
        customer_id: str,
        video_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add YouTube video exclusions at the account level.

        Args:
            customer_id: The customer ID
            video_ids: List of YouTube video IDs to exclude (e.g., ["dQw4w9WgXcQ"])

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_youtube_video_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            video_ids=video_ids,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_youtube_channel_exclusions(
        ctx: Context,
        customer_id: str,
        channel_ids: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add YouTube channel exclusions at the account level.

        Args:
            customer_id: The customer ID
            channel_ids: List of YouTube channel IDs to exclude (e.g., ["UCxxxxxx"])

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_youtube_channel_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            channel_ids=channel_ids,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_ip_block_exclusions(
        ctx: Context,
        customer_id: str,
        ip_addresses: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Add IP block exclusions at the account level.

        Args:
            customer_id: The customer ID
            ip_addresses: List of IP addresses or CIDR ranges to exclude
                (e.g., ["192.168.1.0/24", "10.0.0.1"])

        Returns:
            List of created customer negative criteria with resource names and IDs
        """
        return await service.add_ip_block_exclusions(
            ctx=ctx,
            customer_id=customer_id,
            ip_addresses=ip_addresses,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_negative_keyword_list_exclusion(
        ctx: Context,
        customer_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a negative keyword list exclusion at the account level.

        Links a shared negative keyword list to the account so all keywords
        in the list are excluded account-wide.

        Args:
            customer_id: The customer ID
            shared_set_resource_name: Resource name of the shared set
                (e.g., "customers/1234567890/sharedSets/111222")

        Returns:
            Created customer negative criterion with resource name and ID
        """
        return await service.add_negative_keyword_list_exclusion(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_resource_name=shared_set_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def add_placement_list_exclusion(
        ctx: Context,
        customer_id: str,
        shared_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Exclude placements from a shared placement list at the account level.

        Args:
            customer_id: The customer ID
            shared_set_resource_name: Resource name of the shared set (placement list)
                (e.g., "customers/1234567890/sharedSets/111222")

        Returns:
            Created customer negative criterion with resource name and ID
        """
        return await service.add_placement_list_exclusion(
            ctx=ctx,
            customer_id=customer_id,
            shared_set_resource_name=shared_set_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            add_negative_keywords,
            add_placement_exclusions,
            add_content_label_exclusions,
            add_mobile_application_exclusions,
            add_mobile_app_category_exclusions,
            add_youtube_video_exclusions,
            add_youtube_channel_exclusions,
            add_ip_block_exclusions,
            add_negative_keyword_list_exclusion,
            add_placement_list_exclusion,
            list_negative_criteria,
            remove_negative_criterion,
        ]
    )
    return tools


def register_customer_negative_criterion_tools(
    mcp: FastMCP[Any],
) -> CustomerNegativeCriterionService:
    """Register customer negative criterion tools with the MCP server.

    Returns the CustomerNegativeCriterionService instance for testing purposes.
    """
    service = CustomerNegativeCriterionService()
    tools = create_customer_negative_criterion_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
