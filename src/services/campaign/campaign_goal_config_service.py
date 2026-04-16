"""Campaign goal config service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.campaign_goal_config import (
    CampaignGoalConfig,
)
from google.ads.googleads.v23.services.services.campaign_goal_config_service import (
    CampaignGoalConfigServiceClient,
)
from google.ads.googleads.v23.services.types.campaign_goal_config_service import (
    CampaignGoalConfigOperation,
    MutateCampaignGoalConfigsRequest,
    MutateCampaignGoalConfigsResponse,
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


class CampaignGoalConfigService:
    """Service for managing campaign goal configurations."""

    def __init__(self) -> None:
        self._client: Optional[CampaignGoalConfigServiceClient] = None

    @property
    def client(self) -> CampaignGoalConfigServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CampaignGoalConfigService")
        assert self._client is not None
        return self._client

    async def mutate_campaign_goal_configs(
        self,
        ctx: Context,
        customer_id: str,
        campaign_resource_name: str,
        goal_resource_name: Optional[str] = None,
        operation_type: str = "create",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create, update, or remove a campaign goal config.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_resource_name: Campaign resource name
            goal_resource_name: Goal resource name (for create/update)
            operation_type: create, update, or remove

        Returns:
            Mutation result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = CampaignGoalConfigOperation()

            if operation_type == "create":
                config = CampaignGoalConfig()
                config.campaign = campaign_resource_name
                if goal_resource_name:
                    config.goal = goal_resource_name
                operation.create = config
            elif operation_type == "update":
                config = CampaignGoalConfig()
                config.resource_name = campaign_resource_name
                operation.update = config
                operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=[]))
            elif operation_type == "remove":
                # resource_name should be a campaign_goal_config resource name
                operation.remove = campaign_resource_name

            request = MutateCampaignGoalConfigsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCampaignGoalConfigsResponse = (
                self.client.mutate_campaign_goal_configs(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Mutated campaign goal config for {campaign_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate campaign goal config: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_campaign_goal_config_tools(
    service: CampaignGoalConfigService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the campaign goal config service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_campaign_goal_config(
        ctx: Context,
        customer_id: str,
        campaign_resource_name: str,
        goal_resource_name: Optional[str] = None,
        operation_type: str = "create",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create, update, or remove a campaign goal configuration.

        Args:
            customer_id: The customer ID
            campaign_resource_name: Campaign resource name
            goal_resource_name: Goal resource name (for create/update)
            operation_type: create, update, or remove

        Returns:
            Mutation result
        """
        return await service.mutate_campaign_goal_configs(
            ctx=ctx,
            customer_id=customer_id,
            campaign_resource_name=campaign_resource_name,
            goal_resource_name=goal_resource_name,
            operation_type=operation_type,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.append(mutate_campaign_goal_config)
    return tools


def register_campaign_goal_config_tools(
    mcp: FastMCP[Any],
) -> CampaignGoalConfigService:
    """Register campaign goal config tools with the MCP server."""
    service = CampaignGoalConfigService()
    tools = create_campaign_goal_config_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
