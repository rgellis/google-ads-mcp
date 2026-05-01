"""Customer lifecycle goal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.lifecycle_goals import (
    LifecycleGoalValueSettings,
)
from google.ads.googleads.v23.resources.types.customer_lifecycle_goal import (
    CustomerLifecycleGoal,
)
from google.ads.googleads.v23.services.services.customer_lifecycle_goal_service import (
    CustomerLifecycleGoalServiceClient,
)
from google.ads.googleads.v23.services.types.customer_lifecycle_goal_service import (
    ConfigureCustomerLifecycleGoalsRequest,
    ConfigureCustomerLifecycleGoalsResponse,
    CustomerLifecycleGoalOperation,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
)

logger = get_logger(__name__)


def _build_value_settings(
    value: Optional[float],
    high_lifetime_value: Optional[float],
) -> LifecycleGoalValueSettings:
    settings = LifecycleGoalValueSettings()
    if value is not None:
        settings.value = value
    if high_lifetime_value is not None:
        settings.high_lifetime_value = high_lifetime_value
    return settings


class CustomerLifecycleGoalService:
    """Service for configuring account-level customer lifecycle goals.

    The CustomerLifecycleGoal resource is a singleton per customer
    (resource_name = ``customers/{customer_id}/customerLifecycleGoal``).
    The proto annotates most fields as ``Output only``, but per
    CLAUDE.md the operation docstring drives what's actually settable.
    """

    def __init__(self) -> None:
        self._client: Optional[CustomerLifecycleGoalServiceClient] = None

    @property
    def client(self) -> CustomerLifecycleGoalServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerLifecycleGoalService")
        assert self._client is not None
        return self._client

    async def configure_customer_lifecycle_goals(
        self,
        ctx: Context,
        customer_id: str,
        operation_type: str,
        value: Optional[float] = None,
        high_lifetime_value: Optional[float] = None,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Configure the account-level customer lifecycle goal.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operation_type: ``CREATE`` or ``UPDATE``. The
                CustomerLifecycleGoal is a singleton per customer; use
                CREATE the first time and UPDATE to change settings on
                an already-configured account.
            value: Incremental conversion value for new customers who
                are not high-value.
            high_lifetime_value: Incremental conversion value for
                high-value new customers. Must be greater than
                ``value`` if both are set.
            validate_only: If True, validate the request without
                executing it.

        Returns:
            The serialized ConfigureCustomerLifecycleGoalsResponse.
        """
        if operation_type not in {"CREATE", "UPDATE"}:
            raise ValueError(
                f"operation_type must be CREATE or UPDATE, got {operation_type!r}"
            )

        try:
            customer_id = format_customer_id(customer_id)

            goal = CustomerLifecycleGoal()
            if operation_type == "UPDATE":
                goal.resource_name = f"customers/{customer_id}/customerLifecycleGoal"

            update_paths: List[str] = []
            if value is not None or high_lifetime_value is not None:
                goal.customer_acquisition_goal_value_settings = _build_value_settings(
                    value, high_lifetime_value
                )
                update_paths.append("customer_acquisition_goal_value_settings")

            operation = CustomerLifecycleGoalOperation()
            if operation_type == "CREATE":
                operation.create = goal
            else:
                operation.update = goal
                if update_paths:
                    operation.update_mask.CopyFrom(
                        field_mask_pb2.FieldMask(paths=update_paths)
                    )

            request = ConfigureCustomerLifecycleGoalsRequest()
            request.customer_id = customer_id
            request.operation = operation
            if validate_only:
                request.validate_only = validate_only

            response: ConfigureCustomerLifecycleGoalsResponse = (
                self.client.configure_customer_lifecycle_goals(request=request)
            )

            await ctx.log(
                level="info",
                message=(
                    f"Configured customer lifecycle goal "
                    f"({operation_type}) for customer {customer_id}"
                ),
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to configure customer lifecycle goal: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_lifecycle_goal_tools(
    service: CustomerLifecycleGoalService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def configure_customer_lifecycle_goals(
        ctx: Context,
        customer_id: str,
        operation_type: str,
        value: Optional[float] = None,
        high_lifetime_value: Optional[float] = None,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Configure the account-level customer lifecycle goal.

        The CustomerLifecycleGoal is a singleton per account that drives
        Google Ads' customer-acquisition optimization. See
        https://support.google.com/google-ads/answer/12080169 for
        background on customer-acquisition goals.

        Args:
            customer_id: The customer ID
            operation_type: CREATE the first time, UPDATE thereafter.
            value: Incremental conversion value for non-high-value new
                customers.
            high_lifetime_value: Incremental conversion value for
                high-value new customers. Must be greater than ``value``
                if both are set.
            validate_only: If True, validate without executing.

        Returns:
            The serialized response with operation results.
        """
        return await service.configure_customer_lifecycle_goals(
            ctx=ctx,
            customer_id=customer_id,
            operation_type=operation_type,
            value=value,
            high_lifetime_value=high_lifetime_value,
            validate_only=validate_only,
        )

    tools.append(configure_customer_lifecycle_goals)
    return tools


def register_customer_lifecycle_goal_tools(
    mcp: FastMCP[Any],
) -> CustomerLifecycleGoalService:
    """Register customer lifecycle goal tools with the MCP server."""
    service = CustomerLifecycleGoalService()
    tools = create_customer_lifecycle_goal_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
