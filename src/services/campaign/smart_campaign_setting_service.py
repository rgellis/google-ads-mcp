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
        phone_number: Optional[str] = None,
        phone_country_code: Optional[str] = None,
        advertising_language_code: Optional[str] = None,
        final_url: Optional[str] = None,
        ad_optimized_business_profile_include_lead_form: Optional[bool] = None,
        business_name: Optional[str] = None,
        business_profile_location: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update a Smart campaign setting.

        Per the v23 SmartCampaignSetting proto, the settable fields are:
        ``phone_number`` (sub-message with phone_number + country_code),
        ``advertising_language_code``, the ``landing_page`` oneof
        (``final_url`` OR ``ad_optimized_business_profile_setting``), and
        the ``business_setting`` oneof (``business_name`` OR
        ``business_profile_location``).

        Pass values to set; the wrapper builds the right submessages and a
        precise update_mask. Setting both members of a oneof raises.
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Enforce oneof exclusivity up-front so the wrapper doesn't
            # silently send a malformed payload.
            if final_url is not None and (
                ad_optimized_business_profile_include_lead_form is not None
            ):
                raise ValueError(
                    "final_url and ad_optimized_business_profile_include_lead_form "
                    "are members of the same `landing_page` oneof; pass only one."
                )
            if business_name is not None and business_profile_location is not None:
                raise ValueError(
                    "business_name and business_profile_location are members of "
                    "the same `business_setting` oneof; pass only one."
                )

            setting = SmartCampaignSetting()
            setting.resource_name = setting_resource_name

            update_mask_paths: List[str] = []

            if phone_number is not None or phone_country_code is not None:
                if phone_number is not None:
                    setting.phone_number.phone_number = phone_number
                    update_mask_paths.append("phone_number.phone_number")
                if phone_country_code is not None:
                    setting.phone_number.country_code = phone_country_code
                    update_mask_paths.append("phone_number.country_code")

            if advertising_language_code is not None:
                setting.advertising_language_code = advertising_language_code
                update_mask_paths.append("advertising_language_code")

            if final_url is not None:
                setting.final_url = final_url
                update_mask_paths.append("final_url")

            if ad_optimized_business_profile_include_lead_form is not None:
                setting.ad_optimized_business_profile_setting.include_lead_form = (
                    ad_optimized_business_profile_include_lead_form
                )
                update_mask_paths.append(
                    "ad_optimized_business_profile_setting.include_lead_form"
                )

            if business_name is not None:
                setting.business_name = business_name
                update_mask_paths.append("business_name")

            if business_profile_location is not None:
                setting.business_profile_location = business_profile_location
                update_mask_paths.append("business_profile_location")

            if not update_mask_paths:
                raise ValueError(
                    "At least one updatable field must be provided. Valid: "
                    "phone_number, phone_country_code, advertising_language_code, "
                    "final_url, ad_optimized_business_profile_include_lead_form, "
                    "business_name, business_profile_location."
                )

            operation = SmartCampaignSettingOperation()
            operation.update = setting
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
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
        """Get the status of a Smart campaign including eligibility and optimization score.

        Args:
            resource_name: Smart campaign setting resource name (e.g. customers/123/smartCampaignSettings/456)

        Returns:
            Smart campaign status details including optimization score and eligibility
        """
        return await service.get_smart_campaign_status(
            ctx=ctx, resource_name=resource_name
        )

    async def update_smart_campaign_setting(
        ctx: Context,
        customer_id: str,
        setting_resource_name: str,
        phone_number: Optional[str] = None,
        phone_country_code: Optional[str] = None,
        advertising_language_code: Optional[str] = None,
        final_url: Optional[str] = None,
        ad_optimized_business_profile_include_lead_form: Optional[bool] = None,
        business_name: Optional[str] = None,
        business_profile_location: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a Smart campaign setting.

        Pass values for the fields you want to change. The wrapper builds
        the right submessages and a precise update_mask. The two oneof
        groups are enforced:
          - landing_page: pass either final_url OR
            ad_optimized_business_profile_include_lead_form, not both
          - business_setting: pass either business_name OR
            business_profile_location, not both

        Args:
            customer_id: The customer ID
            setting_resource_name: Setting resource name (e.g.
                customers/123/smartCampaignSettings/456)
            phone_number: Smart campaign phone number
            phone_country_code: Two-letter ISO-3166 country code for the phone
            advertising_language_code: Two-letter language code (e.g. "en")
            final_url: User-provided landing page URL (landing_page oneof)
            ad_optimized_business_profile_include_lead_form: When True,
                enables lead-form on the business profile landing page
                (landing_page oneof)
            business_name: Name of the business (business_setting oneof)
            business_profile_location: Business Profile location resource
                name in form "locations/{locationId}"
                (business_setting oneof)

        Returns:
            Updated smart campaign setting details
        """
        return await service.update_smart_campaign_setting(
            ctx=ctx,
            customer_id=customer_id,
            setting_resource_name=setting_resource_name,
            phone_number=phone_number,
            phone_country_code=phone_country_code,
            advertising_language_code=advertising_language_code,
            final_url=final_url,
            ad_optimized_business_profile_include_lead_form=ad_optimized_business_profile_include_lead_form,
            business_name=business_name,
            business_profile_location=business_profile_location,
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
