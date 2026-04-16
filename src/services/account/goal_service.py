"""Goal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.goal import Goal
from google.ads.googleads.v23.services.services.goal_service import (
    GoalServiceClient,
)
from google.ads.googleads.v23.services.types.goal_service import (
    GoalOperation,
    MutateGoalsRequest,
    MutateGoalsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class GoalService:
    """Service for managing account-level goals."""

    def __init__(self) -> None:
        self._client: Optional[GoalServiceClient] = None

    @property
    def client(self) -> GoalServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("GoalService")
        assert self._client is not None
        return self._client

    async def mutate_goals(
        self,
        ctx: Context,
        customer_id: str,
        goal_resource_name: Optional[str] = None,
        operation_type: str = "create",
    ) -> Dict[str, Any]:
        """Create or update account-level goals.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            goal_resource_name: Goal resource name (for update)
            operation_type: create or update

        Returns:
            Mutation result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = GoalOperation()

            if operation_type == "create":
                goal = Goal()
                operation.create = goal
            elif operation_type == "update" and goal_resource_name:
                goal = Goal()
                goal.resource_name = goal_resource_name
                operation.update = goal
                operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=[]))

            request = MutateGoalsRequest()
            request.customer_id = customer_id
            request.operations = [operation]

            response: MutateGoalsResponse = self.client.mutate_goals(request=request)

            await ctx.log(
                level="info",
                message=f"Mutated goal for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate goal: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_goal_tools(
    service: GoalService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the goal service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_goal(
        ctx: Context,
        customer_id: str,
        goal_resource_name: Optional[str] = None,
        operation_type: str = "create",
    ) -> Dict[str, Any]:
        """Create or update account-level goals.

        Args:
            customer_id: The customer ID
            goal_resource_name: Goal resource name (for update)
            operation_type: create or update

        Returns:
            Mutation result
        """
        return await service.mutate_goals(
            ctx=ctx,
            customer_id=customer_id,
            goal_resource_name=goal_resource_name,
            operation_type=operation_type,
        )

    tools.append(mutate_goal)
    return tools


def register_goal_tools(mcp: FastMCP[Any]) -> GoalService:
    """Register goal tools with the MCP server."""
    service = GoalService()
    tools = create_goal_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
