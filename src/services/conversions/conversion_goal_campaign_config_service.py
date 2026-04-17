"""Google Ads Conversion Goal Campaign Config Service

This module provides functionality for managing conversion goal campaign configurations in Google Ads.
Conversion goal campaign configs define how campaigns use conversion goals for optimization.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.goal_config_level import GoalConfigLevelEnum
from google.ads.googleads.v23.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v23.resources.types.conversion_goal_campaign_config import (
    ConversionGoalCampaignConfig,
)
from google.ads.googleads.v23.services.services.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigServiceClient,
)
from google.ads.googleads.v23.services.types.conversion_goal_campaign_config_service import (
    ConversionGoalCampaignConfigOperation,
    MutateConversionGoalCampaignConfigsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ConversionGoalCampaignConfigService:
    """Service for managing Google Ads conversion goal campaign configurations."""

    def __init__(self) -> None:
        """Initialize the conversion goal campaign config service."""
        self._client: Optional[ConversionGoalCampaignConfigServiceClient] = None

    @property
    def client(self) -> ConversionGoalCampaignConfigServiceClient:
        """Get the conversion goal campaign config service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "ConversionGoalCampaignConfigService"
            )
        assert self._client is not None
        return self._client

    async def mutate_conversion_goal_campaign_configs(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[ConversionGoalCampaignConfigOperation],
        validate_only: bool = False,
        response_content_type: Optional[
            ResponseContentTypeEnum.ResponseContentType
        ] = None,
    ) -> Dict[str, Any]:
        """Mutate conversion goal campaign configurations.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of conversion goal campaign config operations
            validate_only: Whether to only validate the request
            response_content_type: The response content type setting

        Returns:
            Serialized response containing results
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateConversionGoalCampaignConfigsRequest(
                customer_id=customer_id,
                operations=operations,
                validate_only=validate_only,
            )

            if response_content_type is not None:
                request.response_content_type = response_content_type

            response = self.client.mutate_conversion_goal_campaign_configs(
                request=request
            )
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(response.results)} conversion goal campaign configs",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate conversion goal campaign configs: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def update_conversion_goal_campaign_config_operation(
        self,
        resource_name: str,
        goal_config_level: Optional[GoalConfigLevelEnum.GoalConfigLevel] = None,
        custom_conversion_goal: Optional[str] = None,
    ) -> ConversionGoalCampaignConfigOperation:
        """Create a conversion goal campaign config operation for update.

        Args:
            resource_name: The conversion goal campaign config resource name
            goal_config_level: The level of goal config the campaign is using
            custom_conversion_goal: The custom conversion goal resource name

        Returns:
            ConversionGoalCampaignConfigOperation: The operation to update the conversion goal campaign config
        """
        conversion_goal_campaign_config = ConversionGoalCampaignConfig(
            resource_name=resource_name
        )

        update_mask = []
        if goal_config_level is not None:
            conversion_goal_campaign_config.goal_config_level = goal_config_level
            update_mask.append("goal_config_level")
        if custom_conversion_goal is not None:
            conversion_goal_campaign_config.custom_conversion_goal = (
                custom_conversion_goal
            )
            update_mask.append("custom_conversion_goal")

        return ConversionGoalCampaignConfigOperation(
            update=conversion_goal_campaign_config,
            update_mask={"paths": update_mask},
        )


def create_conversion_goal_campaign_config_tools(
    service: ConversionGoalCampaignConfigService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create conversion goal campaign config tools for MCP."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    def _get_goal_config_level_enum(
        level_str: str,
    ) -> GoalConfigLevelEnum.GoalConfigLevel:
        """Convert string to goal config level enum."""
        if level_str == "CUSTOMER":
            return GoalConfigLevelEnum.GoalConfigLevel.CUSTOMER
        elif level_str == "CAMPAIGN":
            return GoalConfigLevelEnum.GoalConfigLevel.CAMPAIGN
        else:
            raise ValueError(f"Invalid goal config level: {level_str}")

    async def mutate_conversion_goal_campaign_configs(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Update conversion goal configurations at the campaign level.

        Controls which conversion goals a campaign optimizes for, overriding account-level defaults.

        Args:
            customer_id: The customer ID
            operations: List of update operations. Each dict must have:
                - operation_type: "update"
                - resource_name: The conversion goal campaign config resource name
                - goal_config_level: CUSTOMER (use account goals) or CAMPAIGN (use campaign-specific goals)
                - custom_conversion_goal: Custom conversion goal resource name (optional)
            validate_only: Only validate the request

        Returns:
            Mutation results with updated resource names
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "update":
                goal_config_level = None
                if "goal_config_level" in op_data:
                    goal_config_level = _get_goal_config_level_enum(
                        op_data["goal_config_level"]
                    )

                operation = service.update_conversion_goal_campaign_config_operation(
                    resource_name=op_data["resource_name"],
                    goal_config_level=goal_config_level,
                    custom_conversion_goal=op_data.get("custom_conversion_goal"),
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        return await service.mutate_conversion_goal_campaign_configs(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            validate_only=validate_only,
        )

    tools.append(mutate_conversion_goal_campaign_configs)

    async def update_conversion_goal_campaign_config(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        goal_config_level: Optional[str] = None,
        custom_conversion_goal: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a conversion goal campaign configuration.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The conversion goal campaign config resource name
            goal_config_level: The level of goal config (CUSTOMER or CAMPAIGN)
            custom_conversion_goal: The custom conversion goal resource name

        Returns:
            Serialized response with updated conversion goal campaign config details
        """
        goal_config_level_enum = None
        if goal_config_level is not None:
            goal_config_level_enum = _get_goal_config_level_enum(goal_config_level)

        operation = service.update_conversion_goal_campaign_config_operation(
            resource_name=resource_name,
            goal_config_level=goal_config_level_enum,
            custom_conversion_goal=custom_conversion_goal,
        )

        return await service.mutate_conversion_goal_campaign_configs(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(update_conversion_goal_campaign_config)

    return tools


def register_conversion_goal_campaign_config_tools(
    mcp: FastMCP[Any],
) -> ConversionGoalCampaignConfigService:
    """Register conversion goal campaign config tools with the MCP server."""
    service = ConversionGoalCampaignConfigService()
    tools = create_conversion_goal_campaign_config_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
