"""Campaign lifecycle goal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.lifecycle_goals import (
    LifecycleGoalValueSettings,
)
from google.ads.googleads.v23.resources.types.campaign_lifecycle_goal import (
    CampaignLifecycleGoal,
    CustomerAcquisitionGoalSettings,
)
from google.ads.googleads.v23.services.services.campaign_lifecycle_goal_service import (
    CampaignLifecycleGoalServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_lifecycle_goal_service import (
    CampaignLifecycleGoalOperation,
    ConfigureCampaignLifecycleGoalsRequest,
    ConfigureCampaignLifecycleGoalsResponse,
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


class CampaignLifecycleGoalService:
    """Service for configuring campaign-level customer lifecycle goals.

    The CampaignLifecycleGoal resource attaches a customer-acquisition
    goal to a single campaign. The proto annotates most fields as
    ``Output only``, but per CLAUDE.md the Output-only annotation isn't
    always trustworthy — the operation docstring explicitly says the
    ``campaign`` field should be set on create, so we expose it.
    """

    def __init__(self) -> None:
        self._client: Optional[CampaignLifecycleGoalServiceClient] = None

    @property
    def client(self) -> CampaignLifecycleGoalServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignLifecycleGoalService")
        assert self._client is not None
        return self._client

    async def configure_campaign_lifecycle_goals(
        self,
        ctx: Context,
        customer_id: str,
        operation_type: str,
        campaign: Optional[str] = None,
        resource_name: Optional[str] = None,
        optimization_mode: Optional[str] = None,
        value: Optional[float] = None,
        high_lifetime_value: Optional[float] = None,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Configure a campaign lifecycle goal (create or update).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operation_type: ``CREATE`` or ``UPDATE``.
            campaign: Required for CREATE — resource name of the
                campaign the goal is attached to. Per the operation
                proto: "The campaign field should be set for this
                operation." For UPDATE the proto says it should NOT be
                set (the campaign is identified by resource_name).
            resource_name: Required for UPDATE — resource name of the
                existing CampaignLifecycleGoal
                (``customers/{customer_id}/campaignLifecycleGoal/{campaign_id}``).
            optimization_mode: Customer-acquisition optimization mode.
                One of TARGET_ALL_EQUALLY, BID_HIGHER_FOR_NEW_CUSTOMER,
                or TARGET_NEW_CUSTOMER.
            value: Incremental conversion value for new customers who
                are not high-value.
            high_lifetime_value: Incremental conversion value for
                high-value new customers. Must be greater than
                ``value`` if both are set.
            validate_only: If True, validate the request without
                executing it.

        Returns:
            The serialized ConfigureCampaignLifecycleGoalsResponse.
        """
        if operation_type not in {"CREATE", "UPDATE"}:
            raise ValueError(
                f"operation_type must be CREATE or UPDATE, got {operation_type!r}"
            )
        if operation_type == "CREATE" and not campaign:
            raise ValueError("operation_type=CREATE requires `campaign`.")
        if operation_type == "UPDATE" and not resource_name:
            raise ValueError("operation_type=UPDATE requires `resource_name`.")

        try:
            customer_id = format_customer_id(customer_id)

            goal = CampaignLifecycleGoal()
            if operation_type == "CREATE":
                goal.campaign = campaign  # type: ignore[assignment]
            else:
                goal.resource_name = resource_name  # type: ignore[assignment]

            update_paths: List[str] = []
            if (
                optimization_mode is not None
                or value is not None
                or high_lifetime_value is not None
            ):
                acquisition = CustomerAcquisitionGoalSettings()
                if optimization_mode is not None:
                    from google.ads.googleads.v23.enums.types.customer_acquisition_optimization_mode import (
                        CustomerAcquisitionOptimizationModeEnum,
                    )

                    acquisition.optimization_mode = getattr(
                        CustomerAcquisitionOptimizationModeEnum.CustomerAcquisitionOptimizationMode,
                        optimization_mode,
                    )
                    update_paths.append(
                        "customer_acquisition_goal_settings.optimization_mode"
                    )
                if value is not None or high_lifetime_value is not None:
                    acquisition.value_settings = _build_value_settings(
                        value, high_lifetime_value
                    )
                    update_paths.append(
                        "customer_acquisition_goal_settings.value_settings"
                    )
                goal.customer_acquisition_goal_settings = acquisition

            operation = CampaignLifecycleGoalOperation()
            if operation_type == "CREATE":
                operation.create = goal
            else:
                operation.update = goal
                if update_paths:
                    operation.update_mask.CopyFrom(
                        field_mask_pb2.FieldMask(paths=update_paths)
                    )

            request = ConfigureCampaignLifecycleGoalsRequest()
            request.customer_id = customer_id
            request.operation = operation
            if validate_only:
                request.validate_only = validate_only

            response: ConfigureCampaignLifecycleGoalsResponse = (
                self.client.configure_campaign_lifecycle_goals(request=request)
            )

            await ctx.log(
                level="info",
                message=(
                    f"Configured campaign lifecycle goal "
                    f"({operation_type}) for customer {customer_id}"
                ),
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to configure campaign lifecycle goal: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_lifecycle_goal_tools(
    service: CampaignLifecycleGoalService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def configure_campaign_lifecycle_goals(
        ctx: Context,
        customer_id: str,
        operation_type: str,
        campaign: Optional[str] = None,
        resource_name: Optional[str] = None,
        optimization_mode: Optional[str] = None,
        value: Optional[float] = None,
        high_lifetime_value: Optional[float] = None,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Configure a campaign customer-acquisition lifecycle goal.

        Use this to attach a customer-acquisition goal to a campaign or
        update an existing one. See
        https://support.google.com/google-ads/answer/12080169 for
        background on customer-acquisition goals.

        Args:
            customer_id: The customer ID
            operation_type: CREATE or UPDATE.
            campaign: Required for CREATE — resource name of the campaign.
            resource_name: Required for UPDATE — resource name of the
                existing CampaignLifecycleGoal.
            optimization_mode: Customer-acquisition optimization mode
                (TARGET_ALL_EQUALLY, BID_HIGHER_FOR_NEW_CUSTOMER, or
                TARGET_NEW_CUSTOMER).
            value: Incremental conversion value for non-high-value new
                customers.
            high_lifetime_value: Incremental conversion value for
                high-value new customers. Must be greater than ``value``
                if both are set.
            validate_only: If True, validate without executing.

        Returns:
            The serialized response with operation results.
        """
        return await service.configure_campaign_lifecycle_goals(
            ctx=ctx,
            customer_id=customer_id,
            operation_type=operation_type,
            campaign=campaign,
            resource_name=resource_name,
            optimization_mode=optimization_mode,
            value=value,
            high_lifetime_value=high_lifetime_value,
            validate_only=validate_only,
        )

    tools.append(configure_campaign_lifecycle_goals)
    return tools


def register_campaign_lifecycle_goal_tools(
    mcp: FastMCP[Any],
) -> CampaignLifecycleGoalService:
    """Register campaign lifecycle goal tools with the MCP server."""
    service = CampaignLifecycleGoalService()
    tools = create_campaign_lifecycle_goal_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
