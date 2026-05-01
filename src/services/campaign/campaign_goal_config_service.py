"""Campaign goal config service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.campaign_goal_settings import (
    CampaignGoalSettings,
)
from google.ads.googleads.v23.common.types.goal_common import (
    CustomerLifecycleOptimizationValueSettings,
)
from google.ads.googleads.v23.enums.types.customer_lifecycle_optimization_mode import (
    CustomerLifecycleOptimizationModeEnum,
)
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


def _build_campaign_retention_settings(
    additional_value: Optional[float],
    additional_high_lifetime_value: Optional[float],
    target_option: Optional[str],
) -> CampaignGoalSettings.CampaignRetentionGoalSettings:
    """Build the CampaignRetentionGoalSettings submessage from optional params."""
    settings = CampaignGoalSettings.CampaignRetentionGoalSettings()
    if additional_value is not None or additional_high_lifetime_value is not None:
        value_override = CustomerLifecycleOptimizationValueSettings()
        if additional_value is not None:
            value_override.additional_value = additional_value
        if additional_high_lifetime_value is not None:
            value_override.additional_high_lifetime_value = (
                additional_high_lifetime_value
            )
        settings.value_settings_override = value_override
    if target_option is not None:
        settings.target_option = getattr(
            CustomerLifecycleOptimizationModeEnum.CustomerLifecycleOptimizationMode,
            target_option,
        )
    return settings


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
        operation_type: str,
        campaign_resource_name: Optional[str] = None,
        goal_resource_name: Optional[str] = None,
        config_resource_name: Optional[str] = None,
        retention_additional_value: Optional[float] = None,
        retention_additional_high_lifetime_value: Optional[float] = None,
        retention_target_option: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create, update, or remove a campaign goal config.

        Per the v23 proto, ``campaign`` and ``goal`` are Immutable: settable
        only on create. ``goal_type`` is Output-only. The only mutable
        submessage is ``campaign_retention_settings``.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operation_type: "create", "update", or "remove"
            campaign_resource_name: Campaign resource name. Required for
                create. The campaign field is Immutable.
            goal_resource_name: Goal resource name. Required for create.
                The goal field is Immutable.
            config_resource_name: CampaignGoalConfig resource name (form:
                ``customers/{cid}/campaignGoalConfigs/{campaign_id}~{goal_id}``).
                Required for update and remove.
            retention_additional_value: Override the goal's additional_value
                for this campaign.
            retention_additional_high_lifetime_value: Override the goal's
                additional_high_lifetime_value for this campaign.
            retention_target_option: TARGET_ALL or TARGET_HIGH_LIFETIME_VALUE
                (defaults to TARGET_ALL on the API side).
            partial_failure: passthrough
            validate_only: passthrough
            response_content_type: passthrough

        Returns:
            Mutation result
        """
        if operation_type not in ("create", "update", "remove"):
            raise ValueError(
                f"Unsupported operation_type: {operation_type!r}. "
                "Use 'create', 'update', or 'remove'."
            )

        try:
            customer_id = format_customer_id(customer_id)

            has_retention_params = (
                retention_additional_value is not None
                or retention_additional_high_lifetime_value is not None
                or retention_target_option is not None
            )

            operation = CampaignGoalConfigOperation()

            if operation_type == "create":
                if not campaign_resource_name:
                    raise ValueError("campaign_resource_name is required for create.")
                if not goal_resource_name:
                    raise ValueError("goal_resource_name is required for create.")
                config = CampaignGoalConfig()
                config.campaign = campaign_resource_name
                config.goal = goal_resource_name
                if has_retention_params:
                    config.campaign_retention_settings = (
                        _build_campaign_retention_settings(
                            retention_additional_value,
                            retention_additional_high_lifetime_value,
                            retention_target_option,
                        )
                    )
                operation.create = config

            elif operation_type == "update":
                if not config_resource_name:
                    raise ValueError("config_resource_name is required for update.")
                if not has_retention_params:
                    raise ValueError(
                        "Update requires at least one of "
                        "retention_additional_value, "
                        "retention_additional_high_lifetime_value, or "
                        "retention_target_option."
                    )
                config = CampaignGoalConfig()
                config.resource_name = config_resource_name
                config.campaign_retention_settings = _build_campaign_retention_settings(
                    retention_additional_value,
                    retention_additional_high_lifetime_value,
                    retention_target_option,
                )
                update_mask_paths: List[str] = []
                if retention_additional_value is not None:
                    update_mask_paths.append(
                        "campaign_retention_settings.value_settings_override.additional_value"
                    )
                if retention_additional_high_lifetime_value is not None:
                    update_mask_paths.append(
                        "campaign_retention_settings.value_settings_override.additional_high_lifetime_value"
                    )
                if retention_target_option is not None:
                    update_mask_paths.append(
                        "campaign_retention_settings.target_option"
                    )
                operation.update = config
                operation.update_mask.CopyFrom(
                    field_mask_pb2.FieldMask(paths=update_mask_paths)
                )

            else:  # remove
                if not config_resource_name:
                    raise ValueError("config_resource_name is required for remove.")
                operation.remove = config_resource_name

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
                message=f"Mutated campaign goal config ({operation_type})",
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
        operation_type: str,
        campaign_resource_name: Optional[str] = None,
        goal_resource_name: Optional[str] = None,
        config_resource_name: Optional[str] = None,
        retention_additional_value: Optional[float] = None,
        retention_additional_high_lifetime_value: Optional[float] = None,
        retention_target_option: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create, update, or remove a campaign goal configuration.

        Per the v23 proto, ``campaign`` and ``goal`` are Immutable: settable
        only on create. The only mutable submessage is
        ``campaign_retention_settings``.

        Args:
            customer_id: The customer ID
            operation_type: "create", "update", or "remove"
            campaign_resource_name: Campaign resource name (required for create)
            goal_resource_name: Goal resource name (required for create)
            config_resource_name: CampaignGoalConfig resource name (form:
                customers/{cid}/campaignGoalConfigs/{campaign_id}~{goal_id}).
                Required for update and remove.
            retention_additional_value: Override the goal's additional_value
                for this campaign
            retention_additional_high_lifetime_value: Override the goal's
                additional_high_lifetime_value for this campaign
            retention_target_option: TARGET_ALL or TARGET_HIGH_LIFETIME_VALUE
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        return await service.mutate_campaign_goal_configs(
            ctx=ctx,
            customer_id=customer_id,
            operation_type=operation_type,
            campaign_resource_name=campaign_resource_name,
            goal_resource_name=goal_resource_name,
            config_resource_name=config_resource_name,
            retention_additional_value=retention_additional_value,
            retention_additional_high_lifetime_value=retention_additional_high_lifetime_value,
            retention_target_option=retention_target_option,
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
