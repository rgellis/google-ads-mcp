"""Goal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.goal_common import (
    CustomerLifecycleOptimizationValueSettings,
)
from google.ads.googleads.v23.common.types.goal_setting import GoalSetting
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
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


def _build_retention_goal(
    additional_value: Optional[float],
    additional_high_lifetime_value: Optional[float],
) -> GoalSetting.RetentionGoal:
    """Build a RetentionGoal submessage from optional value parameters."""
    value_settings = CustomerLifecycleOptimizationValueSettings()
    if additional_value is not None:
        value_settings.additional_value = additional_value
    if additional_high_lifetime_value is not None:
        value_settings.additional_high_lifetime_value = additional_high_lifetime_value
    retention = GoalSetting.RetentionGoal()
    retention.value_settings = value_settings
    return retention


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
        operation_type: str,
        goal_resource_name: Optional[str] = None,
        retention_additional_value: Optional[float] = None,
        retention_additional_high_lifetime_value: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create or update an account-level retention Goal.

        Goal proto only has one settable submessage on the entity itself:
        ``retention_goal_settings`` (a oneof). Identity (``resource_name``,
        ``goal_id``, ``goal_type``, ``owner_customer``,
        ``optimization_eligibility``) is Output-only or Immutable.

        Note: MutateGoalsRequest does not support response_content_type —
        that parameter was removed because passing it was a silent no-op.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operation_type: "create" or "update"
            goal_resource_name: Goal resource name. Required for update.
            retention_additional_value: Incremental conversion value for
                lapsed customers who are not of high value.
            retention_additional_high_lifetime_value: Incremental conversion
                value for lapsed customers who ARE of high value. Should be
                greater than ``retention_additional_value`` if both are set.
            partial_failure: If true, valid mutations succeed even if some fail
            validate_only: If true, only validates without executing

        Returns:
            Mutation result
        """
        if operation_type not in ("create", "update"):
            raise ValueError(
                f"Unsupported operation_type: {operation_type!r}. Use 'create' or 'update'."
            )

        try:
            customer_id = format_customer_id(customer_id)

            has_value_params = (
                retention_additional_value is not None
                or retention_additional_high_lifetime_value is not None
            )

            operation = GoalOperation()

            if operation_type == "create":
                if not has_value_params:
                    raise ValueError(
                        "Goal create requires at least one of "
                        "retention_additional_value or "
                        "retention_additional_high_lifetime_value."
                    )
                goal = Goal()
                goal.retention_goal_settings = _build_retention_goal(
                    retention_additional_value,
                    retention_additional_high_lifetime_value,
                )
                operation.create = goal
            else:  # update
                if not goal_resource_name:
                    raise ValueError(
                        "goal_resource_name is required for update operations."
                    )
                if not has_value_params:
                    raise ValueError(
                        "Goal update requires at least one of "
                        "retention_additional_value or "
                        "retention_additional_high_lifetime_value."
                    )
                goal = Goal()
                goal.resource_name = goal_resource_name
                goal.retention_goal_settings = _build_retention_goal(
                    retention_additional_value,
                    retention_additional_high_lifetime_value,
                )
                # The retention_goal_settings.value_settings.* fields are the
                # only updatable paths on Goal.
                update_mask_paths: List[str] = []
                if retention_additional_value is not None:
                    update_mask_paths.append(
                        "retention_goal_settings.value_settings.additional_value"
                    )
                if retention_additional_high_lifetime_value is not None:
                    update_mask_paths.append(
                        "retention_goal_settings.value_settings.additional_high_lifetime_value"
                    )
                operation.update = goal
                operation.update_mask.CopyFrom(
                    field_mask_pb2.FieldMask(paths=update_mask_paths)
                )

            request = MutateGoalsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
            )

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
        operation_type: str,
        goal_resource_name: Optional[str] = None,
        retention_additional_value: Optional[float] = None,
        retention_additional_high_lifetime_value: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create or update an account-level retention Goal.

        The Goal resource only has the retention_goal_settings submessage as
        a settable field. Pass at least one of the retention_* parameters.

        Args:
            customer_id: The customer ID
            operation_type: "create" or "update"
            goal_resource_name: Goal resource name (required for update)
            retention_additional_value: Incremental conversion value for
                lapsed customers who are not of high value
            retention_additional_high_lifetime_value: Incremental conversion
                value for lapsed high-value customers. Should be greater than
                retention_additional_value if both are set.
            partial_failure: If true, valid mutations succeed even if some fail
            validate_only: If true, only validates without executing

        Returns:
            Mutation result with resource name
        """
        return await service.mutate_goals(
            ctx=ctx,
            customer_id=customer_id,
            operation_type=operation_type,
            goal_resource_name=goal_resource_name,
            retention_additional_value=retention_additional_value,
            retention_additional_high_lifetime_value=retention_additional_high_lifetime_value,
            partial_failure=partial_failure,
            validate_only=validate_only,
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
