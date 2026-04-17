"""Google Ads Custom Conversion Goal Service

This module provides functionality for managing custom conversion goals in Google Ads.
Custom conversion goals allow making arbitrary conversion actions biddable.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.custom_conversion_goal_status import (
    CustomConversionGoalStatusEnum,
)
from google.ads.googleads.v23.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v23.resources.types.custom_conversion_goal import (
    CustomConversionGoal,
)
from google.ads.googleads.v23.services.services.custom_conversion_goal_service import (
    CustomConversionGoalServiceClient,
)
from google.ads.googleads.v23.services.types.custom_conversion_goal_service import (
    CustomConversionGoalOperation,
    MutateCustomConversionGoalsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomConversionGoalService:
    """Service for managing Google Ads custom conversion goals."""

    def __init__(self) -> None:
        """Initialize the custom conversion goal service."""
        self._client: Optional[CustomConversionGoalServiceClient] = None

    @property
    def client(self) -> CustomConversionGoalServiceClient:
        """Get the custom conversion goal service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomConversionGoalService")
        assert self._client is not None
        return self._client

    async def mutate_custom_conversion_goals(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[CustomConversionGoalOperation],
        validate_only: bool = False,
        response_content_type: Optional[
            ResponseContentTypeEnum.ResponseContentType
        ] = None,
    ) -> Dict[str, Any]:
        """Mutate custom conversion goals.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of custom conversion goal operations
            validate_only: Whether to only validate the request
            response_content_type: The response content type setting

        Returns:
            Serialized response containing results
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateCustomConversionGoalsRequest(
                customer_id=customer_id,
                operations=operations,
                validate_only=validate_only,
            )

            if response_content_type is not None:
                request.response_content_type = response_content_type

            response = self.client.mutate_custom_conversion_goals(request=request)
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(response.results)} custom conversion goals",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate custom conversion goals: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def create_custom_conversion_goal_operation(
        self,
        name: str,
        conversion_actions: List[str],
        status: CustomConversionGoalStatusEnum.CustomConversionGoalStatus = CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED,
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for creation.

        Args:
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status of the custom conversion goal

        Returns:
            CustomConversionGoalOperation: The operation to create the custom conversion goal
        """
        custom_conversion_goal = CustomConversionGoal(
            name=name,
            conversion_actions=conversion_actions,
            status=status,
        )

        return CustomConversionGoalOperation(create=custom_conversion_goal)

    def update_custom_conversion_goal_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        conversion_actions: Optional[List[str]] = None,
        status: Optional[
            CustomConversionGoalStatusEnum.CustomConversionGoalStatus
        ] = None,
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for update.

        Args:
            resource_name: The custom conversion goal resource name
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status of the custom conversion goal

        Returns:
            CustomConversionGoalOperation: The operation to update the custom conversion goal
        """
        custom_conversion_goal = CustomConversionGoal(resource_name=resource_name)

        update_mask = []
        if name is not None:
            custom_conversion_goal.name = name
            update_mask.append("name")
        if conversion_actions is not None:
            custom_conversion_goal.conversion_actions = conversion_actions
            update_mask.append("conversion_actions")
        if status is not None:
            custom_conversion_goal.status = status
            update_mask.append("status")

        return CustomConversionGoalOperation(
            update=custom_conversion_goal,
            update_mask={"paths": update_mask},
        )

    def remove_custom_conversion_goal_operation(
        self, resource_name: str
    ) -> CustomConversionGoalOperation:
        """Create a custom conversion goal operation for removal.

        Args:
            resource_name: The custom conversion goal resource name

        Returns:
            CustomConversionGoalOperation: The operation to remove the custom conversion goal
        """
        return CustomConversionGoalOperation(remove=resource_name)


def create_custom_conversion_goal_tools(
    service: CustomConversionGoalService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create custom conversion goal tools for MCP."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    def _get_status_enum(
        status_str: str,
    ) -> CustomConversionGoalStatusEnum.CustomConversionGoalStatus:
        """Convert string to custom conversion goal status enum."""
        if status_str == "ENABLED":
            return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED
        elif status_str == "REMOVED":
            return CustomConversionGoalStatusEnum.CustomConversionGoalStatus.REMOVED
        else:
            raise ValueError(f"Invalid custom conversion goal status: {status_str}")

    async def mutate_custom_conversion_goals(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create, update, or remove custom conversion goals (groups of conversion actions for bidding).

        Args:
            customer_id: The customer ID
            operations: List of operations. Each dict must have:
                - operation_type: "create", "update", or "remove"
                For create:
                    - name: Goal name
                    - conversion_actions: List of conversion action resource names
                    - status: ENABLED or REMOVED (default: ENABLED)
                For update:
                    - resource_name: The custom conversion goal resource name
                    - name, conversion_actions, status: Fields to update (all optional)
                For remove:
                    - resource_name: The custom conversion goal resource name
            validate_only: Only validate the request

        Returns:
            Mutation results with resource names
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                status = (
                    CustomConversionGoalStatusEnum.CustomConversionGoalStatus.ENABLED
                )
                if "status" in op_data:
                    status = _get_status_enum(op_data["status"])

                operation = service.create_custom_conversion_goal_operation(
                    name=op_data["name"],
                    conversion_actions=op_data["conversion_actions"],
                    status=status,
                )
            elif op_type == "update":
                status_val = None
                if "status" in op_data:
                    status_val = _get_status_enum(op_data["status"])

                operation = service.update_custom_conversion_goal_operation(
                    resource_name=op_data["resource_name"],
                    name=op_data.get("name"),
                    conversion_actions=op_data.get("conversion_actions"),
                    status=status_val,
                )
            elif op_type == "remove":
                operation = service.remove_custom_conversion_goal_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        return await service.mutate_custom_conversion_goals(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            validate_only=validate_only,
        )

    tools.append(mutate_custom_conversion_goals)

    async def create_custom_conversion_goal(
        ctx: Context,
        customer_id: str,
        name: str,
        conversion_actions: list[str],
        status: str = "ENABLED",
    ) -> Dict[str, Any]:
        """Create a new custom conversion goal.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status (ENABLED or REMOVED)

        Returns:
            Serialized response with created custom conversion goal details
        """
        operation = service.create_custom_conversion_goal_operation(
            name=name,
            conversion_actions=conversion_actions,
            status=_get_status_enum(status),
        )

        return await service.mutate_custom_conversion_goals(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(create_custom_conversion_goal)

    async def update_custom_conversion_goal(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        name: Optional[str] = None,
        conversion_actions: Optional[list[str]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing custom conversion goal.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The custom conversion goal resource name
            name: The name for this custom conversion goal
            conversion_actions: List of conversion action resource names
            status: The status (ENABLED or REMOVED)

        Returns:
            Serialized response with updated custom conversion goal details
        """
        status_enum = None
        if status is not None:
            status_enum = _get_status_enum(status)

        operation = service.update_custom_conversion_goal_operation(
            resource_name=resource_name,
            name=name,
            conversion_actions=conversion_actions,
            status=status_enum,
        )

        return await service.mutate_custom_conversion_goals(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(update_custom_conversion_goal)

    async def remove_custom_conversion_goal(
        ctx: Context,
        customer_id: str,
        resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a custom conversion goal.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The custom conversion goal resource name

        Returns:
            Serialized response confirming removal
        """
        operation = service.remove_custom_conversion_goal_operation(
            resource_name=resource_name
        )

        return await service.mutate_custom_conversion_goals(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(remove_custom_conversion_goal)

    return tools


def register_custom_conversion_goal_tools(
    mcp: FastMCP[Any],
) -> CustomConversionGoalService:
    """Register custom conversion goal tools with the MCP server."""
    service = CustomConversionGoalService()
    tools = create_custom_conversion_goal_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
