"""Conversion value rule service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.conversion_value_rule_status import (
    ConversionValueRuleStatusEnum,
)
from google.ads.googleads.v23.enums.types.value_rule_operation import (
    ValueRuleOperationEnum,
)
from google.ads.googleads.v23.resources.types.conversion_value_rule import (
    ConversionValueRule,
)
from google.ads.googleads.v23.services.services.conversion_value_rule_service import (
    ConversionValueRuleServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.conversion_value_rule_service import (
    ConversionValueRuleOperation,
    MutateConversionValueRulesRequest,
    MutateConversionValueRulesResponse,
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


class ConversionValueRuleService:
    """Conversion value rule service for managing conversion value adjustments."""

    def __init__(self) -> None:
        """Initialize the conversion value rule service."""
        self._client: Optional[ConversionValueRuleServiceClient] = None

    @property
    def client(self) -> ConversionValueRuleServiceClient:
        """Get the conversion value rule service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ConversionValueRuleService")
        assert self._client is not None
        return self._client

    async def create_conversion_value_rule(
        self,
        ctx: Context,
        customer_id: str,
        action_operation: str,
        action_value: float,
        status: ConversionValueRuleStatusEnum.ConversionValueRuleStatus = ConversionValueRuleStatusEnum.ConversionValueRuleStatus.ENABLED,
        device_types: Optional[List[str]] = None,
        geo_location_geo_target_constants: Optional[List[str]] = None,
        audience_user_lists: Optional[List[str]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a conversion value rule.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            action_operation: Value rule operation - ADD, MULTIPLY, or SET
            action_value: The value to add/multiply/set
            status: Rule status enum value
            device_types: Optional list of device types (MOBILE, DESKTOP, TABLET)
            geo_location_geo_target_constants: Optional list of geo target constant resource names
            audience_user_lists: Optional list of user list resource names

        Returns:
            Created conversion value rule details
        """
        try:
            customer_id = format_customer_id(customer_id)

            rule = ConversionValueRule()
            rule.status = status

            # Set action
            rule.action.operation = getattr(
                ValueRuleOperationEnum.ValueRuleOperation, action_operation
            )
            rule.action.value = action_value

            # Set conditions
            if device_types:
                from google.ads.googleads.v23.enums.types.value_rule_device_type import (
                    ValueRuleDeviceTypeEnum,
                )

                for dt in device_types:
                    rule.device_condition.device_types.append(
                        getattr(ValueRuleDeviceTypeEnum.ValueRuleDeviceType, dt)
                    )

            if geo_location_geo_target_constants:
                for geo_constant in geo_location_geo_target_constants:
                    rule.geo_location_condition.geo_target_constants.append(
                        geo_constant
                    )

            if audience_user_lists:
                for user_list in audience_user_lists:
                    rule.audience_condition.user_lists.append(user_list)

            operation = ConversionValueRuleOperation()
            operation.create = rule

            request = MutateConversionValueRulesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateConversionValueRulesResponse = (
                self.client.mutate_conversion_value_rules(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created conversion value rule with {action_operation} {action_value}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create conversion value rule: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_conversion_value_rule(
        self,
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
        status: Optional[
            ConversionValueRuleStatusEnum.ConversionValueRuleStatus
        ] = None,
        action_operation: Optional[str] = None,
        action_value: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update a conversion value rule.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to update
            status: Optional new status
            action_operation: Optional new operation (ADD, MULTIPLY, SET)
            action_value: Optional new value

        Returns:
            Updated conversion value rule details
        """
        try:
            customer_id = format_customer_id(customer_id)

            rule = ConversionValueRule()
            rule.resource_name = rule_resource_name

            update_mask_fields = []

            if status is not None:
                rule.status = status
                update_mask_fields.append("status")

            if action_operation is not None:
                rule.action.operation = getattr(
                    ValueRuleOperationEnum.ValueRuleOperation, action_operation
                )
                update_mask_fields.append("action.operation")

            if action_value is not None:
                rule.action.value = action_value
                update_mask_fields.append("action.value")

            operation = ConversionValueRuleOperation()
            operation.update = rule
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            request = MutateConversionValueRulesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateConversionValueRulesResponse = (
                self.client.mutate_conversion_value_rules(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Updated conversion value rule {rule_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update conversion value rule: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_conversion_value_rules(
        self,
        ctx: Context,
        customer_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List conversion value rules.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            limit: Maximum number of results

        Returns:
            List of conversion value rules
        """
        try:
            customer_id = format_customer_id(customer_id)

            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            query = f"""
                SELECT
                    conversion_value_rule.resource_name,
                    conversion_value_rule.id,
                    conversion_value_rule.action.operation,
                    conversion_value_rule.action.value,
                    conversion_value_rule.status,
                    conversion_value_rule.owner_customer
                FROM conversion_value_rule
                LIMIT {limit}
            """

            response = google_ads_service.search(customer_id=customer_id, query=query)

            rules = []
            for row in response:
                rules.append(serialize_proto_message(row.conversion_value_rule))

            await ctx.log(
                level="info",
                message=f"Found {len(rules)} conversion value rules",
            )

            return rules

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list conversion value rules: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_conversion_value_rule(
        self,
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a conversion value rule.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = ConversionValueRuleOperation()
            operation.remove = rule_resource_name

            request = MutateConversionValueRulesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateConversionValueRulesResponse = (
                self.client.mutate_conversion_value_rules(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed conversion value rule: {rule_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove conversion value rule: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_conversion_value_rule_tools(
    service: ConversionValueRuleService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the conversion value rule service."""
    tools = []

    async def create_conversion_value_rule(
        ctx: Context,
        customer_id: str,
        action_operation: str,
        action_value: float,
        status: str = "ENABLED",
        device_types: Optional[List[str]] = None,
        geo_location_geo_target_constants: Optional[List[str]] = None,
        audience_user_lists: Optional[List[str]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a conversion value rule to adjust conversion values.

        Args:
            customer_id: The customer ID
            action_operation: Value operation - ADD, MULTIPLY, or SET
            action_value: The value to apply (e.g. 10.0 for ADD $10, 1.5 for MULTIPLY 1.5x)
            status: Rule status - ENABLED, PAUSED, or REMOVED
            device_types: Optional device filter - MOBILE, DESKTOP, TABLET
            geo_location_geo_target_constants: Optional geo target constant resource names
            audience_user_lists: Optional user list resource names

        Returns:
            Created conversion value rule details
        """
        status_enum = getattr(
            ConversionValueRuleStatusEnum.ConversionValueRuleStatus, status
        )
        return await service.create_conversion_value_rule(
            ctx=ctx,
            customer_id=customer_id,
            action_operation=action_operation,
            action_value=action_value,
            status=status_enum,
            device_types=device_types,
            geo_location_geo_target_constants=geo_location_geo_target_constants,
            audience_user_lists=audience_user_lists,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_conversion_value_rule(
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
        status: Optional[str] = None,
        action_operation: Optional[str] = None,
        action_value: Optional[float] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a conversion value rule.

        Args:
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to update
            status: New status - ENABLED, PAUSED, or REMOVED
            action_operation: New operation - ADD, MULTIPLY, or SET
            action_value: New value

        Returns:
            Updated conversion value rule details
        """
        status_enum = (
            getattr(ConversionValueRuleStatusEnum.ConversionValueRuleStatus, status)
            if status
            else None
        )
        return await service.update_conversion_value_rule(
            ctx=ctx,
            customer_id=customer_id,
            rule_resource_name=rule_resource_name,
            status=status_enum,
            action_operation=action_operation,
            action_value=action_value,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def list_conversion_value_rules(
        ctx: Context,
        customer_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List conversion value rules for a customer.

        Args:
            customer_id: The customer ID
            limit: Maximum number of results

        Returns:
            List of conversion value rules
        """
        return await service.list_conversion_value_rules(
            ctx=ctx,
            customer_id=customer_id,
            limit=limit,
        )

    async def remove_conversion_value_rule(
        ctx: Context,
        customer_id: str,
        rule_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a conversion value rule so it no longer adjusts conversion values.

        Args:
            customer_id: The customer ID
            rule_resource_name: Resource name of the rule to remove

        Returns:
            Removal confirmation with resource name

        Returns:
            Removal result
        """
        return await service.remove_conversion_value_rule(
            ctx=ctx,
            customer_id=customer_id,
            rule_resource_name=rule_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_conversion_value_rule,
            update_conversion_value_rule,
            list_conversion_value_rules,
            remove_conversion_value_rule,
        ]
    )
    return tools


def register_conversion_value_rule_tools(
    mcp: FastMCP[Any],
) -> ConversionValueRuleService:
    """Register conversion value rule tools with the MCP server.

    Returns the ConversionValueRuleService instance for testing purposes.
    """
    service = ConversionValueRuleService()
    tools = create_conversion_value_rule_tools(service)

    for tool in tools:
        mcp.tool(tool)

    return service
