"""Recommendation subscription service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.recommendation_type import (
    RecommendationTypeEnum,
)
from google.ads.googleads.v23.resources.types.recommendation_subscription import (
    RecommendationSubscription,
)
from google.ads.googleads.v23.services.services.recommendation_subscription_service import (
    RecommendationSubscriptionServiceClient,
)
from google.ads.googleads.v23.services.types.recommendation_subscription_service import (
    MutateRecommendationSubscriptionRequest,
    MutateRecommendationSubscriptionResponse,
    RecommendationSubscriptionOperation,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class RecommendationSubscriptionService:
    """Service for managing auto-apply recommendation subscriptions."""

    def __init__(self) -> None:
        self._client: Optional[RecommendationSubscriptionServiceClient] = None

    @property
    def client(self) -> RecommendationSubscriptionServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "RecommendationSubscriptionService"
            )
        assert self._client is not None
        return self._client

    async def create_subscription(
        self,
        ctx: Context,
        customer_id: str,
        recommendation_type: str,
    ) -> Dict[str, Any]:
        """Create a recommendation subscription to auto-apply a recommendation type.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            recommendation_type: Type of recommendation to auto-apply (e.g. CAMPAIGN_BUDGET, KEYWORD)

        Returns:
            Created subscription details
        """
        try:
            customer_id = format_customer_id(customer_id)

            subscription = RecommendationSubscription()
            subscription.type_ = getattr(
                RecommendationTypeEnum.RecommendationType, recommendation_type
            )

            operation = RecommendationSubscriptionOperation()
            operation.create = subscription

            request = MutateRecommendationSubscriptionRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateRecommendationSubscriptionResponse = (
                self.client.mutate_recommendation_subscription(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created recommendation subscription for {recommendation_type}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create recommendation subscription: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_subscription(
        self,
        ctx: Context,
        customer_id: str,
        subscription_resource_name: str,
        recommendation_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a recommendation subscription.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            subscription_resource_name: Resource name of the subscription
            recommendation_type: New recommendation type

        Returns:
            Updated subscription details
        """
        try:
            customer_id = format_customer_id(customer_id)

            subscription = RecommendationSubscription()
            subscription.resource_name = subscription_resource_name

            update_mask_fields = []
            if recommendation_type is not None:
                subscription.type_ = getattr(
                    RecommendationTypeEnum.RecommendationType, recommendation_type
                )
                update_mask_fields.append("type")

            operation = RecommendationSubscriptionOperation()
            operation.update = subscription
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            request = MutateRecommendationSubscriptionRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateRecommendationSubscriptionResponse = (
                self.client.mutate_recommendation_subscription(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Updated recommendation subscription {subscription_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update recommendation subscription: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_recommendation_subscription_tools(
    service: RecommendationSubscriptionService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the recommendation subscription service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def create_recommendation_subscription(
        ctx: Context, customer_id: str, recommendation_type: str
    ) -> Dict[str, Any]:
        """Create a subscription to auto-apply a recommendation type.

        Args:
            customer_id: The customer ID
            recommendation_type: Type to auto-apply - CAMPAIGN_BUDGET, KEYWORD,
                MAXIMIZE_CLICKS_OPT_IN, TARGET_CPA_OPT_IN, etc.

        Returns:
            Created subscription details
        """
        return await service.create_subscription(
            ctx=ctx,
            customer_id=customer_id,
            recommendation_type=recommendation_type,
        )

    async def update_recommendation_subscription(
        ctx: Context,
        customer_id: str,
        subscription_resource_name: str,
        recommendation_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a recommendation subscription.

        Args:
            customer_id: The customer ID
            subscription_resource_name: Resource name of the subscription
            recommendation_type: New recommendation type

        Returns:
            Updated subscription details
        """
        return await service.update_subscription(
            ctx=ctx,
            customer_id=customer_id,
            subscription_resource_name=subscription_resource_name,
            recommendation_type=recommendation_type,
        )

    tools.extend(
        [create_recommendation_subscription, update_recommendation_subscription]
    )
    return tools


def register_recommendation_subscription_tools(
    mcp: FastMCP[Any],
) -> RecommendationSubscriptionService:
    """Register recommendation subscription tools with the MCP server."""
    service = RecommendationSubscriptionService()
    tools = create_recommendation_subscription_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
