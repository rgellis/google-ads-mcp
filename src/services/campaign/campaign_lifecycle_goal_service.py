"""Campaign lifecycle goal service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.campaign_lifecycle_goal import (
    CampaignLifecycleGoal,
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
    set_request_options,
)

logger = get_logger(__name__)


class CampaignLifecycleGoalService:
    """Service for configuring campaign lifecycle goals."""

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
        campaign_resource_name: str,
        operation_type: str = "create",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            operation = CampaignLifecycleGoalOperation()
            if operation_type == "create":
                goal = CampaignLifecycleGoal()
                operation.create = goal
            elif operation_type == "update":
                goal = CampaignLifecycleGoal()
                goal.resource_name = campaign_resource_name
                operation.update = goal
                operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=[]))
            request = ConfigureCampaignLifecycleGoalsRequest()
            request.customer_id = customer_id
            request.operation = operation
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            response: ConfigureCampaignLifecycleGoalsResponse = (
                self.client.configure_campaign_lifecycle_goals(request=request)
            )
            await ctx.log(
                level="info",
                message=f"Configured campaign lifecycle goal for {campaign_resource_name}",
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

    async def configure_campaign_lifecycle_goal(
        ctx: Context,
        customer_id: str,
        campaign_resource_name: str,
        operation_type: str = "create",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Configure campaign lifecycle goals (acquisition/retention).

        Args:
            customer_id: The customer ID
            campaign_resource_name: Campaign resource name
            operation_type: create or update
        """
        return await service.configure_campaign_lifecycle_goals(
            ctx=ctx,
            customer_id=customer_id,
            campaign_resource_name=campaign_resource_name,
            operation_type=operation_type,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.append(configure_campaign_lifecycle_goal)
    return tools


def register_campaign_lifecycle_goal_tools(
    mcp: FastMCP[Any],
) -> CampaignLifecycleGoalService:
    service = CampaignLifecycleGoalService()
    tools = create_campaign_lifecycle_goal_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
