"""Customer lifecycle goal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.customer_lifecycle_goal import (
    CustomerLifecycleGoal,
)
from google.ads.googleads.v23.services.services.customer_lifecycle_goal_service import (
    CustomerLifecycleGoalServiceClient,
)
from google.ads.googleads.v23.services.types.customer_lifecycle_goal_service import (
    CustomerLifecycleGoalOperation,
    ConfigureCustomerLifecycleGoalsRequest,
    ConfigureCustomerLifecycleGoalsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerLifecycleGoalService:
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
        self, ctx: Context, customer_id: str, operation_type: str = "create"
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            operation = CustomerLifecycleGoalOperation()
            if operation_type == "create":
                goal = CustomerLifecycleGoal()
                operation.create = goal
            elif operation_type == "update":
                goal = CustomerLifecycleGoal()
                goal.resource_name = f"customers/{customer_id}/customerLifecycleGoals"
                operation.update = goal
                operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=[]))
            request = ConfigureCustomerLifecycleGoalsRequest()
            request.customer_id = customer_id
            request.operation = operation
            response: ConfigureCustomerLifecycleGoalsResponse = (
                self.client.configure_customer_lifecycle_goals(request=request)
            )
            await ctx.log(
                level="info",
                message=f"Configured customer lifecycle goal for {customer_id}",
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

    async def configure_customer_lifecycle_goal(
        ctx: Context, customer_id: str, operation_type: str = "create"
    ) -> Dict[str, Any]:
        """Configure customer lifecycle goals (acquisition/retention).

        Args:
            customer_id: The customer ID
            operation_type: create or update
        """
        return await service.configure_customer_lifecycle_goals(
            ctx=ctx, customer_id=customer_id, operation_type=operation_type
        )

    tools.append(configure_customer_lifecycle_goal)
    return tools


def register_customer_lifecycle_goal_tools(
    mcp: FastMCP[Any],
) -> CustomerLifecycleGoalService:
    service = CustomerLifecycleGoalService()
    tools = create_customer_lifecycle_goal_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
