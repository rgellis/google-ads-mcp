"""Smart campaign setting service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.smart_campaign_setting import (
    SmartCampaignSetting,
)
from google.ads.googleads.v23.services.services.smart_campaign_setting_service import (
    SmartCampaignSettingServiceClient,
)
from google.ads.googleads.v23.services.types.smart_campaign_setting_service import (
    GetSmartCampaignStatusRequest,
    GetSmartCampaignStatusResponse,
    MutateSmartCampaignSettingsRequest,
    MutateSmartCampaignSettingsResponse,
    SmartCampaignSettingOperation,
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


class SmartCampaignSettingService:
    def __init__(self) -> None:
        self._client: Optional[SmartCampaignSettingServiceClient] = None

    @property
    def client(self) -> SmartCampaignSettingServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("SmartCampaignSettingService")
        assert self._client is not None
        return self._client

    async def get_smart_campaign_status(
        self, ctx: Context, resource_name: str
    ) -> Dict[str, Any]:
        try:
            request = GetSmartCampaignStatusRequest()
            request.resource_name = resource_name
            response: GetSmartCampaignStatusResponse = (
                self.client.get_smart_campaign_status(request=request)
            )
            await ctx.log(
                level="info", message=f"Got smart campaign status for {resource_name}"
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get smart campaign status: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_smart_campaign_setting(
        self,
        ctx: Context,
        customer_id: str,
        setting_resource_name: str,
        update_fields: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            setting = SmartCampaignSetting()
            setting.resource_name = setting_resource_name
            operation = SmartCampaignSettingOperation()
            operation.update = setting
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_fields)
            )
            request = MutateSmartCampaignSettingsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            response: MutateSmartCampaignSettingsResponse = (
                self.client.mutate_smart_campaign_settings(request=request)
            )
            await ctx.log(
                level="info",
                message=f"Updated smart campaign setting {setting_resource_name}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update smart campaign setting: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_smart_campaign_setting_tools(
    service: SmartCampaignSettingService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def get_smart_campaign_status(
        ctx: Context, resource_name: str
    ) -> Dict[str, Any]:
        """Get the status of a Smart campaign.

        Args:
            resource_name: Smart campaign setting resource name
        """
        return await service.get_smart_campaign_status(
            ctx=ctx, resource_name=resource_name
        )

    async def update_smart_campaign_setting(
        ctx: Context,
        customer_id: str,
        setting_resource_name: str,
        update_fields: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a Smart campaign setting.

        Args:
            customer_id: The customer ID
            setting_resource_name: Setting resource name
            update_fields: List of field paths to update
        """
        return await service.update_smart_campaign_setting(
            ctx=ctx,
            customer_id=customer_id,
            setting_resource_name=setting_resource_name,
            update_fields=update_fields,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([get_smart_campaign_status, update_smart_campaign_setting])
    return tools


def register_smart_campaign_setting_tools(
    mcp: FastMCP[Any],
) -> SmartCampaignSettingService:
    service = SmartCampaignSettingService()
    tools = create_smart_campaign_setting_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
